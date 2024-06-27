"""
Commitizen plugin for the Commitizen package.

Implements a strict syntax for commit messages that narrows the conventional commit standard.
- Mandates a `!` for breaking changes.
- Limits trailers to a specific set.
- Adds trailer types 'Closes' (e.g. `Closes: #32, #44`)
  and 'BREAKING CHANGE' (e.g. `BREAKING CHANGE: /api/copy endpoint`).
- Adds extra commit types 'security' and 'deprecation'.
- Maps commit types to changelog sections and semver changes.
  'test', 'refactor', 'ci' are added to the 'Miscellaneous' section;
  'style', and 'chore' are not added to the changelog.
- Adds commit link, link to issue, and optional author to changelog entries.
- Replaces the 'BREAKING CHANGE' section with a bold 'Breaking change' note per entry.

**Expreimental; do not use.**
"""

import dataclasses
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Self

from commitizen.cz.base import BaseCommitizen
from commitizen.defaults import Questions
from commitizen.git import GitCommit

type ChangeHook = Callable[[str, ChangeInfo], str]


@dataclass(frozen=True, slots=True, order=True)
class CommitType:
    name: str
    label: str | None
    changelog_section: str | None
    semver_change: str | None
    description: str
    key: str | None = None


@dataclass(frozen=True, slots=True, order=True)
class Scope:
    name: str
    description: str
    key: str | None = None


@dataclass(frozen=True, slots=True, order=True)
class Trailer:
    name: str
    pattern: re.Pattern = ".*"


@dataclass(frozen=True, slots=True, order=True)
class ChangeInfo:
    rev: str
    change_type: str
    is_breaking: bool
    description: str
    body: str | None
    issues: list[str]
    trailers: list[str]
    scope: str | None
    sha1: str
    author: str
    author_email: str
    line: str

    @property
    def commit_link(self: Self) -> str:
        return f"/commit/{self.sha1}"

    @property
    def issue_links(self: Self) -> dict[str, str]:
        return {issue: f"/issues/{issue}" for issue in self.issues}


