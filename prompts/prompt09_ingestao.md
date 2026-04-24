Você está evoluindo um projeto Python do tipo NL2SQL2NL (Natural Language -> SQL -> Natural Language).

## Objetivo desta entrega
Expandir a pipeline orquestrada de ingestão para suportar agora o arquivo:

8. `./data/MimicMedicationMix.ndjson.gz`

Esta entrega dá seguimento à **terceira fase de ingestão de arquivos**.

A ordem de importação deve ser tratada de forma consistente com a pipeline já existente, preservando os recursos anteriores e adicionando `MedicationMix`.

### Ordem completa da pipeline
1. `MimicOrganization`
2. `MimicLocation`
3. `MimicPatient`
4. `MimicEncounter`
5. `MimicEncounterED`
6. `MimicEncounterICU`
7. `MimicMedication`
8. `MimicMedicationMix`

Se existirem relacionamentos entre as tabelas, as **foreign keys devem ser criadas**.

Também continuam obrigatórios:
- qualidade de código
- atualização de `README.md`
- atualização de `CHANGELOG.md`
- logging em arquivo
- testes de unidade
- atualização do `TABLE_RELATIONSHIPS.md`

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

A inclusão de `MedicationMix` deve seguir o mesmo padrão arquitetural já adotado.

---

## Ordem obrigatória da pipeline

A pipeline principal deve executar exatamente nesta ordem:

1. reset completo do banco / schema relacionado
2. criação das tabelas
3. ingestão de `Organization`
4. ingestão de `Location`
5. ingestão de `Patient`
6. ingestão de `Encounter`
7. ingestão de `EncounterED`
8. ingestão de `EncounterICU`
9. ingestão de `Medication`
10. ingestão de `MedicationMix`

Essa orquestração deve continuar centralizada em uma pipeline principal, como `ingest_all`.

---

## Modelagem simplificada atual que deve ser preservada

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

### encounter

Campos:

* `id` (PK)
* `patient_id` (FK -> patient.id, nullable)
* `organization_id` (FK -> organization.id, nullable)
* `status`
* `class_code`
* `start_date`
* `end_date`
* `priority_code`
* `service_type_code`
* `admit_source_code`
* `discharge_disposition_code`
* `identifier`

### encounter_location

Campos:

* `encounter_id` (FK -> encounter.id)
* `location_id` (FK -> location.id)
* `start_date` (nullable)
* `end_date` (nullable)

### encounter_ed

Campos:

* `id` (PK)
* `encounter_id` (FK -> encounter.id, nullable)
* `patient_id` (FK -> patient.id, nullable)
* `organization_id` (FK -> organization.id, nullable)
* `status`
* `class_code`
* `start_date`
* `end_date`
* `admit_source_code`
* `discharge_disposition_code`
* `identifier`

### encounter_icu

Campos:

* `id` (PK)
* `encounter_id` (FK -> encounter.id, nullable)
* `patient_id` (FK -> patient.id, nullable)
* `status`
* `class_code`
* `start_date`
* `end_date`
* `identifier`

### encounter_icu_location

Campos:

* `encounter_icu_id` (FK -> encounter_icu.id)
* `location_id` (FK -> location.id)
* `start_date` (nullable)
* `end_date` (nullable)

### medication

Campos:

* `id` (PK)
* `code`
* `code_system`
* `status`
* `ndc`
* `formulary_drug_cd`
* `name`

Essas tabelas devem ser mantidas.

---

## Novo recurso a ingerir: MedicationMix

Arquivo:

* `./data/MimicMedicationMix.ndjson.gz`

### Estrutura observada no arquivo

Campos observados:

* `id`
* `status`
* `identifier[*].system`
* `identifier[*].value`
* `ingredient[*].itemReference.reference`
* `meta.profile`
* `text.div`
* `resourceType`

### Relacionamento identificado

Foi identificado relacionamento explícito com `Medication`:

* `ingredient[*].itemReference.reference = "Medication/<medication_id>"`

Portanto, `MedicationMix` **deve possuir relacionamento relacional com `Medication`**.

---

## Diretriz de modelagem para MedicationMix

Mantenha a filosofia de modelagem **enxuta e pragmática**.

