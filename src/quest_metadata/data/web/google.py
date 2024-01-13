"""
Module providing a singleton class for managing Google Sheets service.

Classes:
- GoogleSheetService: Singleton class for managing Google Sheets service.
"""
# pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownMemberType=false
# mypy: disable-error-code="import-untyped,no-any-unimported,no-any-return,import-not-found"
# Google need to sort their shit..
import os
from typing import Any, TypeVar

from google.oauth2.service_account import Credentials
from gspread import Client, Spreadsheet, Worksheet, authorize
from pydantic import ValidationError

from base.classes import Singleton
from base.models import BaseModel
from data.model.google.package_mappings import PackageMappings
from utils.error_manager import ErrorManager

CREDENTIALS: dict[str, str] = {
    "type": "service_account",
    "project_id": os.environ["GOOGLE_PROJECT_ID"],
    "private_key_id": os.environ["GOOGLE_PRIVATE_KEY_ID"],
    "private_key": os.environ["GOOGLE_PRIVATE_KEY"],
    "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
    "client_id": os.environ["GOOGLE_CLIENT_ID"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ["GOOGLE_CERT_URL"],
    "universe_domain": "googleapis.com"
}


class GoogleSheetService(Singleton):
    """Singleton class for managing Google Sheets service."""

    def __init__(self) -> None:
        super().__init__()
        self._client: Client = self._get_client()

    @classmethod
    def _get_client(cls) -> Client:  # type: ignore[misc]
        """Get the Google Sheets client."""
        scopes: list[str] = ['https://www.googleapis.com/auth/spreadsheets']
        credentials: Credentials = \
            Credentials.from_service_account_info(CREDENTIALS, scopes=scopes)
        return authorize(credentials)

    _MT = TypeVar("_MT", bound=BaseModel)

    def _request(
        self,
        sheet_id: str,
        worksheet_name: str,
        target_model: type[_MT]
    ) -> _MT | None:
        """Make a request to Google Sheets API."""
        resp: list[Any] = self._download_sheet(sheet_id, worksheet_name)
        return self._validate_model(resp, target_model)

    def _download_sheet(self, sheet_id: str, worksheet_name: str) -> list[Any]:
        """Download data from a Google Sheet."""
        sheet: Spreadsheet = self._client.open_by_key(sheet_id)
        worksheet: Worksheet = sheet.worksheet(worksheet_name)
        return worksheet.get_all_records()

    def _validate_model(
        self,
        response: list[Any],
        target_model: type[_MT]
    ) -> _MT | None:
        """Validate the data using a Pydantic model."""
        try:
            return target_model.model_validate(response)
        except ValidationError as e:
            error: str = ErrorManager().capture(
                e,
                "Validating Google Sheet response",
                f"Captured model validation error: {target_model.__name__}",
                {"data": response}
            )
            self._logger.warning("%s", error)
            return None

    def get_package_mappings(self) -> PackageMappings | None:
        """Get package mappings from a Google Sheet."""
        return self._request(
            "1yzB0eCDUg4_ayGlytSgpsswlxnSjr7q2QHvhraibiJU",
            "package_mapping",
            PackageMappings
        )
