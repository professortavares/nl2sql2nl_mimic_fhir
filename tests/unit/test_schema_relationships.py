"""
Testes dos relacionamentos específicos do schema de ingestão.
"""

from __future__ import annotations

from src.db.schema import build_project_metadata


def test_specific_ed_and_icu_foreign_keys_point_to_the_expected_tables() -> None:
    """
    As tabelas específicas ED/ICU devem ter FKs explícitas para suas equivalentes.
    """

    _, tables = build_project_metadata(
        schema_name="demo_schema",
        organization_table_name="organization",
        location_table_name="location",
        patient_table_name="patient",
        encounter_table_name="encounter",
        encounter_location_table_name="encounter_location",
        encounter_ed_table_name="encounter_ed",
        encounter_icu_table_name="encounter_icu",
        encounter_icu_location_table_name="encounter_icu_location",
        medication_table_name="medication",
        medication_mix_table_name="medication_mix",
        medication_mix_ingredient_table_name="medication_mix_ingredient",
        medication_request_table_name="medication_request",
        specimen_table_name="specimen",
        condition_table_name="condition",
        condition_ed_table_name="condition_ed",
        procedure_table_name="procedure",
        procedure_ed_table_name="procedure_ed",
        procedure_icu_table_name="procedure_icu",
        observation_labevents_table_name="observation_labevents",
        observation_micro_test_table_name="observation_micro_test",
        observation_micro_org_table_name="observation_micro_org",
        observation_micro_org_has_member_table_name="observation_micro_org_has_member",
        observation_micro_susc_table_name="observation_micro_susc",
        observation_chartevents_table_name="observation_chartevents",
        observation_datetimeevents_table_name="observation_datetimeevents",
        observation_outputevents_table_name="observation_outputevents",
        observation_ed_table_name="observation_ed",
        observation_vital_signs_ed_table_name="observation_vital_signs_ed",
        observation_vital_signs_ed_component_table_name="observation_vital_signs_ed_component",
        medication_dispense_table_name="medication_dispense",
        medication_dispense_ed_table_name="medication_dispense_ed",
        medication_administration_table_name="medication_administration",
        medication_administration_icu_table_name="medication_administration_icu",
        medication_statement_ed_table_name="medication_statement_ed",
    )

    assert next(iter(tables.condition_ed.condition_ed.c.encounter_id.foreign_keys)).column.table.name == "encounter_ed"
    assert next(iter(tables.condition.condition.c.encounter_id.foreign_keys)).column.table.name == "encounter"
    assert next(iter(tables.encounter_ed.encounter_ed.c.encounter_id.foreign_keys)).column.table.name == "encounter"
    assert next(iter(tables.encounter_icu.encounter_icu.c.encounter_id.foreign_keys)).column.table.name == "encounter"
    assert next(iter(tables.medication_request.medication_request.c.encounter_id.foreign_keys)).column.table.name == "encounter"
    assert next(iter(tables.medication_dispense.medication_dispense.c.encounter_id.foreign_keys)).column.table.name == "encounter"
    assert next(iter(tables.medication_dispense_ed.medication_dispense_ed.c.encounter_id.foreign_keys)).column.table.name == "encounter_ed"
    assert next(iter(tables.medication_statement_ed.medication_statement_ed.c.encounter_id.foreign_keys)).column.table.name == "encounter_ed"
    assert next(iter(tables.procedure.procedure.c.encounter_id.foreign_keys)).column.table.name == "encounter"
    assert next(iter(tables.observation_micro_test.observation_micro_test.c.encounter_id.foreign_keys)).column.table.name == "encounter"
    assert next(iter(tables.observation_ed.observation_ed.c.encounter_id.foreign_keys)).column.table.name == "encounter_ed"
    assert next(iter(tables.observation_ed.observation_ed.c.procedure_id.foreign_keys)).column.table.name == "procedure_ed"
    assert next(iter(tables.observation_vital_signs_ed.observation_vital_signs_ed.c.encounter_id.foreign_keys)).column.table.name == "encounter_ed"
    assert next(iter(tables.observation_vital_signs_ed.observation_vital_signs_ed.c.procedure_id.foreign_keys)).column.table.name == "procedure_ed"
    assert next(iter(tables.procedure_icu.procedure_icu.c.encounter_id.foreign_keys)).column.table.name == "encounter_icu"
    assert next(iter(tables.medication_administration_icu.medication_administration_icu.c.encounter_id.foreign_keys)).column.table.name == "encounter_icu"
