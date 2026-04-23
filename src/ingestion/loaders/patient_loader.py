"""
Persistência das linhas normalizadas de Patient no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert

from src.db.schema import PatientTables


@dataclass(slots=True, frozen=True)
class PatientBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de Patient."""

    primary_rows: int

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"patient": self.primary_rows}


class PatientLoader:
    """
    Persiste batches de Patient na tabela simplificada.
    """

    def __init__(self, tables: PatientTables) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables

    @property
    def tables(self) -> PatientTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(self, connection: Connection, batch: Sequence[dict[str, Any]]) -> PatientBatchInsertCounts:
        """
        Persiste um lote de patients transformados.
        """

        if not batch:
            return PatientBatchInsertCounts(0)

        connection.execute(insert(self._tables.patient), list(batch))
        return PatientBatchInsertCounts(primary_rows=len(batch))
