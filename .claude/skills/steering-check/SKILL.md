---
name: steering-check
description: Phase 2（Steering作成）の品質ゲート。steering/ 7ファイルを検査する
disable-model-invocation: true
---

## 概要

`steering/` 7ファイル（`product.md` / `tech.md` / `architecture.md` / `security.md` /
`non-functional.md` / `database.md` / `api-standards.md`）を対象に、観点 Skill を順に実行し、
指摘を蓄積してから `gate-report` へ渡す。① 形式検証で不備が見つかった場合、② 以降には進まない。

## 入力の範囲

「渡された検査対象」は、ホストが渡した検査対象の明示的な一覧（context の `review_targets`。snapshot の対象と同じ。gate.yaml の `target_review`、省略時はアクションの出力すべて）を指す。一覧のファイルだけを検査対象とし、一覧に無い出力は検査しない。特定のファイル名を書いた行は、そのファイルが検査対象に無ければfailedで返す。以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | 渡された検査対象 | テンプレパス | `Templates/steering/<同名ファイル>` | ID書式 | なし | 追加検証 | `Templates/steering/` の全ファイルが `steering/` に存在する | 報告単位 | ファイル × セクション |

   プレースホルダーは、不要理由が明記された箇所を指摘しない。理由の無いまま残る `<UPPER_SNAKE>`・未置換の
   `{{...}}` と、値にも不要理由付きの残置にもならず削除されたプレースホルダー（保持が規約）を指摘する。

2. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（相互参照切れ検出）。

   | 対象成果物 | 渡された検査対象 | 検査する事実の種類 | 「○○を参照」形式の章・セクションへの相互参照 | SSoTの所在 | 参照先として名指しされたファイル | 検査の型 | 参照切れ | 報告単位 | 参照表現1件 |

   参照先が存在し、かつ空でないかを見る。

3. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（非機能反映突合）。

   | 上流 | `.aidd/requirement-list.md` | 下流 | 渡された検査対象 | 突合方向 | 上流→下流 | 対応の単位 | 要求ID | 分母の絞り込み | 分類=非機能/制約の行のみ | 報告単位 | 未反映の要求ID |

   - ID の対応だけでなく、要求の内容が steering の記述で満たされているかまで意味判定する（層②。判定したことを指摘に明示）。
   - 続けて同じ上流・下流で、要求一覧の全行（分類を問わない）からチェック項目を作り、steering の記入済み欄
     （埋めたプレースホルダー）が各項目を満たすプロジェクト全体方針になっているかを判定する。機能要求には
     個別の設計を求めず、対象範囲・アーキテクチャ・データ方針等の全体方針で受け止められているかだけを見る。
     この判定の報告単位はチェック項目とする。

4. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（SSoT維持検証・二重定義）。

   | 対象成果物 | 渡された検査対象 | 検査する事実の種類 | 方針・設計ルールの記述 | SSoTの所在 | 7ファイルの記述分担（product / tech / architecture / security / non-functional / database / api-standards の担当領域） | 検査の型 | 二重定義 | 報告単位 | 重複している記述の対 |

   下位ファイルが上位方針を「準拠」として引用するのは二重定義ではない。

5. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する（設計ルール粒度検証）。

   | 対象 | 渡された検査対象（自己参照） | 参照する steering | `steering/*.md` 一式 | 検証観点 | 粒度・実体混入 |

   業務コード・DB エンティティの設計ルールが、各 `design.md` がそれを参照するだけで設計できる粒度か（不足すると
   feature ごとに独自解釈が生じ Phase 6 で衝突する）、個々のコード値・区分値・採番対象・テーブル定義が混入して
   いないかを、「全 feature に等しく適用されるか」を基準に判定する。

6. `.claude/skills/iso25010-coverage/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `steering/non-functional.md` / `steering/architecture.md` | 突合元 | `.aidd/requirement-list.md` の非機能/制約要求 |

   データガバナンス（保持期間・削除・越境移転）を信頼性/セキュリティの下位観点として含める。該当しない特性は
   「不要」とその理由が明記されていれば指摘しない。手順3で未反映と指摘した要求IDは重ねない。

7. `.claude/skills/stride-coverage/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `steering/security.md` |

8. `.claude/skills/slo-quantification/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `steering/non-functional.md` の反映済み記述 |

9. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | 渡された検査対象 | 根拠 | `.aidd/requirement-list.md`（特に非機能/制約）・人間が確定した回答 | 根拠の粒度 | 要求IDの特定、または人間の回答の引用 |

10. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。

## 禁止

- 対象成果物の本文を書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否・重大度を自分で判断しない
