"""
Persistência das linhas normalizadas de EncounterICU no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert

from src.db.schema import EncounterICUTables
from src.ingestion.transformers.encounter_icu_transformer import EncounterICUTransformationResult


@dataclass(slots=True, frozen=True)
class EncounterICUBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de EncounterICU."""

    primary_rows: int
    auxiliary_rows: int

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {
            "encounter_icu": self.primary_rows,
            "encounter_icu_location": self.auxiliary_rows,
        }


class EncounterICULoader:
    """
    Persiste batches de EncounterICU nas tabelas especializadas.
    """

    def __init__(self, tables: EncounterICUTables) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables

    @property
    def tables(self) -> EncounterICUTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[EncounterICUTransformationResult],
    ) -> EncounterICUBatchInsertCounts:
        """
        Persiste um lote de encounters de UTI transformados.
        """

        if not batch:
            return EncounterICUBatchInsertCounts(0, 0)

        encounter_icu_rows: list[dict[str, Any]] = []
        encounter_icu_location_rows: list[dict[str, Any]] = []

        for item in batch:
            encounter_icu_rows.append(item.encounter_icu)
            encounter_icu_location_rows.extend(item.encounter_icu_locations)

        connection.execute(insert(self._tables.encounter_icu), encounter_icu_rows)
        if encounter_icu_location_rows:
            connection.execute(insert(self._tables.encounter_icu_location), encounter_icu_location_rows)
        return EncounterICUBatchInsertCounts(
            primary_rows=len(encounter_icu_rows),
            auxiliary_rows=len(encounter_icu_location_rows),
        )
