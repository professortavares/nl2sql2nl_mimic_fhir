"""
Definição do schema relacional enxuto para Organization, Location, Patient,
Encounter, EncounterED, EncounterICU, Medication e MedicationMix.
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
class EncounterEDTables:
    """Referência à tabela de EncounterED."""

    encounter_ed: Table


@dataclass(slots=True, frozen=True)
class EncounterICUTables:
    """Referência às tabelas de EncounterICU."""

    encounter_icu: Table
    encounter_icu_location: Table


@dataclass(slots=True, frozen=True)
class MedicationTables:
    """Referência à tabela de Medication."""

    medication: Table


@dataclass(slots=True, frozen=True)
class MedicationMixTables:
    """Referência às tabelas de MedicationMix."""

    medication_mix: Table
    medication_mix_ingredient: Table


@dataclass(slots=True, frozen=True)
class ProjectTables:
    """Agrupa todas as tabelas do pipeline."""

    organization: OrganizationTables
    location: LocationTables
    patient: PatientTables
    encounter: EncounterTables
    encounter_ed: EncounterEDTables
    encounter_icu: EncounterICUTables
    medication: MedicationTables
    medication_mix: MedicationMixTables


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
    encounter_ed_table_name: str,
    encounter_icu_table_name: str,
    encounter_icu_location_table_name: str,
    medication_table_name: str,
    medication_mix_table_name: str,
    medication_mix_ingredient_table_name: str,
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
    encounter_ed_table_name : str
        Nome físico da tabela de EncounterED.
    encounter_icu_table_name : str
        Nome físico da tabela de EncounterICU.
    encounter_icu_location_table_name : str
        Nome físico da tabela auxiliar de EncounterICU/Location.
    medication_table_name : str
        Nome físico da tabela de Medication.
    medication_mix_table_name : str
        Nome físico da tabela principal de MedicationMix.
    medication_mix_ingredient_table_name : str
        Nome físico da tabela auxiliar de ingredientes de MedicationMix.

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
    validate_identifier(encounter_ed_table_name, label="encounter_ed table")
    validate_identifier(encounter_icu_table_name, label="encounter_icu table")
    validate_identifier(encounter_icu_location_table_name, label="encounter_icu_location table")
    validate_identifier(medication_table_name, label="medication table")
    validate_identifier(medication_mix_table_name, label="medication_mix table")
    validate_identifier(
        medication_mix_ingredient_table_name,
        label="medication_mix_ingredient table",
    )

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

    encounter_ed = Table(
        encounter_ed_table_name,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column(
            "encounter_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{encounter_table_name}.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
        Column("admit_source_code", Text(), nullable=True),
        Column("discharge_disposition_code", Text(), nullable=True),
        Column("identifier", Text(), nullable=True),
    )
    Index(f"ix_{encounter_ed_table_name}_encounter_id", encounter_ed.c.encounter_id)
    Index(f"ix_{encounter_ed_table_name}_patient_id", encounter_ed.c.patient_id)
    Index(f"ix_{encounter_ed_table_name}_organization_id", encounter_ed.c.organization_id)

    encounter_icu = Table(
        encounter_icu_table_name,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column(
            "encounter_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{encounter_table_name}.id", ondelete="SET NULL"),
            nullable=True,
        ),
        Column(
            "patient_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{patient_table_name}.id", ondelete="SET NULL"),
            nullable=True,
        ),
        Column("status", String(50), nullable=True),
        Column("class_code", String(50), nullable=True),
        Column("start_date", String(30), nullable=True),
        Column("end_date", String(30), nullable=True),
        Column("identifier", Text(), nullable=True),
    )
    Index(f"ix_{encounter_icu_table_name}_encounter_id", encounter_icu.c.encounter_id)
    Index(f"ix_{encounter_icu_table_name}_patient_id", encounter_icu.c.patient_id)

    encounter_icu_location = Table(
        encounter_icu_location_table_name,
        metadata,
        Column(
            "encounter_icu_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{encounter_icu_table_name}.id", ondelete="CASCADE"),
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
    Index(
        f"ix_{encounter_icu_location_table_name}_encounter_icu_id",
        encounter_icu_location.c.encounter_icu_id,
    )
    Index(
        f"ix_{encounter_icu_location_table_name}_location_id",
        encounter_icu_location.c.location_id,
    )

    medication = Table(
        medication_table_name,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column("code", String(100), nullable=True),
        Column("code_system", Text(), nullable=True),
        Column("status", String(50), nullable=True),
        Column("ndc", Text(), nullable=True),
        Column("formulary_drug_cd", Text(), nullable=True),
        Column("name", Text(), nullable=True),
    )

    medication_mix = Table(
        medication_mix_table_name,
        metadata,
        Column("id", String(_FHIR_ID_MAX_LENGTH), primary_key=True),
        Column("status", String(50), nullable=True),
        Column("identifier", Text(), nullable=True),
    )

    medication_mix_ingredient = Table(
        medication_mix_ingredient_table_name,
        metadata,
        Column(
            "medication_mix_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{medication_mix_table_name}.id", ondelete="CASCADE"),
            nullable=False,
        ),
        Column(
            "medication_id",
            String(_FHIR_ID_MAX_LENGTH),
            ForeignKey(f"{schema_name}.{medication_table_name}.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    Index(
        f"ix_{medication_mix_ingredient_table_name}_medication_mix_id",
        medication_mix_ingredient.c.medication_mix_id,
    )
    Index(
        f"ix_{medication_mix_ingredient_table_name}_medication_id",
        medication_mix_ingredient.c.medication_id,
    )

    return metadata, ProjectTables(
        organization=OrganizationTables(organization=organization),
        location=LocationTables(location=location),
        patient=PatientTables(patient=patient),
        encounter=EncounterTables(
            encounter=encounter,
            encounter_location=encounter_location,
        ),
        encounter_ed=EncounterEDTables(encounter_ed=encounter_ed),
        encounter_icu=EncounterICUTables(
            encounter_icu=encounter_icu,
            encounter_icu_location=encounter_icu_location,
        ),
        medication=MedicationTables(medication=medication),
        medication_mix=MedicationMixTables(
            medication_mix=medication_mix,
            medication_mix_ingredient=medication_mix_ingredient,
        ),
    )
