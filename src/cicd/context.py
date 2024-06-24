# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0
"""
Wrapper around repo for Tyranno.
"""

import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path, PurePath
from typing import Self

import jmespath

from cicd._global_vars import GlobalVars
from cicd.wrapped_toml import TomlBranch, TomlLeaf, WrappedToml

__all__ = ["Context", "ContextFactory", "DefaultContextFactory"]
_PATTERN = re.compile(r"\$\{ *([-._A-Za-z0-9]*) *(?:~ *([^~]+) *~ *)?}")


@dataclass(frozen=True, slots=True, kw_only=True)
class Context(GlobalVars):
    repo_dir: Path
    data: WrappedToml
    dry_run: bool

    @property
    def trash_dir(self: Self) -> Path:
        return self.repo_path / self.trash_dir_name

    def resolve_path(self: Self, path: PurePath | str) -> Path:
        path = Path(path).resolve(strict=True)
        if not str(path).startswith(str(self.repo_path)):
            msg = f"{path} is not a descendent of {self.repo_path}"
            raise AssertionError(msg)
        return path.relative_to(self.repo_path)

    def req(self: Self, key: str) -> TomlBranch | TomlLeaf:
        return self._sub(key, None)

    def _sub(self: Self, key: str, james: str | None) -> TomlBranch | TomlLeaf:
        key = "tool.tyranno.data" if key == "." else "tool.tyranno.data" + key
        result = self._get_value(key)
        return jmespath.search(james, result) if james else result

    def _get_value(self, key):
        value = self.data.req(key)
        match value:
            case list():
                result = [self._sub(v, None) for v in value]
            case dict():
                result = {k: self._sub(v, None) for k, v in value.items()}
            case str():
                result = _PATTERN.sub(lambda p: self._sub(p.group(1), p.group(2)), value)
            case int() | float() | datetime() | date():
                result = value
            case _:
                msg = f"Impossible type {value}"
                raise AssertionError(msg)
        return result


@dataclass(frozen=True, slots=True)
class ContextFactory:
    def __call__(self: Self, cwd: Path, global_vars: GlobalVars, *, dry_run: bool) -> Context:
        raise NotImplementedError()


@dataclass(frozen=True, slots=True)
class DefaultContextFactory(ContextFactory):
    def __call__(self: Self, cwd: Path, global_vars: GlobalVars, *, dry_run: bool) -> Context:
        config_path = self._find_config_file(cwd)
        data = WrappedToml.from_toml_file(config_path) if config_path else WrappedToml({"project": {"name": cwd.name}})
        return Context(
            **asdict(global_vars),
            repo_dir=cwd,
            cache_dir=GlobalVars.cache_dir,
            data=data,
        )

    @staticmethod
    def _find_config_file(cwd: Path) -> Path | None:
        for name in (".tyranno.toml", "pyproject.toml"):
            if (cwd / name).exists():
                return cwd / name
        return None
