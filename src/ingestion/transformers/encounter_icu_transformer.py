"""
Transformação de recursos FHIR `Encounter` da subfase de UTI.
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
_ENCOUNTER_REFERENCE_TYPE = "Encounter"
_LOCATION_REFERENCE_TYPE = "Location"


class EncounterICUTransformationError(ValueError):
    """Indica que um recurso EncounterICU não passou na validação mínima."""


@dataclass(slots=True, frozen=True)
class EncounterICUTransformationResult:
    """Conjunto de linhas derivadas de um único EncounterICU."""

    encounter_icu: dict[str, Any]
    encounter_icu_locations: list[dict[str, Any]]


class EncounterICUTransformer:
    """
    Converte recursos FHIR Encounter em estruturas relacionais enxutas para ICU.
    """

    def transform(self, resource: Mapping[str, Any]) -> EncounterICUTransformationResult:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Encounter da subfase ICU.

        Retorno:
        -------
        EncounterICUTransformationResult
            Registro principal e suas localizações associadas.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != "Encounter":
            raise EncounterICUTransformationError(
                f"resourceType inválido para EncounterICU: {resource.get('resourceType')!r}"
            )

        encounter_icu_id = first_non_empty_text(resource.get("id"))
        if encounter_icu_id is None:
            raise EncounterICUTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        encounter_icu = {
            "id": encounter_icu_id,
            "encounter_id": self._extract_reference_id(resource.get("partOf"), _ENCOUNTER_REFERENCE_TYPE),
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE),
            "status": first_non_empty_text(resource.get("status")),
            "class_code": self._extract_class_code(resource.get("class")),
            "start_date": self._extract_period_value(resource.get("period"), "start"),
            "end_date": self._extract_period_value(resource.get("period"), "end"),
            "identifier": self._extract_first_identifier(resource.get("identifier")),
        }

        encounter_icu_locations = self._extract_encounter_icu_locations(
            encounter_icu_id,
            resource.get("location"),
        )
        return EncounterICUTransformationResult(
            encounter_icu=encounter_icu,
            encounter_icu_locations=encounter_icu_locations,
        )

    def _extract_first_identifier(self, identifiers: Any) -> str | None:
        """
        Extrai o primeiro `identifier[*].value` válido encontrado.
        """

        return first_text_from_mappings(identifiers, "value")

    def _extract_class_code(self, encounter_class: Any) -> str | None:
        """
        Extrai `class.code` do recurso EncounterICU.
        """

        if not isinstance(encounter_class, Mapping):
            return None
        return first_non_empty_text(encounter_class.get("code"))

    def _extract_period_value(self, period: Any, key: str) -> str | None:
        """
        Extrai `period.start` ou `period.end`.
        """

        if period is None:
            return None
        if not isinstance(period, Mapping):
            raise EncounterICUTransformationError(
                "O campo 'period' deve ser um objeto FHIR quando presente."
            )
        return first_non_empty_text(period.get(key))

    def _extract_reference_id(self, reference_container: Any, expected_type: str) -> str | None:
        """
        Extrai o identificador de uma referência FHIR aninhada.
        """

        if reference_container is None:
            return None
        if not isinstance(reference_container, Mapping):
            raise EncounterICUTransformationError(
                "A referência FHIR deve ser um objeto quando o campo estiver presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise EncounterICUTransformationError("A referência FHIR está incompleta.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise EncounterICUTransformationError(str(exc)) from exc

    def _extract_encounter_icu_locations(
        self,
        encounter_icu_id: str,
        locations: Any,
    ) -> list[dict[str, Any]]:
        """
        Extrai as localizações associadas ao encounter ICU.
        """

        if locations is None:
            return []
        if not isinstance(locations, list):
            raise EncounterICUTransformationError("O campo 'location' deve ser uma lista quando presente.")

        rows: list[dict[str, Any]] = []
        for location_entry in locations:
            if not isinstance(location_entry, Mapping):
                raise EncounterICUTransformationError("Cada item de 'location' deve ser um objeto FHIR.")
            location_container = location_entry.get("location")
            if not isinstance(location_container, Mapping):
                raise EncounterICUTransformationError("Cada item de 'location' deve conter o objeto 'location'.")
            reference = location_container.get("reference")
            if reference is None:
                raise EncounterICUTransformationError("Cada item de 'location.location' deve possuir 'reference'.")
            try:
                location_id = parse_fhir_reference(reference, _LOCATION_REFERENCE_TYPE)
            except (TypeError, ValueError, FhirReferenceParseError) as exc:
                raise EncounterICUTransformationError(str(exc)) from exc
            period = location_entry.get("period")
            rows.append(
                {
                    "encounter_icu_id": encounter_icu_id,
                    "location_id": location_id,
                    "start_date": self._extract_period_value(period, "start"),
                    "end_date": self._extract_period_value(period, "end"),
                }
            )
        return rows
