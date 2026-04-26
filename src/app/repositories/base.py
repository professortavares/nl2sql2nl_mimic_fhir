"""
Funções compartilhadas pelos repositórios do app Streamlit.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.engine import Connection


def qualified_table_name(schema_name: str, table_name: str) -> str:
    """
    Retorna o nome totalmente qualificado de uma tabela.
    """

    return f'"{schema_name}"."{table_name}"' if schema_name else f'"{table_name}"'


def fetch_mappings(connection: Connection, sql: str, params: Mapping[str, Any]) -> list[dict[str, Any]]:
    """
    Executa uma consulta e retorna o resultado como lista de dicionários.
    """

    result = connection.execute(text(sql), params)
    return [dict(row) for row in result.mappings().all()]


def fetch_mappings_expanding(
    connection: Connection,
    sql: str,
    params: Mapping[str, Any],
    *,
    expanding_parameter_names: tuple[str, ...],
) -> list[dict[str, Any]]:
    """
    Executa uma consulta com parâmetros `IN` expansíveis.
    """

    statement = text(sql)
    for parameter_name in expanding_parameter_names:
        statement = statement.bindparams(bindparam(parameter_name, expanding=True))
    result = connection.execute(statement, params)
    return [dict(row) for row in result.mappings().all()]
