#include "aurions/representation_store.hpp"

#include <sqlite3.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
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
        result.push_back(hex[(bytes[i] >> 4U) & 0x0fU]);
        result.push_back(hex[bytes[i] & 0x0fU]);
    }
    return result;
}

IdBytes parse_id(std::string_view value) {
    if (value.size() != 36) throw std::invalid_argument("representation ID must be a UUID");
    IdBytes bytes{};
    std::size_t out = 0;
    auto nibble = [](char c) -> unsigned char {
        if (c >= '0' && c <= '9') return static_cast<unsigned char>(c - '0');
        if (c >= 'a' && c <= 'f') return static_cast<unsigned char>(c - 'a' + 10);
        if (c >= 'A' && c <= 'F') return static_cast<unsigned char>(c - 'A' + 10);
        throw std::invalid_argument("representation ID contains a non-hexadecimal character");
    };
    for (std::size_t i = 0; i < value.size();) {
        if (i == 8 || i == 13 || i == 18 || i == 23) {
            if (value[i] != '-') throw std::invalid_argument("representation ID is malformed");
            ++i;
            continue;
        }
        if (out >= bytes.size() || i + 1 >= value.size())
            throw std::invalid_argument("representation ID is malformed");
        bytes[out++] = static_cast<unsigned char>(
            (nibble(value[i]) << 4U) | nibble(value[i + 1]));
        i += 2;
    }
    if (out != bytes.size()) throw std::invalid_argument("representation ID is malformed");
    return bytes;
}

