"""
Testes do transformador de ObservationED.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.observation_ed_transformer import (
    ObservationEDTransformationError,
    ObservationEDTransformer,
)


def test_transform_observation_ed_with_value_string() -> None:
    """
    Deve transformar uma ObservationED com `valueString`.
    """

    transformer = ObservationEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-ed-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "partOf": [{"reference": "Procedure/proc-1"}],
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "1234-5",
                        "system": "http://loinc.org",
                        "display": "ED observation",
                    },
                ]
            },
            "category": [
                {
                    "coding": [
                        {"code": "", "system": ""},
                        {
                            "code": "emergency",
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "display": "Emergency",
                        },
                    ]
                }
            ],
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "valueString": "patient stable",
            "dataAbsentReason": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "not-asked",
                        "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
                        "display": "Not Asked",
                    },
                ]
            },
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "obs-ed-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "procedure_id": "proc-1",
        "status": "final",
        "observation_code": "1234-5",
        "observation_code_display": "ED observation",
        "category_code": "emergency",
        "category_system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "category_display": "Emergency",
        "effective_at": "2024-01-01T08:00:00Z",
        "value_string": "patient stable",
        "data_absent_reason_code": "not-asked",
        "data_absent_reason_display": "Not Asked",
    }


def test_transform_observation_ed_with_data_absent_reason() -> None:
    """
    Deve transformar uma ObservationED com `dataAbsentReason`.
    """

    transformer = ObservationEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-ed-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "1234-5"}]},
            "dataAbsentReason": {"coding": [{"code": "unknown"}]},
        }
    )

    assert result["data_absent_reason_code"] == "unknown"
    assert result["value_string"] is None


def test_transform_observation_ed_without_encounter() -> None:
    """
    Deve aceitar ObservationED sem `encounter`.
    """

    transformer = ObservationEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-ed-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "partOf": [{"reference": "Procedure/proc-1"}],
            "code": {"coding": [{"code": "1234-5"}]},
        }
    )

    assert result["encounter_id"] is None


def test_transform_observation_ed_without_partof() -> None:
    """
    Deve aceitar ObservationED sem `partOf`.
    """

    transformer = ObservationEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-ed-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "1234-5"}]},
        }
    )

    assert result["procedure_id"] is None


def test_transform_observation_ed_without_value_string() -> None:
    """
    Deve aceitar ObservationED sem `valueString`.
    """

    transformer = ObservationEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-ed-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "partOf": [{"reference": "Procedure/proc-1"}],
            "code": {"coding": [{"code": "1234-5"}]},
        }
    )

    assert result["value_string"] is None


def test_transform_observation_ed_without_data_absent_reason() -> None:
    """
    Deve aceitar ObservationED sem `dataAbsentReason`.
    """

    transformer = ObservationEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-ed-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "partOf": [{"reference": "Procedure/proc-1"}],
            "code": {"coding": [{"code": "1234-5"}]},
            "valueString": "patient stable",
        }
    )

    assert result["data_absent_reason_code"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("encounter", "Patient/pat-1", "Tipo de referência inválido"),
        ("partOf", "Encounter/enc-1", "Tipo de referência inválido"),
    ],
)
def test_transform_observation_ed_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ObservationEDTransformer()
    payload: dict[str, object] = {
        "id": "obs-ed-1",
        "resourceType": "Observation",
        "status": "final",
        "subject": {"reference": "Patient/pat-1"},
        "encounter": {"reference": "Encounter/enc-1"},
        "partOf": [{"reference": "Procedure/proc-1"}],
        "code": {"coding": [{"code": "1234-5"}]},
    }
    payload[field_name] = {"reference": reference_value} if field_name != "partOf" else [{"reference": reference_value}]

    with pytest.raises(ObservationEDTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_observation_ed_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as estruturas simplificadas do ObservationED.
    """

    transformer = ObservationEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-ed-1",
            "resourceType": "Observation",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "1234-5"}]},
        }
    )

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "procedure_id",
        "status",
        "observation_code",
        "observation_code_display",
        "category_code",
        "category_system",
        "category_display",
        "effective_at",
        "value_string",
        "data_absent_reason_code",
        "data_absent_reason_display",
    }
