from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Callable, Literal


_PYTHON_EXTENSIONS = {".py", ".pyi", ".ipynb"}
_CPP_EXTENSIONS = {
    ".c",
    ".h",
    ".cc",
    ".hh",
    ".cpp",
    ".hpp",
    ".cxx",
    ".hxx",
    ".c++",
    ".h++",
}
_EXCLUDED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}
ToolStatus = Literal["completed", "failed", "skipped"]


@dataclass(frozen=True)
class Finding:
    file: str
    message: str
    severity: str
    line: int | None = None
    column: int | None = None
    code: str | None = None
    cell: int | None = None


@dataclass(frozen=True)
class ToolResult:
    status: ToolStatus
    findings: tuple[Finding, ...] = ()
    command: tuple[str, ...] | None = None
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    error: str | None = None


@dataclass(frozen=True)
class AnalysisReport:
    repository_path: str
    detected_languages: tuple[str, ...]
    tools: dict[str, ToolResult]


def _find_source_files(repository_path: Path) -> dict[str, list[Path]]:
    source_files = {"python": [], "cpp": []}

    def raise_walk_error(error: OSError) -> None:
        raise error

    for directory, directory_names, file_names in os.walk(
        repository_path, followlinks=False, onerror=raise_walk_error
    ):
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name.lower() not in _EXCLUDED_DIRECTORIES
            and not (Path(directory) / name).is_symlink()
        )
        current_directory = Path(directory)
        for file_name in file_names:
            file_path = current_directory / file_name
            if file_path.is_symlink():
                continue
            extension = file_path.suffix.lower()
            if extension in _PYTHON_EXTENSIONS:
                source_files["python"].append(file_path)
            elif extension in _CPP_EXTENSIONS:
                source_files["cpp"].append(file_path)

    for files in source_files.values():
        files.sort()
    return source_files


def _tool_paths(files: list[Path], repository_path: Path) -> list[str]:
    return [
        os.path.join(".", os.fspath(path.relative_to(repository_path)))
        for path in files
    ]


def _relative_path(path: str, repository_path: Path) -> str:
    try:
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = repository_path / file_path
        return file_path.resolve().relative_to(repository_path).as_posix()
    except ValueError:
        return path


def _parse_ruff_findings(output: str, repository_path: Path) -> tuple[Finding, ...]:
    if not output.strip():
        return ()

    diagnostics = json.loads(output)
    return tuple(
        Finding(
            file=_relative_path(diagnostic["filename"], repository_path),
            message=diagnostic["message"],
            severity="error",
            line=diagnostic["location"]["row"],
            column=diagnostic["location"]["column"],
            code=diagnostic.get("code"),
            cell=diagnostic.get("cell"),
        )
        for diagnostic in diagnostics
    )


def _parse_cppcheck_findings(output: str, repository_path: Path) -> tuple[Finding, ...]:
    findings = []
    for line in output.splitlines():
        if not line.strip():
            continue
        try:
            diagnostic = json.loads(line)
        except json.JSONDecodeError:
            raise ValueError(f"Unexpected non-JSON cppcheck output: {line}") from None
        if not isinstance(diagnostic, dict) or "message" not in diagnostic:
            raise ValueError(f"Unexpected cppcheck diagnostic: {line}")
        findings.append(
            Finding(
                file=_relative_path(diagnostic.get("file", ""), repository_path),
                message=diagnostic["message"],
                severity=diagnostic.get("severity", "unknown"),
                line=diagnostic.get("linenr"),
                code=diagnostic.get("id"),
            )
        )
    return tuple(findings)


def _run_tool(
    executable: str,
    arguments: list[str],
    repository_path: Path,
    timeout_seconds: int,
    parse_findings: Callable[[str, Path], tuple[Finding, ...]],
    expected_return_codes: tuple[int, ...],
    fallback_command: tuple[str, ...] | None = None,
) -> ToolResult:
    executable_path = shutil.which(executable)
    if executable_path is None:
        if fallback_command is None:
            return ToolResult(
                status="failed",
                error=f"{executable} was not found on PATH; install it to analyze this repository.",
            )
        command_prefix = fallback_command
    else:
        command_prefix = (executable_path,)
    command = (*command_prefix, *arguments)
    try:
        completed = subprocess.run(
            command,
            cwd=repository_path,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError:
        return ToolResult(
            status="failed",
            command=command,
            error=f"{executable} could not be started; verify that it is installed.",
        )
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        return ToolResult(
            status="failed",
            command=command,
            stdout=stdout,
            stderr=stderr,
            error=f"{executable} exceeded the {timeout_seconds}-second timeout.",
        )

    findings = ()
    parse_error = None
    try:
        findings = parse_findings(completed.stdout + completed.stderr, repository_path)
    except (ValueError, KeyError, TypeError) as error:
        parse_error = f"Could not parse {executable} output: {error}"

    result_status: ToolStatus = (
        "completed"
        if completed.returncode in expected_return_codes and parse_error is None
        else "failed"
    )
    error_message = parse_error
    if completed.returncode not in expected_return_codes:
        error_message = f"{executable} exited with status {completed.returncode}."

    return ToolResult(
        status=result_status,
        findings=findings,
        command=command,
        return_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        error=error_message,
    )


def analyze_repository(
    repository_path: str | Path,
    timeout_seconds: int = 120,
) -> AnalysisReport:
    """Detect Python/C++ source files and run Ruff and/or cppcheck on them."""
    root = Path(repository_path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Repository path is not a directory: {root}")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")

    source_files = _find_source_files(root)
    languages = tuple(
        label
        for language, label in (("python", "Python"), ("cpp", "C/C++"))
        if source_files[language]
    )
    tools: dict[str, ToolResult] = {}

    if source_files["python"]:
        python_paths = _tool_paths(source_files["python"], root)
        tools["ruff"] = _run_tool(
            "ruff",
            ["check", "--output-format=json", *python_paths],
            root,
            timeout_seconds,
            _parse_ruff_findings,
            (0, 1),
            (sys.executable, "-m", "ruff"),
        )
    else:
        tools["ruff"] = ToolResult(status="skipped", error="No Python source files found.")

    if source_files["cpp"]:
        cpp_paths = _tool_paths(source_files["cpp"], root)
        tools["cppcheck"] = _run_tool(
            "cppcheck",
            [
                "--quiet",
                "--enable=warning,style,performance,portability",
                "--template=json",
                "--error-exitcode=2",
                *cpp_paths,
            ],
            root,
            timeout_seconds,
            _parse_cppcheck_findings,
            (0, 2),
        )
    else:
        tools["cppcheck"] = ToolResult(status="skipped", error="No C/C++ source files found.")

    return AnalysisReport(
        repository_path=str(root),
        detected_languages=languages,
        tools=tools,
    )
