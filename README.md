# nl2sql2nl_mimic_fhir

Pipeline em Python para ingerir recursos FHIR compactados em gzip no PostgreSQL local, com modelagem relacional simplificada, orquestração rígida por dependências entre recursos e logging em arquivo.

## Objetivo do projeto

Construir uma base relacional enxuta a partir de dados FHIR/MIMIC-FHIR, preservando os campos analiticamente úteis e oferecendo uma interface Streamlit para explorar a timeline clínica de pacientes.

## Instalação

Pré-requisitos:

- Python 3.13 ou superior
- `uv`

Instale as dependências com:

```bash
uv sync --extra dev
```

## Execução

### Ingestão

Execute a pipeline completa com:

```bash
uv run python -m src.main
```

Ou, se preferir:

```bash
python -m src.main
```

### Streamlit

Execute a interface web com:

```bash
uv run streamlit run src/app/streamlit_app.py
```

## Documentação complementar

- [Documentação de ingestão](docs/ingestao.md)
- [Documentação da interface Streamlit](docs/streamlit.md)
