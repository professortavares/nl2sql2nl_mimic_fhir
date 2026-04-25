"""
Testes do transformador de ConditionED.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.condition_ed_transformer import (
    ConditionEDTransformationError,
    ConditionEDTransformer,
)


def test_transform_condition_ed_with_full_payload() -> None:
    """
    Deve transformar uma ConditionED completa e consolidar o primeiro código útil.
    """

    transformer = ConditionEDTransformer()
    result = transformer.transform(
        {
            "id": "cond-ed-1",
            "resourceType": "Condition",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "I10",
                        "system": "http://hl7.org/fhir/sid/icd-10-cm",
                        "display": "Essential (primary) hypertension",
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
        "id": "cond-ed-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "condition_code": "I10",
        "condition_code_display": "Essential (primary) hypertension",
        "category_code": "problem-list-item",
        "category_display": "Problem List Item",
    }


def test_transform_condition_ed_without_optional_fields() -> None:
    """
    Deve aceitar ConditionED sem campos opcionais consolidados.
    """

    transformer = ConditionEDTransformer()
    result = transformer.transform({"id": "cond-ed-1", "resourceType": "Condition"})

    assert result == {
        "id": "cond-ed-1",
        "patient_id": None,
        "encounter_id": None,
        "condition_code": None,
        "condition_code_display": None,
        "category_code": None,
        "category_display": None,
    }


def test_transform_condition_ed_without_category() -> None:
    """
    Deve aceitar ConditionED sem `category`.
    """

    transformer = ConditionEDTransformer()
    result = transformer.transform(
        {
            "id": "cond-ed-1",
            "resourceType": "Condition",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "I10"}]},
        }
    )

    assert result["category_code"] is None
    assert result["category_display"] is None


def test_transform_condition_ed_without_code() -> None:
    """
    Deve aceitar ConditionED sem `code`.
    """

    transformer = ConditionEDTransformer()
    result = transformer.transform(
        {
            "id": "cond-ed-1",
            "resourceType": "Condition",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
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
def test_transform_condition_ed_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ConditionEDTransformer()
    payload = {
        "id": "cond-ed-1",
        "resourceType": "Condition",
        "subject": {"reference": "Patient/pat-1"},
        "encounter": {"reference": "Encounter/enc-1"},
    }
    payload[field_name] = {"reference": reference_value}

    with pytest.raises(ConditionEDTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_condition_ed_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas do ConditionED.
    """

    transformer = ConditionEDTransformer()
    result = transformer.transform({"id": "cond-ed-1", "resourceType": "Condition"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "condition_code",
        "condition_code_display",
        "category_code",
        "category_display",
    }
