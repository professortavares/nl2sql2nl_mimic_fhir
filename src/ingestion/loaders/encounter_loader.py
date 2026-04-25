"""
Persistência das linhas normalizadas de Encounter no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert

from src.db.schema import EncounterTables
from src.ingestion.transformers.encounter_transformer import EncounterTransformationResult


@dataclass(slots=True, frozen=True)
class EncounterBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de Encounter."""

    encounter_rows: int
    encounter_location_rows: int

    @property
    def primary_rows(self) -> int:
        """
        Retorna a quantidade de linhas principais inseridas.
        """

        return self.encounter_rows

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {
            "encounter": self.encounter_rows,
            "encounter_location": self.encounter_location_rows,
        }


class EncounterLoader:
    """
    Persiste batches de Encounter na tabela principal e na tabela auxiliar de localizações.
    """

    def __init__(self, tables: EncounterTables) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables

    @property
    def tables(self) -> EncounterTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[EncounterTransformationResult],
    ) -> EncounterBatchInsertCounts:
        """
        Persiste um lote de encounters transformados.
        """

        if not batch:
            return EncounterBatchInsertCounts(0, 0)

        encounter_rows: list[dict[str, Any]] = []
        encounter_location_rows: list[dict[str, Any]] = []

        for item in batch:
            encounter_rows.append(item.encounter)
            encounter_location_rows.extend(item.encounter_locations)

        connection.execute(insert(self._tables.encounter), encounter_rows)
        if encounter_location_rows:
            connection.execute(insert(self._tables.encounter_location), encounter_location_rows)

        return EncounterBatchInsertCounts(
            encounter_rows=len(encounter_rows),
            encounter_location_rows=len(encounter_location_rows),
        )
