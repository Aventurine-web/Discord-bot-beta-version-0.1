"""
Optional bridge for an OpenClaw gateway.

Run with: python main.py --mode openclaw

Requires a running OpenClaw gateway and the openclaw-sdk package.
The gateway can route Discord messages to this agent through HTTP.
"""

import os

from dotenv import load_dotenv

load_dotenv()


async def run_openclaw_bridge(host: str = "127.0.0.1", port: int = 8787) -> None:
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        import uvicorn
    except ImportError as exc:
        raise RuntimeError(
            'Install OpenClaw bridge dependencies with: pip install "openclaw-sdk[fastapi]"'
        ) from exc

    from worldistrator.service import run_worldistrator

    app = FastAPI(title="Worldistrator OpenClaw Bridge")

    class ChatRequest(BaseModel):
        user_id: str
        session_id: str
        message: str

    class ChatResponse(BaseModel):
        reply: str

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "agent": "worldistrator"}

    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        reply = await run_worldistrator(
            user_id=request.user_id,
            session_id=request.session_id,
            message=request.message,
        )
        return ChatResponse(reply=reply)

    gateway_url = os.getenv("OPENCLAW_GATEWAY_WS_URL", "ws://127.0.0.1:18789/gateway")
    print(
        "Worldistrator OpenClaw bridge listening on "
        f"http://{host}:{port}/chat (gateway: {gateway_url})"
    )
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
