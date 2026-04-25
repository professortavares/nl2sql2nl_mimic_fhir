"""
Pipeline de ingestão do recurso FHIR ProcedureICU.
"""

from __future__ import annotations

from sqlalchemy.engine import Connection

from src.config.settings import ProjectSettings
from src.ingestion.loaders.procedure_icu_loader import ProcedureICULoader
from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader
from src.ingestion.transformers.procedure_icu_transformer import ProcedureICUTransformer
from src.pipelines.base_resource_pipeline import ResourceIngestionSummary, ingest_ndjson_resource


class ProcedureICUIngestionPipeline:
    """
    Coordena leitura, transformação e persistência de ProcedureICU.
    """

    def __init__(self, settings: ProjectSettings, loader: ProcedureICULoader) -> None:
        """
        Inicializa o pipeline.
        """

        self._settings = settings.procedure_icu
        self._common_settings = settings.common
        self._loader = loader
        self._reader = NdjsonGzipReader(self._settings.input_path)
        self._transformer = ProcedureICUTransformer()

    @property
    def resource_name(self) -> str:
        """
        Retorna o nome lógico do recurso.
        """

        return "ProcedureICU"

    def ingest(self, connection: Connection) -> ResourceIngestionSummary:
        """
        Executa a ingestão de ProcedureICU usando uma conexão já aberta.
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
