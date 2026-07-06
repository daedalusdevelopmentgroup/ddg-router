import argparse
import os
from ddg_router.server import serve

def main() -> None:
    p = argparse.ArgumentParser(prog="ddg-router", description="Local OpenAI-compatible x402-paying proxy for DDG.")
    p.add_argument("--port", type=int, default=int(os.environ.get("DDG_ROUTER_PORT", "4020")))
    p.add_argument("--agent-id", default=os.environ.get("DDG_AGENT_ID", "ddg-router"))
    p.add_argument("--private-key", default=os.environ.get("DDG_PRIVATE_KEY"))
    a = p.parse_args()
    serve(port=a.port, agent_id=a.agent_id, private_key=a.private_key)

if __name__ == "__main__":
    main()
