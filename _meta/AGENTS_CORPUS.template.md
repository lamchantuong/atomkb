# AGENTS.md

Repo này là **cây knowledge** (corpus). CLI nằm ở repo **engine** riêng (`pip install -e .` → lệnh `knowledge-base`).

Trỏ CLI vào đây (cwd = kb-root):

```bash
knowledge-base --root . domains
```

Hoặc env `KB_ROOT` / `KNOWLEDGE_BASE_ROOT` (PowerShell: `$env:KB_ROOT = (Get-Location).Path`).

Rule đầy đủ: repo engine `_meta/RULE_KB_BUILD.md` (ngoài corpus — mở repo engine khi cần chỉnh rule gốc). Cập nhật stub này: `knowledge-base --root . init --force`.

## Sửa note (maintainer)

- Cây: `<domain>/<topic>/` + `intro.md` (định hướng; **không** inventory note; intro **không** cần frontmatter atomic).
- Topic phẳng trong domain — không lồng thư mục theo module sản phẩm.
- Một khái niệm / file; frontmatter đủ: `id`, `title`, `topic`, `description`, `origin`, `derivation`, `status`.
- `derivation`: Q | S | I | A | P | C; `status`: draft | tested | verified.
- Trước khi tạo note: `knowledge-base dup …`; sau khi sửa: `knowledge-base lint --domain <domain>`.
- Tìm note: `route` / `dup` / `catalog` — không duy trì MOC / `index.md`.
- Link Markdown relative (`[note](note.md)`); không `[[wikilink]]`.
- Nguồn mơ hồ / mâu thuẫn → vé `<domain>/_issues/` (inbox triage; thường gitignore).
- Client ngoài → `knowledge-base feedback` → `_feedback/` (**không** sửa atomic note trực tiếp).
- Git repo này = nhật ký đổi note; `_issues` / `_feedback` thường không commit; không tự commit trừ khi được yêu cầu.

Skill Cursor (repo `myskills`, ngoài engine): `kb-maintainer` trên corpus; `kb-consumer` trên app.
