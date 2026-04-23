# nl2sql2nl_mimic_fhir

Pipeline em Python para ingerir recursos FHIR compactados em gzip no PostgreSQL local, com modelagem relacional simplificada, logging em arquivo e orquestração rígida por dependências entre recursos.

## Visão Geral

O projeto está organizado em fases de ingestão.

### Fase 1

Arquivos já suportados:

1. `data/MimicOrganization.ndjson.gz`
2. `data/MimicLocation.ndjson.gz`
3. `data/MimicPatient.ndjson.gz`

### Fase 2

Novo arquivo suportado nesta entrega:

4. `data/MimicEncounter.ndjson.gz`

A ordem de importação é obrigatória:

1. `Organization`
2. `Location`
3. `Patient`
4. `Encounter`

A pipeline faz reset completo do schema, recria a estrutura e ingere os dados novamente a cada execução. O desenho continua preparado para novas fases sem exigir acoplamento excessivo entre recursos.

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
- `config/ingestion/encounter.yaml`
  - caminho do arquivo de `Encounter`
  - batch size
  - nome físico da tabela principal
  - nome físico da tabela auxiliar de localizações
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
6. ingestão de `Encounter`

## Modelagem Final

### Tabela `organization`

- `id` `PK`
- `name`

### Tabela `location`

- `id` `PK`
- `name`
- `managing_organization_id` `FK -> organization.id` `nullable`

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

### Tabela `encounter`

- `id` `PK`
- `patient_id` `FK -> patient.id` `nullable`
- `organization_id` `FK -> organization.id` `nullable`
- `status`
- `class_code`
- `start_date`
- `end_date`
- `priority_code`
- `service_type_code`
- `admit_source_code`
- `discharge_disposition_code`
- `identifier`

### Tabela `encounter_location`

- `encounter_id` `FK -> encounter.id`
- `location_id` `FK -> location.id` `nullable`
- `start_date`
- `end_date`

## Estratégia De Consolidação

Quando uma estrutura FHIR contém listas, a ingestão adota sempre o **primeiro valor não vazio e válido encontrado**.

Isso vale para:

- `name[*].family`
- `identifier[*].value`
- `maritalStatus.coding[*].code`
- `priority.coding[*].code`
- `serviceType.coding[*].code`
- `location[*].location.reference`

As extensões US Core de `Patient` também foram simplificadas:

- race: `text`
- ethnicity: `text`
- birthsex: `valueCode`

No `Encounter`, a referência `serviceProvider.reference` é usada como fonte preferencial para `organization_id`. O campo `identifier[*].assigner.reference` é observado no dado, mas não é materializado nesta fase.

## Relacionamentos

- `location.managing_organization_id -> organization.id`
- `patient.managing_organization_id -> organization.id`
- `encounter.patient_id -> patient.id`
- `encounter.organization_id -> organization.id`
- `encounter_location.encounter_id -> encounter.id`
- `encounter_location.location_id -> location.id`

Se a referência estiver ausente, a coluna permanece nula quando isso fizer sentido. Se existir, o valor precisa seguir o formato FHIR correto. O parser reutilizável de referências fica em `src/ingestion/parsers/fhir_reference_parser.py`.

O diagrama ASCII das relações está documentado em [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md).

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
4. ingere os recursos novamente.

O comportamento padrão é `drop_and_recreate`.

## Testes

Execute os testes de unidade com:

```bash
uv run pytest
```

Os testes cobrem:

- parser de referência FHIR
- leitor NDJSON GZIP
- transformers de `Organization`, `Location`, `Patient` e `Encounter`

## Entrada Principal

O ponto de entrada principal é:

```bash
python -m src.main
```

## Saída Esperada

Exemplo de terminal:

```text
2026-04-23 12:00:00,000 | INFO | src.main | Logging configurado em /path/to/logs/ingestion.log
2026-04-23 12:00:00,001 | INFO | src.pipelines.ingest_all | Iniciando processo de ingestão completo com ordem: ('organization', 'location', 'patient', 'encounter')
2026-04-23 12:00:00,010 | INFO | src.pipelines.ingest_all | Schema resetado e tabelas criadas: mimic_fhir_ingestion
2026-04-23 12:00:01,234 | INFO | src.main | Execução concluída com sucesso: organization_lidos=... organization_inseridos=... location_lidos=... location_inseridos=... patient_lidos=... patient_inseridos=... encounter_lidos=... encounter_inseridos=... tempo=...
```

Exemplo de log em arquivo:

```text
2026-04-23 12:00:00,001 | INFO | src.pipelines.ingest_all | Iniciando processo de ingestão completo com ordem: ('organization', 'location', 'patient', 'encounter')
2026-04-23 12:00:00,010 | INFO | src.pipelines.ingest_all | Schema resetado e tabelas criadas: mimic_fhir_ingestion
2026-04-23 12:00:00,020 | INFO | src.pipelines.base_resource_pipeline | Processando arquivo /path/to/data/MimicOrganization.ndjson.gz para recurso Organization
2026-04-23 12:00:00,030 | INFO | src.pipelines.base_resource_pipeline | Resumo Encounter: lidos=... inseridos=... ignorados=... tempo=... tabelas={'encounter': ..., 'encounter_location': ...}
```

## Evolução Futura

A base ficou preparada para incorporar novos recursos FHIR em fases posteriores sem reintroduzir, por padrão, tabelas auxiliares que não tragam ganho analítico imediato.
