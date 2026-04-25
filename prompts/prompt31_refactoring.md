Você está evoluindo o projeto Python NL2SQL2NL.

## Objetivo
Refatorar a modelagem e os transformers/loaders da pipeline de ingestão para remover colunas de `system` e outras colunas não necessárias durante a ingestão.

Essa alteração deve ser aplicada em:
- models/schema
- transformers
- loaders
- testes unitários
- README.md
- CHANGELOG.md
- TABLE_RELATIONSHIPS.md
- configs YAML, se aplicável

## Regra geral
Remover das tabelas finais e do processo de ingestão todas as colunas listadas abaixo.

Não basta deixar a coluna nula: ela não deve ser criada no banco, não deve ser retornada pelos transformers e não deve ser inserida pelos loaders.

## Correções por tabela

### 1. condition
Não ingerir:
- `condition_code_system`
- `category_system`

Manter, se já existirem:
- `condition_code`
- `condition_code_display`
- `category_code`
- `category_display`

### 2. condition_ed
Não ingerir:
- `condition_code_system`
- `category_system`

Manter:
- `condition_code`
- `condition_code_display`
- `category_code`
- `category_display`

### 3. medication
Não ingerir:
- `code_system`

Manter:
- `code`
- `status`
- `ndc`
- `formulary_drug_cd`
- `name`

### 4. medication_administration
Não ingerir:
- `medication_code_system`
- `dose_system`
- `method_system`

Manter:
- `medication_code`
- `dose_value`
- `dose_unit`
- `dose_code`
- `method_code`

### 5. medication_administration_icu
Não ingerir:
- `category_system`
- `medication_code_system`
- `dose_system`
- `method_system`

Manter:
- `category_code`
- `medication_code`
- `medication_code_display`
- `dose_value`
- `dose_unit`
- `dose_code`
- `method_code`

### 6. medication_dispense
Não ingerir:
- `medication_code_system`

Manter:
- `medication_code`

### 7. medication_dispense_ed
Não ingerir:
- `medication_code_system`

Manter:
- `medication_code`
- `medication_text`

### 8. medication_statement_ed
Não ingerir:
- `medication_code_system`

Manter:
- `medication_code`
- `medication_code_display`
- `medication_text`

### 9. observation_chartevents
Não ingerir:
- `observation_code_system`
- `category_system`
- `value_system`

Manter:
- `observation_code`
- `observation_code_display`
- `category_code`
- `value`
- `value_unit`
- `value_code`
- `value_string`

### 10. observation_datetimeevents
Não ingerir:
- `observation_code_system`
- `category_system`
- `value_system`

Observação: se `value_system` não existir atualmente nessa tabela, apenas garanta que ela não seja criada nem referenciada.

Manter:
- `observation_code`
- `observation_code_display`
- `category_code`
- `value_datetime`

### 11. observation_ed
Não ingerir:
- `observation_code_system`
- `data_absent_reason_system`
- `value_system`

Observação: se `value_system` não existir atualmente nessa tabela, apenas garanta que ela não seja criada nem referenciada.

Manter:
- `observation_code`
- `observation_code_display`
- `category_code`
- `category_system`, se ela existir atualmente e não estiver listada para remoção
- `category_display`
- `value_string`
- `data_absent_reason_code`
- `data_absent_reason_display`

### 12. observation_labevents
Não ingerir:
- `observation_code_system`
- `category_system`
- `value_system`

Manter:
- `observation_code`
- `observation_code_display`
- `category_code`
- `category_display`
- `value`
- `value_unit`
- `value_code`

### 13. observation_micro_org
Não ingerir:
- `organism_code_system`
- `category_system`
- `value_system`

Observação: se `value_system` não existir atualmente nessa tabela, apenas garanta que ela não seja criada nem referenciada.

Manter:
- `organism_code`
- `organism_code_display`
- `category_code`
- `category_display`
- `value_string`

### 14. observation_micro_susc
Atenção: se a tabela estiver nomeada como `observation_micro_susc`, aplique nela.  
Se estiver nomeada como `observation_susc`, alinhe o nome usado no projeto e documente.

