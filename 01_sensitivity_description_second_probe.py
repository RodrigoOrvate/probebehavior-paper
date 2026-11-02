"""Partes A (sensibilidade), B (descrição na PT1) e C (segunda quebra na PT2) do plano
plans/PLANO_sensibilidade_descricao_segunda_quebra.md (hash 9fad5a40…, commit f7dcf37). Saída em results/abc/."""
import os

import numpy as np
import pandas as pd
import probebehavior as pb
import statsmodels.formula.api as smf
from scipy import stats

from dados import PROPRIO, TROCADOS, classicas, experimento, saida

SAIDA = saida('results/abc')
rng = np.random.default_rng(20261102)
pd.set_option('display.width', 230)

# ---------------- dados ----------------
arq = os.path.join(SAIDA, 'provas.csv')
if os.path.exists(arq):
    d = pd.read_csv(arq)
else:
    e = experimento()
    cheia, _ = pb.measure_experiment(e)
    parcial, _ = pb.measure_experiment(e, pb.Settings(partial_window=True))
    x = cheia.set_index('_TrackID').join(parcial.set_index('_TrackID')[['persistence', 'reentries']].add_suffix('_pw'))
    d = x.join(classicas(e)).reset_index().rename(columns={'index': '_TrackID', 'Experimento': 'leva'})
    d.to_csv(arq, index=False)
d['reached'] = d.reached.astype(bool)
base = d[~d._TargetID.isin(TROCADOS | PROPRIO)]

# ---------------- parte A ----------------
CONTRASTES = [('amnésico', 'ZIP × controles', {'ZIP'}, {'VEH', 'SCZIP'}, ['E9L3', 'E9L5', 'E3L1', 'E3L2', 'E5L3', 'E5L4', 'E8L1']),
              ('amnésico', 'ASO × MSO', {'ASO'}, {'MSO'}, ['E8L3']),
              ('amnésico', 'PEP × VEH', {'PEP'}, {'VEH'}, ['E5L2', 'E5L3', 'E8L4']),
              ('sem amnésia', 'ICAP × VEH', {'ICAP'}, {'VEH'}, ['E5L2']),
              ('sem amnésia', 'LAC+ZIP × LAC', {'LAC+ZIP'}, {'LAC'}, ['E8L1']),
              ('sem amnésia', 'DYN+ZIP × DYN', {'DYN+ZIP'}, {'DYN'}, ['E5L3', 'E5L4']),
              ('sem amnésia', 'ZIP × VEH, PT2 em 3 h', {'ZIP'}, {'VEH'}, ['E7L2']),
              ('sem amnésia', 'ZIP 6 h depois × VEH', {'ZIP'}, {'VEH'}, ['E9L1'])]
# sinal: +1 quando valor maior = memória pior
MEDIDAS = {'quadrante': -1, 'gallagher': +1, 'cruzamentos': -1, 'latencia': +1, 'persistencia': -1, 'reentradas': -1}


def orientar(t):
    t = t.copy()
    t['latencia'] = t.arrival_latency_s.where(t.reached, 60.0).fillna(60.0)
    t['persistencia'] = t.persistence_pw.fillna(0.0)
    t['reentradas'] = t.reentries_pw.fillna(0.0)
    for k, s in MEDIDAS.items():
        t[k] = s * t[k]
    return t


def g_ols(y, trat, leva, cov=None):
    """Coeficiente do tratamento dividido pelo DP residual, em y ~ tratamento + leva (+ covariável)."""
    cols = [np.ones_like(y), trat] + [(leva == l).astype(float) for l in np.unique(leva)[1:]]
    if cov is not None:
        cols.append(cov)
    X = np.column_stack(cols)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    return b[1] / np.sqrt(res @ res / (len(y) - X.shape[1]))


def contraste(trat, ctl, levas, fase='PT2'):
    t = base[base.leva.isin(levas) & base.Grupo.isin(trat | ctl)]
    a = orientar(t[t.Fase == fase]).set_index('_TargetID')
    b = orientar(t[t.Fase == 'PT1']).set_index('_TargetID')
    return a.join(b[list(MEDIDAS)].add_suffix('_PT1'), how='inner').assign(trat=lambda x: x.Grupo.isin(trat).astype(float))


