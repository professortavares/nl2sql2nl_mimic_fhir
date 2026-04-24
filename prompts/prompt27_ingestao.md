Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Adicionar ingestão do arquivo:

26. `./data/MimicMedicationDispenseED.ndjson.gz`

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

## Novo recurso: MedicationDispenseED

Campos observados:

- `id`
- `status`
- `context.reference`
- `subject.reference`
- `whenHandedOver`
- `medicationCodeableConcept.text`
- `medicationCodeableConcept.coding[*].code`
- `medicationCodeableConcept.coding[*].system`
- `meta.profile`
- `resourceType`

## Relacionamentos obrigatórios

Criar foreign keys:

- `medication_dispense_ed.patient_id -> patient.id`
- `medication_dispense_ed.encounter_id -> encounter.id`

As referências vêm de:

- `subject.reference = "Patient/<patient_id>"`
- `context.reference = "Encounter/<encounter_id>"`

Não criar FK para `medication_request`, pois o arquivo não possui `authorizingPrescription`.

Não criar FK para `medication`, pois o arquivo usa `medicationCodeableConcept`, não `medicationReference`.

## Modelagem

Criar tabela `medication_dispense_ed` com:

- `id` PK
- `patient_id` FK nullable para `patient.id`
- `encounter_id` FK nullable para `encounter.id`
- `status`
- `when_handed_over`
- `medication_text`
- `medication_code`
- `medication_code_system`

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
- `whenHandedOver` -> `when_handed_over`
- `medicationCodeableConcept.text` -> `medication_text`
- `medicationCodeableConcept.coding[*].code` -> `medication_code`
- `medicationCodeableConcept.coding[*].system` -> `medication_code_system`

## Arquivos

Adicionar/atualizar:

- `./config/ingestion/medication_dispense_ed.yaml`
- `./config/pipeline/resources.yaml`
- `src/ingestion/transformers/medication_dispense_ed_transformer.py`
- `src/ingestion/loaders/medication_dispense_ed_loader.py`
- `src/pipelines/ingest_medication_dispense_ed.py`
- `src/pipelines/ingest_all.py`
- `src/db/models.py`
- `src/db/schema.py`
- `README.md`
- `CHANGELOG.md`
- `TABLE_RELATIONSHIPS.md`
- `tests/unit/test_medication_dispense_ed_transformer.py`

## TABLE_RELATIONSHIPS.md

Adicionar seção:

### medicationDispenseED com patient e encounter

```text
+----------------+
|    patient     |
+----------------+
        ^
        |
        | medication_dispense_ed.patient_id
        |
+--------------------------+
| medication_dispense_ed   |
|--------------------------|
| id (PK)                  |
| patient_id               |
| encounter_id             |
| medication_text          |
| medication_code          |
| when_handed_over         |
+--------------------------+
        |
        | medication_dispense_ed.encounter_id
        v
+----------------+
|   encounter    |
+----------------+
````

Atualizar também a visão consolidada.

## Testes de unidade

Criar testes para `medication_dispense_ed_transformer`.

Cobrir:

* registro válido com `subject`, `context`, `whenHandedOver` e `medicationCodeableConcept`
* registro sem `context`
* registro sem `whenHandedOver`
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

* suporte a `MimicMedicationDispenseED`
* criação da tabela `medication_dispense_ed`
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
