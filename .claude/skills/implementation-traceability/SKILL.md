---
name: implementation-traceability
description: 承認済み要件・設計・タスクの完了条件をfeatureの実コードへ対応づける。
disable-model-invocation: true
---

## 手順

profileが`implementation-task-review-v1`の場合は、task-implement-checkの対象・返却契約を使う。
当該タスクのRequirements/Design参照と完了条件を分母にする。未着手の後続タスクを未実装として指摘しない。
以下のfeature向け手順のうち全タスク・最終レポートを要求する部分は適用せず、実コードで判断する観点は共用する。


全タスクのRequirements/Design参照と受入条件を分母に、manifestに列挙された実コードの
該当箇所を読む。未実装、境界値、異常系、仕様と異なる分岐やデータ更新を根拠付きで指摘する。
タスクのチェックや作者の説明をコードの代用にしない。対象外要求の勝手な追加は行わない。
gate=implementation-traceability、location=実ファイルと箇所、finding=根拠と不一致を返す。
観点実施のIDも返し、指摘0件と未実施を区別する。
