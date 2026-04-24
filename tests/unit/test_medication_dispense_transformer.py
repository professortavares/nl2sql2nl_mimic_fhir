"""
Testes do transformador de MedicationDispense.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.medication_dispense_transformer import (
    MedicationDispenseTransformationError,
    MedicationDispenseTransformer,
)


def test_transform_medication_dispense_with_full_payload() -> None:
    """
    Deve transformar um MedicationDispense completo com as principais referências.
    """

    transformer = MedicationDispenseTransformer()
    result = transformer.transform(
        {
            "id": "md-1",
            "resourceType": "MedicationDispense",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "authorizingPrescription": [
                {"reference": ""},
                {"reference": "MedicationRequest/mr-1"},
            ],
            "identifier": [
                {"value": ""},
                {"value": "disp-123"},
            ],
            "medicationCodeableConcept": {
                "coding": [
                    {"code": "", "system": ""},
                    {
                        "code": "12345",
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    },
                ]
            },
            "dosageInstruction": [
                {
                    "route": {"coding": [{"code": "", "system": ""}, {"code": "PO"}]},
                    "timing": {"code": {"coding": [{"code": "", "system": ""}, {"code": "BID"}]}},
                }
            ],
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "md-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "medication_request_id": "mr-1",
        "status": "completed",
        "identifier": "disp-123",
        "medication_code": "12345",
        "medication_code_system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "route_code": "PO",
        "frequency_code": "BID",
    }


def test_transform_medication_dispense_without_context() -> None:
    """
    Deve aceitar MedicationDispense sem `context`.
    """

    transformer = MedicationDispenseTransformer()
    result = transformer.transform(
        {
            "id": "md-1",
            "resourceType": "MedicationDispense",
            "subject": {"reference": "Patient/pat-1"},
            "authorizingPrescription": [{"reference": "MedicationRequest/mr-1"}],
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        }
    )

    assert result["encounter_id"] is None


def test_transform_medication_dispense_without_authorizing_prescription() -> None:
    """
    Deve aceitar MedicationDispense sem `authorizingPrescription`.
    """

    transformer = MedicationDispenseTransformer()
    result = transformer.transform(
        {
            "id": "md-1",
            "resourceType": "MedicationDispense",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        }
    )

    assert result["medication_request_id"] is None


def test_transform_medication_dispense_without_dosage_instruction() -> None:
    """
    Deve aceitar MedicationDispense sem `dosageInstruction`.
    """

    transformer = MedicationDispenseTransformer()
    result = transformer.transform(
        {
            "id": "md-1",
            "resourceType": "MedicationDispense",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "authorizingPrescription": [{"reference": "MedicationRequest/mr-1"}],
            "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
        }
    )

    assert result["route_code"] is None
    assert result["frequency_code"] is None


def test_transform_medication_dispense_without_medication_codeable_concept() -> None:
    """
    Deve aceitar MedicationDispense sem `medicationCodeableConcept`.
    """

    transformer = MedicationDispenseTransformer()
    result = transformer.transform(
        {
            "id": "md-1",
            "resourceType": "MedicationDispense",
            "subject": {"reference": "Patient/pat-1"},
            "context": {"reference": "Encounter/enc-1"},
            "authorizingPrescription": [{"reference": "MedicationRequest/mr-1"}],
        }
    )

    assert result["medication_code"] is None
    assert result["medication_code_system"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("context", "Patient/pat-1", "Tipo de referência inválido"),
        ("authorizingPrescription", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_medication_dispense_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = MedicationDispenseTransformer()
    payload: dict[str, object] = {
        "id": "md-1",
        "resourceType": "MedicationDispense",
        "subject": {"reference": "Patient/pat-1"},
        "context": {"reference": "Encounter/enc-1"},
        "authorizingPrescription": [{"reference": "MedicationRequest/mr-1"}],
        "medicationCodeableConcept": {"coding": [{"code": "12345"}]},
    }
    if field_name == "subject":
        payload[field_name] = {"reference": reference_value}
    elif field_name == "context":
        payload[field_name] = {"reference": reference_value}
    else:
        payload[field_name] = [{"reference": reference_value}]

    with pytest.raises(MedicationDispenseTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_medication_dispense_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas definidas para MedicationDispense.
    """

    transformer = MedicationDispenseTransformer()
    result = transformer.transform({"id": "md-1", "resourceType": "MedicationDispense"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "medication_request_id",
        "status",
        "identifier",
        "medication_code",
        "medication_code_system",
        "route_code",
        "frequency_code",
    }
