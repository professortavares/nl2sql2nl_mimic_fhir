"""
Leitura incremental de arquivos NDJSON compactados com gzip.
"""

from __future__ import annotations

import gzip
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(slots=True, frozen=True)
class RawNdjsonLine:
    """Linha bruta lida de um arquivo NDJSON."""

    line_number: int
    content: str


class NdjsonGzipReader:
    """
    Lê um arquivo `.ndjson.gz` linha a linha sem materializar todo o conteúdo.
    """

    def __init__(self, file_path: Path) -> None:
        """
        Inicializa o leitor.

        Parâmetros:
        ----------
        file_path : Path
            Caminho do arquivo de entrada.
        """

        self._file_path = file_path

    @property
    def file_path(self) -> Path:
        """Retorna o caminho de entrada associado ao leitor."""

        return self._file_path

    def validate(self) -> None:
        """
        Valida a existência e a extensão esperada do arquivo.

        Exceções:
        --------
        FileNotFoundError
            Quando o arquivo não existe.
        ValueError
            Quando a extensão não segue o padrão `.ndjson.gz`.
        """

        if not self._file_path.exists():
            raise FileNotFoundError(f"Arquivo de entrada não encontrado: {self._file_path}")
        if self._file_path.suffixes != [".ndjson", ".gz"]:
            raise ValueError(
                f"Extensão inválida para ingestão: {self._file_path.name}. "
                "Esperado sufixo .ndjson.gz"
            )

    def iter_lines(self) -> Iterator[RawNdjsonLine]:
        """
        Itera sobre as linhas úteis do arquivo, ignorando linhas em branco.

        Retorno:
        -------
        Iterator[RawNdjsonLine]
            Linhas não vazias com número original.
        """

        self.validate()
        with gzip.open(self._file_path, mode="rt", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                content = raw_line.strip()
                if not content:
                    continue
                yield RawNdjsonLine(line_number=line_number, content=content)

