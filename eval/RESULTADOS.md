# Resultados da avaliação

Gerado por `python -m eval.run_eval` em 2026-10-23. Configuração: consulta híbrida, limiar de distância 0.4, mínimo de 3 evidências, MMR λ=0,7, top 10.

## Resumo

- Perguntas do escopo que chegaram ao modelo com evidência suficiente: 13/13 (100%)
- Precisão@5 média (proxy lexical): 0.92
- Perguntas fora do escopo barradas antes do LLM (camada 1): 8/9 (89%). As demais chegam ao modelo, que deve responder SEM_EVIDENCIA (camada 2).

## Por pergunta

| Pergunta | Esperado | Resultado | Filtros | Evidências | Precisão@5 | Distância média top 5 |
|---|---|---|---|---|---|---|
| Quais são os principais problemas relatados pelos clientes em suas avaliações? | responder | evidência suficiente (segue para o LLM) | nota ≤ 2 | 10 | 1.00 | 0.393 |
| O que os clientes relatam sobre problemas relacionados à entrega? | responder | evidência suficiente (segue para o LLM) | nota ≤ 2 | 10 | 1.00 | 0.243 |
| Quais aspectos da experiência de compra são mais elogiados pelos clientes? | responder | evidência suficiente (segue para o LLM) | nota ≥ 4 | 10 | 0.80 | 0.181 |
| Quais padrões podem ser identificados nas avaliações de clientes insatisfeitos? | responder | evidência suficiente (segue para o LLM) | nota ≤ 2 | 10 | 1.00 | 0.290 |
| Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega? | responder | evidência suficiente (segue para o LLM) | nota ≤ 2 | 10 | 1.00 | 0.197 |
| Quais reclamações relacionadas à entrega aparecem com maior frequência? | responder | evidência suficiente (segue para o LLM) | nota ≤ 2 | 10 | 1.00 | 0.150 |
| Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos? | responder | evidência suficiente (segue para o LLM) | - | 10 | 1.00 | 0.151 |
| O que os clientes falam sobre o atendimento do vendedor? | responder | evidência suficiente (segue para o LLM) | - | 10 | 1.00 | 0.160 |
| Os clientes reclamam de receber produto diferente do anunciado? | responder | evidência suficiente (segue para o LLM) | nota ≤ 2 | 10 | 1.00 | 0.244 |
| Quais são os principais problemas relatados nas avaliações com nota baixa? | responder | evidência suficiente (segue para o LLM) | nota ≤ 2 | 10 | 0.80 | 0.362 |
| O que os clientes mais elogiam em beleza e saúde? | responder | evidência suficiente (segue para o LLM) | nota ≥ 4, categoria = beleza_saude | 10 | 1.00 | 0.279 |
| Quais temas aparecem nas avaliações relacionadas a experiências de entrega insatisfatórias? | responder | evidência suficiente (segue para o LLM) | nota ≤ 2, entrega atrasada ou não entregue | 10 | 0.80 | 0.291 |
| Quais as reclamações sobre cama, mesa e banho em 2018? | responder | evidência suficiente (segue para o LLM) | nota ≤ 2, categoria = cama_mesa_banho, ano da compra = 2018 | 10 | 0.60 | 0.525 |
| Qual a capital da França? | recusar | recusada: fora do escopo | - | 0 | - | - |
| Qual a previsão do tempo para amanhã em São Paulo? | recusar | recusada: fora do escopo | - | 0 | - | - |
| Quem ganhou a Copa do Mundo de 2002? | recusar | recusada: fora do escopo | - | 0 | - | - |
| Como funciona a fotossíntese? | recusar | recusada: fora do escopo | - | 0 | - | - |
| Escreva um poema sobre o mar | recusar | recusada: fora do escopo | - | 0 | - | - |
| Qual o preço do bitcoin hoje? | recusar | recusada: evidência fraca | - | 0 | - | - |
| Como trocar o óleo do carro? | recusar | recusada: evidência fraca | categoria = automotivo | 0 | - | - |
| Qual foi o lucro líquido da Olist em 2018? | recusar | evidência suficiente (segue para o LLM) | ano da compra = 2018 | 10 | - | 0.367 |
| O que os clientes acham do serviço de streaming de filmes da loja? | recusar | recusada: evidência fraca | - | 1 | - | 0.392 |

## Estratégia de consulta x limiar

Cada linha roda as 22 perguntas. "Escopo com evidência" deve ser alto; "fora barradas" também.

| Consulta | Limiar | Escopo com evidência | Precisão@5 | Fora do escopo barradas (camada 1) |
|---|---|---|---|---|
| original | 0.35 | 11/13 (85%) | 0.72 | 9/9 (100%) |
| original | 0.40 | 12/13 (92%) | 0.74 | 9/9 (100%) |
| original | 0.42 | 12/13 (92%) | 0.74 | 9/9 (100%) |
| original | 0.45 | 13/13 (100%) | 0.72 | 8/9 (89%) |
| original | 0.50 | 13/13 (100%) | 0.71 | 6/9 (67%) |
| semantic | 0.35 | 13/13 (100%) | 0.91 | 9/9 (100%) |
| semantic | 0.40 | 13/13 (100%) | 0.91 | 8/9 (89%) |
| semantic | 0.42 | 13/13 (100%) | 0.91 | 8/9 (89%) |
| semantic | 0.45 | 13/13 (100%) | 0.91 | 7/9 (78%) |
| semantic | 0.50 | 13/13 (100%) | 0.91 | 7/9 (78%) |
| hybrid | 0.35 | 13/13 (100%) | 0.94 | 9/9 (100%) |
| hybrid | 0.40 | 13/13 (100%) | 0.92 | 8/9 (89%) |
| hybrid | 0.42 | 13/13 (100%) | 0.92 | 7/9 (78%) |
| hybrid | 0.45 | 13/13 (100%) | 0.92 | 7/9 (78%) |
| hybrid | 0.50 | 13/13 (100%) | 0.92 | 7/9 (78%) |
