---
name: design-check
description: Phase 5（機能設計作成）の品質ゲート（featureスコープ）。specs/<feature>/design.md を検査する
disable-model-invocation: true
---

## 概要

対象 feature の `specs/<feature>/design.md` を検査する。`--item` で渡された feature 名を
すべての観点 Skill 呼び出しに引き継ぐ。① 形式検証で不備があっても ② を省略せず、不備のある節だけを ② から外す。

## 入力の範囲

「渡された検査対象」は、ホストが渡した検査対象の明示的な一覧（context の `review_targets`。snapshot の対象と同じ。gate.yaml の `target_review`、省略時はアクションの出力すべて）を指す。一覧のファイルだけを検査対象とし、一覧に無い出力は検査しない。特定のファイル名を書いた行は、そのファイルが検査対象に無ければfailedで返す。以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 共通ルール

指摘は `.claude/skills/finding-rules/SKILL.md`（検査役が手順の前に読む）に従って出す。書き方・種類・出さない事項（除外）・重ねない決まり・差分の検査・形式不備の扱いはそこに従い、重大度は出さない。どの手順でも、ほかの手順で指摘済みの箇所・同じ原因は重ねない。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | 渡された検査対象 | テンプレパス | `Templates/specs/_template/design.md` | ID書式 | 要件ID = 数値のみ | 追加検証 | 必須セクションの存在 | 報告単位 | セクション |

2. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（要件ID双方向突合・要件トレーサビリティ検証）。

   | 上流 | `specs/<feature>/requirements.md` | 下流 | 渡された検査対象 | 突合方向 | 双方向 | 対応の単位 | 要件ID | 分母の絞り込み | なし | 報告単位 | 要件ID |

   上流→下流では、要件が設計で満たされているかまで意味判定する（ID 対応あり・内容未充足も指摘する）。
   下流→上流では、design が参照する要件IDの実在だけを見る。上流に根拠のない設計の追記は手順5が出す。

3. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（非機能・可観測性反映突合）。

   | 上流 | `steering/non-functional.md`・`steering/architecture.md` | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | 非機能方針（ログ/メトリクス/トレースの三本柱を含む） | 分母の絞り込み | なし | 報告単位 | 未反映の方針・柱 |

4. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 参照する steering | `steering/*.md` 一式 | 検証観点 | 技術選定・アーキテクチャ・security方式への違反・矛盾 | 報告単位 | feature × セクション |

   DB / 業務コードの設計ルールへの違反は design-cross-check が出すので、ここでは出さない。steering に無い拡張
   （無断の拡張）は手順5が出す。

5. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 根拠 | `specs/<feature>/requirements.md`・`steering/*.md` |

6. `.claude/skills/external-integration-contract-explicitness/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象の外部連携記述 |

7. `.claude/skills/dependency-boundary-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 依存先 | `specs/*/design.md`（依存先のみ） |

8. `.claude/skills/finding-verification/SKILL.md` を Read し、蓄積した指摘を確かめる。

9. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。変わっていない節の前回の指摘は L3 が引き継ぐので、出し直さない。

## 禁止

- 対象成果物の本文を書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否を自分で判断しない。重大度は書かない（L3 が種類から決める）
- 依存先 feature の design.md を書き換えない
