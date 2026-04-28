# Documentação de Ingestão

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

### Fase 6

13. `MimicProcedure.ndjson.gz`
14. `MimicProcedureED.ndjson.gz`
15. `MimicProcedureICU.ndjson.gz`

### Fase 7

16. `MimicObservationLabevents.ndjson.gz`
17. `MimicObservationMicroTest.ndjson.gz`
18. `MimicObservationMicroOrg.ndjson.gz`
19. `MimicObservationMicroSusc.ndjson.gz`

### Fase 8

20. `MimicObservationChartevents.ndjson.gz`
21. `MimicObservationDatetimeevents.ndjson.gz`
22. `MimicObservationOutputevents.ndjson.gz`
23. `MimicObservationED.ndjson.gz`
24. `MimicObservationVitalSignsED.ndjson.gz`

### Fase 9

25. `MimicMedicationDispense.ndjson.gz`
26. `MimicMedicationDispenseED.ndjson.gz`
27. `MimicMedicationAdministration.ndjson.gz`
28. `MimicMedicationAdministrationICU.ndjson.gz`
29. `MimicMedicationStatementED.ndjson.gz`

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
15. ingestão de `Procedure`
16. ingestão de `ProcedureED`
17. ingestão de `ProcedureICU`
18. ingestão de `ObservationLabevents`
19. ingestão de `ObservationMicroTest`
20. ingestão de `ObservationMicroOrg`
21. ingestão de `ObservationMicroSusc`
22. ingestão de `ObservationChartevents`
23. ingestão de `ObservationDatetimeevents`
24. ingestão de `ObservationOutputevents`
25. ingestão de `ObservationED`
26. ingestão de `ObservationVitalSignsED`
27. ingestão de `MedicationDispense`
28. ingestão de `MedicationDispenseED`
29. ingestão de `MedicationAdministration`
30. ingestão de `MedicationAdministrationICU`
31. ingestão de `MedicationStatementED`

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
- `config/ingestion/procedure.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/procedure_ed.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/procedure_icu.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/observation_labevents.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/observation_micro_test.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/observation_micro_org.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
  - nome da tabela auxiliar
- `config/ingestion/observation_micro_susc.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/observation_chartevents.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/observation_datetimeevents.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/observation_outputevents.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/observation_ed.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/observation_vital_signs_ed.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela principal
  - nome da tabela auxiliar de components
- `config/ingestion/medication_dispense.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/medication_dispense_ed.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/medication_administration.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/medication_administration_icu.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/ingestion/medication_statement_ed.yaml`
  - caminho do arquivo
  - batch size
  - nome da tabela
- `config/dictionary/dictionary.yaml`
  - habilita ou desabilita a geração
  - caminho de saída do YAML gerado
  - caminho das descrições manuais
  - uso de exemplos reais
  - quantidade máxima de exemplos por coluna
  - descrição textual da base
- `config/dictionary/tables.yaml`
  - descrições humanas para tabelas e colunas
- `config/pipeline/resources.yaml`
  - ordem oficial da pipeline

## Dicionário de Dados

Ao final de uma execução bem-sucedida da pipeline, o projeto gera automaticamente `./dict/dicionario.yaml`.

- O arquivo é criado somente depois que o schema é recriado, os dados são ingeridos e a transação termina com sucesso.
- Se a ingestão falhar, o dicionário não é gerado.
- A estrutura do YAML segue o padrão `database -> tables -> columns`, com metadados de PK, FK, obrigatoriedade, tipos e exemplos.
- As descrições humanas vêm de `./config/dictionary/tables.yaml` quando estiverem disponíveis.
- Os exemplos de valores são extraídos dos dados realmente carregados no banco.

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
- `procedure`
- `procedure_ed`
- `procedure_icu`
- `observation_labevents`
- `observation_micro_test`
- `observation_micro_org`
- `observation_micro_org_has_member`
- `observation_micro_susc`
- `observation_chartevents`
- `observation_datetimeevents`
- `observation_outputevents`
- `observation_ed`
- `observation_vital_signs_ed`
- `observation_vital_signs_ed_component`
- `medication_dispense`
- `medication_dispense_ed`
- `medication_administration`
- `medication_administration_icu`
- `medication_statement_ed`

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

