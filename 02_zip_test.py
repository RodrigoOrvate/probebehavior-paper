"""Teste pré-registrado (plans/PREREGISTRO_quebra_expectativa_v2.md, hash f3d5a349…, commit 24ab89b): a persistência no
local vazio depois da primeira chegada, na PT1, modera o efeito do ZIP sobre o quadrante na PT2? Saída em
results/zip_test/."""
import os

import numpy as np
import pandas as pd
import probebehavior as pb
import statsmodels.formula.api as smf
from scipy import stats

from dados import PROPRIO, TESE, TROCADOS, classicas, experimento, saida

SAIDA = saida('results/zip_test')
rng = np.random.default_rng(20261101)
LEVAS = ['E9L3', 'E9L5', 'E3L1', 'E3L2', 'E5L3', 'E5L4', 'E8L1', 'E7L2']
CONTROLES = {'VEH', 'SCZIP'}


e = experimento()
e = e[e.Experimento.isin(LEVAS)]
q = e.set_index('_TrackID')[['_TargetID', 'Fase', 'Grupo']].join(classicas(e))
quad = q.pivot_table(index='_TargetID', columns='Fase', values='quadrante')
grupo = q.drop_duplicates('_TargetID').set_index('_TargetID').Grupo
m, _ = pb.measure_experiment(e[e.Fase == 'PT1'])
m = m.set_index('_TargetID')[['Experimento', 'reached', 'arrival_latency_s', 'persistence', 'reentries']]
d = m.join(quad, how='inner').join(grupo).reset_index().rename(columns={'index': '_TargetID', 'Experimento': 'leva', 'PT1': 'quad_PT1',
                                                    'PT2': 'quad_PT2', 'persistence': 'persist'})
d = d[d.Grupo.isin(CONTROLES | {'ZIP'})].dropna(subset=['quad_PT1', 'quad_PT2'])
d['ZIP'] = (d.Grupo == 'ZIP').astype(int)
d['exp'] = d.leva.str.extract(r'^(E\d+)')[0]
d.to_csv(os.path.join(SAIDA, 'dados_por_rato.csv'), index=False)

PRINCIPAIS = ['E9L3', 'E9L5', 'E3L1', 'E3L2', 'E5L3', 'E5L4', 'E8L1']
base = d[d.leva.isin(PRINCIPAIS) & ~d._TargetID.isin(TROCADOS | PROPRIO)]
ok = base.dropna(subset=['persist'])

MODELOS = {'Q1': ('quad_PT2 ~ ZIP * persist + ZIP * quad_PT1 + C(leva)', 'ZIP:persist'),
           'Q2': ('quad_PT2 ~ ZIP * reentries + ZIP * quad_PT1 + C(leva)', 'ZIP:reentries'),
           'Q3': ('quad_PT2 ~ ZIP * persist + ZIP * quad_PT1 + ZIP * arrival_latency_s + C(leva)', 'ZIP:persist'),
           'Q4': ('quad_PT2 ~ ZIP * persist + C(leva)', 'ZIP:persist')}


def ajusta(f, termo, dd):
    m = smf.ols(f, dd).fit()
    lo, hi = m.conf_int().loc[termo]
    return m, m.params[termo], lo, hi, m.tvalues[termo], m.pvalues[termo]


def p_perm(f, termo, dd, t_obs, n=10000):
    idx = [np.flatnonzero(dd.leva.values == l) for l in dd.leva.unique()]
    z = dd.ZIP.values
    ts = np.empty(n)
    for k in range(n):
        zz = z.copy()
        for ix in idx:
            zz[ix] = rng.permutation(z[ix])
        ts[k] = smf.ols(f, dd.assign(ZIP=zz)).fit().tvalues[termo]
    return (np.sum(np.abs(ts) >= abs(t_obs)) + 1) / (n + 1)


