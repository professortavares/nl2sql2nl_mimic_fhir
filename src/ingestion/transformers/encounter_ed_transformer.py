"""
Transformação de recursos FHIR `Encounter` da subfase de emergência.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import first_non_empty_text, first_text_from_mappings

_PATIENT_REFERENCE_TYPE = "Patient"
_ORGANIZATION_REFERENCE_TYPE = "Organization"
_ENCOUNTER_REFERENCE_TYPE = "Encounter"


class EncounterEDTransformationError(ValueError):
    """Indica que um recurso EncounterED não passou na validação mínima."""


@dataclass(slots=True, frozen=True)
class EncounterEDTransformationResult:
    """Conjunto de linhas derivadas de um único EncounterED."""

    encounter_ed: dict[str, Any]


class EncounterEDTransformer:
    """
    Converte recursos FHIR Encounter para a tabela especializada de emergência.
    """

    def transform(self, resource: Mapping[str, Any]) -> EncounterEDTransformationResult:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Encounter da subfase ED.

        Retorno:
        -------
        EncounterEDTransformationResult
            Registro pronto para persistência na tabela `encounter_ed`.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != "Encounter":
            raise EncounterEDTransformationError(
                f"resourceType inválido para EncounterED: {resource.get('resourceType')!r}"
            )

        encounter_ed_id = first_non_empty_text(resource.get("id"))
        if encounter_ed_id is None:
            raise EncounterEDTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        encounter_ed = {
            "id": encounter_ed_id,
            "encounter_id": self._extract_reference_id(resource.get("partOf"), _ENCOUNTER_REFERENCE_TYPE),
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE),
            "organization_id": self._extract_reference_id(
                resource.get("serviceProvider"),
                _ORGANIZATION_REFERENCE_TYPE,
            ),
            "status": first_non_empty_text(resource.get("status")),
            "class_code": self._extract_class_code(resource.get("class")),
            "start_date": self._extract_period_value(resource.get("period"), "start"),
            "end_date": self._extract_period_value(resource.get("period"), "end"),
            "admit_source_code": self._extract_first_coding_value(
                self._extract_nested_mapping(resource.get("hospitalization"), "admitSource"),
                "code",
            ),
            "discharge_disposition_code": self._extract_first_coding_value(
                self._extract_nested_mapping(resource.get("hospitalization"), "dischargeDisposition"),
                "code",
            ),
            "identifier": self._extract_first_identifier(resource.get("identifier")),
        }

        return EncounterEDTransformationResult(encounter_ed=encounter_ed)

    def _extract_first_identifier(self, identifiers: Any) -> str | None:
        """
        Extrai o primeiro `identifier[*].value` válido encontrado.
        """

        return first_text_from_mappings(identifiers, "value")

    def _extract_first_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor válido de uma lista `coding[*]`.
        """

        if not isinstance(container, Mapping):
            return None
        return first_text_from_mappings(container.get("coding"), key)

    def _extract_class_code(self, encounter_class: Any) -> str | None:
        """
        Extrai `class.code` do recurso EncounterED.
        """

        if not isinstance(encounter_class, Mapping):
            return None
        return first_non_empty_text(encounter_class.get("code"))

    def _extract_period_value(self, period: Any, key: str) -> str | None:
        """
        Extrai `period.start` ou `period.end`.
        """

        if not isinstance(period, Mapping):
            return None
        return first_non_empty_text(period.get(key))

    def _extract_nested_mapping(self, container: Any, key: str) -> Mapping[str, Any] | None:
        """
        Extrai um mapeamento aninhado, quando presente.
        """

        if not isinstance(container, Mapping):
            return None
        nested = container.get(key)
        if nested is None:
            return None
        if not isinstance(nested, Mapping):
            raise EncounterEDTransformationError(
                f"O campo '{key}' deve ser um objeto FHIR quando presente."
            )
        return nested

    def _extract_reference_id(self, reference_container: Any, expected_type: str) -> str | None:
        """
        Extrai o identificador de uma referência FHIR aninhada.
        """

        if reference_container is None:
            return None
        if not isinstance(reference_container, Mapping):
            raise EncounterEDTransformationError(
                "A referência FHIR deve ser um objeto quando o campo estiver presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise EncounterEDTransformationError("A referência FHIR está incompleta.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise EncounterEDTransformationError(str(exc)) from exc
