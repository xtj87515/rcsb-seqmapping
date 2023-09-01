import os
from typing import Any

from cicd._internal import Metadata

__all__ = ["ApiMeta"]


class ApiMeta:
    api_url: str = os.environ.get("CICD_API_URL", "http://localhost:80/")
    host: str = api_url.split("/")[0]
    client_id: str | None = os.environ.get("CLIENT_ID")
    client_secret: str | None = os.environ.get("CLIENT_SECRET")
    dev_mode: bool = bool(os.environ.get("OAUTHLIB_INSECURE_TRANSPORT", 1))
    metadata: dict[str, Any] = {
        "title": Metadata.title,
        "description": Metadata.summary,
        "version": Metadata.version,
        "contact": {
            "name": "Homepage",
            "url": Metadata.homepage,
        },
        "license_info": {
            "name": Metadata.license,
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
    }
