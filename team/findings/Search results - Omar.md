# Search Results – Omar (A3: Static/Security Analysis)

Task being researched:
> General: tsc --noEmit type errors, ESLint (with a security plugin), Semgrep (JS/TS rulesets plus our own custom rules), optionally CodeQL (heavier, more precise). Compare speed and false positives.

## Search checklist

Concepts
- [x] Static application security testing (SAST) explained
- [x] Taint analysis (source → sink)
- [x] SAST false positives vs false negatives
- [x] SARIF format

Each tool
- [x] TypeScript `tsc --noEmit` type checking and `tsconfig` strict mode
- [x] ESLint rules, `eslint-plugin-security` rules
- [x] Semgrep rule syntax, Semgrep playground, Semgrep rulesets for JS/TS/React
- [x] CodeQL for JavaScript, CodeQL data-flow analysis
- [x] Fill in the comparison table (Section 6) – speed still unknown

Supabase-specific (most important for this assignment)
- [x] Supabase Row Level Security explained (Section 7.1)
- [x] Supabase anon key vs service_role key (Section 7.2)
- [x] Supabase database linter (database advisors, Section 7)
- [x] CVE-2025-48757 (Lovable) (Section 7.3)

---

## 1. Static Application Security Testing (SAST)

SAST is a white-box testing method. It analyses source code, bytecode or binaries to find security vulnerabilities **without running the application**. OWASP: "Source code analysis tools, also known as Static Application Security Testing (SAST) Tools, can help analyze source code or compiled versions of code to help find security flaws" [19].

### 1.1 How it works
SAST acts like an automated code reviewer that reads the program's structure:
- **Code parsing:** turns code into an abstract syntax tree (AST).
- **Pattern matching:** compares code against known vulnerability patterns and secure-coding rules (for example the OWASP Top 10 categories).
- **Data-flow analysis:** tracks how user input moves from where it enters to sensitive operations (database queries, system commands), to catch missing validation. See taint analysis, Section 2.
- **Control-flow analysis:** follows branches, loops and execution paths.

### 1.2 What it detects well
1. Injection flaws (SQL, command injection, cross-site scripting/XSS)
2. Hard-coded secrets (passwords, API keys, tokens)
3. Insecure cryptography (for example MD5 for passwords)
4. Unsafe API and framework usage (for example `eval`, `dangerouslySetInnerHTML`)

### 1.3 What it detects poorly: authentication and authorization
SAST is good at finding **unsafe code that is present**, and weak at finding **checks that are missing**: a route without an authorization check, or a table without Row-Level Security (RLS). Static tools are "agnostic of the goals" of the software, so they cannot find errors in the software as a whole [1, p. 7]. OWASP lists the same weakness: it is "difficult to automate searches for many types of security vulnerabilities, including: Authentication problems, Access control issues" [19].

This matters for RepoPilot. The largest vulnerability class in vibe-coded apps is broken access control: 28.58% of vulnerabilities, affecting 64.00% of audited apps [3, p. 7, Table 2]. Generic SAST rules alone will miss much of it. We need custom rules (for example, "table created without RLS") and behaviour tests.

### 1.4 Advantages ("shift-left" security)
- **Early detection:** finds bugs while code is being written, when fixes are cheaper.
- **No running application needed:** no server or staging environment. However, some tools need dependencies installed: `tsc --noEmit` and ESLint's type-aware rules need `npm install` first, because type definitions live in `node_modules`. *(Verify per tool; record in Section 6.)*
- **Pipeline integration:** runs in IDEs, Git hooks and CI/CD.

### 1.5 Limitations
- **False positives:** flags harmless code, which someone must triage.
- **False negatives:** misses real vulnerabilities, and nobody notices, because a tool never reports what it missed [1, p. 9]. See Section 3.
- **No runtime context:** cannot see issues that appear only in a running app. OWASP: "Frequently unable to find configuration issues, since they are not represented in the code" [19].
- **Limited coverage overall:** OWASP: current SAST tools "can automatically identify only a relatively small percentage of application security flaws" [19].
- **Blind to external services:** cannot see inside third-party APIs or live infrastructure.

---

## 2. Taint Analysis

Taint analysis tracks how untrusted data flows from the point where it enters the program (a **source**) to a security-sensitive operation (a **sink**). If untrusted data reaches a sink without validation or sanitisation, the analysis reports a potential vulnerability. Among our tools, CodeQL and the paid Semgrep engine perform this across files ("cross-file taint analysis" [13]); the free Semgrep version only within a single function [12]. *(General definition from common usage; add a textbook or OWASP source if the final report needs one.)*

