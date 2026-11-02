# Pré-registro: a reação ao local vazio na PT1 prevê o efeito do ZIP?

Escrito em 01/11/2026, antes de calcular qualquer medida alinhada na chegada (pacote probebehavior) no E9 ou no
experimento 3. Nada aqui pode ser ajustado depois de calcular essas medidas.

## O que já se sabe e o que já foi visto

- Já analisados no E9 e no experimento 3: medidas do teste inteiro (tempo no quadrante, Gallagher, tempo perto da
  plataforma, cruzamentos, primeiros 20 s). A interação ZIP × quadrante da PT1 foi confirmada no experimento 3
  (C1, p = 0,028; `PREREGISTRO_confirmacao_exp3.md`) e, com os pares válidos, dá −0,75 (p = 0,0008) com E9 e
  experimento 3 juntos.
- Já testada e não replicada: C4 do mesmo registro, o tempo a até 20 cm da plataforma na PT1 inteira como moderador
  (p = 0,10 no experimento 3). A medida deste registro é diferente (alinhada na primeira chegada e restrita aos 15 s
  seguintes), mas é parente dela, e isso precisa ser dito no artigo.
- Nunca calculadas no E9 nem no experimento 3: as medidas alinhadas na primeira chegada ao local.
- Piloto nos Exp. 5, 7 e 8 (`RESULTADOS_piloto_quebra_expectativa.md`): a persistência varia entre ratos, se relaciona
  pouco com a latência até o local (ρ = −0,26) e se repete do PT1 para o PT2 nos controles (ρ = 0,42).

## Hipótese

Na PT1 sem plataforma, a primeira chegada ao local é um erro de predição. Ratos que insistem mais no local depois de não
encontrar a plataforma viveram um erro de predição mais marcado, a memória se desestabiliza mais, e o ZIP depois da PT1
causa uma perda maior na PT2. A previsão é que a persistência modere o efeito do ZIP além da força da memória medida pelo
quadrante da PT1.

## Dados

- E9 (E9L3 e E9L5; VEH e ZIP) e experimento 3 (E3L1 e E3L2; VEH, scZIP e ZIP), trajetórias da PT1 e da PT2 já
  processadas (`RTRACK/` e `RTRACK_E3/`).
- Base: pares válidos. Saem os 6 ratos da E9L3 cuja PT2 não tem identidade recuperável (1, 2, 16, 18, 23 e 24), pela
  mesma regra de integridade das análises anteriores.
- Controles: VEH no E9; VEH e scZIP juntos no experimento 3 (como na C1).

## Medidas (probebehavior 0.1.0, commit 17cf462, configuração padrão)

- Persistência: fração dos 15 s depois da primeira entrada na plataforma (raio 6 cm) passada a até 20 cm do centro dela.
- Reentradas: entradas na plataforma nesses 15 s, depois da primeira.
- Latência até o local: tempo da primeira entrada.
- Entram na análise principal os ratos que chegam ao local na PT1 com pelo menos 15 s de teste depois da chegada
  (latência ≤ 45 s). Os outros são contados por grupo e descritos à parte.
- Desfecho: tempo no quadrante-alvo na PT2 (%), o mesmo desfecho principal das análises anteriores.

## Hipótese principal (Q1)

- Modelo: `quad_PT2 ~ ZIP × persistência + ZIP × quad_PT1 + leva`, com ZIP = 1 e controles = 0.
- Teste: coeficiente ZIP × persistência negativo, unilateral, α = 0,05, p de permutação (rótulo ZIP embaralhado dentro da
  leva, 10.000 vezes). Também são relatados o p bilateral, a estimativa (por 0,1 de persistência) e o IC 95%.
- Apoiada se p < 0,05 na direção prevista.

## Secundárias (Holm entre as três)

- Q2: o mesmo modelo com as reentradas no lugar da persistência (coeficiente negativo, unilateral).
- Q3: o modelo de Q1 com o termo ZIP × latência até o local acrescentado; o coeficiente ZIP × persistência continua
  negativo (unilateral).
- Q4: o modelo de Q1 sem o termo ZIP × quad_PT1; o coeficiente ZIP × persistência é negativo (unilateral). Serve para
  ver se a persistência modera por si só, mesmo que divida a variância com o quadrante.

## Descritivo (sem teste)

- Repetir no E9 e no experimento 3 o que o piloto mostrou: quantos chegam, variação da persistência e correlação com a
  latência até o local e com o quadrante da PT1.
- Entre os ratos que não chegam ao local na PT1, o efeito do ZIP na PT2 (ANCOVA com quad_PT1), só descrito.

## Sensibilidade (relatadas, sem mudar a conclusão principal)

Todos os registros (com os pares trocados); as exclusões da tese; o critério próprio; só VEH como controle no
experimento 3; E9 e experimento 3 separados, com IC.

## Poder

Com cerca de 69 ratos nos pares válidos e cerca de 73% chegando ao local, devem entrar uns 45 a 50 ratos, um terço deles
ZIP. O poder é baixo para uma interação. Por isso a estimativa com IC é relatada junto do p, e um resultado nulo não será
lido como ausência de efeito.

## Critério

Todos os resultados são relatados, inclusive os nulos. Mudanças depois do cálculo vão para um arquivo de desvios, com
data, e não alteram este texto.
