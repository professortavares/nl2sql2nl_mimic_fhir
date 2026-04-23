"""
Entrada principal da aplicação de ingestão.
"""

from __future__ import annotations

import logging

from src.config.settings import load_project_settings
from src.logging.logger import configure_logging
from src.pipelines.ingest_all import IngestAllPipeline


def main() -> int:
    """
    Executa a ingestão completa de Organization e Location.

    Retorno:
    -------
    int
        Código de saída do processo.
    """

    try:
        settings = load_project_settings()
        log_file_path = configure_logging(settings.logging)
        logger = logging.getLogger(__name__)
        logger.info("Logging configurado em %s", log_file_path)
        pipeline = IngestAllPipeline(settings)
        summary = pipeline.run()
        logger.info(
            "Execução concluída com sucesso: organization_lidos=%s organization_inseridos=%s location_lidos=%s location_inseridos=%s tempo=%.2fs",
            summary.organization.records_read,
            summary.organization.records_inserted,
            summary.location.records_read,
            summary.location.records_inserted,
            summary.elapsed_seconds,
        )
        return 0
    except Exception as exc:  # pragma: no cover - falha de CLI
        logging.exception("Falha na execução da ingestão: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

