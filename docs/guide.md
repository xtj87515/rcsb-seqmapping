# Guide

This document describes how to get your new project up and running.

## First steps

1. Clone this repository.
2. Generate a **classic**
   [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
   Save it as `PAT`.
3. Add secrets `GPG_PRIVATE_KEY` and `GPG_PASSPHRASE`.
4. If you want to use Coveralls, CodeCov.io, PyPi, and/or Docker Hub, add the relevant secrets:
   `COVERALLS_TOKEN`, `CODECOV_TOKEN`, `PYPI_TOKEN`, `DOCKERHUB_TOKEN`+`DOCKERHUB_USERNAME`.
5. Open `pyproject.toml`, and edit the `[project]` and `[tool.tyranno]` sections.
   When finished, run `tyranno sync`.

!!! warning

    Some repository settings will be overridden:
    Pushing updates the repository description, homepage, keywords, and issue labels
    with the values in `.github/project.yaml`.
    You can control this behavior in `.github/workflows/set-repo-metadata.yaml`.

## Notes

We do not follow [Keep a Changelog](https://keepachangelog.com/).
Instead, we use [GitHub release notes](https://docs.github.com/en/github/administering-a-repository/managing-releases-in-a-repository).
See the [maintainer guide](https://dmyersturnbull.github.io/ref/maintainer-guide/) for more information.