### Criar tabela principal `medication_mix`

Campos obrigatórios sugeridos:

* `id` (PK)
* `status`
* `identifier`

### Regras de simplificação para `medication_mix`

* **Não carregar**:

  * `resourceType`
  * `meta.profile`
  * `text.div`
  * `text.status`
  * demais campos não essenciais nesta fase

### Regra para identifier

Extrair o **primeiro valor não vazio e válido** de:

* `identifier[*].value` -> coluna `identifier`

Se quiser, você pode usar também o system apenas para localizar o identificador correto, mas não precisa persisti-lo se ele não agregar valor analítico nesta fase.

---

## Relacionamento com Medication

Como `MedicationMix` contém múltiplos ingredientes em `ingredient[*]`, você deve preservar esse relacionamento em uma tabela auxiliar enxuta.

### Criar tabela `medication_mix_ingredient`

Campos:

* `medication_mix_id` (FK -> `medication_mix.id`)
* `medication_id` (FK -> `medication.id`)

Cada item de `ingredient[*]` deve gerar um registro nessa tabela.

### Regra obrigatória

Extrair:

* `ingredient[*].itemReference.reference` -> `medication_id`

Usar parse robusto do formato:

* `Medication/<id>`

---

## Relacionamentos obrigatórios

Mantenha/crie as foreign keys já existentes:

* `location.managing_organization_id -> organization.id`
* `patient.managing_organization_id -> organization.id`
* `encounter.patient_id -> patient.id`
* `encounter.organization_id -> organization.id`
* `encounter_location.encounter_id -> encounter.id`
* `encounter_location.location_id -> location.id`
* `encounter_ed.encounter_id -> encounter.id`
* `encounter_ed.patient_id -> patient.id`
* `encounter_ed.organization_id -> organization.id`
* `encounter_icu.encounter_id -> encounter.id`
* `encounter_icu.patient_id -> patient.id`
* `encounter_icu_location.encounter_icu_id -> encounter_icu.id`
* `encounter_icu_location.location_id -> location.id`

### Novas foreign keys obrigatórias

* `medication_mix_ingredient.medication_mix_id -> medication_mix.id`
* `medication_mix_ingredient.medication_id -> medication.id`

### Importante

Não crie FKs extras para `MedicationMix` sem evidência explícita no arquivo.

---

## Parse de referências FHIR

Mantenha e reutilize a função de parse de referências FHIR para os recursos que possuem referência.

Ela deve continuar suportando:

* `Organization/<id>`
* `Patient/<id>`
* `Location/<id>`
* `Encounter/<id>`
* `Medication/<id>`

A função deve:

* usar type hints
* ter docstring detalhada em português
* validar formato
* permitir especificar o tipo esperado do recurso
* levantar exceção adequada em caso de valor inválido

---

## Regras de extração para MedicationMix

### Tabela `medication_mix`

Extrair:

* `id`
* `status`
* `identifier[*].value` -> `identifier`

### Tabela `medication_mix_ingredient`

Extrair de `ingredient[*]`:

* `itemReference.reference` -> `medication_id`

Cada item da lista `ingredient[*]` deve gerar um registro em `medication_mix_ingredient`.

### Regras de extração

