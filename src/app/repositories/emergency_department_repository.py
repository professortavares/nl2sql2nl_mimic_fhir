"""
Repositório de dados do contexto Emergency Department.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.app.repositories.base import fetch_mappings, fetch_mappings_expanding, qualified_table_name


class EmergencyDepartmentRepository:
    """Consulta dados clínicos do departamento de emergência."""

    def __init__(
        self,
        *,
        schema_name: str,
        encounter_ed_table_name: str,
        condition_ed_table_name: str,
        procedure_ed_table_name: str,
        observation_ed_table_name: str,
        observation_vital_signs_ed_table_name: str,
        observation_vital_signs_ed_component_table_name: str,
        medication_dispense_ed_table_name: str,
        medication_statement_ed_table_name: str,
    ) -> None:
        self._schema_name = schema_name
        self._encounter_ed_table_name = encounter_ed_table_name
        self._condition_ed_table_name = condition_ed_table_name
        self._procedure_ed_table_name = procedure_ed_table_name
        self._observation_ed_table_name = observation_ed_table_name
        self._observation_vital_signs_ed_table_name = observation_vital_signs_ed_table_name
        self._observation_vital_signs_ed_component_table_name = observation_vital_signs_ed_component_table_name
        self._medication_dispense_ed_table_name = medication_dispense_ed_table_name
        self._medication_statement_ed_table_name = medication_statement_ed_table_name

    def list_encounter_ed(self, connection: Connection, patient_id: str, encounter_id: str) -> list[dict[str, Any]]:
        """Lista permanências no ED."""

        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, self._encounter_ed_table_name)}
            WHERE encounter_id = :encounter_id OR patient_id = :patient_id
        """
        return fetch_mappings(connection, sql, {"encounter_id": encounter_id, "patient_id": patient_id})

    def list_conditions(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista diagnósticos do ED."""

        return self._select_by_encounter(connection, self._condition_ed_table_name, encounter_id)

    def list_procedures(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista procedimentos do ED."""

        return self._select_by_encounter(connection, self._procedure_ed_table_name, encounter_id)

    def list_observations(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista observações do ED."""

        return self._select_by_encounter(connection, self._observation_ed_table_name, encounter_id)

    def list_vital_signs(
        self,
        connection: Connection,
        encounter_id: str,
    ) -> list[dict[str, Any]]:
        """Lista sinais vitais do ED."""

        return self._select_by_encounter(connection, self._observation_vital_signs_ed_table_name, encounter_id)

    def list_vital_sign_components(
        self,
        connection: Connection,
        observation_ids: list[str],
    ) -> list[dict[str, Any]]:
        """Lista componentes associados aos sinais vitais."""

        if not observation_ids:
            return []
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, self._observation_vital_signs_ed_component_table_name)}
            WHERE observation_vital_signs_ed_id IN :observation_ids
        """

        return fetch_mappings_expanding(
            connection,
            sql,
            {"observation_ids": tuple(observation_ids)},
            expanding_parameter_names=("observation_ids",),
        )

    def list_medication_dispenses(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista dispensações do ED."""

        return self._select_by_encounter(connection, self._medication_dispense_ed_table_name, encounter_id)

    def list_medication_statements(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista medication statements do ED."""

        return self._select_by_encounter(connection, self._medication_statement_ed_table_name, encounter_id)

    def _select_by_encounter(self, connection: Connection, table_name: str, encounter_id: str) -> list[dict[str, Any]]:
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, table_name)}
            WHERE encounter_id = :encounter_id
        """
        return fetch_mappings(connection, sql, {"encounter_id": encounter_id})
