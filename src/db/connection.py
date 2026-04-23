"""
Criação de conexões e engines PostgreSQL.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL

from src.config.settings import DatabaseSettings


def build_database_url(settings: DatabaseSettings) -> URL:
    """
    Monta a URL de conexão do PostgreSQL.

    Parâmetros:
    ----------
    settings : DatabaseSettings
        Configurações de conexão carregadas do `.env`.

    Retorno:
    -------
    URL
        URL SQLAlchemy pronta para uso.
    """

    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.user,
        password=settings.password,
        host=settings.host,
        port=settings.port,
        database=settings.database,
    )


def create_engine_from_settings(settings: DatabaseSettings) -> Engine:
    """
    Cria uma engine SQLAlchemy configurada para o PostgreSQL local.

    Parâmetros:
    ----------
    settings : DatabaseSettings
        Configurações de banco e comportamento.

    Retorno:
    -------
    Engine
        Engine SQLAlchemy pronta para uso.
    """

    return create_engine(
        build_database_url(settings),
        echo=settings.echo,
        pool_pre_ping=settings.pool_pre_ping,
        future=True,
    )
