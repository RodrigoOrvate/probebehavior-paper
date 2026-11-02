"""Estratégias do Rtrack antes da primeira chegada, na PT1 dos 278 ratos (exploratória, sem plano prévio; decidida antes de
ver as estratégias). O trecho até a chegada (o teste inteiro quando o rato não chega) vai para o Rtrack; trechos com menos
de 1 s não são classificados. Espaciais = estratégias 6–9, como no plano do critério de exclusão (acd74e7a). Única ligação
com o depois: a persistência difere entre quem chegou por estratégia espacial e quem chegou por não espacial? Precisa do R
com o Rtrack (Rscript no PATH ou na variável RSCRIPT). Saída em results/rtrack/."""
import glob
import os
import shutil
import subprocess

import numpy as np
import pandas as pd
import probebehavior as pb
from scipy import stats

from dados import experimento, saida

SAIDA = saida('results/rtrack')
NOMES = {1: 'thigmotaxis', 2: 'circling', 3: 'random path', 4: 'scanning', 5: 'chaining', 6: 'directed search',
         7: 'corrected path', 8: 'direct path', 9: 'perseverance'}


def rscript():
    achado = os.environ.get('RSCRIPT') or shutil.which('Rscript')
    if not achado:
        achado = next(iter(sorted(glob.glob(r'C:\Program Files\R\R-*\bin\Rscript.exe'), reverse=True)), None)
    if not achado:
        raise SystemExit('Rscript não encontrado: instale o R com o Rtrack ou indique o caminho em RSCRIPT')
    return achado


e = experimento()
e = e[e.Fase == 'PT1']
arq = pb.export_pre_arrival(e, SAIDA)
x = pd.read_csv(arq)
os.makedirs(os.path.join(SAIDA, 'arenas'), exist_ok=True)
dur = []
for i, r in x.iterrows():
    destino = os.path.join('arenas', os.path.basename(r['_Arena']))
    shutil.copyfile(r['_Arena'], os.path.join(SAIDA, destino))
    x.at[i, '_Arena'] = destino.replace('\\', '/')
    t = pd.read_csv(os.path.join(SAIDA, r['_TrackFile'])).iloc[:, 0]
    dur.append(t.iloc[-1] - t.iloc[0])
x['duracao_s'] = dur
curtos = x[x.duracao_s < 1]
print(f'trechos com menos de 1 s, não classificados: {len(curtos)} ({", ".join(curtos._TrackID)})')
x[x.duracao_s >= 1].drop(columns=['exclusion', 'excluded_from']).to_csv(os.path.join(SAIDA, 'experiment.csv'), index=False)
subprocess.run([rscript(), os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rtrack_strategies.R'), SAIDA], check=True)

r = pd.read_csv(os.path.join(SAIDA, 'rtrack_results.csv'))
r = r.rename(columns={'Track_ID': '_TrackID'})[['_TrackID', 'strategy', 'confidence'] + [str(k) for k in NOMES]]
d = x.merge(r, on='_TrackID', how='left')
d['estrategia'] = d.strategy.map(NOMES)
d['espacial'] = d.strategy.isin([6, 7, 8, 9])
d['escore_espacial'] = d[[str(k) for k in (6, 7, 8, 9)]].sum(axis=1, min_count=1)
d['trecho'] = np.where(d.reached, 'antes da chegada', 'teste inteiro (não chegou)')
m, _ = pb.measure_experiment(e)
d = d.merge(m[['_TrackID', 'arrival_latency_s', 'persistence']], on='_TrackID', how='left')
d.to_csv(os.path.join(SAIDA, 'estrategias_pt1.csv'), index=False)

cl = d.dropna(subset=['strategy'])
print(f'\nclassificados: {len(cl)} de {len(d)}; chegaram {int(cl.reached.sum())}, não chegaram {int((~cl.reached).sum())}')
tab = pd.crosstab(cl.estrategia, cl.trecho).reindex([NOMES[k] for k in NOMES]).fillna(0).astype(int)
pct = (100 * tab / tab.sum()).round(0).astype(int)
tab = tab.astype(str) + ' (' + pct.astype(str) + '%)'
print(tab.to_string())
tab.to_csv(os.path.join(SAIDA, 'tabela_estrategias.csv'))
for k, g in cl.groupby('trecho'):
    print(f'  {k}: espaciais {100 * g.espacial.mean():.0f}% (n = {len(g)}); confiança mediana {g.confidence.median():.2f}')

p = cl.dropna(subset=['persistence'])
a, b = p.persistence[p.espacial], p.persistence[~p.espacial]
mw = stats.mannwhitneyu(a, b)
rho = stats.spearmanr(p.escore_espacial, p.persistence)
print(f'\npersistência (chegaram com 15 s pela frente, n = {len(p)}): espacial {a.median():.3f} (n = {len(a)}) × '
      f'não espacial {b.median():.3f} (n = {len(b)}); Mann–Whitney p = {mw.pvalue:.2g}; '
      f'r bisserial {2 * mw.statistic / (len(a) * len(b)) - 1:+.2f} (positivo = maior nos espaciais)')
print(f'persistência × escore espacial: ρ = {rho[0]:+.2f} (p = {rho[1]:.2g})')

# acrescentado depois de ver o resultado acima: a associação é só a latência? (correlação de postos parcial, com a leva)
pr = p.assign(**{c: p[c].rank() for c in ('persistence', 'escore_espacial', 'arrival_latency_s')})
X = pd.get_dummies(pr[['arrival_latency_s', 'Experimento']], drop_first=True, dtype=float).assign(c=1.0).to_numpy()
res = {c: pr[c] - X @ np.linalg.lstsq(X, pr[c], rcond=None)[0] for c in ('persistence', 'escore_espacial')}
parc = stats.pearsonr(res['persistence'], res['escore_espacial'])
print(f'persistência × escore espacial, ajustada pela latência e pela leva: ρ parcial = {parc[0]:+.2f} (p = {parc[1]:.2g})')
print(f'latência × escore espacial: ρ = {stats.spearmanr(p.arrival_latency_s, p.escore_espacial)[0]:+.2f}')
