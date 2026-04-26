"""
Repositório de consulta de encounters.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.app.repositories.base import fetch_mappings, qualified_table_name


class EncounterRepository:
    """Consulta encounters associados a um paciente."""

    def __init__(self, *, schema_name: str, encounter_table_name: str, organization_table_name: str) -> None:
        self._schema_name = schema_name
        self._encounter_table_name = encounter_table_name
        self._organization_table_name = organization_table_name

    def list_by_patient_id(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        """
        Lista todos os encounters de um paciente.
        """

        sql = f"""
            SELECT
                e.*,
                o.name AS organization_name
            FROM {qualified_table_name(self._schema_name, self._encounter_table_name)} AS e
            LEFT JOIN {qualified_table_name(self._schema_name, self._organization_table_name)} AS o
                ON o.id = e.organization_id
            WHERE e.patient_id = :patient_id
        """
        return fetch_mappings(connection, sql, {"patient_id": patient_id})