linhas, boot = [], {}
for tipo, nome, trat, ctl, levas in CONTRASTES:
    c = contraste(trat, ctl, levas).dropna(subset=list(MEDIDAS))
    lv = c.leva.values
    for k in MEDIDAS:
        g = g_ols(c[k].values, c.trat.values, lv)
        cc = c.dropna(subset=[f'{k}_PT1'])
        g2 = g_ols(cc[k].values, cc.trat.values, cc.leva.values, cc[f'{k}_PT1'].values)
        linhas.append(dict(tipo=tipo, contraste=nome, medida=k, g=g, g_ancova=g2, n_trat=int(c.trat.sum()),
                           n_ctl=int((1 - c.trat).sum()), n80_por_grupo=int(np.ceil(2 * (1.96 + 0.8416) ** 2 / g ** 2)) if g else None))
    if tipo == 'amnésico':
        grupos = [np.flatnonzero((lv == l) & (c.trat.values == z)) for l in np.unique(lv) for z in (0, 1)]
        grupos = [gi for gi in grupos if len(gi)]
        bs = np.empty((5000, 3))
        for i in range(5000):
            ix = np.concatenate([rng.choice(gi, len(gi)) for gi in grupos])
            cb = c.iloc[ix]
            bs[i] = [g_ols(cb[k].values, cb.trat.values, cb.leva.values) for k in ('persistencia', 'quadrante', 'gallagher')]
        boot[nome] = bs
a = pd.DataFrame(linhas)
a.to_csv(os.path.join(SAIDA, 'A_sensibilidade.csv'), index=False)
print('PARTE A: g (maior = pior memória no tratado), PT2')
print(a.pivot_table(index=['tipo', 'contraste'], columns='medida', values='g', sort=False).round(2)[list(MEDIDAS)].to_string())
print('\ng com a PT1 como covariável:')
print(a.pivot_table(index=['tipo', 'contraste'], columns='medida', values='g_ancova', sort=False).round(2)[list(MEDIDAS)].to_string())
print('\nn por grupo e n para 80% de poder (ZIP × controles):')
print(a[a.contraste == 'ZIP × controles'][['medida', 'g', 'n_trat', 'n_ctl', 'n80_por_grupo']].round(2).to_string(index=False))
print('\ndiferenças com IC 95% por bootstrap:')
for nome, bs in boot.items():
    for j, ref in ((1, 'quadrante'), (2, 'gallagher')):
        dif = bs[:, 0] - bs[:, j]
        print(f'  {nome:16s} g(persistência) − g({ref}): {np.median(dif):+.2f} [{np.percentile(dif, 2.5):+.2f}; {np.percentile(dif, 97.5):+.2f}]')

# ---------------- parte B ----------------
LEVAS_B = ['E3L1', 'E3L2', 'E5L2', 'E5L3', 'E5L4', 'E7L2', 'E8L1', 'E8L2', 'E8L3', 'E8L4', 'E9L1', 'E9L3', 'E9L5']
POS = ['persistence', 'reentries', 'first_stay_s', 'mean_distance', 'speed', 'turning_deg_s', 'wall_latency_s', 'other_locations_visits']
p1 = d[d.leva.isin(LEVAS_B) & (d.Fase == 'PT1')]
print(f'\nPARTE B: PT1 de {len(p1)} ratos em {p1.leva.nunique()} levas; chegaram {p1.reached.sum()} ({p1.reached.mean():.0%}); '
      f'com 15 s pela frente: {p1.persistence.notna().sum()}')
print(p1.groupby('leva').agg(n=('reached', 'size'), chegaram=('reached', 'mean'), latencia=('arrival_latency_s', 'median'),
                             persistencia=('persistence', 'median')).round(2).T.to_string())
ok = p1.dropna(subset=['persistence'])
for k in POS:
    s = ok[k].dropna()
    print(f'  {k:24s} mediana {s.median():7.2f} [{s.quantile(.25):7.2f}; {s.quantile(.75):7.2f}]  n = {len(s)}')

# acaso: persistência em volta dos locais girados nos mesmos 15 s
fora = []
e = experimento()
for rec in e[e._TrackID.isin(ok._TrackID)].to_dict('records'):
    ar = pb.read_rtrack_arena(rec['_Arena'])
    t, x, y = pb.read_track(rec['_TrackFile'])
    m, _ = pb.measure(t, x, y, ar)
    vals = []
    for gx, gy in pb.rotated_goals(ar):
        mr, _ = pb.measure(t, x, y, pb.Arena(ar.center, ar.radius, (gx, gy), ar.goal_radius))
        w = (t >= m['arrival_latency_s']) & (t < m['arrival_latency_s'] + 15)
        vals.append((np.hypot(x[w] - gx, y[w] - gy) <= 20).mean())
    fora.append(dict(_TrackID=rec['_TrackID'], persist_girados=np.mean(vals)))
