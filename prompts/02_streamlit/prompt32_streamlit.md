Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Criar uma interface gráfica em Streamlit para exploração individual de pacientes.

Esta primeira entrega deve implementar apenas a funcionalidade:

1. Dados individuais

A interface futura terá três áreas:
1. Dados individuais
2. Dados populacionais / BI
3. Chat

Nesta entrega, implemente somente a aba `Dados individuais`.

## Contexto
O projeto já possui uma base PostgreSQL local populada por uma pipeline de ingestão FHIR/MIMIC.

A aplicação deve consultar o banco relacional já existente e montar uma visão clínica cronológica por paciente.

## Requisitos da interface

Criar uma aplicação Streamlit com abas.

Nesta entrega, criar:

- aba `Dados individuais`

As outras abas podem aparecer como placeholders simples:
- `Dados populacionais`
- `Chat`

Mas não devem ser implementadas ainda.

## Funcionalidade principal

Dado um `patient_id`, a interface deve exibir uma timeline do paciente.

O usuário deve conseguir informar o ID do paciente por um campo de texto.

Exemplo:

```text
Patient ID: <uuid>
````

Após clicar em um botão como `Buscar paciente`, a aplicação deve:

1. buscar os dados do paciente
2. exibir a identificação completa disponível
3. buscar todos os encounters associados ao paciente
4. ordenar os encounters cronologicamente
5. para cada encounter, exibir detalhes do que ocorreu, foi realizado ou descoberto

## Dados do paciente

Exibir, se disponíveis:

* id
* name
* gender
* birth_date
* identifier
* race
* ethnicity
* birthsex
* managing_organization_id
* nome da organization, se possível via join

## Timeline de encounters

Buscar todos os registros da tabela `encounter` associados ao paciente.

Ordenar por:

1. `start_date`
2. `end_date`
3. `id`

Para cada encounter, exibir:

* id do encounter
* status
* class_code
* start_date
* end_date
* organization_id
* nome da organization, se possível
* admit_source_code
* discharge_disposition_code
* service_type_code
* priority_code

## Detalhamentos dentro de cada encounter

Para cada encounter, buscar e exibir informações relacionadas, quando existirem.

### Diagnósticos

Tabela:

* `condition`

Buscar por:

* `condition.encounter_id = encounter.id`

Exibir:

* condition_code
* condition_code_display
* category_code
* category_display

### Procedimentos

Tabelas:

* `procedure`
* `procedure_ed`
* `procedure_icu`

Buscar por:

* `encounter_id = encounter.id`

Exibir:

* tipo da origem: procedure / procedure_ed / procedure_icu
* procedure_code
* procedure_code_display
* status
* performed_at ou performed_start/performed_end

### Medicações

Tabelas:

* `medication_request`
* `medication_dispense`
* `medication_dispense_ed`
* `medication_administration`
* `medication_administration_icu`
* `medication_statement_ed`

Buscar por:

* `encounter_id = encounter.id`

Exibir de forma agrupada:

* pedidos de medicação
* dispensações
* administrações
* declarações/medication statements

Campos úteis:

* medication_code
* medication_text, se existir
* status
* authored_on
* effective_at
* when_handed_over
* route_code
* frequency_code
* dose_value
* dose_unit

### Observações laboratoriais

Tabela:

* `observation_labevents`

Como essa tabela pode não ter `encounter_id`, buscar preferencialmente por:

* `patient_id = patient.id`

E exibir dentro do encounter apenas se o horário da observação estiver dentro do intervalo do encounter:

```text
observation_labevents.effective_at >= encounter.start_date
and observation_labevents.effective_at <= encounter.end_date
```

Se o encounter não tiver `end_date`, usar apenas `effective_at >= start_date`.

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

### Microbiologia

Tabelas:

* `observation_micro_test`
* `observation_micro_org`
* `observation_micro_susc`

Exibir quando houver vínculo direto por encounter, patient ou cadeia de relacionamento.

Para `observation_micro_test`:

* buscar por `encounter_id = encounter.id`, quando existir
* também considerar `patient_id = patient.id` e `effective_at` dentro do intervalo do encounter

Para `observation_micro_org`:

* buscar por `derived_from_observation_micro_test_id`

Para `observation_micro_susc`:

* buscar por `derived_from_observation_micro_org_id`

Exibir:

* teste microbiológico
* organismo identificado
* susceptibilidade antimicrobiana
* antibiotic_code
* antibiotic_code_display
* interpretation_code
* interpretation_display
* dilution_value
* dilution_comparator

### Observações charted

Tabelas:

* `observation_chartevents`
* `observation_datetimeevents`
* `observation_outputevents`
* `observation_ed`
* `observation_vital_signs_ed`

Buscar por:

* `encounter_id = encounter.id`

Exibir:

* tipo da observação
* observation_code
* observation_code_display
* effective_at
* value
* value_unit
* value_string
* value_datetime

Para `observation_vital_signs_ed_component`, exibir componentes associados quando existirem.

### Specimens

Tabela:

* `specimen`

Como `specimen` possui `patient_id`, mas pode não ter `encounter_id`, exibir dentro do encounter apenas se:

* `specimen.patient_id = patient.id`
* `specimen.collected_at` estiver dentro do intervalo do encounter

Exibir:

* specimen_type_code
* specimen_type_display
* collected_at
* identifier

## Organização visual da timeline

A interface deve ser clara e navegável.

Sugestão:

* Card/resumo do paciente no topo
* Abaixo, timeline vertical com encounters
* Cada encounter deve ser apresentado dentro de um `st.expander`
* O título do expander deve conter:

  * data inicial
  * data final
  * class_code
  * status
  * id parcial do encounter

Dentro de cada expander, criar seções:

* Resumo do encounter
* Diagnósticos
* Procedimentos
* Medicações
* Laboratório
* Microbiologia
* Observações charted
* Specimens

Usar tabelas Streamlit, como:

* `st.dataframe`
* `st.table`
* ou componentes equivalentes

Se uma seção não tiver dados, exibir mensagem curta:

* `Nenhum registro encontrado.`

## Camada de acesso a dados

Não colocar queries SQL diretamente misturadas com a UI.

Criar camada separada para consultas.

Estrutura sugerida:

```text
src/app/
  streamlit_app.py
  pages/
    individual_data.py
  services/
    patient_timeline_service.py
  repositories/
    patient_repository.py
    encounter_repository.py
    clinical_events_repository.py
  models/
    patient_timeline.py
