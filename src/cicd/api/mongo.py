import os
from collections.abc import Mapping
from functools import cached_property
from typing import Any, Self

from pymongo import MongoClient
from pymongo.collection import Collection as MongoCollection
from pymongo.database import Database

__all__ = ["MONGO"]


class _Mongo:
    def __getattr__(self, item: str) -> MongoCollection[Mapping[str, Any]]:
        return self.instance[item]

    def __getitem__(self, item: str) -> MongoCollection[Mapping[str, Any]]:
        return self.instance[item]

    @cached_property
    def instance(self: Self) -> Database[Mapping[str, Any]]:
        return MongoClient(os.environ["MONGODB_URI"])["app"]


MONGO = _Mongo()
