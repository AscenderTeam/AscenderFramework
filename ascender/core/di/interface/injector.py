from typing import NotRequired, TypedDict


class InjectorOptions(TypedDict):
    """Type of the options argument to `inject`"""
    optional: NotRequired[bool]
    """Use optional injection, and return `None` if the requested token is not found."""
    skip_self: NotRequired[bool]
    """Start injection at the parent of the current injector."""
    only_self: NotRequired[bool]
    """
    Only query the current injector for the token, and don't fall back to the parent injector if
    it's not found.
    """