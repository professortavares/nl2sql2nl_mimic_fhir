"""
Leitura e validação centralizadas das configurações da aplicação.

As credenciais permanecem no `.env`, enquanto os parâmetros de pipeline,
schema e logging ficam em arquivos YAML versionáveis.
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
    """Configurações comuns às ingestões FHIR."""

    reset_policy: str
    skip_invalid_records: bool
    batch_size: int
    ingestion_order: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class OrganizationTableNames:
    """Nomes físicos das tabelas de Organization."""

    organization: str
    meta_profile: str
    identifier: str
    type_coding: str


@dataclass(slots=True, frozen=True)
class LocationTableNames:
    """Nomes físicos das tabelas de Location."""

    location: str
    meta_profile: str
    physical_type_coding: str


@dataclass(slots=True, frozen=True)
class OrganizationIngestionSettings:
    """Configurações específicas da ingestão de Organization."""

    pipeline_name: str
    input_path: Path
    batch_size: int
    table_names: OrganizationTableNames


@dataclass(slots=True, frozen=True)
class LocationIngestionSettings:
    """Configurações específicas da ingestão de Location."""

    pipeline_name: str
    input_path: Path
    batch_size: int
    table_names: LocationTableNames


@dataclass(slots=True, frozen=True)
class ProjectSettings:
    """Agrupa todas as configurações da aplicação."""

    database: DatabaseSettings
    logging: LoggingSettings
    common: CommonIngestionSettings
    organization: OrganizationIngestionSettings
    location: LocationIngestionSettings


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
        Quando a linha está em formato inválido.
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


def _load_resource_tables_organization(
    data: Mapping[str, Any],
    *,
    source: Path,
) -> OrganizationTableNames:
    """
    Carrega os nomes físicos das tabelas de Organization.
    """

    tables = data.get("table_names")
    if not isinstance(tables, Mapping):
        raise ConfigurationError(f"O bloco 'table_names' é obrigatório em {source}")

    return OrganizationTableNames(
        organization=_validate_identifier(
            _require_string(tables, "organization", source=source),
            label="organization table",
        ),
        meta_profile=_validate_identifier(
            _require_string(tables, "organization_meta_profile", source=source),
            label="organization_meta_profile table",
        ),
        identifier=_validate_identifier(
            _require_string(tables, "organization_identifier", source=source),
            label="organization_identifier table",
        ),
        type_coding=_validate_identifier(
            _require_string(tables, "organization_type_coding", source=source),
            label="organization_type_coding table",
        ),
    )


def _load_resource_tables_location(
    data: Mapping[str, Any],
    *,
    source: Path,
) -> LocationTableNames:
    """
    Carrega os nomes físicos das tabelas de Location.
    """

    tables = data.get("table_names")
    if not isinstance(tables, Mapping):
        raise ConfigurationError(f"O bloco 'table_names' é obrigatório em {source}")

    return LocationTableNames(
        location=_validate_identifier(
            _require_string(tables, "location", source=source),
            label="location table",
        ),
        meta_profile=_validate_identifier(
            _require_string(tables, "location_meta_profile", source=source),
            label="location_meta_profile table",
        ),
        physical_type_coding=_validate_identifier(
            _require_string(tables, "location_physical_type_coding", source=source),
            label="location_physical_type_coding table",
        ),
    )


def _load_ingestion_settings(
    data: Mapping[str, Any],
    *,
    source: Path,
    root: Path,
    default_batch_size: int,
) -> tuple[str, Path, int]:
    """
    Extrai campos comuns de um YAML de ingestão.
    """

    pipeline_name = _require_string(data, "pipeline_name", source=source)
    input_path = _resolve_path(root, _require_string(data, "input_path", source=source))
    batch_size_value = data.get("batch_size", default_batch_size)
    if batch_size_value == default_batch_size:
        batch_size = default_batch_size
    elif isinstance(batch_size_value, int) and batch_size_value > 0:
        batch_size = batch_size_value
    elif isinstance(batch_size_value, str):
        try:
            parsed_batch_size = int(batch_size_value)
        except ValueError as exc:
            raise ConfigurationError(f"Campo inteiro positivo inválido em {source}: batch_size") from exc
        if parsed_batch_size <= 0:
            raise ConfigurationError(f"Campo inteiro positivo inválido em {source}: batch_size")
        batch_size = parsed_batch_size
    else:
        raise ConfigurationError(f"Campo inteiro positivo inválido em {source}: batch_size")
    return pipeline_name, input_path, batch_size


def load_project_settings(root: Path | None = None) -> ProjectSettings:
    """
    Carrega as configurações do projeto a partir de `.env` e YAMLs.

    Parâmetros:
    ----------
    root : Path | None, default = None
        Raiz do projeto.

    Retorno:
    -------
    ProjectSettings
        Configurações consolidadas.
    """

    project_dir = root or project_root()
    load_dotenv_file(project_dir / ".env")

    database_yaml_path = project_dir / "config" / "database.yaml"
    logging_yaml_path = project_dir / "config" / "logging.yaml"
    common_yaml_path = project_dir / "config" / "ingestion" / "common.yaml"
    organization_yaml_path = project_dir / "config" / "ingestion" / "organization.yaml"
    location_yaml_path = project_dir / "config" / "ingestion" / "location.yaml"

    database_yaml = load_yaml_file(database_yaml_path)
    logging_yaml = load_yaml_file(logging_yaml_path)
    common_yaml = load_yaml_file(common_yaml_path)
    organization_yaml = load_yaml_file(organization_yaml_path)
    location_yaml = load_yaml_file(location_yaml_path)

    schema_name = _validate_identifier(
        _require_string(database_yaml, "schema_name", source=database_yaml_path),
        label="schema_name",
    )

    database = DatabaseSettings(
        host=_require_string(os.environ, "POSTGRES_HOST", source=project_dir / ".env"),
        port=_require_int(os.environ, "POSTGRES_PORT", source=project_dir / ".env"),
        database=_require_string(os.environ, "POSTGRES_DB", source=project_dir / ".env"),
        user=_require_string(os.environ, "POSTGRES_USER", source=project_dir / ".env"),
        password=_require_string(os.environ, "POSTGRES_PASSWORD", source=project_dir / ".env"),
        schema_name=schema_name,
        echo=_require_bool(database_yaml, "echo", default=False, source=database_yaml_path),
        pool_pre_ping=_require_bool(
            database_yaml,
            "pool_pre_ping",
            default=True,
            source=database_yaml_path,
        ),
    )

    reset_policy = _require_string(common_yaml, "reset_policy", source=common_yaml_path)
    skip_invalid_records = _require_bool(
        common_yaml,
        "skip_invalid_records",
        default=True,
        source=common_yaml_path,
    )
    batch_size_default = _require_int(common_yaml, "batch_size", source=common_yaml_path)
    ingestion_order_raw = common_yaml.get("ingestion_order")
    if not isinstance(ingestion_order_raw, list) or not all(
        isinstance(item, str) and item.strip() for item in ingestion_order_raw
    ):
        raise ConfigurationError(f"Campo 'ingestion_order' inválido em {common_yaml_path}")
    ingestion_order = tuple(item.strip() for item in ingestion_order_raw)

    common = CommonIngestionSettings(
        reset_policy=reset_policy,
        skip_invalid_records=skip_invalid_records,
        batch_size=batch_size_default,
        ingestion_order=ingestion_order,
    )

    organization_tables = _load_resource_tables_organization(
        organization_yaml,
        source=organization_yaml_path,
    )
    organization_name, organization_input_path, organization_batch_size = _load_ingestion_settings(
        organization_yaml,
        source=organization_yaml_path,
        root=project_dir,
        default_batch_size=batch_size_default,
    )
    organization = OrganizationIngestionSettings(
        pipeline_name=organization_name,
        input_path=organization_input_path,
        batch_size=organization_batch_size,
        table_names=organization_tables,
    )

    location_tables = _load_resource_tables_location(
        location_yaml,
        source=location_yaml_path,
    )
    location_name, location_input_path, location_batch_size = _load_ingestion_settings(
        location_yaml,
        source=location_yaml_path,
        root=project_dir,
        default_batch_size=batch_size_default,
    )
    location = LocationIngestionSettings(
        pipeline_name=location_name,
        input_path=location_input_path,
        batch_size=location_batch_size,
        table_names=location_tables,
    )

    logging_settings = LoggingSettings(
        log_dir=_resolve_path(project_dir, _require_string(logging_yaml, "log_dir", source=logging_yaml_path)),
        log_file=_require_string(logging_yaml, "log_file", source=logging_yaml_path),
        level=_require_string(logging_yaml, "level", source=logging_yaml_path),
        console_enabled=_require_bool(
            logging_yaml,
            "console_enabled",
            default=True,
            source=logging_yaml_path,
        ),
        max_bytes=_require_int(logging_yaml, "max_bytes", source=logging_yaml_path),
        backup_count=_require_int(logging_yaml, "backup_count", source=logging_yaml_path),
    )

    return ProjectSettings(
        database=database,
        logging=logging_settings,
        common=common,
        organization=organization,
        location=location,
    )
