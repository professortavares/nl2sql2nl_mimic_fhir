Você está evoluindo um projeto Python do tipo NL2SQL2NL (Natural Language -> SQL -> Natural Language).

## Objetivo desta entrega
Refatorar a pipeline orquestrada de ingestão para suportar os arquivos:

1. `./data/MimicOrganization.ndjson.gz`
2. `./data/MimicLocation.ndjson.gz`
3. `./data/MimicPatient.ndjson.gz`

A ordem de importação deve permanecer **obrigatoriamente**:

1. `MimicOrganization`
2. `MimicLocation`
3. `MimicPatient`

O objetivo desta refatoração é **enxugar a modelagem relacional e o processo de ingestão**, carregando apenas os campos realmente necessários para esta primeira fase estrutural.

Se existirem relacionamentos entre as tabelas, as **foreign keys devem ser mantidas/criadas**.

Também continuam obrigatórios:
- qualidade de código
- atualização de `README.md`
- atualização de `CHANGELOG.md`
- logging em arquivo
- testes de unidade

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

## Diretriz principal desta refatoração

A modelagem anterior estava mais detalhada do que o necessário para esta fase do projeto.

Agora você deve **simplificar a construção das tabelas e da ingestão**, reduzindo tabelas auxiliares e carregando alguns atributos diretamente nas tabelas principais, sempre que isso fizer sentido.

A refatoração deve:

* reduzir o número de tabelas
* reduzir joins desnecessários
* simplificar o pipeline
* manter integridade relacional essencial
* manter extensibilidade para fases futuras
* documentar claramente no README e no CHANGELOG as decisões de simplificação

---

## Ordem obrigatória da pipeline

A pipeline principal deve executar exatamente nesta ordem:

1. reset completo do banco / schema relacionado
2. criação das tabelas
3. ingestão de `Organization`
4. ingestão de `Location`
5. ingestão de `Patient`

Essa orquestração deve continuar centralizada em uma pipeline principal, como `ingest_all`.

---

## Relacionamentos obrigatórios

Mantenha os relacionamentos essenciais:

* `location.managing_organization_id -> organization.id`
* `patient.managing_organization_id -> organization.id`

Se a referência estiver ausente, a coluna pode ser nula.
Se existir, o valor deve ser parseado corretamente a partir do formato FHIR:

* `"Organization/<uuid>"`

Implemente uma função reutilizável para parse de referência FHIR.

---

## Nova modelagem enxuta obrigatória

### 1) Tabela `organization`

**Manter apenas os campos necessários.**

Campos obrigatórios:

* `id` (PK)
* `name`

### Regras importantes para `organization`

* **Não carregar** as colunas:

  * `resource_type`
  * `active`

* **Não criar / não carregar** as tabelas:

  * `organization_identifier`
  * `organization_meta_profile`
  * `organization_type_coding`

---

### 2) Tabela `location`

Campos obrigatórios:

* `id` (PK)
* `name`
* `managing_organization_id` (FK -> `organization.id`, nullable)

### Regras importantes para `location`

* **Não carregar** as colunas:

  * `resource_type`
  * `status`

* **Não criar / não carregar** as tabelas:

  * `location_meta_profile`
  * `location_physical_type_coding`

---

### 3) Tabela `patient`

Campos obrigatórios:

* `id` (PK)
* `gender`
* `birth_date`
* `name`
* `identifier`
* `marital_status_coding`
* `race`
* `ethnicity`
* `birthsex`
* `managing_organization_id` (FK -> `organization.id`, nullable)

### Regras importantes para `patient`

* **Não carregar** a coluna:

  * `resource_type`

* **Não criar / não carregar** as tabelas:

  * `patient_meta_profile`
  * `patient_name`
  * `patient_identifier`
  * `patient_communication_language_coding`
  * `patient_marital_status_coding`
  * `patient_race`
  * `patient_ethnicity`
  * `patient_birthsex`

### Regras de consolidação no `patient`

Os valores abaixo devem ser carregados diretamente na tabela `patient`:

* `patient_name.family` -> coluna `name`
* `patient_identifier.value` -> coluna `identifier`
* `patient_marital_status_coding.code` -> coluna `marital_status_coding`
* `patient_race.text` -> coluna `race`
* `patient_ethnicity.text` -> coluna `ethnicity`
* `patient_birthsex.value_code` -> coluna `birthsex`

Se houver múltiplos valores possíveis em alguma dessas estruturas, adote uma estratégia clara e documentada.
Sugestão:

* usar o **primeiro valor válido encontrado**
* registrar essa decisão no código, README e CHANGELOG

---

## Regras de extração por recurso

### Organization

Arquivo:

* `./data/MimicOrganization.ndjson.gz`

Extrair apenas:

* `id`
* `name`

Ignorar o restante.

---

### Location

Arquivo:

* `./data/MimicLocation.ndjson.gz`

Extrair apenas:

* `id`
* `name`
* `managingOrganization.reference` -> `managing_organization_id`

Ignorar o restante.

---

### Patient

Arquivo:

* `./data/MimicPatient.ndjson.gz`

Extrair:

* `id`
* `gender`
* `birthDate` -> `birth_date`
* `name[*].family` -> `name`
* `identifier[*].value` -> `identifier`
* `maritalStatus.coding[*].code` -> `marital_status_coding`
* extensão race -> `race` (usar `text`)
* extensão ethnicity -> `ethnicity` (usar `text`)
* extensão birthsex -> `birthsex`
* `managingOrganization.reference` -> `managing_organization_id`

