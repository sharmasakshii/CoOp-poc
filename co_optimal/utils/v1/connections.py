# co_optimal/utils/v1/connections.py
import logging
from typing import Optional
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection as pg_connection
from psycopg2.extras import RealDictCursor
from psycopg2 import pool

from co_optimal.config.v1.database_config import postgres_config
from co_optimal.utils.v1.generic_helper import Singleton

logger = logging.getLogger(__name__)


class PostgresConnectionPool(Singleton):
    def __init__(self):
        if not hasattr(self, "connection_pool"):
            self.connection_pool: Optional[pool.ThreadedConnectionPool] = None
            self.min_connections = 1
            self.max_connections = 10

    def create_pool(
        self,
        POSTGRES_DB_NAME: str,
        POSTGRES_HOST: str,
        POSTGRES_USERNAME: Optional[str],
        POSTGRES_PASSWORD: Optional[str],
        POSTGRES_PORT: Optional[int] = 5432,
    ) -> pool.ThreadedConnectionPool:
        if self.connection_pool:
            logger.info("PostgreSQL connection pool already exists.")
            return self.connection_pool

        try:
            connection_params = {
                "dbname": POSTGRES_DB_NAME,
                "host": POSTGRES_HOST,
                "port": POSTGRES_PORT,
            }
            if POSTGRES_USERNAME:
                connection_params["user"] = POSTGRES_USERNAME
            if POSTGRES_PASSWORD:
                connection_params["password"] = POSTGRES_PASSWORD

            # Add SSL configuration for Azure PostgreSQL
            if (
                "azure" in POSTGRES_HOST.lower()
                or "postgres.database.azure.com" in POSTGRES_HOST
            ):
                connection_params["sslmode"] = "require"
                connection_params["sslrootcert"] = None

            self.connection_pool = pool.ThreadedConnectionPool(
                minconn=self.min_connections,
                maxconn=self.max_connections,
                cursor_factory=RealDictCursor,
                **connection_params,
            )
            logger.info("PostgreSQL connection pool established successfully")
            return self.connection_pool
        except Exception as e:
            logger.error(f"Error creating PostgreSQL connection pool: {str(e)}")
            raise

    def get_connection(self) -> pg_connection:
        if not self.connection_pool:
            raise RuntimeError(
                "Connection pool not initialized. Call create_pool() first."
            )
        return self.connection_pool.getconn()

    def return_connection(self, connection: pg_connection):
        if self.connection_pool and connection:
            self.connection_pool.putconn(connection)

    @contextmanager
    def get_connection_context(self):
        """Context manager for safe connection handling"""
        connection = None
        try:
            connection = self.get_connection()
            yield connection
        finally:
            if connection:
                self.return_connection(connection)

    def close_pool(self):
        if self.connection_pool:
            try:
                self.connection_pool.closeall()
                logger.info("PostgreSQL connection pool closed successfully")
            except Exception as e:
                logger.error(f"Error closing PostgreSQL connection pool: {str(e)}")
            self.connection_pool = None

    def check_pool_health(self) -> bool:
        try:
            with self.get_connection_context() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result and result.get("?column?") == 1:
                        logger.info("PostgreSQL connection pool is working")
                        return True
            return False
        except Exception as e:
            logger.error(f"PostgreSQL connection pool health check failed: {str(e)}")
            return False


def create_connections():
    logger.info("Creating connection pool")
    return PostgresConnectionPool().create_pool(
        POSTGRES_DB_NAME=postgres_config.POSTGRES_DB_NAME,
        POSTGRES_HOST=postgres_config.POSTGRES_HOST,
        POSTGRES_USERNAME=postgres_config.POSTGRES_USERNAME,
        POSTGRES_PASSWORD=postgres_config.POSTGRES_PASSWORD,
        POSTGRES_PORT=postgres_config.POSTGRES_PORT,
    )


def remove_connections():
    PostgresConnectionPool().close_pool()


def check_connections():
    logger.info("Checking connection pool")
    return PostgresConnectionPool().check_pool_health()


# Convenience function for getting a connection from the pool
def get_db_connection() -> pg_connection:
    return PostgresConnectionPool().get_connection()


# Convenience function for returning a connection to the pool
def return_db_connection(connection: pg_connection):
    PostgresConnectionPool().return_connection(connection)


# Context manager for safe database operations
@contextmanager
def db_connection_context():
    """Safe context manager for database operations"""
    pool_instance = PostgresConnectionPool()
    with pool_instance.get_connection_context() as conn:
        yield conn
