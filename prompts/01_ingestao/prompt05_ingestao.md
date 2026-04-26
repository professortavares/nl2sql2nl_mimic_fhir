Você está evoluindo um projeto Python do tipo NL2SQL2NL (Natural Language -> SQL -> Natural Language).

## Objetivo desta entrega
Expandir a pipeline orquestrada de ingestão para suportar agora o arquivo:

4. `./data/MimicEncounter.ndjson.gz`

Esta entrega inicia a **segunda fase de ingestão de arquivos**.

A ordem de importação deve ser **obrigatoriamente**:

1. `MimicOrganization`
2. `MimicLocation`
3. `MimicPatient`
4. `MimicEncounter`

Se existirem relacionamentos entre as tabelas, as **foreign keys devem ser criadas**.

Também continuam obrigatórios:
- qualidade de código
- atualização de `README.md`
- atualização de `CHANGELOG.md`
- logging em arquivo
- testes de unidade
- criação de um arquivo markdown na raiz do projeto com um diagrama ASCII mostrando o relacionamento entre as tabelas já ingeridas

---

## Contexto técnico
- Linguagem: Python
- Gerenciador de pacotes: `uv`
- Banco de dados: PostgreSQL local em Docker
- Os arquivos de entrada ficam em `./data`
- Configurações não sensíveis devem ficar em YAML dentro de `./config`
- Credenciais de banco devem ficar em `.env`
- Evite ao máximo valores hardcoded
- Sempre que o processo de ingestão executar, **toda a estrutura e todos os dados devem ser destruídos e recriados**
- Registre todas as mudanças relevantes em `CHANGELOG.md`
- Atualize o `README.md`
- Registre logs em arquivo dentro de `./logs`
- Inclua testes de unidade para os componentes críticos

---

## Configuração do banco
Crie ou mantenha o arquivo `.env` na raiz do projeto com:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app_mimic_fhir
POSTGRES_USER=app_mimic_fhir
POSTGRES_PASSWORD=app_mimic_fhir
````

---

## Diretriz arquitetural

A arquitetura deve continuar baseada em uma **pipeline orquestrada de recursos**, preparada para crescer futuramente com outros recursos FHIR.

A camada central de orquestração deve:

* conhecer a ordem de execução
* executar reset do banco
* criar schema/tabelas
* executar os pipelines dos recursos em ordem
* registrar logs e estatísticas
* permitir evolução para novos recursos com baixo acoplamento

Não implemente uma solução pontual para Encounter.
A solução deve preservar a consistência com os recursos já existentes:

* Organization
* Location
* Patient

---

## Ordem obrigatória da pipeline

A pipeline principal deve executar exatamente nesta ordem:

1. reset completo do banco / schema relacionado
2. criação das tabelas
3. ingestão de `Organization`
4. ingestão de `Location`
5. ingestão de `Patient`
6. ingestão de `Encounter`

Essa orquestração deve continuar centralizada em uma pipeline principal, como `ingest_all`.

---

## Modelagem atual simplificada que deve ser preservada

### organization

Campos:

* `id` (PK)
* `name`

### location

Campos:

* `id` (PK)
* `name`
* `managing_organization_id` (FK -> organization.id, nullable)

### patient

Campos:

* `id` (PK)
* `gender`
* `birth_date`
* `name`
* `identifier`
* `marital_status_coding`
* `race`
* `ethnicity`
* `birthsex`
* `managing_organization_id` (FK -> organization.id, nullable)

Essas tabelas simplificadas devem ser mantidas.

---

## Novo recurso a ingerir: Encounter

Arquivo:

* `./data/MimicEncounter.ndjson.gz`

### Estrutura observada do recurso

Campos observados no arquivo:

* `id`
* `meta.profile`
* `type[*].coding[*]`
* `class.code`
* `class.system`
* `class.display`
* `period.start`
* `period.end`
* `status`
* `subject.reference`
* `location[*].location.reference`
* `priority.coding[*].code`
* `identifier[*].value`
* `identifier[*].assigner.reference`
* `serviceType.coding[*].code`
* `resourceType`
* `hospitalization.admitSource.coding[*].code`
* `hospitalization.dischargeDisposition.coding[*].code`
* `serviceProvider.reference`

