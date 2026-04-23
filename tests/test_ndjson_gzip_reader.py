"""
Testes da leitura incremental de NDJSON compactado.
"""

from __future__ import annotations

import gzip
import tempfile
import unittest
from pathlib import Path

from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader


class NdjsonGzipReaderTests(unittest.TestCase):
    """Verifica leitura e validação do arquivo de entrada."""

    def test_iter_lines_reads_non_empty_lines(self) -> None:
        """Confirma que o leitor preserva apenas linhas úteis."""

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "example.ndjson.gz"
            with gzip.open(file_path, mode="wt", encoding="utf-8") as handle:
                handle.write('{"id": "1"}\n')
                handle.write("\n")
                handle.write('{"id": "2"}\n')

            reader = NdjsonGzipReader(file_path)
            lines = list(reader.iter_lines())

        self.assertEqual([1, 3], [line.line_number for line in lines])
        self.assertEqual(['{"id": "1"}', '{"id": "2"}'], [line.content for line in lines])

    def test_validate_rejects_wrong_extension(self) -> None:
        """Confirma que o leitor rejeita extensões fora do padrão."""

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "example.txt"
            file_path.write_text("dummy", encoding="utf-8")

            reader = NdjsonGzipReader(file_path)

            with self.assertRaises(ValueError):
                reader.validate()


if __name__ == "__main__":
    unittest.main()

