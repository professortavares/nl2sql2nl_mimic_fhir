"""
Testes do transformador de MedicationRequest.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.medication_request_transformer import (
    MedicationRequestTransformationError,
    MedicationRequestTransformer,
)


def test_transform_medication_request_with_full_payload() -> None:
    """
    Deve transformar um MedicationRequest completo e consolidar a primeira dosagem válida.
    """

    transformer = MedicationRequestTransformer()
    result = transformer.transform(
        {
            "id": "mr-1",
            "resourceType": "MedicationRequest",
            "intent": "order",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "authoredOn": "2024-01-01T08:00:00Z",
            "identifier": [
                {"value": "", "system": "ignored"},
                {
                    "value": "53072793",
                    "system": "http://mimic.mit.edu/fhir/mimic/identifier/medication-request-phid",
                },
            ],
            "dispenseRequest": {
                "validityPeriod": {"start": "2024-01-01T08:00:00Z", "end": "2024-01-01T10:00:00Z"}
            },
            "dosageInstruction": [
                {
                    "text": "",
                    "route": {"coding": [{"code": "", "system": "ignored"}]},
                    "timing": {"code": {"coding": [{"code": "", "system": "ignored"}]}}
                },
                {
                    "text": "15g/60mL Bottle",
                    "route": {
                        "coding": [
                            {"code": "", "system": "ignored"},
                            {
                                "code": "PO/NG",
                                "system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-medication-route",
                            },
                        ]
                    },
                    "timing": {
                        "code": {
                            "coding": [
                                {"code": "", "system": "ignored"},
                                {
                                    "code": "ONCE",
                                    "system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-medication-frequency",
                                },
                            ]
                        }
                    },
                    "doseAndRate": [
                        {
                            "doseQuantity": {
                                "value": "",
                                "unit": "",
                                "code": "gm",
                                "system": "ignored",
                            }
                        },
                        {
                            "doseQuantity": {
                                "value": 30,
                                "unit": "gm",
                                "code": "gm",
                                "system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-units",
                            }
                        },
                    ],
                },
            ],
            "medicationReference": {"reference": "Medication/med-1"},
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "mr-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "medication_id": "med-1",
        "intent": "order",
        "status": "completed",
        "authored_on": "2024-01-01T08:00:00Z",
        "identifier": "53072793",
        "validity_start": "2024-01-01T08:00:00Z",
        "validity_end": "2024-01-01T10:00:00Z",
        "dosage_text": "15g/60mL Bottle",
        "route_code": "PO/NG",
        "frequency_code": "ONCE",
        "dose_value": "30",
        "dose_unit": "gm",
    }


def test_transform_medication_request_without_optional_fields() -> None:
    """
    Deve aceitar MedicationRequest sem campos opcionais consolidados.
    """

    transformer = MedicationRequestTransformer()
    result = transformer.transform({"id": "mr-1", "resourceType": "MedicationRequest"})

    assert result == {
        "id": "mr-1",
        "patient_id": None,
        "encounter_id": None,
        "medication_id": None,
        "intent": None,
        "status": None,
        "authored_on": None,
        "identifier": None,
        "validity_start": None,
        "validity_end": None,
        "dosage_text": None,
        "route_code": None,
        "frequency_code": None,
        "dose_value": None,
        "dose_unit": None,
    }


def test_transform_medication_request_without_dispense_request() -> None:
    """
    Deve aceitar MedicationRequest sem `dispenseRequest`.
    """

    transformer = MedicationRequestTransformer()
    result = transformer.transform(
        {
            "id": "mr-1",
            "resourceType": "MedicationRequest",
            "subject": {"reference": "Patient/pat-1"},
        }
    )

    assert result["validity_start"] is None
    assert result["validity_end"] is None


def test_transform_medication_request_without_dosage_instruction() -> None:
    """
    Deve aceitar MedicationRequest sem `dosageInstruction`.
    """

    transformer = MedicationRequestTransformer()
    result = transformer.transform(
        {
            "id": "mr-1",
            "resourceType": "MedicationRequest",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "medicationReference": {"reference": "Medication/med-1"},
        }
    )

    assert result["dosage_text"] is None
    assert result["route_code"] is None
    assert result["frequency_code"] is None
    assert result["dose_value"] is None
    assert result["dose_unit"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("encounter", "Patient/pat-1", "Tipo de referência inválido"),
        ("medicationReference", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_medication_request_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = MedicationRequestTransformer()
    payload = {
        "id": "mr-1",
        "resourceType": "MedicationRequest",
        "subject": {"reference": "Patient/pat-1"},
        "encounter": {"reference": "Encounter/enc-1"},
        "medicationReference": {"reference": "Medication/med-1"},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(MedicationRequestTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_medication_request_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas definidas para MedicationRequest.
    """

    transformer = MedicationRequestTransformer()
    result = transformer.transform({"id": "mr-1", "resourceType": "MedicationRequest"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "medication_id",
        "intent",
        "status",
        "authored_on",
        "identifier",
        "validity_start",
        "validity_end",
        "dosage_text",
        "route_code",
        "frequency_code",
        "dose_value",
        "dose_unit",
    }
