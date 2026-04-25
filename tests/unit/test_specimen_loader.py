"""
Testes do carregador de Specimen.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import Mock

from sqlalchemy import Column, MetaData, String, Table

from src.db.schema import PatientTables, SpecimenTables
from src.ingestion.loaders.specimen_loader import SpecimenLoader


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


def test_insert_batch_nullifies_orphan_patient_references(caplog) -> None:
    """
    Deve transformar referências órfãs de patient em `NULL` antes do insert.
    """

    metadata = MetaData()
    patient_table = Table(
        "patient",
        metadata,
        Column("id", String, primary_key=True),
    )
    specimen_table = Table(
        "specimen",
        metadata,
        Column("id", String, primary_key=True),
        Column("patient_id", String, nullable=True),
    )
    loader = SpecimenLoader(
        tables=SpecimenTables(specimen=specimen_table),
        patient_tables=PatientTables(patient=patient_table),
    )

    connection = Mock()
    connection.execute.side_effect = [
        _FakeResult(["pat-ok"]),
        Mock(),
    ]

    batch = [
        {"id": "spec-1", "patient_id": "pat-ok"},
        {"id": "spec-2", "patient_id": "pat-missing"},
        {"id": "spec-3", "patient_id": None},
    ]

    with caplog.at_level("WARNING"):
        result = loader.insert_batch(connection=connection, batch=batch)

    assert result.primary_rows == 3
    assert result.orphan_patient_references == 1
    assert connection.execute.call_count == 2

    inserted_rows = connection.execute.call_args_list[1].args[1]
    assert inserted_rows == [
        {"id": "spec-1", "patient_id": "pat-ok"},
        {"id": "spec-2", "patient_id": None},
        {"id": "spec-3", "patient_id": None},
    ]
    assert "patient_id órfão" in caplog.text
