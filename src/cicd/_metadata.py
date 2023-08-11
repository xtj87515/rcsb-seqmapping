# SPDX-FileCopyrightText: Copyright 2020-2023, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0

"""
Metadata and environment variables.
"""
import logging
import os
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError
from importlib.metadata import _metadata as __load
from pathlib import Path

import platformdirs

__all__ = ["ProjectInfo", "Vars"]


_pkg = Path(__file__).parent.name
_logger = logging.getLogger(_pkg)
_metadata = None
try:
    _metadata = __load(_pkg)
except PackageNotFoundError:  # pragma: no cover
    _logger.error(f"Could not load package metadata for {_pkg}. Is it installed?")
    __uri__ = None
    __title__ = None
    __summary__ = None
    __version__ = None
    __license__ = None
else:
    __uri__ = _metadata["Home-page"]
    __title__ = _metadata["Name"]
    __summary__ = _metadata["Summary"]
    __license__ = _metadata["License"]
    __version__ = _metadata["Version"]


class ProjectInfo:
    _pkg = _pkg
    homepage = __uri__
    title = __title__
    summary = __summary__
    license = __license__
    version = __version__


class Vars:
    api_url: str = os.environ.get("CICD_API_URL", "http://localhost:80/")
    host: str = api_url.split("/")[0]
    now_utc = datetime.now(UTC)
    now_local = now_utc.astimezone()
    cache_dir: Path = Path(os.environ.get("CICD_CACHE_DIR", platformdirs.user_cache_path(_pkg)))
    config_dir: Path = Path(os.environ.get("CICD_CONFIG_DIR", platformdirs.user_cache_path(_pkg)))
    client_id: str | None = os.environ.get("CLIENT_ID")
    client_secret: str | None = os.environ.get("CLIENT_SECRET")
    dev_mode: bool = bool(os.environ.get("OAUTHLIB_INSECURE_TRANSPORT", 1))
    mongodb_uri: str | None = os.environ.get("MONGODB_URI")
    postgres_uri: str | None = os.environ.get("POSTGRES_URI")
    api_metadata = {
        "title": __title__,
        "description": __summary__,
        "version": __version__,
        "contact": {
            "name": "Homepage",
            "url": __uri__,
        },
        "license_info": {
            "name": __license__,
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
    }
