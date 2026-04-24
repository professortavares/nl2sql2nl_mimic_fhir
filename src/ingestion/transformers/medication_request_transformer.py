"""
Transformação de recursos FHIR `MedicationRequest` para a modelagem simplificada.
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

_RESOURCE_TYPE = "MedicationRequest"
_PATIENT_REFERENCE_TYPE = "Patient"
_ENCOUNTER_REFERENCE_TYPE = "Encounter"
_MEDICATION_REFERENCE_TYPE = "Medication"
_IDENTIFIER_SYSTEM_FRAGMENT = "medication-request"


class MedicationRequestTransformationError(ValueError):
    """Indica que um recurso MedicationRequest não passou na validação mínima."""


class MedicationRequestTransformer:
    """
    Converte recursos FHIR MedicationRequest em um dicionário relacional enxuto.

    A modelagem consolida o primeiro valor não vazio e válido encontrado para
    listas relevantes como `identifier[*]`, `dosageInstruction[*]`, `route.coding[*]`
    e `doseAndRate[*]`.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR MedicationRequest.

        Retorno:
        -------
        dict[str, Any]
            Registro pronto para persistência na tabela `medication_request`.

        Exceções:
        --------
        TypeError
            Quando a entrada não é um mapeamento.
        MedicationRequestTransformationError
            Quando a validação mínima falha.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise MedicationRequestTransformationError(
                f"resourceType inválido para MedicationRequest: {resource.get('resourceType')!r}"
            )

        medication_request_id = first_non_empty_text(resource.get("id"))
        if medication_request_id is None:
            raise MedicationRequestTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": medication_request_id,
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE),
            "encounter_id": self._extract_reference_id(resource.get("encounter"), _ENCOUNTER_REFERENCE_TYPE),
            "medication_id": self._extract_reference_id(
                resource.get("medicationReference"),
                _MEDICATION_REFERENCE_TYPE,
            ),
            "intent": first_non_empty_text(resource.get("intent")),
            "status": first_non_empty_text(resource.get("status")),
            "authored_on": first_non_empty_text(resource.get("authoredOn")),
            "identifier": self._extract_identifier(resource.get("identifier")),
            "validity_start": self._extract_validity_period_value(resource.get("dispenseRequest"), "start"),
            "validity_end": self._extract_validity_period_value(resource.get("dispenseRequest"), "end"),
            "dosage_text": self._extract_dosage_text(resource.get("dosageInstruction")),
            "route_code": self._extract_dosage_route_code(resource.get("dosageInstruction")),
            "frequency_code": self._extract_dosage_frequency_code(resource.get("dosageInstruction")),
            "dose_value": self._extract_dosage_dose_value(resource.get("dosageInstruction")),
            "dose_unit": self._extract_dosage_dose_unit(resource.get("dosageInstruction")),
        }

    def _extract_reference_id(self, reference_container: Any, expected_type: str) -> str | None:
        """
        Extrai o identificador de uma referência FHIR aninhada.
        """

        if reference_container is None:
            return None
        if not isinstance(reference_container, Mapping):
            raise MedicationRequestTransformationError(
                "A referência FHIR deve ser um objeto quando o campo estiver presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise MedicationRequestTransformationError("A referência FHIR está incompleta.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise MedicationRequestTransformationError(str(exc)) from exc

    def _extract_identifier(self, identifiers: Any) -> str | None:
        """
        Extrai o primeiro identificador útil do recurso.

        A busca prioriza o identificador com `system` relacionado ao recurso e,
        se não houver correspondência, usa o primeiro valor não vazio disponível.
        """

        by_system = first_text_from_mappings_matching(
            identifiers,
            "value",
            lambda item: self._system_matches(item.get("system")),
        )
        if by_system is not None:
            return by_system
        return first_text_from_mappings(identifiers, "value")

    def _extract_validity_period_value(self, dispense_request: Any, key: str) -> str | None:
        """
        Extrai `dispenseRequest.validityPeriod.start` ou `end`.
        """

        if dispense_request is None:
            return None
        if not isinstance(dispense_request, Mapping):
            raise MedicationRequestTransformationError(
                "O campo 'dispenseRequest' deve ser um objeto FHIR quando presente."
            )
        validity_period = dispense_request.get("validityPeriod")
        if validity_period is None:
            return None
        if not isinstance(validity_period, Mapping):
            raise MedicationRequestTransformationError(
                "O campo 'dispenseRequest.validityPeriod' deve ser um objeto FHIR quando presente."
            )
        return first_non_empty_text(validity_period.get(key))

    def _extract_dosage_text(self, dosage_instructions: Any) -> str | None:
        """
        Extrai o primeiro `dosageInstruction[*].text` válido encontrado.
        """

        return self._extract_from_dosage_instructions(
            dosage_instructions,
            lambda instruction: first_non_empty_text(instruction.get("text")),
        )

    def _extract_dosage_route_code(self, dosage_instructions: Any) -> str | None:
        """
        Extrai o primeiro `dosageInstruction[*].route.coding[*].code` válido encontrado.
        """

        return self._extract_from_dosage_instructions(
            dosage_instructions,
            lambda instruction: self._extract_first_coding_value(instruction.get("route"), "code"),
        )

    def _extract_dosage_frequency_code(self, dosage_instructions: Any) -> str | None:
        """
        Extrai o primeiro `dosageInstruction[*].timing.code.coding[*].code` válido encontrado.
        """

        return self._extract_from_dosage_instructions(
            dosage_instructions,
            lambda instruction: self._extract_first_coding_value(
                self._extract_nested_mapping(instruction.get("timing"), "code"),
                "code",
            ),
        )

    def _extract_dosage_dose_value(self, dosage_instructions: Any) -> str | None:
        """
        Extrai o primeiro `dosageInstruction[*].doseAndRate[*].doseQuantity.value` válido encontrado.
        """

        return self._extract_from_dosage_instructions(
            dosage_instructions,
            lambda instruction: self._extract_first_dose_quantity_value(instruction.get("doseAndRate"), "value"),
        )

    def _extract_dosage_dose_unit(self, dosage_instructions: Any) -> str | None:
        """
        Extrai o primeiro `dosageInstruction[*].doseAndRate[*].doseQuantity.unit` válido encontrado.
        """

        return self._extract_from_dosage_instructions(
            dosage_instructions,
            lambda instruction: self._extract_first_dose_quantity_value(instruction.get("doseAndRate"), "unit"),
        )

    def _extract_from_dosage_instructions(
        self,
        dosage_instructions: Any,
        extractor: Any,
    ) -> str | None:
        """
        Aplica um extrator sobre a lista `dosageInstruction[*]` e devolve o primeiro valor útil.
        """

        if dosage_instructions is None:
            return None
        if not isinstance(dosage_instructions, list):
            raise MedicationRequestTransformationError(
                "O campo 'dosageInstruction' deve ser uma lista quando presente."
            )
        for index, instruction in enumerate(dosage_instructions):
            if not isinstance(instruction, Mapping):
                raise MedicationRequestTransformationError(
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
            raise MedicationRequestTransformationError(
                "O campo de codificação deve ser um objeto FHIR quando presente."
            )
        return first_text_from_mappings(container.get("coding"), key)

    def _extract_nested_mapping(self, container: Any, key: str) -> Mapping[str, Any] | None:
        """
        Extrai um mapeamento aninhado, quando presente.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise MedicationRequestTransformationError(
                "O campo aninhado esperado deve ser um objeto FHIR quando presente."
            )
        nested = container.get(key)
        if nested is None:
            return None
        if not isinstance(nested, Mapping):
            raise MedicationRequestTransformationError(f"O campo '{key}' deve ser um objeto FHIR quando presente.")
        return nested

    def _extract_first_dose_quantity_value(self, dose_and_rate: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `doseAndRate[*].doseQuantity`.
        """

        if dose_and_rate is None:
            return None
        if not isinstance(dose_and_rate, list):
            raise MedicationRequestTransformationError(
                "O campo 'doseAndRate' deve ser uma lista quando presente."
            )
        for index, entry in enumerate(dose_and_rate):
            if not isinstance(entry, Mapping):
                raise MedicationRequestTransformationError(
                    f"Cada item de 'doseAndRate' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            dose_quantity = entry.get("doseQuantity")
            if dose_quantity is None:
                continue
            if not isinstance(dose_quantity, Mapping):
                raise MedicationRequestTransformationError(
                    "O campo 'doseQuantity' deve ser um objeto FHIR quando presente."
                )
            normalized = first_scalar_text(dose_quantity.get(key))
            if normalized is not None:
                return normalized
        return None

    def _system_matches(self, system: Any) -> bool:
        """
        Indica se o `system` corresponde ao identificador do recurso.
        """

        normalized_system = first_non_empty_text(system)
        if normalized_system is None:
            return False
        return _IDENTIFIER_SYSTEM_FRAGMENT in normalized_system.lower()
