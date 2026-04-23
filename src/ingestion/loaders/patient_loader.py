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
    meta_profiles: int
    names: int
    identifiers: int
    communication_language_codings: int
    marital_status_codings: int
    race: int
    ethnicity: int
    birthsex: int

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {
            "patient": self.primary_rows,
            "patient_meta_profile": self.meta_profiles,
            "patient_name": self.names,
            "patient_identifier": self.identifiers,
            "patient_communication_language_coding": self.communication_language_codings,
            "patient_marital_status_coding": self.marital_status_codings,
            "patient_race": self.race,
            "patient_ethnicity": self.ethnicity,
            "patient_birthsex": self.birthsex,
        }


class PatientLoader:
    """
    Persiste batches de Patient em tabelas normalizadas.
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

    def insert_batch(self, connection: Connection, batch: Sequence[Any]) -> PatientBatchInsertCounts:
        """
        Persiste um lote de patients transformados.
        """

        if not batch:
            return PatientBatchInsertCounts(0, 0, 0, 0, 0, 0, 0, 0, 0)

        patient_rows: list[dict[str, Any]] = []
        meta_profile_rows: list[dict[str, Any]] = []
        name_rows: list[dict[str, Any]] = []
        identifier_rows: list[dict[str, Any]] = []
        communication_language_coding_rows: list[dict[str, Any]] = []
        marital_status_coding_rows: list[dict[str, Any]] = []
        race_rows: list[dict[str, Any]] = []
        ethnicity_rows: list[dict[str, Any]] = []
        birthsex_rows: list[dict[str, Any]] = []

        for item in batch:
            patient_rows.append(item.patient)
            meta_profile_rows.extend(item.meta_profiles)
            name_rows.extend(item.names)
            identifier_rows.extend(item.identifiers)
            communication_language_coding_rows.extend(item.communication_language_codings)
            marital_status_coding_rows.extend(item.marital_status_codings)
            race_rows.extend(item.race)
            ethnicity_rows.extend(item.ethnicity)
            birthsex_rows.extend(item.birthsex)

        connection.execute(insert(self._tables.patient), patient_rows)
        if meta_profile_rows:
            connection.execute(insert(self._tables.meta_profile), meta_profile_rows)
        if name_rows:
            connection.execute(insert(self._tables.name), name_rows)
        if identifier_rows:
            connection.execute(insert(self._tables.identifier), identifier_rows)
        if communication_language_coding_rows:
            connection.execute(
                insert(self._tables.communication_language_coding),
                communication_language_coding_rows,
            )
        if marital_status_coding_rows:
            connection.execute(
                insert(self._tables.marital_status_coding),
                marital_status_coding_rows,
            )
        if race_rows:
            connection.execute(insert(self._tables.race), race_rows)
        if ethnicity_rows:
            connection.execute(insert(self._tables.ethnicity), ethnicity_rows)
        if birthsex_rows:
            connection.execute(insert(self._tables.birthsex), birthsex_rows)

        return PatientBatchInsertCounts(
            primary_rows=len(patient_rows),
            meta_profiles=len(meta_profile_rows),
            names=len(name_rows),
            identifiers=len(identifier_rows),
            communication_language_codings=len(communication_language_coding_rows),
            marital_status_codings=len(marital_status_coding_rows),
            race=len(race_rows),
            ethnicity=len(ethnicity_rows),
            birthsex=len(birthsex_rows),
        )

