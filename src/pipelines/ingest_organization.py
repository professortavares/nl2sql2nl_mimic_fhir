"""
Pipeline de ingestão do recurso FHIR Organization para PostgreSQL.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from src.config.settings import ProjectSettings
from src.db.connection import create_engine_from_settings
from src.ingestion.loaders.organization_loader import OrganizationLoader
from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader
from src.ingestion.transformers.organization_transformer import (
    OrganizationTransformationError,
    OrganizationTransformationResult,
    OrganizationTransformer,
)

LOGGER = logging.getLogger(__name__)


class OrganizationIngestionError(RuntimeError):
    """Erros de execução do pipeline de ingestão."""


@dataclass(slots=True, frozen=True)
class IngestionSummary:
    """Resumo final da execução do pipeline."""

    pipeline_name: str
    input_path: Path
    records_read: int
    organizations_inserted: int
    meta_profiles_inserted: int
    identifiers_inserted: int
    type_codings_inserted: int
    skipped_records: int
    elapsed_seconds: float
    affected_tables: tuple[str, ...]


class OrganizationIngestionPipeline:
    """
    Coordena leitura, transformação e persistência do arquivo Organization.
    """

    def __init__(self, settings: ProjectSettings) -> None:
        """
        Inicializa o pipeline.

        Parâmetros:
        ----------
        settings : ProjectSettings
            Configurações consolidadas da aplicação.
        """

        self._settings = settings
        self._engine = create_engine_from_settings(settings.database)
        self._reader = NdjsonGzipReader(settings.organization.input_path)
        self._transformer = OrganizationTransformer()
        self._loader = OrganizationLoader(
            self._engine,
            settings.database.schema_name,
            settings.organization.table_names,
        )

    def run(self) -> IngestionSummary:
        """
        Executa a ingestão completa com reset do schema e carga transacional.

        Retorno:
        -------
        IngestionSummary
            Resumo consolidado da execução.
        """

        if self._settings.organization.reset_policy != "drop_and_recreate":
            raise OrganizationIngestionError(
                "Esta implementação suporta apenas reset_policy='drop_and_recreate'."
            )

        self._reader.validate()

        started_at = perf_counter()
        records_read = 0
        skipped_records = 0
        organizations_inserted = 0
        meta_profiles_inserted = 0
        identifiers_inserted = 0
        type_codings_inserted = 0
        batch: list[OrganizationTransformationResult] = []

        LOGGER.info(
            "Iniciando ingestão %s para o arquivo %s",
            self._settings.organization.pipeline_name,
            self._reader.file_path,
        )

        with self._engine.begin() as connection:
            self._loader.reset_and_create_schema(connection)

            for raw_line in self._reader.iter_lines():
                records_read += 1
                try:
                    resource = json.loads(raw_line.content)
                    transformed = self._transformer.transform(resource)
                except (json.JSONDecodeError, TypeError, ValueError, OrganizationTransformationError) as exc:
                    if self._settings.organization.skip_invalid_records:
                        skipped_records += 1
                        LOGGER.warning(
                            "Registro ignorado na linha %s: %s",
                            raw_line.line_number,
                            exc,
                        )
                        continue
                    raise OrganizationIngestionError(
                        f"Falha ao processar a linha {raw_line.line_number}"
                    ) from exc

                batch.append(transformed)
                if len(batch) >= self._settings.organization.batch_size:
                    counts = self._loader.insert_batch(connection, batch)
                    organizations_inserted += counts.organizations
                    meta_profiles_inserted += counts.meta_profiles
                    identifiers_inserted += counts.identifiers
                    type_codings_inserted += counts.type_codings
                    LOGGER.info(
                        "Lote persistido: organizations=%s meta_profiles=%s identifiers=%s type_codings=%s",
                        counts.organizations,
                        counts.meta_profiles,
                        counts.identifiers,
                        counts.type_codings,
                    )
                    batch.clear()

            if batch:
                counts = self._loader.insert_batch(connection, batch)
                organizations_inserted += counts.organizations
                meta_profiles_inserted += counts.meta_profiles
                identifiers_inserted += counts.identifiers
                type_codings_inserted += counts.type_codings
                LOGGER.info(
                    "Lote final persistido: organizations=%s meta_profiles=%s identifiers=%s type_codings=%s",
                    counts.organizations,
                    counts.meta_profiles,
                    counts.identifiers,
                    counts.type_codings,
                )

        elapsed_seconds = perf_counter() - started_at
        affected_tables = (
            self._settings.organization.table_names.organization,
            self._settings.organization.table_names.organization_meta_profile,
            self._settings.organization.table_names.organization_identifier,
            self._settings.organization.table_names.organization_type_coding,
        )

        summary = IngestionSummary(
            pipeline_name=self._settings.organization.pipeline_name,
            input_path=self._reader.file_path,
            records_read=records_read,
            organizations_inserted=organizations_inserted,
            meta_profiles_inserted=meta_profiles_inserted,
            identifiers_inserted=identifiers_inserted,
            type_codings_inserted=type_codings_inserted,
            skipped_records=skipped_records,
            elapsed_seconds=elapsed_seconds,
            affected_tables=affected_tables,
        )

        LOGGER.info(
            "Resumo: lidos=%s inseridos=%s ignorados=%s tempo=%.2fs tabelas=%s",
            summary.records_read,
            summary.organizations_inserted,
            summary.skipped_records,
            summary.elapsed_seconds,
            ", ".join(summary.affected_tables),
        )
        return summary
