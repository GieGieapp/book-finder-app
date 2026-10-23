"""
Compatibility Bridge
BaseHttpClient has moved to infrastructure.http_client
"""
from infrastructure.http_client import BaseHttpClient

__all__ = ["BaseHttpClient"]
