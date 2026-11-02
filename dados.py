"""Carga comum dos scripts: o conjunto de dados do Zenodo (pasta dataset/, ou a indicada em PROBE_DATA) e as medidas
clássicas calculadas pelo probebehavior."""
import os

import pandas as pd
import probebehavior as pb

RAIZ = os.path.dirname(os.path.abspath(__file__))
DADOS = os.environ.get('PROBE_DATA', os.path.join(RAIZ, 'dataset'))


def saida(nome):
    p = os.path.join(RAIZ, nome)
    os.makedirs(p, exist_ok=True)
    return p


def experimento():
    """Uma linha por teste, na ordem do conjunto de dados (as permutações e os bootstraps dependem dela)."""
    e = pb.read_rtrack_experiment(os.path.join(DADOS, 'data', 'experiment.csv'))
    return e.rename(columns={'cohort': 'Experimento', 'group': 'Grupo', 'session': 'Fase'})


def _ratos(motivo):
    e = experimento()
    return set(e._TargetID[e.exclusion.fillna('').str.contains(motivo)])


TROCADOS = _ratos('tracked from another rat')
PROPRIO = _ratos('prespecified exclusion criterion')
TESE = _ratos('excluded in the thesis')


def classicas(e):
    """Quadrante-alvo (%), proximidade de Gallagher (cm) e cruzamentos no teste inteiro, por _TrackID."""
    linhas = {}
    for rec in e.to_dict('records'):
        c = pb.classic_measures(*pb.read_track(rec['_TrackFile']), pb.read_rtrack_arena(rec['_Arena']))
        linhas[rec['_TrackID']] = (c['quadrant_pct'], c['proximity'], c['crossings'])
    return pd.DataFrame.from_dict(linhas, orient='index', columns=['quadrante', 'gallagher', 'cruzamentos'])
