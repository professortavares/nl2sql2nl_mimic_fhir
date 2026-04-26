"""
Serviço de montagem da timeline clínica individual.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from time import perf_counter
from typing import Any, Protocol

from sqlalchemy.engine import Connection

from src.app.models.patient_timeline import (
    EncounterSummary,
    EncounterTimeline,
    PatientProfile,
    PatientTimeline,
)
from src.app.repositories.clinical_events_repository import ClinicalEventsRepository
from src.app.repositories.encounter_repository import EncounterRepository
from src.app.repositories.patient_repository import PatientRepository
from src.config.settings import ProjectSettings

LOGGER = logging.getLogger(__name__)


class PatientRepositoryProtocol(Protocol):
    """Contrato para repositórios de paciente."""

    def fetch_patient(self, connection: Connection, patient_id: str) -> dict[str, Any] | None:
        """Busca o paciente pelo ID."""


class EncounterRepositoryProtocol(Protocol):
    """Contrato para repositórios de encounter."""

    def list_by_patient_id(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        """Lista encounters de um paciente."""


class ClinicalEventsRepositoryProtocol(Protocol):
    """Contrato para repositórios de eventos clínicos."""

    def list_conditions(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista diagnósticos."""

    def list_procedures(self, connection: Connection, encounter_id: str) -> dict[str, list[dict[str, Any]]]:
        """Lista procedimentos agrupados."""

    def list_medications(self, connection: Connection, encounter_id: str) -> dict[str, list[dict[str, Any]]]:
        """Lista medicações agrupadas."""

    def list_labevents(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        """Lista observações laboratoriais."""

    def list_micro_tests(
        self,
        connection: Connection,
        patient_id: str,
        encounter_id: str,
    ) -> list[dict[str, Any]]:
        """Lista testes microbiológicos."""

    def list_micro_orgs(self, connection: Connection, test_ids: list[str]) -> list[dict[str, Any]]:
        """Lista organismos microbiológicos."""

    def list_micro_suscs(self, connection: Connection, org_ids: list[str]) -> list[dict[str, Any]]:
        """Lista susceptibilidades microbiológicas."""

    def list_charted_observations(
        self,
        connection: Connection,
        encounter_id: str,
    ) -> dict[str, list[dict[str, Any]]]:
        """Lista observações charted."""

    def list_vital_sign_components(
        self,
        connection: Connection,
        observation_ids: list[str],
    ) -> list[dict[str, Any]]:
        """Lista componentes de sinais vitais."""

    def list_specimens(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        """Lista specimens do paciente."""


class PatientNotFoundError(LookupError):
    """Indica que o paciente não existe na base."""


class TimelineQueryError(RuntimeError):
    """Indica falha ao montar a timeline."""


@dataclass(slots=True, frozen=True)
class TimelineRepositories:
    """Agrupa os repositórios usados pelo serviço."""

    patient_repository: PatientRepositoryProtocol
    encounter_repository: EncounterRepositoryProtocol
    clinical_events_repository: ClinicalEventsRepositoryProtocol


class PatientTimelineService:
    """Monta a visão cronológica de um paciente a partir da base relacional."""

    def __init__(self, repositories: TimelineRepositories) -> None:
        self._repositories = repositories

    def build_timeline(self, connection: Connection, patient_id: str) -> PatientTimeline:
        """
        Monta a timeline clínica de um paciente.
        """

        normalized_patient_id = patient_id.strip()
        if not normalized_patient_id:
            raise ValueError("Patient ID vazio.")

        started_at = perf_counter()
        LOGGER.info("Iniciando busca da timeline para patient_id=%s", normalized_patient_id)

        try:
            patient_row = self._repositories.patient_repository.fetch_patient(connection, normalized_patient_id)
            if patient_row is None:
                raise PatientNotFoundError(f"Paciente não encontrado: {normalized_patient_id}")

            patient = _build_patient_profile(patient_row)
            encounter_rows = self._repositories.encounter_repository.list_by_patient_id(
                connection,
                normalized_patient_id,
            )
            LOGGER.info(
                "Encontrados %s encounters para patient_id=%s",
                len(encounter_rows),
                normalized_patient_id,
            )
            encounters = [
                self._build_encounter_timeline(
                    connection=connection,
                    patient_id=patient.id,
                    encounter_row=encounter_row,
                )
                for encounter_row in sorted(encounter_rows, key=_encounter_sort_key)
            ]
            timeline = PatientTimeline(patient=patient, encounters=encounters)
            LOGGER.info(
                "Timeline montada para patient_id=%s em %.2fs com %s encounters",
                normalized_patient_id,
                perf_counter() - started_at,
                len(encounters),
            )
            return timeline
        except PatientNotFoundError:
            raise
        except Exception as exc:
            LOGGER.exception("Falha ao montar a timeline para patient_id=%s", normalized_patient_id)
            raise TimelineQueryError("Não foi possível montar a timeline do paciente.") from exc

    def _build_encounter_timeline(
        self,
        *,
        connection: Connection,
        patient_id: str,
        encounter_row: dict[str, Any],
    ) -> EncounterTimeline:
        """
        Monta os dados clínicos de um encounter.
        """

        summary = _build_encounter_summary(encounter_row)
        diagnoses = self._repositories.clinical_events_repository.list_conditions(connection, summary.id)
        procedures = self._repositories.clinical_events_repository.list_procedures(connection, summary.id)
        medications = self._repositories.clinical_events_repository.list_medications(connection, summary.id)
        laboratory = self._filter_rows_by_interval(
            rows=self._repositories.clinical_events_repository.list_labevents(connection, patient_id),
            time_field="effective_at",
            start_value=summary.start_date,
            end_value=summary.end_date,
        )
        micro_tests = self._filter_micro_tests(
            rows=self._repositories.clinical_events_repository.list_micro_tests(
                connection,
                patient_id,
                summary.id,
            ),
            summary=summary,
        )
        micro_test_ids = [str(row["id"]) for row in micro_tests if row.get("id") is not None]
        micro_orgs = self._repositories.clinical_events_repository.list_micro_orgs(connection, micro_test_ids)
        micro_orgs = [
            row
            for row in micro_orgs
            if row.get("derived_from_observation_micro_test_id") in micro_test_ids
        ]
        micro_org_ids = [str(row["id"]) for row in micro_orgs if row.get("id") is not None]
        micro_suscs = self._repositories.clinical_events_repository.list_micro_suscs(connection, micro_org_ids)
        micro_suscs = [
            row
            for row in micro_suscs
            if row.get("derived_from_observation_micro_org_id") in micro_org_ids
        ]
        charted_observations = self._repositories.clinical_events_repository.list_charted_observations(
            connection,
            summary.id,
        )
        vital_signs = charted_observations.get("observation_vital_signs_ed", [])
        components = self._repositories.clinical_events_repository.list_vital_sign_components(
            connection,
            [str(row["id"]) for row in vital_signs if row.get("id") is not None],
        )
        charted_observations["observation_vital_signs_ed"] = _attach_components_to_vital_signs(
            vital_signs,
            components,
        )
        specimens = self._filter_rows_by_interval(
            rows=self._repositories.clinical_events_repository.list_specimens(connection, patient_id),
            time_field="collected_at",
            start_value=summary.start_date,
            end_value=summary.end_date,
        )
        return EncounterTimeline(
            summary=summary,
            diagnoses=diagnoses,
            procedures=procedures,
            medications=medications,
            laboratory=laboratory,
            microbiology={
                "observation_micro_test": micro_tests,
                "observation_micro_org": micro_orgs,
                "observation_micro_susc": micro_suscs,
            },
            charted_observations=charted_observations,
            specimens=specimens,
        )

    def _filter_rows_by_interval(
        self,
        *,
        rows: list[dict[str, Any]],
        time_field: str,
        start_value: str | None,
        end_value: str | None,
    ) -> list[dict[str, Any]]:
        """Filtra registros por janela temporal."""

        start_dt = _parse_datetime(start_value)
        end_dt = _parse_datetime(end_value)
        if start_dt is None and end_dt is None:
            return rows

        filtered_rows: list[dict[str, Any]] = []
        for row in rows:
            row_dt = _parse_datetime(row.get(time_field))
            if row_dt is None:
                continue
            if start_dt is not None and row_dt < start_dt:
                continue
            if end_dt is not None and row_dt > end_dt:
                continue
            filtered_rows.append(row)
        return filtered_rows

    def _filter_micro_tests(
        self,
        *,
        rows: list[dict[str, Any]],
        summary: EncounterSummary,
    ) -> list[dict[str, Any]]:
        """Filtra testes microbiológicos por vínculo e intervalo temporal."""

        start_dt = _parse_datetime(summary.start_date)
        end_dt = _parse_datetime(summary.end_date)
        if start_dt is None and end_dt is None:
            return rows

        filtered_rows: list[dict[str, Any]] = []
        for row in rows:
            if row.get("encounter_id") == summary.id:
                filtered_rows.append(row)
                continue
            row_dt = _parse_datetime(row.get("effective_at"))
            if row_dt is None:
                continue
            if start_dt is not None and row_dt < start_dt:
                continue
            if end_dt is not None and row_dt > end_dt:
                continue
            filtered_rows.append(row)
        return filtered_rows


def build_patient_timeline_service(settings: ProjectSettings) -> PatientTimelineService:
    """
    Constrói o serviço de timeline a partir das configurações do projeto.
    """

    repositories = TimelineRepositories(
        patient_repository=PatientRepository(
            schema_name=settings.database.schema_name,
            patient_table_name=settings.patient.table_name,
            organization_table_name=settings.organization.table_name,
        ),
        encounter_repository=EncounterRepository(
            schema_name=settings.database.schema_name,
            encounter_table_name=settings.encounter.table_name,
            organization_table_name=settings.organization.table_name,
        ),
        clinical_events_repository=ClinicalEventsRepository(
            schema_name=settings.database.schema_name,
            condition_table_name=settings.condition.table_name,
            condition_ed_table_name=settings.condition_ed.table_name,
            procedure_table_name=settings.procedure.table_name,
            procedure_ed_table_name=settings.procedure_ed.table_name,
            procedure_icu_table_name=settings.procedure_icu.table_name,
            medication_request_table_name=settings.medication_request.table_name,
            medication_dispense_table_name=settings.medication_dispense.table_name,
            medication_dispense_ed_table_name=settings.medication_dispense_ed.table_name,
            medication_administration_table_name=settings.medication_administration.table_name,
            medication_administration_icu_table_name=settings.medication_administration_icu.table_name,
            medication_statement_ed_table_name=settings.medication_statement_ed.table_name,
            observation_labevents_table_name=settings.observation_labevents.table_name,
            observation_micro_test_table_name=settings.observation_micro_test.table_name,
            observation_micro_org_table_name=settings.observation_micro_org.table_name,
            observation_micro_susc_table_name=settings.observation_micro_susc.table_name,
            observation_chartevents_table_name=settings.observation_chartevents.table_name,
            observation_datetimeevents_table_name=settings.observation_datetimeevents.table_name,
            observation_outputevents_table_name=settings.observation_outputevents.table_name,
            observation_ed_table_name=settings.observation_ed.table_name,
            observation_vital_signs_ed_table_name=settings.observation_vital_signs_ed.table_name,
            observation_vital_signs_ed_component_table_name=settings.observation_vital_signs_ed.auxiliary_table_name
            or "observation_vital_signs_ed_component",
            specimen_table_name=settings.specimen.table_name,
        ),
    )
    return PatientTimelineService(repositories=repositories)


def _build_patient_profile(row: dict[str, Any]) -> PatientProfile:
    """Converte uma linha de paciente em modelo tipado."""

    return PatientProfile(
        id=str(row["id"]),
        name=row.get("name"),
        gender=row.get("gender"),
        birth_date=row.get("birth_date"),
        identifier=row.get("identifier"),
        race=row.get("race"),
        ethnicity=row.get("ethnicity"),
        birthsex=row.get("birthsex"),
        managing_organization_id=row.get("managing_organization_id"),
        managing_organization_name=row.get("managing_organization_name"),
    )


def _build_encounter_summary(row: dict[str, Any]) -> EncounterSummary:
    """Converte uma linha de encounter em resumo tipado."""

    return EncounterSummary(
        id=str(row["id"]),
        status=row.get("status"),
        class_code=row.get("class_code"),
        start_date=row.get("start_date"),
        end_date=row.get("end_date"),
        organization_id=row.get("organization_id"),
        organization_name=row.get("organization_name"),
        admit_source_code=row.get("admit_source_code"),
        discharge_disposition_code=row.get("discharge_disposition_code"),
        service_type_code=row.get("service_type_code"),
        priority_code=row.get("priority_code"),
    )


def _encounter_sort_key(row: dict[str, Any]) -> tuple[int, str, int, str, str]:
    """Ordena encounters por data de início, fim e id."""

    start_value = row.get("start_date")
    end_value = row.get("end_date")
    identifier = str(row.get("id") or "")
    return (
        1 if start_value is None else 0,
        str(start_value or ""),
        1 if end_value is None else 0,
        str(end_value or ""),
        identifier,
    )


def _attach_components_to_vital_signs(
    vital_signs: list[dict[str, Any]],
    components: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Anexa componentes aos registros de sinais vitais."""

    components_by_observation_id: dict[str, list[dict[str, Any]]] = {}
    for component in components:
        observation_id = component.get("observation_vital_signs_ed_id")
        if observation_id is None:
            continue
        components_by_observation_id.setdefault(str(observation_id), []).append(component)

    enriched_vital_signs: list[dict[str, Any]] = []
    for row in vital_signs:
        observation_id = str(row.get("id") or "")
        enriched_row = dict(row)
        enriched_row["components"] = components_by_observation_id.get(observation_id, [])
        enriched_vital_signs.append(enriched_row)
    return enriched_vital_signs


def _parse_datetime(value: Any) -> datetime | None:
    """Converte strings ISO em `datetime` quando possível."""

    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        if len(normalized) == 10:
            try:
                return datetime.fromisoformat(f"{normalized}T00:00:00")
            except ValueError:
                return None
        return None