print(f'base: {len(base)} ratos (ZIP {base.ZIP.sum()}); chegaram com 15 s pela frente: {len(ok)} (ZIP {ok.ZIP.sum()})')
print(base.assign(entra=base.persist.notna()).groupby(['leva', 'Grupo']).entra.agg(['size', 'sum']).T.to_string())
res = []
for q, (f, termo) in MODELOS.items():
    m, est, lo, hi, t, p = ajusta(f, termo, ok)
    pp = p_perm(f, termo, ok, t)
    escala = 0.1 if 'persist' in termo else 1
    res.append(dict(analise=q, termo=termo, estimativa=est * escala, ic_inf=lo * escala, ic_sup=hi * escala,
                    p_param=p, p_perm=pp, n=int(m.nobs), unidade='pp por 0,1 de persistência' if escala == 0.1 else 'pp por reentrada'))
r = pd.DataFrame(res)
ordem = r[r.analise != 'Q1'].sort_values('p_perm')
acum, holm = 0, {}
for i, (k, p) in enumerate(zip(ordem.analise, ordem.p_perm)):
    acum = max(acum, min(1, p * (3 - i)))
    holm[k] = acum
r['p_holm'] = r.analise.map(holm)
pd.set_option('display.width', 220)
print(r.round(4).to_string(index=False))

# inclinação da PT2 sobre a persistência em cada grupo (para ler o sinal), com quad_PT1 no modelo
for g, nome in [(0, 'controles'), (1, 'ZIP')]:
    m = smf.ols('quad_PT2 ~ persist + quad_PT1 + C(leva)', ok[ok.ZIP == g]).fit()
    lo, hi = m.conf_int().loc['persist'] * 0.1
    print(f'  {nome}: {m.params["persist"] * 0.1:+.2f} pp por 0,1 de persistência [{lo:+.2f}; {hi:+.2f}], n = {int(m.nobs)}')

print('\ndescritivo:')
print(f'  persistência: mediana {ok.persist.median():.2f} [{ok.persist.quantile(.25):.2f}; {ok.persist.quantile(.75):.2f}]')
for k in ('arrival_latency_s', 'quad_PT1'):
    rho = stats.spearmanr(ok.persist, ok[k])
    print(f'  persistência × {k}: ρ = {rho[0]:+.2f} (p = {rho[1]:.2g})')
nao = base[base.persist.isna()]
m = smf.ols('quad_PT2 ~ ZIP + quad_PT1 + C(leva)', nao).fit()
print(f'  ratos sem a quebra (não chegaram ou chegaram depois de 45 s): {len(nao)} (ZIP {nao.ZIP.sum()}); '
      f'ZIP na PT2 ajustado pela PT1: {m.params["ZIP"]:+.1f} pp [{m.conf_int().loc["ZIP"][0]:+.1f}; {m.conf_int().loc["ZIP"][1]:+.1f}], p = {m.pvalues["ZIP"]:.2f}')

print('\nsensibilidade (Q1, p paramétrico bilateral):')
f, termo = MODELOS['Q1']
SENS = {'só E9 + experimento 3': base[base.exp.isin(['E9', 'E3'])],
        'todos os registros': d[d.leva.isin(PRINCIPAIS)],
        'exclusões da tese': d[d.leva.isin(PRINCIPAIS) & ~d._TargetID.isin(TROCADOS | TESE)],
        'só VEH como controle no experimento 3': base[base.Grupo != 'SCZIP'],
        'com a E7L2 (PT2 em 3 h)': d[d.leva.isin(PRINCIPAIS + ['E7L2']) & ~d._TargetID.isin(TROCADOS | PROPRIO)]}
for e_ in ['E9', 'E3', 'E5', 'E8']:
    SENS[f'só {e_}'] = base[base.exp == e_]
sens = []
for nome, dd in SENS.items():
    dd = dd.dropna(subset=['persist'])
    try:
        _, est, lo, hi, _, p = ajusta(f, termo, dd)
        sens.append(dict(versao=nome, estimativa=est * 0.1, ic_inf=lo * 0.1, ic_sup=hi * 0.1, p=p, n=len(dd), zip=int(dd.ZIP.sum())))
    except Exception as erro:
        sens.append(dict(versao=nome, n=len(dd), zip=int(dd.ZIP.sum()), erro=str(erro)[:60]))
s = pd.DataFrame(sens)
print(s.round(3).to_string(index=False))
r.to_csv(os.path.join(SAIDA, 'principais.csv'), index=False)
s.to_csv(os.path.join(SAIDA, 'sensibilidade.csv'), index=False)
print('→ results/zip_test/')
