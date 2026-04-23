# nl2sql2nl_mimic_fhir

Pipeline em Python para ingerir recursos FHIR compactados em gzip no PostgreSQL local, com modelagem relacional normalizada e carga em ordem dependente.

## Visão geral

Esta base atualmente processa dois arquivos FHIR:

1. `data/MimicOrganization.ndjson.gz`
2. `data/MimicLocation.ndjson.gz`

A ordem de importação é obrigatória:

1. `Organization`
2. `Location`

O recurso `Location` referencia `Organization` por meio de `managingOrganization.reference`, então a pipeline cria a foreign key correspondente e carrega os dados na ordem correta dentro da mesma transação.

## Requisitos

- Python 3.13 ou superior
- `uv`
- PostgreSQL local acessível em `localhost:5432`
- Docker, se o banco estiver sendo executado em container

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
  - ordem de ingestão
- `config/ingestion/organization.yaml`
  - caminho do arquivo de Organization
  - batch size
  - nomes das tabelas de Organization
- `config/ingestion/location.yaml`
  - caminho do arquivo de Location
  - batch size
  - nomes das tabelas de Location

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

Essa ordem é rígida porque `Location.managing_organization_id` aponta para `organization.id`.

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

O parser de `managingOrganization.reference` aceita o formato FHIR `Organization/<id>` e extrai o identificador para persistência relacional.

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
2026-04-22 ... | INFO | src.pipelines.ingest_all | Schema resetado e tabelas criadas: mimic_fhir_ingestion
2026-04-22 ... | INFO | src.pipelines.base | Processando arquivo .../data/MimicOrganization.ndjson.gz para recurso Organization
2026-04-22 ... | INFO | src.pipelines.base | Resumo Organization: lidos=1 inseridos=1 ignorados=0 tempo=0.00s
2026-04-22 ... | INFO | src.pipelines.base | Processando arquivo .../data/MimicLocation.ndjson.gz para recurso Location
2026-04-22 ... | INFO | src.pipelines.base | Resumo Location: lidos=31 inseridos=31 ignorados=0 tempo=0.01s
2026-04-22 ... | INFO | src.pipelines.ingest_all | Resumo final: organization_lidos=1 organization_inseridos=1 location_lidos=31 location_inseridos=31 tempo=0.06s tabelas=organization, organization_meta_profile, organization_identifier, organization_type_coding, location, location_meta_profile, location_physical_type_coding
```

## Validação local

```bash
uv run ruff check .
uv run python -m unittest discover -s tests -v
```

## Próximos passos

A base foi desenhada para facilitar novas ingestões FHIR:

- criar um YAML por novo recurso;
- adicionar transformer e loader específicos;
- ligar tudo em um pipeline novo;
- incluir o recurso na ordem de ingestão quando houver dependência.

