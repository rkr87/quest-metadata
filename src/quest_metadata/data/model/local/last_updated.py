"""
Module providing model for last update time.
"""
from math import ceil
from time import time

from base.models import BaseModel


class LastUpdated(BaseModel):
    """Model for last update time."""
    epoch_hours: int = ceil(time() / 60 / 60)
