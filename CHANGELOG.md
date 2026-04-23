# Changelog

Todas as alterações relevantes deste projeto são registradas neste arquivo.
O formato segue uma linha próxima de `Keep a Changelog` e usa versionamento
semântico `X.Y.Z`.

## [0.4.0] - 2026-04-23

### Adicionado

- Suporte à ingestão dos três arquivos da fase atual:
  - `data/MimicOrganization.ndjson.gz`
  - `data/MimicLocation.ndjson.gz`
  - `data/MimicPatient.ndjson.gz`
- Pipeline orquestrada com ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
- Foreign keys essenciais mantidas:
  - `location.managing_organization_id -> organization.id`
  - `patient.managing_organization_id -> organization.id`
- Parser reutilizável para referências FHIR no formato `ResourceType/<id>`.
- Funções reutilizáveis para extração de extensões FHIR do `Patient`.
- Estratégia explícita de consolidação para listas FHIR: uso do primeiro valor válido encontrado.
- Logging estruturado em arquivo e console com rotação via `logging.handlers`.
- Testes de unidade para:
  - parser de referência FHIR
  - leitor NDJSON GZIP
  - transformers de `Organization`, `Location` e `Patient`
- Atualização do `README.md` para refletir a modelagem simplificada e o processo de execução.

### Alterado

- Simplificação do schema relacional para apenas três tabelas finais:
  - `organization`
  - `location`
  - `patient`
- Consolidação de atributos no `patient` principal:
  - `name`
  - `identifier`
  - `marital_status_coding`
  - `race`
  - `ethnicity`
  - `birthsex`
- Remoção de colunas e tabelas auxiliares não necessárias nesta fase:
  - `resourceType`
  - `active`
  - `status`
  - tabelas de `meta.profile`
  - tabelas auxiliares de `identifier`, `name`, `coding` e extensões
- Reestruturação da camada de ingestão para trabalhar com um registro principal por recurso.
- Recriação total do schema a cada execução com política padrão `drop_and_recreate`.
- Ajustes na configuração em YAML para refletir a modelagem enxuta e os novos nomes de tabela.

### Corrigido

- Validação mais robusta de referências FHIR inválidas e malformadas.
- Tratamento controlado de JSON inválido por linha no leitor NDJSON GZIP.
- Tratamento controlado de falhas de parsing e integridade durante a ingestão.

## [0.3.0] - 2026-04-22

### Adicionado

- Suporte à ingestão de `data/MimicPatient.ndjson.gz`.
- Pipeline orquestrada de recursos com ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
- Foreign key explícita entre `patient.managing_organization_id` e `organization.id`.
- Parser reutilizável para referências FHIR no formato `ResourceType/<id>`.
- Parsers explícitos para as extensões FHIR de `Patient`:
  - race
  - ethnicity
  - birthsex
- Camada central de orquestração para reset, criação de schema e execução sequencial dos recursos.
- Logging estruturado em arquivo e console com rotação, configurado em `config/logging.yaml`.
- Arquivos YAML adicionais:
  - `config/ingestion/patient.yaml`
  - `config/pipeline/resources.yaml`
- Testes de unidade com `pytest` para parser de referência, leitor NDJSON GZIP e transformers dos três recursos.
- Atualização do `README.md` com a pipeline completa, ordem de importação, logs e testes.

### Alterado

- Refatoração da arquitetura para suportar crescimento com novos recursos FHIR sem acoplamento excessivo.
- Recriação total do schema e das tabelas em cada execução, agora cobrindo `Organization`, `Location` e `Patient`.
- Ajustes na camada de logging para manter saída consistente em `logs/ingestion.log`.
- Atualização da configuração para incluir ordem oficial da pipeline e parâmetros de `Patient`.

### Corrigido

- Validação mais robusta de referências FHIR inválidas em `Location` e `Patient`.
- Tratamento de falhas de integridade durante a persistência em lote.
- Falhas de parsing de extensões de `Patient` tratadas de forma controlada.

## [0.2.0] - 2026-04-22

### Adicionado

- Suporte à ingestão de `data/MimicLocation.ndjson.gz`.
- Ordem obrigatória de ingestão:
  1. `Organization`
  2. `Location`
- Foreign key explícita entre `location.managing_organization_id` e `organization.id`.
- Parser robusto para `managingOrganization.reference` no formato FHIR `Organization/<id>`.
- Novas tabelas normalizadas para `Location`:
  - `location`
  - `location_meta_profile`
  - `location_physical_type_coding`
- Pipeline principal unificado para:
  - reset do schema;
  - criação das tabelas;
  - ingestão de `Organization`;
  - ingestão de `Location`.
- Logging em arquivo e console com rotação, configurado em `config/logging.yaml`.
- Arquivos YAML adicionais:
  - `config/ingestion/common.yaml`
  - `config/ingestion/location.yaml`
  - `config/logging.yaml`
- Atualização do `README.md` com instalação, execução, ordem de ingestão, logs e modelagem.
- Testes para o parser de referência FHIR e para a transformação de `Location`.

### Alterado

- Refatoração da configuração para suportar múltiplos recursos FHIR sem acoplamento excessivo.
- Recriação total do schema e das tabelas em cada execução, agora cobrindo os dois recursos.
- Ajustes na camada de logging para escrever em `logs/ingestion.log`.

### Corrigido

- Validação mais robusta de referências FHIR inválidas em `Location`.
- Tratamento de falhas de integridade durante a persistência em lote.

## [0.1.0] - 2026-04-22

### Adicionado

- Pipeline inicial para ingestão de `Organization`.
- Arquivo `.env` na raiz com credenciais PostgreSQL locais.
- Configuração não sensível em YAML para banco e ingestão de `Organization`.
- Leitura streaming do arquivo `data/MimicOrganization.ndjson.gz`.
- Schema relacional normalizado para `Organization`.
- Execução transacional com reset completo do schema a cada execução.
- Testes básicos para o leitor NDJSON gzip e para o transformador de `Organization`.
- Dependências mínimas para PostgreSQL, SQLAlchemy e YAML.

### Infraestrutura

- Geração do `uv.lock` para congelamento das dependências.
- Atualização do `.gitignore` para ignorar arquivos gerados e o diretório de logs.

### Execução

```bash
uv sync --extra dev
uv run python -m src.main
```
