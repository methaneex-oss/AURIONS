#include "aurions/strategy_store.hpp"

#include <sqlite3.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iterator>
#include <random>
#include <stdexcept>
#include <string_view>
#include <utility>

namespace aurions {
namespace {

using IdBytes = std::array<unsigned char, 16>;

std::int64_t now_ms() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
}

IdBytes make_id() {
    std::random_device random;
    IdBytes bytes{};
    for (auto& byte : bytes) byte = static_cast<unsigned char>(random() & 0xffU);
    bytes[6] = static_cast<unsigned char>((bytes[6] & 0x0fU) | 0x40U);
    bytes[8] = static_cast<unsigned char>((bytes[8] & 0x3fU) | 0x80U);
    return bytes;
}

std::string format_id(const IdBytes& bytes) {
    constexpr char hex[] = "0123456789abcdef";
    std::string result;
    result.reserve(36);
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        if (i == 4 || i == 6 || i == 8 || i == 10) result.push_back('-');
        result.push_back(hex[bytes[i] >> 4U]);
        result.push_back(hex[bytes[i] & 0x0fU]);
    }
    return result;
}

IdBytes parse_id(std::string_view value, const char* label) {
    if (value.size() != 36) throw std::invalid_argument(std::string(label) + " must be a UUID");
    IdBytes bytes{};
    auto nibble = [](char c) -> unsigned char {
        if (c >= '0' && c <= '9') return static_cast<unsigned char>(c - '0');
        if (c >= 'a' && c <= 'f') return static_cast<unsigned char>(c - 'a' + 10);
        if (c >= 'A' && c <= 'F') return static_cast<unsigned char>(c - 'A' + 10);
        throw std::invalid_argument("UUID contains a non-hexadecimal character");
    };
    std::size_t out = 0;
    for (std::size_t i = 0; i < value.size();) {
        if (i == 8 || i == 13 || i == 18 || i == 23) {
            if (value[i++] != '-') throw std::invalid_argument("UUID is malformed");
            continue;
        }
        if (out >= bytes.size() || i + 1 >= value.size())
            throw std::invalid_argument("UUID is malformed");
        bytes[out++] = static_cast<unsigned char>(
            (nibble(value[i]) << 4U) | nibble(value[i + 1]));
        i += 2;
    }
    if (out != bytes.size()) throw std::invalid_argument("UUID is malformed");
    return bytes;
}

void check(int rc, sqlite3* db, std::string_view operation) {
    if (rc != SQLITE_OK && rc != SQLITE_ROW && rc != SQLITE_DONE)
        throw std::runtime_error(std::string(operation) + ": " + sqlite3_errmsg(db));
}

void exec(sqlite3* db, const char* sql) {
    char* error = nullptr;
    const int rc = sqlite3_exec(db, sql, nullptr, nullptr, &error);
    if (rc != SQLITE_OK) {
        const std::string message = error ? error : sqlite3_errmsg(db);
        sqlite3_free(error);
        throw std::runtime_error("SQLite execution failed: " + message);
    }
}

class Statement final {
public:
    Statement(sqlite3* db, const char* sql) : db_(db) {
        check(sqlite3_prepare_v2(db, sql, -1, &stmt_, nullptr), db, "prepare statement");
    }
    ~Statement() { sqlite3_finalize(stmt_); }
    Statement(const Statement&) = delete;
    Statement& operator=(const Statement&) = delete;
    sqlite3_stmt* get() const noexcept { return stmt_; }
private:
    sqlite3* db_{};
    sqlite3_stmt* stmt_{};
};

class Transaction final {
public:
    explicit Transaction(sqlite3* db) : db_(db) { exec(db_, "BEGIN IMMEDIATE"); }
    ~Transaction() {
        if (!committed_) sqlite3_exec(db_, "ROLLBACK", nullptr, nullptr, nullptr);
    }
    void commit() {
        exec(db_, "COMMIT");
        committed_ = true;
    }
private:
    sqlite3* db_{};
    bool committed_{};
};

void bind_id(sqlite3* db, sqlite3_stmt* stmt, int index, const IdBytes& id) {
    check(sqlite3_bind_blob(stmt, index, id.data(), static_cast<int>(id.size()),
                            SQLITE_TRANSIENT), db, "bind UUID");
}

