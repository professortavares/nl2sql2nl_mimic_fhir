"""
Página de exploração de dados individuais do paciente.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

import streamlit as st
from sqlalchemy.engine import Engine

from src.app.models.patient_timeline import EncounterTimeline, PatientTimeline
from src.app.services.patient_timeline_service import (
    PatientNotFoundError,
    TimelineQueryError,
    build_patient_timeline_service,
)
from src.config.settings import ProjectSettings
from src.db.connection import create_engine_from_settings

LOGGER = logging.getLogger(__name__)


@st.cache_resource(show_spinner=False)
def get_engine(database_settings: Any) -> Engine:
    """
    Cria e reaproveita a engine SQLAlchemy.
    """

    return create_engine_from_settings(database_settings)


@st.cache_data(show_spinner=False, ttl=60)
def load_patient_timeline(settings: ProjectSettings, patient_id: str) -> PatientTimeline:
    """
    Carrega a timeline clínica de um paciente.
    """

    service = build_patient_timeline_service(settings)
    engine = get_engine(settings.database)
    with engine.connect() as connection:
        return service.build_timeline(connection, patient_id)


def render_individual_data_tab(settings: ProjectSettings) -> None:
    """
    Renderiza a aba de dados individuais.
    """

    st.subheader("Dados individuais")
    st.write("Informe um `patient_id` para consultar a timeline clínica cronológica.")

    patient_id = st.text_input("Patient ID", placeholder="Patient ID: <uuid>")
    search_clicked = st.button("Buscar paciente", type="primary")

    if not search_clicked:
        st.caption("Use o campo acima para iniciar a busca.")
        return

    normalized_patient_id = patient_id.strip()
    if not normalized_patient_id:
        st.warning("Informe um `patient_id` antes de buscar.")
        return

    LOGGER.info("Busca iniciada na interface para patient_id=%s", normalized_patient_id)

    try:
        with st.spinner("Montando timeline do paciente..."):
            timeline = load_patient_timeline(settings, normalized_patient_id)
    except PatientNotFoundError:
        st.warning("Paciente não encontrado.")
        return
    except TimelineQueryError as exc:
        LOGGER.exception("Erro ao montar timeline para patient_id=%s", normalized_patient_id)
        st.error("Não foi possível consultar a timeline do paciente.")
        st.caption(str(exc))
        return
    except Exception as exc:  # pragma: no cover - proteção de UI
        LOGGER.exception("Falha inesperada na interface para patient_id=%s", normalized_patient_id)
        st.error("Ocorreu um erro inesperado ao consultar o paciente.")
        st.caption(str(exc))
        return

    _render_patient_summary(timeline.patient)
    _render_timeline(timeline.encounters)


def _render_patient_summary(patient) -> None:
    """
    Exibe o cartão-resumo do paciente.
    """

    st.markdown("### Identificação do paciente")
    columns = st.columns(2)
    left_items = [
        ("Patient ID", patient.id),
        ("Nome", patient.name),
        ("Gênero", patient.gender),
        ("Data de nascimento", patient.birth_date),
        ("Identifier", patient.identifier),
    ]
    right_items = [
        ("Raça", patient.race),
        ("Etnia", patient.ethnicity),
        ("Birth sex", patient.birthsex),
        ("Organization ID", patient.managing_organization_id),
        ("Organization", patient.managing_organization_name),
    ]
    _render_key_value_list(columns[0], left_items)
    _render_key_value_list(columns[1], right_items)


def _render_timeline(encounters: Sequence[EncounterTimeline]) -> None:
    """
    Exibe a timeline vertical dos encounters.
    """

    st.markdown("### Timeline de encounters")
    if not encounters:
        st.info("Nenhum encounter encontrado para este paciente.")
        return

    for encounter in encounters:
        title = _build_encounter_title(encounter)
        with st.expander(title, expanded=False):
            _render_encounter_summary(encounter)
            _render_rows_section("Diagnósticos", encounter.diagnoses)
            _render_grouped_sections("Procedimentos", encounter.procedures)
            _render_grouped_sections("Medicações", encounter.medications)
            _render_rows_section("Laboratório", encounter.laboratory)
            _render_microbiology_section(encounter.microbiology)
            _render_grouped_sections("Observações charted", encounter.charted_observations)
            _render_rows_section("Specimens", encounter.specimens)


def _render_encounter_summary(encounter: EncounterTimeline) -> None:
    """
    Exibe o resumo do encounter.
    """

    st.markdown("#### Resumo do encounter")
    columns = st.columns(2)
    left_items = [
        ("Encounter ID", encounter.summary.id),
        ("Status", encounter.summary.status),
        ("Class code", encounter.summary.class_code),
        ("Start date", encounter.summary.start_date),
        ("End date", encounter.summary.end_date),
    ]
    right_items = [
        ("Organization ID", encounter.summary.organization_id),
        ("Organization", encounter.summary.organization_name),
        ("Admit source", encounter.summary.admit_source_code),
        ("Discharge disposition", encounter.summary.discharge_disposition_code),
        ("Service type", encounter.summary.service_type_code),
        ("Priority", encounter.summary.priority_code),
    ]
    _render_key_value_list(columns[0], left_items)
    _render_key_value_list(columns[1], right_items)


def _render_microbiology_section(microbiology: dict[str, list[dict[str, Any]]]) -> None:
    """
    Exibe os eventos de microbiologia por etapa.
    """

    st.markdown("#### Microbiologia")
    if not microbiology:
        st.caption("Nenhum registro encontrado.")
        return

    for section_name, rows in microbiology.items():
        st.markdown(f"**{_friendly_section_name(section_name)}**")
        _render_rows_section(section_name, rows)


def _render_grouped_sections(title: str, grouped_rows: dict[str, list[dict[str, Any]]]) -> None:
    """
    Exibe conjuntos de registros agrupados por fonte.
    """

    st.markdown(f"#### {title}")
    if not grouped_rows:
        st.caption("Nenhum registro encontrado.")
        return

    any_rows = False
    for section_name, rows in grouped_rows.items():
        st.markdown(f"**{_friendly_section_name(section_name)}**")
        _render_rows_section(section_name, rows)
        any_rows = any_rows or bool(rows)
    if not any_rows:
        st.caption("Nenhum registro encontrado.")


def _render_rows_section(title: str, rows: list[dict[str, Any]]) -> None:
    """
    Exibe uma tabela simples ou mensagem vazia.
    """

    if not rows:
        st.caption("Nenhum registro encontrado.")
        return

    display_rows = [_normalize_row(row) for row in rows]
    st.dataframe(display_rows, use_container_width=True, hide_index=True)
    if title == "observation_vital_signs_ed":
        components = _collect_components(rows)
        if components:
            st.markdown("**Componentes**")
            st.dataframe(components, use_container_width=True, hide_index=True)


def _collect_components(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Achata os componentes dos sinais vitais em uma tabela própria.
    """

    collected_components: list[dict[str, Any]] = []
    for row in rows:
        parent_id = row.get("id")
        for component in row.get("components", []):
            enriched_component = dict(component)
            enriched_component["observation_vital_signs_ed_id"] = parent_id
            collected_components.append(enriched_component)
    return collected_components


def _render_key_value_list(column, items: list[tuple[str, Any]]) -> None:
    """
    Renderiza uma lista de pares chave-valor.
    """

    with column:
        for label, value in items:
            st.markdown(f"**{label}**")
            st.write(value if value not in (None, "") else "Não informado.")


def _build_encounter_title(encounter: EncounterTimeline) -> str:
    """
    Monta o título de um expander de encounter.
    """

    start_date = encounter.summary.start_date or "sem início"
    end_date = encounter.summary.end_date or "em aberto"
    class_code = encounter.summary.class_code or "sem class"
    status = encounter.summary.status or "sem status"
    encounter_id = encounter.summary.id[:8]
    return f"{start_date} → {end_date} | class {class_code} | {status} | {encounter_id}"


def _friendly_section_name(section_name: str) -> str:
    """Converte nomes técnicos em rótulos mais legíveis."""

    return section_name.replace("_", " ").title()


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Normaliza valores para exibição na tabela."""

    normalized_row = dict(row)
    normalized_row.pop("components", None)
    return normalized_row
