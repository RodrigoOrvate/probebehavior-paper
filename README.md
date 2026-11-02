# probebehavior-paper

Analysis code for the article *What rats do when the platform is not there: water maze probe tests aligned on the first
arrival at the empty goal* (Orvate et al., in preparation). It reproduces every analysis, figure and supplementary
table of the article from the archived data.

| | |
|---|---|
| Measures | Python package [probebehavior](https://github.com/RodrigoOrvate/probebehavior) 0.1.0, [doi:10.5281/zenodo.23888805](https://doi.org/10.5281/zenodo.23888805) |
| Data | 554 probe-test trajectories of 278 rats, Zenodo, [doi:10.5281/zenodo.23898439](https://doi.org/10.5281/zenodo.23898439) (CC BY 4.0) |
| Code | this repository (MIT) |

## Reproducing the article

1. Python 3.13 (tested with 3.13.2). Install the exact versions used:

   ```
   pip install -r requirements.txt
   ```

2. Download the dataset from [Zenodo](https://doi.org/10.5281/zenodo.23898439) (`watermaze_probe_dataset.zip`) and
   unzip it into `dataset/`, so that `dataset/data/experiment.csv` exists (or set the environment variable `PROBE_DATA`
   to the unzipped folder).

3. Run everything, in order:

   ```
   python run_all.py
   ```

   Results go to `results/` and figures to `figures/`.

Random seeds are fixed in each script, so the permutation and bootstrap results are the same on every run.

## What each script produces

| Script | Analysis | In the article |
|---|---|---|
| `01_sensitivity_description_second_probe.py` | sensitivity of each measure to the drugs (A); description of the first probe (B); first versus second probe in controls (C) | Results; Fig. 4A; Table S3 |
| `02_zip_test.py` | prespecified ZIP test (Q1–Q4) and its sensitivity analyses | Results; Fig. 4B |
| `03_second_probe_dissociation.py` | second-session dissociation between persistence and latency (exploratory) | Results; Fig. 4C |
| `04_robustness.py` | 3 × 3 grid of zone radius and time window | Fig. S1 |
| `05_review_analyses.py` | sample flow, sensitivity without zeros, regression to the mean, kinematic covariates, principal-component loadings (exploratory) | Results; Tables S4, S6 and S7; Fig. S3 |
| `06_figures.py` | figures from the results above | Figs 1–4, S1 and S2 |
| `dados.py` | reads the dataset and computes the classic measures with `probebehavior.classic_measures` | — |

Comments, variable names and printed output are in Portuguese, the language in which the analyses were written.

## Analysis plans

`plans/` holds the analysis plans, byte-identical to the versions whose SHA-256 hashes were recorded before each
analysis was run (Analysis plans and Table S5 in the article). Check them with `sha256sum plans/*.md`.

| Plan | File | SHA-256 (first 8) |
|---|---|---|
| Exclusion criterion | `PREREGISTRO_exclusao_e_rtrack_teste.md` | acd74e7a |
| Pilot (experiments 5, 7, 8) | `PILOTO_quebra_expectativa.md` | 197a84f5 |
| Stability in controls | `PILOTO_quebra_expectativa_ADENDO.md` | f09d84d9 |
| ZIP test, version 1 (replaced before running) | `PREREGISTRO_quebra_expectativa.md` | 25599c57 |
| ZIP test, version 2 | `PREREGISTRO_quebra_expectativa_v2.md` | f3d5a349 |
| Sensitivity, description, second session | `PLANO_sensibilidade_descricao_segunda_quebra.md` | 9fad5a40 |
| Second-session dissociation | `PLANO_dissociacao_segunda_quebra.md` | 196622eb |
| Robustness | `PLANO_robustez_parametros.md` | ef0f797e |

The plans are in Portuguese. They were kept in a private version-controlled repository and were not registered on a
public platform.

## License

Code: MIT (see `LICENSE`). Data: CC BY 4.0, stated in the Zenodo dataset.
