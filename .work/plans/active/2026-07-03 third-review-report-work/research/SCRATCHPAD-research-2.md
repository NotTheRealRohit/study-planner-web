# Scratchpad — third-review-report-work / research (stage 2: evolution trace)
_Plan: (no PLAN.md — pure documentation-gathering task, ceremony=normal) · Log: this file doubles as log until work-journal wrap · Updated: 2026-07-03T16:45 (TASK COMPLETE — handing off to work-journal)_

## Now
**Task complete.** `research/04-application-evolution-trace.md` written and cross-verified:
7 parallel era agents (era 0-6, 2026-05-01 → 07-02, 304 commits) each independently walked
`git log --stat`/`git show` for their exact SHA range, cross-referenced the matching
`.work/plans/` folder(s), and flagged (rather than assumed) whether their era's work was
still true at current HEAD per docs 01-03. Two cross-era ambiguities the agents themselves
flagged were resolved by direct orchestrator verification (not left as open flags in the
final doc) — see doc 04 §9. A short coda covers 2026-07-03's uncommitted state (this task +
UI-bugs Phases 6-8 spec'd-not-built).

## Alignment
Complete, on scope. All three parts of the user's ask are covered: (1) read the three
stage-1 docs first, (2) traced git-log evolution since **2026-05-01** (the user's literal
date, corrected from the prior session's relative "30 days ago" recon — see Resolved), (3)
used parallel agents + `/scratchpad` + (now) `/work-journal`. No false/stale info was
knowingly left in the doc — every claim traces to a cited commit SHA, and claims that
conflicted with docs 01-03 were resolved with fresh verification, not silently kept.

## Open
- Whether the dissertation report wants this as a dedicated "development process" chapter
  or folded into system-architecture — not this stage's call; flagged in doc 04's frontmatter
  scope line for the next drafting session to decide.

## Blockers
— none.

## Deferrals
— none. (This task was pure documentation, no code touched — matches stage 1's precedent.)

## Checklist
- [x] Read prior stage's 3 docs (01-03) + reconciled scratchpads for context
- [x] Corrected recon to the user's literal `--since=2026-05-01` boundary (was `--since="30
      days ago"` in the interrupted prior session — see Resolved)
- [x] Defined 7 chronological eras (0-6) with exact non-overlapping SHA ranges
- [x] Spawned 7 parallel general-purpose agents, one per era, each independently
      git-show-verified (not just trusting commit subject lines) and cross-checked against
      docs 01-03
- [x] Orchestrator direct-verification pass on 2 cross-era ambiguities the agents flagged:
      `videoPlayTimeMinutes` wiring history (confirmed dead in every era, not a regression)
      and `enriched_shrink`'s `ridge=2.0/shrink=6.0` provenance (validated for the dual-prior
      ensemble in era 4, not blindly inherited from era 3's differently-tuned standalone
      result — both era's numbers are correct, for two different model configurations)
- [x] Synthesized into `research/04-application-evolution-trace.md` (10 sections: overview
      table, 7 era sections, cross-era resolutions, 2026-07-03 coda)
- [x] Scratchpad reconciliation pass (this edit)
- [ ] work-journal wrap (STATUS.md row update) — next, immediately after this

## In-flight edits
— none outstanding. `research/04-application-evolution-trace.md` is written and complete;
this scratchpad is the only other file touched this stage. No code files were modified.

## Decisions in force
- Doc 04 lives alongside docs 01-03 in the same `research/` folder, continuing the numbering
  sequence — confirmed correct call (this is a direct sequel to stage 1, same STATUS.md row,
  same dissertation deliverable).
- Era boundaries used exact commit SHA ranges (not just dates) to guarantee the 7 agents'
  coverage was contiguous and non-overlapping — verified by summing commit counts
  (37+16+58+46+42+57+48=304) against `git log --since=2026-05-01 --until="2026-07-03
  23:59" --oneline | wc -l` = 304, exact match.
- Each era agent's raw findings were lightly edited for consistency/length in the final doc
  but no factual claim was altered from what the agent verified — the orchestrator's only
  additions were §9 (cross-era resolutions) and the frontmatter/overview table.

## Resolved (recent)
- **The prior (interrupted) session's era-boundary recon was corrected.** It had run
  `git log --since="30 days ago"` (relative to 2026-07-03) and planned only 6 eras starting
  2026-06-06 — silently excluding the 37 commits from 2026-05-01 to 2026-05-09 (the actual
  progress/calibration-engine genesis, pre-dating any Python code). Fixed this session by
  re-running recon anchored to the user's literal stated date and adding Era 0. **Lesson,
  now also recorded in doc 04 itself implicitly via its explicit date range**: always recon
  with the user's literal stated boundary, never a relative approximation, before defining
  eras for a historical trace.
- **Two cross-era ambiguities the agents flagged were resolved, not left open** — see
  Checklist and doc 04 §9. Both were genuine "does this still hold" questions (not agent
  errors); both resolved cleanly with a git-log/git-show check that took under 5 minutes.
- Stage 1 (docs 01-03) reconciliation — unchanged, see SCRATCHPAD-research-1.md, not
  re-litigated here.
