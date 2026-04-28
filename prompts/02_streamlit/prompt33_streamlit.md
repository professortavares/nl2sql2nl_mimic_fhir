Você está evoluindo a interface Streamlit do projeto Python NL2SQL2NL.

## Objetivo

Refatorar a aba `Dados individuais` para que a timeline do paciente reflita melhor a organização conceitual do MIMIC-IV.

A interface não deve parecer apenas uma listagem de tabelas SQL. Ela deve organizar os eventos clínicos por contexto assistencial, seguindo a separação:

1. General Hospital
2. Emergency Department (ED)
3. Intensive Care Unit (ICU)

Essa separação deve ser aplicada dentro da timeline cronológica de encounters do paciente.

## Contexto

A documentação do MIMIC-IV organiza os dados em grandes domínios, incluindo:
- hospital geral
- unidade de terapia intensiva ICU
- departamento de emergência ED

A aba `Dados individuais` deve refletir essa lógica na experiência do usuário.

## Estrutura visual desejada

A tela deve continuar funcionando assim:

```text
Paciente
  ↓
Identificação completa
  ↓
Timeline cronológica de encounters
  ↓
Encounter individual
  ↓
Blocos por contexto:
    - General Hospital
    - Emergency Department (ED)
    - Intensive Care Unit (ICU)
````

## Layout obrigatório

Na aba `Dados individuais`:

1. Campo para informar `patient_id`
2. Botão para buscar paciente
3. Card/resumo de identificação do paciente
4. Timeline cronológica dos encounters
5. Cada encounter dentro de um `st.expander`
6. Dentro de cada encounter, usar `st.tabs` com:

```text
General Hospital
Emergency Department (ED)
Intensive Care Unit (ICU)
```

Cada aba deve aparecer ou ser preenchida apenas quando houver dados relacionados.

Se uma aba não tiver dados, pode exibir:

```text
Nenhum dado encontrado para este contexto.
```

## Regra principal

A organização dentro de cada encounter deve ser orientada ao domínio clínico, não ao nome técnico das tabelas.

Evite títulos como:

* `observation_chartevents`
* `medication_dispense_ed`
* `condition_ed`

Prefira títulos como:

* Diagnósticos
* Procedimentos
* Medicações
* Exames laboratoriais
* Microbiologia
* Sinais vitais
* Eventos charted
* Informações da permanência

## Contexto 1: General Hospital

A aba `General Hospital` deve agrupar dados hospitalares gerais.

### Seções esperadas

#### Informações da hospitalização

Fonte principal:

* `encounter`

Exibir:

* id
* status
* class_code
* start_date
* end_date
* organization_id
* nome da organização, se disponível
* admit_source_code
* discharge_disposition_code
* service_type_code
* priority_code

#### Diagnósticos

Fonte:

* `condition`

Filtro:

* `condition.encounter_id = encounter.id`

Exibir:

* condition_code
* condition_code_display
* category_code
* category_display

#### Procedimentos gerais

Fonte:

* `procedure`

Filtro:

* `procedure.encounter_id = encounter.id`

Exibir:

* procedure_code
* procedure_code_display
* status
* performed_at

#### Pedidos e eventos gerais de medicação

Fontes:

* `medication_request`
* `medication_dispense`
* `medication_administration`

Filtro:

* `encounter_id = encounter.id`

Agrupar visualmente em:

* Pedidos de medicação
* Dispensações
* Administrações

Exibir campos disponíveis como:

* medication_code
* status
* authored_on
* effective_at
* route_code
* frequency_code
* dose_value
* dose_unit

#### Exames laboratoriais

Fonte:

* `observation_labevents`

Regra:

* Se a tabela tiver apenas `patient_id`, associar ao encounter por intervalo temporal.
* Usar `effective_at` dentro do intervalo `encounter.start_date` e `encounter.end_date`.
* Se `encounter.end_date` estiver vazio, considerar `effective_at >= encounter.start_date`.

Exibir:

* observation_code
* observation_code_display
* effective_at
* value
* value_unit
* reference_low_value
* reference_high_value
* lab_priority
* note

#### Microbiologia

Fontes:

* `observation_micro_test`
* `observation_micro_org`
* `observation_micro_susc`

Regras:

* `observation_micro_test` pode ser associado por `encounter_id`, se existir.
* Também permitir associação por `patient_id` e intervalo temporal.
* `observation_micro_org` deve ser associado ao teste por `derived_from_observation_micro_test_id`.
* `observation_micro_susc` deve ser associado ao organismo por `derived_from_observation_micro_org_id`.

Exibir:

* teste microbiológico
* organismo identificado
* susceptibilidade
* antibiotic_code
* antibiotic_code_display
* interpretation_code
* interpretation_display
* dilution_value
* dilution_comparator

#### Specimens

Fonte:

* `specimen`

Regra:

* Associar por `patient_id`
* Exibir dentro do encounter se `collected_at` estiver no intervalo temporal do encounter.

Exibir:

* specimen_type_code
* specimen_type_display
* collected_at
* identifier

## Contexto 2: Emergency Department (ED)

A aba `Emergency Department (ED)` deve agrupar dados específicos da emergência.

Exibir esta aba com dados quando houver:

* `encounter_ed`
* `condition_ed`
* `procedure_ed`
* `observation_ed`
* `observation_vital_signs_ed`
* `medication_dispense_ed`
* `medication_statement_ed`

### Seções esperadas

#### Informações da permanência no ED

Fonte:

* `encounter_ed`

Relação:

* `encounter_ed.encounter_id = encounter.id`
  ou, quando necessário:
* `encounter_ed.patient_id = patient.id`

Exibir:

* id
* status
* class_code
* start_date
* end_date
* admit_source_code
* discharge_disposition_code

#### Diagnósticos ED

Fonte:

* `condition_ed`

Filtro:

* `condition_ed.encounter_id = encounter.id`

Exibir:

* condition_code
* condition_code_display
* category_code
* category_display

#### Procedimentos ED

Fonte:

* `procedure_ed`

Filtro:

* `procedure_ed.encounter_id = encounter.id`

Exibir:

* procedure_code
* procedure_code_display
* status
* performed_at

#### Observações ED

Fonte:

* `observation_ed`

Filtro:

* `observation_ed.encounter_id = encounter.id`

Exibir:

* observation_code
* observation_code_display
* effective_at
* value_string
* data_absent_reason_code
* data_absent_reason_display

#### Sinais vitais ED

Fonte:

* `observation_vital_signs_ed`

Filtro:

* `observation_vital_signs_ed.encounter_id = encounter.id`

Exibir:

* observation_code
* observation_code_display
* effective_at
* value
* value_unit
* value_code

Se houver componentes em:

* `observation_vital_signs_ed_component`

Exibir abaixo da observação principal:

* component_code
* component_code_display
* value
* value_unit
* value_code

#### Medicações ED

Fontes:

* `medication_dispense_ed`
* `medication_statement_ed`

Filtro:

* `encounter_id = encounter.id`

Agrupar visualmente em:

* Dispensações ED
* Medication statements ED

Exibir:

* medication_text
* medication_code
* medication_code_display, se existir
* status
* when_handed_over
* date_asserted

## Contexto 3: Intensive Care Unit (ICU)

A aba `Intensive Care Unit (ICU)` deve agrupar dados específicos da UTI.

Exibir esta aba com dados quando houver:

* `encounter_icu`
* `procedure_icu`
* `medication_administration_icu`
* `observation_chartevents`
* `observation_datetimeevents`
* `observation_outputevents`

### Seções esperadas

#### Informações da permanência na ICU

Fonte:

* `encounter_icu`

Relação:

* `encounter_icu.encounter_id = encounter.id`
  ou, quando necessário:
* `encounter_icu.patient_id = patient.id`

Exibir:

* id
* status
* class_code
* start_date
* end_date
* identifier

#### Procedimentos ICU

Fonte:

* `procedure_icu`

Filtro:

* `procedure_icu.encounter_id = encounter.id`

Exibir:

* procedure_code
* procedure_code_display
* category_code
* status
* performed_start
* performed_end

#### Administrações de medicação ICU

Fonte:

* `medication_administration_icu`

Filtro:

* `medication_administration_icu.encounter_id = encounter.id`

Exibir:

* medication_code
* medication_code_display
* status
* effective_at
* dose_value
* dose_unit
* method_code

#### Charted events

Fonte:

* `observation_chartevents`

Filtro:

* `observation_chartevents.encounter_id = encounter.id`

Exibir:

* observation_code
* observation_code_display
* category_code
* effective_at
* issued_at
* value
* value_unit
* value_code
* value_string

#### Output events

Fonte:

* `observation_outputevents`

Filtro:

* `observation_outputevents.encounter_id = encounter.id`

Exibir:

* observation_code
* observation_code_display
* category_code
* effective_at
* issued_at
* value
* value_unit
* value_code

#### Date/time events

Fonte:

* `observation_datetimeevents`

Filtro:

* `observation_datetimeevents.encounter_id = encounter.id`

Exibir:

* observation_code
* observation_code_display
* category_code
* effective_at
* issued_at
* value_datetime

## Organização cronológica

Dentro de cada encounter, os blocos devem priorizar ordenação temporal quando houver campo de data.

Ordenações sugeridas:

* Diagnósticos: por código ou categoria
* Procedimentos: por performed_at, performed_start
* Medicações: por authored_on, effective_at, when_handed_over ou date_asserted
* Observações: por effective_at ou issued_at
* Specimens: por collected_at

## Camada de serviço

Não colocar SQL diretamente na UI.

Criar ou refatorar uma camada de serviço para montar a timeline já organizada por domínio.

Sugestão:

```text
src/app/services/patient_timeline_service.py
```

Esse serviço deve retornar uma estrutura lógica como:

```python
{
    "patient": {...},
    "encounters": [
        {
            "summary": {...},
            "general_hospital": {
                "diagnoses": [...],
                "procedures": [...],
                "medications": {...},
                "labs": [...],
                "microbiology": {...},
                "specimens": [...]
            },
            "emergency_department": {
                "stay": {...},
                "diagnoses": [...],
                "procedures": [...],
                "observations": [...],
                "vital_signs": [...],
                "medications": {...}
            },
            "icu": {
                "stay": {...},
                "procedures": [...],
                "medications": [...],
                "charted_events": [...],
                "output_events": [...],
                "datetime_events": [...]
            }
        }
    ]
}
```

## Camada de repositórios

Criar ou refatorar repositories para manter consultas separadas da UI.

Sugestão:

```text
src/app/repositories/
  patient_repository.py
  encounter_repository.py
  general_hospital_repository.py
  emergency_department_repository.py
  icu_repository.py
