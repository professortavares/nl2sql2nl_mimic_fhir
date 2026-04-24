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
    Executa a ingestão completa de Organization, Location, Patient, Encounter,
    EncounterED, EncounterICU, Medication, MedicationMix, MedicationRequest,
    Specimen, Condition, ConditionED, Procedure, ProcedureED, ProcedureICU,
    ObservationLabevents, ObservationMicroTest, ObservationMicroOrg,
    ObservationMicroSusc, ObservationChartevents, ObservationDatetimeevents,
    ObservationOutputevents, ObservationED, ObservationVitalSignsED,
    MedicationDispense, MedicationDispenseED, MedicationAdministration e
    MedicationAdministrationICU.

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
        logger.info("Ordem configurada da pipeline: %s", settings.resources.execution_order)

        pipeline = IngestAllPipeline(settings)
        summary = pipeline.run()

        for resource_name in settings.resources.execution_order:
            resource_summary = summary.resource_summaries[resource_name]
            logger.info(
                "Resumo %s: lidos=%s inseridos=%s ignorados=%s tabelas=%s",
                resource_name,
                resource_summary.records_read,
                resource_summary.records_inserted,
                resource_summary.skipped_records,
                resource_summary.table_counts,
            )

        logger.info("Execução concluída com sucesso em %.2fs", summary.elapsed_seconds)
        return 0
    except Exception as exc:  # pragma: no cover - falha de CLI
        logging.exception("Falha na execução da ingestão: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
