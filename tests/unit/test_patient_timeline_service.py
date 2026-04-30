"""
Testes do serviço de timeline clínica individual.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from unittest.mock import Mock

import pytest

from src.app.services.patient_timeline_service import (
    PatientNotFoundError,
    PatientTimelineService,
    TimelineRepositories,
)


@dataclass(slots=True)
class FakePatientRepository:
    """Repositório fake de pacientes."""

    patient: dict[str, object] | None

    def fetch_patient(self, connection, patient_id: str) -> dict[str, object] | None:
        return self.patient


@dataclass(slots=True)
class FakeEncounterRepository:
    """Repositório fake de encounters."""

    encounters: list[dict[str, object]]

    def list_by_patient_id(self, connection, patient_id: str) -> list[dict[str, object]]:
        return list(self.encounters)


@dataclass(slots=True)
class FakeGeneralHospitalRepository:
    """Repositório fake do contexto General Hospital."""

    encounter_locations: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    conditions: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    procedures: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    medication_requests: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    medication_dispenses: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    medication_administrations: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    medication_events: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    labevents: list[dict[str, object]] = field(default_factory=list)
    micro_tests: list[dict[str, object]] = field(default_factory=list)
    micro_orgs: list[dict[str, object]] = field(default_factory=list)
    micro_suscs: list[dict[str, object]] = field(default_factory=list)
    specimens: list[dict[str, object]] = field(default_factory=list)

    def list_encounter_locations(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.encounter_locations.get(encounter_id, []))

    def list_conditions(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.conditions.get(encounter_id, []))

    def list_procedures(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.procedures.get(encounter_id, []))

    def list_medication_requests(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.medication_requests.get(encounter_id, []))

    def list_medication_dispenses(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.medication_dispenses.get(encounter_id, []))

    def list_medication_administrations(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.medication_administrations.get(encounter_id, []))

    def list_medication_events(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.medication_events.get(encounter_id, []))

    def list_labevents(self, connection, patient_id: str) -> list[dict[str, object]]:
        return list(self.labevents)

    def list_micro_tests(self, connection, patient_id: str, encounter_id: str) -> list[dict[str, object]]:
        return list(self.micro_tests)

    def list_micro_orgs(self, connection, test_ids: list[str]) -> list[dict[str, object]]:
        return list(self.micro_orgs)

    def list_micro_suscs(self, connection, org_ids: list[str]) -> list[dict[str, object]]:
        return list(self.micro_suscs)

    def list_specimens(self, connection, patient_id: str) -> list[dict[str, object]]:
        return list(self.specimens)


@dataclass(slots=True)
class FakeEmergencyDepartmentRepository:
    """Repositório fake do contexto Emergency Department."""

    encounter_ed: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    conditions: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    procedures: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    observations: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    vital_signs: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    vital_sign_components: list[dict[str, object]] = field(default_factory=list)
    medication_dispenses: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    medication_statements: dict[str, list[dict[str, object]]] = field(default_factory=dict)

    def list_encounter_ed(self, connection, patient_id: str, encounter_id: str) -> list[dict[str, object]]:
        return list(self.encounter_ed.get(encounter_id, []))

    def list_conditions(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.conditions.get(encounter_id, []))

    def list_procedures(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.procedures.get(encounter_id, []))

    def list_observations(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.observations.get(encounter_id, []))

    def list_vital_signs(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.vital_signs.get(encounter_id, []))

    def list_vital_sign_components(self, connection, observation_ids: list[str]) -> list[dict[str, object]]:
        return list(self.vital_sign_components)

    def list_medication_dispenses(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.medication_dispenses.get(encounter_id, []))

    def list_medication_statements(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.medication_statements.get(encounter_id, []))


@dataclass(slots=True)
class FakeIcuRepository:
    """Repositório fake do contexto ICU."""

    encounter_icu: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    procedures: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    medication_administrations: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    charted_events: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    datetime_events: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    output_events: dict[str, list[dict[str, object]]] = field(default_factory=dict)

    def list_encounter_icu(self, connection, patient_id: str, encounter_id: str) -> list[dict[str, object]]:
        return list(self.encounter_icu.get(encounter_id, []))

    def list_procedures(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.procedures.get(encounter_id, []))

    def list_medication_administrations(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.medication_administrations.get(encounter_id, []))

    def list_charted_events(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.charted_events.get(encounter_id, []))

    def list_datetime_events(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.datetime_events.get(encounter_id, []))

    def list_output_events(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.output_events.get(encounter_id, []))


def _build_service(
    *,
    patient: dict[str, object] | None,
    encounters: list[dict[str, object]],
    general_hospital: FakeGeneralHospitalRepository | None = None,
    emergency_department: FakeEmergencyDepartmentRepository | None = None,
    icu: FakeIcuRepository | None = None,
) -> PatientTimelineService:
    """Monta um serviço com repositórios fake."""

    repositories = TimelineRepositories(
        patient_repository=FakePatientRepository(patient=patient),
        encounter_repository=FakeEncounterRepository(encounters=encounters),
        general_hospital_repository=general_hospital or FakeGeneralHospitalRepository(),
        emergency_department_repository=emergency_department or FakeEmergencyDepartmentRepository(),
        icu_repository=icu or FakeIcuRepository(),
    )
    return PatientTimelineService(repositories)


def test_build_timeline_raises_for_missing_patient() -> None:
    """Deve falhar quando o paciente não existe."""

    service = _build_service(patient=None, encounters=[])

    with pytest.raises(PatientNotFoundError):
        service.build_timeline(Mock(), "pat-missing")


def test_build_timeline_returns_patient_with_no_encounters() -> None:
    """Deve retornar o paciente mesmo sem encounters."""

    service = _build_service(
        patient={"id": "pat-1", "name": "Jane Doe", "managing_organization_name": "Hospital A"},
        encounters=[],
    )

    timeline = service.build_timeline(Mock(), "pat-1")

    assert timeline.patient.id == "pat-1"
    assert timeline.patient.name == "Jane Doe"
    assert timeline.encounters == []


def test_build_timeline_sorts_encounters_chronologically() -> None:
    """Deve ordenar encounters por início, fim e id."""

    service = _build_service(
        patient={"id": "pat-1"},
        encounters=[
            {"id": "enc-3", "start_date": "2024-01-02", "end_date": "2024-01-02"},
            {"id": "enc-1", "start_date": "2024-01-01", "end_date": "2024-01-01"},
            {"id": "enc-2", "start_date": "2024-01-01", "end_date": "2024-01-03"},
        ],
    )

    timeline = service.build_timeline(Mock(), "pat-1")

    assert [encounter.summary.id for encounter in timeline.encounters] == ["enc-1", "enc-2", "enc-3"]


def test_build_timeline_builds_general_ed_and_icu_contexts() -> None:
    """Deve montar os três contextos clínicos com dados estruturados."""

    general_hospital = FakeGeneralHospitalRepository(
        encounter_locations={
            "enc-1": [
                {"start_date": "2024-01-01T00:00:00", "end_date": "2024-01-01T12:00:00", "location_name": "ED"},
                {"start_date": "2024-01-01T12:00:00", "end_date": None, "location_name": "Ward A"},
            ]
        },
        conditions={"enc-1": [{"id": "cond-1"}]},
        procedures={"enc-1": [{"id": "proc-1"}]},
        medication_requests={"enc-1": [{"id": "mr-1"}]},
        medication_dispenses={"enc-1": [{"id": "md-1"}]},
        medication_administrations={"enc-1": [{"id": "ma-1"}]},
        medication_events={
            "enc-1": [
                {
                    "medication_request_id": "mr-1",
                    "validity_start": "2024-01-01T08:00:00",
                    "validity_end": "2024-01-01T20:00:00",
                    "medication_name": "Morphine",
                    "frequency_code": "ONCE",
                    "request_status": "completed",
                    "request_intent": "order",
                    "request_identifier": "req-1",
                    "medication_administration_id": "ma-1",
                    "effective_at": "2024-01-01T10:00:00",
                    "dose_value": "2",
                    "dose_unit": "mg",
                    "status": "completed",
                }
            ]
        },
        labevents=[{"id": "lab-1", "effective_at": "2024-01-02T10:00:00"}],
        micro_tests=[{"id": "mt-1", "effective_at": "2024-01-02T11:00:00"}],
        micro_orgs=[{"id": "mo-1", "derived_from_observation_micro_test_id": "mt-1"}],
        micro_suscs=[{"id": "ms-1", "derived_from_observation_micro_org_id": "mo-1"}],
        specimens=[{"id": "spec-1", "collected_at": "2024-01-02T08:00:00"}],
    )
    emergency_department = FakeEmergencyDepartmentRepository(
        encounter_ed={"enc-1": [{"id": "enc-ed-1", "encounter_id": "enc-1"}]},
        conditions={"enc-1": [{"id": "cond-ed-1"}]},
        procedures={"enc-1": [{"id": "proc-ed-1"}]},
        observations={"enc-1": [{"id": "obs-ed-1"}]},
        vital_signs={"enc-1": [{"id": "vital-1"}]},
        vital_sign_components=[{"id": "comp-1", "observation_vital_signs_ed_id": "vital-1"}],
        medication_dispenses={"enc-1": [{"id": "mded-1"}]},
        medication_statements={"enc-1": [{"id": "msed-1"}]},
    )
    icu = FakeIcuRepository(
        encounter_icu={"enc-1": [{"id": "enc-icu-1", "encounter_id": "enc-1"}]},
        procedures={"enc-1": [{"id": "proc-icu-1"}]},
        medication_administrations={"enc-1": [{"id": "mai-1"}]},
        charted_events={"enc-1": [{"id": "chart-1"}]},
        datetime_events={"enc-1": [{"id": "dt-1"}]},
        output_events={"enc-1": [{"id": "out-1"}]},
    )
    service = _build_service(
        patient={"id": "pat-1", "name": "Jane Doe"},
        encounters=[{"id": "enc-1", "start_date": "2024-01-01", "end_date": "2024-01-03"}],
        general_hospital=general_hospital,
        emergency_department=emergency_department,
        icu=icu,
    )

    timeline = service.build_timeline(Mock(), "pat-1")
    encounter = timeline.encounters[0]

    assert encounter.general_hospital["hospitalization"]["id"] == "enc-1"
    assert encounter.general_hospital["hospital_transfers"] == [
        {"start_date": "2024-01-01T00:00:00", "end_date": "2024-01-01T12:00:00", "location_name": "ED"},
        {"start_date": "2024-01-01T12:00:00", "end_date": None, "location_name": "Ward A"},
    ]
    assert encounter.general_hospital["diagnoses"] == [{"id": "cond-1"}]
    assert encounter.general_hospital["procedures"] == [{"id": "proc-1"}]
    assert encounter.general_hospital["medications"]["pedidos_de_medicacao"] == [{"id": "mr-1"}]
    assert encounter.general_hospital["medications"]["dispensacoes"] == [{"id": "md-1"}]
    assert encounter.general_hospital["medications"]["administracoes"] == [{"id": "ma-1"}]
    assert encounter.general_hospital["medication_events"] == [
        {
            "medication_request_id": "mr-1",
            "validity_start": "2024-01-01T08:00:00",
            "validity_end": "2024-01-01T20:00:00",
            "medication_name": "Morphine",
            "frequency_code": "ONCE",
            "request_status": "completed",
            "request_intent": "order",
            "request_identifier": "req-1",
            "medication_administration_id": "ma-1",
            "effective_at": "2024-01-01T10:00:00",
            "dose_value": "2",
            "dose_unit": "mg",
            "status": "completed",
        }
    ]
    assert encounter.general_hospital["labs"] == [{"id": "lab-1", "effective_at": "2024-01-02T10:00:00"}]
    assert encounter.general_hospital["microbiology"]["testes"] == [
        {"id": "mt-1", "effective_at": "2024-01-02T11:00:00"}
    ]
    assert encounter.general_hospital["microbiology"]["organismos"] == [
        {"id": "mo-1", "derived_from_observation_micro_test_id": "mt-1"}
    ]
    assert encounter.general_hospital["microbiology"]["susceptibilidades"] == [
        {"id": "ms-1", "derived_from_observation_micro_org_id": "mo-1"}
    ]
    assert encounter.general_hospital["specimens"] == [{"id": "spec-1", "collected_at": "2024-01-02T08:00:00"}]

    assert encounter.emergency_department["stay"] == {"id": "enc-ed-1", "encounter_id": "enc-1"}
    assert encounter.emergency_department["diagnoses"] == [{"id": "cond-ed-1"}]
    assert encounter.emergency_department["procedures"] == [{"id": "proc-ed-1"}]
    assert encounter.emergency_department["observations"] == [{"id": "obs-ed-1"}]
    assert encounter.emergency_department["vital_signs"][0]["components"] == [
        {"id": "comp-1", "observation_vital_signs_ed_id": "vital-1"}
    ]
    assert encounter.emergency_department["medications"]["dispensacoes_ed"] == [{"id": "mded-1"}]
    assert encounter.emergency_department["medications"]["medication_statements_ed"] == [{"id": "msed-1"}]

    assert encounter.icu["stay"] == {"id": "enc-icu-1", "encounter_id": "enc-1"}
    assert encounter.icu["procedures"] == [{"id": "proc-icu-1"}]
    assert encounter.icu["medications"] == [{"id": "mai-1"}]
    assert encounter.icu["charted_events"] == [{"id": "chart-1"}]
    assert encounter.icu["output_events"] == [{"id": "out-1"}]
    assert encounter.icu["datetime_events"] == [{"id": "dt-1"}]


def test_build_timeline_filters_temporal_events_and_keeps_empty_contexts() -> None:
    """Deve filtrar eventos por intervalo e manter contextos vazios vazios."""

    general_hospital = FakeGeneralHospitalRepository(
        labevents=[
            {"id": "lab-in", "effective_at": "2024-01-02T10:00:00"},
            {"id": "lab-out", "effective_at": "2024-01-05T10:00:00"},
            {"id": "lab-missing", "effective_at": None},
        ],
        micro_tests=[
            {"id": "mt-direct", "encounter_id": "enc-1", "effective_at": None},
            {"id": "mt-window", "encounter_id": None, "effective_at": "2024-01-02T12:00:00"},
            {"id": "mt-out", "encounter_id": None, "effective_at": "2024-01-05T12:00:00"},
        ],
        micro_orgs=[
            {"id": "mo-1", "derived_from_observation_micro_test_id": "mt-direct"},
            {"id": "mo-extra", "derived_from_observation_micro_test_id": "other"},
        ],
        micro_suscs=[
            {"id": "ms-1", "derived_from_observation_micro_org_id": "mo-1"},
            {"id": "ms-extra", "derived_from_observation_micro_org_id": "other"},
        ],
        specimens=[
            {"id": "spec-in", "collected_at": "2024-01-02T08:00:00"},
            {"id": "spec-out", "collected_at": "2024-01-05T08:00:00"},
        ],
    )
    service = _build_service(
        patient={"id": "pat-1"},
        encounters=[{"id": "enc-1", "start_date": "2024-01-02T00:00:00", "end_date": "2024-01-03T00:00:00"}],
        general_hospital=general_hospital,
    )

    timeline = service.build_timeline(Mock(), "pat-1")
    context = timeline.encounters[0].general_hospital

    assert [row["id"] for row in context["labs"]] == ["lab-in"]
    assert [row["id"] for row in context["microbiology"]["testes"]] == ["mt-window", "mt-direct"]
    assert [row["id"] for row in context["microbiology"]["organismos"]] == ["mo-1"]
    assert [row["id"] for row in context["microbiology"]["susceptibilidades"]] == ["ms-1"]
    assert [row["id"] for row in context["specimens"]] == ["spec-in"]


def test_build_timeline_keeps_empty_ed_and_icu_contexts_empty() -> None:
    """Deve manter ED e ICU vazios quando não houver dados."""

    service = _build_service(
        patient={"id": "pat-1"},
        encounters=[{"id": "enc-1", "start_date": "2024-01-01", "end_date": "2024-01-02"}],
    )

    timeline = service.build_timeline(Mock(), "pat-1")
    encounter = timeline.encounters[0]

    assert encounter.general_hospital["hospitalization"]["id"] == "enc-1"
    assert encounter.general_hospital["hospital_transfers"] == []
    assert encounter.emergency_department["stay"] is None
    assert encounter.emergency_department["diagnoses"] == []
    assert encounter.emergency_department["procedures"] == []
    assert encounter.emergency_department["observations"] == []
    assert encounter.emergency_department["vital_signs"] == []
    assert encounter.emergency_department["medications"] == {
        "dispensacoes_ed": [],
        "medication_statements_ed": [],
    }
    assert encounter.icu["stay"] is None
    assert encounter.icu["procedures"] == []
    assert encounter.icu["medications"] == []
    assert encounter.icu["charted_events"] == []
    assert encounter.icu["output_events"] == []
    assert encounter.icu["datetime_events"] == []
