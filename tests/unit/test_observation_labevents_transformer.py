"""
Testes do transformador de ObservationLabevents.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.observation_labevents_transformer import (
    ObservationLabeventsTransformationError,
    ObservationLabeventsTransformer,
)


def test_transform_observation_labevents_with_full_payload() -> None:
    """
    Deve transformar uma ObservationLabevents completa consolidando os primeiros valores úteis.
    """

    transformer = ObservationLabeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "specimen": {"reference": "Specimen/spec-1"},
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "59408-5",
                        "system": "http://loinc.org",
                        "display": "Oxygen saturation in Blood",
                    },
                ]
            },
            "category": [
                {
                    "coding": [
                        {"code": "", "system": "", "display": ""},
                        {
                            "code": "laboratory",
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "display": "Laboratory",
                        },
                    ]
                }
            ],
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "issued": "2024-01-01T08:15:00Z",
            "identifier": [
                {"value": ""},
                {"value": "lab-id-1"},
            ],
            "valueQuantity": {"value": 98.7, "unit": "%", "code": "%", "system": "http://unitsofmeasure.org"},
            "referenceRange": [
                {
                    "low": {"value": 95, "unit": "%"},
                    "high": {"value": 100, "unit": "%"},
                }
            ],
            "extension": [
                {"url": "ignored", "valueString": "low"},
                {
                    "url": "http://mimic.mit.edu/fhir/mimic/StructureDefinition/lab-priority",
                    "valueString": "urgent",
                },
            ],
            "note": [{"text": "Coleta sem intercorrências."}],
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "obs-1",
        "patient_id": "pat-1",
        "specimen_id": "spec-1",
        "status": "final",
        "observation_code": "59408-5",
                "observation_code_display": "Oxygen saturation in Blood",
        "category_code": "laboratory",
                "category_display": "Laboratory",
        "effective_at": "2024-01-01T08:00:00Z",
        "issued_at": "2024-01-01T08:15:00Z",
        "identifier": "lab-id-1",
        "value": "98.7",
        "value_unit": "%",
        "value_code": "%",
                "reference_low_value": "95",
        "reference_low_unit": "%",
        "reference_high_value": "100",
        "reference_high_unit": "%",
        "lab_priority": "urgent",
        "note": "Coleta sem intercorrências.",
    }


def test_transform_observation_labevents_without_specimen() -> None:
    """
    Deve aceitar ObservationLabevents sem `specimen`.
    """

    transformer = ObservationLabeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "59408-5"}]},
            "category": {"coding": [{"code": "laboratory"}]},
        }
    )

    assert result["specimen_id"] is None


def test_transform_observation_labevents_without_value_quantity() -> None:
    """
    Deve aceitar ObservationLabevents sem `valueQuantity`.
    """

    transformer = ObservationLabeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "specimen": {"reference": "Specimen/spec-1"},
            "code": {"coding": [{"code": "59408-5"}]},
            "category": {"coding": [{"code": "laboratory"}]},
        }
    )

    assert result["value"] is None
    assert result["value_unit"] is None
    assert result["value_code"] is None
    

def test_transform_observation_labevents_without_reference_range() -> None:
    """
    Deve aceitar ObservationLabevents sem `referenceRange`.
    """

    transformer = ObservationLabeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "specimen": {"reference": "Specimen/spec-1"},
            "code": {"coding": [{"code": "59408-5"}]},
            "category": {"coding": [{"code": "laboratory"}]},
        }
    )

    assert result["reference_low_value"] is None
    assert result["reference_high_value"] is None


def test_transform_observation_labevents_without_note() -> None:
    """
    Deve aceitar ObservationLabevents sem `note`.
    """

    transformer = ObservationLabeventsTransformer()
    result = transformer.transform(
        {
            "id": "obs-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "specimen": {"reference": "Specimen/spec-1"},
            "code": {"coding": [{"code": "59408-5"}]},
            "category": {"coding": [{"code": "laboratory"}]},
        }
    )

    assert result["note"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("specimen", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_observation_labevents_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ObservationLabeventsTransformer()
    payload = {
        "id": "obs-1",
        "resourceType": "Observation",
        "status": "final",
        "subject": {"reference": "Patient/pat-1"},
        "specimen": {"reference": "Specimen/spec-1"},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(ObservationLabeventsTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_observation_labevents_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas da tabela final.
    """

    transformer = ObservationLabeventsTransformer()
    result = transformer.transform({"id": "obs-1", "resourceType": "Observation"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "specimen_id",
        "status",
        "observation_code",
        "observation_code_display",
        "category_code",
        "category_display",
        "effective_at",
        "issued_at",
        "identifier",
        "value",
        "value_unit",
        "value_code",
        "reference_low_value",
        "reference_low_unit",
        "reference_high_value",
        "reference_high_unit",
        "lab_priority",
        "note",
    }
