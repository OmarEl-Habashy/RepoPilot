# RepoPilot: Work Division and Technical Research Plan

**Project:** RepoPilot, an evidence-driven multi-agent framework for automated QA and repair of AI-generated ("vibe-coded") repositories
**Team:** Farag · Maro · Ziad · Omar · Hussein
**Document type:** Internal planning document, version 1.0, 14 October 2026
**Sources:** `tech_description.md`, *Project Understanding* (literature synthesis), the four team summaries (Farag, Hussein, Ziad, Omar), RAP-Gen (arXiv 2309.06057) and *Understanding the (In)Security of Vibe-Coded Applications* (arXiv 2606.23130)

---

## Summary

RepoPilot is split into five workstreams. Each one owns a contiguous part of the pipeline and lines up with the papers that person has already summarised:

| # | Workstream | Owner | Pipeline stages owned | Papers already read |
|---|---|---|---|---|
| WS1 | Repository Ingestion, Code Intelligence and RAG | **Maro** | Repository ingestion, code-understanding agent, code RAG, dependency/knowledge graph, context-window strategy | RepoMem, SGAgent (repo knowledge graph), CAT (context) |
| WS2 | Risk, Test Planning, Test Generation and Execution Harness | **Farag** | Risk-analysis agent, test-planning agent, test-generation agent, sandbox execution, coverage and mutation testing | CodeT5, TestGen-LLM, TestAgent |
| WS3 | Static/Security Analysis, Repair and Regression | **Omar** | Deterministic scanners, repair agent, test-repair path, patch checks, re-testing | RAP-Gen, (In)Security of Vibe-Coded Apps |
| WS4 | Orchestration, Failure Attribution, Artifacts and Reporting | **Ziad** | Orchestrator/harness, failure-analysis agent, artifact schemas, quality gates, review agent, final report, evaluation design | TiCoder, Agentic RAG (Apple), Macedo (agent harness) |
| WS5 | Benchmark, Evaluation Dataset and Baselines | **Hussein** | Benchmark app corpus, seeded and real bugs, ground-truth labels, baseline agents, experiment runner, metrics and variance | CAT, RepoMem, SGAgent (all evaluated on SWE-bench-style benchmarks) |

Each person researches **how** their part should be implemented and brings back a short technical report written to the shared template (see `02_Technical_Report_Writing_Guide.md` and `03_Technical_Report_Template.md`). The report must state the **inputs** they need, the **process** they propose, the **outputs** they produce, and the alternatives they rejected. We then meet, check that the interfaces between workstreams match, and freeze the architecture.

The lists of candidate tools in this plan are **starting points for your search, not decisions**. Your job is to confirm, replace or reject them with evidence.

---

## Table of Contents

1. Introduction and Scope
2. System Overview and Workstream Boundaries
3. WS1 – Repository Ingestion, Code Intelligence and RAG (Mario)
4. WS2 – Risk, Test Planning, Test Generation and Execution Harness (Farag)
5. WS3 – Static/Security Analysis, Repair and Regression (Omar)
6. WS4 – Orchestration, Failure Attribution, Artifacts and Reporting (Ziad)
7. WS5 – Benchmark, Evaluation Dataset and Baselines (Hussein)
8. Interface Contracts Between Workstreams
9. Context-Window Strategy Across the Pipeline
10. Cross-Cutting Decisions (Everyone)
11. Timeline and Discussion Meeting
12. References

---

## 1. Introduction and Scope

### 1.1 What we are building

From the technical description: given a repository, RepoPilot builds a structured representation of the code (static analysis, dependency graphs, semantic search, RAG). An orchestrator then drives specialised agents for code understanding, risk analysis, test planning, test generation, execution, failure analysis, repair and review. Execution results are the evidence. Agents pass structured artifacts to each other instead of relying on chat memory. Every loop is bounded and gated by measurable results.

### 1.2 First target stack

The *Project Understanding* synthesis fixes the first target as **React/Vite + Supabase + Stripe** e-commerce and CRUD apps. The vibe-coding security study supports this choice: 96% of the vibe-coded apps it collected are web apps on React/Vite and 55% use Supabase [2]. Every workstream should research for **this stack first**, and note what would change for others (for example Next.js or a Python backend).

### 1.3 The research core (everyone must keep this in mind)

> When a generated test fails, is the **test** wrong, the **code** wrong, the **environment** broken, or is it **ambiguous**?

Expectations inferred only from the code copy the code's bugs. RepoPilot therefore draws intent from independent sources: README and docs, UI text, types and schemas, commit history, TODOs, agent artifacts (prompts, `CLAUDE.md`) and a verified pattern library. Every workstream either **produces** evidence for this decision or **consumes** the verdict.

### 1.4 Out of scope for this research round

- Building production code. This round is research plus a design proposal, with small spikes or prototypes where they settle a question.
- UI polish. WS4 proposes the interface but does not build it yet.

---

## 2. System Overview and Workstream Boundaries

