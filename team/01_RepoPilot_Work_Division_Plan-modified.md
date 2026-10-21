# RepoPilot: Five-Person Research and Work Plan

**Project:** RepoPilot, an evidence-driven multi-agent framework for automated software quality assurance and repair
**Team:** Farag · Maro · Ziad · Omar · Hussein
**Phase:** Research and planning only. No implementation in this round.
**Document:** Deliverable 1 of 2, version 1.0 (modified), 14 October 2026
**Companion:** `02_Technical_Report_Writing_Guide-modified.md` (Deliverable 2)

---

## Summary

RepoPilot takes an existing repository, usually one generated mostly by AI tools, and tests it, diagnoses failures, repairs what it can, and writes an evidence-backed quality report [TD]. This plan splits the research into five complementary assignments: repository access, code intelligence, RAG and context strategy (Maro); test planning, generation and the execution environment (Farag); deterministic technical analysis and bounded repair (Omar); system architecture, orchestration, failure attribution and integration (Ziad); and evaluation design (Hussein). Each person answers a defined research question, compares options against explicit criteria, and designs (but does not yet run) the validation that would settle the choice. Each then brings a report written to the shared schema. The round takes about 10 working days and ends in a decision session that freezes the architecture. Tool names are offered as candidates to investigate, not decisions.

---

## Contents

1. Evidence Inspected
2. Project Context from the Evidence
3. Key Technical Decisions: Options and Trade-offs
4. Assignment Overview
5. Assignment A1: Repository Access, Code Intelligence, RAG and Context Strategy (Maro)
6. Assignment A2: Test Planning, Test Generation and Execution Environment (Farag)
7. Assignment A3: Technical Analysis and Bounded Repair (Omar)
8. Assignment A4: Architecture, Orchestration, Failure Attribution and Integration (Ziad)
9. Assignment A5: Evaluation Design, Benchmark and Baselines (Hussein)
10. Interfaces Between Assignments
11. Implementation Risks Identified Now
12. Sequence, Checkpoints and Time Estimates
13. Final Team Decision Session
14. Assumptions, Unavailable Materials and Open Decisions
15. Source Register

---

## 1. Evidence Inspected

### 1.1 Project structure

| Path | Type | Role |
|---|---|---|
| `tech_description.md` | Markdown | Capstone technical description (the brief) |
| `Papers/2309.06057.pdf` | Full paper, 13 pages | RAP-Gen (Wang et al., ESEC/FSE 2023) |
| `Papers/Understanding the (In)Security of Vibe-Coded Applications.pdf` | Full paper, 15 pages | Deng, Fan and Meng, arXiv:2606.23130v4 |
| `Papers/Farag-LLMs for Code & Test Generation CodeT5, TestGen-LLM, TestAgent (1).pdf` | Team summary, 7 slides | CodeT5, TestGen-LLM, TestAgent |
| `Papers/Hussein-Three Research Papers.pdf` | Team summary, 10 slides | CAT, RepoMem, SGAgent |
| `Papers/Ziad - Three Papers Intent, RAG Agents, and Harnesses.pdf` | Team summary, 10 slides | TiCoder, Agentic RAG (Apple), Macedo |
| `Papers/Omar-Summary.pdf` | Team summary, 10 slides | RAP-Gen and the vibe-coding security paper |
| `Papers/Project Understanding.pdf` | Team synthesis, 12 slides | Cross-paper synthesis and pipeline mapping |

There are **no implementation files** in the project folder. The `team/` folder contains only the planning documents written in this session.

### 1.2 How each file was reviewed

| File | Coverage | Method and limits |
|---|---|---|
| `tech_description.md` | Complete | Read in full. The ASCII architecture diagram's box-drawing characters are stored in a legacy encoding and render as garbage, but the stage names are readable. |
| RAP-Gen (`2309.06057.pdf`) | All 13 pages | Text extracted page by page and read in full. The extractor reported 16 stream errors (likely embedded images). Equations and figures were not visually inspected, so Figures 2–6 were read only through captions and surrounding text. A handwritten-style note on page 1 reads "Knowledge-base that a RAG could retrieve from" (a team annotation, not paper content). |
| Vibe-coding security paper | All 15 pages | Text extracted page by page and read in full. 53 stream errors (likely images). **Figure 1 (technology shares) extracted with scrambled labels**, so per-technology percentages from that figure are taken from Omar's summary or flagged "verify". A note on page 6 reads "Maybe know the intention of the app to correct the logic if it was wrong" (a team annotation). |
| Four team summaries | All slides | Read in full; text extraction was clean. Charts in the slides were read through their text labels only. |
| `Project Understanding.pdf` | All 12 slides | Read in full. |
| IET *Guide to Technical Report Writing* | All 18 pages | Downloaded from the link the team provided and read in full. Used only for Deliverable 2. **No other web source was consulted for this plan.** |

### 1.3 What could not be reviewed directly

- **Nine of the eleven papers exist only as team summaries.** CodeT5, TestGen-LLM, TestAgent, CAT, RepoMem, SGAgent, TiCoder, Agentic RAG and Macedo are known only through slides by Farag, Hussein and Ziad. Every claim about them in this plan is second-hand and cited to the summary page. Owners should read the originals before relying on a number.
- **The "RepoPilot project brief" (sections 1–6)** is cited on every slide of *Project Understanding* [PU p.2, p.11] but is **not in the folder**. The target stack, the verdict labels (`test_wrong`, `code_wrong`, `ambiguous`, `environment_issue`) and the research questions RQ1, RQ2 and RQ4 come from that brief via *Project Understanding*, not from `tech_description.md`.

