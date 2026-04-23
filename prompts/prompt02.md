Você está evoluindo um projeto Python do tipo NL2SQL2NL (Natural Language -> SQL -> Natural Language).

## Objetivo desta entrega
Expandir o pipeline de ingestão para suportar agora **dois arquivos FHIR**:

1. `./data/MimicOrganization.ndjson.gz`
2. `./data/MimicLocation.ndjson.gz`

A ordem de importação deve ser **obrigatoriamente**:
1. `MimicOrganization`
2. `MimicLocation`

Há relacionamento entre os recursos e, portanto, as **foreign keys devem ser criadas**.

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
- Atualize também o `README.md`
- O log da aplicação deve ser salvo em arquivo dentro da pasta `./logs`

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

## Requisitos funcionais

Implementar a ingestão dos arquivos:

* `./data/MimicOrganization.ndjson.gz`
* `./data/MimicLocation.ndjson.gz`

Ambos são arquivos NDJSON compactados com gzip.

### Estrutura observada dos recursos

### 1) Organization

Campos observados:

* `id`: string
* `resourceType`: string
* `active`: boolean
* `name`: string
* `meta.profile`: lista de strings
* `identifier[*].system`
* `identifier[*].value`
* `type[*].coding[*].system`
* `type[*].coding[*].code`
* `type[*].coding[*].display`

### 2) Location

Campos observados:

* `id`: string
* `resourceType`: string
* `name`: string
* `status`: string
* `meta.profile`: lista de strings
* `physicalType.coding[*].system`
* `physicalType.coding[*].code`
* `physicalType.coding[*].display`
* `managingOrganization.reference`

Exemplo do relacionamento:
`managingOrganization.reference = "Organization/<organization_id>"`

Você deve extrair o `<organization_id>` e persisti-lo como chave estrangeira.

---

## Regra de relacionamento

Crie relacionamento relacional explícito entre Location e Organization.

### Obrigatório

A tabela principal de location deve conter algo como:

* `managing_organization_id` (FK -> `organization.id`)

Se o campo `managingOrganization.reference` estiver ausente, a coluna pode ser nula.
Se existir, o valor deve ser parseado corretamente a partir do formato FHIR:

* `"Organization/<uuid>"`

Implemente validação robusta para esse parse.

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
   * `managing_organization_id` (FK -> organization.id, nullable se necessário)

6. `location_meta_profile`

   * `location_id` (FK -> location.id)
   * `profile`

7. `location_physical_type_coding`

   * `location_id` (FK -> location.id)
   * `system`
   * `code`
   * `display`

Se achar necessário, você pode melhorar a modelagem, mas:

* mantenha-a normalizada
* evite guardar tudo como JSON bruto sem necessidade
* documente a decisão no código, README e CHANGELOG

---

## Ordem obrigatória de execução

A pipeline principal deve executar exatamente nesta ordem:

1. reset completo do banco / schema relacionado
2. criação das tabelas
3. ingestão de `Organization`
4. ingestão de `Location`

Essa ordem deve ser respeitada porque `Location` depende de `Organization`.

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

### Requisitos de log

* salvar logs em arquivo dentro da pasta `./logs`
* criar a pasta automaticamente se não existir
* também permitir saída no console
* registrar:

  * início do processo
  * arquivo sendo processado
  * schema resetado
  * tabelas criadas
  * quantidade de registros lidos
  * quantidade de registros inseridos
  * falhas de parsing
  * falhas de integridade
  * tempo total de execução
* usar rotação de logs se for simples de implementar, preferencialmente com biblioteca padrão (`logging.handlers`)

Sugestão:

* `./logs/ingestion.log`

Evite hardcode excessivo: path de log e nível de log devem estar em YAML.

---

## Configurações em YAML

Centralize configurações não sensíveis em arquivos YAML dentro de `./config`.

Sugestão de estrutura:

