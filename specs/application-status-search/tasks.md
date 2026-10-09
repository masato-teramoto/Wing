---
feature: application-status-search
execution_mode: feature
status: draft
updated_at: 2026-10-09T23:57:47+09:00
---

# 実装計画

> このファイルは **「いつ・どの順で作るか」** を確定させる文書である。各タスクが `_Requirements:` と `_Design:` で要件・設計を参照することで、実装者が `design.md` 全体を読まずに作業できる状態にする。\
> _分担_: 同一 feature の `design.md` が `status: approved` になるまで着手しない。本ファイルが `approved` になるまで実装に進まない。`approved` は人間が付ける（エージェントは付けない）。

> _書き方_: 着手前に計画を書き切る。あとから書き足すのは、進めて分かったことだけにする。

## 注記表記の早見表

> 各タスクに付ける注記の意味を定める節。表記そのものは機械が読むため、形を変えない。

> _書き方_: _Depends: …_ に書くのはタスクの通し番号（`7` のような整数）で、受け入れ基準ID（`1.2` のような形）とは形が違う。取り違えないよう確認する。

| 表記 | 意味 |
|---|---|
| _Requirements: …_ | このタスクが満たす受け入れ基準ID。複数は `,` で区切る |
| _Design: ## …_ | 参照する `design.md` の節。見出しを `##` から書き、英語併記は省く |
| _Boundary: …_ | このタスクが触るコンポーネント名。`design.md` の `### コンポーネント一覧（Summary）` にある名前を書く |
| _Depends: …_ | 先に終わっている必要があるタスクの通し番号 |

## 本計画の前提と規約（画面設計工程の成果物の扱い）

> 本 feature の UI タスクは、AIDD 本フローの外で作られた画面設計工程（ds_mock）の成果物を、利用者の明示指示で入力・規約として取り込む。本節はタスクではない。タスクの完了条件と実装の進め方を縛る前提だけを書く。

### 対象の範囲

- 対象 feature は `application-status-search` だけ。他の feature（property-basic-info・issue-request・issue-request-tutorial・print-report・contract-info-import・contract-info-download）の tasks・design は作らず、触らない。
- 依存先の公開契約は design.md に書かれた範囲で扱う。使うのは、property-basic-info の WTG 申請状態サービス（`getExternalScope`）・`CsvUtils`・`/wtg070/pushApplicationNo`・`/wtg070/returnList`・`/wtg070/deleteShinse` と、issue-request の `TWTGM100` の DB レイアウト（`specs/issue-request/design.md`）である。これらの実装タスクは本計画に含めない。存在の確認だけをタスク 1 で行う。
- design.md の移行方針にある、コードマスタ `WTZ/PARAM/P01` のこの画面の行と、メニュー・`ZMENUAUTH`（`PWTGO060`）の行の登録は「ほかのコードマスタの行・ほかの画面と同じ扱い」で行うため、本計画のタスクにしない。Service の事前条件（`P01` にこの画面の行、`P02` に ALL の行がある）として扱う。

### 画面設計工程の前提ゲート（担体の値で確認した結果）

- `STYLEGUIDE.md` §1-2 改訂履歴の最新行（版 0.3.10・2026-10-09）の `確定` は「済」（by: toshiya-fukunaga）。
- `.aidd/screen-design/_app-shell/screen-map.md` の `features[]` の行ごとの `confirmed` は、application-status-search・_app-shell とも記入済み（by: toshiya-fukunaga・2026-10-09T21:52+09:00）。
- 画面設計書の `status` は、`.aidd/screen-design/application-status-search/screen-spec.md` と `.aidd/screen-design/_app-shell/screen-spec.md` がどちらも `confirmed`。
- `mockup-manifest.json` の `checks` は、パレット検査・動線検査とも pass（両 feature）。`viewed` は両 feature とも記入済み。
- `.aidd/screen-design/README.md` の状態欄と担体の値は食い違っていない。食い違った場合は担体を正とする。

### UI タスクの単位と範囲

- UI タスクの単位は、画面設計書 §1 の画面 ID。本 feature の所有画面は `S-01`（物件契約情報申請状況検索/一覧）の 1 つ。`_app-shell:S-01`・`_app-shell:S-02` の参照行は所有 feature（_app-shell）側の画面なので、本 feature の UI タスクにしない。
- シェル（ヘッダ・ヘッダのリンク・ナビ）と、入口（メニュー）・システムエラーは、feature ごとではなく共通タスク 1 本（タスク 13）にまとめる。`_app-shell` は擬似 feature で `tasks.md` を持たないため、本 feature の `tasks.md` に含める。参照先は `.aidd/screen-design/_app-shell/screen-map.md` の §4 と `.aidd/screen-design/_app-shell/screen-spec.md`。
- 画面設計書 §4 の「分母から外した受け入れ基準」は、application-status-search・_app-shell ともに 0 件。UI タスクにならない受け入れ基準は無い。
- 状態管理（検索条件のセッション）・API 接続・ルーティング（Controller）は UI タスクに含めず、通常の実装タスクとして同じ章（画面）に並べる（タスク 14・15）。
- バリデーションと API 契約の正は design.md。画面設計書はエラーコード・契約名で参照するだけなので、実装タスクは design.md を併読する前提とする。

### feature の着手順

- 画面マップ §3 の順は、入口 `_app-shell:S-01`（メニュー）から `application-status-search:S-01` への分岐、全画面からヘッダのリンク「MENU」で入口へ、例外でシステムエラーへ、である。着手順は、共通タスク 13（_app-shell）の後に本 feature の画面タスクとする。
- `mockup-manifest.json` の `cross_feature_links[]` の `pending` は、application-status-search で 1 件（申請No のリンク → 物件基本情報登録変更画面）。_app-shell は 0 件。`checks.links` の `pending` は両 feature とも 0 件（ヘッダのリンク「MENU」の 11 件は _app-shell の生成で解消済み）。
- 上の 1 件は、行き先の property-basic-info が画面マップ §1 で UI の有無が未判定のため `pages/` が無く、画面マップ §3 にも行が無い（画面マップ §6-2 #2）。本 feature は `forward:/wtg070/pushApplicationNo` までを実装し、行き先の画面の見た目は扱わない。

