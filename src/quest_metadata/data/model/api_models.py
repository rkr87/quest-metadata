"""
api_models.py

This module defines Pydantic models representing API payload variables
and headers for making requests to the Meta API.

_ApiPayloadVariables:
    Pydantic model representing variables in an API payload.

ApiPayload:
    Pydantic model representing an API payload.

ApiHeader:
    Pydantic model representing headers for an API request.
"""

from typing import Callable

from pydantic import Field
from typing_extensions import Literal

from base.base_model import BaseModel
from constants.constants import META_DOMAIN
from utils.string_utils import to_camel, to_kebab


class _ApiPayloadVariables(BaseModel):
    """
    Pydantic model representing variables in an API payload.
    """
    item_id: str | None = None
    hmd_type: Literal["HOLLYWOOD"] = "HOLLYWOOD"
    request_pdp_assets_as_png: Literal["false"] = Field(
        alias="requestPDPAssetsAsPNG", default="false"
    )

    class Config:
        """
        Pydantic model configuration.

        Attributes:
            alias_generator (Callable[..., str]): The alias generator for
                attribute names.
        """
        alias_generator: Callable[..., str] = to_camel


class ApiPayload(BaseModel):
    """
    Pydantic model representing an API payload.
    """
    variables: _ApiPayloadVariables = _ApiPayloadVariables()
    doc_id: Literal[7005322839522027] = 7005322839522027


class ApiHeader(BaseModel):
    """
    Pydantic model representing headers for an API request.
    """
    user_agent: str = '"Google Chrome";v="119", ' + \
        '"Chromium";v="119", "Not?A_Brand";v="24"'
    content_type: str = "application/x-www-form-urlencoded"
    accept_language: str = "en-GB,en-US;q=0.9,en;q=0.8"
    accept: str = "*/*"
    authority: str = "www.meta.com"
    origin: str = META_DOMAIN
    referrer: str = META_DOMAIN
    cookie: str | None

    class Config:
        """
        Pydantic model configuration.

        Attributes:
            alias_generator (Callable[..., str]): The alias generator for
                attribute names.
        """
        alias_generator: Callable[..., str] = to_kebab
