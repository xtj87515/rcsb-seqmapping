# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Tyrannosaurus
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/tyrannosaurus
# SPDX-License-Identifier: Apache-2.0

"""
A stub for the application.
"""

from dataclasses import dataclass

__all__ = ["App", "app"]


@dataclass(frozen=True, slots=True)
class App:
    """A nothing app."""

    def __call__(self) -> str:
        return "This does nothing."


app = App()
