"""
Pipeline principal que orquestra a ingestão de Organization, Location e Patient.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

from sqlalchemy.engine import Connection

from src.config.settings import ProjectSettings
from src.db.connection import create_engine_from_settings
from src.db.reset import reset_schema
from src.db.schema import build_project_metadata
from src.ingestion.loaders.location_loader import LocationLoader
from src.ingestion.loaders.organization_loader import OrganizationLoader
from src.ingestion.loaders.patient_loader import PatientLoader
from src.pipelines.base_resource_pipeline import ResourceIngestionSummary
from src.pipelines.ingest_location import LocationIngestionPipeline
from src.pipelines.ingest_organization import OrganizationIngestionPipeline
from src.pipelines.ingest_patient import PatientIngestionPipeline

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class IngestionRunSummary:
    """
    Resumo consolidado da execução completa.
    """

    resource_summaries: dict[str, ResourceIngestionSummary]
    elapsed_seconds: float
    table_counts: dict[str, int]


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
            settings.patient.table_names,
        )
        self._metadata = metadata
        self._organization_loader = OrganizationLoader(tables.organization)
        self._location_loader = LocationLoader(tables.location)
        self._patient_loader = PatientLoader(tables.patient)
        self._pipelines = {
            "organization": OrganizationIngestionPipeline(
                settings=settings,
                loader=self._organization_loader,
            ),
            "location": LocationIngestionPipeline(
                settings=settings,
                loader=self._location_loader,
            ),
            "patient": PatientIngestionPipeline(
                settings=settings,
                loader=self._patient_loader,
            ),
        }

    def run(self) -> IngestionRunSummary:
        """
        Executa a ingestão completa em uma única transação.
        """

        if self._settings.common.reset_policy != "drop_and_recreate":
            raise ValueError("A política de reset suportada é 'drop_and_recreate'.")
        if self._settings.resources.execution_order != ("organization", "location", "patient"):
            raise ValueError(
                "A ordem de ingestão suportada deve ser ('organization', 'location', 'patient')."
            )

        started_at = perf_counter()
        LOGGER.info(
            "Iniciando processo de ingestão completo com ordem: %s",
            self._settings.resources.execution_order,
        )

        resource_summaries: dict[str, ResourceIngestionSummary] = {}
        with self._engine.begin() as connection:
            self._reset_and_create_schema(connection)
            for resource_name in self._settings.resources.execution_order:
                LOGGER.info("Executando recurso %s", resource_name)
                pipeline = self._pipelines[resource_name]
                resource_summaries[resource_name] = pipeline.ingest(connection)

        elapsed_seconds = perf_counter() - started_at
        table_counts = _merge_table_counts(summary.table_counts for summary in resource_summaries.values())
        summary = IngestionRunSummary(
            resource_summaries=resource_summaries,
            elapsed_seconds=elapsed_seconds,
            table_counts=table_counts,
        )
        LOGGER.info(
            "Resumo final: ordem=%s tempo=%.2fs tabelas=%s",
            self._settings.resources.execution_order,
            summary.elapsed_seconds,
            summary.table_counts,
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


def _merge_table_counts(counts: Iterable[dict[str, int]]) -> dict[str, int]:
    """
    Soma contagens de tabelas provenientes de todos os recursos.
    """

    merged: dict[str, int] = {}
    for summary_counts in counts:
        for table_name, value in summary_counts.items():
            merged[table_name] = merged.get(table_name, 0) + value
    return merged
