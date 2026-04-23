"""
Testes da transformação de Location.
"""

from __future__ import annotations

import unittest

from src.ingestion.transformers.location_transformer import (
    LocationTransformationError,
    LocationTransformer,
    parse_managing_organization_reference,
)


class LocationTransformerTests(unittest.TestCase):
    """Cobre parse de referência e transformação de Location."""

    def test_parse_managing_organization_reference(self) -> None:
        """Confirma o parse correto da referência FHIR."""

        organization_id = parse_managing_organization_reference(
            "Organization/ee172322-118b-5716-abbc-18e4c5437e15"
        )

        self.assertEqual("ee172322-118b-5716-abbc-18e4c5437e15", organization_id)

    def test_parse_managing_organization_reference_rejects_invalid_value(self) -> None:
        """Confirma a rejeição de referências fora do padrão."""

        with self.assertRaises(ValueError):
            parse_managing_organization_reference("Patient/123")

    def test_transform_extracts_location_rows(self) -> None:
        """Confirma que a transformação extrai os campos esperados."""

        transformer = LocationTransformer()
        result = transformer.transform(
            {
                "id": "loc-1",
                "resourceType": "Location",
                "name": "Ward 1",
                "status": "active",
                "meta": {"profile": ["profile-location"]},
                "physicalType": {
                    "coding": [
                        {"system": "sys", "code": "ward", "display": "Ward"},
                    ]
                },
                "managingOrganization": {
                    "reference": "Organization/ee172322-118b-5716-abbc-18e4c5437e15"
                },
            }
        )

        self.assertEqual("loc-1", result.location["id"])
        self.assertEqual(
            "ee172322-118b-5716-abbc-18e4c5437e15",
            result.location["managing_organization_id"],
        )
        self.assertEqual(1, len(result.meta_profiles))
        self.assertEqual(1, len(result.physical_type_codings))

    def test_transform_rejects_invalid_reference(self) -> None:
        """Confirma que referências inválidas falham de forma controlada."""

        transformer = LocationTransformer()

        with self.assertRaises(LocationTransformationError):
            transformer.transform(
                {
                    "id": "loc-1",
                    "resourceType": "Location",
                    "managingOrganization": {"reference": "invalid"},
                }
            )


if __name__ == "__main__":
    unittest.main()

