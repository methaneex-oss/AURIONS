#include "aurions/experience_store.hpp"

#include <cassert>
#include <chrono>
#include <filesystem>
#include <string>
#include <stdexcept>

int main() {
    const auto root = std::filesystem::temp_directory_path() /
        ("aurions-conversation-" +
         std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
    std::filesystem::create_directories(root);
    const auto database = root / "brain.sqlite3";

    {
        aurions::ExperienceStore store(database);
        const auto turn = store.record_conversation_turn(
            "remember cobalt river", "I will remember cobalt river", 0);

        const auto user = store.get(turn.user.id);
        const auto assistant = store.get(turn.assistant.id);
        assert(user.has_value());
        assert(assistant.has_value());
        assert(user->source_type == "conversation_user");
        assert(assistant->source_type == "conversation_assistant");
        assert(assistant->provenance_ref == "experience://" + user->id);
        assert(user->content == "remember cobalt river");
        assert(assistant->content == "I will remember cobalt river");

        bool rejected = false;
        try {
            (void)store.record_conversation_turn("second user", "", 0);
        } catch (const std::invalid_argument&) {
            rejected = true;
        }
        assert(rejected);
        const auto absent = store.search("second user", 10);
        assert(absent.empty());
    }

    std::filesystem::remove_all(root);
    return 0;
}