### 2.1 Core components
- **Sources:** where attacker-controlled data enters (HTTP request parameters, URL query, form fields, files, environment variables).
- **Sinks:** dangerous operations (SQL execution, `eval()`, `innerHTML`, file writes, system commands).
- **Sanitisers/validators:** functions that escape, filter or validate data.
- **Propagators:** assignments and functions that pass the "taint" from one variable to another.

### 2.2 How it works
1. **Mark:** data from a source is marked as tainted.
2. **Trace:** the analyser follows it through assignments, concatenations and function calls.
3. **Check:** if the data passes a recognised sanitiser, the taint is removed.
4. **Report:** if tainted data reaches a sink without sanitisation, a vulnerability (SQL injection, XSS, command injection) is reported.

Laravel example: `$request->input('sort')` (source) → `DB::raw(...)` (sink) with no validation in between = possible SQL injection.

**Open question for the tool comparison:** does the tool track taint *across files*, or only within one file? Real apps pass data through several files, so this decides how much a tool can find (Section 6).

---

## 3. Practitioner Views on SAST False Positives and False Negatives

Ami et al. [1] studied how industry practitioners choose and use SAST tools. They ran a survey (39 valid responses, mostly developers) and in-depth interviews with 20 practitioners from domains including web applications, fintech, healthcare, automotive and open source [1, pp. 2–5, 16–17]. Key findings:

- **False negatives matter more than false positives.** Nearly all participants preferred a tool that misses fewer vulnerabilities, even with many more false alarms [1, p. 8]. One participant: "False negative – that one is going to kill you."
- **High but conditional tolerance for false positives.** Some participants accepted 80% or more false positives, far above the 20% limit suggested in earlier research, as long as the tool also found real vulnerabilities. Two participants dropped tools that produced almost only false alarms [1, pp. 7–8].
- **Developers should not decide alone what is a false positive.** They often dismiss real issues or skip scans; one skipped scan cost a company millions [1, p. 9].
- **Missed vulnerabilities go unnoticed.** Because tools never report what they miss, practitioners assume the tool "just works" or that manual review will catch the rest [1, p. 9].
- **Public benchmarks are not trusted.** They are seen as too basic or biased toward the vendor's own tool [1, p. 7].
- **Main pain points:** missed vulnerabilities, unclear alert messages, and difficult CI/CD integration. Practitioners want each alert to explain why it was flagged and how to fix it [1, p. 11].

**Limitations of the study:** qualitative, only 20 interviewees recruited mostly through personal networks, single coder. The authors call the results "softly generalisable" [1, pp. 4, 11].

---

## 4. Static Analysis Results Interchange Format (SARIF)

SARIF is an open, JSON-based OASIS standard for reporting the results of static analysis tools in one common format [2].

### 4.1 Key features
- **One format for all tools:** findings from different scanners can be merged and processed the same way, instead of parsing each tool's own output.
- **Structure:** a SARIF log contains a `runs` array. Each run describes the tool, its rules, and its `results` (each with a rule ID, message, file location and severity level) [2].
- **Severity levels:** SARIF defines the levels `error`, `warning`, `note` and `none` [2]. How each tool maps its own severities (critical/high/medium/low) onto these levels is the tool's choice, not part of the standard. *(Verify per tool.)*

### 4.2 SARIF vs test-result formats

| Feature | SARIF (static analysis) | JUnit XML (test results) |
|---|---|---|
| What it records | Security weaknesses, code-quality and structural problems | Pass/fail of executed tests |
| How results are produced | By analysing code without running it | By running the code against test assertions |
| Typical finding | "Possible SQL injection on line 42" | "Test `login_with_invalid_password` failed" |
| Example tools | Semgrep, CodeQL, ESLint (via `@microsoft/eslint-formatter-sarif` [8]) | PHPUnit, JUnit, PyTest; Vitest/Jest via reporters |

**Why it matters for RepoPilot:** all our scanners should output SARIF (or be converted to it), so the risk-analysis and failure-analysis agents read one format.

---

## 5. Tool Notes

All sources below are official documentation, read on 14 Oct 2026. "Not found" means the official docs did not state it; we will measure it later on the benchmark apps.

