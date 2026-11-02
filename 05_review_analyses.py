"""Análises exploratórias pedidas na revisão do manuscrito (02/11/2026), sem plano prévio: fluxo de animais, sensibilidade
sem persistência zero para quem não chega, regressão à média contínua, covariáveis motoras e trajetórias representativas
(Figura S3). Saída em results/review/."""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import probebehavior as pb
import statsmodels.formula.api as smf
from matplotlib.patches import Circle
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor

from dados import PROPRIO, TROCADOS, experimento, saida

SAIDA = saida('results/review')
FIG = saida('figures')
rng = np.random.default_rng(20261104)
LEVAS_B = ['E3L1', 'E3L2', 'E5L2', 'E5L3', 'E5L4', 'E7L2', 'E8L1', 'E8L2', 'E8L3', 'E8L4', 'E9L1', 'E9L3', 'E9L5']
ZIP_LEVAS = ['E9L3', 'E9L5', 'E3L1', 'E3L2', 'E5L3', 'E5L4', 'E8L1']
AMN = [('ZIP vs controls', {'ZIP'}, {'VEH', 'SCZIP'}, ZIP_LEVAS), ('ASO vs MSO', {'ASO'}, {'MSO'}, ['E8L3']),
       ('PEP vs VEH', {'PEP'}, {'VEH'}, ['E5L2', 'E5L3', 'E8L4'])]
out = open(os.path.join(SAIDA, 'resumo.txt'), 'w', encoding='utf-8')


def say(s=''):
    print(s)
    out.write(s + '\n')


d = pd.read_csv(os.path.join(saida('results/abc'), 'provas.csv'))
d['reached'] = d.reached.astype(bool)
d = d[d.leva.isin(LEVAS_B)]

# ---------------- covariáveis cinemáticas a partir das trajetórias ----------------
arq = os.path.join(SAIDA, 'cinematica.csv')
if os.path.exists(arq):
    cin = pd.read_csv(arq)
else:
    linhas = []
    e = experimento()
    for rec in e[e._TrackID.isin(d._TrackID[d.reached])].to_dict('records'):
        ar = pb.read_rtrack_arena(rec['_Arena'])
        t, x, y = pb.clean(*pb.read_track(rec['_TrackFile']), 60)
        i = pb.first_arrival(t, x, y, ar)
        if i is None or i < 2:
            continue
        j = max(int(np.searchsorted(t, t[i] - 0.5)), 0)
        v = np.array([x[i] - x[j], y[i] - y[j]])
        fora = np.array([ar.goal[0] - ar.center[0], ar.goal[1] - ar.center[1]])
        ang = np.degrees(np.arccos(np.clip(v @ fora / (np.linalg.norm(v) * np.linalg.norm(fora) + 1e-12), -1, 1)))
        caminho = np.hypot(np.diff(x[:i + 1]), np.diff(y[:i + 1])).sum()
        linhas.append(dict(_TrackID=rec['_TrackID'], entry_angle_deg=ang,
                           arrival_speed=np.linalg.norm(v) / max(t[i] - t[j], 1e-6),
                           pre_speed=caminho / max(t[i] - t[0], 1e-6),
                           goal_to_wall_cm=ar.radius - np.linalg.norm(fora)))
    cin = pd.DataFrame(linhas)
    cin.to_csv(arq, index=False)
d = d.merge(cin, on='_TrackID', how='left')

# ---------------- 1. fluxo de animais ----------------
say('1. FLUXO DE ANIMAIS')
p1 = d[d.Fase == 'PT1']
say(f'  PT1, descrição: {len(p1)} ratos em {p1.leva.nunique()} levas; chegaram {p1.reached.sum()}; '
    f'com 15 s pela frente {p1.persistence.notna().sum()}; com 30 s (curvas) {(p1.arrival_latency_s <= 30).sum()}')
fl = p1.groupby('leva').agg(ratos=('reached', 'size'), chegaram=('reached', 'sum'),
                            com_15s=('persistence', lambda s: s.notna().sum())).reindex(LEVAS_B)
z = pd.read_csv(os.path.join(saida('results/zip_test'), 'dados_por_rato.csv'))
z = z[z.leva.isin(ZIP_LEVAS)]
zb = z[~z._TargetID.isin(TROCADOS | PROPRIO)]
say(f'  teste do ZIP: {len(z)} ratos ZIP ou controle com quadrante nas duas sessões ({z.ZIP.sum()} ZIP); '
    f'excluídos {len(z) - len(zb)}; chegaram na PT1 {zb.reached.sum()}; com 15 s {zb.persist.notna().sum()} '
    f'({zb.dropna(subset=["persist"]).ZIP.sum()} ZIP)')
