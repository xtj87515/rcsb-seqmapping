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

1. Set up GPG keys if you haven’t already.
2. Fork and clone locally.
3. If there isn’t one, [create an issue](https://github.com/dmyersturnbull/cicdsaurus/issues/new/choose).
   You may want to solicit feedback for feature changes before doing any work.
4. `git checkout -b <type>/<username>/<description>`, where `<type>` is the `type:` label of the issue,
   and `description` is a 1-2-word description.
5. To commit, run `hatch run fmt` followed by `hatch run commit --signoff`.
6. Rebase to squash and revise your commits before pushing.
   Most feature branches should end up with between 1 and 10 commits.
7. Push the branch to your fork and open a pull request.
   Name your pull request just like a commit. The type should match the `type:` label of the issue.
   Note that the maintainers will likely squash and lint your commits.
8. When finished, mark the pull request as ready for review.

### Committing

Use `hatch run commit --signoff` instead of `git commit`.
`--signoff` indicates your agreement to the [Developer Certificate of Origin](https://developercertificate.org/),
certifying that you have the right to submit your contributions under this project’s license.

### Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org/) with the following types.

| Type        | Label               | Changelog section  | semver | Description                         |
| ----------- | ------------------- | ------------------ | ------ | ----------------------------------- |
| `security:` | `type: security`    | `🔒 Security`      | minor  | Security issue                      |
| `feat:`     | `type: feature`     | `✨ Features`      | minor  | Add or change a feature             |
| `fix:`      | `type: fix`         | `🐛 Bug fixes`     | patch  | Fix a bug                           |
| `docs:`     | `type: docs`        | `📝 Documentation` | patch  | Add or modify docs or examples      |
| `build:`    | `type: build`       | `🔧 Build system`  | minor  | Modify build, including Docker      |
| `perf:`     | `type: performance` | `⚡️ Performance`  | patch  | Increase speed / decrease resources |
| `test:`     | `type: test`        | `🚨 Tests`         | N/A    | Add or modify tests                 |
| `refactor:` | `type: refactor`    | ignored            | N/A    | Refactor source code                |
| `style:`    | `type: style`       | ignored            | N/A    | Improve style of source code        |
| `chore:`    | `type: chore`       | ignored            | N/A    | Change non-source code              |
| `ci:`       | `type: ci`          | ignored            | N/A    | Modify CI/CD                        |

## For maintainers

### Merging pull requests

Maintainers must rebase pull requests to ensure linear history.
If changes are needed and the author does not respond, consider
[checking out the pull request locally](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/checking-out-pull-requests-locally).

### Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/)
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
