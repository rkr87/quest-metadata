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
    Setup environment
    """
    args: Namespace = setup_args().parse_args()
    if args.save_config:
        await AppConfig.save_defaults()
        return
    config: AppConfig = await AppConfig.load_config(args.config_file)
    logging.config.fileConfig(config.logging_config)
    await _run_app()
    await ErrorManager().save_error_log()


def setup_args() -> ArgumentParser:
    """
    Set up command-line arguments for the script.

    Returns:
    - ArgumentParser: The configured argument parser.
    """
    args = ArgumentParser(
        prog="QuestMetadata",
        description="Fetch metadata and artwork for Meta Quest apps"
    )
    args.add_argument(
        "-c",
        "--config_file",
        type=str,
        help="path to config override",
        required=False
    )
    args.add_argument(
        "-s",
        "--save_config",
        action='store_true',
        help="save default config values to default file location",
        required=False
    )
    return args


async def _run_app() -> None:
    """Run the app"""
    from application import Application  # pylint: disable=C0415
    app: Application = await Application()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
