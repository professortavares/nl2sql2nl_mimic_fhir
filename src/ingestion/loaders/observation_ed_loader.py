"""
Persistência das linhas normalizadas de ObservationED no PostgreSQL.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, Table, insert, select

from src.db.schema import EncounterTables, ObservationEDTables, PatientTables, ProcedureTables

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class ObservationEDBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de ObservationED."""

    primary_rows: int
    orphan_patient_references: int = 0
    orphan_encounter_references: int = 0
    orphan_procedure_references: int = 0

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"observation_ed": self.primary_rows}


class ObservationEDLoader:
    """
    Persiste batches de ObservationED na tabela simplificada.
    """

    def __init__(
        self,
        tables: ObservationEDTables,
        patient_tables: PatientTables,
        encounter_tables: EncounterTables,
        procedure_tables: ProcedureTables,
    ) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables
        self._patient_tables = patient_tables
        self._encounter_tables = encounter_tables
        self._procedure_tables = procedure_tables

    @property
    def tables(self) -> ObservationEDTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[dict[str, Any]],
    ) -> ObservationEDBatchInsertCounts:
        """
        Persiste um lote de observações ED transformadas.
        """

        if not batch:
            return ObservationEDBatchInsertCounts(0)

        normalized_batch = [dict(row) for row in batch]
        valid_patient_ids = self._fetch_existing_ids(
            connection=connection,
            table=self._patient_tables.patient,
            column_name="patient_id",
            batch=normalized_batch,
        )
        valid_encounter_ids = self._fetch_existing_ids(
            connection=connection,
            table=self._encounter_tables.encounter,
            column_name="encounter_id",
            batch=normalized_batch,
        )
        valid_procedure_ids = self._fetch_existing_ids(
            connection=connection,
            table=self._procedure_tables.procedure,
            column_name="procedure_id",
            batch=normalized_batch,
        )

        orphan_patient_references = self._nullify_orphan_references(
            batch=normalized_batch,
            reference_key="patient_id",
            valid_ids=valid_patient_ids,
            warning_label="patient_id",
        )
        orphan_encounter_references = self._nullify_orphan_references(
            batch=normalized_batch,
            reference_key="encounter_id",
            valid_ids=valid_encounter_ids,
            warning_label="encounter_id",
        )
        orphan_procedure_references = self._nullify_orphan_references(
            batch=normalized_batch,
            reference_key="procedure_id",
            valid_ids=valid_procedure_ids,
            warning_label="procedure_id",
        )

        connection.execute(insert(self._tables.observation_ed), normalized_batch)
        return ObservationEDBatchInsertCounts(
            primary_rows=len(normalized_batch),
            orphan_patient_references=orphan_patient_references,
            orphan_encounter_references=orphan_encounter_references,
            orphan_procedure_references=orphan_procedure_references,
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
                "ObservationED com %s órfão não encontrado: %s=%s linhas=%s",
                warning_label,
                warning_label,
                reference_id,
                count,
            )
        return orphan_rows
