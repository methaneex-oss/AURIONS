#include "aurions/inference_adapter.hpp"

#include <spawn.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <poll.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>

#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <random>
#include <stdexcept>
#include <string_view>
#include <unordered_map>
#include <utility>
#include <vector>

extern char** environ;

namespace aurions {
namespace {

struct JsonScalar {
    std::string value;
    bool is_string{};
};

class FlatJsonObjectParser final {
public:
    explicit FlatJsonObjectParser(std::string_view input) : input_(input) {}

    std::unordered_map<std::string, JsonScalar> parse() {
        skip_space();
        expect('{');
        std::unordered_map<std::string, JsonScalar> values;
        skip_space();
        if (consume('}')) {
            finish();
            return values;
        }
        while (true) {
            skip_space();
            const std::string key = parse_string();
            skip_space();
            expect(':');
            skip_space();
            JsonScalar value;
            if (peek() == '"') {
                value.value = parse_string();
                value.is_string = true;
            } else {
                value.value = parse_primitive();
            }
            if (!values.emplace(key, std::move(value)).second)
                throw std::runtime_error("worker response contains a duplicate JSON key");
            skip_space();
            if (consume('}')) break;
            expect(',');
        }
        finish();
        return values;
    }

private:
    char peek() const {
        if (position_ >= input_.size()) throw std::runtime_error("truncated worker JSON response");
        return input_[position_];
    }

    void skip_space() {
        while (position_ < input_.size() &&
               (input_[position_] == ' ' || input_[position_] == '\t' ||
                input_[position_] == '\r' || input_[position_] == '\n')) {
            ++position_;
        }
    }

    bool consume(char expected) {
        if (position_ < input_.size() && input_[position_] == expected) {
            ++position_;
            return true;
        }
        return false;
    }

    void expect(char expected) {
        if (!consume(expected)) throw std::runtime_error("malformed worker JSON response");
    }

    static void append_utf8(std::string& output, std::uint32_t codepoint) {
        if (codepoint <= 0x7f) {
            output.push_back(static_cast<char>(codepoint));
        } else if (codepoint <= 0x7ff) {
            output.push_back(static_cast<char>(0xc0 | (codepoint >> 6)));
            output.push_back(static_cast<char>(0x80 | (codepoint & 0x3f)));
        } else if (codepoint <= 0xffff) {
            output.push_back(static_cast<char>(0xe0 | (codepoint >> 12)));
            output.push_back(static_cast<char>(0x80 | ((codepoint >> 6) & 0x3f)));
            output.push_back(static_cast<char>(0x80 | (codepoint & 0x3f)));
        } else if (codepoint <= 0x10ffff) {
            output.push_back(static_cast<char>(0xf0 | (codepoint >> 18)));
            output.push_back(static_cast<char>(0x80 | ((codepoint >> 12) & 0x3f)));
            output.push_back(static_cast<char>(0x80 | ((codepoint >> 6) & 0x3f)));
            output.push_back(static_cast<char>(0x80 | (codepoint & 0x3f)));
        } else {
            throw std::runtime_error("invalid Unicode scalar in worker response");
        }
    }

    std::uint32_t parse_hex4() {
        if (input_.size() - position_ < 4)
            throw std::runtime_error("truncated Unicode escape in worker response");
        std::uint32_t value = 0;
        for (int i = 0; i < 4; ++i) {
            const char c = input_[position_++];
            value <<= 4;
            if (c >= '0' && c <= '9') value |= static_cast<std::uint32_t>(c - '0');
            else if (c >= 'a' && c <= 'f') value |= static_cast<std::uint32_t>(c - 'a' + 10);
            else if (c >= 'A' && c <= 'F') value |= static_cast<std::uint32_t>(c - 'A' + 10);
            else throw std::runtime_error("invalid Unicode escape in worker response");
        }
        return value;
    }

