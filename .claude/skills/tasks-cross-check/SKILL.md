---
name: tasks-cross-check
description: 全 feature の検査済み tasks を対象に、feature 間の実装順・依存・網羅を確認して最後の人間承認へ渡す。
disable-model-invocation: true
---

## 概要

ホストが承認済みfeature集合から列挙した全tasksが対象。各featureの現行検査が存在することは前段の規則確認が担う。scopeは全件ならphase、Feature 方式の selection 単位（item 付き）ならphase:<item>で、対象はホストが渡す比較集合の tasks。個別の指摘を再検出したことにして集計せず、今回行う全体検査の指摘を記録する。

## 共通ルール

指摘は `.claude/skills/finding-rules/SKILL.md`（検査役が手順の前に読む）に従って出す。書き方・種類・出さない事項（除外）・重ねない決まり・差分の検査・形式不備の扱いはそこに従い、重大度は出さない。どの手順でも、ほかの手順で指摘済みの箇所・同じ原因は重ねない。

## 手順

1. `.claude/skills/dependency-cycle-detection/SKILL.md` をReadする。feature-listの依存と全tasksの境界・依存記載から、依存元→依存先の方向でfeature間の実装依存を照合する。未知名・逆転・循環・受け手不在を指摘する。同じタスク番号はfeatureごとに別の識別子として扱う。
2. `.claude/skills/traceability/SKILL.md` をReadする。承認済みfeature集合を分母に、全featureのrequirements / designとtasksの対応、feature間の提供契約を満たす先行タスクの有無を照合する。Globに存在した数で分母を縮めない。分母の絞り込みは「なし（承認済みfeature集合の全件）」、報告単位は feature × 未対応の要件・契約として渡す。`docs/` は入力・根拠にしない。
3. `.claude/skills/finding-verification/SKILL.md` を Read し、蓄積した指摘を確かめる。
4. `.claude/skills/gate-report/SKILL.md` をReadする。当該実行のscope（phase または phase:<item>）、run、対象、ハッシュで今回の検査だけを末尾追記する。

## 集約

入力snapshotの識別子をそのまま使い、観点ごとの指摘にgate名を付ける。個別実行の未解消指摘と今回の全体指摘はL3の提示処理が合わせて扱う。変わっていない feature の前回の指摘は L3 が引き継ぐので、出し直さない。検査agentは承認・解消を記録しない。

## 部分集合モード（Feature 方式の selection 単位の横断確認）

context に `scope_features` があるときだけ読む。全件方式（`scope_features` が無い）の手順は変えない。

- 分母は `scope_features`（比較集合 C(p)。選択 feature `selection` と依存先、共通機能なら承認済みの利用側）。inputs の解決済みパスだけを読み、glob しない。
- `excluded_features` は U のうち比較集合に入らない feature。これらの成果物が無いこと・読んでいないことを欠落や割当て漏れとして指摘しない。
- 指摘は比較集合の中の矛盾・重複・契約のずれに限る。比較集合の外を経由する循環や未宣言の衝突は構造上検出できないので、最後の全件確認に委ねる（推測で指摘しない）。
- 記録の scope は snapshot の値（`cross:<selection>`、tasks は `phase:<selection>`）をそのまま書く。
