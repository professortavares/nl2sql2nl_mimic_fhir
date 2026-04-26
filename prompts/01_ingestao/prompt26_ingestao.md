Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

25. `./data/MimicMedicationDispense.ndjson.gz`

Esta entrega inicia a nona e última fase de ingestão.

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
23. MimicObservationED
24. MimicObservationVitalSignsED
25. MimicMedicationDispense

## Novo recurso: MedicationDispense

Campos observados:

- `id`
- `status`
- `context.reference`
- `subject.reference`
- `identifier[*].value`
- `dosageInstruction[*].route.coding[*].code`
- `dosageInstruction[*].timing.code.coding[*].code`
- `authorizingPrescription[*].reference`
- `medicationCodeableConcept.coding[*].code`
- `medicationCodeableConcept.coding[*].system`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `medication_dispense.patient_id -> patient.id`
- `medication_dispense.encounter_id -> encounter.id`
- `medication_dispense.medication_request_id -> medication_request.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `context.reference = "Encounter/<encounter_id>"`
- `authorizingPrescription[*].reference = "MedicationRequest/<medication_request_id>"`

Não criar FK para `medication`, pois o arquivo usa `medicationCodeableConcept`, não `medicationReference`.

## Modelagem

Criar tabela `medication_dispense` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `encounter_id` FK nullable para `encounter.id`
- `medication_request_id` FK nullable para `medication_request.id`
- `status`
- `identifier`
- `medication_code`
- `medication_code_system`
- `route_code`
- `frequency_code`

Não carregar:

- `resourceType`
- `meta.profile`

Para listas, usar o primeiro valor não vazio e válido.

## Extração

Mapear:

- `id` -> `id`
- `subject.reference` -> `patient_id`
- `context.reference` -> `encounter_id`
- `authorizingPrescription[*].reference` -> `medication_request_id`
- `status` -> `status`
- `identifier[*].value` -> `identifier`
- `medicationCodeableConcept.coding[*].code` -> `medication_code`
- `medicationCodeableConcept.coding[*].system` -> `medication_code_system`
- `dosageInstruction[*].route.coding[*].code` -> `route_code`
- `dosageInstruction[*].timing.code.coding[*].code` -> `frequency_code`

## Parser FHIR

Garantir suporte para:

- `MedicationRequest/<id>`

Manter suporte para:

- `Organization/<id>`
- `Patient/<id>`
- `Location/<id>`
- `Encounter/<id>`
- `Medication/<id>`
- `Specimen/<id>`
- `Observation/<id>`
- `Procedure/<id>`

## Arquivos

Adicionar/atualizar:

- `./config/ingestion/medication_dispense.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/medication_dispense_transformer.py`
- `src/ingestion/loaders/medication_dispense_loader.py`
- `src/pipelines/ingest_medication_dispense.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_medication_dispense_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### medicationDispense com patient, encounter e medicationRequest

```text
+----------------+
|    patient     |
+----------------+
        ^
        |
        | medication_dispense.patient_id
        |
+--------------------------+
| medication_dispense      |
|--------------------------|
| id (PK)                  |
| patient_id               |
| encounter_id             |
| medication_request_id    |
| medication_code          |
| route_code               |
| frequency_code           |
+--------------------------+
        |              |
        |              | medication_dispense.medication_request_id
        |              v
        |       +--------------------+
        |       | medication_request |
        |       +--------------------+
        |
        | medication_dispense.encounter_id
        v
+----------------+
|   encounter    |
+----------------+
````

Atualizar também a visão consolidada.

## Testes de unidade

Criar testes para `medication_dispense_transformer`.

Cobrir:

* registro válido com `subject`, `context`, `authorizingPrescription`, `identifier`, `dosageInstruction` e `medicationCodeableConcept`
* registro sem `context`
* registro sem `authorizingPrescription`
* registro sem `dosageInstruction`
* registro sem `medicationCodeableConcept`
* referência inválida em `subject`
* referência inválida em `context`
* referência inválida em `authorizingPrescription`
* garantia de que apenas as colunas simplificadas são retornadas

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar início, arquivo processado, registros lidos/inseridos, erros e tempo de execução.

## README e CHANGELOG

Atualizar ambos com:

* início da nona e última fase
* suporte a `MimicMedicationDispense`
* criação da tabela `medication_dispense`
* FKs para `patient`, `encounter` e `medication_request`
* observação de que não há FK para `medication`, pois o arquivo usa `medicationCodeableConcept`
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
