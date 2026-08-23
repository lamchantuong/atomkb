# TOOLS — Knowledge Engine CLI

Cập nhật: 2026-08-17

CLI đọc cây KB **bên ngoài** engine. Root = `--root` hoặc env `KB_ROOT` / `KNOWLEDGE_BASE_ROOT` (bắt buộc một trong hai). Rule note: [`RULE_KB_BUILD.md`](RULE_KB_BUILD.md).

Thư mục `_…` dưới domain (vd. `_issues/`, `_feedback/`) không phải topic — catalog / lint / route bỏ qua.
`intro.md` (domain/topic) = định hướng; **không** inventory note. Tìm note bằng `route` / `dup` / `catalog`.

## Cài đặt (PATH)

Từ root repo engine (một lần):

```bash
pip install -e .
```

Lệnh trên PATH: **`knowledge-base`** (không alias `kb`). Python 3.10+, stdlib only.

Maintainer trong repo: `python tools/knowledge_base_cli.py <command>`.

Ví dụ root (Windows):

```bash
set KB_ROOT=C:\TuongLC\AI_workspace\knowledge
```

---

## Hai mặt lệnh

| Mặt | Lệnh | Ai dùng |
|-----|------|---------|
| **Consumer** | `domains`, `intro`, `route`, `pack`, `show`, `feedback` | Agent project khác (skill `kb-consumer` trong myskills) |
| **Maintainer** | `catalog`, `lint`, `dup`, `init` (+ `--root` / `--paths` / `--compare-spec`) | Người/agent sửa KB (skill `kb-maintainer` trên corpus) |

Consumer: `route` / `pack` / `show` **không** in filesystem `path`. Client **không** sửa note — chỉ `feedback`.

Skill client **không** nằm trong engine. Repo: `C:\TuongLC\Project\myskills` — cài ví dụ:

```bash
npx skills add C:\TuongLC\Project\myskills --skill kb-consumer -g
```

Xem `myskills/README.md` cho recipe theo loại repo (app / corpus / migrate).

---

## Luồng (consumer)

```text
task → knowledge-base domains (chọn domain)
    → knowledge-base intro [topic]
    → knowledge-base route → knowledge-base pack|show → agent context
                              ↓ (nếu nghi sai)
                         knowledge-base feedback
```

Maintainer: `lint` / `catalog` / `dup` / triage `_feedback/` → sửa note (trong repo KB).

---

## Commands

| Command | Việc |
|---------|------|
| `domains` | Liệt kê domain (intro / topics / notes) |
| `intro` | In `intro.md` domain, hoặc topic nếu truyền thêm arg |
| `route` | Match task → id / title / description (không path) |
| `pack` | Gộp intro topic (nếu có) + note theo budget |
| `show` | In một note theo `--id` |
| `feedback` | Ghi vé client vào `<domain>/_feedback/` |
| `catalog` | Scan note → JSON (có path; maintainer) |
| `lint` | Frontmatter, id trùng, topic≠folder, link trong intro, thiếu intro / leftover `index.md` |
| `dup` | Gợi ý trùng title/description trước khi tạo note |
| `init` | Ghi `AGENTS.md` corpus từ template engine; optional `--readme` |

### Consumer — `domains` / `intro` / `route` / `pack` / `show` / `feedback`

```bash
knowledge-base domains
knowledge-base intro <domain>
knowledge-base intro <domain> <topic>
knowledge-base route "mô tả task" --domain <domain> --limit 5
knowledge-base pack --ids <domain>.topic.note-a,<domain>.topic.note-b --budget 4000
knowledge-base show --id <domain>.topic.note-a --domain <domain>
knowledge-base feedback --domain <domain> --about <domain>.topic.note-a --type wrong --title "…" --body "…"
```

Match `route`: exact `id` → keyword `description`/`title` → `topic`.  
Task end-to-end: ưu tiên note `topic: workflows` / id `*.workflow.*`; sau `route`, `pack --ids` theo playbook.

`pack`: kèm `intro.md` topic (một lần / topic) trước body note; bỏ / xếp sau `status: draft` khi đầy budget (~70%). Không nhét MOC/`index.md`.

`feedback` `--type`: `wrong` | `gap` | `stale` | `unclear`.

### Maintainer — `catalog` / `lint` / `dup` / `init`

```bash
knowledge-base catalog --domain <domain>
knowledge-base catalog --domain <domain> -o .cache/kb-catalog.json
knowledge-base lint --domain <domain>
knowledge-base dup --title "Short title" --description "khi nào dùng" --domain <domain>
knowledge-base --root . init                    # AGENTS.md stub (cwd = kb-root)
knowledge-base --root . init --check            # drift check; exit 1 if stale
knowledge-base --root . init --force            # refresh stub from engine template
knowledge-base --root . init --readme           # + README.md cho người (optional)
```

Template nguồn: `_meta/AGENTS_CORPUS.template.md` (và `README_CORPUS.template.md` khi `--readme`). Skill cài riêng: `npx skills add … --skill kb-maintainer` — không gộp vào `init`.

`lint`: exit ≠ 0 nếu lỗi (warning không fail trừ `--strict`). Cảnh báo thiếu `intro.md`, leftover `index.md`; **không** bắt mọi note phải được liệt kê trong intro.

---

## Trì hoãn

- Vector/embedding, MCP đầy đủ, split binary consumer/maintainer, auto-write note — xem roadmap.

---

## So token (pack vs monolith)

Ước lượng thô: `chars/4`. So sánh với nguồn monolith (nếu có):

```bash
knowledge-base pack --query "…" --domain <domain> --budget 4000 --compare-spec <spec-file> -o .cache/pack-sample.md
```

**Kết luận:** `route` rồi `pack --ids … --budget` mới tiết kiệm; `pack --query` với limit cao dễ vượt một file nguồn monolith.
