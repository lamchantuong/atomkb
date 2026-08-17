# RULE — Git theo dõi sửa đổi

Rule độc lập. Áp dụng khi làm việc trên **repo KB** (corpus), không phải repo engine.

Không gắn cứng vào `AGENTS.md` cốt lõi — không bắt agent tự commit mọi lần sửa note.

---

## Nguyên tắc

1. **Git là nhật ký đổi note.** Ưu tiên `git log` / `git diff` / history của file. Không invent changelog song song trong từng note (trừ khi cần ngữ cảnh nghiệp vụ ngắn trong body).
2. **Sửa trên working tree bình thường.** Rename/move topic hoặc note: dùng `git mv` khi giúp giữ history sạch.
3. **Commit khi được yêu cầu** (user / orchestrator), hoặc theo quy ước repo — không tự commit / push mặc định.
4. **Không** `push --force` nhánh chính, không sửa `git config`, không bỏ qua hook trừ khi user yêu cầu rõ.
5. **Không** gắn corpus vào engine bằng submodule / nested `.git` trong cây engine.

---

## Gợi ý khi commit (nếu được yêu cầu)

- Message ngắn, tập trung *vì sao* (thêm topic, sửa sai, migrate SPEC…).
- Chỉ stage file KB / task liên quan; không commit secret (`.env`, credentials…).
