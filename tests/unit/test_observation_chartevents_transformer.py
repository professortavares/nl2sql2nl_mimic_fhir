"""
Testes do transformador de ObservationChartevents.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.observation_chartevents_transformer import (
    ObservationCharteventsTransformationError,
    ObservationCharteventsTransformer,
)


def test_transform_observation_chartevents_with_value_quantity() -> None:
    """
    Deve transformar uma ObservationChartevents com `valueQuantity`.
    """

    transformer = ObservationCharteventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-chart-1",
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
                        "display": "Heart rate",
                    },
                ]
            },
            "category": [
                {
                    "coding": [
                        {"code": "", "system": ""},
                        {
                            "code": "vital-signs",
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        },
                    ]
                }
            ],
            "issued": "2024-01-01T08:01:00Z",
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "valueQuantity": {
                "value": 88,
                "unit": "bpm",
                "code": "/min",
                "system": "http://unitsofmeasure.org",
            },
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "obs-chart-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "status": "final",
        "observation_code": "1234-5",
        "observation_code_system": "http://loinc.org",
        "observation_code_display": "Heart rate",
        "category_code": "vital-signs",
        "category_system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "issued_at": "2024-01-01T08:01:00Z",
        "effective_at": "2024-01-01T08:00:00Z",
        "value": "88",
        "value_unit": "bpm",
        "value_code": "/min",
        "value_system": "http://unitsofmeasure.org",
        "value_string": None,
    }


def test_transform_observation_chartevents_with_value_string() -> None:
    """
    Deve transformar uma ObservationChartevents com `valueString`.
    """

    transformer = ObservationCharteventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-chart-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "category": {"coding": [{"code": "vital-signs"}]},
            "valueString": "patient resting",
        }
    )

    assert result["value"] is None
    assert result["value_string"] == "patient resting"


def test_transform_observation_chartevents_without_encounter() -> None:
    """
    Deve aceitar ObservationChartevents sem `encounter`.
    """

    transformer = ObservationCharteventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-chart-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "category": {"coding": [{"code": "vital-signs"}]},
            "valueString": "patient resting",
        }
    )

    assert result["encounter_id"] is None


def test_transform_observation_chartevents_without_category() -> None:
    """
    Deve aceitar ObservationChartevents sem `category`.
    """

    transformer = ObservationCharteventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-chart-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "valueString": "patient resting",
        }
    )

    assert result["category_code"] is None
    assert result["category_system"] is None


def test_transform_observation_chartevents_without_values() -> None:
    """
    Deve aceitar ObservationChartevents sem `valueQuantity` e sem `valueString`.
    """

    transformer = ObservationCharteventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-chart-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "category": {"coding": [{"code": "vital-signs"}]},
        }
    )

    assert result["value"] is None
    assert result["value_string"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("encounter", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_observation_chartevents_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ObservationCharteventsTransformer()
    payload: dict[str, object] = {
        "id": "obs-chart-1",
        "resourceType": "Observation",
        "status": "final",
        "subject": {"reference": "Patient/pat-1"},
        "encounter": {"reference": "Encounter/enc-1"},
        "code": {"coding": [{"code": "1234-5"}]},
        "category": {"coding": [{"code": "vital-signs"}]},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(ObservationCharteventsTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_observation_chartevents_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as estruturas simplificadas do ObservationChartevents.
    """

    transformer = ObservationCharteventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-chart-1",
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
        "observation_code_system",
        "observation_code_display",
        "category_code",
        "category_system",
        "issued_at",
        "effective_at",
        "value",
        "value_unit",
        "value_code",
        "value_system",
        "value_string",
    }