### MedicationDispense

`MedicationDispense` continua a nona fase com relacionamento para `Patient`, `Encounter` e `MedicationRequest`.
Não é criada FK para `Medication`, porque o arquivo usa `medicationCodeableConcept`, não `medicationReference`.

- `medication_dispense`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `medication_request_id` `FK -> medication_request.id` `nullable`
  - `status`
  - `identifier`
  - `medication_code`
  - `route_code`
  - `frequency_code`

Se a referência de `Patient`, `Encounter` ou `MedicationRequest` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### MedicationDispenseED

`MedicationDispenseED` continua a nona fase com relacionamento para `Patient` e `Encounter`.
Não é criada FK para `MedicationRequest`, porque o arquivo não possui `authorizingPrescription`.
Também não é criada FK para `Medication`, porque o arquivo usa `medicationCodeableConcept`, não `medicationReference`.

- `medication_dispense_ed`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `status`
  - `when_handed_over`
  - `medication_text`
  - `medication_code`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### MedicationAdministration

`MedicationAdministration` continua a nona fase com relacionamento para `Patient`, `Encounter` e `MedicationRequest`.
Não é criada FK para `Medication`, porque o arquivo usa `medicationCodeableConcept`, não `medicationReference`.

- `medication_administration`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `medication_request_id` `FK -> medication_request.id` `nullable`
  - `status`
  - `effective_at`
  - `medication_code`
  - `dosage_text`
  - `dose_value`
  - `dose_unit`
  - `dose_code`
  - `method_code`

Se a referência de `Patient`, `Encounter` ou `MedicationRequest` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### MedicationAdministrationICU

`MedicationAdministrationICU` continua a nona fase com relacionamento para `Patient` e `Encounter`.
Não é criada FK para `MedicationRequest` nem para `Medication`, porque o arquivo não possui `request.reference` e usa `medicationCodeableConcept`, não `medicationReference`.

- `medication_administration_icu`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `status`
  - `effective_at`
  - `category_code`
  - `medication_code`
  - `medication_code_display`
  - `dose_value`
  - `dose_unit`
  - `dose_code`
  - `method_code`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### MedicationStatementED

`MedicationStatementED` finaliza a nona e última fase com relacionamento para `Patient` e `Encounter`.
Não é criada FK para `Medication`, porque o arquivo usa `medicationCodeableConcept`, não `medicationReference`.

- `medication_statement_ed`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `status`
  - `date_asserted`
  - `medication_text`
  - `medication_code`
  - `medication_code_display`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

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
- `ingredient[*].itemReference.reference`
- `dosageInstruction[*].text`
- `dosageInstruction[*].route.coding[*].code`
- `dosageInstruction[*].timing.code.coding[*].code`
- `dosageInstruction[*].doseAndRate[*].doseQuantity.value`
- `dosageInstruction[*].doseAndRate[*].doseQuantity.unit`
- `medicationCodeableConcept.coding[*].code`
- `type.coding[*].code`
- `type.coding[*].display`
- `collection.collectedDateTime`
- `category[*].coding[*].code`
- `category[*].coding[*].display`


- `mimic-medication-ndc` -> `ndc`
- `mimic-medication-formulary-drug-cd` -> `formulary_drug_cd`
- `mimic-medication-name` -> `name`

Em `MedicationMix`, o `identifier` é simplificado para o primeiro valor válido encontrado e os ingredientes são preservados em tabela auxiliar.

Em `MedicationRequest`, a dosagem é consolidada no primeiro conjunto útil encontrado, sem criar tabelas auxiliares.

Em `Specimen`, o tipo e o identificador seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `Condition`, o código principal e a categoria também seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `ConditionED`, o código principal e a categoria seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `Procedure`, o código do procedimento segue a mesma regra de consolidação por primeiro valor útil encontrado.

