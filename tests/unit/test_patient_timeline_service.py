"""
Testes do serviço de timeline clínica individual.
"""

from __future__ import annotations

from dataclasses import dataclass
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
class FakeClinicalEventsRepository:
    """Repositório fake de eventos clínicos."""

    conditions_by_encounter: dict[str, list[dict[str, object]]]
    procedures_by_encounter: dict[str, dict[str, list[dict[str, object]]]]
    medications_by_encounter: dict[str, dict[str, list[dict[str, object]]]]
    labevents: list[dict[str, object]]
    micro_tests: list[dict[str, object]]
    micro_orgs: list[dict[str, object]]
    micro_suscs: list[dict[str, object]]
    charted_by_encounter: dict[str, dict[str, list[dict[str, object]]]]
    vital_sign_components: list[dict[str, object]]
    specimens: list[dict[str, object]]

    def list_conditions(self, connection, encounter_id: str) -> list[dict[str, object]]:
        return list(self.conditions_by_encounter.get(encounter_id, []))

    def list_procedures(self, connection, encounter_id: str) -> dict[str, list[dict[str, object]]]:
        return {
            key: list(value)
            for key, value in self.procedures_by_encounter.get(
                encounter_id,
                {"procedure": [], "procedure_ed": [], "procedure_icu": []},
            ).items()
        }

    def list_medications(self, connection, encounter_id: str) -> dict[str, list[dict[str, object]]]:
        return {
            key: list(value)
            for key, value in self.medications_by_encounter.get(
                encounter_id,
                {
                    "medication_request": [],
                    "medication_dispense": [],
                    "medication_dispense_ed": [],
                    "medication_administration": [],
                    "medication_administration_icu": [],
                    "medication_statement_ed": [],
                },
            ).items()
        }

    def list_labevents(self, connection, patient_id: str) -> list[dict[str, object]]:
        return list(self.labevents)

    def list_micro_tests(self, connection, patient_id: str, encounter_id: str) -> list[dict[str, object]]:
        return list(self.micro_tests)

    def list_micro_orgs(self, connection, test_ids: list[str]) -> list[dict[str, object]]:
        return list(self.micro_orgs)

    def list_micro_suscs(self, connection, org_ids: list[str]) -> list[dict[str, object]]:
        return list(self.micro_suscs)

    def list_charted_observations(self, connection, encounter_id: str) -> dict[str, list[dict[str, object]]]:
        return {
            key: list(value)
            for key, value in self.charted_by_encounter.get(
                encounter_id,
                {
                    "observation_chartevents": [],
                    "observation_datetimeevents": [],
                    "observation_outputevents": [],
                    "observation_ed": [],
                    "observation_vital_signs_ed": [],
                },
            ).items()
        }

    def list_vital_sign_components(self, connection, observation_ids: list[str]) -> list[dict[str, object]]:
        return list(self.vital_sign_components)

    def list_specimens(self, connection, patient_id: str) -> list[dict[str, object]]:
        return list(self.specimens)


def _build_service(
    *,
    patient: dict[str, object] | None,
    encounters: list[dict[str, object]],
    conditions_by_encounter: dict[str, list[dict[str, object]]] | None = None,
    procedures_by_encounter: dict[str, dict[str, list[dict[str, object]]]] | None = None,
    medications_by_encounter: dict[str, dict[str, list[dict[str, object]]]] | None = None,
    labevents: list[dict[str, object]] | None = None,
    micro_tests: list[dict[str, object]] | None = None,
    micro_orgs: list[dict[str, object]] | None = None,
    micro_suscs: list[dict[str, object]] | None = None,
    charted_by_encounter: dict[str, dict[str, list[dict[str, object]]]] | None = None,
    vital_sign_components: list[dict[str, object]] | None = None,
    specimens: list[dict[str, object]] | None = None,
) -> PatientTimelineService:
    """Monta um serviço com repositórios fake."""

    repositories = TimelineRepositories(
        patient_repository=FakePatientRepository(patient=patient),
        encounter_repository=FakeEncounterRepository(encounters=encounters),
        clinical_events_repository=FakeClinicalEventsRepository(
            conditions_by_encounter=conditions_by_encounter or {},
            procedures_by_encounter=procedures_by_encounter or {},
            medications_by_encounter=medications_by_encounter or {},
            labevents=labevents or [],
            micro_tests=micro_tests or [],
            micro_orgs=micro_orgs or [],
            micro_suscs=micro_suscs or [],
            charted_by_encounter=charted_by_encounter or {},
            vital_sign_components=vital_sign_components or [],
            specimens=specimens or [],
        ),
    )
    return PatientTimelineService(repositories)


