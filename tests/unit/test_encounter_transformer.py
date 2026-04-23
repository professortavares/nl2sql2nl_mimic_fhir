"""
Testes do transformador de Encounter.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.encounter_transformer import (
    EncounterTransformationError,
    EncounterTransformer,
)


def test_transform_encounter_with_full_payload() -> None:
    """
    Deve transformar um Encounter completo com múltiplas localizações.
    """

    transformer = EncounterTransformer()
    result = transformer.transform(
        {
            "id": "enc-1",
            "resourceType": "Encounter",
            "status": "finished",
            "class": {"code": "AMB", "system": "ignored", "display": "ignored"},
            "period": {"start": "2024-01-01T10:00:00Z", "end": "2024-01-01T12:00:00Z"},
            "subject": {"reference": "Patient/pat-1"},
            "serviceProvider": {"reference": "Organization/org-1"},
            "priority": {
                "coding": [
                    {"code": ""},
                    {"code": "UR", "system": "ignored", "display": "ignored"},
                ]
            },
            "serviceType": {"coding": [{"code": "MED", "system": "ignored"}]},
            "hospitalization": {
                "admitSource": {"coding": [{"code": "TRANSFER FROM HOSPITAL"}]},
                "dischargeDisposition": {"coding": [{"code": "HOME"}]},
            },
            "identifier": [
                {"value": ""},
                {"value": "22595853", "assigner": {"reference": "Organization/org-2"}},
            ],
            "location": [
                {
                    "period": {"start": "2024-01-01T10:00:00Z", "end": "2024-01-01T11:00:00Z"},
                    "location": {"reference": "Location/loc-1"},
                },
                {
                    "period": {"start": "2024-01-01T11:00:00Z", "end": "2024-01-01T12:00:00Z"},
                    "location": {"reference": "Location/loc-2"},
                },
            ],
        }
    )

    assert result.encounter == {
        "id": "enc-1",
        "patient_id": "pat-1",
        "organization_id": "org-1",
        "status": "finished",
        "class_code": "AMB",
        "start_date": "2024-01-01T10:00:00Z",
        "end_date": "2024-01-01T12:00:00Z",
        "priority_code": "UR",
        "service_type_code": "MED",
        "admit_source_code": "TRANSFER FROM HOSPITAL",
        "discharge_disposition_code": "HOME",
        "identifier": "22595853",
    }
    assert result.encounter_locations == [
        {
            "encounter_id": "enc-1",
            "location_id": "loc-1",
            "start_date": "2024-01-01T10:00:00Z",
            "end_date": "2024-01-01T11:00:00Z",
        },
        {
            "encounter_id": "enc-1",
            "location_id": "loc-2",
            "start_date": "2024-01-01T11:00:00Z",
            "end_date": "2024-01-01T12:00:00Z",
        },
    ]


def test_transform_encounter_without_service_provider() -> None:
    """
    Deve aceitar Encounter sem `serviceProvider`.
    """

    transformer = EncounterTransformer()
    result = transformer.transform(
        {
            "id": "enc-1",
            "resourceType": "Encounter",
            "subject": {"reference": "Patient/pat-1"},
        }
    )

    assert result.encounter["organization_id"] is None
    assert result.encounter_locations == []


def test_transform_encounter_without_location() -> None:
    """
    Deve aceitar Encounter sem lista de locations.
    """

    transformer = EncounterTransformer()
    result = transformer.transform(
        {
            "id": "enc-1",
            "resourceType": "Encounter",
            "subject": {"reference": "Patient/pat-1"},
            "serviceProvider": {"reference": "Organization/org-1"},
        }
    )

    assert result.encounter_locations == []


def test_transform_encounter_rejects_invalid_subject_reference() -> None:
    """
    Deve rejeitar referência inválida em `subject`.
    """

    transformer = EncounterTransformer()

    with pytest.raises(EncounterTransformationError):
        transformer.transform(
            {
                "id": "enc-1",
                "resourceType": "Encounter",
                "subject": {"reference": "Location/loc-1"},
            }
        )


def test_transform_encounter_rejects_invalid_location_reference() -> None:
    """
    Deve rejeitar referência inválida em `location[*].location.reference`.
    """

    transformer = EncounterTransformer()

    with pytest.raises(EncounterTransformationError):
        transformer.transform(
            {
                "id": "enc-1",
                "resourceType": "Encounter",
                "subject": {"reference": "Patient/pat-1"},
                "location": [{"location": {"reference": "Patient/pat-1"}}],
            }
        )


def test_transform_encounter_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas do Encounter.
    """

    transformer = EncounterTransformer()
    result = transformer.transform(
        {
            "id": "enc-1",
            "resourceType": "Encounter",
            "subject": {"reference": "Patient/pat-1"},
        }
    )

    assert set(result.encounter.keys()) == {
        "id",
        "patient_id",
        "organization_id",
        "status",
        "class_code",
        "start_date",
        "end_date",
        "priority_code",
        "service_type_code",
        "admit_source_code",
        "discharge_disposition_code",
        "identifier",
    }
