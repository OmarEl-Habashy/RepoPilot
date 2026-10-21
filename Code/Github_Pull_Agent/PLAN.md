# Plan: Repository Ingestion Agent (GitHub Pull Agent)

First stage of the RepoPilot pipeline. **Scope for now:** take a GitHub repo link, validate it, download (clone) it locally, and emit a structured artifact for the next agent (Code Understanding). No analysis yet.

## 1. Goal & Non-Goals

**Goal:** `link in -> local copy on disk + manifest.json out`.

**Non-goals (later stages):** AST parsing, RAG indexing, dependency graphs, running tests, LLM calls.

## 2. Input / Output Contract

**Input**
```json
{ "repo_url": "https://github.com/owner/name", "ref": "optional branch/tag/commit", "token": "optional (private repos, via env)" }
```

**Output artifact** (`workspace/<owner>__<name>/manifest.json`)
```json
{
  "status": "success | failed",
  "repo_url": "...",
  "owner": "...", "name": "...",
  "ref": "main", "commit_sha": "abc123...",
  "local_path": "workspace/owner__name/repo",
  "size_mb": 12.4, "file_count": 340,
  "primary_languages": {"Python": 0.8},
  "cloned_at": "ISO-8601",
  "error": null
}
```
This manifest is the structured handover to the next agent (matches the "artifact-based handover" principle).

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
5. **Write manifest** and return it (also print a short summary).
6. **Idempotency:** if the target exists, either reuse (same SHA) or re-pull (`--force`).

## 4. Proposed Structure

```
Github_Pull_Agent/
├─ PLAN.md
├─ requirements.txt
├─ main.py              # CLI: python main.py <url> [--ref X] [--force]
├─ agent/
│  ├─ url_parser.py     # parse/validate -> (owner, name, ref)
│  ├─ github_api.py     # pre-flight metadata
│  ├─ cloner.py         # git clone / zip fallback
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
5. Test against 2-3 real repos (small public, one with a branch ref, one invalid)

## 8. Done Criteria

- `python main.py https://github.com/<o>/<r>` produces a local copy and a valid `manifest.json`.
- Invalid or inaccessible links fail with a clear error and leave no junk on disk.
- Unit tests pass.

## 9. Future Hooks

- Orchestrator calls `ingest_repository` as a tool.
- Manifest feeds the Code Understanding Agent (file tree, languages, commit SHA for reproducibility).
- Later: private repos via GitHub App, sandboxed container checkout, submodule support.