def _format_issues(msg: str, info: ChangeInfo) -> str:
    return f"{msg} (closes {", ".join(f"[#{num}]({uri})" for num, uri in info.issue_links.items())})"


def _format_scope(msg: str, info: ChangeInfo) -> str:
    return f"{info.scope}: {msg}"


def _format_breaking(msg: str, info: ChangeInfo) -> str:
    return f"{msg} [breaking change] 💥"


def _format_author(msg: str, info: ChangeInfo) -> str:
    return f"{msg} *– {info.author}*"


def _format_change(msg: str, info: ChangeInfo) -> str:
    return f"{msg} /[({info.sha1[:6]}]({info.commit_link})/"


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangelogHooks:
    format_scope: ChangeHook | None = _format_scope
    format_breaking: ChangeHook | None = _format_breaking
    format_author: ChangeHook | None = _format_author
    format_issues: ChangeHook | None = _format_issues
    format_change: ChangeHook | None = _format_change


@dataclass(frozen=True, slots=True)
class CommitizenGenerator:
    name: str
    commit_types: list[CommitType]
    changelog_sections: list[str]
    scopes: list[Scope]
    trailers: list[Trailer]
    hooks: ChangelogHooks

    def modify(
        self: Self,
        *,
        name: str | None = None,
        commit_types: list[CommitType] | None = None,
        changelog_sections: list[str] | None = None,
        scopes: list[Scope] | None = None,
        trailers: list[Trailer] | None = None,
        hooks: ChangelogHooks | None = None,
    ) -> Self:
        return dataclasses.replace(
            self,
            name=None if name is None else name,
            commit_types=None if commit_types is None else commit_types,
            changelog_sections=None if changelog_sections is None else changelog_sections,
            scopes=None if scopes is None else scopes,
            trailers=None if trailers is None else trailers,
            hooks=None if hooks is None else hooks,
        )

    def build(self: Self) -> BaseCommitizen:
        class X(BaseCommitizen):
            bump_pattern = "^(" + "|".join(c.name for c in self.commit_types) + ")"
            changelog_pattern = "^(" + "|".join(c.name for c in self.commit_types if c.changelog_section) + ")?(!)?"
            bump_map = {c.name: c.semver_change.upper() for c in self.commit_types if c.semver_change}
            commit_parser = f"""\
            ^\
            (?P<change_type>{"|".join(c.name for c in self.change_types)})\
            (?:\\((?P<scope>[-a-z0-9]+)\\))?\
            (?P<breaking>!)?\
            : (?P<message>[^\n]+)\
            .*\
            """
            change_type_map = {c.name: c.changelog_section for c in self.commit_types if c.changelog_section}

            def questions(self_: Self) -> Questions:
                """Questions regarding the commit message."""
                return [
                    dict(
                        type="list",
                        name="change_type",
                        message="Type of change:\n",
                        choices=[
                            dict(value=c.name, name=f"{c.name}: {c.description}", key=c.key) for c in self.commit_types
                        ],
                    ),
                    dict(
                        type="list",
                        name="breaking",
                        message="Breaking change? [y/n]\n",
                        choices=[dict(value="y", name="yes", key="y"), dict(value="n", name="no", key="n")],
                    ),
                    dict(
                        type="input",
                        name="description",
                        message="Short, lowercase, imperative summary:\n",
                    ),
                    dict(
                        type="list",
                        name="scope",
                        message="Scope: (press [enter] to skip).\n",
                        choices=[
                            dict(value="", name="[none]"),
                            *[dict(value=s.name, name=s.description) for s in self.scopes],
                        ],
                    ),
                    dict(
                        type="input",
                        name="body",
                        message="Optional body: (press [enter] to skip)\n",
                    ),
                    dict(
                        type="input",
                        name="issues",
                        multiline=True,
                        message="Closed issues, one per line; e.g. '#23': (press [enter] to skip)\n",
                    ),
                    dict(
                        type="input",
                        name="trailers",
                        multiline=True,
                        message="""\
                        Git trailers, one per line.\
                        Each must be in the form '<key>: <value>';\
                        e.g. 'Reviewed-by: John Johnson <john@git.com>': (press [enter] to skip)\n
                        """,
                    ),
                ]

            def message(self_: Self, a: dict[str, str]) -> str:
                change_type = a["change_type"].strip()
                scope = a.get("scope", "").strip()
                breaking = a["breaking"] == "y"
                description = a["description"].strip()
                body = a["body"].strip() if a["body"] else ""
                issues = [x.strip() for x in a.get("issues", "").splitlines()]
                trailers = [
                    (x.partition(": ")[0], x.partition(": ")[2].strip()) for x in a.get("trailers", "").splitlines()
                ]
                for trailer_name, _ in trailers:
                    if trailer_name not in {t.name for t in self.trailers}:
                        raise ValueError(
                            f"Trailer '{trailer_name}' is not allowed. Trailers are limited to "
                            f"{", ".join(t.name for t in self.trailers)}"
                        )
                # put co-authored-by first and signed-off-by last
                co_authored = [t for t in trailers if t[0] == "Co-authored-by"]
                signed_off = [t for t in trailers if t[0] == "Signed-off-by"]
                trailers = sorted([t for t in trailers if t[0] not in {"Co-authored-by", "Signed-off-by"}])
                footer = (
                    "".join(["\nCloses: " + i for i in issues])
                    + "".join([f"\n{t[0]}{t[1]}" for t in co_authored])
                    + "".join([f"\n{t[0]}{t[1]}" for t in trailers])
                    + "".join([f"\n{t[0]}{t[1]}" for t in signed_off])
                )
                return (
                    change_type
                    + ("(" + scope + ")" if scope else "")
                    + ("!" if breaking else "")
                    + f": {description}"
                    + (f"\n{body}" if body else "")
                    + ("\n" + footer if footer else "")
                )

            def example(self_: Self) -> str:
                return "feat(i18n): add Japanese translation"

            def schema(self_: Self) -> str:
                """Shows the schema used."""
                return """\
                <type>[(<scope>)][!]: <description>\n\n\
                <body>\n\n\
                [Closes: #<issue>]*\n\
                [<Trailer>: <text>]*\n\
                """

            def schema_pattern(self_: Self) -> str:
                return f"""\
                (?P<commit_type>{"|".join(c.name for c in self.commit_types)})\
                (?:\\((?P<scope>[-a-z0-9]+)\\))?\
                (?P<breaking>!)?\
                : (?P<subject>[^\n]+)\
                (?P<body>\n[^\n]+)?\
                (?P<issues>\nCloses: #\\d+(?:, \\d+)*)\
                (?P<trailers>\n[A-Za-z-]: [^\n]+)*\
                """

            def info(self_: Self) -> str:
                return """\
                    We use [Conventional Commits](https://www.conventionalcommits.org/) with the following types.\n\n\
                    | Type | Label | Changelog section | semver | Description |\n\
                    | ---- | ----- | ----------------- | ------ | ----------- |\n\
                    """ + "\n".join(
                    "| "
                    + f"`{c.name}`"
                    + " | "
                    + (f"`{c.label}`" if c.label else "N/A")
                    + " | "
                    + (f"`{c.changelog_section}`" if c.changelog_section else "ignored")
                    + " | "
                    + (c.semver_change if c.semver_change else "N/A")
                    + " | "
                    + c.description
                    + "|"
                    for c in self.commit_types
                )

        def changelog_message_builder_hook(self_: Self, match: dict[str, str], commit: GitCommit) -> dict[str, str]:
            info = ChangeInfo(
                rev=commit.rev,
                change_type=match["change_type"],
                is_breaking=match["breaking"] == "!",
                description=match["message"],
                scope=match["scope"],
                body=match["body"],
                issues=[i.strip() for i in match["issues"].split(", ")],
                trailers=[t.strip() for t in match["trailers"].split(", ")],
                sha1=commit.rev,
                author=commit.author,
                author_email=commit.author_email,
                line=commit.message,
            )
            if info.scope:
                info = self_.run_change_hook(self_.hooks.format_scope, info)
            if info.is_breaking:
                info = self_.run_change_hook(self_.hooks.format_breaking, info)
            info = self_.run_change_hook(self_.hooks.format_author, info)
            if len(info.issues) > 0:
                info = self.run_change_hook(self_.hooks.format_issues, info)
            info = self.run_change_hook(self_.hooks.format_change, info)
            match["message"] = info.line
            return match

        def run_change_hook(self_: Self, hook: ChangeHook | None, info: ChangeInfo) -> ChangeInfo:
            if hook is None:
                return info
            return dataclasses.replace(info, line=hook(info.line, info))

        X.__name__ = self.name
        return X(self.config)


Commitz = CommitizenGenerator(
    "Commitz",
    commit_types=[
        CommitType("feat", "type: feature", "✨ Features", "minor", "Add or change a feature", key="f"),
        CommitType("fix", "type: fix", "🐛 Bug fixes", "patch", "Fix a bug", key="x"),
        CommitType("security", "type: security", "🔒️ Security", "patch", "Fix a security issue", key="v"),
        CommitType("deprecation", "type: deprecation", "🗑️ Deprecation", None, "Deprecation", key="e"),
        CommitType("docs", "type: docs", "📝 Documentation", "patch", "Add or modify docs or examples", key="d"),
        CommitType("build", "type: build", "🔧 Build system", "minor", "Modify build, excluding bug fixes", key="b"),
        CommitType("perf", "type: performance", "⚡️ Performance", "patch", "Decrease resource usage", key="p"),
        CommitType("test", "type: test", "🍒 Miscellaneous", None, "Add or modify tests", key="t"),
        CommitType("refactor", "type: refactor", "🍒 Miscellaneous", None, "Refactor source code", key="r"),
        CommitType("ci", "type: ci", "🍒 Miscellaneous", None, "Alter CI/CD", key="c"),
        CommitType("style", "type: style", None, None, "Improve style of source code", key="s"),
        CommitType("chore", "type: chore", None, None, "Alter non-source code", key="z"),
    ],
    changelog_sections=[
        "✨ Features",
        "🔐 Security",
        "🗑️ Deprecation",
        "🐛 Bug fixes",
        "✏️ Documentation",
        "🔧 Build system",
        "⚡️ Performance",
        "🍒 Miscellaneous",
    ],
    scopes=[
        Scope("i18n", "i18n: Internationalization"),
    ],
    trailers=[
        Trailer("Acked-by"),
        Trailer("Reviewed-by"),
        Trailer("Helped-by"),
        Trailer("Reported-by"),
        Trailer("Mentored-by"),
        Trailer("Suggested-by"),
        Trailer("CC"),
        Trailer("Noticed-by"),
        Trailer("Tested-by"),
        Trailer("Improved-by"),
        Trailer("Thanks-to"),
        Trailer("Based-on-patch-by"),
        Trailer("Contributions-by"),
        Trailer("Co-authored-by"),
        Trailer("Requested-by"),
        Trailer("Original-patch-by"),
        Trailer("Inspired-by"),
        Trailer("Signed-off-by"),
    ],
    hooks=ChangelogHooks(),
)
