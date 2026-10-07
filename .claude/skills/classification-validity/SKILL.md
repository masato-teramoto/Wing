---
name: classification-validity
description: 項目に付与された分類・種別ラベルが、その内容から見て妥当かを検証する
disable-model-invocation: true
---

## 概要

対象成果物の各項目に付与された分類・種別ラベル（要求の分類、feature の種別など）が、
その項目の実際の内容と整合しているかを検証する。ラベルの存在有無は `format-conformance` が
見るが、こちらは**ラベルの値そのものの妥当性**を見る。呼び出し元が対象と分類基準を指定する
ことで、Phase 1（要求の分類）・Phase 3（feature種別）に使い回せる。

## 入力

| 項目 | 内容 | 指定例 |
|---|---|---|
| 対象 | 分類ラベルを検証する成果物 | `.aidd/requirement-list.md` 全行 / `.aidd/feature-list.md` 種別列 |
| 分類基準 | 各ラベルの定義（テンプレート・steeringに準じる） | `機能`/`非機能`/`制約` の定義 |

## 手順

1. `分類基準` を読み、各ラベルが指す内容の定義を把握する。
2. `対象` の各項目について、内容を読み、付与されているラベルが `分類基準` の定義と一致するかを
   確認する。
3. 内容から見て別のラベルが妥当と考えられる場合（例: 性能に関する記述なのに「機能」に
   分類されている）を指摘する。

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
| `location` | 分類が疑わしい項目。`<案件相対パス> § <節見出し> / <ID>` の形。複数箇所なら代表 1 か所＋「ほか n か所」（全件は `evidence`） |
| `subject` | 対象の語（例: `REQ-021`） |
| `kind` | `.claude/skills/finding-rules/SKILL.md` の種類から 1 つ選ぶ。迷ったら上の行。通常 `業務のあいまい・不足` |
| `summary` | 60 字以内。結論を先に、何が・どこで（例: 「`REQ-021` は応答時間の記述だが `機能` に分類されている」） |
| `evidence` | 項目の内容の引用と、`分類基準` の該当する定義 |
| `suggestion` | 妥当なラベル（例: `非機能`）への書き換え |
| `recommendation` | `修正：理由` / `差戻し：理由` / `対応せず進める：理由` / `質問：理由` のどれか。業務の新しい事実が要るときは `質問：…` |
| `is_rollback_candidate` | 通常 `false`（同一フェーズ内でのラベル修正で解消できるため） |

## 禁止

- 対象成果物を書き換えない（ラベルを自動で修正しない）
- 合否を出さない
- 分類基準に明記の無い独自基準で判定しない
