"""
Transformação de recursos FHIR `Location` para a tabela simplificada.
"""

from __future__ import annotations

from typing import Any, Mapping

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import first_non_empty_text

_EXPECTED_REFERENCE_TYPE = "Organization"


class LocationTransformationError(ValueError):
    """Indica que um recurso Location não passou na validação mínima."""


def parse_managing_organization_reference(reference: str) -> str:
    """
    Extrai o identificador da organização a partir de uma referência FHIR.

    Parâmetros:
    ----------
    reference : str
        Referência no formato `Organization/<id>`.

    Retorno:
    -------
    str
        Identificador da organização referenciada.

    Exceções:
    --------
    TypeError
        Quando `reference` não é string.
    ValueError
        Quando o formato não corresponde ao padrão esperado.
    """

    return parse_fhir_reference(reference, _EXPECTED_REFERENCE_TYPE)


class LocationTransformer:
    """
    Converte recursos FHIR Location em um dicionário relacional enxuto.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Location.

        Retorno:
        -------
        dict[str, Any]
            Registro pronto para persistência na tabela `location`.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != "Location":
            raise LocationTransformationError(
                f"resourceType inválido para Location: {resource.get('resourceType')!r}"
            )

        location_id = first_non_empty_text(resource.get("id"))
        if location_id is None:
            raise LocationTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        managing_organization_id = self._extract_managing_organization_id(
            resource.get("managingOrganization")
        )

        return {
            "id": location_id,
            "name": first_non_empty_text(resource.get("name")),
            "managing_organization_id": managing_organization_id,
        }

    def _extract_managing_organization_id(self, managing_organization: Any) -> str | None:
        """
        Extrai o identificador da organização gestora.
        """

        if managing_organization is None:
            return None
        if not isinstance(managing_organization, Mapping):
            raise LocationTransformationError(
                "O campo 'managingOrganization' deve ser um objeto FHIR quando presente."
            )
        reference = managing_organization.get("reference")
        if reference is None:
            raise LocationTransformationError(
                "O campo 'managingOrganization.reference' é obrigatório quando a organização gestora está presente."
            )
        try:
            return parse_managing_organization_reference(reference)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise LocationTransformationError(str(exc)) from exc
