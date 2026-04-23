# nl2sql2nl_mimic_fhir

Pipeline em Python para ingerir recursos FHIR compactados em gzip no PostgreSQL local, com modelagem relacional simplificada, logging em arquivo e orquestração rígida por dependências entre recursos.

## Visão Geral

Esta fase do projeto processa exatamente três arquivos:

1. `data/MimicOrganization.ndjson.gz`
2. `data/MimicLocation.ndjson.gz`
3. `data/MimicPatient.ndjson.gz`

A ordem de importação é obrigatória:

1. `Organization`
2. `Location`
3. `Patient`

A pipeline faz reset completo do schema, recria a estrutura e ingere os dados novamente a cada execução. A implementação foi desenhada para facilitar novas fases com outros recursos FHIR, sem carregar agora tabelas auxiliares desnecessárias.

## Requisitos

- Python 3.13 ou superior
- `uv`
- PostgreSQL local acessível em `localhost:5432`
- Docker, se o banco estiver em container

## Fontes de Dados

- Download dos arquivos de ingestão: https://physionet.org/content/mimic-iv-fhir-demo/2.1.0/
- Documentação do MIMIC FHIR: https://mimic.mit.edu/fhir/index.html

## Configuração

### `.env`

As credenciais ficam somente no `.env` da raiz do projeto:

```dotenv
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app_mimic_fhir
POSTGRES_USER=app_mimic_fhir
POSTGRES_PASSWORD=app_mimic_fhir
```

### YAMLs em `config/`

As configurações não sensíveis ficam versionadas em YAML:

- `config/database.yaml`
  - schema PostgreSQL
  - flags de conexão
- `config/logging.yaml`
  - diretório de log
  - nome do arquivo
  - nível
  - rotação
- `config/ingestion/common.yaml`
  - política de reset
  - política de registros inválidos
  - batch size padrão
- `config/ingestion/organization.yaml`
  - caminho do arquivo de `Organization`
  - batch size
  - nome físico da tabela
- `config/ingestion/location.yaml`
  - caminho do arquivo de `Location`
  - batch size
  - nome físico da tabela
- `config/ingestion/patient.yaml`
  - caminho do arquivo de `Patient`
  - batch size
  - nome físico da tabela
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

Também é possível usar o atalho:

```bash
uv run python main.py
```

## Ordem Da Pipeline

A execução principal segue exatamente esta ordem:

1. reset completo do schema relacionado
2. criação das tabelas
3. ingestão de `Organization`
4. ingestão de `Location`
5. ingestão de `Patient`

## Modelagem Final

### Tabela `organization`

- `id` `PK`
- `name`

Campos ignorados nesta fase:

- `resourceType`
- `active`

Tabelas removidas:

- `organization_identifier`
- `organization_meta_profile`
- `organization_type_coding`

### Tabela `location`

- `id` `PK`
- `name`
- `managing_organization_id` `FK -> organization.id` `nullable`

Campos ignorados nesta fase:

- `resourceType`
- `status`

Tabelas removidas:

- `location_meta_profile`
- `location_physical_type_coding`

### Tabela `patient`

- `id` `PK`
- `gender`
- `birth_date`
- `name`
- `identifier`
- `marital_status_coding`
- `race`
- `ethnicity`
- `birthsex`
- `managing_organization_id` `FK -> organization.id` `nullable`

Campos ignorados nesta fase:

- `resourceType`
- `meta.profile`
- `communication.language.coding`

Tabelas removidas:

- `patient_meta_profile`
- `patient_name`
- `patient_identifier`
- `patient_communication_language_coding`
- `patient_marital_status_coding`
- `patient_race`
- `patient_ethnicity`
- `patient_birthsex`

## Estratégia De Consolidação

Quando uma estrutura FHIR contém listas, a ingestão adota sempre o **primeiro valor não vazio e válido encontrado**.

Isso vale para:

- `name[*].family`
- `identifier[*].value`
- `maritalStatus.coding[*].code`

As extensões US Core de `Patient` também foram simplificadas:

- race: `text`
- ethnicity: `text`
- birthsex: `valueCode`

Essa decisão foi implementada em código e documentada para facilitar manutenção futura.

## Relacionamentos

- `location.managing_organization_id -> organization.id`
- `patient.managing_organization_id -> organization.id`

Se a referência estiver ausente, a coluna permanece nula. Se existir, o valor precisa seguir o formato FHIR `Organization/<id>`. O parser reutilizável de referência fica em `src/ingestion/parsers/fhir_reference_parser.py`.

## Logging

O logging é salvo em arquivo e também pode ir para o console:

- diretório: `logs/`
- arquivo: `logs/ingestion.log`

O arquivo usa rotação com `logging.handlers.RotatingFileHandler`.

## Reset Total

Cada execução:

1. abre uma conexão com o PostgreSQL;
2. derruba o schema configurado;
3. recria o schema e as tabelas;
4. ingere os três recursos novamente.

O comportamento padrão é `drop_and_recreate`.

## Testes

Execute os testes de unidade com:

```bash
uv run pytest
```

Os testes cobrem:

- parser de referência FHIR
- leitor NDJSON GZIP
- transformers de `Organization`, `Location` e `Patient`

## Entrada Principal

O ponto de entrada principal é:

```bash
python -m src.main
```

## Saída Esperada

Exemplo de terminal:

```text
2026-04-23 12:00:00,000 | INFO | src.main | Logging configurado em /path/to/logs/ingestion.log
2026-04-23 12:00:00,001 | INFO | src.pipelines.ingest_all | Iniciando processo de ingestão completo com ordem: ('organization', 'location', 'patient')
2026-04-23 12:00:00,010 | INFO | src.pipelines.ingest_all | Schema resetado e tabelas criadas: mimic_fhir_ingestion
2026-04-23 12:00:01,234 | INFO | src.main | Execução concluída com sucesso: organization_lidos=... organization_inseridos=... location_lidos=... location_inseridos=... patient_lidos=... patient_inseridos=... tempo=...
```

Exemplo de log em arquivo:

```text
2026-04-23 12:00:00,001 | INFO | src.pipelines.ingest_all | Iniciando processo de ingestão completo com ordem: ('organization', 'location', 'patient')
2026-04-23 12:00:00,010 | INFO | src.pipelines.ingest_all | Schema resetado e tabelas criadas: mimic_fhir_ingestion
2026-04-23 12:00:00,020 | INFO | src.pipelines.base_resource_pipeline | Processando arquivo /path/to/data/MimicOrganization.ndjson.gz para recurso Organization
2026-04-23 12:00:00,030 | INFO | src.pipelines.base_resource_pipeline | Resumo Organization: lidos=... inseridos=... ignorados=... tempo=... tabelas={'organization': ...}
```

## Evolução Futura

A base ficou preparada para incorporar novos recursos FHIR em fases posteriores sem reintroduzir, por padrão, tabelas auxiliares que não tragam ganho analítico imediato.
