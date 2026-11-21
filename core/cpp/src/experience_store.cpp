#include "aurions/experience_store.hpp"

#include <sqlite3.h>

#include <algorithm>
#include <array>
#include <cctype>
#include <unordered_set>
#include <vector>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <random>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace aurions {
namespace {

using IdBytes = std::array<unsigned char, 16>;

[[nodiscard]] std::int64_t now_ms() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
}

[[nodiscard]] IdBytes make_id_bytes() {
    std::random_device random;
    IdBytes bytes{};
    for (auto& byte : bytes) {
        byte = static_cast<unsigned char>(random() & 0xffU);
    }
    // RFC 4122 UUID v4 layout.
    bytes[6] = static_cast<unsigned char>((bytes[6] & 0x0fU) | 0x40U);
    bytes[8] = static_cast<unsigned char>((bytes[8] & 0x3fU) | 0x80U);
    return bytes;
}

[[nodiscard]] std::string format_id(const IdBytes& bytes) {
    constexpr char hex[] = "0123456789abcdef";
    std::string result;
    result.reserve(36);
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        if (i == 4 || i == 6 || i == 8 || i == 10) result.push_back('-');
        result.push_back(hex[(bytes[i] >> 4U) & 0x0fU]);
        result.push_back(hex[bytes[i] & 0x0fU]);
    }
    return result;
}

[[nodiscard]] IdBytes parse_id(std::string_view value) {
    if (value.size() != 36) throw std::invalid_argument("experience ID must be a UUID");
    IdBytes bytes{};
    std::size_t out = 0;
    auto nibble = [](char c) -> unsigned char {
        if (c >= '0' && c <= '9') return static_cast<unsigned char>(c - '0');
        if (c >= 'a' && c <= 'f') return static_cast<unsigned char>(c - 'a' + 10);
        if (c >= 'A' && c <= 'F') return static_cast<unsigned char>(c - 'A' + 10);
        throw std::invalid_argument("experience ID contains a non-hexadecimal character");
    };
    for (std::size_t i = 0; i < value.size();) {
        if (i == 8 || i == 13 || i == 18 || i == 23) {
            if (value[i] != '-') throw std::invalid_argument("experience ID is not a UUID");
            ++i;
            continue;
        }
        if (out >= bytes.size() || i + 1 >= value.size()) {
            throw std::invalid_argument("experience ID is malformed");
        }
        bytes[out++] = static_cast<unsigned char>((nibble(value[i]) << 4U) | nibble(value[i + 1]));
        i += 2;
    }
    if (out != bytes.size()) throw std::invalid_argument("experience ID is malformed");
    return bytes;
}

void check_sqlite(int result, sqlite3* db, std::string_view operation) {
    if (result != SQLITE_OK && result != SQLITE_DONE && result != SQLITE_ROW) {
        throw std::runtime_error(std::string(operation) + ": " + sqlite3_errmsg(db));
    }
}

class Statement final {
public:
    Statement(sqlite3* db, const char* sql) : db_(db) {
        check_sqlite(sqlite3_prepare_v2(db, sql, -1, &statement_, nullptr), db, "prepare statement");
    }
    ~Statement() { sqlite3_finalize(statement_); }
    Statement(const Statement&) = delete;
    Statement& operator=(const Statement&) = delete;

    sqlite3_stmt* get() const noexcept { return statement_; }

private:
    sqlite3* db_{};
    sqlite3_stmt* statement_{};
};

void bind_id(sqlite3* db, sqlite3_stmt* statement, int index, const IdBytes& id) {
    check_sqlite(sqlite3_bind_blob(statement, index, id.data(),
        static_cast<int>(id.size()), SQLITE_TRANSIENT), db, "bind experience ID");
}

void bind_text(sqlite3* db, sqlite3_stmt* statement, int index, const std::string& value) {
    check_sqlite(sqlite3_bind_text(statement, index, value.data(),
        static_cast<int>(value.size()), SQLITE_TRANSIENT), db, "bind text");
}

