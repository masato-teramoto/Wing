---
name: tasks-check
description: Phase 7（実装計画作成）の品質ゲート（featureスコープ）。specs/<feature>/tasks.md を検査する
disable-model-invocation: true
---

## 概要

対象 feature の `specs/<feature>/tasks.md` を検査する。`--item` で渡された feature 名を
すべての観点 Skill 呼び出しに引き継ぐ。`tasks-authoring` の `hookPoint: end` に差さり、
feature ごとに実行される（旧版は `tasks-gate-run` での一括実行だったが、他フェーズと揃え
前倒しした。実装ハンドオフ §9-1）。① 形式検証で不備が見つかった場合、② 以降には進まない。
依存循環・タスク番号順と依存の整合は `type: script` のゲート（`dependency-cycle-check` /
`sequence-consistency-check`。`gates.yaml` を見る）が決定的に検証し、その指摘は check-runner
の手順0（`.claude/agents/check-runner.md`）で自動的に合流する。

## 入力の範囲

以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。
上流一覧に `docs/` が含まれていても、検査の入力・根拠にしない（tasks の根拠は requirements / design / steering）。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | `specs/<feature>/tasks.md` | テンプレパス | `Templates/specs/_template/tasks.md` | ID書式 | タスク通し番号・`_Depends:` = 整数、`_Requirements:` = 受け入れ基準ID（`1.2` 形式） | 追加検証 | 要件ID紐づけ・完了条件記述の存在 | 報告単位 | タスク番号 |

2. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `specs/<feature>/tasks.md` | 参照する steering | `steering/*.md` 一式（7ファイル全文） | 検証観点 | `tech.md` の検証前提（コマンド・テスト方針）との矛盾、およびその他 steering への違反・矛盾・逸脱 | 報告単位 | タスク番号 |

3. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（design網羅性検証）。

   | 上流 | `specs/<feature>/design.md` | 下流 | `specs/<feature>/tasks.md` | 突合方向 | 上流→下流 | 対応の単位 | 設計要素のタスク化 | 分母の絞り込み | なし | 報告単位 | タスク化されていない設計要素 |

4. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（AC→完了条件突合）。

   | 上流 | `specs/<feature>/requirements.md` のAC | 下流 | `specs/<feature>/tasks.md` | 突合方向 | 上流→下流 | 対応の単位 | 完了条件によるACのカバー | 分母の絞り込み | なし | 報告単位 | 完了条件でカバーされない AC |

5. `.claude/skills/verifiable-criteria-check/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `specs/<feature>/tasks.md` の各タスク完了条件 |

6. `.claude/skills/schema-migration-task-coverage/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `specs/<feature>/design.md` のデータモデル | 突合先 | `specs/<feature>/tasks.md` |

7. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する（根拠なき数値記述検出）。

   | 対象 | `specs/<feature>/tasks.md` | 根拠 | `specs/<feature>/requirements.md` |

8. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する（design根拠なき設計判断検出）。

   | 対象 | `specs/<feature>/tasks.md` | 根拠 | `specs/<feature>/design.md` のみ | 重点 | 下記4種 |

   `design.md` に無い API のエンドポイント・リクエスト / レスポンス形状／エンティティ・カラム・区分値・業務コード／
   ライブラリ・フレームワーク・技術選定／コンポーネント・ファイル配置・責務境界。tasks にしか存在しない設計判断は
   docs のゲートでは検出できないため、本手順で拾う。

9. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘（check-runner の手順0で
   合流させた `dependency-cycle-check` / `sequence-consistency-check` の分を含む）を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。
design / requirements を差戻し候補とする指摘には、`docs/` も再集約の対象になる旨を添える（下流の無効化自体は L3 が行う）。

## 禁止

- 対象成果物の本文を書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否・重大度を自分で判断しない
- 他 feature の成果物・上流成果物を書き換えない