def test_build_timeline_raises_for_missing_patient() -> None:
    """
    Deve falhar com erro específico quando o paciente não existe.
    """

    service = _build_service(patient=None, encounters=[])

    with pytest.raises(PatientNotFoundError):
        service.build_timeline(Mock(), "pat-missing")


def test_build_timeline_returns_patient_with_no_encounters() -> None:
    """
    Deve retornar a timeline com paciente carregado e sem encounters.
    """

    service = _build_service(
        patient={
            "id": "pat-1",
            "name": "Jane Doe",
            "gender": "female",
            "birth_date": "1980-01-01",
            "identifier": "123",
            "race": "White",
            "ethnicity": "Not Hispanic or Latino",
            "birthsex": "F",
            "managing_organization_id": "org-1",
            "managing_organization_name": "Hospital A",
        },
        encounters=[],
    )

    timeline = service.build_timeline(Mock(), "pat-1")

    assert timeline.patient.id == "pat-1"
    assert timeline.patient.managing_organization_name == "Hospital A"
    assert timeline.encounters == []


def test_build_timeline_sorts_encounters_chronologically() -> None:
    """
    Deve ordenar encounters por início, fim e id.
    """

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


def test_build_timeline_groups_diagnoses_procedures_and_medications_by_encounter() -> None:
    """
    Deve preservar o agrupamento clínico por encounter.
    """

    service = _build_service(
        patient={"id": "pat-1"},
        encounters=[
            {"id": "enc-1", "start_date": "2024-01-01", "end_date": "2024-01-02"},
            {"id": "enc-2", "start_date": "2024-01-03", "end_date": "2024-01-04"},
        ],
        conditions_by_encounter={
            "enc-1": [{"id": "cond-1"}],
            "enc-2": [{"id": "cond-2"}],
        },
        procedures_by_encounter={
            "enc-1": {
                "procedure": [{"id": "proc-1"}],
                "procedure_ed": [],
                "procedure_icu": [],
            },
            "enc-2": {
                "procedure": [],
                "procedure_ed": [{"id": "proc-ed-1"}],
                "procedure_icu": [{"id": "proc-icu-1"}],
            },
        },
        medications_by_encounter={
            "enc-1": {
                "medication_request": [{"id": "mr-1"}],
                "medication_dispense": [],
                "medication_dispense_ed": [],
                "medication_administration": [],
                "medication_administration_icu": [],
                "medication_statement_ed": [],
            },
            "enc-2": {
                "medication_request": [],
                "medication_dispense": [{"id": "md-1"}],
                "medication_dispense_ed": [{"id": "mded-1"}],
                "medication_administration": [{"id": "ma-1"}],
                "medication_administration_icu": [{"id": "maicu-1"}],
                "medication_statement_ed": [{"id": "ms-1"}],
            },
        },
    )

    timeline = service.build_timeline(Mock(), "pat-1")

    encounter_one = timeline.encounters[0]
    encounter_two = timeline.encounters[1]
    assert encounter_one.diagnoses == [{"id": "cond-1"}]
    assert encounter_one.procedures["procedure"] == [{"id": "proc-1"}]
    assert encounter_one.medications["medication_request"] == [{"id": "mr-1"}]
    assert encounter_two.diagnoses == [{"id": "cond-2"}]
    assert encounter_two.procedures["procedure_ed"] == [{"id": "proc-ed-1"}]
    assert encounter_two.procedures["procedure_icu"] == [{"id": "proc-icu-1"}]
    assert encounter_two.medications["medication_dispense"] == [{"id": "md-1"}]
    assert encounter_two.medications["medication_statement_ed"] == [{"id": "ms-1"}]


