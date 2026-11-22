#include "aurions/belief_store.hpp"
#include "aurions/experience_store.hpp"
#include "aurions/inference_adapter.hpp"
#include "aurions/memory_context.hpp"
#include "aurions/strategy_store.hpp"

#include <charconv>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>

namespace {

[[nodiscard]] int parse_sensitivity(std::string_view value) {
    int result{};
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size()) {
        throw std::invalid_argument("sensitivity must be an integer from 0 to 4");
    }
    return result;
}

[[nodiscard]] std::size_t parse_limit(std::string_view value) {
    unsigned long long result{};
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size() ||
        result == 0 || result > 100) {
        throw std::invalid_argument("limit must be an integer from 1 to 100");
    }
    return static_cast<std::size_t>(result);
}

[[nodiscard]] std::size_t parse_context_limit(std::string_view value) {
    unsigned long long result{};
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size() ||
        result == 0 || result > 50) {
        throw std::invalid_argument("max-items must be an integer from 1 to 50");
    }
    return static_cast<std::size_t>(result);
}

[[nodiscard]] double parse_real(std::string_view value, const char* name) {
    double result{};
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size() ||
        !std::isfinite(result)) {
        throw std::invalid_argument(std::string(name) + " must be a finite number");
    }
    return result;
}

[[nodiscard]] std::string json_escape(std::string_view value) {
    std::string output;
    output.reserve(value.size() + 8);
    for (const unsigned char c : value) {
        switch (c) {
            case '"': output += "\\\""; break;
            case '\\': output += "\\\\"; break;
            case '\b': output += "\\b"; break;
            case '\f': output += "\\f"; break;
            case '\n': output += "\\n"; break;
            case '\r': output += "\\r"; break;
            case '\t': output += "\\t"; break;
            default:
                if (c < 0x20) {
                    constexpr char hex[] = "0123456789abcdef";
                    output += "\\u00";
                    output.push_back(hex[(c >> 4U) & 0x0fU]);
                    output.push_back(hex[c & 0x0fU]);
                } else {
                    output.push_back(static_cast<char>(c));
                }
        }
    }
    return output;
}

void print_belief(const aurions::BeliefSnapshot& belief) {
    std::cout << std::setprecision(17)
        << "{\"belief_id\":\"" << belief.id
        << "\",\"proposition\":\"" << json_escape(belief.proposition)
        << "\",\"domain\":\"" << json_escape(belief.domain)
        << "\",\"revisions\":[";
    for (std::size_t i = 0; i < belief.revisions.size(); ++i) {
        if (i != 0) std::cout << ",";
        const auto& revision = belief.revisions[i];
        std::cout
            << "{\"revision\":" << revision.number
            << ",\"confidence\":" << revision.confidence
            << ",\"epistemic_status\":\"" << json_escape(revision.epistemic_status)
            << "\",\"reason\":\"" << json_escape(revision.reason)
            << "\",\"created_at_ms\":" << revision.created_at_ms
            << ",\"evidence_count\":" << revision.evidence_count
            << ",\"evidence_source_ref\":\"" << json_escape(revision.evidence_source_ref)
            << "\",\"evidence_stance\":\"" << json_escape(revision.evidence_stance)
            << "\",\"evidence_reliability\":" << revision.evidence_reliability
            << ",\"evidence_relevance\":" << revision.evidence_relevance
            << ",\"evidence_sensitivity\":" << revision.evidence_sensitivity << "}";
    }
    std::cout << "]}\n";
}


void usage();

[[nodiscard]] std::size_t parse_token_limit(std::string_view value) {
    unsigned long long result{};
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size() ||
        result == 0 || result > 128) {
        throw std::invalid_argument("max-new-tokens must be an integer from 1 to 128");
    }
    return static_cast<std::size_t>(result);
}