### 1.4 How citations work in this document

- Sources are cited as `[KEY p.N]`. Keys are listed in Section 15. For summaries, p.N is the slide number.
- Statements are labelled where it matters:
  - **Evidence:** reported by a source, cited.
  - **Recommendation:** this plan's proposal.
  - **Open:** unresolved; to be investigated or decided.
- **Tool names** (for example tree-sitter, Semgrep, Vitest, LangGraph) come from general engineering knowledge, not from the project papers, unless a citation is given. They are candidates to investigate in official documentation, not verified findings.

---

## 2. Project Context from the Evidence

| Topic | Evidence | Source |
|---|---|---|
| System scope | Orchestrator plus agents for code understanding, risk analysis, test planning, generation, execution, failure analysis, repair and review. Bounded iteration, structured artifacts between agents, quality gates. | [TD] |
| Research core | Failure attribution: is a failing generated test wrong, or is the application wrong? | [TD]; [PU p.2] |
| Verdict labels | `test_wrong`, `code_wrong`, `ambiguous`, `environment_issue`, with calibrated confidence and abstention | [PU p.2] (from the missing brief) |
| First target stack | React/Vite + Supabase + Stripe, e-commerce and CRUD apps | [PU p.2] (from the missing brief) |
| Why that stack | 96.17% of 9,041 vibe-coded apps are web apps. React and Vite dominate. About 55% use Supabase. | [VC p.5–6, §4]; [OS p.5] |
| Typical app size | Median 8,254 LoC in 100 files. 90th percentile 20,239 LoC in 193 files. 95.62% exceed 5,000 LoC. | [VC p.5, §4] |
| Development history | Median development span 8.39 days, but 64.22% have at least 25 commits. Very high commit density for short projects. | [VC p.5–6, §4] |
| Where bugs are | 91.0% of 200 audited deployed apps had at least one vulnerability. Top classes: broken access control 28.58%, injection 16.78%, authentication failures 14.84%. Backend code holds 52.70%. | [VC p.6–7, §5, Table 2] |
| Why bugs appear | Eight failure modes. Hidden security rules (unstated requirements) cause 55.5%; function-fix side effects (an error "fixed" by weakening security) 8.4%; forgotten TODO obligations 4.2%. | [VC p.8–10, §6, Fig. 3] |
| Agents know but do not act | In 90 of 434 insecure runs (20.7%) the agent named the risk and shipped insecure code anyway. | [VC p.12, §7] |
| Run-to-run variance | 22.0% of vulnerability-configuration cells differed across three identical runs. | [VC p.12, §7] |
| Retrieval can hurt | A randomly retrieved fix example scored below no retrieval (52.98 vs 53.46 EM on TFix). | [RG p.10, Table 7] |

**Evidence relevant to repository navigation.** The security study's auditing agents first analysed "repository structure, framework usage, and technology stack" and then invoked technology-specific sub-agents [VC p.4, §3.2]. It also identified AI-generated repositories through fingerprints: a `.claude/` directory, a Lovable author meta tag, and `Co-authored-by` or "Generated with Claude Code" commit trailers [VC p.3–4, §3.1].

---

## 3. Key Technical Decisions: Options and Trade-offs

This section frames the cross-cutting decisions. No option is assumed necessary. Each assignment investigates its rows and proposes a validation, which runs later, during implementation.

### 3.1 How the agent gets and navigates the repository

| Option | How it works | For | Against | Evidence |
|---|---|---|---|---|
| **N1 Full-context packing** | Concatenate the repo (filtered) into the prompt | Simple; nothing missed | Median app is 8,254 LoC and the 90th percentile 20,239 LoC [VC p.5], so token cost scales with size; dilutes attention | No paper tests it for this task |
| **N2 Tool-based exploration** | Agent loop with list/read/search tools, as in coding-agent harnesses | Flexible; reads only what it needs | Nondeterministic; cost varies; may miss files | Macedo: all six real harnesses share loop + tools + context + control [ZS p.7–8] |
| **N3 Pre-built index + retrieval tools** | Parse once into symbols, graph and vectors; agents query them | Repeatable; cheap per query; structural queries (callers, tables) | Upfront work; index quality limits everything | SGAgent: 51.3% → 44.0% without its knowledge graph [HS p.8]; TestAgent uses a test knowledge graph [FS p.5] |
| **N4 Hybrid: profile → repo map → index → tools** | Deterministic stack profile first, then a compact repo map, index-backed retrieval and tool reads on demand | Combines the strengths above | Most components to build | Security-study auditors profiled the stack first, then dispatched specialised sub-agents [VC p.4] |

**Recommendation:** investigate N4 as the main candidate, with N1 as a cost/quality baseline. This is plausible for small apps but unmeasured.
**Validation (later):** run the same localisation and test-planning tasks under N1, N2 and N4 on benchmark apps. Compare file-localisation accuracy, tokens and variance across repeated runs.

### 3.2 How technical analysis is done

