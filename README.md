# nl2sql2nl_mimic_fhir

Pipeline em Python para ingerir recursos FHIR compactados em gzip no PostgreSQL local, com modelagem relacional normalizada, logging em arquivo e orquestração por dependências entre recursos.

## Visão geral

Esta base processa agora três arquivos FHIR:

1. `data/MimicOrganization.ndjson.gz`
2. `data/MimicLocation.ndjson.gz`
3. `data/MimicPatient.ndjson.gz`

A ordem de importação é obrigatória:

1. `Organization`
2. `Location`
3. `Patient`

O pipeline foi desenhado para crescer com novos recursos FHIR no futuro, preservando separação entre leitura, transformação, carga, schema e orquestração.

## Requisitos

- Python 3.13 ou superior
- `uv`
- PostgreSQL local acessível em `localhost:5432`
- Docker, se o banco estiver sendo executado em container

## Fontes de dados e documentação

- Download dos arquivos de ingestão: https://physionet.org/content/mimic-iv-fhir-demo/2.1.0/
- Documentação do MIMIC FHIR: https://mimic.mit.edu/fhir/index.html

## Configuração

### `.env`

As credenciais ficam apenas no `.env` da raiz do projeto:

```dotenv
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app_mimic_fhir
POSTGRES_USER=app_mimic_fhir
POSTGRES_PASSWORD=app_mimic_fhir
```

Também existe um template sem valores em [`.env.example`](/home/leonardo/Documentos/github/nl2sql2nl_mimic_fhir/.env.example).

### YAMLs em `config/`

Configurações não sensíveis ficam em YAML:

- `config/database.yaml`
  - schema PostgreSQL
  - flags de conexão
- `config/logging.yaml`
  - diretório de log
  - arquivo de log
  - nível
  - rotação
- `config/ingestion/common.yaml`
  - política de reset
  - política de registros inválidos
  - batch size padrão
- `config/ingestion/organization.yaml`
  - caminho do arquivo de `Organization`
  - batch size
  - nomes das tabelas de `Organization`
- `config/ingestion/location.yaml`
  - caminho do arquivo de `Location`
  - batch size
  - nomes das tabelas de `Location`
- `config/ingestion/patient.yaml`
  - caminho do arquivo de `Patient`
  - batch size
  - nomes das tabelas de `Patient`
- `config/pipeline/resources.yaml`
  - ordem oficial da pipeline

## Instalação

Instale as dependências com:

```bash
uv sync --extra dev
```

## Execução

Execute a pipeline completa com:

```bash
uv run python -m src.main
```

Também é possível usar:

```bash
uv run python main.py
```

## Ordem de importação

A execução principal segue esta ordem:

1. reset completo do schema relacionado
2. criação das tabelas
3. ingestão de `Organization`
4. ingestão de `Location`
5. ingestão de `Patient`

Essa ordem é rígida porque:

- `Location.managing_organization_id` aponta para `organization.id`
- `Patient.managing_organization_id` aponta para `organization.id`

## Modelagem

### Organization

- `organization`
  - `id`
  - `resource_type`
  - `active`
  - `name`
- `organization_meta_profile`
  - `organization_id`
  - `profile`
- `organization_identifier`
  - `organization_id`
  - `system`
  - `value`
- `organization_type_coding`
  - `organization_id`
  - `system`
  - `code`
  - `display`

### Location

- `location`
  - `id`
  - `resource_type`
  - `name`
  - `status`
  - `managing_organization_id`
- `location_meta_profile`
  - `location_id`
  - `profile`
- `location_physical_type_coding`
  - `location_id`
  - `system`
  - `code`
  - `display`

### Patient

- `patient`
  - `id`
  - `resource_type`
  - `gender`
  - `birth_date`
  - `managing_organization_id`
- `patient_meta_profile`
  - `patient_id`
  - `profile`
- `patient_name`
  - `patient_id`
  - `use`
  - `family`
- `patient_identifier`
  - `patient_id`
  - `system`
  - `value`
- `patient_communication_language_coding`
  - `patient_id`
  - `system`
  - `code`
- `patient_marital_status_coding`
  - `patient_id`
  - `system`
  - `code`
- `patient_race`
  - `patient_id`
  - `omb_category_system`
  - `omb_category_code`
  - `omb_category_display`
  - `text`
- `patient_ethnicity`
  - `patient_id`
  - `omb_category_system`
  - `omb_category_code`
  - `omb_category_display`
  - `text`
- `patient_birthsex`
  - `patient_id`
  - `value_code`

O parser de `managingOrganization.reference` aceita o formato FHIR `Organization/<id>` e extrai o identificador para persistência relacional. As extensões de `Patient` são extraídas explicitamente para tabelas normalizadas.

## Logging

O logging é salvo em arquivo e também pode ir para o console:

- diretório: `logs/`
- arquivo: `logs/ingestion.log`

O arquivo é rotacionado usando a biblioteca padrão `logging.handlers`.

## Reset total

Cada execução:

1. abre uma conexão com o PostgreSQL;
2. derruba o schema configurado;
3. recria o schema e todas as tabelas;
4. insere os dados novamente.

O comportamento padrão é `drop_and_recreate`.

## Saída esperada

Exemplo de terminal:

```text
2026-04-22 ... | INFO | __main__ | Logging configurado em .../logs/ingestion.log
2026-04-22 ... | INFO | src.pipelines.ingest_all | Iniciando processo de ingestão completo.
2026-04-22 ... | INFO | src.pipelines.ingest_all | Ordem da pipeline: ('organization', 'location', 'patient')
2026-04-22 ... | INFO | src.pipelines.ingest_all | Schema resetado e tabelas criadas: mimic_fhir_ingestion
2026-04-22 ... | INFO | src.pipelines.base_resource_pipeline | Processando arquivo .../data/MimicOrganization.ndjson.gz para recurso Organization
2026-04-22 ... | INFO | src.pipelines.base_resource_pipeline | Resumo Organization: lidos=1 inseridos=1 ignorados=0 tempo=0.00s
2026-04-22 ... | INFO | src.pipelines.base_resource_pipeline | Processando arquivo .../data/MimicLocation.ndjson.gz para recurso Location
2026-04-22 ... | INFO | src.pipelines.base_resource_pipeline | Resumo Location: lidos=31 inseridos=31 ignorados=0 tempo=0.01s
2026-04-22 ... | INFO | src.pipelines.base_resource_pipeline | Processando arquivo .../data/MimicPatient.ndjson.gz para recurso Patient
2026-04-22 ... | INFO | src.pipelines.base_resource_pipeline | Resumo Patient: lidos=100 inseridos=100 ignorados=0 tempo=0.02s
2026-04-22 ... | INFO | src.pipelines.ingest_all | Resumo final: ordem=('organization', 'location', 'patient') tempo=0.11s tabelas=organization, organization_meta_profile, organization_identifier, organization_type_coding, location, location_meta_profile, location_physical_type_coding, patient, patient_meta_profile, patient_name, patient_identifier, patient_communication_language_coding, patient_marital_status_coding, patient_race, patient_ethnicity, patient_birthsex
```

## Validação local

Os testes de unidade ficam organizados em `tests/unit/`.

Execute os testes de unidade com:

```bash
uv run pytest
```

Também é possível rodar checagem estática:

```bash
uv run ruff check .
```

## Próximos passos

A base foi desenhada para facilitar novas ingestões FHIR:

- criar um YAML por novo recurso;
- adicionar transformer e loader específicos;
- ligar tudo em um pipeline novo;
- incluir o recurso na ordem de ingestão quando houver dependência.
