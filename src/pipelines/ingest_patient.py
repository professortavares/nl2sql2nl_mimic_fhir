"""
Pipeline de ingestão do recurso FHIR Patient.
"""

from __future__ import annotations

from sqlalchemy.engine import Connection

from src.config.settings import ProjectSettings
from src.ingestion.loaders.patient_loader import PatientLoader
from src.ingestion.readers.ndjson_gzip_reader import NdjsonGzipReader
from src.ingestion.transformers.patient_transformer import PatientTransformer
from src.pipelines.base_resource_pipeline import ResourceIngestionSummary, ingest_ndjson_resource


class PatientIngestionPipeline:
    """
    Coordena leitura, transformação e persistência de Patient.
    """

    def __init__(self, settings: ProjectSettings, loader: PatientLoader) -> None:
        """
        Inicializa o pipeline.
        """

        self._settings = settings.patient
        self._common_settings = settings.common
        self._loader = loader
        self._reader = NdjsonGzipReader(self._settings.input_path)
        self._transformer = PatientTransformer()

    @property
    def resource_name(self) -> str:
        """
        Retorna o nome lógico do recurso.
        """

        return "Patient"

    def ingest(self, connection: Connection) -> ResourceIngestionSummary:
        """
        Executa a ingestão de Patient usando uma conexão já aberta.
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
