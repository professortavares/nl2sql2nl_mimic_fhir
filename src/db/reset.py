"""
Operações de reset do schema PostgreSQL.
"""

from __future__ import annotations

from sqlalchemy.engine import Connection
from sqlalchemy.schema import CreateSchema, DropSchema

from src.db.schema import validate_identifier


def reset_schema(connection: Connection, schema_name: str) -> None:
    """
    Remove e recria o schema alvo.

    Parâmetros:
    ----------
    connection : Connection
        Conexão SQLAlchemy ativa.
    schema_name : str
        Nome do schema a ser recriado.
    """

    validate_identifier(schema_name, label="schema_name")
    connection.execute(DropSchema(schema_name, cascade=True, if_exists=True))
    connection.execute(CreateSchema(schema_name))

