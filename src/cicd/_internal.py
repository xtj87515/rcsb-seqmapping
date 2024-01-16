# SPDX-FileCopyrightText: Copyright 2020-2023, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0
"""
Environment variables and internal utils.
"""

import os
from datetime import UTC, datetime
from pathlib import Path

import platformdirs

__all__ = ["Vars"]


class Vars:
    now_utc = datetime.now(UTC)
    now_local = now_utc.astimezone()
    cache_dir: Path = Path(os.environ.get("CICD_CACHE_DIR", platformdirs.user_cache_path("cicd")))
    config_dir: Path = Path(os.environ.get("CICD_CONFIG_DIR", platformdirs.user_cache_path("cicd")))
