#pragma once

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <vector>

struct sqlite3;

namespace aurions {

struct Experience {
    std::string id;
    std::string source_type;
    std::string content;
    std::string provenance_ref;
    std::int64_t observed_at_ms{};
    std::int64_t recorded_at_ms{};
    int sensitivity{};
};

struct ExperienceMatch {
    Experience experience;
    double relevance{};
};

class ExperienceStore final {
public:
    explicit ExperienceStore(const std::filesystem::path& database_path);
    ~ExperienceStore();

    ExperienceStore(const ExperienceStore&) = delete;
    ExperienceStore& operator=(const ExperienceStore&) = delete;
    ExperienceStore(ExperienceStore&&) = delete;
    ExperienceStore& operator=(ExperienceStore&&) = delete;

    [[nodiscard]] Experience record(
        std::string source_type,
        std::string content,
        std::string provenance_ref,
        int sensitivity = 0,
        std::optional<std::int64_t> observed_at_ms = std::nullopt);

    [[nodiscard]] std::optional<Experience> get(const std::string& id) const;

    // Bounded lexical retrieval over active experiences. Results are ranked by
    // query-term coverage, content matches, then recency and stable ID.
    [[nodiscard]] std::vector<ExperienceMatch> search(
        const std::string& query,
        std::size_t limit = 10) const;

private:
    sqlite3* db_{};
};

}  // namespace aurions
