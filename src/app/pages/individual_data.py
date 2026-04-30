"""
Página de exploração de dados individuais do paciente.
"""

from __future__ import annotations

import html
import logging
from collections.abc import Sequence
from datetime import datetime
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

    st.subheader("Individual Data")
    st.write("Enter a `patient_id` to view the chronological clinical timeline.")

    patient_id = st.text_input("Patient ID", placeholder="Patient ID: <uuid>")
    search_clicked = st.button("Search patient", type="primary")

    if not search_clicked:
        st.caption("Use the field above to start the search.")
        return

    normalized_patient_id = patient_id.strip()
    if not normalized_patient_id:
        st.warning("Please enter a `patient_id` before searching.")
        return

    LOGGER.info("Search started in the interface for patient_id=%s", normalized_patient_id)

    try:
        with st.spinner("Building the patient's timeline..."):
            timeline = load_patient_timeline(settings, normalized_patient_id)
    except PatientNotFoundError:
        st.warning("Patient not found.")
        return
    except TimelineQueryError as exc:
        LOGGER.exception("Error while building the timeline for patient_id=%s", normalized_patient_id)
        st.error("Unable to query the patient's timeline.")
        st.caption(str(exc))
        return
    except Exception as exc:  # pragma: no cover - proteção de UI
        LOGGER.exception("Unexpected interface error for patient_id=%s", normalized_patient_id)
        st.error("An unexpected error occurred while querying the patient.")
        st.caption(str(exc))
        return

    _render_patient_summary(timeline.patient)
    _render_timeline(timeline.encounters)


def _render_patient_summary(patient) -> None:
    """
    Exibe o cartão-resumo do paciente.
    """

    st.markdown("### Patient identification")
    columns = st.columns(3)
    left_items = [
        ("Patient ID", patient.id),
        ("Name", patient.name),
    ]
    middle_items = [
        ("Gender", patient.gender),
        ("Date of birth", patient.birth_date),
        ("Identifier", patient.identifier),
    ]
    right_items = [
        ("Race", patient.race),
        ("Ethnicity", patient.ethnicity),
        ("Birth sex", patient.birthsex),
        ("Organization", patient.managing_organization_name),
    ]
    _render_key_value_list(columns[0], left_items)
    _render_key_value_list(columns[1], middle_items)
    _render_key_value_list(columns[2], right_items)


def _render_timeline(encounters: Sequence[EncounterTimeline]) -> None:
    """
    Exibe a timeline vertical dos encounters.
    """

    st.markdown("### Encounter timeline")
    if not encounters:
        st.info("No encounters found for this patient.")
        return

    for encounter in encounters:
        title = _build_encounter_title(encounter)
        with st.expander(title, expanded=False):
            _render_general_hospital_context(encounter.general_hospital)


def _render_general_hospital_context(context: dict[str, Any]) -> None:
    """
    Renderiza o contexto de hospital geral.
    """

    if not _has_context_data(context):
        st.info("No data found for this context.")
        return

    hospitalization = context.get("hospitalization")
    if not hospitalization:
        st.info("No hospitalization information found for this encounter.")
        return

    st.markdown("### Hospitalization information")
    columns = st.columns(2)
    left_items = [
        ("Encounter ID", hospitalization.get("id")),
        ("Status", hospitalization.get("status")),
        ("Class code", hospitalization.get("class_code")),
        ("Start date", hospitalization.get("start_date")),
        ("End date", hospitalization.get("end_date")),
    ]
    right_items = [
        ("Organization", hospitalization.get("organization_name")),
        ("Admit source", hospitalization.get("admit_source_code")),
        ("Discharge disposition", hospitalization.get("discharge_disposition_code")),
        ("Service type", hospitalization.get("service_type_code")),
        ("Priority", hospitalization.get("priority_code")),
    ]
    _render_key_value_list(columns[0], left_items)
    _render_key_value_list(columns[1], right_items)
    _render_hospital_transfers_section(context.get("hospital_transfers") or [])
    _render_diagnoses_section(context.get("diagnoses") or [])
    _render_medications_section(context.get("medication_events") or [])


def _render_emergency_department_context(context: dict[str, Any]) -> None:
    """
    Renderiza o contexto do departamento de emergência.
    """

    if not _has_context_data(context):
        st.info("No data found for this context.")
        return

    _render_section("ED stay information", context.get("stay"), mode="single")
    _render_section("ED diagnoses", context.get("diagnoses"))
    _render_section("ED procedures", context.get("procedures"))
    _render_section("Emergency observations", context.get("observations"))
    _render_vital_signs_section(context.get("vital_signs") or [])
    medications = context.get("medications") or {}
    _render_section("Medication dispenses", medications.get("dispensacoes_ed"))
    _render_section("Medication statements", medications.get("medication_statements_ed"))


