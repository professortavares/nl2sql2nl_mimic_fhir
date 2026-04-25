"""
Testes do carregador de Procedure.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import Mock

from sqlalchemy import Column, MetaData, String, Table

from src.db.schema import EncounterTables, PatientTables, ProcedureTables
from src.ingestion.loaders.procedure_loader import ProcedureLoader


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


def test_insert_batch_nullifies_orphan_patient_and_encounter_references(caplog) -> None:
    """
    Deve transformar referências órfãs de patient e encounter em `NULL`.
    """

    metadata = MetaData()
    patient_table = Table("patient", metadata, Column("id", String, primary_key=True))
    encounter_table = Table("encounter", metadata, Column("id", String, primary_key=True))
    procedure_table = Table(
        "procedure",
        metadata,
        Column("id", String, primary_key=True),
        Column("patient_id", String, nullable=True),
        Column("encounter_id", String, nullable=True),
    )
    loader = ProcedureLoader(
        tables=ProcedureTables(procedure=procedure_table),
        patient_tables=PatientTables(patient=patient_table),
        encounter_tables=EncounterTables(encounter=encounter_table, encounter_location=Mock()),
    )

    connection = Mock()
    connection.execute.side_effect = [
        _FakeResult(["pat-ok"]),
        _FakeResult(["enc-ok"]),
        Mock(),
    ]

    batch = [
        {"id": "proc-1", "patient_id": "pat-ok", "encounter_id": "enc-ok"},
        {"id": "proc-2", "patient_id": "pat-missing", "encounter_id": "enc-ok"},
        {"id": "proc-3", "patient_id": "pat-ok", "encounter_id": "enc-missing"},
        {"id": "proc-4", "patient_id": "pat-missing", "encounter_id": "enc-missing"},
    ]

    with caplog.at_level("WARNING"):
        result = loader.insert_batch(connection=connection, batch=batch)

    assert result.primary_rows == 4
    assert result.orphan_patient_references == 2
    assert result.orphan_encounter_references == 2
    assert connection.execute.call_count == 3

    inserted_rows = connection.execute.call_args_list[2].args[1]
    assert inserted_rows == [
        {"id": "proc-1", "patient_id": "pat-ok", "encounter_id": "enc-ok"},
        {"id": "proc-2", "patient_id": None, "encounter_id": "enc-ok"},
        {"id": "proc-3", "patient_id": "pat-ok", "encounter_id": None},
        {"id": "proc-4", "patient_id": None, "encounter_id": None},
    ]
    assert "patient_id órfão" in caplog.text
    assert "encounter_id órfão" in caplog.text
