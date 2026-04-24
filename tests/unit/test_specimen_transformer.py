"""
Testes do transformador de Specimen.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.specimen_transformer import (
    SpecimenTransformationError,
    SpecimenTransformer,
)


def test_transform_specimen_with_full_payload() -> None:
    """
    Deve transformar um Specimen completo e consolidar os primeiros valores úteis.
    """

    transformer = SpecimenTransformer()
    result = transformer.transform(
        {
            "id": "spec-1",
            "resourceType": "Specimen",
            "subject": {"reference": "Patient/pat-1"},
            "type": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "BLD",
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0487",
                        "display": "Blood",
                    },
                ]
            },
            "collection": {"collectedDateTime": "2024-01-01T08:00:00Z"},
            "identifier": [
                {"value": "", "system": "ignored"},
                {"value": "spec-identifier", "system": "http://example.invalid"},
            ],
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "spec-1",
        "patient_id": "pat-1",
        "specimen_type_code": "BLD",
        "specimen_type_system": "http://terminology.hl7.org/CodeSystem/v2-0487",
        "specimen_type_display": "Blood",
        "collected_at": "2024-01-01T08:00:00Z",
        "identifier": "spec-identifier",
    }


def test_transform_specimen_without_optional_fields() -> None:
    """
    Deve aceitar Specimen sem campos opcionais consolidados.
    """

    transformer = SpecimenTransformer()
    result = transformer.transform({"id": "spec-1", "resourceType": "Specimen"})

    assert result == {
        "id": "spec-1",
        "patient_id": None,
        "specimen_type_code": None,
        "specimen_type_system": None,
        "specimen_type_display": None,
        "collected_at": None,
        "identifier": None,
    }


def test_transform_specimen_without_collection() -> None:
    """
    Deve aceitar Specimen sem `collection`.
    """

    transformer = SpecimenTransformer()
    result = transformer.transform({"id": "spec-1", "resourceType": "Specimen", "subject": {"reference": "Patient/pat-1"}})

    assert result["collected_at"] is None


def test_transform_specimen_without_type() -> None:
    """
    Deve aceitar Specimen sem `type`.
    """

    transformer = SpecimenTransformer()
    result = transformer.transform({"id": "spec-1", "resourceType": "Specimen", "subject": {"reference": "Patient/pat-1"}})

    assert result["specimen_type_code"] is None
    assert result["specimen_type_system"] is None
    assert result["specimen_type_display"] is None


def test_transform_specimen_rejects_invalid_subject_reference() -> None:
    """
    Deve rejeitar referência FHIR inválida em `subject.reference`.
    """

    transformer = SpecimenTransformer()

    with pytest.raises(SpecimenTransformationError, match="Tipo de referência inválido"):
        transformer.transform(
            {
                "id": "spec-1",
                "resourceType": "Specimen",
                "subject": {"reference": "Encounter/enc-1"},
            }
        )


def test_transform_specimen_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas do Specimen.
    """

    transformer = SpecimenTransformer()
    result = transformer.transform({"id": "spec-1", "resourceType": "Specimen"})

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "specimen_type_code",
        "specimen_type_system",
        "specimen_type_display",
        "collected_at",
        "identifier",
    }
