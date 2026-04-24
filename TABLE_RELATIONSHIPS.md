# Relacionamentos Entre Tabelas

Este documento resume a modelagem relacional criada pela pipeline de ingestão.
A leitura é segmentada em blocos menores para facilitar a navegação por relacionamento.

## Tabelas Existentes

- `organization`
- `location`
- `patient`
- `encounter`
- `encounter_location`
- `encounter_ed`
- `encounter_icu`
- `encounter_icu_location`
- `medication`
- `medication_mix`
- `medication_mix_ingredient`
- `medication_request`
- `specimen`
- `condition`
- `condition_ed`
- `procedure`
- `procedure_ed`
- `procedure_icu`
- `observation_labevents`
- `observation_micro_test`
- `observation_micro_org`
- `observation_micro_org_has_member`
- `observation_micro_susc`
- `observation_chartevents`
- `observation_datetimeevents`
- `observation_outputevents`
- `observation_ed`
- `observation_vital_signs_ed`
- `observation_vital_signs_ed_component`
- `medication_dispense`

## Foreign Keys

- `location.managing_organization_id -> organization.id`
- `patient.managing_organization_id -> organization.id`
- `encounter.patient_id -> patient.id`
- `encounter.organization_id -> organization.id`
- `encounter_location.encounter_id -> encounter.id`
- `encounter_location.location_id -> location.id`
- `encounter_ed.encounter_id -> encounter.id`
- `encounter_ed.patient_id -> patient.id`
- `encounter_ed.organization_id -> organization.id`
- `encounter_icu.encounter_id -> encounter.id`
- `encounter_icu.patient_id -> patient.id`
- `encounter_icu_location.encounter_icu_id -> encounter_icu.id`
- `encounter_icu_location.location_id -> location.id`
- `medication_mix_ingredient.medication_mix_id -> medication_mix.id`
- `medication_mix_ingredient.medication_id -> medication.id`
- `medication_request.patient_id -> patient.id`
- `medication_request.encounter_id -> encounter.id`
- `medication_request.medication_id -> medication.id`
- `specimen.patient_id -> patient.id`
- `condition.patient_id -> patient.id`
- `condition.encounter_id -> encounter.id`
- `condition_ed.patient_id -> patient.id`
- `condition_ed.encounter_id -> encounter.id`
- `procedure.patient_id -> patient.id`
- `procedure.encounter_id -> encounter.id`
- `procedure_ed.patient_id -> patient.id`
- `procedure_ed.encounter_id -> encounter.id`
- `procedure_icu.patient_id -> patient.id`
- `procedure_icu.encounter_id -> encounter.id`
- `observation_labevents.patient_id -> patient.id`
- `observation_labevents.specimen_id -> specimen.id`
- `observation_micro_test.patient_id -> patient.id`
- `observation_micro_test.specimen_id -> specimen.id`
- `observation_micro_test.encounter_id -> encounter.id`
- `observation_micro_org.patient_id -> patient.id`
- `observation_micro_org.derived_from_observation_micro_test_id -> observation_micro_test.id`
- `observation_micro_org_has_member.observation_micro_org_id -> observation_micro_org.id`
- `observation_micro_susc.patient_id -> patient.id`
- `observation_micro_susc.derived_from_observation_micro_org_id -> observation_micro_org.id`
- `observation_chartevents.patient_id -> patient.id`
- `observation_chartevents.encounter_id -> encounter.id`
- `observation_datetimeevents.patient_id -> patient.id`
- `observation_datetimeevents.encounter_id -> encounter.id`
- `observation_outputevents.patient_id -> patient.id`
- `observation_outputevents.encounter_id -> encounter.id`
- `observation_ed.patient_id -> patient.id`
- `observation_ed.encounter_id -> encounter.id`
- `observation_ed.procedure_id -> procedure.id`
- `observation_vital_signs_ed.patient_id -> patient.id`
- `observation_vital_signs_ed.encounter_id -> encounter.id`
- `observation_vital_signs_ed.procedure_id -> procedure.id`
- `observation_vital_signs_ed_component.observation_vital_signs_ed_id -> observation_vital_signs_ed.id`
- `medication_dispense.patient_id -> patient.id`
- `medication_dispense.encounter_id -> encounter.id`
- `medication_dispense.medication_request_id -> medication_request.id`

