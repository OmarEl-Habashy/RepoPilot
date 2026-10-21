from dataclasses import dataclass
import unicodedata
import urllib
import re

@dataclass(frozen=True)
class RepoRef:
    owner : str
    name : str
    ref : str | None
    clone_url : str
    
def _clean_input(raw) -> str : 
    if(raw == None | raw.strip() == "" | len(raw.strip()) == 0):
        raise ValueError("Invalid URL")
    elif(len(raw.strip()) > 500):
        raise ValueError("URL is too long")
    elif("github.com" not in raw):
        raise ValueError("URL is not a github URL")
    elif any(unicodedata.category(char) in ("Cc", "Cf") for char in raw):
        raise ValueError("Input rejected: Control or format characters detected!")  
    else:
        return raw.strip()

def _detect_format(s : string) -> string:
    #HTTPS:
    if(s.startswith("https://")):
        return "HTTPS"
    #SSH:
    elif(s.startswith("git@github.com:")):
        return "SSH"
    else:
        raise ValueError("URL format not supported")

def _parse_https(s):
    parsed_url = urllib.parse.urlparse(s)
    if parsed_url.netloc != "github.com":
        raise ValueError("URL is not a github URL")
    else:
        path = parsed_url.path.strip("/")
        if path.endswith(".git"):
            path = path[:-4]
    
    parts = path.split("/", 2)
    if len(parts) != 2:
        raise ValueError("Invalid github repository URL")
    owner = parts[0]
    name = parts[1]
    clone_url = f"https://github.com/{owner}/{name}.git"
    return RepoRef(owner, name, None, clone_url)

def _parse_ssh(s):
    if not s.startswith("git@github.com"):
        raise ValueError("Not SSH URL")
    if s.endswith(".git"):
        path = s[:-4]
    else:
        path = s
    path = path[len("git@github.com"):]
    parts  = path.split("/",2)
    if len(parts) != 2:
        raise ValueError("Invalid SSH URL")
    owner = parts[0]
    name = parts[1]
    clone_url = f"https://github.com/{owner}/{name}.git"
    return RepoRef(owner, name, None, clone_url)

def _parse_shorthand(s):
    parts = s.split("/",2)
    if(parts > 2 | parts < 2):
        raise ValueError("Invalid URL format")
    owner = parts[0]
    name = parts[1]
    clone_url = f"https://github.com/{owner}/{name}.git"
    return RepoRef(owner, name, None, clone_url)

def _extract_ref(segments):
    parts = segments.split("/",)
    if parts[2] in ("tree", "commit"):
        return "/".joing(segments[3:])
    return None

def _strip_git_suffix(name):
    return name[:-4] if name.endswith(".git") else name 

def validate_repo_name(name):
    if not (3 <= len(name) <= 100):
        raise ValueError("Repo name is either too short or too long")
    if re.match("^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$",name):
        return name
    raise ValueError("Invalid characters in repo name")

def 