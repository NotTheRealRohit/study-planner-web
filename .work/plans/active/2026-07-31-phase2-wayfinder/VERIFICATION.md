# VERIFICATION — 2026-07-31-phase2-wayfinder

Running log for the Phase 2 wayfinder chart. Canonical artifact is the GitHub map ([#9](https://github.com/NotTheRealRohit/study-planner-web/issues/9)); this log tracks charting progress.

## Status

| Item | State |
|---|---|
| Map created (#9) | ✅ done |
| Frontier tickets #10–#17 | ✅ created (8) |
| Blocked tickets #18–#21 | ✅ created (4), wired |
| Research: open-notebook | ✅ `research/external/open-notebook-findings.md` |
| Research: code sandbox (#16) | ✅ resolved + closed — Judge0 CE |
| Execution order (waves) | ✅ set 2026-07-31 — see PLAN.md "Execution order" |
| Decision tickets #10–#15, #17–#21 | ☐ open (one per future session) |
| #10 App IA & navigation | ✅ resolved + closed 2026-07-31 |

## Log

- **2026-07-31** Charted the Phase 2 wayfinder map on GitHub Issues (repo `NotTheRealRohit/study-planner-web`). Named destination via grilling = **spec + working prototypes**; established the **capstone / feature-rich / no-deferrals** standing principle. Locked 7 design decisions (guidance style, trigger, inline-hint surface, full-RAG grounding, full KT coupling, hybrid code execution, out-of-scope fence). Created wayfinder labels, map **#9**, 8 frontier tickets **#10–#17**, 4 blocked tickets **#18–#21** (blocking via `Blocked by:` body refs). Fired two research subagents: open-notebook reuse (report at `research/external/open-notebook-findings.md`; verdict = port patterns, don't run the service) and code-sandbox comparison.
- **2026-07-31** Resolved research ticket **#16** (Code execution sandbox selection): **self-host Judge0 CE** over HTTP (native grading verdicts, 90+ langs, `isolate` isolation; keep over-the-wire re GPL-3.0). Piston = fallback. Report at `research/external/code-sandbox-comparison.md`; resolution comment posted; issue closed; decision recorded on map #9.
  Next: work the frontier — suggested order is the infra trio (#12 content storage → #13 vector store → #14 AI backend, which unblock #18), or build the #17 inline-hint prototype first. Run `/wayfinder 9`.
- **2026-07-31** Set the tackle order as 4 waves (see PLAN.md "Execution order"): Wave 0 frame (#10 → #11 → #15), Wave 1 de-risk (#17 prototype, parallel), Wave 2 AI infra trio (#14 → #12 → #13, unblocks #18), Wave 3 downstream (#18 → #19 → #20 → #21). Rationale: blocking graph + prototype the fuzzy #17 guide early. Each frontier ticket tagged with its wave in the ticket tables.
  Next: **Wave 0 → #10 App IA & navigation**. Run `/wayfinder 9 10` (or `/wayfinder 9` to auto-pick). Parallel tracks available: #10/#11 · #17 · #14→#12→#13.
- **2026-07-31** Resolved Wave-0 ticket **#10 App IA & navigation** (grilling + domain-modeling, grounded in `App.tsx`, `NavBar.tsx`, `AppShell.tsx`, roadmap-engine types). Five decisions: (1) **two top-level tabs** Assessments + Practice, each a Roadmaps-style hub→detail dashboard; (2) items are **material-scoped, 1+ materials** — the selected set is the RAG grounding source (via #12 extracted content) and the KT mastery target (mastery updates each selected material); (3) mobile bottom bar **demotes Settings to a header/profile menu** → clean 6-tab bar (Home/Session/Week/Roadmaps/Assessments/Practice), desktop shows all; (4) **nested path-param routes** `/assessments`, `/assessments/new`, `/assessments/:id` (same for `/practice`) under the `/study` basename per `react-router-v7-basename`; (5) inside `ProtectedRoute→RequireOnboarding→AppShell` — records are **local-first** new event kinds (Dexie + existing SyncEngine), generation is **online-only** via the Intelligence Service (offline = review/redo cached). Resolution comment posted; #10 closed; decision recorded on map #9; new fog added (Material library/detail surface).
  Next: **Wave 0 continues** — #11 Assessment types/formats/scoring and #15 Persistence & local-first fit are both independent and takeable in parallel sessions. Run `/wayfinder 9 11` then `/wayfinder 9 15`. Wave-1 #17 prototype and the Wave-2 infra chain (#14→#12→#13) can also run concurrently. Frontier query: `gh issue list --label wayfinder:phase2 --state open`.