void check(int rc, sqlite3* db, std::string_view operation) {
    if (rc != SQLITE_OK && rc != SQLITE_DONE && rc != SQLITE_ROW)
        throw std::runtime_error(std::string(operation) + ": " + sqlite3_errmsg(db));
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

std::string column_id(sqlite3_stmt* stmt, int column) {
    const auto* data = static_cast<const unsigned char*>(sqlite3_column_blob(stmt, column));
    const int size = sqlite3_column_bytes(stmt, column);
    if (!data || size != 16) throw std::runtime_error("stored representation UUID is malformed");
    IdBytes bytes{};
    std::copy(data, data + size, bytes.begin());
    return format_id(bytes);
}

void execute(sqlite3* db, const char* sql) {
    char* error = nullptr;
    const int rc = sqlite3_exec(db, sql, nullptr, nullptr, &error);
    if (rc != SQLITE_OK) {
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
    bool committed_{};
};

Representation read_row(sqlite3_stmt* stmt) {
    return Representation{
        column_id(stmt, 0), column_id(stmt, 1), column_text(stmt, 2),
        column_text(stmt, 3), column_text(stmt, 4), column_text(stmt, 5),
        sqlite3_column_int64(stmt, 6)
    };
}

}  // namespace

RepresentationStore::RepresentationStore(const std::filesystem::path& database_path) {
    const auto parent = database_path.parent_path();
    if (!parent.empty()) std::filesystem::create_directories(parent);

    const int rc = sqlite3_open_v2(database_path.string().c_str(), &db_,
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX, nullptr);
    if (rc != SQLITE_OK) {
        const std::string message = db_ ? sqlite3_errmsg(db_) : "unable to allocate SQLite handle";
        if (db_) sqlite3_close(db_);
        db_ = nullptr;
        throw std::runtime_error("cannot open representation database: " + message);
    }

    try {
        execute(db_, "PRAGMA foreign_keys=ON");
        check(sqlite3_busy_timeout(db_, 5000), db_, "configure SQLite busy timeout");
        execute(db_, R"sql(
            CREATE TABLE IF NOT EXISTS representations (
              representation_id BLOB PRIMARY KEY CHECK(length(representation_id)=16),
              experience_id BLOB NOT NULL REFERENCES experiences(experience_id),
              representation_type TEXT NOT NULL,
              content_json TEXT NOT NULL CHECK(json_valid(content_json)),
              method TEXT NOT NULL,
              uncertainty_json TEXT NOT NULL CHECK(json_valid(uncertainty_json)),
              created_at_ms INTEGER NOT NULL
            ) STRICT;
            CREATE INDEX IF NOT EXISTS idx_representations_experience
              ON representations(experience_id,created_at_ms DESC);
        )sql");
    } catch (...) {
        sqlite3_close(db_);
        db_ = nullptr;
        throw;
    }
}

RepresentationStore::~RepresentationStore() {
    if (db_) sqlite3_close(db_);
}

Representation RepresentationStore::record(
    const std::string& experience_id,
    std::string representation_type,
    std::string content_json,
    std::string method,
    std::string uncertainty_json) {
    const IdBytes experience_bytes = parse_id(experience_id);
    if (representation_type.empty() || representation_type.size() > 128)
        throw std::invalid_argument("representation_type must contain 1-128 bytes");
    if (method.empty() || method.size() > 512)
        throw std::invalid_argument("representation method must contain 1-512 bytes");
    if (content_json.empty() || content_json.size() > 65536)
        throw std::invalid_argument("representation content JSON must contain 1-65536 bytes");
    if (uncertainty_json.empty() || uncertainty_json.size() > 8192)
        throw std::invalid_argument("uncertainty JSON must contain 1-8192 bytes");

    const IdBytes representation_bytes = make_id();
    const auto created = now_ms();

    Transaction transaction(db_);
    {
        Statement active(db_, "SELECT 1 FROM experiences WHERE experience_id=?1 AND retention_state='active'");
        bind_id(db_, active.get(), 1, experience_bytes);
        const int rc = sqlite3_step(active.get());
        if (rc == SQLITE_DONE) throw std::runtime_error("active source experience not found");
        check(rc, db_, "validate representation source experience");
    }
    {
        Statement insert(db_, R"sql(
            INSERT INTO representations(
                representation_id,experience_id,representation_type,content_json,
                method,uncertainty_json,created_at_ms
            ) VALUES(?1,?2,?3,?4,?5,?6,?7)
        )sql");
        bind_id(db_, insert.get(), 1, representation_bytes);
        bind_id(db_, insert.get(), 2, experience_bytes);
        bind_text(db_, insert.get(), 3, representation_type);
        bind_text(db_, insert.get(), 4, content_json);
        bind_text(db_, insert.get(), 5, method);
        bind_text(db_, insert.get(), 6, uncertainty_json);
        check(sqlite3_bind_int64(insert.get(), 7, created), db_, "bind created timestamp");
        check(sqlite3_step(insert.get()), db_, "insert representation");
    }
    transaction.commit();
    return Representation{
        format_id(representation_bytes), experience_id, std::move(representation_type),
        std::move(content_json), std::move(method), std::move(uncertainty_json), created
    };
}

std::optional<Representation> RepresentationStore::get(const std::string& id) const {
    const IdBytes bytes = parse_id(id);
    Statement query(db_, R"sql(
        SELECT r.representation_id,r.experience_id,r.representation_type,r.content_json,
               r.method,r.uncertainty_json,r.created_at_ms
        FROM representations r JOIN experiences e ON e.experience_id=r.experience_id
        WHERE r.representation_id=?1 AND e.retention_state='active'
    )sql");
    bind_id(db_, query.get(), 1, bytes);
    const int rc = sqlite3_step(query.get());
    if (rc == SQLITE_DONE) return std::nullopt;
    check(rc, db_, "retrieve representation");
    return read_row(query.get());
}

std::vector<Representation> RepresentationStore::list_for_experience(
    const std::string& experience_id, std::size_t limit) const {
    const IdBytes bytes = parse_id(experience_id);
    if (limit == 0 || limit > 100)
        throw std::invalid_argument("representation list limit must be between 1 and 100");
    Statement query(db_, R"sql(
        SELECT r.representation_id,r.experience_id,r.representation_type,r.content_json,
               r.method,r.uncertainty_json,r.created_at_ms
        FROM representations r JOIN experiences e ON e.experience_id=r.experience_id
        WHERE r.experience_id=?1 AND e.retention_state='active'
        ORDER BY r.created_at_ms DESC,r.representation_id ASC LIMIT ?2
    )sql");
    bind_id(db_, query.get(), 1, bytes);
    check(sqlite3_bind_int64(query.get(), 2, static_cast<std::int64_t>(limit)),
          db_, "bind representation list limit");
    std::vector<Representation> result;
    for (;;) {
        const int rc = sqlite3_step(query.get());
        if (rc == SQLITE_DONE) break;
        check(rc, db_, "list representations");
        result.push_back(read_row(query.get()));
    }
    return result;
}

}  // namespace aurions