### 5.1 `tsc --noEmit`

**What it is:** the TypeScript compiler run as a type checker only. `noEmit` means "Do not emit compiler output files like JavaScript source code, source-maps or declarations" [4]. It is a correctness tool, not a security tool.
**Laravel/C++ equivalent:** PHPStan/Larastan; `g++ -fsyntax-only`.

| Question | Answer | Source |
|---|---|---|
| What does it catch? | Type errors: wrong argument types, possibly-null values, missing properties, calls to functions that do not exist on a type. `strict` turns on 9 checks, including `strictNullChecks` and `noImplicitAny`. | [4] |
| What does it NOT catch? | Any security issue that is type-correct (injection, missing auth, missing RLS, leaked keys). | — (by definition) |
| Needs `npm install` first? | Effectively yes. By default, type definitions come from `node_modules/@types` [4], so without installed dependencies, imports fail to resolve and real errors are drowned in noise. | [4] |
| Speed? | No numbers in the docs. `skipLibCheck` lets you "Skip type checking of declaration files" to "save time during compilation at the expense of type-system accuracy". | [4] |
| False positives? | Very low for real type errors, but **depends on the project's `tsconfig`**: vibe-coded apps may not use `strict`, so we must decide whether to use their config or force stricter checks (stricter = more findings, more noise). | [4] + own reasoning |
| Custom rules? | No. | — |
| Cross-file? | Yes; the compiler checks the whole program. | [4] |
| SARIF output? | **No built-in SARIF option found.** We would convert its plain-text output to SARIF ourselves (a small script). | [4], [10] |
| Licence/cost | Free, open source. | [4] |

**Example relevance:** the vibe-coding paper describes code calling `crypto.createCipherGCM`, which does not exist in Node's `crypto` module, so data stayed unencrypted [3, p. 10]. A type checker with Node type definitions installed should flag a call to a non-existent function. *(To verify with a quick test later.)*

**Verdict for RepoPilot:** run on every app. It is cheap and catches "hallucinated API" bugs, but it needs dependencies installed, so it runs inside the sandbox (coordinate with Farag).

### 5.2 ESLint + `eslint-plugin-security` (+ React rules)

**What it is:** a rule-based linter. `eslint-plugin-security` adds security rules; its config is called `recommended` [5].
**Laravel/C++ equivalent:** PHP_CodeSniffer/PHPMD; clang-tidy.

| Question | Answer | Source |
|---|---|---|
| What does it catch? | 15 rules, for example: `detect-eval-with-expression` (eval with variables), `detect-child-process`, `detect-non-literal-fs-filename`, `detect-non-literal-require`, `detect-unsafe-regex` (regex denial-of-service), `detect-possible-timing-attacks`, `detect-object-injection`, `detect-bidi-characters` (trojan-source attacks). Plus `react/no-danger`, which flags dangerous JSX properties such as `dangerouslySetInnerHTML`, "a common source of application vulnerabilities". | [5], [6] |
| What does it NOT catch? | Most rules target **Node.js server code** (child processes, file system, `require`). In a React + Supabase frontend, few apply. Nothing about Supabase, RLS, keys or auth logic. | [5] + own reading |
| Needs `npm install`? | Yes: the plugins themselves must be installed. Type-aware rules also need TypeScript's type information: typed linting "requires TypeScript to analyze your entire project instead of just the file being linted", so these rules "are slower than traditional lint rules but are much more powerful". | [5], [7] |
| Speed? | Not found. | — |
| False positives? | **High, and the plugin says so itself:** it finds "potential security hotspots, but finds a lot of false positives which need triage by a human". `detect-object-injection` is specifically noted for false positives. | [5] |
| Custom rules? | Possible (JavaScript plugin API), but harder than Semgrep. | — |
| Cross-file? | No (rules work per file). | — |
| SARIF output? | Not built in. Use `@microsoft/eslint-formatter-sarif` (`eslint -f @microsoft/sarif -o out.sarif`), which outputs SARIF 2.1.0. | [8] |
| Licence/cost | Free, open source. | [5] |

**Verdict for RepoPilot:** run it, but **as a hint source for triage, not as proof**. Its own maintainers say its findings need human triage [5]. That fits our "recall first, then filter" idea (Section 8). Keep `react/no-danger` because it targets our stack directly.

### 5.3 Semgrep

