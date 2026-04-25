"""
Transformação de recursos FHIR `Observation` da camada microbiológica de susceptibilidade.
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
)

_RESOURCE_TYPE = "Observation"
_PATIENT_REFERENCE_TYPE = "Patient"
_OBSERVATION_REFERENCE_TYPE = "Observation"
_DILUTION_EXTENSION_URL = (
    "http://mimic.mit.edu/fhir/mimic/StructureDefinition/dilution-details"
)


class ObservationMicroSuscTransformationError(ValueError):
    """Indica que uma ObservationMicroSusc não passou na validação mínima."""


class ObservationMicroSuscTransformer:
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
            raise ObservationMicroSuscTransformationError(
                f"resourceType inválido para ObservationMicroSusc: {resource.get('resourceType')!r}"
            )

        susc_id = first_non_empty_text(resource.get("id"))
        if susc_id is None:
            raise ObservationMicroSuscTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": susc_id,
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE, "subject"),
            "derived_from_observation_micro_org_id": self._extract_derived_from_id(resource.get("derivedFrom")),
            "status": first_non_empty_text(resource.get("status")),
            "antibiotic_code": self._extract_coding_value(resource.get("code"), "code"),
            "antibiotic_code_display": self._extract_coding_value(resource.get("code"), "display"),
            "category_code": self._extract_category_value(resource.get("category"), "code"),
            "category_display": self._extract_category_value(resource.get("category"), "display"),
            "effective_at": first_non_empty_text(resource.get("effectiveDateTime")),
            "identifier": self._extract_identifier(resource.get("identifier")),
            "interpretation_code": self._extract_interpretation_value(resource.get("valueCodeableConcept"), "code"),
            "interpretation_display": self._extract_interpretation_value(resource.get("valueCodeableConcept"), "display"),
            "dilution_value": self._extract_dilution_extension(resource.get("extension"), "value"),
            "dilution_comparator": self._extract_dilution_extension(resource.get("extension"), "comparator"),
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
            raise ObservationMicroSuscTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise ObservationMicroSuscTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ObservationMicroSuscTransformationError(str(exc)) from exc

    def _extract_derived_from_id(self, derived_from: Any) -> str | None:
        """
        Extrai o primeiro `derivedFrom[*].reference` útil e válido.
        """

        if derived_from is None:
            return None
        if isinstance(derived_from, Mapping):
            return self._extract_observation_reference(derived_from, "derivedFrom")
        if not isinstance(derived_from, list):
            raise ObservationMicroSuscTransformationError(
                "O campo 'derivedFrom' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, item in enumerate(derived_from):
            if not isinstance(item, Mapping):
                raise ObservationMicroSuscTransformationError(
                    f"Cada item de 'derivedFrom' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            reference = item.get("reference")
            if not isinstance(reference, str) or not reference.strip():
                continue
            try:
                return parse_fhir_reference(reference, _OBSERVATION_REFERENCE_TYPE)
            except (TypeError, ValueError, FhirReferenceParseError) as exc:
                raise ObservationMicroSuscTransformationError(
                    f"Referência inválida em 'derivedFrom[{index}].reference': {exc}"
                ) from exc
        return None

    def _extract_observation_reference(self, item: Mapping[str, Any], field_name: str) -> str | None:
        """
        Extrai uma referência `Observation/<id>` de um objeto FHIR único.
        """

        reference = item.get("reference")
        if reference is None:
            raise ObservationMicroSuscTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, _OBSERVATION_REFERENCE_TYPE)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ObservationMicroSuscTransformationError(str(exc)) from exc

    def _extract_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `code.coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise ObservationMicroSuscTransformationError("O campo 'code' deve ser um objeto FHIR quando presente.")
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
            raise ObservationMicroSuscTransformationError(
                "O campo 'category' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, category in enumerate(categories):
            if not isinstance(category, Mapping):
                raise ObservationMicroSuscTransformationError(
                    f"Cada item de 'category' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            coding_value = self._extract_coding_value(category, key)
            if coding_value is not None:
                return coding_value
        return None

    def _extract_identifier(self, identifiers: Any) -> str | None:
        """
        Extrai o primeiro identificador útil.
        """

        if identifiers is None:
            return None
        if isinstance(identifiers, Mapping):
            return first_non_empty_text(identifiers.get("value"))
        if not isinstance(identifiers, list):
            raise ObservationMicroSuscTransformationError(
                "O campo 'identifier' deve ser um objeto FHIR ou uma lista quando presente."
            )
        return first_text_from_mappings(identifiers, "value")

    def _extract_interpretation_value(self, value_codeable_concept: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `valueCodeableConcept.coding[*]`.
        """

        if value_codeable_concept is None:
            return None
        if not isinstance(value_codeable_concept, Mapping):
            raise ObservationMicroSuscTransformationError(
                "O campo 'valueCodeableConcept' deve ser um objeto FHIR quando presente."
            )
        return first_text_from_mappings(value_codeable_concept.get("coding"), key)

    def _extract_dilution_extension(self, extensions: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil da extensão `dilution-details`.
        """

        if extensions is None:
            return None
        if not isinstance(extensions, list):
            raise ObservationMicroSuscTransformationError("O campo 'extension' deve ser uma lista quando presente.")
        for index, item in enumerate(extensions):
            if not isinstance(item, Mapping):
                raise ObservationMicroSuscTransformationError(
                    f"Cada item de 'extension' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            if first_non_empty_text(item.get("url")) != _DILUTION_EXTENSION_URL:
                continue
            value_quantity = item.get("valueQuantity")
            if not isinstance(value_quantity, Mapping):
                raise ObservationMicroSuscTransformationError(
                    f"O item de 'extension[{index}]' com URL de dilution-details deve conter 'valueQuantity'."
                )
            if key == "value":
                return first_scalar_text(value_quantity.get(key))
            return first_non_empty_text(value_quantity.get(key))
        return None

    def _extract_note(self, notes: Any) -> str | None:
        """
        Extrai a primeira nota textual útil.
        """

        if notes is None:
            return None
        if isinstance(notes, Mapping):
            return first_non_empty_text(notes.get("text"))
        if not isinstance(notes, list):
            raise ObservationMicroSuscTransformationError("O campo 'note' deve ser um objeto FHIR ou uma lista quando presente.")
        return first_text_from_mappings(notes, "text")