def test_build_timeline_filters_events_by_encounter_window() -> None:
    """
    Deve manter apenas eventos dentro do intervalo do encounter.
    """

    service = _build_service(
        patient={"id": "pat-1"},
        encounters=[{"id": "enc-1", "start_date": "2024-01-02T00:00:00", "end_date": "2024-01-04T23:59:59"}],
        labevents=[
            {"id": "lab-in", "effective_at": "2024-01-03T12:00:00"},
            {"id": "lab-before", "effective_at": "2024-01-01T12:00:00"},
            {"id": "lab-after", "effective_at": "2024-01-05T12:00:00"},
            {"id": "lab-missing", "effective_at": None},
        ],
        micro_tests=[
            {"id": "mt-direct", "encounter_id": "enc-1", "effective_at": None},
            {"id": "mt-window", "encounter_id": None, "effective_at": "2024-01-03T10:00:00"},
            {"id": "mt-out", "encounter_id": None, "effective_at": "2024-01-05T10:00:00"},
        ],
        micro_orgs=[
            {"id": "mo-1", "derived_from_observation_micro_test_id": "mt-direct"},
        ],
        micro_suscs=[
            {"id": "ms-1", "derived_from_observation_micro_org_id": "mo-1"},
        ],
        charted_by_encounter={
            "enc-1": {
                "observation_chartevents": [{"id": "chart-1"}],
                "observation_datetimeevents": [{"id": "dt-1"}],
                "observation_outputevents": [{"id": "out-1"}],
                "observation_ed": [{"id": "ed-1"}],
                "observation_vital_signs_ed": [
                    {"id": "vital-1"},
                ],
            }
        },
        vital_sign_components=[{"id": "comp-1", "observation_vital_signs_ed_id": "vital-1"}],
        specimens=[
            {"id": "spec-in", "collected_at": "2024-01-03T08:00:00"},
            {"id": "spec-before", "collected_at": "2024-01-01T08:00:00"},
        ],
    )

    timeline = service.build_timeline(Mock(), "pat-1")
    encounter = timeline.encounters[0]

    assert [row["id"] for row in encounter.laboratory] == ["lab-in"]
    assert [row["id"] for row in encounter.microbiology["observation_micro_test"]] == [
        "mt-direct",
        "mt-window",
    ]
    assert [row["id"] for row in encounter.microbiology["observation_micro_org"]] == ["mo-1"]
    assert [row["id"] for row in encounter.microbiology["observation_micro_susc"]] == ["ms-1"]
    assert [row["id"] for row in encounter.specimens] == ["spec-in"]
    assert encounter.charted_observations["observation_vital_signs_ed"][0]["components"] == [
        {"id": "comp-1", "observation_vital_signs_ed_id": "vital-1"}
    ]


def test_build_timeline_keeps_empty_sections_present() -> None:
    """
    Deve montar a timeline mesmo quando não há eventos associados.
    """

    service = _build_service(
        patient={"id": "pat-1"},
        encounters=[{"id": "enc-1", "start_date": "2024-01-01", "end_date": "2024-01-02"}],
    )

    timeline = service.build_timeline(Mock(), "pat-1")
    encounter = timeline.encounters[0]

    assert encounter.diagnoses == []
    assert encounter.procedures == {"procedure": [], "procedure_ed": [], "procedure_icu": []}
    assert encounter.medications == {
        "medication_request": [],
        "medication_dispense": [],
        "medication_dispense_ed": [],
        "medication_administration": [],
        "medication_administration_icu": [],
        "medication_statement_ed": [],
    }
    assert encounter.laboratory == []
    assert encounter.microbiology == {
        "observation_micro_test": [],
        "observation_micro_org": [],
        "observation_micro_susc": [],
    }
    assert encounter.charted_observations == {
        "observation_chartevents": [],
        "observation_datetimeevents": [],
        "observation_outputevents": [],
        "observation_ed": [],
        "observation_vital_signs_ed": [],
    }
    assert encounter.specimens == []
