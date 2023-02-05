"""czds.utils.exceptions."""
from requests.exceptions import HTTPError


class CZDSConnectionError(HTTPError):
    """Base class for all requests HTTPErrors."""

    def __init__(self, status_code: int, name: str, http_error: HTTPError) -> None:
        """Base exception for CZDS HTTP requests.

        Args:
            status_code (int): The status code received from the request.
            name (str): The name of the error.
            http_error (HTTPError): The HTTP Error from the requests response.
        """
        from ..base import Base

        Base().log(message=f"\n{name} Error Occurred.\nStatus Code: {status_code}\nError: {http_error}\n")


class UnsupportedTypeError(TypeError):
    """Raised when the wrong type is provided."""

    def __init__(self, *args: object) -> None:
        """Wrapper for TypeError exception class which passed arguments along to TypeError."""
        super().__init__(*args)


class CustomExceptionError(Exception):
    """Raised when an error is encountered."""

    def __init__(self, value: str) -> None:
        """Raises when the value is unknown."""
        pass
