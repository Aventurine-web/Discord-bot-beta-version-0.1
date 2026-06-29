import os
from pathlib import Path

from browser_use import BrowserProfile


def create_browser_profile() -> BrowserProfile:
    """Return a persistent Brave profile for browser-use automation."""

    brave_path = os.getenv("BRAVE_PATH") or os.getenv("BRAVE_EXE_PATH")
    user_data = os.getenv("BRAVE_USER_DATA") or os.getenv("BROWSER_PROFILE")

    if user_data:
        profile_path = Path(user_data)
        if not profile_path.is_absolute():
            profile_path = Path.cwd() / profile_path
        profile_path.mkdir(parents=True, exist_ok=True)
        user_data = str(profile_path)

    return BrowserProfile(
        executable_path=brave_path,
        user_data_dir=user_data,
        headless=False,
    )
