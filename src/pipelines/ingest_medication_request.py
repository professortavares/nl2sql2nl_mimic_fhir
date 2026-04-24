"""
Pipeline de ingestão do recurso FHIR MedicationRequest.
"""

from __future__ import annotations

from sqlalchemy.engine import Connection

from src.config.settings import ProjectSettings
from src.ingestion.loaders.medication_request_loader import MedicationRequestLoader
from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader
from src.ingestion.transformers.medication_request_transformer import MedicationRequestTransformer
from src.pipelines.base_resource_pipeline import ResourceIngestionSummary, ingest_ndjson_resource


class MedicationRequestIngestionPipeline:
    """
    Coordena leitura, transformação e persistência de MedicationRequest.
    """

    def __init__(self, settings: ProjectSettings, loader: MedicationRequestLoader) -> None:
        """
        Inicializa o pipeline.
        """

        self._settings = settings.medication_request
        self._common_settings = settings.common
        self._loader = loader
        self._reader = NdjsonGzipReader(self._settings.input_path)
        self._transformer = MedicationRequestTransformer()

    @property
    def resource_name(self) -> str:
        """
        Retorna o nome lógico do recurso.
        """

        return "MedicationRequest"

    def ingest(self, connection: Connection) -> ResourceIngestionSummary:
        """
        Executa a ingestão de MedicationRequest usando uma conexão já aberta.
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