### 実装工程への規約

- mockup の HTML は流用しない。JS なし・固定ダミー値で、画面設計側が再生成すると手を入れた分が消えるため。
- `pages/tokens/styleguide.css` は開かない。実装が参照する見た目の正は、案件ルート直下の `STYLEGUIDE.md` と `styleguide.css` である。
- 受け入れ単位は「画面 × 状態」。状態名は画面設計書（`screen-spec.md` §3-x-5）と同じにし、状態の一覧は `mockup-manifest.json` の `pages[]` で数える。状態を足す・減らす判断は実装側で行わない。
- 部品・変数が足りないときは、コードに色・px などの生値を書かず、案件ルート直下の `STYLEGUIDE-backlog.md` に申告する。申告先はこの 1 か所とする。
- 画面の項目・状態・文言が画面設計書と違うときは `screen-spec.md` を改訂する（コード側だけを直さない）。画面の切り出し・遷移・ナビが違うときは `screen-map.md` を改訂する。要件が違うときは上流の変更管理に回す。いずれも実装側では決めない。
- 画面に出す文言は画面設計書 §3-x-6 のとおりにする。エラーのメッセージは、エラーコードから `messages.properties` の文言を引く。`mockup-manifest.json` の `drafted_wording[]` の起草文（`DS-100024`・`DS-100025`）は実装の正としない。
- 実装コードの生値検査（hex 色・px の直書きがないこと）は画面設計工程の検査の対象外なので、本計画のタスクの完了条件で行う。

### 但し書き（未決のまま残す事項）

- `_app-shell/screen-spec.md` §5-4 #1（システムエラー画面の「種別」の値とメッセージ文言が steering に無い。宛先は steering）: 画面設計書 §3-2-6 の仮置き（種別「システムエラー」、メッセージ「処理を続けられませんでした。お手数ですが、メニューからやり直してください。」、コード `GEF-000000`）のまま、仮置きとして実装する（タスク 13）。steering で確定した後に画面設計書を改訂し、その改訂に合わせて直す。
- 同 §5-4 #2（入口のお知らせ欄。宛先は steering）: 置かないまま実装する。
- 同 §5-4 #3（入口のリンクを権限で出し分けるか。宛先は steering）: 出し分けないまま、全項目を表示する。
- `application-status-search/screen-spec.md` §5-4 の 9 件（ボタン名・確認ダイアログの形・ローディングの有無・`GEF-000025` など実文言の記載が無い件・ラベル「ｽﾃｰﾀｽ」・「検索条件」見出し・ダミー値）は、画面設計書（confirmed）の記載のまま実装する。宛先側で決まったら画面設計書が改訂される。
- `STYLEGUIDE-backlog.md` の未処理 6 件（SGB-11・SGB-12・SGB-16・SGB-17・SGB-18・SGB-19）は本計画のスコープ外とする。このうち本 feature の mockup の `missing[]` にある 4 件（候補つきの入力欄、切り詰めた値の全文を出すツールチップ、月次カレンダーの月送りと曜日見出しの文言、Dialog の閉じるのラベル）は、部品が無いため mockup と同じく描かない。生値で補わず、タスクの完了条件にも含めない。

### 検証の前提

- 自動テストは JUnit 4.12 と spring-test で書き、Mapper などの代わりは手書きの代替クラスにする（`steering/tech.md` の `## テスト方針`、design.md の `## テスト戦略`）。実行は `mvn -f wing/pom.xml test -Dtest=クラス名`（`steering/tech.md` の `## 共通コマンド`。この端末には Java と Maven が無く、同ファイルでも未確認のコマンド）。
- 開発端末の JDK は 1.8（`-source`/`-target` 1.7）で、本番の JDK 1.7 とは異なる（design.md の `### 技術スタック`）。
- Oracle を使う確認（Mapper XML の SQL を実行した結果、営業日数、ページング、件数の上限）は開発端末では動かせないため、総合テスト（試験仕様書）で行う（design.md の `## テスト戦略`）。Mapper XML のタスクは、SQL の書き方（バインド変数・LIKE の逃がし・並び・括弧）を文面で確認する範囲までを完了条件にする。
- 新規ファイルは Checkstyle（`kccs-checkstyle-2.0.1_bugfix`）に通し、Javadoc とファイル冒頭のヘッダを書く（`steering/tech.md` の `## コード規約`）。

## タスク一覧

> 実装を順序付きのタスクに分解する節。

> _書き方_: 章立ては着手順の目安で、上から順に前提が減るように並べる（基盤・準備 → ドメイン / ビジネスロジック → API / 入口 → データアクセス / 永続化 → UI / 表示 → 横断テスト・観測 → ドキュメント / クリーンアップ）。\
> 1 タスクは 1 人が続けて終えられる大きさにする。タスクには通し番号を振り、章をまたいで移動しても番号を変えない。\
> 各タスクには、外から確認できる完了条件を必ず 1 行以上書く（例:「テストが成功する」「`/health` が 200 を返す」）。

### 基盤・準備

