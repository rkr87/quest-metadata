"""
Module providing an API wrapper for fetching Oculus and OculusDB data.

Classes:
- _RequestVars: Internal class representing request variables.
- _SectionVars: Internal class representing section variables.
- _MetaSection: Internal class representing meta section variables.
- _OculusSection: Internal class representing Oculus section variables.
- _Payload: Internal class representing the payload for GraphQL requests.
- Wrapper: Singleton class for making various API requests.
"""
import asyncio
from collections.abc import Callable
from typing import Any, TypeVar
from urllib.parse import urlencode

from aiofiles.os import path
from aiohttp import ClientResponse
from pydantic import Field, ValidationError
from typing_extensions import final

from base.classes import Singleton
from base.models import BaseModel
from config.app_config import AppConfig
from data.model.oculus.app import OculusApp
from data.model.oculus.app_additionals import AppAdditionalDetails, AppImage
from data.model.oculus.app_package import AppPackage
from data.model.oculus.app_versions import AppVersions
from data.model.oculus.store_section import StoreSection
from data.model.oculusdb.apps import OculusDbApps
from data.web.http_client import HttpClient
from helpers.string import to_camel
from utils.error_manager import ErrorManager

OCULUS: str = "https://graph.oculus.com/graphql"
OCULUSDB: str = "https://oculusdb.rui2015.me/api/v1/allapps"

HEADERS: dict[str, str] = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    "Accept-Language": "en-US;q=0.9,en;q=0.8"
}
RATE_LIMIT: int = 50


class _RequestVars(BaseModel):  # pylint: disable=R0902
    """
    Internal class representing request variables for GraphQL queries.

    Attributes:
    - hmd_type (str | None): The HMD type.
    - id (str | None): The ID.
    - item_id (str | None): The item ID.
    - application_id (str | None): The application ID.
    - params (str | None): Additional parameters.
    - request_pdp_assets_as_png (bool | None): Flag to request PDP assets
        as PNG.
    """
    hmd_type: str | None = None
    id: str | None = None
    item_id: str | None = None
    application_id: str | None = \
        Field(default=None, serialization_alias="applicationID")
    params: str | None = None
    request_pdp_assets_as_png: bool | None = \
        Field(default=None, serialization_alias="requestPDPAssetsAsPNG")

    class Config:
        """
        Configurations:
        - alias_generator: Custom alias generator function to convert field
            names to camelCase.
        - populate_by_name: Config to populate the model by name.
        """
        alias_generator: Callable[..., str] = to_camel
        populate_by_name = True


class _SectionVars(_RequestVars):
    """
    Internal class representing section variables for GraphQL queries.

    Attributes:
    - section_id (str | None): The section ID.
    """
    section_id: str | None = None


class _MetaSection(_SectionVars):
    """
    Internal class representing meta section variables for GraphQL queries.

    Attributes:
    - item_count (int): The item count.
    """
    item_count: int = 10000


class _OculusSection(_SectionVars):
    """
    Internal class representing Oculus section variables for GraphQL queries.

    Attributes:
    - section_item_count (int): The section item count.
    """
    section_item_count: int = 10000


class _Payload(BaseModel):
    """
    Internal class representing the payload for GraphQL requests.

    Attributes:
    - access_token (str): The access token.
    - forced_locale (str): The forced locale.
    - variables (_RequestVars): The request variables.
    - doc_id (int | None): The document ID.
    - doc (str | None): The document.
    - server_timestamps (bool | None): Flag for server timestamps.

    Methods:
    - url_encode: Encode the payload into a URL-encoded string.
    """
    access_token: str = "OC|1076686279105243|"
    forced_locale: str = AppConfig().scrape_locale
    variables: _RequestVars = _RequestVars()

    doc_id: int | None = None
    doc: str | None = None
    server_timestamps: bool | None = None

    def url_encode(self) -> str:
        """
        Encode the payload into a URL-encoded string.

        Returns:
        - str: The URL-encoded payload.

        """
        payload: dict[str, Any] = self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude={"variables"}
        )
        variables: str = self.variables.model_dump_json(
            by_alias=True,
            exclude_none=True
        )
        return f"{urlencode(payload)}&variables={variables}"