```text
            ┌──────────────────────────── WS1 (Maro) ─────────────────────────┐
 Repo URL → │ Ingestion → Repo Profile → Code Index (AST, graph, vectors) → RAG│
            └───────────────┬──────────────────────────────────────────────────┘
                            │ repo_profile.json, code_index, retrieval tools
            ┌───────────────▼──────── WS3 (Omar) ─┐   ┌──── WS2 (Farag) ─────────────────────┐
            │ Deterministic scanners (SARIF)      │──►│ Risk map → Test plan → Test gen      │
            └─────────────────────────────────────┘   │ → Sandbox execution → coverage/mutation│
                                                      └───────────────┬───────────────────────┘
                                                                      │ execution_result.json
            ┌──────────────────────── WS4 (Ziad) ─────────────────────▼──────────────────────┐
            │ Failure attribution: test_wrong | code_wrong | environment_issue | ambiguous    │
            └───────┬───────────────────────────┬──────────────────────────────┬─────────────┘
                    │ test_wrong                │ code_wrong                   │ ambiguous
                    ▼                           ▼                              ▼
             WS2 test revision         WS3 bounded repair            yes/no question to owner
                    │                           │                     (TiCoder-style)
                    └──────────► WS2 re-run + regression + mutation ◄──────────┘
                                                │
                                   WS4 review agent → evidence-based report
   WS4 also owns: orchestrator loop, budgets, quality gates, artifact schemas, trace log
   WS5 (Hussein) sits beside the pipeline: benchmark apps + ground truth in, metrics out for every stage
```

**Rule:** a workstream may *use* another workstream's tool, but it must not *redefine* that tool's artifact. Changes to a shared artifact go through its owner.

---

## 3. WS1 – Repository Ingestion, Code Intelligence and RAG (Owner: Maro)

### 3.1 Goal

Turn an untrusted repository into (a) a **repo profile**, (b) a **code index** (AST symbols, dependency and call graph, knowledge graph, embeddings), and (c) **retrieval tools** the other agents call. Also own the **context-window strategy** (Section 9).

### 3.2 Questions you must answer

