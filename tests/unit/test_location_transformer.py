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
            "meta": {"profile": ["profile-location"]},
            "physicalType": {
                "coding": [{"system": "sys", "code": "ward", "display": "Ward"}]
            },
            "managingOrganization": {
                "reference": "Organization/ee172322-118b-5716-abbc-18e4c5437e15"
            },
        }
    )

    assert result.location["id"] == "loc-1"
    assert result.location["managing_organization_id"] == "ee172322-118b-5716-abbc-18e4c5437e15"
    assert result.meta_profiles == [{"location_id": "loc-1", "profile": "profile-location"}]
    assert result.physical_type_codings == [
        {"location_id": "loc-1", "system": "sys", "code": "ward", "display": "Ward"}
    ]


def test_transform_location_without_managing_organization() -> None:
    """
    Deve aceitar Location sem organização gestora.
    """

    transformer = LocationTransformer()
    result = transformer.transform({"id": "loc-1", "resourceType": "Location"})

    assert result.location["managing_organization_id"] is None
    assert result.meta_profiles == []
    assert result.physical_type_codings == []


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

