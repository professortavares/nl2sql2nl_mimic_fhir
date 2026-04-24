# Changelog

Todas as alterações relevantes deste projeto são registradas neste arquivo.
O formato segue uma linha próxima de `Keep a Changelog` e usa versionamento
semântico `X.Y.Z`.

## [0.28.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicMedicationAdministration.ndjson.gz` como continuação da nona e última fase de ingestão.
- Nova tabela principal `medication_administration` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `medication_request_id`
  - `status`
  - `effective_at`
  - `medication_code`
  - `medication_code_system`
  - `dosage_text`
  - `dose_value`
  - `dose_unit`
  - `dose_code`
  - `dose_system`
  - `method_code`
  - `method_system`
- Transformer, loader e pipeline dedicados para `MedicationAdministration`.
- Testes de unidade para o transformer de `MedicationAdministration`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `MedicationAdministration` ao final.
- Reestruturação do schema para incluir a tabela `medication_administration` e suas FKs para `patient`, `encounter` e `medication_request`.
- Atualização do `README.md` com a nova etapa, a modelagem simplificada e a observação de que não há FK para `Medication`.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `MedicationAdministration`.
- Atualização da configuração YAML para incluir `config/ingestion/medication_administration.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `medicationCodeableConcept.coding[*]`, `dosage.text`, `dosage.dose[*]` e `dosage.method.coding[*]` para `MedicationAdministration`.
- Consolidação explícita de `subject.reference`, `context.reference` e `request.reference` com os tipos esperados `Patient`, `Encounter` e `MedicationRequest` para `MedicationAdministration`.
- Normalização de `medication_administration.patient_id`, `medication_administration.encounter_id` e `medication_administration.medication_request_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.27.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicMedicationDispenseED.ndjson.gz` como continuação da nona e última fase de ingestão.
- Nova tabela principal `medication_dispense_ed` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `status`
  - `when_handed_over`
  - `medication_text`
  - `medication_code`
  - `medication_code_system`
- Transformer, loader e pipeline dedicados para `MedicationDispenseED`.
- Testes de unidade para o transformer de `MedicationDispenseED`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `MedicationDispenseED` ao final.
- Reestruturação do schema para incluir a tabela `medication_dispense_ed` e suas FKs para `patient` e `encounter`.
- Atualização do `README.md` com a nova etapa, a modelagem simplificada e a observação de que não há FK para `MedicationRequest` nem `Medication`.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `MedicationDispenseED`.
- Atualização da configuração YAML para incluir `config/ingestion/medication_dispense_ed.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `whenHandedOver` e `medicationCodeableConcept.coding[*]` para `MedicationDispenseED`.
- Consolidação explícita de `subject.reference` e `context.reference` com os tipos esperados `Patient` e `Encounter` para `MedicationDispenseED`.
- Normalização de `medication_dispense_ed.patient_id` e `medication_dispense_ed.encounter_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.26.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicMedicationDispense.ndjson.gz` como início da nona e última fase de ingestão.
- Nova tabela principal `medication_dispense` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `medication_request_id`
  - `status`
  - `identifier`
  - `medication_code`
  - `medication_code_system`
  - `route_code`
  - `frequency_code`
