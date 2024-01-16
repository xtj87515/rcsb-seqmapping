import re
from dataclasses import dataclass
from typing import Self

from commitizen.cz.base import BaseCommitizen
from commitizen.defaults import Questions


@dataclass(frozen=True, slots=True)
class CommitType:
    name: str
    label: str | None
    changelog_section: str | None
    semver_change: str | None
    description: str
    key: str | None = None


@dataclass(frozen=True, slots=True)
class Scope:
    name: str
    description: str
    key: str | None = None


@dataclass(frozen=True, slots=True)
class Trailer:
    name: str
    pattern: re.Pattern = ".*"


@dataclass(frozen=True, slots=True)
class CommitzGenerator(BaseCommitizen):
    name: str
    commit_types: list[CommitType]
    changelog_sections: list[str]
    scopes: list[Scope]
    trailers: list[Trailer]

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

            def questions(self_) -> Questions:
                """Questions regarding the commit message."""
                return [
                    dict(
                        type="list",
                        name="change_type",
                        message="Select the type of change you are committing\n",
                        choices=[
                            dict(value=c.name, name=f"{c.name}: {c.description}", key=c.key) for c in self.commit_types
                        ],
                    ),
                    dict(
                        type="input",
                        name="subject",
                        message="A short, imperative summary: (lowercase and no period).\n",
                    ),
                    dict(
                        type="list",
                        name="scope",
                        message="Scope (press [enter] to skip).\n",
                        choices=[
                            dict(value="", name="[none]"),
                            *[dict(value=s.name, name=s.description) for s in self.scopes],
                        ],
                    ),
                    dict(
                        type="input",
                        name="body",
                        message="Body. Additional information: (press [enter] to skip)\n",
                    ),
                    dict(
                        type="list",
                        name="breaking",
                        message="Is this a breaking change? [y/n]\n",
                        choices=[dict(value="y", name="yes", key="y"), dict(value="n", name="no", key="n")],
                    ),
                    dict(
                        type="input",
                        name="issues",
                        message="Closed issues, separated by commas: (press [enter] to skip)\n",
                    ),
                    dict(
                        type="input",
                        name="trailers",
                        multiline=True,
                        message="""\
                        Git trailers, separated by newlines.\
                        Each must be in the form '<key>: <value>';\
                        e.g., 'Reviewed-by: John Johnson <john@git.com>': (press [enter] to skip)\n
                        """,
                    ),
                ]

            def message(self_, a: dict) -> str:
                change_type = a["change_type"].strip()
                scope = a.get("scope", "").strip()
                breaking = a["breaking"] == "y"
                subject = a["subject"].strip()
                body = a["body"].strip() if a["body"] else ""
                issues = [x.strip() for x in a.get("issues", "").split(",")]
                trailers = [
                    (x.partition(": ")[0], x.partition(": ")[2].strip()) for x in a.get("trailers", "").split("||")
                ]
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
                    + f": {subject}"
                    + (f"\n{body}" if body else "")
                    + ("\n" + footer if footer else "")
                )

            def example(self_) -> str:
                return "feat(i18n): add Japanese translation"

            def schema(self_) -> str:
                """Show the schema used."""
                return """\
                <type>[(<scope>)][!]: <subject>\n\n\
                <body>\n\n\
                [Closes: #<issue>]*\n\
                [Some-trailer: <text>]*\n\
                """

            def schema_pattern(self_) -> str | None:
                return f"""\
                ({"|".join(c.name for c in self.commit_types)})\
                (?:\\(\\([-a-z0-9]+)\\))?\
                (!)?\
                : ([^\n]+)\
                \n?\
                (?:\nCloses: #(\\d+))*\
                (?:\n((?:\
                  {"|".join(t.name for t in self.trailers)}
                ): [^\n]+))*\
                """

            def info(self_):
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

        X.__name__ = self.name
        return X()


Commitz = CommitzGenerator(
    "Commitz",
    commit_types=[
        CommitType("feat", "type: feature", "✨ Features", "minor", "Add or change a feature", key="f"),
        CommitType("fix", "type: fix", "🐛 Bug fixes", "patch", "Fix a bug", key="x"),
        CommitType("security", "type: security", "🔒 Security", "patch", "Fix a security issue", key="v"),
        CommitType("docs", "type: docs", "📚 Documentation", "patch", "Add or modify docs or examples", key="d"),
        CommitType("build", "type: build", "🔧 Build system", "minor", "Modify build, excluding bug fixes", key="b"),
        CommitType("perf", "type: performance", "⚡️ Performance", "patch", "Decrease resource usage", key="p"),
        CommitType("test", "type: test", "⛵ Miscellaneous", None, "Add or modify tests", key="t"),
        CommitType("refactor", "type: refactor", "⛵ Miscellaneous", None, "Refactor source code", key="r"),
        CommitType("ci", "type: ci", "⛵ Miscellaneous", None, "Alter CI/CD", key="c"),
        CommitType("style", "type: style", None, None, "Improve style of source code", key="s"),
        CommitType("chore", "type: chore", None, None, "Alter non-source code", key="z"),
    ],
    changelog_sections=[
        "✨ Features",
        "🔒 Security",
        "🐛 Bug fixes",
        "📚 Documentation",
        "🔧 Build system",
        "⚡️ Performance",
        "⛵ Miscellaneous",
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
).build()
