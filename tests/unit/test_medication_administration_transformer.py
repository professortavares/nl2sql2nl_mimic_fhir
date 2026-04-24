"""
Testes do transformador de MedicationAdministration.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.medication_administration_transformer import (
    MedicationAdministrationTransformationError,
    MedicationAdministrationTransformer,
)


def test_transform_medication_administration_with_full_payload() -> None:
    """
    Deve transformar uma MedicationAdministration completa com as principais referências.
    """

    transformer = MedicationAdministrationTransformer()
    result = transformer.transform(
        {
            "id": "ma-1",
            "resourceType": "MedicationAdministration",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "request": {"reference": "MedicationRequest/mr-1"},
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "medicationCodeableConcept": {
                "coding": [
                    {"code": "", "system": ""},
                    {
                        "code": "12345",
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    },
                ]
            },
            "dosage": {
                "text": "Administrar 1 vez",
                "dose": {
                    "value": 2,
                    "unit": "mL",
                    "code": "mL",
                    "system": "http://unitsofmeasure.org",
                },
                "method": {
                    "coding": [
                        {"code": "", "system": ""},
                        {"code": "IV", "system": "http://example.org/method"},
                    ]
                },
            },
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "ma-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "medication_request_id": "mr-1",
        "status": "completed",
        "effective_at": "2024-01-01T08:00:00Z",
        "medication_code": "12345",
        "medication_code_system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "dosage_text": "Administrar 1 vez",
        "dose_value": "2",
        "dose_unit": "mL",
        "dose_code": "mL",
        "dose_system": "http://unitsofmeasure.org",
        "method_code": "IV",
        "method_system": "http://example.org/method",
    }


def test_transform_medication_administration_without_context() -> None:
    """
    Deve aceitar MedicationAdministration sem `context`.
    """

    transformer = MedicationAdministrationTransformer()
    result = transformer.transform(
        {
            "id": "ma-1",
            "resourceType": "MedicationAdministration",
            "subject": {"reference": "Patient/pat-1"},
            "request": {"reference": "MedicationRequest/mr-1"},
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
            "dosage": {"dose": {"value": 1}},
        }
    )

    assert result["encounter_id"] is None


def test_transform_medication_administration_without_request() -> None:
    """
    Deve aceitar MedicationAdministration sem `request`.
    """

    transformer = MedicationAdministrationTransformer()
    result = transformer.transform(
        {
            "id": "ma-1",
            "resourceType": "MedicationAdministration",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
            "dosage": {"dose": {"value": 1}},
        }
    )

    assert result["medication_request_id"] is None


def test_transform_medication_administration_without_dosage() -> None:
    """
    Deve aceitar MedicationAdministration sem `dosage`.
    """

    transformer = MedicationAdministrationTransformer()
    result = transformer.transform(
        {
            "id": "ma-1",
            "resourceType": "MedicationAdministration",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "request": {"reference": "MedicationRequest/mr-1"},
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        }
    )

    assert result["dosage_text"] is None
    assert result["dose_value"] is None
    assert result["dose_unit"] is None
    assert result["dose_code"] is None
    assert result["dose_system"] is None
    assert result["method_code"] is None
    assert result["method_system"] is None


def test_transform_medication_administration_without_medication_codeable_concept() -> None:
    """
    Deve aceitar MedicationAdministration sem `medicationCodeableConcept`.
    """

    transformer = MedicationAdministrationTransformer()
    result = transformer.transform(
        {
            "id": "ma-1",
            "resourceType": "MedicationAdministration",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "request": {"reference": "MedicationRequest/mr-1"},
            "dosage": {"dose": {"value": 1}},
        }
    )

    assert result["medication_code"] is None
    assert result["medication_code_system"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("context", "Patient/pat-1", "Tipo de referência inválido"),
        ("request", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_medication_administration_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = MedicationAdministrationTransformer()
    payload: dict[str, object] = {
        "id": "ma-1",
        "resourceType": "MedicationAdministration",
        "subject": {"reference": "Patient/pat-1"},
        "context": {"reference": "Encounter/enc-1"},
        "request": {"reference": "MedicationRequest/mr-1"},
        "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        "dosage": {"dose": {"value": 1}},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(MedicationAdministrationTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_medication_administration_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas definidas para MedicationAdministration.
    """

    transformer = MedicationAdministrationTransformer()
    result = transformer.transform({"id": "ma-1", "resourceType": "MedicationAdministration"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "medication_request_id",
        "status",
        "effective_at",
        "medication_code",
        "medication_code_system",
        "dosage_text",
        "dose_value",
        "dose_unit",
        "dose_code",
        "dose_system",
        "method_code",
        "method_system",
    }
