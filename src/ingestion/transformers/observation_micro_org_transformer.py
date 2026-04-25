"""
Transformação de recursos FHIR `Observation` da camada microbiológica de organismo.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import first_non_empty_text, first_text_from_mappings

_RESOURCE_TYPE = "Observation"
_PATIENT_REFERENCE_TYPE = "Patient"
_OBSERVATION_REFERENCE_TYPE = "Observation"


class ObservationMicroOrgTransformationError(ValueError):
    """Indica que uma ObservationMicroOrg não passou na validação mínima."""


@dataclass(slots=True, frozen=True)
class ObservationMicroOrgTransformationResult:
    """Conjunto de linhas derivadas de um único ObservationMicroOrg."""

    observation_micro_org: dict[str, Any]
    observation_micro_org_has_member: list[dict[str, Any]]


class ObservationMicroOrgTransformer:
    """
    Converte recursos FHIR Observation em uma tabela principal simplificada e
    em relacionamentos enxutos com outras observações microbiológicas.
    """

    def transform(self, resource: Mapping[str, Any]) -> ObservationMicroOrgTransformationResult:
        """
        Transforma um recurso JSON carregado em memória.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise ObservationMicroOrgTransformationError(
                f"resourceType inválido para ObservationMicroOrg: {resource.get('resourceType')!r}"
            )

        observation_id = first_non_empty_text(resource.get("id"))
        if observation_id is None:
            raise ObservationMicroOrgTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        observation_micro_org = {
            "id": observation_id,
            "patient_id": self._extract_reference_id(resource.get("subject"), _PATIENT_REFERENCE_TYPE, "subject"),
            "derived_from_observation_micro_test_id": self._extract_derived_from_id(resource.get("derivedFrom")),
            "status": first_non_empty_text(resource.get("status")),
            "organism_code": self._extract_coding_value(resource.get("code"), "code"),
            "organism_code_display": self._extract_coding_value(resource.get("code"), "display"),
            "category_code": self._extract_category_value(resource.get("category"), "code"),
            "category_display": self._extract_category_value(resource.get("category"), "display"),
            "effective_at": first_non_empty_text(resource.get("effectiveDateTime")),
            "value_string": first_non_empty_text(resource.get("valueString")),
        }
        observation_micro_org_has_member = self._extract_has_member_rows(
            observation_id=observation_id,
            has_members=resource.get("hasMember"),
        )
        return ObservationMicroOrgTransformationResult(
            observation_micro_org=observation_micro_org,
            observation_micro_org_has_member=observation_micro_org_has_member,
        )

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
            raise ObservationMicroOrgTransformationError(
                f"O campo '{field_name}' deve ser um objeto FHIR quando presente."
            )
        reference = reference_container.get("reference")
        if reference is None:
            raise ObservationMicroOrgTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, expected_type)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ObservationMicroOrgTransformationError(str(exc)) from exc

    def _extract_derived_from_id(self, derived_from: Any) -> str | None:
        """
        Extrai o primeiro `derivedFrom[*].reference` útil e válido.
        """

        if derived_from is None:
            return None
        if isinstance(derived_from, Mapping):
            return self._extract_observation_reference(derived_from, "derivedFrom")
        if not isinstance(derived_from, list):
            raise ObservationMicroOrgTransformationError(
                "O campo 'derivedFrom' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, item in enumerate(derived_from):
            if not isinstance(item, Mapping):
                raise ObservationMicroOrgTransformationError(
                    f"Cada item de 'derivedFrom' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            reference = item.get("reference")
            if not isinstance(reference, str) or not reference.strip():
                continue
            try:
                return parse_fhir_reference(reference, _OBSERVATION_REFERENCE_TYPE)
            except (TypeError, ValueError, FhirReferenceParseError) as exc:
                raise ObservationMicroOrgTransformationError(
                    f"Referência inválida em 'derivedFrom[{index}].reference': {exc}"
                ) from exc
        return None

    def _extract_observation_reference(self, item: Mapping[str, Any], field_name: str) -> str | None:
        """
        Extrai uma referência `Observation/<id>` de um objeto FHIR único.
        """

        reference = item.get("reference")
        if reference is None:
            raise ObservationMicroOrgTransformationError(f"O campo '{field_name}.reference' é obrigatório.")
        try:
            return parse_fhir_reference(reference, _OBSERVATION_REFERENCE_TYPE)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise ObservationMicroOrgTransformationError(str(exc)) from exc

    def _extract_coding_value(self, container: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `code.coding[*]`.
        """

        if container is None:
            return None
        if not isinstance(container, Mapping):
            raise ObservationMicroOrgTransformationError("O campo 'code' deve ser um objeto FHIR quando presente.")
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
            raise ObservationMicroOrgTransformationError(
                "O campo 'category' deve ser um objeto FHIR ou uma lista quando presente."
            )
        for index, category in enumerate(categories):
            if not isinstance(category, Mapping):
                raise ObservationMicroOrgTransformationError(
                    f"Cada item de 'category' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            coding_value = self._extract_coding_value(category, key)
            if coding_value is not None:
                return coding_value
        return None

    def _extract_has_member_rows(
        self,
        *,
        observation_id: str,
        has_members: Any,
    ) -> list[dict[str, Any]]:
        """
        Extrai os relacionamentos de `hasMember[*].reference`.
        """

        if has_members is None:
            return []
        items = [has_members] if isinstance(has_members, Mapping) else has_members
        if not isinstance(items, list):
            raise ObservationMicroOrgTransformationError(
                "O campo 'hasMember' deve ser um objeto FHIR ou uma lista quando presente."
            )

        rows: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, Mapping):
                raise ObservationMicroOrgTransformationError(
                    f"Cada item de 'hasMember' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            reference = item.get("reference")
            if reference is None:
                raise ObservationMicroOrgTransformationError(f"O campo 'hasMember[{index}].reference' é obrigatório.")
            try:
                member_observation_id = parse_fhir_reference(reference, _OBSERVATION_REFERENCE_TYPE)
            except (TypeError, ValueError, FhirReferenceParseError) as exc:
                raise ObservationMicroOrgTransformationError(
                    f"Referência inválida em 'hasMember[{index}].reference': {exc}"
                ) from exc
            rows.append(
                {
                    "observation_micro_org_id": observation_id,
                    "member_observation_id": member_observation_id,
                }
            )
        return rows
