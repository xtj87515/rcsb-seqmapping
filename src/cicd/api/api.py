from pathlib import Path

from bson import ObjectId, json_util
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_sso.sso.github import GithubSSO
from starlette.requests import Request
from starlette.responses import FileResponse

from cicd._internal import Metadata
from cicd.api._internal import ApiMeta
from cicd.api.middleware import Middleware

__all__ = ["app"]

from cicd.api.mongo import MONGO

app = FastAPI(**ApiMeta.metadata)
Middleware(dev_mode=ApiMeta.dev_mode).add_to(app)


sso = GithubSSO(
    client_id=ApiMeta.client_id,
    client_secret=ApiMeta.client_secret,
    redirect_uri=ApiMeta.api_url + "/auth/callback",
    allow_insecure_http=ApiMeta.dev_mode,
)


@app.get("/auth/login")
async def auth_init():
    """Initializes auth and redirect."""
    return await sso.get_login_redirect()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Verifies login."""
    with sso:
        await sso.verify_and_process(request)


@app.get("/")
async def root():
    return {"name": ApiMeta.metadata["title"], "version": Metadata.version}


@app.put("/data", response_class=ORJSONResponse)
def put_data(post: dict) -> ORJSONResponse:
    print(f"Received PUT: '{post}'")
    the_id = MONGO.data.insert_one(post).inserted_id
    result = json_util.dumps({"id": the_id})
    print(f"Saved as ID '{the_id}'")
    print(f"Returning data '{result}'")
    return ORJSONResponse(result)


@app.get("/data/{the_id}", response_class=ORJSONResponse)
def get_data(the_id: str) -> ORJSONResponse:
    print(f"Received GET for ID '{the_id}'")
    data = MONGO.data.find_one({"_id": ObjectId(the_id)})
    result = json_util.dumps(data)
    print(f"Returning data '{result}'")
    return ORJSONResponse(result)


@app.get("/video/{the_id}")
def video(the_id: str) -> FileResponse:
    return FileResponse(Path(the_id), media_type='video/webm; codecs="av01"')