**What it is:** a pattern-matching scanner whose rules look like code. It runs locally with `semgrep scan --config <rules.yaml>` and can combine registry rulesets with our own rule files [9].
**Laravel/C++ equivalent:** custom PHPStan/Psalm rules or clang-tidy checks, but much easier to write.

| Question | Answer | Source |
|---|---|---|
| What does it catch? | Whatever its rules describe: registry rulesets for JS/TS, plus **our own custom rules** (e.g. `service_role` key used in frontend code, Stripe secret key on the client). | [9] |
| What does it NOT catch? | **SQL files: SQL is not a supported language** (an open feature request exists). So Semgrep **cannot** check Supabase migration files for "table without RLS". It only finds SQL injection by looking at the JS/TS code that builds queries. | [11], [12] |
| Needs `npm install`? | No. It parses source files directly. | [9] |
| Speed? | Not found in docs (generally considered fast; measure later). | — |
| False positives? | Depends on the rules; custom rules can be tuned. The paid engine claims cross-file analysis can "reduce noise". | [13] |
| Custom rules? | **Easy**: YAML rules with code-like patterns; local rule files via `--config`. | [9] |
| Cross-file? | **Not in the free version.** Community Edition is "limited to single-function analysis" for JavaScript and TypeScript. Cross-function and cross-file taint analysis are only in the paid Semgrep Code (Pro engine). | [12], [13] |
| SARIF output? | Built in: `--sarif` / `--sarif-output=<file>`. | [9] |
| Licence/cost | Community Edition free; Pro engine paid. | [12], [13] |

**Verdict for RepoPilot:** main scanner for **our custom stack rules**, on every run. Known limit: the free version only sees inside one function, so data flows across functions or files are missed. We must cover those with tests (Farag) or LLM triage, or justify the paid engine.

### 5.4 CodeQL

**What it is:** GitHub's analysis engine. It builds a database from the code, then runs queries on it, including data-flow (taint) tracking.
**Laravel/C++ equivalent:** Psalm taint analysis (CodeQL itself does not support PHP); Clang Static Analyzer / Coverity.

