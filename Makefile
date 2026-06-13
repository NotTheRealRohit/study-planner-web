UV_RUN ?= uv run --package research-comparison
.PHONY: dataset compare kt figs all
dataset: ; $(UV_RUN) python -m research_comparison.generator.generate
compare: ; $(UV_RUN) python -m research_comparison.runners.calibration
figs:    ; $(UV_RUN) python -m research_comparison.plots.convergence
kt:      ; @echo "KT bench runs in research/kt-bench (see plan part 3)"
all: dataset compare figs
