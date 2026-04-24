# nl2sql2nl_mimic_fhir

Pipeline em Python para ingerir recursos FHIR compactados em gzip no PostgreSQL local, com modelagem relacional simplificada, orquestração rígida por dependências entre recursos e logging em arquivo.

## Visão Geral

O projeto trabalha em fases de ingestão. Cada execução faz `drop_and_recreate` do schema, recria as tabelas e reinsere os dados do zero.

### Fase 1

1. `MimicOrganization.ndjson.gz`
2. `MimicLocation.ndjson.gz`
3. `MimicPatient.ndjson.gz`

### Fase 2

4. `MimicEncounter.ndjson.gz`
5. `MimicEncounterED.ndjson.gz`
6. `MimicEncounterICU.ndjson.gz`

### Fase 3

7. `MimicMedication.ndjson.gz`
8. `MimicMedicationMix.ndjson.gz`
9. `MimicMedicationRequest.ndjson.gz`

### Fase 4

10. `MimicSpecimen.ndjson.gz`

### Fase 5

11. `MimicCondition.ndjson.gz`
12. `MimicConditionED.ndjson.gz`

### Ordem obrigatória da pipeline

1. reset completo do schema
2. criação das tabelas
3. ingestão de `Organization`
4. ingestão de `Location`
5. ingestão de `Patient`
6. ingestão de `Encounter`
7. ingestão de `EncounterED`
8. ingestão de `EncounterICU`
9. ingestão de `Medication`
10. ingestão de `MedicationMix`
11. ingestão de `MedicationRequest`
12. ingestão de `Specimen`
13. ingestão de `Condition`
14. ingestão de `ConditionED`

## Pré-requisitos

- Python 3.13 ou superior
- `uv`
- PostgreSQL local acessível em `localhost:5432`
- Docker, se o banco estiver em container

## Configuração do Banco

As credenciais ficam somente no arquivo `.env` da raiz do projeto:

```dotenv
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app_mimic_fhir
POSTGRES_USER=app_mimic_fhir
POSTGRES_PASSWORD=app_mimic_fhir
```

As demais configurações não sensíveis ficam em YAML dentro de `./config`.

## Configuração em `./config`

- `config/database.yaml`
  - nome do schema
  - flags de conexão
- `config/logging.yaml`
  - diretório de log
  - nome do arquivo de log
  - nível
  - rotação
- `config/ingestion/common.yaml`
  - política de reset
  - política para registros inválidos
  - batch size padrão
- `config/ingestion/organization.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/location.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/patient.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/encounter.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela principal
  - nome da tabela auxiliar de localizações
- `config/ingestion/encounter_ed.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/encounter_icu.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela principal
  - nome da tabela auxiliar de localizações
- `config/ingestion/medication.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/medication_mix.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela principal
  - nome da tabela auxiliar de ingredientes
- `config/ingestion/medication_request.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/specimen.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/condition.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/condition_ed.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
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

Ou, se preferir:

```bash
python -m src.main
```

## Resumo da Modelagem

### Tabelas finais

- `organization`
- `location`
- `patient`
- `encounter`
- `encounter_location`
- `encounter_ed`
- `encounter_icu`
- `encounter_icu_location`
- `medication`
- `medication_mix`
- `medication_mix_ingredient`
- `medication_request`
- `specimen`
- `condition`
- `condition_ed`

### Organização, Location e Patient

- `organization`
  - `id` `PK`
  - `name`
- `location`
  - `id` `PK`
  - `name`
  - `managing_organization_id` `FK -> organization.id` `nullable`
- `patient`
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

### Encounter

- `encounter`
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
- `encounter_location`
  - `encounter_id` `FK -> encounter.id`
  - `location_id` `FK -> location.id` `nullable`
  - `start_date`
  - `end_date`

### EncounterED

- `encounter_ed`
  - `id` `PK`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `patient_id` `FK -> patient.id` `nullable`
  - `organization_id` `FK -> organization.id` `nullable`
  - `status`
  - `class_code`
  - `start_date`
  - `end_date`
  - `admit_source_code`
  - `discharge_disposition_code`
  - `identifier`

### EncounterICU

- `encounter_icu`
  - `id` `PK`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `patient_id` `FK -> patient.id` `nullable`
  - `status`
  - `class_code`
  - `start_date`
  - `end_date`
  - `identifier`
- `encounter_icu_location`
  - `encounter_icu_id` `FK -> encounter_icu.id`
  - `location_id` `FK -> location.id` `nullable`
  - `start_date`
  - `end_date`

### Medication

`Medication` entra nesta fase como uma **dimensão base de medicamentos**.

- `medication`
  - `id` `PK`
  - `code`
  - `code_system`
  - `status`
  - `ndc`
  - `formulary_drug_cd`
  - `name`

Não foram observadas referências FHIR diretas confiáveis para `Patient`, `Encounter`, `Organization` ou `Location` no arquivo `MimicMedication.ndjson.gz`, então nenhuma FK nova é criada nesta fase.

### MedicationMix

`MedicationMix` se relaciona com `Medication` por meio dos ingredientes.

- `medication_mix`
  - `id` `PK`
  - `status`
  - `identifier`
- `medication_mix_ingredient`
  - `medication_mix_id` `FK -> medication_mix.id`
  - `medication_id` `FK -> medication.id`

### MedicationRequest

