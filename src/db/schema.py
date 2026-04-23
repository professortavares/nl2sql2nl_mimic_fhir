"""
Definição e recriação do schema relacional para Organization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from sqlalchemy import Boolean, Column, ForeignKey, Index, MetaData, String, Table, Text
from sqlalchemy.engine import Connection
from sqlalchemy.schema import CreateSchema, DropSchema

from src.config.settings import TableNames

_ORGANIZATION_ID_MAX_LENGTH: Final[int] = 64


@dataclass(slots=True, frozen=True)
class OrganizationTables:
    """Referências fortemente tipadas para as tabelas do schema."""

    organization: Table
    organization_meta_profile: Table
    organization_identifier: Table
    organization_type_coding: Table


def validate_identifier(identifier: str, *, label: str) -> str:
    """
    Valida um identificador SQL simples e seguro.

    Parâmetros:
    ----------
    identifier : str
        Nome do schema ou tabela.
    label : str
        Nome amigável para erro.

    Retorno:
    -------
    str
        Identificador validado.
    """

    if not identifier or not (identifier[0].isalpha() or identifier[0] == "_"):
        raise ValueError(f"{label} inválido: {identifier!r}")
    for character in identifier:
        if not (character.isalnum() or character == "_"):
            raise ValueError(f"{label} inválido: {identifier!r}")
    return identifier


def build_organization_metadata(schema_name: str, table_names: TableNames) -> tuple[MetaData, OrganizationTables]:
    """
    Constrói a metadados e as tabelas do schema de Organization.

    Parâmetros:
    ----------
    schema_name : str
        Schema PostgreSQL onde as tabelas serão criadas.
    table_names : TableNames
        Nomes físicos configurados em YAML.

    Retorno:
    -------
    tuple[MetaData, OrganizationTables]
        Metadados e referências das tabelas.
    """

    validate_identifier(schema_name, label="schema_name")
    validate_identifier(table_names.organization, label="organization table")
    validate_identifier(table_names.organization_meta_profile, label="organization_meta_profile table")
    validate_identifier(table_names.organization_identifier, label="organization_identifier table")
    validate_identifier(table_names.organization_type_coding, label="organization_type_coding table")

    metadata = MetaData(schema=schema_name)

    organization = Table(
        table_names.organization,
        metadata,
        Column("id", String(_ORGANIZATION_ID_MAX_LENGTH), primary_key=True),
        Column("resource_type", String(50), nullable=False),
        Column("active", Boolean(), nullable=True),
        Column("name", Text(), nullable=True),
    )

    organization_meta_profile = Table(
        table_names.organization_meta_profile,
        metadata,
        Column(
            "organization_id",
            String(_ORGANIZATION_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{table_names.organization}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("profile", Text(), nullable=False),
    )
    Index(
        f"ix_{table_names.organization_meta_profile}_organization_id",
        organization_meta_profile.c.organization_id,
    )

    organization_identifier = Table(
        table_names.organization_identifier,
        metadata,
        Column(
            "organization_id",
            String(_ORGANIZATION_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{table_names.organization}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("system", Text(), nullable=True),
        Column("value", Text(), nullable=True),
    )
    Index(
        f"ix_{table_names.organization_identifier}_organization_id",
        organization_identifier.c.organization_id,
    )

    organization_type_coding = Table(
        table_names.organization_type_coding,
        metadata,
        Column(
            "organization_id",
            String(_ORGANIZATION_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{table_names.organization}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("system", Text(), nullable=True),
        Column("code", Text(), nullable=True),
        Column("display", Text(), nullable=True),
    )
    Index(
        f"ix_{table_names.organization_type_coding}_organization_id",
        organization_type_coding.c.organization_id,
    )

    return metadata, OrganizationTables(
        organization=organization,
        organization_meta_profile=organization_meta_profile,
        organization_identifier=organization_identifier,
        organization_type_coding=organization_type_coding,
    )


def reset_schema(connection: Connection, schema_name: str) -> None:
    """
    Remove e recria o schema alvo de forma explícita.

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
