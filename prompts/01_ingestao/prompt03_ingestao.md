Você está evoluindo um projeto Python do tipo NL2SQL2NL (Natural Language -> SQL -> Natural Language).

## Objetivo desta entrega
Expandir a pipeline orquestrada de ingestão para suportar agora os arquivos:

1. `./data/MimicOrganization.ndjson.gz`
2. `./data/MimicLocation.ndjson.gz`
3. `./data/MimicPatient.ndjson.gz`

Esta entrega fecha uma primeira fase de ingestão de arquivos de dimensões / base estrutural.

A ordem de importação deve ser **obrigatoriamente**:

1. `MimicOrganization`
2. `MimicLocation`
3. `MimicPatient`

Se existirem relacionamentos entre as tabelas, as **foreign keys devem ser criadas**.

Também são obrigatórios:
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

## Arquitetura desejada

Implemente a ingestão como uma **pipeline orquestrada de recursos**, preparada para crescer no futuro com outros recursos FHIR.

A ideia é que exista uma camada central de orquestração que:

* conheça a ordem de execução
* execute reset do banco
* crie schema/tabelas
* execute os pipelines dos recursos em ordem
* registre logs e estatísticas
* permita evolução para novos recursos com baixo acoplamento

Não implemente uma solução pontual. Estruture para suportar próximos recursos como `Encounter`, `Observation`, `Condition`, etc.

---

## Arquivos a ingerir

### 1) Organization

Arquivo:

* `./data/MimicOrganization.ndjson.gz`

Campos observados:

* `id`
* `resourceType`
* `active`
* `name`
* `meta.profile[*]`
* `identifier[*].system`
* `identifier[*].value`
* `type[*].coding[*].system`
* `type[*].coding[*].code`
* `type[*].coding[*].display`

### 2) Location

Arquivo:

* `./data/MimicLocation.ndjson.gz`

Campos observados:

* `id`
* `resourceType`
* `name`
* `status`
* `meta.profile[*]`
* `physicalType.coding[*].system`
* `physicalType.coding[*].code`
* `physicalType.coding[*].display`
* `managingOrganization.reference`

Relacionamento observado:

* `managingOrganization.reference = "Organization/<organization_id>"`

### 3) Patient

Arquivo:

* `./data/MimicPatient.ndjson.gz`

Campos observados:

* `id`
* `resourceType`
* `gender`
* `birthDate`
* `name[*].use`
* `name[*].family`
* `meta.profile[*]`
* `identifier[*].system`
* `identifier[*].value`
* `communication[*].language.coding[*].system`
* `communication[*].language.coding[*].code`
* `maritalStatus.coding[*].system`
* `maritalStatus.coding[*].code`
* `extension[*]` com estruturas para:

  * race
  * ethnicity
  * birthsex
* `managingOrganization.reference`

Relacionamento observado:

* `managingOrganization.reference = "Organization/<organization_id>"`

---

## Relacionamentos obrigatórios

Crie modelagem relacional explícita com foreign keys.

### Obrigatório

* `location.managing_organization_id -> organization.id`
* `patient.managing_organization_id -> organization.id`

Se a referência estiver ausente, a coluna pode ser nula.
Se existir, o valor deve ser parseado corretamente a partir do formato FHIR:

* `"Organization/<uuid>"`

Implemente função reutilizável para parse de referências FHIR.

---

## Modelagem esperada

### Tabelas para Organization

1. `organization`

   * `id` (PK)
   * `resource_type`
   * `active`
   * `name`

2. `organization_meta_profile`

   * `organization_id` (FK -> organization.id)
   * `profile`

3. `organization_identifier`

   * `organization_id` (FK -> organization.id)
   * `system`
   * `value`

4. `organization_type_coding`

   * `organization_id` (FK -> organization.id)
   * `system`
   * `code`
   * `display`

### Tabelas para Location

5. `location`

   * `id` (PK)
   * `resource_type`
   * `name`
   * `status`
   * `managing_organization_id` (FK -> organization.id, nullable)

6. `location_meta_profile`

   * `location_id` (FK -> location.id)
   * `profile`

7. `location_physical_type_coding`

   * `location_id` (FK -> location.id)
   * `system`
   * `code`
   * `display`

### Tabelas para Patient

8. `patient`

   * `id` (PK)
   * `resource_type`
   * `gender`
   * `birth_date`
   * `managing_organization_id` (FK -> organization.id, nullable)

