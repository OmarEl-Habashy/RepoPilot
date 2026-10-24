# Plan: Repository Ingestion Agent (GitHub Pull Agent)

First stage of the RepoPilot pipeline. **Scope for now:** take a GitHub repo link, validate it, download (clone) it locally, run available static analyzers for detected languages, emit a structured artifact for the next agent (Code Understanding), and provide a Streamlit UI for this workflow.

## 1. Goal & Non-Goals

**Goal:** `link in -> local copy on disk + analysis report out`.

**Non-goals (later stages):** AST parsing, RAG indexing, dependency graphs, running repository tests, and LLM calls.

## 2. Input / Output Contract

**Input**
```json
{ "repo_url": "https://github.com/owner/name", "ref": "optional branch/tag/commit", "token": "optional (private repos, via env)" }
```

**Current output artifact** (`workspace/<owner>__<name>/analysis.json`)
```json
{
  "repository_path": "workspace/owner__name/repo",
  "detected_languages": ["Python", "C/C++"],
  "tools": {
    "ruff": {"status": "completed", "findings": []},
    "cppcheck": {"status": "completed", "findings": []}
  }
}
```
This report is written beside the clone; it does not modify the cloned repository. A richer ingestion manifest can be added later.

## 3. Steps

1. **Parse & validate URL**
   - Accept `https://github.com/o/r`, `.git` suffix, `git@github.com:o/r.git`, `o/r` shorthand, and `/tree/<branch>` links.
   - Reject non-GitHub hosts and malformed input (prevents command injection / SSRF).
2. **Pre-flight check** (GitHub REST API `GET /repos/{o}/{r}`)
   - Confirms repo exists/is accessible, gets default branch, size, languages.
   - Fail early if size exceeds a limit (e.g. 500 MB, configurable).
3. **Download**
   - `git clone --depth 1 [--branch ref]` into `workspace/<owner>__<name>/repo`.
   - Fallback: download ZIP archive if `git` is unavailable.
   - Use subprocess with argument list (never shell string), timeout, and cleanup of partial clone on failure.
4. **Post-clone verification**
   - Confirm directory is a git repo, record `HEAD` commit SHA.
   - Count files / size; detect language by extension.
5. **Static analysis**
   - Detect Python files and Jupyter notebooks, plus C/C++ source files, by extension.
   - Run Ruff and/or cppcheck as appropriate; report missing tools and findings.
   - Save the report beside the clone, not inside it.
6. **Write the analysis report** and print a short summary.
7. **Idempotency:** if the target exists, either reuse (same SHA) or re-pull (`--force`).

## 4. Proposed Structure

```
Github_Pull_Agent/
├─ PLAN.md
├─ requirements.txt
├─ app.py              # Streamlit UI for repository ingestion and results
├─ main.py              # CLI: python main.py <url> [--ref X] [--force]
├─ try_clone.py         # Interactive clone + static-analysis runner
├─ agent/
│  ├─ url_parser.py     # parse/validate -> (owner, name, ref)
│  ├─ github_api.py     # pre-flight metadata
│  ├─ cloner.py         # git clone / zip fallback
│  ├─ static_analysis.py # Ruff/cppcheck detection, execution, and results
│  ├─ manifest.py       # build + write manifest
│  └─ config.py         # workspace dir, size limit, timeout, token env var
├─ tests/
│  ├─ test_url_parser.py
│  └─ test_cloner.py
└─ workspace/           # cloned repos (gitignored)
```

## 5. Decisions

- **Language:** Python (matches later stack: LLM, AST, test tooling).
- **"Agent" form:** for now a deterministic tool/function (no LLM needed). It is exposed as `ingest_repository(repo_url, ref=None) -> Manifest`, so the Orchestrator can later call it as a tool.
- **Auth:** `GITHUB_TOKEN` env var only; never logged or stored in the manifest.
- **Safety:** clone only, never execute repo code at this stage; shallow clone; size/time limits.

## 6. Error Handling

| Case | Behavior |
|---|---|
| Invalid URL | `failed`, clear message |
| Repo not found / private w/o token | `failed`, suggest token |
| Too large | `failed` before download |
| Network/timeout | retry 2x with backoff, then `failed` |
| Partial clone | delete directory |

## 7. Milestones

1. URL parser + unit tests
2. Cloner (git) + manifest
3. GitHub API pre-flight + size guard
4. ZIP fallback, `--force`, idempotency
5. Run static analysis against Python, C/C++, and mixed-language repositories
6. Test ingestion against 2-3 real repos (small public, one with a branch ref, one invalid)

## 8. Done Criteria

- The clone runner produces a local copy and an `analysis.json` report.
- The Streamlit UI accepts a repository URL and optional ref, then displays the analysis results and offers the JSON report for download.
- Supported source files are analyzed with the corresponding installed tool; missing tools and skipped languages are reported clearly.
- Invalid or inaccessible links fail with a clear error and leave no junk on disk.
- Unit tests pass.

Run the UI from this directory with `streamlit run app.py`.

## 9. Future Hooks

- Orchestrator calls `ingest_repository` as a tool.
- Manifest feeds the Code Understanding Agent (file tree, languages, commit SHA for reproducibility).
- Later: private repos via GitHub App, sandboxed container checkout, submodule support.
