UV ?= uv run --package research-comparison
.PHONY: dataset compare kt figs all
dataset: ; $(UV) python -m research_comparison.generator.generate
compare: ; $(UV) python -m research_comparison.runners.calibration --stub
figs:    ; $(UV) python -m research_comparison.plots.convergence --stub
kt:      ; @echo "KT bench runs in research/kt-bench (see plan part 3)"
all: dataset compare figs
