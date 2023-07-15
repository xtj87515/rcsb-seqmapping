<!--
SPDX-FileCopyrightText: Copyright 2020-2023, Contributors to CICD
SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
SPDX-License-Identifier: Apache-2.0
-->

# Contributing

<!-- :tyranno: ${project.name~|sentence(@)~} -->

# Tyranno

Feel free to
[ask the maintainers a question](https://github.com/dmyersturnbull/cicdsaurus/discussions/new?category=q-a).

## For contributors

New issues and pull requests are welcome.
Contributors are asked to abide by the
[GitHub community guidelines](https://docs.github.com/en/site-policy/github-terms/github-community-guidelines)
and the [Contributor Code of Conduct, version 2.0](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

### How to contribute

1. Fork and clone locally.
2. If there is not one, [create an issue](https://github.com/dmyersturnbull/cicdsaurus/issues/new/choose).
   You may want to solicit feedback for feature changes before doing any work.
3. `git checkout -b <type>/<username>/<description>`, where `<type>` is the `type:` label of the issue,
   and `description` MAY be the issue number.
4. Make the changes. Follow the commit message rules described below.
   (Note: Because linting is applied per commit, you may have to re-run `git commit`.)
5. Consider rebasing to squash and revise your commits before pushing.
6. Push the branch to your fork and open a pull request.
   Name your pull request just like a commit. The type should match the `type:` label of the issue.
   Note that the maintainers will likely squash and lint your commits.
7. When finished, mark the pull request as ready for review.

### Commit messages

When committing, please use GPG keys and commit with `git commit --signoff` or `cz commit --signoff`.

Please follow [Conventional Commits](https://www.conventionalcommits.org/).
Use `!` for breaking changes and use the following types.

_About revert commits:_
Only use `revert:` to revert changes you made in your dev branch, and record the hash of the reverted commit.
Please rebase and ignore both commits before pushing.

| Type        | Label               | Changelog section     | semver | Description                         |
| ----------- | ------------------- | --------------------- | ------ | ----------------------------------- |
| `!`         | `breaking`          | `🔨 Breaking changes` | major  | Breaking change                     |
| `security:` | `type: security`    | `🔒 Security`         | minor  | Security issue                      |
| `feat:`     | `type: feature`     | `✨ Features`         | minor  | Add or change a feature             |
| `fix:`      | `type: fix`         | `🐛 Bug fixes`        | patch  | Fix a bug                           |
| `docs:`     | `type: docs`        | `📝 Documentation`    | patch  | Add or modify docs or examples      |
| `build:`    | `type: build`       | `🔧 Build system`     | minor  | Modify build, including Docker      |
| `perf:`     | `type: performance` | `⚡️ Performance`     | patch  | Increase speed / decrease resources |
| `test:`     | `type: test`        | `🚨 Tests`            | N/A    | Add or modify tests                 |
| `refactor:` | `type: refactor`    | ignored               | N/A    | Refactor source code                |
| `style:`    | `type: style`       | ignored               | N/A    | Improve style of source code        |
| `chore:`    | `type: chore`       | ignored               | N/A    | Change non-source code              |
| `ci:`       | `type: ci`          | ignored               | N/A    | Modify CI/CD                        |
| `revert:`   | always squash       | N/A                   | N/A    | Revert a recent change              |

## For maintainers

### Merging pull requests

Maintainers must rebase pull requests to ensure linear history.
If changes are needed and the author does not respond, consider
[checking out the pull request locally](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/checking-out-pull-requests-locally).

### Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/),
the [Angular commit guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md),
and [Semantic Versioning 2](https://semver.org/spec/v2.0.0.html).
We follow the “Guiding Principles” of [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
but not the “Types of changes”, which contradict the Angular commit types.
Angular-style commit messages get mapped to changelog sections and issue labels.

### Publishing new versions

To automatically bump the version and deploy, run the _Deploy_ workflow on GitHub.
Make sure tests passed on the main branch before doing this.

After the _publish_ workflow succeeded, copy `recipes/` to the
[feedstock](https://github.com/conda-forge/cicd-feedstock).

### Versioning

Versioning is a subset of [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Pre-releases are permitted only in the forms `alpha<int>`, `beta<int>`, and `rc<int>`,
where `<int>` starts at `0`. Alpha/beta/RC MUST NOT be used out of order (e.g., **not** `alpha1`, `beta1`, `alpha2`).

## Conventions

### Filesystem, URL, URI, and IRI node naming

See [Google’s filename conventions](https://developers.google.com/style/filenames).
Prefer kebab-case with one or more filename extensions: `[a-z0-9-]+(\.[a-z0-9]+)+`.
Always use a filename extension, and prefer `.yaml` for YAML and `.html` for HTML.
If necessary, `,`, `+`, and `~` can be used as word separators with reserved meanings.
Always use `/` as a path separator in documentation.

### Python classes

Use [pydantic](https://pydantic-docs.helpmanual.io/) or
[dataclasses](https://docs.python.org/3/library/dataclasses.html).
Use immutable types unless there’s a compelling reason otherwise.

#### With pydantic

```python
import orjson
from pydantic import BaseModel


def to_json(v) -> str:
    return orjson.dumps(v).decode(encoding="utf8")


def from_json(v: str):
    return orjson.loads(v).encode(encoding="utf8")


class Cat(BaseModel):
    breed: str | None
    age: int
    names: frozenset[str]

    class Config:
        frozen = True
        json_loads = from_json
        json_dumps = to_json
```

#### With dataclasses

Use, wherever possible: `slots=True, frozen=True, order=True`
Use `KW_ONLY` in favor of `kwonly=True` (for consistency).

```python
import orjson
from dataclasses import dataclass, KW_ONLY


def to_json(v) -> str:
    return orjson.dumps(v).decode(encoding="utf8")


def from_json(v: str):
    return orjson.loads(v).encode(encoding="utf8")


@dataclass(slots=True, frozen=True, order=True)
class Cat:
    breed: str | None
    age: int
    _: KW_ONLY
    names: frozenset[str]

    def json(self) -> str:
        return to_json(self)
```
