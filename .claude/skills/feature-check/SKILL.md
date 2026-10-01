---
name: feature-check
description: Phase 3（機能分割・優先度決定）の品質ゲート。.aidd/feature-list.md を検査する
disable-model-invocation: true
---

## 概要

`.aidd/feature-list.md` を対象に、観点 Skill を順に実行し、指摘を蓄積してから `gate-report` へ
渡す。① 形式検証で不備が見つかった場合、② 以降には進まない。依存循環・優先度と依存の整合は
`type: script` のゲート（`dependency-cycle-check` / `sequence-consistency-check`。
`gate.yaml` を見る）が決定的に検証し、その指摘は check-runner の手順0
（`.claude/agents/check-runner.md`）で自動的に合流する。

## 入力の範囲

「渡された検査対象」は、ホストが渡した検査対象の明示的な一覧（context の `review_targets`。snapshot の対象と同じ。gate.yaml の `target_review`、省略時はアクションの出力すべて）を指す。一覧のファイルだけを検査対象とし、一覧に無い出力は検査しない。特定のファイル名を書いた行は、そのファイルが検査対象に無ければfailedで返す。以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | 渡された検査対象 | テンプレパス | `Templates/Flow/feature-list.md` | ID書式 | feature 名（`references/paths.md` §5） | 追加検証 | 固定7列・正整数優先度・表順・依存先の先行実在・名前の一意性。形式パーサの指摘を必ず含める | 報告単位 | feature |

2. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（分類=機能の要求IDだけを分母とする双方向突合）。

   | 上流 | `.aidd/requirement-list.md` | 下流 | 渡された検査対象 | 突合方向 | 双方向 | 対応の単位 | 要求ID | 分母の絞り込み | 分類=機能の行のみ（非機能/制約を含めない） | 報告単位 | 未割当・参照先不在の要求ID |

3. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（feature網羅性検証）。

   | 上流 | `.aidd/requirement-list.md`・`steering/*.md`（独立抽出） | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | 機能領域 | 分母の絞り込み | なし | 報告単位 | feature に現れない機能領域 |

4. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（多重割当検出）。

   | 対象成果物 | 渡された検査対象 | 検査する事実の種類 | 要求IDの割当 | 検査の型 | 多重割当 |

5. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（責務重複検出）。

   | 対象成果物 | 渡された検査対象 | 検査する事実の種類 | feature の責務記述 | 検査の型 | 二重定義 |

6. `.claude/skills/classification-validity/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象の種別列 | 分類基準 | `Templates/Flow/feature-list.md` の種別定義 |

7. `.claude/skills/platform-foundation-coverage/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 参照 | `steering/architecture.md`・`steering/*.md` 一式・`.aidd/requirement-list.md` |

   認証・監査ログ・マスタ・バッチ基盤等の Platform feature の漏れを、architecture.md が基盤を名指ししていない
   場合も要求一覧・steering から導いて見る。

8. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する（分割のsteering整合）。

   | 対象 | 渡された検査対象 | 参照する steering | `steering/*.md` 一式 | 検証観点 | 分割方針（対象範囲・やらないこと・アーキテクチャ境界）の逸脱。`product.md` で対象外の範囲が feature 化されていないか | 報告単位 | feature |

9. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 根拠 | `.aidd/requirement-list.md`・`steering/*.md` | 重点 | 優先度（表順） |

   優先度が、依存の必須先行・`steering/product.md` の主要ユースケースと提供価値・要求一覧から導けるかを見て、
   導けない順序を「根拠が示せない」として指摘する。優先度の妥当性そのものは評価しない（異議は③が出す）。

10. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘（check-runner の手順0で
    合流させた `dependency-cycle-check` / `sequence-consistency-check` の分を含む）を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。

## 禁止

- 対象成果物の本文を書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否・重大度を自分で判断しない
