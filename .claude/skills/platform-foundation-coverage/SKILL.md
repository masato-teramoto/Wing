---
name: platform-foundation-coverage
description: architecture.mdが求める基盤系Feature（認証基盤・ロギング基盤等）がfeature-list.mdの分割に漏れていないかを検出する
disable-model-invocation: true
---

## 概要

`steering/architecture.md` に記述されたアーキテクチャ上の前提（認証基盤・ロギング基盤・
共通APIゲートウェイ等、複数 feature が共有する基盤要素）が、`.aidd/feature-list.md` の
feature 分割に独立した feature として、または既存 feature の責務として反映されているかを
検証する漏れ検出である。

## 入力

| 項目 | 内容 | 指定例 |
|---|---|---|
| 対象 | feature分割の結果 | `.aidd/feature-list.md` |
| 参照 | 基盤要素の記述元 | `steering/architecture.md` / `steering/*.md` 一式・`.aidd/requirement-list.md` |

## 手順

1. `参照`（architecture.md）から、複数 feature が前提として共有する基盤要素を洗い出す
   （認証・認可基盤、ロギング・監視基盤、メッセージング基盤、共通APIゲートウェイ等）。
2. `対象`（feature-list.md）の各 feature の責務記述を確認し、洗い出した基盤要素がいずれかの
   feature の責務として、または独立した基盤系 feature として反映されているかを確認する。
3. architecture.md に前提として書かれているにもかかわらず、どの feature の責務にも現れていない
   基盤要素を指摘する。
4. `参照` に要求一覧・他の steering が含まれる場合は、それらが必要とする Platform 系の基盤（認証、監査ログ、
   マスタ、バッチ基盤等）も洗い出す。architecture.md が基盤を名指ししていなくても、どの feature の責務にも
   現れていなければ、必要とする要求ID・steering の記述を `evidence` に書いて指摘する。

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
| `location` | 基盤要素が欠落している `.aidd/feature-list.md` の箇所（architecture.md 等の箇所は `evidence`）。`<案件相対パス> § <節見出し> / <ID>` の形。複数箇所なら代表 1 か所＋「ほか n か所」（全件は `evidence`） |
| `subject` | 対象の語（例: `共通認証基盤`） |
| `kind` | `.claude/skills/finding-rules/SKILL.md` の種類から 1 つ選ぶ。迷ったら上の行。通常 `業務の欠落・矛盾` |
| `summary` | 60 字以内。結論を先に、何が・どこで（例: 「architecture.md の共通認証基盤を担う feature が feature-list.md に無い」） |
| `evidence` | 基盤要素を前提とする architecture.md の箇所、必要とする要求ID・steering の記述 |
| `suggestion` | 既存 feature の責務に加えるか、独立した基盤系 feature にするかの案 |
| `recommendation` | `修正：理由` / `差戻し：理由` / `対応せず進める：理由` / `質問：理由` のどれか。業務の新しい事実が要るときは `質問：…` |
| `is_rollback_candidate` | 通常 `false`（同一フェーズ内でのfeature追加で解消できるため） |

## 禁止

- 対象成果物を書き換えない（featureを自動で追加しない）
- 合否を出さない
- 業務の新しい事実が要る値を自分で決めない。`suggestion` に「何を決めればよいか」と選べる案を書き、`recommendation` を `質問：…` にする
