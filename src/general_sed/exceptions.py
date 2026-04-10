"""Project-specific exceptions."""


class MissingModelDataError(FileNotFoundError):
    """Raised when required BT-NextGen model assets cannot be located."""
