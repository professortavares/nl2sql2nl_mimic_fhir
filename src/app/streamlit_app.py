"""
Ponto de entrada da aplicação Streamlit.
"""

from __future__ import annotations

import logging

import streamlit as st

from src.app.pages.individual_data import render_individual_data_tab
from src.config.settings import load_project_settings
from src.logging.logger import configure_logging


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
