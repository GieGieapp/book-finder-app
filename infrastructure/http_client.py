import os
from http import HTTPStatus
from typing import Optional, Dict, Any
import requests

from core.constants import DEFAULT_TIMEOUT_SECONDS, DEFAULT_USER_AGENT
from core.logger import get_logger

logger = get_logger("infrastructure.http_client")


class BaseHttpClient:
    """
    Reusable base HTTP client for third-party REST API integrations.
    Handles Keep-Alive session pooling, timeout defaults, status code validation, and error logging.
    """

    def __init__(
        self,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
        session: Optional[requests.Session] = None
    ):
        self.timeout = timeout or int(os.getenv("HTTP_TIMEOUT", DEFAULT_TIMEOUT_SECONDS))
        self.user_agent = user_agent or os.getenv("USER_AGENT", DEFAULT_USER_AGENT)
        self.session = session or requests.Session()

    def get_headers(self) -> Dict[str, str]:
        """Provides default request headers including User-Agent"""
        return {
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }

    def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Any]:
        """
        Executes HTTP GET request and deserializes JSON response.
        Returns parsed JSON object or None if the request failed.
        """
        req_headers = self.get_headers()
        if headers:
            req_headers.update(headers)

        try:
            logger.debug("Executing HTTP GET to %s with params %s", url, params)
            response = self.session.get(
                url,
                params=params,
                headers=req_headers,
                timeout=self.timeout
            )

            if response.status_code == HTTPStatus.OK:
                return response.json()

            logger.warning(
                "Remote API returned non-200 HTTP %d from %s",
                response.status_code,
                url
            )
            return None

        except requests.exceptions.Timeout:
            logger.error("HTTP request timed out after %ds: %s", self.timeout, url)
            return None
        except requests.exceptions.RequestException as exc:
            logger.error("HTTP network request failed for %s: %s", url, exc)
            return None
        except ValueError as exc:
            logger.error("Failed to parse JSON response from %s: %s", url, exc)
            return None
