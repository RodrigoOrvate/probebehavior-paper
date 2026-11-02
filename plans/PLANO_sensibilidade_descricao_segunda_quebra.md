# Plano: sensibilidade da medida, descrição na PT1 e a segunda quebra na PT2

Escrito em 01/11/2026, antes de calcular qualquer uma das análises abaixo. Medidas pelo probebehavior (commit local
f640118, com a opção `partial_window`). Exploratório, salvo o critério declarado na parte A.

## Parte A: a medida depois da chegada detecta amnésia melhor que as clássicas?

**Contrastes na PT2** (classificação da tese):

| Tipo | Contraste | Levas |
|---|---|---|
| Amnésico | ZIP × controles | E9L3, E9L5 (VEH); E3L1, E3L2 (VEH + scZIP); E5L3, E5L4, E8L1 (VEH) |
| Amnésico | ASO × MSO | E8L3 |
| Amnésico | PEP × VEH | E5L2, E5L3, E8L4 |
| Sem amnésia | ICAP × VEH | E5L2 |
| Sem amnésia | LAC+ZIP × LAC | E8L1 |
| Sem amnésia | DYN+ZIP × DYN | E5L3, E5L4 |
| Sem amnésia | ZIP × VEH, PT2 em 3 h | E7L2 |
| Sem amnésia | ZIP 6 h depois × VEH | E9L1 (rastreado pelo vídeo) |

Base: pares válidos e critério próprio (como no teste anterior); nenhum outro rato sai.

**Medidas na PT2**, todas orientadas para que valor maior de g signifique pior memória:

- Clássicas: tempo no quadrante-alvo (%), proximidade de Gallagher no teste inteiro (cm), cruzamentos da plataforma,
  latência até o local (s; 60 s para quem não chega).
- Novas: persistência e reentradas depois da primeira chegada, com `partial_window` (quem chega tarde usa o tempo que
  resta, no mínimo 1 s); 0 para quem não chega ou chega com menos de 1 s.

**Efeito:** g = coeficiente do tratamento em `medida_PT2 ~ tratamento + leva`, dividido pelo desvio-padrão residual.
Secundário: o mesmo com a medida da PT1 como covariável. Para cada g, o n por grupo para 80% de poder (bilateral,
α = 0,05).

**Comparação principal (critério):** no contraste ZIP × controles, a diferença g(persistência) − g(quadrante), com IC
95% por bootstrap (5.000 reamostragens de ratos dentro de leva e grupo). A persistência é dita mais sensível se o IC
ficar todo acima de zero. Também relatadas: g(persistência) − g(Gallagher), que é a medida mais sensível em Maei et al.
(2009), e as mesmas diferenças em ASO × MSO e PEP × VEH, só descritas. Nos contrastes sem amnésia, uma boa medida deve
dar g perto de zero: relatado, sem teste.

## Parte B: descrição na PT1 de todas as levas

PT1 de todos os ratos (todos os grupos, porque a droga vem depois da PT1) de E3L1, E3L2, E5L2, E5L3, E5L4, E7L2, E8L1,
E8L2, E8L3, E8L4, E9L1, E9L3 e E9L5. Ficam fora: E6L1 (droga antes da PT1), E10 (L1 com droga antes; L3 e L4 com RO antes;
L2 sem ficha) e E9L2, L6 e L7. Sem `partial_window` (janelas completas, como no piloto).

1. Quantos chegam ao local e quando, por leva.
2. Curvas alinhadas na chegada (mediana e P25–P75).
3. A reação típica: duração da primeira permanência e tempo até a borda.
4. Comparação com o acaso: persistência em volta do local verdadeiro × a mesma medida em volta dos três locais girados,
   nos mesmos 15 s (pareado por rato, Wilcoxon).
5. Estrutura: correlações de Spearman entre as medidas pós-chegada e componentes principais (medidas padronizadas).
6. Relação com a força da memória: Spearman com a latência até o local e a eficiência do caminho.
7. Diferenças entre levas: proporção da variância da persistência explicada pela leva (modelo misto com intercepto
   aleatório por leva).

## Parte C: a segunda quebra na PT2

Ratos que chegam ao local na PT1 (os que aprenderam). PT2 com janelas completas.

1. Controles (VEH, scZIP e MSO), PT1 × PT2 do mesmo rato: proporção que chega (McNemar) e, nos que chegam nas duas,
   latência, persistência, reentradas, primeira permanência e tempo até a borda (Wilcoxon pareado). Pergunta: depois de já
   ter encontrado o local vazio, o rato insiste menos (atualização)?
2. ZIP × controles: nos que chegam nas duas sessões, `persistência_PT2 ~ ZIP + persistência_PT1 + leva`. Exploratório,
   sem previsão de direção.
3. Intervalos diferentes entre PT1 e PT2 (3 h na E7L2, 24 h na maioria, 7 dias na E9L3): relatar a parte C1 por intervalo.

## Cuidados declarados

O E9 e o experimento 3 já foram usados no teste pré-registrado da quebra; a PT2 dos ZIP de E5L3, E5L4 e E8L1 foi vista
nele. A especificidade anterior já calculou interações nesses contrastes, com outras medidas. As exclusões dos
experimentos 5, 7 e 8 da tese não foram aplicadas na base.
