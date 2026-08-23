"""Shared KB helpers: walk notes, parse frontmatter, load catalog."""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

REQUIRED_FIELDS = ("id", "title", "topic", "description", "origin", "derivation", "status")
# intro.md = orientation; index.md kept skipped so leftover MOC is never treated as a note
SKIP_NAMES = {"index.md", "agents.md", "intro.md"}
DOMAIN_SKIP_DIRS = {".git", ".cache", "__pycache__", "_issues", "_feedback"}
FEEDBACK_TYPES = frozenset({"wrong", "gap", "stale", "unclear"})
# [label](target) — skip images ![…](…); optional title in quotes
MDLINK_RE = re.compile(
    r"(?<!!)\[([^\]]*)\]\(\s*<?([^>\s)]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
)
_REMOTE_LINK_RE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)
TOKEN_CHARS = 4  # rough: ~4 chars ≈ 1 token
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def is_topic_dir_name(name: str) -> bool:
    """Topic folders only — skip dot/_ prefix and DOMAIN_SKIP_DIRS (e.g. _issues)."""
    if name.startswith(".") or name.startswith("_"):
        return False
    return name not in DOMAIN_SKIP_DIRS


@dataclass
class NoteMeta:
    id: str
    title: str
    topic: str
    description: str
    origin: str = ""
    derivation: str = ""
    status: str = ""
    path: str = ""
    domain: str = ""
    rel_path: str = ""
    body: str = field(default="", repr=False)

    def to_catalog_row(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("body", None)
        return d


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


KB_ROOT_ENV_KEYS = ("KB_ROOT", "KNOWLEDGE_BASE_ROOT")


def resolve_knowledge_root(cli_root: Path | None = None) -> Path:
    """KB tree root: --root wins, else env KB_ROOT / KNOWLEDGE_BASE_ROOT.

    Engine and corpus are separate repos — never default to <engine>/knowledge.
    """
    if cli_root is not None:
        root = cli_root.expanduser().resolve()
    else:
        raw = None
        for key in KB_ROOT_ENV_KEYS:
            raw = os.environ.get(key)
            if raw:
                break
        if not raw or not str(raw).strip():
            keys = " or ".join(KB_ROOT_ENV_KEYS)
            raise ValueError(
                f"Knowledge root not set. Pass --root PATH or set {keys} to the KB tree."
            )
        root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Knowledge root is not a directory: {root}")
    return root


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    block = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, raw = line.partition(":")
        val = raw.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        meta[key.strip()] = val
    return meta, body


def iter_note_paths(knowledge_root: Path, domain: str | None = None) -> Iterable[Path]:
    root = knowledge_root if domain is None else knowledge_root / domain
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*.md")):
        if path.name.lower() in SKIP_NAMES:
            continue
        # knowledge/AGENTS.md or domain-level non-topic files: need topic parent
        parts = path.relative_to(knowledge_root).parts
        if len(parts) < 3:
            # expect domain/topic/note.md
            continue
        if not is_topic_dir_name(parts[1]):
            continue
        yield path


def load_note(path: Path, knowledge_root: Path) -> NoteMeta | None:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    if not meta:
        return None
    rel = path.relative_to(knowledge_root).as_posix()
    parts = path.relative_to(knowledge_root).parts
    domain = parts[0]
    folder_topic = parts[1]
    return NoteMeta(
        id=meta.get("id", ""),
        title=meta.get("title", ""),
        topic=meta.get("topic", ""),
        description=meta.get("description", ""),
        origin=meta.get("origin", ""),
        derivation=meta.get("derivation", ""),
        status=meta.get("status", ""),
        path=str(path.resolve()),
        domain=domain,
        rel_path=rel,
        body=body,
    )


def build_catalog(knowledge_root: Path, domain: str | None = None) -> list[NoteMeta]:
    notes: list[NoteMeta] = []
    for path in iter_note_paths(knowledge_root, domain):
        note = load_note(path, knowledge_root)
        if note is None:
            continue
        notes.append(note)
    return notes


def list_domains(knowledge_root: Path) -> list[dict[str, Any]]:
    """Domains = immediate subdirs of knowledge/ that look like KB domains."""
    if not knowledge_root.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(knowledge_root.iterdir()):
        if not path.is_dir() or path.name.startswith(".") or path.name in DOMAIN_SKIP_DIRS:
            continue
        # skip stray files-only; require at least one topic dir or intro.md
        intro = path / "intro.md"
        topic_dirs = [p for p in path.iterdir() if p.is_dir() and is_topic_dir_name(p.name)]
        if not intro.is_file() and not topic_dirs:
            continue
        notes = build_catalog(knowledge_root, path.name)
        rows.append(
            {
                "domain": path.name,
                "intro": intro.is_file(),
                "topics": len(topic_dirs),
                "notes": len(notes),
                "workflows": (path / "workflows").is_dir(),
            }
        )
    return rows


def domain_intro_path(knowledge_root: Path, domain: str) -> Path:
    return knowledge_root / domain / "intro.md"


def catalog_to_json(notes: list[NoteMeta]) -> str:
    rows = [n.to_catalog_row() for n in notes]
    return json.dumps(rows, ensure_ascii=False, indent=2)


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + TOKEN_CHARS - 1) // TOKEN_CHARS)