### Relacionamentos observados

* `subject.reference = "Patient/<patient_id>"`
* `location[*].location.reference = "Location/<location_id>"`
* `serviceProvider.reference = "Organization/<organization_id>"`
* `identifier[*].assigner.reference = "Organization/<organization_id>"`

---

## Diretriz de modelagem para Encounter

Mantenha a filosofia de modelagem **enxuta e pragmática**, assim como foi feito para os recursos anteriores.

### Criar tabela principal `encounter`

Campos obrigatórios sugeridos:

* `id` (PK)
* `patient_id` (FK -> `patient.id`, nullable se necessário)
* `organization_id` (FK -> `organization.id`, nullable se necessário)

  * usar preferencialmente `serviceProvider.reference`
* `status`
* `class_code`
* `start_date`
* `end_date`
* `priority_code`
* `service_type_code`
* `admit_source_code`
* `discharge_disposition_code`
* `identifier`

### Regras de simplificação para `encounter`

* **Não carregar**:

  * `resourceType`
  * `meta.profile`
  * `type[*].coding[*]` completo
  * `class.system`
  * `class.display`
  * `priority.coding[*].system`
  * `priority.coding[*].display`
  * `serviceType.coding[*].system`
  * demais campos que não forem essenciais nesta fase

### Observação importante

Como `Encounter` pode ter **múltiplas locations** em `location[*]`, não é adequado perder esse relacionamento.

Portanto, além da tabela principal `encounter`, crie uma tabela auxiliar enxuta para suportar o relacionamento com `location`:

### Criar tabela `encounter_location`

Campos:

* `encounter_id` (FK -> `encounter.id`)
* `location_id` (FK -> `location.id`)
* `start_date` (nullable)
* `end_date` (nullable)

Essa tabela deve representar as locations associadas ao encounter.

---

## Relacionamentos obrigatórios

Mantenha/crie as foreign keys:

* `location.managing_organization_id -> organization.id`
* `patient.managing_organization_id -> organization.id`
* `encounter.patient_id -> patient.id`
* `encounter.organization_id -> organization.id`
* `encounter_location.encounter_id -> encounter.id`
* `encounter_location.location_id -> location.id`

Se as referências estiverem ausentes, as colunas podem ser nulas quando fizer sentido.

---

## Parse de referências FHIR

Implemente e reutilize função(ões) para extrair IDs a partir de referências FHIR no formato:

* `Organization/<id>`
* `Patient/<id>`
* `Location/<id>`

Exemplos:

* `"Organization/ee172322-118b-5716-abbc-18e4c5437e15"`
* `"Patient/0a8eebfd-a352-522e-89f0-1d4a13abdebc"`
* `"Location/501cd59a-cd8a-5f98-8298-2ca9c897d59f"`

A função deve:

* usar type hints
* ter docstring detalhada em português
* validar formato
* permitir especificar o tipo esperado do recurso
* levantar exceção adequada em caso de valor inválido

---

## Regras de extração para Encounter

### Tabela `encounter`

Extrair:

* `id`
* `subject.reference` -> `patient_id`
* `serviceProvider.reference` -> `organization_id`
* `status`
* `class.code` -> `class_code`
* `period.start` -> `start_date`
* `period.end` -> `end_date`
* `priority.coding[*].code` -> `priority_code`
* `serviceType.coding[*].code` -> `service_type_code`
* `hospitalization.admitSource.coding[*].code` -> `admit_source_code`
* `hospitalization.dischargeDisposition.coding[*].code` -> `discharge_disposition_code`
* `identifier[*].value` -> `identifier`

### Regra para listas

Quando houver listas como:

* `priority.coding[*]`
* `serviceType.coding[*]`
* `identifier[*]`

carregar o **primeiro valor não vazio e válido encontrado**.

Documente isso no código, README e CHANGELOG.

