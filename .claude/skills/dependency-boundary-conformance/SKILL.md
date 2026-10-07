---
name: dependency-boundary-conformance
description: design.mdが依存先featureの内部設計に直接依存していないか（公開契約経由の依存になっているか）を検証する
disable-model-invocation: true
---

## 概要

`specs/<feature>/design.md` が、依存先 feature の `design.md` の**内部実装詳細**（非公開の
内部関数・内部データ構造等）に直接依存していないかを検証する。feature 間の依存は、公開された
契約（API/Event/Data Contracts）経由でなければならない。

## 入力

| 項目 | 内容 | 指定例 |
|---|---|---|
| 対象 | 検証する design | `specs/<feature>/design.md` |
| 依存先 | 対象が依存すると宣言している feature の design | `specs/*/design.md`（依存先のみ） |

## 手順

1. `対象` から依存先 feature への参照箇所を抽出する。
2. `依存先` の design.md を読み、参照されている要素が公開契約（API/Event/Data Contracts の
   セクションに明記されたもの）か、内部実装の詳細かを判定する。
3. 内部実装の詳細（依存先の非公開関数名・内部専用のデータ構造・実装上の前提）に直接依存して
   いる箇所を指摘する。

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
| `location` | 内部依存が見つかった対象の箇所（依存先の箇所は `evidence`）。`<案件相対パス> § <節見出し> / <ID>` の形。複数箇所なら代表 1 か所＋「ほか n か所」（全件は `evidence`） |
| `subject` | 対象の語（例: `_calcFee()`） |
| `kind` | `.claude/skills/finding-rules/SKILL.md` の種類から 1 つ選ぶ。迷ったら上の行。通常 `業務の欠落・矛盾` |
| `summary` | 60 字以内。結論を先に、何が・どこで（例: 「checkout が payment の内部関数 `_calcFee()` に直接依存している」） |
| `evidence` | 参照している要素と、依存先 design.md でそれが公開契約に無いこと |
| `suggestion` | 公開契約経由への書き換え、または依存先の契約に足す要素の案 |
| `recommendation` | `修正：理由` / `差戻し：理由` / `対応せず進める：理由` / `質問：理由` のどれか。業務の新しい事実が要るときは `質問：…` |
| `is_rollback_candidate` | 依存先の契約自体が不足している場合は `true`（依存先への差戻し候補） |

## 禁止

- 対象成果物・依存先成果物を書き換えない
- 合否を出さない
- 業務の新しい事実が要る値を自分で決めない。`suggestion` に「何を決めればよいか」と選べる案を書き、`recommendation` を `質問：…` にする
