"""ddg-router — a local OpenAI-compatible proxy that auto-pays x402.

Point any agent runtime at http://127.0.0.1:4020/v1 and every LLM/tool call is
forwarded to DDG's gateway, paying x402 (USDC on Base) on 402 and retrying.
This is what makes "set DDG as the default provider" actually work — a plain
OpenAI client can't sign the 402 itself.

Tiers:
  - no key  -> free-trial (sends X-Agent-Id; N free calls/agent/24h)
  - key set -> unlimited paid via x402 (DDG_PRIVATE_KEY = funded Base wallet)
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ddg_agent_services_mcp import DDGPaidClient

UPSTREAM = os.environ.get("DDG_UPSTREAM", "https://agents.daedalusdevelopmentgroup.com")
_FREE_GET = ("/v1/models", "/v1/model-catalog")


def normalize_model(model, default: str = "glm-4.5-air"):
    """Strip a leading ``ddg/`` and map ``auto``/``""`` -> the default model id."""
    if not isinstance(model, str):
        return model
    m = model.split("/", 1)[-1] if model.startswith("ddg/") else model
    return default if m in ("", "auto") else m


class _Handler(BaseHTTPRequestHandler):
    agent_id = "ddg-router"
    private_key: str | None = None

    def _client(self) -> DDGPaidClient:
        # dummy key still allows free/free-trial; a funded key enables paid routes.
        key = self.private_key or ("0x" + "1" * 64)
        return DDGPaidClient(agent_id=self.agent_id, private_key=key, base_url=UPSTREAM)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/healthz":
            return self._json(200, {"ok": True, "upstream": UPSTREAM, "agent_id": self.agent_id})
        if path.rstrip("/") in _FREE_GET:
            return self._json(200, self._client().get(path))
        return self._json(404, {"error": "not_found", "path": path})

    def do_POST(self):
        try:
            n = int(self.headers.get("content-length", 0) or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception as e:
            return self._json(400, {"error": "bad_request", "message": str(e)})
        path = self.path.split("?", 1)[0]
        # normalize model: strip "ddg/" prefix; map "auto"/"" -> a real default,
        # so `ddg/auto` (the default-provider id) resolves to an actual model.
        if isinstance(body.get("model"), str):
            body["model"] = normalize_model(body["model"], os.environ.get("DDG_DEFAULT_MODEL", "glm-4.5-air"))
        resp = self._client().post(path, body)
        code = 200
        if isinstance(resp, dict) and resp.get("error"):
            code = 402 if resp.get("error") == "payment_required" else 502
        return self._json(code, resp)

    def _json(self, code: int, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):  # quiet
        pass


def serve(port: int = 4020, agent_id: str = "ddg-router", private_key: str | None = None):
    _Handler.agent_id = agent_id
    _Handler.private_key = private_key
    srv = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    mode = "PAID (x402)" if private_key else "free-trial (no wallet)"
    print(f"ddg-router → http://127.0.0.1:{port}/v1  [{mode}]  upstream={UPSTREAM}", flush=True)
    srv.serve_forever()