void bind_text(sqlite3* db, sqlite3_stmt* stmt, int index, const std::string& value) {
    check(sqlite3_bind_text(stmt, index, value.data(), static_cast<int>(value.size()),
                            SQLITE_TRANSIENT), db, "bind text");
}

std::string column_text(sqlite3_stmt* stmt, int column) {
    const auto* value = sqlite3_column_text(stmt, column);
    const int size = sqlite3_column_bytes(stmt, column);
    return value ? std::string(reinterpret_cast<const char*>(value),
                               static_cast<std::size_t>(size)) : std::string{};
}

std::string json_escape(std::string_view value) {
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

struct StrategyStats {
    std::string strategy_ref;
    std::int64_t successes{};
    std::int64_t trials{};
    double posterior{};
    double score{};
};

StrategyStats read_stats(sqlite3* db, const std::string& context,
                         const std::string& strategy) {
    Statement query(db, R"sql(
        SELECT
          coalesce(sum(CASE WHEN json_extract(e.details_json,'$.outcome')='success'
                            THEN 1 ELSE 0 END),0),
          count(*)
        FROM predictions p
        JOIN prediction_evaluations e ON e.prediction_id=p.prediction_id
        WHERE json_extract(p.expected_outcome_json,'$.context_ref')=?1
          AND json_extract(p.expected_outcome_json,'$.strategy_ref')=?2
          AND json_extract(e.details_json,'$.outcome') IN ('success','failure')
    )sql");
    bind_text(db, query.get(), 1, context);
    bind_text(db, query.get(), 2, strategy);
    const int rc = sqlite3_step(query.get());
    check(rc, db, "read strategy outcome history");
    StrategyStats stats;
    stats.strategy_ref = strategy;
    stats.successes = sqlite3_column_int64(query.get(), 0);
    stats.trials = sqlite3_column_int64(query.get(), 1);
    // Beta(1,1) posterior mean: a transparent prior, not a hardcoded
    // strategy preference. Evidence counts remain in each prediction.
    stats.posterior = static_cast<double>(stats.successes + 1) /
                      static_cast<double>(stats.trials + 2);
    return stats;
}

void validate_ref(const std::string& value, const char* label) {
    if (value.empty() || value.size() > 512)
        throw std::invalid_argument(std::string(label) + " must contain 1-512 bytes");
}

}  // namespace

StrategyStore::StrategyStore(const std::filesystem::path& database_path) {
    const int rc = sqlite3_open_v2(database_path.string().c_str(), &db_,
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX, nullptr);
    if (rc != SQLITE_OK) {
        const std::string message = db_ ? sqlite3_errmsg(db_) : "unable to allocate SQLite handle";
        if (db_) sqlite3_close(db_);
        db_ = nullptr;
        throw std::runtime_error("cannot open strategy database: " + message);
    }
    try {
        exec(db_, "PRAGMA foreign_keys=ON");
        // These definitions match the canonical aurion_memory.base.sql tables.
        // An incompatible existing schema fails closed rather than creating a
        // parallel strategy-history store.
        exec(db_, R"sql(
            CREATE TABLE IF NOT EXISTS predictions (
              prediction_id BLOB PRIMARY KEY CHECK(length(prediction_id)=16),
              subject_ref TEXT NOT NULL,
              expected_outcome_json TEXT NOT NULL CHECK(json_valid(expected_outcome_json)),
              evaluation_criteria_json TEXT NOT NULL CHECK(json_valid(evaluation_criteria_json)),
              horizon_end_ms INTEGER,
              created_at_ms INTEGER NOT NULL,
              status TEXT NOT NULL CHECK(status IN
                ('open','partially_evaluated','evaluated','cancelled'))
            ) STRICT;
            CREATE TABLE IF NOT EXISTS prediction_evaluations (
              evaluation_id BLOB PRIMARY KEY CHECK(length(evaluation_id)=16),
              prediction_id BLOB NOT NULL REFERENCES predictions(prediction_id),
              observed_outcome_ref TEXT NOT NULL,
              result TEXT NOT NULL CHECK(result IN
                ('correct','partially_correct','incorrect','inconclusive')),
              evaluator TEXT NOT NULL,
              evaluated_at_ms INTEGER NOT NULL,
              details_json TEXT CHECK(details_json IS NULL OR json_valid(details_json))
            ) STRICT;
        )sql");
    } catch (...) {
        sqlite3_close(db_);
        db_ = nullptr;
        throw;
    }
}

