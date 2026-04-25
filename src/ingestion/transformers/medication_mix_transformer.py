"""
Transformação de recursos FHIR `MedicationMix` para a modelagem simplificada.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import (
    first_non_empty_text,
    first_text_from_mappings,
    first_text_from_mappings_matching,
)

_RESOURCE_TYPE = "Medication"
_IDENTIFIER_SYSTEM_FRAGMENT = "medication-mix"
_INGREDIENT_REFERENCE_TYPE = "Medication"


class MedicationMixTransformationError(ValueError):
    """Indica que um recurso MedicationMix não passou na validação mínima."""


@dataclass(slots=True, frozen=True)
class MedicationMixTransformationResult:
    """Conjunto de linhas derivadas de um único MedicationMix."""

    medication_mix: dict[str, Any]
    medication_mix_ingredients: list[dict[str, Any]]


class MedicationMixTransformer:
    """
    Converte recursos FHIR Medication em uma tabela principal simplificada e
    em relacionamentos enxutos com Medication.

    A modelagem preserva apenas `id`, `status`, `identifier` e os vínculos com
    ingredientes referenciados por `Medication/<id>`.
    """

    def transform(self, resource: Mapping[str, Any]) -> MedicationMixTransformationResult:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR MedicationMix.

        Retorno:
        -------
        MedicationMixTransformationResult
            Registro principal e relacionamentos com medicamentos.

        Exceções:
        --------
        TypeError
            Quando a entrada não é um mapeamento.
        MedicationMixTransformationError
            Quando a validação mínima falha.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise MedicationMixTransformationError(
                f"resourceType inválido para MedicationMix: {resource.get('resourceType')!r}"
            )

        medication_mix_id = first_non_empty_text(resource.get("id"))
        if medication_mix_id is None:
            raise MedicationMixTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        medication_mix = {
            "id": medication_mix_id,
            "status": first_non_empty_text(resource.get("status")),
            "identifier": self._extract_identifier(resource.get("identifier")),
        }
        medication_mix_ingredients = self._extract_ingredients(medication_mix_id, resource.get("ingredient"))
        return MedicationMixTransformationResult(
            medication_mix=medication_mix,
            medication_mix_ingredients=medication_mix_ingredients,
        )

    def _extract_identifier(self, identifiers: Any) -> str | None:
        """
        Extrai o primeiro identificador útil do recurso.

        A busca prioriza o identificador com `system` relacionado a medication-mix
        e, se não houver correspondência, usa o primeiro valor não vazio disponível.
        """

        by_system = first_text_from_mappings_matching(
            identifiers,
            "value",
            lambda item: self._system_matches(item.get("system")),
        )
        if by_system is not None:
            return by_system
        return first_text_from_mappings(identifiers, "value")

    def _extract_ingredients(
        self,
        medication_mix_id: str,
        ingredients: Any,
    ) -> list[dict[str, Any]]:
        """
        Extrai os relacionamentos entre o mix e os medicamentos componentes.
        """

        if ingredients is None:
            return []
        if not isinstance(ingredients, list):
            raise MedicationMixTransformationError("O campo 'ingredient' deve ser uma lista quando presente.")

        rows: list[dict[str, Any]] = []
        for index, ingredient in enumerate(ingredients):
            if not isinstance(ingredient, Mapping):
                raise MedicationMixTransformationError(
                    f"Cada item de 'ingredient' deve ser um objeto FHIR. Item inválido na posição {index}."
                )
            item_reference = ingredient.get("itemReference")
            if not isinstance(item_reference, Mapping):
                raise MedicationMixTransformationError(
                    f"Cada item de 'ingredient' deve conter 'itemReference'. Item inválido na posição {index}."
                )
            reference = item_reference.get("reference")
            if reference is None:
                raise MedicationMixTransformationError(
                    f"Cada item de 'ingredient.itemReference' deve possuir 'reference'. Item inválido na posição {index}."
                )
            try:
                medication_id = parse_fhir_reference(reference, _INGREDIENT_REFERENCE_TYPE)
            except (TypeError, ValueError, FhirReferenceParseError) as exc:
                raise MedicationMixTransformationError(
                    f"Referência inválida em 'ingredient[{index}].itemReference.reference': {exc}"
                ) from exc
            rows.append(
                {
                    "medication_mix_id": medication_mix_id,
                    "medication_id": medication_id,
                }
            )
        return rows

    def _system_matches(self, system: Any) -> bool:
        """
        Indica se o system corresponde ao identificador de medication mix.
        """

        normalized_system = first_non_empty_text(system)
        if normalized_system is None:
            return False
        return _IDENTIFIER_SYSTEM_FRAGMENT in normalized_system.lower()
