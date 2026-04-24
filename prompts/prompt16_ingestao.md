Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

15. `./data/MimicProcedureICU.ndjson.gz`

Esta entrega dá continuidade à sexta fase de ingestão: procedimentos.

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

## Novo recurso: ProcedureICU

Campos observados:

- `id`
- `status`
- `subject.reference`
- `encounter.reference`
- `code.coding[*].code`
- `code.coding[*].system`
- `code.coding[*].display`
- `category.coding[*].code`
- `category.coding[*].system`
- `performedPeriod.start`
- `performedPeriod.end`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `procedure_icu.patient_id -> patient.id`
- `procedure_icu.encounter_id -> encounter.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `encounter.reference = "Encounter/<encounter_id>"`

Não criar FK direta para `procedure`, `procedure_ed`, `encounter_icu` ou outras tabelas sem referência explícita no arquivo.

## Modelagem

Criar tabela `procedure_icu` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `encounter_id` FK nullable para `encounter.id`
- `status`
- `procedure_code`
- `procedure_code_system`
- `procedure_code_display`
- `category_code`
- `category_system`
- `performed_start`
- `performed_end`

Não carregar:

- `resourceType`
- `meta.profile`

Não criar tabelas auxiliares para:

- `procedure_icu_code_coding`
- `procedure_icu_category_coding`
- `procedure_icu_meta_profile`

Para listas como `code.coding[*]` e `category.coding[*]`, usar o primeiro valor não vazio e válido.

## Extração

Mapear:

- `id` -> `id`
- `subject.reference` -> `patient_id`
- `encounter.reference` -> `encounter_id`
- `status` -> `status`
- `code.coding[*].code` -> `procedure_code`
- `code.coding[*].system` -> `procedure_code_system`
- `code.coding[*].display` -> `procedure_code_display`
- `category.coding[*].code` -> `category_code`
- `category.coding[*].system` -> `category_system`
- `performedPeriod.start` -> `performed_start`
- `performedPeriod.end` -> `performed_end`

## Arquivos a criar/alterar

Adicionar ou atualizar:

- `./config/ingestion/procedure_icu.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/procedure_icu_transformer.py`
- `src/ingestion/loaders/procedure_icu_loader.py`
- `src/pipelines/ingest_procedure_icu.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_procedure_icu_transformer.py`

## TABLE_RELATIONSHIPS.md

Atualizar o arquivo mantendo diagramas ASCII segmentados.

Adicionar seção:

### procedureICU com patient e encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | procedure_icu.patient_id
        |
+----------------+
| procedure_icu  |
|----------------|
| id (PK)        |
| patient_id     |
| encounter_id   |
| procedure_code |
| performed_start|
| performed_end  |
+----------------+
        |
        | procedure_icu.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
````

Atualizar também a visão consolidada, se existir.

## Testes de unidade

Criar testes para `procedure_icu_transformer`.

Cobrir:

* registro válido com:

  * `subject.reference`
  * `encounter.reference`
  * `status`
  * `code.coding`
  * `category.coding`
  * `performedPeriod.start`
  * `performedPeriod.end`
* registro sem `encounter`
* registro sem `code`
* registro sem `category`
* registro sem `performedPeriod`
* referência inválida em `subject`
* referência inválida em `encounter`
* garantia de que apenas as colunas simplificadas são retornadas

Atualizar testes do parser FHIR, se necessário.

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar:

* início da ingestão de `ProcedureICU`
* arquivo processado
* quantidade de registros lidos
* quantidade de registros inseridos
* erros de parsing
* erros de integridade
* tempo de execução

## README

Atualizar com:

* nova ordem da pipeline
* sexta fase: procedimentos
* descrição da tabela `procedure_icu`
* relacionamento com `patient` e `encounter`
* diferença entre `performedDateTime` de Procedure/ProcedureED e `performedPeriod` de ProcedureICU
* instruções de execução
* instruções de testes
* referência ao `TABLE_RELATIONSHIPS.md`

## CHANGELOG

Atualizar com:

* suporte a `MimicProcedureICU`
* criação da tabela `procedure_icu`
* criação das FKs para `patient` e `encounter`
* suporte a `performedPeriod.start/end`
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
