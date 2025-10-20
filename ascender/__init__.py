from ascender import core, common, contrib

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # type: ignore # For older Pythons

try:
    __version__ = version("ascender-framework")
except PackageNotFoundError:
    __version__ = "Unknown"

__all__ = core.__all__ + common.__all__ + contrib.__all__

