"""
Persistência das linhas normalizadas de MedicationRequest no PostgreSQL.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert, select

from src.db.schema import MedicationRequestTables, MedicationTables

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class MedicationRequestBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de MedicationRequest."""

    primary_rows: int
    orphan_medication_references: int = 0

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"medication_request": self.primary_rows}


class MedicationRequestLoader:
    """
    Persiste batches de MedicationRequest na tabela simplificada.
    """

    def __init__(
        self,
        tables: MedicationRequestTables,
        medication_tables: MedicationTables,
    ) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables
        self._medication_tables = medication_tables

    @property
    def tables(self) -> MedicationRequestTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[dict[str, Any]],
    ) -> MedicationRequestBatchInsertCounts:
        """
        Persiste um lote de medication requests transformadas.
        """

        if not batch:
            return MedicationRequestBatchInsertCounts(0)

        normalized_batch = [dict(row) for row in batch]
        valid_medication_ids = self._fetch_valid_medication_ids(connection, normalized_batch)
        orphan_medication_references = self._nullify_orphan_medication_references(
            normalized_batch,
            valid_medication_ids,
        )

        connection.execute(insert(self._tables.medication_request), normalized_batch)
        return MedicationRequestBatchInsertCounts(
            primary_rows=len(normalized_batch),
            orphan_medication_references=orphan_medication_references,
        )

    def _fetch_valid_medication_ids(
        self,
        connection: Connection,
        batch: Sequence[dict[str, Any]],
    ) -> set[str]:
        """
        Busca os identificadores de medication existentes para validar FKs.
        """

        requested_medication_ids = {
            medication_id
            for medication_id in (row.get("medication_id") for row in batch)
            if isinstance(medication_id, str) and medication_id.strip()
        }
        if not requested_medication_ids:
            return set()

        statement = select(self._medication_tables.medication.c.id).where(
            self._medication_tables.medication.c.id.in_(requested_medication_ids),
        )
        return set(connection.execute(statement).scalars().all())

    def _nullify_orphan_medication_references(
        self,
        batch: Sequence[dict[str, Any]],
        valid_medication_ids: set[str],
    ) -> int:
        """
        Substitui por `NULL` as referências a medication não encontradas.

        Retorna a quantidade de linhas ajustadas.
        """

        orphan_rows = 0
        orphan_counts: dict[str, int] = {}
        for row in batch:
            medication_id = row.get("medication_id")
            if not isinstance(medication_id, str) or not medication_id.strip():
                continue
            if medication_id in valid_medication_ids:
                continue

            row["medication_id"] = None
            orphan_rows += 1
            orphan_counts[medication_id] = orphan_counts.get(medication_id, 0) + 1

        for medication_id, count in orphan_counts.items():
            LOGGER.warning(
                "MedicationRequest com medication_id órfão não encontrado em medication: medication_id=%s linhas=%s",
                medication_id,
                count,
            )
        return orphan_rows
