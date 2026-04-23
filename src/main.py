"""
Entrada principal da aplicação de ingestão.
"""

from __future__ import annotations

import logging

from src.config.settings import load_project_settings
from src.pipelines.ingest_organization import OrganizationIngestionPipeline


def configure_logging() -> None:
    """
    Configura o logging padrão da aplicação.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> int:
    """
    Executa o pipeline de ingestão de Organization.

    Retorno:
    -------
    int
        Código de saída do processo.
    """

    configure_logging()
    logger = logging.getLogger(__name__)

    try:
        settings = load_project_settings()
        pipeline = OrganizationIngestionPipeline(settings)
        summary = pipeline.run()
        logger.info(
            "Execução concluída com sucesso: pipeline=%s registros_lidos=%s registros_inseridos=%s tempo=%.2fs",
            summary.pipeline_name,
            summary.records_read,
            summary.organizations_inserted,
            summary.elapsed_seconds,
        )
        return 0
    except Exception as exc:  # pragma: no cover - tratamos a falha para saída de CLI
        logger.exception("Falha na execução da ingestão: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
