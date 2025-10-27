import os
from typing import Any, Dict, Optional

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

import requests


class ConfigError(Exception):
    pass


class Messenger:
    def __init__(
        self,
        server_url: Optional[str] = None,
        instance_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.server_url = server_url or os.getenv("SERVER_URL")
        self.instance_id = instance_id or os.getenv("INSTANCE_ID")
        self.api_key = (
            api_key or os.getenv("API_KEY") or os.getenv("AUTHENTICATION_API_KEY")
        )

        if not self.server_url or not self.api_key:
            raise ConfigError(
                "SERVER_URL and API_KEY (or AUTHENTICATION_API_KEY) must be set (or passed to Messenger)"
            )

        if self.server_url.startswith("http://") or self.server_url.startswith(
            "https://"
        ):
            self.base = self.server_url.rstrip("/")
        else:
            self.base = f"https://{self.server_url.rstrip('/')}"

    def _build_url(self, instance_id: Optional[str] = None) -> str:
        iid = instance_id or self.instance_id
        if not iid:
            raise ConfigError(
                "instance_id must be provided either to Messenger or per-call"
            )
        return f"{self.base}/message/sendText/{iid}"

    def send_text(
        self,
        number: str,
        text: str,
        delay: Optional[int] = None,
        link_preview: bool = False,
        timeout: int = 10,
        instance_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "number": number,
            "text": text,
            "delay": delay or 10,
            "linkPreview": bool(link_preview),
        }

        url = self._build_url(instance_id=instance_id)
        headers = {"apikey": self.api_key, "Content-Type": "application/json"}

        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            try:
                body = resp.text
            except Exception:
                body = "(could not read response body)"
            raise RuntimeError(f"Remote API returned {resp.status_code}: {body}")

        return resp.json()