    std::string parse_string() {
        expect('"');
        std::string output;
        while (true) {
            const unsigned char c = static_cast<unsigned char>(peek());
            ++position_;
            if (c == '"') return output;
            if (c < 0x20) throw std::runtime_error("unescaped control character in worker response");
            if (c != '\\') {
                output.push_back(static_cast<char>(c));
                continue;
            }
            const char escaped = peek();
            ++position_;
            switch (escaped) {
                case '"': output.push_back('"'); break;
                case '\\': output.push_back('\\'); break;
                case '/': output.push_back('/'); break;
                case 'b': output.push_back('\b'); break;
                case 'f': output.push_back('\f'); break;
                case 'n': output.push_back('\n'); break;
                case 'r': output.push_back('\r'); break;
                case 't': output.push_back('\t'); break;
                case 'u': {
                    std::uint32_t codepoint = parse_hex4();
                    if (codepoint >= 0xd800 && codepoint <= 0xdbff) {
                        expect('\\');
                        expect('u');
                        const std::uint32_t low = parse_hex4();
                        if (low < 0xdc00 || low > 0xdfff)
                            throw std::runtime_error("invalid Unicode surrogate pair");
                        codepoint = 0x10000 + ((codepoint - 0xd800) << 10) + (low - 0xdc00);
                    } else if (codepoint >= 0xdc00 && codepoint <= 0xdfff) {
                        throw std::runtime_error("unpaired Unicode low surrogate");
                    }
                    append_utf8(output, codepoint);
                    break;
                }
                default: throw std::runtime_error("invalid JSON escape in worker response");
            }
        }
    }

    std::string parse_primitive() {
        const std::size_t start = position_;
        while (position_ < input_.size() && input_[position_] != ',' &&
               input_[position_] != '}' && input_[position_] != ' ' &&
               input_[position_] != '\t' && input_[position_] != '\r' &&
               input_[position_] != '\n') {
            ++position_;
        }
        if (start == position_) throw std::runtime_error("missing worker JSON value");
        const std::string value(input_.substr(start, position_ - start));
        if (value != "null" && value != "true" && value != "false" &&
            !std::all_of(value.begin(), value.end(), [](unsigned char c) {
                return std::isdigit(c) != 0;
            })) {
            throw std::runtime_error("unsupported worker JSON scalar");
        }
        return value;
    }

    void finish() {
        skip_space();
        if (position_ != input_.size())
            throw std::runtime_error("trailing data after worker JSON response");
    }

