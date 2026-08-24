# repo-locate

A portable Agent Skill that delegates cold-start repository localization to FastContext while keeping reasoning, editing, and verification in the outer coding agent.

The same skill directory is designed for Codex, Claude Code, and Antigravity CLI (`agy`).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/janposlusny/repo-locate/blob/main/notebooks/fastcontext_integration_test.ipynb)
[![Open In Kaggle](https://kaggle.com/static/images/open-in-kaggle.svg)](https://www.kaggle.com/notebooks/welcome?src=https://github.com/janposlusny/repo-locate/blob/main/notebooks/kaggle_fastcontext_integration_test.ipynb)

## Install

1. Put this directory somewhere permanent.
2. Run `bash ./install.sh` to symlink it into all three agents.
3. Ensure `fastcontext` is on `PATH` and your local FastContext endpoint variables are configured, or register a FastContext MCP tool in the host agent.

See `references/setup.md` for details.

## Cloud integration test

The notebooks are public, executable tests of the real FastContext CLI/model through the `repo-locate` wrapper. They deliberately use a synthetic repository fixture rather than any private project or competition code. The fixture separates a future-aware valuation kernel, the actual beam-ranking integration point, relevant tests, and plausible decoys across files. The benchmark oracle is stored outside the directory FastContext explores.

### Kaggle — recommended

`notebooks/kaggle_fastcontext_integration_test.ipynb` is the preferred free-GPU path. Enable **Internet** and choose **GPU T4 x2**, then run all cells. It creates isolated Python 3.12 environments for vLLM and FastContext, serves `microsoft/FastContext-1.0-4B-SFT` on one T4, runs three independent localization attempts, and reports how often the final citations recover both required targets.

### Colab

`notebooks/fastcontext_integration_test.ipynb` provides the same benchmark for Colab. Colab GPU availability and its preinstalled Python/CUDA package stack can vary, so Kaggle is the more reproducible fallback when Colab is troublesome.

These notebooks test the FastContext backend and wrapper. Whether a frontier agent autonomously chooses to invoke the skill at the right time is a separate outer-agent policy test.