9. `patient_meta_profile`

   * `patient_id` (FK -> patient.id)
   * `profile`

10. `patient_name`

* `patient_id` (FK -> patient.id)
* `use`
* `family`

11. `patient_identifier`

* `patient_id` (FK -> patient.id)
* `system`
* `value`

12. `patient_communication_language_coding`

* `patient_id` (FK -> patient.id)
* `system`
* `code`

13. `patient_marital_status_coding`

* `patient_id` (FK -> patient.id)
* `system`
* `code`

14. `patient_race`

* `patient_id` (FK -> patient.id)
* `omb_category_system`
* `omb_category_code`
* `omb_category_display`
* `text`

15. `patient_ethnicity`

* `patient_id` (FK -> patient.id)
* `omb_category_system`
* `omb_category_code`
* `omb_category_display`
* `text`

16. `patient_birthsex`

* `patient_id` (FK -> patient.id)
* `value_code`

Se julgar necessário, você pode melhorar a modelagem, mas:

* mantenha normalização adequada
* evite armazenar tudo como JSON bruto sem necessidade
* documente a decisão no código, README e CHANGELOG

---

## Regra para extensões FHIR do Patient

Implemente parse explícito das extensões observadas:

### Race

URL:

* `http://hl7.org/fhir/us/core/StructureDefinition/us-core-race`

Extrair:

* `ombCategory.valueCoding.system`
* `ombCategory.valueCoding.code`
* `ombCategory.valueCoding.display`
* `text`

### Ethnicity

URL:

* `http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity`

Extrair:

* `ombCategory.valueCoding.system`
* `ombCategory.valueCoding.code`
* `ombCategory.valueCoding.display`
* `text`

### Birthsex

URL:

* `http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex`

Extrair:

* `valueCode`

Crie funções pequenas e reutilizáveis para extrair essas extensões.

---

## Ordem obrigatória de execução

A pipeline principal deve executar exatamente nesta ordem:

1. reset completo do banco / schema relacionado
2. criação das tabelas
3. ingestão de `Organization`
4. ingestão de `Location`
5. ingestão de `Patient`

A orquestração deve estar centralizada em um pipeline principal, algo como `ingest_all`.

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

Se achar útil, inclua também testes de utilitários e configuração.

---

## Requisitos de implementação

Implemente:

1. leitura streaming de arquivos `.ndjson.gz`
2. parse linha a linha
3. validação mínima de cada registro
4. transformação para modelo relacional
5. criação/recriação completa do schema
6. inserção transacional
7. respeito à ordem de carga
8. criação de foreign keys
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

* registro válido com listas preenchidas
* campos opcionais ausentes

### 4) Transformer de Location

Casos:

* registro válido com `managingOrganization`
* registro sem `managingOrganization`
* referência inválida

### 5) Transformer de Patient

Casos:

* registro válido com:

  * name
  * identifier
  * marital status
  * communication
  * race
  * ethnicity
  * birthsex
  * managingOrganization
* registro com campos opcionais ausentes
* extensões ausentes
* referência inválida

### Requisitos dos testes

* usar `pytest`
* testes legíveis e pequenos
* fixtures quando fizer sentido
* sem depender do banco para testar transformers e parsers
* focar em unidade real, não pseudo-teste

Se fizer sentido, inclua também testes para carregadores com mocks.

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
* localização dos logs
* comportamento de reset total do banco
* como executar os testes de unidade

O README deve ficar claro, organizado e útil para evolução futura.

---

## CHANGELOG obrigatório

Atualize o `CHANGELOG.md` com todas as mudanças relevantes desta evolução, incluindo:

* adoção explícita da pipeline orquestrada de recursos
* suporte a ingestão de `Patient`
* manutenção da ordem de importação
* criação de foreign key de `patient` para `organization`
* tabelas auxiliares de `patient`
* logging em arquivo
* inclusão de testes de unidade
* atualização do README
* eventuais dependências adicionadas
* refatorações arquiteturais feitas para suportar crescimento

Use um formato limpo, consistente e legível.

---

## Entrega esperada

Forneça:

1. todos os arquivos criados ou alterados
2. conteúdo completo dos arquivos
3. instruções para instalar dependências com `uv`
4. instruções para executar a pipeline completa
5. instruções para executar os testes
6. explicação breve da modelagem
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
