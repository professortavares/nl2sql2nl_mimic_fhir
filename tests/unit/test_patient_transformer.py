"""
Testes do transformador de Patient.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.patient_transformer import (
    PatientTransformationError,
    PatientTransformer,
)


def test_transform_patient_with_full_payload() -> None:
    """
    Deve transformar um Patient com campos principais e extensões.
    """

    transformer = PatientTransformer()
    result = transformer.transform(
        {
            "id": "pat-1",
            "resourceType": "Patient",
            "gender": "female",
            "birthDate": "1980-01-01",
            "meta": {"profile": ["profile-patient"]},
            "name": [{"use": "official", "family": "Doe"}],
            "identifier": [{"system": "sys", "value": "123"}],
            "communication": [{"language": {"coding": [{"system": "lang", "code": "en"}]}}],
            "maritalStatus": {"coding": [{"system": "marital", "code": "S"}]},
            "extension": [
                {
                    "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": "urn:oid:1",
                                "code": "2106-3",
                                "display": "White",
                            },
                        },
                        {"url": "text", "valueString": "White"},
                    ],
                },
                {
                    "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": "urn:oid:1",
                                "code": "2186-5",
                                "display": "Not Hispanic or Latino",
                            },
                        },
                        {"url": "text", "valueString": "Not Hispanic or Latino"},
                    ],
                },
                {
                    "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex",
                    "valueCode": "F",
                },
            ],
            "managingOrganization": {
                "reference": "Organization/ee172322-118b-5716-abbc-18e4c5437e15"
            },
        }
    )

    assert result.patient["id"] == "pat-1"
    assert result.patient["gender"] == "female"
    assert result.patient["birth_date"] == "1980-01-01"
    assert result.patient["managing_organization_id"] == "ee172322-118b-5716-abbc-18e4c5437e15"
    assert result.meta_profiles == [{"patient_id": "pat-1", "profile": "profile-patient"}]
    assert result.names == [{"patient_id": "pat-1", "use": "official", "family": "Doe"}]
    assert result.identifiers == [{"patient_id": "pat-1", "system": "sys", "value": "123"}]
    assert result.communication_language_codings == [
        {"patient_id": "pat-1", "system": "lang", "code": "en"}
    ]
    assert result.marital_status_codings == [
        {"patient_id": "pat-1", "system": "marital", "code": "S"}
    ]
    assert result.race == [
        {
            "patient_id": "pat-1",
            "omb_category_system": "urn:oid:1",
            "omb_category_code": "2106-3",
            "omb_category_display": "White",
            "text": "White",
        }
    ]
    assert result.ethnicity == [
        {
            "patient_id": "pat-1",
            "omb_category_system": "urn:oid:1",
            "omb_category_code": "2186-5",
            "omb_category_display": "Not Hispanic or Latino",
            "text": "Not Hispanic or Latino",
        }
    ]
    assert result.birthsex == [{"patient_id": "pat-1", "value_code": "F"}]


def test_transform_patient_with_optional_fields_missing() -> None:
    """
    Deve aceitar campos opcionais e extensões ausentes.
    """

    transformer = PatientTransformer()
    result = transformer.transform({"id": "pat-1", "resourceType": "Patient"})

    assert result.patient["gender"] is None
    assert result.patient["birth_date"] is None
    assert result.patient["managing_organization_id"] is None
    assert result.meta_profiles == []
    assert result.names == []
    assert result.identifiers == []
    assert result.communication_language_codings == []
    assert result.marital_status_codings == []
    assert result.race == []
    assert result.ethnicity == []
    assert result.birthsex == []


def test_transform_patient_rejects_invalid_reference() -> None:
    """
    Deve rejeitar referência FHIR inválida para a organização gestora.
    """

    transformer = PatientTransformer()

    with pytest.raises(PatientTransformationError):
        transformer.transform(
            {
                "id": "pat-1",
                "resourceType": "Patient",
                "managingOrganization": {"reference": "Location/123"},
            }
        )

