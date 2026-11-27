import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from aurions_ml.provider_runtime import ProviderConfigurationError,chat,load_config
class Response:
 def __init__(self,b): self.b=b
 def __enter__(self): return self
 def __exit__(self,*a): pass
 def read(self,n): return self.b[:n]
class TestProviderRuntime(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/"p.json"
  self.path.write_text(json.dumps({"base_url":"https://api.test/v1","model":"m","api_key_env":"AURIONS_TEST_KEY","timeout_seconds":12,"max_tokens":64}))
 def tearDown(self): self.tmp.cleanup(); os.environ.pop("AURIONS_TEST_KEY",None)
 def test_request_and_auth(self):
  c=load_config(self.path); os.environ["AURIONS_TEST_KEY"]="secret"; captured={}
  def send(req,timeout):
   captured.update(url=req.full_url,headers=req.headers,body=json.loads(req.data),timeout=timeout)
   return Response(b'{"choices":[{"message":{"content":"ok"}}]}')
  self.assertEqual(chat(c,"hello",opener=send),"ok"); self.assertEqual(captured["url"],"https://api.test/v1/chat/completions")
  self.assertEqual(captured["body"]["model"],"m"); self.assertEqual(captured["body"]["messages"],[{"role":"user","content":"hello"}])
  self.assertEqual(captured["headers"]["Authorization"],"Bearer secret"); self.assertEqual(captured["timeout"],12)
 def test_loopback_http(self):
  self.path.write_text('{"base_url":"http://127.0.0.1:11434/v1","model":"local"}')
  c=load_config(self.path); self.assertEqual(chat(c,"hi",opener=lambda *a:Response(b'{"choices":[{"message":{"content":"local"}}]}')),"local")
 def test_reject_nonlocal_http_and_host_suffix(self):
  for u in ["http://example.test","http://localhost.evil.test"]:
   self.path.write_text(json.dumps({"base_url":u,"model":"m"}))
   with self.assertRaises(ProviderConfigurationError): load_config(self.path)
 def test_missing_key_fails_before_send(self):
  with self.assertRaisesRegex(ProviderConfigurationError,"unset"): chat(load_config(self.path),"hi",opener=lambda *a:self.fail("request unexpectedly sent"))
 def test_strict_config_validation(self):
  for c in [{"base_url":"https://x","model":"m","max_tokens":True},{"base_url":"https://x","model":"m","timeout_seconds":float("nan")},{"base_url":"https://x","model":"m","api_key_env":"bad-name"},{"base_url":"https://user:pass@x","model":"m"},{"base_url":"https://x/v1?q=secret","model":"m"},{"base_url":"https://x","model":"m","unknown":1}]:
   self.path.write_text(json.dumps(c))
   with self.subTest(c=c),self.assertRaises(ProviderConfigurationError): load_config(self.path)
 def test_redacted_http_and_bad_response(self):
  c=load_config(self.path)
  with patch.dict(os.environ,{"AURIONS_TEST_KEY":"secret"}):
   with self.assertRaisesRegex(RuntimeError,"format"): chat(c,"hi",opener=lambda *a:Response(b"no-json"))
   def err(*a): raise __import__("urllib.error").error.HTTPError("url",403,"forbidden",None,None)
   with self.assertRaisesRegex(RuntimeError,"HTTP 403") as ctx: chat(c,"hi",opener=err)
   self.assertNotIn("secret",str(ctx.exception))
 def test_limits(self):
  c=load_config(self.path)
  with self.assertRaises(ValueError): chat(c," ")
  with self.assertRaises(ValueError): chat(c,"x"*65537)
  with self.assertRaisesRegex(RuntimeError,"1 MiB"): chat(c,"ok",opener=lambda *a:Response(b"x"*1048577))
if __name__=="__main__": unittest.main()
