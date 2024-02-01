"""
Module providing model for last update time.
"""

from datetime import datetime

from base.models import BaseModel


class LastUpdated(BaseModel):
    """
    Model for last update time.
    """
    last_updated: datetime = datetime.now()