int run_model(int argc, char** argv) {
    if ((argc != 7 && argc != 8) || std::string_view(argv[2]) != "preview") {
        usage();
        return EXIT_FAILURE;
    }
    const std::size_t max_new_tokens = argc == 8 ? parse_token_limit(argv[7]) : 32;
    aurions::PythonProcessInferenceAdapter adapter(argv[3], argv[4]);
    const auto result = adapter.preview(argv[5], argv[6], max_new_tokens);
    std::cout
        << "{\"job_id\":\"" << result.job_id
        << "\",\"candidate_status\":\"" << result.candidate_status
        << "\",\"candidate_artifact_sha256\":\"" << result.candidate_artifact_sha256
        << "\",\"generated_text\":\"" << json_escape(result.generated_text)
        << "\",\"max_new_tokens\":" << result.max_new_tokens << "}\n";
    return EXIT_SUCCESS;
}

void usage() {
    std::cerr
        << "Usage:\n"
        << "  aurions experience record <database> <source> <provenance> <sensitivity 0-4> <content>\n"
        << "  aurions experience show <database> <experience-uuid>\n"
        << "  aurions experience search <database> <query> [limit 1-100]\n"
        << "  aurions experience context <database> <query> [max-items 1-50]\n"
        << "  aurions belief create <database> <domain> <prior-confidence> <proposition>\n"
        << "  aurions belief evidence <database> <belief-uuid> <experience-uuid> <stance> <reliability> [relevance]\n"
        << "  aurions belief show <database> <belief-uuid>\n"
        << "  aurions cognition context <database> <query> [max-items 1-50]\n"
        << "  aurions cognition preview <database> <python-executable> <artifact-store> <artifact-uri> <query> [max-items] [max-new-tokens]\n"
        << "  aurions strategy choose <database> <context-ref> <strategy-ref> [strategy-ref ...]\n"
        << "  aurions strategy outcome <database> <prediction-uuid> <experience-uuid> <success|failure>\n"
        << "  aurions model preview <python-executable> <artifact-store> <artifact-uri> <prompt> [max-new-tokens 1-128]\n";
}

int run_experience(int argc, char** argv) {
    if (argc < 4) { usage(); return EXIT_FAILURE; }
    const std::string_view operation(argv[2]);
    aurions::ExperienceStore store(argv[3]);

    if (operation == "record" && argc == 8) {
        const auto saved = store.record(
            argv[4], argv[7], argv[5], parse_sensitivity(argv[6]));
        std::cout << "{\"experience_id\":\"" << saved.id << "\"}\n";
        return EXIT_SUCCESS;
    }

    if (operation == "search" && (argc == 5 || argc == 6)) {
        const std::size_t limit = argc == 6 ? parse_limit(argv[5]) : 10;
        const auto matches = store.search(argv[4], limit);
        std::cout << "[";
        for (std::size_t i = 0; i < matches.size(); ++i) {
            if (i != 0) std::cout << ",";
            const auto& match = matches[i];
            const auto& experience = match.experience;
            std::cout
                << "{\"experience_id\":\"" << experience.id
                << "\",\"relevance\":" << match.relevance
                << ",\"source_type\":\"" << json_escape(experience.source_type)
                << "\",\"content\":\"" << json_escape(experience.content)
                << "\",\"provenance_ref\":\"" << json_escape(experience.provenance_ref)
                << "\",\"observed_at_ms\":" << experience.observed_at_ms
                << ",\"recorded_at_ms\":" << experience.recorded_at_ms
                << ",\"sensitivity\":" << experience.sensitivity << "}";
        }
        std::cout << "]\n";
        return EXIT_SUCCESS;
    }

    if (operation == "context" && (argc == 5 || argc == 6)) {
        const std::size_t max_items = argc == 6 ? parse_limit(argv[5]) : 8;
        const aurions::MemoryContextBuilder builder(store);
        const auto context = builder.build(argv[4], max_items);
        std::cout
            << "{\"query\":\"" << json_escape(context.query)
            << "\",\"assembled_at_ms\":" << context.assembled_at_ms
            << ",\"payload_bytes\":" << context.payload_bytes
            << ",\"omitted_count\":" << context.omitted_count
            << ",\"evidence\":[";
        for (std::size_t i = 0; i < context.evidence.size(); ++i) {
            if (i != 0) std::cout << ",";
            const auto& item = context.evidence[i];
            const auto& experience = item.experience;
            std::cout
                << "{\"experience_id\":\"" << experience.id
                << "\",\"relevance\":" << item.relevance
                << ",\"source_type\":\"" << json_escape(experience.source_type)
                << "\",\"content\":\"" << json_escape(experience.content)
                << "\",\"provenance_ref\":\"" << json_escape(experience.provenance_ref)
                << "\",\"observed_at_ms\":" << experience.observed_at_ms
                << ",\"recorded_at_ms\":" << experience.recorded_at_ms
                << ",\"sensitivity\":" << experience.sensitivity
                << ",\"estimated_bytes\":" << item.estimated_bytes << "}";
        }
        std::cout << "]}\n";
        return EXIT_SUCCESS;
    }

    if (operation == "show" && argc == 5) {
        const auto found = store.get(argv[4]);
        if (!found) {
            std::cerr << "Experience not found\n";
            return 2;
        }
        std::cout
            << "{\"experience_id\":\"" << found->id
            << "\",\"source_type\":\"" << json_escape(found->source_type)
            << "\",\"content\":\"" << json_escape(found->content)
            << "\",\"provenance_ref\":\"" << json_escape(found->provenance_ref)
            << "\",\"observed_at_ms\":" << found->observed_at_ms
            << ",\"recorded_at_ms\":" << found->recorded_at_ms
            << ",\"sensitivity\":" << found->sensitivity << "}\n";
        return EXIT_SUCCESS;
    }
    usage();
    return EXIT_FAILURE;
}

