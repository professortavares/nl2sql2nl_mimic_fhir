"""
Testes do leitor NDJSON compactado com gzip.
"""

from __future__ import annotations

import gzip
from pathlib import Path

import pytest

from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader, NdjsonGzipReaderError


def _write_gzip_file(path: Path, lines: list[str]) -> None:
    """
    Escreve um arquivo gzip com linhas NDJSON.
    """

    with gzip.open(path, mode="wt", encoding="utf-8") as handle:
        for line in lines:
            handle.write(f"{line}\n")


def test_reader_reads_valid_lines(tmp_path: Path) -> None:
    """
    Deve ler linhas úteis de um arquivo gzip NDJSON.
    """

    file_path = tmp_path / "example.ndjson.gz"
    _write_gzip_file(file_path, ['{"id":"1"}', "", '{"id":"2"}'])

    reader = NdjsonGzipReader(file_path)
    lines = list(reader.iter_lines())

    assert [1, 3] == [line.line_number for line in lines]
    assert ['{"id":"1"}', '{"id":"2"}'] == [line.content for line in lines]


def test_reader_rejects_missing_file(tmp_path: Path) -> None:
    """
    Deve falhar quando o arquivo não existe.
    """

    reader = NdjsonGzipReader(tmp_path / "missing.ndjson.gz")

    with pytest.raises(FileNotFoundError):
        list(reader.iter_lines())


def test_reader_rejects_invalid_extension(tmp_path: Path) -> None:
    """
    Deve falhar quando a extensão não é `.ndjson.gz`.
    """

    file_path = tmp_path / "example.txt"
    file_path.write_text("dummy", encoding="utf-8")

    reader = NdjsonGzipReader(file_path)

    with pytest.raises(ValueError):
        reader.validate()


def test_reader_raises_on_invalid_json_line(tmp_path: Path) -> None:
    """
    Deve falhar quando uma linha contém JSON inválido.
    """

    file_path = tmp_path / "example.ndjson.gz"
    _write_gzip_file(file_path, ['{"id":"1"}', "{invalid-json}"])

    reader = NdjsonGzipReader(file_path)

    with pytest.raises(NdjsonGzipReaderError):
        list(reader.iter_json_objects())
