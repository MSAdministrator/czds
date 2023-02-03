"""czds.base.

This Base class inherits from our LoggingBase metaclass and gives us
shared logging across any class inheriting from Base.
"""
from typing import AnyStr

from .utils.logger import LoggingBase


class Base(metaclass=LoggingBase):
    """Base class to all other classes within this project."""
    BASE_URL: AnyStr = "https://czds-api.icann.org"
    AUTH_URL: AnyStr = "https://account-api.icann.org/api/authenticate"
    BASE_HEADERS: dict = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    USERNAME: AnyStr = None
    PASSWORD: AnyStr = None
    SAVE_PATH: AnyStr = None
    
    # We create a Connector object and set it to this class property in czds.py
    connection = None
