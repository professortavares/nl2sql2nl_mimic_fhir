Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

21. `./data/MimicObservationDatetimeevents.ndjson.gz`

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

## Novo recurso: ObservationDatetimeevents

Campos observados:

- `id`
- `status`
- `subject.reference`
- `encounter.reference`
- `code.coding[*].code`
- `code.coding[*].system`
- `code.coding[*].display`
- `category[*].coding[*].code`
- `category[*].coding[*].system`
- `issued`
- `effectiveDateTime`
- `valueDateTime`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `observation_datetimeevents.patient_id -> patient.id`
- `observation_datetimeevents.encounter_id -> encounter.id`

## Modelagem

Criar tabela `observation_datetimeevents` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `encounter_id` FK nullable para `encounter.id`
- `status`
- `observation_code`
- `observation_code_system`
- `observation_code_display`
- `category_code`
- `category_system`
- `issued_at`
- `effective_at`
- `value_datetime`

Não carregar:

- `resourceType`
- `meta.profile`

Para listas, usar o primeiro valor não vazio e válido.

## Extração

Mapear:

- `id` -> `id`
- `subject.reference` -> `patient_id`
- `encounter.reference` -> `encounter_id`
- `status` -> `status`
- `code.coding[*].code` -> `observation_code`
- `code.coding[*].system` -> `observation_code_system`
- `code.coding[*].display` -> `observation_code_display`
- `category[*].coding[*].code` -> `category_code`
- `category[*].coding[*].system` -> `category_system`
- `issued` -> `issued_at`
- `effectiveDateTime` -> `effective_at`
- `valueDateTime` -> `value_datetime`

## Arquivos a criar/alterar

Adicionar ou atualizar:

- `./config/ingestion/observation_datetimeevents.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/observation_datetimeevents_transformer.py`
- `src/ingestion/loaders/observation_datetimeevents_loader.py`
- `src/pipelines/ingest_observation_datetimeevents.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_observation_datetimeevents_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### observationDatetimeevents com patient e encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_datetimeevents.patient_id
        |
+------------------------------+
| observation_datetimeevents   |
|------------------------------|
| id (PK)                      |
| patient_id                   |
| encounter_id                 |
| observation_code             |
| effective_at                 |
| value_datetime               |
+------------------------------+
        |
        | observation_datetimeevents.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
````

Atualizar também a visão consolidada.

## Testes de unidade

Criar testes para `observation_datetimeevents_transformer`.

Cobrir:

* registro válido com `valueDateTime`
* registro sem `encounter`
* registro sem `category`
* registro sem `valueDateTime`
* referência inválida em `subject`
* referência inválida em `encounter`
* garantia de que apenas as colunas simplificadas são retornadas

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar início, arquivo processado, registros lidos/inseridos, erros e tempo de execução.

## README e CHANGELOG

Atualizar ambos com:

* suporte a `MimicObservationDatetimeevents`
* criação da tabela `observation_datetimeevents`
* FKs para `patient` e `encounter`
* diferença em relação a `observation_chartevents`: uso de `valueDateTime`
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