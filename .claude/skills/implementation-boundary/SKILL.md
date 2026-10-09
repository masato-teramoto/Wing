---
name: implementation-boundary
description: 実コードの変更範囲・責務・公開契約・依存と承認済み設計の整合を確認する。
disable-model-invocation: true
---

## 手順

profileが`implementation-task-review-v1`・`implementation-task-reverify-v1`の場合は、task-implement-checkの対象・返却契約を使う。
当該タスクの変更と宣言された関連入力を読む。影響先が不足する場合はパスと理由を未確認として返す。
以下のfeature向け手順のうち全タスク・最終レポートを要求する部分は適用せず、実コードで判断する観点は共用する。


タスクのBoundary/Dependsと承認済み設計・steeringを読み、実際のimport、呼出し、API、
スキーマ、エラー処理、認可・入力検証、先行featureの公開契約を照合する。
ファイルパスが許可範囲内であることだけで責務整合を判断しない。
不一致はgate=implementation-boundaryとして返す。指摘ごとに location（実ファイルと箇所）・subject・kind・summary（60 字以内）・evidence（実コードの箇所と設計根拠）・suggestion・recommendation・is_rollback_candidate を返す。書き方と kind は `.claude/skills/finding-rules/SKILL.md` に従い、重大度は出さない。
上流仕様の修正が必要なら差戻し候補を提案するが、宛先や修正内容を確定しない。

## この工程で指摘しない事項

- `.claude/skills/finding-rules/SKILL.md` の工程の境界の表・`confirmed_answers`・`learned` に当たる事項
- `TBD（<工程> で確定）` と書いてある値

当たるものは指摘にせず、除外として返す（除外の出典を付ける。書き方は finding-rules）。