* `./config/database.yaml`
* `./config/logging.yaml`
* `./config/ingestion/common.yaml`
* `./config/ingestion/organization.yaml`
* `./config/ingestion/location.yaml`

Esses arquivos podem conter, por exemplo:

* schema do banco
* política de reset
* batch size
* caminhos padrão dos arquivos
* nomes das tabelas
* ordem de ingestão
* configurações de log
* nível de log
* nome do arquivo de log

Credenciais devem continuar no `.env`.

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

E em `src/`:

* `src/config/settings.py`
* `src/config/yaml_loader.py`
* `src/logging/logger.py`
* `src/db/connection.py`
* `src/db/schema.py`
* `src/db/reset.py`
* `src/ingestion/readers/ndjson_gzip_reader.py`
* `src/ingestion/transformers/organization_transformer.py`
* `src/ingestion/transformers/location_transformer.py`
* `src/ingestion/loaders/organization_loader.py`
* `src/ingestion/loaders/location_loader.py`
* `src/pipelines/ingest_organization.py`
* `src/pipelines/ingest_location.py`
* `src/pipelines/ingest_all.py`
* `src/main.py`

A estrutura exata pode variar, desde que fique limpa, modular e extensível.

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

---

## Robustez e validações

Implemente tratamento robusto para:

* arquivo inexistente
* extensão inválida
* JSON inválido por linha
* ausência de campos importantes
* referência FHIR inválida em `managingOrganization.reference`
* erro de integridade referencial
* rollback em caso de falha

A ingestão deve falhar de forma controlada, com mensagens claras.

---

## Parse da referência FHIR

Crie uma função específica para extrair o ID da organização a partir de:

* `Organization/<id>`

Exemplo:

* entrada: `"Organization/ee172322-118b-5716-abbc-18e4c5437e15"`
* saída: `"ee172322-118b-5716-abbc-18e4c5437e15"`

Essa função deve:

* usar type hints
* ter docstring detalhada em português
* validar formato
* levantar exceção adequada se inválido

---

## Interface de execução

Crie uma forma simples de executar a ingestão completa, por exemplo:

```bash
python -m src.main
```

ou equivalente.

A execução principal deve ingerir os dois arquivos na ordem definida.

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

Siga o formato de funções abaixo:

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
* biblioteca padrão `logging`

Evite dependências desnecessárias.

---

## README obrigatório

Atualize o `README.md` com pelo menos:

* visão geral da ingestão
* pré-requisitos
* configuração do `.env`
* estrutura dos arquivos em `./config`
* como instalar dependências com `uv`
* como executar a ingestão
* ordem de importação
* explicação do relacionamento entre `Organization` e `Location`
* localização dos logs
* comportamento de reset total do banco

O README deve ficar claro e útil para manutenção futura.

---

## CHANGELOG obrigatório

Atualize o `CHANGELOG.md` com todas as mudanças relevantes desta evolução, incluindo:

* suporte a ingestão de `Location`
* ordem de importação definida
* criação de foreign key entre `location` e `organization`
* criação/configuração de logging em arquivo
* criação/ajuste de YAMLs
* atualização do pipeline principal
* atualização do README
* eventuais dependências adicionadas

Use um formato limpo, consistente e legível.

---

## Entrega esperada

Forneça:

1. todos os arquivos criados ou alterados
2. conteúdo completo dos arquivos
3. instruções para instalar dependências com `uv`
4. instruções para executar a pipeline completa
5. explicação breve da modelagem
6. exemplo de saída esperada no terminal
7. exemplo de log gerado em arquivo

---

## Importante

* Não deixe credenciais hardcoded fora do `.env`
* Não concentre configurações em código quando puder movê-las para YAML
* Não implemente uma solução descartável
* A base deve estar preparada para ingestão futura de outros recursos FHIR
* Respeite rigorosamente a qualidade de código
* Preserve consistência arquitetural entre os módulos
* Se precisar refatorar a implementação anterior de Organization para manter boa arquitetura, faça isso