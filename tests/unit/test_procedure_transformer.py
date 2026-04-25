"""
Testes do transformador de Procedure.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.procedure_transformer import (
    ProcedureTransformationError,
    ProcedureTransformer,
)


def test_transform_procedure_with_full_payload() -> None:
    """
    Deve transformar um Procedure completo e consolidar o primeiro código útil.
    """

    transformer = ProcedureTransformer()
    result = transformer.transform(
        {
            "id": "proc-1",
            "resourceType": "Procedure",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "performedDateTime": "2024-01-01T08:00:00Z",
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "12345",
                        "system": "http://www.ama-assn.org/go/cpt",
                        "display": "Procedure Example",
                    },
                ]
            },
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "proc-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "status": "completed",
        "procedure_code": "12345",
        "procedure_code_display": "Procedure Example",
        "performed_at": "2024-01-01T08:00:00Z",
    }


def test_transform_procedure_without_encounter() -> None:
    """
    Deve aceitar Procedure sem `encounter`.
    """

    transformer = ProcedureTransformer()
    result = transformer.transform(
        {
            "id": "proc-1",
            "resourceType": "Procedure",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "12345"}]},
            "performedDateTime": "2024-01-01T08:00:00Z",
        }
    )

    assert result["encounter_id"] is None


def test_transform_procedure_without_code() -> None:
    """
    Deve aceitar Procedure sem `code`.
    """

    transformer = ProcedureTransformer()
    result = transformer.transform(
        {
            "id": "proc-1",
            "resourceType": "Procedure",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "performedDateTime": "2024-01-01T08:00:00Z",
        }
    )

    assert result["procedure_code"] is None
    assert result["procedure_code_display"] is None


def test_transform_procedure_without_performed_datetime() -> None:
    """
    Deve aceitar Procedure sem `performedDateTime`.
    """

    transformer = ProcedureTransformer()
    result = transformer.transform(
        {
            "id": "proc-1",
            "resourceType": "Procedure",
            "status": "completed",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "12345"}]},
        }
    )

    assert result["performed_at"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("encounter", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_procedure_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ProcedureTransformer()
    payload = {
        "id": "proc-1",
        "resourceType": "Procedure",
        "status": "completed",
        "subject": {"reference": "Patient/pat-1"},
        "encounter": {"reference": "Encounter/enc-1"},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(ProcedureTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_procedure_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas do Procedure.
    """

    transformer = ProcedureTransformer()
    result = transformer.transform({"id": "proc-1", "resourceType": "Procedure"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "status",
        "procedure_code",
        "procedure_code_display",
        "performed_at",
    }