| Option | For | Against | Evidence |
|---|---|---|---|
| **T1 Deterministic scanners only** | Repeatable, cheap, blocking checks | Misses logic and intent bugs; false positives | Paper recommends compiling implicit requirements into a checkable rule set enforced like policy-as-code [VC p.13, §8] |
| **T2 LLM audit only** | Finds logic and context-dependent issues | Variance; awareness-action gap; cost (2.85 billion tokens for 200 apps in the study [VC p.4–5]) | [VC p.12] |
| **T3 Scanners + LLM triage + execution confirmation** | Scanners for recall, LLM to explain and prioritise, tests or probes to confirm | Most complex | Study used audit agents → a validation agent tracing input to sink with harmless probes → two humans [VC p.5, §3.2]; "execution is the evidence" [PU p.8] |

**Recommendation:** investigate T3. The decision criterion is that no finding is reported as confirmed without execution or human evidence.
**Validation (later):** precision and recall per check family on seeded bugs [PU p.11].

### 3.3 Which RAG, for which corpus

RepoPilot retrieves from **four different corpora**. One RAG design need not fit all four.

| Corpus | Content | Candidate retrieval | Evidence and caution |
|---|---|---|---|
| **Code** | Source, config, migrations, tests | Hybrid lexical + dense, plus graph expansion (callers, tables, policies) | Hybrid beat either alone in RAP-Gen (54.15 vs 53.88/53.93 EM) [RG p.10, Table 7]; graph helped SGAgent [HS p.8]; Agentic RAG reports 65.2% → 87.1% → 94.8% (self-reported, one project) [ZS p.6, p.10] |
| **Intent** | README, docs, UI text, types and schemas, commit messages, TODOs, `CLAUDE.md` | Lexical + dense with source-type metadata; every hit cites its source | Intent must come from outside the code [PU p.9]; commit history is weak for thin histories (−13.1 points) [HS p.6] |
| **Fix patterns** | 10–20 verified bug → fix pairs | Hybrid lexical + dense, top-1, always compared with "no retrieval" | Random retrieval < no retrieval [RG p.10]; library size and rules from the brief [PU p.10]; top-k > 1 gave no gain in RAP-Gen [RG p.5] |
| **Run artifacts** | Earlier verdicts, plans, results in the same run | Structured lookup by ID, not semantic search | Artifacts, not chat memory, carry state [TD] |

Options to compare for the code corpus: **none (long context)**, **lexical only**, **dense only**, **hybrid**, **hybrid + graph**, **agentic retrieval** (the agent decides when and what to retrieve).

**Note on RAP-Gen:** it trained its own dense retriever contrastively on large bug-fix corpora [RG p.5, §3.3]. With a 10–20 item pattern library, training a retriever is likely unnecessary, but that is a **recommendation to verify**, not evidence.

**Validation (later):** retrieval measured on its own (for example Recall@k against labelled relevant files), including a random-retrieval control, as the brief requires [PU p.10].

### 3.4 Where a specialised context-window strategy is needed

| Stage | Need | Candidate strategy | Evidence |
|---|---|---|---|
| Repo overview | Breadth | Compact repo map within a fixed budget | — (Open) |
| Test generation | Precision, many calls | Small focused window: focal unit, signatures, types, one example | TestAgent retrieves context per method [FS p.5] |
| Failure attribution | Independent evidence | Fixed slots: test, trace, focal code, intent evidence, related findings | Intent from outside the code [PU p.9] |
| Repair | Localised edit | Localised snippets + plan + one retrieved pattern | Localise → suggest → fix; suggest stage +13.3 points [HS p.7–8]; longer buggy inputs are harder to fix [RG p.9, Fig. 5] |
| Long agent loops | Do not overflow | Fixed segment + summarised long-term memory + last *k* steps | CAT: under 32k tokens across 500 rounds; 57.6% vs 49.8% ReAct [HS p.3–4]; its summaries are unverified [HS p.10] |

**Open:** the token size of real target apps. A rough estimate of the median app is ~80k tokens, but this is an **unverified assumption** (about 10 tokens per line is a rule of thumb, not a measurement). Whether full-repo context is affordable is therefore unknown.

---

## 4. Assignment Overview

| ID | Owner | Assignment | Covers (from the required areas) | Papers already read |
|---|---|---|---|---|
| A1 | **Maro** | Repository access, code intelligence, RAG and context strategy | Repository access, agent navigation, RAG, context windows | Uses Hussein's summary (RepoMem, SGAgent, CAT) and Ziad's (Agentic RAG) |
| A2 | **Farag** | Test planning, test generation and execution environment | Technical analysis (dynamic), execution evidence | CodeT5, TestGen-LLM, TestAgent |
| A3 | **Omar** | Technical analysis (static and security) and bounded repair | Technical analysis (static), repair, risk | RAP-Gen, vibe-coding security paper |
| A4 | **Ziad** | Architecture, orchestration, failure attribution and integration | System architecture, agent workflow, integration | TiCoder, Agentic RAG, Macedo |
| A5 | **Hussein** | Evaluation design, benchmark and baselines | Evaluation, run variance, measurement | CAT, RepoMem, SGAgent (all evaluated on SWE-bench-style benchmarks [HS p.2]) |

