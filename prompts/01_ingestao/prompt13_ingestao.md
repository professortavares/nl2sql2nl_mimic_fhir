Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

12. `./data/MimicConditionED.ndjson.gz`

Esta entrega continua a quinta fase de ingestão.

## Ordem completa da pipeline
A pipeline deve executar obrigatoriamente nesta ordem:

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

A ingestão deve continuar sendo feita por uma pipeline orquestrada de recursos.

## Novo recurso: MimicConditionED

Arquivo:

```bash
./data/MimicConditionED.ndjson.gz
````

O arquivo é um NDJSON compactado com gzip e contém recursos FHIR do tipo `Condition`.

## Estrutura observada

Campos observados:

* `id`
* `code.coding[*].code`
* `code.coding[*].system`
* `code.coding[*].display`
* `meta.profile`
* `subject.reference`
* `category[*].coding[*].code`
* `category[*].coding[*].system`
* `category[*].coding[*].display`
* `encounter.reference`
* `resourceType`

## Relacionamentos identificados

Criar foreign keys para:

* `condition_ed.patient_id -> patient.id`
* `condition_ed.encounter_id -> encounter.id`

As referências vêm de:

* `subject.reference = "Patient/<patient_id>"`
* `encounter.reference = "Encounter/<encounter_id>"`

Não criar relacionamento com `condition`, `encounter_ed`, `organization`, `location` ou `medication` sem evidência explícita no arquivo.

## Modelagem obrigatória

Criar tabela `condition_ed` com os campos:

* `id` PK
* `patient_id` FK nullable para `patient.id`
* `encounter_id` FK nullable para `encounter.id`
* `condition_code`
* `condition_code_system`
* `condition_code_display`
* `category_code`
* `category_system`
* `category_display`

Não carregar:

* `resourceType`
* `meta.profile`

Não criar tabelas auxiliares para:

* `condition_ed_code_coding`
* `condition_ed_category_coding`
* `condition_ed_meta_profile`

Para listas como `code.coding[*]` e `category[*].coding[*]`, usar o primeiro valor não vazio e válido encontrado.

## Regras de extração

Extrair:

* `id` -> `id`
* `subject.reference` -> `patient_id`
* `encounter.reference` -> `encounter_id`
* `code.coding[*].code` -> `condition_code`
* `code.coding[*].system` -> `condition_code_system`
* `code.coding[*].display` -> `condition_code_display`
* `category[*].coding[*].code` -> `category_code`
* `category[*].coding[*].system` -> `category_system`
* `category[*].coding[*].display` -> `category_display`

## Arquivos/configurações

Adicionar ou atualizar:

* `./config/ingestion/condition_ed.yaml`
* `./config/pipeline/resources.yaml`
* `src/ingestion/transformers/condition_ed_transformer.py`
* `src/ingestion/loaders/condition_ed_loader.py`
* `src/pipelines/ingest_condition_ed.py`
* `src/pipelines/ingest_all.py`
* `src/db/models.py`
* `src/db/schema.py`
* `README.md`
* `CHANGELOG.md`
* `TABLE_RELATIONSHIPS.md`
* `tests/unit/test_condition_ed_transformer.py`

## TABLE_RELATIONSHIPS.md

Atualizar o arquivo na raiz do projeto.

Manter a estratégia de vários diagramas ASCII pequenos.

Adicionar uma seção nova:

### conditionED com patient e encounter

Mostrar:

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | condition_ed.patient_id
        |
+----------------+
| condition_ed   |
|----------------|
| id (PK)        |
| patient_id     |
| encounter_id   |
| condition_code |
+----------------+
        |
        | condition_ed.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
```

Também atualizar a visão consolidada, se existir.

## Testes de unidade obrigatórios

Criar testes para `condition_ed_transformer`.

Cobrir:

* registro válido com:

  * `subject.reference`
  * `encounter.reference`
  * `code.coding`
  * `category.coding`
* registro sem `encounter`
* registro sem `category`
* registro sem `code`
* referência inválida em `subject`
* referência inválida em `encounter`
* garantia de que apenas as colunas simplificadas são retornadas

Também atualizar testes do parser FHIR, se necessário.

## Logging

Manter logging em arquivo dentro de:

```bash
./logs/ingestion.log
```

Registrar:

* início da ingestão de `ConditionED`
* arquivo processado
* quantidade de registros lidos
* quantidade de registros inseridos
* erros de parsing
* erros de integridade
* tempo de execução

## README

Atualizar o README com:

* nova ordem da pipeline
* quinta fase contendo `Condition` e `ConditionED`
* descrição da tabela `condition_ed`
* relacionamento com `patient` e `encounter`
* instruções para executar ingestão
* instruções para executar testes
* referência ao `TABLE_RELATIONSHIPS.md`

## CHANGELOG

Atualizar o CHANGELOG com:

* suporte a `MimicConditionED`
* criação da tabela `condition_ed`
* criação das FKs para `patient` e `encounter`
* atualização da ordem da pipeline
* atualização do README
* atualização do TABLE_RELATIONSHIPS
* inclusão de testes unitários

## Qualidade de código

Todo código deve manter:

* type hints completos
* docstrings em português
* funções pequenas e coesas
* tratamento explícito de exceções
* ausência de hardcoded desnecessário
* configurações em YAML sempre que possível
* credenciais apenas no `.env`
* compatibilidade com `uv`
* testes com `pytest`

## Execução

A ingestão completa deve continuar executando com:

```bash
python -m src.main
```

ou entrypoint equivalente já existente.

A execução deve resetar toda a estrutura e carregar todos os arquivos novamente, respeitando a ordem definida.
