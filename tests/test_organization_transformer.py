"""
Testes da transformação de Organization.
"""

from __future__ import annotations

import unittest

from src.ingestion.transformers.organization_transformer import (
    OrganizationTransformationError,
    OrganizationTransformer,
)


class OrganizationTransformerTests(unittest.TestCase):
    """Cobre a transformação normal e validações mínimas."""

    def test_transform_extracts_rows(self) -> None:
        """Confirma que o transformador extrai todas as listas esperadas."""

        transformer = OrganizationTransformer()
        result = transformer.transform(
            {
                "id": "org-1",
                "resourceType": "Organization",
                "active": True,
                "name": "Hosp",
                "meta": {"profile": ["profile-1"]},
                "identifier": [{"system": "sys", "value": "123"}],
                "type": [{"coding": [{"system": "type-sys", "code": "prov", "display": "Provider"}]}],
            }
        )

        self.assertEqual("org-1", result.organization["id"])
        self.assertEqual(1, len(result.meta_profiles))
        self.assertEqual(1, len(result.identifiers))
        self.assertEqual(1, len(result.type_codings))

    def test_transform_rejects_non_organization(self) -> None:
        """Confirma a rejeição de recursos fora do tipo esperado."""

        transformer = OrganizationTransformer()

        with self.assertRaises(OrganizationTransformationError):
            transformer.transform({"id": "x", "resourceType": "Patient"})


if __name__ == "__main__":
    unittest.main()

