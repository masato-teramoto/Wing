---
name: definition-resolution-completeness
description: 複数のdesign.mdで異なる形状が示唆されている概念が、docs統合時に単一の形状として確定しているかを検証する
disable-model-invocation: true
---

## 概要

feature 横断で見ると、同じデータ・概念について design.md 間で異なる形状（フィールド構成・
型・命名）が示唆されている場合がある。`docs/` への統合時に、これらが単一の形状として確定・
解消されているか（未解消のまま両論併記や矛盾を残していないか）を検証する。

## 入力

| 項目 | 内容 | 指定例 |
|---|---|---|
| 対象 | 統合結果 | `docs/` 3ファイル |
| 突合元 | 形状の競合を確認する design 一式 | `specs/*/design.md` |

## 手順

1. `突合元` から、複数 feature にまたがって現れる共通の概念・データ（例: `User`、`Order`）を
   洗い出し、各 design.md での形状（フィールド・型）を比較する。
2. 形状に競合（フィールド名・型・必須/任意が食い違う）がある概念を特定する。
3. `対象`（docs/）がその概念について単一の形状として確定しているかを確認する。確定しておらず、
   競合がそのまま残っている、または確定の根拠（どちらを正としたか）が書かれていない場合を
   指摘する。

## この工程で指摘しない事項

- `.claude/skills/finding-rules/SKILL.md` の工程の境界の表・`confirmed_answers`・`learned` に当たる事項
- `TBD（<工程> で確定）` と書いてある値

当たるものは指摘にせず、除外として返す（除外の出典を付ける。書き方は finding-rules）。

## 出力の形

指摘ごとに次を返す。書き方は `.claude/skills/finding-rules/SKILL.md`（検査の最初に読む）に従う。重大度は出さない（L3 が `kind` から決める）。

```
{ location, subject, kind, summary, evidence, suggestion, recommendation, is_rollback_candidate }
```

| フィールド | 内容 |
|---|---|
| `location` | 競合が未解消の docs の箇所（design.md 側の箇所は `evidence`）。`<案件相対パス> § <節見出し> / <ID>` の形。複数箇所なら代表 1 か所＋「ほか n か所」（全件は `evidence`） |
| `subject` | 対象の語（例: `Order`） |
| `kind` | `.claude/skills/finding-rules/SKILL.md` の種類から 1 つ選ぶ。迷ったら上の行。通常 `業務の欠落・矛盾` |
| `summary` | 60 字以内。結論を先に、何が・どこで（例: 「`Order` の形状が design 間で異なり、docs でも確定していない」） |
| `evidence` | 概念名と、各 design.md での形状（フィールド・型・必須/任意）の比較、docs の記述 |
| `suggestion` | 修正案（差分・書き換え文）。業務の新しい事実が要るときは、修正案ではなく「何を決めればよいか」と選べる案 |
| `recommendation` | `修正：理由` / `差戻し：理由` / `対応せず進める：理由` / `質問：理由` のどれか。業務の新しい事実が要るときは `質問：…` |
| `is_rollback_candidate` | 上流designの競合が残る場合は `true`。docsだけで形状を決めず、designへの差戻し候補とする |

## 禁止

- 対象成果物・design.mdを書き換えない（形状を自動で統一しない）
- 合否を出さない
- どちらの形状を正とするかを断定しない。両形状を `suggestion` の選べる案にし、`recommendation` を `質問：…` または `差戻し：…` にする
