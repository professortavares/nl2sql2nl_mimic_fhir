"""
Modelos e contratos tipados de tabelas do schema de ingestão.
"""

from __future__ import annotations

from src.db.schema import (
    EncounterTables,
    LocationTables,
    OrganizationTables,
    PatientTables,
    ProjectTables,
)

__all__ = [
    "LocationTables",
    "EncounterTables",
    "OrganizationTables",
    "PatientTables",
    "ProjectTables",
]
