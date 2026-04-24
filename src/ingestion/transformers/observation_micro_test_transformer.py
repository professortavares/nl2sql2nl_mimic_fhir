"""
Transformação de recursos FHIR `Observation` da camada de microbiologia para a modelagem simplificada.
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
_SPECIMEN_REFERENCE_TYPE = "Specimen"
_ENCOUNTER_REFERENCE_TYPE = "Encounter"


class ObservationMicroTestTransformationError(ValueError):
    """Indica que uma ObservationMicroTest não passou na validação mínima."""


class ObservationMicroTestTransformer:
    """
    Converte recursos FHIR Observation em um dicionário relacional enxuto.

    A modelagem preserva apenas o primeiro valor não vazio e válido encontrado
    nas coleções observadas.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise ObservationMicroTestTransformationError(
                f"resourceType inválido para ObservationMicroTest: {resource.get('resourceType')!r}"
            )

        observation_id = first_non_empty_text(resource.get("id"))
        if observation_id is None:
            raise ObservationMicroTestTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": observation_id,
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE, "subject"),
            "specimen_id": self._extract_reference_id(
                resource.get("specimen"),
                _SPECIMEN_REFERENCE_TYPE,
                "specimen",
            ),
            "encounter_id": self._extract_reference_id(
                resource.get("encounter"),
                _ENCOUNTER_REFERENCE_TYPE,
                "encounter",
            ),
            "status": first_non_empty_text(resource.get("status")),
            "observation_code": self._extract_coding_value(resource.get("code"), "code"),
            "observation_code_system": self._extract_coding_value(resource.get("code"), "system"),
            "observation_code_display": self._extract_coding_value(resource.get("code"), "display"),
            "category_code": self._extract_category_value(resource.get("category"), "code"),
            "category_system": self._extract_category_value(resource.get("category"), "system"),
            "category_display": self._extract_category_value(resource.get("category"), "display"),
            "effective_at": first_non_empty_text(resource.get("effectiveDateTime")),
            "value_string": first_non_empty_text(resource.get("valueString")),
            "value_code": self._extract_value_codeable_concept(resource.get("valueCodeableConcept"), "code"),
            "value_code_system": self._extract_value_codeable_concept(resource.get("valueCodeableConcept"), "system"),
            "value_code_display": self._extract_value_codeable_concept(resource.get("valueCodeableConcept"), "display"),
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
            raise ObservationMicroTestTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise ObservationMicroTestTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ObservationMicroTestTransformationError(str(exc)) from exc

    def _extract_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `code.coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise ObservationMicroTestTransformationError("O campo 'code' deve ser um objeto FHIR quando presente.")
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
            raise ObservationMicroTestTransformationError(
                "O campo 'category' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, category in enumerate(categories):
            if not isinstance(category, Mapping):
                raise ObservationMicroTestTransformationError(
                    f"Cada item de 'category' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            coding_value = self._extract_coding_value(category, key)
            if coding_value is not None:
                return coding_value
        return None

    def _extract_value_codeable_concept(self, value_codeable_concept: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `valueCodeableConcept.coding[*]`.
        """

        if value_codeable_concept is None:
            return None
        if not isinstance(value_codeable_concept, Mapping):
            raise ObservationMicroTestTransformationError(
                "O campo 'valueCodeableConcept' deve ser um objeto FHIR quando presente."
            )
        return first_text_from_mappings(value_codeable_concept.get("coding"), key)
