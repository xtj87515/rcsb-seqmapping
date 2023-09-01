import os
from collections.abc import AsyncIterator
from functools import cached_property
from typing import Any, Self

import psycopg_pool
from psycopg import AsyncConnection, AsyncCursor
from psycopg_pool import AsyncConnectionPool

__all__ = ["POSTGRES"]


class _PostgresConnPool:
    @cached_property
    def instance(self: Self) -> AsyncConnectionPool:
        return psycopg_pool.AsyncConnectionPool(conninfo=os.environ["POSTGRES_URI"], open=True)

    async def connection(self: Self) -> AsyncIterator[AsyncConnection]:
        return await self.instance.connection()

    async def cursor(self: Self) -> AsyncIterator[AsyncCursor]:
        async with self.instance.connection() as conn, conn.cursor() as cursor:
            return cursor

    async def execute(self: Self, select: str, data: tuple[Any, ...]) -> None:
        """
        Executes a PostgreSQL query, returning nothing.
        """
        # row_factory=dict_row is broken
        async with self.instance.connection() as conn, conn.cursor() as cursor:
            await cursor.execute(select, data)

    async def fetch_one(self: Self, select: str, data: tuple[Any, ...]) -> tuple:
        """
        Executes a PostgreSQL query, returning the first result.
        """
        # row_factory=dict_row is broken
        async with self.instance.connection() as conn, conn.cursor() as cursor:
            await cursor.execute(select, data)
            return await cursor.fetchone()

    async def fetch_all(self: Self, select: str, data: tuple[Any, ...]) -> tuple:
        """
        Executes a PostgreSQL query, returning all results.
        """
        # row_factory=dict_row is broken
        async with self.instance.connection() as conn, conn.cursor() as cursor:
            await cursor.execute(select, data)
            return await cursor.fetchall()


POSTGRES = _PostgresConnPool()
