"""
meta_wrapper.py

Module providing a singleton wrapper for interacting with the Meta
and Oculus APIs.

Classes:
- MetaWrapper: A singleton class representing a wrapper for the Meta API.
"""
import asyncio
from collections.abc import Generator
from typing import Any

from aiofiles import open as aopen
from aiofiles.os import makedirs, path
from aiohttp import ClientResponse
from pydantic import ValidationError
from typing_extensions import final

from base.base_class import BaseClass
from base.singleton import Singleton
from constants.constants import META_DOMAIN, RESOURCES
from data.model.api_models import (ApiHeader, MetaAppVars, MetaPayload,
                                   MetaSectionVars, OculusPayload,
                                   OculusSectionVars)
from data.model.meta_app import MetaApp
from data.model.meta_models import MetaResource
from data.model.store_section import StoreSection
from data.web.http_client import HttpClient

META_ENDPOINT: str = f"{META_DOMAIN}/ocapi/graphql"
OCULUS_ENDPOINT: str = "https://graph.oculus.com/graphql"
BINARY_TYPE: str = "AndroidBinary"


@final
class MetaWrapper(BaseClass, metaclass=Singleton):  # pyright: ignore[reportMissingTypeArgument]
    """
    A singleton class representing a wrapper for the Meta and Oculus APIs.

    Attributes:
    - `META_ENDPOINT` (str): The endpoint for Meta API.
    - `OCULUS_ENDPOINT` (str): The endpoint for the Oculus API.
    - `BINARY_TYPE` (str): The type of binary, set to "AndroidBinary".
    """

    def __init__(self, cookie: str, http_client: HttpClient) -> None:
        """
        Initializes the MetaWrapper instance.

        Parameters:
        - `cookie` (str): The cookie used for authentication.
        - `http_client` (HttpClient): An instance of the HttpClient class.
        """
        super().__init__()
        self._logger.info("Initializing Meta API Wrapper")
        self._client: HttpClient = http_client
        self._header: ApiHeader = ApiHeader(cookie=cookie)
        self._logos: StoreSection

    async def _async_init(self) -> "MetaWrapper":
        """
        Asynchronously initializes the MetaWrapper instance.

        Returns:
        - `MetaWrapper`: The initialized MetaWrapper instance.
        """
        await self._get_logos()
        return self

    def __await__(self) -> Generator[Any, None, "MetaWrapper"]:
        """
        Asynchronously awaits the initialization of the MetaWrapper instance.

        Returns:
        - Generator: A generator that yields the MetaWrapper instance.
        """
        return self._async_init().__await__()

    async def _get_logos(self) -> None:
        """
        Asynchronously retrieves logos from the Meta and Oculus APIs.
        """
        async def fetch(
            payload: tuple[str, MetaPayload | OculusPayload]
        ) -> StoreSection | None:
            resp: ClientResponse | None = await self._client.post(
                payload[0],
                headers=self._header.model_dump(by_alias=True),
                data=payload[1].url_encode(),
            )
            if resp is None:
                return None
            text = await resp.json(content_type=None)
            try:
                return StoreSection.model_validate(text)
            except ValidationError as e:
                self._logger.info("%s", e)
                return None

        sections: list[tuple[str, MetaPayload | OculusPayload]] = [
            self._get_meta_section("391914765228253", "HOLLYWOOD"),
            self._get_meta_section("3955297897903802", "HOLLYWOOD"),
            self._get_meta_section("731789897435087", "HOLLYWOOD"),
            # PCVR Titles
            # self._meta_section_payload("1736210353282450", "RIFT"),
            self._get_oculus_section("174868819587665"),
            self._get_oculus_section("1888816384764129")
        ]

        results: list[StoreSection | None] = \
            await asyncio.gather(*[fetch(s) for s in sections])

        self._logos = self._merge_sections(results)

    @staticmethod
    def _merge_sections(
        section_list: list[StoreSection | None]
    ) -> StoreSection:
        """
        Merges a list of StoreSection instances.

        Parameters:
        - `section_list` (list[StoreSection | None]): The list of
            StoreSection instances.

        Returns:
        - `StoreSection`: The merged StoreSection instance.
        """
        remove_null: list[StoreSection] = [x for x in section_list if x]
        merged: StoreSection = remove_null[0]
        for i in remove_null[1:]:
            merged.update(i)
        return merged

    @staticmethod
    def _get_meta_section(section: str, hmd: str) -> tuple[str, MetaPayload]:
        """
        Returns a tuple containing Meta API endpoint and payload for a
        given section.

        Parameters:
        - `section` (str): The section ID.
        - `hmd` (str): The HMD type.

        Returns:
        - tuple[str, MetaPayload]: A tuple containing Meta API endpoint and
            payload.
        """
        return META_ENDPOINT, MetaPayload(
            doc_id=6318857928214261,
            variables=MetaSectionVars(section_id=section, hmd_type=hmd)
        )

    @staticmethod
    def _get_oculus_section(section: str) -> tuple[str, OculusPayload]:
        """
        Returns a tuple containing Oculus API endpoint and payload for a
        given section.

        Parameters:
        - `section` (str): The section ID.

        Returns:
        - tuple[str, OculusPayload]: A tuple containing Oculus API endpoint
            and payload.
        """
        return OCULUS_ENDPOINT, OculusPayload(
            doc_id=4743589559102018,
            variables=OculusSectionVars(section_id=section)
        )

    async def get_app(self, uids: list[str]) -> list[MetaApp]:
        """
        Asynchronously retrieves MetaApps for the given list of store IDs.

        Parameters:
        - `uids` (list[str]): The list of store IDs.

        Returns:
        - list[MetaApp]: A list of MetaApp instances.
        """
        payload = MetaPayload(doc_id=7005322839522027, variables=MetaAppVars())

        async def fetch(sid: str) -> MetaApp | None:

            self._logger.debug("Fetching %s from Meta API", sid)
            payload.variables.item_id = sid

            resp: ClientResponse | None = await self._client.post(
                META_ENDPOINT,
                headers=self._header.model_dump(by_alias=True),
                data=payload.url_encode(),
            )
            if resp is None:
                self._logger.info("%s: No response received", sid)
                return None

            text = await resp.json(content_type='text/html; charset="utf-8"')
            try:
                return MetaApp.model_validate(text)
            except ValidationError as e:
                self._logger.info("%s: %s\n%s", sid, e, text)
                return None

        results: list[MetaApp | None] = \
            await asyncio.gather(*[fetch(x) for x in uids])
        return [self._attach_logos(r) for r in results if r]

    def _attach_logos(self, app: MetaApp) -> MetaApp:
        """
        Attaches logos to a MetaApp instance.

        Parameters:
        - `app` (MetaApp): The MetaApp instance.

        Returns:
        - `MetaApp`: The MetaApp instance with attached logos.
        """
        if logos := self._logos.get(app.data.id):
            app.attach_logos(logos)
        return app

    async def get_resources(self, resources: dict[str, MetaResource]) -> None:
        """
        Asynchronously retrieves resources and saves them to the specified
        directory.

        Parameters:
        - `resources` (dict[str, MetaResource]): A dictionary of resource types
            and MetaResource instances.
        """
        for res_type, res in resources.items():
            directory: str = f"{RESOURCES}{res_type}/"
            await makedirs(directory, exist_ok=True)
            if await path.exists(f"{directory}{res}"):
                continue
            if data := await self._client.get(res.url):
                async with aopen(f"{directory}{res}", 'wb') as file:
                    await file.write(await data.read())
