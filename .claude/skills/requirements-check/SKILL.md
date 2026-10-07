---
name: requirements-check
description: Phase 4（機能要件作成）の品質ゲート（featureスコープ）。specs/<feature>/requirements.md を検査する
disable-model-invocation: true
---

## 概要

対象 feature の `specs/<feature>/requirements.md` を検査する。`--item` で渡された feature 名を
すべての観点 Skill 呼び出しに引き継ぐ。① 形式検証で不備があっても ② を省略せず、不備のある節だけを ② から外す。

## 入力の範囲

「渡された検査対象」は、ホストが渡した検査対象の明示的な一覧（context の `review_targets`。snapshot の対象と同じ。gate.yaml の `target_review`、省略時はアクションの出力すべて）を指す。一覧のファイルだけを検査対象とし、一覧に無い出力は検査しない。特定のファイル名を書いた行は、そのファイルが検査対象に無ければfailedで返す。以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 共通ルール

指摘は `.claude/skills/finding-rules/SKILL.md`（検査役が手順の前に読む）に従って出す。書き方・種類・出さない事項（除外）・重ねない決まり・差分の検査・形式不備の扱いはそこに従い、重大度は出さない。どの手順でも、ほかの手順で指摘済みの箇所・同じ原因は重ねない。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | 渡された検査対象 | テンプレパス | `Templates/specs/_template/requirements.md` | ID書式 | 要件ID = 数値のみ（`1`, `1.1`）。当該ファイル内で重複しない | 追加検証 | 各要件に US と AC が存在する・フロントマターの `feature` が `.aidd/feature-list.md` の feature 名と一致する | 報告単位 | 要件ID |

   プレースホルダーは、不要理由が明記された箇所を指摘せず、理由の無いまま残る箇所を指摘する。

2. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（当該feature行の対応要求IDだけを分母とする要求ID突合）。

   | 上流 | `.aidd/feature-list.md`・`.aidd/requirement-list.md` | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | 要求ID | 分母の絞り込み | 当該 feature 行の対応要求IDのみ | 報告単位 | 未反映の要求ID |

   要求の内容が要件で満たされているかまで意味判定する。要求IDに紐づかない要件（上流に根拠のない追記）は
   手順6が出すので、ここでは出さない。

3. `.claude/skills/verifiable-criteria-check/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象の各要件AC |

4. `.claude/skills/ac-coverage-completeness/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象の各要件AC |

5. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（非機能誤配置検出）。

   | 上流 | `steering/non-functional.md`・`steering/security.md` | 下流 | 渡された検査対象 | 突合方向 | 下流→上流 | 対応の単位 | 非機能/制約項目 | 分母の絞り込み | なし | 報告単位 | 誤配置の要件・AC |

6. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 根拠 | `.aidd/feature-list.md`・`.aidd/requirement-list.md`・`steering/*.md` |

7. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（重複要件検出）。

   | 対象成果物 | 渡された検査対象 | 検査する事実の種類 | 要件が定義する振る舞い | SSoTの所在 | 先に記載された要件ID | 検査の型 | 二重定義 | 報告単位 | 重複と判定した要件IDの対 |

   文言ではなく振る舞いの同一性で判定する。加えて、ある要件が他の要件の受け入れ基準の部分集合になっている
   （独立した要件として存在する必要が無い）場合も INVEST の Independent 違反として指摘する。ほかの手順で
   指摘済みの箇所は重ねない。

8. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 参照する steering | `steering/*.md` 一式 | 検証観点 | steering への違反・矛盾 | 報告単位 | 要件ID |

   steering に無い拡張（無断の拡張）は上流に根拠のない追記として手順6が出すので、ここでは出さない。

9. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（Dependencies整合検証）。

   | 対象成果物 | 渡された検査対象・`.aidd/feature-list.md` | 検査する事実の種類 | Dependencies記載 | 検査の型 | 参照切れ |

10. `.claude/skills/finding-verification/SKILL.md` を Read し、蓄積した指摘を確かめる。

11. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。変わっていない節の前回の指摘は L3 が引き継ぐので、出し直さない。

## 禁止

- 対象成果物の本文を書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否を自分で判断しない。重大度は書かない（L3 が種類から決める）
- 他 feature の成果物・上流成果物を書き換えない
