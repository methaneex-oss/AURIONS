#pragma once

#include <cstdint>
#include <filesystem>
#include <string>
#include <vector>

struct sqlite3;

namespace aurions {

struct BeliefRevision {
    int number{};
    double confidence{};
    std::string epistemic_status;
    std::string reason;
    std::int64_t created_at_ms{};
    int evidence_count{};
    std::string evidence_source_ref;
    std::string evidence_stance;
    double evidence_reliability{};
    double evidence_relevance{};
};

struct BeliefSnapshot {
    std::string id;
    std::string proposition;
    std::string domain;
    std::vector<BeliefRevision> revisions;
};

class BeliefStore final {
public:
    explicit BeliefStore(const std::filesystem::path& database_path);
    ~BeliefStore();

    BeliefStore(const BeliefStore&) = delete;
    BeliefStore& operator=(const BeliefStore&) = delete;

    [[nodiscard]] BeliefSnapshot create(
        const std::string& domain,
        const std::string& proposition,
        double prior_confidence = 0.5);

    [[nodiscard]] BeliefSnapshot add_evidence(
        const std::string& belief_id,
        const std::string& experience_id,
        const std::string& stance,
        double reliability,
        double relevance = 1.0);

    [[nodiscard]] BeliefSnapshot get(const std::string& belief_id) const;

private:
    sqlite3* db_{};
};

}  // namespace aurions
