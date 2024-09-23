# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to Tyrannosaurus
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/tyrannosaurus
# SPDX-License-Identifier: Apache-2.0
"""
A set of metadata about this package.
The metadata is determined dynamically.
In order:

1. Attempts to load `importlib.metadata(pkg)`, where `pkg` is this directory name.
2. Looks for a `../../../pyproject.toml` file.
3. Uses an empty map.
"""

import logging
import tomllib
from dataclasses import asdict, dataclass, field
from importlib.metadata import PackageNotFoundError
from importlib.metadata import metadata as __importlib_load
from pathlib import Path
from typing import Self

__all__ = ["About", "about"]
__pkg = Path(__file__).parent.name
logger = logging.getLogger(__pkg)


@dataclass(frozen=True, slots=True, kw_only=True)
class About:
    """
    Metadata about this package (as in pip-installable / PyPi package).
    Attributes correspond to importlib metadata keys (see https://docs.python.org/3/library/importlib.metadata.html).
    The values may be found via either `importlib` (preferred) or `pyproject.toml`.
    Values may differ depending on the process used to find them, but importlib-based definitions are used either way.
    Values are empty (`""`, `[]`, `{}`) if not found.
    This **should** never occur for data from `importlib` but may be expected for some fields if from `pyproject.toml`.
    For example, `description` may be empty if the specified readme file could not be read.

    <b>Notes:</b>

    - `summary` corresponds to the `pyproject.toml` file's `project.description`.
    - `description` ~ (the content of) `project.readme.file`.
    - `title` ~ `project.name`.
    - `namespace` is the name of the directory containing this module.
      e.g. `mypkg` if the project name is `my-pkg`.
    - `homepage` ~ `project.urls.Homepage`.
    - `license` is an SPDX license ID.
    - `author` and `maintainer` ~ `name` from `project.authors` and `project.maintainers`:
      e.g. `authors = [{"name": "Adam Addison", ...}, {"name": "Chloe Cho", ...}]`
      results in `Adam Addison and Chloe Cho`.
    """

    namespace: str
    version: str
    title: str
    summary: str
    license: str
    author: str = ""
    maintainer: str = ""
    description: str = ""
    keywords: list[str] = field(default_factory=list)  # JSON compat
    homepage: str = ""
    hyperlinks: dict[str, str] = field(default_factory=dict)

    @property
    def as_dict(self: Self) -> dict[str, str | list[str] | dict[str, str]]:
        return asdict(self)


def _load_metadata(pkg: str, package_root: Path) -> About:  # nocov
    # 1: First, try `importlib`; will fail if our package is not installed
    try:
        data = __importlib_load(pkg).json
        return About(
            namespace=__pkg,
            version=data.get("Version"),
            title=data.get("Name"),
            summary=data.get("Summary"),
            license=data.get("License"),
            author=data.get("Author", ""),
            maintainer=data.get("Maintainer", ""),
            description=data.get("Description", ""),
            keywords=data.get("Keywords", "").split(","),
            homepage=data.get("Home-page"),
            hyperlinks={s[: s.index(",")]: s[s.index(",") + 2 :] for s in data.get("Project-URL", [])},
        )
    except PackageNotFoundError:
        pass
    logger.debug(f"Did not find importlib metadata for package `{pkg}`. Is it installed?")
    # 2: Now try reading a pyproject.toml file
    pyproject_file = package_root / "pyproject.toml"
    data = {}
    if pyproject_file.exists():
        try:
            data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
            logger.debug(f"Using metadata for package `{pkg}` from pyproject.toml.")
        except tomllib.TOMLDecodeError as e:
            logger.warning(f"Encountered error while decoding `{pyproject_file.resolve()}`.", e)
    data = data.get("project")
    readme_file = pyproject_file.parent / data.get("readme", {}).get("file", "?")
    readme = ""
    if readme_file.name != "?":
        try:
            readme = readme_file.read_text(encoding="utf-8")
        except OSError as e:
            logger.debug(f"Error reading `{readme_file}`.", e)
    abt = About(
        namespace=pkg,
        version=data.get("version", ""),
        title=data.get("name", ""),
        summary=data.get("description", ""),  # yep, this is correct
        license=data.get("license", {}).get("text", ""),
        author=" and ".join([x.get("name", "?") for x in data.get("authors", [])]),
        maintainer=" and ".join([x.get("name", "?") for x in data.get("maintainers", [])]),
        description=readme,  # yep, this is correct, too
        keywords=data.get("keywords", []),
        homepage=data.get("urls", {}).get("Homepage", ""),
        hyperlinks=data.get("urls"),
    )
    missing = {k for k, v in abt.as_dict.items() if v is None or isinstance(v, list | dict) and len(v) == 0}
    logger.debug(f"Read metadata for package `{pkg}` from `pyproject.toml`. Missing {"; ".join(missing)}.")
    return abt


about = _load_metadata(__pkg, Path(__file__).parent.parent.parent)