[[nodiscard]] std::string column_text(sqlite3_stmt* statement, int column) {
    const auto* value = sqlite3_column_text(statement, column);
    const int size = sqlite3_column_bytes(statement, column);
    if (value == nullptr) return {};
    return {reinterpret_cast<const char*>(value), static_cast<std::size_t>(size)};
}

void execute(sqlite3* db, const char* sql) {
    char* error = nullptr;
    const int result = sqlite3_exec(db, sql, nullptr, nullptr, &error);
    if (result != SQLITE_OK) {
        const std::string message = error ? error : sqlite3_errmsg(db);
        sqlite3_free(error);
        throw std::runtime_error("SQLite execution failed: " + message);
    }
}

class Transaction final {
public:
    explicit Transaction(sqlite3* db) : db_(db) { execute(db_, "BEGIN IMMEDIATE"); }
    ~Transaction() {
        if (!committed_) sqlite3_exec(db_, "ROLLBACK", nullptr, nullptr, nullptr);
    }
    void commit() {
        execute(db_, "COMMIT");
        committed_ = true;
    }
private:
    sqlite3* db_{};
    bool committed_{false};
};


[[nodiscard]] std::string ascii_lower(std::string_view value) {
    std::string result;
    result.reserve(value.size());
    for (const unsigned char c : value) {
        result.push_back(static_cast<char>(c < 128 ? std::tolower(c) : c));
    }
    return result;
}

[[nodiscard]] std::vector<std::string> query_terms(std::string_view query) {
    std::vector<std::string> terms;
    std::string current;
    for (const unsigned char c : query) {
        if (std::isalnum(c)) {
            current.push_back(static_cast<char>(c < 128 ? std::tolower(c) : c));
        } else if (!current.empty()) {
            if (current.size() >= 2) terms.push_back(std::move(current));
            current.clear();
        }
    }
    if (current.size() >= 2) terms.push_back(std::move(current));

    std::sort(terms.begin(), terms.end());
    terms.erase(std::unique(terms.begin(), terms.end()), terms.end());
    return terms;
}

[[nodiscard]] std::string like_pattern(const std::string& term) {
    std::string pattern = "%";
    for (const char c : term) {
        if (c == '!' || c == '%' || c == '_') pattern.push_back('!');
        pattern.push_back(c);
    }
    pattern.push_back('%');
    return pattern;
}

[[nodiscard]] double score_experience(
    const Experience& experience,
    const std::vector<std::string>& terms) {
    const std::string content = ascii_lower(experience.content);
    const std::string source = ascii_lower(experience.source_type);
    const std::string provenance = ascii_lower(experience.provenance_ref);
    double score = 0.0;
    for (const auto& term : terms) {
        const auto content_at = content.find(term);
        const auto source_at = source.find(term);
        const auto provenance_at = provenance.find(term);
        if (content_at != std::string::npos) {
            score += 3.0;
            std::size_t position = content_at;
            while ((position = content.find(term, position + term.size())) != std::string::npos) {
                score += 0.25;
            }
        } else if (source_at != std::string::npos || provenance_at != std::string::npos) {
            score += 1.0;
        }
    }
    return score;
}

[[nodiscard]] std::string column_id(sqlite3_stmt* statement, int column) {
    const auto* bytes = static_cast<const unsigned char*>(sqlite3_column_blob(statement, column));
    const int size = sqlite3_column_bytes(statement, column);
    if (bytes == nullptr || size != 16) {
        throw std::runtime_error("stored experience ID is not a 16-byte UUID");
    }
    IdBytes id{};
    std::copy(bytes, bytes + size, id.begin());
    return format_id(id);
}

}  // namespace

