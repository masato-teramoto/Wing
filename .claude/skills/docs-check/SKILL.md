---
name: docs-check
description: Phase 6（全体ドキュメント統合）の品質ゲート。docs/ 3ファイルを検査する
disable-model-invocation: true
---

## 概要

`docs/` 3ファイル（`code-design.md` / `architecture/data-model.md` /
`architecture/system-overview.md`）を対象に、観点 Skill を順に実行し、指摘を蓄積してから
`gate-report` へ渡す。① 形式検証で不備があっても ② を省略せず、不備のある節だけを ② から外す。

## 入力の範囲

「渡された検査対象」は、ホストが渡した検査対象の明示的な一覧（context の `review_targets`。snapshot の対象と同じ。gate.yaml の `target_review`、省略時はアクションの出力すべて）を指す。一覧のファイルだけを検査対象とし、一覧に無い出力は検査しない。特定のファイル名を書いた行は、そのファイルが検査対象に無ければfailedで返す。以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 共通ルール

指摘は `.claude/skills/finding-rules/SKILL.md`（検査役が手順の前に読む）に従って出す。書き方・種類・出さない事項（除外）・重ねない決まり・差分の検査・形式不備の扱いはそこに従い、重大度は出さない。どの手順でも、ほかの手順で指摘済みの箇所・同じ原因は重ねない。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | 渡された検査対象 | テンプレパス | `Templates/docs/<同名ファイル>` | ID書式 | なし | 追加検証 | なし | 報告単位 | ファイル × セクション |

2. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（design→docs網羅性検証）。

   | 上流 | `specs/*/design.md`・`specs/*/requirements.md`（独立抽出） | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | エンティティ / 属性 / 関連、業務コード・区分値・採番対象、主要フロー、コンポーネントと接続 | 分母の絞り込み | なし | 報告単位 | docs 未反映の design 要素 |

   - 抽出は feature 単位で独立に行い、全 feature の spec を一度に読み込まない。抽出を書き留めてから初めて
     `docs/` を読む。作成時の抽出結果を引き継がない。
   - `data-model.md` が各 design のエンティティ間の関係まで網羅しているか、`code-design.md` がすべての
     design で定義されたコード（業務コード・区分値・採番）を網羅しているかを見る。
   - コンポーネントは、各 design のコンポーネントが `system-overview.md` に名前で現れるかまで見る。
   - design に無い docs の要素（補完混入）は上流に根拠のない追記として手順6が出すので、ここでは出さない。

3. `.claude/skills/internal-contradiction-detection/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `docs/architecture/system-overview.md` |

4. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（用語命名一貫性検証）。

   | 対象成果物 | 渡された検査対象・`specs/*/design.md` | 検査する事実の種類 | ユビキタス言語（用語・命名） | 検査の型 | 二重定義 |

5. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（データモデル参照整合性検証）。

   | 対象成果物 | `docs/architecture/data-model.md` | 検査する事実の種類 | データモデルの相互参照 | 検査の型 | 参照切れ |

6. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 根拠 | `specs/*/design.md`・`steering/*.md` |

   design に存在しない docs の要素（エンティティ・コード・コンポーネント等の補完混入）もここで出す。

7. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（steering二重定義検証）。

   | 対象成果物 | 渡された検査対象・`steering/*.md` | 検査する事実の種類 | 業務コード・DB の方針（steering）と実態（docs）の重複・矛盾 | SSoTの所在 | 方針は `steering/`、実態は `docs/` | 検査の型 | 二重定義 | 報告単位 | 重複している記述の対 |

   docs が steering のルールを「準拠」として引用するのは二重定義ではない。`code-design.md` のコードが
   steering のコード設計ルールに従っているかは手順10が出す。

8. `.claude/skills/definition-resolution-completeness/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 突合元 | `specs/*/design.md` |

9. `.claude/skills/design-rule-gap-detection/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `specs/*/design.md` | 既存ルールの所在 | `steering/` の設計ルール（全7ファイル） |

   明文化漏れに加え、既存の steering ルールを design ごとに別解釈している痕跡（同種の要素が feature ごとに
   別の規則で作られている）を Phase 2 への差戻し候補として指摘し、影響 design の洗い出しが必要な旨を evidence に書く。

10. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する（コード設計ルール準拠）。

    | 対象 | `docs/code-design.md` | 参照する steering | `steering/` 7ファイル一式 | 検証観点 | コード設計・命名・レイヤ構成のルールへの準拠 |

    steering 自体の妥当性は評価しない。違反・矛盾は「どちらを直すか」を人に問う形（推奨は `質問：`）で書く。

11. `.claude/skills/finding-verification/SKILL.md` を Read し、蓄積した指摘を確かめる。

12. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。変わっていない節の前回の指摘は L3 が引き継ぐので、出し直さない。

## 禁止

- 対象成果物の本文を書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否を自分で判断しない。重大度は書かない（L3 が種類から決める）
- 参照元の specs/*/design.md を書き換えない
- `docs/` を先に読んでから design を読まない（独立抽出の順序を崩さない）。`tasks.md` を入力にしない
