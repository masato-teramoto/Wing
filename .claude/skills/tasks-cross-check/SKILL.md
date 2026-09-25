---
name: tasks-cross-check
description: 全 feature の検査済み tasks を対象に、feature 間の実装順・依存・網羅を確認して最後の人間承認へ渡す。
disable-model-invocation: true
---

## 概要

ホストが承認済みfeature集合から列挙した全tasksが対象。各featureの現行検査が存在することは前段の規則確認が担う。scopeはphase。個別の指摘を再検出したことにして集計せず、今回行う全体検査の指摘を記録する。

## 手順

1. `.claude/skills/dependency-cycle-detection/SKILL.md` をReadする。feature-listの依存と全tasksの境界・依存記載から、依存元→依存先の方向でfeature間の実装依存を照合する。未知名・逆転・循環・受け手不在を指摘する。同じタスク番号はfeatureごとに別の識別子として扱う。
2. `.claude/skills/traceability/SKILL.md` をReadする。承認済みfeature集合を分母に、全featureのrequirements / designとtasksの対応、feature間の提供契約を満たす先行タスクの有無を照合する。Globに存在した数で分母を縮めない。分母の絞り込みは「なし（承認済みfeature集合の全件）」、報告単位は feature × 未対応の要件・契約として渡す。`docs/` は入力・根拠にしない。
3. `.claude/skills/gate-report/SKILL.md` をReadする。当該実行のscope=phase、run、対象、ハッシュで今回の全体検査だけを末尾追記する。

## 集約

入力snapshotの識別子をそのまま使い、観点ごとの指摘にgate名を付ける。個別実行の未解消指摘と今回の全体指摘はL3の提示処理が合わせて扱う。検査agentは承認・解消を記録しない。