| Question | Answer | Source |
|---|---|---|
| What does it catch? | Built-in query suites. `default` is "highly precise and return[s] few false positive" results. `security-extended` adds more queries but "may return a greater number of false positive" results. `security-and-quality` adds maintainability/reliability queries. | [14] |
| What does it NOT catch? | **SQL is not a supported CodeQL language** (supported: C/C++, C#, GitHub Actions, Go, Java, Kotlin, JavaScript, Python, Ruby, Rust, Swift, TypeScript), so it cannot check migration files for RLS. A `service_role` key in JS code would need a custom query. | [20] |
| Needs a build / `npm install`? | No build for JavaScript/TypeScript: a build command is "Not needed for Python and JavaScript/TypeScript analysis". Node.js 14+ is required if there are TypeScript files; `node_modules` is not extracted by default. | [15] |
| Speed? | Not found in docs (database creation adds time; measure later). | [15] |
| False positives? | Low with `default`; higher with `security-extended` (trade-off stated in docs). | [14] |
| Custom rules? | Yes, in the QL query language; powerful but a steep learning curve. | — |
| Cross-file? | Yes (whole-database data flow). | — |
| SARIF output? | Yes; GitHub code scanning is built on SARIF. | [14] |
| **Licence/cost** | **Restrictive.** The CodeQL terms allow use "to perform academic research" and "analysis on the Open Source Codebase" (OSI-licensed code); databases for automated analysis/CI only for open-source code hosted on GitHub.com. They forbid use "in connection with any codebase that is not an Open Source Codebase" unless you have a paid GitHub Advanced Security licence. | [16] |

**Verdict for RepoPilot:** optional, and **mostly a licensing question**. Our capstone research on open-source benchmark apps is likely covered under "academic research", but a RepoPilot product analysing users' **private** repos would need a commercial licence. **Raise this at the decision session.** If used, start with the `default` suite and compare against `security-extended` to measure the false-positive trade-off ourselves.

---

## 6. Comparison Table

| Tool | What it catches in a React/Vite + Supabase app | Needs `npm install`? | Speed | False-positive reputation | Custom rules | Cross-file? | SARIF? | Licence/cost |
|---|---|---|---|---|---|---|---|---|
| `tsc --noEmit` | Type errors, calls to non-existent APIs | Effectively yes (types) | Not found | Low (depends on tsconfig) | No | Yes | No (convert) | Free |
| ESLint + security plugin + `react/no-danger` | Node-oriented hotspots; `dangerouslySetInnerHTML` | Yes | Not found | **High** (stated by plugin) | Possible, harder | No | Via plugin | Free |
| Semgrep CE | Our custom JS/TS rules + registry rules | No | Not found | Rule-dependent | **Easy** | **No** (single function) | Built in | Free (Pro paid) |
| CodeQL | Taint-based vulnerabilities in JS/TS | No build needed | Not found | Low (`default`) / higher (`security-extended`) | Yes, hard | Yes | Built in | **Free only for research / OSI open source** |

**Draft conclusion (for the decision session):** run `tsc` + ESLint (security + React rules) + Semgrep CE with our custom rules on every app, all converted to SARIF. Add the Supabase database advisors for RLS (Section 7). Treat CodeQL as optional for research runs on open-source benchmark apps, pending a licence decision. Speed numbers are still unknown and must be measured.

---

## 7. Supabase Security: What These Tools Do Not Cover, and What Does

None of the four tools checks Supabase database security: SQL is not supported by Semgrep [11] or CodeQL [20], and `tsc`/ESLint only read JS/TS. This section explains the Supabase background, then the tools that do cover it.

### 7.1 Row-Level Security (RLS)

- **What it is:** "Postgres Row Level Security (RLS) gives you granular authorization rules that run inside the database" [22]. It works like an automatic `WHERE` clause added to every query.
- **Laravel comparison:** like Laravel Policies/Gates, but enforced **inside the database**. That matters because in a typical Supabase app, the browser talks to the database directly through Supabase's Data API, with no Laravel-style backend in between.
- **Why it is critical:** "A table in an exposed schema without RLS is readable and writable by any role with a grant on it" [22]. In other words, anyone with the public key can read and change it.
- **How it is enabled:** `alter table public.reports enable row level security;` [22]
- **Typical owner-only policy** [22]:
  ```sql
  create policy "Users can view their own profile."
  on profiles for select
  to authenticated
  using ( (select auth.uid()) = user_id );
  ```
- **`using` vs `with check`:** `using` filters which existing rows can be read or changed; `with check` validates new or updated rows [22].
- **RLS on, no policies:** "no data is accessible through the API when using a publishable key, until you create policies" [22]. Safe, but the app breaks, which is a typical reason a vibe-coding agent "fixes" the error by weakening security (the "function-fix side effects" failure mode [3, p. 9]).
- **Two traps from the docs:** adding policies does not remove default grants, which must be revoked explicitly; and a `security definer` function in an exposed schema runs with its creator's privileges [22].

### 7.2 Supabase API keys: public vs secret

| | Publishable / legacy `anon` key | Secret / legacy `service_role` key |
|---|---|---|
| Purpose | Identifies the app; low privileges | Full access for backend code |
| Safe in browser? | **Yes**: "Safe to expose online" [23] | **No**: "Never put one in a browser, a shipped application, or source control" [23] |
| RLS | Limited by RLS: "it only reaches what Row Level Security allows" [23] | **Bypasses RLS**: it has `BYPASSRLS` and will "skip every Row Level Security policy" [23] |
| New format | `sb_publishable_...` | `sb_secret_...` [23] |

**Implications for our checks:**
1. Finding the publishable/`anon` key in frontend code is **normal, not a vulnerability**. Our secret-scanning rules must not flag it, or every Supabase app produces a false positive.
2. Finding a `service_role` / `sb_secret_` key in frontend code, a `VITE_*` variable, or the repository **is critical**, because it bypasses all RLS.
3. Supabase says new secret keys are rejected in browsers ("Supabase matches on the User-Agent header and returns HTTP 401 Unauthorized") [23]. **However**, the docs also say that long keys starting with `eyJ` are the legacy format [23], and that browser block is described for the new secret keys. Older vibe-coded apps likely use legacy keys, so we must still flag them.

### 7.3 CVE-2025-48757 (Lovable)

- **Description (NVD):** "An insufficient database Row-Level Security policy in Lovable through 2025-04-15 allows remote unauthenticated attackers to read or write to arbitrary database tables of generated sites" [24].
- **Severity:** CVSS 3.1 base score **9.3 Critical** (`AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N`): network attack, low complexity, no privileges or user interaction needed [24].
- **Weakness type:** CWE-863 (Incorrect Authorization) [24].
- **Published:** 30 May 2025 [24].
- **Note:** the record says the issue "is disputed by the Supplier because each individual customer of the Lovable platform accepts a responsibility over protecting the data of their application" [24]. This is the same "responsibility misalignment" the vibe-coding paper describes: the platform expects the user to secure the app, and the user does not know how [3, p. 13].
- **Why it matters for RepoPilot:** it is the clearest real-world example of our top check (missing or weak RLS), and lint `0013_rls_disabled_in_public` (Section 7.4) detects exactly this.

### 7.4 What does cover it: Supabase database advisors

Supabase has its own deterministic linter. The **database advisors** run security lints, including [17]:

- `0013_rls_disabled_in_public`: "Table publicly accessible" without RLS (the CVE-2025-48757 problem).
- `0024_permissive_rls_policy`: "Security policy allows unrestricted access", i.e. always-true conditions such as `using (true)`.
- `0007_policy_exists_rls_disabled`: policies written but RLS turned off.
- `0008_rls_enabled_no_policy`: RLS on but no policies.
- `0002_auth_users_exposed`: user data exposed through a view referencing `auth.users`.
- `0010_security_definer_view`: a view that bypasses RLS.
- `0015_rls_references_user_metadata`: a policy relying on user-editable data.
- `0028` / `0029`: SECURITY DEFINER functions callable by anonymous or any signed-in users.

**Important details:**
- These lints run against a **database**, not the migration files. We would start the app's local Supabase stack (in Farag's sandbox), apply the migrations, then run the advisors.
- They can be run from the CLI with `supabase db advisors`, with a type of `security` or `performance` [17]. The pages read did not list its other flags or output format. **Open:** run `supabase db advisors --help` once the sandbox exists, to check for JSON output (for SARIF conversion).
- `supabase db lint` is **not** the same thing: it runs the `plpgsql_check` extension to find errors in PL/pgSQL code (typing errors, unreachable code, and "EXECUTE statements against SQL injection"), not RLS checks [18], [21].
- **Database tests:** `supabase test db` "Tests local database with pgTAP" [21]. This is where RLS **behaviour** tests could live ("user A cannot read user B's rows"). Coordinate with Farag.

