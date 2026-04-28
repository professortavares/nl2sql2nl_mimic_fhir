# Documentação da Interface Streamlit

A aplicação web permite explorar um paciente por vez em uma timeline clínica cronológica.

Nesta primeira entrega:

- a aba `Dados individuais` está funcional
- as abas `Dados populacionais` e `Chat` aparecem como placeholders
- o usuário deve informar um `patient_id` no campo de busca para carregar a timeline
- o topo da tela mostra a identificação do paciente e abaixo aparecem os `encounters` em ordem cronológica
- cada encounter é organizado em três blocos clínicos inspirados no MIMIC-IV:
  - `General Hospital`
  - `Emergency Department (ED)`
  - `Intensive Care Unit (ICU)`
- dentro de cada bloco, os eventos são apresentados com nomes clínicos amigáveis, não como nomes técnicos de tabela

As seções exibidas dentro de cada encounter incluem diagnósticos, procedimentos, medicações, laboratório, microbiologia, observações ED, sinais vitais ED, eventos charted, eventos de saída, eventos data/hora e specimens, quando houver dados.

## Execução

Execute a interface web com:

```bash
uv run streamlit run src/app/streamlit_app.py
```

## Regras de Exibição

- a tela continua organizada como paciente -> identificação -> timeline -> encounter -> blocos por contexto
- cada encounter aparece dentro de um `st.expander`
- dentro de cada encounter, a UI usa `st.tabs` com:
  - `General Hospital`
  - `Emergency Department (ED)`
  - `Intensive Care Unit (ICU)`
- se uma aba não tiver dados, pode exibir `Nenhum dado encontrado para este contexto.`
- a organização dentro de cada encounter deve ser orientada ao domínio clínico, não ao nome técnico das tabelas

## Estrutura Visual

### General Hospital

A aba `General Hospital` agrupa dados hospitalares gerais, incluindo:

- informações da hospitalização
- diagnósticos
- procedimentos gerais
- pedidos, dispensações e administrações de medicação
- exames laboratoriais
- microbiologia
- specimens

### Emergency Department (ED)

A aba `Emergency Department (ED)` agrupa dados da emergência, incluindo:

- informações da permanência no ED
- diagnósticos ED
- procedimentos ED
- observações da emergência
- sinais vitais ED
- dispensações de medicamentos
- declarações de medicação

### Intensive Care Unit (ICU)

A aba `Intensive Care Unit (ICU)` agrupa dados da UTI, incluindo:

- informações da permanência na ICU
- procedimentos ICU
- administrações de medicação ICU
- eventos charted
- eventos de saída
- eventos data/hora
