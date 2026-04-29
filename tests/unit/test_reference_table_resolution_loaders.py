"""
Testes de integração leve para a resolução de FKs na ingestão.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import pytest
from sqlalchemy import Column, MetaData, String, Table, create_engine, select

from src.db.schema import (
    ConditionEDTables,
    MedicationAdministrationICUTables,
    MedicationDispenseEDTables,
    MedicationStatementEDTables,
    ObservationEDTables,
    ObservationVitalSignsEDTables,
    PatientTables,
    ProcedureICUTables,
)
from src.ingestion.loaders.condition_ed_loader import ConditionEDLoader
from src.ingestion.loaders.medication_administration_icu_loader import MedicationAdministrationICULoader
from src.ingestion.loaders.medication_dispense_ed_loader import MedicationDispenseEDLoader
from src.ingestion.loaders.medication_statement_ed_loader import MedicationStatementEDLoader
from src.ingestion.loaders.observation_ed_loader import ObservationEDLoader
from src.ingestion.loaders.observation_vital_signs_ed_loader import (
    ObservationVitalSignsEDLoader,
)
from src.ingestion.loaders.procedure_icu_loader import ProcedureICULoader
from src.ingestion.transformers.observation_vital_signs_ed_transformer import (
    ObservationVitalSignsEDTransformationResult,
)


@dataclass(slots=True, frozen=True)
class _LoaderCase:
    name: str
    loader_factory: Callable[[dict[str, Table]], object]
    target_table_name: str
    target_columns: tuple[str, ...]
    batch: list[dict[str, Any]]
    expected_row: dict[str, Any]
    seed_rows: dict[str, list[dict[str, Any]]]
    auxiliary_table_name: str | None = None
    expected_primary_rows: int = 1
    expected_auxiliary_rows: int | None = None


def _build_table(metadata: MetaData, table_name: str, column_names: tuple[str, ...]) -> Table:
    columns = [Column("id", String, primary_key=True)] if "id" in column_names else []
    for column_name in column_names:
        if column_name == "id":
            continue
        columns.append(Column(column_name, String, nullable=True))
    return Table(table_name, metadata, *columns)


def _standard_reference_tables(metadata: MetaData) -> dict[str, Table]:
    table_names = ("patient", "encounter", "encounter_ed", "encounter_icu", "procedure", "procedure_ed")
    return {name: _build_table(metadata, name, ("id",)) for name in table_names}


def _make_loader_cases() -> list[_LoaderCase]:
    return [
        _LoaderCase(
            name="condition_ed",
            loader_factory=lambda tables: ConditionEDLoader(
                tables=ConditionEDTables(condition_ed=tables["condition_ed"]),
                patient_tables=PatientTables(patient=tables["patient"]),
                encounter_table=tables["encounter_ed"],
            ),
            target_table_name="condition_ed",
            target_columns=("id", "patient_id", "encounter_id"),
            batch=[{"id": "cond-ed-1", "patient_id": "pat-1", "encounter_id": "enc-ed-1"}],
            expected_row={"id": "cond-ed-1", "patient_id": "pat-1", "encounter_id": "enc-ed-1"},
            seed_rows={
                "patient": [{"id": "pat-1"}],
                "encounter_ed": [{"id": "enc-ed-1"}],
            },
        ),
        _LoaderCase(
            name="medication_dispense_ed",
            loader_factory=lambda tables: MedicationDispenseEDLoader(
                tables=MedicationDispenseEDTables(medication_dispense_ed=tables["medication_dispense_ed"]),
                patient_tables=PatientTables(patient=tables["patient"]),
                encounter_table=tables["encounter_ed"],
            ),
            target_table_name="medication_dispense_ed",
            target_columns=("id", "patient_id", "encounter_id"),
            batch=[{"id": "md-ed-1", "patient_id": "pat-1", "encounter_id": "enc-ed-1"}],
            expected_row={"id": "md-ed-1", "patient_id": "pat-1", "encounter_id": "enc-ed-1"},
            seed_rows={
                "patient": [{"id": "pat-1"}],
                "encounter_ed": [{"id": "enc-ed-1"}],
            },
        ),
        _LoaderCase(
            name="medication_statement_ed",
            loader_factory=lambda tables: MedicationStatementEDLoader(
                tables=MedicationStatementEDTables(medication_statement_ed=tables["medication_statement_ed"]),
                patient_tables=PatientTables(patient=tables["patient"]),
                encounter_table=tables["encounter_ed"],
            ),
            target_table_name="medication_statement_ed",
            target_columns=("id", "patient_id", "encounter_id"),
            batch=[{"id": "ms-ed-1", "patient_id": "pat-1", "encounter_id": "enc-ed-1"}],
            expected_row={"id": "ms-ed-1", "patient_id": "pat-1", "encounter_id": "enc-ed-1"},
            seed_rows={
                "patient": [{"id": "pat-1"}],
                "encounter_ed": [{"id": "enc-ed-1"}],
            },
        ),
        _LoaderCase(
            name="observation_ed",
            loader_factory=lambda tables: ObservationEDLoader(
                tables=ObservationEDTables(observation_ed=tables["observation_ed"]),
                patient_tables=PatientTables(patient=tables["patient"]),
                encounter_table=tables["encounter_ed"],
                procedure_table=tables["procedure_ed"],
            ),
            target_table_name="observation_ed",
            target_columns=("id", "patient_id", "encounter_id", "procedure_id"),
            batch=[
                {
                    "id": "obs-ed-1",
                    "patient_id": "pat-1",
                    "encounter_id": "enc-ed-1",
                    "procedure_id": "proc-ed-1",
                }
            ],
            expected_row={
                "id": "obs-ed-1",
                "patient_id": "pat-1",
                "encounter_id": "enc-ed-1",
                "procedure_id": "proc-ed-1",
            },
            seed_rows={
                "patient": [{"id": "pat-1"}],
                "encounter_ed": [{"id": "enc-ed-1"}],
                "procedure_ed": [{"id": "proc-ed-1"}],
            },
        ),
        _LoaderCase(
            name="observation_vital_signs_ed",
            loader_factory=lambda tables: ObservationVitalSignsEDLoader(
                tables=ObservationVitalSignsEDTables(
                    observation_vital_signs_ed=tables["observation_vital_signs_ed"],
                    observation_vital_signs_ed_component=tables["observation_vital_signs_ed_component"],
                ),
                patient_tables=PatientTables(patient=tables["patient"]),
                encounter_table=tables["encounter_ed"],
                procedure_table=tables["procedure_ed"],
            ),
            target_table_name="observation_vital_signs_ed",
            target_columns=("id", "patient_id", "encounter_id", "procedure_id"),
            batch=[
                ObservationVitalSignsEDTransformationResult(
                    observation_vital_signs_ed={
                        "id": "ovs-ed-1",
                        "patient_id": "pat-1",
                        "encounter_id": "enc-ed-1",
                        "procedure_id": "proc-ed-1",
                    },
                    observation_vital_signs_ed_components=[],
                )
            ],
            expected_row={
                "id": "ovs-ed-1",
                "patient_id": "pat-1",
                "encounter_id": "enc-ed-1",
                "procedure_id": "proc-ed-1",
            },
            seed_rows={
                "patient": [{"id": "pat-1"}],
                "encounter_ed": [{"id": "enc-ed-1"}],
                "procedure_ed": [{"id": "proc-ed-1"}],
            },
            auxiliary_table_name="observation_vital_signs_ed_component",
            expected_auxiliary_rows=0,
        ),
        _LoaderCase(
            name="procedure_icu",
            loader_factory=lambda tables: ProcedureICULoader(
                tables=ProcedureICUTables(procedure_icu=tables["procedure_icu"]),
                patient_tables=PatientTables(patient=tables["patient"]),
                encounter_table=tables["encounter_icu"],
            ),
            target_table_name="procedure_icu",
            target_columns=("id", "patient_id", "encounter_id"),
            batch=[{"id": "proc-icu-1", "patient_id": "pat-1", "encounter_id": "enc-icu-1"}],
            expected_row={"id": "proc-icu-1", "patient_id": "pat-1", "encounter_id": "enc-icu-1"},
            seed_rows={
                "patient": [{"id": "pat-1"}],
                "encounter_icu": [{"id": "enc-icu-1"}],
            },
        ),
        _LoaderCase(
            name="medication_administration_icu",
            loader_factory=lambda tables: MedicationAdministrationICULoader(
                tables=MedicationAdministrationICUTables(
                    medication_administration_icu=tables["medication_administration_icu"]
                ),
                patient_tables=PatientTables(patient=tables["patient"]),
                encounter_table=tables["encounter_icu"],
            ),
            target_table_name="medication_administration_icu",
            target_columns=("id", "patient_id", "encounter_id"),
            batch=[
                {
                    "id": "ma-icu-1",
                    "patient_id": "pat-1",
                    "encounter_id": "enc-icu-1",
                }
            ],
            expected_row={"id": "ma-icu-1", "patient_id": "pat-1", "encounter_id": "enc-icu-1"},
            seed_rows={
                "patient": [{"id": "pat-1"}],
                "encounter_icu": [{"id": "enc-icu-1"}],
            },
        ),
    ]


@pytest.mark.parametrize("case", _make_loader_cases(), ids=lambda case: case.name)
def test_specific_reference_tables_keep_foreign_keys(case: _LoaderCase) -> None:
    """
    Cada loader listado deve validar FKs contra a tabela específica correta.
    """

    metadata = MetaData()
    tables = _standard_reference_tables(metadata)
    target_table_columns = {
        "condition_ed": ("id", "patient_id", "encounter_id"),
        "medication_dispense_ed": ("id", "patient_id", "encounter_id"),
        "medication_statement_ed": ("id", "patient_id", "encounter_id"),
        "observation_ed": ("id", "patient_id", "encounter_id", "procedure_id"),
        "observation_vital_signs_ed": ("id", "patient_id", "encounter_id", "procedure_id"),
        "procedure_icu": ("id", "patient_id", "encounter_id"),
        "medication_administration_icu": ("id", "patient_id", "encounter_id"),
    }
    for table_name, column_names in target_table_columns.items():
        tables[table_name] = _build_table(metadata, table_name, column_names)
    tables["observation_vital_signs_ed_component"] = _build_table(
        metadata,
        "observation_vital_signs_ed_component",
        ("observation_vital_signs_ed_id", "component_code", "component_code_display", "value", "value_unit", "value_code"),
    )

    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)

    with engine.begin() as connection:
        for table_name, rows in case.seed_rows.items():
            connection.execute(tables[table_name].insert(), rows)

        loader = case.loader_factory(tables)
        result = loader.insert_batch(connection=connection, batch=case.batch)
        inserted_rows = connection.execute(select(tables[case.target_table_name])).mappings().all()

        assert result.primary_rows == case.expected_primary_rows
        if case.expected_auxiliary_rows is not None:
            assert result.auxiliary_rows == case.expected_auxiliary_rows
        assert inserted_rows == [case.expected_row]
