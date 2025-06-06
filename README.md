# MT3_Classifier

This repository contains a modular implementation of the 3-plane CNN + Transformer
pipeline for embryonic CT analysis. The code is organised into reusable modules
for pretraining, finetuning and saliency map generation.

## Directory Overview

- `models/` – network architectures shared across tasks
- `data/` – data transforms and dataset wrappers
- `training/` – routines for pretraining and finetuning
- `saliency/` – utilities for generating saliency maps with Captum
- `scripts/` – entry points that load a YAML config and launch a job
- `configs/` – example configuration files
- `checkpoints/` – default location for saved models

## Usage

The project is configured through YAML files located in `configs/`. Each script
expects a path to one of these files.

### Self-supervised pretraining

```bash
python scripts/pretrain.py configs/pretrain.yaml
```

Edit `configs/pretrain.yaml` so that `data_list` points to your list of
training volumes. The script writes checkpoints to
`checkpoints/ssl_runs/<run_id>` and logs metrics via Weights & Biases. The final
encoder weights can then be used for supervised finetuning.

### Finetuning

Finetuning configs are generated for each classification task. The file
`configs/finetune.yaml` is a generic template without any dataset
information or Weights & Biases project. First create a task specific
config with `scripts/generate_configs.py` (see below) and then run:

```bash
python scripts/finetune.py configs/edema_finetune.yaml  # replace with your task
```

The generated YAML contains the dataset lists and can optionally reference a
self-supervised checkpoint through the `ssl_ckpt` field. Learning rates follow a
cosine schedule with optional linear warmup controlled by `warmup_epochs`.

### Generating finetuning configs

The script `scripts/generate_configs.py` can create a finetuning YAML file
directly from a CSV table of sample labels. It scans a directory of NRRD files,
splits the dataset with a **stratified** shuffle to preserve class ratios and
computes intensity statistics.

```bash
python scripts/generate_configs.py \
    --task edema \  # replace with your task
    --project MyWandBProject \
    --csv path/to/labels.csv \
    --data-dir /path/to/nrrd \
    --ssl-ckpt ssl_runs/<run_id>/ssl_backbone_final.pth \
    --output configs/edema_finetune.yaml
```

`--ssl-ckpt` should point to the pretraining checkpoint relative to
`checkpoints/`. The resulting YAML contains the dataset lists, intensity
statistics, the selected `task` and the `project` name. If `--project` is
omitted, a default name of the form `Embryo_<task>_Classification` is
used. The config can then be supplied to `scripts/finetune.py`.

### Saliency map generation

```bash
python scripts/saliency.py configs/saliency.yaml
```

Specify the classifier checkpoint via `ckpt` and the dataset list via
`data_list`. Saliency maps will be written as NumPy arrays to the directory
given in `out_dir`.

### Checkpoints

All training jobs write their outputs inside `checkpoints/`. Pretraining runs
create a subfolder `ssl_runs/<run_id>` while finetuning creates
`runs/<run_id>`. Configuration files may specify checkpoints relative to this
directory via the `ckpt_dir` field.
