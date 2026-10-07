---
name: slo-quantification
description: 非機能方針に反映された目標値が定量化されているか（数値・単位・測定条件を伴うか）を検証する
disable-model-invocation: true
---

## 概要

`steering/non-functional.md` に反映された SLO（サービスレベル目標）等の記述が、定性的な
表現（「速い」「高い可用性」等）のままでなく、数値・単位・測定条件を伴って定量化されているかを
検証する。

## 入力

| 項目 | 内容 | 指定例 |
|---|---|---|
| 対象 | 検証する記述 | `steering/non-functional.md` の反映済み記述 |

## 手順

1. `対象` から性能・可用性・信頼性等に関する目標値の記述を抽出する。
2. 各記述が「数値 + 単位 + 測定条件（測定方法・パーセンタイル・期間等）」の3要素を伴っているかを
   確認する。
3. 定性語（「高速」「安定」「十分な」等）のみで数値化されていない記述を指摘する。

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
| `location` | 定量化されていない記述の箇所。`<案件相対パス> § <節見出し> / <ID>` の形。複数箇所なら代表 1 か所＋「ほか n か所」（全件は `evidence`） |
| `subject` | 対象の語（例: `可用性目標`） |
| `kind` | `.claude/skills/finding-rules/SKILL.md` の種類から 1 つ選ぶ。迷ったら上の行。通常 `業務のあいまい・不足` |
| `summary` | 60 字以内。結論を先に、何が・どこで（例: 「可用性目標が『高い可用性』のみで数値目標がない」） |
| `evidence` | 該当の記述の引用と、欠けている要素（数値・単位・測定条件） |
| `suggestion` | 数値・単位・測定条件を伴う書き換えの形。数値が業務の新しい事実なら「何を決めればよいか」と選べる案 |
| `recommendation` | `修正：理由` / `差戻し：理由` / `対応せず進める：理由` / `質問：理由` のどれか。業務の新しい事実が要るときは `質問：…` |
| `is_rollback_candidate` | 通常 `false`（同一フェーズ内での数値化で解消できるため） |

## 禁止

- 対象成果物を書き換えない（数値を自動で補完しない）
- 合否を出さない
- 業務の新しい事実が要る値を自分で決めない。`suggestion` に「何を決めればよいか」と選べる案を書き、`recommendation` を `質問：…` にする
