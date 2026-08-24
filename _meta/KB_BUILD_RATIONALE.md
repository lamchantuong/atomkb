# KB_BUILD — Rationale

Chú thích **vì sao** rule như hiện tại. Không nhét vào AGENTS để tiết kiệm context. Đọc khi hiệu chỉnh quy tắc.

Cập nhật: 2026-08-18

---

## Tên file / vị trí

| File | Vai trò |
|------|---------|
| [`RULE_KB_BUILD.md`](RULE_KB_BUILD.md) | **Bản gốc** rule trong repo engine; ship đầy đủ → `knowledge-base --root <kb> init` |
| Repo KB (ngoài engine) | Corpus + `AGENTS.md` đầy đủ (ship từ `RULE_KB_BUILD`); git riêng; CLI trỏ bằng `KB_ROOT` / `--root` |
| `<domain>/AGENTS.md` | Chỉ khi cần override domain (mặc định: không có) |
| Repo skills (`myskills`) | Playbook agent (`npx skills`); **không** nhân bản rule dài — pointer về `_meta/` |

Theo [agents.md](https://agents.md/). Repo engine dùng `AGENTS.md` mỏng ở root làm router; rule chi tiết nằm ở `_meta/RULE_KB_BUILD.md` để tránh inject toàn bộ rule mặc định. Client skills không nằm trong engine.

---

## Quyết định

| Chủ đề | Quyết định | Lý do |
|--------|------------|--------|
| Độ dài note (số từ) | Bỏ | Tập trung một khái niệm; tối ưu độ dài là task riêng. |
| Tổ chức thư mục | `<kb-root>/<domain>/<topic>/` + `intro.md` | **Domain** = phạm vi KB (vd. `acme`) — rộng hơn “product”. **Topic** = đơn vị tri thức phẳng trong domain (không nested theo module sản phẩm). `intro` định hướng; inventory note = tool (`route`/`catalog`), không MOC/`index.md`. |
| Inbox triage | `<domain>/_issues/` | Prefix `_` = không phải topic. Một chỗ cho conflict/gap/stale/unclear khi nạp KB; không thư mục `conflict/` riêng (quá hẹp). Vé pointer + claim, không bản sao note. |
| AGENTS theo domain | Không (một `AGENTS` ở root cây KB) | Tránh lệch bản giữa domain; override domain chỉ khi thật sự lệch rule. |
| Engine vs corpus vs skill | Engine = CLI + rule; corpus = note; skill = myskills | Tránh nested git; skill không trong `_meta/`; nhiều KB / máy chỉ đổi `KB_ROOT`. |
| Session notes trong repo engine | Không commit; `.agents/` local-only | Quyết định bền vững nên ghi vào rationale/rule; chat-minutes hữu ích để xem lại ngắn hạn nhưng dài dòng và không nên thành lịch sử chuẩn của repo. |
| Optional resource / git | Rule `_meta/`, không skill riêng | Quá mỏng / trùng user-rule commit; disclosed từ `kb-maintainer` / `kb-migrate`. |
| `00_ROUTE` / inventory markdown | Không | Topic/`intro.md` định hướng; `route`/`dup`/`catalog` là nguồn tìm note — tránh bảng note trong md (outdate, tốn token). |
| `when` → `description` | Có | Cùng convention skill. |
| Checklist | Đề xuất, không bắt buộc | Tránh conflict rule khác. |
| Task tracking | Không thuộc engine | Knowledge Engine = note + CLI. Queue file tạm = `task-kanban` (myskills). Tracker lâu dài = Task-engine riêng. |
| Resource / git | File rule độc lập trong `_meta/`; không skill riêng | Không phải chuẩn tri thức cốt lõi; disclosed từ skill maintainer/migrate. |
| Migrate SPEC wave | Skill `kb-migrate` (myskills); không trong AGENTS cốt lõi | Kickoff session; prompt engine chỉ pointer. |

---

## Frontmatter

Giữ `derivation` (cách hình thành) + `status` (`draft` \| `tested` \| `verified`) cho tin cậy; `id` / `topic` / `description` cho tool. **Bỏ `confidence`** — agent không truy cập internal model confidence, nên field này chỉ thành proxy tự gán, khó hiệu chuẩn và dễ tạo cảm giác chính xác giả. Với bài toán bảo trì KB, nên ưu tiên tín hiệu dựa trên bằng chứng như `status`, `derivation`, `_feedback` / `_issues`, hoặc một field vận hành riêng nếu sau này thật sự cần. Bỏ `Applied` khỏi enum status — “đã dùng trong task” không phải mức kiểm chứng.
