"""
Testes do parser de referências FHIR.
"""

from __future__ import annotations

import pytest

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)


def test_parse_fhir_reference_valid() -> None:
    """
    Deve extrair o identificador quando a referência é válida.
    """

    assert parse_fhir_reference("Organization/abc-123", "Organization") == "abc-123"


@pytest.mark.parametrize(
    ("reference", "expected_resource_type", "expected_exception"),
    [
        ("", "Organization", ValueError),
        ("Organization/abc-123", "", ValueError),
        ("Patient/abc-123", "Organization", FhirReferenceParseError),
        ("Organization", "Organization", FhirReferenceParseError),
    ],
)
def test_parse_fhir_reference_invalid_cases(
    reference: str,
    expected_resource_type: str,
    expected_exception: type[Exception],
) -> None:
    """
    Deve rejeitar referência vazia, tipo incorreto e formato inválido.
    """

    with pytest.raises(expected_exception):
        parse_fhir_reference(reference, expected_resource_type)
