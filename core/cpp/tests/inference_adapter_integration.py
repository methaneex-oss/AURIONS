import json
import os
import subprocess
import time
import sys
import tempfile
from pathlib import Path


FAKE_WORKER = r'''
import json
import sys

request = json.loads(sys.stdin.readline())
if os.environ.get("AWS_SECRET_ACCESS_KEY") or os.environ.get("GITHUB_TOKEN"):
    response = {
        "protocol_version": "1.0",
        "job_id": request["job_id"],
        "status": "failed",
        "error_code": "secret_environment_leaked",
    }
elif request["prompt"] == "fail":
    response = {
        "protocol_version": "1.0",
        "job_id": request["job_id"],
        "status": "failed",
        "error_code": "candidate_rejected",
    }
else:
    generated = "x" * 70000 if request["prompt"] == "large" else "preview: " + request["prompt"]
    response = {
        "protocol_version": "1.0",
        "job_id": request["job_id"],
        "status": "completed",
        "candidate_status": "quarantined",
        "candidate_artifact_sha256": request["candidate_artifact_ref"].rsplit("/", 1)[1],
        "generated_text": generated,
        "max_new_tokens": request["max_new_tokens"],
    }
print(json.dumps(response, ensure_ascii=False, separators=(",", ":")))
'''


def invoke(executable: str, module_root: Path, artifact_store: Path, prompt: str):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(module_root)
    return subprocess.run(
        [
            executable,
            "model",
            "preview",
            sys.executable,
            str(artifact_store),
            "artifact://sha256/" + "a" * 64,
            prompt,
            "8",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def main():
    executable = sys.argv[1]
    with tempfile.TemporaryDirectory(prefix="aurions-inference-adapter-") as directory:
        root = Path(directory)
        package = root / "aurions_ml"
        package.mkdir()
        (package / "inference_worker.py").write_text(FAKE_WORKER, encoding="utf-8")
        artifact_store = root / "artifacts"
        artifact_store.mkdir()

        os.environ["AWS_SECRET_ACCESS_KEY"] = "must-not-reach-worker"
        os.environ["GITHUB_TOKEN"] = "must-not-reach-worker"
        prompt = 'AURIONS says "hello" \\ path\nand Ẹ káàbọ̀'
        completed = invoke(executable, root, artifact_store, prompt)
        assert completed.returncode == 0, completed.stderr
        response = json.loads(completed.stdout)
        assert response["candidate_status"] == "quarantined"
        assert response["candidate_artifact_sha256"] == "a" * 64
        assert response["generated_text"] == "preview: " + prompt
        assert response["max_new_tokens"] == 8

        rejected = invoke(executable, root, artifact_store, "fail")
        assert rejected.returncode != 0
        assert "candidate_rejected" in rejected.stderr

        oversized_response = invoke(executable, root, artifact_store, "large")
        assert oversized_response.returncode != 0
        assert "byte limit" in oversized_response.stderr


if __name__ == "__main__":
    main()
