# Changelog

## 2026-04-22

### Adicionado

- Criação do arquivo `.env` na raiz do projeto com as credenciais PostgreSQL locais exigidas para a ingestão.
- Criação dos YAMLs de configuração não sensível:
  - `config/database.yaml`
  - `config/ingestion/organization.yaml`
- Implementação de uma base modular em `src/` para ingestão do recurso FHIR `Organization`.
- Leitura incremental do arquivo `data/MimicOrganization.ndjson.gz` linha a linha, sem carregamento integral em memória.
- Validação mínima dos registros:
  - `resourceType` deve ser `Organization`
  - `id` é obrigatório
  - `active`, quando presente, deve ser booleano
- Criação e recriação explícita do schema PostgreSQL a cada execução, com política padrão `drop_and_recreate`.
- Persistência transacional com rollback automático em caso de falha.
- Logging de progresso por lote e resumo final da execução.
- Separação por camadas:
  - configuração
  - conexão com banco
  - definição de schema
  - leitura
  - transformação
  - carga
  - pipeline
  - entrada principal
- Adição das dependências mínimas necessárias no `pyproject.toml`:
  - `sqlalchemy`
  - `psycopg[binary]`
  - `pyyaml`
  - `ruff` como dependência opcional de desenvolvimento

### Modelagem

- Mantida a tabela principal `organization` com os campos base do recurso.
- Criadas tabelas normalizadas separadas para estruturas repetidas:
  - `organization_meta_profile`
  - `organization_identifier`
  - `organization_type_coding`
- A modelagem evita JSON bruto como persistência principal e preserva a repetição natural das listas FHIR.

### Execução

1. Instalar dependências:

   ```bash
   uv sync --extra dev
   ```

2. Executar a ingestão:

   ```bash
   uv run python -m src.main
   ```

3. Opcionalmente, executar o atalho:

   ```bash
   uv run python main.py
   ```

### Observações

- O comportamento padrão é destruir e recriar o schema/tabelas a cada execução.
- O caminho de entrada padrão é `data/MimicOrganization.ndjson.gz`.
- A implementação foi desenhada para servir de base para novos pipelines FHIR no mesmo padrão modular.

