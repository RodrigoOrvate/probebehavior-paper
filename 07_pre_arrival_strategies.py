"""Estratégias do Rtrack antes da primeira chegada, na PT1 dos 278 ratos (exploratória, sem plano prévio; decidida antes de
ver as estratégias). O trecho até a chegada (o teste inteiro quando o rato não chega) vai para o Rtrack; trechos com menos
de 1 s não são classificados. Espaciais = estratégias 6–9, como no plano do critério de exclusão (acd74e7a). Única ligação
com o depois: a persistência difere entre quem chegou por estratégia espacial e quem chegou por não espacial? No fim, o
mesmo na PT2, com o escore espacial como mais uma medida da sensibilidade às drogas (Tabela S3a; acrescentado depois de ver
o resultado). Precisa do R com o Rtrack (Rscript no PATH ou na variável RSCRIPT). Saída em results/rtrack/."""
import glob
import os
import shutil
import subprocess

import numpy as np
import pandas as pd
import probebehavior as pb
from scipy import stats

from dados import PROPRIO, TROCADOS, experimento, saida

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


def classificar(e, pasta):
    """Exporta o trecho até a chegada, roda o Rtrack e devolve a estratégia e o escore espacial de cada teste."""
    x = pd.read_csv(pb.export_pre_arrival(e, pasta))
    os.makedirs(os.path.join(pasta, 'arenas'), exist_ok=True)
    dur = []
    for i, r in x.iterrows():
        destino = os.path.join('arenas', os.path.basename(r['_Arena']))
        shutil.copyfile(r['_Arena'], os.path.join(pasta, destino))
        x.at[i, '_Arena'] = destino.replace('\\', '/')
        t = pd.read_csv(os.path.join(pasta, r['_TrackFile'])).iloc[:, 0]
        dur.append(t.iloc[-1] - t.iloc[0])
    x['duracao_s'] = dur
    curtos = x[x.duracao_s < 1]
    print(f'trechos com menos de 1 s, não classificados: {len(curtos)} ({", ".join(curtos._TrackID)})')
    x[x.duracao_s >= 1].drop(columns=['exclusion', 'excluded_from']).to_csv(os.path.join(pasta, 'experiment.csv'), index=False)
    subprocess.run([rscript(), os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rtrack_strategies.R'), pasta],
                   check=True)
    r = pd.read_csv(os.path.join(pasta, 'rtrack_results.csv'))
    r = r.rename(columns={'Track_ID': '_TrackID'})[['_TrackID', 'strategy', 'confidence'] + [str(k) for k in NOMES]]
    d = x.merge(r, on='_TrackID', how='left')
    d['estrategia'] = d.strategy.map(NOMES)
    d['espacial'] = d.strategy.isin([6, 7, 8, 9])
    d['escore_espacial'] = d[[str(k) for k in (6, 7, 8, 9)]].sum(axis=1, min_count=1)
    return d


todos = experimento()
e = todos[todos.Fase == 'PT1']
d = classificar(e, SAIDA)
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


# ---------------- segunda sessão: o escore espacial como mais uma medida da sensibilidade (Tabela S3a) ----------------
# acrescentado depois de ver o resultado; mesmos contrastes, amostra (ratos com as duas sessões) e d da parte A do script 01
CONTRASTES = [('ZIP vs controls', {'ZIP'}, {'VEH', 'SCZIP'}, ['E9L3', 'E9L5', 'E3L1', 'E3L2', 'E5L3', 'E5L4', 'E8L1']),
              ('ASO vs MSO', {'ASO'}, {'MSO'}, ['E8L3']), ('PEP vs VEH', {'PEP'}, {'VEH'}, ['E5L2', 'E5L3', 'E8L4']),
              ('ICAP vs VEH', {'ICAP'}, {'VEH'}, ['E5L2']), ('LAC+ZIP vs LAC', {'LAC+ZIP'}, {'LAC'}, ['E8L1']),
              ('DYN+ZIP vs DYN', {'DYN+ZIP'}, {'DYN'}, ['E5L3', 'E5L4']), ('ZIP, PT2 at 3 h', {'ZIP'}, {'VEH'}, ['E7L2']),
              ('ZIP 6 h after PT1', {'ZIP'}, {'VEH'}, ['E9L1'])]
AMNESICOS = 3
rng = np.random.default_rng(20261105)
d2 = classificar(todos[todos.Fase == 'PT2'], saida('results/rtrack/pt2'))
prov = pd.read_csv(os.path.join(saida('results/abc'), 'provas.csv'))
prov = prov[~prov._TargetID.isin(TROCADOS | PROPRIO)]
pt2 = prov[(prov.Fase == 'PT2') & prov._TargetID.isin(prov._TargetID[prov.Fase == 'PT1'])]
pt2 = pt2.merge(d2[['_TrackID', 'escore_espacial', 'espacial']], on='_TrackID', how='left')


def d_ols(y, trat, leva):
    """Coeficiente do tratamento dividido pelo DP residual, em y ~ tratamento + leva (o d do script 01)."""
    X = np.column_stack([np.ones_like(y), trat] + [(leva == l).astype(float) for l in np.unique(leva)[1:]])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    return b[1] / np.sqrt(res @ res / (len(y) - X.shape[1]))


linhas = []
for k, (nome, trat, ctl, levas) in enumerate(CONTRASTES):
    c = pt2[pt2.leva.isin(levas) & pt2.Grupo.isin(trat | ctl)]
    c = c.assign(t=c.Grupo.isin(trat).astype(float))
    cc = c.dropna(subset=['escore_espacial'])
    lin = dict(contraste=nome, n=f'{int(c.t.sum())} × {int((1 - c.t).sum())}',
               d_quadrante=d_ols(-c.quadrante.values, c.t.values, c.leva.values),
               d_escore=d_ols(-cc.escore_espacial.values, cc.t.values, cc.leva.values), n_escore=len(cc),
               pct_espacial_tratado=100 * cc.espacial[cc.t == 1].mean(), pct_espacial_controle=100 * cc.espacial[cc.t == 0].mean())
    if k < AMNESICOS:
        lv = cc.leva.values
        grupos = [g for g in (np.flatnonzero((lv == l) & (cc.t.values == z)) for l in np.unique(lv) for z in (0, 1)) if len(g)]
        bs = []
        for _ in range(5000):
            cb = cc.iloc[np.concatenate([rng.choice(g, len(g)) for g in grupos])]
            bs.append(d_ols(-cb.escore_espacial.values, cb.t.values, cb.leva.values)
                      - d_ols(-cb.quadrante.values, cb.t.values, cb.leva.values))
        lin.update(dif=np.median(bs), dif_inf=np.percentile(bs, 2.5), dif_sup=np.percentile(bs, 97.5))
    linhas.append(lin)
sens = pd.DataFrame(linhas)
sens.to_csv(os.path.join(SAIDA, 'sensibilidade_pt2.csv'), index=False)
print('\nPT2: d do escore espacial (positivo = pior memória no tratado) e diferença para o quadrante, nos mesmos ratos')
print(sens.round(2).to_string(index=False))
