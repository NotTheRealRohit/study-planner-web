UV_RUN ?= uv run --package research-comparison
.PHONY: dataset compare compare-detection compare-projection compare-scheduling kt figs figs-calibration figs-detection figs-projection figs-scheduling all
dataset: ; $(UV_RUN) python -m research_comparison.generator.generate
compare: ; $(UV_RUN) python -m research_comparison.runners.calibration
compare-detection: ; $(UV_RUN) python -m research_comparison.runners.detection
compare-projection: ; $(UV_RUN) python -m research_comparison.runners.projection
compare-scheduling: ; $(UV_RUN) python -m research_comparison.runners.scheduling
figs-calibration: compare
	$(UV_RUN) python -m research_comparison.plots.convergence
figs-detection: compare-detection
	$(UV_RUN) python -m research_comparison.plots.detection_latency
figs-projection: compare-projection
	$(UV_RUN) python -m research_comparison.plots.projection_reliability
figs-scheduling: compare-scheduling
	$(UV_RUN) python -m research_comparison.plots.scheduling_metrics
figs: figs-calibration figs-detection figs-projection figs-scheduling
kt:      ; @echo "KT bench runs in research/kt-bench (see plan part 3)"
all: dataset compare compare-detection compare-projection compare-scheduling figs
