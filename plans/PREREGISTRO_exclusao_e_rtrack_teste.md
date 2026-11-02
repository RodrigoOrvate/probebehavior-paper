# Pré-registro: critério de exclusão próprio e estratégias do RTrack nos testes (27/10/2026)

Escrito antes de calcular os critérios e de rodar o RTrack no experimento 3. O hash deste arquivo fica em
`PREREGISTRO_exclusao_e_rtrack_teste.sha256`. Já conhecidos antes: os resultados com todos os ratos e com as exclusões da
tese; no E9, o RTrack nos primeiros 20 s (71% espaciais na PT1, sem diferença VEH × ZIP) e cortado no primeiro cruzamento
(49% espaciais na PT1). Ao transcrever a ficha da E3L1 para o critério C3, as latências do treino já foram vistas.

## Parte 1: critério de exclusão próprio

Motivo: não há registro do critério das exclusões da tese, e os dois arquivos do GraphPad do experimento 3 excluem ratos
diferentes. O critério usa só informação anterior à droga ou de procedimento, igual para todos os grupos. Nunca usa a
memória na PT1, a PT2 ou a mudança entre elas.

Um rato é excluído se cumprir qualquer um:

- **C1, procedimento:** a ficha anota problema de cânula, de infusão ou de saúde do animal. Descrições de comportamento
  ("desorientado", "nada muito") não contam. Ratos riscados (sem PT2) já estão fora dos dados.
- **C2, não nada:** velocidade média na PT1 abaixo da metade da mediana da PT1 da sua leva (TopScan).
- **C3, não aprendeu:** latência média dos quatro trials do último dia de treino de 50 s ou mais (ficha).

Conjuntos: E9 (levas 3 e 5) e experimento 3 (levas 1 e 2). Se faltar a ficha do treino de uma leva, C3 fica pendente
nela e isso é dito.

Testes, iguais aos já usados: interação ZIP × quadrante da PT1 no experimento 3 (permutação unilateral dentro da leva,
10.000 vezes, controles VEH + scZIP), no E9 e nos dois juntos (paramétrico, como em `e9_e3_conjunto.py`). Relatado ao
lado de todos os ratos e das exclusões da tese. Não há hipótese nova: é uma terceira versão dos mesmos testes.

## Parte 2: estratégias do RTrack nos testes

O RTrack tem um único modelo para o labirinto aquático (`mwm_rf_v7`, treinado com camundongos em trials com plataforma).
Cada teste é cortado para ficar parecido com um trial: nos primeiros 20 s (principal, o corte que funcionou na PT1 do E9)
e até o primeiro cruzamento da plataforma (secundário). E9 e experimento 3 juntos, todos os ratos.

Medidas: estratégia chamada (espacial = busca direcionada, trajeto corrigido, trajeto direto ou perseverança, códigos 6 a 9)
e o escore espacial contínuo (soma das confianças do classificador nas estratégias 6 a 9, de 0 a 1).

- **R1 (principal):** no escore espacial com o corte de 20 s, a interação ZIP × escore da PT1 é negativa (mesmo modelo do
  achado principal: escore PT2 ~ ZIP × escore PT1 + leva; permutação unilateral do rótulo ZIP dentro da leva, 10.000 vezes;
  controles VEH + scZIP). Apoiada se p < 0,05.
- **R2:** entre os ratos com estratégia espacial na PT1, a proporção que continua espacial na PT2 é menor no ZIP
  (regressão logística com leva; teste unilateral).
- **R3 (descritivo):** proporção de estratégias espaciais por fase e grupo, nos dois cortes.

Secundárias: R1 com o corte no primeiro cruzamento; R1 com o critério de exclusão da Parte 1.
