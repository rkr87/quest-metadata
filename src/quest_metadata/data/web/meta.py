from time import sleep
from typing import Callable
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright
from pydantic import BaseModel, Field
from requests import Response, post
from typing_extensions import Literal, final

from base.singleton import Singleton
from data.model.meta_response import MetaResponse
from utils.string_helper import (  # pylint: disable=wrong-import-order; Figure this shit out..
    to_camel, to_kebab)

WEB_DOMAIN = "https://www.meta.com"
API_DOMAIN = "https://www.meta.com/ocapi/graphql?forced_locale=en_GB"


class _ApiPayloadVariables(BaseModel):
    """
    TODO
    """
    item_id: str | None = None
    hmd_type: Literal["HOLLYWOOD"] = "HOLLYWOOD"
    request_pdp_assets_as_png: Literal["false"] = Field(
        alias="requestPDPAssetsAsPNG", default="false"
    )

    class Config:
        """
        TODO
        """
        alias_generator: Callable[..., str] = to_camel


class _ApiPayload(BaseModel):
    """
    TODO
    """
    variables: _ApiPayloadVariables = _ApiPayloadVariables()
    doc_id: Literal[7005322839522027] = 7005322839522027


class _Header(BaseModel):
    """
    TODO
    """
    user_agent: str = '"Google Chrome";v="119", ' + \
        '"Chromium";v="119", "Not?A_Brand";v="24"'
    content_type: str = "application/x-www-form-urlencoded"
    accept_language: str = "en-GB,en-US;q=0.9,en;q=0.8"
    accept: str = "*/*"
    authority: str = "www.meta.com"
    origin: str = WEB_DOMAIN
    referrer: str = WEB_DOMAIN
    cookie: str | None

    class Config:
        """
        TODO
        """
        alias_generator: Callable[..., str] = to_kebab


@final
class MetaWrapper(metaclass=Singleton):  # pyright: ignore[reportMissingTypeArgument]; pylint: disable=line-too-long
    """
    MetaScraper class for scraping metadata from meta.com.
    """

    def __init__(self) -> None:
        """
        Initialize MetaScraper with headers and payload.
        """
        self._header: _Header = _Header(cookie=self._get_cookie())
        self._payload: _ApiPayload = _ApiPayload()

    def _get_cookie(self) -> str:
        """
        Retrieve and return cookies for meta.com.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto(WEB_DOMAIN)
            consent = page.wait_for_selector("text=Allow all cookies")
            sleep(2)
            if consent is not None:
                consent.click(force=True)
            while 'gu' not in [c['name'] for c in context.cookies()]:
                sleep(1)
            cookies: str = ";".join(
                [f"{c['name']}={c['value']}" for c in context.cookies()]
            )
            return cookies

    def get(self, store_id: str) -> MetaResponse:
        """
        Scrape metadata for the specified store ID
        and save the result to a JSON file.
        """
        self._header.referrer = f"{WEB_DOMAIN}/en-gb/experiences/{store_id}"
        self._payload.variables.item_id = store_id

        resp: Response = post(
            API_DOMAIN,
            headers=self._header.model_dump(by_alias=True),
            data=urlencode(self._payload.model_dump(by_alias=True)),
            timeout=10
        )
        return MetaResponse.model_validate(resp.json())