`MedicationRequest` se relaciona com `Patient`, `Encounter` e `Medication`.
Quando uma referência a `Medication` não encontra correspondência na tabela já carregada,
o valor é normalizado para `NULL` e o evento é registrado em log para evitar que um
único vínculo órfão interrompa toda a ingestão.

- `medication_request`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `medication_id` `FK -> medication.id` `nullable`
  - `intent`
  - `status`
  - `authored_on`
  - `identifier`
  - `validity_start`
  - `validity_end`
  - `dosage_text`
  - `route_code`
  - `frequency_code`
  - `dose_value`
  - `dose_unit`

### Estratégia de Consolidação

Quando um recurso contém listas FHIR, a ingestão usa sempre o **primeiro valor não vazio e válido encontrado**.

Isso vale, por exemplo, para:

- `name[*].family`
- `identifier[*].value`
- `maritalStatus.coding[*].code`
- `priority.coding[*].code`
- `serviceType.coding[*].code`
- `location[*].location.reference`
- `hospitalization.admitSource.coding[*].code`
- `hospitalization.dischargeDisposition.coding[*].code`
- `code.coding[*].code`
- `code.coding[*].system`
- `ingredient[*].itemReference.reference`
- `dosageInstruction[*].text`
- `dosageInstruction[*].route.coding[*].code`
- `dosageInstruction[*].timing.code.coding[*].code`
- `dosageInstruction[*].doseAndRate[*].doseQuantity.value`
- `dosageInstruction[*].doseAndRate[*].doseQuantity.unit`
- `type.coding[*].code`
- `type.coding[*].system`
- `type.coding[*].display`
- `collection.collectedDateTime`
- `category[*].coding[*].code`
- `category[*].coding[*].system`
- `category[*].coding[*].display`

Em `Medication`, os identificadores são consolidados por `system`:

- `mimic-medication-ndc` -> `ndc`
- `mimic-medication-formulary-drug-cd` -> `formulary_drug_cd`
- `mimic-medication-name` -> `name`

Em `MedicationMix`, o `identifier` é simplificado para o primeiro valor válido encontrado e os ingredientes são preservados em tabela auxiliar.

Em `MedicationRequest`, a dosagem é consolidada no primeiro conjunto útil encontrado, sem criar tabelas auxiliares.

Em `Specimen`, o tipo e o identificador seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `Condition`, o código principal e a categoria também seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `ConditionED`, o código principal e a categoria seguem a mesma regra de consolidação por primeiro valor útil encontrado.

### Condition

`Condition` entra nesta fase com relacionamento para `Patient` e `Encounter`.

- `condition`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `condition_code`
  - `condition_code_system`
  - `condition_code_display`
  - `category_code`
  - `category_system`
  - `category_display`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ConditionED

`ConditionED` entra nesta fase com relacionamento para `Patient` e `Encounter`.

- `condition_ed`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `condition_code`
  - `condition_code_system`
  - `condition_code_display`
  - `category_code`
  - `category_system`
  - `category_display`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### Specimen

`Specimen` entra nesta fase com relacionamento para `Patient`.

- `specimen`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `specimen_type_code`
  - `specimen_type_system`
  - `specimen_type_display`
  - `collected_at`
  - `identifier`

Se a referência de `Patient` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

## Relacionamentos

Os relacionamentos atualmente materializados são:

- `location.managing_organization_id -> organization.id`
- `patient.managing_organization_id -> organization.id`
- `encounter.patient_id -> patient.id`
- `encounter.organization_id -> organization.id`
- `encounter_location.encounter_id -> encounter.id`
- `encounter_location.location_id -> location.id`
- `encounter_ed.encounter_id -> encounter.id`
- `encounter_ed.patient_id -> patient.id`
- `encounter_ed.organization_id -> organization.id`
- `encounter_icu.encounter_id -> encounter.id`
- `encounter_icu.patient_id -> patient.id`
- `encounter_icu_location.encounter_icu_id -> encounter_icu.id`
- `encounter_icu_location.location_id -> location.id`
- `medication_mix_ingredient.medication_mix_id -> medication_mix.id`
- `medication_mix_ingredient.medication_id -> medication.id`
- `medication_request.patient_id -> patient.id`
- `medication_request.encounter_id -> encounter.id`
- `medication_request.medication_id -> medication.id`
- `specimen.patient_id -> patient.id`
- `condition.patient_id -> patient.id`
- `condition.encounter_id -> encounter.id`
- `condition_ed.patient_id -> patient.id`
- `condition_ed.encounter_id -> encounter.id`

## Logging

Os logs são gravados em `./logs`, com arquivo principal configurado em `config/logging.yaml`.

Exemplo padrão:

- `logs/ingestion.log`

A configuração suporta:

- criação automática do diretório
- saída em console
- rotação por tamanho
- backup de arquivos antigos

## Reset Total

A execução segue a política `drop_and_recreate`:

1. abre a conexão com o banco
2. destrói o schema de ingestão
3. recria o schema e as tabelas
4. reinsere todos os dados

Essa política é configurada em `config/ingestion/common.yaml`.

## Testes

Execute os testes de unidade com:

```bash
uv run pytest
```

Os testes cobrem:

- parser de referência FHIR
- leitor NDJSON GZIP
- transformers de `Organization`, `Location`, `Patient`, `Encounter`, `EncounterED`, `EncounterICU`, `Medication`, `MedicationMix`, `MedicationRequest`, `Specimen`, `Condition` e `ConditionED`

## Documentação Relacional

Veja também [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) para uma visão segmentada dos relacionamentos entre as tabelas.
