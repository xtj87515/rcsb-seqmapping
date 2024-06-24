# SPDX-FileCopyrightText: Copyright 2020-2024, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0
"""

"""

from datetime import datetime
from operator import itemgetter
from typing import Self
from zoneinfo import ZoneInfo

import httpx
import orjson
from jmespath import functions
from semver import Version

NOW_LOCAL = datetime.now().astimezone()
NOW_UTC = NOW_LOCAL.astimezone(ZoneInfo("Etc/UTC"))
LOCAL_TIMESTAMP = NOW_LOCAL.isoformat(timespec="microseconds")
UTC_TIMESTAMP = NOW_UTC.isoformat(timespec="microseconds").replace("+00:00", "Z")


class TyrannoFunctions(functions.Functions):
    """ """

    @functions.signature({"types": ["list", "string"]})
    def _func_semver_max(self: Self, versions: list[str] | str) -> str:
        if isinstance(versions, str):
            return versions
        return str(max(Version.parse(v) for v in versions))

    @functions.signature({"types": ["list", "string"]})
    def _func_semver_min(self: Self, versions: list[str] | str) -> str:
        if isinstance(versions, str):
            return versions
        return str(min(Version.parse(v) for v in versions))

    @functions.signature({"types": ["list"]})
    def _func_semver_major_list(self: Self, versions: list[str]) -> list[str]:
        return [str(Version.parse(v).major) for v in versions]

    @functions.signature({"types": ["string"]})
    def _func_semver_major(self: Self, version: str) -> str:
        return str(Version.parse(version).major)

    @functions.signature({"types": ["list"]})
    def _func_semver_minor_list(self: Self, versions: list[str]) -> list[str]:
        return [str(Version.parse(v).minor) for v in versions]

    @functions.signature({"types": ["string"]})
    def _func_semver_minor(self: Self, version: str) -> str:
        return str(Version.parse(version).minor)

    @functions.signature({"types": ["list"]})
    def _func_semver_patch_list(self: Self, versions: list[str]) -> list[str]:
        return [str(Version.parse(v).patch) for v in versions]

    @functions.signature({"types": ["string"]})
    def _func_semver_patch(self: Self, version: str) -> str:
        return str(Version.parse(version).patch)

    @functions.signature({"types": ["string"]})
    def _func_spdx_license(self: Self, short: str) -> dict[str, str]:
        url = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/details/" + short + ".json"
        response = httpx.get(url)
        if response.status_code != 200:
            msg = f"Failed to get {url} (status code {response.status_code})"
            raise OSError(msg)
        data = orjson.loads(response.content)
        urls = (u for u in data["crossRef"] if u.get("isValid") and u.get("isLive"))
        urls = sorted(urls, key=itemgetter("order"))
        # noinspection HttpUrlsUsage
        urls = [u.url.replace("http://", "https://") for u in urls]
        return {
            "id": short,
            "name": data["name"],
            "url": f"https://spdx.org/licenses/${short}.html",
            "urls": urls,
            "header": f"SPDX-License-Identifier: ${short}",
            "text": data["licenseText"],
        }

    @functions.signature({"types": ["string"]})
    def _func_now_local(self: Self) -> str:
        return LOCAL_TIMESTAMP

    @functions.signature({"types": ["string"]})
    def _func_now_utc(self: Self) -> str:
        return UTC_TIMESTAMP

    @functions.signature({"types": ["string"]}, {"types": ["string"]})
    def _func_format_datetime(self: Self, dt: str, fmt: str) -> str:
        return datetime.fromisoformat(dt.replace("Z", "+00:00")).strftime(fmt)

    @functions.signature({"types": ["string"]})
    def _func_year(self: Self, dt: str) -> str:
        return datetime.fromisoformat(dt.replace("Z", "+00:00")).strftime("%Y")

    @functions.signature({"types": ["string"]})
    def _func_date(self: Self, dt: str) -> str:
        return datetime.fromisoformat(dt.replace("Z", "+00:00")).strftime("%Y-%m-%d")

    @functions.signature({"types": ["dict"]})
    def _func_pypi_data(self: Self, obj: dict[str, str]) -> dict:
        name, version = obj["name"], obj["version"]
        response = httpx.get(f"https://pypi.org/pypi/${name}/json")
        if response.status_code != 200:
            return orjson.loads(response.text)
        msg = f"Failed with {response}"
        raise OSError(msg)  # TODO