@final
class Wrapper(Singleton):
    """
    Singleton class for making various API requests.

    Attributes:
    - _client (HttpClient): The HTTP client instance.

    Methods:
    - _request: Make a GraphQL request.
    - _process_response: Process the HTTP response.
    - _validate_model: Validate the received data against a Pydantic model.
    - get_oculusdb_apps: Get the list of apps from OculusDB.
    - get_store_apps: Get store items from Oculus.
    - _merge_sections: Merge multiple store sections.
    - get_app_versions: Get app versions.
    - get_version_package: Get the app package for a specific version.
    - get_app_additionals: Get additional details for an app.
    - get_app_details: Get details for an app.
    - get_resources: Download resources (app images).
    - _download_resource: Download a resource (app image).
    - _stream_data: Stream data from the HTTP response.
    """

    def __init__(
        self,
        http_client: HttpClient
    ) -> None:
        super().__init__()
        self._logger.info("Initializing API Wrapper")
        self._client: HttpClient = http_client

    _MT = TypeVar("_MT", bound=BaseModel)

    async def _request(
        self,
        payload: _Payload,
        target_model: type[_MT]
    ) -> _MT | None:
        """
        Make a GraphQL request.

        Args:
        - payload (_Payload): The GraphQL payload.
        - target_model (type[_MT]): The target Pydantic model.

        Returns:
        - _MT | None: The validated data or None if an error occurs.
        """
        await asyncio.sleep(1 / RATE_LIMIT)
        resp: ClientResponse | None = await self._client.post(
            OCULUS,
            headers=HEADERS,
            data=payload.url_encode(),
        )
        if (text := await self._process_response(resp, payload)) is None:
            return None
        return self._validate_model(text, target_model)

    async def _process_response(
        self,
        resp: ClientResponse | None,
        payload: _Payload
    ) -> Any:
        """
        Process the HTTP response.

        Args:
        - resp (ClientResponse | None): The HTTP response.
        - payload (_Payload): The GraphQL payload.

        Returns:
        - Any: The processed response data.
        """
        if resp is None:
            return None
        try:
            text = await resp.json(content_type=None)
        except asyncio.TimeoutError as e:
            error: str = ErrorManager().capture(
                e,
                "Reading http request response",
                error_info={
                    "request_info": resp.request_info,
                    "payload": payload.model_dump_json(exclude_none=True)
                }
            )
            self._logger.warning("%s", error)
            return None
        return text

    def _validate_model(
        self,
        text: Any,
        target_model: type[_MT]
    ) -> _MT | None:
        """
        Validate the received data against a Pydantic model.

        Args:
        - text (Any): The received data.
        - target_model (type[_MT]): The target Pydantic model.

        Returns:
        - _MT | None: The validated data or None if validation fails.
        """
        try:
            return target_model.model_validate(text)
        except ValidationError as e:
            error: str = ErrorManager().capture(
                e,
                "Validating http response",
                f"Captured model validation error: {target_model.__name__}",
                {"data": text}
            )
            self._logger.warning("%s", error)
            return None

    async def get_oculusdb_apps(self) -> OculusDbApps:
        """
        Get the list of apps from OculusDB.

        Returns:
        - OculusDbApps: The list of apps from OculusDB.
        """
        self._logger.info("Fetching app list from OculusDB")
        if (resp := await self._client.get(OCULUSDB)) is None:
            return OculusDbApps()
        text = await resp.json(content_type=None)
        data: OculusDbApps = OculusDbApps.model_validate(text)
        return data

    async def get_store_apps(self) -> StoreSection:
        """
        Get store items from Oculus.

        Returns:
        - StoreSection: The store items.
        """
        self._logger.info("Fetching store items from Oculus")
        meta_vars: list[_MetaSection] = [
            _MetaSection(section_id="391914765228253", hmd_type="HOLLYWOOD"),
            _MetaSection(section_id="3955297897903802", hmd_type="HOLLYWOOD"),
            _MetaSection(section_id="731789897435087", hmd_type="HOLLYWOOD"),
            _MetaSection(section_id="1736210353282450", hmd_type="RIFT")
        ]
        ocu_vars: list[_OculusSection] = [
            _OculusSection(section_id="174868819587665"),
            _OculusSection(section_id="1888816384764129")
        ]

        payloads: list[_Payload] = \
            [_Payload(doc_id=6318857928214261, variables=i) for i in meta_vars]

        payloads += \
            [_Payload(doc_id=4743589559102018, variables=i) for i in ocu_vars]

        results: list[StoreSection | None] = await asyncio.gather(
            *[self._request(p, StoreSection) for p in payloads]
        )

        return self._merge_sections(results)

    @staticmethod
    def _merge_sections(sections: list[StoreSection | None]) -> StoreSection:
        """
        Merge multiple store sections.

        Args:
        - sections (list[StoreSection | None]): List of store sections.

        Returns:
        - StoreSection: Merged store section.
        """
        remove_null: list[StoreSection] = [x for x in sections if x]
        merged: StoreSection = remove_null[0]
        for i in remove_null[1:]:
            merged.extend(i, True)
        return merged

    async def get_app_versions(self, app_id: str) -> AppVersions | None:
        """
        Get app versions.

        Args:
        - app_id (str): The ID of the app.

        Returns:
        - AppVersions | None: The app versions.
        """
        payload = _Payload(doc_id=2885322071572384)
        payload.variables.application_id = app_id
        return await self._request(payload, AppVersions)

    async def get_version_package(
        self,
        app_id: str,
        version_code: int
    ) -> AppPackage | None:
        """
        Get the app package for a specific version.

        Args:
        - app_id (str): The ID of the app.
        - version_code (int): The version code.

        Returns:
        - AppPackage | None: The app package.
        """
        payload = _Payload(
            doc="""
                query ($params: AppBinaryInfoArgs!) {
                    app_binary_info(args: $params) {
                        info {binary {... on AndroidBinary {
                            id package_name version_code asset_files {
                                edges {node {... on AssetFile {
                                    file_name uri size}}}}}}}}}"""
        )
        payload.variables.params = \
            '{"app_params":[{"app_id":"%s","version_code":"%i"}]}' \
            % (app_id, version_code)
        return await self._request(payload, AppPackage)

    async def get_app_additionals(
        self,
        app_id: str
    ) -> AppAdditionalDetails | None:
        """
        Get additional details for an app.

        Args:
        - app_id (str): The ID of the app.

        Returns:
        - AppAdditionalDetails | None: Additional details for the app.
        """
        payload = _Payload(doc_id=6771539532935162)
        payload.variables.application_id = app_id
        return await self._request(payload, AppAdditionalDetails)

    async def get_app_details(self, app_id: str) -> OculusApp | None:
        """
        Get details for an app.

        Args:
        - app_id (str): The ID of the app.

        Returns:
        - OculusApp | None: Details for the app.
        """
        payload = _Payload(doc_id=7005322839522027)
        payload.variables.item_id = app_id
        payload.variables.hmd_type = "HOLLYWOOD"
        payload.variables.request_pdp_assets_as_png = False
        return await self._request(payload, OculusApp)

    async def get_resources(
        self,
        app_images: list[AppImage]
    ) -> list[AppImage]:
        """
        Download resources (app images) asynchronously.

        Args:
        - app_images (list[AppImage]): A list of AppImage instances.

        Returns:
        - list[AppImage]: A list of AppImage instances with downloaded data.
        """
        result: list[AppImage | None] = await asyncio.gather(
            *[self._download_resource(res) for res in app_images]
        )
        return [i for i in result if i is not None]

    async def _download_resource(self, res: AppImage) -> AppImage | None:
        """
        Download a resource (app image) asynchronously.

        Args:
        - res (AppImage): An AppImage instance.

        Returns:
        - AppImage: The AppImage instance with downloaded data.
        """
        if await path.exists(
            f"{AppConfig().resource_path}/{res.type}/{res.name}"
        ):
            return None
        await asyncio.sleep(1 / RATE_LIMIT)
        if (data := await self._client.get(res.url)) is None:
            return res
        if (stream := await self._stream_data(data, res)) is None:
            return res
        res.data = stream
        return res

    async def _stream_data(
        self,
        data: ClientResponse,
        res: AppImage
    ) -> bytes | None:
        """
        Stream data from the HTTP response.

        Args:
        - data (ClientResponse): The HTTP response.
        - res (AppImage): An AppImage instance.

        Returns:
        - bytes | None: The streamed data or None if an error occurs.
        """
        try:
            stream: bytes = await data.read()
        except asyncio.TimeoutError as e:
            error: str = ErrorManager().capture(
                e,
                "Downloading image data",
                error_info={
                    "request": data.request_info,
                    "image_details": res.model_dump(exclude_none=True)
                }
            )
            self._logger.warning("%s", error)
            return None
        return stream
