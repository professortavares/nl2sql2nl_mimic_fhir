"""
Repositório de eventos clínicos usados na timeline do paciente.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy.engine import Connection

from src.app.repositories.base import fetch_mappings, fetch_mappings_expanding, qualified_table_name


class ClinicalEventsRepository:
    """Reúne consultas para diagnósticos, procedimentos, medicações e observações."""

    def __init__(
        self,
        *,
        schema_name: str,
        condition_table_name: str,
        condition_ed_table_name: str,
        procedure_table_name: str,
        procedure_ed_table_name: str,
        procedure_icu_table_name: str,
        medication_request_table_name: str,
        medication_dispense_table_name: str,
        medication_dispense_ed_table_name: str,
        medication_administration_table_name: str,
        medication_administration_icu_table_name: str,
        medication_statement_ed_table_name: str,
        observation_labevents_table_name: str,
        observation_micro_test_table_name: str,
        observation_micro_org_table_name: str,
        observation_micro_susc_table_name: str,
        observation_chartevents_table_name: str,
        observation_datetimeevents_table_name: str,
        observation_outputevents_table_name: str,
        observation_ed_table_name: str,
        observation_vital_signs_ed_table_name: str,
        observation_vital_signs_ed_component_table_name: str,
        specimen_table_name: str,
    ) -> None:
        self._schema_name = schema_name
        self._condition_table_name = condition_table_name
        self._condition_ed_table_name = condition_ed_table_name
        self._procedure_table_name = procedure_table_name
        self._procedure_ed_table_name = procedure_ed_table_name
        self._procedure_icu_table_name = procedure_icu_table_name
        self._medication_request_table_name = medication_request_table_name
        self._medication_dispense_table_name = medication_dispense_table_name
        self._medication_dispense_ed_table_name = medication_dispense_ed_table_name
        self._medication_administration_table_name = medication_administration_table_name
        self._medication_administration_icu_table_name = medication_administration_icu_table_name
        self._medication_statement_ed_table_name = medication_statement_ed_table_name
        self._observation_labevents_table_name = observation_labevents_table_name
        self._observation_micro_test_table_name = observation_micro_test_table_name
        self._observation_micro_org_table_name = observation_micro_org_table_name
        self._observation_micro_susc_table_name = observation_micro_susc_table_name
        self._observation_chartevents_table_name = observation_chartevents_table_name
        self._observation_datetimeevents_table_name = observation_datetimeevents_table_name
        self._observation_outputevents_table_name = observation_outputevents_table_name
        self._observation_ed_table_name = observation_ed_table_name
        self._observation_vital_signs_ed_table_name = observation_vital_signs_ed_table_name
        self._observation_vital_signs_ed_component_table_name = observation_vital_signs_ed_component_table_name
        self._specimen_table_name = specimen_table_name

    def list_conditions(self, connection: Connection, encounter_id: str) -> list[dict[str, Any]]:
        """Lista diagnósticos associados a um encounter."""

        return self._select_by_encounter(connection, self._condition_table_name, encounter_id)

    def list_procedures(self, connection: Connection, encounter_id: str) -> dict[str, list[dict[str, Any]]]:
        """Lista procedimentos agrupados por origem."""

        return {
            "procedure": self._select_by_encounter(connection, self._procedure_table_name, encounter_id),
            "procedure_ed": self._select_by_encounter(connection, self._procedure_ed_table_name, encounter_id),
            "procedure_icu": self._select_by_encounter(connection, self._procedure_icu_table_name, encounter_id),
        }

    def list_medications(self, connection: Connection, encounter_id: str) -> dict[str, list[dict[str, Any]]]:
        """Lista eventos de medicação agrupados por tipo."""

        return {
            "medication_request": self._select_by_encounter(connection, self._medication_request_table_name, encounter_id),
            "medication_dispense": self._select_by_encounter(connection, self._medication_dispense_table_name, encounter_id),
            "medication_dispense_ed": self._select_by_encounter(
                connection,
                self._medication_dispense_ed_table_name,
                encounter_id,
            ),
            "medication_administration": self._select_by_encounter(
                connection,
                self._medication_administration_table_name,
                encounter_id,
            ),
            "medication_administration_icu": self._select_by_encounter(
                connection,
                self._medication_administration_icu_table_name,
                encounter_id,
            ),
            "medication_statement_ed": self._select_by_encounter(
                connection,
                self._medication_statement_ed_table_name,
                encounter_id,
            ),
        }

    def list_labevents(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        """Lista observações laboratoriais de um paciente."""

        return self._select_by_patient(connection, self._observation_labevents_table_name, patient_id)

    def list_micro_tests(self, connection: Connection, patient_id: str, encounter_id: str) -> list[dict[str, Any]]:
        """Lista testes microbiológicos ligados ao paciente e/ou encounter."""

        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, self._observation_micro_test_table_name)}
            WHERE patient_id = :patient_id OR encounter_id = :encounter_id
        """
        return fetch_mappings(connection, sql, {"patient_id": patient_id, "encounter_id": encounter_id})

    def list_micro_orgs(self, connection: Connection, test_ids: Iterable[str]) -> list[dict[str, Any]]:
        """Lista organismos microbiológicos derivados dos testes informados."""

        test_ids = tuple(test_ids)
        if not test_ids:
            return []
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, self._observation_micro_org_table_name)}
            WHERE derived_from_observation_micro_test_id IN :test_ids
        """
        return fetch_mappings_expanding(
            connection,
            sql,
            {"test_ids": test_ids},
            expanding_parameter_names=("test_ids",),
        )

    def list_micro_suscs(self, connection: Connection, org_ids: Iterable[str]) -> list[dict[str, Any]]:
        """Lista susceptibilidades microbiológicas derivadas dos organismos informados."""

        org_ids = tuple(org_ids)
        if not org_ids:
            return []
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, self._observation_micro_susc_table_name)}
            WHERE derived_from_observation_micro_org_id IN :org_ids
        """
        return fetch_mappings_expanding(
            connection,
            sql,
            {"org_ids": org_ids},
            expanding_parameter_names=("org_ids",),
        )

    def list_charted_observations(self, connection: Connection, encounter_id: str) -> dict[str, list[dict[str, Any]]]:
        """Lista observações charted e de sinais vitais por encounter."""

        return {
            "observation_chartevents": self._select_by_encounter(
                connection,
                self._observation_chartevents_table_name,
                encounter_id,
            ),
            "observation_datetimeevents": self._select_by_encounter(
                connection,
                self._observation_datetimeevents_table_name,
                encounter_id,
            ),
            "observation_outputevents": self._select_by_encounter(
                connection,
                self._observation_outputevents_table_name,
                encounter_id,
            ),
            "observation_ed": self._select_by_encounter(connection, self._observation_ed_table_name, encounter_id),
            "observation_vital_signs_ed": self._select_by_encounter(
                connection,
                self._observation_vital_signs_ed_table_name,
                encounter_id,
            ),
        }

    def list_vital_sign_components(
        self,
        connection: Connection,
        observation_ids: Iterable[str],
    ) -> list[dict[str, Any]]:
        """Lista componentes associados aos sinais vitais de ED."""

        observation_ids = tuple(observation_ids)
        if not observation_ids:
            return []
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, self._observation_vital_signs_ed_component_table_name)}
            WHERE observation_vital_signs_ed_id IN :observation_ids
        """
        return fetch_mappings_expanding(
            connection,
            sql,
            {"observation_ids": observation_ids},
            expanding_parameter_names=("observation_ids",),
        )

    def list_specimens(self, connection: Connection, patient_id: str) -> list[dict[str, Any]]:
        """Lista specimen por paciente."""

        return self._select_by_patient(connection, self._specimen_table_name, patient_id)

    def _select_by_encounter(
        self,
        connection: Connection,
        table_name: str,
        encounter_id: str,
    ) -> list[dict[str, Any]]:
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, table_name)}
            WHERE encounter_id = :encounter_id
        """
        return fetch_mappings(connection, sql, {"encounter_id": encounter_id})

    def _select_by_patient(
        self,
        connection: Connection,
        table_name: str,
        patient_id: str,
    ) -> list[dict[str, Any]]:
        sql = f"""
            SELECT *
            FROM {qualified_table_name(self._schema_name, table_name)}
            WHERE patient_id = :patient_id
        """
        return fetch_mappings(connection, sql, {"patient_id": patient_id})
