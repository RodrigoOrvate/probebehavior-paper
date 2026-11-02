# Piloto: o que o rato faz depois de chegar ao local vazio na PT1

Escrito em 01/11/2026, antes de calcular qualquer medida abaixo. Exploratório: serve para decidir se a ideia vale um
pré-registro, não para testar hipótese.

## Pergunta

Na PT1, a primeira chegada ao local da plataforma é uma quebra de expectativa (o rato espera a plataforma e ela não está
lá). O piloto pergunta: (1) quantos ratos chegam ao local; (2) o que eles fazem nos 30 s seguintes; (3) se os ratos variam
nessa reação; (4) se essa variação é só força da memória, ou seja, se ela se explica pelo nado até o local.

## Dados

Só a PT1 dos Exp. 5 (L2–L4), 7 (L2) e 8 (L1–L4): a droga veio depois da PT1, então a PT1 é comportamento sem droga.
Trajetórias do TopScan já processadas (RTRACK_ESP). Ficam de fora: E9 e Exp. 3 (reservados para o teste com
pré-registro), E10 (L1 com droga antes; L2–L4 sem ficha), E6L1 (droga 2 h antes da PT1) e E9L2, L6 e L7. A PT2 e os
grupos de droga não são usados.

## Definições

- t0: primeiro instante dentro do círculo da plataforma (raio 6 cm). Coordenadas em cm, piscina com raio de 100 cm.
- Antes de t0 (força da memória): latência até t0 e eficiência do caminho (distância em linha reta da largada ao local,
  dividida pelo trajeto até t0).
- Depois de t0, nos 15 s seguintes: fração do tempo a até 20 cm do local (persistência); reentradas na plataforma;
  duração da primeira permanência na zona de 20 cm; distância média ao local; velocidade; giro (média do valor absoluto da
  mudança de direção por segundo).
- Depois de t0, nos 30 s seguintes: tempo até a primeira entrada na borda (20% externos do raio) e visitas às três
  posições equivalentes nos outros quadrantes (zona de 20 cm em volta do local girado de 90°, 180° e 270°).
- Curvas alinhadas em t0, de 5 s antes a 30 s depois, em janelas de 1 s: distância ao local, distância à parede e
  velocidade. Só ratos com t0 até 30 s entram nas curvas, para todos terem os 30 s seguintes.

## Análises

1. Quantos chegam ao local e quando.
2. Curvas médias alinhadas em t0, com a faixa entre ratos (percentis 25 e 75).
3. Variação entre ratos de cada medida pós-t0 (mediana e intervalo interquartil).
4. Correlação de Spearman das medidas pós-t0 com as medidas pré-t0 (latência e eficiência). Se a persistência for quase
   toda explicada pela latência (|ρ| > 0,7), a ideia perde força: seria só força da memória.
5. Perfis de reação: agrupamento (k-médias, k de 2 a 4 pelo índice de silhueta) das curvas de distância ao local nos 30 s
   depois de t0, só como descrição.

## O que conta como sinal para seguir

Variação ampla entre ratos nas medidas pós-t0 e correlação moderada ou fraca com as medidas pré-t0. Se todos os ratos
fizerem a mesma coisa, ou se a reação for só a latência com outro nome, a ideia para aqui.
