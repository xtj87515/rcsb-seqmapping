# SPDX-FileCopyrightText: Copyright 2020-2023, Contributors to CICD
# SPDX-PackageHomePage: https://github.com/dmyersturnbull/cicd
# SPDX-License-Identifier: Apache-2.0


import aenum
import cramjam
from bson import ObjectId, json_util
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_sso.sso.github import GithubSSO
from msgpack_asgi import MessagePackMiddleware
from pymongo import MongoClient
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette_cramjam.compression import Compression, compression_backends
from starlette_cramjam.middleware import CompressionMiddleware

from cicd._metadata import ProjectInfo, Vars

app = FastAPI(**Vars.api_metadata)
mongo = MongoClient(Vars.mongodb_uri)["app"]


sso = GithubSSO(
    client_id=Vars.client_id,
    client_secret=Vars.client_secret,
    redirect_uri=Vars.api_url + "/auth/callback",
    allow_insecure_http=Vars.dev_mode,
)

aenum.extend_enum(Compression, "snappy", "snappy")
aenum.extend_enum(Compression, "lz4", "lz4")
aenum.extend_enum(Compression, "zstd", "zstd")
compression_backends["snappy"] = cramjam.snappy
compression_backends["lz4"] = cramjam.lz4
compression_backends["zstd"] = cramjam.zstd

app.add_middleware(ServerErrorMiddleware)
if not Vars.dev_mode:
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=Vars.host)
app.add_middleware(ExceptionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "POST", "PUT"],
    allow_headers=["*"],
)
app.add_middleware(CompressionMiddleware, compression=list(Compression))
app.add_middleware(MessagePackMiddleware)


@app.get("/")
async def root():
    return {"name": ProjectInfo.summary}


@app.put("/data", response_class=ORJSONResponse)
async def put_data(post: dict):
    print(f"Received PUT: '{post}'")
    the_id = mongo.data.insert_one(post).inserted_id
    result = json_util.dumps({"id": the_id})
    print(f"Saved as ID '{the_id}'")
    print(f"Returning data '{result}'")
    return ORJSONResponse(result)


@app.get("/data/{the_id}", response_class=ORJSONResponse)
async def get_data(the_id: str):
    print(f"Received GET for ID '{the_id}'")
    data = mongo.data.find_one({"_id": ObjectId(the_id)})
    result = json_util.dumps(data)
    print(f"Returning data '{result}'")
    return ORJSONResponse(result)


@app.get("/auth/login")
async def auth_init():
    """Initializes auth and redirect."""
    return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verifies login."""
    return await sso.verify_and_process(request)
