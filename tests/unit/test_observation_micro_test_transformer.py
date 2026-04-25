"""
Testes do transformador de ObservationMicroTest.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.observation_micro_test_transformer import (
    ObservationMicroTestTransformationError,
    ObservationMicroTestTransformer,
)


def test_transform_observation_micro_test_with_full_payload() -> None:
    """
    Deve transformar uma ObservationMicroTest completa consolidando os primeiros valores úteis.
    """

    transformer = ObservationMicroTestTransformer()
    result = transformer.transform(
        {
            "id": "obs-micro-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "specimen": {"reference": "Specimen/spec-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "1234-5",
                        "system": "http://loinc.org",
                        "display": "Micro test code",
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
            "valueString": "positive",
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "obs-micro-1",
        "patient_id": "pat-1",
        "specimen_id": "spec-1",
        "encounter_id": "enc-1",
        "status": "final",
        "observation_code": "1234-5",
                "observation_code_display": "Micro test code",
        "category_code": "laboratory",
                "category_display": "Laboratory",
        "effective_at": "2024-01-01T08:00:00Z",
        "value_string": "positive",
        "value_code": None,
                "value_code_display": None,
    }


def test_transform_observation_micro_test_with_value_codeable_concept() -> None:
    """
    Deve transformar ObservationMicroTest com `valueCodeableConcept`.
    """

    transformer = ObservationMicroTestTransformer()
    result = transformer.transform(
        {
            "id": "obs-micro-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "specimen": {"reference": "Specimen/spec-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "category": {"coding": [{"code": "laboratory"}]},
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "valueCodeableConcept": {
                "coding": [
                    {
                        "code": "POS",
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0136",
                        "display": "Positive",
                    }
                ]
            },
        }
    )

    assert result["value_string"] is None
    assert result["value_code"] == "POS"
    assert result["value_code_display"] == "Positive"


def test_transform_observation_micro_test_without_encounter() -> None:
    """
    Deve aceitar ObservationMicroTest sem `encounter`.
    """

    transformer = ObservationMicroTestTransformer()
    result = transformer.transform(
        {
            "id": "obs-micro-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "specimen": {"reference": "Specimen/spec-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "category": {"coding": [{"code": "laboratory"}]},
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "valueString": "positive",
        }
    )

    assert result["encounter_id"] is None


def test_transform_observation_micro_test_without_specimen() -> None:
    """
    Deve aceitar ObservationMicroTest sem `specimen`.
    """

    transformer = ObservationMicroTestTransformer()
    result = transformer.transform(
        {
            "id": "obs-micro-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "category": {"coding": [{"code": "laboratory"}]},
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "valueString": "positive",
        }
    )

    assert result["specimen_id"] is None


def test_transform_observation_micro_test_without_value_string() -> None:
    """
    Deve aceitar ObservationMicroTest sem `valueString`.
    """

    transformer = ObservationMicroTestTransformer()
    result = transformer.transform(
        {
            "id": "obs-micro-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "specimen": {"reference": "Specimen/spec-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "category": {"coding": [{"code": "laboratory"}]},
            "effectiveDateTime": "2024-01-01T08:00:00Z",
        }
    )

    assert result["value_string"] is None


def test_transform_observation_micro_test_without_value_codeable_concept() -> None:
    """
    Deve aceitar ObservationMicroTest sem `valueCodeableConcept`.
    """

    transformer = ObservationMicroTestTransformer()
    result = transformer.transform(
        {
            "id": "obs-micro-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "specimen": {"reference": "Specimen/spec-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "category": {"coding": [{"code": "laboratory"}]},
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "valueString": "positive",
        }
    )

    assert result["value_code"] is None
    assert result["value_code_display"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("specimen", "Patient/pat-1", "Tipo de referência inválido"),
        ("encounter", "Specimen/spec-1", "Tipo de referência inválido"),
    ],
)
def test_transform_observation_micro_test_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ObservationMicroTestTransformer()
    payload = {
        "id": "obs-micro-1",
        "resourceType": "Observation",
        "status": "final",
        "subject": {"reference": "Patient/pat-1"},
        "specimen": {"reference": "Specimen/spec-1"},
        "encounter": {"reference": "Encounter/enc-1"},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(ObservationMicroTestTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_observation_micro_test_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas da tabela final.
    """

    transformer = ObservationMicroTestTransformer()
    result = transformer.transform({"id": "obs-micro-1", "resourceType": "Observation"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "specimen_id",
        "encounter_id",
        "status",
        "observation_code",
        "observation_code_display",
        "category_code",
        "category_display",
        "effective_at",
        "value_string",
        "value_code",
        "value_code_display",
    }