    std::string_view input_;
    std::size_t position_{};
};

std::string json_escape(std::string_view value) {
    std::string output;
    output.reserve(value.size() + 8);
    constexpr char hex[] = "0123456789abcdef";
    for (const unsigned char c : value) {
        switch (c) {
            case '"': output += "\\\""; break;
            case '\\': output += "\\\\"; break;
            case '\b': output += "\\b"; break;
            case '\f': output += "\\f"; break;
            case '\n': output += "\\n"; break;
            case '\r': output += "\\r"; break;
            case '\t': output += "\\t"; break;
            default:
                if (c < 0x20) {
                    output += "\\u00";
                    output.push_back(hex[(c >> 4) & 0x0f]);
                    output.push_back(hex[c & 0x0f]);
                } else {
                    output.push_back(static_cast<char>(c));
                }
        }
    }
    return output;
}

std::string make_job_id() {
    std::array<unsigned char, 16> bytes{};
    std::random_device random;
    for (auto& byte : bytes) byte = static_cast<unsigned char>(random() & 0xffU);
    bytes[6] = static_cast<unsigned char>((bytes[6] & 0x0fU) | 0x40U);
    bytes[8] = static_cast<unsigned char>((bytes[8] & 0x3fU) | 0x80U);
    constexpr char hex[] = "0123456789abcdef";
    std::string id;
    id.reserve(36);
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        if (i == 4 || i == 6 || i == 8 || i == 10) id.push_back('-');
        id.push_back(hex[bytes[i] >> 4]);
        id.push_back(hex[bytes[i] & 0x0f]);
    }
    return id;
}

std::string required_string(
    const std::unordered_map<std::string, JsonScalar>& values, const char* key) {
    const auto found = values.find(key);
    if (found == values.end() || !found->second.is_string)
        throw std::runtime_error(std::string("worker response is missing string field: ") + key);
    return found->second.value;
}

void set_cloexec(int fd) {
    const int flags = fcntl(fd, F_GETFD);
    if (flags < 0 || fcntl(fd, F_SETFD, flags | FD_CLOEXEC) < 0)
        throw std::runtime_error("could not set close-on-exec on worker pipe");
}

void close_if_open(int& fd) noexcept {
    if (fd >= 0) {
        close(fd);
        fd = -1;
    }
}

std::string run_worker_process(
    const std::string& python,
    const std::filesystem::path& artifact_store,
    const std::string& request,
    std::chrono::milliseconds timeout,
    std::size_t max_response_bytes) {
    int input_pair[2]{-1, -1};
    int output_pipe[2]{-1, -1};
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, input_pair) != 0)
        throw std::runtime_error("could not create worker input socket");
    if (pipe(output_pipe) != 0) {
        close_if_open(input_pair[0]);
        close_if_open(input_pair[1]);
        throw std::runtime_error("could not create worker output pipe");
    }
    try {
        for (const int fd : {input_pair[0], input_pair[1], output_pipe[0], output_pipe[1]})
            set_cloexec(fd);
    } catch (...) {
        close_if_open(input_pair[0]); close_if_open(input_pair[1]);
        close_if_open(output_pipe[0]); close_if_open(output_pipe[1]);
        throw;
    }

    posix_spawn_file_actions_t actions;
    int rc = posix_spawn_file_actions_init(&actions);
    if (rc != 0) {
        close_if_open(input_pair[0]); close_if_open(input_pair[1]);
        close_if_open(output_pipe[0]); close_if_open(output_pipe[1]);
        throw std::runtime_error("could not initialize worker process actions");
    }
    posix_spawn_file_actions_adddup2(&actions, input_pair[1], STDIN_FILENO);
    posix_spawn_file_actions_adddup2(&actions, output_pipe[1], STDOUT_FILENO);
    posix_spawn_file_actions_addclose(&actions, input_pair[0]);
    posix_spawn_file_actions_addclose(&actions, output_pipe[0]);
    posix_spawn_file_actions_addclose(&actions, input_pair[1]);
    posix_spawn_file_actions_addclose(&actions, output_pipe[1]);

    const std::vector<std::string> arguments{
        python, "-m", "aurions_ml.inference_worker",
        "--artifact-store", artifact_store.string(),
        "--max-message-bytes", "16384"
    };
    std::vector<char*> argv;
    argv.reserve(arguments.size() + 1);
    for (const auto& argument : arguments)
        argv.push_back(const_cast<char*>(argument.c_str()));
    argv.push_back(nullptr);

    pid_t child{};
    rc = posix_spawnp(&child, python.c_str(), &actions, nullptr, argv.data(), environ);
    posix_spawn_file_actions_destroy(&actions);
    close_if_open(input_pair[1]);
    close_if_open(output_pipe[1]);
    if (rc != 0) {
        close_if_open(input_pair[0]); close_if_open(output_pipe[0]);
        throw std::runtime_error("could not start Python inference worker");
    }

    auto terminate_child = [&]() noexcept {
        kill(child, SIGKILL);
        int status{};
        while (waitpid(child, &status, 0) < 0 && errno == EINTR) {}
    };

    std::size_t written = 0;
    while (written < request.size()) {
        const ssize_t count = send(
            input_pair[0], request.data() + written, request.size() - written, MSG_NOSIGNAL);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) {
            close_if_open(input_pair[0]);
            close_if_open(output_pipe[0]);
            terminate_child();
            throw std::runtime_error("failed to send request to inference worker");
        }
        written += static_cast<std::size_t>(count);
    }
    shutdown(input_pair[0], SHUT_WR);
    close_if_open(input_pair[0]);

    std::string response;
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    std::array<char, 4096> buffer{};
    while (true) {
        const auto remaining = std::chrono::duration_cast<std::chrono::milliseconds>(
            deadline - std::chrono::steady_clock::now());
        if (remaining.count() <= 0) {
            close_if_open(output_pipe[0]);
            terminate_child();
            throw std::runtime_error("inference worker timed out");
        }
        pollfd descriptor{output_pipe[0], static_cast<short>(POLLIN | POLLHUP), 0};
        const int poll_result = poll(&descriptor, 1, static_cast<int>(remaining.count()));
        if (poll_result < 0 && errno == EINTR) continue;
        if (poll_result == 0) {
            close_if_open(output_pipe[0]);
            terminate_child();
            throw std::runtime_error("inference worker timed out");
        }
        if (poll_result < 0) {
            close_if_open(output_pipe[0]);
            terminate_child();
            throw std::runtime_error("failed while waiting for inference worker");
        }
        const ssize_t count = read(output_pipe[0], buffer.data(), buffer.size());
        if (count < 0 && errno == EINTR) continue;
        if (count < 0) {
            close_if_open(output_pipe[0]);
            terminate_child();
            throw std::runtime_error("failed to read inference worker response");
        }
        if (count == 0) break;
        if (response.size() + static_cast<std::size_t>(count) > max_response_bytes) {
            close_if_open(output_pipe[0]);
            terminate_child();
            throw std::runtime_error("inference worker response exceeded its byte limit");
        }
        response.append(buffer.data(), static_cast<std::size_t>(count));
    }
    close_if_open(output_pipe[0]);

    int status{};
    while (waitpid(child, &status, 0) < 0) {
        if (errno == EINTR) continue;
        throw std::runtime_error("could not collect inference worker process");
    }
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0)
        throw std::runtime_error("inference worker exited unsuccessfully");
    return response;
}

}  // namespace