def tokenize_query(q: str) -> list[str]:
    q = q.lower().strip()
    parts = re.split(r"[^\w.]+", q, flags=re.UNICODE)
    stop = {"the", "a", "an", "va", "và", "cho", "cua", "của", "tren", "trên", "voi", "với", "mot", "một"}
    return [p for p in parts if len(p) > 1 and p not in stop]


def score_note(note: NoteMeta, query: str, tokens: list[str]) -> float:
    q = query.lower().strip()
    score = 0.0
    nid = note.id.lower()
    if q == nid or q == note.id:
        return 1000.0
    if q in nid or nid in q:
        score += 80.0
    title = note.title.lower()
    desc = note.description.lower()
    topic = note.topic.lower()
    for t in tokens:
        if t in nid:
            score += 25.0
        if t in title:
            score += 12.0
        if t in desc:
            score += 18.0
        if t in topic or t.replace("_", "-") in topic:
            score += 10.0
    # phrase boost
    if len(q) >= 4 and q in desc:
        score += 30.0
    if len(q) >= 4 and q in title:
        score += 20.0
    # Task playbooks: prefer over atomic notes when query already matched
    if score > 0 and (topic == "workflows" or ".workflow." in nid):
        score += 45.0
    return score


def topic_intro_path(knowledge_root: Path, domain: str, topic: str) -> Path:
    return knowledge_root / domain / topic / "intro.md"


def extract_note_links(text: str) -> list[str]:
    """Local note link targets from Markdown [label](path) only."""
    out: list[str] = []
    for m in MDLINK_RE.finditer(text):
        raw = m.group(2).strip()
        if not raw or raw.startswith("#"):
            continue
        if _REMOTE_LINK_RE.match(raw):
            continue
        out.append(raw)
    return out


def normalize_link_target(link: str) -> str:
    """Strip URL fragment and normalize separators."""
    target = link.strip()
    if not target:
        return ""
    target = target.split("#", 1)[0].strip()
    target = target.replace("\\", "/").rstrip("/")
    return target


def resolve_note_link(link: str, from_dir: Path) -> Path | None:
    """Resolve a Markdown relative note path from from_dir."""
    target = normalize_link_target(link)
    if not target:
        return None
    cand = (from_dir / target).resolve()
    if cand.is_dir():
        intro = cand / "intro.md"
        return intro if intro.is_file() else None
    if cand.suffix.lower() == ".md":
        return cand if cand.is_file() else None
    md = Path(str(cand) + ".md")
    if md.is_file():
        return md
    same = from_dir / f"{Path(target).name}.md"
    return same if same.is_file() else None


def slugify_feedback_title(title: str) -> str:
    s = _SLUG_RE.sub("-", title.lower().strip()).strip("-")
    return s or "feedback"


def feedback_dir(knowledge_root: Path, domain: str) -> Path:
    return knowledge_root / domain / "_feedback"


def ensure_under_dir(path: Path, parent: Path) -> Path:
    """Resolve path and require it stays under parent. Raises ValueError on escape."""
    parent_r = parent.resolve()
    path_r = path.resolve()
    try:
        path_r.relative_to(parent_r)
    except ValueError as e:
        raise ValueError(f"path escapes feedback dir: {path}") from e
    return path_r


def unique_feedback_path(feedback_root: Path, slug: str) -> Path:
    """Pick feedback_root/<slug>.md or <slug>-N.md; must stay under feedback_root."""
    feedback_root = feedback_root.resolve()
    feedback_root.mkdir(parents=True, exist_ok=True)
    candidate = ensure_under_dir(feedback_root / f"{slug}.md", feedback_root)
    if not candidate.exists():
        return candidate
    n = 2
    while True:
        candidate = ensure_under_dir(feedback_root / f"{slug}-{n}.md", feedback_root)
        if not candidate.exists():
            return candidate
        n += 1


