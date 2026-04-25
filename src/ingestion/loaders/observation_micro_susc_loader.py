"""
Persistência das linhas normalizadas de ObservationMicroSusc no PostgreSQL.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, Table, insert, select

from src.db.schema import ObservationMicroOrgTables, ObservationMicroSuscTables, PatientTables

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class ObservationMicroSuscBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de ObservationMicroSusc."""

    primary_rows: int
    orphan_patient_references: int = 0
    orphan_derived_from_references: int = 0

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"observation_micro_susc": self.primary_rows}


class ObservationMicroSuscLoader:
    """
    Persiste batches de ObservationMicroSusc na tabela simplificada.
    """

    def __init__(
        self,
        tables: ObservationMicroSuscTables,
        patient_tables: PatientTables,
        observation_micro_org_tables: ObservationMicroOrgTables,
    ) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables
        self._patient_tables = patient_tables
        self._observation_micro_org_tables = observation_micro_org_tables

    @property
    def tables(self) -> ObservationMicroSuscTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[dict[str, Any]],
    ) -> ObservationMicroSuscBatchInsertCounts:
        """
        Persiste um lote de observações microbiológicas de susceptibilidade.
        """

        if not batch:
            return ObservationMicroSuscBatchInsertCounts(0)

        normalized_batch = [dict(row) for row in batch]
        valid_patient_ids = self._fetch_existing_ids(
            connection=connection,
            table=self._patient_tables.patient,
            column_name="patient_id",
            batch=normalized_batch,
        )
        valid_derived_from_ids = self._fetch_existing_ids(
            connection=connection,
            table=self._observation_micro_org_tables.observation_micro_org,
            column_name="derived_from_observation_micro_org_id",
            batch=normalized_batch,
        )

        orphan_patient_references = self._nullify_orphan_references(
            batch=normalized_batch,
            reference_key="patient_id",
            valid_ids=valid_patient_ids,
            warning_label="patient_id",
        )
        orphan_derived_from_references = self._nullify_orphan_references(
            batch=normalized_batch,
            reference_key="derived_from_observation_micro_org_id",
            valid_ids=valid_derived_from_ids,
            warning_label="derived_from_observation_micro_org_id",
        )

        connection.execute(insert(self._tables.observation_micro_susc), normalized_batch)
        return ObservationMicroSuscBatchInsertCounts(
            primary_rows=len(normalized_batch),
            orphan_patient_references=orphan_patient_references,
            orphan_derived_from_references=orphan_derived_from_references,
        )

    def _fetch_existing_ids(
        self,
        *,
        connection: Connection,
        table: Table,
        column_name: str,
        batch: Sequence[dict[str, Any]],
    ) -> set[str]:
        """
        Busca os identificadores existentes para validar FKs.
        """

        requested_ids = {
            item_id
            for item_id in (row.get(column_name) for row in batch)
            if isinstance(item_id, str) and item_id.strip()
        }
        if not requested_ids:
            return set()

        statement = select(table.c.id).where(table.c.id.in_(requested_ids))
        return set(connection.execute(statement).scalars().all())

    def _nullify_orphan_references(
        self,
        *,
        batch: Sequence[dict[str, Any]],
        reference_key: str,
        valid_ids: set[str],
        warning_label: str,
    ) -> int:
        """
        Substitui por `NULL` as referências não encontradas.
        """

        orphan_rows = 0
        orphan_counts: dict[str, int] = {}
        for row in batch:
            reference_id = row.get(reference_key)
            if not isinstance(reference_id, str) or not reference_id.strip():
                continue
            if reference_id in valid_ids:
                continue

            row[reference_key] = None
            orphan_rows += 1
            orphan_counts[reference_id] = orphan_counts.get(reference_id, 0) + 1

        for reference_id, count in orphan_counts.items():
            LOGGER.warning(
                "ObservationMicroSusc com %s órfão não encontrado: %s=%s linhas=%s",
                warning_label,
                warning_label,
                reference_id,
                count,
            )
        return orphan_rows
