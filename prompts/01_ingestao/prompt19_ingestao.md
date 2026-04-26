Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

18. `./data/MimicObservationMicroOrg.ndjson.gz`

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

## Novo recurso: ObservationMicroOrg

Campos observados:

- `id`
- `status`
- `subject.reference`
- `code.coding[*].code`
- `code.coding[*].system`
- `code.coding[*].display`
- `category[*].coding[*].code`
- `category[*].coding[*].system`
- `category[*].coding[*].display`
- `effectiveDateTime`
- `valueString`
- `derivedFrom[*].reference`
- `hasMember[*].reference`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `observation_micro_org.patient_id -> patient.id`
- `observation_micro_org.derived_from_observation_micro_test_id -> observation_micro_test.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `derivedFrom[*].reference = "Observation/<observation_micro_test_id>"`

Como `derivedFrom` aponta para uma observação microbiológica de teste já importada na etapa 17, mapear o primeiro valor válido para `observation_micro_test`.

## Modelagem

Criar tabela `observation_micro_org` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `derived_from_observation_micro_test_id` FK nullable para `observation_micro_test.id`
- `status`
- `organism_code`
- `organism_code_system`
- `organism_code_display`
- `category_code`
- `category_system`
- `category_display`
- `effective_at`
- `value_string`

Criar tabela auxiliar `observation_micro_org_has_member` com:

- `observation_micro_org_id` FK para `observation_micro_org.id`
- `member_observation_id`

Não criar FK em `member_observation_id` ainda, porque os membros podem apontar para observações de susceptibilidade que ainda não foram ingeridas nesta etapa.

Não carregar:

- `resourceType`
- `meta.profile`

Não criar tabelas auxiliares para:

- `observation_micro_org_code_coding`
- `observation_micro_org_category_coding`
- `observation_micro_org_meta_profile`

Para listas, usar o primeiro valor não vazio e válido, exceto `hasMember`, que deve gerar múltiplas linhas na tabela auxiliar.

## Extração

Mapear:

- `id` -> `id`
- `subject.reference` -> `patient_id`
- `derivedFrom[*].reference` -> `derived_from_observation_micro_test_id`
- `status` -> `status`
- `code.coding[*].code` -> `organism_code`
- `code.coding[*].system` -> `organism_code_system`
- `code.coding[*].display` -> `organism_code_display`
- `category[*].coding[*].code` -> `category_code`
- `category[*].coding[*].system` -> `category_system`
- `category[*].coding[*].display` -> `category_display`
- `effectiveDateTime` -> `effective_at`
- `valueString` -> `value_string`

Para `hasMember[*].reference`, extrair o ID de `Observation/<id>` e inserir em `observation_micro_org_has_member.member_observation_id`.

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

- `./config/ingestion/observation_micro_org.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/observation_micro_org_transformer.py`
- `src/ingestion/loaders/observation_micro_org_loader.py`
- `src/pipelines/ingest_observation_micro_org.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_observation_micro_org_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### observationMicroOrg com patient e observationMicroTest

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_micro_org.patient_id
        |
+--------------------------+
| observation_micro_org    |
|--------------------------|
| id (PK)                  |
| patient_id               |
| derived_from_test_id     |
| organism_code            |
| effective_at             |
| value_string             |
+--------------------------+
        |
        | observation_micro_org.derived_from_observation_micro_test_id
        v
+--------------------------+
| observation_micro_test   |
|--------------------------|
| id (PK)                  |
| patient_id               |
| specimen_id              |
| encounter_id             |
+--------------------------+
````

Adicionar também seção para hasMember:

```text
+--------------------------+
| observation_micro_org    |
|--------------------------|
| id (PK)                  |
+--------------------------+
        |
        | observation_micro_org_has_member.observation_micro_org_id
        v
+--------------------------------+
| observation_micro_org_has_member|
|--------------------------------|
| observation_micro_org_id        |
| member_observation_id          |
+--------------------------------+
```

Explicar que `member_observation_id` ainda não tem FK porque pode apontar para observações microbiológicas futuras ainda não ingeridas.

## Testes de unidade

Criar testes para `observation_micro_org_transformer`.

Cobrir:

* registro válido com:

  * `subject.reference`
  * `derivedFrom.reference`
  * `hasMember.reference`
  * `status`
  * `code.coding`
  * `category.coding`
  * `effectiveDateTime`
  * `valueString`
* registro sem `derivedFrom`
* registro sem `hasMember`
* registro sem `valueString`
* referência inválida em `subject`
* referência inválida em `derivedFrom`
* referência inválida em `hasMember`
* garantia de que a tabela principal simplificada é retornada corretamente
* garantia de que `observation_micro_org_has_member` é montada corretamente

Atualizar testes do parser FHIR para referência `Observation`.

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar:

* início da ingestão de `ObservationMicroOrg`
* arquivo processado
* quantidade de registros lidos
* quantidade de registros inseridos em `observation_micro_org`
* quantidade de registros inseridos em `observation_micro_org_has_member`
* erros de parsing
* erros de integridade
* tempo de execução

## README

Atualizar com:

* nova ordem da pipeline
* sétima fase: observações laboratoriais e microbiologia
* descrição da tabela `observation_micro_org`
* descrição da tabela `observation_micro_org_has_member`
* relacionamento com `patient`
* relacionamento com `observation_micro_test`
* observação sobre `hasMember` sem FK nesta etapa
* instruções de execução
* instruções de testes
* referência ao `TABLE_RELATIONSHIPS.md`

## CHANGELOG

Atualizar com:

* suporte a `MimicObservationMicroOrg`
* criação da tabela `observation_micro_org`
* criação da tabela `observation_micro_org_has_member`
* criação das FKs para `patient` e `observation_micro_test`
* suporte a parser FHIR para `Observation/<id>`
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