```

Os nomes podem variar, mas a separação deve ficar clara.

## UI Streamlit

Na aba `Dados individuais`, renderizar a estrutura retornada pelo serviço.

Sugestão de componentes:

* `st.text_input` para patient_id
* `st.button` para busca
* `st.container` para resumo do paciente
* `st.expander` para cada encounter
* `st.tabs` para General Hospital / ED / ICU
* `st.dataframe` para listas tabulares
* `st.caption` para observações auxiliares

## Regras de exibição

* Não exibir seções vazias, exceto quando todo o contexto estiver vazio.
* Quando todo o contexto estiver vazio, mostrar `Nenhum dado encontrado para este contexto.`
* Evitar nomes técnicos de tabela na UI.
* Usar nomes clínicos amigáveis.
* Preservar IDs técnicos apenas quando forem úteis para rastreabilidade.
* Mostrar datas em formato legível.

## Logging

Registrar:

* início da busca por paciente
* patient_id informado
* quantidade de encounters encontrados
* quantidade de eventos por contexto
* erros de consulta
* tempo total de montagem da timeline

## Tratamento de erros

Tratar:

* patient_id vazio
* paciente inexistente
* erro de conexão com banco
* encounter sem datas
* registros clínicos sem data
* tabelas vazias

A UI deve exibir mensagens amigáveis.

## Testes

Atualizar ou criar testes para:

```text
tests/unit/test_patient_timeline_service.py
```

Cobrir:

* paciente sem encounters
* paciente com encounter apenas hospitalar
* paciente com dados ED
* paciente com dados ICU
* encounter com dados mistos General + ED + ICU
* ordenação cronológica dos encounters
* associação temporal de labs e specimens ao encounter
* agrupamento de microbiologia em teste, organismo e susceptibilidade
* ausência de seções vazias
* estrutura final retornada pelo serviço

Usar mocks para repositories.

## README

Atualizar o README com:

* explicação da aba `Dados individuais`
* explicação da timeline por paciente
* explicação da organização por General Hospital / ED / ICU
* instrução de execução:

```bash
uv run streamlit run src/app/streamlit_app.py
```

* observação de que a organização visual segue a separação conceitual do MIMIC-IV

## CHANGELOG

Atualizar o CHANGELOG com:

* refatoração da aba Dados individuais
* organização da timeline por General Hospital, ED e ICU
* criação/refatoração de serviços e repositories
* melhorias na exibição dos encounters
* atualização dos testes
* atualização do README

## Qualidade

Manter:

* type hints completos
* docstrings em português
* funções pequenas e coesas
* separação entre UI, serviços e repositórios
* tratamento explícito de exceções
* logs em arquivo
* compatibilidade com `uv`
* testes com `pytest`

## Resultado esperado

Ao executar:

```bash
uv run streamlit run src/app/streamlit_app.py
```

o usuário deve conseguir informar um `patient_id` e visualizar uma timeline cronológica em que cada encounter é organizado em:

1. General Hospital
2. Emergency Department (ED)
3. Intensive Care Unit (ICU)

A experiência deve refletir a separação conceitual do MIMIC-IV e facilitar a leitura clínica do histórico do paciente.