Em `ProcedureED`, o código do procedimento segue a mesma regra de consolidação por primeiro valor útil encontrado.

Em `ProcedureICU`, o código do procedimento e a categoria seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `ObservationLabevents`, o código, a categoria, o identificador, o valor, os limites de referência, a prioridade laboratorial e a nota seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `ObservationMicroTest`, o código, a categoria e o valor seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `ObservationMicroOrg`, o código do organismo, a categoria e o valor também seguem a mesma regra de consolidação por primeiro valor útil encontrado, enquanto `hasMember` é materializado em tabela auxiliar com múltiplas linhas.

Em `ObservationMicroSusc`, o código do antibiótico, a categoria e a interpretação seguem a mesma regra de consolidação por primeiro valor útil encontrado, enquanto a extensão `dilution-details` é mapeada para colunas escalares.

Em `ObservationChartevents`, o código, a categoria, o valor numérico e o valor textual seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `ObservationDatetimeevents`, o código, a categoria e o valor temporal seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `ObservationOutputevents`, o código, a categoria e o valor numérico seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `ObservationED`, o código, a categoria, o valor textual e o motivo de ausência seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `MedicationDispense`, `identifier`, `route`, `frequency` e `medicationCodeableConcept` seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `MedicationDispenseED`, `whenHandedOver` e `medicationCodeableConcept` seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `MedicationAdministration`, `effectiveDateTime`, `medicationCodeableConcept`, `dosage.text`, `dosage.dose` e `dosage.method` seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `MedicationAdministrationICU`, `effectiveDateTime`, `category`, `medicationCodeableConcept` e `dosage` seguem a mesma regra de consolidação por primeiro valor útil encontrado.

Em `MedicationStatementED`, `dateAsserted` e `medicationCodeableConcept` seguem a mesma regra de consolidação por primeiro valor útil encontrado.

### Condition

`Condition` entra nesta fase com relacionamento para `Patient` e `Encounter`.

- `condition`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `condition_code`
  - `condition_code_display`
  - `category_code`
  - `category_display`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ConditionED

`ConditionED` entra nesta fase com relacionamento para `Patient` e `Encounter`.

- `condition_ed`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `condition_code`
  - `condition_code_display`
  - `category_code`
  - `category_display`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### Procedure

`Procedure` entra nesta fase com relacionamento para `Patient` e `Encounter`.

- `procedure`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `status`
  - `procedure_code`
  - `procedure_code_display`
  - `performed_at`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ProcedureED

`ProcedureED` entra nesta fase com relacionamento para `Patient` e `Encounter`.

- `procedure_ed`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `status`
  - `procedure_code`
  - `procedure_code_display`
  - `performed_at`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ProcedureICU

`ProcedureICU` entra nesta fase com relacionamento para `Patient` e `Encounter`.

- `procedure_icu`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `status`
  - `procedure_code`
  - `procedure_code_display`
  - `category_code`
  - `performed_start`
  - `performed_end`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

`ProcedureICU` usa `performedPeriod.start` e `performedPeriod.end`, enquanto `Procedure` e `ProcedureED` usam `performedDateTime`. A modelagem guarda os dois limites do período para manter a janela temporal observada no recurso ICU.

### ObservationLabevents

`ObservationLabevents` entra nesta fase com relacionamento para `Patient` e `Specimen`.

- `observation_labevents`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `specimen_id` `FK -> specimen.id` `nullable`
  - `status`
  - `observation_code`
  - `observation_code_display`
  - `category_code`
  - `category_display`
  - `effective_at`
  - `issued_at`
  - `identifier`
  - `value`
  - `value_unit`
  - `value_code`
  - `reference_low_value`
  - `reference_low_unit`
  - `reference_high_value`
  - `reference_high_unit`
  - `lab_priority`
  - `note`

Se a referência de `Patient` ou `Specimen` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

`encounter` não é usado aqui porque o arquivo não expõe uma referência explícita para esse vínculo.

### ObservationMicroTest

