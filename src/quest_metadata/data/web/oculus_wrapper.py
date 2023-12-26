"""
Module providing a wrapper for interacting with OculusDB
and GraphQL for Oculus apps.

Classes:
- OculusWrapper: Singleton class for handling interactions
    with OculusDB and GraphQL.
"""
from aiohttp import ClientResponse
from typing_extensions import final

from base.base_class import BaseClass
from base.singleton import Singleton
from data.model.oculus_models import BinaryPackage, LatestBinary, OculusApps
from data.web.http_client import HttpClient

OCULUSDB: str = "https://oculusdb.rui2015.me/api/v1/allapps"

OCULUS_GRAPH: str = "https://graph.oculus.com/graphql?access_token=OC|1317831034909742|"

BINARY_TYPE: str = "AndroidBinary"


@final
class OculusWrapper(BaseClass, metaclass=Singleton):  # pyright: ignore[reportMissingTypeArgument]
    """
    Singleton class for handling interactions with OculusDB and
    GraphQL for Oculus apps.

    Attributes:
    - OCULUSDB (str): The URL for the OculusDB API.
    - OCULUS_GRAPH (str): The URL for the Oculus GraphQL API.
    - BINARY_TYPE (str): The type of binary for Android.
    """

    def __init__(self, http_client: HttpClient) -> None:
        """
        Initialize the OculusWrapper instance.

        Parameters:
        - http_client (HttpClient): An instance of the HttpClient
            for making HTTP requests.
        """
        super().__init__()
        self._logger.info("Initializing OculusDB Wrapper")
        self._client: HttpClient = http_client

    async def get_oculus_apps(self) -> OculusApps:
        """
        Fetches the list of Oculus apps from OculusDB.

        Returns:
        - OculusApps: An instance of OculusApps containing
            the list of Oculus apps.
        """
        self._logger.info("Fetching app update list from OculusDB")
        if (resp := await self._client.get(OCULUSDB)) is None:
            return OculusApps()
        text = await resp.json(content_type=None)
        data: OculusApps = OculusApps.model_validate(text)
        return data

    async def get_version(self, app_id: str) -> int | None:
        """
        Retrieves the version code for a given app ID.

        Parameters:
        - app_id (str): The ID of the Oculus app.

        Returns:
        - int | None: The version code of the app if available,
            None otherwise.
        """
        doc: int = 3828663700542720
        resp: ClientResponse | None = await self._client.get(
            f"{OCULUS_GRAPH}&" +
            f"doc_id={doc}&" +
            f"variables={{\"applicationID\":\"{app_id}\"}}"
        )

        if resp:
            text = await resp.json(content_type=None)
            binary: LatestBinary = LatestBinary.model_validate(text)
            if binary.type_name == BINARY_TYPE:
                return binary.version_code
        return None

    async def get_package(
        self,
        app_id: str,
        version_code: int
    ) -> str | None:
        """
        Retrieves the package name for a given app ID and version code.

        Parameters:
        - app_id (str): The ID of the Oculus app.
        - version_code (int): The version code of the app.

        Returns:
        - str | None: The package name of the app if available, None otherwise.
        """
        query = """
            query ($params: AppBinaryInfoArgs!) {
                app_binary_info(args: $params) {
                    info {binary {... on AndroidBinary {
                        id package_name version_code asset_files {
                            edges {node {... on AssetFile {
                                file_name uri size
            }}}}}}}}}"""
        params = '''
            {"params":{
            "app_params":[
                {"app_id":"%s","version_code":"%i"}
            ]}}''' % (app_id, version_code)
        resp: ClientResponse | None = await self._client.get(
            f"{OCULUS_GRAPH}&doc={query}&variables={params}"
        )
        if resp:
            text = await resp.json(content_type=None)
            package: BinaryPackage = BinaryPackage.model_validate(text)
            return package.package_name
        return None
