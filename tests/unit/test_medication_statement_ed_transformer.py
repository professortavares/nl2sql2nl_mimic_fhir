"""
Testes do transformador de MedicationStatementED.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.medication_statement_ed_transformer import (
    MedicationStatementEDTransformationError,
    MedicationStatementEDTransformer,
)


def test_transform_medication_statement_ed_with_full_payload() -> None:
    """
    Deve transformar uma MedicationStatementED completa com as principais referências.
    """

    transformer = MedicationStatementEDTransformer()
    result = transformer.transform(
        {
            "id": "msed-1",
            "resourceType": "MedicationStatement",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "dateAsserted": "2024-01-01T08:00:00Z",
            "medicationCodeableConcept": {
                "text": "Paracetamol",
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "12345",
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "display": "Paracetamol 500mg",
                    },
                ],
            },
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "msed-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "status": "completed",
        "date_asserted": "2024-01-01T08:00:00Z",
        "medication_text": "Paracetamol",
        "medication_code": "12345",
                "medication_code_display": "Paracetamol 500mg",
    }


def test_transform_medication_statement_ed_without_context() -> None:
    """
    Deve aceitar MedicationStatementED sem `context`.
    """

    transformer = MedicationStatementEDTransformer()
    result = transformer.transform(
        {
            "id": "msed-1",
            "resourceType": "MedicationStatement",
            "subject": {"reference": "Patient/pat-1"},
            "dateAsserted": "2024-01-01T08:00:00Z",
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        }
    )

    assert result["encounter_id"] is None


def test_transform_medication_statement_ed_without_date_asserted() -> None:
    """
    Deve aceitar MedicationStatementED sem `dateAsserted`.
    """

    transformer = MedicationStatementEDTransformer()
    result = transformer.transform(
        {
            "id": "msed-1",
            "resourceType": "MedicationStatement",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        }
    )

    assert result["date_asserted"] is None


def test_transform_medication_statement_ed_without_medication_codeable_concept() -> None:
    """
    Deve aceitar MedicationStatementED sem `medicationCodeableConcept`.
    """

    transformer = MedicationStatementEDTransformer()
    result = transformer.transform(
        {
            "id": "msed-1",
            "resourceType": "MedicationStatement",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "dateAsserted": "2024-01-01T08:00:00Z",
        }
    )

    assert result["medication_text"] is None
    assert result["medication_code"] is None
    assert result["medication_code_display"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("context", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_medication_statement_ed_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = MedicationStatementEDTransformer()
    payload: dict[str, object] = {
        "id": "msed-1",
        "resourceType": "MedicationStatement",
        "subject": {"reference": "Patient/pat-1"},
        "context": {"reference": "Encounter/enc-1"},
        "dateAsserted": "2024-01-01T08:00:00Z",
        "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(MedicationStatementEDTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_medication_statement_ed_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas definidas para MedicationStatementED.
    """

    transformer = MedicationStatementEDTransformer()
    result = transformer.transform({"id": "msed-1", "resourceType": "MedicationStatement"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "status",
        "date_asserted",
        "medication_text",
        "medication_code",
        "medication_code_display",
    }
