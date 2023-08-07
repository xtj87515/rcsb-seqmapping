# SPDX-FileCopyrightText: Copyright 2020-2023, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0
from typing import Self

import pytest


class TestMain:
    def test_it(self: Self) -> None:
        assert True


if __name__ == "__main__":
    pytest.main()
