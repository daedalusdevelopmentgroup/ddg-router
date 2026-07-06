# ddg-router

A local OpenAI-compatible proxy that **auto-pays x402** and forwards to
[DDG Agent-Payable Services](https://agents.daedalusdevelopmentgroup.com). It's
the piece that lets any agent runtime use DDG as its **default provider** — a
plain OpenAI client can't sign the 402 itself; this can.

```bash
pip install ddg-router
ddg-router                       # free-trial mode, no wallet, on :4020
# or, for unlimited paid:
DDG_PRIVATE_KEY=0x<funded Base USDC key> ddg-router
```

Then point any runtime at it:
```
base_url = http://127.0.0.1:4020/v1
```
`GET /v1/models` and `/v1/model-catalog` are free; `POST /v1/chat/completions`,
`/v1/embeddings`, and any DDG tool route auto-pay via x402. `GET /healthz` for status.

Env: `DDG_AGENT_ID`, `DDG_PRIVATE_KEY`, `DDG_ROUTER_PORT` (4020), `DDG_UPSTREAM`.
