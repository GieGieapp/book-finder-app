from http import HTTPStatus
from typing import Optional, Dict, Any
import requests

from core.constants import DEFAULT_TIMEOUT_SECONDS, DEFAULT_USER_AGENT
from core.logger import get_logger

logger = get_logger("infrastructure.http_client")


class BaseHttpClient:
    """
    Reusable HTTP client adapter with Keep-Alive connection pooling,
    automatic timeouts, and structured error handling.
    """

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        user_agent: str = DEFAULT_USER_AGENT,
        session: Optional[requests.Session] = None,
    ):
        self.timeout = timeout
        self.user_agent = user_agent
        self.session = session or requests.Session()

    def get_headers(self) -> Dict[str, str]:
        """Provides default request headers"""
        return {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

    def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[Any]:
        """
        Executes HTTP GET and deserializes JSON response.
        Returns parsed JSON object or None on failure.
        """
        req_headers = self.get_headers()
        if headers:
            req_headers.update(headers)

        try:
            logger.debug("Executing GET %s with params %s", url, params)
            response = self.session.get(
                url,
                params=params,
                headers=req_headers,
                timeout=self.timeout,
            )

            if response.status_code == HTTPStatus.OK:
                return response.json()

            logger.warning("Remote API returned status %d from %s", response.status_code, url)
            return None

        except requests.exceptions.Timeout:
            logger.error("HTTP request timed out after %ds: %s", self.timeout, url)
            return None
        except requests.exceptions.RequestException as exc:
            logger.error("HTTP request failed for %s: %s", url, exc)
            return None
        except ValueError as exc:
            logger.error("Failed to parse JSON response from %s: %s", url, exc)
            return None

    def close(self) -> None:
        """Closes the underlying requests Session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
