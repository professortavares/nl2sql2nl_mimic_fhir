"""
Funções auxiliares para extrair extensões FHIR específicas do MIMIC.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Mapping

from src.ingestion.utils.selection import normalize_text


def find_extension(extensions: Any, url: str) -> Mapping[str, Any] | None:
    """
    Localiza uma extensão FHIR pelo URL.

    Parâmetros:
    ----------
    extensions : Any
        Lista de extensões FHIR.
    url : str
        URL da extensão desejada.

    Retorno:
    -------
    Mapping[str, Any] | None
        Extensão correspondente ou `None` quando não encontrada.
    """

    if not isinstance(extensions, Iterable) or isinstance(extensions, (str, bytes, Mapping)):
        return None
    for extension in extensions:
        if isinstance(extension, Mapping) and extension.get("url") == url:
            return extension
    return None


def extract_nested_extension_text(extension: Mapping[str, Any]) -> str | None:
    """
    Extrai o texto armazenado em uma extensão do tipo US Core Race/Ethnicity.

    A estrutura esperada é uma lista em `extension`, contendo um item com
    `url == "text"` e o valor em `valueString`.
    """

    nested_extensions = extension.get("extension")
    if not isinstance(nested_extensions, Iterable) or isinstance(
        nested_extensions, (str, bytes, Mapping)
    ):
        return None
    for nested_extension in nested_extensions:
        if not isinstance(nested_extension, Mapping):
            continue
        if nested_extension.get("url") != "text":
            continue
        normalized = normalize_text(nested_extension.get("valueString"))
        if normalized is not None:
            return normalized
    return None


def extract_extension_value_code(extension: Mapping[str, Any]) -> str | None:
    """
    Extrai o campo `valueCode` de uma extensão FHIR.
    """

    return normalize_text(extension.get("valueCode"))
