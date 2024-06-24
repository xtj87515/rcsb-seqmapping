# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0
"""
`tyranno clean` command.
"""

import shutil
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from cicd.context import Context

__all__ = ["Clean"]


@dataclass(frozen=True, slots=True)
class Clean:
    context: Context
    trash_patterns: list[str]
    dry_run: bool

    def run(self: Self) -> Generator[Path]:
        for path in self._find():
            self._trash(path)
            yield path

    def _find(self: Self) -> Generator[Path]:
        for pat in self.trash_patterns:
            yield from self.context.repo_dir.glob(pat)

    def _trash(self: Self, source: Path) -> None:
        dest = self.context.repo_dir / source
        if not self.dry_run:
            dest.parent.mkdir(exist_ok=True, parents=True)
            shutil.move(str(source), str(dest))
