"""
Testes do transformador de ObservationDatetimeevents.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.observation_datetimeevents_transformer import (
    ObservationDatetimeeventsTransformationError,
    ObservationDatetimeeventsTransformer,
)


def test_transform_observation_datetimeevents_with_value_datetime() -> None:
    """
    Deve transformar uma ObservationDatetimeevents com `valueDateTime`.
    """

    transformer = ObservationDatetimeeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-date-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "1234-5",
                        "system": "http://loinc.org",
                        "display": "Encounter start",
                    },
                ]
            },
            "category": [
                {
                    "coding": [
                        {"code": "", "system": ""},
                        {
                            "code": "exam",
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        },
                    ]
                }
            ],
            "issued": "2024-01-01T08:01:00Z",
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "valueDateTime": "2024-01-01T08:05:00Z",
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "obs-date-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "status": "final",
        "observation_code": "1234-5",
                "observation_code_display": "Encounter start",
        "category_code": "exam",
                "issued_at": "2024-01-01T08:01:00Z",
        "effective_at": "2024-01-01T08:00:00Z",
        "value_datetime": "2024-01-01T08:05:00Z",
    }


def test_transform_observation_datetimeevents_without_encounter() -> None:
    """
    Deve aceitar ObservationDatetimeevents sem `encounter`.
    """

    transformer = ObservationDatetimeeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-date-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "valueDateTime": "2024-01-01T08:05:00Z",
        }
    )

    assert result["encounter_id"] is None


def test_transform_observation_datetimeevents_without_category() -> None:
    """
    Deve aceitar ObservationDatetimeevents sem `category`.
    """

    transformer = ObservationDatetimeeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-date-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "valueDateTime": "2024-01-01T08:05:00Z",
        }
    )

    assert result["category_code"] is None
    

def test_transform_observation_datetimeevents_without_value_datetime() -> None:
    """
    Deve aceitar ObservationDatetimeevents sem `valueDateTime`.
    """

    transformer = ObservationDatetimeeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-date-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
        }
    )

    assert result["value_datetime"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("encounter", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_observation_datetimeevents_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ObservationDatetimeeventsTransformer()
    payload: dict[str, object] = {
        "id": "obs-date-1",
        "resourceType": "Observation",
        "status": "final",
        "subject": {"reference": "Patient/pat-1"},
        "encounter": {"reference": "Encounter/enc-1"},
        "code": {"coding": [{"code": "1234-5"}]},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(ObservationDatetimeeventsTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_observation_datetimeevents_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as estruturas simplificadas do ObservationDatetimeevents.
    """

    transformer = ObservationDatetimeeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-date-1",
            "resourceType": "Observation",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "1234-5"}]},
        }
    )

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "status",
        "observation_code",
        "observation_code_display",
        "category_code",
        "issued_at",
        "effective_at",
        "value_datetime",
    }