ExperienceStore::ExperienceStore(const std::filesystem::path& database_path) {
    const auto parent = database_path.parent_path();
    if (!parent.empty()) std::filesystem::create_directories(parent);

    const int result = sqlite3_open_v2(database_path.string().c_str(), &db_,
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX, nullptr);
    if (result != SQLITE_OK) {
        const std::string message = db_ ? sqlite3_errmsg(db_) : "unable to allocate SQLite handle";
        if (db_) sqlite3_close(db_);
        db_ = nullptr;
        throw std::runtime_error("cannot open experience database: " + message);
    }

    try {
        execute(db_, "PRAGMA foreign_keys = ON");
        execute(db_, R"sql(
            CREATE TABLE IF NOT EXISTS experience_payloads (
                payload_id BLOB PRIMARY KEY CHECK(length(payload_id) = 16),
                payload TEXT NOT NULL
            ) STRICT;
            CREATE TABLE IF NOT EXISTS experiences (
                experience_id BLOB PRIMARY KEY CHECK(length(experience_id) = 16),
                source_type TEXT NOT NULL,
                observed_at_ms INTEGER NOT NULL,
                recorded_at_ms INTEGER NOT NULL,
                content_ref TEXT NOT NULL,
                sensitivity INTEGER NOT NULL CHECK(sensitivity BETWEEN 0 AND 4),
                provenance_ref TEXT NOT NULL,
                retention_state TEXT NOT NULL DEFAULT 'active'
                    CHECK(retention_state IN ('active','archived','pending_deletion',
                                              'deleted_active','backup_expiry_pending')),
                deleted_at_ms INTEGER,
                FOREIGN KEY(experience_id) REFERENCES experience_payloads(payload_id)
            ) STRICT;
            CREATE INDEX IF NOT EXISTS idx_experiences_time
                ON experiences(observed_at_ms DESC);
        )sql");
    } catch (...) {
        sqlite3_close(db_);
        db_ = nullptr;
        throw;
    }
}

ExperienceStore::~ExperienceStore() {
    if (db_) sqlite3_close(db_);
}

Experience ExperienceStore::record(
    std::string source_type,
    std::string content,
    std::string provenance_ref,
    int sensitivity,
    std::optional<std::int64_t> observed_at_ms) {

    if (source_type.empty()) throw std::invalid_argument("source_type must not be empty");
    if (content.empty()) throw std::invalid_argument("experience content must not be empty");
    if (provenance_ref.empty()) throw std::invalid_argument("provenance_ref must not be empty");
    if (sensitivity < 0 || sensitivity > 4) {
        throw std::invalid_argument("sensitivity must be between 0 and 4");
    }

    const IdBytes id_bytes = make_id_bytes();
    const std::string id = format_id(id_bytes);
    const std::int64_t recorded = now_ms();
    const std::int64_t observed = observed_at_ms.value_or(recorded);
    const std::string content_ref = "sqlite://experience_payloads/" + id;

    Transaction transaction(db_);
    {
        Statement payload(db_, "INSERT INTO experience_payloads(payload_id, payload) VALUES(?1, ?2)");
        bind_id(db_, payload.get(), 1, id_bytes);
        bind_text(db_, payload.get(), 2, content);
        check_sqlite(sqlite3_step(payload.get()), db_, "insert experience payload");
    }
    {
        Statement experience(db_, R"sql(
            INSERT INTO experiences(
                experience_id, source_type, observed_at_ms, recorded_at_ms,
                content_ref, sensitivity, provenance_ref, retention_state
            ) VALUES(?1, ?2, ?3, ?4, ?5, ?6, ?7, 'active')
        )sql");
        bind_id(db_, experience.get(), 1, id_bytes);
        bind_text(db_, experience.get(), 2, source_type);
        check_sqlite(sqlite3_bind_int64(experience.get(), 3, observed), db_, "bind observed timestamp");
        check_sqlite(sqlite3_bind_int64(experience.get(), 4, recorded), db_, "bind recorded timestamp");
        bind_text(db_, experience.get(), 5, content_ref);
        check_sqlite(sqlite3_bind_int(experience.get(), 6, sensitivity), db_, "bind sensitivity");
        bind_text(db_, experience.get(), 7, provenance_ref);
        check_sqlite(sqlite3_step(experience.get()), db_, "insert experience");
    }
    transaction.commit();

    return Experience{id, std::move(source_type), std::move(content),
        std::move(provenance_ref), observed, recorded, sensitivity};
}

