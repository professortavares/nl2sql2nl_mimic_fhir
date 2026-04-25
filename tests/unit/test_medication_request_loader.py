"""
Testes do carregador de MedicationRequest.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import Mock

from sqlalchemy import Column, MetaData, String, Table

from src.db.schema import MedicationRequestTables, MedicationTables
from src.ingestion.loaders.medication_request_loader import MedicationRequestLoader


@dataclass(slots=True)
class _FakeScalars:
    values: list[str]

    def all(self) -> list[str]:
        return list(self.values)


@dataclass(slots=True)
class _FakeResult:
    values: list[str]

    def scalars(self) -> _FakeScalars:
        return _FakeScalars(self.values)


def test_insert_batch_nullifies_orphan_medication_references(caplog) -> None:
    """
    Deve transformar referências órfãs de medication em `NULL` antes do insert.
    """

    metadata = MetaData()
    medication_table = Table(
        "medication",
        metadata,
        Column("id", String, primary_key=True),
    )
    medication_request_table = Table(
        "medication_request",
        metadata,
        Column("id", String, primary_key=True),
        Column("medication_id", String, nullable=True),
    )
    loader = MedicationRequestLoader(
        tables=MedicationRequestTables(medication_request=medication_request_table),
        medication_tables=MedicationTables(medication=medication_table),
    )

    connection = Mock()
    connection.execute.side_effect = [
        _FakeResult(["med-ok"]),
        Mock(),
    ]

    batch = [
        {"id": "mr-1", "medication_id": "med-ok"},
        {"id": "mr-2", "medication_id": "med-missing"},
        {"id": "mr-3", "medication_id": None},
    ]

    with caplog.at_level("WARNING"):
        result = loader.insert_batch(connection=connection, batch=batch)

    assert result.primary_rows == 3
    assert result.orphan_medication_references == 1

    assert connection.execute.call_count == 2
    inserted_rows = connection.execute.call_args_list[1].args[1]
    assert inserted_rows == [
        {"id": "mr-1", "medication_id": "med-ok"},
        {"id": "mr-2", "medication_id": None},
        {"id": "mr-3", "medication_id": None},
    ]
    assert "medication_id órfão" in caplog.text
