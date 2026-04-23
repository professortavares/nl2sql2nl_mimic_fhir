# Relacionamentos Entre Tabelas

Este documento resume a modelagem relacional atualmente criada pela pipeline de ingestão.

## Tabelas Existentes

- `organization`
- `location`
- `patient`
- `encounter`
- `encounter_location`

## Foreign Keys

- `location.managing_organization_id -> organization.id`
- `patient.managing_organization_id -> organization.id`
- `encounter.patient_id -> patient.id`
- `encounter.organization_id -> organization.id`
- `encounter_location.encounter_id -> encounter.id`
- `encounter_location.location_id -> location.id`

## Diagrama ASCII

```text
+----------------------+      +----------------------+
|    organization      |      |       location       |
|----------------------|      |----------------------|
| id (PK)              |      | id (PK)              |
| name                 |      | name                 |
|                      |      | managing_organization_id (FK)
+----------------------+      +----------------------+
           ^
           |
           |
           |                +----------------------+
           |                |       patient        |
           |                |----------------------|
           |                | id (PK)              |
           |                | gender               |
           |                | birth_date           |
           |                | name                 |
           |                | identifier           |
           |                | marital_status_coding|
           |                | race                 |
           |                | ethnicity            |
           |                | birthsex             |
           |                | managing_organization_id (FK)
           |                +----------------------+
           |                          ^
           |                          |
           |                          |
           |                +----------------------+
           |                |      encounter       |
           |                |----------------------|
           |                | id (PK)              |
           |                | patient_id (FK)      |
           |                | organization_id (FK) |
           |                | status               |
           |                | class_code           |
           |                | start_date           |
           |                | end_date             |
           |                | priority_code        |
           |                | service_type_code    |
           |                | admit_source_code    |
           |                | discharge_disposition_code |
           |                | identifier           |
           |                +----------------------+
           |                          |
           |                          |
           |                          v
           |                +----------------------+
           +---------------> |  encounter_location  |
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
- `identifier[*].assigner.reference` aparece nos dados, mas não é materializado nesta fase.
