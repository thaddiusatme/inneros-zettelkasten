# Compatibility shim — SafeImageProcessor now lives in media.py
from .media import SafeImageProcessor

__all__ = ["SafeImageProcessor"]
