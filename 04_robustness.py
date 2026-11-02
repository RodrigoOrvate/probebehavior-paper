"""Robustez ao raio da zona e à janela (plans/PLANO_robustez_parametros.md, hash ef0f797e…, commit a38bf16)."""
import itertools
import os

import numpy as np
import pandas as pd
import probebehavior as pb
import statsmodels.formula.api as smf
from scipy import stats

from dados import PROPRIO, TROCADOS, experimento, saida

SAIDA = saida('results/abc')
LEVAS_B = ['E3L1', 'E3L2', 'E5L2', 'E5L3', 'E5L4', 'E7L2', 'E8L1', 'E8L2', 'E8L3', 'E8L4', 'E9L1', 'E9L3', 'E9L5']
LEVAS_ZIP = ['E9L3', 'E9L5', 'E3L1', 'E3L2', 'E5L3', 'E5L4', 'E8L1']
LEVAS_24H = ['E3L1', 'E3L2', 'E5L2', 'E5L3', 'E5L4', 'E8L1', 'E8L2', 'E8L3', 'E8L4', 'E9L1', 'E9L5']
GRADE = list(itertools.product((15.0, 20.0, 25.0), (10.0, 15.0, 20.0)))

prov = pd.read_csv(os.path.join(SAIDA, 'provas.csv'))[['_TrackID', '_TargetID', 'leva', 'Grupo', 'Fase', 'quadrante']]
arq = os.path.join(SAIDA, 'robustez_medidas.csv')
if os.path.exists(arq):
    m = pd.read_csv(arq)
else:
    linhas = []
    e = experimento()
    for rec in e[e._TrackID.isin(prov._TrackID)].to_dict('records'):
        ar = pb.read_rtrack_arena(rec['_Arena'])
        t, x, y = pb.read_track(rec['_TrackFile'])
        for z, w in GRADE:
            s = pb.Settings(zone_radius=z, short_window=w)
            cheio, _ = pb.measure(t, x, y, ar, s)
            parc, _ = pb.measure(t, x, y, ar, pb.Settings(zone_radius=z, short_window=w, partial_window=True))
            lin = dict(_TrackID=rec['_TrackID'], zona=z, janela=w, reached=cheio['reached'],
                       latencia=cheio.get('arrival_latency_s'), persist=cheio.get('persistence'), persist_pw=parc.get('persistence'))
            if cheio.get('persistence') is not None:
                t0 = cheio['arrival_latency_s']
                k = (t >= t0) & (t < t0 + w)
                lin['persist_girados'] = np.mean([(np.hypot(x[k] - gx, y[k] - gy) <= z).mean() for gx, gy in pb.rotated_goals(ar)])
            linhas.append(lin)
    m = pd.DataFrame(linhas)
    m.to_csv(arq, index=False)
m = m.merge(prov, on='_TrackID')
base = m[~m._TargetID.isin(TROCADOS | PROPRIO)]


def g_ols(y, trat, leva):
    X = np.column_stack([np.ones_like(y), trat] + [(leva == l).astype(float) for l in np.unique(leva)[1:]])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ b
    return b[1] / np.sqrt(r @ r / (len(y) - X.shape[1]))


res = []
for z, w in GRADE:
    g = m[(m.zona == z) & (m.janela == w)]
    gb = base[(base.zona == z) & (base.janela == w)]
    # 1 e 2: PT1 das levas da parte B
    p1 = g[g.leva.isin(LEVAS_B) & (g.Fase == 'PT1')].dropna(subset=['persist'])
    acaso = stats.wilcoxon(p1.persist, p1.persist_girados).pvalue
    rho_lat = stats.spearmanr(p1.persist, p1.latencia)[0]
    # 3: repetição nos controles
    wv = g[g.leva.isin(LEVAS_B) & g.Grupo.isin(['VEH', 'SCZIP', 'MSO'])].pivot_table(index='_TargetID', columns='Fase', values='persist')
    wv = wv.dropna()
    rho_rep = stats.spearmanr(wv.PT1, wv.PT2)
    # 4: sensibilidade ZIP × controles na PT2
    c = gb[gb.leva.isin(LEVAS_ZIP) & gb.Grupo.isin(['ZIP', 'VEH', 'SCZIP']) & (gb.Fase == 'PT2')].copy()
    c['trat'] = (c.Grupo == 'ZIP').astype(float)
    dif = g_ols(-c.persist_pw.fillna(0).values, c.trat.values, c.leva.values) - g_ols(-c.quadrante.values, c.trat.values, c.leva.values)
    # 5: Q1
    q = gb[gb.leva.isin(LEVAS_ZIP) & gb.Grupo.isin(['ZIP', 'VEH', 'SCZIP'])].pivot_table(
        index=['_TargetID', 'leva', 'Grupo'], columns='Fase', values=['persist', 'quadrante']).reset_index()
    q.columns = ['_'.join(k).rstrip('_') for k in q.columns]
    q = q.dropna(subset=['persist_PT1', 'quadrante_PT1', 'quadrante_PT2']).assign(ZIP=lambda x: (x.Grupo == 'ZIP').astype(int))
    mq = smf.ols('quadrante_PT2 ~ ZIP * persist_PT1 + ZIP * quadrante_PT1 + C(leva)', q).fit()
    # 6: dissociação nos controles com PT2 em 24 h
    dv = gb[gb.leva.isin(LEVAS_24H) & gb.Grupo.isin(['VEH', 'SCZIP', 'MSO'])].pivot_table(
        index='_TargetID', columns='Fase', values=['persist', 'latencia']).dropna()
    dv.columns = [f'{a}_{b}' for a, b in dv.columns]
    zf = lambda v, ref: (v - ref.mean()) / ref.std()
    ida1, ida2 = -np.log(dv.latencia_PT1), -np.log(dv.latencia_PT2)
    D = (zf(dv.persist_PT2, dv.persist_PT1) - zf(dv.persist_PT1, dv.persist_PT1)) - (zf(ida2, ida1) - zf(ida1, ida1))
    res.append(dict(zona_cm=z, janela_s=w, n_pt1=len(p1), persist_local=p1.persist.median(), persist_girados=p1.persist_girados.median(),
                    acaso_p=acaso, rho_latencia=rho_lat, rho_pt1_pt2=rho_rep[0], rho_pt1_pt2_p=rho_rep[1], n_rep=len(wv),
                    sens_dif_g=dif, q1_est_por_0_1=mq.params['ZIP:persist_PT1'] * 0.1, q1_p=mq.pvalues['ZIP:persist_PT1'], q1_n=int(mq.nobs),
                    D_mediana=np.median(D), D_p=stats.wilcoxon(D).pvalue, D_n=len(D)))
r = pd.DataFrame(res)
r.to_csv(os.path.join(SAIDA, 'robustez_parametros.csv'), index=False)
pd.set_option('display.width', 250)
print(r.round(3).to_string(index=False))
