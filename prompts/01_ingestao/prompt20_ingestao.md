Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

19. `./data/MimicObservationMicroSusc.ndjson.gz`

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
18. MimicObservationMicroOrg
19. MimicObservationMicroSusc

## Novo recurso: ObservationMicroSusc

Campos observados:

- `id`
- `status`
- `subject.reference`
- `derivedFrom[*].reference`
- `code.coding[*].code`
- `code.coding[*].system`
- `code.coding[*].display`
- `category[*].coding[*].code`
- `category[*].coding[*].system`
- `category[*].coding[*].display`
- `effectiveDateTime`
- `identifier[*].value`
- `valueCodeableConcept.coding[*].code`
- `valueCodeableConcept.coding[*].system`
- `valueCodeableConcept.coding[*].display`
- `extension[*]` com URL `dilution-details`
- `extension[*].valueQuantity.value`
- `extension[*].valueQuantity.comparator`
- `note[*].text`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `observation_micro_susc.patient_id -> patient.id`
- `observation_micro_susc.derived_from_observation_micro_org_id -> observation_micro_org.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `derivedFrom[*].reference = "Observation/<observation_micro_org_id>"`

Como `derivedFrom` aponta para observação microbiológica de organismo já importada na etapa 18, mapear o primeiro valor válido para `observation_micro_org`.

## Modelagem

Criar tabela `observation_micro_susc` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `derived_from_observation_micro_org_id` FK nullable para `observation_micro_org.id`
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

Não carregar:

- `resourceType`
- `meta.profile`

Não criar tabelas auxiliares para:

- `observation_micro_susc_code_coding`
- `observation_micro_susc_category_coding`
- `observation_micro_susc_value_codeable_concept`
- `observation_micro_susc_note`
- `observation_micro_susc_meta_profile`

Para listas, usar o primeiro valor não vazio e válido.

## Extração

Mapear:

- `id` -> `id`
- `subject.reference` -> `patient_id`
- `derivedFrom[*].reference` -> `derived_from_observation_micro_org_id`
- `status` -> `status`
- `code.coding[*].code` -> `antibiotic_code`
- `code.coding[*].system` -> `antibiotic_code_system`
- `code.coding[*].display` -> `antibiotic_code_display`
- `category[*].coding[*].code` -> `category_code`
- `category[*].coding[*].system` -> `category_system`
- `category[*].coding[*].display` -> `category_display`
- `effectiveDateTime` -> `effective_at`
- `identifier[*].value` -> `identifier`
- `valueCodeableConcept.coding[*].code` -> `interpretation_code`
- `valueCodeableConcept.coding[*].system` -> `interpretation_system`
- `valueCodeableConcept.coding[*].display` -> `interpretation_display`
- extensão com URL `http://mimic.mit.edu/fhir/mimic/StructureDefinition/dilution-details`, campo `valueQuantity.value` -> `dilution_value`
- extensão com URL `http://mimic.mit.edu/fhir/mimic/StructureDefinition/dilution-details`, campo `valueQuantity.comparator` -> `dilution_comparator`
- `note[*].text` -> `note`

## Parser FHIR

Garantir suporte para referências:

- `Observation/<id>`

Manter suporte para:

- `Organization/<id>`
- `Patient/<id>`
- `Location/<id>`
- `Encounter/<id>`
- `Medication/<id>`
- `Specimen/<id>`

## Arquivos a criar/alterar

Adicionar ou atualizar:

- `./config/ingestion/observation_micro_susc.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/observation_micro_susc_transformer.py`
- `src/ingestion/loaders/observation_micro_susc_loader.py`
- `src/pipelines/ingest_observation_micro_susc.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_observation_micro_susc_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### observationMicroSusc com patient e observationMicroOrg

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_micro_susc.patient_id
        |
+--------------------------+
| observation_micro_susc   |
|--------------------------|
| id (PK)                  |
| patient_id               |
| derived_from_org_id      |
| antibiotic_code          |
| interpretation_code      |
| dilution_value           |
| dilution_comparator      |
+--------------------------+
        |
        | observation_micro_susc.derived_from_observation_micro_org_id
        v
+--------------------------+
| observation_micro_org    |
|--------------------------|
| id (PK)                  |
| patient_id               |
| derived_from_test_id     |
| organism_code            |
+--------------------------+
````

Atualizar também a visão consolidada, se existir.

## Testes de unidade

Criar testes para `observation_micro_susc_transformer`.

Cobrir:

* registro válido com:

  * `subject.reference`
  * `derivedFrom.reference`
  * `status`
  * `code.coding`
  * `category.coding`
  * `effectiveDateTime`
  * `identifier`
  * `valueCodeableConcept`
  * extensão `dilution-details` com `value`
  * extensão `dilution-details` com `comparator`
  * `note`
* registro sem `derivedFrom`
* registro sem `valueCodeableConcept`
* registro sem extensão `dilution-details`
* registro sem `note`
* referência inválida em `subject`
* referência inválida em `derivedFrom`
* garantia de que apenas as colunas simplificadas são retornadas

Atualizar testes do parser FHIR para referência `Observation`, se ainda não existir.

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar:

* início da ingestão de `ObservationMicroSusc`
* arquivo processado
* quantidade de registros lidos
* quantidade de registros inseridos em `observation_micro_susc`
* erros de parsing
* erros de integridade
* tempo de execução

## README

Atualizar com:

* nova ordem da pipeline
* sétima fase: observações laboratoriais e microbiologia
* descrição da tabela `observation_micro_susc`
* relacionamento com `patient`
* relacionamento com `observation_micro_org`
* explicação de que `derivedFrom` liga susceptibilidade ao organismo identificado
* instruções de execução
* instruções de testes
* referência ao `TABLE_RELATIONSHIPS.md`

## CHANGELOG

Atualizar com:

* suporte a `MimicObservationMicroSusc`
* criação da tabela `observation_micro_susc`
* criação das FKs para `patient` e `observation_micro_org`
* suporte à extração da extensão `dilution-details`
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
