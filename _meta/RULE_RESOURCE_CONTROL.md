# RULE — Resource control

Rule độc lập. Chỉ áp dụng khi bulk edit, pipeline migrate lớn, hoặc đang chạm hạn mức API/RPM.

Không gắn vào `AGENTS.md` cốt lõi — sửa vài note không cần sleep hay tách queue.

---

## Rules

1. **Không bulk lan rộng một lượt:** Nhiều topic / hàng chục file → tách thành lượt nhỏ (một topic / phiên). Lock queue nếu cần: skill `task-kanban` (myskills, stopgap) — không phải rule engine.
2. **Throttling:** Gọi LLM/API liên tiếp trong cùng phiên nặng → nghỉ ngắn giữa các lần (theo hạn mức provider). Không gắn một vendor cụ thể.
