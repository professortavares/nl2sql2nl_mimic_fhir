"""
Pipeline de ingestão do recurso FHIR EncounterICU.
"""

from __future__ import annotations

from sqlalchemy.engine import Connection

from src.config.settings import ProjectSettings
from src.ingestion.loaders.encounter_icu_loader import EncounterICULoader
from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader
from src.ingestion.transformers.encounter_icu_transformer import EncounterICUTransformer
from src.pipelines.base_resource_pipeline import ResourceIngestionSummary, ingest_ndjson_resource


class EncounterICUIngestionPipeline:
    """
    Coordena leitura, transformação e persistência de EncounterICU.
    """

    def __init__(self, settings: ProjectSettings, loader: EncounterICULoader) -> None:
        """
        Inicializa o pipeline.
        """

        self._settings = settings.encounter_icu
        self._common_settings = settings.common
        self._loader = loader
        self._reader = NdjsonGzipReader(self._settings.input_path)
        self._transformer = EncounterICUTransformer()

    @property
    def resource_name(self) -> str:
        """
        Retorna o nome lógico do recurso.
        """

        return "EncounterICU"

    def ingest(self, connection: Connection) -> ResourceIngestionSummary:
        """
        Executa a ingestão de EncounterICU usando uma conexão já aberta.
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
