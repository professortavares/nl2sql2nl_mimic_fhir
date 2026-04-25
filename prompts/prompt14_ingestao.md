Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

13. `./data/MimicProcedure.ndjson.gz`

Esta entrega inicia a sexta fase de ingestão: procedimentos.

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

## Novo recurso: Procedure

Campos observados:

- `id`
- `code.coding[*].code`
- `code.coding[*].system`
- `code.coding[*].display`
- `meta.profile`
- `status`
- `subject.reference`
- `encounter.reference`
- `performedDateTime`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `procedure.patient_id -> patient.id`
- `procedure.encounter_id -> encounter.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `encounter.reference = "Encounter/<encounter_id>"`

Não criar FKs extras sem referência explícita no arquivo.

## Modelagem

Criar tabela `procedure` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `encounter_id` FK nullable para `encounter.id`
- `status`
- `procedure_code`
- `procedure_code_system`
- `procedure_code_display`
- `performed_at`

Não carregar:

- `resourceType`
- `meta.profile`

Não criar tabelas auxiliares para:

- `procedure_code_coding`
- `procedure_meta_profile`

Para `code.coding[*]`, usar o primeiro valor não vazio e válido.

## Extração

Mapear:

- `id` -> `id`
- `subject.reference` -> `patient_id`
- `encounter.reference` -> `encounter_id`
- `status` -> `status`
- `code.coding[*].code` -> `procedure_code`
- `code.coding[*].system` -> `procedure_code_system`
- `code.coding[*].display` -> `procedure_code_display`
- `performedDateTime` -> `performed_at`

## Arquivos a criar/alterar

Adicionar ou atualizar:

- `./config/ingestion/procedure.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/procedure_transformer.py`
- `src/ingestion/loaders/procedure_loader.py`
- `src/pipelines/ingest_procedure.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_procedure_transformer.py`

## TABLE_RELATIONSHIPS.md

Atualizar o arquivo mantendo diagramas ASCII segmentados.

Adicionar seção:

### procedure com patient e encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | procedure.patient_id
        |
+----------------+
|   procedure    |
|----------------|
| id (PK)        |
| patient_id     |
| encounter_id   |
| procedure_code |
| performed_at   |
+----------------+
        |
        | procedure.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
````

Atualizar também a visão consolidada, se existir.

## Testes de unidade

Criar testes para `procedure_transformer`.

Cobrir:

* registro válido com:

  * `subject.reference`
  * `encounter.reference`
  * `status`
  * `code.coding`
  * `performedDateTime`
* registro sem `encounter`
* registro sem `code`
* registro sem `performedDateTime`
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

* início da ingestão de `Procedure`
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
* descrição da tabela `procedure`
* relacionamento com `patient` e `encounter`
* instruções de execução
* instruções de testes
* referência ao `TABLE_RELATIONSHIPS.md`

## CHANGELOG

Atualizar com:

* início da sexta fase de ingestão
* suporte a `MimicProcedure`
* criação da tabela `procedure`
* criação das FKs para `patient` e `encounter`
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
