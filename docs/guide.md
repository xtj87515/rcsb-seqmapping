# Guide

This document describes how to get your new project up and running.

## First steps

1. Install and authorize [Probot settings](https://github.com/probot/settings).
2. Edit `pyproject.toml` and search for `# FIXME`. Fix all of those lines.
   !!! tip "Minimum required"
   You **must** edit these keys before proceeding:
   - `project.name`
   - `tool.tyranno.vendor`
     If you created with `tyranno new`, these were already filled in.
3. Generate a **classic**
   [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
4. Save it as `PAT`.
