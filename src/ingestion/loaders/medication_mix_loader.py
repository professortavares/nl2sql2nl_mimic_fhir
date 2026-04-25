"""
Persistência das linhas normalizadas de MedicationMix no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert

from src.db.schema import MedicationMixTables
from src.ingestion.transformers.medication_mix_transformer import MedicationMixTransformationResult


@dataclass(slots=True, frozen=True)
class MedicationMixBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de MedicationMix."""

    primary_rows: int
    auxiliary_rows: int

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {
            "medication_mix": self.primary_rows,
            "medication_mix_ingredient": self.auxiliary_rows,
        }


class MedicationMixLoader:
    """
    Persiste batches de MedicationMix na tabela principal e na tabela auxiliar de ingredientes.
    """

    def __init__(self, tables: MedicationMixTables) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables

    @property
    def tables(self) -> MedicationMixTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[MedicationMixTransformationResult],
    ) -> MedicationMixBatchInsertCounts:
        """
        Persiste um lote de medication mix transformados.
        """

        if not batch:
            return MedicationMixBatchInsertCounts(0, 0)

        medication_mix_rows: list[dict[str, Any]] = []
        ingredient_rows: list[dict[str, Any]] = []
        for item in batch:
            medication_mix_rows.append(item.medication_mix)
            ingredient_rows.extend(item.medication_mix_ingredients)

        connection.execute(insert(self._tables.medication_mix), medication_mix_rows)
        if ingredient_rows:
            connection.execute(insert(self._tables.medication_mix_ingredient), ingredient_rows)
        return MedicationMixBatchInsertCounts(
            primary_rows=len(medication_mix_rows),
            auxiliary_rows=len(ingredient_rows),
        )