- [ ] 1 依存先と開発環境の利用可能性を確認する（変更を加えない確認）
  - 本 feature が使う依存先が実装済みで、開発端末で組み立てられることを、変更を加えずに確認する。確認の対象は、WTG 申請状態サービスの `getExternalScope`、`CsvUtils`（orangesignal-csv 2.2.1）、`/wtg070/pushApplicationNo`、既存の共通基盤（`ServiceBase` の `validateSearchLimitCount`、`CodeMstService`、`StringUtils.escapeSQLforLike`、共通部品 `common/pager`・`common/pageCount`・`common/emptyMsg`）、`TWTGM100` の列（`specs/issue-request/design.md` の DB レイアウト）。
  - 観測可能な完了条件: 上記の各クラス・メソッド・口・列が、ソースまたは設計書のどこに在るか（ファイルパスと行）を一覧にして実装メモに記録している。1 つでも無ければ本 feature の実装に着手せず、先行 feature の実装が先であることを実装メモの既知の制約に記録して止める。
  - 観測可能な完了条件: `mvn -v` が JDK 1.8 と Maven 3.3.9 以上を示し、`mvn -f wing/pom.xml package` が終了コード 0 で完了する。
  - _Requirements: —_
  - _Design: ## 責務境界、## アーキテクチャ_
  - _Boundary: 申請状況検索一覧 Service_
  - _Depends: なし_

### データアクセス

- [ ] 2 検索条件・一覧行の bean と Mapper インターフェースをテストから作る
  - `Pwtgo060Form`・`Pwtgo060CondInfo`（検索条件 38 項目）・`Pwtgo060SearchCond`（SQL に渡す条件）・`Pwtgo060SearchInfo`（一覧と CSV の 1 行。`@CsvEntity`、14 項目に `@CsvColumn`）と、`Pwtgo060Mapper` のインターフェース（件数・表示ページの行・CSV の全件・取込中の確認の 4 つ）を作る。更新者の氏名は一覧・CSV の項目に入れない。
  - テスト `Pwtgo060SearchInfoTest` を先に作り、意図した失敗（RED）を確認してから実装する。テストは、`Pwtgo060CondInfo` の項目が検索条件の表の No.1〜38 と同数（38）であること、`Pwtgo060SearchInfo` の `@CsvColumn` の見出しが `申請No,依頼内容,ｽﾃｰﾀｽ,状態,稟議ﾊﾞｰｺｰﾄﾞNo,基地局番号,基地局名,案件小ｸﾞﾙｰﾌﾟ,起案会社名,ｴﾘｱ,起案担当者,起案日,発注希望日,施策` の順で 14 個であること、更新者の氏名の項目が無いことを確認する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060SearchInfoTest` で、同一タスク内の RED から GREEN を確認し、全件が成功する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml package` が終了コード 0 で完了する。
  - _Requirements: 1.1, 3.1_
  - _Design: ## ファイル配置計画、## データモデル_
  - _Boundary: 申請状況検索一覧 Mapper_
  - _Depends: 1_

