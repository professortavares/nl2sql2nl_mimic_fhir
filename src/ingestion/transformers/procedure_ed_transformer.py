"""
Transformação de recursos FHIR `Procedure` da camada ED para a modelagem simplificada.
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


class ProcedureEDTransformationError(ValueError):
    """Indica que um recurso ProcedureED não passou na validação mínima."""


class ProcedureEDTransformer:
    """
    Converte recursos FHIR Procedure da camada ED em um dicionário relacional enxuto.

    A modelagem preserva apenas o primeiro valor não vazio e válido encontrado em
    `code.coding[*]`.
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
            Registro pronto para persistência na tabela `procedure_ed`.

        Exceções:
        --------
        TypeError
            Quando a entrada não é um mapeamento.
        ProcedureEDTransformationError
            Quando a validação mínima falha.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise ProcedureEDTransformationError(
                f"resourceType inválido para ProcedureED: {resource.get('resourceType')!r}"
            )

        procedure_id = first_non_empty_text(resource.get("id"))
        if procedure_id is None:
            raise ProcedureEDTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

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
            "performed_at": first_non_empty_text(resource.get("performedDateTime")),
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
            raise ProcedureEDTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise ProcedureEDTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ProcedureEDTransformationError(str(exc)) from exc

    def _extract_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `code.coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise ProcedureEDTransformationError("O campo 'code' deve ser um objeto FHIR quando presente.")
        return first_text_from_mappings(container.get("coding"), key)
