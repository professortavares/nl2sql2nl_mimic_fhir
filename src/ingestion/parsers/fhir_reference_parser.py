"""
Funções para parse de referências FHIR em formato `ResourceType/id`.
"""

from __future__ import annotations

import re

_FHIR_REFERENCE_PATTERN = re.compile(r"^(?P<resource_type>[A-Za-z][A-Za-z0-9]*)/(?P<resource_id>[A-Za-z0-9\-\.]{1,64})$")


class FhirReferenceParseError(ValueError):
    """Indica que uma referência FHIR não está no formato esperado."""


def parse_fhir_reference(reference: str, expected_resource_type: str) -> str:
    """
    Extrai o identificador de uma referência FHIR do tipo `ResourceType/id`.

    Parâmetros:
    ----------
    reference : str
        Referência FHIR no formato `ResourceType/id`.
    expected_resource_type : str
        Tipo de recurso esperado, por exemplo `Organization`.

    Retorno:
    -------
    str
        Identificador extraído da referência.

    Exceções:
    --------
    TypeError
        Quando os parâmetros não são strings.
    ValueError
        Quando a referência está vazia, o tipo é diferente do esperado ou o
        formato é inválido.

    Exemplos de uso:
    ----------------
    parse_fhir_reference("Organization/abc123", "Organization")
    """

    if not isinstance(reference, str):
        raise TypeError("A referência FHIR deve ser uma string.")
    if not isinstance(expected_resource_type, str):
        raise TypeError("O tipo esperado de recurso deve ser uma string.")

    normalized_reference = reference.strip()
    normalized_expected_type = expected_resource_type.strip()
    if not normalized_reference:
        raise ValueError("A referência FHIR não pode ser vazia.")
    if not normalized_expected_type:
        raise ValueError("O tipo esperado de recurso não pode ser vazio.")

    match = _FHIR_REFERENCE_PATTERN.fullmatch(normalized_reference)
    if match is None:
        raise FhirReferenceParseError(
            "A referência FHIR deve seguir o formato 'ResourceType/id'."
        )

    parsed_resource_type = match.group("resource_type")
    resource_id = match.group("resource_id")
    if parsed_resource_type != normalized_expected_type:
        raise FhirReferenceParseError(
            f"Tipo de referência inválido: esperado {normalized_expected_type!r}, "
            f"mas encontrado {parsed_resource_type!r}."
        )
    return resource_id

