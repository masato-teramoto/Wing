---
name: docs-check
description: Phase 6（全体ドキュメント統合）の品質ゲート。docs/ 3ファイルを検査する
disable-model-invocation: true
---

## 概要

`docs/` 3ファイル（`code-design.md` / `architecture/data-model.md` /
`architecture/system-overview.md`）を対象に、観点 Skill を順に実行し、指摘を蓄積してから
`gate-report` へ渡す。① 形式検証で不備が見つかった場合、② 以降には進まない。

## 入力の範囲

「渡された検査対象」は、ホストが渡した検査対象の明示的な一覧（context の `review_targets`。snapshot の対象と同じ。gate.yaml の `target_review`、省略時はアクションの出力すべて）を指す。一覧のファイルだけを検査対象とし、一覧に無い出力は検査しない。特定のファイル名を書いた行は、そのファイルが検査対象に無ければfailedで返す。以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | 渡された検査対象 | テンプレパス | `Templates/docs/<同名ファイル>` | ID書式 | なし | 追加検証 | なし | 報告単位 | ファイル × セクション |

2. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（design→docs網羅性検証）。

   | 上流 | `specs/*/design.md`・`specs/*/requirements.md`（独立抽出） | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | エンティティ / 属性 / 関連、業務コード・区分値・採番対象、主要フロー、コンポーネントと接続 | 分母の絞り込み | なし | 報告単位 | docs 未反映の design 要素 |

   - 抽出は feature 単位で独立に行い、全 feature の spec を一度に読み込まない。抽出を書き留めてから初めて
     `docs/` を読む。作成時の抽出結果を引き継がない。
   - `data-model.md` が各 design のエンティティ間の関係まで網羅しているか、`code-design.md` がすべての
     design で定義されたコード（業務コード・区分値・採番）を網羅しているかを見る。

3. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（docs補完混入検出）。

   | 上流 | `specs/*/design.md` | 下流 | 渡された検査対象 | 突合方向 | 下流→上流 | 対応の単位 | 手順2と同じ | 分母の絞り込み | なし | 報告単位 | design に存在しない docs の要素 |

4. `.claude/skills/internal-contradiction-detection/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `docs/architecture/system-overview.md` |

5. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（用語命名一貫性検証）。

   | 対象成果物 | 渡された検査対象・`specs/*/design.md` | 検査する事実の種類 | ユビキタス言語（用語・命名） | 検査の型 | 二重定義 |

6. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（データモデル参照整合性検証）。

   | 対象成果物 | `docs/architecture/data-model.md` | 検査する事実の種類 | データモデルの相互参照 | 検査の型 | 参照切れ |

7. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（コンポーネント突合）。

   | 上流 | `specs/*/design.md` | 下流 | `docs/architecture/system-overview.md` | 突合方向 | 双方向 | 対応の単位 | コンポーネント名 | 分母の絞り込み | なし | 報告単位 | コンポーネント |

8. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 根拠 | `specs/*/design.md`・`steering/*.md` |

9. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（steering二重定義検証）。

   | 対象成果物 | 渡された検査対象・`steering/*.md` | 検査する事実の種類 | 業務コード・DB の方針（steering）と実態（docs）の重複・矛盾 | SSoTの所在 | 方針は `steering/`、実態は `docs/` | 検査の型 | 二重定義 | 報告単位 | 重複している記述の対 |

   docs が steering のルールを「準拠」として引用するのは二重定義ではない。あわせて `code-design.md` のコードが
   steering のコード設計ルールに従っているかを、ルール側を正として突き合わせる。

10. `.claude/skills/definition-resolution-completeness/SKILL.md` を Read し、次を指定して実行する。

    | 対象 | 渡された検査対象 | 突合元 | `specs/*/design.md` |

11. `.claude/skills/design-rule-gap-detection/SKILL.md` を Read し、次を指定して実行する。

    | 対象 | `specs/*/design.md` | 既存ルールの所在 | `steering/` の設計ルール（全7ファイル） |

    明文化漏れに加え、既存の steering ルールを design ごとに別解釈している痕跡（同種の要素が feature ごとに
    別の規則で作られている）を Phase 2 への差戻し候補として指摘し、影響 design の洗い出しが必要な旨を添える。

12. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する（コード設計ルール準拠）。

    | 対象 | `docs/code-design.md` | 参照する steering | `steering/` 7ファイル一式 | 検証観点 | コード設計・命名・レイヤ構成のルールへの準拠 |

    steering 自体の妥当性は評価しない。逸脱は「どちらを直すか」を人に問う形で書く。

13. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。

## 禁止

- 対象成果物の本文を書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否・重大度を自分で判断しない
- 参照元の specs/*/design.md を書き換えない
- `docs/` を先に読んでから design を読まない（独立抽出の順序を崩さない）。`tasks.md` を入力にしない
