from playwright._impl._api_structures import Cookie as BrowserCookie
from playwright.sync_api._context_manager import PlaywrightContextManager
from playwright.sync_api._generated import BrowserContext

ChromiumBrowserContext = BrowserContext
Cookie: BrowserCookie

def sync_playwright() -> PlaywrightContextManager:
    ...
