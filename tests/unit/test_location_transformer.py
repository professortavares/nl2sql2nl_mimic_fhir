"""
Testes do transformador de Location.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.location_transformer import (
    LocationTransformationError,
    LocationTransformer,
    parse_managing_organization_reference,
)


def test_parse_managing_organization_reference_valid() -> None:
    """
    Deve extrair o ID de organização a partir da referência FHIR.
    """

    assert parse_managing_organization_reference(
        "Organization/ee172322-118b-5716-abbc-18e4c5437e15"
    ) == "ee172322-118b-5716-abbc-18e4c5437e15"


def test_transform_location_with_managing_organization() -> None:
    """
    Deve transformar um Location válido com referência de organização.
    """

    transformer = LocationTransformer()
    result = transformer.transform(
        {
            "id": "loc-1",
            "resourceType": "Location",
            "name": "Emergency",
            "status": "active",
            "managingOrganization": {
                "reference": "Organization/ee172322-118b-5716-abbc-18e4c5437e15"
            },
        }
    )

    assert result == {
        "id": "loc-1",
        "name": "Emergency",
        "managing_organization_id": "ee172322-118b-5716-abbc-18e4c5437e15",
    }


def test_transform_location_without_managing_organization() -> None:
    """
    Deve aceitar Location sem organização gestora.
    """

    transformer = LocationTransformer()
    result = transformer.transform({"id": "loc-1", "resourceType": "Location"})

    assert result == {"id": "loc-1", "name": None, "managing_organization_id": None}


def test_transform_location_rejects_invalid_reference() -> None:
    """
    Deve rejeitar referência FHIR malformada.
    """

    transformer = LocationTransformer()

    with pytest.raises(LocationTransformationError):
        transformer.transform(
            {
                "id": "loc-1",
                "resourceType": "Location",
                "managingOrganization": {"reference": "Patient/123"},
            }
        )


def test_transform_location_does_not_include_removed_fields() -> None:
    """
    Deve retornar somente os campos simplificados.
    """

    transformer = LocationTransformer()
    result = transformer.transform(
        {
            "id": "loc-1",
            "resourceType": "Location",
            "status": "active",
            "name": "Ward",
        }
    )

    assert set(result.keys()) == {"id", "name", "managing_organization_id"}
