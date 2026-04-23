"""
Leitura e validação das configurações da aplicação.

Este módulo concentra a leitura do arquivo `.env` e dos YAMLs não sensíveis,
mantendo credenciais fora do código-fonte e permitindo ajustes de pipeline sem
alterar a implementação.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class ConfigurationError(ValueError):
    """Indica que uma configuração obrigatória está ausente ou inválida."""


@dataclass(slots=True, frozen=True)
class DatabaseSettings:
    """Configuração de conexão e comportamento do banco de dados."""

    host: str
    port: int
    database: str
    user: str
    password: str
    schema_name: str
    echo: bool = False
    pool_pre_ping: bool = True


@dataclass(slots=True, frozen=True)
class TableNames:
    """Nomes físicos das tabelas usadas pelo pipeline de Organization."""

    organization: str
    organization_meta_profile: str
    organization_identifier: str
    organization_type_coding: str


@dataclass(slots=True, frozen=True)
class OrganizationIngestionSettings:
    """Configurações do pipeline de ingestão de Organization."""

    pipeline_name: str
    input_path: Path
    batch_size: int
    reset_policy: str
    skip_invalid_records: bool
    table_names: TableNames


@dataclass(slots=True, frozen=True)
class ProjectSettings:
    """Agrupamento das configurações da aplicação."""

    database: DatabaseSettings
    organization: OrganizationIngestionSettings


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
    Carrega variáveis de ambiente a partir de um arquivo `.env` simples.

    Parâmetros:
    ----------
    path : Path
        Caminho para o arquivo `.env`.

    Exceções:
    --------
    FileNotFoundError
        Quando o arquivo não existe.
    ConfigurationError
        Quando o formato de uma linha é inválido.
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


def load_yaml_file(path: Path) -> dict[str, Any]:
    """
    Lê um arquivo YAML e retorna seu conteúdo como dicionário.

    Parâmetros:
    ----------
    path : Path
        Caminho do arquivo YAML.

    Retorno:
    -------
    dict[str, Any]
        Conteúdo carregado.

    Exceções:
    --------
    FileNotFoundError
        Quando o arquivo não existe.
    ConfigurationError
        Quando o conteúdo não é um mapeamento YAML válido.
    """

    if not path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path}")

    content = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(content, dict):
        raise ConfigurationError(f"O arquivo YAML deve conter um mapeamento: {path}")
    return content


def _require_string(data: Mapping[str, Any], key: str, *, source: Path) -> str:
    """
    Obtém uma string obrigatória de um mapeamento.

    Parâmetros:
    ----------
    data : Mapping[str, Any]
        Mapeamento de origem.
    key : str
        Chave esperada.
    source : Path
        Arquivo de origem usado nas mensagens de erro.

    Retorno:
    -------
    str
        Valor encontrado e validado.
    """

    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"Campo obrigatório ausente ou inválido em {source}: {key}")
    return value.strip()


def _require_bool(data: Mapping[str, Any], key: str, *, default: bool, source: Path) -> bool:
    """
    Obtém um booleano opcional de um mapeamento.

    Parâmetros:
    ----------
    data : Mapping[str, Any]
        Mapeamento de origem.
    key : str
        Chave esperada.
    default : bool
        Valor padrão caso a chave não exista.
    source : Path
        Arquivo de origem usado nas mensagens de erro.
    """

    value = data.get(key, default)
    if isinstance(value, bool):
        return value
    raise ConfigurationError(f"Campo booleano inválido em {source}: {key}")


def _require_int(data: Mapping[str, Any], key: str, *, source: Path) -> int:
    """
    Obtém um inteiro obrigatório de um mapeamento.

    Parâmetros:
    ----------
    data : Mapping[str, Any]
        Mapeamento de origem.
    key : str
        Chave esperada.
    source : Path
        Arquivo de origem usado nas mensagens de erro.
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

    Parâmetros:
    ----------
    name : str
        Nome do identificador.
    label : str
        Rótulo usado na mensagem de erro.

    Retorno:
    -------
    str
        Identificador validado.
    """

    if not _IDENTIFIER_PATTERN.fullmatch(name):
        raise ConfigurationError(f"{label} inválido: {name!r}")
    return name


def load_project_settings(root: Path | None = None) -> ProjectSettings:
    """
    Carrega as configurações do projeto a partir de `.env` e YAML.

    Parâmetros:
    ----------
    root : Path | None, default = None
        Raiz do projeto. Quando omitida, a função descobre a raiz a partir do
        próprio módulo.

    Retorno:
    -------
    ProjectSettings
        Configurações consolidadas.

    Exceções:
    --------
    FileNotFoundError
        Quando `.env` ou os YAMLs não existem.
    ConfigurationError
        Quando algum campo obrigatório estiver ausente ou inválido.
    """

    project_dir = root or project_root()
    load_dotenv_file(project_dir / ".env")

    database_yaml_path = project_dir / "config" / "database.yaml"
    organization_yaml_path = project_dir / "config" / "ingestion" / "organization.yaml"

    database_yaml = load_yaml_file(database_yaml_path)
    organization_yaml = load_yaml_file(organization_yaml_path)

    database = DatabaseSettings(
        host=_require_string(os.environ, "POSTGRES_HOST", source=project_dir / ".env"),
        port=_require_int(os.environ, "POSTGRES_PORT", source=project_dir / ".env"),
        database=_require_string(os.environ, "POSTGRES_DB", source=project_dir / ".env"),
        user=_require_string(os.environ, "POSTGRES_USER", source=project_dir / ".env"),
        password=_require_string(os.environ, "POSTGRES_PASSWORD", source=project_dir / ".env"),
        schema_name=_validate_identifier(
            _require_string(database_yaml, "schema_name", source=database_yaml_path),
            label="schema_name",
        ),
        echo=_require_bool(database_yaml, "echo", default=False, source=database_yaml_path),
        pool_pre_ping=_require_bool(
            database_yaml,
            "pool_pre_ping",
            default=True,
            source=database_yaml_path,
        ),
    )

    table_names_data = organization_yaml.get("table_names")
    if not isinstance(table_names_data, dict):
        raise ConfigurationError(
            f"O bloco 'table_names' é obrigatório em {organization_yaml_path}"
        )

    table_names = TableNames(
        organization=_validate_identifier(
            _require_string(table_names_data, "organization", source=organization_yaml_path),
            label="organization table",
        ),
        organization_meta_profile=_validate_identifier(
            _require_string(
                table_names_data,
                "organization_meta_profile",
                source=organization_yaml_path,
            ),
            label="organization_meta_profile table",
        ),
        organization_identifier=_validate_identifier(
            _require_string(
                table_names_data,
                "organization_identifier",
                source=organization_yaml_path,
            ),
            label="organization_identifier table",
        ),
        organization_type_coding=_validate_identifier(
            _require_string(
                table_names_data,
                "organization_type_coding",
                source=organization_yaml_path,
            ),
            label="organization_type_coding table",
        ),
    )

    input_path = _require_string(organization_yaml, "input_path", source=organization_yaml_path)
    resolved_input_path = Path(input_path)
    if not resolved_input_path.is_absolute():
        resolved_input_path = (project_dir / resolved_input_path).resolve()

    organization = OrganizationIngestionSettings(
        pipeline_name=_require_string(
            organization_yaml,
            "pipeline_name",
            source=organization_yaml_path,
        ),
        input_path=resolved_input_path,
        batch_size=_require_int(organization_yaml, "batch_size", source=organization_yaml_path),
        reset_policy=_require_string(
            organization_yaml,
            "reset_policy",
            source=organization_yaml_path,
        ),
        skip_invalid_records=_require_bool(
            organization_yaml,
            "skip_invalid_records",
            default=True,
            source=organization_yaml_path,
        ),
        table_names=table_names,
    )

    return ProjectSettings(database=database, organization=organization)
