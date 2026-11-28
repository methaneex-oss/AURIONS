#pragma once

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <vector>

struct sqlite3;

namespace aurions {

struct Representation {
    std::string id;
    std::string experience_id;
    std::string representation_type;
    std::string content_json;
    std::string method;
    std::string uncertainty_json;
    std::int64_t created_at_ms{};
};

// Stores modality-neutral, provenance-linked representations. It never
// interprets representation content or upgrades it into verified knowledge.
class RepresentationStore final {
public:
    explicit RepresentationStore(const std::filesystem::path& database_path);
    ~RepresentationStore();

    RepresentationStore(const RepresentationStore&) = delete;
    RepresentationStore& operator=(const RepresentationStore&) = delete;
    RepresentationStore(RepresentationStore&&) = delete;
    RepresentationStore& operator=(RepresentationStore&&) = delete;

    [[nodiscard]] Representation record(
        const std::string& experience_id,
        std::string representation_type,
        std::string content_json,
        std::string method,
        std::string uncertainty_json);

    [[nodiscard]] std::optional<Representation> get(const std::string& id) const;
    [[nodiscard]] std::vector<Representation> list_for_experience(
        const std::string& experience_id,
        std::size_t limit = 20) const;

private:
    sqlite3* db_{};
};

}  // namespace aurions
