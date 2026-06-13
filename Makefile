UV_RUN ?= uv run --package research-comparison
.PHONY: dataset compare compare-detection kt figs figs-calibration figs-detection all
dataset: ; $(UV_RUN) python -m research_comparison.generator.generate
compare: ; $(UV_RUN) python -m research_comparison.runners.calibration
compare-detection: ; $(UV_RUN) python -m research_comparison.runners.detection
figs-calibration: compare
	$(UV_RUN) python -m research_comparison.plots.convergence
figs-detection: compare-detection
	$(UV_RUN) python -m research_comparison.plots.detection_latency
figs: figs-calibration figs-detection
kt:      ; @echo "KT bench runs in research/kt-bench (see plan part 3)"
all: dataset compare compare-detection figs
