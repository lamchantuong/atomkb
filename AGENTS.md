# AGENTS.md

Repo này là **Knowledge Engine** (CLI + rule). Cây note nằm **ngoài** repo — truyền bằng `--root` hoặc env `KB_ROOT` / `KNOWLEDGE_BASE_ROOT`.

- `AGENTS.md` này là **router ngắn**: cho biết nên đọc rule nào, khi nào.
- Rule chi tiết nằm trong `_meta/`. Không nhét full rule vào đây để tránh tăng context mặc định.
- **Engine ≠ corpus ≠ skill.** Client skills sống ở `C:\TuongLC\Project\myskills` — cài bằng `npx skills add` (không nằm trong repo này).

## Đọc khi nào

| File | Khi đọc |
|------|---------|
| [`_meta/RULE_KB_BUILD.md`](_meta/RULE_KB_BUILD.md) | Tạo/sửa note trong KB root ngoài engine, thêm topic/`intro.md`, xử lý `_issues/` / `_feedback/` |
| [`_meta/AGENTS_CORPUS.template.md`](_meta/AGENTS_CORPUS.template.md) | Stub `AGENTS.md` cho repo corpus — ship bằng `knowledge-base --root <kb-root> init` |
| [`_meta/RULE_RESOURCE_CONTROL.md`](_meta/RULE_RESOURCE_CONTROL.md) | Bulk edit, migrate nhiều file, hoặc cần throttling |
| [`_meta/RULE_GIT.md`](_meta/RULE_GIT.md) | Theo dõi/commit thay đổi note trong **repo KB** (git riêng) |
| [`_meta/TOOLS.md`](_meta/TOOLS.md) | CLI `knowledge-base` (`pip install -e .`): consumer `route`/`pack`/`show`/`feedback`; maintainer `catalog`/`lint`/`dup`/`init` |
| [`_meta/ROADMAP.md`](_meta/ROADMAP.md) | Định hướng engine: đã có / tiếp theo / ngoài phạm vi — không phải rule xây note |
| [`_meta/KB_BUILD_RATIONALE.md`](_meta/KB_BUILD_RATIONALE.md) | Chỉ đọc khi muốn chỉnh chính rule hoặc hiểu vì sao rule được thiết kế như vậy |
| [`PROMPT_KB_MIGRATE_WAVES.md`](PROMPT_KB_MIGRATE_WAVES.md) | Pointer migrate wave → skill `kb-migrate` trong myskills |

## Ghi nhớ nhanh

- Engine ≠ corpus ≠ skill: note không sống trong repo này; skill client không sống trong repo này.
- **Task tracking không thuộc engine.** Queue file tạm: skill `task-kanban` (myskills). Tracker lâu dài: Task-engine riêng (dự kiến).
- Root KB qua `KB_ROOT` hoặc `--root`. Skills: `C:\TuongLC\Project\myskills` (`kb-consumer`, `kb-maintainer`, `kb-migrate`, …).
- Với KB: `intro.md` (domain/topic) để định hướng; tìm note bằng `knowledge-base route`/`dup`, rồi mới đọc note cụ thể.
- Note mới/sửa phải theo `RULE_KB_BUILD`; đừng suy từ các file prompt/agent cũ.
