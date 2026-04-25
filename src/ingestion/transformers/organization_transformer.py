"""
Transformação de recursos FHIR `Organization` para a tabela simplificada.
"""

from __future__ import annotations

from typing import Any, Mapping

from src.ingestion.utils.selection import first_non_empty_text


class OrganizationTransformationError(ValueError):
    """Indica que um recurso Organization não passou na validação mínima."""


class OrganizationTransformer:
    """
    Converte recursos FHIR Organization em um dicionário relacional enxuto.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Organization.

        Retorno:
        -------
        dict[str, Any]
            Registro pronto para persistência na tabela `organization`.

        Exceções:
        --------
        TypeError
            Quando a entrada não é mapeável.
        OrganizationTransformationError
            Quando a validação mínima falha.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != "Organization":
            raise OrganizationTransformationError(
                f"resourceType inválido para Organization: {resource.get('resourceType')!r}"
            )

        organization_id = first_non_empty_text(resource.get("id"))
        if organization_id is None:
            raise OrganizationTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": organization_id,
            "name": first_non_empty_text(resource.get("name")),
        }
