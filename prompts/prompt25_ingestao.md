Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

24. `./data/MimicObservationVitalSignsED.ndjson.gz`

Esta entrega dá continuidade à oitava fase: observações charted.

## Ordem completa da pipeline
1. MimicOrganization
2. MimicLocation
3. MimicPatient
4. MimicEncounter
5. MimicEncounterED
6. MimicEncounterICU
7. MimicMedication
8. MimicMedicationMix
9. MimicMedicationRequest
10. MimicSpecimen
11. MimicCondition
12. MimicConditionED
13. MimicProcedure
14. MimicProcedureED
15. MimicProcedureICU
16. MimicObservationLabevents
17. MimicObservationMicroTest
18. MimicObservationMicroOrg
19. MimicObservationMicroSusc
20. MimicObservationChartevents
21. MimicObservationDatetimeevents
22. MimicObservationOutputevents
23. MimicObservationED
24. MimicObservationVitalSignsED

## Novo recurso: ObservationVitalSignsED

Campos observados:

- `id`
- `status`
- `subject.reference`
- `encounter.reference`
- `partOf[*].reference`
- `code.coding[*].code`
- `code.coding[*].system`
- `code.coding[*].display`
- `category[*].coding[*].code`
- `category[*].coding[*].system`
- `category[*].coding[*].display`
- `effectiveDateTime`
- `valueQuantity.value`
- `valueQuantity.unit`
- `valueQuantity.code`
- `valueQuantity.system`
- `component[*].code.coding[*].code`
- `component[*].code.coding[*].system`
- `component[*].code.coding[*].display`
- `component[*].valueQuantity.value`
- `component[*].valueQuantity.unit`
- `component[*].valueQuantity.code`
- `component[*].valueQuantity.system`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `observation_vital_signs_ed.patient_id -> patient.id`
- `observation_vital_signs_ed.encounter_id -> encounter.id`
- `observation_vital_signs_ed.procedure_id -> procedure.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `encounter.reference = "Encounter/<encounter_id>"`
- `partOf[*].reference = "Procedure/<procedure_id>"`

`encounter_id` e `procedure_id` devem ser nullable.

## Modelagem

Criar tabela principal `observation_vital_signs_ed` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `encounter_id` FK nullable para `encounter.id`
- `procedure_id` FK nullable para `procedure.id`
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

Criar tabela auxiliar `observation_vital_signs_ed_component` com:

- `observation_vital_signs_ed_id` FK para `observation_vital_signs_ed.id`
- `component_code`
- `component_code_system`
- `component_code_display`
- `value`
- `value_unit`
- `value_code`
- `value_system`

Essa tabela auxiliar é necessária porque sinais vitais compostos, como pressão arterial, usam `component[*]`.

Não carregar:

- `resourceType`
- `meta.profile`

Para listas simples, usar o primeiro valor não vazio e válido.
Para `component[*]`, gerar uma linha por componente válido.

## Extração

Tabela `observation_vital_signs_ed`:

- `id` -> `id`
- `subject.reference` -> `patient_id`
- `encounter.reference` -> `encounter_id`
- `partOf[*].reference` -> `procedure_id`
- `status` -> `status`
- `code.coding[*].code` -> `observation_code`
- `code.coding[*].system` -> `observation_code_system`
- `code.coding[*].display` -> `observation_code_display`
- `category[*].coding[*].code` -> `category_code`
- `category[*].coding[*].system` -> `category_system`
- `category[*].coding[*].display` -> `category_display`
- `effectiveDateTime` -> `effective_at`
- `valueQuantity.value` -> `value`
- `valueQuantity.unit` -> `value_unit`
- `valueQuantity.code` -> `value_code`
- `valueQuantity.system` -> `value_system`

Tabela `observation_vital_signs_ed_component`:

- `component[*].code.coding[*].code` -> `component_code`
- `component[*].code.coding[*].system` -> `component_code_system`
- `component[*].code.coding[*].display` -> `component_code_display`
- `component[*].valueQuantity.value` -> `value`
- `component[*].valueQuantity.unit` -> `value_unit`
- `component[*].valueQuantity.code` -> `value_code`
- `component[*].valueQuantity.system` -> `value_system`

## Arquivos

Adicionar/atualizar:

- `./config/ingestion/observation_vital_signs_ed.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/observation_vital_signs_ed_transformer.py`
- `src/ingestion/loaders/observation_vital_signs_ed_loader.py`
- `src/pipelines/ingest_observation_vital_signs_ed.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_observation_vital_signs_ed_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### observationVitalSignsED com patient, encounter, procedure e components

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_vital_signs_ed.patient_id
        |
+--------------------------------+
| observation_vital_signs_ed     |
|--------------------------------|
| id (PK)                        |
| patient_id                     |
| encounter_id                   |
| procedure_id                   |
| observation_code               |
| effective_at                   |
| value                          |
| value_unit                     |
+--------------------------------+
        |              |
        |              | observation_vital_signs_ed.procedure_id
        |              v
        |       +----------------+
        |       |   procedure    |
        |       |----------------|
        |       | id (PK)        |
        |       +----------------+
        |
        | observation_vital_signs_ed.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+

+--------------------------------+
| observation_vital_signs_ed     |
|--------------------------------|
| id (PK)                        |
+--------------------------------+
        |
        | observation_vital_signs_ed_component.observation_vital_signs_ed_id
        v
+----------------------------------------+
| observation_vital_signs_ed_component   |
|----------------------------------------|
| observation_vital_signs_ed_id          |
| component_code                         |
| value                                  |
| value_unit                             |
+----------------------------------------+
````

Atualizar também a visão consolidada.

## Testes de unidade

Criar testes para `observation_vital_signs_ed_transformer`.

Cobrir:

* registro válido com `valueQuantity`
* registro válido com `component` de pressão arterial
* registro com múltiplos componentes
* registro sem `encounter`
* registro sem `partOf`
* registro sem `valueQuantity`
* registro sem `component`
* referência inválida em `subject`
* referência inválida em `encounter`
* referência inválida em `partOf`
* garantia de que a tabela principal simplificada é retornada corretamente
* garantia de que a tabela de components é montada corretamente

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar início, arquivo processado, registros lidos/inseridos na tabela principal e na tabela de componentes, erros e tempo de execução.

## README e CHANGELOG

Atualizar ambos com:

* suporte a `MimicObservationVitalSignsED`
* criação da tabela `observation_vital_signs_ed`
* criação da tabela `observation_vital_signs_ed_component`
* FKs para `patient`, `encounter`, `procedure` e components
* explicação do uso de `component[*]` para pressão arterial
* atualização da ordem da pipeline
* atualização do `TABLE_RELATIONSHIPS.md`
* testes unitários

## Qualidade

Manter type hints, docstrings em português, tratamento de exceções, YAML para configurações, `.env` para credenciais, compatibilidade com `uv` e testes com `pytest`.

## Execução

A ingestão completa deve continuar executando com:

```bash
python -m src.main
```