# ROADMAP — Knowledge Engine

Cập nhật: 2026-08-18

## Định hướng (map rule)

- Router: [`../AGENTS.md`](../AGENTS.md).
- Rule KB gốc: [`RULE_KB_BUILD.md`](RULE_KB_BUILD.md) → khi ship: dùng làm nguồn cho `AGENTS.md` của repo KB đích.
- Corpus: **ngoài** engine — root qua `KB_ROOT` / `KNOWLEDGE_BASE_ROOT` hoặc `--root` (vd. `C:\TuongLC\AI_workspace\knowledge`). Không nested git trong engine.
- Skills: **ngoài** engine — `C:\TuongLC\Project\myskills` (`npx skills add`). Không `_meta/skills/` trong engine.
- Rationale: [`KB_BUILD_RATIONALE.md`](KB_BUILD_RATIONALE.md).
- Optional: [`RULE_RESOURCE_CONTROL.md`](RULE_RESOURCE_CONTROL.md), [`RULE_GIT.md`](RULE_GIT.md).
- Task tracking: **không** thuộc engine. Stopgap: skill `task-kanban` (myskills). Lâu dài: Task-engine riêng.
- Migrate wave: skill `kb-migrate` (myskills); pointer engine [`../PROMPT_KB_MIGRATE_WAVES.md`](../PROMPT_KB_MIGRATE_WAVES.md).

## Đã có

### Rule & cấu trúc mục tiêu

- Cây: `<domain>/<topic>/` dưới KB root (`intro.md` + atomic notes) — chuẩn trong `RULE_KB_BUILD`.
- Map migrate (nếu có) nằm **trong domain**: `<domain>/MIGRATE_SPEC_MAP.md` — không gắn `_meta` engine.

### Tool truy vấn / gộp thông tin

- Spec: [`TOOLS.md`](TOOLS.md). Entry: `knowledge-base` (`pip install -e .`); maintainer: `python tools/knowledge_base_cli.py`.
- Consumer: `domains` / `intro` / `route` / `pack` / `show` / `feedback`.
- Maintainer: `catalog` / `lint` / `dup`.
- Index theo frontmatter (`id`, `topic`, `description`) — keyword match, chưa embedding / MCP.
- Skill client: repo **myskills** (`kb-consumer`, `kb-maintainer`, `kb-migrate`, …) — không trong engine.
- Engine ↔ corpus ↔ skill tách repo; CLI bắt buộc có root (env hoặc `--root`).

## Tiếp theo

Ưu tiên **nội dung + kiểm chứng**, không mở rộng tool cho đến khi corpus ổn.

### 1. Validate CLI trên KB ngoài

- `KB_ROOT` trỏ repo corpus; `domains` / `lint` / `route` / `pack` chạy trên note thật.
- **Done khi:** lint domain seed exit 0; consumer skill dùng được với env root.

### 2. Migrate wave (nếu có nguồn SPEC)

- Viết `MIGRATE_SPEC_MAP.md` trong domain; một lượt agent = **một topic**.
- Kickoff: `/kb-migrate` (myskills) — xem pointer [`../PROMPT_KB_MIGRATE_WAVES.md`](../PROMPT_KB_MIGRATE_WAVES.md). Queue lock nếu cần: `task-kanban` (stopgap), không phải CLI engine.
- **Done khi:** topic đích lint sạch; không sửa map/`_meta` trong cùng lượt.

### 3. Validate đường consumer

- Cài skill `kb-consumer` từ myskills; thử luồng `route` → `pack|show` → (nếu cần) `feedback` từ góc agent ngoài engine.
- **Done khi:** pack theo budget trả đúng id; vé `_feedback/` tạo được; maintainer triage được ít nhất một vé mẫu.

## Ngoài phạm vi hiện tại

- MCP wrapper / vector search.
- Split binary consumer/maintainer hay auto-write note.
- Git submodule / nested repo engine+corpus.
- Task tracker / Kanban trong engine (Task-engine riêng).