int run_belief(int argc, char** argv) {
    if (argc < 4) { usage(); return EXIT_FAILURE; }
    // ExperienceStore creates/owns the experiences table referenced by canonical
    // evidence_items. Beliefs and their revisions share this same database.
    aurions::ExperienceStore experiences(argv[3]);
    aurions::BeliefStore beliefs(argv[3]);
    const std::string_view operation(argv[2]);

    if (operation == "create" && argc == 7) {
        print_belief(beliefs.create(argv[4], argv[6], parse_real(argv[5], "prior confidence")));
        return EXIT_SUCCESS;
    }
    if (operation == "evidence" && (argc == 8 || argc == 9)) {
        const double relevance = argc == 9 ? parse_real(argv[8], "relevance") : 1.0;
        print_belief(beliefs.add_evidence(
            argv[4], argv[5], argv[6], parse_real(argv[7], "reliability"), relevance));
        return EXIT_SUCCESS;
    }
    if (operation == "show" && argc == 5) {
        print_belief(beliefs.get(argv[4]));
        return EXIT_SUCCESS;
    }
    usage();
    return EXIT_FAILURE;
}

struct CognitionPreviewPrompt {
    std::string text;
    std::size_t included_observations{};
    std::size_t included_beliefs{};
    std::size_t omitted_sensitive{};
    std::size_t omitted_unverified{};
    std::size_t omitted_budget{};
};

