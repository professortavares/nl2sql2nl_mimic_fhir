"""
Testes do transformador de ObservationOutputevents.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.observation_outputevents_transformer import (
    ObservationOutputeventsTransformationError,
    ObservationOutputeventsTransformer,
)


def test_transform_observation_outputevents_with_value_quantity() -> None:
    """
    Deve transformar uma ObservationOutputevents com `valueQuantity`.
    """

    transformer = ObservationOutputeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-out-1",
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
                        "display": "Output volume",
                    },
                ]
            },
            "category": [
                {
                    "coding": [
                        {"code": "", "system": ""},
                        {
                            "code": "laboratory",
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        },
                    ]
                }
            ],
            "issued": "2024-01-01T08:01:00Z",
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "valueQuantity": {
                "value": 1200,
                "unit": "mL",
                "code": "mL",
                "system": "http://unitsofmeasure.org",
            },
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "obs-out-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "status": "final",
        "observation_code": "1234-5",
                "observation_code_display": "Output volume",
        "category_code": "laboratory",
                "issued_at": "2024-01-01T08:01:00Z",
        "effective_at": "2024-01-01T08:00:00Z",
        "value": "1200",
        "value_unit": "mL",
        "value_code": "mL",
            }


def test_transform_observation_outputevents_without_encounter() -> None:
    """
    Deve aceitar ObservationOutputevents sem `encounter`.
    """

    transformer = ObservationOutputeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-out-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "valueQuantity": {"value": 1},
        }
    )

    assert result["encounter_id"] is None


def test_transform_observation_outputevents_without_category() -> None:
    """
    Deve aceitar ObservationOutputevents sem `category`.
    """

    transformer = ObservationOutputeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-out-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "valueQuantity": {"value": 1},
        }
    )

    assert result["category_code"] is None
    

def test_transform_observation_outputevents_without_value_quantity() -> None:
    """
    Deve aceitar ObservationOutputevents sem `valueQuantity`.
    """

    transformer = ObservationOutputeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-out-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
        }
    )

    assert result["value"] is None
    assert result["value_unit"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("encounter", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_observation_outputevents_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ObservationOutputeventsTransformer()
    payload: dict[str, object] = {
        "id": "obs-out-1",
        "resourceType": "Observation",
        "status": "final",
        "subject": {"reference": "Patient/pat-1"},
        "encounter": {"reference": "Encounter/enc-1"},
        "code": {"coding": [{"code": "1234-5"}]},
        "valueQuantity": {"value": 1},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(ObservationOutputeventsTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_observation_outputevents_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as estruturas simplificadas do ObservationOutputevents.
    """

    transformer = ObservationOutputeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-out-1",
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
        "value",
        "value_unit",
        "value_code",
    }
