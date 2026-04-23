"""
Definição do schema relacional enxuto para Organization, Location e Patient.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from sqlalchemy import Column, ForeignKey, Index, MetaData, String, Table, Text

_FHIR_ID_MAX_LENGTH: Final[int] = 64


@dataclass(slots=True, frozen=True)
class OrganizationTables:
    """Referência às tabelas de Organization."""

    organization: Table


@dataclass(slots=True, frozen=True)
class LocationTables:
    """Referência às tabelas de Location."""

    location: Table


@dataclass(slots=True, frozen=True)
class PatientTables:
    """Referência às tabelas de Patient."""

    patient: Table


@dataclass(slots=True, frozen=True)
class EncounterTables:
    """Referência às tabelas de Encounter."""

    encounter: Table
    encounter_location: Table


@dataclass(slots=True, frozen=True)
class ProjectTables:
    """Agrupa todas as tabelas do pipeline."""

    organization: OrganizationTables
    location: LocationTables
    patient: PatientTables
    encounter: EncounterTables


def validate_identifier(identifier: str, *, label: str) -> str:
    """
    Valida identificadores SQL simples.

    Parâmetros:
    ----------
    identifier : str
        Nome a ser validado.
    label : str
        Rótulo usado nas mensagens de erro.

    Retorno:
    -------
    str
        O próprio identificador quando válido.

    Exceções:
    --------
    ValueError
        Quando o identificador não segue o padrão esperado.
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
    organization_table_name: str,
    location_table_name: str,
    patient_table_name: str,
    encounter_table_name: str,
    encounter_location_table_name: str,
) -> tuple[MetaData, ProjectTables]:
    """
    Constrói os metadados e as tabelas do schema relacional simplificado.

    Parâmetros:
    ----------
    schema_name : str
        Nome do schema PostgreSQL.
    organization_table_name : str
        Nome físico da tabela de Organization.
    location_table_name : str
        Nome físico da tabela de Location.
    patient_table_name : str
        Nome físico da tabela de Patient.
    encounter_table_name : str
        Nome físico da tabela de Encounter.
    encounter_location_table_name : str
        Nome físico da tabela auxiliar de Encounter/Location.

    Retorno:
    -------
    tuple[MetaData, ProjectTables]
        Metadados SQLAlchemy e referências tipadas para as tabelas criadas.
    """

    validate_identifier(schema_name, label="schema_name")
    validate_identifier(organization_table_name, label="organization table")
    validate_identifier(location_table_name, label="location table")
    validate_identifier(patient_table_name, label="patient table")
    validate_identifier(encounter_table_name, label="encounter table")
    validate_identifier(encounter_location_table_name, label="encounter_location table")

    metadata = MetaData(schema=schema_name)

    organization = Table(
        organization_table_name,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column("name", Text(), nullable=True),
    )

    location = Table(
        location_table_name,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column("name", Text(), nullable=True),
        Column(
            "managing_organization_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{organization_table_name}.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    Index(
        f"ix_{location_table_name}_managing_organization_id",
        location.c.managing_organization_id,
    )

    patient = Table(
        patient_table_name,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column("gender", String(20), nullable=True),
        Column("birth_date", String(20), nullable=True),
        Column("name", Text(), nullable=True),
        Column("identifier", Text(), nullable=True),
        Column("marital_status_coding", Text(), nullable=True),
        Column("race", Text(), nullable=True),
        Column("ethnicity", Text(), nullable=True),
        Column("birthsex", Text(), nullable=True),
        Column(
            "managing_organization_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{organization_table_name}.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    Index(
        f"ix_{patient_table_name}_managing_organization_id",
        patient.c.managing_organization_id,
    )

    encounter = Table(
        encounter_table_name,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column(
            "patient_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{patient_table_name}.id", ondelete="SET NULL"),
            nullable=True,
        ),
        Column(
            "organization_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{organization_table_name}.id", ondelete="SET NULL"),
            nullable=True,
        ),
        Column("status", String(50), nullable=True),
        Column("class_code", String(50), nullable=True),
        Column("start_date", String(30), nullable=True),
        Column("end_date", String(30), nullable=True),
        Column("priority_code", String(50), nullable=True),
        Column("service_type_code", String(50), nullable=True),
        Column("admit_source_code", Text(), nullable=True),
        Column("discharge_disposition_code", Text(), nullable=True),
        Column("identifier", Text(), nullable=True),
    )
    Index(f"ix_{encounter_table_name}_patient_id", encounter.c.patient_id)
    Index(f"ix_{encounter_table_name}_organization_id", encounter.c.organization_id)

    encounter_location = Table(
        encounter_location_table_name,
        metadata,
        Column(
            "encounter_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{encounter_table_name}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column(
            "location_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{location_table_name}.id", ondelete="SET NULL"),
            nullable=True,
        ),
        Column("start_date", String(30), nullable=True),
        Column("end_date", String(30), nullable=True),
    )
    Index(f"ix_{encounter_location_table_name}_encounter_id", encounter_location.c.encounter_id)
    Index(f"ix_{encounter_location_table_name}_location_id", encounter_location.c.location_id)

    return metadata, ProjectTables(
        organization=OrganizationTables(organization=organization),
        location=LocationTables(location=location),
        patient=PatientTables(patient=patient),
        encounter=EncounterTables(
            encounter=encounter,
            encounter_location=encounter_location,
        ),
    )
