"""
Testes do transformador de ProcedureICU.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.procedure_icu_transformer import (
    ProcedureICUTransformationError,
    ProcedureICUTransformer,
)


def test_transform_procedure_icu_with_full_payload() -> None:
    """
    Deve transformar um ProcedureICU completo e consolidar os primeiros valores úteis.
    """

    transformer = ProcedureICUTransformer()
    result = transformer.transform(
        {
            "id": "proc-icu-1",
            "resourceType": "Procedure",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "12345",
                        "system": "http://www.ama-assn.org/go/cpt",
                        "display": "Procedure ICU Example",
                    },
                ]
            },
            "category": {
                "coding": [
                    {"code": "", "system": ""},
                    {
                        "code": "inpatient",
                        "system": "http://terminology.hl7.org/CodeSystem/procedure-category",
                    },
                ]
            },
            "performedPeriod": {"start": "2024-01-01T08:00:00Z", "end": "2024-01-01T10:30:00Z"},
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "proc-icu-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "status": "completed",
        "procedure_code": "12345",
        "procedure_code_system": "http://www.ama-assn.org/go/cpt",
        "procedure_code_display": "Procedure ICU Example",
        "category_code": "inpatient",
        "category_system": "http://terminology.hl7.org/CodeSystem/procedure-category",
        "performed_start": "2024-01-01T08:00:00Z",
        "performed_end": "2024-01-01T10:30:00Z",
    }


def test_transform_procedure_icu_without_encounter() -> None:
    """
    Deve aceitar ProcedureICU sem `encounter`.
    """

    transformer = ProcedureICUTransformer()
    result = transformer.transform(
        {
            "id": "proc-icu-1",
            "resourceType": "Procedure",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "12345"}]},
            "category": {"coding": [{"code": "inpatient"}]},
            "performedPeriod": {"start": "2024-01-01T08:00:00Z", "end": "2024-01-01T10:30:00Z"},
        }
    )

    assert result["encounter_id"] is None


def test_transform_procedure_icu_without_code() -> None:
    """
    Deve aceitar ProcedureICU sem `code`.
    """

    transformer = ProcedureICUTransformer()
    result = transformer.transform(
        {
            "id": "proc-icu-1",
            "resourceType": "Procedure",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "category": [{"coding": [{"code": "inpatient"}]}],
            "performedPeriod": {"start": "2024-01-01T08:00:00Z", "end": "2024-01-01T10:30:00Z"},
        }
    )

    assert result["procedure_code"] is None
    assert result["procedure_code_system"] is None
    assert result["procedure_code_display"] is None


def test_transform_procedure_icu_without_category() -> None:
    """
    Deve aceitar ProcedureICU sem `category`.
    """

    transformer = ProcedureICUTransformer()
    result = transformer.transform(
        {
            "id": "proc-icu-1",
            "resourceType": "Procedure",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "12345"}]},
            "performedPeriod": {"start": "2024-01-01T08:00:00Z", "end": "2024-01-01T10:30:00Z"},
        }
    )

    assert result["category_code"] is None
    assert result["category_system"] is None


def test_transform_procedure_icu_without_performed_period() -> None:
    """
    Deve aceitar ProcedureICU sem `performedPeriod`.
    """

    transformer = ProcedureICUTransformer()
    result = transformer.transform(
        {
            "id": "proc-icu-1",
            "resourceType": "Procedure",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "12345"}]},
            "category": [{"coding": [{"code": "inpatient"}]}],
        }
    )

    assert result["performed_start"] is None
    assert result["performed_end"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("encounter", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_procedure_icu_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ProcedureICUTransformer()
    payload = {
        "id": "proc-icu-1",
        "resourceType": "Procedure",
        "status": "completed",
        "subject": {"reference": "Patient/pat-1"},
        "encounter": {"reference": "Encounter/enc-1"},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(ProcedureICUTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_procedure_icu_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas do ProcedureICU.
    """

    transformer = ProcedureICUTransformer()
    result = transformer.transform({"id": "proc-icu-1", "resourceType": "Procedure"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "status",
        "procedure_code",
        "procedure_code_system",
        "procedure_code_display",
        "category_code",
        "category_system",
        "performed_start",
        "performed_end",
    }
