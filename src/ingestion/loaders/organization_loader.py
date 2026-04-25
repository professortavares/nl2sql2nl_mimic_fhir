"""
Persistência das linhas normalizadas de Organization no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert

from src.db.schema import OrganizationTables


@dataclass(slots=True, frozen=True)
class OrganizationBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de Organization."""

    primary_rows: int

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"organization": self.primary_rows}


class OrganizationLoader:
    """
    Persiste batches de Organization na tabela simplificada.
    """

    def __init__(self, tables: OrganizationTables) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables

    @property
    def tables(self) -> OrganizationTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(self, connection: Connection, batch: Sequence[dict[str, Any]]) -> OrganizationBatchInsertCounts:
        """
        Persiste um lote de organizações transformadas.
        """

        if not batch:
            return OrganizationBatchInsertCounts(0)

        connection.execute(insert(self._tables.organization), list(batch))
        return OrganizationBatchInsertCounts(primary_rows=len(batch))
