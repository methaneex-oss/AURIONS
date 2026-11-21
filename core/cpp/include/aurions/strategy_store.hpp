#pragma once

#include <cstdint>
#include <filesystem>
#include <string>
#include <vector>

struct sqlite3;

namespace aurions {

struct StrategyChoice {
    std::string prediction_id;
    std::string context_ref;
    std::string strategy_ref;
    double posterior_success_probability{};
    double selection_score{};
    std::int64_t successes{};
    std::int64_t trials{};
    std::string selection_basis;
};

struct StrategyOutcome {
    std::string prediction_id;
    std::string experience_id;
    std::string context_ref;
    std::string strategy_ref;
    std::string outcome;
    std::string evaluation_result;
    double predicted_success_probability{};
};

class StrategyStore final {
public:
    explicit StrategyStore(const std::filesystem::path& database_path);
    ~StrategyStore();

    StrategyStore(const StrategyStore&) = delete;
    StrategyStore& operator=(const StrategyStore&) = delete;

    [[nodiscard]] StrategyChoice choose(
        const std::string& context_ref,
        std::vector<std::string> strategy_refs);

    [[nodiscard]] StrategyOutcome record_outcome(
        const std::string& prediction_id,
        const std::string& experience_id,
        const std::string& outcome);

private:
    sqlite3* db_{};
};

}  // namespace aurions
