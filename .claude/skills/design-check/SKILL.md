---
name: design-check
description: Phase 5（機能設計作成）の品質ゲート（featureスコープ）。specs/<feature>/design.md を検査する
disable-model-invocation: true
---

## 概要

対象 feature の `specs/<feature>/design.md` を検査する。`--item` で渡された feature 名を
すべての観点 Skill 呼び出しに引き継ぐ。① 形式検証で不備が見つかった場合、② 以降には進まない。

## 入力の範囲

「渡された検査対象」は、ホストが渡した検査対象の明示的な一覧（context の `review_targets`。snapshot の対象と同じ。gate.yaml の `target_review`、省略時はアクションの出力すべて）を指す。一覧のファイルだけを検査対象とし、一覧に無い出力は検査しない。特定のファイル名を書いた行は、そのファイルが検査対象に無ければfailedで返す。以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | 渡された検査対象 | テンプレパス | `Templates/specs/_template/design.md` | ID書式 | 要件ID = 数値のみ | 追加検証 | 必須セクションの存在 | 報告単位 | セクション |

2. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（要件ID双方向突合・機械）。

   | 上流 | `specs/<feature>/requirements.md` | 下流 | 渡された検査対象 | 突合方向 | 双方向 | 対応の単位 | 要件ID | 分母の絞り込み | なし | 報告単位 | 要件ID |

3. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（要件トレーサビリティ検証）。

   | 上流 | `specs/<feature>/requirements.md` | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | 要件が設計で満たされているか | 分母の絞り込み | なし | 報告単位 | 要件ID |

4. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（非機能反映突合）。

   | 上流 | `steering/non-functional.md` | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | 非機能方針 | 分母の絞り込み | なし | 報告単位 | 未反映の方針 |

5. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（可観測性反映突合）。

   | 上流 | `steering/non-functional.md`・`steering/architecture.md` | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | ログ/メトリクス/トレースの三本柱 | 分母の絞り込み | なし | 報告単位 | 未反映の柱 |

6. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 参照する steering | `steering/*.md` 一式 | 検証観点 | 技術選定・アーキテクチャ・security方式・DB / 業務コードの設計ルールへの違反・矛盾・逸脱 | 報告単位 | feature × セクション |

7. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 根拠 | `specs/<feature>/requirements.md`・`steering/*.md` |

8. `.claude/skills/external-integration-contract-explicitness/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象の外部連携記述 |

9. `.claude/skills/dependency-boundary-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 依存先 | `specs/*/design.md`（依存先のみ） |

10. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。

## 禁止

- 対象成果物の本文を書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否・重大度を自分で判断しない
- 依存先 feature の design.md を書き換えない
