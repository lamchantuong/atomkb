# AGENTS.md

> **Source rule:** `RULE_KB_BUILD.md` — bản gốc rule xây / sửa knowledge base. Khi ship vào KB đích: copy nội dung phù hợp vào `AGENTS.md` của repo KB đó.
> **Scope:** Quy tắc xây / sửa knowledge base (atomic notes). Không gồm task Kanban hay throttling — xem file rule độc lập trong `_meta/`.
> Corpus nằm **ngoài** repo engine — CLI trỏ bằng `--root` / `KB_ROOT`. Sửa rule tại file này (engine); agent sửa note làm việc trong repo KB.

---

## Goal

Knowledge dễ capture, dễ tìm, dễ tin. Agent định hướng bằng `intro.md` (domain/topic), tìm note bằng tool (`route` / `dup` / `catalog`), rồi đọc note cụ thể — **không** duy trì bảng liệt kê note (MOC) trong markdown.

---

## Structure

- **One concept per file** — một khái niệm / một logic / một pattern. Không gộp chủ đề lệch nhau.
- **Domain** rồi mới **topic**: `<kb-root>/<domain>/<topic>/` (kb-root = env/`--root`, không nằm trong repo engine).
  - `<domain>` = phạm vi KB (vd. `acme`) — tách nhiều domain cạnh nhau, không trộn note.
  - `<topic>/` = đơn vị tri thức; mỗi topic có `intro.md` (định hướng), không nhồi nội dung note, **không** làm inventory note.
  - Trong một domain: chỉ topic phẳng — không thêm tầng thư mục theo module sản phẩm.
  - Thư mục tên bắt đầu `_` **không** phải topic (vd. `_issues/`) — không `intro.md` topic, không atomic note.
- Tên domain, topic, file note: `lowercase-kebab-case`. `id`: dot-namespace ổn định (`acme.forms.tabs`).
- Note và `intro.md`: mặc định tiếng Việt (override theo domain nếu cần). Snippet mã nguồn giữ nguyên.
- `AGENTS.md` nằm ở root cây KB (kb-root). Domain **không** nhân đôi file này trừ khi cần override ngắn, có chủ đích.
- Mỗi domain **có thể** có `intro.md` (cửa vào domain — không thay `workflows/` hay `knowledge-base route`; không cần frontmatter atomic).
- Mỗi topic **có** `intro.md` (topic là gì / khi nào mở — ngắn; không bảng liệt kê mọi note).
- Mỗi domain **có thể** có `_issues/` — inbox triage khi nạp / sửa tri thức (conflict, gap, …). Không phải kiến thức tin được; không nhân đôi body note.
- Mỗi domain **có thể** có `_feedback/` — inbox **client** (agent ngoài engine) qua `knowledge-base feedback`; không sửa note trực tiếp.

```text
<kb-root>/                 ← repo git riêng; CLI: KB_ROOT hoặc --root
├── AGENTS.md              ← copy/tóm tắt từ RULE_KB_BUILD khi ship
├── <domain>/
│   ├── intro.md           ← optional: domain là gì / cửa vào
│   ├── workflows/         ← optional: playbook theo task
│   ├── _issues/           ← optional: vé triage maintainer (không phải topic)
│   ├── _feedback/         ← optional: vé feedback client (không phải topic)
│   ├── <topic>/
│   │   ├── intro.md       ← định hướng topic (không inventory note)
│   │   └── <note>.md
│   └── …
└── <other-domain>/
    └── <topic>/…
```

### `intro.md` (domain / topic)

- **Không** thay thế `route` / `dup` / `catalog`: intro định hướng; tool mới là nguồn “có note nào / id nào”.
- **Không** bắt buộc cập nhật intro mỗi khi thêm/xóa note — tránh outdate và tốn token.
- Topic intro: vài câu (phạm vi, khi nào dùng); có thể trỏ 1–2 note “cửa vào”, không bảng đủ mọi file.
- Không tạo `index.md` / MOC song song.

### `_issues/` (triage)

Khi nạp kiến thức mới mà **chưa** ghi/sửa note an toàn (mâu thuẫn, thiếu chỗ gắn, nguồn mơ hồ, note cũ lỗi thời): tạo vé trong `<domain>/_issues/`, **không** tạo topic/`conflict/` riêng, **không** copy full body note (anti-duplication).

- File: `lowercase-kebab-case.md` (một vé / file).
- Không liệt kê trong `intro.md`; tool catalog/lint/route **bỏ qua** thư mục này.
- Lock / theo dõi công việc **không** thuộc engine. Stopgap file-queue: skill `task-kanban` (myskills). Tracker lâu dài: Task-engine riêng.

```yaml
---
id: "issue.acme.foo-vs-bar"
title: "Foo vs bar — mâu thuẫn nguồn"
type: "conflict"             # conflict | gap | stale | unclear
affects: "topic.note-a, topic.note-b"
status: "open"               # open | resolved
---
```

Body tối thiểu: hai (hoặc nhiều) phía claim + nguồn; pointer `affects` tới `id` note. Khi `resolved`: cập nhật note liên quan (`status` / nội dung), rồi xóa vé hoặc đổi `status: resolved` và archive (không để claim đối lập cạnh note `verified`).

### `_feedback/` (client inbox)

Agent/client **không** sửa atomic note. Khi nghi sai / thiếu / stale: `knowledge-base feedback` ghi vé dưới `<domain>/_feedback/`.

