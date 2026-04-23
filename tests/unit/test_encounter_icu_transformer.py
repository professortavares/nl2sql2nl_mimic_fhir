"""
Testes do transformador de EncounterICU.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.encounter_icu_transformer import (
    EncounterICUTransformationError,
    EncounterICUTransformer,
)


def test_transform_encounter_icu_with_full_payload() -> None:
    """
    Deve transformar um EncounterICU completo.
    """

    transformer = EncounterICUTransformer()
    result = transformer.transform(
        {
            "id": "icu-1",
            "resourceType": "Encounter",
            "status": "finished",
            "class": {"code": "ICU", "system": "ignored"},
            "partOf": {"reference": "Encounter/enc-1"},
            "period": {"start": "2024-01-01T10:00:00Z", "end": "2024-01-01T12:00:00Z"},
            "subject": {"reference": "Patient/pat-1"},
            "location": [
                {
                    "location": {"reference": "Location/loc-1"},
                    "period": {"start": "2024-01-01T10:00:00Z", "end": "2024-01-01T11:00:00Z"},
                },
                {
                    "location": {"reference": "Location/loc-2"},
                    "period": {"start": "2024-01-01T11:00:00Z", "end": "2024-01-01T12:00:00Z"},
                },
            ],
            "identifier": [
                {"value": ""},
                {"value": "icu-identifier", "system": "http://mimic.mit.edu/fhir/mimic/identifier/icu"},
            ],
        }
    )

    assert result.encounter_icu == {
        "id": "icu-1",
        "encounter_id": "enc-1",
        "patient_id": "pat-1",
        "status": "finished",
        "class_code": "ICU",
        "start_date": "2024-01-01T10:00:00Z",
        "end_date": "2024-01-01T12:00:00Z",
        "identifier": "icu-identifier",
    }
    assert result.encounter_icu_locations == [
        {
            "encounter_icu_id": "icu-1",
            "location_id": "loc-1",
            "start_date": "2024-01-01T10:00:00Z",
            "end_date": "2024-01-01T11:00:00Z",
        },
        {
            "encounter_icu_id": "icu-1",
            "location_id": "loc-2",
            "start_date": "2024-01-01T11:00:00Z",
            "end_date": "2024-01-01T12:00:00Z",
        },
    ]


def test_transform_encounter_icu_without_partof() -> None:
    """
    Deve aceitar EncounterICU sem `partOf`.
    """

    transformer = EncounterICUTransformer()
    result = transformer.transform(
        {
            "id": "icu-1",
            "resourceType": "Encounter",
            "subject": {"reference": "Patient/pat-1"},
        }
    )

    assert result.encounter_icu["encounter_id"] is None


def test_transform_encounter_icu_without_subject() -> None:
    """
    Deve aceitar EncounterICU sem `subject`.
    """

    transformer = EncounterICUTransformer()
    result = transformer.transform(
        {
            "id": "icu-1",
            "resourceType": "Encounter",
            "partOf": {"reference": "Encounter/enc-1"},
        }
    )

    assert result.encounter_icu["patient_id"] is None


def test_transform_encounter_icu_without_location() -> None:
    """
    Deve aceitar EncounterICU sem `location`.
    """

    transformer = EncounterICUTransformer()
    result = transformer.transform(
        {
            "id": "icu-1",
            "resourceType": "Encounter",
            "partOf": {"reference": "Encounter/enc-1"},
            "subject": {"reference": "Patient/pat-1"},
        }
    )

    assert result.encounter_icu_locations == []


def test_transform_encounter_icu_rejects_invalid_partof_reference() -> None:
    """
    Deve rejeitar referência inválida em `partOf`.
    """

    transformer = EncounterICUTransformer()

    with pytest.raises(EncounterICUTransformationError):
        transformer.transform(
            {
                "id": "icu-1",
                "resourceType": "Encounter",
                "partOf": {"reference": "Patient/pat-1"},
                "subject": {"reference": "Patient/pat-1"},
            }
        )


def test_transform_encounter_icu_rejects_invalid_subject_reference() -> None:
    """
    Deve rejeitar referência inválida em `subject`.
    """

    transformer = EncounterICUTransformer()

    with pytest.raises(EncounterICUTransformationError):
        transformer.transform(
            {
                "id": "icu-1",
                "resourceType": "Encounter",
                "partOf": {"reference": "Encounter/enc-1"},
                "subject": {"reference": "Encounter/enc-1"},
            }
        )


def test_transform_encounter_icu_rejects_invalid_location_reference() -> None:
    """
    Deve rejeitar referência inválida em `location`.
    """

    transformer = EncounterICUTransformer()

    with pytest.raises(EncounterICUTransformationError):
        transformer.transform(
            {
                "id": "icu-1",
                "resourceType": "Encounter",
                "partOf": {"reference": "Encounter/enc-1"},
                "subject": {"reference": "Patient/pat-1"},
                "location": [{"location": {"reference": "Encounter/enc-1"}}],
            }
        )


def test_transform_encounter_icu_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as colunas simplificadas definidas para EncounterICU.
    """

    transformer = EncounterICUTransformer()
    result = transformer.transform(
        {
            "id": "icu-1",
            "resourceType": "Encounter",
            "partOf": {"reference": "Encounter/enc-1"},
            "subject": {"reference": "Patient/pat-1"},
        }
    )

    assert set(result.encounter_icu.keys()) == {
        "id",
        "encounter_id",
        "patient_id",
        "status",
        "class_code",
        "start_date",
        "end_date",
        "identifier",
    }

