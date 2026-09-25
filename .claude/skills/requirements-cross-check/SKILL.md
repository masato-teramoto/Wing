---
name: requirements-cross-check
description: Phase 4 の横断品質ゲート。全 feature の requirements.md をまたいだ整合を検査する
disable-model-invocation: true
---

## 概要

`requirements-cross-gate`（全 feature の requirements.md が揃った後に1回だけ呼ばれる）の
event 本体として実行される。`specs/*/requirements.md` 一式を対象に、feature をまたいだ
要求IDの全件突合と相互整合を検査する。横断スコープは承認対象の文書を持たないため、`status` を
遷移させない（`references/status-protocol.md` §6）。

## 入力の範囲

以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 手順

1. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（feature-listで対象featureに割り当てた機能要求IDの全件突合。非機能・制約を分母に含めない）。

   | 上流 | `.aidd/requirement-list.md` | 下流 | `specs/*/requirements.md` 一式 | 突合方向 | 双方向 | 対応の単位 | 要求ID | 分母の絞り込み | feature-list で割り当てた分類=機能の要求IDのみ | 報告単位 | どの requirements.md にも反映されていない要求ID |

2. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（受け手不在検証）。

   | 対象成果物 | `specs/*/requirements.md` 一式 | 検査する事実の種類 | feature間の依存・連携前提（Dependencies / Adjacent の期待） | SSoTの所在 | `.aidd/feature-list.md` の依存列 | 検査の型 | 受け手不在 | 報告単位 | 受け手のいない期待 |

3. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。

## 禁止

- 対象の requirements.md をいずれも書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否・重大度を自分で判断しない
- `status` を遷移させない（横断スコープは承認対象の文書を持たない）
