"""
Testes do transformador de Organization.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.organization_transformer import (
    OrganizationTransformationError,
    OrganizationTransformer,
)


def test_transform_organization_with_optional_fields() -> None:
    """
    Deve transformar um registro válido e ignorar campos extras.
    """

    transformer = OrganizationTransformer()
    result = transformer.transform(
        {
            "id": "org-1",
            "resourceType": "Organization",
            "active": True,
            "name": "Beth Israel",
            "identifier": [{"value": "ignored"}],
            "type": [{"coding": [{"code": "prov"}]}],
        }
    )

    assert result == {"id": "org-1", "name": "Beth Israel"}


def test_transform_organization_with_optional_fields_missing() -> None:
    """
    Deve aceitar campos opcionais ausentes.
    """

    transformer = OrganizationTransformer()
    result = transformer.transform({"id": "org-1", "resourceType": "Organization"})

    assert result == {"id": "org-1", "name": None}


def test_transform_organization_rejects_invalid_resource_type() -> None:
    """
    Deve rejeitar recurso com tipo inválido.
    """

    transformer = OrganizationTransformer()

    with pytest.raises(OrganizationTransformationError):
        transformer.transform({"id": "org-1", "resourceType": "Patient"})
