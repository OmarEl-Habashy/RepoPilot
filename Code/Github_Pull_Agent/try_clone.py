from dataclasses import asdict
import json
from pathlib import Path

from agent.cloner import clone_repository
from agent.static_analysis import AnalysisReport, analyze_repository
from agent.url_parser import parse_repo_url


DEFAULT_URL = "https://github.com/octocat/Hello-World"


def _print_analysis_report(report: AnalysisReport, report_path: Path) -> None:
    print(f"Detected languages: {', '.join(report.detected_languages) or 'none'}")
    for tool_name, result in report.tools.items():
        print(f"\n{tool_name}: {result.status}")
        if result.error:
            print(f"  Error: {result.error}")
        for finding in result.findings:
            location = finding.file
            if finding.cell is not None:
                location += f" [cell {finding.cell}]"
            if finding.line is not None:
                location += f":{finding.line}"
                if finding.column is not None:
                    location += f":{finding.column}"
            code = f" [{finding.code}]" if finding.code else ""
            print(f"  {location}{code}: {finding.message}")
        if result.status == "completed":
            print(f"  Findings: {len(result.findings)}")
    print(f"\nAnalysis report saved to: {report_path}")


def main() -> None:
    repo_url = input(f"GitHub repository URL [{DEFAULT_URL}]: ").strip() or DEFAULT_URL
    repo = parse_repo_url(repo_url)
    target_dir = (
        Path(__file__).resolve().parent
        / "workspace"
        / f"{repo.owner}__{repo.name}"
        / "repo"
    )

    if target_dir.exists():
        if not target_dir.is_dir():
            raise NotADirectoryError(f"Clone destination is not a directory: {target_dir}")
        cloned_path = target_dir
        print(f"Using existing repository at: {cloned_path}")
    else:
        cloned_path = clone_repository(repo)
        print(f"Successfully cloned {repo.owner}/{repo.name} to: {cloned_path}")

    report = analyze_repository(cloned_path)
    report_path = target_dir.parent / "analysis.json"
    report_path.write_text(
        json.dumps(asdict(report), indent=2),
        encoding="utf-8",
    )
    _print_analysis_report(report, report_path)


if __name__ == "__main__":
    main()
