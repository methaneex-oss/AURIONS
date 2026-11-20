#include "aurions/experience_store.hpp"

#include <charconv>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

[[nodiscard]] int parse_sensitivity(std::string_view value) {
    int result{};
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size()) {
        throw std::invalid_argument("sensitivity must be an integer from 0 to 4");
    }
    return result;
}

[[nodiscard]] std::size_t parse_limit(std::string_view value) {
    unsigned long long result{};
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size() ||
        result == 0 || result > 100) {
        throw std::invalid_argument("limit must be an integer from 1 to 100");
    }
    return static_cast<std::size_t>(result);
}

[[nodiscard]] std::string json_escape(std::string_view value) {
    std::string output;
    output.reserve(value.size() + 8);
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
                    constexpr char hex[] = "0123456789abcdef";
                    output += "\\u00";
                    output.push_back(hex[(c >> 4U) & 0x0fU]);
                    output.push_back(hex[c & 0x0fU]);
                } else {
                    output.push_back(static_cast<char>(c));
                }
        }
    }
    return output;
}

void usage() {
    std::cerr
        << "Usage:\n"
        << "  aurions experience record <database> <source> <provenance> <sensitivity 0-4> <content>\n"
        << "  aurions experience show <database> <experience-uuid>\n";
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc < 2 || std::string_view(argv[1]) != "experience" || argc < 4) {
            usage();
            return EXIT_FAILURE;
        }

        const std::string_view operation(argv[2]);
        aurions::ExperienceStore store(argv[3]);

        if (operation == "record" && argc == 8) {
            const auto saved = store.record(
                argv[4], argv[7], argv[5], parse_sensitivity(argv[6]));
            std::cout << "{\"experience_id\":\"" << saved.id << "\"}\n";
            return EXIT_SUCCESS;
        }


        if (operation == "search" && (argc == 6 || argc == 7)) {
            const std::size_t limit = argc == 7 ? parse_limit(argv[6]) : 10;
            const auto matches = store.search(argv[5], limit);
            std::cout << "[";
            for (std::size_t i = 0; i < matches.size(); ++i) {
                if (i != 0) std::cout << ",";
                const auto& match = matches[i];
                const auto& experience = match.experience;
                std::cout
                    << "{\"experience_id\":\"" << experience.id
                    << "\",\"relevance\":" << match.relevance
                    << ",\"source_type\":\"" << json_escape(experience.source_type)
                    << "\",\"content\":\"" << json_escape(experience.content)
                    << "\",\"provenance_ref\":\"" << json_escape(experience.provenance_ref)
                    << "\",\"observed_at_ms\":" << experience.observed_at_ms
                    << ",\"recorded_at_ms\":" << experience.recorded_at_ms
                    << ",\"sensitivity\":" << experience.sensitivity << "}";
            }
            std::cout << "]\n";
            return EXIT_SUCCESS;
        }

        if (operation == "show" && argc == 5) {
            const auto found = store.get(argv[4]);
            if (!found) {
                std::cerr << "Experience not found\n";
                return 2;
            }
            std::cout
                << "{\"experience_id\":\"" << found->id
                << "\",\"source_type\":\"" << json_escape(found->source_type)
                << "\",\"content\":\"" << json_escape(found->content)
                << "\",\"provenance_ref\":\"" << json_escape(found->provenance_ref)
                << "\",\"observed_at_ms\":" << found->observed_at_ms
                << ",\"recorded_at_ms\":" << found->recorded_at_ms
                << ",\"sensitivity\":" << found->sensitivity << "}\n";
            return EXIT_SUCCESS;
        }

        usage();
        return EXIT_FAILURE;
    } catch (const std::exception& error) {
        std::cerr << "AURIONS: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
