"""
Pipeline de ingestão do recurso FHIR ObservationDatetimeevents.
"""

from __future__ import annotations

from sqlalchemy.engine import Connection

from src.config.settings import ProjectSettings
from src.ingestion.loaders.observation_datetimeevents_loader import (
    ObservationDatetimeeventsLoader,
)
from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader
from src.ingestion.transformers.observation_datetimeevents_transformer import (
    ObservationDatetimeeventsTransformer,
)
from src.pipelines.base_resource_pipeline import ResourceIngestionSummary, ingest_ndjson_resource


class ObservationDatetimeeventsIngestionPipeline:
    """
    Coordena leitura, transformação e persistência de ObservationDatetimeevents.
    """

    def __init__(
        self,
        settings: ProjectSettings,
        loader: ObservationDatetimeeventsLoader,
    ) -> None:
        """
        Inicializa o pipeline.
        """

        self._settings = settings.observation_datetimeevents
        self._common_settings = settings.common
        self._loader = loader
        self._reader = NdjsonGzipReader(self._settings.input_path)
        self._transformer = ObservationDatetimeeventsTransformer()

    @property
    def resource_name(self) -> str:
        """
        Retorna o nome lógico do recurso.
        """

        return "ObservationDatetimeevents"

    def ingest(self, connection: Connection) -> ResourceIngestionSummary:
        """
        Executa a ingestão de ObservationDatetimeevents usando uma conexão já aberta.
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
