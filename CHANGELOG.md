# Changelog

Todas as alterações relevantes deste projeto são registradas neste arquivo.
O formato segue uma linha próxima de `Keep a Changelog` e usa versionamento
semântico `X.Y.Z`.

## [0.16.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicProcedureICU.ndjson.gz` como continuação da sexta fase de ingestão.
- Nova tabela principal `procedure_icu` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `status`
  - `procedure_code`
  - `procedure_code_system`
  - `procedure_code_display`
  - `category_code`
  - `category_system`
  - `performed_start`
  - `performed_end`
- Transformer, loader e pipeline dedicados para `ProcedureICU`.
- Testes de unidade para o transformer de `ProcedureICU`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ProcedureICU` ao final.
- Reestruturação do schema para incluir a tabela `procedure_icu` e suas FKs para `patient` e `encounter`.
- Atualização do `README.md` com a nova fase, a diferença entre `performedDateTime` e `performedPeriod` e as instruções de execução e testes.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `ProcedureICU`.
- Atualização da configuração YAML para incluir `config/ingestion/procedure_icu.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]` e `category.coding[*]` para `ProcedureICU`.
- Consolidação explícita de `subject.reference` e `encounter.reference` com os tipos esperados `Patient` e `Encounter` para `ProcedureICU`.
- Normalização de `procedure_icu.patient_id` e `procedure_icu.encounter_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.15.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicProcedureED.ndjson.gz` como continuação da sexta fase de ingestão.
- Nova tabela principal `procedure_ed` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `status`
  - `procedure_code`
  - `procedure_code_system`
  - `procedure_code_display`
  - `performed_at`
- Transformer, loader e pipeline dedicados para `ProcedureED`.
- Testes de unidade para o transformer de `ProcedureED`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ProcedureED` ao final.
- Reestruturação do schema para incluir a tabela `procedure_ed` e suas FKs para `patient` e `encounter`.
- Atualização do `README.md` com a nova fase, a modelagem simplificada e as instruções de execução e testes.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `ProcedureED`.
- Atualização da configuração YAML para incluir `config/ingestion/procedure_ed.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]` para `ProcedureED`.
- Consolidação explícita de `subject.reference` e `encounter.reference` com os tipos esperados `Patient` e `Encounter` para `ProcedureED`.
- Normalização de `procedure_ed.patient_id` e `procedure_ed.encounter_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.14.0] - 2026-04-24

### Adicionado

- Início da sexta fase de ingestão com suporte ao arquivo `data/MimicProcedure.ndjson.gz`.
- Pipeline orquestrada ampliada para a ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
  4. `Encounter`
  5. `EncounterED`
  6. `EncounterICU`
  7. `Medication`
  8. `MedicationMix`
  9. `MedicationRequest`
  10. `Specimen`
  11. `Condition`
  12. `ConditionED`
  13. `Procedure`
- Nova tabela principal `procedure` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `status`
  - `procedure_code`
  - `procedure_code_system`
  - `procedure_code_display`
  - `performed_at`
- Transformer, loader e pipeline dedicados para `Procedure`.
- Testes de unidade para o transformer e o loader de `Procedure`.
- Atualização do arquivo [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) com a nova tabela e seus vínculos com `Patient` e `Encounter`.
- Atualização do `README.md` para documentar a sexta fase, a modelagem simplificada e os relacionamentos de `Procedure`.

### Alterado

- Ajuste da configuração YAML para incluir `config/ingestion/procedure.yaml`.
- Atualização da ordem da pipeline em `config/pipeline/resources.yaml`.
- Reestruturação do schema para incluir `procedure`.
- Expansão do resumo final de ingestão para contemplar `Procedure`.
- Atualização da versão do pacote para refletir a nova etapa.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]`.
- Consolidação explícita de `subject.reference` e `encounter.reference` com os tipos esperados `Patient` e `Encounter`.
- Normalização de `procedure.patient_id` e `procedure.encounter_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado, preservando a ingestão e registrando o evento em log.
- Preservação da estratégia explícita de manter a modelagem enxuta, sem tabelas auxiliares para `Procedure`.

## [0.13.0] - 2026-04-24

### Adicionado

- Continuidade da quinta fase de ingestão com suporte ao arquivo `data/MimicConditionED.ndjson.gz`.
- Pipeline orquestrada ampliada para a ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
  4. `Encounter`
  5. `EncounterED`
  6. `EncounterICU`
  7. `Medication`
  8. `MedicationMix`
  9. `MedicationRequest`
  10. `Specimen`
  11. `Condition`
  12. `ConditionED`
- Nova tabela principal `condition_ed` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `condition_code`
  - `condition_code_system`
  - `condition_code_display`
  - `category_code`
  - `category_system`
  - `category_display`
- Transformer, loader e pipeline dedicados para `ConditionED`.
- Testes de unidade para o transformer e o loader de `ConditionED`.
- Atualização do arquivo [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) com a nova tabela e seus vínculos com `Patient` e `Encounter`.
- Atualização do `README.md` para documentar a nova fase, a modelagem simplificada e os relacionamentos de `ConditionED`.

### Alterado

- Ajuste da configuração YAML para incluir `config/ingestion/condition_ed.yaml`.
- Atualização da ordem da pipeline em `config/pipeline/resources.yaml`.
- Reestruturação do schema para incluir `condition_ed`.
- Expansão do resumo final de ingestão para contemplar `ConditionED`.
- Atualização da versão do pacote para refletir a nova etapa.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]` e `category[*].coding[*]`.
- Consolidação explícita de `subject.reference` e `encounter.reference` com os tipos esperados `Patient` e `Encounter`.
- Normalização de `condition_ed.patient_id` e `condition_ed.encounter_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado, preservando a ingestão e registrando o evento em log.
- Preservação da estratégia explícita de manter a modelagem enxuta, sem tabelas auxiliares para `ConditionED`.

## [0.12.0] - 2026-04-24

### Adicionado

- Início da quinta fase de ingestão com suporte ao arquivo `data/MimicCondition.ndjson.gz`.
- Pipeline orquestrada ampliada para a ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
  4. `Encounter`
  5. `EncounterED`
  6. `EncounterICU`
  7. `Medication`
  8. `MedicationMix`
  9. `MedicationRequest`
  10. `Specimen`
  11. `Condition`
- Nova tabela principal `condition` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `condition_code`
  - `condition_code_system`
  - `condition_code_display`
  - `category_code`
  - `category_system`
  - `category_display`
- Transformer, loader e pipeline dedicados para `Condition`.
- Testes de unidade para o transformer e o loader de `Condition`.
- Atualização do arquivo [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) com a nova tabela e seus vínculos com `Patient` e `Encounter`.
- Atualização do `README.md` para documentar a nova fase, a modelagem simplificada e os relacionamentos de `Condition`.

### Alterado

- Ajuste da configuração YAML para incluir `config/ingestion/condition.yaml`.
- Atualização da ordem da pipeline em `config/pipeline/resources.yaml`.
- Reestruturação do schema para incluir `condition`.
- Expansão do resumo final de ingestão para contemplar `Condition`.
- Atualização da versão do pacote para refletir a nova etapa.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]` e `category[*].coding[*]`.
- Consolidação explícita de `subject.reference` e `encounter.reference` com os tipos esperados `Patient` e `Encounter`.
- Normalização de `condition.patient_id` e `condition.encounter_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado, preservando a ingestão e registrando o evento em log.
- Preservação da estratégia explícita de manter a modelagem enxuta, sem tabelas auxiliares para `Condition`.

## [0.11.0] - 2026-04-24

### Adicionado

- Início da quarta fase de ingestão com suporte ao arquivo `data/MimicSpecimen.ndjson.gz`.
- Pipeline orquestrada ampliada para a ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
  4. `Encounter`
  5. `EncounterED`
  6. `EncounterICU`
  7. `Medication`
  8. `MedicationMix`
  9. `MedicationRequest`
  10. `Specimen`
- Nova tabela principal `specimen` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `specimen_type_code`
  - `specimen_type_system`
  - `specimen_type_display`
  - `collected_at`
  - `identifier`
- Transformer, loader e pipeline dedicados para `Specimen`.
- Testes de unidade para o transformer e o loader de `Specimen`.
- Atualização do arquivo [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) com a nova tabela e o vínculo com `Patient`.
- Atualização do `README.md` para documentar a nova fase, a modelagem simplificada e o relacionamento de `Specimen`.

### Alterado

- Ajuste da configuração YAML para incluir `config/ingestion/specimen.yaml`.
- Atualização da ordem da pipeline em `config/pipeline/resources.yaml`.
- Reestruturação do schema para incluir `specimen`.
- Expansão do resumo final de ingestão para contemplar `Specimen`.
- Atualização da versão do pacote para refletir a nova etapa.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `type.coding[*]`, `identifier[*]` e `collection.collectedDateTime`.
- Consolidação explícita de `subject.reference` com o tipo esperado `Patient`.
- Normalização de `specimen.patient_id` para `NULL` quando a referência aponta para um `Patient` inexistente no conjunto já carregado, preservando a ingestão e registrando o evento em log.
- Preservação da estratégia explícita de manter a modelagem enxuta, sem tabelas auxiliares para `Specimen`.

## [0.10.0] - 2026-04-24

### Adicionado

- Continuidade da terceira fase de ingestão com suporte ao arquivo `data/MimicMedicationRequest.ndjson.gz`.
- Pipeline orquestrada ampliada para a ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
  4. `Encounter`
  5. `EncounterED`
  6. `EncounterICU`
  7. `Medication`
  8. `MedicationMix`
  9. `MedicationRequest`
- Nova tabela principal `medication_request` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `medication_id`
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
- Transformer e loader dedicados para `MedicationRequest`.
- Testes de unidade para o transformer de `MedicationRequest`.
- Atualização do arquivo [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) com a nova tabela e seus vínculos.
- Atualização do `README.md` para documentar a continuidade da terceira fase, a modelagem simplificada e os relacionamentos de `MedicationRequest`.

### Alterado

- Ajuste da configuração YAML para incluir `config/ingestion/medication_request.yaml`.
- Atualização da ordem da pipeline em `config/pipeline/resources.yaml`.
- Reestruturação do schema para incluir `medication_request`.
- Expansão do resumo final de ingestão para contemplar `MedicationRequest`.
- Refatoração da orquestração principal para suportar a nova ordem completa sem acoplamento a nomes fixos de recursos.
- Atualização da versão do pacote para refletir a nova etapa.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `identifier[*]`, `dosageInstruction[*]`, `route.coding[*]`, `timing.code.coding[*]` e `doseAndRate[*]`.
- Consolidação explícita de referências FHIR em `subject.reference`, `encounter.reference` e `medicationReference.reference` com os tipos esperados.
- Normalização de `medication_request.medication_id` para `NULL` quando a referência aponta para um `Medication` inexistente no conjunto já carregado, preservando a ingestão e registrando o evento em log.
- Preservação da decisão arquitetural de manter a ingestão enxuta e sem tabelas auxiliares desnecessárias para `MedicationRequest`.
- Manutenção da estratégia explícita de usar o primeiro valor não vazio e válido encontrado nas listas FHIR relevantes.

## [0.9.0] - 2026-04-24

### Adicionado

- Continuidade da terceira fase de ingestão com suporte ao arquivo `data/MimicMedicationMix.ndjson.gz`.
- Pipeline orquestrada ampliada para a ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
  4. `Encounter`
  5. `EncounterED`
  6. `EncounterICU`
  7. `Medication`
  8. `MedicationMix`
- Nova tabela principal `medication_mix` com colunas simplificadas:
  - `id`
  - `status`
  - `identifier`
- Nova tabela auxiliar `medication_mix_ingredient` com FKs para:
  - `medication_mix.id`
  - `medication.id`
- Transformer e loader dedicados para `MedicationMix`.
- Testes de unidade para o transformer de `MedicationMix`.
- Atualização do arquivo [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) com a dimensão independente de `Medication` e o relacionamento entre `MedicationMix` e `Medication`.
- Atualização do `README.md` para documentar a nova fase, a modelagem simplificada e a relação via ingredientes.

### Alterado

- Ajuste da configuração YAML para incluir `config/ingestion/medication_mix.yaml`.
- Atualização da ordem da pipeline em `config/pipeline/resources.yaml`.
- Reestruturação do schema para incluir `medication_mix` e `medication_mix_ingredient`.
- Expansão do resumo final de ingestão para contemplar `MedicationMix`.
- Refatoração da orquestração principal para suportar a nova ordem completa sem acoplamento a nomes fixos de recursos.
- Atualização da versão do pacote para refletir a nova etapa.

### Corrigido

- Consolidação explícita do primeiro identificador útil em `MedicationMix.identifier`.
- Consolidação explícita de referências FHIR em `MedicationMix.ingredient[*].itemReference.reference` com o tipo esperado `Medication`.
- Preservação da decisão arquitetural de manter `Medication` como dimensão independente nesta fase.
- Manutenção da estratégia explícita de usar o primeiro valor não vazio e válido encontrado nas listas FHIR relevantes.

## [0.8.0] - 2026-04-24

### Adicionado

- Início da terceira fase de ingestão com suporte ao arquivo `data/MimicMedication.ndjson.gz`.
- Pipeline orquestrada ampliada para a ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
  4. `Encounter`
  5. `EncounterED`
  6. `EncounterICU`
  7. `Medication`
- Nova tabela principal `medication` com colunas simplificadas:
  - `id`
  - `code`
  - `code_system`
  - `status`
  - `ndc`
  - `formulary_drug_cd`
  - `name`
- Transformer e loader dedicados para `Medication`.
- Testes de unidade para o transformer de `Medication`.
- Atualização do arquivo [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) com a documentação segmentada e a dimensão independente de `Medication`.
- Atualização do `README.md` para documentar a terceira fase, a modelagem simplificada e os logs.

### Alterado

- Ajuste da configuração YAML para incluir `config/ingestion/medication.yaml`.
- Atualização da ordem da pipeline em `config/pipeline/resources.yaml`.
- Reestruturação do schema para incluir `medication`.
- Expansão do resumo final de ingestão para contemplar `Medication`.
- Refatoração da orquestração principal para suportar a nova ordem completa sem acoplamento a nomes fixos de recursos.
- Atualização da descrição do pacote para refletir a nova fase.

### Corrigido

- Consolidação explícita de `Medication.code.coding[*]` usando o primeiro valor não vazio e válido encontrado.
- Consolidação explícita de identificadores de `Medication` por fragmento de `system`:
  - `mimic-medication-ndc`
  - `mimic-medication-formulary-drug-cd`
  - `mimic-medication-name`
- Preservação da decisão arquitetural de não criar foreign keys para `Medication` sem referência FHIR explícita no arquivo de origem.
- Manutenção da estratégia explícita de usar o primeiro valor não vazio e válido encontrado nas listas FHIR relevantes.

## [0.7.0] - 2026-04-23

### Adicionado

- Suporte à ingestão do arquivo `data/MimicEncounterICU.ndjson.gz`.
- Pipeline orquestrada ampliada para a ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
  4. `Encounter`
  5. `EncounterED`
  6. `EncounterICU`
- Nova tabela principal `encounter_icu` com FKs para:
  - `encounter.id`
  - `patient.id`
- Nova tabela auxiliar `encounter_icu_location` com FKs para:
  - `encounter_icu.id`
  - `location.id`
- Transformer e loader dedicados para `EncounterICU`.
- Testes de unidade para o transformer de `EncounterICU`.
- Atualização do arquivo [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) com diagramas ASCII segmentados por relacionamento, incluindo a especialização de UTI.
- Atualização do `README.md` para documentar a nova fase de ingestão, a modelagem de `EncounterICU` e a documentação relacional segmentada.

### Alterado

- Ajuste da configuração YAML para incluir `config/ingestion/encounter_icu.yaml`.
- Atualização da ordem da pipeline em `config/pipeline/resources.yaml`.
- Reestruturação do schema para incluir `encounter_icu` e `encounter_icu_location`.
- Expansão do resumo final de ingestão para contemplar `EncounterICU`.
- Consolidação da documentação da modelagem relacional simplificada da segunda fase.

### Corrigido

- Tratamento de referências FHIR em `EncounterICU.partOf.reference`, `EncounterICU.subject.reference` e `EncounterICU.location[*].location.reference`.
- Manutenção da estratégia explícita de usar o primeiro valor não vazio e válido encontrado nas listas FHIR relevantes.
- Preservação da decisão arquitetural de não criar relacionamento com `organization` para `EncounterICU` sem evidência no arquivo de origem.

## [0.6.0] - 2026-04-23

### Adicionado

- Suporte à ingestão do arquivo `data/MimicEncounterED.ndjson.gz`.
- Pipeline orquestrada ampliada para a ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
  4. `Encounter`
  5. `EncounterED`
- Nova tabela principal `encounter_ed` com FKs para:
  - `encounter.id`
  - `patient.id`
  - `organization.id`
- Transformer e loader dedicados para `EncounterED`.
- Testes de unidade para o transformer de `EncounterED`.
- Atualização do arquivo [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) com diagramas ASCII segmentados por relacionamento.
- Atualização do `README.md` para documentar a nova fase de ingestão, a modelagem de `EncounterED` e a documentação relacional segmentada.

### Alterado

- Ajuste da configuração YAML para incluir `config/ingestion/encounter_ed.yaml`.
- Atualização da ordem da pipeline em `config/pipeline/resources.yaml`.
- Reestruturação do schema para incluir `encounter_ed`.
- Expansão do resumo final de ingestão para contemplar `EncounterED`.
- Consolidação da documentação da modelagem relacional simplificada da segunda fase.

### Corrigido

- Tratamento de referências FHIR em `EncounterED.partOf.reference`, `EncounterED.subject.reference` e `EncounterED.serviceProvider.reference`.
- Manutenção da estratégia explícita de usar o primeiro valor não vazio e válido encontrado nas listas FHIR relevantes.

## [0.5.0] - 2026-04-23

### Adicionado

- Início da segunda fase de ingestão com suporte ao arquivo `data/MimicEncounter.ndjson.gz`.
- Pipeline orquestrada ampliada para a ordem obrigatória:
  1. `Organization`
  2. `Location`
  3. `Patient`
  4. `Encounter`
- Nova tabela principal `encounter` com FKs para:
  - `patient.id`
  - `organization.id`
- Nova tabela auxiliar `encounter_location` com FKs para:
  - `encounter.id`
  - `location.id`
- Transformer e loader dedicados para `Encounter`.
- Testes de unidade para o transformer de `Encounter`.
- Atualização do arquivo [`TABLE_RELATIONSHIPS.md`](TABLE_RELATIONSHIPS.md) com diagrama ASCII dos relacionamentos.
- Atualização do `README.md` para documentar as duas fases de ingestão e os relacionamentos de `Encounter`.

### Alterado

- Ajuste da configuração YAML para incluir `config/ingestion/encounter.yaml`.
- Atualização da ordem da pipeline em `config/pipeline/resources.yaml`.
- Reestruturação do schema para incluir `encounter` e `encounter_location`.
- Expansão do resumo final de ingestão para contemplar `Encounter`.
- Consolidação da documentação da modelagem relacional simplificada da fase 2.

### Corrigido

- Tratamento de referências FHIR em `Encounter.subject.reference`, `Encounter.location[*].location.reference` e `Encounter.serviceProvider.reference`.
- Manutenção da estratégia explícita de usar o primeiro valor não vazio e válido encontrado nas listas FHIR relevantes.

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
