"""
constants.py

This module defines constant values used throughout the application.

META_DOMAIN (str):
    The base domain for Meta API requests.

RESOURCES (str):
    The path to the directory where resources are stored.

DATA (str):
    The path to the directory where data files are stored.

VERSION (str):
    The version number of the application.
"""
from utils.env_utils import github_actions

META_DOMAIN: str = "https://www.meta.com"
RESOURCES: str = github_actions("res/")
DATA: str = github_actions("data/")
VERSION = "0.2.0"