fz = zb.groupby(['leva', 'ZIP']).agg(n=('ZIP', 'size'), com_15s=('persist', lambda s: s.notna().sum())).unstack('ZIP')
fz.columns = [f'{a}_{"ZIP" if b else "ctl"}' for a, b in fz.columns]
fl = fl.join(fz)
dc = pd.read_csv(os.path.join(saida('results/abc'), 'dissociacao_controles.csv'))
say(f'  PT1 → PT2 nos controles (24 h): {len(dc)} chegaram nas duas sessões com 15 s pela frente')
fl = fl.join(dc.groupby('leva').size().rename('ctl_PT1_PT2'))
fl.fillna(0).astype(int).to_csv(os.path.join(SAIDA, 'fluxo_por_leva.csv'))
say(fl.fillna(0).astype(int).to_string())

# ---------------- 2. sensibilidade sem persistência zero ----------------
say('\n2. SENSIBILIDADE SEM PERSISTÊNCIA ZERO PARA QUEM NÃO CHEGA (PT2)')
base = d[~d._TargetID.isin(TROCADOS | PROPRIO)]


def g_ols(y, trat, leva):
    cols = [np.ones_like(y), trat] + [(leva == l).astype(float) for l in np.unique(leva)[1:]]
    X = np.column_stack(cols)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    return b[1] / np.sqrt(res @ res / (len(y) - X.shape[1]))


def g_boot(c, cols, n=5000):
    lv, tr = c.leva.values, c.trat.values
    grupos = [gi for gi in (np.flatnonzero((lv == l) & (tr == k)) for l in np.unique(lv) for k in (0, 1)) if len(gi)]
    bs = np.empty((n, len(cols)))
    for i in range(n):
        ix = np.concatenate([rng.choice(gi, len(gi)) for gi in grupos])
        bs[i] = [g_ols(c[k].values[ix], tr[ix], lv[ix]) for k in cols]
    return bs


sens = []
for nome, trat, ctl, levas in AMN:
    c = base[base.leva.isin(levas) & base.Grupo.isin(trat | ctl) & (base.Fase == 'PT2')].copy()
    c['trat'] = c.Grupo.isin(trat).astype(float)
    c['quadrante'] = -c.quadrante
    c['chegou'] = -c.reached.astype(float)
    c['persistencia'] = -c.persistence_pw
    todos = c.dropna(subset=['quadrante'])
    ch = todos.dropna(subset=['persistencia'])
    g_ch = [g_ols(ch[k].values, ch.trat.values, ch.leva.values) for k in ('persistencia', 'quadrante')]
    bs = g_boot(ch, ['persistencia', 'quadrante'])
    dif = bs[:, 0] - bs[:, 1]
    g_r = g_ols(todos.chegou.values, todos.trat.values, todos.leva.values)
    bq = g_boot(todos, ['chegou', 'quadrante'])
    sens.append(dict(contraste=nome, n_todos=len(todos), n_trat_todos=int(todos.trat.sum()), g_chegou=g_r,
                     g_quadrante_todos=g_ols(todos.quadrante.values, todos.trat.values, todos.leva.values),
                     dif_chegou_quad=np.median(bq[:, 0] - bq[:, 1]), dif_chegou_lo=np.percentile(bq[:, 0] - bq[:, 1], 2.5),
                     dif_chegou_hi=np.percentile(bq[:, 0] - bq[:, 1], 97.5),
                     n_chegaram=len(ch), n_trat_chegaram=int(ch.trat.sum()), g_persist_chegaram=g_ch[0], g_quad_chegaram=g_ch[1],
                     dif_med=np.median(dif), dif_lo=np.percentile(dif, 2.5), dif_hi=np.percentile(dif, 97.5)))
sens = pd.DataFrame(sens)
sens.to_csv(os.path.join(SAIDA, 'sensibilidade_sem_zero.csv'), index=False)
for r in sens.itertuples():
    say(f'  {r.contraste}: todos n = {r.n_todos} ({r.n_trat_todos} trat): g(chegou) {r.g_chegou:+.2f}, g(quadrante) {r.g_quadrante_todos:+.2f}, '
        f'diferença {r.dif_chegou_quad:+.2f} [{r.dif_chegou_lo:+.2f}; {r.dif_chegou_hi:+.2f}]')
    say(f'  {"":{len(r.contraste)}}  só quem chegou n = {r.n_chegaram} ({r.n_trat_chegaram} trat): g(persistência) {r.g_persist_chegaram:+.2f}, '
        f'g(quadrante) {r.g_quad_chegaram:+.2f}, diferença {r.dif_med:+.2f} [{r.dif_lo:+.2f}; {r.dif_hi:+.2f}]')

