---
name: tasks-check
description: Phase 7（実装計画作成）の品質ゲート（featureスコープ）。specs/<feature>/tasks.md を検査する
disable-model-invocation: true
---

## 概要

対象 feature の `specs/<feature>/tasks.md` を検査する。`--item` で渡された feature 名を
すべての観点 Skill 呼び出しに引き継ぐ。`tasks-authoring` の `hookPoint: end` に差さり、
feature ごとに実行される（旧版は `tasks-gate-run` での一括実行だったが、他フェーズと揃え
前倒しした。実装ハンドオフ §9-1）。① 形式検証で不備があっても ② を省略せず、不備のある節だけを ② から外す。
依存循環・タスク番号順と依存の整合は `type: script` のゲート（`dependency-cycle-check` /
`sequence-consistency-check`。`gate.yaml` を見る）が決定的に検証し、その指摘は check-runner
の手順0（`.claude/agents/check-runner.md`）で自動的に合流する。

## 入力の範囲

「渡された検査対象」は、ホストが渡した検査対象の明示的な一覧（context の `review_targets`。snapshot の対象と同じ。gate.yaml の `target_review`、省略時はアクションの出力すべて）を指す。一覧のファイルだけを検査対象とし、一覧に無い出力は検査しない。特定のファイル名を書いた行は、そのファイルが検査対象に無ければfailedで返す。以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。
上流一覧に `docs/` が含まれていても、検査の入力・根拠にしない（tasks の根拠は requirements / design / steering）。

## 共通ルール

指摘は `.claude/skills/finding-rules/SKILL.md`（検査役が手順の前に読む）に従って出す。書き方・種類・出さない事項（除外）・重ねない決まり・差分の検査・形式不備の扱いはそこに従い、重大度は出さない。どの手順でも、ほかの手順で指摘済みの箇所・同じ原因は重ねない。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | 渡された検査対象 | テンプレパス | `Templates/specs/_template/tasks.md` | ID書式 | タスク通し番号・`_Depends:` = 整数、`_Requirements:` = 受け入れ基準ID（`1.2` 形式）、直接対応するACがないタスクは `—` | 追加検証 | 要件ID紐づけ・完了条件記述の存在 | 報告単位 | タスク番号 |

2. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 参照する steering | `steering/*.md` 一式（7ファイル全文） | 検証観点 | `tech.md` の検証前提（コマンド・テスト方針）との矛盾、およびその他 steering への違反・矛盾 | 報告単位 | タスク番号 |

   steering に無い拡張（無断の拡張）は上流に根拠のない追記として手順7・8が出すので、ここでは出さない。

3. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（design網羅性検証）。

   | 上流 | `specs/<feature>/design.md` | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | 設計要素のタスク化。通常の機能実装は、対応テスト作成・RED・実装・GREEN・VERIFYを同一タスクが担うことまで含む | 分母の絞り込み | なし | 報告単位 | 未タスク化の設計要素、またはタスク化済みでも同一タスク内でTDD責務が完結しない設計要素（対象・関連タスク番号と不足する責務を示す） |

   設計要素を担う通常の機能実装タスクは、本文・完了条件・Dependsを合わせて読み、対応するテスト作成、
   意図した失敗の確認、実装、成功確認と回帰検証までが同一タスクの責務に含まれるかを`traceability`で突合する。
   Phase 8は同一task_id・execution_idのRED→GREEN→VERIFYを要求する。実装と対応テストを別タスクへ割り当てている場合は、
   順序を逆転してもDependsで接続しても不足は解消しない。対象タスク番号・関連番号・該当本文と、
   どの責務が別タスクへ漏れて当該タスク内で完結しないかを、既存の`traceability`指摘として報告する。
   特定の語句や新しいTDD欄の有無では判定しない。各タスク内で実装・テスト・検証が完結する構成は指摘しない。
   非コード準備や既存コマンドによる横断確認は、実際の責務と完了条件が独立している限り分離を不備としない。
   新規テストコードの作成は名称だけで非コードに分類しない。現行条件で成立しない既存実装へのテスト追加等は、
   適用条件の未解決点を報告し、免除や正常な実装の破壊を解決案にしない。実行済み証跡の有無はPhase 7では要求しない。

4. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（AC→完了条件突合）。

   | 上流 | `specs/<feature>/requirements.md` のAC | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | 完了条件によるACのカバー | 分母の絞り込み | なし | 報告単位 | 完了条件でカバーされない AC |

5. `.claude/skills/verifiable-criteria-check/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象の各タスク完了条件 |

6. `.claude/skills/schema-migration-task-coverage/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `specs/<feature>/design.md` のデータモデル | 突合先 | 渡された検査対象 |

7. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する（根拠なき数値記述検出）。

   | 対象 | 渡された検査対象 | 根拠 | `specs/<feature>/requirements.md` |

8. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する（design根拠なき設計判断検出）。

   | 対象 | 渡された検査対象 | 根拠 | `specs/<feature>/design.md` のみ | 重点 | 下記4種 |

   `design.md` に無い API のエンドポイント・リクエスト / レスポンス形状／エンティティ・カラム・区分値・業務コード／
   ライブラリ・フレームワーク・技術選定／コンポーネント・ファイル配置・責務境界。tasks にしか存在しない設計判断は
   docs のゲートでは検出できないため、本手順で拾う。

9. `.claude/skills/finding-verification/SKILL.md` を Read し、蓄積した指摘を確かめる。

10. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘（check-runner の手順0で
    合流させた `dependency-cycle-check` / `sequence-consistency-check` の分を含む）を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。変わっていない節の前回の指摘は L3 が引き継ぐので、出し直さない。
design / requirements を差戻し候補とする指摘には、`docs/` も再集約の対象になる旨を evidence に書く（下流の無効化自体は L3 が行う）。

## 禁止

- 対象成果物の本文を書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否を自分で判断しない。重大度は書かない（L3 が種類から決める）
- 他 feature の成果物・上流成果物を書き換えない
