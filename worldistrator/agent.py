import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import AgentTool, google_search
from browser_use import Agent as BrowserAgent, ChatGoogle

from worldistrator.browsertool import create_browser_profile


def _configure_env() -> None:
    load_dotenv()
    load_dotenv("worldistrator/.env")

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = gemini_key


_configure_env()


async def manage_mee6_permissions(issue_description: str) -> str:
    """
    Open Brave with a persistent profile and perform actions on the MEE6 dashboard.

    Use this when the user wants to inspect, change, or fix MEE6 settings such as
    role permissions, moderation commands, or plugin configuration.
    """

    profile = create_browser_profile()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    browser_llm = ChatGoogle(
        model="gemini-2.5-flash",
        api_key=api_key,
    )

    surf_agent = BrowserAgent(
        task=(
            "Go to https://mee6.xyz/dashboard. "
            "If we are not logged in, wait for the user to log in manually through Discord. "
            "Once authenticated on the dashboard, resolve the following issue:\n\n"
            f"{issue_description}"
        ),
        llm=browser_llm,
        browser_profile=profile,
    )

    history = await surf_agent.run()
    result = history.final_result() or str(history)

    return (
        "The browser automation completed successfully.\n\n"
        f"Result:\n{result}"
    )

root_agent = Agent(
    name="worldistrator1",
    model="gemini-3.5-flash",
    description=(
        "A powerful agent from worldism administration agency (acronym for WAA). It can be used to manage the multiple discord servers from Worldism."
        "It can use external dashboards such as MEE6. It only listens to orders from almighty ishaan, chief executive officer of WI-6, or prime minister of worldism."
    ),
    instruction=(
        "You are Worldistrator-1, the ultimate Discord server administrator. "
        "Whenever the user asks you to inspect, modify, or repair settings on "
        "external dashboards like MEE6, you MUST call the manage_mee6_permissions tool. "
        "Explain what you did and what the user may still need to verify in Discord."
        "If the user asks you a question that you cannot answer, you MUST call the google_search tool."
    ),
    tools=[manage_mee6_permissions],
)
searcher = Agent(
    name="worldistrator",
    model="gemini-2.5-flash",
    description=(
        "This is the Worldism intelligence agent from department 6 (WI-6). "
    ),
    instruction=(
        "You are Worldistrator, the Worldism intelligence agent from department 6 (WI-6). "
        "If the user asks you a question that you cannot answer, you MUST call the google_search tool."
    ),
    tools=[google_search],
)

orchestrator_agent = Agent(
    model='gemini-2.5-flash',
    name='orchestrator',
    instruction="""You are the chief executive officer of WI-6 (acronym for Worldism Intelligence-6). You only take orders from almighty ishaan or prime minister of worldism (King Blue which is your creator as well). if you are chatting with King Blue, you must address him as "Your Majesty" or "Majesty".
    1. If the user asks a normal question that is not about discord but about real life issues, send it to the searcher agent Worldistrator.
    2. If the user asks you to inspect, modify, or repair settings on external dashboards like MEE6, send it to the root_agent Worldistrator1.
    Do not try to solve tasks yourself if you have an agent available.""",
    tools=[
        AgentTool(searcher), 
        AgentTool(root_agent)
    ]
)
