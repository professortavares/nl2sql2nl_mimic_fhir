"""
Leitura e validação centralizadas das configurações da aplicação.

As credenciais de banco ficam no arquivo `.env` da raiz do projeto.
As demais configurações não sensíveis são lidas de arquivos YAML em `./config`.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from src.config.yaml_loader import load_yaml_file

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class ConfigurationError(ValueError):
    """Indica que uma configuração obrigatória está ausente ou inválida."""


@dataclass(slots=True, frozen=True)
class DatabaseSettings:
    """Configuração de conexão com o PostgreSQL."""

    host: str
    port: int
    database: str
    user: str
    password: str
    schema_name: str
    echo: bool = False
    pool_pre_ping: bool = True


@dataclass(slots=True, frozen=True)
class LoggingSettings:
    """Configuração do logging da aplicação."""

    log_dir: Path
    log_file: str
    level: str
    console_enabled: bool
    max_bytes: int
    backup_count: int


@dataclass(slots=True, frozen=True)
class CommonIngestionSettings:
    """Configurações compartilhadas entre as ingestões."""

    reset_policy: str
    skip_invalid_records: bool
    batch_size: int


@dataclass(slots=True, frozen=True)
class PipelineResourcesSettings:
    """Configuração da ordem de execução da pipeline."""

    execution_order: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ResourceIngestionSettings:
    """Configurações específicas de um recurso FHIR."""

    pipeline_name: str
    input_path: Path
    batch_size: int
    table_name: str


@dataclass(slots=True, frozen=True)
class ProjectSettings:
    """Agrupa todas as configurações da aplicação."""

    database: DatabaseSettings
    logging: LoggingSettings
    common: CommonIngestionSettings
    resources: PipelineResourcesSettings
    organization: ResourceIngestionSettings
    location: ResourceIngestionSettings
    patient: ResourceIngestionSettings


def project_root() -> Path:
    """
    Localiza a raiz do projeto.

    Retorno:
    -------
    Path
        Caminho absoluto da raiz do repositório.
    """

    return Path(__file__).resolve().parents[2]


def load_dotenv_file(path: Path) -> None:
    """
    Carrega variáveis de ambiente a partir de um arquivo `.env`.

    Parâmetros:
    ----------
    path : Path
        Caminho para o arquivo `.env`.

    Exceções:
    --------
    FileNotFoundError
        Quando o arquivo não existe.
    ConfigurationError
        Quando uma linha não possui o formato `CHAVE=VALOR`.
    """

    if not path.exists():
        raise FileNotFoundError(f"Arquivo .env não encontrado: {path}")

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigurationError(f"Linha inválida em {path}: {raw_line!r}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            raise ConfigurationError(f"Chave vazia no arquivo {path}: {raw_line!r}")
        os.environ.setdefault(key, value)


def _require_string(data: Mapping[str, Any], key: str, *, source: Path) -> str:
    """
    Obtém uma string obrigatória de um mapeamento.
    """

    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"Campo obrigatório ausente ou inválido em {source}: {key}")
    return value.strip()


def _optional_string(data: Mapping[str, Any], key: str) -> str | None:
    """
    Obtém uma string opcional de um mapeamento.
    """

    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _require_bool(data: Mapping[str, Any], key: str, *, default: bool, source: Path) -> bool:
    """
    Obtém um valor booleano com fallback padrão.
    """

    value = data.get(key, default)
    if isinstance(value, bool):
        return value
    raise ConfigurationError(f"Campo booleano inválido em {source}: {key}")


def _require_int(data: Mapping[str, Any], key: str, *, source: Path) -> int:
    """
    Obtém um valor inteiro positivo de um mapeamento.
    """

    value = data.get(key)
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, str):
        try:
            parsed_value = int(value)
        except ValueError as exc:
            raise ConfigurationError(f"Campo inteiro positivo inválido em {source}: {key}") from exc
        if parsed_value > 0:
            return parsed_value
    raise ConfigurationError(f"Campo inteiro positivo inválido em {source}: {key}")


def _validate_identifier(name: str, *, label: str) -> str:
    """
    Valida um identificador SQL simples.
    """

    if not _IDENTIFIER_PATTERN.fullmatch(name):
        raise ConfigurationError(f"{label} inválido: {name!r}")
    return name


def _resolve_path(root: Path, value: str) -> Path:
    """
    Resolve um caminho relativo à raiz do projeto.
    """

    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (root / candidate).resolve()


def _load_resource_settings(
    data: Mapping[str, Any],
    *,
    source: Path,
    root: Path,
) -> ResourceIngestionSettings:
    """
    Carrega as configurações de um recurso FHIR simplificado.
    """

    pipeline_name = _require_string(data, "pipeline_name", source=source)
    input_path = _resolve_path(root, _require_string(data, "input_path", source=source))
    batch_size = _require_int(data, "batch_size", source=source)
    table_name = _require_string(data, "table_name", source=source)
    _validate_identifier(table_name, label=f"table_name em {source.name}")
    return ResourceIngestionSettings(
        pipeline_name=pipeline_name,
        input_path=input_path,
        batch_size=batch_size,
        table_name=table_name,
    )


def load_project_settings() -> ProjectSettings:
    """
    Carrega e valida todas as configurações da aplicação.

    Retorno:
    -------
    ProjectSettings
        Estrutura consolidada com as configurações prontas para uso.

    Exceções:
    --------
    FileNotFoundError
        Quando o `.env` ou um YAML obrigatório não existir.
    ConfigurationError
        Quando algum valor obrigatório estiver ausente ou inválido.
    """

    root = project_root()
    load_dotenv_file(root / ".env")

    database_yaml = load_yaml_file(root / "config/database.yaml")
    logging_yaml = load_yaml_file(root / "config/logging.yaml")
    common_yaml = load_yaml_file(root / "config/ingestion/common.yaml")
    resources_yaml = load_yaml_file(root / "config/pipeline/resources.yaml")
    organization_yaml = load_yaml_file(root / "config/ingestion/organization.yaml")
    location_yaml = load_yaml_file(root / "config/ingestion/location.yaml")
    patient_yaml = load_yaml_file(root / "config/ingestion/patient.yaml")

    database = DatabaseSettings(
        host=_require_string(os.environ, "POSTGRES_HOST", source=root / ".env"),
        port=_require_int_from_env("POSTGRES_PORT", source=root / ".env"),
        database=_require_string(os.environ, "POSTGRES_DB", source=root / ".env"),
        user=_require_string(os.environ, "POSTGRES_USER", source=root / ".env"),
        password=_require_string(os.environ, "POSTGRES_PASSWORD", source=root / ".env"),
        schema_name=_require_string(database_yaml, "schema_name", source=root / "config/database.yaml"),
        echo=_require_bool(database_yaml, "echo", default=False, source=root / "config/database.yaml"),
        pool_pre_ping=_require_bool(
            database_yaml,
            "pool_pre_ping",
            default=True,
            source=root / "config/database.yaml",
        ),
    )

    logging_settings = LoggingSettings(
        log_dir=_resolve_path(root, _require_string(logging_yaml, "log_dir", source=root / "config/logging.yaml")),
        log_file=_require_string(logging_yaml, "log_file", source=root / "config/logging.yaml"),
        level=_require_string(logging_yaml, "level", source=root / "config/logging.yaml"),
        console_enabled=_require_bool(
            logging_yaml,
            "console_enabled",
            default=True,
            source=root / "config/logging.yaml",
        ),
        max_bytes=_require_int(logging_yaml, "max_bytes", source=root / "config/logging.yaml"),
        backup_count=_require_int(logging_yaml, "backup_count", source=root / "config/logging.yaml"),
    )

    common = CommonIngestionSettings(
        reset_policy=_require_string(common_yaml, "reset_policy", source=root / "config/ingestion/common.yaml"),
        skip_invalid_records=_require_bool(
            common_yaml,
            "skip_invalid_records",
            default=True,
            source=root / "config/ingestion/common.yaml",
        ),
        batch_size=_require_int(common_yaml, "batch_size", source=root / "config/ingestion/common.yaml"),
    )

    execution_order = resources_yaml.get("execution_order")
    if not isinstance(execution_order, list) or not execution_order:
        raise ConfigurationError(
            f"Campo obrigatório ausente ou inválido em {root / 'config/pipeline/resources.yaml'}: execution_order"
        )
    normalized_execution_order: list[str] = []
    for item in execution_order:
        if not isinstance(item, str) or not item.strip():
            raise ConfigurationError(
                f"execution_order inválido em {root / 'config/pipeline/resources.yaml'}: {item!r}"
            )
        normalized_execution_order.append(item.strip())

    resources = PipelineResourcesSettings(execution_order=tuple(normalized_execution_order))

    organization = _load_resource_settings(
        organization_yaml,
        source=root / "config/ingestion/organization.yaml",
        root=root,
    )
    location = _load_resource_settings(
        location_yaml,
        source=root / "config/ingestion/location.yaml",
        root=root,
    )
    patient = _load_resource_settings(
        patient_yaml,
        source=root / "config/ingestion/patient.yaml",
        root=root,
    )

    return ProjectSettings(
        database=database,
        logging=logging_settings,
        common=common,
        resources=resources,
        organization=organization,
        location=location,
        patient=patient,
    )


def _require_int_from_env(key: str, *, source: Path) -> int:
    """
    Obtém um inteiro positivo diretamente de uma variável de ambiente.
    """

    value = os.getenv(key)
    if value is None or not value.strip():
        raise ConfigurationError(f"Variável de ambiente obrigatória ausente em {source}: {key}")
    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise ConfigurationError(f"Variável de ambiente inválida em {source}: {key}") from exc
    if parsed_value <= 0:
        raise ConfigurationError(f"Variável de ambiente inválida em {source}: {key}")
    return parsed_value
