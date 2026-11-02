# Rtrack strategy calls for the part of each first probe before the first arrival (written by 07_pre_arrival_strategies.py).
library(Rtrack)
pasta <- commandArgs(trailingOnly = TRUE)[1]
experimento <- read_experiment(file.path(pasta, "experiment.csv"), format = "csv", project.dir = pasta, data.dir = pasta, threads = 1)
estrategias <- call_strategy(experimento$metrics)
export_results(experimento, estrategias, file = file.path(pasta, "rtrack_results.csv"))
cat("Rtrack", as.character(packageVersion("Rtrack")), "-", R.version.string, "\n")