- Transformer, loader e pipeline dedicados para `MedicationDispense`.
- Testes de unidade para o transformer de `MedicationDispense`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `MedicationDispense` ao final.
- Reestruturação do schema para incluir a tabela `medication_dispense` e suas FKs para `patient`, `encounter` e `medication_request`.
- Atualização do `README.md` com a nona e última fase, a modelagem simplificada e a observação de que não há FK para `Medication`.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `MedicationDispense`.
- Atualização da configuração YAML para incluir `config/ingestion/medication_dispense.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `identifier[*]`, `medicationCodeableConcept.coding[*]`, `dosageInstruction[*].route.coding[*]` e `dosageInstruction[*].timing.code.coding[*]` para `MedicationDispense`.
- Consolidação explícita de `subject.reference`, `context.reference` e `authorizingPrescription[*].reference` com os tipos esperados `Patient`, `Encounter` e `MedicationRequest` para `MedicationDispense`.
- Normalização de `medication_dispense.patient_id`, `medication_dispense.encounter_id` e `medication_dispense.medication_request_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.25.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicObservationVitalSignsED.ndjson.gz` como continuação da oitava fase de ingestão.
- Nova tabela principal `observation_vital_signs_ed` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `procedure_id`
  - `status`
  - `observation_code`
  - `observation_code_system`
  - `observation_code_display`
  - `category_code`
  - `category_system`
  - `category_display`
  - `effective_at`
  - `value`
  - `value_unit`
  - `value_code`
  - `value_system`
- Nova tabela auxiliar `observation_vital_signs_ed_component` para os `component[*]` de sinais vitais compostos:
  - `observation_vital_signs_ed_id`
  - `component_code`
  - `component_code_system`
  - `component_code_display`
  - `value`
  - `value_unit`
  - `value_code`
  - `value_system`
- Transformer, loader e pipeline dedicados para `ObservationVitalSignsED`.
- Testes de unidade para o transformer de `ObservationVitalSignsED`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ObservationVitalSignsED` ao final.
- Reestruturação do schema para incluir a tabela `observation_vital_signs_ed`, a tabela auxiliar `observation_vital_signs_ed_component` e suas FKs para `patient`, `encounter` e `procedure`.
- Atualização do `README.md` com a nova etapa, a modelagem simplificada e o uso de `component[*]` para sinais vitais compostos, como pressão arterial.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `ObservationVitalSignsED`.
- Atualização da configuração YAML para incluir `config/ingestion/observation_vital_signs_ed.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]`, `category[*].coding[*]`, `valueQuantity[*]` e `component[*]` para `ObservationVitalSignsED`.
- Consolidação explícita de `subject.reference`, `encounter.reference` e `partOf[*].reference` com os tipos esperados `Patient`, `Encounter` e `Procedure` para `ObservationVitalSignsED`.
- Normalização de `observation_vital_signs_ed.patient_id`, `observation_vital_signs_ed.encounter_id` e `observation_vital_signs_ed.procedure_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.24.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicObservationED.ndjson.gz` como continuação da oitava fase de ingestão.
- Nova tabela principal `observation_ed` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `procedure_id`
  - `status`
  - `observation_code`
  - `observation_code_system`
  - `observation_code_display`
  - `category_code`
  - `category_system`
  - `category_display`
  - `effective_at`
  - `value_string`
  - `data_absent_reason_code`
  - `data_absent_reason_system`
  - `data_absent_reason_display`
- Transformer, loader e pipeline dedicados para `ObservationED`.
- Testes de unidade para o transformer de `ObservationED`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ObservationED` ao final.
- Reestruturação do schema para incluir a tabela `observation_ed` e suas FKs para `patient`, `encounter` e `procedure`.
- Atualização do `README.md` com a nova etapa, a modelagem simplificada e a relação entre `ObservationED` e `Procedure`.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `ObservationED`.
- Atualização da configuração YAML para incluir `config/ingestion/observation_ed.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]`, `category[*].coding[*]`, `valueString` e `dataAbsentReason.coding[*]` para `ObservationED`.
- Consolidação explícita de `subject.reference`, `encounter.reference` e `partOf[*].reference` com os tipos esperados `Patient`, `Encounter` e `Procedure` para `ObservationED`.
- Normalização de `observation_ed.patient_id`, `observation_ed.encounter_id` e `observation_ed.procedure_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.23.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicObservationOutputevents.ndjson.gz` como continuação da oitava fase de ingestão.
- Nova tabela principal `observation_outputevents` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `status`
  - `observation_code`
  - `observation_code_system`
  - `observation_code_display`
  - `category_code`
  - `category_system`
  - `issued_at`
  - `effective_at`
  - `value`
  - `value_unit`
  - `value_code`
  - `value_system`
- Transformer, loader e pipeline dedicados para `ObservationOutputevents`.
- Testes de unidade para o transformer de `ObservationOutputevents`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ObservationOutputevents` ao final.
- Reestruturação do schema para incluir a tabela `observation_outputevents` e suas FKs para `patient` e `encounter`.
- Atualização do `README.md` com a nova etapa, a modelagem simplificada e a manutenção do padrão de consolidação de listas.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `ObservationOutputevents`.
- Atualização da configuração YAML para incluir `config/ingestion/observation_outputevents.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]`, `category[*].coding[*]` e `valueQuantity[*]` para `ObservationOutputevents`.
- Consolidação explícita de `subject.reference` e `encounter.reference` com os tipos esperados `Patient` e `Encounter` para `ObservationOutputevents`.
- Normalização de `observation_outputevents.patient_id` e `observation_outputevents.encounter_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.22.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicObservationDatetimeevents.ndjson.gz` como continuação da oitava fase de ingestão.
- Nova tabela principal `observation_datetimeevents` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `status`
  - `observation_code`
  - `observation_code_system`
  - `observation_code_display`
  - `category_code`
  - `category_system`
  - `issued_at`
  - `effective_at`
  - `value_datetime`
