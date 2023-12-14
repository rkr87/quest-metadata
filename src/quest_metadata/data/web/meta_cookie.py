"""
meta_cookie.py

This module defines the MetaCookie class, responsible for fetching and
returning the required cookie for interacting with the Meta API.

Usage:
    To use the MetaCookie, call the `fetch` method, which opens a browser,
    navigates to the Meta domain, handles cookie consent, and waits until the
    required 'gu' cookie is available.

    Example:
    ```python
    from data.web.meta_cookie import MetaCookie

    # Fetch the required Meta cookie
    meta_cookie = MetaCookie.fetch()

    # Use the obtained cookie for Meta API requests
    print(meta_cookie)
    ```

Attributes:
    META_DOMAIN (str): The base URL of the Meta domain.
"""
import asyncio
from logging import Logger, getLogger

from playwright._impl._api_structures import SetCookieParam
from playwright.async_api import async_playwright
from playwright.async_api._generated import (Browser, BrowserContext, Page,
                                             Response)
from typing_extensions import final

from base.non_instantiable import NonInstantiable
from constants.constants import META_DOMAIN

REQ_COOKIE = 'gu'
TIMEOUT_SECONDS = 20


@final
class MetaCookie(NonInstantiable):
    """
    MetaCookie class for fetching the required cookie for interacting with the
    Meta API.

    Attributes:
        _launch_method (str): The method to be used for creating instances.
    """
    _launch_method = "fetch"

    @staticmethod
    async def fetch() -> str:
        """
        Fetch the required cookie for interacting with the Meta API.

        Returns:
            str: The formatted cookie string.
        """
        logger: Logger = getLogger(__name__)
        logger.info("Acquiring cookies from meta.com")

        async with async_playwright() as p:
            browser: Browser = await p.chromium.launch()
            context: BrowserContext = await browser.new_context()
            locale: SetCookieParam = {
                "name": "locale",
                "value": "en_GB",
                "domain": ".www.meta.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "sameSite": "None"
            }
            await context.add_cookies([locale])
            page: Page = await context.new_page()
            await page.goto(META_DOMAIN)

            await MetaCookie._handle_cookie_consent(page)
            await MetaCookie._wait_for_cookie(context)
            return await MetaCookie._get_cookie_string(context)

    @staticmethod
    async def _handle_cookie_consent(page: Page) -> None:
        """
        Handle the cookie consent on the Meta page.

        Args:
            page (Page): The Playwright Page instance.
        """
        page_content: str = await page.content()
        logger: Logger = getLogger(__name__)
        logger.info(page_content)

        # consent: ElementHandle | None = await page.wait_for_selector(
        #     "text=Allow all cookies"
        # )
        # if consent is not None:
        #     await consent.click(force=True)

    @staticmethod
    async def _wait_for_cookie(context: BrowserContext) -> None:
        """
        Wait for the required cookie to be available within a specified
        timeout.

        Args:
            context (BrowserContext): The Playwright BrowserContext instance.
        """
        cookie_found = asyncio.Event()

        async def wait_for_cookie(response: Response) -> None:  # pylint: disable=W0613
            """
            Callback function to be triggered on each response.

            Args:
                response (Response): The Playwright Response instance.
            """
            cookies = await context.cookies()
            if REQ_COOKIE in [c.get('name') for c in cookies]:
                cookie_found.set()

        context.on("response", wait_for_cookie)
        await asyncio.wait_for(cookie_found.wait(), TIMEOUT_SECONDS)

    @staticmethod
    async def _get_cookie_string(context: BrowserContext) -> str:
        """
        Retrieve and format the cookie string.

        Args:
            context (BrowserContext): The Playwright BrowserContext instance.

        Returns:
            str: The formatted cookie string.
        """
        cookies = await context.cookies()
        return ";".join([f"{c.get('name')}={c.get('value')}" for c in cookies])
