"""
Persistência das linhas normalizadas de Organization no PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy import Engine, insert
from sqlalchemy.engine import Connection

from src.config.settings import TableNames
from src.db.schema import OrganizationTables, build_organization_metadata, reset_schema
from src.ingestion.transformers.organization_transformer import OrganizationTransformationResult


@dataclass(slots=True, frozen=True)
class BatchInsertCounts:
    """Resumo das linhas inseridas em um lote."""

    organizations: int
    meta_profiles: int
    identifiers: int
    type_codings: int


class OrganizationLoader:
    """
    Gerencia a recriação do schema e a persistência em lote das tabelas de Organization.
    """

    def __init__(self, engine: Engine, schema_name: str, table_names: TableNames) -> None:
        """
        Inicializa o carregador.

        Parâmetros:
        ----------
        engine : Engine
            Engine SQLAlchemy conectada ao PostgreSQL.
        schema_name : str
            Schema de destino.
        table_names : TableNames
            Nomes físicos configurados.
        """

        self._engine = engine
        self._schema_name = schema_name
        self._metadata, self._tables = build_organization_metadata(schema_name, table_names)

    @property
    def tables(self) -> OrganizationTables:
        """
        Retorna as tabelas gerenciadas pelo carregador.
        """

        return self._tables

    def reset_and_create_schema(self, connection: Connection) -> None:
        """
        Derruba e recria o schema, seguido da criação das tabelas.

        Parâmetros:
        ----------
        connection : Connection
            Conexão SQLAlchemy aberta no contexto transacional.
        """

        reset_schema(connection, self._schema_name)
        self._metadata.create_all(connection)

    def insert_batch(
        self,
        connection: Connection,
        batch: Sequence[OrganizationTransformationResult],
    ) -> BatchInsertCounts:
        """
        Persiste um lote de recursos transformados.

        Parâmetros:
        ----------
        connection : Connection
            Conexão ativa dentro da transação.
        batch : Sequence[OrganizationTransformationResult]
            Conjunto de recursos transformados.

        Retorno:
        -------
        BatchInsertCounts
            Quantidade de linhas inseridas por tabela.
        """

        if not batch:
            return BatchInsertCounts(0, 0, 0, 0)

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
            connection.execute(insert(self._tables.organization_meta_profile), meta_profile_rows)
        if identifier_rows:
            connection.execute(insert(self._tables.organization_identifier), identifier_rows)
        if type_coding_rows:
            connection.execute(insert(self._tables.organization_type_coding), type_coding_rows)

        return BatchInsertCounts(
            organizations=len(organization_rows),
            meta_profiles=len(meta_profile_rows),
            identifiers=len(identifier_rows),
            type_codings=len(type_coding_rows),
        )

