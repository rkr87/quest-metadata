from typing import Any

from playwright.sync_api._generated import Playwright

class PlaywrightContextManager:
    def __init__(self) -> None:
        ...
    def __enter__(self) -> Playwright:
        ...
    def start(self) -> Playwright:
        ...
    def __exit__(self, *args: Any) -> None:
        ...