StrategyStore::~StrategyStore() {
    if (db_) sqlite3_close(db_);
}

StrategyChoice StrategyStore::choose(
    const std::string& context_ref,
    std::vector<std::string> strategy_refs) {
    validate_ref(context_ref, "context reference");
    if (strategy_refs.empty() || strategy_refs.size() > 50)
        throw std::invalid_argument("provide between 1 and 50 candidate strategies");
    for (const auto& ref : strategy_refs) validate_ref(ref, "strategy reference");
    std::sort(strategy_refs.begin(), strategy_refs.end());
    if (std::adjacent_find(strategy_refs.begin(), strategy_refs.end()) != strategy_refs.end())
        throw std::invalid_argument("candidate strategy references must be unique");

    Transaction transaction(db_);
    std::vector<StrategyStats> stats;
    stats.reserve(strategy_refs.size());
    std::int64_t total_trials = 0;
    for (const auto& strategy : strategy_refs) {
        stats.push_back(read_stats(db_, context_ref, strategy));
        total_trials += stats.back().trials;
    }

    auto selected = stats.end();
    for (auto it = stats.begin(); it != stats.end(); ++it) {
        if (it->trials == 0) {
            selected = it;
            break; // deterministic initial exploration of unseen alternatives
        }
    }

    std::string basis = "untried";
    if (selected == stats.end()) {
        basis = "ucb1";
        const double log_total = std::log(static_cast<double>(
            std::max<std::int64_t>(1, total_trials)));
        selected = stats.begin();
        selected->score = selected->posterior +
            std::sqrt(2.0 * log_total / static_cast<double>(selected->trials));
        for (auto it = std::next(stats.begin()); it != stats.end(); ++it) {
            it->score = it->posterior +
                std::sqrt(2.0 * log_total / static_cast<double>(it->trials));
            if (it->score > selected->score + 1e-12) selected = it;
        }
    } else {
        selected->score = 0.0;
    }

    const IdBytes prediction_bytes = make_id();
    const std::string prediction_id = format_id(prediction_bytes);
    const std::string expected =
        "{\"kind\":\"strategy_success\",\"context_ref\":\"" +
        json_escape(context_ref) + "\",\"strategy_ref\":\"" +
        json_escape(selected->strategy_ref) + "\",\"success_probability\":" +
        std::to_string(selected->posterior) + ",\"successes\":" +
        std::to_string(selected->successes) + ",\"trials\":" +
        std::to_string(selected->trials) + ",\"selection_score\":" +
        std::to_string(selected->score) + ",\"selection_basis\":\"" + basis + "\"}";
    const std::string criteria =
        "{\"metric\":\"binary_success\",\"posterior\":\"Beta(1,1)\","
        "\"selection_policy\":\"UCB1_with_initial_untried_exploration\"}";

    Statement insert(db_, R"sql(
        INSERT INTO predictions(
          prediction_id,subject_ref,expected_outcome_json,evaluation_criteria_json,
          horizon_end_ms,created_at_ms,status
        ) VALUES(?1,'strategy-selection',?2,?3,NULL,?4,'open')
    )sql");
    bind_id(db_, insert.get(), 1, prediction_bytes);
    bind_text(db_, insert.get(), 2, expected);
    bind_text(db_, insert.get(), 3, criteria);
    check(sqlite3_bind_int64(insert.get(), 4, now_ms()), db_, "bind prediction timestamp");
    check(sqlite3_step(insert.get()), db_, "persist strategy prediction");
    transaction.commit();

    return StrategyChoice{
        prediction_id, context_ref, selected->strategy_ref, selected->posterior,
        selected->score, selected->successes, selected->trials, basis
    };
}

