"""
Transformação de recursos FHIR `Organization` para linhas relacionais.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class OrganizationTransformationError(ValueError):
    """Indica que um recurso Organization não passou na validação mínima."""


@dataclass(slots=True, frozen=True)
class OrganizationTransformationResult:
    """Conjunto de linhas derivadas de um único recurso Organization."""

    organization: dict[str, Any]
    meta_profiles: list[dict[str, Any]]
    identifiers: list[dict[str, Any]]
    type_codings: list[dict[str, Any]]


class OrganizationTransformer:
    """
    Converte recursos FHIR Organization em estruturas relacionais normalizadas.
    """

    def transform(self, resource: Mapping[str, Any]) -> OrganizationTransformationResult:
        """
        Transforma um recurso JSON carregado em memória.

        Parâmetros:
        ----------
        resource : Mapping[str, Any]
            Dicionário representando um recurso FHIR Organization.

        Retorno:
        -------
        OrganizationTransformationResult
            Linhas prontas para persistência.

        Exceções:
        --------
        TypeError
            Quando a entrada não é mapeável.
        OrganizationTransformationError
            Quando a validação mínima falha.
        """

        if not isinstance(resource, Mapping):
            raise TypeError("O recurso deve ser um mapeamento JSON.")

        resource_type = resource.get("resourceType")
        if resource_type != "Organization":
            raise OrganizationTransformationError(
                f"resourceType inválido para o pipeline de Organization: {resource_type!r}"
            )

        organization_id = self._require_text(resource.get("id"), field_name="id")
        active = resource.get("active")
        if active is not None and not isinstance(active, bool):
            raise OrganizationTransformationError("O campo 'active' precisa ser booleano quando presente.")

        organization = {
            "id": organization_id,
            "resource_type": "Organization",
            "active": active,
            "name": self._optional_text(resource.get("name")),
        }

        meta_profiles = self._extract_meta_profiles(organization_id, resource.get("meta"))
        identifiers = self._extract_identifiers(organization_id, resource.get("identifier"))
        type_codings = self._extract_type_codings(organization_id, resource.get("type"))

        return OrganizationTransformationResult(
            organization=organization,
            meta_profiles=meta_profiles,
            identifiers=identifiers,
            type_codings=type_codings,
        )

    def _extract_meta_profiles(
        self,
        organization_id: str,
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
                rows.append(
                    {
                        "organization_id": organization_id,
                        "profile": normalized_profile,
                    }
                )
        return rows

    def _extract_identifiers(
        self,
        organization_id: str,
        identifiers: Any,
    ) -> list[dict[str, Any]]:
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
                    "organization_id": organization_id,
                    "system": self._optional_text(identifier.get("system")),
                    "value": self._optional_text(identifier.get("value")),
                }
            )
        return rows

    def _extract_type_codings(
        self,
        organization_id: str,
        organization_types: Any,
    ) -> list[dict[str, Any]]:
        """
        Extrai os codings aninhados em `type[].coding[]`.
        """

        if not isinstance(organization_types, list):
            return []

        rows: list[dict[str, Any]] = []
        for organization_type in organization_types:
            if not isinstance(organization_type, Mapping):
                continue
            codings = organization_type.get("coding")
            if not isinstance(codings, list):
                continue
            for coding in codings:
                if not isinstance(coding, Mapping):
                    continue
                rows.append(
                    {
                        "organization_id": organization_id,
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
            raise OrganizationTransformationError(
                f"O campo obrigatório '{field_name}' está ausente ou vazio."
            )
        return normalized

    def _optional_text(self, value: Any) -> str | None:
        """
        Normaliza valores opcionais para texto limpo ou `None`.
        """

        if value is None:
            return None
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None

