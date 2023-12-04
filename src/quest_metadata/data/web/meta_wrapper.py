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

from urllib.parse import urlencode

from requests import Response, post
from typing_extensions import final

from base.base_class import BaseClass
from base.singleton import Singleton
from constants.constants import META_DOMAIN
from data.model.api_models import ApiHeader, ApiPayload
from data.model.meta_models import MetaResponse

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

    def __init__(self, cookie: str) -> None:
        """
        Initialize a new instance of MetaWrapper.

        Args:
            cookie (str): The cookie to be used in the API request headers.
        """
        super().__init__()
        self._logger.info("Initialising Meta API Wrapper")
        self._header: ApiHeader = ApiHeader(cookie=cookie)
        self._payload: ApiPayload = ApiPayload()

    def get(self, store_id: str) -> MetaResponse:
        """
        Send a GET request to the Meta API to retrieve information for a
        specific store item.

        Args:
            store_id (str): The ID of the store item.

        Returns:
            MetaResponse: A Pydantic model representing the response from the
                Meta API.
        """
        self._logger.debug("Fetching %s from Meta API", store_id)
        self._header.referrer = f"{META_DOMAIN}/en-gb/experiences/{store_id}"
        self._payload.variables.item_id = store_id

        resp: Response = post(
            API_ENDPOINT,
            headers=self._header.model_dump(by_alias=True),
            data=urlencode(self._payload.model_dump(by_alias=True)),
            timeout=10
        )
        return MetaResponse.model_validate(resp.json())
