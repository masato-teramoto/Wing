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

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 2 | 2026-10-01T19:11:29+09:00 | ①② | [".aidd/feature-list.md"] | {".aidd/feature-list.md": "d179a4dd574f96926ca8b8834784bdab67c632c91bf3ad9f623c91c0af686268"} | 3 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | ssot-consistency | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記（1〜3点目）／同ファイル冒頭の注記「スコープ・完了条件はここに書きません。それらは specs/&lt;feature&gt;/requirements.md（Boundary Context / Acceptance Criteria）が正です」 | 二重定義: 注記は feature の責務（property-basic-info が契約局情報 TWTGM140 を登録・更新・削除する、発行依頼書情報 TWTGM100 を読むだけとする、変更履歴 TWTGA120 をどの feature も使わない）を定めている。同じファイルの冒頭は、スコープの正を specs/&lt;feature&gt;/requirements.md の Boundary Context とし、本ファイルは順序と根拠だけを持つと定めているため、責務の記述が2か所に置かれる形になる。requirements.md は今回の検査対象に無く、両者が同一内容か食い違うかは判定できない。どちらを正とするかは人間による確認が必要。なお注記2点目の依存の向き（issue-request → property-basic-info）は依存列と同一内容である。 |  |  |
| 2 | steering-conformance | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記 3点目／steering/database.md 「設計思想」3点目／steering/product.md 「ビジネスルール / ポリシー」申請・承認の履歴 | 矛盾（成立するかは判定不能）: 注記は「変更履歴（TWTGA120）はどの feature も使わない」とする。database.md は「申請・承認の対象データは、変更履歴を履歴テーブル（種別 A）に残す（REQ-012・REQ-027）」とし、product.md は同じ方針の適用範囲を物件基本情報と発行依頼書としている。TWTGA120 は命名上種別 A（変更履歴）の表だが、何の変更履歴かは steering・要求一覧に記述が無い。TWTGA120 が物件基本情報または発行依頼書の変更履歴であれば、どの feature も使わないことは上記の方針と両立しない。どちらに当たるかは人間による確認が必要。 |  |  |
| 3 | evidence-guard | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記（1〜3点目） | 根拠なし: 注記に書かれたテーブルID TWTGM140（契約局情報）・TWTGM100（発行依頼書情報）・TWTGA120（変更履歴）、「契約局取込のボタンも物件基本情報登録変更画面にある」、「TWTGM100 が無くても画面は動く」に対応する記述が、.aidd/requirement-list.md・steering/*.md のどこにも無い（契約局情報は product.md 主要ユースケース4と REQ-016 に帳票の出力情報として現れるだけで、契約局取込に当たる要求は無い）。注記は出典を「Phase 4 からの差戻しによる修正。回答者 Junichi Noumi、2026-10-01」と記しているが、根拠として指定された上流成果物の中では追跡できない。 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 1 | 対応せず進める | 責務の正は各 requirements.md の Boundary Context とする。feature 一覧の注記は、依存の向きの根拠を説明するものとして残す | Junichi Noumi | 2026-10-01T19:18:13+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 2 | 対応せず進める | 物件基本情報の履歴は承認履歴 TWTGM180 で残し、項目の変更履歴は持たない。発行依頼書の変更履歴は TWTGA130 で、issue-request が登録する。TWTGA120（物件基本情報変更履歴）は正解の CRUD 図で使われていない | Junichi Noumi | 2026-10-01T19:18:14+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 3 | 対応せず進める | テーブルの所有と契約局取込の画面は、人間が確定した（Phase 4 からの差戻しの回答）。中身は property-basic-info の requirements で定める | Junichi Noumi | 2026-10-01T19:18:16+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 2 | .aidd/feature-list.md | Junichi Noumi | 2026-10-01T19:18:17+09:00 | d179a4dd574f96926ca8b8834784bdab67c632c91bf3ad9f623c91c0af686268 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| phase | 2 | 1 | 対応せず進める | 責務の正は各 requirements.md の Boundary Context とする。feature 一覧の注記は、依存の向きの根拠を説明するものとして残す | phase | 2 |
| phase | 2 | 2 | 対応せず進める | 物件基本情報の履歴は承認履歴 TWTGM180 で残し、項目の変更履歴は持たない。発行依頼書の変更履歴は TWTGA130 で、issue-request が登録する。TWTGA120（物件基本情報変更履歴）は正解の CRUD 図で使われていない | phase | 2 |
| phase | 2 | 3 | 対応せず進める | テーブルの所有と契約局取込の画面は、人間が確定した（Phase 4 からの差戻しの回答）。中身は property-basic-info の requirements で定める | phase | 2 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 3 | 2026-10-01T20:18:53+09:00 | ①② | [".aidd/feature-list.md"] | {".aidd/feature-list.md": "d179a4dd574f96926ca8b8834784bdab67c632c91bf3ad9f623c91c0af686268"} | 1 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | platform-foundation-coverage | steering/security.md 「認可」「権限モデル」（モデル・定義の置き場・禁止）／steering/product.md 「ビジネスルール / ポリシー」申請・承認の履歴／.aidd/requirement-list.md REQ-011・REQ-027／.aidd/feature-list.md 「フィーチャー一覧」property-basic-info・issue-request 行の目的列 | 今回再承認された security.md は、承認フローで誰の番か（起案者・申請者・確認者・承認者）を審査権限マスタ TWTGM170 とコードマスタ P82 で判定し、承認フローの番の判定をそれ以外の仕組みで作らないと定める。product.md は申請・承認の対象を物件基本情報と発行依頼書とし、REQ-027 は発行依頼書の各申請・承認時の履歴登録を求めるため、承認フローの番の判定は property-basic-info と issue-request の両方が前提とする共通の仕組みに当たりうる。feature-list では承認フローは property-basic-info の目的（「承認フローへ申請し」）にだけ現れ、issue-request の目的にも独立した Platform feature にも、番の判定と TWTGM170 の参照・登録（マスタの保守）を担う記述が無い。TWTGM170 が既存のマスタか本案件で作るものかは steering・要求一覧に記述が無く、マスタの保守を担う feature が必要かは判定できない。人間による確認が必要。 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 3 | 1 | 対応せず進める | TWTGM170 を保守する画面は作らない。データは導入時と運用時に DB へ直接登録する（導入手順書で扱う）。テーブルの定義は property-basic-info が持ち、issue-request は参照だけする。誰の番かの判定は property-basic-info の承認フローで行う。発行依頼書の履歴（REQ-027）は、その申請と承認の操作に合わせて issue-request が登録する | Junichi Noumi | 2026-10-01T20:24:09+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 3 | .aidd/feature-list.md | Junichi Noumi | 2026-10-01T20:24:10+09:00 | d179a4dd574f96926ca8b8834784bdab67c632c91bf3ad9f623c91c0af686268 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| phase | 3 | 1 | 対応せず進める | TWTGM170 を保守する画面は作らない。データは導入時と運用時に DB へ直接登録する（導入手順書で扱う）。テーブルの定義は property-basic-info が持ち、issue-request は参照だけする。誰の番かの判定は property-basic-info の承認フローで行う。発行依頼書の履歴（REQ-027）は、その申請と承認の操作に合わせて issue-request が登録する | phase | 3 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 4 | 2026-10-02T10:58:45+09:00 | ①② | [".aidd/feature-list.md"] | {".aidd/feature-list.md": "bdc11bd9c5aa38cb81b4f4039b93582d9f44e045f87e754b7d1aa54f1dcc3540"} | 2 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | ssot-consistency | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記 1点目・2点目 | 二重定義（食い違いあり）: 契約局情報 TWTGM140 を更新する責務が2か所に書かれている。1点目は「契約局情報（TWTGM140）は property-basic-info が登録・更新・削除する」とし、property-basic-info だけを挙げている。2点目は property-basic-info の操作に「並替え」を加え、さらに「issue-request も、発行依頼書登録変更画面の更新で TWTGM140 の行を登録・更新する（削除はしない）」としている。このため、同じテーブルの行の登録・更新を2つの feature が受け持つことになる。1点目は、2点目と比べて並替えと issue-request の分が無く、内容が一致していない。どちらの記述を正とするか、また2つの feature が同じ行を登録・更新する形でよいかについて、SSoT の所在が示されていないため人間による確認が必要。 |  |  |
| 2 | evidence-guard | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記 2点目（「正解の CRUD 図では、物件申請情報登録・編集が TWTGM140 を SIUD、発行依頼書登録・変更が SIU である」） | 出典不明: 注記が根拠として挙げる「正解の CRUD 図」と、その中の名前「物件申請情報登録・編集」「発行依頼書登録・変更」は、.aidd/requirement-list.md・steering/*.md のどこにも無い。issue-request が TWTGM140 を登録・更新するという点は、steering/product.md 「ビジネスルール / ポリシー」の申請・承認の履歴と一部が合う（契約局情報の変更履歴 TWTGA150 は、issue-request が発行依頼書登録変更画面の更新と発番のときに登録する）。一方、TWTGM140 そのものを誰が SIUD または SIU で扱うかは、根拠に指定された上流には書かれていない。注記の出典は「Phase 4 issue-request 作成中の差戻し指示、回答者 Junichi Noumi、2026-10-02」とされているが、指定された上流の中では追跡できない。 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 4 | 1 | 修正 | 注記の1点目を消し、2点目だけを残す。&#10;2点目を正とする。&#10;TWTGM140 の行は2つの feature が扱う形でよい。役割は次のとおりで、同じ操作を2つが持つことは無い。&#10;・テーブルの定義は property-basic-info が持つ。&#10;・property-basic-info は、物件基本情報登録変更画面で行の登録・更新・削除・並替えをする。&#10;・issue-request は、発行依頼書登録変更画面の更新で、その画面の契約局の行を登録・更新する。削除はしない。&#10;この役割分担を注記の中で「SSoT はこの注記」と明記する。 | Junichi Noumi | 2026-10-02T11:16:31+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 4 | 2 | 修正 | 注記の2点目にある「正解の CRUD 図では〜」の一文を消す。&#10;出典は「Phase 4 issue-request 作成中の差戻しへの人間の回答（回答者 Junichi Noumi、2026-10-02）」とする。&#10;上流の文書には書かれていない決定なので、出典は人間の判断であることをそのまま示す。 | Junichi Noumi | 2026-10-02T11:16:34+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 5 | 2026-10-02T11:16:58+09:00 | ①② | [".aidd/feature-list.md"] | {".aidd/feature-list.md": "24ee88ef24c82686acd706708035a837f59326a21421b27c4ac80bb861a5ecdd"} | 2 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | ssot-consistency | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記 1点目（「契約局情報（TWTGM140）の役割分担は、この注記を SSoT とする」「契約情報取込で TWTGM140 を更新するかは、Phase 4 の contract-info-import で扱う」）／同ファイル冒頭の注記（「スコープ・完了条件はここに書きません。それらは specs/&lt;feature&gt;/requirements.md（Boundary Context / Acceptance Criteria）が正です。本ファイルは「どの順で、何を根拠に作るか」だけを持ちます」） | 二重定義（SSoT の所在が2か所で宣言されている）: 注記 1点目は、TWTGM140 を feature ごとにどう扱うか（テーブル定義の所有、property-basic-info の登録・更新・削除・並替え、issue-request の登録・更新）について「この注記を SSoT とする」と定める。一方、同じファイルの冒頭は、feature の範囲の正を specs/&lt;feature&gt;/requirements.md の Boundary Context とし、本ファイルは順序とその根拠だけを持つと定めている。このため、同じ責務の正が2か所にあることになる。さらに同じ点で、contract-info-import が TWTGM140 を更新するかを Phase 4 の contract-info-import に委ねている。その結果、SSoT とした注記の役割分担が、注記の外（contract-info-import の requirements）で増える可能性があり、「同じ操作を 2 つの feature が持つことは無い」が確かめられるのも注記の外になる。requirements.md は今回の検査対象に無く、両者が同じ内容か食い違うかは判定できない。冒頭の定めと注記のどちらを正とするか、また contract-info-import で決まった分を注記に戻すかは、人間による確認が必要。 |  |  |
| 2 | steering-conformance | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記 1点目（「property-basic-info は、物件基本情報登録変更画面で行の登録・更新・削除・並替えをする」）／steering/product.md 「ビジネスルール / ポリシー」申請・承認の履歴／steering/database.md 「設計思想」3点目 | 矛盾（成立するかは判定不能）: product.md は、申請・承認の対象データについてステータスと履歴を管理するとしている（適用範囲は物件基本情報・発行依頼書・契約局情報）。そのうえで、契約局情報の項目の変更履歴（TWTGA150）は「issue-request が、発行依頼書登録変更画面の更新と発番のときに登録する」とし、database.md も TWTGA150 を契約局情報の変更履歴の表としている。一方、注記は property-basic-info も物件基本情報登録変更画面で契約局情報（TWTGM140）の行を登録・更新・削除・並替えすると定めている。product.md の書き方では、property-basic-info による契約局情報の変更（特に削除）は TWTGA150 に残らない。product.md の適用範囲には「履歴に残す項目と契機は各 feature で決める」とあるが、TWTGA150 の登録の契機は issue-request の操作に限っている。property-basic-info による変更を履歴に残さないことが、product.md の「契約局情報の履歴を管理する」と両立するかは、steering・要求一覧からは判定できない。注記と product.md のどちらに合わせるかは、人間による確認が必要。 |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 2 | 人間による確認 | 直すべきなのが本ファイルの注記（Phase 3）か steering/product.md の申請・承認の履歴（Phase 2）かを、上流からは決められないため |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 5 | 1 | 対応せず進める | 冒頭の定めを正とする。&#10;feature の範囲の正は、各 requirements の Boundary Context である。&#10;注記は、依存の向きと担当の根拠を示す要約として読む。&#10;注記の「この注記を SSoT とする」は、Phase 3 の時点で決めた担当の要約という意味に読む。&#10;contract-info-import で決まった分は、注記に戻さない。その requirements の Boundary Context に書く。 | Junichi Noumi | 2026-10-02T11:34:27+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 5 | 2 | 対応せず進める | 注記と product.md は両立するものとして進める。&#10;契約局情報の変更履歴（TWTGA150）は、発行依頼書登録変更画面で契約局の項目を変えたときに残す。&#10;物件基本情報登録変更画面での契約局の行の並替えと削除は、変更履歴に残さない。&#10;product.md の「契約局情報の履歴を管理する」は、この範囲のことと読む。&#10;履歴に残す項目ときっかけは、product.md のとおり各 feature で決める。 | Junichi Noumi | 2026-10-02T11:34:29+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 4 | 1 | phase | 5 | Junichi Noumi | 2026-10-02T11:34:31+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 4 | 2 | phase | 5 | Junichi Noumi | 2026-10-02T11:34:34+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 5 | .aidd/feature-list.md | Junichi Noumi | 2026-10-02T11:34:36+09:00 | 24ee88ef24c82686acd706708035a837f59326a21421b27c4ac80bb861a5ecdd |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| phase | 5 | 1 | 対応せず進める | 冒頭の定めを正とする。&#10;feature の範囲の正は、各 requirements の Boundary Context である。&#10;注記は、依存の向きと担当の根拠を示す要約として読む。&#10;注記の「この注記を SSoT とする」は、Phase 3 の時点で決めた担当の要約という意味に読む。&#10;contract-info-import で決まった分は、注記に戻さない。その requirements の Boundary Context に書く。 | phase | 5 |
| phase | 5 | 2 | 対応せず進める | 注記と product.md は両立するものとして進める。&#10;契約局情報の変更履歴（TWTGA150）は、発行依頼書登録変更画面で契約局の項目を変えたときに残す。&#10;物件基本情報登録変更画面での契約局の行の並替えと削除は、変更履歴に残さない。&#10;product.md の「契約局情報の履歴を管理する」は、この範囲のことと読む。&#10;履歴に残す項目ときっかけは、product.md のとおり各 feature で決める。 | phase | 5 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 6 | 2026-10-05T18:25:55+09:00 | ①② | [".aidd/feature-list.md"] | {".aidd/feature-list.md": "71a64dc3cbf71bc6ddb02a4dc6f8247344064ca63e8a291e5881763ef59256ae"} | 4 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | ssot-consistency | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記 1点目（「contract-info-import は、取込のとき申請No ごとに契約局情報の行を全部消して、ファイルの内容で入れ直す（洗替）」）／同ファイル冒頭の注記（「スコープ・完了条件はここに書きません。それらは specs/&lt;feature&gt;/requirements.md（Boundary Context / Acceptance Criteria）が正です」） | 二重定義（SSoT の所在の確認）: 注記 1点目は、今回 contract-info-import が TWTGM140 を洗替で扱うことを、「この注記を SSoT とする」とした役割分担に加えた。ゲート記録の phase 5 回目 指摘1 の判断では、冒頭の定めを正とし、「contract-info-import で決まった分は、注記に戻さない。その requirements の Boundary Context に書く」としている。今回の記載で、contract-info-import が TWTGM140 をどう扱うかが、この注記と contract-info-import の requirements の Boundary Context の 2 か所に書かれる形になる。requirements.md は今回の検査対象に無いため、両者が同じ内容か食い違うかは判定できない。今回の差戻し指示で前回の判断の扱いを変えたのか、どちらを正とするかは、人間による確認が必要。 |  |  |
| 2 | ssot-consistency | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記 2点目（TWTGM100 の削除と複製、「複製で引き継ぐ項目と空にする項目の決まりは issue-request が持つ（specs/issue-request/requirements.md の 7.5・7.6）」「そのため依存の向きは issue-request → property-basic-info のままとする」）／同注記 1点目（TWTGM140 のテーブル定義の所有と「同じ操作を 2 つの feature が持つことは無い」）／「フィーチャー一覧」property-basic-info 行の依存列（なし）・優先度列（1） | 責務の分割（判定不能）: 注記 2点目は、発行依頼書情報 TWTGM100 の複製について、操作を property-basic-info に置き、引き継ぐ項目と空にする項目の決まりを issue-request に置いている。このため、1 つの複製の責務が 2 つの feature に分かれている。TWTGM140 については、注記 1点目でテーブル定義の所有と、画面での同じ操作を 2 つの feature が持たないことを定めている。一方、TWTGM100 については、テーブル定義をどの feature が持つかが書かれていない。property-basic-info は依存なし・優先度 1 である。そのため、優先度 2 の issue-request が持つ決まり（とテーブル）に従って削除と複製を行う形になる。注記が依存の向きの根拠として挙げる「TWTGM100 が無くても物件基本情報登録変更画面は動き、削除と複製は行があるときだけ行う」は、実行時の条件である。作る順で前にある property-basic-info が、後にある issue-request の定めを前提とすることと両立するかは、本ファイルからは判定できない。TWTGM100 のテーブル定義の所有と依存の向きについて、人間による確認が必要。 |  |  |
| 3 | steering-conformance | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記 2点目（「発行依頼書の項目の登録と更新は issue-request が持つ」）／steering/product.md 「ビジネスルール / ポリシー」申請・承認の履歴（「契約情報取込（contract-info-import）も、洗替のときに TWTGA150・TWTGA130 に変更履歴を登録する。登録するのは内容が変わった行の取込前の内容だけとする」）／steering/database.md 「クエリパターン」洗替 | 矛盾（成立するかは判定不能）: 再承認された product.md は、contract-info-import が洗替のときに、発行依頼書の変更履歴 TWTGA130 にも、内容が変わった行の取込前の内容を登録するとしている。database.md も TWTGA130 を発行依頼書の項目の変更履歴の表としている。これは、contract-info-import が取込で発行依頼書の内容を変えることを前提にしていると読める。一方、注記 2点目は、発行依頼書の項目の登録と更新は issue-request が持つとしている。注記 1点目で contract-info-import に加えたのは、TWTGM140（契約局情報）の洗替だけである。contract-info-import による発行依頼書の更新が「issue-request が持つ」と両立するのか、注記の範囲が画面での操作に限られるのかは、本ファイルと steering からは判定できない。人間による確認が必要。 |  |  |
| 4 | evidence-guard | .aidd/feature-list.md 「フィーチャー一覧」表の直後の注記 2点目（「発行依頼書情報（TWTGM100）」「申請の削除で行を物理削除する」「修正稟議と再製本で行を新しい申請No に複製する」） | 出典不明: 注記 2点目のテーブルID TWTGM100（発行依頼書情報）、申請の削除で行を物理削除すること、修正稟議で行を複製することに対応する記述が、.aidd/requirement-list.md・steering/*.md のどこにも無い。steering にあるのは、再製本（security.md 「チェックの適用箇所」の再製本ボタン、product.md 主要ユースケース4）と、物件基本情報の引用による複製（REQ-010）だけである。注記は出典を「Phase 4 横断検査 1 回目 指摘2 の差戻し指示、回答者 Junichi Noumi、2026-10-05」としているが、根拠として指定された上流成果物の中では追跡できない。 |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 3 | 人間による確認 | 直すべきなのが本ファイルの注記（Phase 3）か steering/product.md の申請・承認の履歴（Phase 2）かを、上流からは決められないため |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 1 | 対応せず進める | 前回の判断は変えない。冒頭の定めのとおり、contract-info-import が契約局情報をどう扱うかの正は、その requirements の Boundary Context と 2.3・2.4 にある。注記 1点目の洗替の一文は、TWTGM140 の役割分担を一覧で見渡すための要約で、中身は requirements と同じ。食い違ったときは requirements を正とする。 | Junichi Noumi | 2026-10-05T18:36:18+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 2 | 対応せず進める | 発行依頼書情報（TWTGM100）のテーブル定義は issue-request が持つ。property-basic-info の削除と複製は、そのテーブルの行を消すことと写すことだけで、どの項目を引き継ぎどれを空にするかは issue-request の決まりに従う。どちらの requirements も承認済みなので、property-basic-info の design は issue-request の requirements を見て書ける。作る順と依存の向きは変えない。 | Junichi Noumi | 2026-10-05T18:36:21+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 3 | 対応せず進める | 注記 2点目の「発行依頼書の項目の登録と更新は issue-request が持つ」は、画面での操作のことと読む。注記 1点目の「同じ操作を 2 つの feature が持つことは無い」と同じ読み方。契約情報取込は、洗替で発行依頼書も入れ直し、変更履歴を登録する（specs/contract-info-import/requirements.md の 2.3・2.5・3.1）。steering は直さない。今回は差し戻さない。 | Junichi Noumi | 2026-10-05T18:36:24+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 4 | 対応せず進める | 出典は人間の判断で、業務の決まりとして確定したもの。根拠は注記に書いた差戻し指示のとおり。上流の要求一覧と steering に同じ記述が無くても、この注記を正とする。 | Junichi Noumi | 2026-10-05T18:36:27+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 6 | .aidd/feature-list.md | Junichi Noumi | 2026-10-05T18:36:30+09:00 | 71a64dc3cbf71bc6ddb02a4dc6f8247344064ca63e8a291e5881763ef59256ae |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| phase | 6 | 1 | 対応せず進める | 前回の判断は変えない。冒頭の定めのとおり、contract-info-import が契約局情報をどう扱うかの正は、その requirements の Boundary Context と 2.3・2.4 にある。注記 1点目の洗替の一文は、TWTGM140 の役割分担を一覧で見渡すための要約で、中身は requirements と同じ。食い違ったときは requirements を正とする。 | phase | 6 |
| phase | 6 | 2 | 対応せず進める | 発行依頼書情報（TWTGM100）のテーブル定義は issue-request が持つ。property-basic-info の削除と複製は、そのテーブルの行を消すことと写すことだけで、どの項目を引き継ぎどれを空にするかは issue-request の決まりに従う。どちらの requirements も承認済みなので、property-basic-info の design は issue-request の requirements を見て書ける。作る順と依存の向きは変えない。 | phase | 6 |
| phase | 6 | 3 | 対応せず進める | 注記 2点目の「発行依頼書の項目の登録と更新は issue-request が持つ」は、画面での操作のことと読む。注記 1点目の「同じ操作を 2 つの feature が持つことは無い」と同じ読み方。契約情報取込は、洗替で発行依頼書も入れ直し、変更履歴を登録する（specs/contract-info-import/requirements.md の 2.3・2.5・3.1）。steering は直さない。今回は差し戻さない。 | phase | 6 |
| phase | 6 | 4 | 対応せず進める | 出典は人間の判断で、業務の決まりとして確定したもの。根拠は注記に書いた差戻し指示のとおり。上流の要求一覧と steering に同じ記述が無くても、この注記を正とする。 | phase | 6 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 7 | 2026-10-09T17:05:49+09:00 | ①② | [".aidd/feature-list.md"] | {".aidd/feature-list.md": "9c8fae4dbc53b2ff6cc98e2476e7c02797d2077359d9b2709d5eff7e5111b642"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 7 | .aidd/feature-list.md | masato-teramoto | 2026-10-09T17:08:04+09:00 | 9c8fae4dbc53b2ff6cc98e2476e7c02797d2077359d9b2709d5eff7e5111b642 |
