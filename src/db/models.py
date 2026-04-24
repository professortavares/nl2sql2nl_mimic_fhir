"""
Modelos e contratos tipados de tabelas do schema de ingestão.
"""

from __future__ import annotations

from src.db.schema import (
    EncounterEDTables,
    EncounterICUTables,
    EncounterTables,
    MedicationTables,
    LocationTables,
    OrganizationTables,
    PatientTables,
    ProjectTables,
)

__all__ = [
    "LocationTables",
    "EncounterTables",
    "EncounterEDTables",
    "EncounterICUTables",
    "MedicationTables",
    "OrganizationTables",
    "PatientTables",
    "ProjectTables",
]
