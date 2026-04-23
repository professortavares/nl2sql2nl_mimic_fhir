"""
Leitura incremental de arquivos NDJSON compactados com gzip.
"""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping


@dataclass(slots=True, frozen=True)
class RawNdjsonLine:
    """Linha bruta lida de um arquivo NDJSON."""

    line_number: int
    content: str


class NdjsonGzipReaderError(ValueError):
    """Indica falha de leitura ou parsing em um arquivo `.ndjson.gz`."""


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

    def iter_json_objects(self) -> Iterator[Mapping[str, Any]]:
        """
        Itera sobre os objetos JSON presentes no arquivo.

        Retorno:
        -------
        Iterator[Mapping[str, Any]]
            Objetos JSON decodificados linha a linha.

        Exceções:
        --------
        NdjsonGzipReaderError
            Quando uma linha contém JSON inválido ou um objeto não mapeável.
        """

        for raw_line in self.iter_lines():
            try:
                payload = json.loads(raw_line.content)
            except json.JSONDecodeError as exc:
                raise NdjsonGzipReaderError(
                    f"JSON inválido na linha {raw_line.line_number} de {self._file_path.name}."
                ) from exc
            if not isinstance(payload, Mapping):
                raise NdjsonGzipReaderError(
                    f"A linha {raw_line.line_number} de {self._file_path.name} "
                    "não contém um objeto JSON mapeável."
                )
            yield payload
