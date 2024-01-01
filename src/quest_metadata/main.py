"""
Main script for running the Oculus app updater.

Modules:
- asyncio: Asynchronous I/O operations.
- logging.config: Configuration for logging.
- os: Operating system-specific functionality.
- application: The Application module for managing and updating Oculus apps.
- constants.constants: Constants used in the application.

Functions:
- main: Asynchronous function to run the Oculus app updater.
"""
import asyncio
import logging.config
import os

from application import Application
from constants.constants import DATA, RESOURCES


async def main() -> None:
    """
    Asynchronous function to run the Oculus app updater.

    Execution steps:
    - Configure logging from 'logging.conf'.
    - Create necessary directories for app data and resources.
    - Initialize the Application instance.
    - Run the application to update local apps and scrape app data.
    """
    logging.config.fileConfig('.config_app/logging.conf')
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(RESOURCES, exist_ok=True)
    app: Application = await Application()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
