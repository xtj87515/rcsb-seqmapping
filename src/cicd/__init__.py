# SPDX-FileCopyrightText: Copyright 2020-2023, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0

"""
Project description.
"""
from pathlib import Path


def run(path: Path) -> None:
    """
    Does a thing.

    Arguments:
        path: A path to a place
    """
    print(path)


def execute(path: Path) -> None:
    print(path)
