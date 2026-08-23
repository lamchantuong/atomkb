# Knowledge corpus

Cây note atomic cho Knowledge Engine. Rule cho agent: [AGENTS.md](AGENTS.md) (bản đầy đủ ship từ engine `RULE_KB_BUILD`).

## Setup

1. Cài CLI từ repo engine: `pip install -e .` → lệnh `knowledge-base`.
2. Trỏ root vào repo này: `knowledge-base --root . domains`, hoặc set `KB_ROOT` / `KNOWLEDGE_BASE_ROOT`.
3. Cursor (corpus): `npx skills add <myskills-path> --skill kb-maintainer`. App kéo KB: `--skill kb-consumer -g`.

Sau khi engine cập nhật rule: `knowledge-base --root . init --force` (và `--readme --force` nếu dùng README).
