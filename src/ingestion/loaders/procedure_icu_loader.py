"""
Persistência das linhas normalizadas de ProcedureICU no PostgreSQL.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, Table, insert, select

from src.db.schema import EncounterTables, PatientTables, ProcedureICUTables
from src.ingestion.reference_table_resolver import extract_table

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class ProcedureICUBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de ProcedureICU."""

    primary_rows: int
    orphan_patient_references: int = 0
    orphan_encounter_references: int = 0

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"procedure_icu": self.primary_rows}


class ProcedureICULoader:
    """
    Persiste batches de ProcedureICU na tabela simplificada.
    """

    def __init__(
        self,
        tables: ProcedureICUTables,
        patient_tables: PatientTables,
        encounter_tables: EncounterTables | object | None = None,
        encounter_table: Table | object | None = None,
    ) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables
        self._patient_tables = patient_tables
        encounter_source = encounter_table if encounter_table is not None else encounter_tables
        if encounter_source is None:
            raise ValueError("É necessário informar encounter_tables ou encounter_table.")
        self._encounter_table = extract_table(encounter_source, "encounter")

    @property
    def tables(self) -> ProcedureICUTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[dict[str, Any]],
    ) -> ProcedureICUBatchInsertCounts:
        """
        Persiste um lote de procedures ICU transformadas.
        """

        if not batch:
            return ProcedureICUBatchInsertCounts(0)

        normalized_batch = [dict(row) for row in batch]
        valid_patient_ids = self._fetch_existing_ids(
            connection=connection,
            table=self._patient_tables.patient,
            column_name="patient_id",
            batch=normalized_batch,
        )
        valid_encounter_ids = self._fetch_existing_ids(
            connection=connection,
            table=self._encounter_table,
            column_name="encounter_id",
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

        connection.execute(insert(self._tables.procedure_icu), normalized_batch)
        return ProcedureICUBatchInsertCounts(
            primary_rows=len(normalized_batch),
            orphan_patient_references=orphan_patient_references,
            orphan_encounter_references=orphan_encounter_references,
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
                "ProcedureICU com %s órfão não encontrado: %s=%s linhas=%s",
                warning_label,
                warning_label,
                reference_id,
                count,
            )
        return orphan_rows
