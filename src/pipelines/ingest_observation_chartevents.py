"""
Pipeline de ingestão do recurso FHIR ObservationChartevents.
"""

from __future__ import annotations

from sqlalchemy.engine import Connection

from src.config.settings import ProjectSettings
from src.ingestion.loaders.observation_chartevents_loader import ObservationCharteventsLoader
from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader
from src.ingestion.transformers.observation_chartevents_transformer import (
    ObservationCharteventsTransformer,
)
from src.pipelines.base_resource_pipeline import ResourceIngestionSummary, ingest_ndjson_resource


class ObservationCharteventsIngestionPipeline:
    """
    Coordena leitura, transformação e persistência de ObservationChartevents.
    """

    def __init__(self, settings: ProjectSettings, loader: ObservationCharteventsLoader) -> None:
        """
        Inicializa o pipeline.
        """

        self._settings = settings.observation_chartevents
        self._common_settings = settings.common
        self._loader = loader
        self._reader = NdjsonGzipReader(self._settings.input_path)
        self._transformer = ObservationCharteventsTransformer()

    @property
    def resource_name(self) -> str:
        """
        Retorna o nome lógico do recurso.
        """

        return "ObservationChartevents"

    def ingest(self, connection: Connection) -> ResourceIngestionSummary:
        """
        Executa a ingestão de ObservationChartevents usando uma conexão já aberta.
        """

        return ingest_ndjson_resource(
            connection=connection,
            reader=self._reader,
            transformer=self._transformer,
            loader=self._loader,
            batch_size=self._settings.batch_size or self._common_settings.batch_size,
            skip_invalid_records=self._common_settings.skip_invalid_records,
            resource_name=self.resource_name,
        )