## Diagramas Segmentados

### 1) Organization e Location

```text
+----------------------+
|     organization     |
|----------------------|
| id (PK)              |
| name                 |
+----------------------+
           ^
           |
           |
+----------------------+
|       location       |
|----------------------|
| id (PK)              |
| name                 |
| managing_organization_id (FK)
+----------------------+
```

### 2) Organization e Patient

```text
+----------------------+
|     organization     |
|----------------------|
| id (PK)              |
| name                 |
+----------------------+
           ^
           |
           |
+----------------------+
|       patient        |
|----------------------|
| id (PK)              |
| gender               |
| birth_date           |
| name                 |
| identifier           |
| marital_status_coding|
| race                 |
| ethnicity            |
| birthsex             |
| managing_organization_id (FK)
+----------------------+
```

### 3) Encounter, Patient e Organization

```text
+----------------------+      +----------------------+
|     organization     |      |       patient        |
|----------------------|      |----------------------|
| id (PK)              |      | id (PK)              |
| name                 |      | ...                  |
+----------------------+      +----------------------+
           ^                             ^
           |                             |
           |                             |
           +-------------+---------------+
                         |
                         v
+----------------------+
|      encounter       |
|----------------------|
| id (PK)              |
| patient_id (FK)      |
| organization_id (FK) |
| status               |
| class_code           |
| start_date           |
| end_date             |
| priority_code        |
| service_type_code    |
| admit_source_code    |
| discharge_disposition_code |
| identifier           |
+----------------------+
```

### 4) Encounter e Location

```text
+----------------------+
|      encounter       |
|----------------------|
| id (PK)              |
| ...                  |
+----------------------+
           |
           |
           v
+----------------------+
|  encounter_location  |
|----------------------|
| encounter_id (FK)    |
| location_id (FK)     |
| start_date           |
| end_date             |
+----------------------+

+----------------------+
|       location       |
|----------------------|
| id (PK)              |
| name                 |
| managing_organization_id (FK)
+----------------------+
```

### 5) EncounterED e seus vínculos

```text
+----------------------+
|      encounter       |
|----------------------|
| id (PK)              |
| ...                  |
+----------------------+
           ^
           |
           |
+----------------------+
|    encounter_ed      |
|----------------------|
| id (PK)              |
| encounter_id (FK)    |
| patient_id (FK)      |
| organization_id (FK) |
| status               |
| class_code           |
| start_date           |
| end_date             |
| admit_source_code    |
| discharge_disposition_code |
| identifier           |
+----------------------+

+----------------------+
|       patient        |
|----------------------|
| id (PK)              |
| ...                  |
+----------------------+

+----------------------+
|     organization     |
|----------------------|
| id (PK)              |
| name                 |
+----------------------+
```

### 6) EncounterICU e seus vínculos

```text
+----------------------+
|      encounter       |
|----------------------|
| id (PK)              |
| ...                  |
+----------------------+
           ^
           |
           |
+----------------------+
|    encounter_icu     |
|----------------------|
| id (PK)              |
| encounter_id (FK)    |
| patient_id (FK)      |
| status               |
| class_code           |
| start_date           |
| end_date             |
| identifier           |
+----------------------+
           |
           |
           v
+----------------------------+
| encounter_icu_location     |
|----------------------------|
| encounter_icu_id (FK)      |
| location_id (FK)           |
| start_date                 |
| end_date                   |
+----------------------------+

+----------------------+
|       patient        |
|----------------------|
| id (PK)              |
| ...                  |
+----------------------+

+----------------------+
|       location       |
|----------------------|
| id (PK)              |
| name                 |
| managing_organization_id (FK)
+----------------------+
```

### 7) Medication como dimensão base

`Medication` continua como dimensão base de medicamentos, sem foreign keys diretas para os demais recursos clínicos nesta fase.

```text
+----------------------+
|      medication      |
|----------------------|
| id (PK)              |
| code                 |
| code_system          |
| status               |
| ndc                  |
| formulary_drug_cd    |
| name                 |
+----------------------+

Sem FK nesta fase:

medication
  -> sem vínculo direto com organization
  -> sem vínculo direto com location
  -> sem vínculo direto com patient
  -> sem vínculo direto com encounter
```

