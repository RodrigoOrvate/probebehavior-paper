"""Figures of the probebehavior article (Fig. 1–4 and S1) from the results in results/abc/ and results/zip_test/."""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import probebehavior as pb
from matplotlib.patches import Circle, Wedge
from scipy import stats

from dados import PROPRIO, TROCADOS, experimento, saida

ABC = saida('results/abc')
AQUI = saida('figures')
AZUL, LARANJA, CINZA, TINTA, MUDO, PRETO = '#1F5FAF', '#B8501C', '#8A8F98', '#18212B', '#5B6370', '#111111'
LEVAS_B = ['E3L1', 'E3L2', 'E5L2', 'E5L3', 'E5L4', 'E7L2', 'E8L1', 'E8L2', 'E8L3', 'E8L4', 'E9L1', 'E9L3', 'E9L5']
rng = np.random.default_rng(7)
plt.rcParams.update({'font.family': ['Arial', 'DejaVu Sans'], 'font.size': 9, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.linewidth': 0.8, 'axes.edgecolor': '#9A9EA6', 'xtick.color': MUDO,
                     'ytick.color': MUDO, 'axes.labelcolor': TINTA, 'axes.titlesize': 9, 'axes.titleweight': 'bold',
                     'axes.titlelocation': 'left', 'legend.frameon': False, 'legend.fontsize': 8})


def letra(ax, s):
    ax.text(-0.16, 1.06, s, transform=ax.transAxes, fontsize=12, fontweight='bold', va='bottom')


def tres(altura=6.4, hspace=0.55, wspace=1.0):
    """Three panels: A and B on top, C centred below (at most two columns)."""
    fig = plt.figure(figsize=(7.2, altura))
    gs = fig.add_gridspec(2, 4, hspace=hspace, wspace=wspace)
    return fig, [fig.add_subplot(gs[0, 0:2]), fig.add_subplot(gs[0, 2:4]), fig.add_subplot(gs[1, 1:3])], gs


def quatro(altura=6.4):
    fig, ax = plt.subplots(2, 2, figsize=(7.2, altura), gridspec_kw=dict(hspace=0.6, wspace=0.45))
    return fig, list(ax.flat)


