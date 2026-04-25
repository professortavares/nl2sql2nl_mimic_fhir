"""
Transformação de recursos FHIR `Specimen` para a modelagem simplificada.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import first_non_empty_text, first_text_from_mappings

_RESOURCE_TYPE = "Specimen"
_EXPECTED_REFERENCE_TYPE = "Patient"


class SpecimenTransformationError(ValueError):
    """Indica que um recurso Specimen não passou na validação mínima."""


class SpecimenTransformer:
    """
    Converte recursos FHIR Specimen em um dicionário relacional enxuto.

    A transformação preserva apenas os campos analiticamente úteis:
    `id`, `patient_id`, `specimen_type_code`, `specimen_type_display`,
    `collected_at` e `identifier`.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Specimen.

        Retorno:
        -------
        dict[str, Any]
            Registro pronto para persistência na tabela `specimen`.

        Exceções:
        --------
        TypeError
            Quando a entrada não é um mapeamento.
        SpecimenTransformationError
            Quando a validação mínima falha.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != _RESOURCE_TYPE:
            raise SpecimenTransformationError(
                f"resourceType inválido para Specimen: {resource.get('resourceType')!r}"
            )

        specimen_id = first_non_empty_text(resource.get("id"))
        if specimen_id is None:
            raise SpecimenTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": specimen_id,
            "patient_id": self._extract_patient_id(resource.get("subject")),
            "specimen_type_code": self._extract_type_value(resource.get("type"), "code"),
            "specimen_type_display": self._extract_type_value(resource.get("type"), "display"),
            "collected_at": self._extract_collected_at(resource.get("collection")),
            "identifier": self._extract_identifier(resource.get("identifier")),
        }

    def _extract_patient_id(self, subject: Any) -> str | None:
        """
        Extrai o identificador do paciente a partir de `subject.reference`.
        """

        if subject is None:
            return None
        if not isinstance(subject, Mapping):
            raise SpecimenTransformationError("O campo 'subject' deve ser um objeto FHIR quando presente.")
        reference = subject.get("reference")
        if reference is None:
            raise SpecimenTransformationError(
                "O campo 'subject.reference' é obrigatório quando o sujeito está presente."
            )
        try:
            return parse_fhir_reference(reference, _EXPECTED_REFERENCE_TYPE)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise SpecimenTransformationError(str(exc)) from exc

    def _extract_type_value(self, specimen_type: Any, key: str) -> str | None:
        """
        Extrai o primeiro valor útil de `type.coding[*]`.
        """

        if specimen_type is None:
            return None
        if not isinstance(specimen_type, Mapping):
            raise SpecimenTransformationError("O campo 'type' deve ser um objeto FHIR quando presente.")
        return first_text_from_mappings(specimen_type.get("coding"), key)

    def _extract_collected_at(self, collection: Any) -> str | None:
        """
        Extrai `collection.collectedDateTime`.
        """

        if collection is None:
            return None
        if not isinstance(collection, Mapping):
            raise SpecimenTransformationError("O campo 'collection' deve ser um objeto FHIR quando presente.")
        return first_non_empty_text(collection.get("collectedDateTime"))

    def _extract_identifier(self, identifiers: Any) -> str | None:
        """
        Extrai o primeiro identificador útil do recurso.
        """

        return first_text_from_mappings(identifiers, "value")
