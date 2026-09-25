---
name: implementation-traceability
description: 承認済み要件・設計・タスクの完了条件をfeatureの実コードへ対応づける。
disable-model-invocation: true
---

## 手順

全タスクのRequirements/Design参照と受入条件を分母に、manifestに列挙された実コードの
該当箇所を読む。未実装、境界値、異常系、仕様と異なる分岐やデータ更新を根拠付きで指摘する。
タスクのチェックや作者の説明をコードの代用にしない。対象外要求の勝手な追加は行わない。
gate=implementation-traceability、location=実ファイルと箇所、finding=根拠と不一致を返す。
観点実施のIDも返し、指摘0件と未実施を区別する。
