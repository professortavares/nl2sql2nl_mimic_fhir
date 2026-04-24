"""
Transformação de recursos FHIR `MedicationDispense` da camada ED.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import first_non_empty_text, first_text_from_mappings

_RESOURCE_TYPE = "MedicationDispense"
_PATIENT_REFERENCE_TYPE = "Patient"
_ENCOUNTER_REFERENCE_TYPE = "Encounter"


class MedicationDispenseEDTransformationError(ValueError):
    """Indica que um recurso MedicationDispenseED não passou na validação mínima."""


class MedicationDispenseEDTransformer:
    """
    Converte recursos FHIR MedicationDispense em um dicionário relacional enxuto.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise MedicationDispenseEDTransformationError(
                f"resourceType inválido para MedicationDispenseED: {resource.get('resourceType')!r}"
            )

        medication_dispense_id = first_non_empty_text(resource.get("id"))
        if medication_dispense_id is None:
            raise MedicationDispenseEDTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": medication_dispense_id,
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE, "subject"),
            "encounter_id": self._extract_reference_id(resource.get("context"), _ENCOUNTER_REFERENCE_TYPE, "context"),
            "status": first_non_empty_text(resource.get("status")),
            "when_handed_over": first_non_empty_text(resource.get("whenHandedOver")),
            "medication_text": self._extract_medication_text(resource.get("medicationCodeableConcept")),
            "medication_code": self._extract_medication_code(resource.get("medicationCodeableConcept"), "code"),
            "medication_code_system": self._extract_medication_code(
                resource.get("medicationCodeableConcept"),
                "system",
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
            raise MedicationDispenseEDTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise MedicationDispenseEDTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise MedicationDispenseEDTransformationError(str(exc)) from exc

    def _extract_medication_text(self, medication: Any) -> str | None:
        """
        Extrai `medicationCodeableConcept.text` quando presente.
        """

        if medication is None:
            return None
        if not isinstance(medication, Mapping):
            raise MedicationDispenseEDTransformationError(
                "O campo 'medicationCodeableConcept' deve ser um objeto FHIR quando presente."
            )
        return first_non_empty_text(medication.get("text"))

    def _extract_medication_code(self, medication: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `medicationCodeableConcept.coding[*]`.
        """

        if medication is None:
            return None
        if not isinstance(medication, Mapping):
            raise MedicationDispenseEDTransformationError(
                "O campo 'medicationCodeableConcept' deve ser um objeto FHIR quando presente."
            )
        return first_text_from_mappings(medication.get("coding"), key)
