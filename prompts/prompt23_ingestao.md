Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

22. `./data/MimicObservationOutputevents.ndjson.gz`

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

## Novo recurso: ObservationOutputevents

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
- `valueQuantity.value`
- `valueQuantity.unit`
- `valueQuantity.code`
- `valueQuantity.system`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `observation_outputevents.patient_id -> patient.id`
- `observation_outputevents.encounter_id -> encounter.id`

## Modelagem

Criar tabela `observation_outputevents` com:

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
- `value`
- `value_unit`
- `value_code`
- `value_system`

Não carregar `resourceType` nem `meta.profile`.

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
- `valueQuantity.value` -> `value`
- `valueQuantity.unit` -> `value_unit`
- `valueQuantity.code` -> `value_code`
- `valueQuantity.system` -> `value_system`

Para listas, usar o primeiro valor não vazio e válido.

## Arquivos

Adicionar/atualizar:

- `./config/ingestion/observation_outputevents.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/observation_outputevents_transformer.py`
- `src/ingestion/loaders/observation_outputevents_loader.py`
- `src/pipelines/ingest_observation_outputevents.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_observation_outputevents_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### observationOutputevents com patient e encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_outputevents.patient_id
        |
+-----------------------------+
| observation_outputevents    |
|-----------------------------|
| id (PK)                     |
| patient_id                  |
| encounter_id                |
| observation_code            |
| effective_at                |
| value                       |
| value_unit                  |
+-----------------------------+
        |
        | observation_outputevents.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
````

Atualizar também a visão consolidada.

## Testes de unidade

Criar testes para `observation_outputevents_transformer`.

Cobrir:

* registro válido com `valueQuantity`
* registro sem `encounter`
* registro sem `category`
* registro sem `valueQuantity`
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

* suporte a `MimicObservationOutputevents`
* criação da tabela `observation_outputevents`
* FKs para `patient` e `encounter`
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