StrategyOutcome StrategyStore::record_outcome(
    const std::string& prediction_id,
    const std::string& experience_id,
    const std::string& outcome) {
    const IdBytes prediction_bytes = parse_id(prediction_id, "prediction ID");
    const IdBytes experience_bytes = parse_id(experience_id, "experience ID");
    if (outcome != "success" && outcome != "failure")
        throw std::invalid_argument("outcome must be success or failure");

    Transaction transaction(db_);
    std::string source_type;
    std::string provenance_ref;
    {
        Statement experience(db_, R"sql(
            SELECT source_type,provenance_ref FROM experiences
            WHERE experience_id=?1 AND retention_state='active'
        )sql");
        bind_id(db_, experience.get(), 1, experience_bytes);
        const int rc = sqlite3_step(experience.get());
        if (rc == SQLITE_DONE) throw std::runtime_error("active outcome experience not found");
        check(rc, db_, "read outcome experience");
        source_type = column_text(experience.get(), 0);
        provenance_ref = column_text(experience.get(), 1);
    }

    {
        Statement reused(db_, R"sql(
            SELECT 1
            FROM prediction_evaluations e
            JOIN predictions p ON p.prediction_id=e.prediction_id
            WHERE p.subject_ref='strategy-selection'
              AND e.observed_outcome_ref=?1
            LIMIT 1
        )sql");
        bind_text(db_, reused.get(), 1, "experience:" + format_id(experience_bytes));
        const int rc = sqlite3_step(reused.get());
        if (rc == SQLITE_ROW)
            throw std::runtime_error("outcome experience has already been used for strategy learning");
        check(rc, db_, "check reused strategy evidence");
    }

    std::string context_ref;
    std::string strategy_ref;
    double probability = 0.0;
    {
        Statement prediction(db_, R"sql(
            SELECT json_extract(expected_outcome_json,'$.context_ref'),
                   json_extract(expected_outcome_json,'$.strategy_ref'),
                   json_extract(expected_outcome_json,'$.success_probability'), status
            FROM predictions WHERE prediction_id=?1
        )sql");
        bind_id(db_, prediction.get(), 1, prediction_bytes);
        const int rc = sqlite3_step(prediction.get());
        if (rc == SQLITE_DONE) throw std::runtime_error("prediction not found");
        check(rc, db_, "read strategy prediction");
        context_ref = column_text(prediction.get(), 0);
        strategy_ref = column_text(prediction.get(), 1);
        probability = sqlite3_column_double(prediction.get(), 2);
        if (column_text(prediction.get(), 3) != "open")
            throw std::runtime_error("prediction is not open for outcome evaluation");
    }

    const IdBytes evaluation_bytes = make_id();
    const std::string details =
        "{\"outcome\":\"" + outcome + "\",\"experience_id\":\"" +
        format_id(experience_bytes) + "\",\"source_type\":\"" +
        json_escape(source_type) + "\",\"provenance_ref\":\"" +
        json_escape(provenance_ref) + "\",\"classification\":\"caller_supplied\"}";
    const std::string result = outcome == "success" ? "correct" : "incorrect";
    {
        Statement insert(db_, R"sql(
            INSERT INTO prediction_evaluations(
              evaluation_id,prediction_id,observed_outcome_ref,result,evaluator,
              evaluated_at_ms,details_json
            ) VALUES(?1,?2,?3,?4,'caller_classified',?5,?6)
        )sql");
        bind_id(db_, insert.get(), 1, evaluation_bytes);
        bind_id(db_, insert.get(), 2, prediction_bytes);
        bind_text(db_, insert.get(), 3, "experience:" + format_id(experience_bytes));
        bind_text(db_, insert.get(), 4, result);
        check(sqlite3_bind_int64(insert.get(), 5, now_ms()), db_, "bind evaluation timestamp");
        bind_text(db_, insert.get(), 6, details);
        check(sqlite3_step(insert.get()), db_, "persist prediction evaluation");
    }
    {
        Statement update(db_, "UPDATE predictions SET status='evaluated' WHERE prediction_id=?1 AND status='open'");
        bind_id(db_, update.get(), 1, prediction_bytes);
        check(sqlite3_step(update.get()), db_, "close evaluated prediction");
        if (sqlite3_changes(db_) != 1)
            throw std::runtime_error("prediction changed during outcome evaluation");
    }
    transaction.commit();

    return StrategyOutcome{
        format_id(prediction_bytes), format_id(experience_bytes), context_ref,
        strategy_ref, outcome, result, probability
    };
}

}  // namespace aurions
