import argparse
import asyncio


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the orchestrator agent.")
    parser.add_argument(
        "--mode",
        choices=("discord", "openclaw", "test"),
        default="discord",
        help="discord: native Discord bot, openclaw: HTTP bridge, test: browser tool smoke test",
    )
    parser.add_argument("--host", default="127.0.0.1", help="OpenClaw bridge host")
    parser.add_argument("--port", type=int, default=8787, help="OpenClaw bridge port")
    args = parser.parse_args()

    if args.mode == "discord":
        from worldistrator.discord_bot import run_discord_bot

        run_discord_bot()
        return

    if args.mode == "openclaw":
        from worldistrator.openclaw_bridge import run_openclaw_bridge

        asyncio.run(run_openclaw_bridge(host=args.host, port=args.port))
        return

    from worldistrator.agent import manage_mee6_permissions

    async def smoke_test() -> None:
        result = await manage_mee6_permissions(
            "Open https://mee6.xyz and confirm whether the dashboard loads."
        )
        print(result)

    asyncio.run(smoke_test())


if __name__ == "__main__":
    main()
