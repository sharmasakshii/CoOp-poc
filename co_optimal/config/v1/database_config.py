from typing import Optional

from co_optimal.config.v1 import BaseSettingsWrapper


class PostgresConfig(BaseSettingsWrapper):
    """
    Configuration class for PostgreSQL database settings

    :param POSTGRES_DB_NAME: The name of the PostgreSQL database
    :type POSTGRES_DB_NAME: str

    :param POSTGRES_HOST: The host address of the PostgreSQL server
    :type POSTGRES_HOST: str

    :param POSTGRES_USERNAME: The username for PostgreSQL authentication
    :type POSTGRES_USERNAME: Optional[str]

    :param POSTGRES_PASSWORD: The password for PostgreSQL authentication
    :type POSTGRES_PASSWORD: Optional[str]

    :param POSTGRES_PORT: The port number for PostgreSQL connection
    :type POSTGRES_PORT: int

    :param POSTGRES_SSLMODE: SSL mode for PostgreSQL connection
    :type POSTGRES_SSLMODE: str

    :returns: Instance of PostgresConfig with specific settings
    :return type: PostgresConfig
    """

    POSTGRES_DB_NAME: str = "co_optimal"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_USERNAME: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_PORT: int = 5432
    POSTGRES_SSLMODE: str = "prefer"


postgres_config = PostgresConfig()
