---
format_version: 2
phase: docs
created_at: 2026-10-09T21:20:29+09:00
---

# ゲート記録

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 1 | 2026-10-09T21:20:29+09:00 | ①② | ["docs/code-design.md","docs/architecture/data-model.md","docs/architecture/system-overview.md"] | {"docs/code-design.md":"b8c95f94964296efaf7075c9588817a457d178d6a5f700fd889eb127f3b8b60b","docs/architecture/data-model.md":"4b9b734151cb3d1ff705505abbd83a4a9f0a141fe6dc0c5e64948cabb379ead6","docs/architecture/system-overview.md":"b37749c30298d2308360eae85fa55f693302dc6a40ae8f6bf6b045aa28ee5340"} | 11 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | format-conformance | 書式 | 軽微 | 0842b0c5ff15c5d9 | e66a2c465689398f | docs/code-design.md § コード定義一覧 / 表示順 6（ほか 表示順 14） | 検索条件のコンボの選択肢（その他） | コード定義一覧の行 6 が 3 識別を 1 行に束ね、宣言した単位に反する | 本書の「本書での単位」は「1 行を TWTZM040 の識別（システム区分／種別／コード番号）の 1 つとして揃える」と宣言している。表示順 6 は管理コード欄に WTG/PARAM/P31・P32・P53 の 3 識別を並べている（項目名も「その他」で業務名が無い）。テンプレート（Templates/docs/code-design.md）の書き方も「管理コードには 1 つの値を書く」。上流の対応は _handoff/phase5-application-status-search-conditions.md（design の補足資料が正とする表）の No.33 押印種別＝P31、No.34 発送書類名の候補＝P32、No.38 転貸借契約種別＝P53。なお表示順 14 は管理マスタが messages.properties で、宣言した単位（TWTZM040 の識別）の外にある。 | 表示順 6 を 3 行（押印種別＝P31、発送書類名の候補＝P32、転貸借の契約種別＝P53）に分け、項目名を業務名にする。表示順 14 を残すなら「本書での単位」にメッセージキーを含める旨を足す。 | 修正：対応表は上流資料にあり、新しい業務の事実は要らない | 確認済み |  |  |
| 2 | traceability | 業務の欠落・矛盾 | 重大 | 26db08edee3ef56c | - | docs/code-design.md § コード定義一覧（行の欠落） | 承認履歴の判定・審査権限・単独複数局ﾌﾗｸﾞ・既存メッセージキー | design が使う判定・審査権限・単独複数局フラグ・検証メッセージが無い | specs/application-status-search/design.md が検索・一覧で使う区分値のうち、code-design に行が無いもの。（a）承認履歴の判定 01 申請依頼・02 申請・03 確認・04 承認（design 『承認履歴の日時』）、（b）審査権限 '01'（進捗の日数・起案日）、（c）単独複数局ﾌﾗｸﾞ "0"（「他n局」の条件。pbi design の TWTGM080 列表で 0:単独局／1:複数局）、（d）入力チェックの既存メッセージキー WTG-000003・GEF-000025・WTL-000007・GEF-000014・GEF-000003（design 『バリデーション設計』）。code-design は DS-100024・DS-100025 は載せ、WTG-100018 も行にしているので、既存メッセージキーの載せ方が揃っていない。pbi design 247 行付近は「コードマスタを作らない属性（判定・権限ID）は DB レイアウトの備考の値を使う」としており、TWTZM040 の識別に当たらないため『本書での単位』から漏れている。 | 選べる案：（1）管理マスタを TWTGM180 の列（備考の値）などとした行を足す（2）本書の範囲外と範囲注記に明記する。既存メッセージキーも、載せる／載せないのどちらかに揃える。 | 質問：TWTZM040 に無い区分値とメッセージキーを code-design に載せるかは、本書の範囲の決め方（人の判断）による | 確認済み |  |  |
| 3 | traceability | 業務の欠落・矛盾 | 重大 | 55d1bf40b655fa0a | e573a638127f21a8 | docs/architecture/system-overview.md § ドメイン境界の地図 / 補足 2・4 | /wtg070/deleteShinse の戻り | deleteShinse 後の /wtg060/return 戻りが system-overview に無い | design『データ契約と外部連携』と『申請状況検索一覧 Controller の呼び出し元』は、/wtg060/return への戻り元を 3 つ挙げる。（1）物件基本情報登録変更画面の /wtg070/returnList（2）契約情報取込の /wtg090/execute の後（3）物件基本情報登録変更画面で申請を削除した後の /wtg070/deleteShinse（design-check 3 回目 #1）。system-overview は（1）を補足 2、（2）を補足 4 に書くが、（3）はどこにも無い（docs 全体を検索して deleteShinse の記述なし）。 | 補足に「申請を削除した後（/wtg070/deleteShinse）も /wtg060/return で受け、セッションの条件で再検索する（削除した申請は一覧から消える。未検索なら初期表示）。pbi design 側の受け先 URL の記述は上流持ち越し」を足す。 | 修正：design に書かれた事実を転記するだけで、新しい業務の事実は要らない | 確認済み |  |  |
| 4 | traceability | 業務の欠落・矛盾 | 重大 | 675009206f0d85bf | cf680b9022ebd0f9 | docs/architecture/data-model.md § 主要エンティティ一覧 | ZMENUAUTH | メニュー権限 ZMENUAUTH の PWTGO060 行の登録が data-model に載っていない | design『移行方針』と『移行対象ファイル一覧』は、追加するデータとして TWTZM040 の P01 行と「メニューと ZMENUAUTH の PWTGO060 の行」の 2 つを挙げ、『維持する統合ポイント』『セキュリティ上の考慮』も ZMENUAUTH を使う。data-model は TWTZM040 の 1 行追加だけを書き、ZMENUAUTH は主要エンティティ一覧・ER 図・ドメイン境界のどこにも無い（docs 全体で ZMENUAUTH は system-overview の前提 1 か所のみ）。 | 主要エンティティ一覧に ZMENUAUTH（メニュー権限。既存の共通基盤の表。本機能は PWTGO060 の行を登録するだけ）を足すか、載せない理由を「本書での扱い」に書く。 | 修正：design の記述を反映するだけ | 確認済み |  |  |
| 5 | internal-contradiction-detection | 業務のあいまい・不足 | 要判断 | 85cc47adcd84d9fd | e573a638127f21a8 | docs/architecture/system-overview.md § ドメイン境界の地図 / 補足 1 | WTG 申請状態サービスの呼出し | A1→B1 の getExternalScope 呼出しが補足 1 の「呼ばず」と食い違う | 図は A1（申請状況検索一覧）から B1（物件基本情報登録変更画面 GWTG070・WTG 申請状態サービス）へ「getExternalScope」の矢印を引き、補足 3 も「物件基本情報の WTG 申請状態サービス」を使うと書く。一方、補足 1 は「他のまとまりのテーブルを読むだけで書かない。他の機能パッケージの Service・Mapper は呼ばず」と書く。本書の単位は機能ID（feature）のため、B1 を呼ぶことが補足 1 の「呼ばず」と食い違って読める。design（依存してよい対象）では WTG 申請状態サービスは function/wtg/common（共通）に置かれ、呼んでよい公開契約と位置づけられている。どちらの記述が正かは design の位置づけで解消できる。 | 補足 1 に「ただし WTG 申請状態サービスは function/wtg/common にある公開契約であり、呼んでよい」と書く。B1 のノード名も画面とサービスを分ける。 | 修正：design の位置づけで解消できる | 確認済み |  |  |
| 6 | evidence-guard | 業務の欠落・矛盾 | 重大 | 5e50f9e50a71214a | be137a46fda8b3ff | docs/architecture/data-model.md § ER 図 / TWTGM080 | PK 表記 | TWTGM080 を PK と描くが pbi design は主キーを持たず一意キー | ER 図は TWTGM080 の CompanyCD・Application_No に PK を付ける。pbi design（物理データモデル）は「TWTGM080 は主キーは持たず、ユニークキー AK_TWTGM080_1（CompanyCD, Application_No）」と書く。TWTGM100 も ir design で一意キー AK_TWTGM100_1（CompanyCD, Application_No）。TWTGM140 は一意キー（CompanyCD, Application_No, Renban, Keikaku_Kichikyoku_No）、TWTGM180 は（CompanyCD, Application_No, Shinsa_Count, Tsuban）だが、図の説明は「連番」「審査回」だけを省いたと書き、Keikaku_Kichikyoku_No・Tsuban の省略には触れていない。 | 図の説明に「PK はユニークキー（AK_…）を表し、主キー制約は持たない」と書き、TWTGM140・TWTGM180 の省略した列に Keikaku_Kichikyoku_No・Tsuban も挙げる。 | 修正：上流の事実に合わせて注記するだけ（PK の描き方を変えるなら質問） | 確認済み |  |  |
| 7 | definition-resolution-completeness | 業務の欠落・矛盾 | 重大 | 1ad19609af16fbb6 | e66a2c465689398f | docs/code-design.md § コード定義一覧 / 表示順 14 | WTG-100018 | WTG-100018 を新規と書くが pbi design は既存とし、根拠が無い | code-design 表示順 14 は WTG-100018 を「本 feature が新しく足す」と書く（application-status-search design『機能固有エラーコード』と同じ）。property-basic-info design は『メッセージキー』の節で「取込中の申請は一覧が既存の WTG-100018 を出す」と書き、新規か既存かが 2 つの design で食い違う。application-status-search design は「今の wing に無い」として pbi の直しを Phase 5 の最後に持ち越すと書くが、pbi design は未修正のまま。docs はどちらを正としたかの根拠を書いておらず、/wtg060 と /wtg060/return の食い違いを system-overview 補足 2 で根拠付きで解いているのと扱いが違う。 | 選べる案：（1）pbi design を直して「新規」に揃える（上流に差戻し）（2）docs に「新規。pbi design の『既存』は誤りで上流持ち越し」と根拠を書く。 | 差戻し：食い違いの原因は pbi design の記述で、docs だけで形状を決めない | 確認済み |  |  |
| 8 | design-rule-gap-detection | 業務のあいまい・不足 | 要判断 | 537e9abd024a7974 | 8386e642b72fcab9 | specs/application-status-search/design.md § 技術スタック（Technology Stack） / 開発端末の JDK 1.8（ほか 6 design） | 開発端末の JDK | 7 design が開発端末 JDK 1.8 を載せるが tech.md は JDK 1.7 のみ | 7 つの design（property-basic-info・issue-request・issue-request-tutorial・print-report・application-status-search・contract-info-import・contract-info-download）の技術スタック表が「開発端末の JDK 1.8（-source/-target 1.7）」を採り、うち 6 つは「steering/tech.md から意図して外れる。上流は Phase 5 の最後にまとめて直す（upstream-carryover）」と書く。tech.md は『コアテクノロジ』『開発環境／必須ツール』で JDK 1.7（1.7.0.55）だけを定め、開発端末の JDK 1.8 の扱いは steering のどこにも無い。全 design で『意図して外れる』は 51 か所、upstream-carryover は 71 か所（6 design）あり、steering 直しの洗い出しが必要。 | 選べる案：（1）tech.md の必須ツールに開発端末の JDK 1.8（-source/-target 1.7）を明記する（2）各 design の例外を維持し steering は変えない。 | 差戻し：ルールの持ち主は Phase 2（steering）。影響する design の洗い出しが要る | 確認済み |  |  |
| 9 | design-rule-gap-detection | 業務のあいまい・不足 | 要判断 | 23ae2a5e7067dd73 | 8f34cd39ab11bf9f | specs/application-status-search/design.md § データ契約と外部連携 / CSV（ほか 2 design） | CSV 出力規約 | CSV 出力規約が 3 design で繰り返されるが steering に無い | 3 つの design が同じ CSV 規約を書く。（pbi design の CsvUtils 新設）、application-status-search『データ契約と外部連携』（MS932・全項目ダブルクォート・CRLF・NULL は空文字・見出し行・ファイル名は機能ID_yyyyMMddHHmmss.csv）、contract-info-download（同じ CsvUtils.defaultCsvConfig の規約）。steering には CSV の文字コード・囲み・改行・ファイル名の規則が無い（tech.md に Windows-31J の言及が OS の項に 1 つあるだけ）。 | 繰り返されている規約から読めるルール案：文字コード MS932、全項目をダブルクォートで囲む、改行 CRLF、NULL は空文字、ファイル名は機能ID_yyyyMMddHHmmss.csv、共通部品 CsvUtils。steering のどこに書くかを決める。 | 質問：steering に CSV 規約を足すか、pbi の公開契約（CsvUtils）を正とするかは人の判断 | 確認済み |  |  |
| 10 | design-rule-gap-detection | 業務のあいまい・不足 | 要判断 | 710e298d8264eaa9 | 610e05342e03f3e9 | specs/application-status-search/design.md § ドメインモデル / 社外ユーザー（ほか 2 design・docs/code-design.md 表示順 10） | P71 のキー3 | P71 のキー3 を 3 design は権限区分と読むが steering は「グループ」 | steering/security.md『所有権・エンティティ境界』は「P71 のキー3 がログインユーザーのグループ」と書く。application-status-search（社外ユーザー）、property-basic-info（826 行付近。「steering の『ログインユーザーのグループ』は、この権限区分（WTZ/CODE/C05）」と解釈を記す）、issue-request（『社外ユーザーの判定』。「requirements の『ログインユーザーのグループ』は権限区分」）はいずれも権限区分をキー3 にする。security.md の AuthContext は『所属グループ（グループID…）』と権限区分を別項目に挙げ、同じ節の画面表示の行は『P71 の G6』とも書くため、steering の文言がどちらとも読める。docs/code-design.md 表示順 10 は design の読み（権限区分）に合わせている。影響する design の洗い出しが必要。 | 選べる案：（1）security.md を『権限区分（Kengen_Kbn）』に直す（2）design を『グループ』に直す。 | 差戻し：ルールの持ち主は Phase 2（steering）。粒度不足で design ごとに解釈している | 確認済み |  |  |
| 11 | steering-conformance | 業務のあいまい・不足 | 要判断 | 9e7b65cdb1504d9e | e66a2c465689398f | docs/code-design.md § コード定義一覧 / 表示順 2〜5・9 | コード値 | 形式が「design に記載なし」で、TWTZM040 の個別の値が code-design に無い | steering/database.md『関連ドキュメント』は code-design を「TWTZM040・TWTZM050 の個別の値」の置き場と定める。表示順 2〜5・9 の形式欄は「コード（値の組み立ては design に記載なし）」とし、値を載せていない。application-status-search design『補足資料』が「本書の正」とする _handoff/phase5-application-status-search-conditions.md には値がある（P26 のキー3 001〜005、P27 の 01 下書き〜07 完了、P28 の 00 未起案〜05 承認済、P29 の 1 稟議依頼・2 再製本依頼）。表示順 1 では '06' だけが載っている。 | 選べる案：（1）上流資料の値を形式欄に載せる（2）値は TWTZM040 と各 design が持つので本書は識別だけを持つと範囲注記に書く。 | 質問：steering の置き場の定めと本書の単位の宣言が食い違うため、どちらに合わせるか人の判断 | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 7 | Phase 5 design（specs/property-basic-info/design.md の WTG-100018 の記述） | pbi design が WTG-100018 を既存と書き、application-status-search design は新規と書くため（upstream-carryover の未修正） |
| 8 | Phase 2 steering（tech.md） | 全 7 design が開発端末 JDK 1.8 で steering と食い違い、steering に扱いが無いため |
| 9 | Phase 2 steering（tech.md ほか） | CSV 出力規約を 3 design が繰り返し、steering に規則が無いため（人の判断で差戻し先を確定） |
| 10 | Phase 2 steering（security.md） | P71 のキー3 の定義が「グループ」と権限区分で読み分けられているため |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T21:30:03+09:00 |  |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 1 | 修正 | AI 推奨を採用: 対応表は上流資料にあり、新しい業務の事実は要らない | masato-teramoto | 2026-10-09T21:30:22+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 3 | 修正 | AI 推奨を採用: design に書かれた事実を転記するだけで、新しい業務の事実は要らない | masato-teramoto | 2026-10-09T21:30:27+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 4 | 修正 | AI 推奨を採用: design の記述を反映するだけ | masato-teramoto | 2026-10-09T21:30:31+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 5 | 修正 | AI 推奨を採用: design の位置づけで解消できる | masato-teramoto | 2026-10-09T21:30:35+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 6 | 修正 | AI 推奨を採用: 上流の事実に合わせて注記するだけ（PK の描き方を変えるなら質問） | masato-teramoto | 2026-10-09T21:30:39+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 2 | 対応せず進める | Phase 6 は application-status-search 分のみ。推奨が質問のため対象外とする（ユーザー指示） | masato-teramoto | 2026-10-09T21:30:43+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 7 | 対応せず進める | 差戻し先が他 feature の design（pbi）のため対象外とする（ユーザー指示：他機能には一切手をつけない） | masato-teramoto | 2026-10-09T21:30:47+09:00 | 対象外 |  | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 8 | 対応せず進める | 差戻し先が Phase 2 steering・他 design のため対象外とする（ユーザー指示） | masato-teramoto | 2026-10-09T21:30:51+09:00 | 対象外 |  | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 9 | 対応せず進める | 推奨が質問のため対象外とする（ユーザー指示） | masato-teramoto | 2026-10-09T21:30:55+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 10 | 対応せず進める | 差戻し先が Phase 2 steering のため対象外とする（ユーザー指示） | masato-teramoto | 2026-10-09T21:31:00+09:00 | 対象外 |  | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 1 | 11 | 対応せず進める | 推奨が質問のため対象外とする（ユーザー指示） | masato-teramoto | 2026-10-09T21:31:04+09:00 | 対象外 |  |  |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 2 | 2026-10-09T21:35:31+09:00 | ①② | ["docs/code-design.md","docs/architecture/data-model.md","docs/architecture/system-overview.md"] | {"docs/code-design.md":"0a1460c08e0a03770cd1ab8d64eabce94e715dc78a2daa65f5079ba19d1a09f1","docs/architecture/data-model.md":"5fc65fbe02a565dfe37f4d35d358411599e5e9c860915c0c10920cdb024cd857","docs/architecture/system-overview.md":"38a399f5826db843fd546631d41c1745fd77128833cbdd79286994b402c73a57"} | 4 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | evidence-guard | 出典・根拠 | 軽微 | 1c074e58cfc7b8e3 | 1331e05069bc9a4c | docs/architecture/data-model.md § ER 図 / 本書での図の範囲 | PK＝ユニークキー（AK_…） | 「PK はユニークキー（AK_…）で主キー制約なし」の出典が無い | 区分：根拠なし（探した範囲は specs/application-status-search/design.md、requirements.md、steering/*.md）。docs の記述「図の `PK` はユニークキー（`AK_…`）を表し、主キー制約は持たない」。application-status-search の design の物理データモデル・ドメインモデルは TWTGM080 の自然キーを「会社コード＋申請No」と書くだけで、`AK_` も主キー制約の有無も書かない。steering/database.md にも `AK_` の規則は無い。この事実は他 feature（property-basic-info など）の design にしか無いと見られ、application-status-search の design には根拠が無い。図の説明に出典（持ち主の design の節）も書かれていない（前回 #6 の修正で追記された文）。 | 出典として持ち主の design の物理データモデルの節名を図の説明に添える。出典を示せないなら「PK は結合キーを示す記号。主キー制約の有無は持ち主の design に従う」に言い換える。 | 修正：事実は application-status-search の design に無く、出典を添えるか断定を弱めれば直せる | 確認済み |  |  |
| 2 | evidence-guard | 出典・根拠 | 軽微 | 3db6f099d199b660 | 1331e05069bc9a4c | docs/architecture/data-model.md § ER 図 / 本書での図の範囲 | Keikaku_Kichikyoku_No・Tsuban | 省略した連番列名 Keikaku_Kichikyoku_No・Tsuban の出典が無い | 区分：出典不明（探した範囲は specs/application-status-search/design.md、requirements.md、steering/*.md、_handoff の検索条件表）。docs は「`TWTGM140` の連番（`Keikaku_Kichikyoku_No`・`Tsuban`）、`TWTGM180` の審査回の列は…本図では描かない」と書く。application-status-search の design は TWTGM140 を「連番 1 の行」、TWTGM180 を「最新の審査回（`Shinsa_Count`）」と書くのみで、列名 `Keikaku_Kichikyoku_No`・`Tsuban` は一度も出さない（steering/database.md の命名規則の例に `Keikaku_Kichikyoku_No` があるだけで、TWTGM140 の列とは書かれていない）。TWTGM140 の列の帰属（連番を 2 列で持つこと）は他 feature の design にしか無い事実で、本書に出典が無い。TWTGM180 側の審査回の列名（design は `Shinsa_Count`）は書かれておらず、「TWTGM140 の連番（A・B）、TWTGM180 の審査回の列」の並びは、どの列がどの表か読み取りにくい。 | 列名を挙げるなら出典（TWTGM140 を所有する design の節）を添え、TWTGM180 の審査回は `Shinsa_Count`（application-status-search の design の記載）と書く。出典を示せなければ列名を外し「連番の列」とだけ書く。 | 修正：application-status-search の design の記述で直せる（出典を足すか列名を外す） | 確認済み |  |  |
| 3 | ssot-consistency | 文書間の参照 | 軽微 | 70f66423d858b220 | e922f392c85221e2 | docs/architecture/data-model.md § ドメイン境界（DB 観点） / 共通基盤（コードマスタ） | 共通基盤の帰属（ZMENUAUTH） | data-model は共通基盤に ZMENUAUTH を置くが system-overview の地図に無い | 両方の所在：data-model.md「共通基盤（コードマスタ）: `TWTZM040`・`ZMENUAUTH`（メニュー権限）」。system-overview.md の「ドメイン境界の地図」の subgraph「共通基盤（コードマスタ）」は E1[("TWTZM040")] だけで、ZMENUAUTH が無く、AS からの矢印も「区分値・件数の読み取り」だけ。data-model の同節は「まとまりの名前は system-overview の `## ドメイン境界の地図` と揃える」と書く。食い違いの種類：帰属の記述の不一致（二重定義ではなく、片方にだけ ZMENUAUTH がある）。前回 #4 の修正（ZMENUAUTH の追加）が system-overview 側に及んでいない。また、まとまりの名前が「（コードマスタ）」なのに、コードマスタではない ZMENUAUTH を含む。 | system-overview の共通基盤にも ZMENUAUTH を足す（AS→ZMENUAUTH は権限判定のためインターセプタ経由で、AS の design は行の登録だけと書くため図には描かない扱いでもよい）。または data-model 側の「共通基盤」の名前を「共通基盤（コードマスタ・メニュー権限）」にして両書で揃える。 | 修正：docs 内で名前と帰属を揃えれば直せる | 確認済み |  |  |
| 4 | format-conformance | 書式 | 軽微 | c4de7e5134a0309b | 4d301c7bc4f548db | docs/architecture/data-model.md § 主要エンティティ一覧 / ZMENUAUTH | ZMENUAUTH の概要の文末 | ZMENUAUTH 行の概要の文末が「登録するだけで」で途切れている | 概要欄が「…application-status-search は、メニュー「[WTG060]物件契約情報申請状況検索/一覧」の `PWTGO060` の行を登録するだけで」で終わり、文として閉じていない（前回 #4 の修正で追加された文）。あわせて同節「本書での扱い」は application-status-search を「どのテーブルも所有しない（読むだけ）」と書くが、ZMENUAUTH と TWTZM040 には行を登録・追加する旨が書かれており、「読むだけ」の意味（表の定義・実行時の書込みはしない、の意）が書かれていない（design は「表は作らず変えない」「データベースに書かない」と、移行方針の行の登録を別に書く）。 | 「…`PWTGO060` の行を登録するだけである（表の定義は持たない）」と閉じる。「読むだけ」は「表の定義を持たず、実行時に書かない（行の登録は移行で行う）」と書き添える。 | 修正：文を閉じる書き直しで足り、新しい業務の事実は要らない | 確認済み |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 2 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T21:40:50+09:00 |  |  |  |
| phase | 2 | 2 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T21:40:50+09:00 |  |  |  |
| phase | 2 | 3 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T21:40:50+09:00 |  |  |  |
| phase | 2 | 4 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T21:40:50+09:00 |  |  |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 1 | 1 | phase | 2 | system（自動）：再検査で再検出なし | 2026-10-09T21:40:50+09:00 |
| phase | 1 | 3 | phase | 2 | system（自動）：再検査で再検出なし | 2026-10-09T21:40:50+09:00 |
| phase | 1 | 5 | phase | 2 | system（自動）：再検査で再検出なし | 2026-10-09T21:40:50+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 3 | 2026-10-09T21:44:32+09:00 | ①② | ["docs/code-design.md","docs/architecture/data-model.md","docs/architecture/system-overview.md"] | {"docs/code-design.md":"0a1460c08e0a03770cd1ab8d64eabce94e715dc78a2daa65f5079ba19d1a09f1","docs/architecture/data-model.md":"332134ff13e1f434f905ef3279dea563981e7646b3ff533324842b7408423f0e","docs/architecture/system-overview.md":"69b3b24ed1a3e64237b41d8064c8ebff0d6c4cec66a71016746812ba961071ef"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 文書間の参照 | 軽微 | 29852f81afafbb73 | 67025925d49335c8 | docs/architecture/data-model.md § 主要エンティティ一覧 / TWTGM180 | 承認履歴の使い方（進捗の日数） | TWTGM180 の概要が進捗の日数を一覧の列のように読める書き方になっている | data-model の TWTGM180 行は「検索では最新の審査回の日時と比べ、一覧の起案日と進捗の日数（審査回 1 の申請依頼の行）に使う」と書く。specs/application-status-search/design.md（ドメインモデル『進捗の日数』）は、進捗の日数を検索条件であり「一覧・CSV には出さない」とし、審査回 1・審査権限 '01'・判定 '01' の行の Last_UpdatedDT で数える。一覧に出すのは起案日で、最新の審査回の審査権限 '01' の行を使う（一覧の 14 列の表）。docs の文は「一覧の起案日と進捗の日数」と続けて、進捗の日数も一覧の項目であるかに読め、括弧の「審査回 1」が起案日にも掛かるように読めて、design の最新の審査回との使い分けが伝わらない。docs の他の箇所に進捗の日数の記述は無く、system-overview にも一覧の列としての記述は無い。なお、今回確認した 2 回目の #1〜#4・前回未解消の #1-4（ZMENUAUTH）・#1-6（TWTGM080 の PK）の修正は、design（移行方針・移行対象ファイル一覧・ドメインモデル・DB レイアウト）と矛盾しないことを確認した。 | 概要を「検索では最新の審査回の日時と比べ、一覧の起案日（最新の審査回の審査権限 '01' の行）に使う。検索条件の進捗の日数（一覧・CSV には出さない）は審査回 1 の申請依頼の行で数える」の形に書き分ける。 | 修正：design に書かれた事実の言い分けだけで、新しい業務の事実は要らない | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase | 3 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T21:48:06+09:00 |  |  |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 1 | 4 | phase | 3 | system（自動）：再検査で再検出なし | 2026-10-09T21:48:06+09:00 |
| phase | 1 | 6 | phase | 3 | system（自動）：再検査で再検出なし | 2026-10-09T21:48:06+09:00 |
| phase | 2 | 1 | phase | 3 | system（自動）：再検査で再検出なし | 2026-10-09T21:48:06+09:00 |
| phase | 2 | 2 | phase | 3 | system（自動）：再検査で再検出なし | 2026-10-09T21:48:06+09:00 |
| phase | 2 | 3 | phase | 3 | system（自動）：再検査で再検出なし | 2026-10-09T21:48:06+09:00 |
| phase | 2 | 4 | phase | 3 | system（自動）：再検査で再検出なし | 2026-10-09T21:48:06+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 4 | 2026-10-09T21:51:14+09:00 | ①② | ["docs/code-design.md","docs/architecture/data-model.md","docs/architecture/system-overview.md"] | {"docs/code-design.md":"0a1460c08e0a03770cd1ab8d64eabce94e715dc78a2daa65f5079ba19d1a09f1","docs/architecture/data-model.md":"7ba47e6faa19d462b726efd176282948c802980f6e719f1fd9db407d439728e4","docs/architecture/system-overview.md":"69b3b24ed1a3e64237b41d8064c8ebff0d6c4cec66a71016746812ba961071ef"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 3 | 1 | phase | 4 | system（自動）：再検査で再検出なし | 2026-10-09T21:54:08+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 4 | docs/code-design.md | masato-teramoto | 2026-10-09T21:54:34+09:00 | 0a1460c08e0a03770cd1ab8d64eabce94e715dc78a2daa65f5079ba19d1a09f1 |
| phase | 4 | docs/architecture/data-model.md | masato-teramoto | 2026-10-09T21:54:34+09:00 | 7ba47e6faa19d462b726efd176282948c802980f6e719f1fd9db407d439728e4 |
| phase | 4 | docs/architecture/system-overview.md | masato-teramoto | 2026-10-09T21:54:34+09:00 | 69b3b24ed1a3e64237b41d8064c8ebff0d6c4cec66a71016746812ba961071ef |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| phase | 1 | 2 | 対応せず進める | Phase 6 は application-status-search 分のみ。推奨が質問のため対象外とする（ユーザー指示） | phase | 4 |
| phase | 1 | 7 | 対応せず進める | 差戻し先が他 feature の design（pbi）のため対象外とする（ユーザー指示：他機能には一切手をつけない） | phase | 4 |
| phase | 1 | 8 | 対応せず進める | 差戻し先が Phase 2 steering・他 design のため対象外とする（ユーザー指示） | phase | 4 |
| phase | 1 | 9 | 対応せず進める | 推奨が質問のため対象外とする（ユーザー指示） | phase | 4 |
| phase | 1 | 10 | 対応せず進める | 差戻し先が Phase 2 steering のため対象外とする（ユーザー指示） | phase | 4 |
| phase | 1 | 11 | 対応せず進める | 推奨が質問のため対象外とする（ユーザー指示） | phase | 4 |
