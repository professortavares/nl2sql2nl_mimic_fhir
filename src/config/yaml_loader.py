"""
Funções utilitárias para leitura de arquivos YAML.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml_file(path: Path) -> dict[str, Any]:
    """
    Carrega um arquivo YAML como dicionário.

    Parâmetros:
    ----------
    path : Path
        Caminho do arquivo YAML.

    Retorno:
    -------
    dict[str, Any]
        Conteúdo carregado.

    Exceções:
    --------
    FileNotFoundError
        Quando o arquivo não existe.
    ValueError
        Quando o conteúdo não é um mapeamento YAML válido.
    """

    if not path.exists():
        raise FileNotFoundError(f"Arquivo YAML não encontrado: {path}")

    content = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(content, dict):
        raise ValueError(f"O arquivo YAML deve conter um mapeamento: {path}")
    return content