- Transformer, loader e pipeline dedicados para `ObservationDatetimeevents`.
- Testes de unidade para o transformer de `ObservationDatetimeevents`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ObservationDatetimeevents` ao final.
- Reestruturação do schema para incluir a tabela `observation_datetimeevents` e suas FKs para `patient` e `encounter`.
- Atualização do `README.md` com a nova etapa, a modelagem simplificada e a diferença entre `valueDateTime` e `valueQuantity`/`valueString`.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `ObservationDatetimeevents`.
- Atualização da configuração YAML para incluir `config/ingestion/observation_datetimeevents.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]`, `category[*].coding[*]` e `valueDateTime` para `ObservationDatetimeevents`.
- Consolidação explícita de `subject.reference` e `encounter.reference` com os tipos esperados `Patient` e `Encounter` para `ObservationDatetimeevents`.
- Normalização de `observation_datetimeevents.patient_id` e `observation_datetimeevents.encounter_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.21.0] - 2026-04-24

### Adicionado

- Início da oitava fase de ingestão com suporte ao arquivo `data/MimicObservationChartevents.ndjson.gz`.
- Nova tabela principal `observation_chartevents` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `encounter_id`
  - `status`
  - `observation_code`
  - `observation_code_system`
  - `observation_code_display`
  - `category_code`
  - `category_system`
  - `issued_at`
  - `effective_at`
  - `value`
  - `value_unit`
  - `value_code`
  - `value_system`
  - `value_string`
- Transformer, loader e pipeline dedicados para `ObservationChartevents`.
- Testes de unidade para o transformer de `ObservationChartevents`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ObservationChartevents` ao final.
- Reestruturação do schema para incluir a tabela `observation_chartevents` e suas FKs para `patient` e `encounter`.
- Atualização do `README.md` com a nova fase, a modelagem simplificada e as instruções de execução e testes.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `ObservationChartevents`.
- Atualização da configuração YAML para incluir `config/ingestion/observation_chartevents.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]`, `category[*].coding[*]`, `valueQuantity[*]` e `valueString` para `ObservationChartevents`.
- Consolidação explícita de `subject.reference` e `encounter.reference` com os tipos esperados `Patient` e `Encounter` para `ObservationChartevents`.
- Normalização de `observation_chartevents.patient_id` e `observation_chartevents.encounter_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.20.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicObservationMicroSusc.ndjson.gz` como continuação da sétima fase de ingestão.
- Nova tabela principal `observation_micro_susc` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `derived_from_observation_micro_org_id`
  - `status`
  - `antibiotic_code`
  - `antibiotic_code_system`
  - `antibiotic_code_display`
  - `category_code`
  - `category_system`
  - `category_display`
  - `effective_at`
  - `identifier`
  - `interpretation_code`
  - `interpretation_system`
  - `interpretation_display`
  - `dilution_value`
  - `dilution_comparator`
  - `note`
- Transformer, loader e pipeline dedicados para `ObservationMicroSusc`.
- Testes de unidade para o transformer de `ObservationMicroSusc`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ObservationMicroSusc` ao final.
- Reestruturação do schema para incluir a tabela `observation_micro_susc` e suas FKs para `patient` e `observation_micro_org`.
- Atualização do `README.md` com a nova fase, a modelagem simplificada, a ligação entre susceptibilidade e organismo identificado e as instruções de execução e testes.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `ObservationMicroSusc`.
- Atualização da configuração YAML para incluir `config/ingestion/observation_micro_susc.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]`, `category[*].coding[*]`, `identifier[*].value`, `valueCodeableConcept.coding[*]`, `extension[*]` e `note[*].text` para `ObservationMicroSusc`.
- Consolidação explícita de `subject.reference` e `derivedFrom[*].reference` com os tipos esperados `Patient` e `Observation` para `ObservationMicroSusc`.
- Normalização de `observation_micro_susc.patient_id` e `observation_micro_susc.derived_from_observation_micro_org_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.19.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicObservationMicroOrg.ndjson.gz` como continuação da sétima fase de ingestão.
- Nova tabela principal `observation_micro_org` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `derived_from_observation_micro_test_id`
  - `status`
  - `organism_code`
  - `organism_code_system`
  - `organism_code_display`
  - `category_code`
  - `category_system`
  - `category_display`
  - `effective_at`
  - `value_string`
