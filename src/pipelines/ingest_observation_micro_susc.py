"""
Pipeline de ingestão do recurso FHIR ObservationMicroSusc.
"""

from __future__ import annotations

from sqlalchemy.engine import Connection

from src.config.settings import ProjectSettings
from src.ingestion.loaders.observation_micro_susc_loader import ObservationMicroSuscLoader
from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader
from src.ingestion.transformers.observation_micro_susc_transformer import (
    ObservationMicroSuscTransformer,
)
from src.pipelines.base_resource_pipeline import ResourceIngestionSummary, ingest_ndjson_resource


class ObservationMicroSuscIngestionPipeline:
    """
    Coordena leitura, transformação e persistência de ObservationMicroSusc.
    """

    def __init__(self, settings: ProjectSettings, loader: ObservationMicroSuscLoader) -> None:
        """
        Inicializa o pipeline.
        """

        self._settings = settings.observation_micro_susc
        self._common_settings = settings.common
        self._loader = loader
        self._reader = NdjsonGzipReader(self._settings.input_path)
        self._transformer = ObservationMicroSuscTransformer()

    @property
    def resource_name(self) -> str:
        """
        Retorna o nome lógico do recurso.
        """

        return "ObservationMicroSusc"

    def ingest(self, connection: Connection) -> ResourceIngestionSummary:
        """
        Executa a ingestão de ObservationMicroSusc usando uma conexão já aberta.
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