def salvar(fig, nome):
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(AQUI, f'{nome}.{ext}'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('->', nome)


prov = pd.read_csv(os.path.join(ABC, 'provas.csv'))
trilhas = {}
e = experimento()
for rec in e[e._TrackID.isin(prov._TrackID)].to_dict('records'):
    trilhas[rec['_TrackID']] = (rec['_TrackFile'], rec['_Arena'])
pt1 = prov[prov.leva.isin(LEVAS_B) & (prov.Fase == 'PT1')]
ok = pd.read_csv(os.path.join(ABC, 'B_pt1.csv'))

# curvas alinhadas (PT1, levas B, chegada até 30 s)
curvas = []
for tid in pt1._TrackID:
    f, a = trilhas[tid]
    _, c = pb.measure(*pb.read_track(f), pb.read_rtrack_arena(a))
    if c is not None:
        curvas.append(c)
T = curvas[0]['time_s']
DG = np.vstack([c['distance_to_goal'] for c in curvas])
DW = np.vstack([c['distance_to_wall'] for c in curvas])


def piscina(ax, ar, z=20):
    ax.add_patch(Circle(ar.center, ar.radius, fill=False, ec='#9A9EA6', lw=1))
    ax.add_patch(Wedge(ar.center, ar.radius, 0, 360, width=ar.radius * 0.2, color='#ECEAE2', lw=0))
    ax.add_patch(Circle(ar.goal, z, fill=False, ec=AZUL, lw=0.8, ls='--'))
    ax.add_patch(Circle(ar.goal, ar.goal_radius, color=AZUL, alpha=0.35, lw=0))
    for gx, gy in pb.rotated_goals(ar):
        ax.add_patch(Circle((gx, gy), z, fill=False, ec=CINZA, lw=0.6, ls=':'))
    ax.set(xlim=(-104, 104), ylim=(-104, 104), aspect='equal')
    ax.axis('off')


def trajetoria(ax, tid, titulo):
    f, a = trilhas[tid]
    t, x, y = pb.read_track(f)
    ar = pb.read_rtrack_arena(a)
    m, _ = pb.measure(t, x, y, ar)
    t0 = m['arrival_latency_s']
    piscina(ax, ar)
    for k, cor, lw in [((t <= t0), '#B9BDC4', 0.8), ((t >= t0) & (t <= t0 + 15), AZUL, 1.1), ((t > t0 + 15) & (t <= t0 + 30), '#9DB8DE', 0.8)]:
        ax.plot(np.where(k, x, np.nan), np.where(k, y, np.nan), color=cor, lw=lw)
    i0 = np.argmax(t >= t0)
    ax.plot(x[0], y[0], 'o', ms=4, color=TINTA)
    ax.plot(x[i0], y[i0], '*', ms=9, color=LARANJA, mec='white', mew=0.5)
    ax.set_title(f'{titulo} ({m["persistence"]:.2f})', fontsize=8, fontweight='normal')


# ---------------- Figure 1: the method ----------------
fig = plt.figure(figsize=(7.2, 6.6))
gs = fig.add_gridspec(2, 4, hspace=0.3, wspace=0.4, height_ratios=[1, 1])
ax = fig.add_subplot(gs[0, 0:2])
ar = pb.Arena((0, 0), 100, (42, 38), 6)
piscina(ax, ar)
ax.annotate('platform location\n(12 cm diameter)', ar.goal, (50, 96), fontsize=7, color=AZUL,
            arrowprops=dict(arrowstyle='-', color=AZUL, lw=0.5))
ax.annotate('zone, 20 cm radius', (42, 18), (18, -12), fontsize=7, color=AZUL, arrowprops=dict(arrowstyle='-', color=AZUL, lw=0.5))
ax.text(-104, 104, 'pool, 200 cm diameter', fontsize=7, color=MUDO, ha='left', va='bottom')
ax.annotate('wall band (outer 20%)', (-70, -72), (-104, -118), fontsize=7, color=MUDO, annotation_clip=False,
            arrowprops=dict(arrowstyle='-', color=MUDO, lw=0.5))
ax.annotate('rotated locations', (-42, 18), (-60, -8), fontsize=7, color=MUDO, ha='center',
            arrowprops=dict(arrowstyle='-', color=MUDO, lw=0.5))
letra(ax, 'A')
ax2 = fig.add_subplot(gs[0, 2:4])
ax2.axis('off')
ax2.add_patch(plt.Rectangle((0, 0.45), 0.35, 0.1, color='#B9BDC4'))
ax2.add_patch(plt.Rectangle((0.35, 0.45), 0.3, 0.1, color=AZUL))
ax2.add_patch(plt.Rectangle((0.65, 0.45), 0.3, 0.1, color='#9DB8DE'))
ax2.plot(0.35, 0.5, '*', ms=11, color=LARANJA, mec='white', mew=0.5)
for xx, s in [(0.17, 'search for\nthe platform'), (0.5, 'first 15 s'), (0.8, '15–30 s')]:
    ax2.text(xx, 0.68, s, ha='center', fontsize=7, color=TINTA)
ax2.text(0.35, 0.28, 'first arrival at\nthe empty goal', ha='center', fontsize=7, color=LARANJA)
ax2.set(xlim=(0, 1), ylim=(0, 1))
letra(ax2, 'B')
sel = ok[(ok.arrival_latency_s > 4) & (ok.arrival_latency_s < 15)]
alto = sel.iloc[(sel.persistence - sel.persistence.quantile(0.9)).abs().argsort()[:1]]._TrackID.iloc[0]
baixo = sel.iloc[(sel.persistence - sel.persistence.quantile(0.1)).abs().argsort()[:1]]._TrackID.iloc[0]
sub = gs[1, 0:4].subgridspec(1, 2, wspace=0.05)
a3 = fig.add_subplot(sub[0])
trajetoria(a3, alto, 'High persistence')
letra(a3, 'C')
a4 = fig.add_subplot(sub[1])
trajetoria(a4, baixo, 'Low persistence')
salvar(fig, 'Fig1')

# ---------------- Figure 2: what rats do after not finding the platform ----------------
fig, ax, _ = tres()
for arr, cor, nome in [(DG, AZUL, 'distance to goal'), (DW, LARANJA, 'distance to wall')]:
    ax[0].fill_between(T, np.nanpercentile(arr, 25, 0), np.nanpercentile(arr, 75, 0), color=cor, alpha=0.15, lw=0)
    ax[0].plot(T, np.nanmedian(arr, 0), color=cor, lw=1.5, label=nome)
ax[0].axvline(0, color=MUDO, lw=0.6, ls=':')
ax[0].set(xlabel='time from first arrival (s)', ylabel='cm', title=f'Aligned on arrival (n = {len(DG)})')
ax[0].legend(loc='upper right')
letra(ax[0], 'A')
pares = np.column_stack([ok.persist_girados, ok.persistence]) * 100
for p in pares:
    ax[1].plot([0, 1], p, color=CINZA, lw=0.3, alpha=0.4)
ax[1].boxplot(pares, positions=[0, 1], widths=0.35, showfliers=False, medianprops=dict(color=TINTA, lw=1.5),
              boxprops=dict(color=TINTA, lw=0.8), whiskerprops=dict(color=TINTA, lw=0.8), capprops=dict(color=TINTA, lw=0.8))
ax[1].set_xticks([0, 1], ['rotated\nlocations', 'goal'])
ax[1].set(ylabel='% of next 15 s within 20 cm', title=f'Local search (n = {len(ok)})')
letra(ax[1], 'B')
bins = np.arange(0, 31, 1.0)
ax[2].hist(ok.first_stay_s.clip(upper=30), bins=bins, histtype='step', lw=1.4, color=AZUL, label='first stay in 20-cm zone')
ax[2].hist(ok.wall_latency_s.dropna(), bins=bins, histtype='step', lw=1.4, color=LARANJA, label='time to wall band')
ax[2].set(xlabel='seconds after arrival', ylabel='rats', title='Leaving the goal')
ax[2].legend(loc='center right', fontsize=7)
letra(ax[2], 'C')
salvar(fig, 'Fig2')

# ---------------- Figure 3: structure and individuality ----------------
POS = ['persistence', 'reentries', 'first_stay_s', 'mean_distance', 'speed', 'turning_deg_s', 'wall_latency_s', 'other_locations_visits']
ROT = ['persistence', 're-entries', 'first stay', 'mean distance', 'speed', 'turning', 'time to wall', 'other locations']
z = ok[POS].dropna()
val = np.linalg.eigvalsh(np.corrcoef(((z - z.mean()) / z.std()).T.values))[::-1]
fig, ax = quatro(altura=6.6)
ordem_m = [0, 1, 2, 5, 6, 3, 4, 7]  # staying measures first, then the exploring ones
cm = z.iloc[:, ordem_m].corr('spearman').values
im = ax[0].imshow(cm, cmap='RdBu_r', vmin=-1, vmax=1)
cb = fig.colorbar(im, ax=ax[0], fraction=0.046, pad=0.04, ticks=[-1, 0, 1])
cb.ax.tick_params(labelsize=6)
ax[0].set_xticks(range(8), [ROT[i] for i in ordem_m], rotation=90, fontsize=6)
ax[0].set_yticks(range(8), [ROT[i] for i in ordem_m], fontsize=6)
ax[0].spines[:].set_visible(False)
ax[0].set_title(f'Staying vs exploring\n(PC1 {val[0] / val.sum():.0%}, PC2 {val[1] / val.sum():.0%})', fontsize=8)
letra(ax[0], 'A')
ordem = ok.groupby('leva').persistence.median().sort_values().index
for i, l in enumerate(ordem):
    s = ok[ok.leva == l].persistence * 100
    ax[1].plot(np.full(len(s), i) + rng.uniform(-0.18, 0.18, len(s)), s, 'o', ms=2, color=PRETO, alpha=0.35, mew=0)
    ax[1].plot([i - 0.32, i + 0.32], [s.median()] * 2, color=PRETO, lw=2.2, solid_capstyle='butt')
ax[1].set_xticks(range(len(ordem)), ordem, rotation=90, fontsize=6)
ax[1].set(ylabel='persistence (%)', title='Across cohorts')
letra(ax[1], 'B')
rho = stats.spearmanr(ok.arrival_latency_s, ok.persistence)[0]
ax[2].plot(ok.arrival_latency_s, ok.persistence * 100, 'o', ms=2.5, color=PRETO, alpha=0.45, mew=0)
ax[2].set(xlabel='latency to goal (s)', ylabel='persistence (%)', title='Memory strength')
ax[2].text(0.97, 0.95, f'ρ = {rho:+.2f}', transform=ax[2].transAxes, ha='right', va='top', fontsize=8)
letra(ax[2], 'C')
c = pd.read_csv(os.path.join(ABC, 'C_pt1_pt2.csv'))
c = c[c.Grupo.isin(['VEH', 'SCZIP', 'MSO'])].dropna(subset=['persistence_PT1', 'persistence_PT2'])
rr = stats.spearmanr(c.persistence_PT1, c.persistence_PT2)
ax[3].plot(c.persistence_PT1 * 100, c.persistence_PT2 * 100, 'o', ms=2.5, color=PRETO, alpha=0.55, mew=0)
ax[3].set(xlabel='PT1 persistence (%)', ylabel='PT2 persistence (%)', title='Same rat, controls')
ax[3].text(0.97, 0.95, f'ρ = {rr[0]:+.2f}\nn = {len(c)}', transform=ax[3].transAxes, ha='right', va='top', fontsize=8)
letra(ax[3], 'D')
salvar(fig, 'Fig3')

# ---------------- Figure 4: what it adds ----------------
CONTRASTES = [('ZIP vs controls', {'ZIP'}, {'VEH', 'SCZIP'}, ['E9L3', 'E9L5', 'E3L1', 'E3L2', 'E5L3', 'E5L4', 'E8L1'], True),
              ('ASO vs MSO', {'ASO'}, {'MSO'}, ['E8L3'], True), ('PEP vs VEH', {'PEP'}, {'VEH'}, ['E5L2', 'E5L3', 'E8L4'], True),
              ('ICAP vs VEH', {'ICAP'}, {'VEH'}, ['E5L2'], False), ('LAC+ZIP vs LAC', {'LAC+ZIP'}, {'LAC'}, ['E8L1'], False),
              ('DYN+ZIP vs DYN', {'DYN+ZIP'}, {'DYN'}, ['E5L3', 'E5L4'], False), ('ZIP, PT2 at 3 h', {'ZIP'}, {'VEH'}, ['E7L2'], False),
              ('ZIP 6 h after PT1', {'ZIP'}, {'VEH'}, ['E9L1'], False)]
# the figure shows the amnesic contrasts and three measures; every contrast and measure is in the supplementary table
MED = [('quadrante', -1, 'quadrant', CINZA, 'o'), ('gallagher', +1, 'proximity', CINZA, 's'), ('persistence_pw', -1, 'persistence', AZUL, 'o')]
AMN = [c for c in CONTRASTES if c[4]]
base = prov[~prov._TargetID.isin(TROCADOS | PROPRIO) & (prov.Fase == 'PT2')].copy()
base['persistence_pw'] = base.persistence_pw.fillna(0)


def g_ols(y, trat, leva):
    X = np.column_stack([np.ones_like(y), trat] + [(leva == l).astype(float) for l in np.unique(leva)[1:]])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ b
    return b[1] / np.sqrt(r @ r / (len(y) - X.shape[1]))


fig, ax, _ = tres(altura=7.0, hspace=0.75, wspace=2.2)
for i, (nome, trat, ctl, levas, amn) in enumerate(AMN):
    s = base[base.leva.isin(levas) & base.Grupo.isin(trat | ctl)]
    tr, lv = s.Grupo.isin(trat).astype(float).values, s.leva.values
    grupos = [np.flatnonzero((lv == l) & (tr == k)) for l in np.unique(lv) for k in (0, 1)]
    grupos = [gg for gg in grupos if len(gg)]
    for j, (col, sinal, rot, cor, mk) in enumerate(MED):
        y = sinal * s[col].values
        g = g_ols(y, tr, lv)
        bs = [g_ols(y[ix], tr[ix], lv[ix]) for ix in (np.concatenate([rng.choice(gg, len(gg)) for gg in grupos]) for _ in range(1000))]
        yy = i + (j - 1) * 0.22
        ic = np.percentile(bs, [2.5, 97.5])
        topo = max(topo, ic[1]) if i or j else ic[1]
        ax[0].plot(ic, [yy, yy], color=cor, lw=1)
        ax[0].plot(g, yy, mk, ms=5, color=cor, mfc='white' if cor == CINZA else cor, label=rot if i == 0 else None)
ax[0].axvline(0, color=MUDO, lw=0.6, ls=':')
ax[0].set_yticks(range(len(AMN)), [f'{c[0]}\n({int(sum(1 for _ in c[3]))} cohort{"s" if len(c[3]) > 1 else ""})' for c in AMN], fontsize=7)
ax[0].set_ylim(len(AMN) - 0.5, -0.5)
ax[0].set(xlabel='standardised effect d (positive = worse memory)', title='Sensitivity at PT2', xlim=(-1.5, np.ceil(topo + 0.3)))
ax[0].legend(loc='upper left', fontsize=6.5, ncol=3, bbox_to_anchor=(-0.05, -0.22), handletextpad=0.2, columnspacing=0.8)
letra(ax[0], 'A')
q = pd.read_csv(os.path.join(saida('results/zip_test'), 'principais.csv'))
rot = {'Q1': 'Q1 primary', 'Q2': 'Q2 re-entries', 'Q3': 'Q3 + latency', 'Q4': 'Q4 no PT1 quadrant'}
for i, r_ in q.iterrows():
    ax[1].plot([r_.ic_inf, r_.ic_sup], [i, i], color=LARANJA, lw=1)
    ax[1].plot(r_.estimativa, i, 'o', ms=4.5, color=LARANJA)
    ax[1].text(8, i, f'p = {r_.p_perm:.2g}', fontsize=6.5, va='center', color=MUDO)
ax[1].axvline(0, color=MUDO, lw=0.6, ls=':')
ax[1].set_yticks(range(len(q)), [rot[a] for a in q.analise], fontsize=7)
ax[1].invert_yaxis()
ax[1].set(xlabel='ZIP × measure on PT2 quadrant\n(pp per unit; persistence per 0.1)', title='Preregistered ZIP test', xlim=(-20, 14))
letra(ax[1], 'B')
dsc = pd.read_csv(os.path.join(ABC, 'dissociacao_controles.csv'))
zf = lambda v, ref: (v - ref.mean()) / ref.std()
dsc['d_in'] = zf(dsc.persistence_PT2, dsc.persistence_PT1) - zf(dsc.persistence_PT1, dsc.persistence_PT1)
i1, i2 = -np.log(dsc.arrival_latency_s_PT1), -np.log(dsc.arrival_latency_s_PT2)
dsc['d_ida'] = zf(i2, i1) - zf(i1, i1)
med = dsc.persistence_PT1.median()
for k, (nome, s) in enumerate([('low PT1\npersistence', dsc[dsc.persistence_PT1 <= med]), ('high PT1\npersistence', dsc[dsc.persistence_PT1 > med])]):
    for dx, col, cor, rot_ in [(-0.15, 'd_ida', CINZA, 'going to goal'), (0.15, 'd_in', AZUL, 'persistence')]:
        b = [np.median(rng.choice(s[col].values, len(s))) for _ in range(2000)]
        ax[2].plot([k + dx] * 2, np.percentile(b, [2.5, 97.5]), color=cor, lw=1)
        ax[2].plot(k + dx, s[col].median(), 'o', ms=5, color=cor, label=rot_ if k == 0 else None)
ax[2].axhline(0, color=MUDO, lw=0.6, ls=':')
ax[2].set_xticks([0, 1], ['low', 'high'], fontsize=7)
ax[2].set(xlim=(-0.6, 1.6), xlabel='PT1 persistence (half)', ylabel='PT2 − PT1 (SD)', title='Second violation, controls')
ax[2].legend(loc='upper right', fontsize=6.5)
letra(ax[2], 'C')
salvar(fig, 'Fig4')

# ---------------- Figure S1: robustness ----------------
rb = pd.read_csv(os.path.join(ABC, 'robustez_parametros.csv'))
PAINEIS = [('persist_local', 'persistence at goal'), ('rho_latencia', 'ρ with latency'), ('rho_pt1_pt2', 'ρ PT1 × PT2 (controls)'),
           ('sens_dif_g', 'g(persistence) − g(quadrant)'), ('q1_est_por_0_1', 'Q1 estimate (pp per 0.1)'), ('D_mediana', 'second-violation D')]
fig, ax = plt.subplots(3, 2, figsize=(5.6, 7.4), gridspec_kw=dict(wspace=0.55, hspace=0.75))
# fixed scales, centred on zero where the sign matters, so the colour never exaggerates small differences
ESCALA = {'persist_local': ('Blues', 0, 0.25), 'rho_latencia': ('RdBu_r', -0.6, 0.6), 'rho_pt1_pt2': ('RdBu_r', -0.6, 0.6),
          'sens_dif_g': ('RdBu_r', -0.5, 0.5), 'q1_est_por_0_1': ('RdBu_r', -12, 12), 'D_mediana': ('RdBu_r', -0.5, 0.5)}
pq = rb.pivot(index='zona_cm', columns='janela_s', values='q1_p').values
for a, (col, tit) in zip(ax.flat, PAINEIS):
    mtx = rb.pivot(index='zona_cm', columns='janela_s', values=col)
    cmap, lo, hi = ESCALA[col]
    im = a.imshow(mtx.values, cmap=cmap, vmin=lo, vmax=hi)
    for (i, j), vv in np.ndenumerate(mtx.values):
        txt = f'{vv:.1f}\np = {pq[i, j]:.2f}' if col == 'q1_est_por_0_1' else f'{vv:.2f}'
        n_ = im.norm(vv)
        a.text(j, i, txt, ha='center', va='center', fontsize=6.5,
               color='white' if n_ > 0.8 or (cmap != 'Blues' and n_ < 0.2) else TINTA)
    a.set_xticks(range(3), [f'{int(x)} s' for x in mtx.columns])
    a.set_yticks(range(3), [f'{int(x)} cm' for x in mtx.index])
    a.set(xlabel='window', ylabel='zone radius', title=tit)
    a.spines[:].set_visible(False)
salvar(fig, 'FigS1')
