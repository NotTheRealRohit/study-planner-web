# Phase 2 wayfinder chart — Assessments + LLM-guided Practice

**Task id:** `2026-07-31-phase2-wayfinder`
**Type:** wayfinder charting (planning; destination = spec + working prototypes)
**Tracker:** GitHub Issues on `NotTheRealRohit/study-planner-web` (the map + tickets are the canonical artifact; this doc is the `.work/` index/pointer).
**Map:** [#9 Phase 2 map: Assessments + LLM-guided Practice](https://github.com/NotTheRealRohit/study-planner-web/issues/9)

> This is an M.Tech **capstone**: build feature-rich and complete — no ship-fast / MVP / deferral tradeoffs.
> **Amended by #14 (2026-08-01):** the "development cost is not a constraint" clause is **reversed for the AI/model layer only** — no funds for Claude, so models run **cost-effective, accurate-enough** on the **Google Gemini free tier**. Feature scope stays full; only the models go cheap.

## Destination

A validated, feature-rich Phase 2 spec — Assessments (quiz / written / coding) plus an LLM-guided Practice area — **RAG-grounded** and **coupled to the knowledge-tracing / adaptation research pillar**, backed by **working throwaway prototypes** of the risky parts (above all the inline-hint live guide). Output: a spec ready for implementation planning.

## Decisions locked during charting (grilling)

1. Destination shape — spec **+ working prototypes** (execution rides into the map).
2. Guidance style — **tiered Socratic**; the guide never hands over the answer.
3. When it helps — **hybrid on-demand**: user asks + cheap signals (idle timer, failed test run) that *offer* a hint.
4. Moment-to-moment surface — **inline hints** (Copilot/Cursor UX, but ghost text is a hint/question, never finished code/prose).
5. Content grounding — **full RAG now**: ingestion + chunking + embeddings + pgvector + async worker.
6. Research coupling — **fully couple to KT/adaptation**: outcomes → mastery signal → adaptive difficulty → roadmap feedback.
7. Code execution — **hybrid**: client-side (Pyodide/JS) instant feedback + server sandbox for authoritative grading.
8. Server sandbox (resolved, #16) — **self-host Judge0 CE** over HTTP; Piston = fallback.

**Out of scope:** multiplayer / peer features · voice / podcast · proctoring / anti-cheat.
**Reference:** `../../../../research/external/open-notebook-findings.md` (port, don't run) · `../../../../research/external/code-sandbox-comparison.md`.

## Execution order (waves)

Order is driven by the blocking graph + the capstone rule "de-risk the fuzzy part early". #16 already done.
Legend: ☐ open · ✅ done.

**Wave 0 — Frame (cheap, constrains everything)**
1. ✅ #10 App IA & navigation — where the features live; every later ticket references it. (resolved 2026-07-31: 2 tabs, material-scoped, path-param routes, local-first records + online generation)
2. ✅ #11 Assessment types, formats & scoring — self-contained schema decision; later unblocks #19. (resolved 2026-08-01: Question-atom + mixed-container Assessment; 3 families/closed format enum; unified `[0,1]`+per-skill-binary KT contract, τ≈0.6; difficulty 1..5 authored + reserved empirical slot)
3. ✅ #15 Persistence & local-first fit — the event/data-model spine everything must obey. (resolved 2026-08-01: three-layer split — pointer event + server-owned content rows + redacted `assessmentContentCache`; per-Question runId-grouped `QuestionAttempted`→`QuestionGraded` [retry = fresh KT observation]; all grading server-side; mastery = `masteryCache` projection [`MasteryUpdated` reserved for #19]; Dexie **v5→v6** adds the two cache tables only. **Wave 0 complete.**)

**Wave 1 — De-risk the centerpiece (runs in parallel with the rest)**
4. ✅ #17 Inline-hint live guide (prototype) — highest uncertainty; grounds the practice spec; unblocks #21. (resolved 2026-08-01: **Variant C** anchored coach popover chosen HITL from 3 built surfaces; line-anchored + line-aware tiered-Socratic hints [nudge→hint→targeted→gated-reveal, orient-then-ask copy], hybrid triggers [I'm stuck / idle / failed-test that OFFER], reveal gated in prompt + structurally; guide = streamed Intelligence-Service LLM call, **model TBD=#14**; real editor needs Monaco/CodeMirror [#21 build note]. Throwaway branch `prototype/wf17-inline-hint-guide`, route `/study/practice-prototype`. **Wave 1 complete.**)

**Wave 2 — AI infra trio (internal order matters)**
5. ✅ #14 AI backend home & streaming — the home all model calls assume. (resolved 2026-08-01: single JWT-verified Intelligence Service owns all model+embedding calls; **cost-principle reversed** → Google Gemini free tier via `google-genai` behind a provider abstraction [Ollama fallback] — guide=`gemini-3.5-flash-lite`, generation+grading=`gemini-3.6-flash`, embeddings=`gemini-embedding-001`@768-dim; streaming = `POST`+`fetch` ReadableStream over `/v1/*` [not EventSource], provider-neutral SSE frames, reveal=separate gated call, generation streams per-question, grading req/resp; prompt arch = git-versioned Jinja + SSTI variable rule + untrusted-as-data + native `responseSchema`; abuse hardening = key server-side, **no endpoint runs the model on arbitrary text — every call bound to a user-owned artifact**, durable Postgres rate-limits + free-tier circuit breaker, audit logging; #14/#13 seam = #14 owns embedding client, #13 bulk-drives it. Graduated the prompt-arch/injection fog.)
6. ✅ **#22 Data + service architecture refactor** — split from #12 (2026-08-01), resolved 2026-08-02. **async = pgmq / Supabase Queues** (Kafka rejected: no Kafka-shaped load, fan-out tiny, replay already owned by `public.events`, job state now inside the SoT DB). **Two Python services**: Ingestion Service (worker-only: parsers → extract `full_text` → chunk) + Intelligence Service (API + worker: embed per #14, LLM topics); #13 chunk/embed splits along the #14 seam. **pgmq stage queues** `ingest.extract→embed→topics` (Postgres-trigger enqueue, visibility-timeout retry, one-image/two-entrypoints web+worker). **Spine = Tine C / no bus to the frontend**: write path stays local-first & untouched; migration `004` = server-owned content tables (`full_text`/chunks/`content_embeddings` pgvector) as Postgres SoT; pointer-events-only on log/snapshot; Dexie = redacted cache. **Audit gaps fixed**: `sync_checkpoints` migration (RLS `auth.uid()`); 5 MB cap = enforce client-side (skip+telemetry, full-replay fallback). **Unblocked #12; #13's job-mechanism half decided.**
7. ✅ #12 Content ingestion & storage — resolved 2026-08-03 on the #22 spine. **Material = A/unify + first-class server-owned library** (add materials in a store, attach to roadmaps; grain **1 material = 1 ingested body**; multi-source study = N materials in one assessment → N clean KT signals). **Fork 2a**: material is a **server-first entity** (Postgres `materials` = SoT, direct supabase-js CRUD, RLS; NOT event-sourced), only a thin roadmap-attach pointer `{materialId,title,role,estimatedDuration}` rides the log so the roadmap-engine/progress projections stay untouched; `materialId` DB-minted; onboarding material-add becomes online-requiring. **Creation trigger-driven** (client INSERT + Storage upload → Postgres trigger → pgmq; workers service-role; no bespoke ingestion endpoint). **Migration `004`** = `materials` (nullable `source_type` → contentless items allowed) + `content_chunks` with **folded `halfvec(768)`** HNSW cosine; RLS `auth.uid()=user_id`, `user_id` denormalized on chunks, workers service-role. **`material-raw`** bucket (private, `<uid>/<materialId>/<file>`, 25 MB, pdf/docx/pptx/txt/md; keep raw after extract). **Status = 5a** single `materials.status` state machine (`pending→extracting→chunking→embedding→ready`+`failed`+`error`; pgmq transport-only; read via Supabase Realtime; partial ingest keeps `full_text` displayable, RAG gates on `ready`). **Recovery** = retry (re-enqueue failed stage, no re-upload) / delete+re-add (FK cascade + client Storage remove; new id) / replace-keep-id. Free-tier verified: ~900–1000+ avg materials with halfvec; ⚠️ Free project pauses after 7 days idle (keep warm for demo). Delete-referenced-by-roadmap edge → owned by #10. Unblocked #13.
8. ✅ #13 Vector store, embeddings & async jobs — resolved 2026-08-03 on the #12/#22 base. **Chunking** 400-token/60-overlap, structure-then-recursive, tiktoken, `start_seconds` col (YT citations). **Preprocess** (Ingestion, zero Gemini quota): deterministic cleaning (A) + local-ML transcript punctuation (B, `deepmultilingualpunctuation`); YouTube transcript = `youtube-transcript-api` in the Python worker (existing `materials-metadata` edge fn is official-API metadata-only, can't fetch captions — untouched); `ytfetcher`, contextual-augmentation, semantic-chunking rejected (quota/determinism → eval note). **Embeddings** `gemini-embedding-001`@768 **L2-normalized before store** (Gemini doesn't self-normalize <3072 — beyond open-notebook, which stores raw), keep cosine; batch 100 + per-batch commit; **resume = idempotent NULL-scan**; **backpressure = automatic pgmq-redelivery** on 429/circuit-open (manual Retry only for real failures); **reserve RPM headroom for the interactive query path**; `status_detail` via Realtime. **Retrieval** server-internal only; RPC `match_content_chunks(query_embedding, material_ids[], match_count, min_similarity)` under the user's JWT (RLS) + **mandatory `material_id` scoping**; top-k 10 + loose distance floor; **local `bge-reranker` on generation+grading, off for the live guide**; generation = full_text-in-context-when-it-fits (retrieve-vs-coverage policy deferred to #18). **Lifecycle** replace-keep-id = drop+rebuild / retry = resume-NULLs; HNSW `m=16`/`ef_construction=64`/`ef_search=100`, single index + **`hnsw.iterative_scan` (relaxed_order)** for filtered recall. **Eval hook** retrieval logging + levers-as-config; gold-set recall@k/MRR + rerank ablation named as a future eval deliverable. New deps: Ingestion `youtube-transcript-api`/`tiktoken`/`deepmultilingualpunctuation`/parsers, Intelligence `bge-reranker`. **Trio complete → #18 fully unblocked.**

**Wave 3 — Downstream (open as upstream closes)**
8. ✅ #18 Grounded generation pipeline — resolved 2026-08-03 on the #12/#13/#14/#15 base (**keystone**). Two-stage **plan→generate** (ported open-notebook `ask` fan-out, synthesis barrier dropped; stage-2 = transformation-execution pattern + native `responseSchema`). **Grounding** two-tier: full_text-when-it-fits (~60-70% budget, sized from chunk `token_count`) else topic-stratified coverage-sampling + MMR (net-new); similarity-retrieval reserved for targeted slots; blueprint routes per slot. **Adaptive difficulty** (#18↔#19 seam) = client-supplied mastery snapshot `p∈[0,1]` in the request (no server mastery store), ZPD "aim just above" + calibration-spread cold-start. **Composition** = user `{count,family-mix}`; groundedness-over-count (fewer + `Warning[]`); coding gated on code material. **Typed gen** per-format `responseSchema` = envelope + visible payload + server-only hidden block; Judge0 self-check at gen. **Validation** = structural + citation-id grounding verification + coding self-check; online groundedness = citation-id only (LLM judge → offline #23); one repair → else drop + dedup. **Granularity** = per-slot fan-out, one Question per SSE frame. **Storage** `007` = `assessments`+`questions`; answer-key secrecy = **column-level `hidden_block` revoke** (service-role grades); thin `AssessmentCreated` pointer; redacted `assessmentContentCache` = envelope+visible_payload; `grounding_stale` flag. **Eval** = telemetry now + 3 offline metrics → tracked ticket **#23**.
9. ☐ #19 Grading → mastery signal — technically unblocked once #11 + #15 done; **sharpened by #18** (client mastery-snapshot read contract `masteryCache[skill]→p∈[0,1]` + per-question `material_id` = one clean KT observation); remains blocked only on its own mastery MATH.
10. ☐ #20 KT model & adaptive-difficulty loop — needs #19.
11. ☐ #21 Practice session model — needs the #17 prototype.

**Parallel tracks** (if running concurrent sessions): (A) #10/#11 product framing · (B) #17 prototype · (C) #14→#12→#13 infra chain. They converge at #18/#19.

**Why not pure foundation-first:** destination includes prototypes, and #17 (the inline guide) is the biggest unknown most likely to reshape the spec — prove it before building RAG around assumptions.

## Tickets

### Frontier (takeable now)

| # | Ticket | Type | Wave | Status |
|---|---|---|---|---|
| [#10](https://github.com/NotTheRealRohit/study-planner-web/issues/10) | App IA & navigation for Assessments + Practice | grilling | 0 | ✅ closed |
| [#11](https://github.com/NotTheRealRohit/study-planner-web/issues/11) | Assessment types, formats & scoring spec | grilling | 0 | ✅ closed |
| [#22](https://github.com/NotTheRealRohit/study-planner-web/issues/22) | Data + service architecture refactor | grilling | 2 | ✅ closed — **pgmq** (Kafka rejected); 2 services; migration `004`; gaps fixed |
| [#12](https://github.com/NotTheRealRohit/study-planner-web/issues/12) | Content ingestion & storage design | grilling | 2 | ✅ closed — A/unify + first-class library; Fork 2a server-first; migration `004` (`materials`+`content_chunks` folded `halfvec`); `material-raw` bucket; status 5a + Realtime |
| [#13](https://github.com/NotTheRealRohit/study-planner-web/issues/13) | Vector store, embeddings & async job mechanism | grilling | 2 | ✅ closed — 400/60 chunks + zero-quota preprocess; `gemini-embedding-001`@768 **L2-normalized**, batch 100, NULL-scan resume, auto-redelivery backpressure; retrieval server-internal RPC (user-JWT + `material_id` scope), top-k 10, `bge-reranker` gen+grading; HNSW 16/64/100 + `iterative_scan` (pgvector ≥0.8) |
| [#14](https://github.com/NotTheRealRohit/study-planner-web/issues/14) | AI backend home & streaming | grilling | 2 | ✅ closed — Gemini free tier |
| [#15](https://github.com/NotTheRealRohit/study-planner-web/issues/15) | Persistence & local-first fit | grilling | 0 | ✅ closed |
| [#16](https://github.com/NotTheRealRohit/study-planner-web/issues/16) | Code execution sandbox selection | research | — | ✅ closed — Judge0 CE |
| [#17](https://github.com/NotTheRealRohit/study-planner-web/issues/17) | Inline-hint live guide (prototype) | prototype | 1 | ✅ closed — Variant C |

### Blocked (wired, wait for upstream)

| # | Ticket | Type | Wave | Blocked by |
|---|---|---|---|---|
| [#18](https://github.com/NotTheRealRohit/study-planner-web/issues/18) | Grounded assessment-generation pipeline | grilling | 3 | ✅ closed — two-stage plan→generate; two-tier grounding (full_text-when-fits + topic-stratified coverage/MMR); per-format `responseSchema` + column-level `hidden_block` revoke; Judge0 self-check + citation-id verification; per-slot fan-out; migration `007`; eval → #23 |
| [#19](https://github.com/NotTheRealRohit/study-planner-web/issues/19) | Grading → mastery signal mapping | grilling | 3 | #11 #15 (sharpened by #18: mastery-snapshot read contract) |
| [#20](https://github.com/NotTheRealRohit/study-planner-web/issues/20) | KT model & adaptive-difficulty loop | grilling | 3 | #19 (#18 seam: `observedDifficulty` = #23 calibration target) |
| [#21](https://github.com/NotTheRealRohit/study-planner-web/issues/21) | Practice session model (written + coding) | grilling | 3 | ✅ #17 (now unblocked) |
| [#23](https://github.com/NotTheRealRohit/study-planner-web/issues/23) | Generation-quality evaluation harness (groundedness / difficulty-calibration / dedup) | task | 3 | #18 (groundedness+dedup) · #20 (difficulty-calibration); written triggers in ticket |

### Fog (not yet specified) / see map

Spaced-repetition scheduling · roadmap-feedback UX · capstone evaluation & metrics (+ #14: grader-robustness metric, free-tier data-use ethics note) · ~~prompt architecture + injection safety~~ (✅ graduated/resolved by #14) · material library/detail surface (surfaced by #10) · assessment feedback/review surface (surfaced by #11) · content cache lifecycle/eviction (surfaced by #15).

## Migration ledger (server-side schema — single source of truth)

Several tickets each said "migration `004`" in isolation. That is a **coordination** artifact, not a per-ticket decision — the number belongs here, not in a ticket. This ledger assigns the number, the owner, and (the part that matters) the **apply order by FK / dependency**. Convention: **integer prefixes** (matches the existing `003_`), applied in ascending order.

| # | File | Owner | Contents | Depends on |
|---|---|---|---|---|
| `003` | `003_events_table.sql` | (exists) | `events` table, `sync-snapshots` bucket | — |
| `004` | `004_sync_checkpoints.sql` | #22 | `sync_checkpoints` table + RLS `auth.uid()` (fixes the latent restore bug — `SyncEngine` reads/writes a table with no migration) | independent |
| `005` | `005_pgmq_bootstrap.sql` | #22 / #13 | enable `pgmq` + **`vector` ≥ 0.8** (`hnsw.iterative_scan` needed for filtered retrieval recall — #13); create stage queues (`ingest.extract`, `embed`, `topics`) + the KT derived-computation fan-out queues | — (shared infra) |
| `006` | `006_content_materials.sql` | **#12** / #13 | `materials`, `content_chunks` (folded `halfvec(768)` + HNSW cosine `m=16`/`ef_construction=64`; chunk cols `chunk_index`/`token_count`/`start_seconds` — #13), `material-raw` Storage bucket, RLS `auth.uid()=user_id`, the pgmq **enqueue trigger**, and the **`match_content_chunks(query_embedding, material_ids[], match_count, min_similarity)` RPC** (#13, reads the vector store) | `005` (queues + `vector`≥0.8 must exist before the trigger/RPC) |
| `007` | `007_assessments.sql` | #15 / #18 | `assessments` (`material_ids[]`,`recipe`,`blueprint`,`status`,`warnings`,`grounding_stale`; row created up-front `status='generating'`) + `questions` (per-question FK `material_id → materials`; `visible_payload`,`hidden_block`,`citations bigint[]`); **answer-key secrecy = column-level `REVOKE SELECT (hidden_block) FROM authenticated`** (RLS gates rows, column-grant gates the key; service-role reads for grading) — finalized by #18 (2026-08-03) | `006` |

Notes:
- **#12's content tables moved from "`004`" to `006`** — no cross-ticket coordination needed anymore; this table is the single source of truth. The closed #12 resolution comment says "migration `004`" (self-consistent at decision time); read the number from **here**.
- The **5 MB snapshot-cap enforcement (#22) is NOT a migration** — it is client-side code in `SyncEngine` (hard size-check before upload). It never claimed a migration slot; dropped from the collision set.
- Numbers are reserved on decision; the implementer applies them in ascending order. If a future ticket needs a new table, append the next integer here **before** writing the SQL.

## How to continue

Run `/wayfinder 9` (optionally naming a ticket). One decision ticket per session; research tickets may resolve AFK. Frontier query: `gh issue list --label wayfinder:phase2 --state open`. Claim a ticket by assigning it to yourself first.
