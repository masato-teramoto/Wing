---
format_version: 2
phase: feature
created_at: 2026-10-01T18:34:22+09:00
---

# ゲート記録

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 1 | 2026-10-01T18:34:22+09:00 | ①② | [".aidd/feature-list.md"] | {".aidd/feature-list.md": "4ea8f44148bd789ba40646fca22e3698a8436bcc0a5daad4c6d21af082a66ef7"} | 5 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | traceability | steering/product.md 「主要ユースケース」3／.aidd/requirement-list.md REQ-011・REQ-066／.aidd/feature-list.md 「フィーチャー一覧」property-basic-info 行の目的列 | 機能領域「承認者による承認・差戻し、申請者による取下げ」（product.md 主要ユースケース3「承認フローの承認者が、回ってきた申請を確認し、承認または差戻しを行う」、REQ-066「申請の差戻し・取下げができる」）が、どの feature の目的にも現れない。REQ-011・REQ-066 は property-basic-info の対応要求IDに割り当てられているが、目的は「登録・変更して承認フローへ申請し」と申請側だけを述べている（意味判定: ID対応あり・目的の記述に承認側の領域なし）。 |  |  |
| 2 | ssot-consistency | .aidd/feature-list.md 「フィーチャー一覧」対応要求ID列（property-basic-info・issue-request・issue-request-tutorial・application-status-search・contract-info-import・contract-info-download の各行） | 多重割当: REQ-063（各画面は入力チェック（必須・桁数・形式）を行い、エラー時はメッセージを表示して処理を止める）が 6 つの feature に割り当てられている（print-report には無い）。要求文は「各画面」を対象とする横断的な要求である。複数割当のままとするか、どれか1つに所有させるかは人間による確認が必要。 |  |  |
| 3 | classification-validity | .aidd/feature-list.md 「フィーチャー一覧」issue-request-tutorial 行の種別列 | 種別が `User` だが、目的は「発行依頼書登録変更画面のボタンから開くポップアップで、…選んだ値と入力した値を発行依頼書の項目へ設定する」であり、テンプレートの判定の一問「この feature だけが出来上がった状態で、誰かが用事を済ませて終われるか」に対し、設定した値の登録は issue-request が行うため単体では終われない（「他の feature の中で使われる」に当たる）。一方で Platform の定義「他の feature に使われて働く共通の仕組み」のうち「共通の」には当たらない（使うのは issue-request だけ）。定義の2つの条件が分かれており、`User` のままか `Platform` かは人間による確認が必要。 |  |  |
| 4 | evidence-guard | .aidd/feature-list.md 「フィーチャー一覧」優先度列（issue-request-tutorial=3、print-report=4、application-status-search=5、contract-info-import=6） | 出典不明: 依存の必須先行で決まらない範囲の順序（issue-request-tutorial を print-report・application-status-search・contract-info-import より先、print-report を application-status-search より先、application-status-search を contract-info-import より先）が、steering/product.md・.aidd/requirement-list.md から導けない。product.md の主要ユースケースの列挙順とはおおむね一致するが、product.md は列挙順を優先度として定めておらず、チュートリアルは主要ユースケースに無い（「解決する課題」「提供価値」に入力補助として現れるだけ）。成果物にこの順序の出典（作成時の回答など）の記載が無く、追跡できない。 |  |  |
| 5 | evidence-guard | .aidd/feature-list.md 「フィーチャー一覧」目的列（GWTG070・GWTG080・GWTG081・GWTG090・GWTG100・PWTGO072） | 出典不明: 目的列に書かれた画面ID GWTG070・GWTG080・GWTG081・GWTG090・GWTG100 とプログラムID PWTGO072 が、.aidd/requirement-list.md・steering/*.md のどこにも無い（steering/tech.md の命名規則の例に GWTG060・PWTGB090・RWTG070 があるだけ）。REQ-005 は画面・帳票・バッチの構成を基本設計で決めるとしており、成果物に ID の出典（作成時の回答など）の記載が無いため追跡できない。 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 1 | 1 | 対応せず進める | 承認、差戻し、取下げは REQ-011 と REQ-066 として property-basic-info に割り当て済みで、中身は Phase 4 の requirements で定める | Junichi Noumi | 2026-10-01T18:43:58+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 1 | 2 | 対応せず進める | 入力チェックは画面ごとに項目が違い、各 feature で定めるため複数割当のままとする。print-report は入力欄が無いので割り当てない | Junichi Noumi | 2026-10-01T18:43:59+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 1 | 3 | 対応せず進める | User のままとする。利用者が自分で操作する画面で、使うのは issue-request だけなので共通の仕組みに当たらない | Junichi Noumi | 2026-10-01T18:44:00+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 1 | 4 | 対応せず進める | 優先度は人間が確定した（Phase 3 計画了承の回答と Q-FEA-002 の回答） | Junichi Noumi | 2026-10-01T18:44:02+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 1 | 5 | 対応せず進める | 画面ID とプログラムID は人間が確定した（Phase 2 の回答1と回答3、Phase 3 計画了承の回答） | Junichi Noumi | 2026-10-01T18:44:03+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 1 | .aidd/feature-list.md | Junichi Noumi | 2026-10-01T18:44:04+09:00 | 4ea8f44148bd789ba40646fca22e3698a8436bcc0a5daad4c6d21af082a66ef7 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| phase | 1 | 1 | 対応せず進める | 承認、差戻し、取下げは REQ-011 と REQ-066 として property-basic-info に割り当て済みで、中身は Phase 4 の requirements で定める | phase | 1 |
| phase | 1 | 2 | 対応せず進める | 入力チェックは画面ごとに項目が違い、各 feature で定めるため複数割当のままとする。print-report は入力欄が無いので割り当てない | phase | 1 |
| phase | 1 | 3 | 対応せず進める | User のままとする。利用者が自分で操作する画面で、使うのは issue-request だけなので共通の仕組みに当たらない | phase | 1 |
| phase | 1 | 4 | 対応せず進める | 優先度は人間が確定した（Phase 3 計画了承の回答と Q-FEA-002 の回答） | phase | 1 |
| phase | 1 | 5 | 対応せず進める | 画面ID とプログラムID は人間が確定した（Phase 2 の回答1と回答3、Phase 3 計画了承の回答） | phase | 1 |
