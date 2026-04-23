"""
Transformação de recursos FHIR `Encounter` para a modelagem simplificada.
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
_LOCATION_REFERENCE_TYPE = "Location"


class EncounterTransformationError(ValueError):
    """Indica que um recurso Encounter não passou na validação mínima."""


@dataclass(slots=True, frozen=True)
class EncounterTransformationResult:
    """Conjunto de linhas derivadas de um único Encounter."""

    encounter: dict[str, Any]
    encounter_locations: list[dict[str, Any]]


class EncounterTransformer:
    """
    Converte recursos FHIR Encounter em estruturas relacionais enxutas.
    """

    def transform(self, resource: Mapping[str, Any]) -> EncounterTransformationResult:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Encounter.

        Retorno:
        -------
        EncounterTransformationResult
            Registro principal e suas localizações associadas.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != "Encounter":
            raise EncounterTransformationError(
                f"resourceType inválido para Encounter: {resource.get('resourceType')!r}"
            )

        encounter_id = first_non_empty_text(resource.get("id"))
        if encounter_id is None:
            raise EncounterTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        encounter = {
            "id": encounter_id,
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE),
            "organization_id": self._extract_organization_id(resource.get("serviceProvider")),
            "status": first_non_empty_text(resource.get("status")),
            "class_code": self._extract_class_code(resource.get("class")),
            "start_date": self._extract_period_value(resource.get("period"), "start"),
            "end_date": self._extract_period_value(resource.get("period"), "end"),
            "priority_code": self._extract_first_coding_value(resource.get("priority"), "code"),
            "service_type_code": self._extract_first_coding_value(resource.get("serviceType"), "code"),
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

        encounter_locations = self._extract_encounter_locations(encounter_id, resource.get("location"))
        return EncounterTransformationResult(encounter=encounter, encounter_locations=encounter_locations)

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
        Extrai `class.code` do recurso Encounter.
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
            raise EncounterTransformationError(f"O campo '{key}' deve ser um objeto FHIR quando presente.")
        return nested

    def _extract_reference_id(self, reference_container: Any, expected_type: str) -> str | None:
        """
        Extrai o identificador de uma referência FHIR aninhada.
        """

        if reference_container is None:
            return None
        if not isinstance(reference_container, Mapping):
            raise EncounterTransformationError(
                "A referência FHIR deve ser um objeto quando o campo estiver presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise EncounterTransformationError("A referência FHIR está incompleta.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise EncounterTransformationError(str(exc)) from exc

    def _extract_organization_id(self, reference_container: Any) -> str | None:
        """
        Extrai a referência da organização responsável pelo encounter.
        """

        return self._extract_reference_id(reference_container, _ORGANIZATION_REFERENCE_TYPE)

    def _extract_encounter_locations(
        self,
        encounter_id: str,
        locations: Any,
    ) -> list[dict[str, Any]]:
        """
        Extrai as localizações associadas ao encounter.
        """

        if locations is None:
            return []
        if not isinstance(locations, list):
            raise EncounterTransformationError("O campo 'location' deve ser uma lista quando presente.")

        rows: list[dict[str, Any]] = []
        for location_entry in locations:
            if not isinstance(location_entry, Mapping):
                raise EncounterTransformationError("Cada item de 'location' deve ser um objeto FHIR.")
            location_container = location_entry.get("location")
            if not isinstance(location_container, Mapping):
                raise EncounterTransformationError("Cada item de 'location' deve conter o objeto 'location'.")
            reference = location_container.get("reference")
            if reference is None:
                raise EncounterTransformationError("Cada item de 'location.location' deve possuir 'reference'.")
            try:
                location_id = parse_fhir_reference(reference, _LOCATION_REFERENCE_TYPE)
            except (TypeError, ValueError, FhirReferenceParseError) as exc:
                raise EncounterTransformationError(str(exc)) from exc
            period = location_entry.get("period")
            rows.append(
                {
                    "encounter_id": encounter_id,
                    "location_id": location_id,
                    "start_date": self._extract_period_value(period, "start"),
                    "end_date": self._extract_period_value(period, "end"),
                }
            )
        return rows
