"""
Main script for running the Oculus app updater.


Functions:
- main: Asynchronous function to run the Oculus app updater.
"""
import asyncio
import logging.config
from argparse import ArgumentParser, Namespace

from config.app_config import AppConfig
from utils.error_manager import ErrorManager


async def main() -> None:
    """
    Asynchronous function to run the Oculus app updater.
    """
    from application import Application  # pylint: disable=C0415
    app: Application = await Application()
    await app.run()


def setup_args() -> ArgumentParser:
    """
    Set up command-line arguments for the script.

    Returns:
    - ArgumentParser: The configured argument parser.
    """
    arg_parser = ArgumentParser(
        prog="QuestMetadata",
        description="Fetch metadata and artwork for Meta Quest apps"
    )
    arg_parser.add_argument(
        "-c",
        "--config_file",
        type=str,
        help="path to config override",
        required=False
    )
    arg_parser.add_argument(
        "-s",
        "--save_config",
        action='store_true',
        help="save default config values to default file location",
        required=False
    )
    return arg_parser


async def load_config(override_file: str | None) -> None:
    """
    Load configuration.

    Args:
    - override_file (str | None): Path to a config override file.
    """
    await AppConfig.load_config(override_file)


async def save_config() -> None:
    """
    Save default configuration values to the default file location.
    """
    await AppConfig.save_defaults()

if __name__ == "__main__":
    args: Namespace = setup_args().parse_args()
    if args.save_config:
        asyncio.run(save_config())
    else:
        asyncio.run(load_config(args.config_file))
        logging.config.fileConfig(AppConfig().logging_config)
        asyncio.run(main())
        asyncio.run(ErrorManager().save_error_log())