CognitionPreviewPrompt build_cognition_preview_prompt(
    const std::string& query,
    const aurions::MemoryContext& memory,
    const std::vector<aurions::BeliefSnapshot>& beliefs) {
    if (query.empty() || query.size() > 4096)
        throw std::invalid_argument("cognition preview query must contain 1-4096 bytes");
    CognitionPreviewPrompt result;
    const std::string question_footer = "\nQuestion: " + query + "\n";
    result.text = "AURIONS preview; evidence only, no actions.\n";
    auto append = [&](const std::string& section) {
        if (result.text.size() + section.size() + question_footer.size() > 8192) {
            ++result.omitted_budget;
            return false;
        }
        result.text += section;
        return true;
    };
    result.omitted_budget += memory.omitted_count;
    for (const auto& item : memory.evidence) {
        const auto& experience = item.experience;
        if (experience.sensitivity != 0) {
            ++result.omitted_sensitive;
            continue;
        }
        std::ostringstream section;
        section << "O source_type=" << experience.source_type
                << " provenance=" << experience.provenance_ref
                << " sensitivity=0: " << experience.content << "\n";
        if (append(section.str())) ++result.included_observations;
    }
    append("");
    for (const auto& belief : beliefs) {
        bool has_evidence = false;
        bool public_evidence_only = true;
        for (const auto& revision : belief.revisions) {
            if (revision.evidence_count == 0) continue;
            has_evidence = true;
            if (revision.evidence_sensitivity != 0) public_evidence_only = false;
        }
        if (!has_evidence) {
            ++result.omitted_unverified;
            continue;
        }
        if (!public_evidence_only) {
            ++result.omitted_sensitive;
            continue;
        }
        if (belief.revisions.empty()) continue;
        const auto& current = belief.revisions.back();
        std::ostringstream section;
        section << "B domain=" << belief.domain
                << " confidence=" << std::setprecision(8) << current.confidence
                << " status=" << current.epistemic_status
                << " stance=" << current.evidence_stance
                << " reliability=" << current.evidence_reliability
                << " sensitivity=0: " << belief.proposition << "\n";
        if (append(section.str())) ++result.included_beliefs;
    }
    if (result.text.size() + question_footer.size() > 8192)
        throw std::runtime_error("cognition preview prompt exceeded its byte limit");
    result.text += question_footer;
    return result;
}

int run_cognition_preview(int argc, char** argv) {
    if (argc < 8 || argc > 10 || std::string_view(argv[2]) != "preview") {
        usage();
        return EXIT_FAILURE;
    }
    const std::size_t max_items = argc >= 9 ? parse_context_limit(argv[8]) : 8;
    const std::size_t max_new_tokens = argc == 10 ? parse_token_limit(argv[9]) : 32;
    aurions::ExperienceStore experiences(argv[3]);
    aurions::BeliefStore beliefs(argv[3]);
    aurions::MemoryContextBuilder builder(experiences);
    const std::string query = argv[7];
    const auto memory = builder.build(query, max_items, 4096);
    const auto relevant_beliefs = beliefs.search(query, max_items);
    const auto prompt = build_cognition_preview_prompt(query, memory, relevant_beliefs);
    aurions::PythonProcessInferenceAdapter adapter(argv[4], argv[5]);
    const auto result = adapter.preview(argv[6], prompt.text, max_new_tokens);
    std::cout
        << "{\"job_id\":\"" << result.job_id
        << "\",\"candidate_status\":\"" << result.candidate_status
        << "\",\"candidate_artifact_sha256\":\"" << result.candidate_artifact_sha256
        << "\",\"generated_text\":\"" << json_escape(result.generated_text)
        << "\",\"included_observations\":" << prompt.included_observations
        << ",\"included_beliefs\":" << prompt.included_beliefs
        << ",\"omitted_sensitive\":" << prompt.omitted_sensitive
        << ",\"omitted_unverified\":" << prompt.omitted_unverified
        << ",\"omitted_budget\":" << prompt.omitted_budget
        << ",\"prompt_bytes\":" << prompt.text.size() << "}\n";
    return EXIT_SUCCESS;
}

