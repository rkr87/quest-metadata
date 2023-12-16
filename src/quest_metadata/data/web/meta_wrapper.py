"""
meta_wrapper.py
This module defines the MetaWrapper class, responsible for interacting
with the Meta API to retrieve information for specific store items.

Usage:
    To use MetaWrapper, create an instance by providing the required
    cookie, and then use the `get` method to retrieve information for a
    specific store item.

    Example:
    ```python
    from data.web.meta_wrapper import MetaWrapper
    # Create an instance of MetaWrapper with a valid cookie
    meta_wrapper = MetaWrapper(cookie=..., http_client=...)
    # Use the get method to retrieve information for a specific store item
    response = await meta_wrapper.get(uids=["your_store_id_here"])
    ```

Attributes:
    API_ENDPOINT (str): The base URL for the Meta API.
"""

from urllib.parse import urlencode

from aiohttp import ClientResponse
from typing_extensions import final

from base.base_class import BaseClass
from base.singleton import Singleton
from constants.constants import META_DOMAIN
from data.model.api_models import ApiHeader, ApiPayload
from data.model.meta_response import MetaResponse
from data.web.http_client import HttpClient

API_ENDPOINT = f"{META_DOMAIN}/ocapi/graphql?forced_locale=en_GB"


@final
class MetaWrapper(BaseClass, metaclass=Singleton):  # pyright: ignore[reportMissingTypeArgument]
    """
    MetaWrapper class for interacting with the Meta API.

    Attributes:
        _header (ApiHeader): An instance of the ApiHeader class representing
            the headers to be sent with API requests.
        _payload (ApiPayload): An instance of the ApiPayload class representing
            the payload to be sent with API requests.
    """

    def __init__(self, cookie: str, http_client: HttpClient) -> None:
        """
        Initialize a new instance of MetaWrapper.

        Args:
            cookie (str): The cookie to be used in the API request headers.
            http_client (HttpClient): An instance of the HttpClient class used
                for making HTTP requests to the Meta API.
        """
        super().__init__()
        self._logger.info("Initializing Meta API Wrapper")
        self._client: HttpClient = http_client
        self._header: ApiHeader = ApiHeader(cookie=cookie)
        self._payload: ApiPayload = ApiPayload()

    async def get(self, uids: list[str]) -> list[MetaResponse]:
        """
        Get meta information for a list of store items.

        Args:
            uids (list[str]): A list of store IDs.

        Returns:
            list[MetaResponse]: A list of MetaResponse objects.
        """
        async def fetch(sid: str) -> MetaResponse | None:
            """
            Fetch meta information for a specific store item.

            Args:
                sid (str): The store item ID.

            Returns:
                MetaResponse | None: A MetaResponse object or None if not
                    found.
            """
            self._logger.debug("Fetching %s from Meta API", sid)
            self._header.referrer = f"{META_DOMAIN}/en-gb/experiences/{sid}"
            self._payload.variables.item_id = sid

            resp: ClientResponse | None = await self._client.post(
                API_ENDPOINT,
                headers=self._header.model_dump(by_alias=True),
                data=urlencode(self._payload.model_dump(by_alias=True)),
            )
            if resp is None:
                return None

            text = await resp.json(content_type='text/html; charset="utf-8"')
            return MetaResponse.model_validate(text)

        return [y for x in uids if (y := await fetch(x))]
