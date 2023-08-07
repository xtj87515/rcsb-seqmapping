# SPDX-FileCopyrightText: Copyright 2020-2023, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0

"""
Project description.
"""
import logging
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError
from importlib.metadata import metadata as __load
from pathlib import Path

import platformdirs


def run(path: Path) -> None:
    """
    Does a thing.

    Arguments:
        path: A path to a place
    """
    print(path)
