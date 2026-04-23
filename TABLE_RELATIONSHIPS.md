# Relacionamentos Entre Tabelas

Este documento resume a modelagem relacional atualmente criada pela pipeline de ingestão.

## Tabelas Existentes

- `organization`
- `location`
- `patient`
- `encounter`
- `encounter_location`
- `encounter_ed`

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

### 6) Visão Consolidada

```text
+----------------------+      +----------------------+
|     organization     |      |       location       |
|----------------------|      |----------------------|
| id (PK)              |      | id (PK)              |
| name                 |      | name                 |
+----------------------+      | managing_organization_id (FK)
           ^                  +----------------------+
           |                             ^
           |                             |
           |                             |
           |                  +----------------------+
           |                  |       patient        |
           |                  |----------------------|
           |                  | id (PK)              |
           |                  | ...                  |
           |                  | managing_organization_id (FK)
           |                  +----------------------+
           |                             ^
           |                             |
           |                             |
           |                  +----------------------+
           |                  |      encounter       |
           |                  |----------------------|
           |                  | id (PK)              |
           |                  | patient_id (FK)      |
           |                  | organization_id (FK) |
           |                  | ...                  |
           |                  +----------------------+
           |                             ^
           |                             |
           |                             |
           |                  +----------------------+
           |                  |    encounter_ed      |
           |                  |----------------------|
           |                  | id (PK)              |
           |                  | encounter_id (FK)    |
           |                  | patient_id (FK)      |
           |                  | organization_id (FK) |
           |                  | ...                  |
           |                  +----------------------+
           |
           +------------------------------+
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
```

## Observações

- `encounter_location` preserva múltiplas localizações associadas ao mesmo encounter.
- `encounter.organization_id` usa preferencialmente `serviceProvider.reference`.
- `encounter_ed.encounter_id` vem de `partOf.reference` e materializa a relação com o encounter-pai.
- `identifier[*].assigner.reference` aparece nos dados, mas não é materializado como coluna independente nesta fase.
