"""
Models for handling variables, payloads, and headers in an API.

This module defines Pydantic models for representing variables, payloads,
and headers used in API requests. It includes base classes for variable and
payload models, as well as specific models for the MetaApp, MetaSection,
OculusSection, MetaPayload, OculusPayload, and API headers.
"""
from collections.abc import Callable
from typing import Any
from urllib.parse import urlencode

from pydantic import Field
from typing_extensions import Literal

from base.base_model import BaseModel
from utils.string_utils import to_camel, to_kebab


class BaseVarsModel(BaseModel):
    """
    Base class for variable models.
    """
    class Config:
        """
        Pydantic model configuration.

        Config:
            alias_generator (Callable[..., str]): The alias generator for
                attribute names.
            populate_by_name (bool): Whether to populate the model's fields
            based on attribute names.
        """
        alias_generator: Callable[..., str] = to_camel
        populate_by_name = True


class MetaAppVars(BaseVarsModel):
    """
    Variables model for the MetaApp.
    """
    item_id: str | None = None
    hmd_type: str = "HOLLYWOOD"
    request_pdp_assets_as_png: Literal["false"] = Field(
        alias="requestPDPAssetsAsPNG", default="false"
    )


class MetaSectionVars(BaseVarsModel):
    """
    Variables model for the MetaSection.
    """
    section_id: str
    hmd_type: str
    item_count: int = 10000
    cursor: None = None
    sort_order: list[Any] = []


class OculusSectionVars(BaseVarsModel):
    """
    Variables model for the OculusSection.
    """
    section_id: str
    section_item_count: int = 10000
    sort_order: list[Any] = []


class BasePayloadModel(BaseModel):
    """
    Base class for payload models.
    """
    doc_id: int
    server_timestamps: bool = True
    forced_locale: str = "en_GB"

    def url_encode(self) -> str:
        """
        URL encodes the model's dump, replacing "None" with "null".

        Returns:
            str: The URL-encoded string.
        """
        dump: str = urlencode(self.model_dump(by_alias=True))
        return dump.replace("None", "null")


class MetaPayload(BasePayloadModel):
    """
    Payload model for Meta.
    """
    variables: MetaSectionVars | MetaAppVars


class OculusPayload(BasePayloadModel):
    """
    Payload model for Oculus.
    """
    variables: OculusSectionVars
    access_token: str = "OC|1076686279105243|"


class ApiHeader(BaseModel):
    """
    Pydantic model representing headers for an API request.
    """
    user_agent: str = '"Google Chrome";v="119", ' + \
        '"Chromium";v="119", "Not?A_Brand";v="24"'
    content_type: str = "application/x-www-form-urlencoded"
    accept_language: str = "en-GB,en-US;q=0.9,en;q=0.8"
    accept: str = "*/*"
    cookie: str | None

    class Config:
        """
        Pydantic model configuration.

        Attributes:
            alias_generator (Callable[..., str]): The alias generator for
                attribute names.
        """
        alias_generator: Callable[..., str] = to_kebab