* Para `identifier[*]`, usar o **primeiro valor não vazio e válido encontrado**
* Para `ingredient[*]`, gerar todos os relacionamentos válidos encontrados
* Se houver referência inválida em `ingredient[*]`, tratar de forma robusta e com log claro

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
* `./config/ingestion/encounter_ed.yaml`
* `./config/ingestion/encounter_icu.yaml`
* `./config/ingestion/medication.yaml`
* `./config/ingestion/medication_mix.yaml`
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
* `TABLE_RELATIONSHIPS.md`
* `./config/database.yaml`
* `./config/logging.yaml`
* `./config/ingestion/common.yaml`
* `./config/ingestion/organization.yaml`
* `./config/ingestion/location.yaml`
* `./config/ingestion/patient.yaml`
* `./config/ingestion/encounter.yaml`
* `./config/ingestion/encounter_ed.yaml`
* `./config/ingestion/encounter_icu.yaml`
* `./config/ingestion/medication.yaml`
* `./config/ingestion/medication_mix.yaml`
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
* `src/ingestion/transformers/encounter_ed_transformer.py`
* `src/ingestion/transformers/encounter_icu_transformer.py`
* `src/ingestion/transformers/medication_transformer.py`
* `src/ingestion/transformers/medication_mix_transformer.py`
* `src/ingestion/loaders/organization_loader.py`
* `src/ingestion/loaders/location_loader.py`
* `src/ingestion/loaders/patient_loader.py`
* `src/ingestion/loaders/encounter_loader.py`
* `src/ingestion/loaders/encounter_ed_loader.py`
* `src/ingestion/loaders/encounter_icu_loader.py`
* `src/ingestion/loaders/medication_loader.py`
* `src/ingestion/loaders/medication_mix_loader.py`
* `src/pipelines/base_resource_pipeline.py`
* `src/pipelines/ingest_organization.py`
* `src/pipelines/ingest_location.py`
* `src/pipelines/ingest_patient.py`
* `src/pipelines/ingest_encounter.py`
* `src/pipelines/ingest_encounter_ed.py`
* `src/pipelines/ingest_encounter_icu.py`
* `src/pipelines/ingest_medication.py`
* `src/pipelines/ingest_medication_mix.py`
* `src/pipelines/ingest_all.py`
* `src/main.py`

Em `tests/`:

* `tests/unit/test_fhir_reference_parser.py`
* `tests/unit/test_ndjson_gzip_reader.py`
* `tests/unit/test_organization_transformer.py`
* `tests/unit/test_location_transformer.py`
* `tests/unit/test_patient_transformer.py`
* `tests/unit/test_encounter_transformer.py`
* `tests/unit/test_encounter_ed_transformer.py`
* `tests/unit/test_encounter_icu_transformer.py`
* `tests/unit/test_medication_transformer.py`
* `tests/unit/test_medication_mix_transformer.py`

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
12. atualização do arquivo markdown com o relacionamento entre as tabelas

---

## TABLE_RELATIONSHIPS.md

Atualize o `TABLE_RELATIONSHIPS.md` na raiz do projeto.

### Diretriz obrigatória

O arquivo deve continuar com **diversos diagramas ASCII menores**, separados por assunto, para facilitar o entendimento por partes.

### Objetivo

Tornar a documentação relacional mais fácil de ler, navegando por blocos de relacionamento.

### O arquivo deve conter

* explicação breve do objetivo do documento
* lista das tabelas existentes
* explicação das foreign keys
* seções com diagramas ASCII segmentados

### Diagramas mínimos esperados

Atualize os diagramas para refletir a modelagem já existente e incluir `medication_mix`.

#### 1. organization - location

Mostrar:

* `location.managing_organization_id -> organization.id`

#### 2. patient - organization

Mostrar:

* `patient.managing_organization_id -> organization.id`

#### 3. encounter - patient - organization

Mostrar:

* `encounter.patient_id -> patient.id`
* `encounter.organization_id -> organization.id`

#### 4. encounter - location

Mostrar:

* `encounter_location.encounter_id -> encounter.id`
* `encounter_location.location_id -> location.id`

#### 5. encounter e encounterED

Mostrar:

* `encounter_ed.encounter_id -> encounter.id`
* `encounter_ed.patient_id -> patient.id`
* `encounter_ed.organization_id -> organization.id`

#### 6. encounter e encounterICU

Mostrar:

* `encounter_icu.encounter_id -> encounter.id`
* `encounter_icu.patient_id -> patient.id`
* `encounter_icu_location.encounter_icu_id -> encounter_icu.id`
* `encounter_icu_location.location_id -> location.id`

#### 7. medication

Como `medication` ainda não possui FK para os demais recursos clínicos nesta fase, mostrar isso explicitamente.

#### 8. medication_mix e medication

Mostrar:

* `medication_mix_ingredient.medication_mix_id -> medication_mix.id`
* `medication_mix_ingredient.medication_id -> medication.id`

#### 9. visão consolidada

Além dos diagramas segmentados, pode haver uma visão geral resumida ao final, desde que os diagramas por parte sejam o foco principal.

### Requisito importante

Os diagramas devem refletir **exatamente a modelagem final implementada**.

Use arte ASCII clara, legível e consistente.

