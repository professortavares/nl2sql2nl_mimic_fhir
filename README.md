# nl2sql2nl_mimic_fhir

Pipeline em Python para ingerir o arquivo `data/MimicOrganization.ndjson.gz` em PostgreSQL local, com modelagem relacional normalizada para recursos FHIR `Organization`.

## Visão geral

Este projeto foi estruturado para servir como base de ingestões FHIR futuras. A implementação atual:

- lê o arquivo `MimicOrganization.ndjson.gz` linha a linha;
- valida os registros de forma mínima;
- recria o schema e as tabelas a cada execução;
- persiste os dados em PostgreSQL de forma transacional;
- separa configuração, schema, leitura, transformação, carga e orquestração em módulos distintos;
- registra logs claros e um resumo final da execução.

## Requisitos

- Python 3.13 ou superior
- `uv`
- PostgreSQL local acessível em `localhost:5432`
- Docker, se você estiver subindo o banco por container

## Estrutura principal

- `.env`: credenciais de conexão com o PostgreSQL
- `config/database.yaml`: configurações não sensíveis do banco
- `config/ingestion/organization.yaml`: configurações do pipeline
- `src/`: código-fonte da ingestão
- `data/MimicOrganization.ndjson.gz`: arquivo de entrada

## Instalação

1. Instale as dependências do projeto:

   ```bash
   uv sync --extra dev
   ```

2. Verifique se o arquivo `.env` existe na raiz do projeto com estas variáveis:

   ```dotenv
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=app_mimic_fhir
   POSTGRES_USER=app_mimic_fhir
   POSTGRES_PASSWORD=app_mimic_fhir
   ```

3. Confirme que o arquivo de entrada existe:

   ```text
   data/MimicOrganization.ndjson.gz
   ```

## Execução

Execute a ingestão com:

```bash
uv run python -m src.main
```

Também é possível usar o atalho:

```bash
uv run python main.py
```

O pipeline vai:

1. abrir conexão com o PostgreSQL;
2. destruir o schema de ingestão configurado;
3. recriar a estrutura de tabelas;
4. ler o NDJSON gzip linha a linha;
5. transformar os recursos `Organization`;
6. inserir os dados em lote dentro de uma transação;
7. exibir um resumo final no terminal.

## Modelagem adotada

O recurso `Organization` foi dividido em tabelas normalizadas:

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

Essa abordagem evita persistir tudo como JSON bruto e preserva a estrutura repetida do FHIR de maneira relacional.

## Configuração

As configurações não sensíveis ficam em YAML:

- `config/database.yaml`
  - nome do schema PostgreSQL
  - flags de conexão
- `config/ingestion/organization.yaml`
  - nome do pipeline
  - caminho padrão do arquivo de entrada
  - tamanho do batch
  - política de reset
  - nomes das tabelas

As credenciais ficam exclusivamente no `.env`.

## Dependências

Dependências principais:

- `sqlalchemy`
- `psycopg[binary]`
- `pyyaml`

Dependência opcional de desenvolvimento:

- `ruff`

## Saída esperada

Exemplo de execução bem-sucedida:

```text
2026-04-22 ... | INFO | src.pipelines.ingest_organization | Iniciando ingestão ingest_organization para o arquivo .../data/MimicOrganization.ndjson.gz
2026-04-22 ... | INFO | src.pipelines.ingest_organization | Lote final persistido: organizations=1 meta_profiles=1 identifiers=1 type_codings=1
2026-04-22 ... | INFO | src.pipelines.ingest_organization | Resumo: lidos=1 inseridos=1 ignorados=0 tempo=0.05s tabelas=organization, organization_meta_profile, organization_identifier, organization_type_coding
2026-04-22 ... | INFO | __main__ | Execução concluída com sucesso: pipeline=ingest_organization registros_lidos=1 registros_inseridos=1 tempo=0.05s
```

## Validação local

Você pode verificar a qualidade do código com:

```bash
uv run ruff check .
uv run python -m unittest discover -s tests -v
```

## Troubleshooting

- Se a execução falhar por conexão, verifique se o PostgreSQL está ativo e escutando em `localhost:5432`.
- Se o arquivo de entrada não for encontrado, confirme o caminho `data/MimicOrganization.ndjson.gz`.
- Se o `schema_name` ou nomes de tabelas forem alterados, mantenha identificadores válidos para PostgreSQL.

## Próximos passos

A base atual foi desenhada para facilitar novas ingestões FHIR com o mesmo padrão:

- criar um novo YAML em `config/ingestion/`;
- reutilizar a camada de conexão e schema;
- implementar um novo transformer e loader;
- adicionar um novo pipeline em `src/pipelines/`.

