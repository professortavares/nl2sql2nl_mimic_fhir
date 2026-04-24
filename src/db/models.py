"""
Modelos e contratos tipados de tabelas do schema de ingestão.
"""

from __future__ import annotations

from src.db.schema import (
    ConditionEDTables,
    ConditionTables,
    EncounterEDTables,
    EncounterICUTables,
    EncounterTables,
    MedicationTables,
    MedicationMixTables,
    MedicationRequestTables,
    LocationTables,
    OrganizationTables,
    PatientTables,
    ProjectTables,
    ProcedureTables,
    ProcedureEDTables,
    ProcedureICUTables,
    SpecimenTables,
)

__all__ = [
    "LocationTables",
    "EncounterTables",
    "EncounterEDTables",
    "EncounterICUTables",
    "MedicationTables",
    "MedicationMixTables",
    "MedicationRequestTables",
    "OrganizationTables",
    "PatientTables",
    "SpecimenTables",
    "ConditionTables",
    "ConditionEDTables",
    "ProcedureTables",
    "ProcedureEDTables",
    "ProcedureICUTables",
    "ProjectTables",
]
