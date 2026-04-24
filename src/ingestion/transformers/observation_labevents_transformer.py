"""
Transformação de recursos FHIR `Observation` da camada de labevents para a modelagem simplificada.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import (
    first_non_empty_text,
    first_scalar_text,
    first_text_from_mappings,
    first_text_from_mappings_matching,
)

_RESOURCE_TYPE = "Observation"
_PATIENT_REFERENCE_TYPE = "Patient"
_SPECIMEN_REFERENCE_TYPE = "Specimen"
_LAB_PRIORITY_EXTENSION_URL = (
    "http://mimic.mit.edu/fhir/mimic/StructureDefinition/lab-priority"
)


class ObservationLabeventsTransformationError(ValueError):
    """Indica que uma ObservationLabevents não passou na validação mínima."""


class ObservationLabeventsTransformer:
    """
    Converte recursos FHIR Observation em um dicionário relacional enxuto.

    A modelagem preserva apenas o primeiro valor não vazio e válido encontrado
    nas coleções observadas.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Observation.

        Retorno:
        -------
        dict[str, Any]
            Registro pronto para persistência na tabela `observation_labevents`.

        Exceções:
        --------
        TypeError
            Quando a entrada não é um mapeamento.
        ObservationLabeventsTransformationError
            Quando a validação mínima falha.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise ObservationLabeventsTransformationError(
                f"resourceType inválido para ObservationLabevents: {resource.get('resourceType')!r}"
            )

        observation_id = first_non_empty_text(resource.get("id"))
        if observation_id is None:
            raise ObservationLabeventsTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": observation_id,
            "patient_id": self._extract_reference_id(
                resource.get("subject"),
                _PATIENT_REFERENCE_TYPE,
                "subject",
            ),
            "specimen_id": self._extract_reference_id(
                resource.get("specimen"),
                _SPECIMEN_REFERENCE_TYPE,
                "specimen",
            ),
            "status": first_non_empty_text(resource.get("status")),
            "observation_code": self._extract_coding_value(resource.get("code"), "code"),
            "observation_code_system": self._extract_coding_value(resource.get("code"), "system"),
            "observation_code_display": self._extract_coding_value(resource.get("code"), "display"),
            "category_code": self._extract_category_value(resource.get("category"), "code"),
            "category_system": self._extract_category_value(resource.get("category"), "system"),
            "category_display": self._extract_category_value(resource.get("category"), "display"),
            "effective_at": first_non_empty_text(resource.get("effectiveDateTime")),
            "issued_at": first_non_empty_text(resource.get("issued")),
            "identifier": self._extract_identifier(resource.get("identifier")),
            "value": self._extract_quantity_value(resource.get("valueQuantity"), "value"),
            "value_unit": self._extract_quantity_value(resource.get("valueQuantity"), "unit"),
            "value_code": self._extract_quantity_value(resource.get("valueQuantity"), "code"),
            "value_system": self._extract_quantity_value(resource.get("valueQuantity"), "system"),
            "reference_low_value": self._extract_reference_range_value(resource.get("referenceRange"), "low", "value"),
            "reference_low_unit": self._extract_reference_range_value(resource.get("referenceRange"), "low", "unit"),
            "reference_high_value": self._extract_reference_range_value(resource.get("referenceRange"), "high", "value"),
            "reference_high_unit": self._extract_reference_range_value(resource.get("referenceRange"), "high", "unit"),
            "lab_priority": self._extract_lab_priority(resource.get("extension")),
            "note": self._extract_note(resource.get("note")),
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
            raise ObservationLabeventsTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise ObservationLabeventsTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ObservationLabeventsTransformationError(str(exc)) from exc

    def _extract_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `code.coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise ObservationLabeventsTransformationError("O campo 'code' deve ser um objeto FHIR quando presente.")
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
            raise ObservationLabeventsTransformationError(
                "O campo 'category' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, category in enumerate(categories):
            if not isinstance(category, Mapping):
                raise ObservationLabeventsTransformationError(
                    f"Cada item de 'category' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            coding_value = self._extract_coding_value(category, key)
            if coding_value is not None:
                return coding_value
        return None

    def _extract_identifier(self, identifiers: Any) -> str | None:
        """
        Extrai o primeiro identificador textual útil.
        """

        if identifiers is None:
            return None
        if isinstance(identifiers, Mapping):
            return first_non_empty_text(identifiers.get("value"))
        if not isinstance(identifiers, list):
            raise ObservationLabeventsTransformationError(
                "O campo 'identifier' deve ser um objeto FHIR ou uma lista quando presente."
            )
        return first_text_from_mappings(identifiers, "value")

    def _extract_quantity_value(self, quantity: Any, key: str) -> str | None:
        """
        Extrai um valor escalar de `valueQuantity`.
        """

        if quantity is None:
            return None
        if not isinstance(quantity, Mapping):
            raise ObservationLabeventsTransformationError(
                "O campo 'valueQuantity' deve ser um objeto FHIR quando presente."
            )
        return first_scalar_text(quantity.get(key))

    def _extract_reference_range_value(self, ranges: Any, bound: str, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `referenceRange[*].low|high`.
        """

        if ranges is None:
            return None
        if isinstance(ranges, Mapping):
            return self._extract_bound_value(ranges.get(bound), key)
        if not isinstance(ranges, list):
            raise ObservationLabeventsTransformationError(
                "O campo 'referenceRange' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, item in enumerate(ranges):
            if not isinstance(item, Mapping):
                raise ObservationLabeventsTransformationError(
                    f"Cada item de 'referenceRange' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            extracted = self._extract_bound_value(item.get(bound), key)
            if extracted is not None:
                return extracted
        return None

    def _extract_bound_value(self, bound: Any, key: str) -> str | None:
        """
        Extrai um valor de `low` ou `high`.
        """

        if bound is None:
            return None
        if not isinstance(bound, Mapping):
            raise ObservationLabeventsTransformationError(
                "Os limites de 'referenceRange' devem ser objetos FHIR quando presentes."
            )
        return first_scalar_text(bound.get(key))

    def _extract_lab_priority(self, extensions: Any) -> str | None:
        """
        Extrai o valor da extensão de prioridade laboratorial.
        """

        if extensions is None:
            return None
        if not isinstance(extensions, list):
            raise ObservationLabeventsTransformationError("O campo 'extension' deve ser uma lista quando presente.")
        return first_text_from_mappings_matching(
            extensions,
            "valueString",
            lambda item: first_non_empty_text(item.get("url")) == _LAB_PRIORITY_EXTENSION_URL,
        )

    def _extract_note(self, notes: Any) -> str | None:
        """
        Extrai a primeira nota textual útil.
        """

        if notes is None:
            return None
        if isinstance(notes, Mapping):
            return first_non_empty_text(notes.get("text"))
        if not isinstance(notes, list):
            raise ObservationLabeventsTransformationError("O campo 'note' deve ser um objeto FHIR ou uma lista quando presente.")
        return first_text_from_mappings(notes, "text")
