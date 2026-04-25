"""
Testes do transformador de MedicationMix.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.medication_mix_transformer import (
    MedicationMixTransformationError,
    MedicationMixTransformer,
)


def test_transform_medication_mix_with_full_payload() -> None:
    """
    Deve transformar um MedicationMix completo com múltiplos ingredientes.
    """

    transformer = MedicationMixTransformer()
    result = transformer.transform(
        {
            "id": "mix-1",
            "resourceType": "Medication",
            "status": "active",
            "identifier": [
                {"value": "", "system": "http://example.invalid"},
                {
                    "value": "Meropenem--MERO1I--63323050831_0.9% Sodium Chloride (Mini Bag Plus)--NS/MBP100I--00338055318",
                    "system": "http://mimic.mit.edu/fhir/mimic/identifier/medication-mix",
                },
            ],
            "ingredient": [
                {"itemReference": {"reference": "Medication/f84ef276-2687-5ea5-bef5-c66fd7c158cd"}},
                {"itemReference": {"reference": "Medication/7c46a14c-af29-58d1-9e4d-6a064c39d856"}},
            ],
            "meta": {"profile": ["ignored"]},
            "text": {"div": "<div>ignored</div>", "status": "generated"},
        }
    )

    assert result.medication_mix == {
        "id": "mix-1",
        "status": "active",
        "identifier": "Meropenem--MERO1I--63323050831_0.9% Sodium Chloride (Mini Bag Plus)--NS/MBP100I--00338055318",
    }
    assert result.medication_mix_ingredients == [
        {
            "medication_mix_id": "mix-1",
            "medication_id": "f84ef276-2687-5ea5-bef5-c66fd7c158cd",
        },
        {
            "medication_mix_id": "mix-1",
            "medication_id": "7c46a14c-af29-58d1-9e4d-6a064c39d856",
        },
    ]


def test_transform_medication_mix_without_identifier() -> None:
    """
    Deve aceitar MedicationMix sem identificador útil.
    """

    transformer = MedicationMixTransformer()
    result = transformer.transform({"id": "mix-1", "resourceType": "Medication", "status": "active"})

    assert result.medication_mix == {
        "id": "mix-1",
        "status": "active",
        "identifier": None,
    }
    assert result.medication_mix_ingredients == []


def test_transform_medication_mix_without_ingredient() -> None:
    """
    Deve aceitar MedicationMix sem ingredientes.
    """

    transformer = MedicationMixTransformer()
    result = transformer.transform(
        {
            "id": "mix-1",
            "resourceType": "Medication",
            "status": "active",
            "identifier": [{"value": "mix-1"}],
        }
    )

    assert result.medication_mix_ingredients == []


def test_transform_medication_mix_rejects_invalid_ingredient_reference() -> None:
    """
    Deve rejeitar referência inválida em `ingredient[*].itemReference.reference`.
    """

    transformer = MedicationMixTransformer()

    with pytest.raises(MedicationMixTransformationError):
        transformer.transform(
            {
                "id": "mix-1",
                "resourceType": "Medication",
                "ingredient": [{"itemReference": {"reference": "Patient/pat-1"}}],
            }
        )


def test_transform_medication_mix_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as estruturas simplificadas do MedicationMix.
    """

    transformer = MedicationMixTransformer()
    result = transformer.transform({"id": "mix-1", "resourceType": "Medication"})

    assert set(result.medication_mix.keys()) == {"id", "status", "identifier"}
    assert result.medication_mix_ingredients == []
