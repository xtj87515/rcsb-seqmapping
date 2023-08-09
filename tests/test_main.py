# SPDX-FileCopyrightText: Copyright 2020-2023, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from typing import Self

import cicd
import pytest


class TestMain:
    def test_it(self: Self) -> None:
        assert cicd.run(Path()) is None


if __name__ == "__main__":
    pytest.main()