def _render_icu_context(context: dict[str, Any]) -> None:
    """
    Renderiza o contexto de UTI.
    """

    if not _has_context_data(context):
        st.info("No data found for this context.")
        return

    _render_section("ICU stay information", context.get("stay"), mode="single")
    _render_section("ICU procedures", context.get("procedures"))
    _render_section("ICU medication administrations", context.get("medications"))
    _render_section("Charted events", context.get("charted_events"))
    _render_section("Output events", context.get("output_events"))
    _render_section("Date/time events", context.get("datetime_events"))


def _render_vital_signs_section(rows: list[dict[str, Any]]) -> None:
    """
    Renderiza sinais vitais ED com componentes associados.
    """

    if not rows:
        st.caption("No records found.")
        return

    st.markdown("#### ED vital signs")
    st.dataframe(_normalize_rows(rows), use_container_width=True, hide_index=True)
    components = _collect_components(rows)
    if components:
        st.markdown("##### Components")
        st.dataframe(_normalize_rows(components), use_container_width=True, hide_index=True)


def _render_section(title: str, data: Any, *, mode: str = "table") -> None:
    """
    Renderiza uma seção clínica simples.
    """

    if not data:
        st.caption("No records found.")
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


def _render_diagnoses_section(rows: list[dict[str, Any]]) -> None:
    """
    Renderiza os diagnósticos associados ao encounter atual.
    """

    st.markdown("#### Diagnoses")
    if not rows:
        st.caption("No diagnoses found for this encounter.")
        return

    diagnosis_rows = [
        {
            "condition_code": row.get("condition_code"),
            "condition_code_display": row.get("condition_code_display"),
        }
        for row in rows
    ]
    st.dataframe(diagnosis_rows, use_container_width=True, hide_index=True)


