import asyncio
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Self

import aenum
import cramjam
from fastapi import FastAPI
from msgpack_asgi import MessagePackMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette_cramjam.compression import Compression, compression_backends
from starlette_cramjam.middleware import CompressionMiddleware

__all__ = ["Middleware"]

aenum.extend_enum(Compression, "snappy", "snappy")
aenum.extend_enum(Compression, "lz4", "lz4")
aenum.extend_enum(Compression, "zstd", "zstd")
compression_backends["snappy"] = cramjam.snappy
compression_backends["lz4"] = cramjam.lz4
compression_backends["zstd"] = cramjam.zstd
all_compression_methods = frozenset({"deflate", "gzip", "br", "snappy", "lz4", "zstd"})

if os.name == "nt":
    # workaround for asyncio loop policy for Windows users
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@dataclass(frozen=True, slots=True, kw_only=True)
class Middleware:
    dev_mode: bool
    allowed_hosts: Iterable[str] = frozenset({"*"})
    cors: Mapping[str, Any] | None = None
    compression_methods: Iterable[str] = all_compression_methods

    def add_to(self: Self, app: FastAPI) -> None:
        app.add_middleware(ServerErrorMiddleware)
        if not self.dev_mode:
            app.add_middleware(HTTPSRedirectMiddleware)
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=self.allowed_hosts)
        app.add_middleware(ExceptionMiddleware)
        app.add_middleware(SessionMiddleware)
        if self.cors:
            app.add_middleware(CORSMiddleware, **self.cors)
        app.add_middleware(CompressionMiddleware, compression=list(self.compression_methods))
        app.add_middleware(MessagePackMiddleware)