### 7.5 Still not covered by any tool (need custom rules or tests)

- A `service_role` / `sb_secret_` key in frontend code or `VITE_*` variables → custom Semgrep rule + secret scanner (gitleaks/trufflehog).
- Authentication checks done only on the client → behaviour tests (Farag).
- Placeholder security: "TODO: add password verification", Base64 as "encryption" [3, p. 9] → custom Semgrep rules.
- Whether the RLS policies are **correct for the app's intent** (e.g. should guests see products, should admins see all orders?). No linter can know this; it needs intent evidence and tests. This links back to RepoPilot's failure-attribution research question.

---

## 8. Ideas for RepoPilot (my own, not from the sources)

- **Recall first, then filter:** configure scanners to catch as much as possible, accepting extra false positives, then filter with LLM triage plus actual test runs. This follows the practitioner preference in [1, p. 8].
- **No silent dismissals:** no agent may mark a finding as a false positive without recorded evidence (from [1, p. 9]).
- **Own benchmark:** test the scanners on our own apps with planted bugs, not on public benchmarks [1, p. 7]. Planted bugs also let us count what the scanners **miss**.
- **Explain every finding:** each reported finding says why it was flagged and how to fix it [1, p. 11].
- **Pattern library link:** known-good fix patterns (for example "enable RLS + owner-only policy") could be retrieved from a knowledge base to guide repairs. This belongs to the repair part of A3, not to SAST itself.
- **Intent evidence:** because SAST cannot see what the app is supposed to do [1, p. 7], RepoPilot also needs intent evidence (README, UI text, schemas) alongside static analysis.

---

## References

[1] A. S. Ami, K. Moran, D. Poshyvanyk, and A. Nadkarni, "'False negative – that one is going to kill you': Understanding industry perspectives of static analysis based security testing," arXiv:2307.16325v3, Jun. 2024. *(Check whether a peer-reviewed version exists and cite that venue.)*

[2] OASIS, *Static Analysis Results Interchange Format (SARIF) Version 2.1.0*, OASIS Standard, Mar. 2020. [Online]. Available: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html (accessed Oct. 14, 2026).

