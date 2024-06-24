# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0
"""
CI/CD example.
"""

from cicd._project_metadata import ProjectMetadata as __ProjectMetadata

__metadata__ = __ProjectMetadata
__uri__ = __ProjectMetadata.homepage
__title__ = __ProjectMetadata.title
__summary__ = __ProjectMetadata.summary
__version__ = __ProjectMetadata.version
__license__ = __ProjectMetadata.license
