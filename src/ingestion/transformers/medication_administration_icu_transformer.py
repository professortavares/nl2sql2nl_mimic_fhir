"""
Transformação de recursos FHIR `MedicationAdministration` da camada ICU.
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


class MedicationAdministrationICUTransformationError(ValueError):
    """Indica que um recurso MedicationAdministrationICU não passou na validação mínima."""


class MedicationAdministrationICUTransformer:
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
            raise MedicationAdministrationICUTransformationError(
                f"resourceType inválido para MedicationAdministrationICU: {resource.get('resourceType')!r}"
            )

        medication_administration_id = first_non_empty_text(resource.get("id"))
        if medication_administration_id is None:
            raise MedicationAdministrationICUTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": medication_administration_id,
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE, "subject"),
            "encounter_id": self._extract_reference_id(resource.get("context"), _ENCOUNTER_REFERENCE_TYPE, "context"),
            "status": first_non_empty_text(resource.get("status")),
            "effective_at": first_non_empty_text(resource.get("effectiveDateTime")),
            "category_code": self._extract_category_value(resource.get("category"), "code"),
            "category_system": self._extract_category_value(resource.get("category"), "system"),
            "medication_code": self._extract_medication_code(resource.get("medicationCodeableConcept"), "code"),
            "medication_code_system": self._extract_medication_code(
                resource.get("medicationCodeableConcept"),
                "system",
            ),
            "medication_code_display": self._extract_medication_code(
                resource.get("medicationCodeableConcept"),
                "display",
            ),
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
            raise MedicationAdministrationICUTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise MedicationAdministrationICUTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise MedicationAdministrationICUTransformationError(str(exc)) from exc

    def _extract_category_value(self, categories: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `category[*].coding[*]`.
        """

        if categories is None:
            return None
        if isinstance(categories, Mapping):
            return self._extract_coding_value(categories, key)
        if not isinstance(categories, list):
            raise MedicationAdministrationICUTransformationError(
                "O campo 'category' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, category in enumerate(categories):
            if not isinstance(category, Mapping):
                raise MedicationAdministrationICUTransformationError(
                    f"Cada item de 'category' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            coding_value = self._extract_coding_value(category, key)
            if coding_value is not None:
                return coding_value
        return None

    def _extract_medication_code(self, medication: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `medicationCodeableConcept.coding[*]`.
        """

        if medication is None:
            return None
        if not isinstance(medication, Mapping):
            raise MedicationAdministrationICUTransformationError(
                "O campo 'medicationCodeableConcept' deve ser um objeto FHIR quando presente."
            )
        return first_text_from_mappings(medication.get("coding"), key)

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

    def _extract_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise MedicationAdministrationICUTransformationError(
                "O campo de codificação deve ser um objeto FHIR quando presente."
            )
        return first_text_from_mappings(container.get("coding"), key)

    def _extract_nested_mapping(self, container: Any, key: str) -> Mapping[str, Any] | None:
        """
        Extrai um mapeamento aninhado quando presente.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise MedicationAdministrationICUTransformationError(
                "O campo 'dosage' deve ser um objeto FHIR quando presente."
            )
        nested = container.get(key)
        if nested is None:
            return None
        if not isinstance(nested, Mapping):
            raise MedicationAdministrationICUTransformationError(
                f"O campo 'dosage.{key}' deve ser um objeto FHIR quando presente."
            )
        return nested
