Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

16. `./data/MimicObservationLabevents.ndjson.gz`

Esta entrega inicia a sétima fase de ingestão: observações laboratoriais e microbiologia.

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

## Novo recurso: ObservationLabevents

Campos observados:

- `id`
- `status`
- `subject.reference`
- `specimen.reference`
- `code.coding[*].code`
- `code.coding[*].system`
- `code.coding[*].display`
- `category[*].coding[*].code`
- `category[*].coding[*].system`
- `category[*].coding[*].display`
- `effectiveDateTime`
- `issued`
- `identifier[*].value`
- `valueQuantity.value`
- `valueQuantity.unit`
- `valueQuantity.code`
- `valueQuantity.system`
- `referenceRange[*].low.value`
- `referenceRange[*].low.unit`
- `referenceRange[*].high.value`
- `referenceRange[*].high.unit`
- `extension[*]` com URL `lab-priority` e campo `valueString`
- `note[*].text`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `observation_labevents.patient_id -> patient.id`
- `observation_labevents.specimen_id -> specimen.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `specimen.reference = "Specimen/<specimen_id>"`

Não criar FK para `encounter` sem referência explícita no arquivo.

## Modelagem

Criar tabela `observation_labevents` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `specimen_id` FK nullable para `specimen.id`
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

Não carregar:

- `resourceType`
- `meta.profile`

Não criar tabelas auxiliares para:

- `observation_labevents_code_coding`
- `observation_labevents_category_coding`
- `observation_labevents_reference_range`
- `observation_labevents_note`
- `observation_labevents_meta_profile`

Para listas, usar o primeiro valor não vazio e válido.

## Extração

Mapear:

- `id` -> `id`
- `subject.reference` -> `patient_id`
- `specimen.reference` -> `specimen_id`
- `status` -> `status`
- `code.coding[*].code` -> `observation_code`
- `code.coding[*].system` -> `observation_code_system`
- `code.coding[*].display` -> `observation_code_display`
- `category[*].coding[*].code` -> `category_code`
- `category[*].coding[*].system` -> `category_system`
- `category[*].coding[*].display` -> `category_display`
- `effectiveDateTime` -> `effective_at`
- `issued` -> `issued_at`
- `identifier[*].value` -> `identifier`
- `valueQuantity.value` -> `value`
- `valueQuantity.unit` -> `value_unit`
- `valueQuantity.code` -> `value_code`
- `valueQuantity.system` -> `value_system`
- `referenceRange[*].low.value` -> `reference_low_value`
- `referenceRange[*].low.unit` -> `reference_low_unit`
- `referenceRange[*].high.value` -> `reference_high_value`
- `referenceRange[*].high.unit` -> `reference_high_unit`
- extensão com URL `http://mimic.mit.edu/fhir/mimic/StructureDefinition/lab-priority`, campo `valueString` -> `lab_priority`
- `note[*].text` -> `note`

## Parser FHIR

Atualizar o parser de referências FHIR para suportar também:

- `Specimen/<id>`

Manter suporte para:

- `Organization/<id>`
- `Patient/<id>`
- `Location/<id>`
- `Encounter/<id>`
- `Medication/<id>`

## Arquivos a criar/alterar

Adicionar ou atualizar:

- `./config/ingestion/observation_labevents.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/observation_labevents_transformer.py`
- `src/ingestion/loaders/observation_labevents_loader.py`
- `src/pipelines/ingest_observation_labevents.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_observation_labevents_transformer.py`

## TABLE_RELATIONSHIPS.md

Atualizar o arquivo mantendo diagramas ASCII segmentados.

Adicionar seção:

### observationLabevents com patient e specimen

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_labevents.patient_id
        |
+--------------------------+
| observation_labevents    |
|--------------------------|
| id (PK)                  |
| patient_id               |
| specimen_id              |
| observation_code         |
| effective_at             |
| value                    |
| value_unit               |
+--------------------------+
        |
        | observation_labevents.specimen_id
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

Criar testes para `observation_labevents_transformer`.

Cobrir:

* registro válido com:

  * `subject.reference`
  * `specimen.reference`
  * `status`
  * `code.coding`
  * `category.coding`
  * `effectiveDateTime`
  * `issued`
  * `identifier`
  * `valueQuantity`
  * `referenceRange`
  * extensão `lab-priority`
  * `note`
* registro sem `specimen`
* registro sem `valueQuantity`
* registro sem `referenceRange`
* registro sem `note`
* referência inválida em `subject`
* referência inválida em `specimen`
* garantia de que apenas as colunas simplificadas são retornadas

Atualizar testes do parser FHIR para referência `Specimen`.

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar:

* início da ingestão de `ObservationLabevents`
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
* descrição da tabela `observation_labevents`
* relacionamento com `patient` e `specimen`
* observação de que `encounter` não é usado aqui por ausência de referência explícita no arquivo
* instruções de execução
* instruções de testes
* referência ao `TABLE_RELATIONSHIPS.md`

## CHANGELOG

Atualizar com:

* início da sétima fase de ingestão
* suporte a `MimicObservationLabevents`
* criação da tabela `observation_labevents`
* criação das FKs para `patient` e `specimen`
* suporte a parser FHIR para `Specimen/<id>`
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
