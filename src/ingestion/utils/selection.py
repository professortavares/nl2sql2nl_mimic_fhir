"""
Utilitários para seleção do primeiro valor textual válido.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Mapping


def normalize_text(value: Any) -> str | None:
    """
    Normaliza um valor textual opcional.

    Parâmetros:
    ----------
    value : Any
        Valor a ser normalizado.

    Retorno:
    -------
    str | None
        Texto limpo ou `None` quando o valor não for textual.
    """

    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def first_non_empty_text(value: Any) -> str | None:
    """
    Retorna o primeiro texto não vazio encontrado em um valor ou coleção.

    Parâmetros:
    ----------
    value : Any
        Texto, lista ou tupla a ser inspecionada.

    Retorno:
    -------
    str | None
        O primeiro texto válido ou `None` quando nada útil for encontrado.
    """

    normalized = normalize_text(value)
    if normalized is not None:
        return normalized
    if isinstance(value, (list, tuple)):
        for item in value:
            normalized_item = first_non_empty_text(item)
            if normalized_item is not None:
                return normalized_item
    return None


def first_text_from_mappings(values: Any, key: str) -> str | None:
    """
    Retorna o primeiro texto não vazio de uma lista de mapeamentos.

    Parâmetros:
    ----------
    values : Any
        Coleção de mapeamentos FHIR.
    key : str
        Chave a ser lida em cada mapeamento.

    Retorno:
    -------
    str | None
        O primeiro texto válido encontrado.
    """

    if not isinstance(values, Iterable) or isinstance(values, (str, bytes, Mapping)):
        return None
    for item in values:
        if not isinstance(item, Mapping):
            continue
        normalized = first_non_empty_text(item.get(key))
        if normalized is not None:
            return normalized
    return None


def first_text_from_mappings_matching(
    values: Any,
    key: str,
    predicate: Callable[[Mapping[str, Any]], bool],
) -> str | None:
    """
    Retorna o primeiro texto não vazio de uma lista de mapeamentos que satisfaçam um predicado.

    Parâmetros:
    ----------
    values : Any
        Coleção de mapeamentos FHIR.
    key : str
        Chave a ser lida em cada mapeamento.
    predicate : Callable[[Mapping[str, Any]], bool]
        Função que decide se um item deve ser considerado.

    Retorno:
    -------
    str | None
        O primeiro texto válido encontrado.
    """

    if not isinstance(values, Iterable) or isinstance(values, (str, bytes, Mapping)):
        return None
    for item in values:
        if not isinstance(item, Mapping):
            continue
        if not predicate(item):
            continue
        normalized = first_non_empty_text(item.get(key))
        if normalized is not None:
            return normalized
    return None
