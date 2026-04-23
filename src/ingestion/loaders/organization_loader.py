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
    meta_profiles: int
    identifiers: int
    type_codings: int

    def table_counts(self) -> dict[str, int]:
        """
        Retorna a contagem de linhas por tabela.
        """

        return {
            "organization": self.primary_rows,
            "organization_meta_profile": self.meta_profiles,
            "organization_identifier": self.identifiers,
            "organization_type_coding": self.type_codings,
        }


class OrganizationLoader:
    """
    Persiste batches de Organization em tabelas normalizadas.
    """

    def __init__(self, tables: OrganizationTables) -> None:
        """
        Inicializa o carregador.

        Parâmetros:
        ----------
        tables : OrganizationTables
            Referências das tabelas já construídas no schema.
        """

        self._tables = tables

    @property
    def tables(self) -> OrganizationTables:
        """
        Retorna as tabelas associadas ao carregador.
        """

        return self._tables

    def insert_batch(self, connection: Connection, batch: Sequence[Any]) -> OrganizationBatchInsertCounts:
        """
        Persiste um lote de organizações transformadas.

        Parâmetros:
        ----------
        connection : Connection
            Conexão SQLAlchemy ativa dentro da transação.
        batch : Sequence[Any]
            Conjunto de registros transformados.

        Retorno:
        -------
        OrganizationBatchInsertCounts
            Quantidade de linhas persistidas.
        """

        if not batch:
            return OrganizationBatchInsertCounts(0, 0, 0, 0)

        organization_rows: list[dict[str, Any]] = []
        meta_profile_rows: list[dict[str, Any]] = []
        identifier_rows: list[dict[str, Any]] = []
        type_coding_rows: list[dict[str, Any]] = []

        for item in batch:
            organization_rows.append(item.organization)
            meta_profile_rows.extend(item.meta_profiles)
            identifier_rows.extend(item.identifiers)
            type_coding_rows.extend(item.type_codings)

        connection.execute(insert(self._tables.organization), organization_rows)
        if meta_profile_rows:
            connection.execute(insert(self._tables.meta_profile), meta_profile_rows)
        if identifier_rows:
            connection.execute(insert(self._tables.identifier), identifier_rows)
        if type_coding_rows:
            connection.execute(insert(self._tables.type_coding), type_coding_rows)

        return OrganizationBatchInsertCounts(
            primary_rows=len(organization_rows),
            meta_profiles=len(meta_profile_rows),
            identifiers=len(identifier_rows),
            type_codings=len(type_coding_rows),
        )
