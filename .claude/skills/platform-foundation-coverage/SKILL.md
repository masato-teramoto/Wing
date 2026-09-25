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
   現れていなければ、必要とする要求ID・steering の記述を添えて指摘する。

## 出力の形

```
{ id, location, finding, is_rollback_candidate }
```

| フィールド | 内容 |
|---|---|
| `id` | この Skill 内で一意な通し番号 |
| `location` | architecture.md中の該当箇所と、feature-list.md側で欠落している旨 |
| `finding` | 漏れの事実（例: 「`architecture.md` が前提とする『共通認証基盤』を担うfeatureが `feature-list.md` に無い」） |
| `is_rollback_candidate` | 通常 `false`（同一フェーズ内でのfeature追加で解消できるため） |

## 禁止

- 対象成果物を書き換えない（featureを自動で追加しない）
- 合否を出さない
- 基盤系featureの担当割り当てまでは提案しない（漏れの事実の指摘に留める）
