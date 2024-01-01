"""
Module providing constants and configurations.

Constants:
- RESOURCES (str): Path to resources directory.
- DATA (str): Path to data directory.
- VERSION (str): Current version of the application.
- BINARY_TYPE (str): Type of binary, specifically for Android.
- DEFAULT_LOCALE (str): Default locale for the application.
"""
from utils.env import github_actions

RESOURCES: str = github_actions("res/")
DATA: str = github_actions("data/")
VERSION: str = "0.2.0"
DEFAULT_LOCALE: str = "en_US"
