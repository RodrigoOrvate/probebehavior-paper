"""Teste da dissociação na segunda quebra (plans/PLANO_dissociacao_segunda_quebra.md, hash 196622eb…, commit d58a85f)."""
import os

import numpy as np
import pandas as pd
import probebehavior as pb
from scipy import stats

from dados import PROPRIO, TROCADOS, experimento, saida

SAIDA = saida('results/abc')
rng = np.random.default_rng(20261103)
LEVAS_24H = ['E3L1', 'E3L2', 'E5L2', 'E5L3', 'E5L4', 'E8L1', 'E8L2', 'E8L3', 'E8L4', 'E9L1', 'E9L5']
CONTROLES = ['VEH', 'SCZIP', 'MSO']

d = pd.read_csv(os.path.join(SAIDA, 'provas.csv'))
dur = {}
e = experimento()
for rec in e[e._TrackID.isin(d._TrackID)].to_dict('records'):
    t, _, _ = pb.read_track(rec['_TrackFile'])
    dur[rec['_TrackID']] = np.nanmax(t)
d['duracao_s'] = d._TrackID.map(dur)
inc = d[d.duracao_s < 58]
print(f'sessões incompletas (< 58 s): {len(inc)}')
print(inc[['_TrackID', 'Grupo', 'Fase', 'duracao_s']].round(1).to_string(index=False))
ruins = set(inc._TargetID)

w = d.pivot_table(index=['_TargetID', 'leva', 'Grupo'], columns='Fase', values=['reached', 'arrival_latency_s', 'persistence', 'reentries'],
                  aggfunc='first')
w.columns = [f'{a}_{b}' for a, b in w.columns]
w = w.reset_index()
w = w[w.Grupo.isin(CONTROLES) & ~w._TargetID.isin(TROCADOS | PROPRIO | ruins)]


def teste(t, insist='persistence', rotulo=''):
    ida1, ida2 = -np.log(t.arrival_latency_s_PT1), -np.log(t.arrival_latency_s_PT2)
    in1, in2 = t[f'{insist}_PT1'], t[f'{insist}_PT2']
    z = lambda v, ref: (v - ref.mean()) / ref.std()
    d_ida = z(ida2, ida1) - z(ida1, ida1)
    d_in = z(in2, in1) - z(in1, in1)
    D = (d_in - d_ida).values
    bs = [np.median(rng.choice(D, len(D))) for _ in range(5000)]
    p = stats.wilcoxon(D).pvalue
    print(f'  {rotulo:44s} n = {len(t):3d}; mudança da ida {np.median(d_ida):+.2f} (p = {stats.wilcoxon(d_ida).pvalue:.2g}); '
          f'da insistência {np.median(d_in):+.2f} (p = {stats.wilcoxon(d_in).pvalue:.2g}); '
          f'D {np.median(D):+.2f} [{np.percentile(bs, 2.5):+.2f}; {np.percentile(bs, 97.5):+.2f}], p = {p:.2g}')
    return D


lv = w[w.leva.isin(LEVAS_24H)]
chegou1 = lv[(lv.reached_PT1 == True) & lv.persistence_PT1.notna()]
principal = chegou1[(chegou1.reached_PT2 == True) & chegou1.persistence_PT2.notna()]
print(f'\ncontroles com PT2 em 24 h, completos: {len(lv)}; chegaram na PT1 com 15 s: {len(chegou1)}; também na PT2: {len(principal)}')
print('PRINCIPAL')
teste(principal, rotulo='persistência, chegaram nas duas')
print('CHECAGENS')
med = principal.persistence_PT1.median()
teste(principal[principal.persistence_PT1 > med], rotulo='metade alta da persistência na PT1')
teste(principal[principal.persistence_PT1 <= med], rotulo='metade baixa da persistência na PT1')
todos = chegou1.copy()
sem = ~((todos.reached_PT2 == True) & todos.persistence_PT2.notna())
todos.loc[sem, 'arrival_latency_s_PT2'] = todos.loc[sem, 'arrival_latency_s_PT2'].where(todos.reached_PT2 == True, 60.0)
todos.loc[sem, 'persistence_PT2'] = 0.0
todos.loc[sem, 'reentries_PT2'] = 0.0
teste(todos, rotulo='todos que chegaram na PT1 (60 s e 0 na PT2)')
teste(principal, 'reentries', rotulo='reentradas no lugar da persistência')
print('INTERVALOS, só descritos')
for nome, l in [('3 h (E7L2)', 'E7L2'), ('7 dias (E9L3)', 'E9L3')]:
    s = w[(w.leva == l) & (w.reached_PT1 == True) & (w.reached_PT2 == True)].dropna(subset=['persistence_PT1', 'persistence_PT2'])
    print(f'  {nome}: n = {len(s)}; persistência {s.persistence_PT1.median():.2f} → {s.persistence_PT2.median():.2f}; '
          f'latência {s.arrival_latency_s_PT1.median():.1f} → {s.arrival_latency_s_PT2.median():.1f} s')
principal.to_csv(os.path.join(SAIDA, 'dissociacao_controles.csv'), index=False)