`ObservationMicroTest` entra nesta fase com relacionamento para `Patient`, `Specimen` e `Encounter`.

- `observation_micro_test`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `specimen_id` `FK -> specimen.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `status`
  - `observation_code`
  - `observation_code_display`
  - `category_code`
  - `category_display`
  - `effective_at`
  - `value_string`
  - `value_code`
  - `value_code_display`

`encounter` é opcional aqui porque nem todos os registros carregam `encounter.reference`.

Se a referência de `Patient`, `Specimen` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ObservationMicroOrg

`ObservationMicroOrg` entra nesta fase com relacionamento para `Patient` e `ObservationMicroTest`.

- `observation_micro_org`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `derived_from_observation_micro_test_id` `FK -> observation_micro_test.id` `nullable`
  - `status`
  - `organism_code`
  - `organism_code_display`
  - `category_code`
  - `category_display`
  - `effective_at`
  - `value_string`
- `observation_micro_org_has_member`
  - `observation_micro_org_id` `FK -> observation_micro_org.id`
  - `member_observation_id`

`derivedFrom` aponta para a observação microbiológica de teste já carregada na etapa anterior.

`hasMember` gera múltiplas linhas na tabela auxiliar e, nesta etapa, `member_observation_id` ainda não possui FK porque pode apontar para observações microbiológicas futuras.

Se a referência de `Patient` ou `ObservationMicroTest` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ObservationMicroSusc

`ObservationMicroSusc` entra nesta fase com relacionamento para `Patient` e `ObservationMicroOrg`.

- `observation_micro_susc`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `derived_from_observation_micro_org_id` `FK -> observation_micro_org.id` `nullable`
  - `status`
  - `antibiotic_code`
  - `antibiotic_code_display`
  - `category_code`
  - `category_display`
  - `effective_at`
  - `identifier`
  - `interpretation_code`
  - `interpretation_display`
  - `dilution_value`
  - `dilution_comparator`
  - `note`

`derivedFrom` liga a susceptibilidade ao organismo identificado na etapa anterior.

Se a referência de `Patient` ou `ObservationMicroOrg` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ObservationChartevents

`ObservationChartevents` inicia a oitava fase com relacionamento para `Patient` e `Encounter`.

- `observation_chartevents`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `status`
  - `observation_code`
  - `observation_code_display`
  - `category_code`
  - `issued_at`
  - `effective_at`
  - `value`
  - `value_unit`
  - `value_code`
  - `value_string`

`encounter` é opcional aqui porque nem todos os registros carregam `encounter.reference`.

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ObservationDatetimeevents

`ObservationDatetimeevents` complementa a oitava fase com relacionamento para `Patient` e `Encounter`.

- `observation_datetimeevents`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `status`
  - `observation_code`
  - `observation_code_display`
  - `category_code`
  - `issued_at`
  - `effective_at`
  - `value_datetime`

`ObservationDatetimeevents` usa `valueDateTime`, enquanto `ObservationChartevents` guarda `valueQuantity` ou `valueString`.

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ObservationOutputevents

`ObservationOutputevents` complementa a oitava fase com relacionamento para `Patient` e `Encounter`.

- `observation_outputevents`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `status`
  - `observation_code`
  - `observation_code_display`
  - `category_code`
  - `issued_at`
  - `effective_at`
  - `value`
  - `value_unit`
  - `value_code`

Se a referência de `Patient` ou `Encounter` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ObservationED

`ObservationED` complementa a oitava fase com relacionamento para `Patient`, `Encounter` e `Procedure`.

- `observation_ed`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `procedure_id` `FK -> procedure.id` `nullable`
  - `status`
  - `observation_code`
  - `observation_code_display`
  - `category_code`
  - `category_display`
  - `effective_at`
  - `value_string`
  - `data_absent_reason_code`
  - `data_absent_reason_display`

Se a referência de `Patient`, `Encounter` ou `Procedure` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### ObservationVitalSignsED

`ObservationVitalSignsED` encerra a oitava fase com relacionamento para `Patient`, `Encounter`, `Procedure` e uma tabela auxiliar de `component`.

- `observation_vital_signs_ed`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `encounter_id` `FK -> encounter.id` `nullable`
  - `procedure_id` `FK -> procedure.id` `nullable`
  - `status`
  - `observation_code`
  - `observation_code_display`
  - `category_code`
  - `category_display`
  - `effective_at`
  - `value`
  - `value_unit`
  - `value_code`
- `observation_vital_signs_ed_component`
  - `observation_vital_signs_ed_id` `FK -> observation_vital_signs_ed.id`
  - `component_code`
  - `component_code_display`
  - `value`
  - `value_unit`
  - `value_code`

`component[*]` é usado para sinais vitais compostos, como pressão arterial, permitindo preservar os subvalores em linhas próprias.

Se a referência de `Patient`, `Encounter` ou `Procedure` não estiver presente no conjunto já carregado, o valor é normalizado para `NULL` e o evento é registrado em log para manter a ingestão resiliente.

### Specimen

`Specimen` entra nesta fase com relacionamento para `Patient`.

- `specimen`
  - `id` `PK`
  - `patient_id` `FK -> patient.id` `nullable`
  - `specimen_type_code`
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
- `procedure.patient_id -> patient.id`
- `procedure.encounter_id -> encounter.id`
- `procedure_ed.patient_id -> patient.id`
- `procedure_ed.encounter_id -> encounter.id`
- `procedure_icu.patient_id -> patient.id`
- `procedure_icu.encounter_id -> encounter.id`
- `observation_labevents.patient_id -> patient.id`
- `observation_labevents.specimen_id -> specimen.id`
- `observation_micro_test.patient_id -> patient.id`
- `observation_micro_test.specimen_id -> specimen.id`
- `observation_micro_test.encounter_id -> encounter.id`
- `observation_micro_org.patient_id -> patient.id`
- `observation_micro_org.derived_from_observation_micro_test_id -> observation_micro_test.id`
- `observation_micro_org_has_member.observation_micro_org_id -> observation_micro_org.id`
- `observation_micro_susc.patient_id -> patient.id`
- `observation_micro_susc.derived_from_observation_micro_org_id -> observation_micro_org.id`
- `observation_chartevents.patient_id -> patient.id`
- `observation_chartevents.encounter_id -> encounter.id`
- `observation_datetimeevents.patient_id -> patient.id`
- `observation_datetimeevents.encounter_id -> encounter.id`
- `observation_outputevents.patient_id -> patient.id`
- `observation_outputevents.encounter_id -> encounter.id`
- `observation_ed.patient_id -> patient.id`
- `observation_ed.encounter_id -> encounter.id`
- `observation_ed.procedure_id -> procedure.id`
- `observation_vital_signs_ed.patient_id -> patient.id`
- `observation_vital_signs_ed.encounter_id -> encounter.id`
- `observation_vital_signs_ed.procedure_id -> procedure.id`
- `observation_vital_signs_ed_component.observation_vital_signs_ed_id -> observation_vital_signs_ed.id`

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
  - transformers de `Organization`, `Location`, `Patient`, `Encounter`, `EncounterED`, `EncounterICU`, `Medication`, `MedicationMix`, `MedicationRequest`, `Specimen`, `Condition`, `ConditionED`, `Procedure`, `ProcedureED`, `ProcedureICU`, `ObservationLabevents`, `ObservationMicroTest`, `ObservationMicroOrg`, `ObservationMicroSusc`, `ObservationChartevents`, `ObservationDatetimeevents`, `ObservationOutputevents`, `ObservationED`, `ObservationVitalSignsED`, `MedicationDispense`, `MedicationDispenseED`, `MedicationAdministration`, `MedicationAdministrationICU` e `MedicationStatementED`

## Documentação Relacional

Veja também [`TABLE_RELATIONSHIPS.md`](../TABLE_RELATIONSHIPS.md) para uma visão segmentada dos relacionamentos entre as tabelas.
