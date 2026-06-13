UV_RUN ?= uv run --package research-comparison
.PHONY: dataset compare compare-detection compare-projection compare-scheduling sweep closed-loop kt figs figs-calibration figs-detection figs-projection figs-scheduling figs-robustness all
dataset: ; $(UV_RUN) python -m research_comparison.generator.generate
compare: ; $(UV_RUN) python -m research_comparison.runners.calibration
compare-detection: ; $(UV_RUN) python -m research_comparison.runners.detection
compare-projection: ; $(UV_RUN) python -m research_comparison.runners.projection
compare-scheduling: ; $(UV_RUN) python -m research_comparison.runners.scheduling
sweep: ; $(UV_RUN) python -m research_comparison.runners.sweep
closed-loop: ; $(UV_RUN) python -m research_comparison.runners.closed_loop --closed-loop
figs-calibration: compare
	$(UV_RUN) python -m research_comparison.plots.convergence
figs-detection: compare-detection
	$(UV_RUN) python -m research_comparison.plots.detection_latency
figs-projection: compare-projection
	$(UV_RUN) python -m research_comparison.plots.projection_reliability
figs-scheduling: compare-scheduling
	$(UV_RUN) python -m research_comparison.plots.scheduling_metrics
figs-robustness: sweep
	$(UV_RUN) python -m research_comparison.plots.robustness_heatmap
figs: figs-calibration figs-detection figs-projection figs-scheduling figs-robustness
kt:      ; @echo "KT bench runs in research/kt-bench (see plan part 3)"
all: dataset compare compare-detection compare-projection compare-scheduling sweep figs
