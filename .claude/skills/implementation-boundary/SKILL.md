---
name: implementation-boundary
description: 実コードの変更範囲・責務・公開契約・依存と承認済み設計の整合を確認する。
disable-model-invocation: true
---

## 手順

タスクのBoundary/Dependsと承認済み設計・steeringを読み、実際のimport、呼出し、API、
スキーマ、エラー処理、認可・入力検証、先行featureの公開契約を照合する。
ファイルパスが許可範囲内であることだけで責務整合を判断しない。
不一致はgate=implementation-boundaryとして実コードの箇所と設計根拠を返す。
上流仕様の修正が必要なら差戻し候補を提案するが、宛先や修正内容を確定しない。
