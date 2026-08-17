# Prompt — migrate wave (SPEC / monolith → atomic notes)

**Không phải rule.** Canonical kickoff: skill **`kb-migrate`** trong repo skills (`C:\TuongLC\Project\myskills` → `skills/kb/kb-migrate/SKILL.md`), cài vào corpus:

```bash
npx skills add ./myskills --skill kb-migrate --skill kb-maintainer
```

Queue lock (nếu nhiều agent): thêm `--skill task-kanban` — stopgap file-queue, **không** phải Knowledge Engine. Tracker lâu dài: Task-engine riêng.

Rồi chạy `/kb-migrate` (hoặc dán khối kickoff trong skill đó).

File này giữ trong engine chỉ làm **pointer**. SoT note: [`_meta/RULE_KB_BUILD.md`](_meta/RULE_KB_BUILD.md). Bulk: [`_meta/RULE_RESOURCE_CONTROL.md`](_meta/RULE_RESOURCE_CONTROL.md).

## Không dùng khi

- Viết/sửa vài note lẻ → `/kb-maintainer` + corpus `AGENTS.md`.
- Chỉ cần lock queue → `/task-kanban` (myskills) hoặc Task-engine khi có.
