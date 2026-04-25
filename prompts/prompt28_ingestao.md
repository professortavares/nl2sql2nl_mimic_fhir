Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

27. `./data/MimicMedicationAdministration.ndjson.gz`

Esta entrega dá continuidade à nona e última fase: eventos de medicação.

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
26. MimicMedicationDispenseED
27. MimicMedicationAdministration

## Novo recurso: MedicationAdministration

Campos observados:

- `id`
- `status`
- `subject.reference`
- `context.reference`
- `request.reference`
- `effectiveDateTime`
- `medicationCodeableConcept.coding[*].code`
- `medicationCodeableConcept.coding[*].system`
- `dosage.text`
- `dosage.dose.value`
- `dosage.dose.unit`
- `dosage.dose.code`
- `dosage.dose.system`
- `dosage.method.coding[*].code`
- `dosage.method.coding[*].system`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `medication_administration.patient_id -> patient.id`
- `medication_administration.encounter_id -> encounter.id`
- `medication_administration.medication_request_id -> medication_request.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `context.reference = "Encounter/<encounter_id>"`
- `request.reference = "MedicationRequest/<medication_request_id>"`

Não criar FK para `medication`, pois o arquivo usa `medicationCodeableConcept`, não `medicationReference`.

`encounter_id` e `medication_request_id` devem ser nullable.

## Modelagem

Criar tabela `medication_administration` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `encounter_id` FK nullable para `encounter.id`
- `medication_request_id` FK nullable para `medication_request.id`
- `status`
- `effective_at`
- `medication_code`
- `medication_code_system`
- `dosage_text`
- `dose_value`
- `dose_unit`
- `dose_code`
- `dose_system`
- `method_code`
- `method_system`

Não carregar:

- `resourceType`
- `meta.profile`

Para listas, usar o primeiro valor não vazio e válido.

## Extração

Mapear:

- `id` -> `id`
- `subject.reference` -> `patient_id`
- `context.reference` -> `encounter_id`
- `request.reference` -> `medication_request_id`
- `status` -> `status`
- `effectiveDateTime` -> `effective_at`
- `medicationCodeableConcept.coding[*].code` -> `medication_code`
- `medicationCodeableConcept.coding[*].system` -> `medication_code_system`
- `dosage.text` -> `dosage_text`
- `dosage.dose.value` -> `dose_value`
- `dosage.dose.unit` -> `dose_unit`
- `dosage.dose.code` -> `dose_code`
- `dosage.dose.system` -> `dose_system`
- `dosage.method.coding[*].code` -> `method_code`
- `dosage.method.coding[*].system` -> `method_system`

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

- `./config/ingestion/medication_administration.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/medication_administration_transformer.py`
- `src/ingestion/loaders/medication_administration_loader.py`
- `src/pipelines/ingest_medication_administration.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_medication_administration_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### medicationAdministration com patient, encounter e medicationRequest

```text
+----------------+
|    patient     |
+----------------+
        ^
        |
        | medication_administration.patient_id
        |
+-----------------------------+
| medication_administration   |
|-----------------------------|
| id (PK)                     |
| patient_id                  |
| encounter_id                |
| medication_request_id       |
| medication_code             |
| effective_at                |
| dose_value                  |
| dose_unit                   |
+-----------------------------+
        |              |
        |              | medication_administration.medication_request_id
        |              v
        |       +--------------------+
        |       | medication_request |
        |       +--------------------+
        |
        | medication_administration.encounter_id
        v
+----------------+
|   encounter    |
+----------------+
````

Atualizar também a visão consolidada.

## Testes de unidade

Criar testes para `medication_administration_transformer`.

Cobrir:

* registro válido com `subject`, `context`, `request`, `effectiveDateTime`, `medicationCodeableConcept` e `dosage`
* registro sem `context`
* registro sem `request`
* registro sem `dosage`
* registro sem `medicationCodeableConcept`
* referência inválida em `subject`
* referência inválida em `context`
* referência inválida em `request`
* garantia de que apenas as colunas simplificadas são retornadas

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar início, arquivo processado, registros lidos/inseridos, erros e tempo de execução.

## README e CHANGELOG

Atualizar ambos com:

* suporte a `MimicMedicationAdministration`
* criação da tabela `medication_administration`
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
