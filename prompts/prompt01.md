Você está trabalhando em um projeto Python do tipo NL2SQL2NL (Natural Language -> SQL -> Natural Language).

Objetivo desta tarefa:
Implementar a ingestão do arquivo `./data/MimicOrganization.ndjson.gz` para um banco PostgreSQL local, seguindo rigorosamente as regras abaixo.

## Contexto técnico
- Linguagem: Python
- Gerenciador de pacotes: `uv`
- Banco de dados: PostgreSQL rodando localmente em Docker
- Os arquivos de entrada ficam em `./data`
- As configurações não sensíveis devem ficar em arquivos YAML dentro de `./config`
- As credenciais de conexão devem ficar em um arquivo `.env`
- Evite ao máximo valores hardcoded
- Sempre que o processo de ingestão executar, toda a estrutura de tabelas e os dados devem ser destruídos e recriados do zero
- Registre todas as mudanças relevantes no arquivo `CHANGELOG.md`

## Configuração do banco
Crie um arquivo `.env` na raiz do projeto com estas variáveis:

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app_mimic_fhir
POSTGRES_USER=app_mimic_fhir
POSTGRES_PASSWORD=app_mimic_fhir

## Requisitos funcionais
Implemente a ingestão do arquivo `./data/MimicOrganization.ndjson.gz`.

O arquivo é um NDJSON compactado com gzip e contém recursos FHIR do tipo `Organization`.

Estrutura observada no arquivo:
- `id`: string
- `resourceType`: string
- `active`: boolean
- `name`: string
- `meta.profile`: lista de strings
- `identifier`: lista de objetos com campos como:
  - `system`
  - `value`
- `type`: lista de objetos, contendo:
  - `coding`: lista de objetos com campos como:
    - `system`
    - `code`
    - `display`

Mesmo que o arquivo atual tenha poucos registros, a implementação deve ser genérica e preparada para volumes maiores.

## Modelagem esperada
Crie uma modelagem relacional normalizada, evitando guardar tudo como JSON bruto sem necessidade.

Sugestão de tabelas:
1. `organization`
   - `id` (PK)
   - `resource_type`
   - `active`
   - `name`

2. `organization_meta_profile`
   - `organization_id` (FK -> organization.id)
   - `profile`

3. `organization_identifier`
   - `organization_id` (FK -> organization.id)
   - `system`
   - `value`

4. `organization_type_coding`
   - `organization_id` (FK -> organization.id)
   - `system`
   - `code`
   - `display`

Se houver necessidade, você pode ajustar a modelagem, mas explique no código e no changelog a justificativa.

## Requisitos de implementação
Implemente:
1. Leitura do arquivo `.ndjson.gz`
2. Parse linha a linha sem carregar tudo em memória desnecessariamente
3. Validação mínima dos registros
4. Criação/recriação completa do schema/tabelas
5. Inserção transacional dos dados
6. Logging claro do processo
7. Separação por camadas

## Estrutura sugerida de arquivos
Você pode criar ou ajustar algo semelhante a:

- `.env`
- `./config/database.yaml`
- `./config/ingestion/organization.yaml`
- `./src/...`

Sugestão de módulos:
- `src/config/settings.py`
- `src/db/connection.py`
- `src/db/schema.py`
- `src/ingestion/readers/ndjson_gzip_reader.py`
- `src/ingestion/transformers/organization_transformer.py`
- `src/ingestion/loaders/organization_loader.py`
- `src/pipelines/ingest_organization.py`
- `src/main.py`

## Configurações em YAML
Crie arquivos YAML dentro de `./config` para concentrar configurações não sensíveis, por exemplo:
- nome da tabela
- caminho padrão do arquivo de entrada
- tamanho de batch
- schema do banco
- política de reset
- nomes lógicos do pipeline

As credenciais devem permanecer no `.env`.

## Reset completo a cada execução
A execução da ingestão deve:
1. abrir conexão com o banco
2. destruir todas as tabelas relacionadas à ingestão atual
3. recriar toda a estrutura
4. inserir os dados novamente

Esse comportamento deve ser explícito, previsível e configurável via YAML, mas o default desta tarefa deve ser “drop and recreate”.

## Qualidade de código
Todo o código gerado deve seguir este padrão:

- type hints completos
- docstrings detalhadas em português
- tratamento de exceções
- nomes claros e consistentes
- funções pequenas e coesas
- evitar acoplamento desnecessário
- evitar números mágicos e strings hardcoded
- código pronto para manutenção

Siga o estilo abaixo para funções e métodos:

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
````

## Dependências

Adicione apenas dependências realmente necessárias. Priorize bibliotecas leves e maduras.

Sugestão:

* `sqlalchemy`
* `psycopg[binary]` ou equivalente compatível
* `pydantic` ou `pydantic-settings` se fizer sentido
* `pyyaml`
* ferramentas de logging padrão da biblioteca padrão, se possível

Use `uv` para gerenciar dependências.

## Interface de execução

Crie uma forma simples de executar a ingestão, por exemplo:

* `python -m src.main`
  ou
* um entrypoint equivalente claro

A execução deve processar especificamente o arquivo `MimicOrganization.ndjson.gz`.

## Requisitos de robustez

* Validar existência do arquivo
* Validar extensão esperada
* Validar JSON por linha
* Ignorar ou falhar de forma controlada em registros inválidos
* Garantir rollback em caso de falha no carregamento
* Exibir resumo final:

  * quantidade de registros lidos
  * quantidade de registros inseridos
  * tempo de execução
  * tabelas afetadas

## CHANGELOG

Atualize o arquivo `CHANGELOG.md` com todas as mudanças relevantes desta entrega:

* criação de `.env`
* criação dos YAMLs
* criação da estrutura de banco
* criação do pipeline de ingestão
* dependências adicionadas
* instruções de execução

Use um formato organizado e legível.

## Entrega esperada

Forneça:

1. todos os arquivos necessários
2. conteúdo completo dos arquivos criados/alterados
3. instruções para instalar dependências com `uv`
4. instruções para executar a ingestão
5. explicação curta da modelagem adotada
6. exemplo de saída esperada no terminal

## Importante

* Não deixe credenciais hardcoded fora do `.env`
* Não concentre configurações em código quando puder movê-las para YAML
* Não implemente solução descartável; ela deve servir como base para próximas ingestões de outros arquivos FHIR
* Escreva código limpo, modular e extensível, pois outros arquivos serão adicionados depois
* Mantenha o foco nesta etapa de ingestão