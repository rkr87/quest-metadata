"""
Module providing the `RookieService` class for retrieving and managing Rookie
metadata.

Classes:
- `RookieService`: Singleton class for retrieving Rookie metadata.
"""
import csv
import os
import subprocess

from base.classes import Singleton
from config.app_config import AppConfig
from data.model.rookie.releases import Releases

TEMP_PATH: str = ".config/temp/meta.7z "
GAME_LIST_FILE: str = "VRP-GameList.txt"
NOTES_PATH: str = os.path.join(".meta", "notes")


class RookieService(Singleton):
    """Singleton class for retrieving Rookie metadata."""

    def __init__(self) -> None:
        super().__init__()
        self._logger.info("Initialising Rookie Service")
        zip_file: str = self._fetch_update_list()
        self._extract_zip(zip_file)
        self._releases: Releases = self._load_gamelist()

    def _fetch_update_list(self) -> str:
        """
        Fetches the update list for Rookie. (Needs update for automatic updates
        via HTTP client)

        Returns:
        - str: The path to the downloaded zip file.
        """
        # Update this method to get automatic updates via http client
        self._logger.info("Fetching Rookie update list")
        return TEMP_PATH

    def _extract_zip(self, zip_file: str) -> None:
        """Extracts the contents of the zip file to the Rookie path."""
        self._logger.info("Extracting Rookie metadata")
        subprocess.run(
            f"7z x {zip_file} " +
            f"-o{AppConfig().rookie_path} " +
            f"-p{os.environ["ROOKIE_ZIP_PASSWORD"]} " +
            f"{GAME_LIST_FILE} {NOTES_PATH} -y",
            check=True,
            stdout=subprocess.DEVNULL
        )

    def _load_gamelist(self) -> Releases:
        """Parses the game list and release notes for Rookie."""
        self._logger.info("Parsing Rookie update list")
        notes: str = os.path.join(AppConfig().rookie_path, NOTES_PATH)
        updates: str = os.path.join(AppConfig().rookie_path, GAME_LIST_FILE)
        with open(updates, "r", encoding="utf8", newline='') as file:
            csv_data = list(csv.DictReader(file, delimiter=";"))
            model: Releases = Releases.model_validate(csv_data)
        for note in os.listdir(notes):
            with open(f"{notes}/{note}", "r", encoding="utf8") as file:
                note_text: str = file.read()
            model.set_release_note(note[:-4], note_text)
        return model

    def get_releases(self) -> Releases:
        """Get Rookie releases."""
        return self._releases