# ---------------- 3. regressão à média, contínua ----------------
say('\n3. REGRESSÃO À MÉDIA, MODELO CONTÍNUO (controles, PT2 em 24 h, chegaram nas duas sessões)')
rtm = []
for rot, a, b in [('persistência', dc.persistence_PT1, dc.persistence_PT2),
                  ('ida ao local, −log latência', -np.log(dc.arrival_latency_s_PT1), -np.log(dc.arrival_latency_s_PT2))]:
    z1, z2 = (a - a.mean()) / a.std(), (b - a.mean()) / a.std()
    t = pd.DataFrame(dict(delta=z2 - z1, base=z1, leva=dc.leva))
    m = smf.ols('delta ~ base + C(leva, Sum)', t).fit()
    r = stats.pearsonr(z1, z2)[0]
    esp = r * (b.std() / a.std()) - 1
    lo, hi = m.conf_int().loc['base']
    il, ih = m.conf_int().loc['Intercept']
    rtm.append(dict(medida=rot, n=len(t), r_teste_reteste=r, inclinacao=m.params['base'], inc_lo=lo, inc_hi=hi,
                    inclinacao_esperada_rtm=esp, mudanca_na_media=m.params['Intercept'], mud_lo=il, mud_hi=ih))
    say(f'  {rot:30s} n = {len(t)}; r = {r:.2f}; inclinação da mudança sobre a PT1 {m.params["base"]:+.2f} [{lo:+.2f}; {hi:+.2f}] '
        f'(esperada só por regressão à média: {esp:+.2f}); mudança na média da PT1 {m.params["Intercept"]:+.2f} DP [{il:+.2f}; {ih:+.2f}]')
pd.DataFrame(rtm).to_csv(os.path.join(SAIDA, 'regressao_media_continua.csv'), index=False)

# ---------------- 4. covariáveis motoras ----------------
say('\n4. COVARIÁVEIS MOTORAS (PT1, chegaram com 15 s pela frente)')
COV = {'arrival_speed': 'velocidade na chegada', 'pre_speed': 'velocidade antes da chegada',
       'entry_angle_deg': 'ângulo de entrada (0° = rumo à parede)'}
ok = p1.dropna(subset=['persistence'] + list(COV)).copy()
say('  (a eficiência antes da chegada fica fora: é medida de memória, não motora)')
say(f'  n = {len(ok)} (de {p1.persistence.notna().sum()}); distância do local à parede: '
    f'{ok.goal_to_wall_cm.min():.0f}–{ok.goal_to_wall_cm.max():.0f} cm (igual nos locais girados, que ficam à mesma distância do centro)')
zs = ok[list(COV)].apply(lambda s: (s - s.mean()) / s.std())
ok[[f'z_{k}' for k in COV]] = zs.values
ok['z_persist'] = (ok.persistence - ok.persistence.mean()) / ok.persistence.std()
mot = []
for k, rot in COV.items():
    m = smf.ols(f'z_persist ~ z_{k} + C(leva)', ok).fit()
    lo, hi = m.conf_int().loc[f'z_{k}']
    rho = stats.spearmanr(ok[k], ok.persistence)[0]
    mot.append(dict(covariavel=rot, beta=m.params[f'z_{k}'], lo=lo, hi=hi, p=m.pvalues[f'z_{k}'], rho=rho))
    say(f'  {rot:42s} β = {m.params[f"z_{k}"]:+.2f} DP [{lo:+.2f}; {hi:+.2f}], p = {m.pvalues[f"z_{k}"]:.2g}; ρ = {rho:+.2f}')
X = zs.values
vif = [variance_inflation_factor(np.column_stack([np.ones(len(X)), X]), i + 1) for i in range(X.shape[1])]
say(f'  VIF no modelo conjunto: ' + ', '.join(f'{COV[k].split(" (")[0]} {v:.2f}' for k, v in zip(COV, vif)))
mj = smf.ols('z_persist ~ ' + ' + '.join(f'z_{k}' for k in COV) + ' + C(leva)', ok).fit()
m0 = smf.ols('z_persist ~ C(leva)', ok).fit()
say(f'  modelo conjunto: R² {mj.rsquared:.2f} contra {m0.rsquared:.2f} só com a leva (parcial {(mj.rsquared - m0.rsquared) / (1 - m0.rsquared):.2f})')
for k in COV:
    say(f'    {COV[k]:42s} β = {mj.params[f"z_{k}"]:+.2f} [{mj.conf_int().loc[f"z_{k}"][0]:+.2f}; {mj.conf_int().loc[f"z_{k}"][1]:+.2f}]')
ok['persist_resid'] = mj.resid
say('  persistência sem a parte motora, com a força da memória:')
for k, rot in (('arrival_latency_s', 'latência'), ('path_efficiency', 'eficiência'), ('quadrante', 'quadrante')):
    say(f'    {rot}: ρ bruto {stats.spearmanr(ok[k], ok.persistence)[0]:+.2f}, ρ do resíduo {stats.spearmanr(ok[k], ok.persist_resid)[0]:+.2f}')
