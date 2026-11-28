#include "aurions/experience_store.hpp"
#include "aurions/representation_store.hpp"

#include <chrono>
#include <filesystem>
#include <iostream>
#include <stdexcept>

int main() {
    const auto unique = std::chrono::steady_clock::now().time_since_epoch().count();
    const auto root = std::filesystem::temp_directory_path() /
        ("aurions-representation-" + std::to_string(unique));
    const auto database = root / "deep" / "brain.sqlite";
    bool passed = false;

    try {
        std::string source_id;
        std::string representation_id;
        {
            aurions::ExperienceStore experiences(database);
            const auto source = experiences.record(
                "observation", "A vehicle is approaching from the east.",
                "test://observation/001", 0);
            source_id = source.id;

            aurions::RepresentationStore representations(database);
            const auto recorded = representations.record(
                source.id, "scene_graph",
                R"({"entities":[{"type":"vehicle","direction":"east"}],"relations":[]})",
                "test-parser-v1", R"({"confidence":0.83,"unknowns":["distance"]})");
            representation_id = recorded.id;

            const auto fetched = representations.get(recorded.id);
            if (!fetched || fetched->experience_id != source.id ||
                fetched->representation_type != "scene_graph" ||
                fetched->content_json != recorded.content_json ||
                fetched->method != "test-parser-v1") {
                throw std::runtime_error("representation retrieval lost its fields or provenance");
            }

            const auto second = representations.record(
                source.id, "semantic",
                R"({"summary":"vehicle approaching","entities":["vehicle"]})",
                "test-semantic-v1", R"({"confidence":0.7})");
            const auto all = representations.list_for_experience(source.id, 10);
            if (all.size() != 2 || all[0].experience_id != source.id ||
                all[1].experience_id != source.id) {
                throw std::runtime_error("representation listing did not return linked records");
            }
            if (representations.get("00000000-0000-4000-8000-000000000000"))
                throw std::runtime_error("missing representation lookup returned a record");

            bool invalid_json_rejected = false;
            try {
                (void)representations.record(source.id, "invalid", "{", "test", "{}");
            } catch (const std::exception&) {
                invalid_json_rejected = true;
            }
            if (!invalid_json_rejected)
                throw std::runtime_error("invalid representation JSON was accepted");

            bool missing_source_rejected = false;
            try {
                (void)representations.record(
                    "00000000-0000-4000-8000-000000000000",
                    "semantic", R"({"summary":"orphan"})", "test", "{}");
            } catch (const std::exception&) {
                missing_source_rejected = true;
            }
            if (!missing_source_rejected)
                throw std::runtime_error("representation with unknown source was accepted");
            if (second.id == recorded.id || recorded.created_at_ms <= 0)
                throw std::runtime_error("representation identity or timestamp invalid");
        }

        // Reopening the shared database must preserve linked representations.
        {
            aurions::RepresentationStore reopened(database);
            const auto persisted = reopened.get(representation_id);
            const auto listed = reopened.list_for_experience(source_id);
            passed = persisted.has_value() && listed.size() == 2;
        }
    } catch (const std::exception& error) {
        std::cerr << "representation integration failed: " << error.what() << '\n';
    }

    std::error_code cleanup_error;
    std::filesystem::remove_all(root, cleanup_error);
    if (!passed || cleanup_error) return 1;
    return 0;
}
