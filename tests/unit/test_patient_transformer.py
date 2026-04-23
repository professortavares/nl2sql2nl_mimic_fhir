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
            "name": [{"family": ""}, {"family": "Doe"}],
            "identifier": [{"value": ""}, {"value": "123"}],
            "maritalStatus": {"coding": [{"code": ""}, {"code": "S"}]},
            "extension": [
                {
                    "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                    "extension": [{"url": "text", "valueString": "White"}],
                },
                {
                    "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
                    "extension": [{"url": "text", "valueString": "Not Hispanic or Latino"}],
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

    assert result == {
        "id": "pat-1",
        "gender": "female",
        "birth_date": "1980-01-01",
        "name": "Doe",
        "identifier": "123",
        "marital_status_coding": "S",
        "race": "White",
        "ethnicity": "Not Hispanic or Latino",
        "birthsex": "F",
        "managing_organization_id": "ee172322-118b-5716-abbc-18e4c5437e15",
    }


def test_transform_patient_with_optional_fields_missing() -> None:
    """
    Deve aceitar campos opcionais e extensões ausentes.
    """

    transformer = PatientTransformer()
    result = transformer.transform({"id": "pat-1", "resourceType": "Patient"})

    assert result == {
        "id": "pat-1",
        "gender": None,
        "birth_date": None,
        "name": None,
        "identifier": None,
        "marital_status_coding": None,
        "race": None,
        "ethnicity": None,
        "birthsex": None,
        "managing_organization_id": None,
    }


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


def test_transform_patient_returns_only_simplified_columns() -> None:
    """
    Deve retornar somente as colunas simplificadas definidas para a fase atual.
    """

    transformer = PatientTransformer()
    result = transformer.transform({"id": "pat-1", "resourceType": "Patient"})

    assert set(result.keys()) == {
        "id",
        "gender",
        "birth_date",
        "name",
        "identifier",
        "marital_status_coding",
        "race",
        "ethnicity",
        "birthsex",
        "managing_organization_id",
    }
