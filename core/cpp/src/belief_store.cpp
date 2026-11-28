#include "aurions/belief_store.hpp"

#include <sqlite3.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <random>
#include <sstream>
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

IdBytes parse_id(std::string_view value) {
    if (value.size() != 36) throw std::invalid_argument("ID must be a UUID");
    IdBytes bytes{};
    auto nibble = [](char c) -> unsigned char {
        if (c >= '0' && c <= '9') return static_cast<unsigned char>(c - '0');
        if (c >= 'a' && c <= 'f') return static_cast<unsigned char>(c - 'a' + 10);
        if (c >= 'A' && c <= 'F') return static_cast<unsigned char>(c - 'A' + 10);
        throw std::invalid_argument("ID contains a non-hexadecimal character");
    };
    std::size_t out = 0;
    for (std::size_t i = 0; i < value.size();) {
        if (i == 8 || i == 13 || i == 18 || i == 23) {
            if (value[i++] != '-') throw std::invalid_argument("ID is not a UUID");
            continue;
        }
        if (out >= bytes.size() || i + 1 >= value.size())
            throw std::invalid_argument("ID is malformed");
        bytes[out++] = static_cast<unsigned char>((nibble(value[i]) << 4U) | nibble(value[i + 1]));
        i += 2;
    }
    if (out != bytes.size()) throw std::invalid_argument("ID is malformed");
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
    ~Transaction() { if (!committed_) sqlite3_exec(db_, "ROLLBACK", nullptr, nullptr, nullptr); }
    void commit() { exec(db_, "COMMIT"); committed_ = true; }
private:
    sqlite3* db_{};
    bool committed_{};
};

void bind_id(sqlite3* db, sqlite3_stmt* stmt, int index, const IdBytes& id) {
    check(sqlite3_bind_blob(stmt, index, id.data(), static_cast<int>(id.size()), SQLITE_TRANSIENT),
          db, "bind UUID");
}
void bind_text(sqlite3* db, sqlite3_stmt* stmt, int index, const std::string& value) {
    check(sqlite3_bind_text(stmt, index, value.data(), static_cast<int>(value.size()), SQLITE_TRANSIENT),
          db, "bind text");
}
std::string column_text(sqlite3_stmt* stmt, int column) {
    const auto* value = sqlite3_column_text(stmt, column);
    const int size = sqlite3_column_bytes(stmt, column);
    return value ? std::string(reinterpret_cast<const char*>(value), static_cast<std::size_t>(size))
                 : std::string{};
}
std::string column_id(sqlite3_stmt* stmt, int column) {
    const auto* bytes = static_cast<const unsigned char*>(sqlite3_column_blob(stmt, column));
    if (!bytes || sqlite3_column_bytes(stmt, column) != 16)
        throw std::runtime_error("stored UUID is malformed");
    IdBytes id{};
    std::copy(bytes, bytes + id.size(), id.begin());
    return format_id(id);
}

std::string status_for(double confidence) {
    if (confidence >= 0.9) return "supported";
    if (confidence <= 0.1) return "disputed";
    return "provisional";
}

double updated_confidence(double prior, double reliability, double relevance,
                          const std::string& stance) {
    constexpr double epsilon = 1e-9;
    const double p = std::clamp(prior, epsilon, 1.0 - epsilon);
    double log_odds = std::log(p / (1.0 - p));
    if (stance != "contextualizes" && relevance > 0.0) {
        const double evidence_weight = std::log(reliability / (1.0 - reliability)) * relevance;
        log_odds += stance == "supports" ? evidence_weight : -evidence_weight;
    }
    log_odds = std::clamp(log_odds, -20.0, 20.0);
    return 1.0 / (1.0 + std::exp(-log_odds));
}