### 8) MedicationMix e Medication

```text
+----------------------+
|    medication_mix    |
|----------------------|
| id (PK)              |
| status               |
| identifier           |
+----------------------+
           |
           |
           v
+----------------------------+
| medication_mix_ingredient  |
|----------------------------|
| medication_mix_id (FK)     |
| medication_id (FK)         |
+----------------------------+
           |
           |
           v
+----------------------+
|      medication      |
|----------------------|
| id (PK)              |
| code                 |
| code_system          |
| status               |
| ndc                  |
| formulary_drug_cd    |
| name                 |
+----------------------+
```

### 9) MedicationRequest com Patient, Encounter e Medication

```text
+----------------------+
|    medication_request |
|----------------------|
| id (PK)              |
| patient_id (FK)      |
| encounter_id (FK)    |
| medication_id (FK)   |
| intent               |
| status               |
| authored_on          |
| identifier           |
| validity_start       |
| validity_end         |
| dosage_text          |
| route_code           |
| frequency_code       |
| dose_value           |
| dose_unit            |
+----------------------+
```

### 10) MedicationDispense com patient, encounter e medicationRequest

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
        |       | medication_request  |
        |       +--------------------+
        |
        | medication_dispense.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
```

### 11) Specimen e Patient

```text
+----------------------+
|       patient        |
|----------------------|
| id (PK)              |
| ...                  |
+----------------------+
           ^
           |
           |
+----------------------+
|       specimen       |
|----------------------|
| id (PK)              |
| patient_id (FK)      |
| specimen_type_code   |
| specimen_type_system |
| specimen_type_display|
| collected_at        |
| identifier          |
+----------------------+
```

### 11) Condition com Patient e Encounter

```text
+----------------------+
|       patient        |
|----------------------|
| id (PK)              |
| ...                  |
+----------------------+
           ^                     +----------------------+
           |                     |      encounter       |
           |                     |----------------------|
           |                     | id (PK)              |
           |                     | ...                  |
           |                     +----------------------+
           |                               ^
           |                               |
           +---------------+---------------+
                           |
                           v
+----------------------+
|      condition       |
|----------------------|
| id (PK)              |
| patient_id (FK)      |
| encounter_id (FK)    |
| condition_code       |
| condition_code_system|
| condition_code_display|
| category_code        |
| category_system      |
| category_display     |
+----------------------+
```

### 12) ConditionED com Patient e Encounter

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
| condition_code_system |
| condition_code_display|
| category_code   |
| category_system |
| category_display|
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

### 13) Procedure com Patient e Encounter

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
```

### 14) procedureED com Patient e Encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | procedure_ed.patient_id
        |
+----------------+
|  procedure_ed  |
|----------------|
| id (PK)        |
| patient_id     |
| encounter_id   |
| procedure_code |
| performed_at   |
+----------------+
        |
        | procedure_ed.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
```

### 15) procedureICU com Patient e Encounter

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
```

### 16) observationLabevents com patient e specimen

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
```

### 17) observationMicroTest com patient, specimen e encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_micro_test.patient_id
        |
+--------------------------+
| observation_micro_test   |
|--------------------------|
| id (PK)                  |
| patient_id               |
| specimen_id              |
| encounter_id             |
| observation_code         |
| effective_at             |
| value_string             |
| value_code               |
+--------------------------+
        |              |
        |              | observation_micro_test.encounter_id
        |              v
        |       +----------------+
        |       |   encounter    |
        |       |----------------|
        |       | id (PK)        |
        |       +----------------+
        |
        | observation_micro_test.specimen_id
        v
+----------------+
|    specimen    |
|----------------|
| id (PK)        |
| patient_id     |
+----------------+
```

### 18) observationMicroOrg com patient, observationMicroTest e hasMember

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
| derived_from_observation_micro_test_id |
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
| member_observation_id           |
+--------------------------------+
```

`member_observation_id` ainda não possui FK nesta etapa porque pode apontar para observações microbiológicas futuras ainda não ingeridas.

### 19) observationMicroSusc com patient e observationMicroOrg

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
| derived_from_observation_micro_org_id |
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
| derived_from_observation_micro_test_id |
| organism_code            |
+--------------------------+
```