p2 = d[(d.Fase == 'PT2') & d._TargetID.isin(dc._TargetID)].dropna(subset=['persistence'] + list(COV)).copy()
p2[[f'z_{k}' for k in COV]] = ((p2[list(COV)] - ok[list(COV)].mean()) / ok[list(COV)].std()).values
p2['z_persist'] = (p2.persistence - ok.persistence.mean()) / ok.persistence.std()
p2['persist_resid'] = p2.z_persist - mj.predict(p2.assign(leva=p2.leva))
par = ok.set_index('_TargetID')[['persistence', 'persist_resid']].join(
    p2.set_index('_TargetID')[['persistence', 'persist_resid']], rsuffix='_PT2', how='inner')
say(f'  estabilidade PT1 → PT2 nos controles (n = {len(par)}): ρ bruto {stats.spearmanr(par.persistence, par.persistence_PT2)[0]:.2f}, '
    f'ρ do resíduo {stats.spearmanr(par.persist_resid, par.persist_resid_PT2)[0]:.2f}')
pd.DataFrame(mot).to_csv(os.path.join(SAIDA, 'covariaveis_motoras.csv'), index=False)

# ---------------- 5. Figura S3: trajetórias representativas ----------------
CINZA, PRETO, MUDO, TINTA = '#8A8F98', '#111111', '#5B6370', '#18212B'
plt.rcParams.update({'font.family': ['Arial', 'DejaVu Sans'], 'font.size': 9, 'axes.titlesize': 9, 'axes.titleweight': 'bold',
                     'axes.titlelocation': 'left'})
q = ok.persistence
casos = [('Low persistence', ok.iloc[(q - q.quantile(.1)).abs().argsort().iloc[0]]),
         ('Median persistence', ok.iloc[(q - q.median()).abs().argsort().iloc[0]]),
         ('High persistence', ok.iloc[(q - q.quantile(.9)).abs().argsort().iloc[0]]),
         ('Fast crossing', ok[ok.persistence <= q.quantile(.25)].sort_values('arrival_speed').iloc[-1]),
         ('Late arrival (less than 15 s left)', p1[p1.reached & p1.persistence.isna()].sort_values('arrival_latency_s').iloc[0]),
         ('Never reached the location', p1[~p1.reached].iloc[0])]
exp = experimento().set_index('_TrackID')
fig, ax = plt.subplots(3, 2, figsize=(7.2, 10.2), gridspec_kw=dict(hspace=0.35, wspace=0.15))
for a, (rot, c), L in zip(ax.flat, casos, 'ABCDEF'):
    rec = exp.loc[c._TrackID]
    ar = pb.read_rtrack_arena(rec._Arena)
    t, x, y = pb.clean(*pb.read_track(rec._TrackFile), 60)
    i = pb.first_arrival(t, x, y, ar)
    cx, cy = ar.center
    a.add_patch(Circle((0, 0), ar.radius, fill=False, ec=MUDO, lw=0.9))
    a.add_patch(Circle((0, 0), ar.radius * 0.8, fill=False, ec=CINZA, lw=0.5, ls=':'))
    gx, gy = ar.goal[0] - cx, ar.goal[1] - cy
    a.add_patch(Circle((gx, gy), 20, fill=False, ec=CINZA, lw=0.6, ls='--'))
    a.add_patch(Circle((gx, gy), ar.goal_radius, fill=False, ec=TINTA, lw=1))
    if i is None:
        a.plot(x - cx, y - cy, color=CINZA, lw=0.7)
        sub = 'no arrival in 60 s'
    else:
        a.plot(x[:i + 1] - cx, y[:i + 1] - cy, color=CINZA, lw=0.7)
        w = (t >= t[i]) & (t <= t[i] + 15)
        a.plot(x[w] - cx, y[w] - cy, color=PRETO, lw=1.1)
        a.plot(gx, gy, 'o', ms=3, color=PRETO)
        sub = f'arrival {t[i]:.1f} s' + (f'; persistence {c.persistence:.0%}' if pd.notna(c.persistence) else '; partial window')
    a.set_title(f'{L}  {rot}', loc='left')
    a.text(0, -ar.radius * 1.13, sub, ha='center', va='top', color=MUDO, fontsize=8)
    a.set_xlim(-ar.radius * 1.05, ar.radius * 1.05)
    a.set_ylim(-ar.radius * 1.25, ar.radius * 1.05)
    a.set_aspect('equal')
    a.axis('off')
for ext in ('png', 'pdf'):
    fig.savefig(os.path.join(FIG, f'FigS3.{ext}'), dpi=300, bbox_inches='tight', facecolor='white')
say('\n5. Figura S3: ' + '; '.join(f'{r}: {c._TrackID}' for r, c in casos))
out.close()
