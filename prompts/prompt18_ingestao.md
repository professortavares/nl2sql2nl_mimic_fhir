Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

17. `./data/MimicObservationMicroTest.ndjson.gz`

Esta entrega dá continuidade à sétima fase: observações laboratoriais e microbiologia.

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

## Novo recurso: ObservationMicroTest

Campos observados:

- `id`
- `status`
- `subject.reference`
- `specimen.reference`
- `encounter.reference`
- `code.coding[*].code`
- `code.coding[*].system`
- `code.coding[*].display`
- `category[*].coding[*].code`
- `category[*].coding[*].system`
- `category[*].coding[*].display`
- `effectiveDateTime`
- `valueString`
- `valueCodeableConcept.coding[*].code`
- `valueCodeableConcept.coding[*].system`
- `valueCodeableConcept.coding[*].display`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `observation_micro_test.patient_id -> patient.id`
- `observation_micro_test.specimen_id -> specimen.id`
- `observation_micro_test.encounter_id -> encounter.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `specimen.reference = "Specimen/<specimen_id>"`
- `encounter.reference = "Encounter/<encounter_id>"`

`encounter_id` deve ser nullable, pois nem todos os registros possuem `encounter.reference`.

## Modelagem

Criar tabela `observation_micro_test` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `specimen_id` FK nullable para `specimen.id`
- `encounter_id` FK nullable para `encounter.id`
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

Não carregar:

- `resourceType`
- `meta.profile`

Não criar tabelas auxiliares para:

- `observation_micro_test_code_coding`
- `observation_micro_test_category_coding`
- `observation_micro_test_value_codeable_concept`
- `observation_micro_test_meta_profile`

Para listas, usar o primeiro valor não vazio e válido.

## Extração

Mapear:

- `id` -> `id`
- `subject.reference` -> `patient_id`
- `specimen.reference` -> `specimen_id`
- `encounter.reference` -> `encounter_id`
- `status` -> `status`
- `code.coding[*].code` -> `observation_code`
- `code.coding[*].system` -> `observation_code_system`
- `code.coding[*].display` -> `observation_code_display`
- `category[*].coding[*].code` -> `category_code`
- `category[*].coding[*].system` -> `category_system`
- `category[*].coding[*].display` -> `category_display`
- `effectiveDateTime` -> `effective_at`
- `valueString` -> `value_string`
- `valueCodeableConcept.coding[*].code` -> `value_code`
- `valueCodeableConcept.coding[*].system` -> `value_code_system`
- `valueCodeableConcept.coding[*].display` -> `value_code_display`

## Parser FHIR

Garantir suporte para:

- `Specimen/<id>`

Manter suporte para:

- `Organization/<id>`
- `Patient/<id>`
- `Location/<id>`
- `Encounter/<id>`
- `Medication/<id>`

## Arquivos a criar/alterar

Adicionar ou atualizar:

- `./config/ingestion/observation_micro_test.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/observation_micro_test_transformer.py`
- `src/ingestion/loaders/observation_micro_test_loader.py`
- `src/pipelines/ingest_observation_micro_test.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_observation_micro_test_transformer.py`

## TABLE_RELATIONSHIPS.md

Atualizar o arquivo mantendo diagramas ASCII segmentados.

Adicionar seção:

### observationMicroTest com patient, specimen e encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_micro_test.patient_id
        |
+--------------------------+
| observation_micro_test   |
|--------------------------|
| id (PK)                  |
| patient_id               |
| specimen_id              |
| encounter_id             |
| observation_code         |
| effective_at             |
| value_string             |
| value_code               |
+--------------------------+
        |              |
        |              | observation_micro_test.encounter_id
        |              v
        |       +----------------+
        |       |   encounter    |
        |       |----------------|
        |       | id (PK)        |
        |       +----------------+
        |
        | observation_micro_test.specimen_id
        v
+----------------+
|    specimen    |
|----------------|
| id (PK)        |
| patient_id     |
+----------------+
````

Atualizar também a visão consolidada, se existir.

## Testes de unidade

Criar testes para `observation_micro_test_transformer`.

Cobrir:

* registro válido com:

  * `subject.reference`
  * `specimen.reference`
  * `encounter.reference`
  * `status`
  * `code.coding`
  * `category.coding`
  * `effectiveDateTime`
  * `valueString`
* registro válido com `valueCodeableConcept`
* registro sem `encounter`
* registro sem `specimen`
* registro sem `valueString`
* registro sem `valueCodeableConcept`
* referência inválida em `subject`
* referência inválida em `specimen`
* referência inválida em `encounter`
* garantia de que apenas as colunas simplificadas são retornadas

Atualizar testes do parser FHIR para referência `Specimen`, se ainda não existir.

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar:

* início da ingestão de `ObservationMicroTest`
* arquivo processado
* quantidade de registros lidos
* quantidade de registros inseridos
* erros de parsing
* erros de integridade
* tempo de execução

## README

Atualizar com:

* nova ordem da pipeline
* sétima fase: observações laboratoriais e microbiologia
* descrição da tabela `observation_micro_test`
* relacionamento com `patient`, `specimen` e `encounter`
* observação de que `encounter` é opcional
* instruções de execução
* instruções de testes
* referência ao `TABLE_RELATIONSHIPS.md`

## CHANGELOG

Atualizar com:

* suporte a `MimicObservationMicroTest`
* criação da tabela `observation_micro_test`
* criação das FKs para `patient`, `specimen` e `encounter`
* atualização da ordem da pipeline
* atualização do README
* atualização do TABLE_RELATIONSHIPS
* inclusão de testes unitários

## Qualidade

Manter:

* type hints completos
* docstrings em português
* funções pequenas e coesas
* tratamento explícito de exceções
* configurações em YAML
* credenciais apenas no `.env`
* compatibilidade com `uv`
* testes com `pytest`

## Execução

A ingestão completa deve continuar executando com:

```bash
python -m src.main
```

A execução deve resetar toda a estrutura e carregar todos os arquivos novamente, respeitando a ordem definida.
