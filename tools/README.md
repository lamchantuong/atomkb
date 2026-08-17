# tools/

CLI Knowledge Engine. Spec: [`../_meta/TOOLS.md`](../_meta/TOOLS.md).

Cài PATH (từ root repo engine): `pip install -e .` → lệnh **`knowledge-base`**.

Root KB (bắt buộc): env `KB_ROOT` / `KNOWLEDGE_BASE_ROOT`, hoặc `--root`.

```bash
set KB_ROOT=C:\TuongLC\AI_workspace\knowledge
knowledge-base intro <domain>
knowledge-base intro <domain> <topic>
knowledge-base route "…" --domain <domain>
knowledge-base pack --ids <domain>.topic.note --budget 4000
knowledge-base show --id <domain>.topic.note --domain <domain>
knowledge-base feedback --domain <domain> --type gap --title "missing X" --body "…"
```

Maintainer: `python tools/knowledge_base_cli.py …` — thêm `catalog` / `lint` / `dup`.

Modules: `knowledge_base_cli.py`, `knowledge_base_lib.py` (stdlib, Python 3.10+).