Ignorar:

* `resourceType`
* `meta.profile`
* `communication.language.coding`
* demais campos não necessários nesta fase

---

## Regras para extensões FHIR do Patient

### Race

URL:

* `http://hl7.org/fhir/us/core/StructureDefinition/us-core-race`

Extrair apenas:

* `text` -> coluna `race`

### Ethnicity

URL:

* `http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity`

Extrair apenas:

* `text` -> coluna `ethnicity`

### Birthsex

URL:

* `http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex`

Extrair apenas:

* `valueCode` -> coluna `birthsex`

Crie funções pequenas e reutilizáveis para extrair essas extensões.

---

## Estratégia para campos repetidos

Em vários pontos do FHIR existem listas, por exemplo:

* `name[*]`
* `identifier[*]`
* `maritalStatus.coding[*]`

Como nesta fase a modelagem será simplificada, adote uma regra explícita para carregar apenas um valor por coluna.

### Regra obrigatória

* usar o **primeiro valor não vazio e válido encontrado**

Implemente isso de forma reutilizável e documentada.

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
* `./config/database.yaml`
* `./config/logging.yaml`
* `./config/ingestion/common.yaml`
* `./config/ingestion/organization.yaml`
* `./config/ingestion/location.yaml`
* `./config/ingestion/patient.yaml`
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
* `src/ingestion/loaders/organization_loader.py`
* `src/ingestion/loaders/location_loader.py`
* `src/ingestion/loaders/patient_loader.py`
* `src/pipelines/base_resource_pipeline.py`
* `src/pipelines/ingest_organization.py`
* `src/pipelines/ingest_location.py`
* `src/pipelines/ingest_patient.py`
* `src/pipelines/ingest_all.py`
* `src/main.py`

Em `tests/`:

* `tests/unit/test_fhir_reference_parser.py`
* `tests/unit/test_ndjson_gzip_reader.py`
* `tests/unit/test_patient_transformer.py`
* `tests/unit/test_location_transformer.py`
* `tests/unit/test_organization_transformer.py`

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

## Parse de referência FHIR

Crie uma função reutilizável para extrair o ID de referências no formato:

* `Organization/<id>`

Exemplo:

* entrada: `"Organization/ee172322-118b-5716-abbc-18e4c5437e15"`
* saída: `"ee172322-118b-5716-abbc-18e4c5437e15"`

A função deve:

* usar type hints
* ter docstring detalhada em português
* validar formato
* permitir especificar o tipo esperado do recurso
* levantar exceção adequada em caso de valor inválido

---

## Testes de unidade obrigatórios

Crie testes de unidade cobrindo no mínimo:

### 1) Parser de referência FHIR

Casos:

* referência válida
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
* campos opcionais ausentes
* extração apenas de `id` e `name`

### 4) Transformer de Location

Casos:

* registro válido com `managingOrganization`
* registro sem `managingOrganization`
* referência inválida
* garantia de que `resource_type` e `status` não são carregados

### 5) Transformer de Patient

Casos:

* registro válido com:

  * name
  * identifier
  * marital status
  * race
  * ethnicity
  * birthsex
  * managingOrganization
* registro com campos opcionais ausentes
* extensões ausentes
* referência inválida
* garantia de que apenas as colunas simplificadas são retornadas

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

A execução principal deve ingerir os três arquivos na ordem definida.

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
* pré-requisitos
* configuração do `.env`
* estrutura de configuração em `./config`
* como instalar dependências com `uv`
* como executar a ingestão
* ordem de importação
* explicação dos relacionamentos:

  * `location -> organization`
  * `patient -> organization`
* explicação da simplificação da modelagem
* lista das tabelas finais realmente criadas
* localização dos logs
* comportamento de reset total do banco
* como executar os testes de unidade

O README deve ficar claro, organizado e útil para evolução futura.

---

## CHANGELOG obrigatório

Atualize o `CHANGELOG.md` com todas as mudanças relevantes desta evolução, incluindo:

* simplificação da modelagem relacional
* redução de tabelas auxiliares
* consolidação de atributos de patient na tabela principal
* remoção de colunas não necessárias em organization, location e patient
* manutenção da pipeline orquestrada
* manutenção da ordem de importação
* manutenção/criação das foreign keys necessárias
* logging em arquivo
* testes de unidade
* atualização do README
* eventuais refatorações arquiteturais feitas para suportar a simplificação

Use um formato limpo, consistente e legível.

---

## Entrega esperada

Forneça:

1. todos os arquivos criados ou alterados
2. conteúdo completo dos arquivos
3. instruções para instalar dependências com `uv`
4. instruções para executar a pipeline completa
5. instruções para executar os testes
6. explicação breve da nova modelagem simplificada
7. exemplo de saída esperada no terminal
8. exemplo de log gerado em arquivo

---

## Importante

* Não deixe credenciais hardcoded fora do `.env`
* Não concentre configurações em código quando puder movê-las para YAML
* Não implemente solução descartável
* A base deve estar preparada para ingestão futura de outros recursos FHIR
* Se precisar refatorar a implementação anterior para manter boa arquitetura, faça isso
* Preserve consistência entre código, README, CHANGELOG, configs e testes
* A modelagem final desta fase deve ser enxuta, pragmática e orientada ao uso analítico inicial