- Nova tabela auxiliar `observation_micro_org_has_member` para materializar `hasMember[*].reference`.
- Transformer, loader e pipeline dedicados para `ObservationMicroOrg`.
- Testes de unidade para o transformer de `ObservationMicroOrg`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ObservationMicroOrg` ao final.
- Reestruturação do schema para incluir a tabela `observation_micro_org`, sua tabela auxiliar `observation_micro_org_has_member` e as FKs para `patient` e `observation_micro_test`.
- Atualização do parser de referências FHIR nos testes para cobrir `Observation/<id>`.
- Atualização do `README.md` com a nova fase, a modelagem simplificada, a observação sobre `hasMember` sem FK nesta etapa e as instruções de execução e testes.
- Atualização do `TABLE_RELATIONSHIPS.md` com os novos relacionamentos de `ObservationMicroOrg`.
- Atualização da configuração YAML para incluir `config/ingestion/observation_micro_org.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]`, `category[*].coding[*]`, `derivedFrom[*].reference` e `hasMember[*].reference` para `ObservationMicroOrg`.
- Consolidação explícita de `subject.reference` e `derivedFrom[*].reference` com os tipos esperados `Patient` e `Observation` para `ObservationMicroOrg`.
- Normalização de `observation_micro_org.patient_id` e `observation_micro_org.derived_from_observation_micro_test_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.18.0] - 2026-04-24

### Adicionado

- Suporte ao arquivo `data/MimicObservationMicroTest.ndjson.gz` como continuação da sétima fase de ingestão.
- Nova tabela principal `observation_micro_test` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `specimen_id`
  - `encounter_id`
  - `status`
  - `observation_code`
  - `observation_code_system`
  - `observation_code_display`
  - `category_code`
  - `category_system`
  - `category_display`
  - `effective_at`
  - `value_string`
  - `value_code`
  - `value_code_system`
  - `value_code_display`
- Transformer, loader e pipeline dedicados para `ObservationMicroTest`.
- Testes de unidade para o transformer de `ObservationMicroTest`.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ObservationMicroTest` ao final.
- Reestruturação do schema para incluir a tabela `observation_micro_test` e suas FKs para `patient`, `specimen` e `encounter`.
- Atualização do `README.md` com a nova fase, a modelagem simplificada, a observação de que `encounter` é opcional e as instruções de execução e testes.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `ObservationMicroTest`.
- Atualização da configuração YAML para incluir `config/ingestion/observation_micro_test.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]`, `category[*].coding[*]` e `valueCodeableConcept.coding[*]` para `ObservationMicroTest`.
- Consolidação explícita de `subject.reference`, `specimen.reference` e `encounter.reference` com os tipos esperados `Patient`, `Specimen` e `Encounter` para `ObservationMicroTest`.
- Normalização de `observation_micro_test.patient_id`, `observation_micro_test.specimen_id` e `observation_micro_test.encounter_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

## [0.17.0] - 2026-04-24

### Adicionado

- Início da sétima fase de ingestão com suporte ao arquivo `data/MimicObservationLabevents.ndjson.gz`.
- Nova tabela principal `observation_labevents` com colunas simplificadas:
  - `id`
  - `patient_id`
  - `specimen_id`
  - `status`
  - `observation_code`
  - `observation_code_system`
  - `observation_code_display`
  - `category_code`
  - `category_system`
  - `category_display`
  - `effective_at`
  - `issued_at`
  - `identifier`
  - `value`
  - `value_unit`
  - `value_code`
  - `value_system`
  - `reference_low_value`
  - `reference_low_unit`
  - `reference_high_value`
  - `reference_high_unit`
  - `lab_priority`
  - `note`
- Transformer, loader e pipeline dedicados para `ObservationLabevents`.
- Testes de unidade para o transformer de `ObservationLabevents`.
- Atualização do parser de referências FHIR com suporte explícito a `Specimen/<id>` nos testes.

### Alterado

- Atualização da ordem obrigatória da pipeline para incluir `ObservationLabevents` ao final.
- Reestruturação do schema para incluir a tabela `observation_labevents` e suas FKs para `patient` e `specimen`.
- Atualização do `README.md` com a nova fase, a modelagem simplificada, a ausência de vínculo com `encounter` e as instruções de execução e testes.
- Atualização do `TABLE_RELATIONSHIPS.md` com o novo relacionamento de `ObservationLabevents`.
- Atualização da configuração YAML para incluir `config/ingestion/observation_labevents.yaml`.

### Corrigido

- Consolidação explícita do primeiro valor não vazio e válido encontrado em `code.coding[*]`, `category[*].coding[*]`, `identifier[*].value`, `referenceRange[*]`, `extension[*]` e `note[*].text` para `ObservationLabevents`.
- Consolidação explícita de `subject.reference` e `specimen.reference` com os tipos esperados `Patient` e `Specimen` para `ObservationLabevents`.
- Normalização de `observation_labevents.patient_id` e `observation_labevents.specimen_id` para `NULL` quando as referências apontam para registros inexistentes no conjunto já carregado.

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
