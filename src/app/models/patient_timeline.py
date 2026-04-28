"""
Modelos de dados para a timeline clínica de um paciente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class PatientProfile:
    """Resumo identificador do paciente."""

    id: str
    name: str | None
    gender: str | None
    birth_date: str | None
    identifier: str | None
    race: str | None
    ethnicity: str | None
    birthsex: str | None
    managing_organization_id: str | None
    managing_organization_name: str | None


@dataclass(slots=True, frozen=True)
class EncounterSummary:
    """Resumo de um encounter clínico."""

    id: str
    status: str | None
    class_code: str | None
    start_date: str | None
    end_date: str | None
    organization_id: str | None
    organization_name: str | None
    admit_source_code: str | None
    discharge_disposition_code: str | None
    service_type_code: str | None
    priority_code: str | None


@dataclass(slots=True)
class EncounterTimeline:
    """Agrupa os eventos clínicos associados a um encounter."""

    summary: EncounterSummary
    general_hospital: dict[str, Any] = field(default_factory=dict)
    emergency_department: dict[str, Any] = field(default_factory=dict)
    icu: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PatientTimeline:
    """Timeline completa de um paciente."""

    patient: PatientProfile
    encounters: list[EncounterTimeline] = field(default_factory=list)
