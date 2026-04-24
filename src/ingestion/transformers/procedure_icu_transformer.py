"""
Transformação de recursos FHIR `Procedure` da camada ICU para a modelagem simplificada.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import first_non_empty_text, first_text_from_mappings

_RESOURCE_TYPE = "Procedure"
_PATIENT_REFERENCE_TYPE = "Patient"
_ENCOUNTER_REFERENCE_TYPE = "Encounter"


class ProcedureICUTransformationError(ValueError):
    """Indica que um recurso ProcedureICU não passou na validação mínima."""


class ProcedureICUTransformer:
    """
    Converte recursos FHIR Procedure da camada ICU em um dicionário relacional enxuto.

    A modelagem preserva apenas o primeiro valor não vazio e válido encontrado em
    `code.coding[*]` e `category.coding[*]`.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Procedure.

        Retorno:
        -------
        dict[str, Any]
            Registro pronto para persistência na tabela `procedure_icu`.

        Exceções:
        --------
        TypeError
            Quando a entrada não é um mapeamento.
        ProcedureICUTransformationError
            Quando a validação mínima falha.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise ProcedureICUTransformationError(
                f"resourceType inválido para ProcedureICU: {resource.get('resourceType')!r}"
            )

        procedure_id = first_non_empty_text(resource.get("id"))
        if procedure_id is None:
            raise ProcedureICUTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": procedure_id,
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
            "status": first_non_empty_text(resource.get("status")),
            "procedure_code": self._extract_coding_value(resource.get("code"), "code"),
            "procedure_code_system": self._extract_coding_value(resource.get("code"), "system"),
            "procedure_code_display": self._extract_coding_value(resource.get("code"), "display"),
            "category_code": self._extract_category_value(resource.get("category"), "code"),
            "category_system": self._extract_category_value(resource.get("category"), "system"),
            "performed_start": self._extract_performed_period_value(resource.get("performedPeriod"), "start"),
            "performed_end": self._extract_performed_period_value(resource.get("performedPeriod"), "end"),
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
            raise ProcedureICUTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise ProcedureICUTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ProcedureICUTransformationError(str(exc)) from exc

    def _extract_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `code.coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise ProcedureICUTransformationError("O campo 'code' deve ser um objeto FHIR quando presente.")
        return first_text_from_mappings(container.get("coding"), key)

    def _extract_category_value(self, categories: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `category[*].coding[*]`.
        """

        if categories is None:
            return None
        if not isinstance(categories, list):
            raise ProcedureICUTransformationError("O campo 'category' deve ser uma lista quando presente.")
        for index, category in enumerate(categories):
            if not isinstance(category, Mapping):
                raise ProcedureICUTransformationError(
                    f"Cada item de 'category' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            coding_value = self._extract_coding_value(category, key)
            if coding_value is not None:
                return coding_value
        return None

    def _extract_performed_period_value(self, period: Any, key: str) -> str | None:
        """
        Extrai o valor textual de `performedPeriod`.
        """

        if period is None:
            return None
        if not isinstance(period, Mapping):
            raise ProcedureICUTransformationError("O campo 'performedPeriod' deve ser um objeto FHIR quando presente.")
        return first_non_empty_text(period.get(key))
