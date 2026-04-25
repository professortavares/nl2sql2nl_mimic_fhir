"""
Transformação de recursos FHIR `MedicationDispense` para a modelagem simplificada.
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
_MEDICATION_REQUEST_REFERENCE_TYPE = "MedicationRequest"


class MedicationDispenseTransformationError(ValueError):
    """Indica que um recurso MedicationDispense não passou na validação mínima."""


class MedicationDispenseTransformer:
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
            raise MedicationDispenseTransformationError(
                f"resourceType inválido para MedicationDispense: {resource.get('resourceType')!r}"
            )

        medication_dispense_id = first_non_empty_text(resource.get("id"))
        if medication_dispense_id is None:
            raise MedicationDispenseTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": medication_dispense_id,
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE, "subject"),
            "encounter_id": self._extract_reference_id(resource.get("context"), _ENCOUNTER_REFERENCE_TYPE, "context"),
            "medication_request_id": self._extract_medication_request_id(resource.get("authorizingPrescription")),
            "status": first_non_empty_text(resource.get("status")),
            "identifier": self._extract_identifier(resource.get("identifier")),
            "medication_code": self._extract_medication_code(resource.get("medicationCodeableConcept"), "code"),
            "route_code": self._extract_route_code(resource.get("dosageInstruction")),
            "frequency_code": self._extract_frequency_code(resource.get("dosageInstruction")),
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
            raise MedicationDispenseTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise MedicationDispenseTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise MedicationDispenseTransformationError(str(exc)) from exc

    def _extract_medication_request_id(self, authorizing_prescriptions: Any) -> str | None:
        """
        Extrai o primeiro `authorizingPrescription[*].reference` útil e válido.
        """

        if authorizing_prescriptions is None:
            return None
        items = [authorizing_prescriptions] if isinstance(authorizing_prescriptions, Mapping) else authorizing_prescriptions
        if not isinstance(items, list):
            raise MedicationDispenseTransformationError(
                "O campo 'authorizingPrescription' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, item in enumerate(items):
            if not isinstance(item, Mapping):
                raise MedicationDispenseTransformationError(
                    f"Cada item de 'authorizingPrescription' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            reference = item.get("reference")
            if not isinstance(reference, str) or not reference.strip():
                continue
            try:
                return parse_fhir_reference(reference, _MEDICATION_REQUEST_REFERENCE_TYPE)
            except (TypeError, ValueError, FhirReferenceParseError) as exc:
                raise MedicationDispenseTransformationError(
                    f"Referência inválida em 'authorizingPrescription[{index}].reference': {exc}"
                ) from exc
        return None

    def _extract_identifier(self, identifiers: Any) -> str | None:
        """
        Extrai o primeiro identificador útil do recurso.
        """

        return first_text_from_mappings(identifiers, "value")

    def _extract_medication_code(self, medication: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `medicationCodeableConcept.coding[*]`.
        """

        if medication is None:
            return None
        if not isinstance(medication, Mapping):
            raise MedicationDispenseTransformationError(
                "O campo 'medicationCodeableConcept' deve ser um objeto FHIR quando presente."
            )
        return first_text_from_mappings(medication.get("coding"), key)

    def _extract_route_code(self, dosage_instructions: Any) -> str | None:
        """
        Extrai o primeiro `dosageInstruction[*].route.coding[*].code` útil.
        """

        return self._extract_from_dosage_instructions(
            dosage_instructions,
            lambda instruction: self._extract_first_coding_value(instruction.get("route"), "code"),
        )

    def _extract_frequency_code(self, dosage_instructions: Any) -> str | None:
        """
        Extrai o primeiro `dosageInstruction[*].timing.code.coding[*].code` útil.
        """

        return self._extract_from_dosage_instructions(
            dosage_instructions,
            lambda instruction: self._extract_first_coding_value(
                self._extract_nested_mapping(instruction.get("timing"), "code"),
                "code",
            ),
        )

    def _extract_from_dosage_instructions(self, dosage_instructions: Any, extractor: Any) -> str | None:
        """
        Aplica um extrator sobre `dosageInstruction[*]` e retorna o primeiro valor útil.
        """

        if dosage_instructions is None:
            return None
        if not isinstance(dosage_instructions, list):
            raise MedicationDispenseTransformationError(
                "O campo 'dosageInstruction' deve ser uma lista quando presente."
            )
        for index, instruction in enumerate(dosage_instructions):
            if not isinstance(instruction, Mapping):
                raise MedicationDispenseTransformationError(
                    f"Cada item de 'dosageInstruction' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            normalized = extractor(instruction)
            if normalized is not None:
                return normalized
        return None

    def _extract_first_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor válido de uma lista `coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise MedicationDispenseTransformationError(
                "O campo de codificação deve ser um objeto FHIR quando presente."
            )
        return first_text_from_mappings(container.get("coding"), key)

    def _extract_nested_mapping(self, container: Any, key: str) -> Any:
        """
        Retorna um mapeamento aninhado quando existir.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise MedicationDispenseTransformationError(
                "O campo aninhado deve ser um objeto FHIR quando presente."
            )
        nested = container.get(key)
        if nested is None:
            return None
        if not isinstance(nested, Mapping):
            raise MedicationDispenseTransformationError(
                "O campo aninhado deve ser um objeto FHIR quando presente."
            )
        return nested