def engine_root() -> Path:
    """Repo engine root (parent of tools/). Editable install: sibling of _meta/."""
    return Path(__file__).resolve().parent.parent


def read_engine_template(template_name: str) -> str:
    """Load _meta/<template_name> from the engine repo."""
    path = engine_root() / "_meta" / template_name
    if not path.is_file():
        raise FileNotFoundError(f"missing engine template: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    return text


_CORPUS_AGENTS_HEADER = """# AGENTS.md

> **Corpus rule** — bản đầy đủ ship từ engine `_meta/RULE_KB_BUILD.md`.
> Refresh: `knowledge-base --root . init --force`. Sửa rule gốc ở **engine**; đừng coi edit file này là SoT.
> **Scope:** Quy tắc xây / sửa knowledge base (atomic notes). Không gồm task Kanban hay throttling — xem rule optional ở repo engine `_meta/`.
> CLI: `--root` / `KB_ROOT` / `KNOWLEDGE_BASE_ROOT` trỏ vào **repo này** (kb-root).

---
"""

_CORPUS_OPTIONAL_RULES = """## Optional rules

Các file sau nằm trong repo **engine** `_meta/` (không có trong corpus). Mở engine khi cần bulk/throttle, git corpus, tra CLI, hoặc rationale:

| Rule | Khi dùng |
|------|----------|
| `RULE_RESOURCE_CONTROL.md` | Bulk edit, hạn mức API |
| `RULE_GIT.md` | Theo dõi sửa note bằng git (không tự commit mặc định) |
| `TOOLS.md` | Tra / gói note: `knowledge-base domains\\|intro\\|route\\|pack\\|show\\|feedback` (+ maintainer `lint`/`dup`/`catalog`/`init`) |

Skills client (myskills): `kb-consumer` / `kb-maintainer` / `kb-migrate` — cài bằng `npx skills`. Queue công việc: `task-kanban` (stopgap) hoặc Task-engine (dự kiến) — **không** rule engine.

Lý do thiết kế: engine `_meta/KB_BUILD_RATIONALE.md`.

---
"""


def build_corpus_agents_md() -> str:
    """Full RULE_KB_BUILD adapted as corpus AGENTS.md (header + optional links)."""
    raw = read_engine_template("RULE_KB_BUILD.md")
    # Drop engine title + blockquote; keep from ## Goal onward
    marker = "## Goal"
    idx = raw.find(marker)
    if idx < 0:
        raise ValueError("RULE_KB_BUILD.md missing ## Goal — cannot ship corpus AGENTS.md")
    body = raw[idx:]
    body = body.replace(
        "├── AGENTS.md              ← copy/tóm tắt từ RULE_KB_BUILD khi ship",
        "├── AGENTS.md              ← full RULE_KB_BUILD via knowledge-base init",
    )
    opt = body.find("## Optional rules")
    if opt < 0:
        raise ValueError("RULE_KB_BUILD.md missing ## Optional rules")
    checklist = body.find("## Checklist", opt)
    if checklist < 0:
        raise ValueError("RULE_KB_BUILD.md missing ## Checklist")
    body = body[:opt] + _CORPUS_OPTIONAL_RULES + "\n" + body[checklist:]
    text = _CORPUS_AGENTS_HEADER + "\n" + body
    if not text.endswith("\n"):
        text += "\n"
    return text


def init_corpus_file(
    root: Path,
    dest_name: str,
    template_name: str,
    *,
    force: bool = False,
    check: bool = False,
) -> str:
    """Write or check one corpus bootstrap file. Returns action token."""
    dest = root / dest_name
    if template_name == "RULE_KB_BUILD.md":
        new_text = build_corpus_agents_md()
    else:
        new_text = read_engine_template(template_name)
    if dest.is_file():
        old_text = dest.read_text(encoding="utf-8")
        if not old_text.endswith("\n"):
            old_text += "\n"
        if old_text == new_text:
            return "unchanged"
        if check:
            return "differs"
        if not force:
            return "skipped"
        dest.write_text(new_text, encoding="utf-8")
        return "updated"
    if check:
        return "missing"
    dest.write_text(new_text, encoding="utf-8")
    return "created"


# dest filename → _meta template (used by knowledge-base init)
INIT_CORPUS_FILES: tuple[tuple[str, str], ...] = (
    ("AGENTS.md", "RULE_KB_BUILD.md"),
)
INIT_README_FILES: tuple[tuple[str, str], ...] = (
    ("README.md", "README_CORPUS.template.md"),
)
