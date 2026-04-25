"""
Testes do transformador de Medication.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.medication_transformer import (
    MedicationTransformationError,
    MedicationTransformer,
)


def test_transform_medication_with_full_payload() -> None:
    """
    Deve transformar um Medication completo e mapear os systems corretos.
    """

    transformer = MedicationTransformer()
    result = transformer.transform(
        {
            "id": "med-1",
            "resourceType": "Medication",
            "status": "active",
            "code": {
                "coding": [
                    {"code": "", "system": ""},
                    {
                        "code": "51079030020",
                        "system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-medication-ndc",
                    },
                ]
            },
            "meta": {"profile": ["ignored"]},
            "identifier": [
                {
                    "value": "51079030020",
                    "system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-medication-ndc",
                },
                {
                    "value": "CATA2",
                    "system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-medication-formulary-drug-cd",
                },
                {
                    "value": "CloniDINE",
                    "system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/mimic-medication-name",
                },
            ],
        }
    )

    assert result == {
        "id": "med-1",
        "code": "51079030020",
        "status": "active",
        "ndc": "51079030020",
        "formulary_drug_cd": "CATA2",
        "name": "CloniDINE",
    }


def test_transform_medication_with_optional_fields_missing() -> None:
    """
    Deve aceitar Medication sem identificadores opcionais.
    """

    transformer = MedicationTransformer()
    result = transformer.transform({"id": "med-1", "resourceType": "Medication"})

    assert result == {
        "id": "med-1",
        "code": None,
        "status": None,
        "ndc": None,
        "formulary_drug_cd": None,
        "name": None,
    }


def test_transform_medication_with_empty_coding() -> None:
    """
    Deve aceitar `code.coding` vazio sem inventar valores.
    """

    transformer = MedicationTransformer()
    result = transformer.transform(
        {
            "id": "med-1",
            "resourceType": "Medication",
            "code": {"coding": []},
            "identifier": [],
        }
    )

    assert result["code"] is None


def test_transform_medication_rejects_invalid_resource_type() -> None:
    """
    Deve rejeitar recurso com tipo inválido.
    """

    transformer = MedicationTransformer()

    with pytest.raises(MedicationTransformationError):
        transformer.transform({"id": "med-1", "resourceType": "Patient"})


def test_transform_medication_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas definidas para Medication.
    """

    transformer = MedicationTransformer()
    result = transformer.transform({"id": "med-1", "resourceType": "Medication"})

    assert set(result.keys()) == {
        "id",
        "code",
        "status",
        "ndc",
        "formulary_drug_cd",
        "name",
    }
