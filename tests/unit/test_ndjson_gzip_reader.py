"""
Testes do leitor NDJSON compactado com gzip.
"""

from __future__ import annotations

import gzip
from dataclasses import dataclass
from pathlib import Path

import pytest

from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader
from src.pipelines.base_resource_pipeline import ingest_ndjson_resource


@dataclass(slots=True)
class _DummyBatchResult:
    primary_rows: int = 1

    def table_counts(self) -> dict[str, int]:
        return {"dummy": self.primary_rows}


class _DummyLoader:
    def insert_batch(self, connection, batch):  # type: ignore[no-untyped-def]
        return _DummyBatchResult(primary_rows=len(batch))


class _DummyTransformer:
    def transform(self, resource):  # type: ignore[no-untyped-def]
        return resource


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


def test_reader_skips_or_raises_on_invalid_json_line(tmp_path: Path) -> None:
    """
    A ingestão streaming deve lidar com linha JSON inválida de forma controlada.
    """

    file_path = tmp_path / "example.ndjson.gz"
    _write_gzip_file(file_path, ['{"id":"1"}', "{invalid-json}"])

    reader = NdjsonGzipReader(file_path)
    summary = ingest_ndjson_resource(
        connection=object(),  # type: ignore[arg-type]
        reader=reader,
        transformer=_DummyTransformer(),
        loader=_DummyLoader(),
        batch_size=10,
        skip_invalid_records=True,
        resource_name="Dummy",
    )

    assert summary.records_read == 2
    assert summary.records_inserted == 1
    assert summary.skipped_records == 1
    assert summary.table_counts == {"dummy": 1}
