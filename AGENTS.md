# AGENTS.md

Guia curto para continuar o desenvolvimento de `nl2sql2nl_mimic_fhir` sem perder o contexto das regras mais sensiveis do projeto.

## Visao Do Produto

- O projeto ingere recursos FHIR/MIMIC-FHIR compactados em `.ndjson.gz` para um PostgreSQL local.
- A pipeline transforma os recursos em um schema relacional simplificado para analise e para a interface Streamlit.
- A ordem de ingestao importa, porque varias tabelas dependem de tabelas pai ja carregadas.

## Estrutura Principal

- `src/main.py`: ponto de entrada da ingestao completa.
- `src/pipelines/`: pipelines por recurso e o orquestrador em `ingest_all.py`.
- `src/ingestion/loaders/`: persistencia e validacao de FKs antes do insert.
- `src/ingestion/transformers/`: normalizacao dos registros FHIR para o modelo relacional.
- `src/db/schema.py`: definicao do schema SQLAlchemy e dos dataclasses de agrupamento de tabelas.
- `src/ingestion/reference_table_resolver.py`: resolucao centralizada de tabelas de referencia para FKs.
- `tests/unit/`: cobertura de transformadores, loaders, schema e resolvedor de referencias.

## Regra Mais Importante Da Ingestao

Nao espalhar regras hardcoded de FK pelos loaders.

Use sempre o resolvedor central em `src/ingestion/reference_table_resolver.py` quando a tabela pai depender de excecoes de dominio.

Defaults atuais:

- `encounter_id -> encounter`
- `procedure_id -> procedure`

Overrides explicitos ja suportados:

- `condition_ed.encounter_id -> encounter_ed`
- `medication_dispense_ed.encounter_id -> encounter_ed`
- `medication_statement_ed.encounter_id -> encounter_ed`
- `procedure_ed.encounter_id -> encounter_ed`
- `observation_ed.encounter_id -> encounter_ed`
- `observation_ed.procedure_id -> procedure_ed`
- `observation_vital_signs_ed.encounter_id -> encounter_ed`
- `observation_vital_signs_ed.procedure_id -> procedure_ed`
- `procedure_icu.encounter_id -> encounter_icu`
- `medication_administration_icu.encounter_id -> encounter_icu`

Observacao importante:

- Tabelas genericas como `condition`, `procedure`, `medication_request`, `medication_dispense`, `medication_administration`, `observation_micro_test`, `encounter_ed` e `encounter_icu` devem manter o comportamento esperado no schema e no loader.
- Nao assumir que todo sufixo `_ed` ou `_icu` deve trocar FK automaticamente.

## Ajustes Recentes Que Viraram Convenicao

- `EncounterED` deve referenciar `encounter`.
- `EncounterICU` deve referenciar `encounter`.
- `ProcedureED` deve validar `encounter_id` contra `encounter_ed`.
- `ProcedureICU` deve validar `encounter_id` contra `encounter_icu`.
- `MedicationDispense` generico continua usando `encounter`.
- `MedicationRequest` generico continua usando `encounter`.
- `Condition` generico continua usando `encounter`.
- `ObservationMicroTest` generico continua usando `encounter`.

## Workflow Recomendado

1. Localize a resolucao de FK no wiring central em `src/pipelines/ingest_all.py`.
2. Se o caso for uma excecao de dominio, atualize `reference_table_resolver.py`.
3. Se a tabela fisica do schema estiver errada, ajuste `src/db/schema.py`.
4. Se o loader validar FKs, garanta que ele aceite a tabela resolvida sem depender de um grupo errado.
5. Atualize os testes de schema e do resolvedor.

## Testes E Lint

Comandos usados com mais frequencia:

```bash
uv run pytest tests/unit/test_schema_relationships.py tests/unit/test_reference_table_resolver.py tests/unit/test_reference_table_resolution_loaders.py tests/unit/test_condition_ed_loader.py tests/unit/test_procedure_loader.py tests/unit/test_medication_request_loader.py
uv run ruff check src/db/schema.py src/ingestion/reference_table_resolver.py src/ingestion/loaders/procedure_ed_loader.py src/pipelines/ingest_all.py tests/unit/test_schema_relationships.py tests/unit/test_reference_table_resolver.py tests/unit/test_reference_table_resolution_loaders.py
```

Quando mexer em ingestao, prefira sempre:

- rodar a suite focada acima;
- adicionar um teste de schema para o relacionamento afetado;
- adicionar um teste de resolver para o override afetado;
- adicionar um teste de loader para confirmar que a FK nao vira `NULL` quando a entidade existe na tabela correta.

## Convenios De Trabalho

- Nao reverter mudancas do usuario.
- Nao usar comandos destrutivos.
- Preferir `apply_patch` para edicao.
- Manter comentarios e nomes em ASCII quando possivel.
- Manter os arquivos de prompt e artefatos locais fora de commits, a menos que o usuario peça explicitamente.

## Estado Conhecido Do Projeto

- O projeto ja passou por varias correcoes de FK em tabelas ED e ICU.
- O ponto sensivel atual e manter alinhados: `schema.py`, `reference_table_resolver.py`, `ingest_all.py` e os testes.
- Se um novo erro de FK surgir, primeiro verifique se ele vem do schema fisico ou da validacao em runtime do loader.
- A tela `src/app/pages/individual_data.py` usa `PatientTimelineService` para montar a visao individual do paciente.
- O contexto `general_hospital` agora inclui `hospital_transfers` e `medication_events` para o `encounter_id` atual, alem de diagnosticos, procedimentos e medicamentos ja existentes.
- A query de transferencias usa `encounter_location` + `location`; a query de medicações usa `medication_request` + `medication` + `medication_administration` com `LEFT JOIN` para nao perder pedidos sem administracao.
- Em `medication_events`, o nome da medicacao pode ficar `NULL` quando nao houver `medication_id` e tambem nao existir `medication_code` na administracao associada.
