# Changelog

Todas as alterações relevantes deste projeto são registradas neste arquivo.
O formato segue uma linha próxima de `Keep a Changelog` e usa versionamento
semântico `X.Y.Z`.

## [0.3.0] - 2026-04-22

### Adicionado

- Suporte à ingestão de `data/MimicPatient.ndjson.gz`.
- Pipeline orquestrada de recursos com ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
- Foreign key explícita entre `patient.managing_organization_id` e `organization.id`.
- Novas tabelas normalizadas para `Patient`:
  - `patient`
  - `patient_meta_profile`
  - `patient_name`
  - `patient_identifier`
  - `patient_communication_language_coding`
  - `patient_marital_status_coding`
  - `patient_race`
  - `patient_ethnicity`
  - `patient_birthsex`
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
- Falhas de parsing de extensões de `Patient` agora são tratadas de forma controlada.

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

