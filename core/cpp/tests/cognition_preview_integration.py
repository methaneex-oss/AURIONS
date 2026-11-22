import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


FAKE_WORKER = r'''
import json
import sys

request = json.loads(sys.stdin.readline())
response = {
    "protocol_version": "1.0",
    "job_id": request["job_id"],
    "status": "completed",
    "candidate_status": "quarantined",
    "candidate_artifact_sha256": request["candidate_artifact_ref"].rsplit("/", 1)[1],
    "generated_text": request["prompt"],
    "max_new_tokens": request["max_new_tokens"],
}
print(json.dumps(response, ensure_ascii=False, separators=(",", ":")))
'''


def run(executable: str, *arguments: str, env=None):
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
    executable = sys.argv[1]
    with tempfile.TemporaryDirectory(prefix="aurions-cognition-preview-") as directory:
        root = Path(directory)
        database = root / "cognition.db"
        artifact_store = root / "artifacts"
        artifact_store.mkdir()
        package_root = root / "python"
        package = package_root / "aurions_ml"
        package.mkdir(parents=True)
        (package / "inference_worker.py").write_text(FAKE_WORKER, encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(package_root)

        public_experience = run(
            executable, "experience", "record", str(database), "observation",
            "source:public", "0",
            "AURIONS public evidence shows the sample has a stable property.",
        )
        sensitive_experience = run(
            executable, "experience", "record", str(database), "observation",
            "source:confidential", "3",
            "AURIONS confidential evidence contains a private result.",
        )
        public_belief = run(
            executable, "belief", "create", str(database), "public-domain", "0.5",
            "AURIONS public evidence supports the public hypothesis.",
        )
        sensitive_belief = run(
            executable, "belief", "create", str(database), "private-domain", "0.5",
            "AURIONS confidential evidence supports the secret hypothesis.",
        )
        unverified_belief = run(
            executable, "belief", "create", str(database), "unknown-domain", "0.5",
            "AURIONS evidence has not yet been checked.",
        )
        run(
            executable, "belief", "evidence", str(database), public_belief["belief_id"],
            public_experience["experience_id"], "supports", "0.8",
        )
        run(
            executable, "belief", "evidence", str(database), sensitive_belief["belief_id"],
            sensitive_experience["experience_id"], "supports", "0.8",
        )

        preview = run(
            executable, "cognition", "preview", str(database), sys.executable,
            str(artifact_store), "artifact://sha256/" + "a" * 64,
            "AURIONS evidence", "8", "8", env=env,
        )
        prompt = preview["generated_text"]
        assert preview["candidate_status"] == "quarantined"
        assert preview["included_observations"] == 1
        assert preview["included_beliefs"] == 1
        assert preview["omitted_sensitive"] == 2
        assert preview["omitted_unverified"] == 1
        assert "AURIONS public evidence shows" in prompt
        assert "AURIONS public evidence supports the public hypothesis" in prompt
        assert "confidential evidence" not in prompt.lower()
        assert "secret hypothesis" not in prompt.lower()
        assert "private result" not in prompt.lower()


if __name__ == "__main__":
    main()
