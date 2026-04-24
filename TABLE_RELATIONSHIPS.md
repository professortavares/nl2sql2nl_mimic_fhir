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

### 7) Medication como dimensão independente

`Medication` foi incluído nesta fase sem foreign keys diretas, porque o arquivo `MimicMedication.ndjson.gz` não mostrou referências FHIR explícitas e confiáveis para as demais entidades já ingeridas.

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

### 8) Visão Consolidada

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

medication  (dimensão independente nesta fase)
```
