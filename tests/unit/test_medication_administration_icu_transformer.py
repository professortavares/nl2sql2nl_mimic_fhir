"""
Testes do transformador de MedicationAdministrationICU.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.medication_administration_icu_transformer import (
    MedicationAdministrationICUTransformationError,
    MedicationAdministrationICUTransformer,
)


def test_transform_medication_administration_icu_with_full_payload() -> None:
    """
    Deve transformar uma MedicationAdministrationICU completa com as principais referências.
    """

    transformer = MedicationAdministrationICUTransformer()
    result = transformer.transform(
        {
            "id": "mau-1",
            "resourceType": "MedicationAdministration",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "category": {"coding": [{"code": "icu", "system": "http://example.org/category"}]},
            "medicationCodeableConcept": {
                "coding": [
                    {
                        "code": "12345",
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "display": "Drug",
                    }
                ]
            },
            "dosage": {
                "dose": {
                    "value": 2,
                    "unit": "mL",
                    "code": "mL",
                    "system": "http://unitsofmeasure.org",
                },
                "method": {"coding": [{"code": "IV", "system": "http://example.org/method"}]},
            },
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "mau-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "status": "completed",
        "effective_at": "2024-01-01T08:00:00Z",
        "category_code": "icu",
        "category_system": "http://example.org/category",
        "medication_code": "12345",
        "medication_code_system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "medication_code_display": "Drug",
        "dose_value": "2",
        "dose_unit": "mL",
        "dose_code": "mL",
        "dose_system": "http://unitsofmeasure.org",
        "method_code": "IV",
        "method_system": "http://example.org/method",
    }


def test_transform_medication_administration_icu_without_context() -> None:
    """
    Deve aceitar MedicationAdministrationICU sem `context`.
    """

    transformer = MedicationAdministrationICUTransformer()
    result = transformer.transform(
        {
            "id": "mau-1",
            "resourceType": "MedicationAdministration",
            "subject": {"reference": "Patient/pat-1"},
            "category": {"coding": [{"code": "icu"}]},
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
            "dosage": {"dose": {"value": 1}},
        }
    )

    assert result["encounter_id"] is None


def test_transform_medication_administration_icu_without_category() -> None:
    """
    Deve aceitar MedicationAdministrationICU sem `category`.
    """

    transformer = MedicationAdministrationICUTransformer()
    result = transformer.transform(
        {
            "id": "mau-1",
            "resourceType": "MedicationAdministration",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
            "dosage": {"dose": {"value": 1}},
        }
    )

    assert result["category_code"] is None
    assert result["category_system"] is None


def test_transform_medication_administration_icu_without_dosage() -> None:
    """
    Deve aceitar MedicationAdministrationICU sem `dosage`.
    """

    transformer = MedicationAdministrationICUTransformer()
    result = transformer.transform(
        {
            "id": "mau-1",
            "resourceType": "MedicationAdministration",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "category": {"coding": [{"code": "icu"}]},
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        }
    )

    assert result["dose_value"] is None
    assert result["method_code"] is None


def test_transform_medication_administration_icu_without_medication_codeable_concept() -> None:
    """
    Deve aceitar MedicationAdministrationICU sem `medicationCodeableConcept`.
    """

    transformer = MedicationAdministrationICUTransformer()
    result = transformer.transform(
        {
            "id": "mau-1",
            "resourceType": "MedicationAdministration",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "category": {"coding": [{"code": "icu"}]},
            "dosage": {"dose": {"value": 1}},
        }
    )

    assert result["medication_code"] is None
    assert result["medication_code_system"] is None
    assert result["medication_code_display"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("context", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_medication_administration_icu_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = MedicationAdministrationICUTransformer()
    payload: dict[str, object] = {
        "id": "mau-1",
        "resourceType": "MedicationAdministration",
        "subject": {"reference": "Patient/pat-1"},
        "context": {"reference": "Encounter/enc-1"},
        "category": {"coding": [{"code": "icu"}]},
        "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        "dosage": {"dose": {"value": 1}},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(MedicationAdministrationICUTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_medication_administration_icu_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas definidas para MedicationAdministrationICU.
    """

    transformer = MedicationAdministrationICUTransformer()
    result = transformer.transform({"id": "mau-1", "resourceType": "MedicationAdministration"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "status",
        "effective_at",
        "category_code",
        "category_system",
        "medication_code",
        "medication_code_system",
        "medication_code_display",
        "dose_value",
        "dose_unit",
        "dose_code",
        "dose_system",
        "method_code",
        "method_system",
    }
