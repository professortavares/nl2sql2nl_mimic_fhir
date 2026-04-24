"""
Pipeline principal que orquestra a ingestão de Organization, Location, Patient,
Encounter, EncounterED, EncounterICU, Medication, MedicationMix,
MedicationRequest, Specimen, Condition, ConditionED, Procedure,
ProcedureED, ProcedureICU, ObservationLabevents, ObservationMicroTest,
ObservationMicroOrg, ObservationMicroSusc e ObservationChartevents.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

from sqlalchemy.engine import Connection

from src.config.settings import ProjectSettings
from src.db.connection import create_engine_from_settings
from src.db.reset import reset_schema
from src.db.schema import build_project_metadata
from src.ingestion.loaders.location_loader import LocationLoader
from src.ingestion.loaders.encounter_loader import EncounterLoader
from src.ingestion.loaders.encounter_ed_loader import EncounterEDLoader
from src.ingestion.loaders.encounter_icu_loader import EncounterICULoader
from src.ingestion.loaders.medication_loader import MedicationLoader
from src.ingestion.loaders.medication_mix_loader import MedicationMixLoader
from src.ingestion.loaders.medication_request_loader import MedicationRequestLoader
from src.ingestion.loaders.condition_loader import ConditionLoader
from src.ingestion.loaders.condition_ed_loader import ConditionEDLoader
from src.ingestion.loaders.procedure_loader import ProcedureLoader
from src.ingestion.loaders.procedure_ed_loader import ProcedureEDLoader
from src.ingestion.loaders.procedure_icu_loader import ProcedureICULoader
from src.ingestion.loaders.observation_labevents_loader import ObservationLabeventsLoader
from src.ingestion.loaders.observation_micro_test_loader import ObservationMicroTestLoader
from src.ingestion.loaders.observation_micro_org_loader import ObservationMicroOrgLoader
from src.ingestion.loaders.observation_micro_susc_loader import ObservationMicroSuscLoader
from src.ingestion.loaders.observation_chartevents_loader import ObservationCharteventsLoader
from src.ingestion.loaders.specimen_loader import SpecimenLoader
from src.ingestion.loaders.organization_loader import OrganizationLoader
from src.ingestion.loaders.patient_loader import PatientLoader
from src.pipelines.base_resource_pipeline import ResourceIngestionSummary
from src.pipelines.ingest_encounter import EncounterIngestionPipeline
from src.pipelines.ingest_encounter_ed import EncounterEDIngestionPipeline
from src.pipelines.ingest_encounter_icu import EncounterICUIngestionPipeline
from src.pipelines.ingest_medication import MedicationIngestionPipeline
from src.pipelines.ingest_medication_mix import MedicationMixIngestionPipeline
from src.pipelines.ingest_medication_request import MedicationRequestIngestionPipeline
from src.pipelines.ingest_condition import ConditionIngestionPipeline
from src.pipelines.ingest_condition_ed import ConditionEDIngestionPipeline
from src.pipelines.ingest_procedure import ProcedureIngestionPipeline
from src.pipelines.ingest_procedure_ed import ProcedureEDIngestionPipeline
from src.pipelines.ingest_procedure_icu import ProcedureICUIngestionPipeline
from src.pipelines.ingest_observation_labevents import ObservationLabeventsIngestionPipeline
from src.pipelines.ingest_observation_micro_test import ObservationMicroTestIngestionPipeline
from src.pipelines.ingest_observation_micro_org import ObservationMicroOrgIngestionPipeline
from src.pipelines.ingest_observation_micro_susc import ObservationMicroSuscIngestionPipeline
from src.pipelines.ingest_observation_chartevents import ObservationCharteventsIngestionPipeline
from src.pipelines.ingest_specimen import SpecimenIngestionPipeline
from src.pipelines.ingest_location import LocationIngestionPipeline
from src.pipelines.ingest_organization import OrganizationIngestionPipeline
from src.pipelines.ingest_patient import PatientIngestionPipeline

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class IngestionRunSummary:
    """
    Resumo consolidado da execução completa.
    """

    resource_summaries: dict[str, ResourceIngestionSummary]
    elapsed_seconds: float
    table_counts: dict[str, int]


class IngestAllPipeline:
    """
    Orquestra o reset do schema, criação das tabelas e ingestão na ordem correta.
    """

    def __init__(self, settings: ProjectSettings) -> None:
        """
        Inicializa o pipeline principal.
        """

        self._settings = settings
        self._engine = create_engine_from_settings(settings.database)
        metadata, tables = build_project_metadata(
            settings.database.schema_name,
            settings.organization.table_name,
            settings.location.table_name,
            settings.patient.table_name,
            settings.encounter.table_name,
            settings.encounter.auxiliary_table_name or "encounter_location",
            settings.encounter_ed.table_name,
            settings.encounter_icu.table_name,
            settings.encounter_icu.auxiliary_table_name or "encounter_icu_location",
            settings.medication.table_name,
            settings.medication_mix.table_name,
            settings.medication_mix.auxiliary_table_name or "medication_mix_ingredient",
            settings.medication_request.table_name,
            settings.specimen.table_name,
            settings.condition.table_name,
            settings.condition_ed.table_name,
            settings.procedure.table_name,
            settings.procedure_ed.table_name,
            settings.procedure_icu.table_name,
            settings.observation_labevents.table_name,
            settings.observation_micro_test.table_name,
            settings.observation_micro_org.table_name,
            settings.observation_micro_org.auxiliary_table_name or "observation_micro_org_has_member",
            settings.observation_micro_susc.table_name,
            settings.observation_chartevents.table_name,
        )
        self._metadata = metadata
        self._organization_loader = OrganizationLoader(tables.organization)
        self._location_loader = LocationLoader(tables.location)
        self._patient_loader = PatientLoader(tables.patient)
        self._encounter_loader = EncounterLoader(tables.encounter)
        self._encounter_ed_loader = EncounterEDLoader(tables.encounter_ed)
        self._encounter_icu_loader = EncounterICULoader(tables.encounter_icu)
        self._medication_loader = MedicationLoader(tables.medication)
        self._medication_mix_loader = MedicationMixLoader(tables.medication_mix)
        self._medication_request_loader = MedicationRequestLoader(
            tables=tables.medication_request,
            medication_tables=tables.medication,
        )
        self._specimen_loader = SpecimenLoader(
            tables=tables.specimen,
            patient_tables=tables.patient,
        )
        self._condition_loader = ConditionLoader(
            tables=tables.condition,
            patient_tables=tables.patient,
            encounter_tables=tables.encounter,
        )
        self._condition_ed_loader = ConditionEDLoader(
            tables=tables.condition_ed,
            patient_tables=tables.patient,
            encounter_tables=tables.encounter,
        )
        self._procedure_loader = ProcedureLoader(
            tables=tables.procedure,
            patient_tables=tables.patient,
            encounter_tables=tables.encounter,
        )
        self._procedure_ed_loader = ProcedureEDLoader(
            tables=tables.procedure_ed,
            patient_tables=tables.patient,
            encounter_tables=tables.encounter,
        )
        self._procedure_icu_loader = ProcedureICULoader(
            tables=tables.procedure_icu,
            patient_tables=tables.patient,
            encounter_tables=tables.encounter,
        )
        self._observation_labevents_loader = ObservationLabeventsLoader(
            tables=tables.observation_labevents,
            patient_tables=tables.patient,
            specimen_tables=tables.specimen,
        )
        self._observation_micro_test_loader = ObservationMicroTestLoader(
            tables=tables.observation_micro_test,
            patient_tables=tables.patient,
            specimen_tables=tables.specimen,
            encounter_tables=tables.encounter,
        )
        self._observation_micro_org_loader = ObservationMicroOrgLoader(
            tables=tables.observation_micro_org,
            patient_tables=tables.patient,
            observation_micro_test_tables=tables.observation_micro_test,
        )
        self._observation_micro_susc_loader = ObservationMicroSuscLoader(
            tables=tables.observation_micro_susc,
            patient_tables=tables.patient,
            observation_micro_org_tables=tables.observation_micro_org,
        )
        self._observation_chartevents_loader = ObservationCharteventsLoader(
            tables=tables.observation_chartevents,
            patient_tables=tables.patient,
            encounter_tables=tables.encounter,
        )
        self._pipelines = {
            "organization": OrganizationIngestionPipeline(
                settings=settings,
                loader=self._organization_loader,
            ),
            "location": LocationIngestionPipeline(
                settings=settings,
                loader=self._location_loader,
            ),
            "patient": PatientIngestionPipeline(
                settings=settings,
                loader=self._patient_loader,
            ),
            "encounter": EncounterIngestionPipeline(
                settings=settings,
                loader=self._encounter_loader,
            ),
            "encounter_ed": EncounterEDIngestionPipeline(
                settings=settings,
                loader=self._encounter_ed_loader,
            ),
            "encounter_icu": EncounterICUIngestionPipeline(
                settings=settings,
                loader=self._encounter_icu_loader,
            ),
            "medication": MedicationIngestionPipeline(
                settings=settings,
                loader=self._medication_loader,
            ),
            "medication_mix": MedicationMixIngestionPipeline(
                settings=settings,
                loader=self._medication_mix_loader,
            ),
            "medication_request": MedicationRequestIngestionPipeline(
                settings=settings,
                loader=self._medication_request_loader,
            ),
            "specimen": SpecimenIngestionPipeline(
                settings=settings,
                loader=self._specimen_loader,
            ),
            "condition": ConditionIngestionPipeline(
                settings=settings,
                loader=self._condition_loader,
            ),
            "condition_ed": ConditionEDIngestionPipeline(
                settings=settings,
                loader=self._condition_ed_loader,
            ),
            "procedure": ProcedureIngestionPipeline(
                settings=settings,
                loader=self._procedure_loader,
            ),
            "procedure_ed": ProcedureEDIngestionPipeline(
                settings=settings,
                loader=self._procedure_ed_loader,
            ),
            "procedure_icu": ProcedureICUIngestionPipeline(
                settings=settings,
                loader=self._procedure_icu_loader,
            ),
            "observation_labevents": ObservationLabeventsIngestionPipeline(
                settings=settings,
                loader=self._observation_labevents_loader,
            ),
            "observation_micro_test": ObservationMicroTestIngestionPipeline(
                settings=settings,
                loader=self._observation_micro_test_loader,
            ),
            "observation_micro_org": ObservationMicroOrgIngestionPipeline(
                settings=settings,
                loader=self._observation_micro_org_loader,
            ),
            "observation_micro_susc": ObservationMicroSuscIngestionPipeline(
                settings=settings,
                loader=self._observation_micro_susc_loader,
            ),
            "observation_chartevents": ObservationCharteventsIngestionPipeline(
                settings=settings,
                loader=self._observation_chartevents_loader,
            ),
        }

    def run(self) -> IngestionRunSummary:
        """
        Executa a ingestão completa em uma única transação.
        """

        if self._settings.common.reset_policy != "drop_and_recreate":
            raise ValueError("A política de reset suportada é 'drop_and_recreate'.")
        if self._settings.resources.execution_order != (
            "organization",
            "location",
            "patient",
            "encounter",
            "encounter_ed",
            "encounter_icu",
            "medication",
            "medication_mix",
            "medication_request",
            "specimen",
            "condition",
            "condition_ed",
            "procedure",
            "procedure_ed",
            "procedure_icu",
            "observation_labevents",
            "observation_micro_test",
            "observation_micro_org",
            "observation_micro_susc",
            "observation_chartevents",
        ):
            raise ValueError(
                "A ordem de ingestão suportada deve ser ('organization', 'location', 'patient', 'encounter', 'encounter_ed', 'encounter_icu', 'medication', 'medication_mix', 'medication_request', 'specimen', 'condition', 'condition_ed', 'procedure', 'procedure_ed', 'procedure_icu', 'observation_labevents', 'observation_micro_test', 'observation_micro_org', 'observation_micro_susc', 'observation_chartevents')."
            )

        started_at = perf_counter()
        LOGGER.info(
            "Iniciando processo de ingestão completo com ordem: %s",
            self._settings.resources.execution_order,
        )

        resource_summaries: dict[str, ResourceIngestionSummary] = {}
        with self._engine.begin() as connection:
            self._reset_and_create_schema(connection)
            for resource_name in self._settings.resources.execution_order:
                LOGGER.info("Executando recurso %s", resource_name)
                pipeline = self._pipelines[resource_name]
                resource_summaries[resource_name] = pipeline.ingest(connection)

        elapsed_seconds = perf_counter() - started_at
        table_counts = _merge_table_counts(summary.table_counts for summary in resource_summaries.values())
        summary = IngestionRunSummary(
            resource_summaries=resource_summaries,
            elapsed_seconds=elapsed_seconds,
            table_counts=table_counts,
        )
        LOGGER.info(
            "Resumo final: ordem=%s tempo=%.2fs tabelas=%s",
            self._settings.resources.execution_order,
            summary.elapsed_seconds,
            summary.table_counts,
        )
        return summary

    def _reset_and_create_schema(self, connection: Connection) -> None:
        """
        Remove e recria o schema, seguido da criação de todas as tabelas.
        """

        reset_schema(connection, self._settings.database.schema_name)
        self._metadata.create_all(connection)
        LOGGER.info("Schema resetado e tabelas criadas: %s", self._settings.database.schema_name)


def _merge_table_counts(counts: Iterable[dict[str, int]]) -> dict[str, int]:
    """
    Soma contagens de tabelas provenientes de todos os recursos.
    """

    merged: dict[str, int] = {}
    for summary_counts in counts:
        for table_name, value in summary_counts.items():
            merged[table_name] = merged.get(table_name, 0) + value
    return merged