std::vector<std::string> belief_query_terms(std::string_view query) {
    std::vector<std::string> terms;
    std::string current;
    for (const unsigned char ch : query) {
        if (std::isalnum(ch)) {
            current.push_back(static_cast<char>(ch < 128 ? std::tolower(ch) : ch));
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

std::string belief_like_pattern(const std::string& term) {
    std::string pattern = "%";
    for (const char ch : term) {
        if (ch == '!' || ch == '%' || ch == '_') pattern.push_back('!');
        pattern.push_back(ch);
    }
    pattern.push_back('%');
    return pattern;
}

double belief_relevance(const BeliefSnapshot& belief,
                        const std::vector<std::string>& terms) {
    std::string text = belief.proposition + " " + belief.domain;
    for (char& ch : text) {
        const auto value = static_cast<unsigned char>(ch);
        if (value < 128) ch = static_cast<char>(std::tolower(value));
    }
    double score = 0.0;
    for (const auto& term : terms) {
        if (text.find(term) != std::string::npos) score += 1.0;
    }
    return score;
}

BeliefSnapshot load_snapshot(sqlite3* db, const IdBytes& id) {
    BeliefSnapshot result;
    {
        Statement query(db, R"sql(
            SELECT k.proposition, k.domain
            FROM beliefs b JOIN knowledge_items k ON k.knowledge_id=b.knowledge_id
            WHERE b.belief_id=?1 AND k.status='active'
        )sql");
        bind_id(db, query.get(), 1, id);
        const int rc = sqlite3_step(query.get());
        if (rc == SQLITE_DONE) throw std::runtime_error("belief not found");
        check(rc, db, "read belief");
        result.id = format_id(id);
        result.proposition = column_text(query.get(), 0);
        result.domain = column_text(query.get(), 1);
    }
    Statement revisions(db, R"sql(
        SELECT r.revision_number, r.confidence, r.epistemic_status,
               r.revision_reason, r.created_at_ms,
               (SELECT count(*) FROM belief_revision_evidence x WHERE x.revision_id=r.revision_id),
               coalesce(e.source_ref,''), coalesce(x.stance,''), 
               coalesce(json_extract(e.reliability_json,'$.reliability'),0.0),
               coalesce(x.relevance,0.0), coalesce(ex.sensitivity,-1)
        FROM belief_revisions r
        LEFT JOIN belief_revision_evidence x ON x.revision_id=r.revision_id
        LEFT JOIN evidence_items e ON e.evidence_id=x.evidence_id
        LEFT JOIN experiences ex ON ex.experience_id=e.source_experience_id
        WHERE r.belief_id=?1 ORDER BY r.revision_number
    )sql");
    bind_id(db, revisions.get(), 1, id);
    for (;;) {
        const int rc = sqlite3_step(revisions.get());
        if (rc == SQLITE_DONE) break;
        check(rc, db, "read belief revisions");
        result.revisions.push_back(BeliefRevision{
            sqlite3_column_int(revisions.get(), 0),
            sqlite3_column_double(revisions.get(), 1),
            column_text(revisions.get(), 2),
            column_text(revisions.get(), 3),
            sqlite3_column_int64(revisions.get(), 4),
            sqlite3_column_int(revisions.get(), 5),
            column_text(revisions.get(), 6),
            column_text(revisions.get(), 7),
            sqlite3_column_double(revisions.get(), 8),
            sqlite3_column_double(revisions.get(), 9),
            sqlite3_column_int(revisions.get(), 10)
        });
    }
    if (result.revisions.empty()) throw std::runtime_error("belief has no revision");
    return result;
}

}  // namespace

BeliefStore::BeliefStore(const std::filesystem::path& database_path) {
    const auto parent = database_path.parent_path();
    if (!parent.empty()) std::filesystem::create_directories(parent);
    const int rc = sqlite3_open_v2(database_path.string().c_str(), &db_,
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX, nullptr);
    if (rc != SQLITE_OK) {
        const std::string message = db_ ? sqlite3_errmsg(db_) : "unable to allocate SQLite handle";
        if (db_) sqlite3_close(db_);
        db_ = nullptr;
        throw std::runtime_error("cannot open belief database: " + message);
    }
    try {
        exec(db_, "PRAGMA foreign_keys=ON");
        check(sqlite3_busy_timeout(db_, 5000), db_, "configure SQLite busy timeout");
        exec(db_, R"sql(
            CREATE TABLE IF NOT EXISTS knowledge_items (
              knowledge_id BLOB PRIMARY KEY CHECK(length(knowledge_id)=16),
              proposition TEXT NOT NULL, domain TEXT NOT NULL,
              status TEXT NOT NULL CHECK(status IN ('active','superseded','withdrawn')),
              created_at_ms INTEGER NOT NULL, updated_at_ms INTEGER NOT NULL
            ) STRICT;
            CREATE TABLE IF NOT EXISTS beliefs (
              belief_id BLOB PRIMARY KEY CHECK(length(belief_id)=16),
              knowledge_id BLOB NOT NULL REFERENCES knowledge_items(knowledge_id),
              created_at_ms INTEGER NOT NULL, updated_at_ms INTEGER NOT NULL
            ) STRICT;
            CREATE TABLE IF NOT EXISTS belief_revisions (
              revision_id BLOB PRIMARY KEY CHECK(length(revision_id)=16),
              belief_id BLOB NOT NULL REFERENCES beliefs(belief_id),
              revision_number INTEGER NOT NULL CHECK(revision_number>0),
              previous_revision_id BLOB REFERENCES belief_revisions(revision_id),
              epistemic_status TEXT NOT NULL CHECK(epistemic_status IN
                ('provisional','supported','consolidated','disputed','withdrawn')),
              confidence REAL CHECK(confidence IS NULL OR confidence BETWEEN 0.0 AND 1.0),
              revision_reason TEXT NOT NULL, created_at_ms INTEGER NOT NULL,
              UNIQUE(belief_id,revision_number), UNIQUE(belief_id,revision_id)
            ) STRICT;
            CREATE INDEX IF NOT EXISTS idx_belief_revision_order
              ON belief_revisions(belief_id,revision_number DESC);
            CREATE TABLE IF NOT EXISTS evidence_items (
              evidence_id BLOB PRIMARY KEY CHECK(length(evidence_id)=16),
              source_experience_id BLOB REFERENCES experiences(experience_id),
              source_ref TEXT NOT NULL, evidence_type TEXT NOT NULL,
              observed_at_ms INTEGER, recorded_at_ms INTEGER NOT NULL,
              reliability_json TEXT CHECK(reliability_json IS NULL OR json_valid(reliability_json))
            ) STRICT;
            CREATE TABLE IF NOT EXISTS belief_revision_evidence (
              revision_id BLOB NOT NULL REFERENCES belief_revisions(revision_id),
              evidence_id BLOB NOT NULL REFERENCES evidence_items(evidence_id),
              stance TEXT NOT NULL CHECK(stance IN ('supports','contradicts','contextualizes')),
              relevance REAL CHECK(relevance IS NULL OR relevance BETWEEN 0.0 AND 1.0),
              PRIMARY KEY(revision_id,evidence_id,stance)
            ) STRICT;
        )sql");
    } catch (...) {
        sqlite3_close(db_);
        db_ = nullptr;
        throw;
    }
}

BeliefStore::~BeliefStore() {
    if (db_) sqlite3_close(db_);
}

BeliefSnapshot BeliefStore::create(const std::string& domain,
                                   const std::string& proposition,
                                   double prior_confidence) {
    if (domain.empty() || proposition.empty())
        throw std::invalid_argument("belief domain and proposition must not be empty");
    if (!std::isfinite(prior_confidence) || prior_confidence <= 0.0 || prior_confidence >= 1.0)
        throw std::invalid_argument("prior confidence must be greater than 0 and less than 1");
    const IdBytes knowledge_id = make_id();
    const IdBytes belief_id = make_id();
    const IdBytes revision_id = make_id();
    const auto now = now_ms();
    Transaction transaction(db_);
    {
        Statement insert(db_, "INSERT INTO knowledge_items VALUES(?1,?2,?3,'active',?4,?4)");
        bind_id(db_, insert.get(), 1, knowledge_id);
        bind_text(db_, insert.get(), 2, proposition);
        bind_text(db_, insert.get(), 3, domain);
        check(sqlite3_bind_int64(insert.get(), 4, now), db_, "bind timestamp");
        check(sqlite3_step(insert.get()), db_, "insert knowledge");
    }
    {
        Statement insert(db_, "INSERT INTO beliefs VALUES(?1,?2,?3,?3)");
        bind_id(db_, insert.get(), 1, belief_id);
        bind_id(db_, insert.get(), 2, knowledge_id);
        check(sqlite3_bind_int64(insert.get(), 3, now), db_, "bind timestamp");
        check(sqlite3_step(insert.get()), db_, "insert belief");
    }
    {
        Statement insert(db_, R"sql(
            INSERT INTO belief_revisions(
                revision_id,belief_id,revision_number,previous_revision_id,
                epistemic_status,confidence,revision_reason,created_at_ms
            ) VALUES(?1,?2,1,NULL,'provisional',?3,'initial prior',?4)
        )sql");
        bind_id(db_, insert.get(), 1, revision_id);
        bind_id(db_, insert.get(), 2, belief_id);
        check(sqlite3_bind_double(insert.get(), 3, prior_confidence), db_, "bind confidence");
        check(sqlite3_bind_int64(insert.get(), 4, now), db_, "bind timestamp");
        check(sqlite3_step(insert.get()), db_, "insert initial revision");
    }
    transaction.commit();
    return load_snapshot(db_, belief_id);
}

BeliefSnapshot BeliefStore::add_evidence(const std::string& belief_id_text,
                                         const std::string& experience_id_text,
                                         const std::string& stance,
                                         double reliability,
                                         double relevance) {
    if (stance != "supports" && stance != "contradicts" && stance != "contextualizes")
        throw std::invalid_argument("stance must be supports, contradicts, or contextualizes");
    if (!std::isfinite(reliability) || reliability < 0.5 || reliability >= 1.0)
        throw std::invalid_argument("reliability must be at least 0.5 and less than 1");
    if (!std::isfinite(relevance) || relevance < 0.0 || relevance > 1.0)
        throw std::invalid_argument("relevance must be between 0 and 1");

    const IdBytes belief_id = parse_id(belief_id_text);
    const IdBytes experience_id = parse_id(experience_id_text);
    Transaction transaction(db_);

    std::string source_ref;
    std::int64_t observed_at{};
    {
        Statement query(db_, "SELECT provenance_ref,observed_at_ms FROM experiences WHERE experience_id=?1 AND retention_state='active'");
        bind_id(db_, query.get(), 1, experience_id);
        const int rc = sqlite3_step(query.get());
        if (rc == SQLITE_DONE) throw std::invalid_argument("active source experience not found");
        check(rc, db_, "read source experience");
        source_ref = column_text(query.get(), 0);
        observed_at = sqlite3_column_int64(query.get(), 1);
    }
    {
        Statement duplicate(db_, R"sql(
            SELECT 1 FROM belief_revision_evidence x
            JOIN belief_revisions r ON r.revision_id=x.revision_id
            JOIN evidence_items e ON e.evidence_id=x.evidence_id
            WHERE r.belief_id=?1 AND e.source_experience_id=?2 LIMIT 1
        )sql");
        bind_id(db_, duplicate.get(), 1, belief_id);
        bind_id(db_, duplicate.get(), 2, experience_id);
        const int duplicate_result = sqlite3_step(duplicate.get());
        if (duplicate_result == SQLITE_ROW)
            throw std::invalid_argument("experience has already been used as evidence for this belief");
        check(duplicate_result, db_, "check duplicate belief evidence");
    }

    int previous_number{};
    double prior{};
    IdBytes previous_revision{};
    {
        Statement latest(db_, R"sql(
            SELECT revision_id,revision_number,confidence FROM belief_revisions
            WHERE belief_id=?1 ORDER BY revision_number DESC LIMIT 1
        )sql");
        bind_id(db_, latest.get(), 1, belief_id);
        const int rc = sqlite3_step(latest.get());
        if (rc == SQLITE_DONE) throw std::invalid_argument("belief not found");
        check(rc, db_, "read latest belief revision");
        const auto* bytes = static_cast<const unsigned char*>(sqlite3_column_blob(latest.get(), 0));
        if (!bytes || sqlite3_column_bytes(latest.get(), 0) != 16)
            throw std::runtime_error("latest belief revision ID is malformed");
        std::copy(bytes, bytes + previous_revision.size(), previous_revision.begin());
        previous_number = sqlite3_column_int(latest.get(), 1);
        prior = sqlite3_column_double(latest.get(), 2);
    }

    const double posterior = updated_confidence(prior, reliability, relevance, stance);
    const IdBytes evidence_id = make_id();
    const IdBytes revision_id = make_id();
    const auto now = now_ms();
    std::ostringstream reliability_json;
    reliability_json << std::setprecision(17) << "{\"reliability\":" << reliability << "}";

    {
        Statement insert(db_, R"sql(
            INSERT INTO evidence_items(
                evidence_id,source_experience_id,source_ref,evidence_type,
                observed_at_ms,recorded_at_ms,reliability_json
            ) VALUES(?1,?2,?3,'experience',?4,?5,?6)
        )sql");
        bind_id(db_, insert.get(), 1, evidence_id);
        bind_id(db_, insert.get(), 2, experience_id);
        bind_text(db_, insert.get(), 3, source_ref);
        check(sqlite3_bind_int64(insert.get(), 4, observed_at), db_, "bind observed timestamp");
        check(sqlite3_bind_int64(insert.get(), 5, now), db_, "bind recorded timestamp");
        bind_text(db_, insert.get(), 6, reliability_json.str());
        check(sqlite3_step(insert.get()), db_, "insert evidence");
    }
    {
        Statement insert(db_, R"sql(
            INSERT INTO belief_revisions(
                revision_id,belief_id,revision_number,previous_revision_id,
                epistemic_status,confidence,revision_reason,created_at_ms
            ) VALUES(?1,?2,?3,?4,?5,?6,?7,?8)
        )sql");
        bind_id(db_, insert.get(), 1, revision_id);
        bind_id(db_, insert.get(), 2, belief_id);
        check(sqlite3_bind_int(insert.get(), 3, previous_number + 1), db_, "bind revision number");
        bind_id(db_, insert.get(), 4, previous_revision);
        bind_text(db_, insert.get(), 5, status_for(posterior));
        check(sqlite3_bind_double(insert.get(), 6, posterior), db_, "bind confidence");
        bind_text(db_, insert.get(), 7, "Bayesian evidence update: " + stance);
        check(sqlite3_bind_int64(insert.get(), 8, now), db_, "bind timestamp");
        check(sqlite3_step(insert.get()), db_, "insert belief revision");
    }
    {
        Statement link(db_, R"sql(
            INSERT INTO belief_revision_evidence(revision_id,evidence_id,stance,relevance)
            VALUES(?1,?2,?3,?4)
        )sql");
        bind_id(db_, link.get(), 1, revision_id);
        bind_id(db_, link.get(), 2, evidence_id);
        bind_text(db_, link.get(), 3, stance);
        check(sqlite3_bind_double(link.get(), 4, relevance), db_, "bind relevance");
        check(sqlite3_step(link.get()), db_, "link belief evidence");
    }
    {
        Statement update(db_, "UPDATE beliefs SET updated_at_ms=?1 WHERE belief_id=?2");
        check(sqlite3_bind_int64(update.get(), 1, now), db_, "bind timestamp");
        bind_id(db_, update.get(), 2, belief_id);
        check(sqlite3_step(update.get()), db_, "update belief timestamp");
    }
    {
        Statement update(db_, "UPDATE knowledge_items SET updated_at_ms=?1 WHERE knowledge_id=(SELECT knowledge_id FROM beliefs WHERE belief_id=?2)");
        check(sqlite3_bind_int64(update.get(), 1, now), db_, "bind timestamp");
        bind_id(db_, update.get(), 2, belief_id);
        check(sqlite3_step(update.get()), db_, "update knowledge timestamp");
    }

    transaction.commit();
    return load_snapshot(db_, belief_id);
}

BeliefSnapshot BeliefStore::get(const std::string& belief_id_text) const {
    return load_snapshot(db_, parse_id(belief_id_text));
}

std::vector<BeliefSnapshot> BeliefStore::search(
    const std::string& query_text, std::size_t limit) const {
    if (query_text.size() > 4096)
        throw std::invalid_argument("belief search query must not exceed 4096 bytes");
    if (limit == 0 || limit > 50)
        throw std::invalid_argument("belief search limit must be between 1 and 50");
    const auto terms = belief_query_terms(query_text);
    if (terms.empty())
        throw std::invalid_argument("belief search query must contain a term of at least two characters");

    std::string sql = R"sql(
        SELECT b.belief_id
        FROM beliefs b JOIN knowledge_items k ON k.knowledge_id=b.knowledge_id
        WHERE k.status='active' AND (
    )sql";
    int parameter = 1;
    for (std::size_t i = 0; i < terms.size(); ++i) {
        if (i != 0) sql += " OR ";
        const int proposition_parameter = parameter++;
        const int domain_parameter = parameter++;
        sql += "(k.proposition LIKE ?" + std::to_string(proposition_parameter) +
               " ESCAPE '!' OR k.domain LIKE ?" + std::to_string(domain_parameter) +
               " ESCAPE '!')";
    }
    sql += ") ORDER BY b.updated_at_ms DESC, b.belief_id ASC LIMIT 200";

    Statement statement(db_, sql.c_str());
    int bind_index = 1;
    for (const auto& term : terms) {
        const auto pattern = belief_like_pattern(term);
        bind_text(db_, statement.get(), bind_index++, pattern);
        bind_text(db_, statement.get(), bind_index++, pattern);
    }

    std::vector<BeliefSnapshot> matches;
    for (;;) {
        const int rc = sqlite3_step(statement.get());
        if (rc == SQLITE_DONE) break;
        check(rc, db_, "search beliefs");
        const auto* bytes = static_cast<const unsigned char*>(sqlite3_column_blob(statement.get(), 0));
        if (!bytes || sqlite3_column_bytes(statement.get(), 0) != 16)
            throw std::runtime_error("stored belief ID is malformed");
        IdBytes id{};
        std::copy(bytes, bytes + id.size(), id.begin());
        auto belief = load_snapshot(db_, id);
        belief.relevance = belief_relevance(belief, terms);
        matches.push_back(std::move(belief));
    }

    std::sort(matches.begin(), matches.end(), [](const auto& left, const auto& right) {
        if (left.relevance != right.relevance) return left.relevance > right.relevance;
        return left.id < right.id;
    });
    if (matches.size() > limit) matches.resize(limit);
    return matches;
}

}  // namespace aurions
