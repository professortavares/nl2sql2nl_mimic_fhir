"""
Persistência das linhas normalizadas de MedicationRequest no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert

from src.db.schema import MedicationRequestTables


@dataclass(slots=True, frozen=True)
class MedicationRequestBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de MedicationRequest."""

    primary_rows: int

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"medication_request": self.primary_rows}


class MedicationRequestLoader:
    """
    Persiste batches de MedicationRequest na tabela simplificada.
    """

    def __init__(self, tables: MedicationRequestTables) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables

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

        connection.execute(insert(self._tables.medication_request), list(batch))
        return MedicationRequestBatchInsertCounts(primary_rows=len(batch))
