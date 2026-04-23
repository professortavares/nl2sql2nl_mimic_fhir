"""
Modelos e contratos tipados de tabelas do schema de ingestão.
"""

from __future__ import annotations

from src.db.schema import (
    EncounterEDTables,
    EncounterTables,
    LocationTables,
    OrganizationTables,
    PatientTables,
    ProjectTables,
)

__all__ = [
    "LocationTables",
    "EncounterTables",
    "EncounterEDTables",
    "OrganizationTables",
    "PatientTables",
    "ProjectTables",
]
