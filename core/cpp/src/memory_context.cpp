#include "aurions/memory_context.hpp"

#include <chrono>
#include <stdexcept>
#include <utility>

namespace aurions {
namespace {

[[nodiscard]] std::int64_t current_time_ms() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
}

[[nodiscard]] std::size_t estimate_item_bytes(const Experience& experience) {
    // Includes conservative allowance for field names, JSON delimiters and
    // scalar metadata. This is a payload budget, not an exact allocator size.
    return experience.id.size() + experience.source_type.size() +
        experience.content.size() + experience.provenance_ref.size() + 128;
}

}  // namespace

MemoryContextBuilder::MemoryContextBuilder(const ExperienceStore& store) noexcept
    : store_(store) {}

MemoryContext MemoryContextBuilder::build(
    const std::string& query,
    std::size_t max_items,
    std::size_t max_bytes) const {
    if (max_items == 0 || max_items > 50) {
        throw std::invalid_argument("memory context max_items must be between 1 and 50");
    }
    if (max_bytes < 256 || max_bytes > 64 * 1024) {
        throw std::invalid_argument("memory context max_bytes must be between 256 and 65536");
    }

    const auto candidates = store_.search(query, 100);
    MemoryContext context;
    context.query = query;
    context.assembled_at_ms = current_time_ms();
    context.evidence.reserve(max_items);

    for (const auto& candidate : candidates) {
        if (context.evidence.size() >= max_items) break;
        const std::size_t item_bytes = estimate_item_bytes(candidate.experience);
        if (item_bytes > max_bytes || context.payload_bytes > max_bytes - item_bytes) {
            ++context.omitted_count;
            continue;
        }
        context.payload_bytes += item_bytes;
        context.evidence.push_back(MemoryContextItem{
            candidate.experience, candidate.relevance, item_bytes
        });
    }

    context.omitted_count += candidates.size() -
        context.evidence.size() - context.omitted_count;
    return context;
}

}  // namespace aurions
