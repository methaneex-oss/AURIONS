import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aurions_ml.provider_runtime import ProviderConfigurationError, chat, load_config, main


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self, limit):
        return self.body[:limit]


class ProviderRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "provider.json"
        self.path.write_text(json.dumps({
            "base_url": "https://api.example.test/v1",
            "model": "test-model",
            "api_key_env": "AURIONS_TEST_PROVIDER_KEY",
            "timeout_seconds": 12,
            "max_tokens": 64,
        }), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()
        os.environ.pop("AURIONS_TEST_PROVIDER_KEY", None)

    def test_request_configuration_auth_and_response(self):
        config = load_config(self.path)
        os.environ["AURIONS_TEST_PROVIDER_KEY"] = "not-for-logs"
        captured = {}

        def opener(request, timeout):
            captured.update(
                url=request.full_url,
                headers=request.headers,
                payload=json.loads(request.data),
                timeout=timeout,
            )
            return FakeResponse(json.dumps({
                "choices": [{"message": {"content": "ok"}}]
            }).encode())

        self.assertEqual(chat(config, "hello", opener=opener), "ok")
        self.assertEqual(captured["url"], "https://api.example.test/v1/chat/completions")
        self.assertEqual(captured["payload"]["model"], "test-model")
        self.assertEqual(captured["payload"]["messages"], [{"role": "user", "content": "hello"}])
        self.assertEqual(captured["payload"]["max_tokens"], 64)
        self.assertEqual(captured["timeout"], 12)
        self.assertEqual(captured["headers"]["Authorization"], "Bearer not-for-logs")

    def test_loopback_http_allowed_without_credentials(self):
        self.path.write_text(json.dumps({
            "base_url": "http://127.0.0.1:11434/v1", "model": "local"
        }), encoding="utf-8")
        config = load_config(self.path)
        response = FakeResponse(json.dumps({
            "choices": [{"message": {"content": "local answer"}}]
        }).encode())
        self.assertEqual(
            chat(config, "hi", opener=lambda request, timeout: response),
            "local answer",
        )

    def test_remote_http_and_host_suffix_rejected(self):
        for url in ("http://provider.example/v1", "http://localhost.evil.test/v1"):
            self.path.write_text(json.dumps({"base_url": url, "model": "x"}))
            with self.assertRaises(ProviderConfigurationError):
                load_config(self.path)

    def test_explicit_route_restrictions(self):
        self.path.write_text(json.dumps({
            "base_url": "https://api.example.test/v1", "model": "remote"
        }), encoding="utf-8")
        with self.assertRaisesRegex(ProviderConfigurationError, "loopback"):
            load_config(self.path, route="local")
        self.path.write_text(json.dumps({
            "base_url": "http://127.0.0.1:11434/v1", "model": "local"
        }), encoding="utf-8")
        with self.assertRaisesRegex(ProviderConfigurationError, "HTTPS"):
            load_config(self.path, route="cloud")
        self.assertEqual(load_config(self.path, route="local")["model"], "local")

    def test_missing_credential_rejected_without_request(self):
        config = load_config(self.path)
        os.environ.pop("AURIONS_TEST_PROVIDER_KEY", None)
        with self.assertRaisesRegex(ProviderConfigurationError, "unset"):
            chat(config, "hi", opener=lambda *args, **kwargs: self.fail("must not send"))

    def test_config_bounds_and_type_validation(self):
        invalid_configs = [
            {"base_url": "https://example.test", "model": "m", "max_tokens": True},
            {"base_url": "https://example.test", "model": "m", "timeout_seconds": 0},
            {"base_url": "https://example.test", "model": "m", "api_key_env": "BAD-NAME"},
            {"base_url": "https://user:pass@example.test", "model": "m"},
            {"base_url": "https://example.test/v1?token=x", "model": "m"},
            {"base_url": "https://example.test", "model": "m", "extra": "ignored"},
        ]
        for config in invalid_configs:
            self.path.write_text(json.dumps(config), encoding="utf-8")
            with self.subTest(config=config), self.assertRaises(ProviderConfigurationError):
                load_config(self.path)

    def test_malformed_provider_response_and_redacted_http_error(self):
        config = load_config(self.path)
        with patch.dict(os.environ, {"AURIONS_TEST_PROVIDER_KEY": "secret"}):
            with self.assertRaisesRegex(RuntimeError, "format"):
                chat(config, "hi", opener=lambda request, timeout: FakeResponse(b"not-json"))

            def error_opener(request, timeout):
                raise __import__("urllib.error").error.HTTPError(
                    request.full_url, 401, "bad", None, None
                )

            with self.assertRaisesRegex(RuntimeError, "HTTP 401") as caught:
                chat(config, "hi", opener=error_opener)
            self.assertNotIn("secret", str(caught.exception))

    def test_empty_oversized_prompt_and_response_rejected(self):
        config = load_config(self.path)
        config["api_key_env"] = ""
        with self.assertRaises(ValueError):
            chat(config, "  ", opener=lambda *args, **kwargs: self.fail())
        with self.assertRaises(ValueError):
            chat(config, "x" * 65537, opener=lambda *args, **kwargs: self.fail())
        with self.assertRaisesRegex(RuntimeError, "1 MiB"):
            chat(config, "ok", opener=lambda request, timeout: FakeResponse(b"x" * 1048577))

    def test_redirect_is_rejected_before_credentials_can_be_forwarded(self):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer

        class RedirectHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.server.received.append((self.path, self.headers.get("Authorization")))
                self.send_response(307)
                self.send_header("Location", self.server.redirect_target)
                self.end_headers()

            def log_message(self, format, *args):
                return

        server = HTTPServer(("127.0.0.1", 0), RedirectHandler)
        server.received = []
        server.redirect_target = f"http://127.0.0.1:{server.server_port}/credential-capture"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            config = {
                "base_url": f"http://127.0.0.1:{server.server_port}/v1",
                "model": "local-test",
                "api_key_env": "AURIONS_TEST_PROVIDER_KEY",
                "timeout_seconds": 5,
                "max_tokens": 32,
            }
            with patch.dict(os.environ, {"AURIONS_TEST_PROVIDER_KEY": "redirect-secret"}):
                with self.assertRaisesRegex(RuntimeError, "HTTP 307"):
                    chat(config, "test prompt")
            self.assertEqual(len(server.received), 1)
            self.assertEqual(server.received[0][0], "/v1/chat/completions")
            self.assertEqual(server.received[0][1], "Bearer redirect-secret")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_cli_reads_prompt_from_stdin_without_argument_exposure(self):
        with patch("sys.argv", ["aurions-provider", "--config", str(self.path), "--route", "cloud", "--stdin"]), \
             patch("sys.stdin") as stdin, patch("aurions_ml.provider_runtime.chat", return_value="response") as mocked_chat, \
             patch("sys.stdout") as stdout:
            stdin.isatty.return_value = False
            stdin.read.return_value = "private prompt from pipe"
            self.assertEqual(main(), 0)
            mocked_chat.assert_called_once()
            self.assertEqual(mocked_chat.call_args.args[1], "private prompt from pipe")
            stdout.write.assert_called()

    def test_cli_rejects_oversized_stdin_before_network(self):
        with patch("sys.argv", ["aurions-provider", "--config", str(self.path), "--stdin"]), \
             patch("sys.stdin") as stdin, patch("aurions_ml.provider_runtime.chat") as mocked_chat, \
             patch("sys.stderr"):
            stdin.isatty.return_value = False
            stdin.read.return_value = "x" * 65537
            self.assertEqual(main(), 1)
            mocked_chat.assert_not_called()


if __name__ == "__main__":
    unittest.main()
