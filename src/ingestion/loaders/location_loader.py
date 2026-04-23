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
    meta_profiles: int
    physical_type_codings: int


class LocationLoader:
    """
    Persiste batches de Location em tabelas normalizadas.
    """

    def __init__(self, tables: LocationTables) -> None:
        """
        Inicializa o carregador.

        Parâmetros:
        ----------
        tables : LocationTables
            Referências das tabelas já construídas no schema.
        """

        self._tables = tables

    @property
    def tables(self) -> LocationTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(self, connection: Connection, batch: Sequence[Any]) -> LocationBatchInsertCounts:
        """
        Persiste um lote de locations transformadas.

        Parâmetros:
        ----------
        connection : Connection
            Conexão SQLAlchemy ativa dentro da transação.
        batch : Sequence[Any]
            Conjunto de registros transformados.

        Retorno:
        -------
        LocationBatchInsertCounts
            Quantidade de linhas persistidas.
        """

        if not batch:
            return LocationBatchInsertCounts(0, 0, 0)

        location_rows: list[dict[str, Any]] = []
        meta_profile_rows: list[dict[str, Any]] = []
        physical_type_coding_rows: list[dict[str, Any]] = []

        for item in batch:
            location_rows.append(item.location)
            meta_profile_rows.extend(item.meta_profiles)
            physical_type_coding_rows.extend(item.physical_type_codings)

        connection.execute(insert(self._tables.location), location_rows)
        if meta_profile_rows:
            connection.execute(insert(self._tables.meta_profile), meta_profile_rows)
        if physical_type_coding_rows:
            connection.execute(
                insert(self._tables.physical_type_coding),
                physical_type_coding_rows,
            )

        return LocationBatchInsertCounts(
            primary_rows=len(location_rows),
            meta_profiles=len(meta_profile_rows),
            physical_type_codings=len(physical_type_coding_rows),
        )