std::optional<Experience> ExperienceStore::get(const std::string& id) const {
    const IdBytes id_bytes = parse_id(id);
    Statement query(db_, R"sql(
        SELECT e.source_type, p.payload, e.provenance_ref,
               e.observed_at_ms, e.recorded_at_ms, e.sensitivity
        FROM experiences AS e
        JOIN experience_payloads AS p ON p.payload_id = e.experience_id
        WHERE e.experience_id = ?1 AND e.retention_state = 'active'
    )sql");
    bind_id(db_, query.get(), 1, id_bytes);
    const int result = sqlite3_step(query.get());
    if (result == SQLITE_DONE) return std::nullopt;
    check_sqlite(result, db_, "retrieve experience");

    return Experience{
        id,
        column_text(query.get(), 0),
        column_text(query.get(), 1),
        column_text(query.get(), 2),
        sqlite3_column_int64(query.get(), 3),
        sqlite3_column_int64(query.get(), 4),
        sqlite3_column_int(query.get(), 5)
    };
}


std::vector<ExperienceMatch> ExperienceStore::search(
    const std::string& query_text,
    std::size_t limit) const {
    if (limit == 0 || limit > 100) {
        throw std::invalid_argument("experience search limit must be between 1 and 100");
    }
    if (query_text.size() > 512) {
        throw std::invalid_argument("experience search query must not exceed 512 bytes");
    }
    const auto terms = query_terms(query_text);
    if (terms.empty()) {
        throw std::invalid_argument("experience search query must contain a term of at least two characters");
    }

    // Candidate selection is performed in SQLite with bound LIKE patterns.
    // Ranking is deterministic in-process; at most 500 recent lexical candidates
    // are scored per query to keep retrieval bounded on local devices.
    std::string sql = R"sql(
        SELECT e.experience_id, e.source_type, p.payload, e.provenance_ref,
               e.observed_at_ms, e.recorded_at_ms, e.sensitivity
        FROM experiences AS e
        JOIN experience_payloads AS p ON p.payload_id = e.experience_id
        WHERE e.retention_state = 'active' AND (
    )sql";
    int parameter = 1;
    for (std::size_t i = 0; i < terms.size(); ++i) {
        if (i != 0) sql += " OR ";
        sql += "(p.payload LIKE ?" + std::to_string(parameter++) +
               " ESCAPE '!' OR e.source_type LIKE ?" +
               std::to_string(parameter++) +
               " ESCAPE '!' OR e.provenance_ref LIKE ?" +
               std::to_string(parameter++) + " ESCAPE '!')";
    }
    sql += ") ORDER BY e.observed_at_ms DESC, e.experience_id ASC LIMIT 500";

    Statement statement(db_, sql.c_str());
    int bind_index = 1;
    for (const auto& term : terms) {
        const auto pattern = like_pattern(term);
        for (int field = 0; field < 3; ++field) {
            check_sqlite(sqlite3_bind_text(statement.get(), bind_index++, pattern.c_str(),
                static_cast<int>(pattern.size()), SQLITE_TRANSIENT), db_, "bind search term");
        }
    }

    std::vector<ExperienceMatch> matches;
    for (;;) {
        const int result = sqlite3_step(statement.get());
        if (result == SQLITE_DONE) break;
        check_sqlite(result, db_, "search experiences");
        Experience experience{
            column_id(statement.get(), 0),
            column_text(statement.get(), 1),
            column_text(statement.get(), 2),
            column_text(statement.get(), 3),
            sqlite3_column_int64(statement.get(), 4),
            sqlite3_column_int64(statement.get(), 5),
            sqlite3_column_int(statement.get(), 6)
        };
        const double relevance = score_experience(experience, terms);
        if (relevance > 0.0) {
            matches.push_back(ExperienceMatch{std::move(experience), relevance});
        }
    }

    std::sort(matches.begin(), matches.end(),
        [](const ExperienceMatch& left, const ExperienceMatch& right) {
            if (left.relevance != right.relevance) return left.relevance > right.relevance;
            if (left.experience.observed_at_ms != right.experience.observed_at_ms) {
                return left.experience.observed_at_ms > right.experience.observed_at_ms;
            }
            return left.experience.id < right.experience.id;
        });
    if (matches.size() > limit) matches.resize(limit);
    return matches;
}

}  // namespace aurions