### Tabela `encounter_location`

Extrair de `location[*]`:

* `location.location.reference` -> `location_id`
* `period.start` -> `start_date`
* `period.end` -> `end_date`

Cada item da lista `location[*]` deve gerar um registro em `encounter_location`.

---

## Reset completo a cada execução

A execução deve:

1. abrir conexão com o banco
2. destruir todas as tabelas relacionadas à ingestão
3. recriar toda a estrutura
4. inserir os dados novamente

Esse comportamento deve ser:

* explícito
* previsível
* configurável via YAML
* com default = `drop_and_recreate`

---

## Logging obrigatório em arquivo

Implemente logging estruturado e legível.

### Requisitos

* salvar logs em arquivo dentro da pasta `./logs`
* criar a pasta automaticamente se não existir
* também permitir saída no console
* registrar:

  * início do processo
  * ordem da pipeline
  * schema resetado
  * tabelas criadas
  * recurso sendo processado
  * arquivo sendo processado
  * quantidade de registros lidos por recurso
  * quantidade de registros inseridos por tabela
  * falhas de parsing
  * falhas de integridade
  * tempo total da execução
* usar rotação de logs, preferencialmente com biblioteca padrão (`logging.handlers`)

Sugestão:

* `./logs/ingestion.log`

Evite hardcode excessivo: path, nível e rotação devem ser configuráveis em YAML.

---

## Configurações em YAML

Centralize configurações não sensíveis em arquivos YAML dentro de `./config`.

Sugestão:

* `./config/database.yaml`
* `./config/logging.yaml`
* `./config/ingestion/common.yaml`
* `./config/ingestion/organization.yaml`
* `./config/ingestion/location.yaml`
* `./config/ingestion/patient.yaml`
* `./config/ingestion/encounter.yaml`
* `./config/pipeline/resources.yaml`

Esses arquivos podem conter:

* schema do banco
* política de reset
* batch size
* ordem da pipeline
* caminhos dos arquivos
* nomes das tabelas
* configurações de log
* nível de log
* nome do arquivo de log
* flags de comportamento

Credenciais sensíveis devem continuar no `.env`.

---

## Estrutura sugerida de código

Você pode criar ou ajustar algo como:

* `.env`
* `README.md`
* `CHANGELOG.md`
* `TABLE_RELATIONSHIPS.md`  (ou outro nome adequado, desde que fique na raiz)
* `./config/database.yaml`
* `./config/logging.yaml`
* `./config/ingestion/common.yaml`
* `./config/ingestion/organization.yaml`
* `./config/ingestion/location.yaml`
* `./config/ingestion/patient.yaml`
* `./config/ingestion/encounter.yaml`
* `./config/pipeline/resources.yaml`

Em `src/`:

* `src/config/settings.py`
* `src/config/yaml_loader.py`
* `src/logging/logger.py`
* `src/db/connection.py`
* `src/db/schema.py`
* `src/db/reset.py`
* `src/db/models.py`
* `src/ingestion/readers/ndjson_gzip_reader.py`
* `src/ingestion/parsers/fhir_reference_parser.py`
* `src/ingestion/transformers/organization_transformer.py`
* `src/ingestion/transformers/location_transformer.py`
* `src/ingestion/transformers/patient_transformer.py`
* `src/ingestion/transformers/encounter_transformer.py`
* `src/ingestion/loaders/organization_loader.py`
* `src/ingestion/loaders/location_loader.py`
* `src/ingestion/loaders/patient_loader.py`
* `src/ingestion/loaders/encounter_loader.py`
* `src/pipelines/base_resource_pipeline.py`
* `src/pipelines/ingest_organization.py`
* `src/pipelines/ingest_location.py`
* `src/pipelines/ingest_patient.py`
* `src/pipelines/ingest_encounter.py`
* `src/pipelines/ingest_all.py`
* `src/main.py`

Em `tests/`:

* `tests/unit/test_fhir_reference_parser.py`
* `tests/unit/test_ndjson_gzip_reader.py`
* `tests/unit/test_organization_transformer.py`
* `tests/unit/test_location_transformer.py`
* `tests/unit/test_patient_transformer.py`
* `tests/unit/test_encounter_transformer.py`

