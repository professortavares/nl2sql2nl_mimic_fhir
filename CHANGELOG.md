# Changelog

## 2026-04-22

### Organização inicial

- Criação do pipeline inicial para `Organization`.
- Criação do arquivo `.env` na raiz com credenciais PostgreSQL locais.
- Criação de configuração não sensível em YAML para banco e ingestão de `Organization`.
- Implementação de leitura streaming do arquivo `data/MimicOrganization.ndjson.gz`.
- Criação do schema relacional normalizado para `Organization`.
- Criação de execução transacional com reset completo do schema a cada run.
- Adição de testes básicos para leitor e transformador de `Organization`.

### Expansão para Location

- Suporte à ingestão de `data/MimicLocation.ndjson.gz`.
- Ordem obrigatória de ingestão consolidada:
  1. `Organization`
  2. `Location`
- Criação de foreign key explícita de `location.managing_organization_id` para `organization.id`.
- Implementação do parser robusto para `managingOrganization.reference` no formato `Organization/<id>`.
- Criação das tabelas normalizadas de `Location`:
  - `location`
  - `location_meta_profile`
  - `location_physical_type_coding`
- Refatoração da orquestração para um pipeline principal único que:
  - reseta o schema;
  - cria as tabelas;
  - ingere `Organization`;
  - ingere `Location`.
- Criação de logging em arquivo e console com rotação, configurado em `config/logging.yaml`.
- Criação dos YAMLs adicionais:
  - `config/ingestion/common.yaml`
  - `config/ingestion/location.yaml`
  - `config/logging.yaml`
- Atualização do `README.md` com instruções de instalação, execução, ordem de ingestão, logs e modelagem.
- Inclusão de testes para o parser de referência FHIR e transformação de `Location`.

### Dependências e infraestrutura

- Manutenção do stack leve com:
  - `sqlalchemy`
  - `psycopg[binary]`
  - `pyyaml`
- Geração/atualização do `uv.lock` para congelar versões compatíveis.
- Atualização do `.gitignore` para excluir a pasta `logs/`.

### Execução

```bash
uv sync --extra dev
uv run python -m src.main
```

### Resultado validado

- `Organization` carregado com 1 registro principal.
- `Location` carregado com 31 registros principais.
- As tabelas dependentes foram persistidas corretamente dentro da mesma transação.