### 20) observationChartevents com patient e encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_chartevents.patient_id
        |
+--------------------------+
| observation_chartevents  |
|--------------------------|
| id (PK)                  |
| patient_id               |
| encounter_id             |
| observation_code         |
| effective_at             |
| value                    |
| value_string             |
+--------------------------+
        |
        | observation_chartevents.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
```

### 21) observationDatetimeevents com patient e encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_datetimeevents.patient_id
        |
+------------------------------+
| observation_datetimeevents   |
|------------------------------|
| id (PK)                      |
| patient_id                   |
| encounter_id                 |
| observation_code             |
| effective_at                 |
| value_datetime               |
+------------------------------+
        |
        | observation_datetimeevents.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
```

### 22) observationOutputevents com patient e encounter

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_outputevents.patient_id
        |
+-----------------------------+
| observation_outputevents    |
|-----------------------------|
| id (PK)                     |
| patient_id                  |
| encounter_id                |
| observation_code            |
| effective_at                |
| value                       |
| value_unit                  |
+-----------------------------+
        |
        | observation_outputevents.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
```

### 23) observationED com patient, encounter e procedure

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_ed.patient_id
        |
+--------------------------+
| observation_ed           |
|--------------------------|
| id (PK)                  |
| patient_id               |
| encounter_id             |
| procedure_id             |
| observation_code         |
| effective_at             |
| value_string             |
+--------------------------+
        |              |
        |              | observation_ed.procedure_id
        |              v
        |       +----------------+
        |       |   procedure    |
        |       |----------------|
        |       | id (PK)        |
        |       +----------------+
        |
        | observation_ed.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+
```

### 24) observationVitalSignsED com patient, encounter, procedure e components

```text
+----------------+
|    patient     |
|----------------|
| id (PK)        |
+----------------+
        ^
        |
        | observation_vital_signs_ed.patient_id
        |
+--------------------------------+
| observation_vital_signs_ed     |
|--------------------------------|
| id (PK)                        |
| patient_id                     |
| encounter_id                   |
| procedure_id                   |
| observation_code               |
| effective_at                   |
| value                          |
| value_unit                     |
+--------------------------------+
        |              |
        |              | observation_vital_signs_ed.procedure_id
        |              v
        |       +----------------+
        |       |   procedure    |
        |       |----------------|
        |       | id (PK)        |
        |       +----------------+
        |
        | observation_vital_signs_ed.encounter_id
        v
+----------------+
|   encounter    |
|----------------|
| id (PK)        |
+----------------+

+--------------------------------+
| observation_vital_signs_ed     |
|--------------------------------|
| id (PK)                        |
+--------------------------------+
        |
        | observation_vital_signs_ed_component.observation_vital_signs_ed_id
        v
+----------------------------------------+
| observation_vital_signs_ed_component   |
|----------------------------------------|
| observation_vital_signs_ed_id          |
| component_code                         |
| component_code_system                  |
| component_code_display                 |
| value                                  |
| value_unit                             |
| value_code                             |
| value_system                           |
+----------------------------------------+
```

### 25) Visão Consolidada

```text
organization  <-- location
      ^
      |
      +-- patient
             ^
             |
             +-- encounter -- encounter_location -- location
                    |
                    +-- encounter_ed
                    |
                    +-- encounter_icu -- encounter_icu_location -- location

medication  <--- medication_mix_ingredient ---> medication_mix
      ^
      |
      +--- medication_request --- patient / encounter

patient --- specimen

patient --- condition --- encounter

patient --- condition_ed --- encounter

patient --- procedure --- encounter

patient --- procedure_ed --- encounter

patient --- procedure_icu --- encounter

patient --- observation_labevents --- specimen

patient --- observation_micro_test --- specimen / encounter

patient --- observation_micro_org --- observation_micro_test

patient --- observation_micro_susc --- observation_micro_org

patient --- observation_chartevents --- encounter

patient --- observation_datetimeevents --- encounter

patient --- observation_outputevents --- encounter

patient --- observation_ed --- procedure / encounter

patient --- observation_vital_signs_ed --- procedure / encounter

observation_vital_signs_ed --- observation_vital_signs_ed_component

patient --- medication_dispense --- medication_request / encounter

observation_micro_org --- observation_micro_org_has_member
```
