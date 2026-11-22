import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from aurions_ml.artifact_store import ArtifactStore
from aurions_ml.inference import load_candidate_model_from_bytes


def run_cli(executable: str, *arguments: str, env=None):
    completed = subprocess.run(
        [executable, *arguments],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: cpp_model_preview_e2e.py <aurions-executable> <candidate-checkpoint>")
    executable, checkpoint_path = sys.argv[1], Path(sys.argv[2])
    checkpoint_bytes = checkpoint_path.read_bytes()
    model, tokenizer = load_candidate_model_from_bytes(checkpoint_bytes)

    with tempfile.TemporaryDirectory(prefix="aurions-cpp-model-e2e-") as directory:
        root = Path(directory)
        database = root / "cognition.db"
        store = ArtifactStore(root / "artifact-store")
        candidate_ref = store.put_bytes(checkpoint_bytes).uri

        public_experience = run_cli(
            executable, "experience", "record", str(database), "observation",
            "source:public", "0",
            "AURIONS public evidence shows the sample has a stable property.",
        )
        sensitive_experience = run_cli(
            executable, "experience", "record", str(database), "observation",
            "source:confidential", "3",
            "AURIONS confidential evidence contains a private result.",
        )
        public_belief = run_cli(
            executable, "belief", "create", str(database), "public-domain", "0.5",
            "AURIONS public evidence supports the public hypothesis.",
        )
        sensitive_belief = run_cli(
            executable, "belief", "create", str(database), "private-domain", "0.5",
            "AURIONS confidential evidence supports the secret hypothesis.",
        )
        run_cli(
            executable, "belief", "create", str(database), "unknown-domain", "0.5",
            "AURIONS evidence has not yet been checked.",
        )
        run_cli(
            executable, "belief", "evidence", str(database), public_belief["belief_id"],
            public_experience["experience_id"], "supports", "0.8",
        )
        run_cli(
            executable, "belief", "evidence", str(database), sensitive_belief["belief_id"],
            sensitive_experience["experience_id"], "supports", "0.8",
        )

        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
        preview = run_cli(
            executable, "cognition", "preview", str(database), sys.executable,
            str(store.root), candidate_ref, "AURIONS evidence", "8", "8", env=env,
        )
        expected_prompt = (
            "Evidence only; no actions.\n"
            "O source:public: AURIONS public evidence shows the sample has a stable property.\n"
            "B public-domain 0.8 supported supports 0.8: AURIONS public evidence supports the public hypothesis.\n"
            "\nQ AURIONS evidence\n"
        )

        # The complete prompt must fit the actual candidate's context, not merely
        # the outer 8 KiB transport limit.
        prompt_tokens = tokenizer.encode(expected_prompt, add_boundaries=False)
        assert len(prompt_tokens) + 1 <= model.config.context_length
        assert preview["candidate_status"] == "quarantined"
        assert preview["candidate_artifact_sha256"] == candidate_ref.rsplit("/", 1)[1]
        assert preview["generated_text"].startswith(expected_prompt)
        assert preview["included_observations"] == 1
        assert preview["included_beliefs"] == 1
        assert preview["omitted_sensitive"] == 2
        assert preview["omitted_unverified"] == 1
        assert "confidential evidence" not in preview["generated_text"].lower()
        assert "secret hypothesis" not in preview["generated_text"].lower()
        assert preview["prompt_bytes"] == len(expected_prompt.encode("utf-8"))


if __name__ == "__main__":
    main()
