"""
Testes do transformador de EncounterED.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.encounter_ed_transformer import (
    EncounterEDTransformationError,
    EncounterEDTransformer,
)


def test_transform_encounter_ed_with_full_payload() -> None:
    """
    Deve transformar um EncounterED completo.
    """

    transformer = EncounterEDTransformer()
    result = transformer.transform(
        {
            "id": "ed-1",
            "resourceType": "Encounter",
            "status": "in-progress",
            "class": {"code": "EMER", "system": "ignored", "display": "ignored"},
            "partOf": {"reference": "Encounter/enc-1"},
            "period": {"start": "2024-01-01T10:00:00Z", "end": "2024-01-01T14:00:00Z"},
            "subject": {"reference": "Patient/pat-1"},
            "serviceProvider": {"reference": "Organization/org-1"},
            "hospitalization": {
                "admitSource": {"coding": [{"code": "AMBULANCE"}]},
                "dischargeDisposition": {"coding": [{"code": "ADMITTED"}]},
            },
            "identifier": [
                {"value": ""},
                {"value": "33258284", "assigner": {"reference": "Organization/org-2"}},
            ],
        }
    )

    assert result.encounter_ed == {
        "id": "ed-1",
        "encounter_id": "enc-1",
        "patient_id": "pat-1",
        "organization_id": "org-1",
        "status": "in-progress",
        "class_code": "EMER",
        "start_date": "2024-01-01T10:00:00Z",
        "end_date": "2024-01-01T14:00:00Z",
        "admit_source_code": "AMBULANCE",
        "discharge_disposition_code": "ADMITTED",
        "identifier": "33258284",
    }


def test_transform_encounter_ed_without_partof() -> None:
    """
    Deve aceitar EncounterED sem `partOf`.
    """

    transformer = EncounterEDTransformer()
    result = transformer.transform(
        {
            "id": "ed-1",
            "resourceType": "Encounter",
            "subject": {"reference": "Patient/pat-1"},
        }
    )

    assert result.encounter_ed["encounter_id"] is None


def test_transform_encounter_ed_without_service_provider() -> None:
    """
    Deve aceitar EncounterED sem `serviceProvider`.
    """

    transformer = EncounterEDTransformer()
    result = transformer.transform(
        {
            "id": "ed-1",
            "resourceType": "Encounter",
            "partOf": {"reference": "Encounter/enc-1"},
            "subject": {"reference": "Patient/pat-1"},
        }
    )

    assert result.encounter_ed["organization_id"] is None


def test_transform_encounter_ed_without_hospitalization() -> None:
    """
    Deve aceitar EncounterED sem `hospitalization`.
    """

    transformer = EncounterEDTransformer()
    result = transformer.transform(
        {
            "id": "ed-1",
            "resourceType": "Encounter",
            "partOf": {"reference": "Encounter/enc-1"},
            "subject": {"reference": "Patient/pat-1"},
            "serviceProvider": {"reference": "Organization/org-1"},
        }
    )

    assert result.encounter_ed["admit_source_code"] is None
    assert result.encounter_ed["discharge_disposition_code"] is None


def test_transform_encounter_ed_rejects_invalid_partof_reference() -> None:
    """
    Deve rejeitar referência inválida em `partOf`.
    """

    transformer = EncounterEDTransformer()

    with pytest.raises(EncounterEDTransformationError):
        transformer.transform(
            {
                "id": "ed-1",
                "resourceType": "Encounter",
                "partOf": {"reference": "Patient/pat-1"},
                "subject": {"reference": "Patient/pat-1"},
            }
        )


def test_transform_encounter_ed_rejects_invalid_subject_reference() -> None:
    """
    Deve rejeitar referência inválida em `subject`.
    """

    transformer = EncounterEDTransformer()

    with pytest.raises(EncounterEDTransformationError):
        transformer.transform(
            {
                "id": "ed-1",
                "resourceType": "Encounter",
                "partOf": {"reference": "Encounter/enc-1"},
                "subject": {"reference": "Encounter/enc-1"},
            }
        )


def test_transform_encounter_ed_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas definidas para EncounterED.
    """

    transformer = EncounterEDTransformer()
    result = transformer.transform(
        {
            "id": "ed-1",
            "resourceType": "Encounter",
            "partOf": {"reference": "Encounter/enc-1"},
            "subject": {"reference": "Patient/pat-1"},
        }
    )

    assert set(result.encounter_ed.keys()) == {
        "id",
        "encounter_id",
        "patient_id",
        "organization_id",
        "status",
        "class_code",
        "start_date",
        "end_date",
        "admit_source_code",
        "discharge_disposition_code",
        "identifier",
    }
