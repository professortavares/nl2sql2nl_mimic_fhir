"""
Transformação de recursos FHIR `Observation` da camada de observações ED.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import first_non_empty_text, first_text_from_mappings

_RESOURCE_TYPE = "Observation"
_PATIENT_REFERENCE_TYPE = "Patient"
_ENCOUNTER_REFERENCE_TYPE = "Encounter"
_PROCEDURE_REFERENCE_TYPE = "Procedure"


class ObservationEDTransformationError(ValueError):
    """Indica que uma ObservationED não passou na validação mínima."""


class ObservationEDTransformer:
    """
    Converte recursos FHIR Observation em um dicionário relacional enxuto.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise ObservationEDTransformationError(
                f"resourceType inválido para ObservationED: {resource.get('resourceType')!r}"
            )

        observation_id = first_non_empty_text(resource.get("id"))
        if observation_id is None:
            raise ObservationEDTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": observation_id,
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE, "subject"),
            "encounter_id": self._extract_reference_id(
                resource.get("encounter"),
                _ENCOUNTER_REFERENCE_TYPE,
                "encounter",
            ),
            "procedure_id": self._extract_procedure_id(resource.get("partOf")),
            "status": first_non_empty_text(resource.get("status")),
            "observation_code": self._extract_coding_value(resource.get("code"), "code"),
            "observation_code_display": self._extract_coding_value(resource.get("code"), "display"),
            "category_code": self._extract_category_value(resource.get("category"), "code"),
            "category_system": self._extract_category_value(resource.get("category"), "system"),
            "category_display": self._extract_category_value(resource.get("category"), "display"),
            "effective_at": first_non_empty_text(resource.get("effectiveDateTime")),
            "value_string": first_non_empty_text(resource.get("valueString")),
            "data_absent_reason_code": self._extract_data_absent_reason_value(
                resource.get("dataAbsentReason"),
                "code",
            ),
            "data_absent_reason_display": self._extract_data_absent_reason_value(
                resource.get("dataAbsentReason"),
                "display",
            ),
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
            raise ObservationEDTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise ObservationEDTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ObservationEDTransformationError(str(exc)) from exc

    def _extract_procedure_id(self, part_of: Any) -> str | None:
        """
        Extrai o primeiro `partOf[*].reference` útil e válido.
        """

        if part_of is None:
            return None
        if isinstance(part_of, Mapping):
            return self._extract_procedure_reference(part_of, "partOf")
        if not isinstance(part_of, list):
            raise ObservationEDTransformationError(
                "O campo 'partOf' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, item in enumerate(part_of):
            if not isinstance(item, Mapping):
                raise ObservationEDTransformationError(
                    f"Cada item de 'partOf' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            reference = item.get("reference")
            if not isinstance(reference, str) or not reference.strip():
                continue
            try:
                return parse_fhir_reference(reference, _PROCEDURE_REFERENCE_TYPE)
            except (TypeError, ValueError, FhirReferenceParseError) as exc:
                raise ObservationEDTransformationError(
                    f"Referência inválida em 'partOf[{index}].reference': {exc}"
                ) from exc
        return None

    def _extract_procedure_reference(self, item: Mapping[str, Any], field_name: str) -> str | None:
        """
        Extrai uma referência `Procedure/<id>` de um objeto FHIR único.
        """

        reference = item.get("reference")
        if reference is None:
            raise ObservationEDTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, _PROCEDURE_REFERENCE_TYPE)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ObservationEDTransformationError(str(exc)) from exc

    def _extract_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `code.coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise ObservationEDTransformationError("O campo 'code' deve ser um objeto FHIR quando presente.")
        return first_text_from_mappings(container.get("coding"), key)

    def _extract_category_value(self, categories: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `category[*].coding[*]`.
        """

        if categories is None:
            return None
        if isinstance(categories, Mapping):
            return self._extract_coding_value(categories, key)
        if not isinstance(categories, list):
            raise ObservationEDTransformationError(
                "O campo 'category' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, category in enumerate(categories):
            if not isinstance(category, Mapping):
                raise ObservationEDTransformationError(
                    f"Cada item de 'category' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            coding_value = self._extract_coding_value(category, key)
            if coding_value is not None:
                return coding_value
        return None

    def _extract_data_absent_reason_value(self, data_absent_reason: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `dataAbsentReason.coding[*]`.
        """

        if data_absent_reason is None:
            return None
        if not isinstance(data_absent_reason, Mapping):
            raise ObservationEDTransformationError(
                "O campo 'dataAbsentReason' deve ser um objeto FHIR quando presente."
            )
        return first_text_from_mappings(data_absent_reason.get("coding"), key)