Se fizer sentido, inclua testes de loader com mocks.

---

## Requisitos de implementação

Implemente:

1. leitura streaming de arquivos `.ndjson.gz`
2. parse linha a linha
3. validação mínima de cada registro
4. transformação para modelo relacional simplificado
5. criação/recriação completa do schema
6. inserção transacional
7. respeito à ordem de carga
8. criação de foreign keys necessárias
9. logging em arquivo e console
10. resumo final de execução
11. testes de unidade para componentes críticos
12. geração/atualização do arquivo markdown com o relacionamento entre as tabelas

---

## Arquivo markdown com relacionamento entre tabelas

Crie um arquivo markdown na raiz do projeto para documentar o relacionamento entre as tabelas já ingeridas.

Você pode usar um nome como:

* `TABLE_RELATIONSHIPS.md`
  ou outro nome equivalente, desde que fique claro e esteja na raiz.

### Requisitos desse arquivo

* explicar brevemente o objetivo do documento
* listar as tabelas existentes
* explicar as foreign keys
* conter uma **arte em ASCII** mostrando os relacionamentos

### Exemplo de direção esperada

Produza algo nesse espírito, mas adaptado à modelagem real final do projeto:

```text
+------------------+
|   organization   |
|------------------|
| id (PK)          |
| name             |
+------------------+
        ^   ^
        |   |
        |   +----------------------+
        |                          |
+------------------+      +------------------+
|     location     |      |     patient      |
|------------------|      |------------------|
| id (PK)          |      | id (PK)          |
| name             |      | ...              |
| managing_org_id  |      | managing_org_id  |
+------------------+      +------------------+
                                  ^
                                  |
                           +------------------+
                           |    encounter     |
                           |------------------|
                           | id (PK)          |
                           | patient_id       |
                           | organization_id  |
                           | ...              |
                           +------------------+
                                  |
                                  v
                           +----------------------+
                           |  encounter_location  |
                           |----------------------|
                           | encounter_id         |
                           | location_id          |
                           | start_date           |
                           | end_date             |
                           +----------------------+
```

O conteúdo final deve refletir exatamente a modelagem implementada.

---

## Robustez e validações

Implemente tratamento robusto para:

* arquivo inexistente
* extensão inválida
* JSON inválido por linha
* ausência de campos importantes
* referência FHIR inválida
* erro de integridade referencial
* rollback em caso de falha

A ingestão deve falhar de forma controlada, com mensagens claras.

---

## Testes de unidade obrigatórios

Crie testes de unidade cobrindo no mínimo:

### 1) Parser de referência FHIR

Casos:

* referência válida para `Organization`
* referência válida para `Patient`
* referência válida para `Location`
* referência vazia
* referência com tipo incorreto
* referência malformada

### 2) Leitor NDJSON GZIP

Casos:

* leitura válida
* arquivo inexistente
* extensão inválida
* linha JSON inválida

### 3) Transformer de Organization

Casos:

* registro válido
* extração apenas de `id` e `name`

### 4) Transformer de Location

Casos:

* registro válido com `managingOrganization`
* registro sem `managingOrganization`
* referência inválida

### 5) Transformer de Patient

Casos:

* registro válido com todos os campos simplificados
* registro com campos opcionais ausentes
* extensões ausentes
* referência inválida

### 6) Transformer de Encounter

Casos:

* registro válido com:

  * patient
  * serviceProvider
  * identifier
  * priority
  * serviceType
  * hospitalization
  * múltiplas locations
* registro sem `serviceProvider`
* registro sem `location`
* referência inválida em `subject`
* referência inválida em `location`
* garantia de que apenas as colunas simplificadas são retornadas para `encounter`
* garantia de que a tabela derivada `encounter_location` é montada corretamente

### Requisitos dos testes

* usar `pytest`
* testes legíveis e pequenos
* fixtures quando fizer sentido
* sem depender do banco para testar transformers e parsers
* focar em unidade real, não pseudo-teste

