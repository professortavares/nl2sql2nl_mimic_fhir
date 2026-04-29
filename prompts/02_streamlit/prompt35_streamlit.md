Atualize a seção "Hospitalization information" para incluir uma subseção de diagnósticos relacionados ao encounter atual.

Requisitos:
- Dentro do card de "Hospitalization information", adicione uma subseção chamada "Diagnoses".
- Recupere os diagnósticos usando o encounter_id do encounter selecionado/atual.
- A consulta deve seguir este padrão:

select c.condition_code, c.condition_code_display
from mimic_fhir_ingestion."condition" c
where c.encounter_id = '<encounter_id_atual>'

- Não fixe o encounter_id no código; use dinamicamente o id do encounter atual.
- Exiba os resultados em uma tabela simples ou lista dentro da subseção "Diagnoses".
- Mostre pelo menos:
  - condition_code
  - condition_code_display
- Caso não existam diagnósticos, exiba uma mensagem discreta como "No diagnoses found for this encounter."

Preserve a lógica existente e altere apenas o necessário para buscar e renderizar esses diagnósticos. Ao final, liste os arquivos alterados e resuma as mudanças.