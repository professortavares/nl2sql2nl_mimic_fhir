"""
Transformação de recursos FHIR `MedicationAdministration` para a modelagem simplificada.
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

_RESOURCE_TYPE = "MedicationAdministration"
_PATIENT_REFERENCE_TYPE = "Patient"
_ENCOUNTER_REFERENCE_TYPE = "Encounter"
_MEDICATION_REQUEST_REFERENCE_TYPE = "MedicationRequest"


class MedicationAdministrationTransformationError(ValueError):
    """Indica que um recurso MedicationAdministration não passou na validação mínima."""


class MedicationAdministrationTransformer:
    """
    Converte recursos FHIR MedicationAdministration em um dicionário relacional enxuto.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise MedicationAdministrationTransformationError(
                f"resourceType inválido para MedicationAdministration: {resource.get('resourceType')!r}"
            )

        medication_administration_id = first_non_empty_text(resource.get("id"))
        if medication_administration_id is None:
            raise MedicationAdministrationTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": medication_administration_id,
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE, "subject"),
            "encounter_id": self._extract_reference_id(resource.get("context"), _ENCOUNTER_REFERENCE_TYPE, "context"),
            "medication_request_id": self._extract_reference_id(
                resource.get("request"),
                _MEDICATION_REQUEST_REFERENCE_TYPE,
                "request",
            ),
            "status": first_non_empty_text(resource.get("status")),
            "effective_at": first_non_empty_text(resource.get("effectiveDateTime")),
            "medication_code": self._extract_medication_code(resource.get("medicationCodeableConcept"), "code"),
            "medication_code_system": self._extract_medication_code(
                resource.get("medicationCodeableConcept"),
                "system",
            ),
            "dosage_text": self._extract_dosage_text(resource.get("dosage")),
            "dose_value": self._extract_dosage_dose_value(resource.get("dosage"), "value"),
            "dose_unit": self._extract_dosage_dose_value(resource.get("dosage"), "unit"),
            "dose_code": self._extract_dosage_dose_value(resource.get("dosage"), "code"),
            "dose_system": self._extract_dosage_dose_value(resource.get("dosage"), "system"),
            "method_code": self._extract_dosage_method_code(resource.get("dosage")),
            "method_system": self._extract_dosage_method_system(resource.get("dosage")),
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
            raise MedicationAdministrationTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise MedicationAdministrationTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise MedicationAdministrationTransformationError(str(exc)) from exc

    def _extract_medication_code(self, medication: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `medicationCodeableConcept.coding[*]`.
        """

        if medication is None:
            return None
        if not isinstance(medication, Mapping):
            raise MedicationAdministrationTransformationError(
                "O campo 'medicationCodeableConcept' deve ser um objeto FHIR quando presente."
            )
        return first_text_from_mappings(medication.get("coding"), key)

    def _extract_dosage_text(self, dosage: Any) -> str | None:
        """
        Extrai `dosage.text` quando presente.
        """

        if dosage is None:
            return None
        if not isinstance(dosage, Mapping):
            raise MedicationAdministrationTransformationError(
                "O campo 'dosage' deve ser um objeto FHIR quando presente."
            )
        return first_non_empty_text(dosage.get("text"))

    def _extract_dosage_dose_value(self, dosage: Any, key: str) -> str | None:
        """
        Extrai `dosage.dose.<key>` quando presente.
        """

        dose = self._extract_nested_mapping(dosage, "dose")
        if dose is None:
            return None
        if key == "value":
            return first_scalar_text(dose.get(key))
        return first_non_empty_text(dose.get(key))

    def _extract_dosage_method_code(self, dosage: Any) -> str | None:
        """
        Extrai o primeiro `dosage.method.coding[*].code` útil.
        """

        method = self._extract_nested_mapping(dosage, "method")
        if method is None:
            return None
        return first_text_from_mappings(method.get("coding"), "code")

    def _extract_dosage_method_system(self, dosage: Any) -> str | None:
        """
        Extrai o primeiro `dosage.method.coding[*].system` útil.
        """

        method = self._extract_nested_mapping(dosage, "method")
        if method is None:
            return None
        return first_text_from_mappings(method.get("coding"), "system")

    def _extract_nested_mapping(self, container: Any, key: str) -> Mapping[str, Any] | None:
        """
        Extrai um mapeamento aninhado quando presente.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise MedicationAdministrationTransformationError(
                "O campo 'dosage' deve ser um objeto FHIR quando presente."
            )
        nested = container.get(key)
        if nested is None:
            return None
        if not isinstance(nested, Mapping):
            raise MedicationAdministrationTransformationError(
                f"O campo 'dosage.{key}' deve ser um objeto FHIR quando presente."
            )
        return nested
