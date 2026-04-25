"""
Transformação de recursos FHIR `Condition` da camada ED para a modelagem simplificada.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import first_non_empty_text, first_text_from_mappings

_RESOURCE_TYPE = "Condition"
_PATIENT_REFERENCE_TYPE = "Patient"
_ENCOUNTER_REFERENCE_TYPE = "Encounter"


class ConditionEDTransformationError(ValueError):
    """Indica que um recurso ConditionED não passou na validação mínima."""


class ConditionEDTransformer:
    """
    Converte recursos FHIR Condition em um dicionário relacional enxuto.

    A transformação consolida apenas o primeiro valor não vazio e válido
    encontrado em `code.coding[*]` e `category[*].coding[*]`.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Condition.

        Retorno:
        -------
        dict[str, Any]
            Registro pronto para persistência na tabela `condition_ed`.

        Exceções:
        --------
        TypeError
            Quando a entrada não é um mapeamento.
        ConditionEDTransformationError
            Quando a validação mínima falha.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise ConditionEDTransformationError(
                f"resourceType inválido para ConditionED: {resource.get('resourceType')!r}"
            )

        condition_id = first_non_empty_text(resource.get("id"))
        if condition_id is None:
            raise ConditionEDTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": condition_id,
            "patient_id": self._extract_reference_id(
                resource.get("subject"),
                _PATIENT_REFERENCE_TYPE,
                "subject",
            ),
            "encounter_id": self._extract_reference_id(
                resource.get("encounter"),
                _ENCOUNTER_REFERENCE_TYPE,
                "encounter",
            ),
            "condition_code": self._extract_coding_value(resource.get("code"), "code"),
            "condition_code_display": self._extract_coding_value(resource.get("code"), "display"),
            "category_code": self._extract_category_value(resource.get("category"), "code"),
            "category_display": self._extract_category_value(resource.get("category"), "display"),
        }

    def _extract_reference_id(
        self,
        reference_container: Any,
        expected_type: str,
        field_name: str,
    ) -> str | None:
        """
        Extrai o identificador de uma referência FHIR aninhada.
        """

        if reference_container is None:
            return None
        if not isinstance(reference_container, Mapping):
            raise ConditionEDTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise ConditionEDTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ConditionEDTransformationError(str(exc)) from exc

    def _extract_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `code.coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise ConditionEDTransformationError("O campo 'code' deve ser um objeto FHIR quando presente.")
        return first_text_from_mappings(container.get("coding"), key)

    def _extract_category_value(self, categories: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `category[*].coding[*]`.
        """

        if categories is None:
            return None
        if not isinstance(categories, list):
            raise ConditionEDTransformationError("O campo 'category' deve ser uma lista quando presente.")
        for index, category in enumerate(categories):
            if not isinstance(category, Mapping):
                raise ConditionEDTransformationError(
                    f"Cada item de 'category' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            coding_value = self._extract_coding_value(category, key)
            if coding_value is not None:
                return coding_value
        return None
