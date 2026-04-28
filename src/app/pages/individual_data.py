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
            tabs = st.tabs(["General Hospital", "Emergency Department (ED)", "Intensive Care Unit (ICU)"])
            with tabs[0]:
                _render_general_hospital_context(encounter.general_hospital)
            with tabs[1]:
                _render_emergency_department_context(encounter.emergency_department)
            with tabs[2]:
                _render_icu_context(encounter.icu)


def _render_general_hospital_context(context: dict[str, Any]) -> None:
    """
    Renderiza o contexto de hospital geral.
    """

    if not _has_context_data(context):
        st.info("Nenhum dado encontrado para este contexto.")
        return

    _render_section("Informações da hospitalização", context.get("hospitalization"), mode="single")
    _render_section("Diagnósticos", context.get("diagnoses"))
    _render_section("Procedimentos gerais", context.get("procedures"))
    medications = context.get("medications") or {}
    _render_section("Pedidos de medicação", medications.get("pedidos_de_medicacao"))
    _render_section("Dispensações", medications.get("dispensacoes"))
    _render_section("Administrações", medications.get("administracoes"))
    _render_section("Exames laboratoriais", context.get("labs"))
    microbiology = context.get("microbiology") or {}
    _render_section("Testes microbiológicos", microbiology.get("testes"))
    _render_section("Organismos identificados", microbiology.get("organismos"))
    _render_section("Susceptibilidades", microbiology.get("susceptibilidades"))
    _render_section("Specimens", context.get("specimens"))


def _render_emergency_department_context(context: dict[str, Any]) -> None:
    """
    Renderiza o contexto do departamento de emergência.
    """

    if not _has_context_data(context):
        st.info("Nenhum dado encontrado para este contexto.")
        return

    _render_section("Informações da permanência no ED", context.get("stay"), mode="single")
    _render_section("Diagnósticos ED", context.get("diagnoses"))
    _render_section("Procedimentos ED", context.get("procedures"))
    _render_section("Observações da emergência", context.get("observations"))
    _render_vital_signs_section(context.get("vital_signs") or [])
    medications = context.get("medications") or {}
    _render_section("Dispensações de medicamentos", medications.get("dispensacoes_ed"))
    _render_section("Declarações de medicação", medications.get("medication_statements_ed"))


def _render_icu_context(context: dict[str, Any]) -> None:
    """
    Renderiza o contexto de UTI.
    """

    if not _has_context_data(context):
        st.info("Nenhum dado encontrado para este contexto.")
        return

    _render_section("Informações da permanência na ICU", context.get("stay"), mode="single")
    _render_section("Procedimentos ICU", context.get("procedures"))
    _render_section("Administrações de medicação ICU", context.get("medications"))
    _render_section("Eventos charted", context.get("charted_events"))
    _render_section("Eventos de saída", context.get("output_events"))
    _render_section("Eventos data/hora", context.get("datetime_events"))


def _render_vital_signs_section(rows: list[dict[str, Any]]) -> None:
    """
    Renderiza sinais vitais ED com componentes associados.
    """

    if not rows:
        st.caption("Nenhum registro encontrado.")
        return

    st.markdown("#### Sinais vitais ED")
    st.dataframe(_normalize_rows(rows), use_container_width=True, hide_index=True)
    components = _collect_components(rows)
    if components:
        st.markdown("##### Componentes")
        st.dataframe(_normalize_rows(components), use_container_width=True, hide_index=True)


def _render_section(title: str, data: Any, *, mode: str = "table") -> None:
    """
    Renderiza uma seção clínica simples.
    """

    if not data:
        st.caption("Nenhum registro encontrado.")
        return

    st.markdown(f"#### {title}")
    if mode == "single":
        st.dataframe(_normalize_rows([data]), use_container_width=True, hide_index=True)
        return
    if isinstance(data, list):
        st.dataframe(_normalize_rows(data), use_container_width=True, hide_index=True)
        return
    if isinstance(data, dict):
        for subsection_title, subsection_rows in data.items():
            st.markdown(f"**{_friendly_section_name(subsection_title)}**")
            _render_section(subsection_title, subsection_rows)
        return
    st.write(data)


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

    start_date = _format_display_value(encounter.summary.start_date) or "sem início"
    end_date = _format_display_value(encounter.summary.end_date) or "em aberto"
    class_code = _format_display_value(encounter.summary.class_code) or "sem class"
    status = _format_display_value(encounter.summary.status) or "sem status"
    encounter_id = encounter.summary.id[:8]
    return f"{start_date} → {end_date} | class {class_code} | {status} | {encounter_id}"


def _friendly_section_name(section_name: str) -> str:
    """Converte nomes técnicos em rótulos mais legíveis."""

    return section_name.replace("_", " ").title()


def _normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normaliza registros para exibição na tabela."""

    return [_normalize_row(row) for row in rows]


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Remove estruturas internas e formata datas para exibição."""

    normalized_row = dict(row)
    normalized_row.pop("components", None)
    for key, value in list(normalized_row.items()):
        normalized_row[key] = _format_display_value(value)
    return normalized_row


def _format_display_value(value: Any) -> Any:
    """Formata valores de exibição sem alterar identificadores ou textos."""

    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return [_format_display_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _format_display_value(item) for key, item in value.items()}
    return value


def _has_context_data(context: dict[str, Any]) -> bool:
    """Indica se um contexto clínico possui dados relevantes."""

    for value in context.values():
        if isinstance(value, list) and value:
            return True
        if isinstance(value, dict) and _has_context_data(value):
            return True
        if value not in (None, [], {}):
            return True
    return False