---

## Robustez e validações

Implemente tratamento robusto para:

* arquivo inexistente
* extensão inválida
* JSON inválido por linha
* ausência de campos importantes
* erro de transformação
* referência inválida em ingredient
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
* referência válida para `Encounter`
* referência válida para `Medication`
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

### 7) Transformer de EncounterED

Casos:

* registro válido com:

  * `partOf.reference`
  * `subject.reference`
  * `serviceProvider.reference`
  * `identifier`
  * `hospitalization.admitSource`
  * `hospitalization.dischargeDisposition`
* registro sem `partOf`
* registro sem `serviceProvider`
* registro sem `hospitalization`
* referência inválida em `partOf`
* referência inválida em `subject`

### 8) Transformer de EncounterICU

Casos:

* registro válido com:

  * `partOf.reference`
  * `subject.reference`
  * `identifier`
  * múltiplas locations
* registro sem `partOf`
* registro sem `subject`
* registro sem `location`
* referência inválida em `partOf`
* referência inválida em `subject`
* referência inválida em `location`

### 9) Transformer de Medication

Casos:

* registro válido com:

  * `code.coding`
  * `status`
  * identificador NDC
  * identificador formulary drug cd
  * identificador name
* registro sem um ou mais identificadores
* registro com `code.coding` vazio
* registro com campos opcionais ausentes
* garantia de que apenas as colunas simplificadas são retornadas
* garantia de que systems corretos são mapeados para colunas corretas

### 10) Transformer de MedicationMix

Casos:

* registro válido com:

  * `status`
  * `identifier`
  * múltiplos ingredientes
* registro sem `identifier`
* registro sem `ingredient`
* referência inválida em `ingredient`
* garantia de que a tabela principal simplificada é retornada corretamente
* garantia de que a tabela derivada `medication_mix_ingredient` é montada corretamente

### Requisitos dos testes

* usar `pytest`
* testes legíveis e pequenos
* fixtures quando fizer sentido
* sem depender do banco para testar transformers e parsers
* focar em unidade real, não pseudo-teste

---

## Interface de execução

Crie uma forma simples de executar a ingestão completa, por exemplo:

```bash id="69795"
python -m src.main
```

ou equivalente.

A execução principal deve ingerir os oito arquivos na ordem definida.

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

```python id="67646"
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
* separação entre primeira, segunda e terceira fase de ingestão
* pré-requisitos
* configuração do `.env`
* estrutura de configuração em `./config`
* como instalar dependências com `uv`
* como executar a ingestão
* ordem de importação
* explicação dos relacionamentos existentes
* explicação de que `medication` entra como dimensão independente
* explicação de que `medication_mix` se relaciona com `medication` por meio de seus ingredientes
* explicação da modelagem simplificada
* lista das tabelas finais realmente criadas
* localização dos logs
* comportamento de reset total do banco
* como executar os testes de unidade
* referência ao `TABLE_RELATIONSHIPS.md`

O README deve ficar claro, organizado e útil para evolução futura.

---

## CHANGELOG obrigatório

Atualize o `CHANGELOG.md` com todas as mudanças relevantes desta evolução, incluindo:

* continuidade da terceira fase de ingestão
* suporte a ingestão de `MedicationMix`
* atualização da ordem da pipeline
* criação da tabela `medication_mix`
* criação da tabela `medication_mix_ingredient`
* criação das FKs entre `medication_mix` e `medication`
* atualização do `TABLE_RELATIONSHIPS.md`
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
6. explicação breve da nova modelagem com `medication_mix`
7. exemplo de saída esperada no terminal
8. exemplo de log gerado em arquivo
9. conteúdo atualizado do `TABLE_RELATIONSHIPS.md`

---

## Importante

* Não deixe credenciais hardcoded fora do `.env`
* Não concentre configurações em código quando puder movê-las para YAML
* Não implemente solução descartável
* A base deve estar preparada para ingestão futura de outros recursos FHIR
* Se precisar refatorar a implementação anterior para manter boa arquitetura, faça isso
* Preserve consistência entre código, README, CHANGELOG, configs, testes e documentação relacional
* A modelagem final desta fase deve ser enxuta, pragmática e orientada ao uso analítico inicial
