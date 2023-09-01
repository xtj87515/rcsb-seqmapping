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
from importlib.metadata import metadata as __load
from pathlib import Path

import platformdirs
import tomlkit

__all__ = ["Metadata", "Utils", "Vars"]


_pkg = Path(__file__).parent.name
logger = logging.getLogger(_pkg)
_metadata = None
try:
    _metadata = __load(_pkg)
except PackageNotFoundError:  # pragma: no cover
    _pyproject = Path(__file__).parent / "pyproject.toml"
    if _pyproject.exists():
        _data = tomlkit.loads(_pyproject.read_text(encoding="utf-8"))
        _metadata = {k.capitalize(): v for k, v in _data["project"]}
    else:
        logger.error(f"Could not load metadata for package {_pkg}. Is it installed?")


class Metadata:
    pkg = _pkg
    homepage = _metadata.get("Home-page")
    title = _metadata.get("Name")
    summary = _metadata.get("Summary")
    license = _metadata.get("License")
    version = _metadata.get("Version")


class Utils:
    def parse_boolean(self, s: str) -> bool:
        if s.lower() in {"true", "yes", "1"}:
            return True
        if s.lower() in {"false", "no", "0"}:
            return False
        _msg = f"{s} could not be parsed as boolean"
        raise ValueError(_msg)


class Vars:
    now_utc = datetime.now(UTC)
    now_local = now_utc.astimezone()
    cache_dir: Path = Path(os.environ.get("CICD_CACHE_DIR", platformdirs.user_cache_path(_pkg)))
    config_dir: Path = Path(os.environ.get("CICD_CONFIG_DIR", platformdirs.user_cache_path(_pkg)))
