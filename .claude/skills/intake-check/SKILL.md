---
name: intake-check
description: Phase 1（要求受入）の品質ゲート。.aidd/requirement-list.md を検査する
disable-model-invocation: true
---

## 概要

`.aidd/requirement-list.md` を対象に、観点 Skill を順に実行し、指摘を蓄積してから
`gate-report` へ渡す。対象は成果物単位（Phase 1 はドキュメント1件のため feature 分割は無い）。
① 形式検証で不備が見つかった場合、② 以降には進まない（`references/status-protocol.md` §6）。
要求ID書式・欠番の再利用禁止は `type: script` のゲート（`id-format-check` /
`revision-diff-check`。`gate.yaml` を見る）が決定的に検証し、その指摘は check-runner の
手順0（`.claude/agents/check-runner.md`）で自動的に合流する。

## 入力の範囲

「渡された検査対象」は、ホストが渡した検査対象の明示的な一覧（context の `review_targets`。snapshot の対象と同じ。gate.yaml の `target_review`、省略時はアクションの出力すべて）を指す。一覧のファイルだけを検査対象とし、一覧に無い出力は検査しない。特定のファイル名を書いた行は、そのファイルが検査対象に無ければfailedで返す。以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | 渡された検査対象 | テンプレパス | `Templates/Flow/requirement-list.md` | ID書式 | 要求ID = `REQ-\d{3,}` | 追加検証 | 下記 | 報告単位 | 要求ID |

   追加検証: 欠番の再利用禁止 / 全行で要求ID・要求文・出典種別・出典アンカー・分類の5欄が空でない /
   出典種別が `RFP` か `壁打ち` のいずれか / 出典アンカーが出典種別と整合する（`RFP` 種別は `.aidd/rfp/**` 内の
   実在する位置を指す、`壁打ち` 種別は `壁打ち` と記載）。RFP 自体には形式検証を適用しない。

2. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（取り漏らし検出）。

   | 上流 | `.aidd/rfp/**`（独立抽出。要求一覧を先に読まない） | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | 要求の意味単位（章・見出しを単位にしない） | 分母の絞り込み | 下流は出典種別=RFPの行のみ | 報告単位 | 要求一覧に見当たらない RFP の記述（該当箇所を引用） |

3. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（意味的重複検出）。

   | 対象成果物 | 渡された検査対象 | 検査する事実の種類 | 要求文が指す実現したい事柄 | SSoTの所在 | 先に採番された要求ID（後の方を重複側とする） | 検査の型 | 二重定義 | 報告単位 | 重複と判定した要求IDの対 |

   同一性は文言の類似ではなく「一方が満たされれば他方も自動的に満たされるか」で判定する（ISO/IEC/IEEE 29148
   非冗長性）。文言が似ていても対象範囲・条件が異なれば重複としない。手順5で矛盾として指摘する組は重ねない。

4. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象の全行 | 根拠 | `.aidd/rfp/**`・人間が壁打ちで確定した回答 | 根拠の粒度 | `RFP` 種別は RFP 内の実在位置、`壁打ち` 種別は人間の確定回答 |

   出典種別=壁打ちの行は、確定回答が入力に無いことだけを理由に根拠なしとしない（手続きの確認は手順8が扱う）。

5. `.claude/skills/internal-contradiction-detection/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象の全行 | 突合単位 | 要求ID同士 |

6. `.claude/skills/classification-validity/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象の全行 | 分類基準 | `Templates/Flow/requirement-list.md` の分類定義 |

7. `.claude/skills/summarization-fidelity/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象のうち出典種別=RFPの行 | 根拠 | `.aidd/rfp/**` |

   改版時は、改版後 RFP に照らした差分判定（維持 / 変更 / 新規 / 廃止）の妥当性も見る。

8. `.claude/skills/adhoc-entry-validity/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象のうち出典種別=壁打ちの行 |

   既存要求の詳細化にすぎない行が新規要求として追加されていないかも見て、該当すれば寄せ先の既存要求IDを示す。

9. `.claude/skills/legal-compliance-identification/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象の制約/非機能の行 | 根拠 | `.aidd/rfp/**` |

   RFP→要求一覧の欠落に加え、法令・規制に基づくと推測される行で、その根拠が RFP の言及にも要求一覧の
   分類・記述にも読み取れないものを指摘する。法令名は特定・断定しない。手順10で同趣旨の提案がある箇所は重ねない。

10. `.claude/skills/gap-proposal/SKILL.md` を Read し、次を指定して実行する。

    | 対象 | `.aidd/rfp/**` 全体 | 突合先 | 渡された検査対象 |

11. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘（check-runner の手順0で
    合流させた `id-format-check` / `revision-diff-check` の分を含む）を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。

## 禁止

- 対象成果物の本文を書き換えない
- 判断（修正/差戻し/対応せず進める/未対応）・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない（上書き・削除禁止）
- 指示された観点 Skill 以外を勝手に実行しない
- 合否・重大度を自分で判断しない
