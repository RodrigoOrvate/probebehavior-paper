# Plano: na segunda quebra, a insistência cai mais que a ida ao local?

Escrito em 01/11/2026, depois da parte C (`RESULTADOS_abc_quebra.md`) e antes de calcular qualquer coisa abaixo.
Medidas pelo probebehavior (commit local f640118). A parte C sugeriu a hipótese; este teste a examina com as regras
fixadas aqui. Por ter nascido dos mesmos dados, o resultado é exploratório e assim será relatado.

## Hipótese

Na PT2, depois de já ter encontrado o local vazio na PT1, o rato sabe onde é o local (a ida até ele se mantém) mas espera
menos achar a plataforma ali (a insistência depois da chegada cai). Previsão: a queda da insistência é maior que a queda
da ida ao local.

## Ratos

- Controles sem tratamento amnésico (VEH, scZIP, MSO) das levas da parte B, com PT2 24 h depois da PT1 (todas, menos
  E7L2 e E9L3).
- Fora: pares trocados, critério próprio e **sessões incompletas**: trajetória com menos de 58 s (de um teste de 60 s);
  se uma das duas sessões do rato for incompleta, o rato sai.
- Análise principal: ratos que chegam ao local na PT1 e na PT2 com 15 s pela frente nas duas.

## Medidas, na mesma escala

- Ida ao local: −log(latência até o local), maior = vai mais rápido.
- Insistência: persistência nos 15 s depois da chegada, maior = insiste mais.
- Cada uma padronizada pela média e pelo desvio-padrão da PT1 destes ratos.
- Mudança de cada uma: PT2 − PT1. Dissociação: D = mudança da insistência − mudança da ida ao local.

## Teste

D diferente de zero, Wilcoxon pareado bilateral, α = 0,05; relatar a mediana de D com IC 95% por bootstrap (5.000) e as
mudanças de cada medida separadas. Previsão: D < 0.

## Checagens (relatadas, não mudam o teste)

1. Regressão à média: repetir dividindo os ratos pela mediana da persistência na PT1. Se a queda da insistência aparecer só
   na metade alta, pode ser regressão à média; se aparecer nas duas metades, não.
2. Seleção pela chegada: repetir com todos os controles que chegam na PT1 com 15 s pela frente, com latência de 60 s e
   persistência 0 na PT2 para quem não chega (ou chega com menos de 15 s).
3. Reentradas no lugar da persistência.
4. Intervalos de 3 h (E7L2) e 7 dias (E9L3), só sessões completas: descritos, sem teste.
