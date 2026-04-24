Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

23. `./data/MimicObservationED.ndjson.gz`

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

## Novo recurso: ObservationED

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
- `valueString`
- `dataAbsentReason.coding[*].code`
- `dataAbsentReason.coding[*].system`
- `dataAbsentReason.coding[*].display`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `observation_ed.patient_id -> patient.id`
- `observation_ed.encounter_id -> encounter.id`
- `observation_ed.procedure_id -> procedure.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `encounter.reference = "Encounter/<encounter_id>"`
- `partOf[*].reference = "Procedure/<procedure_id>"`

`encounter_id` e `procedure_id` devem ser nullable.

## Modelagem

Criar tabela `observation_ed` com:

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
- `value_string`
- `data_absent_reason_code`
- `data_absent_reason_system`
- `data_absent_reason_display`

Não carregar:

- `resourceType`
- `meta.profile`

Não criar tabelas auxiliares para codings/meta/partOf nesta fase.

Para listas, usar o primeiro valor não vazio e válido.

## Extração

Mapear:

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
- `valueString` -> `value_string`
- `dataAbsentReason.coding[*].code` -> `data_absent_reason_code`
- `dataAbsentReason.coding[*].system` -> `data_absent_reason_system`
- `dataAbsentReason.coding[*].display` -> `data_absent_reason_display`

## Parser FHIR

Garantir suporte para:

- `Procedure/<id>`

Manter suporte para:

- `Organization/<id>`
- `Patient/<id>`
- `Location/<id>`
- `Encounter/<id>`
- `Medication/<id>`
- `Specimen/<id>`
- `Observation/<id>`

## Arquivos

Adicionar/atualizar:

- `./config/ingestion/observation_ed.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/observation_ed_transformer.py`
- `src/ingestion/loaders/observation_ed_loader.py`
- `src/pipelines/ingest_observation_ed.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_observation_ed_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### observationED com patient, encounter e procedure

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_ed.patient_id
        |
+--------------------------+
| observation_ed           |
|--------------------------|
| id (PK)                  |
| patient_id               |
| encounter_id             |
| procedure_id             |
| observation_code         |
| effective_at             |
| value_string             |
+--------------------------+
        |              |
        |              | observation_ed.procedure_id
        |              v
        |       +----------------+
        |       |   procedure    |
        |       |----------------|
        |       | id (PK)        |
        |       +----------------+
        |
        | observation_ed.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
````

Atualizar também a visão consolidada.

## Testes de unidade

Criar testes para `observation_ed_transformer`.

Cobrir:

* registro válido com:

  * `subject.reference`
  * `encounter.reference`
  * `partOf.reference`
  * `status`
  * `code.coding`
  * `category.coding`
  * `effectiveDateTime`
  * `valueString`
* registro válido com `dataAbsentReason`
* registro sem `encounter`
* registro sem `partOf`
* registro sem `valueString`
* registro sem `dataAbsentReason`
* referência inválida em `subject`
* referência inválida em `encounter`
* referência inválida em `partOf`
* garantia de que apenas as colunas simplificadas são retornadas

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar início, arquivo processado, registros lidos/inseridos, erros e tempo de execução.

## README e CHANGELOG

Atualizar ambos com:

* suporte a `MimicObservationED`
* criação da tabela `observation_ed`
* FKs para `patient`, `encounter` e `procedure`
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
