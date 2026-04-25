"""
Transformação de recursos FHIR `Patient` para a tabela simplificada.
"""

from __future__ import annotations

from typing import Any, Mapping

from src.ingestion.parsers.fhir_extensions import (
    extract_extension_value_code,
    extract_nested_extension_text,
    find_extension,
)
from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)
from src.ingestion.utils.selection import first_non_empty_text, first_text_from_mappings

_PATIENT_MANAGING_ORGANIZATION_TYPE = "Organization"
_RACE_EXTENSION_URL = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"
_ETHNICITY_EXTENSION_URL = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity"
_BIRTHSEX_EXTENSION_URL = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex"


class PatientTransformationError(ValueError):
    """Indica que um recurso Patient não passou na validação mínima."""


class PatientTransformer:
    """
    Converte recursos FHIR Patient em um dicionário relacional enxuto.
    """

    def transform(self, resource: Mapping[str, Any]) -> dict[str, Any]:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Patient.

        Retorno:
        -------
        dict[str, Any]
            Registro pronto para persistência na tabela `patient`.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        if resource.get("resourceType") != "Patient":
            raise PatientTransformationError(
                f"resourceType inválido para Patient: {resource.get('resourceType')!r}"
            )

        patient_id = first_non_empty_text(resource.get("id"))
        if patient_id is None:
            raise PatientTransformationError("O campo obrigatório 'id' está ausente ou vazio.")

        return {
            "id": patient_id,
            "gender": first_non_empty_text(resource.get("gender")),
            "birth_date": first_non_empty_text(resource.get("birthDate")),
            "name": self._extract_first_name_family(resource.get("name")),
            "identifier": self._extract_first_identifier(resource.get("identifier")),
            "marital_status_coding": self._extract_first_marital_status_code(
                resource.get("maritalStatus")
            ),
            "race": self._extract_extension_text(resource.get("extension"), _RACE_EXTENSION_URL),
            "ethnicity": self._extract_extension_text(
                resource.get("extension"),
                _ETHNICITY_EXTENSION_URL,
            ),
            "birthsex": self._extract_birthsex(resource.get("extension")),
            "managing_organization_id": self._extract_managing_organization_id(
                resource.get("managingOrganization")
            ),
        }

    def _extract_first_name_family(self, names: Any) -> str | None:
        """
        Extrai o primeiro `family` válido encontrado em `name[*]`.
        """

        if not isinstance(names, list):
            return None
        for name in names:
            if not isinstance(name, Mapping):
                continue
            family = first_non_empty_text(name.get("family"))
            if family is not None:
                return family
        return None

    def _extract_first_identifier(self, identifiers: Any) -> str | None:
        """
        Extrai o primeiro `value` válido encontrado em `identifier[*]`.
        """

        return first_text_from_mappings(identifiers, "value")

    def _extract_first_marital_status_code(self, marital_status: Any) -> str | None:
        """
        Extrai o primeiro `code` válido encontrado em `maritalStatus.coding[*]`.
        """

        if not isinstance(marital_status, Mapping):
            return None
        return first_text_from_mappings(marital_status.get("coding"), "code")

    def _extract_extension_text(self, extensions: Any, url: str) -> str | None:
        """
        Extrai o texto da extensão FHIR correspondente ao URL informado.
        """

        extension = find_extension(extensions, url)
        if extension is None:
            return None
        text_value = extract_nested_extension_text(extension)
        if text_value is not None:
            return text_value
        raise PatientTransformationError(
            f"A extensão {url!r} foi encontrada, mas não contém o texto esperado."
        )

    def _extract_birthsex(self, extensions: Any) -> str | None:
        """
        Extrai o `valueCode` da extensão US Core Birthsex.
        """

        extension = find_extension(extensions, _BIRTHSEX_EXTENSION_URL)
        if extension is None:
            return None
        value_code = extract_extension_value_code(extension)
        if value_code is not None:
            return value_code
        raise PatientTransformationError(
            f"A extensão {_BIRTHSEX_EXTENSION_URL!r} foi encontrada, mas não contém `valueCode`."
        )

    def _extract_managing_organization_id(self, managing_organization: Any) -> str | None:
        """
        Extrai o identificador da organização gestora.
        """

        if managing_organization is None:
            return None
        if not isinstance(managing_organization, Mapping):
            raise PatientTransformationError(
                "O campo 'managingOrganization' deve ser um objeto FHIR quando presente."
            )
        reference = managing_organization.get("reference")
        if reference is None:
            raise PatientTransformationError(
                "O campo 'managingOrganization.reference' é obrigatório quando a organização gestora está presente."
            )
        try:
            return parse_fhir_reference(reference, _PATIENT_MANAGING_ORGANIZATION_TYPE)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise PatientTransformationError(str(exc)) from exc