[3] J. Deng, Z. Fan, and R. Meng, "Understanding the (in)security of vibe-coded applications," arXiv:2606.23130v4, Sep. 2026.

[4] Microsoft, "TSConfig reference," TypeScript Documentation. [Online]. Available: https://www.typescriptlang.org/tsconfig/ (accessed Oct. 14, 2026).

[5] ESLint Community, "eslint-plugin-security," GitHub repository README. [Online]. Available: https://github.com/eslint-community/eslint-plugin-security (accessed Oct. 14, 2026).

[6] jsx-eslint, "react/no-danger," eslint-plugin-react documentation. [Online]. Available: https://github.com/jsx-eslint/eslint-plugin-react/blob/master/docs/rules/no-danger.md (accessed Oct. 14, 2026).

[7] typescript-eslint, "Linting with type information." [Online]. Available: https://typescript-eslint.io/getting-started/typed-linting/ (read from the documentation source on GitHub, Oct. 14, 2026).

[8] Microsoft, "@microsoft/eslint-formatter-sarif," npm package. [Online]. Available: https://www.npmjs.com/package/@microsoft/eslint-formatter-sarif (accessed Oct. 14, 2026).

[9] Semgrep, "CLI reference," Semgrep Docs. [Online]. Available: https://docs.semgrep.dev/cli-reference (accessed Oct. 14, 2026).

[10] SARIF Standard, "sarif-sdk-typescript," GitHub repository. [Online]. Available: https://github.com/sarif-standard/sarif-sdk-typescript (accessed Oct. 14, 2026). (Converters exist for Clang/Cppcheck/Infer, not for tsc.)

[11] Semgrep, "Add support for SQL," GitHub issue #8351. [Online]. Available: https://github.com/semgrep/semgrep/issues/8351 (accessed Oct. 14, 2026).

[12] Semgrep, "Supported languages for Semgrep Community Edition (CE)," Semgrep Docs. [Online]. Available: https://docs.semgrep.dev/semgrep-ce-languages (accessed Oct. 14, 2026).

[13] Semgrep, "Semgrep Pro Engine overview," Semgrep Docs. [Online]. Available: https://docs.semgrep.dev/semgrep-code/semgrep-pro-engine-intro (accessed Oct. 14, 2026).

[14] GitHub, "CodeQL query suites," GitHub Docs. [Online]. Available: https://docs.github.com/en/code-security/code-scanning/managing-your-code-scanning-configuration/codeql-query-suites (accessed Oct. 14, 2026).

[15] GitHub, "Preparing your code for CodeQL analysis," GitHub Docs. [Online]. Available: https://docs.github.com/en/code-security/codeql-cli/getting-started-with-the-codeql-cli/preparing-your-code-for-codeql-analysis (accessed Oct. 14, 2026).

[16] GitHub, "GitHub CodeQL Terms and Conditions," codeql-cli-binaries LICENSE.md. [Online]. Available: https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md (accessed Oct. 14, 2026).

[17] Supabase, "Database advisors," Supabase Docs. [Online]. Available: https://supabase.com/docs/guides/database/database-advisors (accessed Oct. 14, 2026).

[18] Supabase, "supabase db lint," Supabase CLI reference. [Online]. Available: https://supabase.com/docs/reference/cli/supabase-db-lint (accessed Oct. 14, 2026).

[19] OWASP Foundation, "Source code analysis tools," OWASP Community. [Online]. Available: https://community.owasp.org/Source_Code_Analysis_Tools (accessed Oct. 14, 2026).

[20] GitHub, "Supported languages and frameworks," CodeQL documentation. [Online]. Available: https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/ (accessed Oct. 14, 2026).

[21] Supabase, "Testing and linting," Supabase Docs. [Online]. Available: https://supabase.com/docs/guides/local-development/cli/testing-and-linting (accessed Oct. 14, 2026).

[22] Supabase, "Row Level Security," Supabase Docs. [Online]. Available: https://supabase.com/docs/guides/database/postgres/row-level-security (accessed Oct. 14, 2026).

[23] Supabase, "Understanding API keys," Supabase Docs. [Online]. Available: https://supabase.com/docs/guides/api/api-keys (accessed Oct. 14, 2026).

[24] NIST, "CVE-2025-48757," National Vulnerability Database. [Online]. Available: https://nvd.nist.gov/vuln/detail/CVE-2025-48757 (accessed Oct. 14, 2026 via the NVD API).
