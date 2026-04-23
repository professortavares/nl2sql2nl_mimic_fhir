"""
Pipeline principal que orquestra a ingestão de Organization e Location.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from time import perf_counter

from sqlalchemy.engine import Connection

from src.config.settings import ProjectSettings
from src.db.connection import create_engine_from_settings
from src.db.reset import reset_schema
from src.db.schema import build_project_metadata
from src.ingestion.loaders.location_loader import LocationLoader
from src.ingestion.loaders.organization_loader import OrganizationLoader
from src.pipelines.ingest_location import LocationIngestionPipeline, LocationPipelineSummary
from src.pipelines.ingest_organization import (
    OrganizationIngestionPipeline,
    OrganizationPipelineSummary,
)

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class IngestionRunSummary:
    """
    Resumo consolidado da execução completa.
    """

    organization: OrganizationPipelineSummary
    location: LocationPipelineSummary
    elapsed_seconds: float
    affected_tables: tuple[str, ...]


class IngestAllPipeline:
    """
    Orquestra o reset do schema, criação das tabelas e ingestão na ordem correta.
    """

    def __init__(self, settings: ProjectSettings) -> None:
        """
        Inicializa o pipeline principal.
        """

        self._settings = settings
        self._engine = create_engine_from_settings(settings.database)
        metadata, tables = build_project_metadata(
            settings.database.schema_name,
            settings.organization.table_names,
            settings.location.table_names,
        )
        self._metadata = metadata
        self._organization_loader = OrganizationLoader(tables.organization)
        self._location_loader = LocationLoader(tables.location)
        self._organization_pipeline = OrganizationIngestionPipeline(
            settings=settings,
            loader=self._organization_loader,
        )
        self._location_pipeline = LocationIngestionPipeline(
            settings=settings,
            loader=self._location_loader,
        )

    def run(self) -> IngestionRunSummary:
        """
        Executa a ingestão completa em uma única transação.
        """

        if self._settings.common.reset_policy != "drop_and_recreate":
            raise ValueError("A política de reset suportada é 'drop_and_recreate'.")
        if self._settings.common.ingestion_order != ("organization", "location"):
            raise ValueError(
                "A ordem de ingestão suportada deve ser ('organization', 'location')."
            )

        started_at = perf_counter()
        LOGGER.info("Iniciando processo de ingestão completo.")

        with self._engine.begin() as connection:
            self._reset_and_create_schema(connection)
            organization_summary = self._organization_pipeline.ingest(connection)
            location_summary = self._location_pipeline.ingest(connection)

        elapsed_seconds = perf_counter() - started_at
        affected_tables = (
            self._settings.organization.table_names.organization,
            self._settings.organization.table_names.meta_profile,
            self._settings.organization.table_names.identifier,
            self._settings.organization.table_names.type_coding,
            self._settings.location.table_names.location,
            self._settings.location.table_names.meta_profile,
            self._settings.location.table_names.physical_type_coding,
        )

        summary = IngestionRunSummary(
            organization=organization_summary,
            location=location_summary,
            elapsed_seconds=elapsed_seconds,
            affected_tables=affected_tables,
        )
        LOGGER.info(
            "Resumo final: organization_lidos=%s organization_inseridos=%s location_lidos=%s location_inseridos=%s tempo=%.2fs tabelas=%s",
            organization_summary.records_read,
            organization_summary.records_inserted,
            location_summary.records_read,
            location_summary.records_inserted,
            summary.elapsed_seconds,
            ", ".join(summary.affected_tables),
        )
        return summary

    def _reset_and_create_schema(self, connection: Connection) -> None:
        """
        Remove e recria o schema, seguido da criação de todas as tabelas.
        """

        reset_schema(connection, self._settings.database.schema_name)
        self._metadata.create_all(connection)
        LOGGER.info(
            "Schema resetado e tabelas criadas: %s",
            self._settings.database.schema_name,
        )
