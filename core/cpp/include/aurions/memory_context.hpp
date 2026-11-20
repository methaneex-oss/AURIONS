#pragma once

#include "aurions/experience_store.hpp"

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace aurions {

struct MemoryContextItem {
    Experience experience;
    double relevance{};
    std::size_t estimated_bytes{};
};

struct MemoryContext {
    std::string query;
    std::int64_t assembled_at_ms{};
    std::vector<MemoryContextItem> evidence;
    std::size_t payload_bytes{};
    std::size_t omitted_count{};
};

// Builds a bounded, provenance-preserving evidence packet for a cognitive
// consumer. It does not decide truth or silently convert retrieved records
// into beliefs; downstream reasoning must evaluate the evidence.
class MemoryContextBuilder final {
public:
    explicit MemoryContextBuilder(const ExperienceStore& store) noexcept;

    [[nodiscard]] MemoryContext build(
        const std::string& query,
        std::size_t max_items = 8,
        std::size_t max_bytes = 16 * 1024) const;

private:
    const ExperienceStore& store_;
};

}  // namespace aurions