- [ ] 3 Mapper XML の共通結合と、文字・コード・社外範囲の条件をテストから作る
  - `Pwtgo060Mapper.xml` に、件数の SQL の土台となる共通の結合（`TWTGM080` に `TWTGM100`・`TWTGM140`（全部の契約局の行）・`TWTGM180`（最新の審査回）を外部結合し、申請No でまとめる）と、前方一致（申請No・稟議バーコードNo・基地局番号・発送書類名）・部分一致（基地局名・更新者名・所属①②・起案担当者・案件小グループ）・完全一致（エリア・審査フェーズ・状態・依頼内容・施策・起案会社・押印種別・転貸借の契約種別）の条件と、社外ユーザーの範囲（会社コードの条件と、`( 起案会社コード ＝ 自社 OR 登録者 ＝ 本人 )` を括弧でくくって AND）を書く。比べる列は design.md の検索条件の表（補足資料）に従う。
  - テスト `Pwtgo060MapperXmlTest` を先に作り、RED を確認してから実装する。テストは、Mapper XML を MyBatis の XML 解析で読み込めること、値が `#{}` だけで渡り `${` が無いこと、前方・部分一致の LIKE が `ESCAPE '/'` を伴うこと、社外範囲が括弧でくくられていること、契約局情報の比較が全行を対象にした結合（1 行目に限らない）であることを確認する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060MapperXmlTest` で、同一タスク内の RED から GREEN を確認し、全件が成功する。
  - 観測可能な完了条件: `grep -n '\${' wing/src/main/resources/jp/co/kccs/wt/function/wtg/wtg060/Pwtgo060Mapper.xml` が 0 件である。
  - 観測可能な完了条件: Oracle での実行結果は総合テスト（試験仕様書）で確認する対象として、本タスクの範囲外であることを実装メモに記録している。
  - _Requirements: 1.2, 1.3, 1.4, 1.7_
  - _Design: ## データモデル、## 追加検討事項_
  - _Boundary: 申請状況検索一覧 Mapper_
  - _Depends: 2_

- [ ] 4 Mapper XML の日時・日付・進捗の日数の条件をテストから作る
  - `Pwtgo060Mapper.xml` に、起案日時・稟議承認日・申請日時・確認日時（最新の審査回の承認履歴の判定 01・04・02・03 の `Last_UpdatedDT` を種類ごとの EXISTS で比べ、両端を含み片方だけも受ける）、初回支払日（`First_Pay_Day1`〜`4` のどれかが From 以上、どれかが To 以下を別々に判定）、発送希望日（`Hasso_Kibo_Date` を yyyyMMdd の文字列で比べる）、進捗の日数（審査回 1・審査権限 '01'・判定 '01' の行の日付から今日までの営業日数。`WTI/CODE/C06` の休日を会社コードごとに引いて除く。「以上」「以下」の切り替え）の条件を書く。
  - テスト `Pwtgo060MapperXmlTest` に、日時の 4 種類が種類ごとの EXISTS で書かれていること、承認履歴の審査回が MAX で絞られていること、初回支払日の From と To が別々の判定であること、休日が `C06` から引かれていること、`${` が無いことを確認するケースを先に足し、RED を確認してから実装する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060MapperXmlTest` で、同一タスク内の RED から GREEN を確認し、全件（タスク 3 の分を含む）が成功する。
  - 観測可能な完了条件: `grep -n '\${' wing/src/main/resources/jp/co/kccs/wt/function/wtg/wtg060/Pwtgo060Mapper.xml` が 0 件である。
  - _Requirements: 1.5_
  - _Design: ## データモデル_
  - _Boundary: 申請状況検索一覧 Mapper_
  - _Depends: 3_

- [ ] 5 Mapper XML の一覧の取得・件数・並び・CSV の全件・取込中の確認をテストから作る
  - `Pwtgo060Mapper.xml` に、件数の SQL、表示ページの行を取る SQL（`ROW_NUMBER() OVER (ORDER BY Application_No DESC)`）、CSV の全件の SQL（画面の検索と同じ条件・絞り込み・上限件数）、取込中（`JOTAI_KBN` が '06'）の確認の SQL を書く。選ぶ列は一覧の 14 項目の元（名称は `TWTZM040` の `P28`・`P27`・`P30`・`C01`・`M11`・`P35` を外部結合して引く。稟議バーコードNo は契約局情報の連番 1 の行を別に結合する。再申請の判定に使う審査回の最大値と、契約局の行数も選ぶ）。
  - テスト `Pwtgo060MapperXmlTest` に、並びが申請No の降順だけであること、4 つの文が定義されていること、14 項目の元の列が選ばれていること、連番 1 の契約局の行が別に結合されていること、`${` が無いことを確認するケースを先に足し、RED を確認してから実装する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060MapperXmlTest` で、同一タスク内の RED から GREEN を確認し、全件が成功する。
  - 観測可能な完了条件: `grep -n '\${' wing/src/main/resources/jp/co/kccs/wt/function/wtg/wtg060/Pwtgo060Mapper.xml` が 0 件である。
  - _Requirements: 2.1, 2.4, 2.8, 3.3_
  - _Design: ## データモデル、## コンポーネントとインターフェース_
  - _Boundary: 申請状況検索一覧 Mapper_
  - _Depends: 4_

### ドメイン / ビジネスロジック

- [ ] 6 画面の初期値と社外ユーザーの固定値（初期表示）をテストから作る
  - `Pwtgo060Service` の `initDisplay` を、テストから作る。社内ユーザーはどの項目も空、時刻の From は 00:00・To は 23:59、進捗検索(選択)は「以上」。社外ユーザー（`P71` のログインの権限区分の行の文字項目1 が '1'）は、起案会社に自社の会社名（`P71` の文字項目2 をキー3 にした `P26` の名称）を入れて変更不可、所属①②は空で変更不可、進捗検索(日数)・(選択)を出さない。`P71` の行が無い、または文字項目1 が '1' 以外なら社内。コンボの選択肢（エリア `C01`・審査フェーズ `P28`・状態 `P27`・依頼内容 `P29`・施策 `P30`・起案会社 `P26`・押印種別 `P31`・転貸借の契約種別 `P53`・進捗(選択)）を返す。
  - テスト `Pwtgo060ServiceTest` の `initDisplay` で始まるケースを先に作り（コードマスタ・Mapper の代わりは手書きの代替クラス）、RED を確認してから実装する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060ServiceTest#initDisplay*` で、同一タスク内の RED から GREEN を確認し、社内・社外・`P71` の行なしの各ケースを含めて全件が成功する。
  - _Requirements: 1.1, 1.6_
  - _Design: ## データモデル、## コンポーネントとインターフェース_
  - _Boundary: 申請状況検索一覧 Service_
  - _Depends: 2_

- [ ] 7 検索と CSV の入力チェックをテストから作る
  - `Pwtgo060Service` の入力チェック（`checkXxx`）を、`BindingResult.rejectValue` にエラーを積む方式でテストから作る。検索と CSV で同じチェックを使う。どの項目も必須にしない。日付・時刻・進捗の日数だけ形式を検査し、桁は検索条件の表のバイト数（申請No 11・稟議ﾊﾞｰｺｰﾄﾞNo 25・基地局番号 9・基地局名 120・更新者 20・所属①② 100・起案担当者 100・発送書類名 256・案件小ｸﾞﾙｰﾌﾟ 50）で検査する。文字種は検査せず、範囲の開始が終了より後でも検査しない。使うキーは新しく作らず、稟議承認日・初回支払日・発送希望日の日付は `WTG-000003`、起案日時・申請日時・確認日時の日付は `GEF-000025`、時刻は `WTL-000007`、進捗検索(日数)（半角数字 2 桁）は `GEF-000014`、文字の桁は `GEF-000003`。
  - テスト `Pwtgo060ServiceTest` の `check` で始まるケースを先に作り、RED を確認してから実装する。ケースは、すべて空で通る、各キーが積まれる誤り（実在しない日付・時刻の形式違い・進捗の日数が全角や 3 桁・桁超過）、開始が終了より後でも通る、文字種の誤り（申請No に記号）でも通る、を含める。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060ServiceTest#check*` で、同一タスク内の RED から GREEN を確認し、全件が成功する。
  - 観測可能な完了条件: `git diff --stat -- wing/src/main/resources/messages.properties` に、本タスクによる変更が無い（新しいキーを作らない）。
  - _Requirements: 1.1, 4.1_
  - _Design: ## 機能固有のエラー処理、## データモデル_
  - _Boundary: 申請状況検索一覧 Service_
  - _Depends: 2_

- [ ] 8 検索条件から SQL の条件を組み立てる（一致の仕方・日時の範囲）をテストから作る
  - `Pwtgo060CondInfo` から `Pwtgo060SearchCond` を組み立てる処理を、テストから作る。空の項目は条件に入れず、入れた項目だけを AND でつなぐ。前方・部分一致の値は `StringUtils.escapeSQLforLike` で `%`・`_` を逃がす。日時の From に秒 00、To に秒 59 を付け、稟議承認日は From に 00:00:00、To に 23:59:59 を付ける。日付があって時刻が空なら、その端を条件から外す。発送希望日は「/」を除いた yyyyMMdd にする。進捗の日数は「以上」「以下」の選択に従い、日数が空なら条件にしない。依頼内容は選んだ行の名称（稟議依頼・再製本依頼）で比べる。
  - テスト `Pwtgo060ServiceTest` の `buildCond` で始まるケースを先に作り、RED を確認してから実装する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060ServiceTest#buildCond*` で、同一タスク内の RED から GREEN を確認し、空の項目が入らない・`%` と `_` が逃がされる・秒の付き方・時刻が空の端が外れる・片方だけの範囲・進捗の「以上」「以下」の各ケースを含めて全件が成功する。
  - _Requirements: 1.2, 1.3, 1.4, 1.5_
  - _Design: ## データモデル_
  - _Boundary: 申請状況検索一覧 Service_
  - _Depends: 2_

- [ ] 9 社外ユーザーの範囲と、画面から送られた値の無効化をテストから作る
  - 社外ユーザーのとき、`Pwtgo060Service` が起案会社・所属①②・進捗検索(日数)・(選択) の値を空として扱って条件に入れず、WTG 申請状態サービスの `getExternalScope` で得る範囲（自社の会社コードの起案会社、または本人が登録した申請）を括弧付きで足すようにする。範囲はログインユーザーから毎回作り、画面から送られた値に頼らない。社内ユーザーは会社コードの条件だけを付ける。
  - テスト `Pwtgo060ServiceTest` の `externalScope` で始まるケースを先に作り（`getExternalScope` の代わりは手書きの代替クラス）、RED を確認してから実装する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060ServiceTest#externalScope*` で、同一タスク内の RED から GREEN を確認し、社外ユーザーが起案会社・所属・進捗の値を送っても条件に入らない・範囲の条件が付く・社内ユーザーは会社の条件だけ、の各ケースを含めて全件が成功する。
  - _Requirements: 1.6, 1.7_
  - _Design: ## データモデル、## 追加検討事項_
  - _Boundary: 申請状況検索一覧 Service_
  - _Depends: 8_

- [ ] 10 一覧の 1 行の値の形（再申請・他n局・エリア・切り詰め）をテストから作る
  - Mapper が返した元の値から、一覧の 14 項目の値の形を作る処理を、テストから作る。審査フェーズは名称で、審査回の最大値が 2 以上なら後ろに「(再申請)」。基地局番号・基地局名は、単独複数局ﾌﾗｸﾞが "0" 以外で契約局の行数が 2 以上のとき後ろに「他（行数－1）局」（"0"・行数 0〜1 では付けない）。エリアは「コード:名称」（コードが空なら空）。案件小グループは M11 の名称、無ければ P35 の名称、無ければ `Sonota1_Freeform`。日付は YYYY/MM/DD。状態が取込中（`JOTAI_KBN` が '06'）の行は申請No をリンクにしない印を付ける。基地局名 16・案件小グループ 15・起案会社名 22・エリア 15・起案担当者 10 の表示バイト数で切った値と、全文の両方を持たせる（CSV は切らない）。バイト数の数え方は既存共通部品 `StringUtils`（`lengthB`）に合わせる。発行依頼書・契約局情報・承認履歴が無い申請の列は空にする。
  - テスト `Pwtgo060ServiceTest` の `rowValue` で始まるケースを先に作り、RED を確認してから実装する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060ServiceTest#rowValue*` で、同一タスク内の RED から GREEN を確認し、「(再申請)」の有無・「他n局」の付く場合と付かない場合・エリア・案件小グループの名称の順・日付の形・切り詰めと全文・取込中の印・外部結合で空の列、の各ケースを含めて全件が成功する。
  - _Requirements: 2.1, 2.2, 2.3, 2.8_
  - _Design: ## データモデル_
  - _Boundary: 申請状況検索一覧 Service_
  - _Depends: 2_

- [ ] 11 検索結果の CSV 出力をテストから作る
  - `Pwtgo060Service` の `outputCsv` を、テストから作る。画面の一覧と同じ 14 列・同じ値の形（切り詰めない）を、`CsvUtils.save(list, stream, "MS932", CsvUtils.defaultCsvConfig(), new CsvEntityListHandler<>(Pwtgo060SearchInfo.class))` で書く。全項目をダブルクォートで囲み（値の中の " は ""）、改行は CRLF、NULL は空文字。ファイル名は `WTG060_yyyyMMddHHmmss.csv`（出力した時刻）。条件は押した時点の画面の入力で、絞り込み（社外ユーザーの範囲）と上限件数は検索と同じにし、警告件数の確認は出さない。検索結果が 0 件、または上限件数を超える場合は、要素が null の 1 つのリストを渡して見出し行だけにする。入力チェックのエラーがあれば CSV を出さず、エラーを積む。更新者の氏名は出力しない。
  - テスト `Pwtgo060ServiceTest` の `outputCsv` で始まるケースを先に作り（Mapper の代わりは手書きの代替クラス）、RED を確認してから実装する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060ServiceTest#outputCsv*` で、同一タスク内の RED から GREEN を確認し、出力のバイト列を MS932 で読み戻して 1 行目が見出し 14 列と一致する・全項目がダブルクォート付き・改行が CRLF・ファイル名が `WTG060_` に 14 桁の数字と `.csv` が続く形・0 件と上限超えで見出し行だけ・入力エラーで出力しない、の各ケースを含めて全件が成功する。
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1_
  - _Design: ## データモデル、## コンポーネントとインターフェース_
  - _Boundary: 申請状況検索一覧 Service_
  - _Depends: 5, 7, 8, 9, 10_

- [ ] 12 取込中の申請の確認と、メッセージ WTG-100018 の追加をテストから作る
  - `Pwtgo060Service` の `checkImporting`（会社コード・申請No を受け、取込中なら `WTG-100018` を `BindingResult` に積む）と、`wing/src/main/resources/messages.properties` への `WTG-100018`（文言「取込処理中のため登録画面へ遷移できません」。種別 Warning）の追加を、テストから作る。
  - テスト `Pwtgo060ServiceTest` の `checkImporting` で始まるケースと、`messages.properties` に `WTG-100018` が在って文言が上のとおりであることを確認するケースを先に作り、RED を確認してから実装する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060ServiceTest#checkImporting*` で、同一タスク内の RED から GREEN を確認し、取込中でエラーが積まれる・取込中でなければ積まれない、の各ケースを含めて全件が成功する。
  - 観測可能な完了条件: `grep -n 'WTG-100018' wing/src/main/resources/messages.properties` が 1 件で、文言が上のとおりである。
  - _Requirements: 2.8_
  - _Design: ## 機能固有のエラー処理、## ファイル配置計画_
  - _Boundary: 申請状況検索一覧 Service_
  - _Depends: 2_

### 共通（_app-shell）

- [ ] 13 既存 wing の共通ヘッダ・メニュー・エラー画面を、画面設計書に合わせて確認・改修する（UI タスク。_app-shell の 2 画面 × 各 1 状態）
  - 方針: 新しく作らず、既存 wing の共通ヘッダ・メニュー・エラー画面を、画面設計書（`.aidd/screen-design/_app-shell/screen-spec.md` と `screen-map.md` の §4）と見比べ、違う箇所を改修する（質問 Q-TK-AS-003 の回答 A）。違いが無い箇所は変えない。
  - 実装先（既存 wing のコードを調べて特定した。いずれも `wing/src/main/webapp/WEB-INF/pages/` 配下の Thymeleaf テンプレートと、`wing/src/main/java/jp/co/kccs/wt/` 配下の Java）:
    - シェル（ヘッダ）: `common/header.html`（フラグメント `common_header(viewId, viewName, viewManual, viewMenuLink)`。画面名は `'[' + viewId + ']' + viewName` で出す。現状は ﾕｰｻﾞｰ名・画面名・ｸﾞﾙｰﾌﾟの表示と、リンク `[MENU]`・`[TOP MENU]`・`[LOG OUT]`（`/menu/return`・`/menu/top`・`/logout`）を持つ）。
    - 入口（メニュー）: `wtz/wtz001/menu.html`（ヘッダは `common_header('GWTZ000', 'ﾒﾆｭｰ', true, true)` で呼ぶ）、`wtz/wtz001/menuScript.html`、`static/vender/kccs/css/wtz/wtz001/menu.css`、`function/wtz/wtz001/controller/MenuController.java`（`/menu/`）、`function/wtz/wtz001/service/MenuService.java`（メニュー項目を取得する）。メニュー項目はメニュー情報から `menuList` として渡る作りで、テンプレートだけでは項目の中身を決めない。
    - システムエラー: `error.html`（種別・ｺｰﾄﾞ・ﾒｯｾｰｼﾞの表。値は `errorKind`・`errorCode`・`errorMessage` で受け、`戻る(C)` ボタンを持つ）、`common/handler/ExceptionResolver.java`（`error` 画面に値を渡す）。`sessionerror.html`（認証エラー）は画面設計書に無いので対象にしない。
  - 画面設計書に合わせる内容: 利用者・所属・画面名の見出しとヘッダのリンク「MENU」「LOGOUT」（入口では「MENU」を無効表示、「LOGOUT」は全画面で無効表示）、入口の見出し「契約・管財管理」、ナビ項目「物件基本情報登録変更」は無効表示、「物件契約情報申請状況検索/一覧」は `/wtg060` へのリンク、システムエラーは見出し「システムエラー」と種別・コード・メッセージの表だけ（スタックトレース・詳細欄・戻るボタンは置かない）。ヘッダの画面名は `[画面ID]画面名` の形（入口は「メニュー」、システムエラーは「システムエラー」）。現状と違う箇所（例: `[TOP MENU]` のリンク、入口のお知らせ欄、`戻る(C)` ボタン、ラベル文言）は、画面設計書のとおりに直す。
  - 仮置きと但し書き: システムエラーの種別「システムエラー」とメッセージ「処理を続けられませんでした。お手数ですが、メニューからやり直してください。」は仮置き（steering で確定した後に画面設計書を改訂する）。入口のお知らせ欄は置かない。入口のリンクは権限で出し分けず、全項目を表示する。
  - 注記（WTG 以外への波及）: `common/header.html` は WTG 以外を含む 32 のテンプレートが共通で呼んでおり、`menu.html`・`error.html` も WTG 以外の画面から使われる。`steering/product.md` は「WTG 以外の WiNG 機能は改修しない」としているが、本タスクはそれに反して WTG 以外の画面にも変更が及ぶ。人が質問 Q-TK-AS-003 で A（既存 wing の共通ヘッダ・メニュー・エラー画面を画面設計書に合わせて確認・改修する。WTG 以外への波及を上流で許容する）を選んだ事実として、ここに明記する。
  - 画面設計書の参照: `.aidd/screen-design/_app-shell/screen-spec.md` の S-01 メニュー（§3-1-2〜§3-1-6、状態「通常」）と S-02 システムエラー（§3-2-2〜§3-2-6、状態「通常」）、`.aidd/screen-design/_app-shell/screen-map.md` の §3 と §4（§4-1・§4-2）。見比べる mockup は `.aidd/screen-design/_app-shell/pages/` の `s-01-default.html`・`s-02-default.html`。
  - 観測可能な完了条件: 画面設計書の状態数と同数の状態別レンダリングが確認できる。`mockup-manifest.json` の `pages[]` は 2 件（S-01 通常、S-02 通常）で、各状態の出力を JUnit で確認し、2 件とも成功する。
  - 観測可能な完了条件: `STYLEGUIDE.md` と `styleguide.css`（案件ルート直下）の変数・部品クラスに従い、改修した箇所に hex 色・px の直書きが 0 件である。`grep -nE '#[0-9a-fA-F]{3,8}|[0-9]+px'` を改修した箇所に当てて 0 件で、使うクラス名がすべて `styleguide.css` に定義されている（改修していない既存の記述は対象外）。
  - 観測可能な完了条件: ナビ項目の遷移先（`/wtg060`）と、ヘッダのリンクの有効・無効の表示が、画面マップ §3 と §4-1 の表と一致する。
  - 観測可能な完了条件: 既存の呼び出し元（`common/header.html` を呼ぶ他のテンプレート、`error.html` を返す `ExceptionResolver`）が `mvn -f wing/pom.xml package` で終了コード 0 のまま組み立てられ、`git diff --stat` の変更ファイルが上の実装先に挙げたファイルだけである。
  - _Requirements: —_
  - _Design: ## コンポーネントとインターフェース_
  - _Boundary: _app-shell（共通シェル・入口・システムエラー。design.md のコンポーネント一覧に無い共通部で、根拠は画面マップ §4 と _app-shell の画面設計書）_
  - _Depends: 1_

- [ ] 14 検索の実行・件数の上限・ページ送り・検索条件のセッション（状態管理）をテストから作る
  - `Pwtgo060Service` の `search` を、テストから作る。流れは、入力チェック → 社外ユーザーの値の無効化と範囲 → 条件の組立て → `validateSearchLimitCount`（1 ページの件数は `P01` のこの画面の行の 50、上限件数と警告件数は `P02` の ALL の行。上限を超えたら `DS-100024`、警告件数を超えて確認の印が無ければ `DS-100025` の確認）→ 件数が 0 なら 0 件の状態 → 表示ページの行を取って一覧の値の形にする。検索の成功後に検索条件をセッション（キー "PWTGO060Form"）に置き、初期表示とクリアで消す。ページ送りはセッションの条件でそのページを出す。戻り（`/wtg060/return` 向け）はセッションの条件で前に見ていたページを再検索し（警告の確認は出さない）、未検索なら初期表示にする。
  - テスト `Pwtgo060ServiceTest` の `search` で始まるケースを先に作り（Mapper・セッションの代わりは手書きの代替クラス）、RED を確認してから実装する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060ServiceTest#search*` で、同一タスク内の RED から GREEN を確認し、上限超過・警告超過と確認の印あり・0 件・1 ページ目と 2 ページ目・セッションに条件が置かれる/消える・戻りで前のページを再検索・未検索で戻ると初期表示、の各ケースを含めて全件が成功する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060ServiceTest` が、タスク 6〜12 の分を含めて全件成功する。
  - _Requirements: 2.5, 2.6, 2.10_
  - _Design: ## データモデル、## 処理フロー、## 機能固有のエラー処理_
  - _Boundary: 申請状況検索一覧 Service_
  - _Depends: 5, 6, 7, 8, 9, 10_

- [ ] 15 Controller の 7 つの口とルーティングをテストから作る
  - `Pwtgo060Controller`（`@RequestMapping("/wtg060")`・`@FuncID("PWTGO060")`）を、テストから作る。口は `/wtg060`（GET・POST。初期表示）・`/wtg060/search`・`/wtg060/page`・`/wtg060/clear`・`/wtg060/return`（GET・POST）・`/wtg060/detail`・`/wtg060/csv` の 7 つ。入力チェックのエラーは HTTP 200 で同じ画面にメッセージを出す。`/wtg060/detail` は取込中でなければ申請No を渡して `forward:/wtg070/pushApplicationNo`、取込中なら今のページを再検索した同じ画面に `WTG-100018` を出す。`/wtg060/csv` は `Content-Disposition: attachment`・`application/octet-stream` でダウンロードさせる。Mapper を直接呼ばず、ほかの機能パッケージ（`wtg070` ほか）の Service・Mapper を呼ばない。`servlet-context.xml` は変えない。
  - テスト `Pwtgo060ControllerTest` を先に作り（Service の代わりは手書きの代替クラス）、RED を確認してから実装する。
  - 観測可能な完了条件: `mvn -f wing/pom.xml test -Dtest=Pwtgo060ControllerTest` で、同一タスク内の RED から GREEN を確認し、7 つの口それぞれの応答（画面名・forward 先・ダウンロードのヘッダ）と、入力エラー・取込中・上限超過で同じ画面になるケースを含めて全件が成功する。
  - 観測可能な完了条件: `git diff --stat -- wing/src/main/resources/servlet-context.xml` が空で、`grep -rn 'wtg070' wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg060` の出力が `forward:/wtg070/pushApplicationNo` の文字列だけである。
  - _Requirements: 1.1, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1_
  - _Design: ## コンポーネントとインターフェース、## 処理フロー、## 機能固有のエラー処理_
  - _Boundary: 申請状況検索一覧 Controller_
  - _Depends: 11, 12, 14_

- [ ] 16 物件契約情報申請状況検索/一覧画面 S-01 の全状態を画面設計書どおりに作る（UI タスク。S-01 の 11 状態）
  - 画面テンプレート `pwtgo060.html` とスクリプト `pwtgo060Script.html` を、画面設計書どおりに作る。検索条件の 2 つの条件表（A: 文字・選択の項目、B: 日付・日時の範囲）、アクション行の Button「検索(F)」「ｸﾘｱ(R)」「CSV出力(O)」（新規登録のボタンは置かない）、一覧の 14 列（列幅の段は画面設計書 §3-1-2 の割り付け。表の中だけで横に流す）、ページ送り（`common/pager`）、0 件の表示（`common/emptyMsg`）、通知（Banner）、警告件数超過の確認（Dialog。「続行(Y)」「中止(N)」）、月次カレンダー（Dialog）。出力は `th:text` で行い、`th:utext` は使わない。社外ユーザーの状態は、起案会社が自社の会社名で変更不可、所属①②が空で変更不可、進捗検索(日数)・(選択)を置かない（空のセルで格子を保つ）。
  - 状態名は画面設計書 §3-1-5 と同じ 11 個: 初期表示・通常・検索結果 0 件・ローディング・入力エラー・上限件数超過・警告件数超過の確認・取込中の申請No を押した・社外ユーザー・長文・月次カレンダー。
  - 画面設計書の参照: `.aidd/screen-design/application-status-search/screen-spec.md` の S-01（§3-1-1〜§3-1-6、状態は §3-1-5、要件被覆は §4）。見比べる mockup は `.aidd/screen-design/application-status-search/pages/` の `s-01-initial.html`・`s-01-default.html`・`s-01-zero.html`・`s-01-loading.html`・`s-01-input-error.html`・`s-01-over-limit.html`・`s-01-warning-confirm.html`・`s-01-importing.html`・`s-01-external.html`・`s-01-long-text.html`・`s-01-calendar.html`。
  - 範囲外の扱い: `mockup-manifest.json` の `missing[]` の 4 件（SGB-16・SGB-17・SGB-18・SGB-19）は、部品が無いため mockup と同じく描かず、完了条件に含めない。生値で補わない。
  - 観測可能な完了条件: 画面設計書の状態数と同数の状態別レンダリングが確認できる。`mockup-manifest.json` の `pages[]` は 11 件で、各状態のモデルを与えた出力を JUnit で確認し、11 件とも成功する。状態名が画面設計書 §3-1-5 と 1 対 1 で一致する。
  - 観測可能な完了条件: `STYLEGUIDE.md` と `styleguide.css`（案件ルート直下）の変数・部品クラスに従い、hex 色・px の直書きが 0 件である。`grep -nE '#[0-9a-fA-F]{3,8}|[0-9]+px'` を `pwtgo060.html` と `pwtgo060Script.html` に当てて 0 件で、使うクラス名がすべて `styleguide.css` に定義されている。
  - 観測可能な完了条件: 社外ユーザーの出力に起案会社の読取専用の選択・所属①②の読取専用の入力があり、進捗検索の 2 項目が無い。通常の出力で取込中の行の申請No がリンクでなく、新規登録のボタンが無い。入力エラーの出力に画面設計書のダミーと同じ形のエラー行（コード付き）がある。
  - _Requirements: 1.1, 1.5, 1.6, 1.7, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.8, 2.9, 4.1_
  - _Design: ## コンポーネントとインターフェース、## データモデル、## 追加検討事項_
  - _Boundary: 申請状況検索一覧画面のテンプレートとスクリプト_
  - _Depends: 13, 15_

### 横断確認

- [ ] 17 全体結合確認用の smoke wrapper を作る（結合確認タスク）
  - 案件の全体結合確認の smoke が呼ぶ wrapper（`tools/smoke.py`）を作る。内容は、wing を `steering/tech.md` の共通コマンドの起動手順（`mvn -f wing/pom.xml tomcat7:run`。同ファイルでは未確認のコマンド）で起動し、起動の完了を待ち、1 経路を通し、起動したサーバーを停止する。
  - 起動完了の判定と 1 経路は、DB に依存しない口 `/menu` の HTTP 200 とする（質問 Q-TK-AS-001 の回答 B）。接続先は `wing/pom.xml` の tomcat7 設定（port 8080・path `/`）に従う。
  - 未確認の事項: `/menu` が DB に依存するか、認証（ログイン）を要するかは未確認で、smoke 実行時に確認する。ソースでは `/menu/` は `MenuController`（`/menu/`）が `MenuService` を呼び、`servlet-context.xml` のセッション検査の対象から外れていない。確認の結果は実装メモの既知の制約に記録する。
  - 観測可能な完了条件: `python3 -B tools/smoke.py` が終了コード 0 で終わり、終了後に起動した Tomcat のプロセスが残っていない。
  - 観測可能な完了条件: wrapper が起動完了までの待ちの間 `/menu` を呼び、HTTP 200 を確認して経路を通し、確認できなければ（待ちの上限を超えた場合を含む）非 0 で終わる。
  - _Requirements: —_
  - _Design: ## 処理フロー_
  - _Boundary: 申請状況検索一覧 Controller_
  - _Depends: 13, 15, 16_

## 実装メモ（Implementation Notes）

> 実装中に分かったことを追記していく節。計画そのものではなく、進めた結果を残す。\
> _分担_: 設計を変える必要が出たら、先に `design.md` を更新してから、その理由をここに記録する。

> _書き方_: 実装が進むにつれて追記する。着手時点では空でよい。

> 次の3節の実績用スロットはPhase 7の必須回答・未記入数に含めない。新規計画では空欄にできる。既存のスロット行は一括削除せず、実装時の許可更新履歴で項目を追記する。計画本文の未記入欄にはこの例外を適用しない。

### 決定ログ

> 実装中に下した判断を残す節。

> _書き方_: 1 項目 1 行で、何を決めたかと、なぜそう決めたかを書く。決めた時点で書き、後からまとめて書かない。

- <TSK_DECISION_LOG_N>

### 既知の制約 / 残課題

> このフィーチャーに残ったまま運用する制限を挙げる節。\
> _分担_: 送り先が決まっているものは `### 後続への申し送り`。

> _書き方_: 回避する方法があるものは併記する。次に手を入れる人が同じ問題を踏まないことを目的にする。

- <TSK_KNOWN_ISSUE_N>

### 後続への申し送り

> 次のフィーチャーや後続タスクに送るものを挙げる節。\
> _分担_: このフィーチャーに残り続けるものは `### 既知の制約 / 残課題`。

> _書き方_: 今回は扱わないと判断したもののうち、送り先が決まっているものを書く。

- <TSK_HANDOVER_N>

---

_「いつ・どの順で作るか」を確定させる文書。_
