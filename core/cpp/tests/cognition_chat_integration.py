import json
import os
import subprocess
import tempfile
from pathlib import Path


FAKE_PROVIDER = r'''#!/usr/bin/env python3
import sys
prompt = sys.stdin.read()
if len(prompt.encode("utf-8")) > 8192:
    raise SystemExit(9)
if "simulate provider failure" in prompt.lower():
    raise SystemExit(7)
marker = "cobalt river"
private_marker = "violet harbor"
if prompt.lower().count(marker) >= 2:
    print("CONTEXT_PRESENT")
elif prompt.lower().count(private_marker) >= 2:
    print("PRIVATE_CONTEXT_PRESENT")
elif private_marker in prompt.lower():
    print("PRIVATE_CONTEXT_FILTERED")
elif marker in prompt.lower():
    print("CONTEXT_FILTERED")
else:
    print("NO_MATCH")
'''


def invoke(executable, database, fake_python, module_root, config, query,
           *, sensitivity=0, route="local", allow_cloud=False):
    command = [
        executable, "cognition", "chat", str(database), str(fake_python),
        str(module_root), str(config), route, str(sensitivity), "-", 
    ]
    if allow_cloud:
        command.append("--allow-cloud")
    command.append("--stdin")
    return subprocess.run(
        command, input=query, capture_output=True, text=True, check=False,
        timeout=30,
    )


def main():
    executable = os.path.abspath(__import__("sys").argv[1])
    with tempfile.TemporaryDirectory(prefix="aurions-cognition-chat-") as directory:
        root = Path(directory)
        database = root / "brain.sqlite3"
        fake_python = root / "fake-python"
        fake_python.write_text(FAKE_PROVIDER, encoding="utf-8")
        fake_python.chmod(0o755)
        module_root = root / "modules"
        module_root.mkdir()
        config = root / "provider.json"
        config.write_text("{}", encoding="utf-8")

        first = invoke(
            executable, database, fake_python, module_root, config,
            "Remember this unique phrase: cobalt river.",
        )
        assert first.returncode == 0, first.stderr
        assert json.loads(first.stdout)["answer"] == "CONTEXT_FILTERED"

        # A separate process must retrieve the durable prior experience.
        second = invoke(
            executable, database, fake_python, module_root, config,
            "What phrase did I ask you to remember: cobalt river?",
        )
        assert second.returncode == 0, second.stderr
        assert json.loads(second.stdout)["answer"] == "CONTEXT_PRESENT"

        private = invoke(
            executable, database, fake_python, module_root, config,
            "Private marker violet harbor.", sensitivity=2,
        )
        assert private.returncode == 0, private.stderr
        filtered = invoke(
            executable, database, fake_python, module_root, config,
            "Check private marker violet harbor.", sensitivity=0,
        )
        assert filtered.returncode == 0, filtered.stderr
        assert json.loads(filtered.stdout)["answer"] == "PRIVATE_CONTEXT_FILTERED"

        # A failed provider call must not persist a partial conversation turn.
        failed = invoke(
            executable, database, fake_python, module_root, config,
            "simulate provider failure now",
        )
        assert failed.returncode != 0
        no_partial_turn = subprocess.run(
            [executable, "experience", "search", str(database),
             "simulate provider failure"],
            capture_output=True, text=True, check=False,
        )
        assert no_partial_turn.returncode == 0, no_partial_turn.stderr
        assert json.loads(no_partial_turn.stdout) == []

        oversized = invoke(
            executable, database, fake_python, module_root, config,
            "x" * 4097,
        )
        assert oversized.returncode != 0
        assert "stdin input exceeds" in oversized.stderr

        denied_cloud = invoke(
            executable, database, fake_python, module_root, config,
            "cloud test", route="cloud",
        )
        assert denied_cloud.returncode != 0
        assert "explicit --allow-cloud" in denied_cloud.stderr

        denied_private_cloud = invoke(
            executable, database, fake_python, module_root, config,
            "cloud private test", sensitivity=2, route="cloud", allow_cloud=True,
        )
        assert denied_private_cloud.returncode != 0
        assert "non-public input" in denied_private_cloud.stderr

        # The chat prompt must reserve space for its instruction suffix even
        # when retrieval contains many large public records.
        for index in range(20):
            completed = subprocess.run(
                [executable, "experience", "record", str(database),
                 "research", f"prompt-budget-{index}", "0",
                 "cobalt river " + ("public context " * 120)],
                capture_output=True, text=True, check=False,
            )
            assert completed.returncode == 0, completed.stderr
        bounded_prompt = invoke(
            executable, database, fake_python, module_root, config,
            "cobalt river public context",
        )
        assert bounded_prompt.returncode == 0, bounded_prompt.stderr

        allowed_cloud = invoke(
            executable, database, fake_python, module_root, config,
            "public cloud test", route="cloud", allow_cloud=True,
        )
        assert allowed_cloud.returncode == 0, allowed_cloud.stderr
        assert json.loads(allowed_cloud.stdout)["route"] == "cloud"


if __name__ == "__main__":
    main()