ok = ok.merge(pd.DataFrame(fora), on='_TrackID')
w = stats.wilcoxon(ok.persistence, ok.persist_girados)
print(f'  acaso: persistência no local {ok.persistence.median():.2f} × locais girados {ok.persist_girados.median():.2f} '
      f'(Wilcoxon p = {w.pvalue:.2g}, n = {len(ok)})')
print('  Spearman com a força da memória:')
for k in POS:
    s = ok[['arrival_latency_s', 'path_efficiency', k]].dropna()
    print(f'    {k:24s} latência ρ = {stats.spearmanr(s.arrival_latency_s, s[k])[0]:+.2f}; eficiência ρ = {stats.spearmanr(s.path_efficiency, s[k])[0]:+.2f}')
z = ok[POS].dropna()
z = (z - z.mean()) / z.std()
val, vec = np.linalg.eigh(np.corrcoef(z.T.values))
o = np.argsort(val)[::-1]
print(f'  componentes principais: variância explicada {np.round(val[o][:3] / val.sum(), 2)}')
print(pd.DataFrame(vec[:, o[:2]], index=POS, columns=['CP1', 'CP2']).round(2).to_string())
mm = smf.mixedlm('persistence ~ 1', ok, groups=ok.leva).fit()
var_l = float(mm.cov_re.iloc[0, 0])
print(f'  variância da persistência entre levas: {var_l / (var_l + mm.scale):.0%}')
ok.to_csv(os.path.join(SAIDA, 'B_pt1.csv'), index=False)

# ---------------- parte C ----------------
pv = d[d.leva.isin(LEVAS_B)].pivot_table(index=['_TargetID', 'leva', 'Grupo'], columns='Fase',
                                          values=['reached', 'arrival_latency_s', 'persistence', 'reentries', 'first_stay_s', 'wall_latency_s'],
                                          aggfunc='first')
pv.columns = [f'{a}_{b}' for a, b in pv.columns]
pv = pv.reset_index()
pv = pv[~pv._TargetID.isin(TROCADOS | PROPRIO) & (pv.reached_PT1 == True)]
ctl = pv[pv.Grupo.isin(['VEH', 'SCZIP', 'MSO'])]
print(f'\nPARTE C: controles que chegaram na PT1: {len(ctl)}; chegaram também na PT2: {(ctl.reached_PT2 == True).sum()}')
for interv, levas in [('todos', LEVAS_B), ('3 h (E7L2)', ['E7L2']), ('24 h', [l for l in LEVAS_B if l not in ('E7L2', 'E9L3')]), ('7 dias (E9L3)', ['E9L3'])]:
    c = ctl[ctl.leva.isin(levas)]
    both = c[c.reached_PT2 == True]
    print(f'  {interv}: n = {len(c)}, chegam na PT2: {len(both)} ({len(both) / max(len(c), 1):.0%})')
    for k in ['arrival_latency_s', 'persistence', 'reentries', 'first_stay_s', 'wall_latency_s']:
        s = both[[f'{k}_PT1', f'{k}_PT2']].dropna()
        if len(s) >= 6:
            w = stats.wilcoxon(s.iloc[:, 0], s.iloc[:, 1])
            print(f'    {k:20s} PT1 {s.iloc[:, 0].median():6.2f} → PT2 {s.iloc[:, 1].median():6.2f}  (p = {w.pvalue:.2g}, n = {len(s)})')
zc = pv[pv.leva.isin(['E9L3', 'E9L5', 'E3L1', 'E3L2', 'E5L3', 'E5L4', 'E8L1']) & pv.Grupo.isin(['ZIP', 'VEH', 'SCZIP'])]
zc = zc.dropna(subset=['persistence_PT1', 'persistence_PT2']).assign(ZIP=lambda x: (x.Grupo == 'ZIP').astype(int))
m = smf.ols('persistence_PT2 ~ ZIP + persistence_PT1 + C(leva)', zc).fit()
lo, hi = m.conf_int().loc['ZIP']
print(f'  ZIP × controles na persistência da PT2 (ajustada pela PT1): {m.params["ZIP"]:+.3f} [{lo:+.3f}; {hi:+.3f}], p = {m.pvalues["ZIP"]:.2g}, '
      f'n = {int(m.nobs)} (ZIP {zc.ZIP.sum()})')
pv.to_csv(os.path.join(SAIDA, 'C_pt1_pt2.csv'), index=False)
print('→ results/abc/')
