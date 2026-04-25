"""
Persistência das linhas normalizadas de ObservationMicroOrg no PostgreSQL.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, Table, insert, select

from src.db.schema import ObservationMicroOrgTables, ObservationMicroTestTables, PatientTables
from src.ingestion.transformers.observation_micro_org_transformer import (
    ObservationMicroOrgTransformationResult,
)

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class ObservationMicroOrgBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de ObservationMicroOrg."""

    primary_rows: int
    auxiliary_rows: int
    orphan_patient_references: int = 0
    orphan_derived_from_references: int = 0

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {
            "observation_micro_org": self.primary_rows,
            "observation_micro_org_has_member": self.auxiliary_rows,
        }


class ObservationMicroOrgLoader:
    """
    Persiste batches de ObservationMicroOrg nas tabelas principal e auxiliar.
    """

    def __init__(
        self,
        tables: ObservationMicroOrgTables,
        patient_tables: PatientTables,
        observation_micro_test_tables: ObservationMicroTestTables,
    ) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables
        self._patient_tables = patient_tables
        self._observation_micro_test_tables = observation_micro_test_tables

    @property
    def tables(self) -> ObservationMicroOrgTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[ObservationMicroOrgTransformationResult],
    ) -> ObservationMicroOrgBatchInsertCounts:
        """
        Persiste um lote de observações microbiológicas de organismo transformadas.
        """

        if not batch:
            return ObservationMicroOrgBatchInsertCounts(0, 0)

        normalized_micro_org_rows: list[dict[str, Any]] = []
        member_rows: list[dict[str, Any]] = []
        for item in batch:
            normalized_micro_org_rows.append(dict(item.observation_micro_org))
            member_rows.extend(item.observation_micro_org_has_member)

        valid_patient_ids = self._fetch_existing_ids(
            connection=connection,
            table=self._patient_tables.patient,
            column_name="patient_id",
            batch=normalized_micro_org_rows,
        )
        valid_derived_from_ids = self._fetch_existing_ids(
            connection=connection,
            table=self._observation_micro_test_tables.observation_micro_test,
            column_name="derived_from_observation_micro_test_id",
            batch=normalized_micro_org_rows,
        )

        orphan_patient_references = self._nullify_orphan_references(
            batch=normalized_micro_org_rows,
            reference_key="patient_id",
            valid_ids=valid_patient_ids,
            warning_label="patient_id",
        )
        orphan_derived_from_references = self._nullify_orphan_references(
            batch=normalized_micro_org_rows,
            reference_key="derived_from_observation_micro_test_id",
            valid_ids=valid_derived_from_ids,
            warning_label="derived_from_observation_micro_test_id",
        )

        connection.execute(insert(self._tables.observation_micro_org), normalized_micro_org_rows)
        if member_rows:
            connection.execute(insert(self._tables.observation_micro_org_has_member), member_rows)
        return ObservationMicroOrgBatchInsertCounts(
            primary_rows=len(normalized_micro_org_rows),
            auxiliary_rows=len(member_rows),
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
                "ObservationMicroOrg com %s órfão não encontrado: %s=%s linhas=%s",
                warning_label,
                warning_label,
                reference_id,
                count,
            )
        return orphan_rows
