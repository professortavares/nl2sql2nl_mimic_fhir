"""
Componentes reutilizáveis para ingestão de recursos FHIR.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol, Sequence, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Connection

from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader

LOGGER = logging.getLogger(__name__)

TTransformed = TypeVar("TTransformed")


class BatchInsertResult(Protocol):
    """
    Contrato mínimo para resultados de inserção em lote.
    """

    primary_rows: int


class BatchLoader(Protocol[TTransformed]):
    """
    Contrato mínimo para carregadores de batches transformados.
    """

    def insert_batch(self, connection: Connection, batch: Sequence[TTransformed]) -> BatchInsertResult:
        """Persiste um lote e retorna um resumo das inserções."""


class ResourceTransformer(Protocol[TTransformed]):
    """
    Contrato mínimo para transformadores de recursos brutos.
    """

    def transform(self, resource: Any) -> TTransformed:
        """Converte um recurso bruto em registros relacionais."""


@dataclass(slots=True, frozen=True)
class ResourceIngestionSummary:
    """
    Resumo de ingestão de um único arquivo de recurso.
    """

    resource_name: str
    input_path: Path
    records_read: int
    records_inserted: int
    skipped_records: int
    elapsed_seconds: float


def ingest_ndjson_resource(
    *,
    connection: Connection,
    reader: NdjsonGzipReader,
    transformer: ResourceTransformer[TTransformed],
    loader: BatchLoader[TTransformed],
    batch_size: int,
    skip_invalid_records: bool,
    resource_name: str,
) -> ResourceIngestionSummary:
    """
    Ingere um arquivo NDJSON compactado com processamento streaming.

    Parâmetros:
    ----------
    reader : NdjsonGzipReader
        Leitor do arquivo gzipped NDJSON.
    connection : Connection
        Conexão SQLAlchemy ativa dentro da transação.
    transformer : ResourceTransformer[TTransformed]
        Transformador do recurso bruto.
    loader : BatchLoader[TTransformed]
        Persistidor do batch transformado.
    batch_size : int
        Tamanho máximo do lote em memória.
    skip_invalid_records : bool
        Se `True`, registros inválidos são ignorados com log.
    resource_name : str
        Nome lógico do recurso, usado em mensagens.

    Retorno:
    -------
    ResourceIngestionSummary
        Resumo da ingestão concluída.
    """

    reader.validate()

    started_at = perf_counter()
    records_read = 0
    records_inserted = 0
    skipped_records = 0
    batch: list[TTransformed] = []

    LOGGER.info("Processando arquivo %s para recurso %s", reader.file_path, resource_name)

    for raw_line in reader.iter_lines():
        records_read += 1
        try:
            resource = json.loads(raw_line.content)
            transformed = transformer.transform(resource)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            if skip_invalid_records:
                skipped_records += 1
                LOGGER.warning(
                    "Registro ignorado em %s na linha %s: %s",
                    reader.file_path.name,
                    raw_line.line_number,
                    exc,
                )
                continue
            raise RuntimeError(
                f"Falha ao processar o recurso {resource_name} na linha {raw_line.line_number}."
            ) from exc

        batch.append(transformed)
        if len(batch) >= batch_size:
            try:
                batch_result = loader.insert_batch(connection=connection, batch=batch)
            except IntegrityError as exc:
                raise RuntimeError(
                    f"Falha de integridade ao persistir lote de {resource_name}."
                ) from exc
            records_inserted += batch_result.primary_rows
            LOGGER.info(
                "Lote persistido para %s: registros=%s",
                resource_name,
                batch_result.primary_rows,
            )
            batch.clear()

    if batch:
        try:
            batch_result = loader.insert_batch(connection=connection, batch=batch)
        except IntegrityError as exc:
            raise RuntimeError(
                f"Falha de integridade ao persistir lote final de {resource_name}."
            ) from exc
        records_inserted += batch_result.primary_rows
        LOGGER.info(
            "Lote final persistido para %s: registros=%s",
            resource_name,
            batch_result.primary_rows,
        )

    elapsed_seconds = perf_counter() - started_at
    summary = ResourceIngestionSummary(
        resource_name=resource_name,
        input_path=reader.file_path,
        records_read=records_read,
        records_inserted=records_inserted,
        skipped_records=skipped_records,
        elapsed_seconds=elapsed_seconds,
    )
    LOGGER.info(
        "Resumo %s: lidos=%s inseridos=%s ignorados=%s tempo=%.2fs",
        resource_name,
        summary.records_read,
        summary.records_inserted,
        summary.skipped_records,
        summary.elapsed_seconds,
    )
    return summary
