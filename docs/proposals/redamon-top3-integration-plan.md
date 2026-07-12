# Top-3 Redamon Integrations — Implementation Plan

Companion to [`redamon-feature-integration.md`](redamon-feature-integration.md). Decomposes the
three recommended first integrations into **rule-compliant PRs** per
[`CONTRIBUTING_AGENT.md`](../../CONTRIBUTING_AGENT.md) and [`QUALITY_BAR.md`](../QUALITY_BAR.md):
each PR is **1 logical concern, ≤ 400 runtime lines, ≤ 10 files**, with a real end-to-end
verification statement. File paths below were confirmed against the current `main` tree.

> **Prerequisite that shapes everything:** the AI-surface cluster needs a `Technology` KG node kind.
> KG node kinds live in `packages/aegiscore-core/aegiscore_core/types/kg.py` and are exercised by
> `packages/aegiscore-core/tests/test_public_api_stability.py` + `test_kg_detection_types.py` —
> i.e. a **public-type-surface change**. `types/**` is *not* in `.github/CODEOWNERS` today (only
> `contracts/**`, `protocols/**`, `registry/**` are), so it may self-merge on green — but because it
> is load-bearing public API, it should land via a short **ADR** (`docs/adr/**`, which *is*
> owner-gated) so the schema decision is reviewed. Build this first; the classifiers then land cheaply.

---

## A. AI-surface discovery cluster (proposal items 1–4)

**Why first:** closes Aegiscore's single biggest categorical blind spot — the `llm-redteam` plugin
can attack Ollama/vLLM/LangChain/MLflow targets it currently cannot *find*. Pure-Python regex
catalogs ported from `redamon/recon/helpers/ai_signal_catalog.py`; they drop into the existing
`kg_ingest_*` fan-in in `packages/aegiscore/aegiscore/tools/research/tools.py`.

| PR | Concern | Files (≈) | Tier | CODEOWNERS-gated? |
|----|---------|-----------|------|-------------------|
| **A0 — ADR + `Technology` node kind** | Add `Technology` NodeKind (+ optional `Certificate`) to `types/kg.py`, KG migration, ADR | `docs/adr/NNNN-ai-surface-technology-node.md`, `types/kg.py`, migration, type tests | Tier-owner (ADR) | **Yes** — `docs/adr/**` → waits for `@PurpleCHOIms` |
| **A1 — AI signal catalog module** | New `tools/research/ai_signatures.py`: header/port/title/banner/endpoint catalogs + pure match functions, fully unit-tested | `ai_signatures.py` + `tests/.../test_ai_signatures.py` | Tier-delegate | No |
| **A2 — httpx ingester: AI header + title** | Call `match_ai_header` / `match_ai_title` inside `kg_ingest_httpx_jsonl` (tools.py:968); MERGE `Technology` nodes | `tools/research/tools.py` + tests | Tier-delegate | No (depends on A0) |
| **A3 — port catalog in masscan/nmap ingest** | `lookup_ai_port` in `kg_ingest_masscan` (tools.py:1998) + `kg_ingest_nmap_xml` (tools.py:713); two-tier disambiguation gate | `tools/research/tools.py` + tests | Tier-delegate | No (depends on A0) |
| **A4 — endpoint AI interface-type classifier** | Tag URL/Entrypoint nodes with `ai_interface_type` in the katana/httpx path; route AI hits to `llm-redteam` objective drafting | `tools/research/tools.py` (+ routing) + tests | Tier-delegate | No (depends on A0) |

