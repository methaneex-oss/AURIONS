import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


FAKE_WORKER = r'''
import json
import os
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
elif request["prompt"] == "wrong_job":
    response = {"protocol_version": "1.0", "job_id": "00000000-0000-4000-8000-000000000000",
                "status": "completed", "candidate_status": "quarantined",
                "candidate_artifact_sha256": request["candidate_artifact_ref"].rsplit("/", 1)[1],
                "generated_text": "bad", "max_new_tokens": request["max_new_tokens"]}
elif request["prompt"] == "wrong_digest":
    response = {"protocol_version": "1.0", "job_id": request["job_id"],
                "status": "completed", "candidate_status": "quarantined",
                "candidate_artifact_sha256": "b" * 64,
                "generated_text": "bad", "max_new_tokens": request["max_new_tokens"]}
elif request["prompt"] == "wrong_protocol":
    response = {"protocol_version": "99.0", "job_id": request["job_id"],
                "status": "completed", "candidate_status": "quarantined",
                "candidate_artifact_sha256": request["candidate_artifact_ref"].rsplit("/", 1)[1],
                "generated_text": "bad", "max_new_tokens": request["max_new_tokens"]}
elif request["prompt"] == "duplicate":
    print('{"protocol_version":"1.0","job_id":"' + request["job_id"] +
          '","job_id":"' + request["job_id"] + '","status":"completed"}')
    raise SystemExit(0)
elif request["prompt"] == "malformed":
    print("{not-json")
    raise SystemExit(0)
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


def invoke(executable: str, module_root: Path, artifact_store: Path, prompt: str, *, use_stdin=False):
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
            "--stdin" if use_stdin else prompt,
            "8",
        ],
        input=prompt if use_stdin else None,
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

        private_prompt = "private prompt must not be in argv: " + "x" * 200
        stdin_completed = invoke(executable, root, artifact_store, private_prompt, use_stdin=True)
        assert stdin_completed.returncode == 0, stdin_completed.stderr
        stdin_response = json.loads(stdin_completed.stdout)
        assert stdin_response["generated_text"] == "preview: " + private_prompt

        oversized_stdin = invoke(executable, root, artifact_store, "x" * 8193, use_stdin=True)
        assert oversized_stdin.returncode != 0
        assert "stdin input exceeds" in oversized_stdin.stderr

        rejected = invoke(executable, root, artifact_store, "fail")
        assert rejected.returncode != 0
        assert "candidate_rejected" in rejected.stderr

        for hostile_prompt, expected_error in (
            ("wrong_job", "job ID does not match"),
            ("wrong_digest", "mismatched candidate digest"),
            ("wrong_protocol", "unsupported protocol version"),
            ("duplicate", "duplicate JSON key"),
            ("malformed", "malformed worker JSON response"),
        ):
            hostile = invoke(executable, root, artifact_store, hostile_prompt)
            assert hostile.returncode != 0, hostile_prompt
            assert expected_error in hostile.stderr, (hostile_prompt, hostile.stderr)

        oversized_response = invoke(executable, root, artifact_store, "large")
        assert oversized_response.returncode != 0
        assert "byte limit" in oversized_response.stderr


if __name__ == "__main__":
    main()
