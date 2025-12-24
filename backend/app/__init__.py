# Lazy import to avoid circular dependencies
try:
    from .main import app  # noqa: F401
except ImportError:
    pass