PythonProcessInferenceAdapter::PythonProcessInferenceAdapter(
    std::string python_executable,
    std::filesystem::path artifact_store,
    std::chrono::milliseconds timeout,
    std::size_t max_response_bytes)
    : python_executable_(std::move(python_executable)),
      artifact_store_(std::move(artifact_store)),
      timeout_(timeout),
      max_response_bytes_(max_response_bytes) {
    if (python_executable_.empty() || artifact_store_.empty())
        throw std::invalid_argument("Python executable and artifact store are required");
    if (timeout_.count() < 1 || timeout_ > std::chrono::minutes(2))
        throw std::invalid_argument("worker timeout must be between 1 ms and 120 seconds");
    if (max_response_bytes_ < 256 || max_response_bytes_ > 1'048'576)
        throw std::invalid_argument("worker response limit must be between 256 bytes and 1 MiB");
}

InferencePreviewResult PythonProcessInferenceAdapter::preview(
    const std::string& candidate_artifact_ref,
    const std::string& prompt,
    std::size_t max_new_tokens) const {
    constexpr std::string_view prefix = "artifact://sha256/";
    if (candidate_artifact_ref.size() != prefix.size() + 64 ||
        candidate_artifact_ref.compare(0, prefix.size(), prefix) != 0 ||
        !std::all_of(candidate_artifact_ref.begin() + static_cast<std::ptrdiff_t>(prefix.size()),
                     candidate_artifact_ref.end(), [](unsigned char c) {
                         return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
                     })) {
        throw std::invalid_argument("candidate artifact reference must be a SHA-256 artifact URI");
    }
    if (prompt.empty() || prompt.size() > 8192)
        throw std::invalid_argument("prompt must contain 1-8192 UTF-8 bytes");
    if (max_new_tokens < 1 || max_new_tokens > 128)
        throw std::invalid_argument("max_new_tokens must be between 1 and 128");

    const std::string job_id = make_job_id();
    const std::string digest = candidate_artifact_ref.substr(prefix.size());
    const std::string request =
        "{\"protocol_version\":\"1.0\",\"job_id\":\"" + job_id +
        "\",\"job_type\":\"candidate_inference_preview\",\"candidate_artifact_ref\":\"" +
        json_escape(candidate_artifact_ref) + "\",\"prompt\":\"" + json_escape(prompt) +
        "\",\"max_new_tokens\":" + std::to_string(max_new_tokens) + "}\n";

    const std::string response = run_worker_process(
        python_executable_, artifact_store_, request, timeout_, max_response_bytes_);
    FlatJsonObjectParser parser(response);
    const auto fields = parser.parse();
    if (required_string(fields, "protocol_version") != "1.0")
        throw std::runtime_error("inference worker returned an unsupported protocol version");
    if (required_string(fields, "job_id") != job_id)
        throw std::runtime_error("inference worker response job ID does not match request");
    const std::string status = required_string(fields, "status");
    if (status == "failed") {
        const std::string code = required_string(fields, "error_code");
        throw std::runtime_error("inference worker rejected request: " + code);
    }
    if (status != "completed")
        throw std::runtime_error("inference worker returned an unknown status");
    if (required_string(fields, "candidate_status") != "quarantined")
        throw std::runtime_error("inference worker returned a non-quarantined candidate");
    if (required_string(fields, "candidate_artifact_sha256") != digest)
        throw std::runtime_error("inference worker returned a mismatched candidate digest");
    const auto token_count = fields.find("max_new_tokens");
    if (token_count == fields.end() || token_count->second.is_string ||
        token_count->second.value != std::to_string(max_new_tokens))
        throw std::runtime_error("inference worker returned a mismatched token limit");

    return InferencePreviewResult{
        job_id, digest, "quarantined", required_string(fields, "generated_text"),
        max_new_tokens
    };
}

}  // namespace aurions
