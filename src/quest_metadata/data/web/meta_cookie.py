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

from playwright.async_api import async_playwright
from playwright.async_api._generated import Response
from typing_extensions import final

from base.non_instantiable import NonInstantiable
from constants.constants import META_DOMAIN

REQ_COOKIE = 'gu'


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
            str: The obtained cookie.
        """
        logger: Logger = getLogger(__name__)
        logger.info("Acquiring cookies from meta.com")
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(META_DOMAIN)
            consent = await page.wait_for_selector("text=Allow all cookies")
            if consent is not None:
                await consent.click(force=True)

            cookie_found = asyncio.Event()

            async def wait_for_cookie(response: Response) -> None:  # pylint: disable=W0613
                cookies = await context.cookies()
                if REQ_COOKIE in [c.get('name') for c in cookies]:
                    cookie_found.set()

            page.on("response", wait_for_cookie)

            await asyncio.wait_for(cookie_found.wait(), 20)

            cookie_jar = await context.cookies()

            cookies: str = ";".join(
                [f"{c['name']}={c['value']}" for c in cookie_jar]
            )
            return cookies
