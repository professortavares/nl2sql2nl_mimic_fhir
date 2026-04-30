"""
Testes do repositório de contexto General Hospital.
"""

from __future__ import annotations

from sqlalchemy import Column, MetaData, String, Table, create_engine

from src.app.repositories.general_hospital_repository import GeneralHospitalRepository


def test_general_hospital_repository_lists_transfers_and_medication_events() -> None:
    """Deve consultar transferências e medicações do encounter atual."""

    metadata = MetaData()
    location = Table(
        "location",
        metadata,
        Column("id", String, primary_key=True),
        Column("name", String),
    )
    encounter_location = Table(
        "encounter_location",
        metadata,
        Column("encounter_id", String),
        Column("location_id", String),
        Column("start_date", String),
        Column("end_date", String),
    )
    medication = Table(
        "medication",
        metadata,
        Column("id", String, primary_key=True),
        Column("name", String),
    )
    medication_request = Table(
        "medication_request",
        metadata,
        Column("id", String, primary_key=True),
        Column("encounter_id", String),
        Column("medication_id", String),
        Column("validity_start", String),
        Column("validity_end", String),
        Column("frequency_code", String),
        Column("status", String),
        Column("intent", String),
        Column("identifier", String),
        Column("medication_code", String),
    )
    medication_administration = Table(
        "medication_administration",
        metadata,
        Column("id", String, primary_key=True),
        Column("medication_request_id", String),
        Column("effective_at", String),
        Column("dose_value", String),
        Column("dose_unit", String),
        Column("status", String),
        Column("medication_code", String),
    )

    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)

    with engine.begin() as connection:
        connection.execute(
            location.insert(),
            [
                {"id": "loc-1", "name": "ED"},
                {"id": "loc-2", "name": "Ward A"},
            ],
        )
        connection.execute(
            encounter_location.insert(),
            [
                {
                    "encounter_id": "enc-1",
                    "location_id": "loc-1",
                    "start_date": "2024-01-01T00:00:00",
                    "end_date": "2024-01-01T12:00:00",
                },
                {
                    "encounter_id": "enc-1",
                    "location_id": "loc-2",
                    "start_date": "2024-01-01T12:00:00",
                    "end_date": None,
                },
            ],
        )
        connection.execute(medication.insert(), [{"id": "med-1", "name": "Morphine"}])
        connection.execute(
            medication_request.insert(),
            [
                {
                    "id": "mr-1",
                    "encounter_id": "enc-1",
                    "medication_id": "med-1",
                    "validity_start": "2024-01-01T08:00:00",
                    "validity_end": "2024-01-01T20:00:00",
                    "frequency_code": "ONCE",
                    "status": "completed",
                    "intent": "order",
                    "identifier": "req-1",
                    "medication_code": None,
                },
                {
                    "id": "mr-2",
                    "encounter_id": "enc-1",
                    "medication_id": None,
                    "validity_start": "2024-01-01T09:00:00",
                    "validity_end": None,
                    "frequency_code": "BID",
                    "status": "active",
                    "intent": "order",
                    "identifier": "req-2",
                    "medication_code": "Acetaminophen",
                },
            ],
        )
        connection.execute(
            medication_administration.insert(),
            [
                {
                    "id": "ma-1",
                    "medication_request_id": "mr-1",
                    "effective_at": "2024-01-01T10:00:00",
                    "dose_value": "2",
                    "dose_unit": "mg",
                    "status": "completed",
                    "medication_code": "Morphine",
                }
            ],
        )

        repository = GeneralHospitalRepository(
            schema_name="",
            encounter_location_table_name="encounter_location",
            location_table_name="location",
            condition_table_name="condition",
            procedure_table_name="procedure",
            medication_table_name="medication",
            medication_request_table_name="medication_request",
            medication_dispense_table_name="medication_dispense",
            medication_administration_table_name="medication_administration",
            observation_labevents_table_name="observation_labevents",
            observation_micro_test_table_name="observation_micro_test",
            observation_micro_org_table_name="observation_micro_org",
            observation_micro_susc_table_name="observation_micro_susc",
            specimen_table_name="specimen",
        )

        transfers = repository.list_encounter_locations(connection, "enc-1")
        medication_events = repository.list_medication_events(connection, "enc-1")

    assert transfers == [
        {"start_date": "2024-01-01T00:00:00", "end_date": "2024-01-01T12:00:00", "location_name": "ED"},
        {"start_date": "2024-01-01T12:00:00", "end_date": None, "location_name": "Ward A"},
    ]
    assert medication_events == [
        {
            "medication_request_id": "mr-1",
            "validity_start": "2024-01-01T08:00:00",
            "validity_end": "2024-01-01T20:00:00",
            "medication_name": "Morphine",
            "frequency_code": "ONCE",
            "request_status": "completed",
            "request_intent": "order",
            "request_identifier": "req-1",
            "medication_administration_id": "ma-1",
            "effective_at": "2024-01-01T10:00:00",
            "dose_value": "2",
            "dose_unit": "mg",
            "status": "completed",
        },
        {
            "medication_request_id": "mr-2",
            "validity_start": "2024-01-01T09:00:00",
            "validity_end": None,
            "medication_name": None,
            "frequency_code": "BID",
            "request_status": "active",
            "request_intent": "order",
            "request_identifier": "req-2",
            "medication_administration_id": None,
            "effective_at": None,
            "dose_value": None,
            "dose_unit": None,
            "status": None,
        },
    ]
