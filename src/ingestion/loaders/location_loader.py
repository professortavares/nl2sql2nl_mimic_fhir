"""
Persistência das linhas normalizadas de Location no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert

from src.db.schema import LocationTables


@dataclass(slots=True, frozen=True)
class LocationBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de Location."""

    primary_rows: int

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"location": self.primary_rows}


class LocationLoader:
    """
    Persiste batches de Location na tabela simplificada.
    """

    def __init__(self, tables: LocationTables) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables

    @property
    def tables(self) -> LocationTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(self, connection: Connection, batch: Sequence[dict[str, Any]]) -> LocationBatchInsertCounts:
        """
        Persiste um lote de locations transformadas.
        """

        if not batch:
            return LocationBatchInsertCounts(0)

        connection.execute(insert(self._tables.location), list(batch))
        return LocationBatchInsertCounts(primary_rows=len(batch))
