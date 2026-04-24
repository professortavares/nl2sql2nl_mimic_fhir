"""
Persistência das linhas normalizadas de Specimen no PostgreSQL.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Connection, insert, select

from src.db.schema import PatientTables, SpecimenTables

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class SpecimenBatchInsertCounts:
    """Resumo das linhas inseridas em um lote de Specimen."""

    primary_rows: int
    orphan_patient_references: int = 0

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {"specimen": self.primary_rows}


class SpecimenLoader:
    """
    Persiste batches de Specimen na tabela simplificada.
    """

    def __init__(self, tables: SpecimenTables, patient_tables: PatientTables) -> None:
        """
        Inicializa o carregador.
        """

        self._tables = tables
        self._patient_tables = patient_tables

    @property
    def tables(self) -> SpecimenTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[dict[str, Any]],
    ) -> SpecimenBatchInsertCounts:
        """
        Persiste um lote de specimens transformados.
        """

        if not batch:
            return SpecimenBatchInsertCounts(0)

        normalized_batch = [dict(row) for row in batch]
        valid_patient_ids = self._fetch_valid_patient_ids(connection, normalized_batch)
        orphan_patient_references = self._nullify_orphan_patient_references(
            normalized_batch,
            valid_patient_ids,
        )

        connection.execute(insert(self._tables.specimen), normalized_batch)
        return SpecimenBatchInsertCounts(
            primary_rows=len(normalized_batch),
            orphan_patient_references=orphan_patient_references,
        )

    def _fetch_valid_patient_ids(
        self,
        connection: Connection,
        batch: Sequence[dict[str, Any]],
    ) -> set[str]:
        """
        Busca os identificadores de patient existentes para validar FKs.
        """

        requested_patient_ids = {
            patient_id
            for patient_id in (row.get("patient_id") for row in batch)
            if isinstance(patient_id, str) and patient_id.strip()
        }
        if not requested_patient_ids:
            return set()

        statement = select(self._patient_tables.patient.c.id).where(
            self._patient_tables.patient.c.id.in_(requested_patient_ids),
        )
        return set(connection.execute(statement).scalars().all())

    def _nullify_orphan_patient_references(
        self,
        batch: Sequence[dict[str, Any]],
        valid_patient_ids: set[str],
    ) -> int:
        """
        Substitui por `NULL` as referências a patient não encontradas.
        """

        orphan_rows = 0
        orphan_counts: dict[str, int] = {}
        for row in batch:
            patient_id = row.get("patient_id")
            if not isinstance(patient_id, str) or not patient_id.strip():
                continue
            if patient_id in valid_patient_ids:
                continue

            row["patient_id"] = None
            orphan_rows += 1
            orphan_counts[patient_id] = orphan_counts.get(patient_id, 0) + 1

        for patient_id, count in orphan_counts.items():
            LOGGER.warning(
                "Specimen com patient_id órfão não encontrado em patient: patient_id=%s linhas=%s",
                patient_id,
                count,
            )
        return orphan_rows