- Không liệt kê trong `intro.md`; catalog/lint/route **bỏ qua** (prefix `_`).
- Khác `_issues/`: `_issues` = maintainer khi build KB; `_feedback` = tín hiệu từ client, chờ người/agent KB triage → sửa note hoặc chuyển `_issues/`.
- Frontmatter tối thiểu: `id`, `title`, `type` (`wrong` | `gap` | `stale` | `unclear`), `status`, `source: client`; optional `about` (note id).

---

## Frontmatter

Mọi note có frontmatter. Điền phần tĩnh **trước** body; cập nhật `status` **sau** khi viết xong (hoặc khi có bằng chứng kiểm).

```yaml
---
id: "acme.forms.tabs"
title: "Form — Tabs"
topic: "forms"                   # khớp thư mục <kb-root>/<domain>/<topic>/
description: "Thêm / cấu hình tab trên form"
origin: "…"
derivation: "S"                  # Q | S | I | A | P | C  [tĩnh]
status: "draft"                  # draft | tested | verified  [động]
---
```

`description`: một dòng, cùng vai trò description của skill — Agent/tool match task.

Frontmatter phải là YAML hợp lệ.

### `derivation` (cách hình thành)

| Mã | Nghĩa | Khi dùng |
|----|--------|----------|
| **Q** | Trích dẫn gần nguyên văn | Copy rule/code từ nguồn |
| **S** | Tóm tắt / cấu trúc lại | Migrate SPEC → note (mặc định) |
| **I** | Suy luận từ nhiều nguồn | Workflow / playbook ghép từ note |
| **A** | Giả định chưa có bằng chứng | Tạm; nên kèm `_issues/` |
| **P** | Suy đoán yếu | Hiếm; ưu tiên `A` + issue |
| **C** | Sáng tạo mới (không từ nguồn) | Pattern tự nghĩ |

### `status` (mức kiểm chứng)

| Giá trị | Nghĩa |
|---------|--------|
| `draft` | Đã ghi, **chưa** kiểm trên project / runtime |
| `tested` | Đã thử trên môi trường thật (dev/UAT/customer) |
| `verified` | Ổn định, đối chiếu nguồn + thực tế |

Quy tắc điền: note mới / migrate SPEC → `draft`. Chỉ lên `tested` khi có bằng chứng chạy thật. `verified` hiếm. `derivation` ∈ {A, P, C} → mặc định `draft`.

---

## Anti-duplication

1. Trước khi tạo note: `knowledge-base dup` (và/hoặc `route` / `catalog`) trong **đúng domain**; đối chiếu `id` / title / `description`.
2. Có thể đọc `intro.md` topic để nắm phạm vi — **không** coi intro là danh sách đủ note.
3. Đã có khái niệm → bổ sung file cũ, không tạo song song.
4. Note mới / đổi tên / xóa: **không** bắt buộc sửa `intro.md` trừ khi đổi *phạm vi* hoặc *cửa vào* của topic.

---

## Editing

- Giữ tri thức cũ khi có thể; cải thiện hơn là viết lại toàn bộ.
- Không tái cấu trúc lan sang topic / domain ngoài phạm vi task.
- Link note liên quan khi giúp hiểu chủ đề; tránh link vô nghĩa.
  - Dùng Markdown relative (editor/preview nhảy được): `[tabs](tabs.md)` hoặc `[tabs](./tabs.md)`.
  - Không dùng `[[wikilink]]`.

---

## Agent — lưu ý

- **Tìm note bằng tool**, không đoán path hay dựng bảng note trong intro.
- Consumer: `domains` → `intro` (domain/topic) → `route` → `pack`/`show`; sai/thiếu → `feedback` (không sửa note).
- Maintainer: `dup` trước khi tạo; `lint` sau khi sửa; triage `_feedback/` / `_issues/`.
- Đừng tái tạo `index.md` / MOC “cho tiện” — dễ lệch catalog và tốn token.

---

## Optional rules

| Rule | Khi dùng |
|------|----------|
| [`RULE_RESOURCE_CONTROL.md`](RULE_RESOURCE_CONTROL.md) | Bulk edit, hạn mức API |
| [`RULE_GIT.md`](RULE_GIT.md) | Theo dõi sửa note bằng git (không tự commit mặc định) |
| [`TOOLS.md`](TOOLS.md) | Tra / gói note: `knowledge-base domains\|intro\|route\|pack\|show\|feedback` (+ maintainer `lint`/`dup`/`catalog`) |

Skills client (myskills): `kb-consumer` / `kb-maintainer` / `kb-migrate` — cài bằng `npx skills`; không nằm trong `_meta/`. Queue công việc: `task-kanban` (stopgap) hoặc Task-engine (dự kiến) — **không** rule engine.

Lý do thiết kế: [`KB_BUILD_RATIONALE.md`](KB_BUILD_RATIONALE.md).

---

## Checklist (đề xuất)

Không bắt buộc. Dùng khi hữu ích, bỏ qua nếu conflict rule khác:

- Đã `dup` / `route` trong domain / tránh trùng
- Một khái niệm / file; frontmatter đủ; `description` rõ
- Topic có `intro.md` định hướng (không inventory)
- Mâu thuẫn / chưa gắn được → vé `_issues/` (không ghi đè note khi chưa resolve)
