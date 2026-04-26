"""
Testes do gerador de dicionário de dados.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy import Column, ForeignKey, MetaData, String, Table, Text, create_engine

from src.dictionary.data_dictionary_generator import generate_data_dictionary


def test_generate_data_dictionary_writes_expected_yaml_structure(tmp_path: Path) -> None:
    """
    Deve gerar YAML com metadados da tabela, PK, FK, descrições e exemplos.
    """

    engine = create_engine(f"sqlite:///{tmp_path / 'dictionary.db'}")
    metadata = MetaData()

    organization = Table(
        "organization",
        metadata,
        Column("id", String, primary_key=True),
        Column("name", Text, nullable=True),
    )
    patient = Table(
        "patient",
        metadata,
        Column("id", String, primary_key=True),
        Column("organization_id", String, ForeignKey("organization.id"), nullable=True),
        Column("status", String, nullable=False),
        Column("nickname", String, nullable=True),
        Column("notes", Text, nullable=True),
    )

    with engine.begin() as connection:
        metadata.create_all(connection)
        connection.execute(
            organization.insert(),
            [
                {"id": "org-1", "name": "Alpha"},
                {"id": "org-2", "name": "Beta"},
            ],
        )
        connection.execute(
            patient.insert(),
            [
                {
                    "id": "pat-1",
                    "organization_id": "org-1",
                    "status": "active",
                    "nickname": "Ana",
                    "notes": None,
                },
                {
                    "id": "pat-2",
                    "organization_id": "org-1",
                    "status": "completed",
                    "nickname": None,
                    "notes": None,
                },
                {
                    "id": "pat-3",
                    "organization_id": "org-2",
                    "status": "draft",
                    "nickname": "Bia",
                    "notes": None,
                },
                {
                    "id": "pat-4",
                    "organization_id": None,
                    "status": "entered-in-error",
                    "nickname": "Carla",
                    "notes": None,
                },
            ],
        )

    output_path = tmp_path / "dict" / "dicionario.yaml"
    generate_data_dictionary(
        output_path,
        engine,
        {
            "database": {
                "name": "demo_db",
                "description": "Base de teste para o gerador.",
            },
            "tables": {
                "patient": {
                    "description": "Tabela manual de pacientes.",
                    "columns": {
                        "id": "Identificador manual do paciente.",
                        "organization_id": "Organização associada ao paciente.",
                        "status": "Status clínico do paciente.",
                    },
                }
            },
            "include_examples": True,
            "max_examples_per_column": 3,
        },
    )

    payload = yaml.safe_load(output_path.read_text(encoding="utf-8"))
    assert payload["database"] == {
        "name": "demo_db",
        "description": "Base de teste para o gerador.",
    }
    assert [table["name"] for table in payload["tables"]] == ["organization", "patient"]

    organization_table = payload["tables"][0]
    assert organization_table["description"] == "Descrição não informada."
    assert organization_table["columns"][0]["primary_key"] is True
    assert organization_table["columns"][0]["required"] is True

    patient_table = payload["tables"][1]
    assert patient_table["description"] == "Tabela manual de pacientes."

    patient_columns = {column["name"]: column for column in patient_table["columns"]}
    assert patient_columns["id"]["description"] == "Identificador manual do paciente."
    assert patient_columns["id"]["primary_key"] is True
    assert patient_columns["id"]["required"] is True
    assert patient_columns["organization_id"]["foreign_key"] is True
    assert patient_columns["organization_id"]["references"] == {
        "table": "organization",
        "column": "id",
    }
    assert patient_columns["organization_id"]["required"] is False
    assert patient_columns["status"]["required"] is True
    assert patient_columns["status"]["examples"] == ["active", "completed", "draft"]
    assert patient_columns["nickname"]["description"] == "Descrição não informada."
    assert patient_columns["nickname"]["required"] is False
    assert patient_columns["notes"]["examples"] == []

