"""
Repositório de dados do contexto General Hospital.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy.engine import Connection

from src.app.repositories.base import fetch_mappings, fetch_mappings_expanding, qualified_table_name


class GeneralHospitalRepository:
    """Consulta dados clínicos do hospital geral."""

    def __init__(
        self,
        *,
        schema_name: str,
        encounter_location_table_name: str,
        location_table_name: str,
        condition_table_name: str,
        procedure_table_name: str,
        medication_table_name: str,
        medication_request_table_name: str,
        medication_dispense_table_name: str,
        medication_administration_table_name: str,
        observation_labevents_table_name: str,
        observation_micro_test_table_name: str,
        observation_micro_org_table_name: str,
        observation_micro_susc_table_name: str,
        specimen_table_name: str,
    ) -> None:
        self._schema_name = schema_name
        self._encounter_location_table_name = encounter_location_table_name
        self._location_table_name = location_table_name
        self._condition_table_name = condition_table_name
        self._procedure_table_name = procedure_table_name
        self._medication_table_name = medication_table_name
        self._medication_request_table_name = medication_request_table_name
        self._medication_dispense_table_name = medication_dispense_table_name
        self._medication_administration_table_name = medication_administration_table_name
        self._observation_labevents_table_name = observation_labevents_table_name
        self._observation_micro_test_table_name = observation_micro_test_table_name
        self._observation_micro_org_table_name = observation_micro_org_table_name
        self._observation_micro_susc_table_name = observation_micro_susc_table_name
        self._specimen_table_name = specimen_table_name

    def list_encounter_locations(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista as transferencias hospitalares de um encounter."""

        sql = f"""
            SELECT
                el.start_date,
                el.end_date,
                l.name AS location_name
            FROM {qualified_table_name(self._schema_name, self._encounter_location_table_name)} AS el
            INNER JOIN {qualified_table_name(self._schema_name, self._location_table_name)} AS l
                ON el.location_id = l.id
            WHERE el.encounter_id = :encounter_id
            ORDER BY el.start_date ASC
        """
        return fetch_mappings(connection, sql, {"encounter_id": encounter_id})

    def list_conditions(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista diagnósticos."""

        return self._select_by_encounter(connection, self._condition_table_name, encounter_id)

    def list_procedures(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista procedimentos."""

        return self._select_by_encounter(connection, self._procedure_table_name, encounter_id)

    def list_medication_requests(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista pedidos de medicação."""

        return self._select_by_encounter(connection, self._medication_request_table_name, encounter_id)

    def list_medication_dispenses(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista dispensações de medicação."""

        return self._select_by_encounter(connection, self._medication_dispense_table_name, encounter_id)

    def list_medication_administrations(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista administrações de medicação."""

        return self._select_by_encounter(connection, self._medication_administration_table_name, encounter_id)

    def list_medication_events(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista pedidos e administrações de medicação de um encounter."""

        sql = f"""
            SELECT
                mr.id AS medication_request_id,
                mr.validity_start,
                mr.validity_end,
                COALESCE(m.name, ma.medication_code) AS medication_name,
                mr.frequency_code,
                mr.status AS request_status,
                mr.intent AS request_intent,
                mr.identifier AS request_identifier,
                ma.id AS medication_administration_id,
                ma.effective_at,
                ma.dose_value,
                ma.dose_unit,
                ma.status
            FROM {qualified_table_name(self._schema_name, self._medication_request_table_name)} AS mr
            LEFT JOIN {qualified_table_name(self._schema_name, self._medication_table_name)} AS m
                ON m.id = mr.medication_id
            LEFT JOIN {qualified_table_name(self._schema_name, self._medication_administration_table_name)} AS ma
                ON ma.medication_request_id = mr.id
            WHERE mr.encounter_id = :encounter_id
            ORDER BY CASE WHEN ma.effective_at IS NULL THEN 1 ELSE 0 END,
                ma.effective_at ASC,
                mr.validity_start ASC,
                mr.id ASC,
                ma.id ASC
        """
        return fetch_mappings(connection, sql, {"encounter_id": encounter_id})

    def list_labevents(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        """Lista exames laboratoriais do paciente."""

        return self._select_by_patient(connection, self._observation_labevents_table_name, patient_id)

    def list_micro_tests(self, connection: Connection, patient_id: str, encounter_id: str) -> list[dict[str, Any]]:
        """Lista testes microbiológicos associados ao paciente ou encounter."""

        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, self._observation_micro_test_table_name)}
            WHERE patient_id = :patient_id OR encounter_id = :encounter_id
        """
        return fetch_mappings(connection, sql, {"patient_id": patient_id, "encounter_id": encounter_id})

    def list_micro_orgs(self, connection: Connection, test_ids: Iterable[str]) -> list[dict[str, Any]]:
        """Lista organismos microbiológicos derivados dos testes informados."""

        normalized_ids = tuple(test_ids)
        if not normalized_ids:
            return []
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, self._observation_micro_org_table_name)}
            WHERE derived_from_observation_micro_test_id IN :test_ids
        """
        return fetch_mappings_expanding(
            connection,
            sql,
            {"test_ids": normalized_ids},
            expanding_parameter_names=("test_ids",),
        )

    def list_micro_suscs(self, connection: Connection, org_ids: Iterable[str]) -> list[dict[str, Any]]:
        """Lista susceptibilidades derivadas dos organismos informados."""

        normalized_ids = tuple(org_ids)
        if not normalized_ids:
            return []
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, self._observation_micro_susc_table_name)}
            WHERE derived_from_observation_micro_org_id IN :org_ids
        """
        return fetch_mappings_expanding(
            connection,
            sql,
            {"org_ids": normalized_ids},
            expanding_parameter_names=("org_ids",),
        )

    def list_specimens(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        """Lista specimen do paciente."""

        return self._select_by_patient(connection, self._specimen_table_name, patient_id)

    def _select_by_encounter(self, connection: Connection, table_name: str, encounter_id: str) -> list[dict[str, Any]]:
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, table_name)}
            WHERE encounter_id = :encounter_id
        """
        return fetch_mappings(connection, sql, {"encounter_id": encounter_id})

    def _select_by_patient(self, connection: Connection, table_name: str, patient_id: str) -> list[dict[str, Any]]:
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, table_name)}
            WHERE patient_id = :patient_id
        """
        return fetch_mappings(connection, sql, {"patient_id": patient_id})
