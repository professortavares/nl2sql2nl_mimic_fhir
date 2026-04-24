"""
Transformação de recursos FHIR `Medication` para a tabela simplificada.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.ingestion.utils.selection import (
    first_non_empty_text,
    first_text_from_mappings,
    first_text_from_mappings_matching,
)

_MEDICATION_RESOURCE_TYPE = "Medication"
_NDC_SYSTEM_FRAGMENT = "mimic-medication-ndc"
_FORMULARY_DRUG_CD_SYSTEM_FRAGMENT = "mimic-medication-formulary-drug-cd"
_NAME_SYSTEM_FRAGMENT = "mimic-medication-name"


class MedicationTransformationError(ValueError):
    """Indica que um recurso Medication não passou na validação mínima."""


class MedicationTransformer:
    """
    Converte recursos FHIR Medication em um dicionário relacional enxuto.

    A consolidação segue a regra de primeiro valor não vazio e válido encontrado
    em cada lista relevante. Não são preservados `resourceType` nem `meta.profile`.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Medication.

        Retorno:
        -------
        dict[str, Any]
            Registro pronto para persistência na tabela `medication`.

        Exceções:
        --------
        TypeError
            Quando a entrada não é um mapeamento.
        MedicationTransformationError
            Quando a validação mínima falha.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _MEDICATION_RESOURCE_TYPE:
            raise MedicationTransformationError(
                f"resourceType inválido para Medication: {resource.get('resourceType')!r}"
            )

        medication_id = first_non_empty_text(resource.get("id"))
        if medication_id is None:
            raise MedicationTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": medication_id,
            "code": self._extract_first_code(resource.get("code")),
            "code_system": self._extract_first_code_system(resource.get("code")),
            "status": first_non_empty_text(resource.get("status")),
            "ndc": self._extract_identifier_by_system(resource.get("identifier"), _NDC_SYSTEM_FRAGMENT),
            "formulary_drug_cd": self._extract_identifier_by_system(
                resource.get("identifier"),
                _FORMULARY_DRUG_CD_SYSTEM_FRAGMENT,
            ),
            "name": self._extract_identifier_by_system(resource.get("identifier"), _NAME_SYSTEM_FRAGMENT),
        }

    def _extract_first_code(self, code_container: Any) -> str | None:
        """
        Extrai o primeiro `code.coding[*].code` válido encontrado.
        """

        if not isinstance(code_container, Mapping):
            return None
        return first_text_from_mappings(code_container.get("coding"), "code")

    def _extract_first_code_system(self, code_container: Any) -> str | None:
        """
        Extrai o primeiro `code.coding[*].system` válido encontrado.
        """

        if not isinstance(code_container, Mapping):
            return None
        return first_text_from_mappings(code_container.get("coding"), "system")

    def _extract_identifier_by_system(self, identifiers: Any, system_fragment: str) -> str | None:
        """
        Extrai o primeiro `identifier[*].value` cujo `system` contenha o fragmento informado.
        """

        if not isinstance(system_fragment, str) or not system_fragment.strip():
            raise TypeError("O fragmento de system deve ser uma string não vazia.")

        normalized_fragment = system_fragment.strip().lower()
        return first_text_from_mappings_matching(
            identifiers,
            "value",
            lambda item: self._system_matches(item.get("system"), normalized_fragment),
        )

    def _system_matches(self, system: Any, normalized_fragment: str) -> bool:
        """
        Verifica se o `system` informado contém o fragmento esperado.
        """

        normalized_system = first_non_empty_text(system)
        if normalized_system is None:
            return False
        return normalized_fragment in normalized_system.lower()
