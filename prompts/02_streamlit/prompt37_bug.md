Você precisa corrigir um bug no processo de ingestão de dados.

Contexto:
Atualmente, algumas tabelas estão sendo ingeridas com FKs vazias porque o processo de ingestão está resolvendo as referências contra a tabela errada. Em tabelas específicas de ED ou ICU, os campos de referência devem apontar para as tabelas equivalentes também específicas de ED ou ICU, e não para as tabelas genéricas.

Objetivo:
Corrigir a lógica de ingestão para que as FKs sejam resolvidas usando a tabela de referência correta, conforme o mapeamento abaixo.

Mapeamentos que devem ser corrigidos:

1. Tabela: procedure_ed
   - Coluna: encounter_id
   - Hoje referencia incorretamente: encounter
   - Deve referenciar: encounter_ed

Tarefa:
1. Investigue onde a lógica de resolução de foreign keys é definida no processo de ingestão.
2. Identifique se existe algum mapeamento centralizado de dependências/referências entre tabelas.
3. Corrija o mapeamento para que as tabelas listadas acima usem as tabelas de referência corretas.
4. Evite criar regras hardcoded espalhadas pelo código. Se já existir um mecanismo centralizado de configuração/mapeamento, use esse mecanismo.
5. Garanta que a correção não altere o comportamento das tabelas que já usam corretamente as referências genéricas `encounter` e `procedure`.
6. Adicione ou atualize testes cobrindo os casos acima.

Comportamento esperado:
Após a correção, durante a ingestão:

- Tabelas com sufixo `_ed` devem resolver `encounter_id` usando `encounter_ed` quando explicitamente listado acima.
- Tabelas com sufixo `_ed` devem resolver `procedure_id` usando `procedure_ed` quando explicitamente listado acima.
- Tabelas com sufixo `_icu` devem resolver `encounter_id` usando `encounter_icu` quando explicitamente listado acima.
- As FKs não devem ficar vazias quando a entidade correspondente existir na tabela correta.
- A ingestão não deve tentar resolver essas FKs contra `encounter` ou `procedure` genéricos para os casos listados.

Critérios de aceite:
- `condition_ed.encounter_id` é resolvido a partir de `encounter_ed`.
- `medication_dispense_ed.encounter_id` é resolvido a partir de `encounter_ed`.
- `medication_statement_ed.encounter_id` é resolvido a partir de `encounter_ed`.
- `observation_ed.encounter_id` é resolvido a partir de `encounter_ed`.
- `observation_ed.procedure_id` é resolvido a partir de `procedure_ed`.
- `observation_vital_signs_ed.encounter_id` é resolvido a partir de `encounter_ed`.
- `observation_vital_signs_ed.procedure_id` é resolvido a partir de `procedure_ed`.
- `procedure_ed.encounter_id` é resolvido a partir de `encounter_ed`.
- `medication_administration_icu.encounter_id` é resolvido a partir de `encounter_icu`.
- Testes automatizados demonstram que a resolução aponta para as tabelas corretas.
- Nenhum teste existente deve quebrar.
- Não devem ser introduzidas mudanças de schema desnecessárias, a menos que o código atual dependa explicitamente disso.

Sugestão de implementação:
Procure por configurações ou funções relacionadas a:
- foreign key mapping
- reference mapping
- dependency mapping
- parent table resolution
- ingestion relationships
- entity/table mapping
- encounter_id resolution
- procedure_id resolution

Se existir uma estrutura parecida com:

{
  "table": {
    "column": "referenced_table"
  }
}

adicione ou corrija os mapeamentos nela.

Exemplo conceitual esperado:

{
  "condition_ed": {
    "encounter_id": "encounter_ed"
  },
  "medication_dispense_ed": {
    "encounter_id": "encounter_ed"
  },
  "medication_statement_ed": {
    "encounter_id": "encounter_ed"
  },
  "observation_ed": {
    "encounter_id": "encounter_ed",
    "procedure_id": "procedure_ed"
  },
  "observation_vital_signs_ed": {
    "encounter_id": "encounter_ed",
    "procedure_id": "procedure_ed"
  },
  "procedure_icu": {
    "encounter_id": "encounter_icu"
  },
  "medication_administration_icu": {
    "encounter_id": "encounter_icu"
  }
}

Importante:
Não assuma que todas as tabelas com sufixo `_ed` ou `_icu` devem automaticamente trocar suas referências. Aplique a correção apenas aos casos listados, a menos que encontre uma regra já existente no domínio do projeto que justifique uma generalização segura.

Depois de implementar:
- Rode os testes relevantes.
- Rode lint/typecheck se existirem scripts no projeto.
- Explique resumidamente quais arquivos foram alterados e por quê.