**Why this division.** A2–A5 follow each person's literature. Maro takes A1 so that Hussein can own evaluation, which nobody else covers and which matches the benchmark-heavy evaluation in his papers. Maro will lean on Hussein's summary for RepoMem, SGAgent and CAT. Ziad's Agentic RAG material feeds A1 as well. **Implementation risks** are owned by everyone: each assignment lists its own, and Section 11 consolidates them.

---

## 5. Assignment A1: Repository Access, Code Intelligence, RAG and Context Strategy (Maro)

**Research question.** How should RepoPilot obtain an untrusted repository, build a navigable representation of it, and give each agent the right context within a budget?

**Scope.** In: input forms, cloning and pinning, safety of handling untrusted code, stack profiling, parsing and graphs, the four retrieval corpora (Section 3.3), and the context strategy per stage (Section 3.4). Out: test execution (A2), scanner rules (A3).

**Inputs and materials.** [TD]; [VC p.3–5] (fingerprints, scale, auditor workflow); [HS p.3–10]; [ZS p.5–6, p.10]; [RG p.2, p.5, p.10]; [PU p.9–11]; artifact conventions from A4.

**Investigation process.**
1. List supported inputs (public URL, private repo with token, archive upload) and decide what v1 needs.
2. Compare full clone vs shallow clone. Evidence: short but commit-dense histories [VC p.5–6] mean commit messages may be cheap, useful intent evidence. Decide whether to pin a commit SHA per run.
3. Define safe handling: where cloning and dependency installation happen (coordinate with A2's sandbox), and how secrets are detected and redacted before any content reaches an external model (coordinate with A3).
4. Design deterministic **stack profiling** from manifest and config files, including AI fingerprints [VC p.3–4] as intent sources.
5. Compare parsing approaches (syntax-tree parsers vs full type-aware compiler APIs) and graph types (module imports, calls, component tree, routes, database tables and access policies).
6. Propose a knowledge-graph schema. Starting points: SGAgent's 3 entity types / 7 relations [HS p.7] and Agentic RAG's 15 edge types such as Requires, Validates and Covers [ZS p.5].
7. For each corpus in Section 3.3, list the retrieval options and choose a candidate with criteria.
8. Draft the per-stage context budgets (Section 3.4) with each stage's owner.

**Options and decision criteria.**

| Decision | Options | Criteria |
|---|---|---|
| Navigation | N1–N4 (Section 3.1) | Localisation quality, tokens per app, determinism, build effort |
| Chunking | Fixed-size text vs syntax-aware (function/component/policy) | Retrieval precision, chunk coherence |
| Code retrieval | Lexical, dense, hybrid, hybrid + graph, agentic | Evidence in Section 3.3; cost; ease of measuring |
| Embeddings and store | Local vs hosted models; simple vs graph-capable stores | Licence, cost, metadata filtering, team familiarity |
| Commit memory | Use / hint-only / skip | RepoMem's thin-history loss [HS p.6] vs commit density [VC p.5–6] |

**Validation design (to run later).** A localisation benchmark with labelled relevant files, Recall@k, a random-retrieval control, N1 vs N4 cost comparison, and token counts of benchmark apps (with A5).

**Expected output.** A report with: the ingestion flow; the `repo_profile` field list; the code-index design (graphs plus knowledge-graph schema); the retrieval tool interface (for example search, get symbol, neighbours, repo map, get file); a retrieval design per corpus; a context-budget table; and the validation design.

**Dependencies.** A2 (sandbox for cloning and installing), A3 (secret detection), A4 (artifact conventions), A5 (apps and labels for validation).

**Open questions.** Is full-repo context affordable for typical apps? Do graph edges for database access and access policies need a dedicated parser for SQL migrations?

**Expected learnings.** Whether RAG is necessary at all for apps of this size, and which corpus benefits most from retrieval.

**Presentation agenda (15 min).** Problem (2 min) → navigation options and choice (4) → RAG per corpus (4) → context budgets (3) → open questions (2).

---

## 6. Assignment A2: Test Planning, Test Generation and Execution Environment (Farag)

**Research question.** How should RepoPilot decide what to test, generate tests that run against the real app, and capture execution evidence reliably and safely?

**Scope.** In: risk ranking, requirement-based test planning, test generation and filtering, test levels, the execution sandbox design, coverage and mutation measurement, and flakiness. Out: deciding *why* a test failed (A4).

**Inputs and materials.** [TD]; [FS p.3–7]; [PU p.4, p.8, p.11]; [VC p.6–10] (what typically breaks); the repo profile from A1; scanner findings from A3; artifact conventions from A4.

**Investigation process.**
1. Define **risk ranking** inputs: scanner findings, security-sensitive areas (the top vulnerability classes [VC p.7]), structural centrality from A1, and missing existing tests.
2. Design **test planning** after TestAgent: normal, boundary and error requirements per unit or flow [FS p.5]. Each requirement records its intent source (`intent_evidence`) [PU p.9].
3. Choose **test levels** for the stack: unit/component, integration against the backend, end-to-end user flows, and **security behaviour tests** (for example access by an anonymous or a different user).
4. Adapt **TestGen-LLM's filters** (builds; passes 5 runs; adds coverage [FS p.4]) with one key change. TestGen-LLM discards failing tests, which are exactly the cases RepoPilot must explain [PU p.8]. Keep deterministic failures; discard only build failures and flaky tests.
5. Design the **execution sandbox**: isolation level, bringing up the app and its backend services locally, payment-provider test mode, network policy, resource limits, timeouts, and evidence capture (results, traces, logs).
6. Decide on **adequacy metrics**: coverage and mutation score, remembering that both are proxies [FS p.7]; TestAgent reports 83.69% mutation score vs 43.59% for EvoSuite [FS p.5].
7. Estimate run time and cost per app. Mutation testing is likely the slowest step.

**Options and decision criteria.**

| Decision | Options | Criteria |
|---|---|---|
| Isolation | Container per run vs microVM sandbox vs hosted sandbox | Security, start-up time, cost, support for nested services |
| Test frameworks | Native framework of the stack vs alternatives | Compatibility with Vite apps, reporters, coverage support |
| Flakiness | Repeat N runs (TestGen-LLM uses 5 [FS p.4]) | Time vs reliability |
| Mutation scope | Whole app vs high-risk files only vs time-boxed | Run time vs signal |

**Validation design (to run later).** Bugs detected on seeded apps, false-positive rate, mutation score, flaky-test rate, and run time per app.

**Expected output.** A report with: the risk-score design; the `test_plan` fields (including `intent_evidence`); generation context and filter rules; the sandbox architecture diagram; the `execution_result` fields; and the metric plan.

**Dependencies.** A1 (profile, retrieval), A3 (findings, regression runs after repair), A4 (schemas, verdicts), A5 (seeded apps).

**Open questions.** Can backend services be run reliably inside the sandbox? How should external services such as payments be handled? Which test level finds the top vulnerability classes most cheaply?

**Expected learnings.** The realistic cost and time to execute one app end to end, which drives the whole budget.

**Presentation agenda (15 min).** Risk → plan → generation and filters (5) → sandbox design (5) → metrics and cost (3) → open questions (2).

---

## 7. Assignment A3: Technical Analysis and Bounded Repair (Omar)

**Research question.** Which deterministic analyses should RepoPilot run, and how should it propose repairs that fix defects without weakening security?

**Scope.** In: static and security checks, stack-specific rules, finding normalisation, the repair pipeline (`code_wrong` path), the test-repair path (`test_wrong`, shared with A2), patch acceptance gates and the fix-pattern library. Out: deciding the verdict (A4).

**Inputs and materials.** [RG all pages, especially p.2, p.5–6, p.10–11]; [VC p.6–13]; [OS p.2–10]; [HS p.7–8]; [PU p.7, p.10–11].

**Investigation process.**
1. Map the **top vulnerability classes and failure modes** [VC p.7–10] to checks that can be detected statically: missing access policies, secrets in client code, client-side-only authentication, TODO placeholders on auth paths, fake encryption, unvalidated input to sinks.
2. Survey **analysis tool families** (type checker, linter, pattern-based scanner, secret scanner, dependency audit) and how their output is normalised into one format.
3. Design the **repair pipeline** after SGAgent: localise (up to 5 locations) → suggest a plan with risks → generate candidate patches [HS p.7]. The suggest stage was worth +13.3 points [HS p.8].
4. Design the **fix-pattern library** after RAP-Gen: 10–20 verified patterns [PU p.10], hybrid retrieval [RG p.5], top-1 [RG p.5], with error information in the input (removing it hurt in RAP-Gen [RG p.8–9]). Add a leakage rule that keeps benchmark apps out of the library [RG p.6]; [PU p.10].
5. Define **patch acceptance gates** enforced by code, not by the model: the failing test now passes; regression passes; no new findings; and the patch does not weaken a check. The function-fix side-effects mode [VC p.9] and the awareness-action gap [VC p.12] are why the last gate exists.
6. Set **bounds**: attempts, diff size, and which files may change (code only for `code_wrong`, tests only for `test_wrong`).

**Options and decision criteria.**

| Decision | Options | Criteria |
|---|---|---|
| Analysis mix | T1 / T2 / T3 (Section 3.2) | Precision and recall per family, cost, determinism |
| Custom rules | Pattern rules vs small purpose-built parsers (for SQL migrations) | Expressiveness, maintenance |
| Repair staging | Direct patch vs localise → suggest → fix | SGAgent ablation [HS p.8]; cost |
| Pattern retrieval | None / lexical / dense / hybrid | RAP-Gen Table 7 [RG p.10]; must beat "no retrieval" |
| Weakened-check detection | Diff rules vs syntax-tree rules vs LLM review | False negatives are dangerous; prefer deterministic |

**Validation design (to run later).** Scanner precision and recall on seeded bugs; repair success without regressions; weakened-check rate in proposed patches [PU p.11]; pattern retrieval vs no retrieval.

**Expected output.** A report with: a check catalogue mapped to the vulnerability classes; the normalised finding format; the repair pipeline diagram; the pattern-library format with 5 example entries (described, not built); the gate list; and the bounds.

**Dependencies.** A1 (repo access, retrieval), A2 (regression and mutation runs), A4 (verdicts, budgets), A5 (seeded bugs, leakage split).

**Open questions.** Can access-policy problems be detected from migration files alone, or only by running queries? How small can a library be and still help?

**Expected learnings.** Which vulnerability classes are cheap to catch statically and which need execution evidence.

**Presentation agenda (15 min).** Threat picture from the evidence (3) → check catalogue (4) → repair pipeline and patterns (5) → gates and bounds (2) → open questions (1).

---

## 8. Assignment A4: Architecture, Orchestration, Failure Attribution and Integration (Ziad)

**Research question.** What architecture lets specialised agents cooperate under enforced control, and how should a failing test be attributed to the test, the code or the environment, or reported as ambiguous?

**Scope.** In: overall architecture and agent workflow, harness control, artifact schemas, tracing, the failure-attribution method, abstention and owner questions, the review and report stage, and integration of all assignments. Out: individual stage internals.

**Inputs and materials.** [TD]; [ZS p.3–10]; [PU p.2, p.8–9, p.11–12]; [FS p.5] (TestAgent's failure voting); [VC p.12–13] (blocking, not warning); requirements from A1, A2, A3 and A5.

**Investigation process.**
1. Map RepoPilot onto Macedo's four harness conditions: loop, tools, task-aware context, and control that does not depend on the model obeying [ZS p.7]. Decide what is a fixed pipeline and what is an adaptive agent loop. Macedo classifies a fixed-graph orchestrator as not a harness [ZS p.8].
2. Define **control**: budgets (tokens, time, retries, diff size), quality gates as code, and stop rules. Evidence for blocking over warning: [VC p.12–13].
3. Draft the **artifact vocabulary** early (names and required fields), so others can write against it.
4. Design **failure attribution**:
   - Rule-based detection of environment problems first.
   - Then an evidence-based judge using intent from independent sources [PU p.9], compared against a code-only judge (the core hypothesis).
   - Consider voting (TestAgent uses three LLM voters [FS p.5]), but note that voters reading the same code share blind spots [PU p.8].
   - Add calibrated confidence with abstention to `ambiguous`.
   - Resolve ambiguity with one yes/no question to the owner after TiCoder (one query lifted MBPP pass@1 from 48.24% to 70.73% with a *simulated* user [ZS p.4, p.10]).
5. Define **tracing** of every agent step and tool call, and the structure of the final report.
6. Run the **integration check**: every artifact has one producer and named consumers (Section 10).

**Options and decision criteria.**

| Decision | Options | Criteria |
|---|---|---|
| Orchestration | Fixed pipeline / state-graph framework / custom loop / provider agent SDK | Control, resumability, tracing, model swapping, team skill |
| Tool interface | Direct function calls vs a standard tool protocol | Reuse across agents and models |
| Attribution | Rules + single judge / + voting / + intent evidence / + owner question | Verdict accuracy vs code-only judge, calibration, cost |
| Abstention | Fixed threshold vs calibrated per class | Calibration error; abstention rate the user tolerates |

**Validation design (to run later, with A5).** Verdict accuracy against human labels, calibration, abstention rate, and the intent-aware judge vs a code-only judge.

**Expected output.** A report with: the architecture diagram; harness and control design; the artifact vocabulary (v0 by checkpoint 1, v1 after the decision session); the attribution method; the trace and report structure; and the integration matrix.

**Dependencies.** Everyone. Ziad is the integration owner.

**Open questions.** Which intent sources are actually available in typical apps? Does a single yes/no question to the owner work when the "owner" is a non-expert vibe coder [VC p.12–13, §8]?

**Expected learnings.** The minimal control layer that turns separate stages into a dependable pipeline.

**Presentation agenda (15 min).** Architecture and control (5) → artifact vocabulary (3) → attribution method (5) → integration gaps found (2).

---

## 9. Assignment A5: Evaluation Design, Benchmark and Baselines (Hussein)

**Research question.** How will the team show, with repeatable evidence, that each RepoPilot stage helps and that the whole system beats simpler alternatives?

**Scope.** In: benchmark composition, bug seeding, ground-truth labelling, baselines and ablations, metrics per stage, repeated runs and statistics, and leakage control. Out: running experiments (implementation phase).

**Inputs and materials.** [HS p.2–10] (benchmark-based evaluation, ablations); [VC p.3–5, p.11–12] (dataset construction, labelling with Cohen's κ, replay design, variance); [RG p.6, p.11] (leakage guard, threats to validity); [FS p.6–7] (proxy metrics, single-run limits); [ZS p.10] (simulated users, self-reported results); [PU p.11–12].

**Investigation process.**
1. **Benchmark sources.** Self-generated apps with saved prompts (intent ground truth); public vibe-coded apps found through the fingerprints and selection criteria in [VC p.3–4]; known-vulnerability targets (the study measured recall on OWASP Juice Shop [VC p.5]). Check whether the study's VibeApps and VibeVulns datasets are available (**Open**).
2. **Bug seeding** based on the eight failure modes and top OWASP classes [VC p.7–10]. Compare manual vs automated seeding.
3. **Labelling protocol** for failure verdicts: two annotators, written guideline, Cohen's κ (the study reached 0.87 for vulnerabilities [VC p.5] and 0.82 for root causes [VC p.8]).
4. **Baselines and ablations.** A general-purpose coding agent with the same budget; a code-only judge; RepoPilot with one stage removed at a time. Each stage must earn its place through a measured ablation [PU p.11].
5. **Repeated runs and statistics.** At least 3 runs per configuration, with spread reported, motivated by the 22.0% non-unanimous cells [VC p.12] and the single-run limits flagged in [FS p.7] and [PU p.12].
6. **Leakage control.** Development vs held-out apps; nothing from the benchmark goes into the pattern library [RG p.6]; [PU p.10].
7. **Metric catalogue** agreed with each owner (see the validation designs in Sections 5–8).

**Options and decision criteria.**

| Decision | Options | Criteria |
|---|---|---|
| App sources | Self-generated / public / known-vulnerable apps / mix | Realism, licence, buildability, ground-truth quality |
| Seeding | Manual / mutation-based / replaying real vulnerabilities | Realism vs effort |
| Ground truth | One annotator / two + κ / expert review | Reliability vs effort |
| Statistics | Means only / spread + paired tests / bootstrap intervals | Validity with few apps |

**Expected output.** A report with: the benchmark specification (sources, sizes, splits); the seeding procedure; the labelling guideline; baselines and ablation matrix; the metric catalogue; the repeated-run protocol; and a threats-to-validity section.

**Dependencies.** A2 (the sandbox decides which apps can run), A3 (leakage with patterns), A4 (research questions, verdict definitions), and every owner's metrics.

**Open questions.** How many apps are feasible to label? Is a simulated owner acceptable for the yes/no question, given TiCoder's simulated-user caveat [ZS p.10]?

**Expected learnings.** Which claims the project can actually support with the data it can afford.

**Presentation agenda (15 min).** What we must prove (3) → benchmark and seeding (5) → labels and baselines (4) → statistics and threats (3).

---

## 10. Interfaces Between Assignments

| Artifact (working name) | Producer | Consumers | Minimum content |
|---|---|---|---|
| `repo_profile` | A1 | A2, A3, A4 | commit SHA, stack, versions, entry points, env vars, routes, tables, AI fingerprints, size |
| Retrieval tools | A1 | all agents | search, symbol lookup, neighbours, repo map, file read |
| `static_findings` | A3 | A2 (risk), A4 | rule, location, severity, vulnerability class |
| `risk_map` | A2 | A2, A4 | ranked targets with reasons |
| `test_plan` | A2 | A2, A4 | requirement, case type, target, `intent_evidence` |
| `execution_result` | A2 | A3, A4 | status, error class, trace, repeat count, flaky flag, coverage delta |
| `failure_verdict` | A4 | A2, A3, report | verdict, confidence, evidence citations, owner question |
| `repair_proposal` | A3 | A2, A4 | locations, plan, diff, pattern ID, attempt |
| `validation_report` | A3 (using A2 runners) | A4 | each gate with pass/fail and numbers |
| `trace_event` | everyone, via A4 | A4, A5 | agent, step, tool, tokens, time, outcome |
| `benchmark_manifest`, `ground_truth` | A5 | everyone | apps, splits, bugs, labelled verdicts |

Names and fields are **working proposals** until A4 issues the vocabulary at checkpoint 1.

---

## 11. Implementation Risks Identified Now

| # | Risk | Evidence | Owner | Mitigation to investigate |
|---|---|---|---|---|
| R1 | Backend services and payments cannot run reliably in a sandbox | — (Open) | A2 | Design local service stack and test modes early |
| R2 | Retrieval adds noise instead of signal | Random retrieval < none [RG p.10] | A1, A3 | Measure retrieval on its own with a random control |
| R3 | Judge copies the code's bugs | [PU p.2, p.9] | A4 | Independent intent sources; code-only baseline |
| R4 | Repairs weaken security | Function-fix side effects [VC p.9]; awareness-action gap [VC p.12] | A3 | Deterministic weakened-check gate |
| R5 | Results not reproducible | 22.0% non-unanimous cells [VC p.12] | A5 | ≥3 runs, report spread, scripted runs |
| R6 | Cost per app too high | Study audit used 2.85B tokens for 200 apps [VC p.4–5]; SGAgent $1.48 per issue [HS p.8] | A4, A1 | Budgets per agent; full-context vs RAG comparison |
| R7 | Thin intent sources | Short histories [VC p.5]; RepoMem thin-history loss [HS p.6] | A1, A4 | Multiple sources; abstain when evidence is weak |
| R8 | Benchmark leakage | [RG p.6]; [PU p.10, p.12] | A5, A3 | Dev/test split; library audit |
| R9 | Untrusted code harms the host or leaks secrets | — (Open) | A1, A2 | Sandbox-only install; redaction before model calls |
| R10 | Second-hand evidence is wrong | Nine papers known only via summaries (Section 1.3) | All | Read originals before citing numbers in final reports |

---

## 12. Sequence, Checkpoints and Time Estimates

### 12.1 Sequence

| Day | Activity | Checkpoint |
|---|---|---|
| 0 | Kick-off (30 min): read this plan; confirm owners; agree tool and report conventions | — |
| 1–2 | Everyone: read assigned sources and originals where possible. Ziad drafts the artifact vocabulary v0. | **C1 (day 2, 20 min):** vocabulary v0 shared; each person lists their top 5 questions |
| 3–5 | Options analysis and design drafts | **C2 (day 5, 30 min):** each person shows shortlisted options and the inputs they need from others; interface gaps logged |
| 6–8 | Write reports to the shared schema; draft validation designs | — |
| 9 | Submit reports (v1.0) | **C3:** all five reports in the shared folder |
| 10 | Everyone reads all reports and writes 2 questions per report | — |
| 11 | **Final team decision session** (Section 13) | Decisions log published by Ziad |

### 12.2 Time estimates (research only, about 2–2.5 hours a day alongside courses)

| Owner | Reading | Options and design | Report | Total | Calendar |
|---|---|---|---|---|---|
| Farag (A2) | 10–12 h | 4–6 h | 5–6 h | 19–24 h | 8–10 days |
| Ziad (A4) | 8–10 h | 5–6 h (+4 h vocabulary) | 5–6 h | 18–22 h + 4 h | 8–9 days |
| Maro (A1) | 8–10 h | 4–5 h | 5 h | 17–20 h | 7–9 days |
| Omar (A3) | 8–9 h | 4–5 h | 5 h | 17–19 h | 7–8 days |
| Hussein (A5) | 8–9 h | 4–5 h | 5 h | 17–19 h | 7–8 days |

These estimates are assumptions, not measurements. Allow 3 weeks during exams.

---

## 13. Final Team Decision Session

**Length:** about 2.5 hours. **Chair:** Ziad (integration owner). **Note-taker:** rotates.

| # | Item | Time |
|---|---|---|
| 1 | Five presentations (Sections 5–9 agendas), 15 min each, questions held to the end | 75 min |
| 2 | Interface walk-through of Section 10: does every consumer get what it needs? | 20 min |
| 3 | Decisions in Section 14.3: decide, or assign an owner and a deadline | 30 min |
| 4 | Budget check: sum token and time budgets; estimated cost per app | 10 min |
| 5 | Risks (Section 11): confirm owners | 10 min |
| 6 | Next steps and the implementation-phase plan | 5 min |

**Decisions log format:**

| ID | Decision | Options considered | Chosen | Evidence | Owner | Date | Revisit if |
|---|---|---|---|---|---|---|---|

---

## 14. Assumptions, Unavailable Materials and Open Decisions

### 14.1 Assumptions

1. The team has five members with the assignments above.
2. This round is research and design only. Validation experiments are designed now and run later.
3. The target stack and verdict labels from *Project Understanding* reflect the missing project brief correctly.
4. About 2–2.5 hours a day per person is available.
5. Token-size estimates for apps are rough until measured.

### 14.2 Unavailable or partially reviewed materials

1. **RepoPilot project brief** (cited by *Project Understanding*): not in the folder.
2. **Original papers** for CodeT5, TestGen-LLM, TestAgent, CAT, RepoMem, SGAgent, TiCoder, Agentic RAG and Macedo: only the team summaries are available.
3. **Figures** in both full papers were not visually inspected; Figure 1 of the vibe-coding paper extracted with unreadable labels.
4. **Release status of VibeApps and VibeVulns**: not stated in the text reviewed.

### 14.3 Decisions the team still needs to make

| # | Decision | Input from |
|---|---|---|
| D1 | Repository navigation approach (N1–N4) | A1 |
| D2 | Retrieval design per corpus, or no RAG for small apps | A1, A3 |
| D3 | Technical-analysis mix (T1–T3) and the initial check catalogue | A3 |
| D4 | Sandbox isolation approach and handling of backend services and payments | A2 |
| D5 | Orchestration approach and control mechanisms | A4 |
| D6 | Failure-attribution method and abstention policy | A4, A5 |
| D7 | Benchmark composition, labelling effort and statistics | A5 |
| D8 | Models used per stage and the budget per app | A4, all |
| D9 | Implementation language(s) and repository layout for our own code | All |
| D10 | Whether to obtain the missing project brief and original papers before finalising | All |

---

## 15. Source Register

| Key | File | Notes |
|---|---|---|
| TD | `tech_description.md` | Capstone technical description |
| PU | `Papers/Project Understanding.pdf` | Team synthesis; p.N = slide N; cites a project brief not in the folder |
| FS | `Papers/Farag-LLMs for Code & Test Generation CodeT5, TestGen-LLM, TestAgent (1).pdf` | p.3 CodeT5, p.4 TestGen-LLM, p.5 TestAgent, p.6 comparison, p.7 takeaways |
| HS | `Papers/Hussein-Three Research Papers.pdf` | p.3–4 CAT, p.5–6 RepoMem, p.7–8 SGAgent, p.9 comparison, p.10 limits |
| ZS | `Papers/Ziad - Three Papers Intent, RAG Agents, and Harnesses.pdf` | p.3–4 TiCoder, p.5–6 Agentic RAG, p.7–8 Macedo, p.9–10 wrap-up |
| OS | `Papers/Omar-Summary.pdf` | p.3–4 RAP-Gen, p.5–8 vibe-coding study, p.9–10 comparison and takeaways |
| RG | `Papers/2309.06057.pdf` | W. Wang, Y. Wang, S. Joty and S. C. H. Hoi, "RAP-Gen: Retrieval-Augmented Patch Generation with CodeT5 for Automatic Program Repair," ESEC/FSE '23, doi:10.1145/3611643.3616256 |
| VC | `Papers/Understanding the (In)Security of Vibe-Coded Applications.pdf` | J. Deng, Z. Fan and R. Meng, arXiv:2606.23130v4, 14 Sep 2026 |
