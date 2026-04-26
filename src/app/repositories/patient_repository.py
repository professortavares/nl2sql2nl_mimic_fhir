"""
Repositório de consulta de pacientes.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.app.repositories.base import fetch_mappings, qualified_table_name


class PatientRepository:
    """Consulta dados de pacientes com apoio da organização gestora."""

    def __init__(self, *, schema_name: str, patient_table_name: str, organization_table_name: str) -> None:
        self._schema_name = schema_name
        self._patient_table_name = patient_table_name
        self._organization_table_name = organization_table_name

    def fetch_patient(self, connection: Connection, patient_id: str) -> dict[str, Any] | None:
        """
        Busca um paciente pelo identificador.
        """

        sql = f"""
            SELECT
                p.*,
                o.name AS managing_organization_name
            FROM {qualified_table_name(self._schema_name, self._patient_table_name)} AS p
            LEFT JOIN {qualified_table_name(self._schema_name, self._organization_table_name)} AS o
                ON o.id = p.managing_organization_id
            WHERE p.id = :patient_id
            LIMIT 1
        """
        rows = fetch_mappings(connection, sql, {"patient_id": patient_id})
        return rows[0] if rows else None