```

Ou estrutura equivalente, mantendo separação clara entre:

* interface Streamlit
* regras de montagem da timeline
* acesso ao banco

## Conexão com banco

Usar as mesmas configurações existentes do projeto:

* `.env`
* `./config/database.yaml`

Não duplicar credenciais.

Reutilizar o módulo existente de conexão com PostgreSQL sempre que possível.

## Performance

Implementar cache para consultas com Streamlit quando adequado:

* `st.cache_data` para dados consultados
* `st.cache_resource` para engine/conexão

Cuidado para não cachear dados sensíveis de forma inadequada.

## Tratamento de erros

A interface deve tratar:

* patient_id vazio
* paciente inexistente
* erro de conexão com banco
* erro de query
* encounter sem datas
* ausência de eventos clínicos

Exibir mensagens amigáveis na interface e registrar erros no log.

## Logging

Usar o logging já existente do projeto.

Registrar:

* início da busca por paciente
* patient_id consultado
* quantidade de encounters encontrados
* erros de consulta
* tempo aproximado da montagem da timeline

## Testes

Criar testes unitários para a camada de serviço, não necessariamente para a UI Streamlit.

Criar arquivo:

```text
tests/unit/test_patient_timeline_service.py
```

Cobrir:

* paciente inexistente
* paciente existente sem encounters
* paciente com encounters
* ordenação cronológica dos encounters
* agrupamento correto de diagnósticos por encounter
* agrupamento correto de procedimentos por encounter
* agrupamento correto de medicações por encounter
* filtragem de eventos por intervalo de tempo do encounter
* montagem de timeline com seções vazias

Usar mocks para repositories.

## README

Atualizar o README com:

* nova interface Streamlit
* como executar a aplicação
* exemplo:

```bash
uv run streamlit run src/app/streamlit_app.py
```

* descrição da aba `Dados individuais`
* instrução para informar `patient_id`
* observação de que as abas `Dados populacionais` e `Chat` ainda serão implementadas

## CHANGELOG

Atualizar o CHANGELOG com:

* criação da aplicação Streamlit
* criação da aba Dados individuais
* criação da timeline por paciente
* criação da camada de serviços/repositórios
* criação de testes unitários
* atualização do README

## Dependências

Adicionar Streamlit ao projeto com `uv`.

Exemplo:

```bash
uv add streamlit
```

Adicionar outras dependências apenas se realmente necessário.

## Qualidade de código

Manter:

* type hints completos
* docstrings em português
* funções pequenas e coesas
* separação entre UI, serviço e repositórios
* tratamento explícito de exceções
* uso de configs existentes
* compatibilidade com `uv`
* testes com `pytest`

## Resultado esperado

Ao executar:

```bash
uv run streamlit run src/app/streamlit_app.py
```

o usuário deve conseguir abrir a interface, acessar a aba `Dados individuais`, informar um `patient_id` e visualizar:

1. identificação do paciente
2. timeline cronológica dos encounters
3. detalhes clínicos agrupados dentro de cada encounter

