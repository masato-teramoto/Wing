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

## 出力の形

```
{ id, location, finding, is_rollback_candidate }
```

| フィールド | 内容 |
|---|---|
| `id` | この Skill 内で一意な通し番号 |
| `location` | 競合が未解消の概念名と、該当する design.md / docs の箇所 |
| `finding` | 未解消の事実（例: 「`Order` の形状が `checkout/design.md` と `billing/design.md` で異なり、`docs/architecture/data-model.md` でも確定していない」） |
| `is_rollback_candidate` | 上流designの競合が残る場合は `true`。docsだけで形状を決めず、designへの差戻し候補とする |

## 禁止

- 対象成果物・design.mdを書き換えない（形状を自動で統一しない）
- 合否を出さない
- どちらの形状を正とすべきかを決めない（未解消である事実の指摘に留める）
