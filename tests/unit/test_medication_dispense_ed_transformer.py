"""
Testes do transformador de MedicationDispenseED.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.medication_dispense_ed_transformer import (
    MedicationDispenseEDTransformationError,
    MedicationDispenseEDTransformer,
)


def test_transform_medication_dispense_ed_with_full_payload() -> None:
    """
    Deve transformar um MedicationDispenseED completo com as principais referências.
    """

    transformer = MedicationDispenseEDTransformer()
    result = transformer.transform(
        {
            "id": "mded-1",
            "resourceType": "MedicationDispense",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "whenHandedOver": "2024-01-01T12:00:00Z",
            "medicationCodeableConcept": {
                "text": "Acetaminophen",
                "coding": [
                    {"code": "", "system": ""},
                    {"code": "12345", "system": "http://www.nlm.nih.gov/research/umls/rxnorm"},
                ],
            },
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "mded-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "status": "completed",
        "when_handed_over": "2024-01-01T12:00:00Z",
        "medication_text": "Acetaminophen",
        "medication_code": "12345",
        "medication_code_system": "http://www.nlm.nih.gov/research/umls/rxnorm",
    }


def test_transform_medication_dispense_ed_without_context() -> None:
    """
    Deve aceitar MedicationDispenseED sem `context`.
    """

    transformer = MedicationDispenseEDTransformer()
    result = transformer.transform(
        {
            "id": "mded-1",
            "resourceType": "MedicationDispense",
            "subject": {"reference": "Patient/pat-1"},
            "whenHandedOver": "2024-01-01T12:00:00Z",
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        }
    )

    assert result["encounter_id"] is None


def test_transform_medication_dispense_ed_without_when_handed_over() -> None:
    """
    Deve aceitar MedicationDispenseED sem `whenHandedOver`.
    """

    transformer = MedicationDispenseEDTransformer()
    result = transformer.transform(
        {
            "id": "mded-1",
            "resourceType": "MedicationDispense",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        }
    )

    assert result["when_handed_over"] is None


def test_transform_medication_dispense_ed_without_medication_codeable_concept() -> None:
    """
    Deve aceitar MedicationDispenseED sem `medicationCodeableConcept`.
    """

    transformer = MedicationDispenseEDTransformer()
    result = transformer.transform(
        {
            "id": "mded-1",
            "resourceType": "MedicationDispense",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
        }
    )

    assert result["medication_text"] is None
    assert result["medication_code"] is None
    assert result["medication_code_system"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("context", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_medication_dispense_ed_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = MedicationDispenseEDTransformer()
    payload: dict[str, object] = {
        "id": "mded-1",
        "resourceType": "MedicationDispense",
        "subject": {"reference": "Patient/pat-1"},
        "context": {"reference": "Encounter/enc-1"},
        "whenHandedOver": "2024-01-01T12:00:00Z",
        "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(MedicationDispenseEDTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_medication_dispense_ed_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas definidas para MedicationDispenseED.
    """

    transformer = MedicationDispenseEDTransformer()
    result = transformer.transform({"id": "mded-1", "resourceType": "MedicationDispense"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "status",
        "when_handed_over",
        "medication_text",
        "medication_code",
        "medication_code_system",
    }
