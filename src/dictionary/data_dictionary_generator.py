"""
Geração do dicionário de dados em YAML a partir do schema e dos dados carregados.
"""

from __future__ import annotations

import enum
import logging
from collections.abc import Mapping
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml
from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.engine import Connection, Engine

LOGGER = logging.getLogger(__name__)
_DEFAULT_DESCRIPTION = "Descrição não informada."


def generate_data_dictionary(output_path: Path, engine: Engine, descriptions_config: dict) -> None:
    """
    Gera o dicionário de dados da base relacional em formato YAML.

    Parâmetros:
    ----------
    output_path : Path
        Caminho final do arquivo YAML a ser gerado.
    engine : Engine
        Engine SQLAlchemy conectada ao banco PostgreSQL.
    descriptions_config : dict
        Configuração com descrições humanas das tabelas e colunas.

    Retorno:
    -------
    None

    Exceções:
    --------
    Levanta RuntimeError em caso de falha na introspecção do banco ou escrita do arquivo.
    """

    output_path = Path(output_path)
    LOGGER.info("Iniciando geração do dicionário de dados em %s", output_path)

    try:
        data = _build_dictionary_payload(engine, descriptions_config)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        LOGGER.info(
            "Dicionário de dados gerado em %s com %s tabelas documentadas",
            output_path,
            len(data["tables"]),
        )
    except Exception as exc:  # pragma: no cover - erro operacional
        LOGGER.exception("Falha ao gerar o dicionário de dados em %s", output_path)
        raise RuntimeError(f"Falha ao gerar o dicionário de dados em {output_path}") from exc


def _build_dictionary_payload(engine: Engine, descriptions_config: Mapping[str, Any]) -> dict[str, Any]:
    """
    Monta a estrutura final do dicionário de dados.
    """

    schema_name = _optional_string(descriptions_config.get("schema_name"))
    database_config = _mapping_or_empty(descriptions_config.get("database"))
    database_name = _optional_string(database_config.get("name")) or _fallback_database_name(engine)
    database_description = _optional_string(database_config.get("description")) or _DEFAULT_DESCRIPTION
    include_examples = _optional_bool(descriptions_config.get("include_examples"), default=True)
    max_examples = _positive_int_or_default(descriptions_config.get("max_examples_per_column"), 3)
    table_descriptions = _mapping_or_empty(descriptions_config.get("tables"))

    with engine.connect() as connection:
        inspector = inspect(connection)
        table_names = sorted(inspector.get_table_names(schema=schema_name))
        tables = [
            _build_table_entry(
                connection=connection,
                inspector=inspector,
                table_name=table_name,
                schema_name=schema_name,
                table_descriptions=table_descriptions,
                include_examples=include_examples,
                max_examples=max_examples,
            )
            for table_name in table_names
        ]

    return {
        "database": {
            "name": database_name,
            "description": database_description,
        },
        "tables": tables,
    }


def _build_table_entry(
    connection: Connection,
    inspector: Any,
    table_name: str,
    schema_name: str | None,
    table_descriptions: Mapping[str, Any],
    include_examples: bool,
    max_examples: int,
) -> dict[str, Any]:
    """
    Constrói a documentação de uma tabela.
    """

    columns_info = inspector.get_columns(table_name, schema=schema_name)
    pk_columns = set(inspector.get_pk_constraint(table_name, schema=schema_name).get("constrained_columns") or [])
    fk_map = _build_foreign_key_map(inspector.get_foreign_keys(table_name, schema=schema_name))
    table_description = _lookup_table_description(table_name, table_descriptions)
    reflected_table = (
        Table(table_name, MetaData(), schema=schema_name, autoload_with=connection)
        if include_examples
        else None
    )

    return {
        "name": table_name,
        "description": table_description,
        "columns": [
            _build_column_entry(
                connection=connection,
                reflected_table=reflected_table,
                column_info=column_info,
                table_name=table_name,
                pk_columns=pk_columns,
                fk_map=fk_map,
                table_descriptions=table_descriptions,
                include_examples=include_examples,
                max_examples=max_examples,
            )
            for column_info in columns_info
        ],
    }


