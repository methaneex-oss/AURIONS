"""Configurable OpenAI-compatible local/hosted model inference (stdlib only)."""
from __future__ import annotations
import argparse, json, math, os, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path

class ProviderConfigurationError(ValueError): pass

def load_config(path: Path):
    try: raw=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as e: raise ProviderConfigurationError("cannot read provider config JSON") from e
    allowed={"base_url","model","api_key_env","timeout_seconds","max_tokens"}
    if not isinstance(raw,dict): raise ProviderConfigurationError("provider config must be a JSON object")
    if raw.keys()-allowed: raise ProviderConfigurationError("provider config contains unknown fields")
    if not {"base_url","model"}<=raw.keys(): raise ProviderConfigurationError("config requires base_url and model")
    url,model=raw["base_url"],raw["model"]
    if not isinstance(url,str) or not isinstance(model,str) or not url.strip() or not model.strip(): raise ProviderConfigurationError("base_url and model must be non-empty strings")
    if any(ord(c)<32 for c in url+model): raise ProviderConfigurationError("control characters are forbidden")
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme not in {"https","http"} or not parsed.hostname or parsed.username or parsed.password: raise ProviderConfigurationError("base_url must be valid HTTP(S) without embedded credentials")
    if parsed.query or parsed.fragment: raise ProviderConfigurationError("base_url cannot contain query or fragment")
    if parsed.scheme=="http" and parsed.hostname not in {"localhost","127.0.0.1","::1"}: raise ProviderConfigurationError("HTTP is allowed only for loopback local providers")
    key_env=raw.get("api_key_env","")
    if not isinstance(key_env,str) or (key_env and not key_env.isidentifier()): raise ProviderConfigurationError("api_key_env must be an environment variable name")
    timeout=raw.get("timeout_seconds",45); tokens=raw.get("max_tokens",512)
    if isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or not math.isfinite(timeout) or not 1<=timeout<=180: raise ProviderConfigurationError("timeout_seconds must be finite and between 1 and 180")
    if isinstance(tokens,bool) or not isinstance(tokens,int) or not 1<=tokens<=8192: raise ProviderConfigurationError("max_tokens must be an integer from 1 to 8192")
    return {"base_url":url.rstrip("/"),"model":model.strip(),"api_key_env":key_env,"timeout_seconds":timeout,"max_tokens":tokens}

def chat(config,prompt,*,opener=None):
    if not isinstance(prompt,str) or not prompt.strip(): raise ValueError("prompt must be non-empty")
    if len(prompt.encode("utf-8"))>65536: raise ValueError("prompt exceeds 65536 UTF-8 bytes")
    env=config["api_key_env"]; key=os.environ.get(env,"") if env else ""
    if env and not key: raise ProviderConfigurationError(f"credential environment variable is unset: {env}")
    payload=json.dumps({"model":config["model"],"messages":[{"role":"user","content":prompt}],"max_tokens":config["max_tokens"]}).encode()
    req=urllib.request.Request(config["base_url"]+"/chat/completions",data=payload,headers={"Content-Type":"application/json","Accept":"application/json",**({"Authorization":"Bearer "+key} if key else {})},method="POST")
    try:
        with (opener or urllib.request.urlopen)(req,timeout=config["timeout_seconds"]) as response: raw=response.read(1048577)
    except urllib.error.HTTPError as e: raise RuntimeError(f"provider returned HTTP {e.code}") from None
    except (urllib.error.URLError,TimeoutError,OSError) as e: raise RuntimeError(f"provider request failed: {type(e).__name__}") from None
    if len(raw)>1048576: raise RuntimeError("provider response exceeded 1 MiB")
    try: text=json.loads(raw.decode("utf-8"))["choices"][0]["message"]["content"]
    except (UnicodeDecodeError,json.JSONDecodeError,KeyError,IndexError,TypeError): raise RuntimeError("provider response did not match chat-completions format") from None
    if not isinstance(text,str): raise RuntimeError("provider response content was not text")
    return text

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--config",type=Path,required=True); p.add_argument("--prompt",required=True); a=p.parse_args()
    try: output=chat(load_config(a.config),a.prompt)
    except (ProviderConfigurationError,RuntimeError,ValueError) as e: print("aurions-provider: "+str(e),file=sys.stderr); return 1
    print(output); return 0
if __name__=="__main__": raise SystemExit(main())
