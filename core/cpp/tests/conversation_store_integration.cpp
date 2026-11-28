#include "aurions/experience_store.hpp"

#include <chrono>
#include <filesystem>
#include <string>
#include <stdexcept>

void require(bool condition, const char* message) { if (!condition) throw std::runtime_error(message); }

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
        require(user.has_value(), "user experience was not persisted");
        require(assistant.has_value(), "assistant experience was not persisted");
        require(user->source_type == "conversation_user", "user source type mismatch");
        require(assistant->source_type == "conversation_assistant", "assistant source type mismatch");
        require(assistant->provenance_ref == "experience://" + user->id, "assistant provenance mismatch");
        require(user->content == "remember cobalt river", "user content mismatch");
        require(assistant->content == "I will remember cobalt river", "assistant content mismatch");

        bool rejected = false;
        try {
            (void)store.record_conversation_turn("second user", "", 0);
        } catch (const std::invalid_argument&) {
            rejected = true;
        }
        require(rejected, "empty assistant response was accepted");
        const auto absent = store.search("second user", 10);
        require(absent.empty(), "invalid turn partially persisted");
    }

    std::filesystem::remove_all(root);
    return 0;
}
