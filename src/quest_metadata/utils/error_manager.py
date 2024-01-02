"""
Module providing error management and logging functionality.

Classes:
- _ErrorEntry: Model class representing an entry for logged errors.
- ErrorManager: Singleton class for managing and logging errors.
"""
from datetime import datetime, timedelta
from typing import Annotated, Any

from aiofiles.os import listdir
from aiofiles.os import makedirs as amakedirs
from aiofiles.os import remove
from pydantic import Field

from base.models import BaseModel, SingletonModel

ERROR_DIR = ".errors"
LOG_RETENTION_DAYS = 7


class _ErrorEntry(BaseModel):
    """
    Model class representing an entry for logged errors.
    """
    exception: Annotated[Exception | str, Field(exclude=True)]
    context: str
    error_type: str | None = None
    error_message: str | None = None
    log_message: str
    error_information: dict[str, Any]

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization hook for the model.

        Args:
        - __context (Any): The context of the model post-initialization.
        """
        if isinstance(self.exception, str):
            self.error_type = self.exception
            return super().model_post_init(__context)
        self.error_type = self.exception.__class__.__name__
        self.error_message = str(self.exception)
        return super().model_post_init(__context)

    class Config:
        """
        Pydantic configuration class for _ErrorEntry.

        Attributes:
        - arbitrary_types_allowed (bool): Allow arbitrary types during
            serialization.
        """
        arbitrary_types_allowed = True


class ErrorManager(SingletonModel):
    """
    Singleton class for managing and logging errors.
    """
    timestamp: datetime = datetime.now()
    errors_logged: list[_ErrorEntry] = []

    def capture(
        self,
        exception: Exception | str,
        context: str,
        log_message: str | None = None,
        error_info: dict[str, Any] | None = None
    ) -> str:
        """
        Capture and log an error.

        Returns:
        - str: The log message associated with the error entry.
        """
        if log_message is None:
            log_message = f"Captured exception: {exception.__class__.__name__}"
        entry = _ErrorEntry(
            exception=exception,
            context=context,
            log_message=log_message,
            error_information=error_info or {}
        )
        self.errors_logged.append(entry)
        return entry.log_message

    async def save_error_log(self) -> None:
        """
        Save error log to a file and perform log retention.

        Log files are saved with a timestamp, and old log files are removed
        based on the configured log retention period.
        """
        date_format = "%Y-%m-%d %H.%M.%S"
        date_string: str = self.timestamp.strftime(date_format)
        await amakedirs(ERROR_DIR, exist_ok=True)
        if len(self.errors_logged) > 0:
            await self.save_json(f"{ERROR_DIR}/{date_string}.json")
        for file in await listdir(ERROR_DIR):
            date_str: str = file.replace(".json", "")
            date_val: datetime = datetime.strptime(date_str, date_format)
            delta: timedelta = datetime.now() - date_val
            if delta.days > LOG_RETENTION_DAYS:
                await remove(f"{ERROR_DIR}/{file}")
