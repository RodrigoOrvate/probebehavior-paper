# Pré-registro, versão 2: a reação ao local vazio na PT1 prevê o efeito do ZIP?

Escrito em 01/11/2026, antes de calcular qualquer medida alinhada na chegada (pacote probebehavior) nos ratos tratados
com ZIP ou nos seus controles das levas abaixo, e antes de olhar a PT2 dos ratos ZIP de qualquer uma delas. Substitui a
versão 1 (`PREREGISTRO_quebra_expectativa.md`, hash 25599c57…, commit a035154), que não chegou a ser executada. Nada
aqui pode ser ajustado depois do cálculo; desvios vão para um arquivo à parte.

## O que mudou da versão 1, e por quê (decisões do autor, antes de qualquer cálculo)

1. Teste bilateral: a teoria admite as duas direções (mais erro de predição, mais perda; ou expectativa mais firme, menos
   perda).
2. Mais ratos, pelo desenho: entram todas as levas com ZIP logo após a PT1, PT2 em 24 h e VEH como controle, além do E9
   e do experimento 3: E5L3, E5L4 e E8L1. O critério é o desenho, não o resultado.
3. A Q1 continua principal, com a ressalva sobre a sobreposição com o quadrante da PT1 (abaixo).
4. O artigo é sobre o comportamento nos testes; o ZIP é uma aplicação. O registro trata só da parte com o ZIP.

## O que já foi visto

- E9 e experimento 3: medidas do teste inteiro e a interação ZIP × quadrante da PT1 (C1 confirmada, p = 0,028; com os
  pares válidos, E9 + experimento 3 dão −0,75, p = 0,0008).
- Já testada e não replicada: C4 (`PREREGISTRO_confirmacao_exp3.md`), o tempo a até 20 cm da plataforma na PT1 inteira
  como moderador (p = 0,10 no experimento 3). A persistência é parente dela.
- E5L3, E5L4 e E8L1: no piloto foram vistas a PT1 de todos os ratos (medidas alinhadas, sem grupo nem PT2) e a PT1 e a
  PT2 dos VEH (estabilidade). A PT2 dos ZIP e a relação com o grupo nunca foram vistas. Na análise de especificidade
  anterior, a interação ZIP × quadrante da PT1 nessas levas já foi calculada (réplica do ZIP, −0,51, p = 0,155).

## Hipótese

A primeira chegada ao local vazio na PT1 é um erro de predição. A persistência no local depois dela, rato a rato, modera
o efeito do ZIP aplicado logo após a PT1 sobre a memória na PT2, além da força da memória medida pelo quadrante da PT1. A
direção não é fixada.

## Dados

| Leva | Desenho | Tratados × controles |
|---|---|---|
| E9L3 | PT1 no dia 8; ZIP ou VEH logo após; PT2 7 dias depois | ZIP × VEH |
| E9L5 | PT1 7 dias após o treino; ZIP ou VEH logo após; PT2 24 h depois | ZIP × VEH |
| E3L1, E3L2 | PT1 no dia 8; ZIP, scZIP ou VEH logo após; PT2 24 h depois | ZIP × (VEH + scZIP) |
| E5L3, E5L4 | PT1 no dia 8; droga logo após; PT2 24 h depois | ZIP × VEH (DYN, DYN+ZIP e PEP ficam fora) |
| E8L1 | PT1 no dia 8; droga logo após; PT2 24 h depois | ZIP × VEH (LAC e LAC+ZIP ficam fora) |

- Trajetórias: `RTRACK/` (E9), `RTRACK_E3/` (experimento 3), `RTRACK_ESP/` (E5 e E8). Tempo no quadrante-alvo de cada
  `parametros.csv`.
- Base: pares válidos (saem E9L3 ratos 1, 2, 16, 18, 23 e 24, PT2 sem identidade recuperável) e critério próprio de
  exclusão (`PREREGISTRO_exclusao_e_rtrack_teste.md`): saem E3L1 rato 11 e E9L5 rato 21; nas levas E5L3, E5L4 e E8L1 o
  critério não tirou ninguém (`revisao_fichas/exclusoes_criterio_proprio_levas_zip.csv`, calculado sem medidas de teste).

## Medidas (probebehavior, commit 17cf462, configuração padrão)

- Persistência: fração dos 15 s depois da primeira entrada na plataforma (raio 6 cm) passada a até 20 cm do centro dela.
- Reentradas: entradas na plataforma nesses 15 s, depois da primeira.
- Latência até o local: tempo da primeira entrada.
- Entram os ratos que chegam ao local na PT1 com pelo menos 15 s de teste depois da chegada (latência ≤ 45 s). Quem não
  chega não viveu a quebra de expectativa; esses ratos são contados por grupo e descritos à parte.
- Desfecho: tempo no quadrante-alvo na PT2 (%).

## Hipótese principal (Q1)

- Modelo: `quad_PT2 ~ ZIP × persistência + ZIP × quad_PT1 + leva`, ZIP = 1, controles = 0.
- Teste: coeficiente ZIP × persistência diferente de zero, bilateral, α = 0,05, p de permutação (rótulo ZIP embaralhado
  dentro da leva, 10.000 vezes; estatística t do termo). Relatados também a estimativa por 0,1 de persistência e o IC 95%.
- Ressalva, a declarar no artigo: o tempo no quadrante da PT1 inclui o tempo depois da chegada, então persistência e
  quad_PT1 se sobrepõem. Controlar pelo quadrante pode subestimar o papel da persistência; a Q4 mostra o modelo sem esse
  controle.

## Secundárias (bilaterais, Holm entre as três)

- Q2: o modelo de Q1 com as reentradas no lugar da persistência.
- Q3: o modelo de Q1 com o termo ZIP × latência até o local acrescentado.
- Q4: o modelo de Q1 sem o termo ZIP × quad_PT1.

## Descritivo e sensibilidade (sem mudar a conclusão principal)

- Repetir o descritivo do piloto nos ratos destas levas: quantos chegam, variação da persistência, correlação com a
  latência até o local e com o quadrante da PT1.
- Ratos que não chegam ao local: efeito do ZIP na PT2 (ANCOVA com quad_PT1), só descrito.
- Sensibilidade: só E9 + experimento 3 (o conjunto da versão 1); todos os registros (com os pares trocados); exclusões
  da tese no E9 e no experimento 3 e as marcas "EXCLUIDO" da planilha na E5L3; só VEH como controle no experimento 3;
  E7L2 (PT2 em 3 h) acrescentada; cada experimento separado, com IC.

## Poder

Com cerca de 95 ratos ZIP e controles nestas levas e cerca de 70% chegando ao local com 15 s pela frente, devem entrar
uns 65 ratos, um terço ZIP. O poder continua limitado para uma interação; a estimativa com IC é relatada junto do p, e um
resultado nulo não será lido como ausência de efeito.

## Critério

Todos os resultados são relatados, inclusive os nulos.
