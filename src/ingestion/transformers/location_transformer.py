"""
Transformação de recursos FHIR `Location` para linhas relacionais.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

_MANAGING_ORGANIZATION_REFERENCE_PATTERN = re.compile(
    r"^Organization/(?P<organization_id>[A-Za-z0-9\-\.]{1,64})$"
)


class LocationTransformationError(ValueError):
    """Indica que um recurso Location não passou na validação mínima."""


@dataclass(slots=True, frozen=True)
class LocationTransformationResult:
    """Conjunto de linhas derivadas de um único recurso Location."""

    location: dict[str, Any]
    meta_profiles: list[dict[str, Any]]
    physical_type_codings: list[dict[str, Any]]


def parse_managing_organization_reference(reference: str) -> str:
    """
    Extrai o identificador da organização a partir de uma referência FHIR.

    Parâmetros:
    ----------
    reference : str
        Referência no formato `Organization/<id>`.

    Retorno:
    -------
    str
        Identificador da organização referenciada.

    Exceções:
    --------
    TypeError
        Quando `reference` não é string.
    ValueError
        Quando o formato não corresponde ao padrão esperado.

    Exemplos de uso:
    ----------------
    parse_managing_organization_reference("Organization/abc123")
    """

    if not isinstance(reference, str):
        raise TypeError("A referência de organização deve ser uma string.")

    normalized_reference = reference.strip()
    match = _MANAGING_ORGANIZATION_REFERENCE_PATTERN.fullmatch(normalized_reference)
    if match is None:
        raise ValueError(
            "A referência managingOrganization.reference deve seguir o formato 'Organization/<id>'."
        )
    return match.group("organization_id")


class LocationTransformer:
    """
    Converte recursos FHIR Location em estruturas relacionais normalizadas.
    """

    def transform(self, resource: Mapping[str, Any]) -> LocationTransformationResult:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Location.

        Retorno:
        -------
        LocationTransformationResult
            Linhas prontas para persistência.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        resource_type = resource.get("resourceType")
        if resource_type != "Location":
            raise LocationTransformationError(
                f"resourceType inválido para o pipeline de Location: {resource_type!r}"
            )

        location_id = self._require_text(resource.get("id"), field_name="id")
        status = self._optional_text(resource.get("status"))
        name = self._optional_text(resource.get("name"))
        managing_organization_id = self._extract_managing_organization_id(resource.get("managingOrganization"))

        location = {
            "id": location_id,
            "resource_type": "Location",
            "name": name,
            "status": status,
            "managing_organization_id": managing_organization_id,
        }

        meta_profiles = self._extract_meta_profiles(location_id, resource.get("meta"))
        physical_type_codings = self._extract_physical_type_codings(
            location_id,
            resource.get("physicalType"),
        )

        return LocationTransformationResult(
            location=location,
            meta_profiles=meta_profiles,
            physical_type_codings=physical_type_codings,
        )

    def _extract_managing_organization_id(self, managing_organization: Any) -> str | None:
        """
        Extrai o identificador da organização gestora.
        """

        if managing_organization is None:
            return None
        if not isinstance(managing_organization, Mapping):
            raise LocationTransformationError(
                "O campo 'managingOrganization' deve ser um objeto FHIR quando presente."
            )
        reference = managing_organization.get("reference")
        if reference is None:
            raise LocationTransformationError(
                "O campo 'managingOrganization.reference' é obrigatório quando a organização gestora está presente."
            )
        try:
            return parse_managing_organization_reference(reference)
        except (TypeError, ValueError) as exc:
            raise LocationTransformationError(str(exc)) from exc

    def _extract_meta_profiles(
        self,
        location_id: str,
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
                rows.append({"location_id": location_id, "profile": normalized_profile})
        return rows

    def _extract_physical_type_codings(
        self,
        location_id: str,
        physical_type: Any,
    ) -> list[dict[str, Any]]:
        """
        Extrai os codings de `physicalType.coding`.
        """

        if not isinstance(physical_type, Mapping):
            return []
        codings = physical_type.get("coding")
        if not isinstance(codings, list):
            return []

        rows: list[dict[str, Any]] = []
        for coding in codings:
            if not isinstance(coding, Mapping):
                continue
            rows.append(
                {
                    "location_id": location_id,
                    "system": self._optional_text(coding.get("system")),
                    "code": self._optional_text(coding.get("code")),
                    "display": self._optional_text(coding.get("display")),
                }
            )
        return rows

    def _require_text(self, value: Any, *, field_name: str) -> str:
        """
        Valida se um campo obrigatório contém texto não vazio.
        """

        normalized = self._optional_text(value)
        if normalized is None:
            raise LocationTransformationError(
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

