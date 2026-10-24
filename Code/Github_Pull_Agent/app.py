import hashlib
import json
import subprocess
from dataclasses import asdict, replace
from pathlib import Path

import streamlit as st

from agent.cloner import clone_repository
from agent.static_analysis import AnalysisReport, analyze_repository
from agent.url_parser import parse_repo_url, validate_ref

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT / "workspace"

st.set_page_config(
    page_title="RepoPilot | Repository inspector",
    page_icon=":material/travel_explore:",
    layout="wide",
)


def _ingest_repository(
    repo_url: str,
    requested_ref: str,
) -> tuple[AnalysisReport, Path, bool]:
    repo = parse_repo_url(repo_url)
    ref = validate_ref(requested_ref.strip()) if requested_ref.strip() else repo.ref
    if ref != repo.ref:
        repo = replace(repo, ref=ref)

    workspace_root = WORKSPACE_ROOT
    if ref is not None:
        ref_id = hashlib.sha256(ref.encode("utf-8")).hexdigest()[:16]
        workspace_root = WORKSPACE_ROOT / "refs" / ref_id

    repository_dir = workspace_root / f"{repo.owner}__{repo.name}"
    target_dir = repository_dir / "repo"
    reused = target_dir.exists()

    if reused:
        if not target_dir.is_dir():
            raise NotADirectoryError(f"Clone destination is not a directory: {target_dir}")
    else:
        clone_repository(repo, workspace_root=workspace_root)

    report = analyze_repository(target_dir)
    report_path = repository_dir / "analysis.json"
    report_path.write_text(
        json.dumps(asdict(report), indent=2),
        encoding="utf-8",
    )
    return report, report_path, reused


def _render_report(report: AnalysisReport, report_path: Path, reused: bool) -> None:
    total_findings = sum(len(result.findings) for result in report.tools.values())
    completed_tools = sum(result.status == "completed" for result in report.tools.values())

    st.subheader("Inspection results")
    st.caption(
        f"{'Using existing clone' if reused else 'Repository cloned'} · "
        f"Report saved to `{report_path}`"
    )

    with st.container(horizontal=True):
        st.metric("Languages detected", len(report.detected_languages), border=True)
        st.metric("Findings", total_findings, border=True)
        st.metric("Analyzers completed", completed_tools, border=True)

    if report.detected_languages:
        st.markdown("**Languages**")
        st.markdown(" ".join(f"`{language}`" for language in report.detected_languages))
    else:
        st.info("No supported Python or C/C++ source files were found.")

    st.markdown("#### Static analysis")
    tool_columns = st.columns(len(report.tools), gap="medium")
    for column, (tool_name, result) in zip(tool_columns, report.tools.items()):
        with column, st.container(border=True):
            st.markdown(f"**{tool_name}**")
            status_colors = {
                "completed": "green",
                "failed": "red",
                "skipped": "gray",
            }
            st.badge(
                result.status.title(),
                color=status_colors[result.status],
            )
            if result.error:
                st.caption(result.error)
            elif result.status == "completed":
                st.caption(f"{len(result.findings)} finding(s)")

    findings = [
        {
            "Analyzer": tool_name,
            "Severity": finding.severity,
            "File": finding.file,
            "Line": finding.line,
            "Code": finding.code,
            "Finding": finding.message,
        }
        for tool_name, result in report.tools.items()
        for finding in result.findings
    ]
    if findings:
        st.markdown("#### Findings")
        st.dataframe(findings, hide_index=True, width="stretch")
    elif any(result.status == "failed" for result in report.tools.values()):
        st.warning("No findings were returned by the analyzers. Review the failed tool status above.")
    elif completed_tools:
        st.success("No findings reported by the completed analyzers.")
    else:
        st.info("No analyzers ran for this repository.")

    st.download_button(
        "Download analysis.json",
        data=report_path.read_bytes(),
        file_name="analysis.json",
        mime="application/json",
        icon=":material/download:",
    )


st.title("RepoPilot")
st.caption("Bring a GitHub repository in. Get a local clone and a clear static-analysis report.")

with st.container(border=True):
    st.markdown("#### Inspect a repository")
    with st.form("repository_form"):
        repo_url = st.text_input(
            "GitHub repository",
            placeholder="https://github.com/owner/repository",
            help="Paste a GitHub URL or use the owner/repository shorthand.",
        )
        requested_ref = st.text_input(
            "Branch, tag, or commit (optional)",
            placeholder="main",
            help="Leave blank to use the repository's default branch.",
        )
        submitted = st.form_submit_button(
            "Clone and analyze",
            type="primary",
            icon=":material/rocket_launch:",
        )

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_error" not in st.session_state:
    st.session_state.analysis_error = None

if submitted:
    st.session_state.analysis_result = None
    st.session_state.analysis_error = None
    try:
        with st.spinner("Cloning and analyzing the repository..."):
            st.session_state.analysis_result = _ingest_repository(repo_url, requested_ref)
    except subprocess.CalledProcessError as error:
        details = (error.stderr or error.stdout or "").strip()
        st.session_state.analysis_error = (
            f"Git could not clone this repository. {details or error}"
        )
    except subprocess.TimeoutExpired as error:
        st.session_state.analysis_error = (
            f"Cloning exceeded the {error.timeout}-second time limit."
        )
    except (OSError, ValueError) as error:
        st.session_state.analysis_error = str(error)

if st.session_state.analysis_error:
    st.error(st.session_state.analysis_error, icon=":material/error:")

if st.session_state.analysis_result:
    _render_report(*st.session_state.analysis_result)

with st.sidebar:
    st.markdown("### How it works")
    st.markdown(
        "1. Validate a GitHub repository reference\n"
        "2. Shallow-clone it into the local workspace\n"
        "3. Detect Python and C/C++ source files\n"
        "4. Run available analyzers and save `analysis.json`"
    )
    st.caption("Public repositories only. Repository code is not executed.")
