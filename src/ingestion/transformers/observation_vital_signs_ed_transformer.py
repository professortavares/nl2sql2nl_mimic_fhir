"""
Transformação de recursos FHIR `Observation` da camada de sinais vitais ED.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import first_non_empty_text, first_scalar_text, first_text_from_mappings

_RESOURCE_TYPE = "Observation"
_PATIENT_REFERENCE_TYPE = "Patient"
_ENCOUNTER_REFERENCE_TYPE = "Encounter"
_PROCEDURE_REFERENCE_TYPE = "Procedure"


class ObservationVitalSignsEDTransformationError(ValueError):
    """Indica que uma ObservationVitalSignsED não passou na validação mínima."""


@dataclass(slots=True, frozen=True)
class ObservationVitalSignsEDTransformationResult:
    """Conjunto de linhas derivadas de um único ObservationVitalSignsED."""

    observation_vital_signs_ed: dict[str, Any]
    observation_vital_signs_ed_components: list[dict[str, Any]]


class ObservationVitalSignsEDTransformer:
    """
    Converte recursos FHIR Observation em uma tabela principal simplificada e
    em uma tabela auxiliar de components.
    """

    def transform(self, resource: Mapping[str, Any]) -> ObservationVitalSignsEDTransformationResult:
        """
        Transforma um recurso JSON carregado em memória.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise ObservationVitalSignsEDTransformationError(
                f"resourceType inválido para ObservationVitalSignsED: {resource.get('resourceType')!r}"
            )

        observation_id = first_non_empty_text(resource.get("id"))
        if observation_id is None:
            raise ObservationVitalSignsEDTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        observation_vital_signs_ed = {
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
            "category_display": self._extract_category_value(resource.get("category"), "display"),
            "effective_at": first_non_empty_text(resource.get("effectiveDateTime")),
            "value": self._extract_quantity_value(resource.get("valueQuantity"), "value"),
            "value_unit": self._extract_quantity_value(resource.get("valueQuantity"), "unit"),
            "value_code": self._extract_quantity_value(resource.get("valueQuantity"), "code"),
        }
        observation_vital_signs_ed_components = self._extract_component_rows(
            observation_id=observation_id,
            components=resource.get("component"),
        )
        return ObservationVitalSignsEDTransformationResult(
            observation_vital_signs_ed=observation_vital_signs_ed,
            observation_vital_signs_ed_components=observation_vital_signs_ed_components,
        )

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
            raise ObservationVitalSignsEDTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise ObservationVitalSignsEDTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ObservationVitalSignsEDTransformationError(str(exc)) from exc

    def _extract_procedure_id(self, part_of: Any) -> str | None:
        """
        Extrai o primeiro `partOf[*].reference` útil e válido.
        """

        if part_of is None:
            return None
        if isinstance(part_of, Mapping):
            return self._extract_procedure_reference(part_of, "partOf")
        if not isinstance(part_of, list):
            raise ObservationVitalSignsEDTransformationError(
                "O campo 'partOf' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, item in enumerate(part_of):
            if not isinstance(item, Mapping):
                raise ObservationVitalSignsEDTransformationError(
                    f"Cada item de 'partOf' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            reference = item.get("reference")
            if not isinstance(reference, str) or not reference.strip():
                continue
            try:
                return parse_fhir_reference(reference, _PROCEDURE_REFERENCE_TYPE)
            except (TypeError, ValueError, FhirReferenceParseError) as exc:
                raise ObservationVitalSignsEDTransformationError(
                    f"Referência inválida em 'partOf[{index}].reference': {exc}"
                ) from exc
        return None

    def _extract_procedure_reference(self, item: Mapping[str, Any], field_name: str) -> str | None:
        """
        Extrai uma referência `Procedure/<id>` de um objeto FHIR único.
        """

        reference = item.get("reference")
        if reference is None:
            raise ObservationVitalSignsEDTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, _PROCEDURE_REFERENCE_TYPE)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ObservationVitalSignsEDTransformationError(str(exc)) from exc

    def _extract_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `code.coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise ObservationVitalSignsEDTransformationError("O campo 'code' deve ser um objeto FHIR quando presente.")
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
            raise ObservationVitalSignsEDTransformationError(
                "O campo 'category' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, category in enumerate(categories):
            if not isinstance(category, Mapping):
                raise ObservationVitalSignsEDTransformationError(
                    f"Cada item de 'category' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            coding_value = self._extract_coding_value(category, key)
            if coding_value is not None:
                return coding_value
        return None

    def _extract_quantity_value(self, quantity: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `valueQuantity`.
        """

        if quantity is None:
            return None
        if not isinstance(quantity, Mapping):
            raise ObservationVitalSignsEDTransformationError(
                "O campo 'valueQuantity' deve ser um objeto FHIR quando presente."
            )
        if key == "value":
            return first_scalar_text(quantity.get(key))
        return first_non_empty_text(quantity.get(key))

    def _extract_component_rows(
        self,
        *,
        observation_id: str,
        components: Any,
    ) -> list[dict[str, Any]]:
        """
        Extrai uma linha por `component[*]` válido.
        """

        if components is None:
            return []
        items = [components] if isinstance(components, Mapping) else components
        if not isinstance(items, list):
            raise ObservationVitalSignsEDTransformationError(
                "O campo 'component' deve ser um objeto FHIR ou uma lista quando presente."
            )

        rows: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, Mapping):
                raise ObservationVitalSignsEDTransformationError(
                    f"Cada item de 'component' deve ser um objeto FHIR. Item inválido na posição {index}."
                )

            row = {
                "observation_vital_signs_ed_id": observation_id,
                "component_code": self._extract_coding_value(item.get("code"), "code"),
                "component_code_display": self._extract_coding_value(item.get("code"), "display"),
                "value": self._extract_quantity_value(item.get("valueQuantity"), "value"),
                "value_unit": self._extract_quantity_value(item.get("valueQuantity"), "unit"),
                "value_code": self._extract_quantity_value(item.get("valueQuantity"), "code"),
            }
            if any(value is not None for key, value in row.items() if key != "observation_vital_signs_ed_id"):
                rows.append(row)
        return rows
