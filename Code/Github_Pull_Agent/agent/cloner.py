from pathlib import Path
import subprocess
import tempfile

from agent.url_parser import RepoRef, validate_ref


def clone_repository(
    repo: RepoRef,
    workspace_root: Path | None = None,
    timeout_seconds: int = 300,
) -> Path:
    """Shallow-clone a parsed GitHub repository into the local workspace."""
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")

    workspace = (
        Path(workspace_root)
        if workspace_root is not None
        else Path(__file__).resolve().parent.parent / "workspace"
    )
    repository_dir = workspace / f"{repo.owner}__{repo.name}"
    target_dir = repository_dir / "repo"
    repository_dir.mkdir(parents=True, exist_ok=True)

    if target_dir.exists():
        raise FileExistsError(f"Clone destination already exists: {target_dir}")

    command = ["git", "clone", "--depth", "1"]
    if repo.ref is not None:
        command.extend(["--branch", validate_ref(repo.ref)])

    with tempfile.TemporaryDirectory(prefix=".clone-", dir=repository_dir) as temp_dir:
        temporary_clone = Path(temp_dir) / "repo"
        command.extend([repo.clone_url, str(temporary_clone)])
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        temporary_clone.rename(target_dir)

    return target_dir
