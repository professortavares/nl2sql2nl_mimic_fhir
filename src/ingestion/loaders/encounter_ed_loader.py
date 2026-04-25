"""
Persistência das linhas normalizadas de EncounterED no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert

from src.db.schema import EncounterEDTables
from src.ingestion.transformers.encounter_ed_transformer import EncounterEDTransformationResult


@dataclass(slots=True, frozen=True)
class EncounterEDBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de EncounterED."""

    primary_rows: int

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"encounter_ed": self.primary_rows}


class EncounterEDLoader:
    """
    Persiste batches de EncounterED na tabela especializada.
    """

    def __init__(self, tables: EncounterEDTables) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables

    @property
    def tables(self) -> EncounterEDTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[EncounterEDTransformationResult],
    ) -> EncounterEDBatchInsertCounts:
        """
        Persiste um lote de encounters de emergência transformados.
        """

        if not batch:
            return EncounterEDBatchInsertCounts(0)

        encounter_ed_rows: list[dict[str, Any]] = []
        for item in batch:
            encounter_ed_rows.append(item.encounter_ed)

        connection.execute(insert(self._tables.encounter_ed), encounter_ed_rows)
        return EncounterEDBatchInsertCounts(primary_rows=len(encounter_ed_rows))
