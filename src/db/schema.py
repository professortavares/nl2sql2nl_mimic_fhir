"""
Definição do schema relacional para Organization e Location.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from sqlalchemy import Boolean, Column, ForeignKey, Index, MetaData, String, Table, Text

from src.config.settings import LocationTableNames, OrganizationTableNames

_FHIR_ID_MAX_LENGTH: Final[int] = 64


@dataclass(slots=True, frozen=True)
class OrganizationTables:
    """Referências das tabelas de Organization."""

    organization: Table
    meta_profile: Table
    identifier: Table
    type_coding: Table


@dataclass(slots=True, frozen=True)
class LocationTables:
    """Referências das tabelas de Location."""

    location: Table
    meta_profile: Table
    physical_type_coding: Table


@dataclass(slots=True, frozen=True)
class ProjectTables:
    """Agrupa todas as tabelas do pipeline."""

    organization: OrganizationTables
    location: LocationTables


def validate_identifier(identifier: str, *, label: str) -> str:
    """
    Valida identificadores SQL simples.

    Parâmetros:
    ----------
    identifier : str
        Nome a ser validado.
    label : str
        Rótulo usado na mensagem de erro.

    Retorno:
    -------
    str
        Identificador validado.
    """

    if not identifier:
        raise ValueError(f"{label} inválido: {identifier!r}")
    first_character = identifier[0]
    if not (first_character.isalpha() or first_character == "_"):
        raise ValueError(f"{label} inválido: {identifier!r}")
    for character in identifier:
        if not (character.isalnum() or character == "_"):
            raise ValueError(f"{label} inválido: {identifier!r}")
    return identifier


def build_project_metadata(
    schema_name: str,
    organization_tables: OrganizationTableNames,
    location_tables: LocationTableNames,
) -> tuple[MetaData, ProjectTables]:
    """
    Constrói os metadados e as tabelas do schema relacional.

    Parâmetros:
    ----------
    schema_name : str
        Nome do schema PostgreSQL.
    organization_tables : OrganizationTableNames
        Nomes físicos de Organization.
    location_tables : LocationTableNames
        Nomes físicos de Location.

    Retorno:
    -------
    tuple[MetaData, ProjectTables]
        Metadados e referências das tabelas.
    """

    validate_identifier(schema_name, label="schema_name")
    validate_identifier(organization_tables.organization, label="organization table")
    validate_identifier(organization_tables.meta_profile, label="organization_meta_profile table")
    validate_identifier(organization_tables.identifier, label="organization_identifier table")
    validate_identifier(organization_tables.type_coding, label="organization_type_coding table")
    validate_identifier(location_tables.location, label="location table")
    validate_identifier(location_tables.meta_profile, label="location_meta_profile table")
    validate_identifier(
        location_tables.physical_type_coding,
        label="location_physical_type_coding table",
    )

    metadata = MetaData(schema=schema_name)

    organization = Table(
        organization_tables.organization,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column("resource_type", String(50), nullable=False),
        Column("active", Boolean(), nullable=True),
        Column("name", Text(), nullable=True),
    )

    organization_meta_profile = Table(
        organization_tables.meta_profile,
        metadata,
        Column(
            "organization_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{organization_tables.organization}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("profile", Text(), nullable=False),
    )
    Index(
        f"ix_{organization_tables.meta_profile}_organization_id",
        organization_meta_profile.c.organization_id,
    )

    organization_identifier = Table(
        organization_tables.identifier,
        metadata,
        Column(
            "organization_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{organization_tables.organization}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("system", Text(), nullable=True),
        Column("value", Text(), nullable=True),
    )
    Index(
        f"ix_{organization_tables.identifier}_organization_id",
        organization_identifier.c.organization_id,
    )

    organization_type_coding = Table(
        organization_tables.type_coding,
        metadata,
        Column(
            "organization_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{organization_tables.organization}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("system", Text(), nullable=True),
        Column("code", Text(), nullable=True),
        Column("display", Text(), nullable=True),
    )
    Index(
        f"ix_{organization_tables.type_coding}_organization_id",
        organization_type_coding.c.organization_id,
    )

    location = Table(
        location_tables.location,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column("resource_type", String(50), nullable=False),
        Column("name", Text(), nullable=True),
        Column("status", String(50), nullable=True),
        Column(
            "managing_organization_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{organization_tables.organization}.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )
    Index(
        f"ix_{location_tables.location}_managing_organization_id",
        location.c.managing_organization_id,
    )

    location_meta_profile = Table(
        location_tables.meta_profile,
        metadata,
        Column(
            "location_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{location_tables.location}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("profile", Text(), nullable=False),
    )
    Index(
        f"ix_{location_tables.meta_profile}_location_id",
        location_meta_profile.c.location_id,
    )

    location_physical_type_coding = Table(
        location_tables.physical_type_coding,
        metadata,
        Column(
            "location_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{location_tables.location}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("system", Text(), nullable=True),
        Column("code", Text(), nullable=True),
        Column("display", Text(), nullable=True),
    )
    Index(
        f"ix_{location_tables.physical_type_coding}_location_id",
        location_physical_type_coding.c.location_id,
    )

    return metadata, ProjectTables(
        organization=OrganizationTables(
            organization=organization,
            meta_profile=organization_meta_profile,
            identifier=organization_identifier,
            type_coding=organization_type_coding,
        ),
        location=LocationTables(
            location=location,
            meta_profile=location_meta_profile,
            physical_type_coding=location_physical_type_coding,
        ),
    )

