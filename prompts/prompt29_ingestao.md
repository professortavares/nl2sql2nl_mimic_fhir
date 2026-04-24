Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

28. `./data/MimicMedicationAdministrationICU.ndjson.gz`

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
28. MimicMedicationAdministrationICU

## Novo recurso: MedicationAdministrationICU

Campos observados:

- `id`
- `status`
- `subject.reference`
- `context.reference`
- `effectiveDateTime`
- `category.coding[*].code`
- `category.coding[*].system`
- `medicationCodeableConcept.coding[*].code`
- `medicationCodeableConcept.coding[*].system`
- `medicationCodeableConcept.coding[*].display`
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

- `medication_administration_icu.patient_id -> patient.id`
- `medication_administration_icu.encounter_id -> encounter.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `context.reference = "Encounter/<encounter_id>"`

Não criar FK para `medication_request`, pois o arquivo não possui `request.reference`.

Não criar FK para `medication`, pois o arquivo usa `medicationCodeableConcept`, não `medicationReference`.

## Modelagem

Criar tabela `medication_administration_icu` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `encounter_id` FK nullable para `encounter.id`
- `status`
- `effective_at`
- `category_code`
- `category_system`
- `medication_code`
- `medication_code_system`
- `medication_code_display`
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
- `status` -> `status`
- `effectiveDateTime` -> `effective_at`
- `category.coding[*].code` -> `category_code`
- `category.coding[*].system` -> `category_system`
- `medicationCodeableConcept.coding[*].code` -> `medication_code`
- `medicationCodeableConcept.coding[*].system` -> `medication_code_system`
- `medicationCodeableConcept.coding[*].display` -> `medication_code_display`
- `dosage.dose.value` -> `dose_value`
- `dosage.dose.unit` -> `dose_unit`
- `dosage.dose.code` -> `dose_code`
- `dosage.dose.system` -> `dose_system`
- `dosage.method.coding[*].code` -> `method_code`
- `dosage.method.coding[*].system` -> `method_system`

## Arquivos

Adicionar/atualizar:

- `./config/ingestion/medication_administration_icu.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/medication_administration_icu_transformer.py`
- `src/ingestion/loaders/medication_administration_icu_loader.py`
- `src/pipelines/ingest_medication_administration_icu.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_medication_administration_icu_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### medicationAdministrationICU com patient e encounter

```text
+----------------+
|    patient     |
+----------------+
        ^
        |
        | medication_administration_icu.patient_id
        |
+---------------------------------+
| medication_administration_icu   |
|---------------------------------|
| id (PK)                         |
| patient_id                      |
| encounter_id                    |
| medication_code                 |
| effective_at                    |
| dose_value                      |
| dose_unit                       |
| method_code                     |
+---------------------------------+
        |
        | medication_administration_icu.encounter_id
        v
+----------------+
|   encounter    |
+----------------+
````

Atualizar também a visão consolidada.

## Testes de unidade

Criar testes para `medication_administration_icu_transformer`.

Cobrir:

* registro válido com `subject`, `context`, `effectiveDateTime`, `category`, `medicationCodeableConcept` e `dosage`
* registro sem `context`
* registro sem `category`
* registro sem `dosage`
* registro sem `medicationCodeableConcept`
* referência inválida em `subject`
* referência inválida em `context`
* garantia de que apenas as colunas simplificadas são retornadas

## Logging

Manter logs em:

```bash
./logs/ingestion.log
```

Registrar início, arquivo processado, registros lidos/inseridos, erros e tempo de execução.

## README e CHANGELOG

Atualizar ambos com:

* suporte a `MimicMedicationAdministrationICU`
* criação da tabela `medication_administration_icu`
* FKs para `patient` e `encounter`
* observação de que não há FK para `medication_request` nem `medication`
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
