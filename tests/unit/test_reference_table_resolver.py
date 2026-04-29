"""
Testes do resolvedor central de tabelas de referência de ingestão.
"""

from __future__ import annotations

import pytest

from src.ingestion.reference_table_resolver import resolve_reference_table_name


@pytest.mark.parametrize(
    ("primary_table_name", "reference_column", "expected"),
    [
        ("condition_ed", "encounter_id", "encounter_ed"),
        ("medication_dispense_ed", "encounter_id", "encounter_ed"),
        ("medication_statement_ed", "encounter_id", "encounter_ed"),
        ("observation_ed", "encounter_id", "encounter_ed"),
        ("observation_ed", "procedure_id", "procedure_ed"),
        ("observation_vital_signs_ed", "encounter_id", "encounter_ed"),
        ("observation_vital_signs_ed", "procedure_id", "procedure_ed"),
        ("procedure_ed", "encounter_id", "encounter_ed"),
        ("procedure_icu", "encounter_id", "encounter_icu"),
        ("medication_administration_icu", "encounter_id", "encounter_icu"),
    ],
)
def test_resolve_reference_table_name_uses_explicit_overrides(
    primary_table_name: str,
    reference_column: str,
    expected: str,
) -> None:
    """
    As exceções do domínio devem apontar para as tabelas específicas.
    """

    assert resolve_reference_table_name(primary_table_name, reference_column) == expected


@pytest.mark.parametrize(
    ("primary_table_name", "reference_column", "expected"),
    [
        ("condition", "encounter_id", "encounter"),
        ("procedure", "encounter_id", "encounter"),
        ("medication_request", "encounter_id", "encounter"),
        ("observation_chartevents", "encounter_id", "encounter"),
        ("medication_dispense", "encounter_id", "encounter"),
        ("medication_administration", "encounter_id", "encounter"),
    ],
)
def test_resolve_reference_table_name_keeps_generic_defaults(
    primary_table_name: str,
    reference_column: str,
    expected: str,
) -> None:
    """
    As tabelas genéricas continuam usando as referências genéricas.
    """

    assert resolve_reference_table_name(primary_table_name, reference_column) == expected
