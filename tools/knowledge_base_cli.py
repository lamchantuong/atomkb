#!/usr/bin/env python3
"""Knowledge Engine CLI (PATH command: knowledge-base)."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# Allow `python tools/knowledge_base_cli.py` before / without editable install
sys.path.insert(0, str(Path(__file__).resolve().parent))

from knowledge_base_lib import (
    FEEDBACK_TYPES,
    INIT_CORPUS_FILES,
    INIT_README_FILES,
    REQUIRED_FIELDS,
    SKIP_NAMES,
    build_catalog,
    catalog_to_json,
    resolve_knowledge_root,
    domain_intro_path,
    ensure_under_dir,
    estimate_tokens,
    extract_note_links,
    feedback_dir,
    init_corpus_file,
    is_topic_dir_name,
    list_domains,
    load_note,
    parse_frontmatter,
    resolve_note_link,
    score_note,
    slugify_feedback_title,
    tokenize_query,
    topic_intro_path,
    unique_feedback_path,
)


def cmd_catalog(args: argparse.Namespace) -> int:
    notes = build_catalog(args.root, args.domain)
    out = catalog_to_json(notes)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"Wrote {len(notes)} notes -> {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


def cmd_lint(args: argparse.Namespace) -> int:
    root: Path = args.root
    domain = args.domain
    errors: list[str] = []
    warnings: list[str] = []

    domain_root = root / domain if domain else root
    if not domain_root.is_dir():
        print(f"ERROR: missing knowledge tree {domain_root}", file=sys.stderr)
        return 2

    # Scan topic notes only (skip _issues / underscore dirs)
    note_files: list[Path] = []
    for path in sorted(domain_root.rglob("*.md")):
        if path.name.lower() in SKIP_NAMES:
            continue
        rel_parts = path.relative_to(root).parts
        if len(rel_parts) < 3:
            continue
        if not is_topic_dir_name(rel_parts[1]):
            continue
        note_files.append(path)

    notes = []
    ids: dict[str, list[str]] = defaultdict(list)

    for path in note_files:
        text = path.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(text)
        rel = path.relative_to(root).as_posix()
        folder_topic = path.relative_to(root).parts[1]
        if not meta:
            errors.append(f"{rel}: missing YAML frontmatter")
            continue
        for f in REQUIRED_FIELDS:
            if not meta.get(f):
                errors.append(f"{rel}: missing frontmatter field `{f}`")
        tid = meta.get("id", "")
        if tid:
            ids[tid].append(rel)
        topic = meta.get("topic", "")
        if topic and topic != folder_topic:
            errors.append(f"{rel}: topic `{topic}` != folder `{folder_topic}`")
        note = load_note(path, root)
        if note:
            notes.append(note)

    for nid, paths in sorted(ids.items()):
        if len(paths) > 1:
            errors.append(f"duplicate id `{nid}`: {', '.join(paths)}")

    # topic intro.md (orientation only — no note-inventory sync)
    if domain:
        topic_dirs = [p for p in (root / domain).iterdir() if p.is_dir() and is_topic_dir_name(p.name)]
    else:
        topic_dirs = []
        for d in root.iterdir():
            if d.is_dir() and is_topic_dir_name(d.name):
                topic_dirs.extend(p for p in d.iterdir() if p.is_dir() and is_topic_dir_name(p.name))

    for tdir in topic_dirs:
        domain_name = tdir.parent.name
        topic_name = tdir.name
        note_stems = {p.stem for p in tdir.glob("*.md") if p.name.lower() not in SKIP_NAMES}
        intro = tdir / "intro.md"
        leftover_index = tdir / "index.md"
        if leftover_index.is_file():
            warnings.append(
                f"{domain_name}/{topic_name}: leftover index.md (use intro.md; do not maintain MOC)"
            )
        if note_stems and not intro.is_file():
            warnings.append(f"{domain_name}/{topic_name}: missing intro.md")
        if intro.is_file():
            intro_text = intro.read_text(encoding="utf-8")
            for link in extract_note_links(intro_text):
                target = resolve_note_link(link, tdir)
                if target is None:
                    errors.append(f"{domain_name}/{topic_name}/intro.md: dead link `{link}`")

    for e in errors:
        print(f"ERROR: {e}")
    for w in warnings:
        print(f"WARN: {w}")

    print(f"lint: {len(notes)} notes, {len(errors)} errors, {len(warnings)} warnings", file=sys.stderr)
    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    notes = build_catalog(args.root, args.domain)
    tokens = tokenize_query(args.query)
    ranked = []
    for n in notes:
        s = score_note(n, args.query, tokens)
        if s > 0:
            ranked.append((s, n))
    ranked.sort(key=lambda x: (-x[0], x[1].id))
    top = ranked[: args.limit]
    rows = [
        {
            "score": round(s, 2),
            "id": n.id,
            "title": n.title,
            "topic": n.topic,
            "description": n.description,
            "status": n.status,
        }
        for s, n in top
    ]
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    notes = build_catalog(args.root, args.domain)
    by_id = {n.id: n for n in notes}
    selected: list = []

    if args.ids:
        for raw in args.ids.split(","):
            nid = raw.strip()
            if not nid:
                continue
            if nid not in by_id:
                print(f"WARN: unknown id `{nid}`", file=sys.stderr)
                continue
            selected.append(by_id[nid])
    elif args.query:
        tokens = tokenize_query(args.query)
        ranked = sorted(
            ((score_note(n, args.query, tokens), n) for n in notes),
            key=lambda x: (-x[0], x[1].id),
        )
        selected = [n for s, n in ranked if s > 0][: args.limit]
    elif args.paths:
        for raw in args.paths.split(","):
            rel = raw.strip().replace("\\", "/")
            match = next((n for n in notes if n.rel_path == rel), None)
            if match:
                selected.append(match)
            else:
                print(f"WARN: unknown path `{rel}`", file=sys.stderr)
    else:
        print("ERROR: provide --ids, --query, or --paths", file=sys.stderr)
        return 2

    budget = args.budget
    parts: list[str] = []
    used = 0
    included_intros: set[tuple[str, str]] = set()
    included_ids: list[str] = []

    header = f"<!-- kb-pack budget={budget} notes_candidate={len(selected)} -->\n"
    used += estimate_tokens(header)
    parts.append(header)

    for n in selected:
        if n.status.strip().lower() == "draft" and used > budget * 0.7:
            continue
        key = (n.domain, n.topic)
        if key not in included_intros:
            intro = topic_intro_path(args.root, n.domain, n.topic)
            if intro.is_file():
                intro_text = intro.read_text(encoding="utf-8")
                block = f"\n---\n# intro: {n.domain}/{n.topic}\n\n{intro_text.strip()}\n"
                cost = estimate_tokens(block)
                if used + cost <= budget:
                    parts.append(block)
                    used += cost
                    included_intros.add(key)
        body_block = (
            f"\n---\n# {n.title}\n"
            f"<!-- id={n.id} status={n.status} -->\n\n"
            f"{n.body.strip()}\n"
        )
        cost = estimate_tokens(body_block)
        if used + cost > budget:
            if args.truncate and budget - used > 200:
                remain = (budget - used) * 4
                trunc = body_block[:remain] + "\n\n… [truncated by kb-pack]\n"
                parts.append(trunc)
                used = budget
                included_ids.append(n.id + " (truncated)")
            break
        parts.append(body_block)
        used += cost
        included_ids.append(n.id)

    footer = f"\n---\n<!-- packed_ids: {', '.join(included_ids)} tokens~={used}/{budget} -->\n"
    parts.append(footer)
    bundle = "".join(parts)
    if args.output:
        Path(args.output).write_text(bundle, encoding="utf-8")
        print(f"Wrote pack tokens~={used}/{budget} -> {args.output}", file=sys.stderr)
    else:
        print(bundle)

    if args.compare_spec:
        spec_path = Path(args.compare_spec)
        if spec_path.is_file():
            spec_tok = estimate_tokens(spec_path.read_text(encoding="utf-8"))
            print(
                f"compare: pack~={used} tokens vs SPEC {spec_path.name}~={spec_tok} tokens "
                f"({100 * used / spec_tok:.0f}% of SPEC)" if spec_tok else "compare: empty SPEC",
                file=sys.stderr,
            )
        else:
            print(f"WARN: compare-spec not found: {spec_path}", file=sys.stderr)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    notes = build_catalog(args.root, args.domain)
    note = next((n for n in notes if n.id == args.id), None)
    if note is None:
        print(f"ERROR: unknown id `{args.id}`", file=sys.stderr)
        return 1
    # Read source file; do not print filesystem path
    text = Path(note.path).read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    print(text, end="")
    return 0


def cmd_feedback(args: argparse.Namespace) -> int:
    ftype = args.type.strip().lower()
    if ftype not in FEEDBACK_TYPES:
        print(
            f"ERROR: --type must be one of {', '.join(sorted(FEEDBACK_TYPES))}",
            file=sys.stderr,
        )
        return 2
    domain = args.domain.strip()
    if not domain or "/" in domain or "\\" in domain or ".." in domain:
        print("ERROR: invalid --domain", file=sys.stderr)
        return 2
    domain_root = args.root / domain
    if not domain_root.is_dir():
        print(f"ERROR: missing domain `{domain}`", file=sys.stderr)
        return 2

    title = args.title.strip()
    body = args.body.strip()
    if not title or not body:
        print("ERROR: --title and --body are required", file=sys.stderr)
        return 2

    slug = slugify_feedback_title(title)
    fb_root = feedback_dir(args.root, domain)
    try:
        out_path = unique_feedback_path(fb_root, slug)
        ensure_under_dir(out_path, fb_root.resolve())
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    about = (args.about or "").strip()
    fid = f"feedback.{domain}.{out_path.stem}"
    about_line = f'about: "{about}"\n' if about else ""
    text = (
        f"---\n"
        f'id: "{fid}"\n'
        f'title: "{title}"\n'
        f'type: "{ftype}"\n'
        f"{about_line}"
        f'status: "open"\n'
        f'source: "client"\n'
        f"---\n\n"
        f"{body}\n"
    )
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote feedback id={fid}", file=sys.stderr)
    return 0


def cmd_dup(args: argparse.Namespace) -> int:
    notes = build_catalog(args.root, args.domain)
    title = (args.title or "").lower()
    desc = (args.description or "").lower()
    hits = []
    for n in notes:
        score = 0.0
        if title and title in n.title.lower():
            score += 20
        if title and any(t in n.title.lower() for t in title.split() if len(t) > 2):
            score += 8
        if desc and desc in n.description.lower():
            score += 25
        for t in tokenize_query(desc or title):
            if t in n.description.lower():
                score += 10
            if t in n.title.lower():
                score += 6
        if score > 0:
            hits.append((score, n))
    hits.sort(key=lambda x: -x[0])
    rows = [
        {"score": round(s, 2), "id": n.id, "title": n.title, "description": n.description, "path": n.rel_path}
        for s, n in hits[: args.limit]
    ]
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def cmd_domains(args: argparse.Namespace) -> int:
    rows = list_domains(args.root)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    if not rows:
        print("WARN: no domains under knowledge root", file=sys.stderr)
        return 1
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    root: Path = args.root
    targets = list(INIT_CORPUS_FILES)
    if args.readme:
        targets.extend(INIT_README_FILES)

    exit_code = 0
    for dest_name, template_name in targets:
        try:
            action = init_corpus_file(
                root,
                dest_name,
                template_name,
                force=args.force,
                check=args.check,
            )
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

        rel = dest_name
        if action == "created":
            print(f"Wrote {rel}", file=sys.stderr)
        elif action == "updated":
            print(f"Updated {rel}", file=sys.stderr)
        elif action == "unchanged":
            print(f"OK: {rel} matches template", file=sys.stderr)
        elif action == "skipped":
            print(f"SKIP: {rel} exists (use --force to overwrite)", file=sys.stderr)
        elif action == "missing":
            print(f"MISSING: {rel} (run init without --check to create)", file=sys.stderr)
            exit_code = 1
        elif action == "differs":
            print(f"DIFF: {rel} differs from engine template (use --force to update)", file=sys.stderr)
            exit_code = 1

    return exit_code


def cmd_intro(args: argparse.Namespace) -> int:
    topic = (args.topic or "").strip()
    if topic:
        path = topic_intro_path(args.root, args.domain, topic)
        label = f"{args.domain}/{topic}/intro.md"
    else:
        path = domain_intro_path(args.root, args.domain)
        label = f"{args.domain}/intro.md"
    if not path.is_file():
        print(f"ERROR: missing {label}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    print(text, end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="knowledge-base", description="Knowledge Engine CLI")
    p.add_argument(
        "--root",
        type=Path,
        default=None,
        help="KB tree root (default: env KB_ROOT or KNOWLEDGE_BASE_ROOT)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("catalog", help="Scan notes → JSON catalog")
    c.add_argument("--domain", default=None)
    c.add_argument("-o", "--output", default=None)
    c.set_defaults(func=cmd_catalog)

    dom = sub.add_parser("domains", help="List KB domains under knowledge/")
    dom.set_defaults(func=cmd_domains)

    intro = sub.add_parser("intro", help="Print domain or topic intro.md")
    intro.add_argument("domain", help="domain id, e.g. acme")
    intro.add_argument("topic", nargs="?", default=None, help="optional topic id")
    intro.set_defaults(func=cmd_intro)

    l = sub.add_parser("lint", help="Validate frontmatter and intro links")
    l.add_argument("--domain", required=True)
    l.add_argument("--strict", action="store_true", help="warnings fail")
    l.set_defaults(func=cmd_lint)

    r = sub.add_parser("route", help="Match task → note list")
    r.add_argument("query")
    r.add_argument("--domain", default=None)
    r.add_argument("--limit", type=int, default=5)
    r.set_defaults(func=cmd_route)

    pk = sub.add_parser("pack", help="Assemble note bundle under token budget")
    pk.add_argument("--domain", default=None)
    pk.add_argument("--ids", default=None, help="comma-separated ids")
    pk.add_argument("--paths", default=None, help="comma-separated rel paths")
    pk.add_argument("--query", default=None)
    pk.add_argument("--limit", type=int, default=5, help="when using --query")
    pk.add_argument("--budget", type=int, default=4000)
    pk.add_argument("--truncate", action="store_true", help="truncate last note to fill budget")
    pk.add_argument("-o", "--output", default=None)
    pk.add_argument("--compare-spec", default=None, help="path to SPEC file for token compare")
    pk.set_defaults(func=cmd_pack)

    sh = sub.add_parser("show", help="Print one note by id (consumer)")
    sh.add_argument("--id", required=True, help="note id")
    sh.add_argument("--domain", default=None)
    sh.set_defaults(func=cmd_show)

    fb = sub.add_parser("feedback", help="Write client feedback under domain/_feedback/")
    fb.add_argument("--domain", required=True)
    fb.add_argument("--about", default="", help="related note id")
    fb.add_argument("--type", required=True, help="wrong | gap | stale | unclear")
    fb.add_argument("--title", required=True)
    fb.add_argument("--body", required=True)
    fb.set_defaults(func=cmd_feedback)

    d = sub.add_parser("dup", help="Suggest existing notes before creating")
    d.add_argument("--title", default="")
    d.add_argument("--description", default="")
    d.add_argument("--domain", default=None)
    d.add_argument("--limit", type=int, default=8)
    d.set_defaults(func=cmd_dup)

    init = sub.add_parser("init", help="Ship full RULE_KB_BUILD as corpus AGENTS.md (optional README)")
    init.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing files",
    )
    init.add_argument(
        "--check",
        action="store_true",
        help="report drift; exit 1 if update needed",
    )
    init.add_argument(
        "--readme",
        action="store_true",
        help="also write README.md for humans (AGENTS.md is enough for agents)",
    )
    init.set_defaults(func=cmd_init)

    return p


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.root = resolve_knowledge_root(args.root)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