Não ingerir:
- `antibiotic_code_system`
- `category_system`
- `interpretation_system`

Manter:
- `antibiotic_code`
- `antibiotic_code_display`
- `category_code`
- `category_display`
- `interpretation_code`
- `interpretation_display`

### 15. observation_micro_test
Atenção: se a tabela estiver nomeada como `observation_micro_test`, aplique nela.  
Se estiver nomeada como `observation_test`, alinhe o nome usado no projeto e documente.

Não ingerir:
- `observation_code_system`
- `category_system`
- `value_code_system`

Manter:
- `observation_code`
- `observation_code_display`
- `category_code`
- `category_display`
- `value_code`
- `value_code_display`
- `value_string`

### 16. observation_outputevents
Não ingerir:
- `observation_code_system`
- `category_system`
- `value_system`

Manter:
- `observation_code`
- `observation_code_display`
- `category_code`
- `value`
- `value_unit`
- `value_code`

### 17. observation_vital_signs_ed
Não ingerir:
- `observation_code_system`
- `category_system`
- `value_system`

Manter:
- `observation_code`
- `observation_code_display`
- `category_code`
- `category_display`
- `value`
- `value_unit`
- `value_code`

### 18. observation_vital_signs_ed_component
Atenção: se a tabela estiver nomeada como `observation_vital_ed_component`, aplique nela.  
Se estiver nomeada como `observation_vital_signs_ed_component`, alinhe com o nome real do projeto e documente.

Não ingerir:
- `observation_vital_signs_system`
- `value_system`

Observação: se a coluna real for `component_code_system`, remover essa coluna.  
A intenção é não persistir o system do código do componente.

Manter:
- `component_code`
- `component_code_display`
- `value`
- `value_unit`
- `value_code`

### 19. procedure
Não ingerir:
- `procedure_code_system`

Manter:
- `procedure_code`
- `procedure_code_display`

### 20. procedure_ed
Não ingerir:
- `procedure_code_system`

Manter:
- `procedure_code`
- `procedure_code_display`

### 21. procedure_icu
Não ingerir:
- `procedure_code_system`
- `category_system`

Manter:
- `procedure_code`
- `procedure_code_display`
- `category_code`

### 22. specimen
Não ingerir:
- `specimen_type_system`

Manter:
- `specimen_type_code`
- `specimen_type_display`

## Implementação obrigatória

### Schema/models
Atualizar a criação das tabelas para remover as colunas acima.

### Transformers
Atualizar os transformers para não retornar as chaves removidas.

### Loaders
Atualizar os loaders para não tentar inserir as colunas removidas.

### Testes
Atualizar testes existentes para garantir que as colunas removidas não aparecem no payload transformado.

Adicionar assertions como:

```python
assert "condition_code_system" not in transformed
assert "category_system" not in transformed
```

Adaptar para cada tabela correspondente.

### README

Atualizar a documentação da modelagem simplificada, explicando que os campos `system` foram removidos da maior parte das tabelas para reduzir largura, ruído e redundância.

### CHANGELOG

Registrar:

* remoção de colunas `system` e equivalentes em múltiplas tabelas
* ajuste de schema
* ajuste de transformers
* ajuste de loaders
* ajuste de testes
* atualização da documentação

### TABLE_RELATIONSHIPS.md

Atualizar os diagramas ASCII quando eles mostrarem alguma das colunas removidas.

Não é necessário alterar relações/FKs, a menos que alguma coluna removida apareça em algum diagrama.

## Qualidade

Manter:

* type hints completos
* docstrings em português
* funções pequenas e coesas
* tratamento explícito de exceções
* configurações em YAML quando aplicável
* credenciais apenas no `.env`
* compatibilidade com `uv`
* testes com `pytest`

## Execução esperada

Após a refatoração:

```bash
python -m src.main
pytest
```

A ingestão deve resetar toda a estrutura, recriar as tabelas sem as colunas removidas e carregar os dados normalmente.
