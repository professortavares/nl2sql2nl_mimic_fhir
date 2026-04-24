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
    assert parse_fhir_reference("Patient/abc-123", "Patient") == "abc-123"
    assert parse_fhir_reference("Location/abc-123", "Location") == "abc-123"
    assert parse_fhir_reference("Encounter/abc-123", "Encounter") == "abc-123"
    assert parse_fhir_reference("Medication/abc-123", "Medication") == "abc-123"
    assert parse_fhir_reference("Specimen/abc-123", "Specimen") == "abc-123"


@pytest.mark.parametrize(
    ("reference", "expected_resource_type", "expected_exception"),
    [
        ("", "Organization", ValueError),
        ("Organization/abc-123", "", ValueError),
        ("Patient/abc-123", "Organization", FhirReferenceParseError),
        ("Organization", "Organization", FhirReferenceParseError),
        ("Location/abc-123", "Patient", FhirReferenceParseError),
        ("Encounter/abc-123", "Organization", FhirReferenceParseError),
        (None, "Organization", TypeError),
        ("Organization/abc-123", None, TypeError),
    ],
)
def test_parse_fhir_reference_invalid_cases(
    reference: object,
    expected_resource_type: object,
    expected_exception: type[Exception],
) -> None:
    """
    Deve rejeitar referência vazia, tipo incorreto e formato inválido.
    """

    with pytest.raises(expected_exception):
        parse_fhir_reference(reference, expected_resource_type)
