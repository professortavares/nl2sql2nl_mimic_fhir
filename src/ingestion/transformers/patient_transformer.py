"""
Transformação de recursos FHIR `Patient` para linhas relacionais.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.ingestion.parsers.fhir_reference_parser import (
    FhirReferenceParseError,
    parse_fhir_reference,
)

_PATIENT_MANAGING_ORGANIZATION_TYPE = "Organization"
_RACE_EXTENSION_URL = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"
_ETHNICITY_EXTENSION_URL = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity"
_BIRTHSEX_EXTENSION_URL = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex"


class PatientTransformationError(ValueError):
    """Indica que um recurso Patient não passou na validação mínima."""


@dataclass(slots=True, frozen=True)
class PatientTransformationResult:
    """Conjunto de linhas derivadas de um único recurso Patient."""

    patient: dict[str, Any]
    meta_profiles: list[dict[str, Any]]
    names: list[dict[str, Any]]
    identifiers: list[dict[str, Any]]
    communication_language_codings: list[dict[str, Any]]
    marital_status_codings: list[dict[str, Any]]
    race: list[dict[str, Any]]
    ethnicity: list[dict[str, Any]]
    birthsex: list[dict[str, Any]]


class PatientTransformer:
    """
    Converte recursos FHIR Patient em estruturas relacionais normalizadas.
    """

    def transform(self, resource: Mapping[str, Any]) -> PatientTransformationResult:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Patient.

        Retorno:
        -------
        PatientTransformationResult
            Linhas prontas para persistência.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        resource_type = resource.get("resourceType")
        if resource_type != "Patient":
            raise PatientTransformationError(
                f"resourceType inválido para o pipeline de Patient: {resource_type!r}"
            )

        patient_id = self._require_text(resource.get("id"), field_name="id")
        patient = {
            "id": patient_id,
            "resource_type": "Patient",
            "gender": self._optional_text(resource.get("gender")),
            "birth_date": self._optional_text(resource.get("birthDate")),
            "managing_organization_id": self._extract_managing_organization_id(
                resource.get("managingOrganization")
            ),
        }

        meta_profiles = self._extract_meta_profiles(patient_id, resource.get("meta"))
        names = self._extract_names(patient_id, resource.get("name"))
        identifiers = self._extract_identifiers(patient_id, resource.get("identifier"))
        communication_language_codings = self._extract_communication_language_codings(
            patient_id,
            resource.get("communication"),
        )
        marital_status_codings = self._extract_marital_status_codings(
            patient_id,
            resource.get("maritalStatus"),
        )
        race = self._extract_race(patient_id, resource.get("extension"))
        ethnicity = self._extract_ethnicity(patient_id, resource.get("extension"))
        birthsex = self._extract_birthsex(patient_id, resource.get("extension"))

        return PatientTransformationResult(
            patient=patient,
            meta_profiles=meta_profiles,
            names=names,
            identifiers=identifiers,
            communication_language_codings=communication_language_codings,
            marital_status_codings=marital_status_codings,
            race=race,
            ethnicity=ethnicity,
            birthsex=birthsex,
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
            return None
        try:
            return parse_fhir_reference(reference, _PATIENT_MANAGING_ORGANIZATION_TYPE)
        except (TypeError, ValueError, FhirReferenceParseError) as exc:
            raise PatientTransformationError(str(exc)) from exc

    def _extract_meta_profiles(
        self,
        patient_id: str,
        meta: Any,
    ) -> list[dict[str, Any]]:
        """
        Extrai os perfis de `meta.profile`.
        """

        if not isinstance(meta, Mapping):
            return []
        profiles = meta.get("profile")
        if not isinstance(profiles, list):
            return []

        rows: list[dict[str, Any]] = []
        for profile in profiles:
            normalized_profile = self._optional_text(profile)
            if normalized_profile is not None:
                rows.append({"patient_id": patient_id, "profile": normalized_profile})
        return rows

    def _extract_names(self, patient_id: str, names: Any) -> list[dict[str, Any]]:
        """
        Extrai nomes do recurso `Patient`.
        """

        if not isinstance(names, list):
            return []

        rows: list[dict[str, Any]] = []
        for name in names:
            if not isinstance(name, Mapping):
                continue
            rows.append(
                {
                    "patient_id": patient_id,
                    "use": self._optional_text(name.get("use")),
                    "family": self._optional_text(name.get("family")),
                }
            )
        return rows

    def _extract_identifiers(self, patient_id: str, identifiers: Any) -> list[dict[str, Any]]:
        """
        Extrai a lista de identificadores do recurso.
        """

        if not isinstance(identifiers, list):
            return []

        rows: list[dict[str, Any]] = []
        for identifier in identifiers:
            if not isinstance(identifier, Mapping):
                continue
            rows.append(
                {
                    "patient_id": patient_id,
                    "system": self._optional_text(identifier.get("system")),
                    "value": self._optional_text(identifier.get("value")),
                }
            )
        return rows

    def _extract_communication_language_codings(
        self,
        patient_id: str,
        communication: Any,
    ) -> list[dict[str, Any]]:
        """
        Extrai os codings de `communication.language.coding`.
        """

        if not isinstance(communication, list):
            return []

        rows: list[dict[str, Any]] = []
        for entry in communication:
            if not isinstance(entry, Mapping):
                continue
            language = entry.get("language")
            if not isinstance(language, Mapping):
                continue
            codings = language.get("coding")
            if not isinstance(codings, list):
                continue
            for coding in codings:
                if not isinstance(coding, Mapping):
                    continue
                rows.append(
                    {
                        "patient_id": patient_id,
                        "system": self._optional_text(coding.get("system")),
                        "code": self._optional_text(coding.get("code")),
                    }
                )
        return rows

    def _extract_marital_status_codings(
        self,
        patient_id: str,
        marital_status: Any,
    ) -> list[dict[str, Any]]:
        """
        Extrai os codings de `maritalStatus.coding`.
        """

        if not isinstance(marital_status, Mapping):
            return []
        codings = marital_status.get("coding")
        if not isinstance(codings, list):
            return []

        rows: list[dict[str, Any]] = []
        for coding in codings:
            if not isinstance(coding, Mapping):
                continue
            rows.append(
                {
                    "patient_id": patient_id,
                    "system": self._optional_text(coding.get("system")),
                    "code": self._optional_text(coding.get("code")),
                }
            )
        return rows

    def _extract_race(self, patient_id: str, extensions: Any) -> list[dict[str, Any]]:
        """
        Extrai a extensão US Core Race.
        """

        extension = self._find_extension(extensions, _RACE_EXTENSION_URL)
        if extension is None:
            return []

        category = self._extract_omb_category(extension)
        text_value = self._extract_text_value(extension)
        return [
            {
                "patient_id": patient_id,
                "omb_category_system": category.get("system"),
                "omb_category_code": category.get("code"),
                "omb_category_display": category.get("display"),
                "text": text_value,
            }
        ]

    def _extract_ethnicity(self, patient_id: str, extensions: Any) -> list[dict[str, Any]]:
        """
        Extrai a extensão US Core Ethnicity.
        """

        extension = self._find_extension(extensions, _ETHNICITY_EXTENSION_URL)
        if extension is None:
            return []

        category = self._extract_omb_category(extension)
        text_value = self._extract_text_value(extension)
        return [
            {
                "patient_id": patient_id,
                "omb_category_system": category.get("system"),
                "omb_category_code": category.get("code"),
                "omb_category_display": category.get("display"),
                "text": text_value,
            }
        ]

    def _extract_birthsex(self, patient_id: str, extensions: Any) -> list[dict[str, Any]]:
        """
        Extrai a extensão US Core Birthsex.
        """

        extension = self._find_extension(extensions, _BIRTHSEX_EXTENSION_URL)
        if extension is None:
            return []
        value_code = self._optional_text(extension.get("valueCode")) if isinstance(extension, Mapping) else None
        return [{"patient_id": patient_id, "value_code": value_code}]

    def _find_extension(self, extensions: Any, expected_url: str) -> Mapping[str, Any] | None:
        """
        Localiza uma extensão pelo URL esperado.
        """

        if not isinstance(extensions, list):
            return None
        for extension in extensions:
            if isinstance(extension, Mapping) and extension.get("url") == expected_url:
                return extension
        return None

    def _extract_omb_category(self, extension: Mapping[str, Any]) -> dict[str, str | None]:
        """
        Extrai `ombCategory.valueCoding` de uma extensão US Core.
        """

        nested_extensions = extension.get("extension")
        if not isinstance(nested_extensions, list):
            return {"system": None, "code": None, "display": None}

        for nested_extension in nested_extensions:
            if not isinstance(nested_extension, Mapping):
                continue
            if nested_extension.get("url") != "ombCategory":
                continue
            value_coding = nested_extension.get("valueCoding")
            if not isinstance(value_coding, Mapping):
                return {"system": None, "code": None, "display": None}
            return {
                "system": self._optional_text(value_coding.get("system")),
                "code": self._optional_text(value_coding.get("code")),
                "display": self._optional_text(value_coding.get("display")),
            }
        return {"system": None, "code": None, "display": None}

    def _extract_text_value(self, extension: Mapping[str, Any]) -> str | None:
        """
        Extrai o texto da extensão US Core.
        """

        nested_extensions = extension.get("extension")
        if not isinstance(nested_extensions, list):
            return None

        for nested_extension in nested_extensions:
            if not isinstance(nested_extension, Mapping):
                continue
            if nested_extension.get("url") != "text":
                continue
            return self._optional_text(nested_extension.get("valueString"))
        return None

    def _require_text(self, value: Any, *, field_name: str) -> str:
        """
        Valida se um campo obrigatório contém texto não vazio.
        """

        normalized = self._optional_text(value)
        if normalized is None:
            raise PatientTransformationError(
                f"O campo obrigatório '{field_name}' está ausente ou vazio."
            )
        return normalized

    def _optional_text(self, value: Any) -> str | None:
        """
        Normaliza valores opcionais para texto limpo ou `None`.
        """

        if value is None or not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None

