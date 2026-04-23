"""
Definição do schema relacional para Organization, Location e Patient.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from sqlalchemy import Boolean, Column, ForeignKey, Index, MetaData, String, Table, Text

from src.config.settings import LocationTableNames, OrganizationTableNames, PatientTableNames

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
class PatientTables:
    """Referências das tabelas de Patient."""

    patient: Table
    meta_profile: Table
    name: Table
    identifier: Table
    communication_language_coding: Table
    marital_status_coding: Table
    race: Table
    ethnicity: Table
    birthsex: Table


@dataclass(slots=True, frozen=True)
class ProjectTables:
    """Agrupa todas as tabelas do pipeline."""

    organization: OrganizationTables
    location: LocationTables
    patient: PatientTables


def validate_identifier(identifier: str, *, label: str) -> str:
    """
    Valida identificadores SQL simples.
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
    patient_tables: PatientTableNames,
) -> tuple[MetaData, ProjectTables]:
    """
    Constrói os metadados e as tabelas do schema relacional.
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
    validate_identifier(patient_tables.patient, label="patient table")
    validate_identifier(patient_tables.meta_profile, label="patient_meta_profile table")
    validate_identifier(patient_tables.name, label="patient_name table")
    validate_identifier(patient_tables.identifier, label="patient_identifier table")
    validate_identifier(
        patient_tables.communication_language_coding,
        label="patient_communication_language_coding table",
    )
    validate_identifier(
        patient_tables.marital_status_coding,
        label="patient_marital_status_coding table",
    )
    validate_identifier(patient_tables.race, label="patient_race table")
    validate_identifier(patient_tables.ethnicity, label="patient_ethnicity table")
    validate_identifier(patient_tables.birthsex, label="patient_birthsex table")

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

    patient = Table(
        patient_tables.patient,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column("resource_type", String(50), nullable=False),
        Column("gender", String(20), nullable=True),
        Column("birth_date", String(20), nullable=True),
        Column(
            "managing_organization_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{organization_tables.organization}.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )
    Index(
        f"ix_{patient_tables.patient}_managing_organization_id",
        patient.c.managing_organization_id,
    )

    patient_meta_profile = Table(
        patient_tables.meta_profile,
        metadata,
        Column(
            "patient_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{patient_tables.patient}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("profile", Text(), nullable=False),
    )
    Index(
        f"ix_{patient_tables.meta_profile}_patient_id",
        patient_meta_profile.c.patient_id,
    )

    patient_name = Table(
        patient_tables.name,
        metadata,
        Column(
            "patient_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{patient_tables.patient}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("use", Text(), nullable=True),
        Column("family", Text(), nullable=True),
    )
    Index(
        f"ix_{patient_tables.name}_patient_id",
        patient_name.c.patient_id,
    )

    patient_identifier = Table(
        patient_tables.identifier,
        metadata,
        Column(
            "patient_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{patient_tables.patient}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("system", Text(), nullable=True),
        Column("value", Text(), nullable=True),
    )
    Index(
        f"ix_{patient_tables.identifier}_patient_id",
        patient_identifier.c.patient_id,
    )

    patient_communication_language_coding = Table(
        patient_tables.communication_language_coding,
        metadata,
        Column(
            "patient_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{patient_tables.patient}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("system", Text(), nullable=True),
        Column("code", Text(), nullable=True),
    )
    Index(
        f"ix_{patient_tables.communication_language_coding}_patient_id",
        patient_communication_language_coding.c.patient_id,
    )

    patient_marital_status_coding = Table(
        patient_tables.marital_status_coding,
        metadata,
        Column(
            "patient_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{patient_tables.patient}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("system", Text(), nullable=True),
        Column("code", Text(), nullable=True),
    )
    Index(
        f"ix_{patient_tables.marital_status_coding}_patient_id",
        patient_marital_status_coding.c.patient_id,
    )

    patient_race = Table(
        patient_tables.race,
        metadata,
        Column(
            "patient_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{patient_tables.patient}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("omb_category_system", Text(), nullable=True),
        Column("omb_category_code", Text(), nullable=True),
        Column("omb_category_display", Text(), nullable=True),
        Column("text", Text(), nullable=True),
    )
    Index(f"ix_{patient_tables.race}_patient_id", patient_race.c.patient_id)

    patient_ethnicity = Table(
        patient_tables.ethnicity,
        metadata,
        Column(
            "patient_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{patient_tables.patient}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("omb_category_system", Text(), nullable=True),
        Column("omb_category_code", Text(), nullable=True),
        Column("omb_category_display", Text(), nullable=True),
        Column("text", Text(), nullable=True),
    )
    Index(
        f"ix_{patient_tables.ethnicity}_patient_id",
        patient_ethnicity.c.patient_id,
    )

    patient_birthsex = Table(
        patient_tables.birthsex,
        metadata,
        Column(
            "patient_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{patient_tables.patient}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column("value_code", Text(), nullable=True),
    )
    Index(
        f"ix_{patient_tables.birthsex}_patient_id",
        patient_birthsex.c.patient_id,
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
        patient=PatientTables(
            patient=patient,
            meta_profile=patient_meta_profile,
            name=patient_name,
            identifier=patient_identifier,
            communication_language_coding=patient_communication_language_coding,
            marital_status_coding=patient_marital_status_coding,
            race=patient_race,
            ethnicity=patient_ethnicity,
            birthsex=patient_birthsex,
        ),
    )