**TDD per PR:** table-driven tests over the regex catalogs (known header → expected vendor/category;
known port → expected Technology; benign input → no match / `disambiguate` deferral). Watch each fail
before implementing (charter rule #10).

**End-to-end verification (the hard part):** rule #12 requires actually running the ingest path and
seeing a `Technology` node in Neo4j. That needs the stack up (`make dev` / `make dogfood`, Neo4j +
LiteLLM + sandbox). Plan: run `kg_ingest_httpx_jsonl` against a captured httpx JSONL containing an
Ollama/vLLM banner on a live engagement, query Neo4j for the `Technology` node, confirm the
`llm-redteam` plugin then enumerates it. If the full stack cannot be stood up in CI/this environment,
that gap is declared explicitly in the PR body per QUALITY_BAR §Wired-end-to-end — never ticked falsely.

---

## B. JS endpoint + parameter classification taxonomy (proposal item 9)

**Why:** the biggest recon→exploit handoff gap for web. Turns a flat URL dump into vuln-class-tagged
targets (`file_params`→LFI, `command_params`→RCE, `redirect_params`→SSRF) the chain planner can weight.
Port **only** `redamon/recon/main_recon_modules/resource_enum/classification.py` — *not* Redamon's
`ThreadPoolExecutor` scheduler (conflicts with Aegiscore's bash-tmux/`task()` parallelism).

| PR | Concern | Files (≈) | Tier | Gated? |
|----|---------|-----------|------|--------|
| **B1 — classify_endpoints tool** | New pure-Python `classify_endpoints` `@tool` (endpoint + param taxonomy, type inference) | `tools/research/<module>.py` + tests | Tier-delegate | No |
| **B2 — fold classes onto KG** | Add endpoint/param category props in `kg_ingest_katana` (tools.py:1934) / `kg_ingest_ffuf` (tools.py:2067); let objective suggestion weight high-risk param classes | `tools/research/tools.py` + tests | Tier-delegate | No |

**TDD:** fixtures of real URL/param sets → expected class labels; assert objective-suggestion ranking
shifts for `command_params`. **E2E:** run katana ingest on a crawled target, confirm classified props
land on URL nodes and a high-risk param raises an objective.

---

## C. Mid-run guidance injection (proposal item 5)

**Why:** the biggest operator-control gap — steer a long autonomous run without kill/restart.
Reuses the proven `before_model` injection seam (the notifications middleware;
`packages/aegiscore/.../middleware` + `tests/unit/middleware/test_notifications.py`). Use a
**file-backed per-engagement inbox with a byte-offset cursor** (mirror `FileBackedApprovalTransport`),
**not** Redamon's in-process `asyncio.Queue` (wrong fit for the LangGraph Platform thread/run model).

| PR | Concern | Files (≈) | Tier | Gated? |
|----|---------|-----------|------|--------|
| **C1 — guidance middleware** | New `GUIDANCE` middleware slot draining `workspace/<slug>/guidance/inbox.jsonl`; injected as trusted OPERATOR guidance that refines the current objective and **can never relax RoE** | middleware module + tests | Tier-delegate | No |
| **C2 — operator entry points** | `POST /…/guidance` web route + CLI `/guide` command writing to the inbox | web route + CLI hook + tests | Tier-delegate | No |

**Guard-rail note (charter rule #5):** injected guidance is untrusted-by-origin only insofar as the
operator is trusted; it must be framed so it cannot widen scope or relax RoE/OPPLAN. State this
explicitly in the PR body. **E2E:** start an engagement, drop a guidance line mid-run, observe the
next dispatch incorporate it without an RoE relaxation.

---

## Sequencing

1. **A0 (ADR + Technology node)** — unblocks A1–A4 and the wider tech-detection work. Owner-gated; open early.
2. **A1 → A2 → A3 → A4** — land in order once A0 is in.
3. **B1/B2** and **C1/C2** are independent of A and of each other — parallelizable.

## Commit / PR conventions for this repo (differs from defaults)

- **No `Co-Authored-By:` trailer.** [`CONTRIBUTING_AGENT.md`](../../CONTRIBUTING_AGENT.md) hard-rule #1
  and [`COWORK.md` §4.5](../COWORK.md) forbid AI co-author trailers; they are stripped. Commit under the
  contributor's own identity.
- **Conventional-Commit titles**, squash-merge, delete branch after merge.
- **One concern per PR**; do not bundle. Run `make quality` before pushing and paste the tail in the PR body.
- Every PR links an issue or this ADR in the **Intent** field and fills the **End-to-end verification** section honestly.
