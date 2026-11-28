#pragma once
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <vector>
struct sqlite3;
namespace aurions {
struct TaskRun { std::string id,task_definition_ref,state; std::int64_t revision{}; double priority{}; std::string budget_json,checkpoint_refs_json; std::int64_t created_at_ms{},updated_at_ms{}; std::optional<std::string> failure_ref; };
struct TaskRunTransition { std::string event_id,task_run_id; std::optional<std::string> from_state; std::string to_state; std::int64_t previous_revision{},revision{}; std::string cause_type,cause_ref,actor_ref; std::optional<std::string> checkpoint_ref,failure_ref,reconciliation_ref; std::int64_t occurred_at_ms{}; };
// Durable task-run state and immutable transition history; never dispatches work.
class TaskRunStore final {
public:
 explicit TaskRunStore(const std::filesystem::path& database_path); ~TaskRunStore();
 TaskRunStore(const TaskRunStore&)=delete; TaskRunStore& operator=(const TaskRunStore&)=delete;
 TaskRunStore(TaskRunStore&&)=delete; TaskRunStore& operator=(TaskRunStore&&)=delete;
 [[nodiscard]] TaskRun create(const std::string& task_definition_ref,double priority,const std::string& budget_json,const std::string& cause_ref,const std::string& actor_ref);
 [[nodiscard]] TaskRun transition(const std::string& task_run_id,std::int64_t expected_revision,const std::string& to_state,const std::string& cause_type,const std::string& cause_ref,const std::string& actor_ref,std::optional<std::string> checkpoint_ref=std::nullopt,std::optional<std::string> failure_ref=std::nullopt,std::optional<std::string> reconciliation_ref=std::nullopt);
 [[nodiscard]] std::optional<TaskRun> get(const std::string& task_run_id) const;
 [[nodiscard]] std::vector<TaskRunTransition> transitions(const std::string& task_run_id) const;
private: sqlite3* db_{};
};
} // namespace aurions
