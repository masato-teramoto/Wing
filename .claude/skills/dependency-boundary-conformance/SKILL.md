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

## 出力の形

```
{ id, location, finding, is_rollback_candidate }
```

| フィールド | 内容 |
|---|---|
| `id` | この Skill 内で一意な通し番号 |
| `location` | 内部依存が見つかった対象・依存先双方の箇所 |
| `finding` | 越境依存の事実（例: 「`checkout/design.md` が `payment` の内部関数 `_calcFee()` に直接依存している」） |
| `is_rollback_candidate` | 依存先の契約自体が不足している場合は `true`（依存先への差戻し候補） |

## 禁止

- 対象成果物・依存先成果物を書き換えない
- 合否を出さない
- 契約として何を追加すべきかまでは提案しない（越境依存の事実の指摘に留める）