def _build_column_entry(
    connection: Connection,
    reflected_table: Table | None,
    column_info: Mapping[str, Any],
    table_name: str,
    pk_columns: set[str],
    fk_map: Mapping[str, dict[str, str]],
    table_descriptions: Mapping[str, Any],
    include_examples: bool,
    max_examples: int,
) -> dict[str, Any]:
    """
    Constrói a documentação de uma coluna.
    """

    column_name = str(column_info["name"])
    primary_key = column_name in pk_columns
    nullable = bool(column_info.get("nullable", True))
    foreign_key = column_name in fk_map
    references = fk_map.get(column_name)
    description = _lookup_column_description(table_name, column_name, table_descriptions)
    examples = (
        _collect_examples(connection, reflected_table, column_name, max_examples)
        if include_examples and reflected_table is not None
        else []
    )

    return {
        "name": column_name,
        "description": description,
        "type": _serialize_type(column_info.get("type"), connection),
        "required": primary_key or not nullable,
        "primary_key": primary_key,
        "foreign_key": foreign_key,
        "references": references if foreign_key else None,
        "examples": examples,
    }


def _build_foreign_key_map(foreign_keys: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """
    Normaliza a lista de foreign keys para consulta por coluna.
    """

    fk_map: dict[str, dict[str, str]] = {}
    for foreign_key in foreign_keys:
        constrained_columns = foreign_key.get("constrained_columns") or []
        referred_table = foreign_key.get("referred_table")
        referred_columns = foreign_key.get("referred_columns") or []
        if not constrained_columns or not referred_table or not referred_columns:
            continue
        constrained_column = str(constrained_columns[0])
        fk_map[constrained_column] = {
            "table": str(referred_table),
            "column": str(referred_columns[0]),
        }
    return fk_map


def _collect_examples(
    connection: Connection,
    reflected_table: Table,
    column_name: str,
    max_examples: int,
) -> list[Any]:
    """
    Busca exemplos distintos e não nulos para uma coluna.
    """

    if max_examples <= 0:
        return []
    column = reflected_table.c[column_name]
    statement = (
        select(column)
        .where(column.is_not(None))
        .distinct()
        .order_by(column)
        .limit(max_examples)
    )
    values = connection.execute(statement).scalars().all()
    return [_serialize_example_value(value) for value in values]


def _lookup_table_description(table_name: str, table_descriptions: Mapping[str, Any]) -> str:
    """
    Obtém a descrição manual de uma tabela.
    """

    table_config = _mapping_or_empty(table_descriptions.get(table_name))
    description = _optional_string(table_config.get("description"))
    return description or _DEFAULT_DESCRIPTION


def _lookup_column_description(
    table_name: str,
    column_name: str,
    table_descriptions: Mapping[str, Any],
) -> str:
    """
    Obtém a descrição manual de uma coluna.
    """

    table_config = _mapping_or_empty(table_descriptions.get(table_name))
    columns_config = _mapping_or_empty(table_config.get("columns"))
    column_config = columns_config.get(column_name)
    if isinstance(column_config, str):
        description = _optional_string(column_config)
    elif isinstance(column_config, Mapping):
        description = _optional_string(column_config.get("description"))
    else:
        description = None
    return description or _DEFAULT_DESCRIPTION


def _serialize_type(column_type: Any, connection: Connection) -> str:
    """
    Converte o tipo SQLAlchemy para uma representação textual estável.
    """

    if column_type is None:
        return "unknown"
    try:
        compiled_type = column_type.compile(dialect=connection.dialect)
    except Exception:
        return str(column_type).lower()
    return str(compiled_type).lower()


def _serialize_example_value(value: Any) -> Any:
    """
    Converte valores de banco para tipos serializáveis em YAML.
    """

    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, enum.Enum):
        return _serialize_example_value(value.value)
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _optional_string(value: Any) -> str | None:
    """
    Normaliza valores textuais opcionais.
    """

    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _mapping_or_empty(value: Any) -> Mapping[str, Any]:
    """
    Garante um mapeamento, ou retorna um dicionário vazio.
    """

    if isinstance(value, Mapping):
        return value
    return {}


def _positive_int_or_default(value: Any, default: int) -> int:
    """
    Converte um valor opcional em inteiro positivo.
    """

    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, str):
        try:
            parsed_value = int(value)
        except ValueError:
            return default
        if parsed_value > 0:
            return parsed_value
    return default


def _optional_bool(value: Any, *, default: bool) -> bool:
    """
    Converte um valor opcional em booleano com fallback seguro.
    """

    if isinstance(value, bool):
        return value
    return default


def _fallback_database_name(engine: Engine) -> str:
    """
    Obtém um nome de banco de dados razoável a partir da engine.
    """

    database_name = getattr(engine.url, "database", None)
    return database_name or "database"
