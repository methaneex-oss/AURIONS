#pragma once

#include <chrono>
#include <cstddef>
#include <filesystem>
#include <string>

namespace aurions {

struct InferencePreviewResult {
    std::string job_id;
    std::string candidate_artifact_sha256;
    std::string candidate_status;
    std::string generated_text;
    std::size_t max_new_tokens{};
};

class InferenceAdapter {
public:
    virtual ~InferenceAdapter() = default;
    [[nodiscard]] virtual InferencePreviewResult preview(
        const std::string& candidate_artifact_ref,
        const std::string& prompt,
        std::size_t max_new_tokens) const = 0;
};

// A bounded POSIX process adapter. The Python worker is untrusted and can only
// return a quarantined preview; it has no live cognition or activation authority.
class PythonProcessInferenceAdapter final : public InferenceAdapter {
public:
    PythonProcessInferenceAdapter(
        std::string python_executable,
        std::filesystem::path artifact_store,
        std::chrono::milliseconds timeout = std::chrono::seconds(15),
        std::size_t max_response_bytes = 65536);

    [[nodiscard]] InferencePreviewResult preview(
        const std::string& candidate_artifact_ref,
        const std::string& prompt,
        std::size_t max_new_tokens) const override;

private:
    std::string python_executable_;
    std::filesystem::path artifact_store_;
    std::chrono::milliseconds timeout_;
    std::size_t max_response_bytes_;
};

}  // namespace aurions