int run_cognition(int argc, char** argv) {
    if (argc >= 3 && std::string_view(argv[2]) == "preview")
        return run_cognition_preview(argc, argv);
    if (argc < 5 || argc > 6 || std::string_view(argv[2]) != "context") {
        usage();
        return EXIT_FAILURE;
    }
    aurions::ExperienceStore experiences(argv[3]);
    aurions::BeliefStore beliefs(argv[3]);
    const std::size_t max_items = argc == 6 ? parse_limit(argv[5]) : 8;
    const std::string query = argv[4];
    const aurions::MemoryContextBuilder memory_builder(experiences);
    const auto memory = memory_builder.build(query, max_items);
    const auto relevant_beliefs = beliefs.search(query, max_items);

    std::cout << "{\"query\":\"" << json_escape(query) << "\",\"memory_evidence\":[";
    for (std::size_t i = 0; i < memory.evidence.size(); ++i) {
        if (i != 0) std::cout << ",";
        const auto& item = memory.evidence[i];
        const auto& experience = item.experience;
        std::cout
            << "{\"experience_id\":\"" << experience.id
            << "\",\"relevance\":" << item.relevance
            << ",\"content\":\"" << json_escape(experience.content)
            << "\",\"source_type\":\"" << json_escape(experience.source_type)
            << "\",\"provenance_ref\":\"" << json_escape(experience.provenance_ref)
            << "\",\"sensitivity\":" << experience.sensitivity << "}";
    }
    std::cout << "],\"beliefs\":[";
    for (std::size_t i = 0; i < relevant_beliefs.size(); ++i) {
        if (i != 0) std::cout << ",";
        const auto& belief = relevant_beliefs[i];
        const auto& current = belief.revisions.back();
        std::cout << std::setprecision(17)
            << "{\"belief_id\":\"" << belief.id
            << "\",\"proposition\":\"" << json_escape(belief.proposition)
            << "\",\"domain\":\"" << json_escape(belief.domain)
            << "\",\"relevance\":" << belief.relevance
            << ",\"confidence\":" << current.confidence
            << ",\"epistemic_status\":\"" << json_escape(current.epistemic_status)
            << "\",\"revision\":" << current.number
            << ",\"evidence_source_ref\":\"" << json_escape(current.evidence_source_ref)
            << "\",\"evidence_stance\":\"" << json_escape(current.evidence_stance)
            << "\",\"evidence_reliability\":" << current.evidence_reliability
            << ",\"evidence_sensitivity\":" << current.evidence_sensitivity << "}";
    }
    std::cout << "]}\n";
    return EXIT_SUCCESS;
}


int run_strategy(int argc, char** argv) {
    if (argc < 4) { usage(); return EXIT_FAILURE; }
    aurions::StrategyStore strategies(argv[3]);
    const std::string_view operation(argv[2]);

    if (operation == "choose" && argc >= 6 && argc <= 55) {
        std::vector<std::string> candidates;
        for (int i = 5; i < argc; ++i) candidates.emplace_back(argv[i]);
        const auto choice = strategies.choose(argv[4], std::move(candidates));
        std::cout << std::setprecision(17)
            << "{\"prediction_id\":\"" << choice.prediction_id
            << "\",\"context_ref\":\"" << json_escape(choice.context_ref)
            << "\",\"strategy_ref\":\"" << json_escape(choice.strategy_ref)
            << "\",\"posterior_success_probability\":" << choice.posterior_success_probability
            << ",\"selection_score\":" << choice.selection_score
            << ",\"successes\":" << choice.successes
            << ",\"trials\":" << choice.trials
            << ",\"selection_basis\":\"" << choice.selection_basis << "\"}\n";
        return EXIT_SUCCESS;
    }

    if (operation == "outcome" && argc == 7) {
        const auto result = strategies.record_outcome(argv[4], argv[5], argv[6]);
        std::cout << std::setprecision(17)
            << "{\"prediction_id\":\"" << result.prediction_id
            << "\",\"experience_id\":\"" << result.experience_id
            << "\",\"context_ref\":\"" << json_escape(result.context_ref)
            << "\",\"strategy_ref\":\"" << json_escape(result.strategy_ref)
            << "\",\"outcome\":\"" << result.outcome
            << "\",\"evaluation_result\":\"" << result.evaluation_result
            << "\",\"predicted_success_probability\":"
            << result.predicted_success_probability << "}\n";
        return EXIT_SUCCESS;
    }
    usage();
    return EXIT_FAILURE;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc < 2) { usage(); return EXIT_FAILURE; }
        const std::string_view group(argv[1]);
        if (group == "experience") return run_experience(argc, argv);
        if (group == "belief") return run_belief(argc, argv);
        if (group == "cognition") return run_cognition(argc, argv);
        if (group == "strategy") return run_strategy(argc, argv);
        if (group == "model") return run_model(argc, argv);
        usage();
        return EXIT_FAILURE;
    } catch (const std::exception& error) {
        std::cerr << "AURIONS: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
