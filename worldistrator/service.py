from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.utils.context_utils import Aclosing
from google.genai import types

from worldistrator.agent import orchestrator_agent

APP_NAME = "worldistrator"
_runner = Runner(
    agent=orchestrator_agent,
    app_name=APP_NAME,
    artifact_service=InMemoryArtifactService(),
    session_service=InMemorySessionService(),
    memory_service=InMemoryMemoryService(),
    auto_create_session=True,
)


async def run_worldistrator(
    user_id: str,
    session_id: str,
    message: str,
) -> str:
    """Send a message to the ADK agent and return the final text reply."""

    content = types.Content(role="user", parts=[types.Part(text=message)])
    replies: list[str] = []

    async with Aclosing(
        _runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        )
    ) as event_stream:
        async for event in event_stream:
            if not event.content or not event.content.parts:
                continue
            if event.author != orchestrator_agent.name:
                continue

            text = "".join(part.text or "" for part in event.content.parts)
            if text:
                replies.append(text)

    if replies:
        return replies[-1]

    return "I finished processing your request, but I did not produce a text reply."
