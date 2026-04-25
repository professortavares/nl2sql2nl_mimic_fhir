"""
Testes do transformador de Condition.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.condition_transformer import (
    ConditionTransformationError,
    ConditionTransformer,
)


def test_transform_condition_with_full_payload() -> None:
    """
    Deve transformar uma Condition completa e consolidar o primeiro código útil.
    """

    transformer = ConditionTransformer()
    result = transformer.transform(
        {
            "id": "cond-1",
            "resourceType": "Condition",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "E11.9",
                        "system": "http://hl7.org/fhir/sid/icd-10-cm",
                        "display": "Type 2 diabetes mellitus without complications",
                    },
                ]
            },
            "category": [
                {
                    "coding": [
                        {"code": "", "system": "", "display": ""},
                        {
                            "code": "problem-list-item",
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "display": "Problem List Item",
                        },
                    ]
                }
            ],
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "cond-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "condition_code": "E11.9",
        "condition_code_display": "Type 2 diabetes mellitus without complications",
        "category_code": "problem-list-item",
        "category_display": "Problem List Item",
    }


def test_transform_condition_without_optional_fields() -> None:
    """
    Deve aceitar Condition sem campos opcionais consolidados.
    """

    transformer = ConditionTransformer()
    result = transformer.transform({"id": "cond-1", "resourceType": "Condition"})

    assert result == {
        "id": "cond-1",
        "patient_id": None,
        "encounter_id": None,
        "condition_code": None,
        "condition_code_display": None,
        "category_code": None,
        "category_display": None,
    }


def test_transform_condition_without_category() -> None:
    """
    Deve aceitar Condition sem `category`.
    """

    transformer = ConditionTransformer()
    result = transformer.transform(
        {
            "id": "cond-1",
            "resourceType": "Condition",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "E11.9"}]},
        }
    )

    assert result["category_code"] is None
    assert result["category_display"] is None


def test_transform_condition_without_code() -> None:
    """
    Deve aceitar Condition sem `code`.
    """

    transformer = ConditionTransformer()
    result = transformer.transform(
        {
            "id": "cond-1",
            "resourceType": "Condition",
            "subject": {"reference": "Patient/pat-1"},
            "category": [{"coding": [{"code": "problem-list-item"}]}],
        }
    )

    assert result["condition_code"] is None
    assert result["condition_code_display"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("encounter", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_condition_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ConditionTransformer()
    payload = {
        "id": "cond-1",
        "resourceType": "Condition",
        "subject": {"reference": "Patient/pat-1"},
        "encounter": {"reference": "Encounter/enc-1"},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(ConditionTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_condition_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas do Condition.
    """

    transformer = ConditionTransformer()
    result = transformer.transform({"id": "cond-1", "resourceType": "Condition"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "condition_code",
        "condition_code_display",
        "category_code",
        "category_display",
    }
