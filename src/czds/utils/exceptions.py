"""czds.utils.exceptions."""


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
