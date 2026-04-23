"""
Testes do transformador de Organization.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.organization_transformer import (
    OrganizationTransformationError,
    OrganizationTransformer,
)


def test_transform_organization_with_lists() -> None:
    """
    Deve transformar um registro válido com listas preenchidas.
    """

    transformer = OrganizationTransformer()
    result = transformer.transform(
        {
            "id": "org-1",
            "resourceType": "Organization",
            "active": True,
            "name": "Hospital",
            "meta": {"profile": ["profile-1"]},
            "identifier": [{"system": "sys", "value": "123"}],
            "type": [{"coding": [{"system": "type-sys", "code": "prov", "display": "Provider"}]}],
        }
    )

    assert result.organization["id"] == "org-1"
    assert result.organization["resource_type"] == "Organization"
    assert result.organization["active"] is True
    assert result.organization["name"] == "Hospital"
    assert result.meta_profiles == [{"organization_id": "org-1", "profile": "profile-1"}]
    assert result.identifiers == [{"organization_id": "org-1", "system": "sys", "value": "123"}]
    assert result.type_codings == [
        {
            "organization_id": "org-1",
            "system": "type-sys",
            "code": "prov",
            "display": "Provider",
        }
    ]


def test_transform_organization_with_optional_fields_missing() -> None:
    """
    Deve aceitar campos opcionais ausentes.
    """

    transformer = OrganizationTransformer()
    result = transformer.transform({"id": "org-1", "resourceType": "Organization"})

    assert result.organization["active"] is None
    assert result.organization["name"] is None
    assert result.meta_profiles == []
    assert result.identifiers == []
    assert result.type_codings == []


def test_transform_organization_rejects_invalid_resource_type() -> None:
    """
    Deve rejeitar recurso com tipo inválido.
    """

    transformer = OrganizationTransformer()

    with pytest.raises(OrganizationTransformationError):
        transformer.transform({"id": "org-1", "resourceType": "Patient"})

