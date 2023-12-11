# pyright: reportMissingTypeArgument=false
"""
meta_wrapper.py

This module defines the MetaWrapper class, which is responsible for interacting
with the Meta API to retrieve information for specific store items.

Usage:
    To use the MetaWrapper, create an instance by providing the required
    cookie, and then use the `get` method to retrieve information for a
    specific store item.

    Example:
    ```python
    from data.web.meta_wrapper import MetaWrapper

    # Create an instance of MetaWrapper with a valid cookie
    meta_wrapper = MetaWrapper(cookie="your_cookie_here")

    # Use the get method to retrieve information for a specific store item
    response = meta_wrapper.get(store_id="your_store_id_here")
    ```

Attributes:
    API_DOMAIN (str): The base URL for the Meta API.
"""

from http import HTTPStatus
from typing import overload
from urllib.parse import urlencode

from aiohttp import ClientResponse, ClientSession
from typing_extensions import final

from base.base_class import BaseClass
from base.singleton import Singleton
from constants.constants import META_DOMAIN
from data.model.api_models import ApiHeader, ApiPayload
from data.model.meta_response import MetaResponse

API_ENDPOINT = f"{META_DOMAIN}/ocapi/graphql?forced_locale=en_GB"


@final
class MetaWrapper(BaseClass, metaclass=Singleton):
    """
    MetaWrapper class for interacting with the Meta API.

    Attributes:
        _header (ApiHeader): An instance of the ApiHeader class representing
            the headers to be sent with API requests.
        _payload (ApiPayload): An instance of the ApiPayload class representing
            the payload to be sent with API requests.
    """

    def __init__(self, cookie: str, http_session: ClientSession) -> None:
        """
        Initialize a new instance of MetaWrapper.

        Args:
            cookie (str): The cookie to be used in the API request headers.
        """
        super().__init__()
        self._logger.info("Initialising Meta API Wrapper")
        self._session: ClientSession = http_session
        self._header: ApiHeader = ApiHeader(cookie=cookie)
        self._payload: ApiPayload = ApiPayload()

    @overload
    async def get(self, uid: str) -> list[MetaResponse]:
        """
        Get meta information for a single store item.

        Args:
            uid (str): The store item ID.

        Returns:
            list[MetaResponse]: A list containing a single MetaResponse object.
        """
    @overload
    async def get(self, uid: list[str]) -> list[MetaResponse]:
        """
        Get meta information for a list of store items.

        Args:
            uid (list[str]): List of store item IDs.

        Returns:
            list[MetaResponse]: A list of MetaResponse objects.
        """

    async def get(self, uid: list[str] | str) -> list[MetaResponse]:
        """
        Get meta information for one or more store items.

        Args:
            uid (str | list[str]): The store ID or a list of store IDs.

        Returns:
            list[MetaResponse]: A list of MetaResponse objects.
        """
        async def fetch(sid: str) -> MetaResponse:
            self._logger.debug("Fetching %s from Meta API", sid)
            self._header.referrer = f"{META_DOMAIN}/en-gb/experiences/{sid}"
            self._payload.variables.item_id = sid

            resp: ClientResponse = await self._session.post(
                API_ENDPOINT,
                headers=self._header.model_dump(by_alias=True),
                data=urlencode(self._payload.model_dump(by_alias=True)),
            )
            assert resp.status == HTTPStatus.OK
            text = await resp.json(content_type='text/html; charset="utf-8"')
            return MetaResponse.model_validate(text)

        uids: list[str] = [uid] if isinstance(uid, str) else uid

        responses: list[MetaResponse] = []
        for store_id in uids:
            resp: MetaResponse = await fetch(store_id)
            responses.append(resp)
        return responses
