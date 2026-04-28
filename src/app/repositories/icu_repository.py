"""
Repositório de dados do contexto Intensive Care Unit.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.app.repositories.base import fetch_mappings, qualified_table_name


class IcuRepository:
    """Consulta dados clínicos da UTI."""

    def __init__(
        self,
        *,
        schema_name: str,
        encounter_icu_table_name: str,
        procedure_icu_table_name: str,
        medication_administration_icu_table_name: str,
        observation_chartevents_table_name: str,
        observation_datetimeevents_table_name: str,
        observation_outputevents_table_name: str,
    ) -> None:
        self._schema_name = schema_name
        self._encounter_icu_table_name = encounter_icu_table_name
        self._procedure_icu_table_name = procedure_icu_table_name
        self._medication_administration_icu_table_name = medication_administration_icu_table_name
        self._observation_chartevents_table_name = observation_chartevents_table_name
        self._observation_datetimeevents_table_name = observation_datetimeevents_table_name
        self._observation_outputevents_table_name = observation_outputevents_table_name

    def list_encounter_icu(self, connection: Connection, patient_id: str, encounter_id: str) -> list[dict[str, Any]]:
        """Lista permanências em UTI."""

        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, self._encounter_icu_table_name)}
            WHERE encounter_id = :encounter_id OR patient_id = :patient_id
        """
        return fetch_mappings(connection, sql, {"encounter_id": encounter_id, "patient_id": patient_id})

    def list_procedures(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista procedimentos em UTI."""

        return self._select_by_encounter(connection, self._procedure_icu_table_name, encounter_id)

    def list_medication_administrations(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista administrações de medicação em UTI."""

        return self._select_by_encounter(connection, self._medication_administration_icu_table_name, encounter_id)

    def list_charted_events(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista eventos charted em UTI."""

        return self._select_by_encounter(connection, self._observation_chartevents_table_name, encounter_id)

    def list_datetime_events(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista eventos com data/hora em UTI."""

        return self._select_by_encounter(connection, self._observation_datetimeevents_table_name, encounter_id)

    def list_output_events(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista output events em UTI."""

        return self._select_by_encounter(connection, self._observation_outputevents_table_name, encounter_id)

    def _select_by_encounter(self, connection: Connection, table_name: str, encounter_id: str) -> list[dict[str, Any]]:
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, table_name)}
            WHERE encounter_id = :encounter_id
        """
        return fetch_mappings(connection, sql, {"encounter_id": encounter_id})
