from dataclasses import dataclass
import unicodedata
import re
from urllib.parse import unquote, urlparse

@dataclass(frozen=True)
class RepoRef:
    owner: str
    name: str
    ref: str | None
    clone_url: str
    
def _clean_input(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("Invalid URL")
    if len(raw.strip()) > 500:
        raise ValueError("URL is too long")
    if any(unicodedata.category(char) in ("Cc", "Cf") for char in raw):
        raise ValueError("Input rejected: Control or format characters detected!")
    return raw.strip()

def _detect_format(s: str) -> str:
    if s.startswith("https://"):
        return "HTTPS"
    if s.startswith("git@github.com:"):
        return "SSH"
    return "SHORTHAND"

def _extract_ref(segments: list[str]) -> str | None:
    if not segments:
        return None
    if segments[0] not in ("tree", "commit") or len(segments) < 2:
        raise ValueError("Invalid GitHub repository URL")
    return "/".join(segments[1:])

def _make_repo_ref(owner: str, name: str, ref: str | None = None) -> RepoRef:
    owner = validate_owner(owner)
    name = validate_repo_name(_strip_git_suffix(name))
    ref = validate_ref(ref)
    return RepoRef(owner, name, ref, build_clone_url(owner, name))

def _parse_https(s: str) -> RepoRef:
    parsed_url = urlparse(s)
    if (
        parsed_url.scheme != "https"
        or parsed_url.netloc.lower() != "github.com"
        or parsed_url.query
        or parsed_url.fragment
    ):
        raise ValueError("URL is not a github URL")
    parts = [unquote(part) for part in parsed_url.path.strip("/").split("/")]
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError("Invalid github repository URL")
    owner = parts[0]
    name = parts[1]
    ref = _extract_ref(parts[2:])
    if name.endswith(".git") and ref is not None:
        raise ValueError("A .git URL cannot include a ref path")
    return _make_repo_ref(owner, name, ref)

def _parse_ssh(s: str) -> RepoRef:
    prefix = "git@github.com:"
    if not s.startswith(prefix):
        raise ValueError("Not SSH URL")
    parts = s[len(prefix):].split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("Invalid SSH URL")
    owner = parts[0]
    name = parts[1]
    return _make_repo_ref(owner, name)

def _parse_shorthand(s: str) -> RepoRef:
    parts = s.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("Invalid URL format")
    owner = parts[0]
    name = parts[1]
    return _make_repo_ref(owner, name)

def _strip_git_suffix(name):
    return name[:-4] if name.endswith(".git") else name 

def validate_repo_name(name):
    if not isinstance(name, str) or not (1 <= len(name) <= 100):
        raise ValueError("Repo name is either too short or too long")
    if re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,99})", name):
        return name
    raise ValueError("Invalid characters in repo name")

def validate_owner(owner):
    if not isinstance(owner, str):
        raise ValueError("Owner must be a string")
    if not owner:
        raise ValueError("Owner cannot be empty")
    if len(owner) > 39:
        raise ValueError("Owner is too long")
    if owner.startswith("-") or owner.endswith("-"):
        raise ValueError("Owner cannot start or end with a hyphen")
    if not re.fullmatch(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$", owner):
        raise ValueError("Invalid owner name")
    return owner

def validate_ref(ref):
    if ref is None:
        return None
    if not isinstance(ref, str):
        raise ValueError("Ref must be a string")
    if not ref:
        raise ValueError("Ref cannot be empty")
    if ref.startswith("-"):
        raise ValueError("Ref cannot start with a hyphen")
    if ".." in ref:
        raise ValueError("Ref cannot contain '..'")
    if any(char.isspace() or unicodedata.category(char) == "Cc" for char in ref):
        raise ValueError("Ref cannot contain spaces or control characters")
    if any(char in "~^:?*[" + "\\" for char in ref):
        raise ValueError("Ref contains invalid characters")
    return ref

def build_clone_url(owner: str, name: str) -> str:
    return f"https://github.com/{owner}/{name}.git"

def parse_repo_url(raw: str) -> RepoRef:
    """Parse a GitHub HTTPS, SSH, or owner/repository shorthand reference."""
    cleaned = _clean_input(raw)
    url_format = _detect_format(cleaned)
    if url_format == "HTTPS":
        return _parse_https(cleaned)
    if url_format == "SSH":
        return _parse_ssh(cleaned)
    return _parse_shorthand(cleaned)