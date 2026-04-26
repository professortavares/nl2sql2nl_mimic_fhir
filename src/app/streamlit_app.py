"""
Ponto de entrada da aplicação Streamlit.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st  # noqa: E402

from src.app.pages.individual_data import render_individual_data_tab  # noqa: E402
from src.config.settings import load_project_settings  # noqa: E402
from src.logging.logger import configure_logging  # noqa: E402


def main() -> None:
    """
    Inicializa a aplicação Streamlit com abas de navegação.
    """

    st.set_page_config(page_title="NL2SQL2NL", layout="wide")
    settings = load_project_settings()
    configure_logging(settings.logging)
    logger = logging.getLogger(__name__)
    logger.info("Aplicação Streamlit inicializada")

    st.title("NL2SQL2NL")
    st.caption("Exploração clínica individual sobre a base PostgreSQL já ingerida.")

    tabs = st.tabs(["Dados individuais", "Dados populacionais", "Chat"])
    with tabs[0]:
        render_individual_data_tab(settings)
    with tabs[1]:
        st.info("Aba em construção: Dados populacionais / BI.")
    with tabs[2]:
        st.info("Aba em construção: Chat.")


if __name__ == "__main__":
    main()
