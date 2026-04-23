"""
Configuração de logging com saída em console e arquivo rotativo.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config.settings import LoggingSettings


def configure_logging(settings: LoggingSettings) -> Path:
    """
    Configura o logging da aplicação.

    Parâmetros:
    ----------
    settings : LoggingSettings
        Configuração carregada do YAML.

    Retorno:
    -------
    Path
        Caminho completo do arquivo de log.
    """

    log_dir = settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / settings.log_file

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, settings.level.upper(), logging.INFO))

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=settings.max_bytes,
        backupCount=settings.backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if settings.console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    return log_file_path

