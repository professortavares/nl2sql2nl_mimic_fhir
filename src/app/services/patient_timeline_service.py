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
from src.app.repositories.emergency_department_repository import EmergencyDepartmentRepository
from src.app.repositories.general_hospital_repository import GeneralHospitalRepository
from src.app.repositories.icu_repository import IcuRepository
from src.app.repositories.encounter_repository import EncounterRepository
from src.app.repositories.patient_repository import PatientRepository
from src.config.settings import ProjectSettings

LOGGER = logging.getLogger(__name__)


class PatientRepositoryProtocol(Protocol):
    """Contrato para repositórios de paciente."""

    def fetch_patient(self, connection: Connection, patient_id: str) -> dict[str, Any] | None:
        """Busca o paciente pelo ID."""


class EncounterRepositoryProtocol(Protocol):
    """Contrato para repositórios de encounters."""

    def list_by_patient_id(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        """Lista encounters por paciente."""


class GeneralHospitalRepositoryProtocol(Protocol):
    """Contrato para consultas do contexto geral."""

    def list_conditions(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_procedures(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_medication_requests(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_medication_dispenses(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_medication_administrations(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_labevents(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        ...

    def list_micro_tests(self, connection: Connection, patient_id: str, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_micro_orgs(self, connection: Connection, test_ids: list[str]) -> list[dict[str, Any]]:
        ...

    def list_micro_suscs(self, connection: Connection, org_ids: list[str]) -> list[dict[str, Any]]:
        ...

    def list_specimens(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        ...


class EmergencyDepartmentRepositoryProtocol(Protocol):
    """Contrato para consultas do contexto de emergência."""

    def list_encounter_ed(self, connection: Connection, patient_id: str, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_conditions(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_procedures(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_observations(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_vital_signs(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_vital_sign_components(self, connection: Connection, observation_ids: list[str]) -> list[dict[str, Any]]:
        ...

    def list_medication_dispenses(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_medication_statements(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...


class IcuRepositoryProtocol(Protocol):
    """Contrato para consultas do contexto ICU."""

    def list_encounter_icu(self, connection: Connection, patient_id: str, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_procedures(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_medication_administrations(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_charted_events(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_datetime_events(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...

    def list_output_events(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        ...


class PatientNotFoundError(LookupError):
    """Indica que o paciente não existe na base."""


class TimelineQueryError(RuntimeError):
    """Indica falha ao montar a timeline."""


@dataclass(slots=True, frozen=True)
class TimelineRepositories:
    """Agrupa os repositórios usados pelo serviço."""

    patient_repository: PatientRepositoryProtocol
    encounter_repository: EncounterRepositoryProtocol
    general_hospital_repository: GeneralHospitalRepositoryProtocol
    emergency_department_repository: EmergencyDepartmentRepositoryProtocol
    icu_repository: IcuRepositoryProtocol


@dataclass(slots=True, frozen=True)
class TimelineBuildResult:
    """Resumo auxiliar da montagem da timeline."""

    patient: PatientProfile
    encounters: list[EncounterTimeline]


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
            encounter_rows = sorted(encounter_rows, key=_encounter_sort_key)
            LOGGER.info(
                "Encontrados %s encounters para patient_id=%s",
                len(encounter_rows),
                normalized_patient_id,
            )
            encounters = [
                self._build_encounter_timeline(
                    connection=connection,
                    patient=patient,
                    encounter_row=encounter_row,
                )
                for encounter_row in encounter_rows
            ]
            result = TimelineBuildResult(patient=patient, encounters=encounters)
            LOGGER.info(
                "Timeline montada para patient_id=%s em %.2fs com %s encounters",
                normalized_patient_id,
                perf_counter() - started_at,
                len(encounters),
            )
            return PatientTimeline(patient=result.patient, encounters=result.encounters)
        except PatientNotFoundError:
            raise
        except Exception as exc:
            LOGGER.exception("Falha ao montar a timeline para patient_id=%s", normalized_patient_id)
            raise TimelineQueryError("Não foi possível montar a timeline do paciente.") from exc

    def _build_encounter_timeline(
        self,
        *,
        connection: Connection,
        patient: PatientProfile,
        encounter_row: dict[str, Any],
    ) -> EncounterTimeline:
        """
        Monta os dados clínicos de um encounter separados por contexto.
        """

        summary = _build_encounter_summary(encounter_row)
        general_hospital = self._build_general_hospital_context(connection, patient, summary)
        emergency_department = self._build_emergency_department_context(connection, patient, summary)
        icu = self._build_icu_context(connection, patient, summary)
        LOGGER.info(
            "Contextos montados para encounter_id=%s: GH=%s ED=%s ICU=%s",
            summary.id,
            _count_context_events(general_hospital),
            _count_context_events(emergency_department),
            _count_context_events(icu),
        )
        return EncounterTimeline(
            summary=summary,
            general_hospital=general_hospital,
            emergency_department=emergency_department,
            icu=icu,
        )

    def _build_general_hospital_context(
        self,
        connection: Connection,
        patient: PatientProfile,
        summary: EncounterSummary,
    ) -> dict[str, Any]:
        """Monta o contexto hospitalar geral."""

        repo = self._repositories.general_hospital_repository
        diagnoses = _sort_rows(
            repo.list_conditions(connection, summary.id),
            ("category_code", "condition_code"),
        )
        procedures = _sort_rows(repo.list_procedures(connection, summary.id), ("performed_at", "procedure_code"))
        medication_requests = _sort_rows(
            repo.list_medication_requests(connection, summary.id),
            ("authored_on", "medication_code"),
        )
        medication_dispenses = _sort_rows(
            repo.list_medication_dispenses(connection, summary.id),
            ("effective_at", "medication_code"),
        )
        medication_administrations = _sort_rows(
            repo.list_medication_administrations(connection, summary.id),
            ("effective_at", "medication_code"),
        )
        labs = _filter_rows_by_interval(
            rows=repo.list_labevents(connection, patient.id),
            time_field="effective_at",
            start_value=summary.start_date,
            end_value=summary.end_date,
        )
        labs = _sort_rows(labs, ("effective_at", "id"))
        micro_tests = _filter_micro_tests_by_context(
            rows=repo.list_micro_tests(connection, patient.id, summary.id),
            encounter_id=summary.id,
            start_value=summary.start_date,
            end_value=summary.end_date,
        )
        micro_tests = _sort_rows(micro_tests, ("effective_at", "id"))
        micro_test_ids = [str(row["id"]) for row in micro_tests if row.get("id") is not None]
        micro_orgs = repo.list_micro_orgs(connection, micro_test_ids)
        micro_orgs = [row for row in micro_orgs if row.get("derived_from_observation_micro_test_id") in micro_test_ids]
        micro_orgs = _sort_rows(micro_orgs, ("derived_from_observation_micro_test_id", "id"))
        micro_org_ids = [str(row["id"]) for row in micro_orgs if row.get("id") is not None]
        micro_suscs = repo.list_micro_suscs(connection, micro_org_ids)
        micro_suscs = [
            row for row in micro_suscs if row.get("derived_from_observation_micro_org_id") in micro_org_ids
        ]
        micro_suscs = _sort_rows(micro_suscs, ("derived_from_observation_micro_org_id", "id"))
        specimens = _filter_rows_by_interval(
            rows=repo.list_specimens(connection, patient.id),
            time_field="collected_at",
            start_value=summary.start_date,
            end_value=summary.end_date,
        )
        specimens = _sort_rows(specimens, ("collected_at", "id"))
        return {
            "hospitalization": _to_mapping(summary),
            "diagnoses": diagnoses,
            "procedures": procedures,
            "medications": {
                "pedidos_de_medicacao": medication_requests,
                "dispensacoes": medication_dispenses,
                "administracoes": medication_administrations,
            },
            "labs": labs,
            "microbiology": {
                "testes": micro_tests,
                "organismos": micro_orgs,
                "susceptibilidades": micro_suscs,
            },
            "specimens": specimens,
        }

    def _build_emergency_department_context(
        self,
        connection: Connection,
        patient: PatientProfile,
        summary: EncounterSummary,
    ) -> dict[str, Any]:
        """Monta o contexto do departamento de emergência."""

        repo = self._repositories.emergency_department_repository
        encounter_ed = _pick_first_sorted(repo.list_encounter_ed(connection, patient.id, summary.id), ("start_date", "id"))
        diagnoses = _sort_rows(repo.list_conditions(connection, summary.id), ("category_code", "condition_code"))
        procedures = _sort_rows(repo.list_procedures(connection, summary.id), ("performed_at", "procedure_code"))
        observations = _sort_rows(repo.list_observations(connection, summary.id), ("effective_at", "issued_at"))
        vital_signs = _sort_rows(repo.list_vital_signs(connection, summary.id), ("effective_at", "observation_code"))
        vital_sign_components = repo.list_vital_sign_components(
            connection,
            [str(row["id"]) for row in vital_signs if row.get("id") is not None],
        )
        vital_signs = _attach_components_to_vital_signs(vital_signs, vital_sign_components)
        medication_dispenses = _sort_rows(
            repo.list_medication_dispenses(connection, summary.id),
            ("when_handed_over", "medication_code"),
        )
        medication_statements = _sort_rows(
            repo.list_medication_statements(connection, summary.id),
            ("date_asserted", "medication_code"),
        )
        return {
            "stay": _first_or_none_mapping(encounter_ed),
            "diagnoses": diagnoses,
            "procedures": procedures,
            "observations": observations,
            "vital_signs": vital_signs,
            "medications": {
                "dispensacoes_ed": medication_dispenses,
                "medication_statements_ed": medication_statements,
            },
        }

    def _build_icu_context(
        self,
        connection: Connection,
        patient: PatientProfile,
        summary: EncounterSummary,
    ) -> dict[str, Any]:
        """Monta o contexto da UTI."""

        repo = self._repositories.icu_repository
        encounter_icu = _pick_first_sorted(repo.list_encounter_icu(connection, patient.id, summary.id), ("start_date", "id"))
        procedures = _sort_rows(repo.list_procedures(connection, summary.id), ("performed_start", "performed_end"))
        medication_administrations = _sort_rows(
            repo.list_medication_administrations(connection, summary.id),
            ("effective_at", "medication_code"),
        )
        charted_events = _sort_rows(repo.list_charted_events(connection, summary.id), ("effective_at", "issued_at"))
        datetime_events = _sort_rows(repo.list_datetime_events(connection, summary.id), ("effective_at", "issued_at"))
        output_events = _sort_rows(repo.list_output_events(connection, summary.id), ("effective_at", "issued_at"))
        return {
            "stay": _first_or_none_mapping(encounter_icu),
            "procedures": procedures,
            "medications": medication_administrations,
            "charted_events": charted_events,
            "output_events": output_events,
            "datetime_events": datetime_events,
        }


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
        general_hospital_repository=GeneralHospitalRepository(
            schema_name=settings.database.schema_name,
            condition_table_name=settings.condition.table_name,
            procedure_table_name=settings.procedure.table_name,
            medication_request_table_name=settings.medication_request.table_name,
            medication_dispense_table_name=settings.medication_dispense.table_name,
            medication_administration_table_name=settings.medication_administration.table_name,
            observation_labevents_table_name=settings.observation_labevents.table_name,
            observation_micro_test_table_name=settings.observation_micro_test.table_name,
            observation_micro_org_table_name=settings.observation_micro_org.table_name,
            observation_micro_susc_table_name=settings.observation_micro_susc.table_name,
            specimen_table_name=settings.specimen.table_name,
        ),
        emergency_department_repository=EmergencyDepartmentRepository(
            schema_name=settings.database.schema_name,
            encounter_ed_table_name=settings.encounter_ed.table_name,
            condition_ed_table_name=settings.condition_ed.table_name,
            procedure_ed_table_name=settings.procedure_ed.table_name,
            observation_ed_table_name=settings.observation_ed.table_name,
            observation_vital_signs_ed_table_name=settings.observation_vital_signs_ed.table_name,
            observation_vital_signs_ed_component_table_name=settings.observation_vital_signs_ed.auxiliary_table_name
            or "observation_vital_signs_ed_component",
            medication_dispense_ed_table_name=settings.medication_dispense_ed.table_name,
            medication_statement_ed_table_name=settings.medication_statement_ed.table_name,
        ),
        icu_repository=IcuRepository(
            schema_name=settings.database.schema_name,
            encounter_icu_table_name=settings.encounter_icu.table_name,
            procedure_icu_table_name=settings.procedure_icu.table_name,
            medication_administration_icu_table_name=settings.medication_administration_icu.table_name,
            observation_chartevents_table_name=settings.observation_chartevents.table_name,
            observation_datetimeevents_table_name=settings.observation_datetimeevents.table_name,
            observation_outputevents_table_name=settings.observation_outputevents.table_name,
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
    """Ordena encounters por início, fim e id."""

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


def _sort_rows(rows: list[dict[str, Any]], date_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    """Ordena registros por campos temporais e depois por identificador."""

    def sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        parts: list[Any] = []
        for field_name in date_fields:
            value = row.get(field_name)
            parts.append(1 if value is None else 0)
            parts.append(str(value or ""))
        parts.append(str(row.get("id") or ""))
        return tuple(parts)

    return sorted(rows, key=sort_key)


def _filter_rows_by_interval(
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


def _filter_micro_tests_by_context(
    *,
    rows: list[dict[str, Any]],
    encounter_id: str,
    start_value: str | None,
    end_value: str | None,
) -> list[dict[str, Any]]:
    """Filtra testes microbiológicos mantendo vínculos diretos ao encounter."""

    start_dt = _parse_datetime(start_value)
    end_dt = _parse_datetime(end_value)
    if start_dt is None and end_dt is None:
        return rows

    filtered_rows: list[dict[str, Any]] = []
    for row in rows:
        if str(row.get("encounter_id") or "") == encounter_id:
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


def _pick_first_sorted(rows: list[dict[str, Any]], date_fields: tuple[str, ...]) -> dict[str, Any] | None:
    """Retorna o primeiro registro de uma lista ordenada ou `None`."""

    if not rows:
        return None
    return _first_or_none_mapping(_sort_rows(rows, date_fields)[0])


def _count_context_events(context: dict[str, Any]) -> int:
    """Conta o volume aproximado de eventos de um contexto."""

    total = 0
    for value in context.values():
        if isinstance(value, list):
            total += len(value)
        elif isinstance(value, dict):
            total += _count_context_events(value)
        elif value:
            total += 1
    return total


def _to_mapping(summary: EncounterSummary) -> dict[str, Any]:
    """Converte o resumo do encounter em mapeamento serializável."""

    return {
        "id": summary.id,
        "status": summary.status,
        "class_code": summary.class_code,
        "start_date": summary.start_date,
        "end_date": summary.end_date,
        "organization_id": summary.organization_id,
        "organization_name": summary.organization_name,
        "admit_source_code": summary.admit_source_code,
        "discharge_disposition_code": summary.discharge_disposition_code,
        "service_type_code": summary.service_type_code,
        "priority_code": summary.priority_code,
    }


def _first_or_none_mapping(row: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normaliza o retorno de um registro único."""

    if row is None:
        return None
    return dict(row)


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
