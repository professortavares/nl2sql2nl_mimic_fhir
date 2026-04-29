"""
Resolve tabelas de referência usadas na ingestão.
"""

from __future__ import annotations

from dataclasses import is_dataclass
from typing import Final

from sqlalchemy import Table

from src.db.schema import ProjectTables

_DEFAULT_REFERENCE_TABLES: Final[dict[str, str]] = {
    "encounter_id": "encounter",
    "procedure_id": "procedure",
}

_REFERENCE_TABLE_OVERRIDES: Final[dict[str, dict[str, str]]] = {
    "condition_ed": {"encounter_id": "encounter_ed"},
    "medication_dispense_ed": {"encounter_id": "encounter_ed"},
    "medication_statement_ed": {"encounter_id": "encounter_ed"},
    "procedure_ed": {"encounter_id": "encounter_ed"},
    "observation_ed": {
        "encounter_id": "encounter_ed",
        "procedure_id": "procedure_ed",
    },
    "observation_vital_signs_ed": {
        "encounter_id": "encounter_ed",
        "procedure_id": "procedure_ed",
    },
    "procedure_icu": {"encounter_id": "encounter_icu"},
    "medication_administration_icu": {"encounter_id": "encounter_icu"},
}


def resolve_reference_table_name(primary_table_name: str, reference_column: str) -> str | None:
    """
    Retorna o nome da tabela que deve ser usada para validar uma FK.
    """

    override = _REFERENCE_TABLE_OVERRIDES.get(primary_table_name, {}).get(reference_column)
    if override is not None:
        return override
    return _DEFAULT_REFERENCE_TABLES.get(reference_column)


def resolve_reference_table(
    tables: ProjectTables,
    *,
    primary_table_name: str,
    reference_column: str,
) -> Table:
    """
    Retorna a tabela SQLAlchemy correta para validar a referência informada.
    """

    reference_table_name = resolve_reference_table_name(primary_table_name, reference_column)
    if reference_table_name is None:
        raise KeyError(
            f"Não foi possível resolver a tabela de referência para {primary_table_name}.{reference_column}"
        )

    table_group = getattr(tables, reference_table_name)
    reference_table = getattr(table_group, reference_table_name)
    if not isinstance(reference_table, Table):
        raise TypeError(
            f"O atributo {reference_table_name}.{reference_table_name} não é uma tabela SQLAlchemy válida."
        )
    return reference_table


def extract_table(table_or_group: object, table_name: str) -> Table:
    """
    Normaliza um objeto de tabela ou grupo de tabelas para um `Table` SQLAlchemy.
    """

    if isinstance(table_or_group, Table):
        return table_or_group

    if not is_dataclass(table_or_group):
        raise TypeError(f"Objeto de tabela inválido para {table_name}.")

    table = getattr(table_or_group, table_name)
    if not isinstance(table, Table):
        raise TypeError(f"O atributo {table_name} não é uma tabela SQLAlchemy válida.")
    return table
