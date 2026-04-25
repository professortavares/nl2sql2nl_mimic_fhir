"""
Persistência das linhas normalizadas de Medication no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert

from src.db.schema import MedicationTables


@dataclass(slots=True, frozen=True)
class MedicationBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de Medication."""

    primary_rows: int

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"medication": self.primary_rows}


class MedicationLoader:
    """
    Persiste batches de Medication na tabela simplificada.
    """

    def __init__(self, tables: MedicationTables) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables

    @property
    def tables(self) -> MedicationTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(self, connection: Connection, batch: Sequence[dict[str, Any]]) -> MedicationBatchInsertCounts:
        """
        Persiste um lote de medications transformadas.
        """

        if not batch:
            return MedicationBatchInsertCounts(0)

        connection.execute(insert(self._tables.medication), list(batch))
        return MedicationBatchInsertCounts(primary_rows=len(batch))