**A. How does the agent get the repository?**
1. Input forms: public GitHub URL, private repo (GitHub App installation token vs personal access token), or zip upload. Which do we support in v1?
2. Clone strategy: full clone vs `--depth 1`. Vibe-coded apps have short histories (median 8.39 days of development [2]), so a full clone is cheap and keeps commit messages as intent evidence. Confirm this.
3. Pin the analysed commit SHA so every run is reproducible.
4. Safety: the repo is untrusted. Clone and install **only inside the sandbox** (coordinate with WS2). Never run `npm install` lifecycle scripts on the host. Check `npm ci --ignore-scripts` for profiling-only steps.
5. Secret hygiene: scan for secrets (coordinate with WS3, e.g. gitleaks) **before** any file content is sent to an external LLM API, and redact what is found.
6. Look at existing "repo to LLM" tools (gitingest, repomix, Aider's repo map) and decide what we reuse.

**B. Repository profiling (what kind of app is this?)**
1. Detect the stack from `package.json`, lockfile, `vite.config.*`, `tsconfig.json`, `supabase/` (`config.toml`, `migrations/*.sql`, `functions/`), `.env.example`, Stripe SDK usage, router setup.
2. Detect AI-generation fingerprints used in [2]: `.claude/` folder, `CLAUDE.md`, Lovable author meta tag, `Co-authored-by:` trailers. These feed WS4 as intent evidence.
3. Extract runtime requirements (Node version from `.nvmrc`/`engines`, package manager, env vars needed) and hand them to WS2.

**C. Code intelligence (structure)**
1. Parsing: compare **tree-sitter** (TS/TSX/JS/SQL, fast, error-tolerant) with the **TypeScript compiler API / ts-morph** (full type and symbol resolution). One option is to use both: tree-sitter for chunking, ts-morph for symbols and types.
2. Graphs: module dependency graph (dependency-cruiser, madge), call graph (ts-morph or SCIP via `scip-typescript`), React component tree, routes (react-router), and the **database schema plus RLS policies** parsed from Supabase migrations.
3. Knowledge-graph design. SGAgent uses 3 entity types and 7 relations [3]. Apple's Agentic RAG uses 15 edge types such as Requires, Validates and Covers [4]. Propose ours. Starting point:
   - Entities: File, Module, Function/Component, Route, API/Edge Function, DB Table, RLS Policy, Env Var, Test, Requirement/Intent item.
   - Edges: imports, calls, renders, routes_to, reads_table, writes_table, protected_by, uses_secret, tested_by, covers, derived_from (intent).
4. Storage: in-memory NetworkX + SQLite vs an embedded graph DB (Kùzu) vs Neo4j. Choose based on app size (median about 8,254 LOC [2]) and query needs.

**D. RAG design (what kind of RAG?)**
1. **Recommended direction to evaluate: agentic hybrid RAG.** Agents call retrieval as *tools* when they need context. There is no single up-front retrieval. Three channels, fused:
   - **Lexical** (BM25) for identifiers, error strings and file names.
   - **Dense** (code embeddings) for meaning.
   - **Graph expansion**: from a hit, follow edges (callers, callees, the tables it touches, the RLS policies on those tables).
   - Fuse with reciprocal rank fusion, then optionally a cross-encoder reranker.
   Evidence: RAP-Gen's hybrid BM25 + dense retriever beat either alone (54.15 vs 53.88/53.93 EM) [1]. Agentic RAG went from 65.2% (basic RAG) to 87.1% (hybrid vector-graph) to 94.8% (agentic) [4]. SGAgent dropped from 51.3% to 44.0% without its knowledge graph [3].
2. Chunking: **AST-aware chunks** (one function, component, hook, SQL policy or route per chunk) with a header carrying the file path, symbol name and signature. Do not use fixed-size text windows. Justify the chunk size.
3. Embedding model: compare at least two code embedding models (for example CodeRankEmbed, used as a baseline in RepoMem; nomic-embed-code; jina code embeddings; voyage-code). Report licence, cost and local vs API.
4. Vector store: Qdrant, Chroma, LanceDB or pgvector. Pick the simplest one that supports metadata filters.
5. **Retrieval must be measured on its own.** RAP-Gen found a random retrieved example scored *below* no retrieval (52.98 vs 53.46) [1]. Propose a metric (for example Recall@k / Acc@k file localisation, as in RepoMem) and a small labelled set.
6. Commit-history memory (RepoMem): useful or not for our apps? RepoMem *lost* 13.1 points on repositories with thin histories [5]. Expect it to be a weak signal for us. Propose using it only as a hint that must be verified in code.

**E. Is RAG even needed for small apps?** (key question)
A median vibe-coded app is about 8k LOC, which may fit in a long-context model's window. Measure the token count of 3 to 5 real sample apps. Propose an ablation: **full-repo context vs repo map + RAG** on the same tasks (cost, latency, accuracy). The answer may differ per agent (see Section 9).

### 3.3 Inputs you need

| Input | From |
|---|---|
| Repo URL / archive, optional access token | User (via WS4 interface) |
| Sandbox to clone and install inside | WS2 |
| Secret-scan results for redaction | WS3 |
| Required artifact format (schema conventions) | WS4 |

### 3.4 Outputs you deliver

- `repo_profile.json`: stack, versions, package manager, entry points, routes, DB tables, env vars, AI fingerprints, commit SHA, LOC and token counts.
- `code_index`: symbol table, graphs, embeddings and the knowledge graph, plus how it is stored.
- **Retrieval tool API** that the other agents call, for example `search_code(query, k, filters)`, `get_symbol(name)`, `neighbors(node, edge_types, depth)`, `repo_map(budget_tokens)`, `get_file(path, range)`.
- Retrieval evaluation numbers on the sample apps.
- Context-window recommendation per agent (Section 9).

### 3.5 Reading to extend

RepoMem, SGAgent and CAT summaries; Agentic RAG (Ziad's summary); RAP-Gen retriever section; Aider repo-map design; tree-sitter, ts-morph and SCIP documentation; Supabase migrations format.

---

## 4. WS2 – Risk, Test Planning, Test Generation and Execution Harness (Owner: Farag)

### 4.1 Goal

Decide **where to test** (risk map), **what to test** (test plan), **how to write tests** (generation), and **how to run them safely and measure them** (sandbox, coverage, mutation). Produce execution evidence that WS4 can judge.

### 4.2 Questions you must answer

**A. Execution harness / sandbox (build this first; everyone depends on it)**
1. Isolation: Docker container per run vs microVM sandboxes (E2B, Daytona, Firecracker). Compare startup time, cost, Docker-in-Docker needs and network control.
2. Bringing the app up: install with the detected package manager and Node version from WS1, build with Vite, and start a **local Supabase** stack (Supabase CLI `supabase start` or its docker-compose). Apply migrations and seed data. Find out how to run this inside the sandbox; Supabase CLI itself needs Docker.
3. Stripe: Stripe test mode via `stripe-mock` or the Stripe CLI, and how to fire webhooks for tests.
4. Network policy (deny by default, allowlist the package registry), CPU/memory limits, per-command timeouts.
5. Evidence capture: test results as JUnit XML or Vitest JSON, raw stdout/stderr, normalised stack traces, Playwright traces and screenshots, build/compiler errors.

**B. Test levels and frameworks for the target stack**
1. Unit/component: **Vitest + React Testing Library** (native to Vite projects).
2. Integration: against the local Supabase, plus network mocking (MSW) where needed.
3. End-to-end user flows: **Playwright** (sign-up, login, cart, checkout).
4. **Security behaviour tests** (with WS3): for example, can an anonymous user or *another* user read or modify rows (RLS) using supabase-js with different JWTs? Can the price be changed on the client? Is the webhook signature checked? This directly targets the top vulnerability classes: broken access control 28.6%, injection 16.8%, authentication failures 14.8% [2].

**C. Risk analysis**
Propose a scoring formula over scanner findings (WS3), security-sensitive tags (auth, payments, DB writes, secrets), graph centrality (WS1), complexity and the absence of existing tests. Output a ranked `risk_map.json` that decides where the test budget goes.

**D. Test planning (TestAgent style)**
For each high-risk unit or user flow, list requirements as **normal / boundary / error** cases [6]. Each requirement must cite its **intent source** (README line, UI text, type or Zod schema, DB constraint, TODO, CLAUDE.md, pattern), recorded in `intent_evidence` for WS4.

**E. Test generation and filtering**
1. Context given to the generator: the focal unit, signatures of its dependencies, relevant types, an existing test as a style example, and the plan item. Keep it small (see Section 9).
2. Filtering, adapted from TestGen-LLM [7]: must **build**, run **N times** to detect flakiness (TestGen-LLM uses 5), and add coverage or target a risk. **Important difference:** TestGen-LLM *discards* failing tests. RepoPilot *keeps* deterministic failures and sends them to WS4 for attribution. Only build failures and flaky tests are discarded or revised.
3. Bounded self-repair of tests that do not compile (maximum K attempts).

**F. Adequacy metrics**
1. Coverage: Vitest v8 or istanbul, line and branch, per file.
2. Mutation: **StrykerJS** (has a Vitest runner). Mutation testing is slow, so propose limiting it to high-risk files and time-boxing it. TestAgent reached an 83.69% mutation score vs 43.59% for EvoSuite [6].
3. Remember that coverage and mutation are proxies (Farag's summary). Also report true bugs found.

### 4.3 Inputs you need

| Input | From |
|---|---|
| `repo_profile.json`, retrieval tools, graph centrality | WS1 |
| Scanner findings (SARIF) | WS3 |
| Artifact schemas, budgets, retry limits | WS4 |
| Verdict `test_wrong` (to revise a test) | WS4 |
| Patched code (to re-run regression) | WS3 |

### 4.4 Outputs you deliver

- Working sandbox recipe (Dockerfile / compose) able to bring up at least one sample React/Vite + Supabase app.
- `risk_map.json`, `test_plan.json` (with `intent_evidence` per item), generated test files.
- `execution_result.json` per run: pass/fail per test, error type, stack trace, logs, flakiness count, coverage delta, mutation score.
- A regression-run command WS3 can call after each patch.

### 4.5 Reading to extend

TestGen-LLM, TestAgent and CodeT5 summaries; Vitest, Playwright and StrykerJS documentation; Supabase local development and testing docs (including database tests with pgTAP); Stripe testing docs; sandboxing options.

---

## 5. WS3 – Static/Security Analysis, Repair and Regression (Owner: Omar)

### 5.1 Goal

Provide **deterministic** findings (no LLM) that feed risk and testing. Then design the **bounded repair** process: localise, plan, patch, verify. Patches must never weaken a security check.

### 5.2 Questions you must answer

**A. Deterministic scanners (the "checks must block, not warn" layer)**
1. General: `tsc --noEmit` type errors, ESLint (with a security plugin), **Semgrep** (JS/TS rulesets plus our own custom rules), optionally CodeQL (heavier, more precise). Compare speed and false positives.
2. Secrets: gitleaks or trufflehog. Shared with WS1 for redaction before LLM calls.
3. Supply chain: `npm audit` or osv-scanner.
4. **Stack-specific checks** (the high-value part). Write them as Semgrep rules or small parsers:
   - Supabase tables without `enable row level security`, and policies like `using (true)`. Reference: CVE-2025-48757 (CVSS 9.3), missing RLS in Lovable sites [2]. Also check Supabase's own database linter (`supabase db lint` / splinter) and whether it covers this.
   - `service_role` key or other secrets in client code (`VITE_*` env vars ship to the browser).
   - Stripe secret key on the client, prices taken from the client, webhook handler without signature verification.
   - Auth checks done only on the client; TODO-style placeholders ("TODO: add password verification"), Base64 used as "encryption", static demo keys. These are the "demo-oriented design" failure mode [2].
5. Normalise all output to **SARIF**, then map to OWASP categories. Measure precision and recall per check family on seeded bugs.

**B. Bounded repair (code_wrong path)**
1. Staging, from SGAgent [3]: **localise** (up to 5 candidate locations) → **suggest** (a written repair plan with risks) → **fix** (candidate patches). The suggest stage was worth +13.3 points in SGAgent's ablation.
2. **Pattern library with retrieval, after RAP-Gen [1]:** 10 to 20 *verified* fix patterns for our stack (for example: enable RLS plus an owner-only policy; move a secret into an Edge Function; verify the Stripe webhook signature; look up the price on the server; validate input with Zod). Each pattern is a pair: bug example → fix example, plus a test that proves the fix. Retrieve with hybrid BM25 + dense. Always compare against "no retrieval". Keep benchmark apps out of the library (RAP-Gen's leakage guard).
3. Patch format: unified diff vs search/replace blocks. Which do LLMs apply more reliably? Apply in a git branch or worktree inside the sandbox.
4. Bounds: maximum attempts per defect, maximum diff size (lines and files), allowed file paths (no edits to tests during a code repair, and no edits to code during a test repair).

**C. Patch acceptance (quality gate, run by code, not by the model)**
1. The originally failing test now passes.
2. The full regression suite still passes (WS2 runner).
3. Scanners show no new findings.
4. **Weakened-check detector:** reject patches that remove auth checks, disable RLS, loosen a policy, delete or weaken assertions, add `skip`/`only`, or catch-and-ignore errors. This addresses "function-fix side effects" (an error "fixed" by weakening security) [2]. Implement as diff + AST rules.
5. Mutation score on the patched area does not drop.

**D. Test-repair path (test_wrong verdict)**
Coordinate with WS2. Same bounds, but only test files may be edited.

### 5.3 Inputs you need

| Input | From |
|---|---|
| Repo checkout in sandbox, `repo_profile.json`, retrieval tools | WS1 |
| Failure verdict `code_wrong` with evidence and localisation hints | WS4 |
| Regression runner, mutation runner | WS2 |
| Budgets and retry limits | WS4 |

### 5.4 Outputs you deliver

- `static_findings.sarif` (plus an OWASP mapping).
- Pattern library format and first 10 patterns (description, bug example, fix example, proving test).
- `repair_proposal.json`: localisation, plan, diff, retrieved pattern ID, attempt count.
- `validation_report.json`: gate results (failing test, regression, scanners, weakened-check, mutation).

### 5.5 Reading to extend

RAP-Gen (full paper in `Papers/`), the vibe-coded security study (Sections 5 to 7), SGAgent summary, Semgrep rule writing, Supabase RLS documentation, Stripe webhook security, SARIF specification.

---

## 6. WS4 – Orchestration, Failure Attribution, Artifacts and Reporting (Owner: Ziad)

### 6.1 Goal

Own the **harness** that runs everything, the **artifact schemas** everyone writes to, the **failure-attribution** research core, and the **final report**. Also propose the **evaluation design**.

### 6.2 Questions you must answer

**A. Harness and orchestration**
1. Map RepoPilot to Macedo's four conditions [8]: T1 agent loop, T2 tool interface, T3 task-aware context, T4 control that does not depend on the model obeying. Note that Macedo classifies a fixed-graph orchestrator as *not* a harness, so decide what is fixed (the pipeline order) and what is adaptive (each agent's inner loop).
2. Framework: compare LangGraph (state graph, checkpoints, resumable runs), an agent SDK from a model provider, and a thin custom Python loop. Criteria: control over loops, structured outputs, tool calling, tracing, ease of swapping models.
3. **Control (T4):** budgets per app and per agent (tokens, wall time, retries, diff size), coded quality gates (an agent cannot declare success; the gate checks evidence), and stopping rules.
4. Tracing: every agent step and tool call logged (for example OpenTelemetry, Langfuse or LangSmith). This is the "complete agent/action trace" deliverable.
5. Tool interface (T2): consider exposing WS1/WS2/WS3 tools through **MCP** so that any agent or model can use them.

**B. Artifact schemas (the contract between agents)**
Define JSON Schema / Pydantic models with versioning for: `repo_profile`, `risk_map`, `test_plan`, `test_case`, `execution_result`, `failure_verdict`, `repair_proposal`, `validation_report`, `final_report`, `trace_event`. Circulate a draft **in week 1** so others can write to it.

**C. Failure attribution (the research core)**
1. Verdicts: `test_wrong | code_wrong | environment_issue | ambiguous`, each with a calibrated confidence and cited evidence.
2. Two stages:
   - **Rules first** for environment issues (module not found, ECONNREFUSED to Supabase, timeouts, missing env var, port in use). These are cheap and deterministic.
   - **LLM judge** for the rest, with structured output. Inputs: the test, the plan item and its `intent_evidence`, the focal code, the stack trace, related scanner findings and the matching pattern.
3. **Independent intent sources** (core hypothesis, RQ1/RQ2): README and docs, UI text, types and Zod schemas, DB constraints and RLS, commit messages, TODOs, `CLAUDE.md` and prompts, pattern library. The baseline is a **code-only judge**. We must show the intent-aware judge beats it.
4. Robustness: multiple samples or votes (TestAgent uses three LLM voters [6]). Note the warning in *Project Understanding*: voters that all read the same code share the same blind spot.
5. **Abstention and calibration:** choose a confidence threshold below which the verdict is `ambiguous`. Measure calibration (for example expected calibration error and a reliability diagram).
6. **Ambiguity resolution, from TiCoder [9]:** turn an ambiguous verdict into a single yes/no question about concrete behaviour for the repo owner ("When a user is not logged in, should /orders return an empty list or an error?"). One query raised MBPP pass@1 from 48.24% to 70.73% in TiCoder.

**D. Review agent and final report**
Structure the evidence-backed report: risks found, tests generated, results, verdicts, repairs, regression and mutation results, cost, and the trace. Decide the formats (HTML/Markdown, JSON) and sketch the developer interface (submit a repo, watch progress, read the report).

**E. Evaluation design (coordinate with everyone)**
1. Benchmark apps: self-generated vibe-coded apps with saved prompts (kept separate from the pattern library), plus some public ones, with **seeded bugs** and naturally occurring bugs.
2. Ground-truth labels for failure verdicts by two annotators, reported with Cohen's κ.
3. Repeated runs to report variance. The security study found 22% of replay cells changed outcome across identical runs [2].
4. Baselines: a single general-purpose coding agent prompted to "QA and fix this repo"; a code-only judge; RepoPilot with each stage removed (ablations).

### 6.3 Inputs you need

| Input | From |
|---|---|
| Tool APIs and artifact needs | WS1, WS2, WS3 |
| `execution_result.json`, `test_plan.json` with `intent_evidence` | WS2 |
| Static findings, pattern library | WS3 |
| Intent sources (README, UI text, commits, CLAUDE.md, types) via retrieval | WS1 |

### 6.4 Outputs you deliver

- Artifact schema pack v0 (week 1), then v1 after the meeting.
- Orchestrator design: state diagram, budgets, gates, stop rules, framework choice.
- `failure_verdict.json` design and the attribution method, with a small pilot on hand-made failing tests if time allows.
- Final report outline and evaluation protocol.

### 6.5 Reading to extend

TiCoder, Agentic RAG and Macedo summaries; TestAgent's failure voting; LangGraph and agent SDK documentation; MCP specification; literature on LLM-as-judge calibration and selective prediction (abstention).

---

## 7. WS5 – Benchmark, Evaluation Dataset and Baselines (Owner: Hussein)

### 7.1 Goal

Build the **shared benchmark** that every workstream measures against, and the **experiment runner** that produces comparable numbers. WS4 decides *what* the evaluation must show (protocol, research questions). WS5 builds *the data and tooling* to show it: apps, bugs, labels, baselines, metrics and repeated runs. Without this, no stage can prove it "earns its place" (*Project Understanding*, Lesson on ablations).

### 7.2 Questions you must answer

**A. Benchmark app corpus**
1. **Self-generated apps:** generate React/Vite + Supabase + Stripe apps (e-commerce, CRUD) with Lovable, Bolt or Claude Code, and **save every prompt** and agent artifact (`CLAUDE.md`, chat logs). These saved prompts are intent ground truth. How many apps are feasible (target: 8–12)? What is the cost per app?
2. **Public apps:** find real vibe-coded apps on GitHub using the fingerprints from [2]: `.claude/` folder, `CLAUDE.md`, Lovable author meta tag, `Co-authored-by:` trailers. Check licences and that each app builds in the WS2 sandbox.
3. **Existing benchmarks to evaluate:** OWASP Juice Shop (the security study used it to measure recall, 95.7% [2]), JS bug datasets such as BugsJS, and the VibeApps/VibeVulns datasets from [2] if they are released. Report what each is useful for and what it cannot measure.
4. **Leakage control:** benchmark apps must stay out of the WS3 pattern library and out of any few-shot examples (RAP-Gen's leakage guard [1]). Define a split: *development* apps (tune on these) vs *held-out test* apps (report on these only).

**B. Bugs and ground truth**
1. **Seeded bugs:** design a seeding procedure based on the real vulnerability classes and failure modes in [2]: missing RLS, client-side-only auth, price taken from the client, unverified webhook, secret in `VITE_*` env, demo placeholders (TODO auth, Base64 "encryption"), incomplete change propagation (guard added to new routes only). Plus functional bugs (off-by-one in cart totals, wrong status codes). Manual seeding vs mutation-based seeding: compare.
2. **Natural bugs:** bugs that already exist in public apps, confirmed by a human.
3. **Failure-verdict labels:** for a set of failing generated tests, label each as `test_wrong | code_wrong | environment_issue | ambiguous`. Use **two annotators** and report **Cohen's κ** (the security study reached κ = 0.87 [2]). Write the labelling guideline first.
4. Store everything in a versioned **ground-truth file** per app.

**C. Baselines**
1. **General-purpose agent baseline:** one off-the-shelf coding agent (for example Claude Code, Codex CLI, OpenHands or SWE-agent, the harnesses listed by Macedo [8]) prompted to "find bugs, write tests and fix this repo". Same budget as RepoPilot.
2. **Code-only judge** for failure attribution (the WS4 hypothesis baseline).
3. **Classic test generation** where applicable (no-LLM or single-prompt LLM tests).
4. **Ablations:** RepoPilot with one stage removed at a time (no RAG, no knowledge graph, no intent evidence, no pattern retrieval, no suggest stage). SGAgent's ablations (51.3% → 38.0% without the suggest stage, → 44.0% without the graph [3]) are the model to follow.

**D. Metrics and experiment runner**
1. Metrics per stage, agreed with each owner: retrieval Recall@k (WS1); bugs found, false-positive rate, coverage and mutation score (WS2); scanner precision/recall per check family and repair success without regressions (WS3); verdict accuracy, calibration and abstention rate (WS4); cost and time per app (everyone).
2. **Repeated runs:** every configuration runs at least 3 times; report mean and spread. The security study found 22% of identical-run cells changed outcome [2], and TestAgent is criticised for single-run results (Farag's summary).
3. A scripted runner: one command runs configuration × app × seed, stores every artifact and trace, and produces a results table. No hand-edited numbers (a response to the self-reported results in Agentic RAG [4]).
4. Statistical comparison: which test to use when comparing two configurations on the same apps (for example a paired test with bootstrap confidence intervals).

### 7.3 Inputs you need

| Input | From |
|---|---|
| Evaluation protocol and research questions | WS4 |
| Sandbox that builds and runs each app | WS2 |
| Metric definitions and stage outputs per workstream | WS1, WS2, WS3, WS4 |
| Pattern library contents (to check for leakage) | WS3 |
| One sample app from each team member | Everyone (Section 10) |

### 7.4 Outputs you deliver

- `benchmark_manifest.json`: each app with source, commit SHA, stack, split (dev/test), licence, build status, saved prompts location.
- `ground_truth/<app>.json`: seeded and natural bugs (location, class, OWASP category, how to trigger) and labelled failure verdicts with annotator IDs.
- Labelling guideline and the inter-annotator agreement result.
- Baseline definitions and run scripts.
- Experiment runner design and the results-table format.

### 7.5 Reading to extend

Evaluation sections of CAT, RepoMem and SGAgent (SWE-bench, SWE-bench-Lite/Verified/Live setup); the vibe-coding security study Sections 3–4 and 7 (dataset building, audit, replay design); TestAgent and TestGen-LLM evaluation setups; guidance on benchmark contamination and Cohen's κ.

---

## 8. Interface Contracts Between Workstreams

| Artifact | Producer | Consumers | Must contain (minimum) |
|---|---|---|---|
| `repo_profile.json` | WS1 | WS2, WS3, WS4 | commit SHA, stack, versions, scripts, env vars, routes, tables, AI fingerprints, size in tokens |
| Retrieval tools | WS1 | all agents | `search_code`, `get_symbol`, `neighbors`, `repo_map`, `get_file` |
| `static_findings.sarif` | WS3 | WS2 (risk), WS4 (attribution, report) | rule ID, location, severity, OWASP category |
| `risk_map.json` | WS2 | WS2 planner, WS4 report | ranked units/flows, score, reasons |
| `test_plan.json` | WS2 | WS2 generator, WS4 attribution | requirement, case type, target, `intent_evidence[]` |
| `execution_result.json` | WS2 | WS4, WS3 | per test: status, error class, trace, runs, flaky flag, coverage delta |
| `failure_verdict.json` | WS4 | WS2 (test fix), WS3 (repair), report | verdict, confidence, evidence citations, question-for-owner |
| `repair_proposal.json` | WS3 | WS2 (re-run), WS4 | locations, plan, diff, pattern ID, attempt |
| `validation_report.json` | WS3 (gates) using WS2 runners | WS4 | each gate pass/fail with numbers |
| `trace_event` | everyone (via WS4 logger) | WS4 report | agent, step, tool, tokens, time, result |
| `benchmark_manifest.json` | WS5 | everyone | app list, commit SHA, dev/test split, build status |
| `ground_truth/<app>.json` | WS5 | WS5 runner, WS4 evaluation | bug locations and classes, labelled verdicts, annotator IDs |
| Results table | WS5 runner | WS4 report, everyone | configuration, app, run, metric values, cost, time |

**Conventions (WS4 to confirm):** JSON with a `schema_version` field; every artifact carries `run_id`, `commit_sha` and `created_by`; file paths relative to the repo root; line ranges 1-indexed.

---

## 9. Context-Window Strategy Across the Pipeline

Maro owns this section's final recommendation. Each owner reports what *their* agent needs. Starting hypothesis:

| Agent | Context need | Proposed strategy |
|---|---|---|
| Code understanding | Whole-app overview | **Repo map** (file tree plus ranked signatures) within a fixed token budget. If the app fits (about 8k LOC), test full-repo context as an ablation. |
| Risk analysis | Findings and structure, not raw code | Scanner summaries + graph metrics + repo map; pull code only on demand. |
| Test planning | One unit or flow + its intent | Focal code + intent evidence retrieved via RAG. |
| Test generation | Narrow and precise | Focal unit + dependency signatures + types + one example test. Small window; many cheap calls. |
| Failure attribution | Test + failure + intent, from independent sources | Fixed slots: test, trace, focal code, plan item, intent evidence, related findings. Truncate traces to the frames that belong to the project. |
| Repair | Localised code + plan + pattern | Localised snippets + repair plan + one retrieved pattern + failing evidence. Output as diff or search/replace. |
| Orchestrator (long run) | Many steps over a long run | **Never accumulate raw history.** State lives in artifacts. If an agent's inner loop runs long, use CAT-style layout: fixed segment (system + task) + summarised long-term memory + last *k* steps verbatim [10]. Cache the fixed segment (prompt caching). |

Two principles: (1) artifacts, not chat history, carry state between agents; (2) every agent gets a **declared token budget**, logged per run, so cost per app is measurable. For reference, CAT kept context under 32k tokens over 500 rounds and SGAgent cost $1.48 per issue [10], [3].

---

## 10. Cross-Cutting Decisions (Everyone)

Bring an opinion on each of these to the meeting:

1. **Implementation language:** Python for the orchestrator and agents (strongest agent/RAG ecosystem), with Node tooling called inside the sandbox for the JS/TS app. Agree or propose otherwise.
2. **LLM choice:** one strong model for reasoning-heavy agents (attribution, repair, planning) and a cheaper model for high-volume calls (test generation, classification). Compare at least two providers on cost and structured-output reliability. Keep models swappable behind one interface.
3. **Sample apps:** each person brings **one** real React/Vite + Supabase app (generated with Lovable, Bolt or Claude Code, or found on GitHub) so all experiments start from the same 5 apps; WS5 adds them to the shared benchmark.
4. **Repository layout** for our own code (monorepo with `ingest/`, `analysis/`, `testing/`, `repair/`, `orchestrator/`, `schemas/`).

---

## 11. Timeline and Discussion Meeting

| When | What |
|---|---|
| Day 1–2 | Read this plan. WS4 circulates **schema pack v0**. Everyone picks one sample app. |
| Day 3–10 | Research and small spikes. WS2 gets the sandbox running one sample app early because others depend on it. |
| Day 11 | Each person submits their technical report (template in `03_Technical_Report_Template.md`). |
| Day 12 | Everyone reads all five reports **before** the meeting and writes 2 questions per report. |
| Day 13 | **Discussion meeting** (about 2 hours). |
| Day 14 | WS4 publishes the frozen architecture and schemas v1. Implementation starts. |

### 11.1 Meeting agenda

1. Each owner presents for 15 minutes: approach chosen, alternatives rejected and why, **inputs → process → outputs**, open risks.
2. Interface check (20 min): walk Section 8's table artifact by artifact. Does the producer's output match what the consumer needs?
3. Context and cost check (10 min): sum the token budgets and estimate cost per app.
4. Decisions log (10 min): record every decision with owner and date.

### 11.2 What every report must contain

The minimum is listed here; the full structure is in the writing guide:

- **Inputs:** what you need, in which format, from whom.
- **Process:** the steps, tools and models you propose, with a diagram.
- **Outputs:** the artifacts you produce, with schema sketches.
- **Evidence:** papers, docs and (ideally) a spike result showing it works.
- **Alternatives considered** and why they were rejected.
- **Risks and open questions.**

---

## 12. References

[1] W. Wang, Y. Wang, S. Joty and S. C. H. Hoi, "RAP-Gen: Retrieval-Augmented Patch Generation with CodeT5 for Automatic Program Repair," in *Proc. ESEC/FSE*, 2023. arXiv:2309.06057.
[2] Deng, Fan and Meng, "Understanding the (In)Security of Vibe-Coded Applications," arXiv:2606.23130v4, 2026.
[3] Zhang et al., "SGAgent," arXiv:2602.23647v2, May 2026 (as summarised by Hussein).
[4] Hariharan et al., "Agentic RAG for test artifact generation," Apple (as summarised by Ziad).
[5] Wang et al., "RepoMem: Repository Memory for code localisation," in *Proc. ICLR*, 2026 (as summarised by Hussein).
[6] Zhang et al., "TestAgent," 2026 (as summarised by Farag).
[7] N. Alshahwan et al., "Automated Unit Test Improvement using Large Language Models at Meta," in *Proc. FSE*, 2024.
[8] Macedo, "What makes an agent harness" (as summarised by Ziad).
[9] S. Lahiri et al., "Interactive code generation via test-driven user-intent formalization (TiCoder)," Microsoft Research.
[10] Liu et al., "Context as a Tool (CAT)," in *Findings of ACL*, 2026 (as summarised by Hussein).
[11] Team RepoPilot, "Project Understanding: Literature Synthesis," internal, 2026.

> **Note:** *Project Understanding* cites a "RepoPilot project brief, sections 1–6". That brief is not in the `Papers/` folder. If it exists, every owner should check this plan against it.