def _render_hospital_transfers_section(rows: list[dict[str, Any]]) -> None:
    """
    Renderiza as transferências hospitalares do encounter atual.
    """

    st.subheader("Hospital transfers")
    if not rows:
        st.info("No hospital transfers found for this encounter.")
        return

    for row in rows:
        location_name = _format_display_value(row.get("location_name")) or "Unknown location"
        start_date = _format_datetime_display(row.get("start_date")) or "-"
        end_date = _format_datetime_display(row.get("end_date")) or "Ongoing"
        st.markdown(
            f"""
            <div style="
                border: 1px solid rgba(49, 51, 63, 0.18);
                border-radius: 0.75rem;
                padding: 0.85rem 1rem;
                margin-bottom: 0.5rem;
                background: rgba(250, 250, 250, 0.75);
            ">
                <div style="font-weight: 700; margin-bottom: 0.15rem;">{html.escape(str(location_name))}</div>
                <div style="color: rgba(49, 51, 63, 0.75);">
                    {html.escape(start_date)} &rarr; {html.escape(end_date)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_medications_section(rows: list[dict[str, Any]]) -> None:
    """
    Renderiza as medicações do encounter atual.
    """

    st.subheader("Medications")
    if not rows:
        st.info("No medications found for this encounter.")
        return

    medication_groups = _group_medication_events(rows)
    for medication in medication_groups:
        title = medication["medication_name"]
        prescription_count = len(medication["prescriptions"])
        expander_label = title if prescription_count == 1 else f"{title} ({prescription_count} prescriptions)"
        with st.expander(expander_label, expanded=False):
            for index, prescription in enumerate(medication["prescriptions"], start=1):
                if index > 1:
                    st.divider()
                st.markdown(f"**Prescription {index}**")
                left_column, middle_column, right_column = st.columns(3)
                left_items = [
                    ("Valid from", _format_datetime_display(prescription.get("validity_start")) or "-"),
                    ("Valid to", _format_datetime_display(prescription.get("validity_end")) or "-"),
                ]
                middle_items = [
                    ("Frequency", prescription.get("frequency_code")),
                    ("Request status", prescription.get("request_status")),
                ]
                right_items = [
                    ("Intent", prescription.get("request_intent")),
                    ("Request ID", prescription.get("medication_request_id")),
                ]
                _render_key_value_list(left_column, left_items)
                _render_key_value_list(middle_column, middle_items)
                _render_key_value_list(right_column, right_items)

                administrations = prescription["administrations"]
                if not administrations:
                    st.caption("No administrations recorded yet.")
                    continue

                st.markdown("**Administrations**")
                st.dataframe(
                    [
                        {
                            "effective_at": _format_datetime_display(administration.get("effective_at")) or "-",
                            "dose_value": administration.get("dose_value"),
                            "dose_unit": administration.get("dose_unit"),
                            "status": administration.get("status"),
                        }
                        for administration in administrations
                    ],
                    use_container_width=True,
                    hide_index=True,
                )


def _group_medication_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Agrupa linhas de medicação por nome e por prescription/request.
    """

    grouped_by_name: dict[str, dict[str, Any]] = {}
    for row in rows:
        medication_name = _format_display_value(row.get("medication_name")) or "Unknown medication"
        request_id = str(row.get("medication_request_id") or f"{medication_name}-{row.get('validity_start') or 'request'}")
        medication_group = grouped_by_name.setdefault(
            medication_name,
            {"medication_name": medication_name, "prescriptions": {}},
        )
        prescriptions: dict[str, Any] = medication_group["prescriptions"]
        prescription = prescriptions.setdefault(
            request_id,
            {
                "medication_request_id": row.get("medication_request_id"),
                "validity_start": row.get("validity_start"),
                "validity_end": row.get("validity_end"),
                "frequency_code": row.get("frequency_code"),
                "request_status": row.get("request_status"),
                "request_intent": row.get("request_intent"),
                "request_identifier": row.get("request_identifier"),
                "administrations": [],
            },
        )
        administration_id = row.get("medication_administration_id")
        if administration_id is not None or row.get("effective_at") is not None or row.get("status") is not None:
            prescription["administrations"].append(
                {
                    "id": administration_id,
                    "effective_at": row.get("effective_at"),
                    "dose_value": row.get("dose_value"),
                    "dose_unit": row.get("dose_unit"),
                    "status": row.get("status"),
                }
            )

    grouped_rows: list[dict[str, Any]] = []
    for medication_name, payload in grouped_by_name.items():
        prescriptions = list(payload["prescriptions"].values())
        prescriptions.sort(
            key=lambda item: (
                1 if item.get("validity_start") is None else 0,
                str(item.get("validity_start") or ""),
                str(item.get("medication_request_id") or ""),
            )
        )
        grouped_rows.append({"medication_name": medication_name, "prescriptions": prescriptions})

    grouped_rows.sort(key=lambda item: item["medication_name"].lower())
    return grouped_rows


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
            st.write(value if value not in (None, "") else "Not provided.")


def _build_encounter_title(encounter: EncounterTimeline) -> str:
    """
    Monta o título de um expander de encounter.
    """

    start_date = _format_display_value(encounter.summary.start_date) or "no start date"
    end_date = _format_display_value(encounter.summary.end_date) or "open-ended"
    class_code = _format_display_value(encounter.summary.class_code) or "no class"
    status = _format_display_value(encounter.summary.status) or "no status"
    encounter_id = encounter.summary.id[:8]
    return f"{start_date} → {end_date} | class {class_code} | {status} | {encounter_id}"


SECTION_LABELS = {
    "administracoes": "Administrations",
    "charted_events": "Charted Events",
    "datetime_events": "Date/Time Events",
    "diagnoses": "Diagnoses",
    "dispensacoes": "Dispenses",
    "dispensacoes_ed": "Medication Dispenses",
    "hospitalization": "Hospitalization",
    "labs": "Lab Tests",
    "medication_statements_ed": "Medication Statements",
    "medications": "Medications",
    "observations": "Observations",
    "organismos": "Identified Organisms",
    "output_events": "Output Events",
    "pedidos_de_medicacao": "Medication Requests",
    "procedures": "Procedures",
    "specimens": "Specimens",
    "stay": "Stay",
    "susceptibilidades": "Susceptibilities",
    "testes": "Tests",
    "vital_signs": "Vital Signs",
}


def _friendly_section_name(section_name: str) -> str:
    """Converts technical names into friendlier labels."""

    return SECTION_LABELS.get(section_name, section_name.replace("_", " ").title())


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


def _format_datetime_display(value: Any) -> str | None:
    """Formata datas ISO para um texto legível na interface."""

    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return value
    if parsed.time() == datetime.min.time():
        return parsed.strftime("%Y-%m-%d")
    return parsed.strftime("%Y-%m-%d %H:%M")


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
