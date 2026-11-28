#include "aurions/belief_store.hpp"
#include "aurions/strategy_store.hpp"

#include <chrono>
#include <filesystem>
#include <iostream>
#include <string>

int main() {
    const auto unique = std::chrono::steady_clock::now().time_since_epoch().count();
    const auto root = std::filesystem::temp_directory_path() /
        ("aurions-store-path-" + std::to_string(unique));
    const auto nested = root / "deep" / "directory";
    bool passed = false;

    try {
        {
            aurions::BeliefStore beliefs(nested / "beliefs.sqlite");
            aurions::StrategyStore strategies(nested / "strategies.sqlite");
        }
        passed = std::filesystem::is_regular_file(nested / "beliefs.sqlite") &&
                std::filesystem::is_regular_file(nested / "strategies.sqlite");
    } catch (const std::exception& error) {
        std::cerr << "store path creation failed: " << error.what() << '\n';
    }

    std::error_code cleanup_error;
    std::filesystem::remove_all(root, cleanup_error);
    if (!passed) {
        std::cerr << "constructors must create missing parent directories and database files\n";
        return 1;
    }
    if (cleanup_error) {
        std::cerr << "test cleanup failed: " << cleanup_error.message() << '\n';
        return 1;
    }
    return 0;
}