---

## Interface de execução

Crie uma forma simples de executar a ingestão completa, por exemplo:

```bash
python -m src.main
```

ou equivalente.

A execução principal deve ingerir os quatro arquivos na ordem definida.

---

## Qualidade de código

Todo o código deve seguir rigorosamente estas regras:

* type hints completos
* docstrings detalhadas em português
* tratamento de exceções
* nomes claros
* funções pequenas, coesas e reutilizáveis
* baixo acoplamento
* evitar strings mágicas e números mágicos
* código preparado para manutenção e crescimento
* seguir um padrão consistente de estilo em todo o projeto

Siga o formato abaixo para funções e métodos:

```python
def exemplo_funcao(parametro: str = "") -> str:
    """
    Descreve claramente o objetivo da função.

    Parâmetros:
    ----------
    parametro : str, default = ""
        Descrição do parâmetro.

    Retorno:
    -------
    str
        Descrição do retorno.

    Exceções:
    --------
    Levanta ValueError ou TypeError quando aplicável.

    Exemplos de uso:
    ----------------
    print(exemplo_funcao("abc"))
    """
    try:
        parametro = str(parametro)
        return parametro.strip()
    except (TypeError, ValueError) as e:
        raise TypeError("Parâmetro inválido.") from e
```

---

## Dependências

Adicione apenas dependências realmente necessárias e compatíveis com `uv`.

Sugestão:

* `sqlalchemy`
* `psycopg[binary]`
* `pyyaml`
* `pydantic` ou `pydantic-settings` se fizer sentido
* `pytest`
* biblioteca padrão `logging`

Evite dependências desnecessárias.

---

## README obrigatório

Atualize o `README.md` com pelo menos:

* visão geral da pipeline orquestrada de recursos
* separação entre primeira e segunda fase de ingestão
* pré-requisitos
* configuração do `.env`
* estrutura de configuração em `./config`
* como instalar dependências com `uv`
* como executar a ingestão
* ordem de importação
* explicação dos relacionamentos:

  * `location -> organization`
  * `patient -> organization`
  * `encounter -> patient`
  * `encounter -> organization`
  * `encounter_location -> encounter`
  * `encounter_location -> location`
* explicação da modelagem simplificada
* lista das tabelas finais realmente criadas
* localização dos logs
* comportamento de reset total do banco
* como executar os testes de unidade
* referência ao arquivo markdown com o diagrama ASCII das relações

O README deve ficar claro, organizado e útil para evolução futura.

---

## CHANGELOG obrigatório

Atualize o `CHANGELOG.md` com todas as mudanças relevantes desta evolução, incluindo:

* início da segunda fase de ingestão
* suporte a ingestão de `Encounter`
* atualização da ordem da pipeline
* criação das FKs de `encounter`
* criação da tabela `encounter_location`
* atualização do arquivo markdown de relacionamentos
* atualização dos testes de unidade
* atualização do README
* eventuais refatorações arquiteturais necessárias

Use um formato limpo, consistente e legível.

---

## Entrega esperada

Forneça:

1. todos os arquivos criados ou alterados
2. conteúdo completo dos arquivos
3. instruções para instalar dependências com `uv`
4. instruções para executar a pipeline completa
5. instruções para executar os testes
6. explicação breve da nova modelagem com `encounter`
7. exemplo de saída esperada no terminal
8. exemplo de log gerado em arquivo
9. conteúdo do markdown de relacionamentos com arte ASCII

---

## Importante

* Não deixe credenciais hardcoded fora do `.env`
* Não concentre configurações em código quando puder movê-las para YAML
* Não implemente solução descartável
* A base deve estar preparada para ingestão futura de outros recursos FHIR
* Se precisar refatorar a implementação anterior para manter boa arquitetura, faça isso
* Preserve consistência entre código, README, CHANGELOG, configs, testes e documentação relacional
* A modelagem final desta fase deve ser enxuta, pragmática e orientada ao uso analítico inicial
