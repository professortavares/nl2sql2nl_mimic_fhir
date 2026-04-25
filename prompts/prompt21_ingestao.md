Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

20. `./data/MimicObservationChartevents.ndjson.gz`

Esta entrega inicia a oitava fase: observações charted.

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

## Novo recurso: ObservationChartevents

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
- `valueString`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `observation_chartevents.patient_id -> patient.id`
- `observation_chartevents.encounter_id -> encounter.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `encounter.reference = "Encounter/<encounter_id>"`

`encounter_id` deve ser nullable.

## Modelagem

Criar tabela `observation_chartevents` com:

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
- `value_string`

Não carregar:

- `resourceType`
- `meta.profile`

Não criar tabelas auxiliares para codings/meta.

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
- `valueQuantity.value` -> `value`
- `valueQuantity.unit` -> `value_unit`
- `valueQuantity.code` -> `value_code`
- `valueQuantity.system` -> `value_system`
- `valueString` -> `value_string`

## Arquivos a criar/alterar

Adicionar ou atualizar:

- `./config/ingestion/observation_chartevents.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/observation_chartevents_transformer.py`
- `src/ingestion/loaders/observation_chartevents_loader.py`
- `src/pipelines/ingest_observation_chartevents.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_observation_chartevents_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### observationChartevents com patient e encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_chartevents.patient_id
        |
+--------------------------+
| observation_chartevents  |
|--------------------------|
| id (PK)                  |
| patient_id               |
| encounter_id             |
| observation_code         |
| effective_at             |
| value                    |
| value_string             |
+--------------------------+
        |
        | observation_chartevents.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
````

Atualizar também a visão consolidada.

## Testes de unidade

Criar testes para `observation_chartevents_transformer`.

Cobrir:

* registro válido com `valueQuantity`
* registro válido com `valueString`
* registro sem `encounter`
* registro sem `category`
* registro sem `valueQuantity` e sem `valueString`
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

* início da oitava fase
* suporte a `MimicObservationChartevents`
* criação da tabela `observation_chartevents`
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
