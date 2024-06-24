# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0
"""
CLI for CICD.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Self

import typer
from loguru import logger

from cicd._project_metadata import ProjectMetadata
from cicd.context import Context, DefaultContextFactory


@dataclass(frozen=True, slots=True, kw_only=True)
class Messenger:
    success_color: str = typer.colors.GREEN
    error_color: str = typer.colors.RED

    def success(self: Self, msg: str) -> None:
        typer.echo(typer.style(msg, fg=self.success_color, bold=True))

    def info(self: Self, msg: str) -> None:
        typer.echo(msg)

    def failure(self: Self, msg: str) -> None:
        typer.echo(typer.style(msg, fg=self.error_color, bold=True))

    def write_info(self: Self) -> None:
        self.info(f"{ProjectMetadata.pkg} v{ProjectMetadata.version}")


@dataclass(frozen=True, slots=True, kw_only=True)
class CliState:
    verbose: bool = False
    quiet: bool = False

    def __post_init__(self: Self) -> None:
        logger.remove()
        if self.verbose:
            logger.add(sys.stderr, level="DEBUG")
        elif self.quiet:
            logger.add(sys.stderr, level="WARNING")
        else:
            logger.add(sys.stderr, level="INFO")


class _Opts:
    dry_run = Annotated[bool, typer.Option(allow_dash=True, help="Don't write; just output")]
    verbose = Annotated[bool, typer.Option("Show DEBUG-level logging")]
    quiet = Annotated[bool, typer.Option("Hide INFO-level logging")]


Msg = Messenger()
cli = typer.Typer()


class CliCommands:
    """
    Commands for Tyranno.
    """

    @staticmethod
    @cli.command()
    def new(
        path: Annotated[Path, typer.Argument("name", help="name", exists=False)] = Path.cwd(),
        *,
        name: Annotated[str, typer.Option(help="Full project name")] = "my-project",
        vendor: Annotated[str, typer.Option(help="vendor")] = "@git.user",
        version: Annotated[str, typer.Option(help="version")] = "0.0.0",
        description: Annotated[str, typer.Option(help="description")] = "my project",
        keywords: Annotated[list[str] | None, typer.Option(help="keywords")] = None,
        classifiers: Annotated[list[str] | None, typer.Option(help="PyPi classifiers")] = None,
        license_id: Annotated[str, typer.Option("--license", help="vendor")] = "Apache-2.0",
        prompt: Annotated[bool, typer.Option(help="Prompt for info")] = False,
        dry_run: _Opts.dry_run = False,
        verbose: _Opts.verbose = False,
        quiet: _Opts.quiet = False,
    ) -> None:
        if classifiers is None:
            classifiers = []
        if keywords is None:
            keywords = []
        if path is None and name is None:
            raise typer.Exit()
        CliState(verbose=verbose, quiet=quiet)
        typer.echo(f"Done! Created a new repository under {name}")
        Msg.success("See https://dmyersturnbull.github.io/tyranno/guide.html")

    @staticmethod
    @cli.command()
    def sync(
        *,
        dry_run: _Opts.dry_run = False,
        verbose: _Opts.verbose = False,
        quiet: _Opts.quiet = False,
    ) -> None:
        """
        Sync project metadata between configured files.
        """
        state = CliState(verbose=verbose, quiet=quiet)
        context = DefaultContextFactory()(Path(os.getcwd()), dry_run=dry_run)
        Msg.info("Syncing metadata...")
        Msg.info("Currently, only targets 'init' and 'recipe' are implemented.")
        # targets = Sync(context).sync()
        # Msg.success(f"Done. Synced to {len(targets)} targets: {targets}")

    @staticmethod
    @cli.command()
    def env(
        *,
        path: Annotated[Path, typer.Option("environment.yaml", help="Write to this path")] = Path.cwd(),
        name: Annotated[str, typer.Option("${project.name}", help="Name of the environment")] = "environment.yaml",
        dependency_groups: Annotated[list[str] | None, typer.Option([], help="Dependency groups to include")] = None,
        dry_run: _Opts.dry_run = False,
        verbose: _Opts.verbose = False,
        quiet: _Opts.quiet = False,
    ) -> None:
        if dependency_groups is None:
            dependency_groups = []
        CliState(verbose=verbose, quiet=quiet)
        typer.echo("Writing environment file...")
        Msg.success(f"Wrote environment file {path}")

    @staticmethod
    @cli.command()
    def recipe(
        *,
        dry_run: _Opts.dry_run = False,
        verbose: _Opts.verbose = False,
        quiet: _Opts.quiet = False,
    ) -> None:
        CliState(verbose=verbose, quiet=quiet)

    @staticmethod
    @cli.command()
    def reqs(
        dry_run: _Opts.dry_run = False,
        verbose: _Opts.verbose = False,
        quiet: _Opts.quiet = False,
    ) -> None:
        CliState(verbose=verbose, quiet=quiet)
        Context.this()

    @staticmethod
    @cli.command(help="Removes unwanted files")
    def clean(
        dry_run: _Opts.dry_run = False,
        verbose: _Opts.verbose = False,
        quiet: _Opts.quiet = False,
    ) -> None:
        CliState(verbose=verbose, quiet=quiet)
        # trashed = Clean(dists, aggressive, hard_delete, dry_run).clean(Path(os.getcwd()))
        # Msg.info(f"Trashed {len(trashed)} paths.")


if __name__ == "__main__":
    cli()
