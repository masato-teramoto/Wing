---
feature: contract-info-download
status: approved
updated_at: 2026-10-09T21:02:19+09:00
---

# 技術設計書

> このファイルは **「どう作るか」** を確定させる文書である。実装者ごとの解釈の食い違いを防ぎ、レビュー・実装・検証の共通の土台にする。\
> _分担_: 同一 feature の `requirements.md` が `status: approved` になるまで着手しない。本ファイルが `approved` になるまで `tasks.md` に進まない。`approved` は人間が付ける（エージェントは付けない）。

> _書き方_: 各節は結論から書き、検討の過程や調査ログは残さない。

> _出典の表記_: 「要件 N」「N.M」は `specs/contract-info-download/requirements.md` の要件と受け入れ基準ID。「Q-DS-CD-xxx」は本 feature の design 作成中の質問への回答（回答者 Junichi Noumi、2026-10-08。原文は `.aidd/.engine/answer-ds-cd-20261008-1845.txt`）。「出力の定義」は CSV の 381 列の表で、本書「物理データモデル」の `#### 出力 CSV の項目定義（381 列）` に取り込んだもの、「作業用テーブルの表」は作業用テーブルとビューの表で、同じ節の `#### 作業用テーブルとビューの定義` に取り込んだもので、どちらも回答者が渡した表のとおりに本書の本文に置き、本書の正とする。「pbi design」は `specs/property-basic-info/design.md`（approved）、「ci design」は `specs/contract-info-import/design.md`（approved）。既存 wing のパスは、既存の実装から読み取った根拠を示す。\
> _上流との関係_: 本書で「上流から意図して外れる」と書いた箇所は、人間の回答に従って書いたもので、上流（requirements・steering）は Phase 5 の最後にまとめて直す（upstream-carryover）。

## 概要（Overview）

> 実装者が最初に読む節。何を誰に提供し、既存の何が変わるかを示す。\
> _分担_: 要件そのものは `requirements.md`。ここには設計上の位置づけだけを書く。

> _書き方_: 設計用語を使わず、この設計書を初めて読む人に通じる言葉で書く。

- **目的（Purpose）**: 起案者・申請者・確認者（ベンダー／施工会社の利用者を含む） に 既存の契約情報を条件で探し、選んだ行を契約情報取込にそのまま使える 381 列の CSV で受け取れる画面（契約情報ダウンロード GWTG100） を提供する。
- **利用者（Users）**: 物件基本情報登録変更画面の契約局DL ボタンを使える利用者（`requirements.md` の概要、Q-DS-CD-008）
- **影響（Impact）**: 現在の 取込用の CSV を手で作るしかない状態 を 既存の契約情報（`TWTGM010`〜`TWTGM030`）から取込用の CSV を出せる形 に変更する。

### 達成目標（Goals）
> このフィーチャーが成功したと言える状態を定める節。

> _書き方_: 1 項目 1 行。基準を明記して、達成したかどうかを後から判定できる書き方にする。

- 契約局DL ボタンで、申請No を隠し項目に持った画面がポップアップで開き、検索条件は空のまま出る（1.1・1.2・1.6、Q-DS-CD-008・Q-DS-CD-009）
- 15 項目の検索条件が、`### ドメインモデル（Domain Model）` の表の一致の仕方で働き、入れた項目だけが AND で効く（1.3、Q-DS-CD-004）
- 一覧に 19 項目（対象・No を含む）が GWTG004 と同じ並びで、1 ページ 100 件で出る（1.4・1.5、Q-DS-CD-003・Q-DS-CD-007）
- ベンダー区分か施工会社区分に値のある利用者には、工事案件マスタに行が無い契約情報と、値のある区分に合う行がある契約情報だけが出る。両方空の利用者には絞り込みが無い（2.1・2.2）
- 表示中のページで選んだ行だけが、出力 CSV の項目定義の 381 列・MS932・見出し行付きで `WTG100_yyyyMMddHHmmss.csv` として出る。今の申請の基地局番号の行が先頭に来る（3.1〜3.6、Q-DS-CD-001・Q-DS-CD-002・Q-DS-CD-009）
- 1 行も選ばずに出力すると `GEF-000057` を出し、CSV を出さない（3.3、Q-DS-CD-010）

### やらないこと（Non-Goals）

> 達成目標に含めないことを先に宣言する節。`### 達成目標（Goals）` と対で読む。\
> _分担_: 実装として持たないものは `### このスペックが持たない責務（Out of Boundary）`。ここには目標の話だけを書く。

> _書き方_: 今回やらないだけのものと、今後もやらないものを書き分ける。

- 今後もやらない：ページをまたいだ選択の記憶（出力するのは表示中のページで選んだ行だけ。Q-DS-CD-006 の B）
- 今後もやらない：サーバーでの検索条件の桁・形式のチェック（画面の入力桁と IME の入力モードで抑える。Q-DS-CD-005）
- 今後もやらない：検索件数の上限と警告（`P02`・`DS-100024`・`DS-100025`）と、CSV の件数の上限（3.4、Q-DS-CD-007）
- 今後もやらない：開いたとき・出力のときに、渡された申請No の申請でこの画面を使えるかを確かめ直すこと、社外ユーザーの範囲を当てること（Q-DS-CD-009 の 2・4）
- 今後もやらない：閉じるボタン（ウインドウはブラウザーで閉じる。Q-DS-CD-008 の 2）と、基地局番号のリンク（ラベルで表示する。Q-DS-CD-003 の 2）
- 今回やらない：本 feature 固有の性能目標値を設けること（`requirements.md` の非機能要件。既存 WiNG の水準に従う）
- 今回やらない：画面の配置と見た目を決めること。本書は項目・一覧の列・ボタンとその規則だけを書き、配置と見た目は Phase 8 の実装で決める（物件基本情報登録変更と同じ）

## 責務境界（Boundary Commitments）

> 実装物として**どのスペックが何を持つか**を確定させる節。タスク分解と後工程の検証もここを基準にする。\
> _分担_: 何を作り何を作らないかは `requirements.md` の `## スコープの境界（Boundary Context）`。ここには所有するデータとインターフェース、依存してよい相手を書く。

### このスペックが持つ責務（This Spec Owns）

> このスペックが持ち主になるものを宣言する節。

> _書き方_: 各項目 1 行。他のスペックとの間で担当が曖昧になりやすいものから先に書く。振る舞いをどのコンポーネントが担うかは `## コンポーネントとインターフェース（Components and Interfaces）` に書く。

- **所有するデータ**:
  - 作業用テーブル `TWTGD050`（発行依頼書リバースデータ）・`TWTGD060`（発行依頼書フォーマット）と、ビュー `VWTGM010`（発行依頼書リバースデータビュー）。定義は作業用テーブルとビューの定義（Q-DS-CD-002）。DDL は本 feature の tasks で作る（Q-DS-CD-002 の 5）
  - 検索条件のセッション（キー "PWTGO100Form"。検索のたびにフォーム全体を置き、初期表示とクリアで消す）（既存の検索一覧と同じ。`wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg002/controller/Pwtgo004Controller.java:75`〜`:100`）
  - コードマスタ `WTZ/PARAM/P01` のこの画面の行（キー3＝`PWTGO100`、数値項目1＝100）と、`ZMENUAUTH` の `PWTGO100` の行（Q-DS-CD-007・Q-DS-CD-008）。投入の文と手順は本 feature の tasks で作る
- **定義するインターフェース**:
  - 契約情報ダウンロード画面（GWTG100）と、その口（`/wtg100`・`/wtg100/search`・`/wtg100/page`・`/wtg100/clear`・`/wtg100/csv`）（Q-DS-CD-008）
  - 出力する CSV の 381 列の見出しと値の形（出力 CSV の項目定義。Q-DS-CD-001 の 6）

### このスペックが持たない責務（Out of Boundary）

> 関連はするが、このスペックが持ち主にならないものを宣言する節。「ついでに」で実装範囲が広がるのを防ぐ。\
> _分担_: ここには持ち主が他にあるものだけを書く。目標として掲げないものと、今回やらないと決めただけのものは `### やらないこと（Non-Goals）`。

> _書き方_: 他に任せるものは委譲先を必ず添える。委譲先が決まっていないものは `## 設計判断（Design Decisions）` で扱う。

- **他に任せる範囲と、その委譲先**:
  - 契約局DL ボタンの表示と、この画面を開く口（`/wtg070/keyakuDl` から `/wtg100?FunctionID=WTG100&applicationNo=<申請No>` でポップアップで開く。pbi design は「申請No だけを渡す」と書いており、`FunctionID` とパラメータ名 `applicationNo` を足すことを Phase 5 の最後にまとめて直す（upstream-carryover。design-check 1 回目 #6））→ `specs/property-basic-info/design.md`（14.14、Q-DS-CD-008 の 1）
  - CSV の取込と、取り込む側のリバースの 381 列の定義 → `specs/contract-info-import/design.md`。ci design は直さない。出力 CSV の項目定義と取込側の表の列の並びが同じであることは、全機能をまたいだ確認で確かめる（Q-DS-CD-001 の 6。upstream-carryover に記録）
  - 既存の契約情報（`TWTGM010`〜`TWTGM030`）・計画マスタ（`TWTBM010`）・工事案件マスタ（`TWTBM080`）の定義と更新 → 既存の WTG・WTB。本 feature は読むだけ
  - 物件申請情報（`TWTGM080`）の定義 → pbi design。本 feature は基地局番号を読むだけ
  - CSV の共通部品 `CsvUtils`（orangesignal-csv）→ pbi design が新しく作る。本 feature は引数を足さずに使う（Q-DS-CD-001 の 5）
  - コードマスタ `P01` の行と `ZMENUAUTH` の行の投入 → 発注者が導入手順書に沿って行う（Q-DS-CD-007 の 3・Q-DS-CD-008 の 4）
- **後のフェーズに回す作業**:
  - 画面の配置・見た目：Phase 8 の実装で決める（物件基本情報登録変更と同じ）
  - 2 つの作業用テーブルとビューの DDL、`P01`・`ZMENUAUTH` の投入の文と手順：本 feature の tasks で作る（Q-DS-CD-002 の 5・Q-DS-CD-007 の 3・Q-DS-CD-008 の 4）
  - Oracle を使う確認（Mapper XML の SQL とビュー）：総合テスト（試験仕様書）に回す（物件基本情報登録変更と同じ。Q-DS-PBI-014）

### 依存してよい対象（Allowed Dependencies）

> このフィーチャーが前提にしてよい既存の仕組みを列挙する節。\
> _分担_: 要件として何に依存するかは `requirements.md` の `## 前提と依存（Dependencies / Assumptions）`。ここには実装が使ってよい範囲と守る制約を書く。

> _書き方_: 依存先は、システム名・コンポーネント名・共有基盤名など後から特定できる固有名で書く。制約には一方向性、循環の禁止、レイヤをまたぐ条件など、守るべき条件を書く。

- **依存先**:
  - 既存の契約情報 `TWTGM010`（契約基本情報）・`TWTGM020`（契約者情報）・`TWTGM030`（契約支払情報）、計画マスタ `TWTBM010`、工事案件マスタ `TWTBM080`、コードマスタ `TWTZM040`（読むだけ）
  - 物件申請情報 `TWTGM080` の `Kichikyoku_No`（pbi design。読むだけ）
  - wing の共通基盤：`ServiceBase` の 1 ページの件数（`selectListSize`）とページ（`createPasesInfo`・`createInitPasesInfo`）（`wing/src/main/java/jp/co/kccs/wt/common/service/ServiceBase.java:112`〜`:242`）、`SessionService`、`StringUtils.escapeSQLforLike`（`wing/src/main/java/jp/co/kccs/wt/common/utils/StringUtils.java:936`）、`LoginUserUtils`（ベンダー区分 `getCoVendKbn`・施工会社区分 `getCoSekoKbn`。`wing/src/main/java/jp/co/kccs/wt/function/wte/wte020/service/Pwteo021Service.java:224`〜`:225`）、`CodeMstService`、共通部品 `common/pager`・`common/pageCount`・`common/emptyMsg`
  - CSV：`CsvUtils`（pbi design が新しく作る）と、orangesignal-csv 2.2.1 の `CsvEntityListHandler`・`@CsvEntity`・`@CsvColumn`（pbi design が依存に足す。申請状況検索一覧の CSV と同じ使い方）
  - コードマスタ：WTG/PARAM/`P21`・`P15`、WTB/CODE/`C39`、WTZ/MASTER/`M04`・`M05`、WTZ/PARAM/`P01`。ビューの名称の引き方は作業用テーブルとビューの定義のとおり（`P07`・`P08`・`P10`・`P16`〜`P18`・`P23`・`P24`、WTG/CODE/`C02`、WTZ/MASTER/`M01`・`M10`・`M11`）
- **依存の制約**:
  - Controller → Service → Mapper の向きだけで呼び、ほかの機能パッケージ（`wtg002`・`wtg070` ほか）の Service・Mapper を呼ばない。GWTG004 の作りは手本として写し、呼ばない（`steering/architecture.md` の `## レイヤーと依存ルール`）
  - 書くのは自分が持つ作業用テーブル（`TWTGD050`・`TWTGD060`）だけ。業務の表は書かない

### 再確認が必要になる変更（Revalidation Triggers）

> ここに挙げた変更が起きたら、依存するスペックや利用側に再確認を依頼する節。

> _書き方_: 1 項目 1 行（例: 契約の形（API・イベント・型の定義）の変更、データ所有権の移動、依存方向の変更、起動・実行時の前提条件の変更）。

- 契約情報取込のリバースの 381 列の並び・形の変更（ci design）。出力 CSV の項目定義を合わせて直す
- `TWTGM010`〜`TWTGM030`・`TWTBM010`・`TWTBM080` の列の変更
- `/wtg070/keyakuDl` からこの画面を開く口（URL・渡す値）の変更（pbi design）
- `TWTGM080.Kichikyoku_No` の意味の変更（pbi design）
- コードマスタ（`P21`・`P15`・`C39`・`M04`・`M05`・`P01` とビューで引く名称）の意味の変更
- `CsvUtils` の入出力の変更（pbi design）

## アーキテクチャ（Architecture）

> このフィーチャーをどの構成に載せるかを決める節。\
> _分担_: レイヤ構成と依存のルールは `steering/architecture.md` の `## レイヤーと依存ルール`、命名とコード規約は `steering/tech.md` の `## 命名規則` と `## コード規約`。ここにはこのフィーチャー固有の構成だけを書く。

### 既存アーキテクチャの分析（Existing Architecture Analysis）

> 既存システムに手を入れる場合に、守るべき前提を確認する節。

> _書き方_: 今回の変更で壊してはいけないものを挙げる。現状の評価や改善案は書かない。

- **現行のパターンと制約**: 既存の契約情報検索／一覧（GWTG004。`wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg002/controller/Pwtgo004Controller.java`、`@RequestMapping("/wtg002")`・`@FuncID("PWTGO004")`）は、契約基本情報の「会社コード＋計画基地局番号＋枝番」ごとに 1 行とし、契約者情報と契約支払情報を外部結合して `MAX` でまとめる（`wing/src/main/resources/jp/co/kccs/wt/function/wtg/wtg002/Pwtgo004Mapper.xml:264`〜`:283`・`:505`〜`:520`）。件数を数えてから表示ページの行だけを取り、ページ送りは `/<機能ID>/page`、検索条件はセッションに置く。全選択・全解除はブラウザ側で表示中の行のチェックを切り替えるだけ（`wing/src/main/webapp/WEB-INF/pages/wtg/wtg002/pwtgo004Script.html:47`〜`:60`）。1 ページの件数は `ServiceBase.selectListSize` がコードマスタ `P01` から決める
- **守るべきドメイン境界**: 既存の契約情報（`TWTGM010`〜`TWTGM030`）は既存の WTG、計画マスタ・工事案件マスタは既存の WTB、物件申請情報は物件基本情報登録変更が持つ。本 feature は読むだけ
- **維持する統合ポイント**: ログインとセッション、メニュー権限（`ZMENUAUTH`）、コードマスタ（`TWTZM040`）、メッセージ（`wing/src/main/resources/messages.properties`）
- **解消 / 回避する技術的負債**: <DSN_EXISTING_DEBT>（不要：既存の構成（Spring MVC＋MyBatis、既存の共通部品）にそのまま乗せる新しい機能で既存のコードは直さないため、解消する技術的負債も、避けるために設計を変える技術的負債も無い — 回答者 Junichi Noumi、2026-10-07（物件基本情報登録変更と同じ））

### アーキテクチャ方式と境界図（Architecture Pattern & Boundary Map）

> 採用する構成とコンポーネント間の関係を、図と文で示す節。

> _書き方_: 図は例であり、大文字の名前はすべて実際のコンポーネント名に置き換えたり、ノードを追加したりして関係性を示すようにする。関係が複雑でない場合は図を省いて文だけでもよい。

```mermaid
flowchart LR
    PBI[物件基本情報登録変更画面<br/>GWTG070 契約局DL] -.ポップアップ /wtg100?FunctionID=WTG100＋申請No.-> UI[契約情報ダウンロード画面<br/>GWTG100]
    UI --> CTL[契約情報ダウンロード Controller]
    CTL --> SVC[契約情報ダウンロード Service]
    SVC --> MAP[(契約情報ダウンロード Mapper)]
    MAP --> DB[(Oracle<br/>TWTGM010〜030・TWTBM010・TWTBM080<br/>TWTGM080・TWTZM040)]
    MAP --> WK[(作業用 TWTGD050・TWTGD060<br/>ビュー VWTGM010)]
    SVC --> CSV[CsvUtils]
```

- **選択したパターン**: 既存 wing の 3 層（Controller → Service → Mapper）と、既存の契約情報検索／一覧（GWTG004）と同じ検索・ページ・セッションの作り。CSV は作業用テーブルで 1 契約 1 行に組み立ててから書き出す（Q-DS-CD-002）
- **ドメイン / 機能の切り分け**: 申請No の基地局番号の取得・ベンダー／施工会社の区分の取得・検索条件の組立て・作業用テーブルの作り直しの順序・CSV の書き出しは Service、検索の SQL（結合・条件・まとめ・ページ）と作業用テーブルの削除・登録・更新・読取りは Mapper、データ種別ごとの列の形のそろえ方はビュー `VWTGM010`、画面の入力と一覧の表示と全選択・全解除は画面のテンプレートとスクリプト
- **既存パターンとの整合**: プログラムID `PWTGO100`、機能ID `WTG100`、画面ID `GWTG100`、パッケージ `function/wtg/wtg100`、URL `/wtg100/<アクション>`（`steering/tech.md` の `## 命名規則`、Q-DS-CD-008 の 1）
- **新規コンポーネントを置く理由**: 既存の契約情報から取込用の CSV を出す画面は既存に無い（`requirements.md` の要件 1・3）
- **steering との整合**: 新しい技術を持ち込まない。CSV は pbi design が足す orangesignal-csv の共通部品を使う。画面を使えるかは `AccessControlInterceptor`、既存の契約情報の絞り込みは既存の WTB と同じ計画マスタの方式で比べる列と区分の扱いを合わせる（`steering/security.md` の `#### 所有権・エンティティ境界`）。ただし工事案件マスタに行が無い契約情報を出す点は既存の WTB と違う（`## 追加検討事項（Additional Considerations）`。steering から意図して外れる）

### 技術スタック（Technology Stack）

> このフィーチャーで追加する、または例外的に採用する技術を書く節。\
> _分担_: プロジェクト共通のスタックは `steering/tech.md` の `## コアテクノロジ` と `## 主要ライブラリ`。ここには差分だけを書く。

> _書き方_: 1 行 1 技術。レイヤは Frontend / CLI、Backend / Service、Data / Storage、Messaging / Event、Infrastructure / Runtime などから選ぶ。

| レイヤ | 採用 / バージョン | このフィーチャーでの役割 | 備考 |
|---|---|---|---|
| Infrastructure / Runtime | 開発端末の JDK 1.8（`-source`/`-target` 1.7） | 開発端末でのコンパイルと自動テストの実行 | 本番は JDK 1.7（`steering/tech.md`）。物件基本情報登録変更と同じ（Q-DS-PBI-014）。steering/tech.md から意図して外れる。上流は Phase 5 の最後にまとめて直す（upstream-carryover） |

## データモデル（Data Models）

> このフィーチャーで変更するデータ構造を確定させる節。\
> _分担_: システム全体の ER 図・全体スキーマは `docs/architecture/data-model.md` の `## ER 図` に従う。命名と型の共通ルールは `steering/database.md` の `## 命名規則` と `## 型の指針`。

> _書き方_: このフィーチャーで変更するエンティティだけを書く。物理データモデルを変えたら `docs/architecture/data-model.md` との整合を確認する。

### ドメインモデル（Domain Model）

> 業務上の概念とその関係を、保存形式に依らない形で書く節。

> _書き方_: 実装の都合ではなく、業務としてどう成り立っているかで書く。集約は、一緒に更新しないと辻褄が合わなくなるデータのまとまり。値オブジェクトは、金額や住所のように、値が同じなら同じものとして扱ってよいもの。ドメインイベントは、「注文が確定した」のように業務で起きた出来事のうち、他に知らせる必要があるものを指す。不変条件は、いつ見ても成り立っていなければならない決まりを指す。

- **集約とトランザクション境界**: 「契約」（契約基本情報の「会社コード＋計画基地局番号＋枝番」）を 1 行として読む。1 契約に契約者情報 0..n・契約支払情報 0..n が付く。CSV の作り直し（作業用テーブルの削除 → `TWTGD050` の登録 → `TWTGD060` の登録と更新 → 読取り）は 1 つのトランザクションで行う（読み取り専用にしない。Q-DS-CD-002 の 3）
- **エンティティ / 値オブジェクト / ドメインイベント**: 値オブジェクトは検索条件（15 項目）・一覧の 1 行（19 項目）・CSV の 1 行（381 列）。作業用テーブルの行は、実行ユーザーID で分けた一時的な写しで、業務のエンティティではない。ドメインイベントは無い
- **ビジネスルール / 不変条件**:
  - **検索条件**（1.2・1.3、Q-DS-CD-004・Q-DS-CD-005）：15 項目。空の項目は条件に入れず、入れた項目だけを AND でつなぐ。前方一致と部分一致は `StringUtils.escapeSQLforLike` で `%`・`_` を逃がし、`LIKE … ESCAPE '/'` で比べる（GWTG004 と同じ。`Pwtgo004Mapper.xml:361`〜`:499`）。サーバーでは桁・形式を確かめない（`### バリデーション設計`）

    | 検索条件 | 比べる列 | 一致の仕方 | 入力桁 | IME |
    |---|---|---|---|---|
    | 登録状態 | `TWTGM010.Status_Kind` | 一致（コンボ。`WTG/PARAM/P21`、先頭は空） | ― | ― |
    | 計画基地局番号 | `TWTGM010.Keikaku_Kichikyoku_No` | 前方一致 | 9 | 半角英数 |
    | 計画基地局名 | `TWTGM010.Keikaku_Kichikyoku_Name` | 部分一致 | 120 | ひらがな |
    | 枝番 | `TWTGM010.Plan_SiteID_Branch` | 一致 | 5 | 半角英数 |
    | 契約者番号 | `TWTGM020.Constract_CD` | 前方一致 | 20 | 半角英数 |
    | ロケーションID | `TWTBM010.LOCATION_ID` | 前方一致 | 20 | 半角英数 |
    | 代表契約局番 | `TWTGM010.Represent_Contract_No` | 前方一致 | 9 | 半角英数 |
    | 代表契約枝番 | `TWTGM010.Represent_Contract_Branch_No` | 前方一致 | 5 | 半角英数 |
    | 転貸借 | `TWTGM010.Move_Lease` | 一致（コンボ。`WTB/CODE/C39`、先頭は空） | ― | ― |
    | 建物、ﾋﾞﾙ | `TWTGM010.ADDRESS4` | 部分一致 | 100 | ひらがな |
    | 基地局番号 | `TWTGM010.Kichikyoku_No` | 前方一致 | 9 | 半角英数 |
    | 基地局名 | `TWTGM010.Kichikyoku_Name` | 部分一致 | 120 | ひらがな |
    | 転貸借契約書名 | `TWTGM010.MOVE_LEASE_CONTRACT` | 一致（コンボ。`WTG/PARAM/P15` の「キー3:名称」を表示順に出し、先頭は空） | ― | ― |
    | 法人名/個人名 | `TWTGM020.Name` | 部分一致 | 60 | ひらがな |
    | 法人名/個人名(ｶﾅ) | `TWTGM020.Name_Kana` | 部分一致 | 80 | ひらがな |

    - 代表契約局番・代表契約枝番を前方一致にするのは requirements 1.3（GWTG004 と同じ。GWTG004 は一致）から意図して外れる。転貸借契約書名は GWTG004 に無いので、Q-DS-CD-004 で定めた形にする。上流は Phase 5 の最後にまとめて直す（upstream-carryover）
    - 契約者番号・法人名/個人名の条件は、その契約のどれか 1 行の契約者情報が合えば当たる（GWTG004 と同じ外部結合と `MAX` のまとめ）
  - **ベンダー／施工会社の絞り込み**（2.1・2.2、Q-DS-CD 冒頭の訂正 13）：ログインユーザーのベンダー区分（`LoginUserUtils.getLoginUserInfo().getCoVendKbn()`）か施工会社区分（`getCoSekoKbn()`）に値があるときだけ、次の条件を AND で足す。両方空なら足さない
    - 結合の順：契約基本情報 →（会社コード・計画基地局番号）→ 計画マスタ `TWTBM010` →（会社コード・計画基地局番号）→ 工事案件マスタ `TWTBM080`
    - 条件：「その契約の工事案件マスタの行が 1 行も無い」**または**「工事案件マスタのどれか 1 行が、値のある区分について `TWTBM080.Bs_Vendor_Cd ＝ ベンダー区分` か `TWTBM080.Motouke_Kaisya_Cd ＝ 施工会社区分` に合う」。両方に値があれば 2 つの比べ方を OR でつなぎ、値の無い区分は比べない。全体を括弧でくくって AND で足す
    - 計画マスタに行が無い契約情報も、工事案件マスタの行が無いものとして出す
    - requirements 2.1・2.2 の「計画マスタ（`TWTBM080`）」は「工事案件マスタ（`TWTBM080`）」の書き誤りとして読む。上流は Phase 5 の最後にまとめて直す（upstream-carryover）
    - 比べる列と値のある区分だけで絞る点は既存の WTB（`WTX/WEB-INF/src/jp/co/kccs/wt/wtb/wtb020/PWTBO021Action.java:724`〜`:756`、wing の同じ形は `wing/src/main/resources/jp/co/kccs/wt/function/wte/wte020/Pwteo021Mapper.xml:169`〜`:185`）と同じ。工事案件マスタに行が無い契約情報を出す点は既存の WTB（`EXISTS` だけ）と違い、`steering/security.md` 285 行目の「既存の WTB と同じ方式」から意図して外れる。上流は Phase 5 の最後にまとめて直す（upstream-carryover）
    - 検索と同じ絞り込みを CSV の作り直しでも当てる（`### 機能固有のエラー処理`・`### セキュリティ上の考慮`）
  - **一覧の 19 項目**（1.4、Q-DS-CD-003）

    | 順 | 項目 | 出す値 | 表示 |
    |---|---|---|---|
    | 1 | 対象 | チェックボックス | 中央 |
    | 2 | No | 表示中のページの通し番号 | 5 桁 |
    | 3 | 基地局番号 | `TWTGM010.Kichikyoku_No`（ラベル。リンクにしない） | 全部表示 |
    | 4 | 枝番 | `TWTGM010.Plan_SiteID_Branch` | 全部表示 |
    | 5 | 登録状態 | `P21` の「キー3:名称」 | 全部表示 |
    | 6 | 基地局名 | `TWTGM010.Kichikyoku_Name` | 20 バイト＋ツールチップ |
    | 7 | ロケーションID | `TWTBM010.LOCATION_ID` | 全部表示 |
    | 8 | 都道府県 | `TWTGM010.ADDRESS_CD1` の `M05` の名称 | 8 バイト |
    | 9 | 市区町村 | `TWTGM010.ADDRESS_CD2` の `M04` の名称 | 12 バイト＋ツールチップ |
    | 10 | 字、番地 | `TWTGM010.ADDRESS3` | 20 バイト＋ツールチップ |
    | 11 | 建物、ﾋﾞﾙ | `TWTGM010.ADDRESS4` | 20 バイト＋ツールチップ |
    | 12 | 契約先/法人名 | `TWTGM020.Name` | 20 バイト＋ツールチップ |
    | 13 | 契約先/法人名(ｶﾅ) | `TWTGM020.Name_Kana` | 20 バイト＋ツールチップ |
    | 14 | 契約先/所属部署名 | `TWTGM020.Belonging_Post` | 20 バイト＋ツールチップ |
    | 15 | 契約先/都道府県 | `TWTGM020.Address_CD1` の `M05` の名称 | 8 バイト＋ツールチップ |
    | 16 | 契約先/市区町村 | `TWTGM020.Address_CD2` の `M04` の名称 | 12 バイト＋ツールチップ |
    | 17 | 契約先/字、番地 | `TWTGM020.Address3` | 20 バイト＋ツールチップ |
    | 18 | 契約先/建物、ﾋﾞﾙ | `TWTGM020.Address4` | 20 バイト＋ツールチップ |
    | 19 | 受電方法 | `TWTGM010.Elect_Kind`（1:電力会社直受／2:ﾃﾅﾝﾄ受電／3:ａｕ受電） | 20 バイト＋ツールチップ |

    - 「契約先/…」の 7 項目は、その契約の契約者情報のうち契約者区分 1 の行から 1 行を選んで出す。検索条件のうち契約者に掛かるもの（契約者番号＝前方一致、法人名/個人名・法人名/個人名(ｶﾅ)＝部分一致。入力があるものだけ）で契約者区分 1 の行を絞り、契約者番号の降順で先頭の 1 行を出す。絞って当たらなければ、条件を外した契約者区分 1 の行の、契約者番号の降順で先頭の 1 行を出す。比べ方は検索条件と同じ（`escapeSQLforLike` で逃がした LIKE）にする。GWTG004 の手順（`wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg002/service/Pwtgo004Service.java:404`〜`:460`、`Pwtgo004Mapper.xml:769`〜`:793`・`:823`〜`:836`）にならうが、GWTG004 の「法人名の条件をカナの値で上書きする」（Service:408）と「法人名を完全一致で比べる」（Mapper:824）はまねしない（design-check 1 回目 #5）
    - 表示のバイト数で切り、ツールチップで全部を出す
    - 並びは GWTG004 と同じで、会社コード・基地局番号・枝番・基地局名・契約者名・住居の都道府県コード・市区町村コード・字地番・建物ビルの昇順（`Pwtgo004Mapper.xml:509`〜`:520`）。今の申請の基地局番号を先頭にするのは CSV だけ（Q-DS-CD-003 の 1）
  - **件数**（1.5、Q-DS-CD-007）：1 ページの件数は `ServiceBase.selectListSize` で `WTZ/PARAM/P01` のこの画面の行（キー3＝`PWTGO100`、数値項目1＝100）から取る。件数の上限と警告（`P02`・`DS-100024`・`DS-100025`）は掛けない（`validateSearchLimitCount` を呼ばない）。0 件なら共通部品 `common/emptyMsg` の「該当するデータはありません」を出す（メッセージキーは使わない）
  - **選択**（3.1・3.3、Q-DS-CD-006）：出力するのは表示中のページでチェックした行だけ。全選択(X)・全解除(Y) は表示中のページの行のチェックをブラウザ側で切り替える。検索し直したとき・ページを移ったとき・クリアしたときは、それまでの選択を残さない
  - **今の申請の基地局番号**（3.5、Q-DS-CD-009）：画面の隠し項目に持った申請No で、`TWTGM080` を会社コード＝ログイン会社、申請No＝その申請No で引き、`Kichikyoku_No` を取る。複数局の申請でも見るのはこの 1 つだけで、`TWTGM140` は見ない。申請No が無い、または物件申請情報に無いときは、エラーにせず先頭にする行が無いものとして並べる。開いたとき・出力のときに、その申請でこの画面を使えるかは確かめない。社外ユーザーの範囲は当てない。検索条件の初期値には使わない（1.6）
  - **CSV**（3.1〜3.6、Q-DS-CD-001・Q-DS-CD-002）：1 行は契約 1 件（計画基地局番号＋枝番）。列は出力 CSV の項目定義の 381 列（契約基本 46 列、契約者①〜⑤ 各 27 列、支払情報①〜④ 各 50 列）
    - 契約者①〜⑤：契約者情報から関係_地位（`RELATION`）に「旧」を含む行を除き、契約者区分の昇順・契約者番号の昇順で 1〜5 番目を入れる
    - 支払情報①〜④：契約支払情報のうち支払有効期間TO（`PAY_EFFECTIVE_TO`）が空の行を、支払内容区分の昇順で 1〜4 番目を入れる
    - どちらも枠を超えた行は出さず、足りない枠は空にする。`TWTGM040`・`TWTGM050`・`TWTGM060` は使わない
    - 見出し行は出力 CSV の項目定義の「見出し」のとおり（`TWTGD060` の列の表示名）。No 6 と No 44 は同じ見出し「契約基本_基地局名_ｶﾅ」で、値は No 6 が基地局名_ｶﾅ、No 44 が予備項目3。「ｶﾅ」と「カナ」の混在も表のとおり
    - 値はすべて文字列。日付は出力 CSV の項目定義で `YYYY/MM/DD` にしている列だけをその形で出し、ほかの列は元の値のまま。ただし、契約者①〜⑤_契約者区分は「契約者」「関係者」、法人_個人区分は「法人」「個人」（`P06` の名称と同じ）、契約基本_受電方法は予備項目4（`YOBI_KOMOKU4`）に値があればその値、空なら `ELECT_KIND` を「1:電力会社直受」「2:テナント受電」「3:ａｕ受電」の文字にして、ビュー `VWTGM010` で出す。支払情報①〜④_消費税扱いはコードのまま出す（取込はキー3 で照合する）（横断確認 1 回目 #1。出力 CSV の項目定義・作業用テーブルとビュー）
    - 並び：`ORDER BY CASE WHEN 基地局番号 ＝ 今の申請の基地局番号 THEN 1 ELSE 2 END, 基地局番号 昇順, 枝番 降順, 基地局名, 契約者①の法人名/個人名, 住居の都道府県コード, 市区町村コード, 字地番, 建物ビル`（同じ行を 2 回出さない形。Q-DS-CD-009 の 1）。今の申請の基地局番号が無ければ CASE はすべて 2 になる
    - 0 件（選んだ行から 1 行も作れなかった）のときは見出し行だけを出す
    - 件数の上限は設けない（3.4）
    - ファイル名は `WTG100_yyyyMMddHHmmss.csv`（出力した時刻。3.2）。文字コードは MS932（Java の `Windows-31J`）、書き方は `CsvUtils.defaultCsvConfig()`（カンマ区切り、全項目をダブルクォートで囲む、改行 CRLF、NULL は空文字）

### 論理データモデル（Logical Data Model）
> ドメインモデルをデータ構造として整理する節。

> _書き方_: 保存先の製品には依存させない。製品固有の話は物理データモデルに書く

- **エンティティ間の多重度（カーディナリティ）**: 契約 1 : 契約者情報 0..n（一覧は契約者区分 1 の先頭 1 行、CSV は①〜⑤）、契約 1 : 契約支払情報 0..n（CSV は支払有効期間TO が空の①〜④）、契約 0..1 : 計画マスタ（計画基地局番号）、計画マスタ 1 : 工事案件マスタ 0..n。作業用 `TWTGD050` は契約 1 につき 基本 1 行＋契約者 n 行＋支払 n 行、`TWTGD060` は契約 1 につき 1 行
- **属性と型**: 既存の表は読むだけ。作業用テーブルの列はすべて文字列（`TWTGD050` の処理順2 だけ数値）で、列名・型・桁は作業用テーブルとビューの定義のとおり
- **自然キー / 識別子**: 契約は「会社コード＋計画基地局番号＋枝番」。作業用テーブルの行は実行ユーザーID で分け、`TWTGD050` はデータ種別と処理順、`TWTGD060` は計画基地局番号＋枝番で識別する（キーの制約は持たない）
- **参照整合性のルール**: <DSN_LOGICAL_INTEGRITY>（不要：既存の表は読むだけで整合を保つ責任は持ち主にあり、作業用テーブルは出力のたびに作り直す写しで、外部キーを持たない — Q-DS-CD-002 の 2）

### 物理データモデル（Physical Data Model）
> 論理データモデルを実際の保存形式に落とした定義を書く節。

> _書き方_: 種別は RDB / Document Store / Event Store / KV・Wide-column などから選ぶ。RDB ならテーブル定義・主キー・外部キー・インデックス・分割方針、Document Store ならコレクション構造・埋め込みと参照の使い分け・シャードキーを書く。

| 種別 | 記載 |
|---|---|
| RDB（検索） | 表は変えない。主表 `TWTGM010`（`CompanyCD ＝ ログイン会社コード`）に `TWTGM020`・`TWTGM030`・`TWTBM010` を外部結合し、「会社コード＋計画基地局番号＋枝番」で GROUP BY する（GWTG004 と同じ）。件数を数えてから `ROW_NUMBER() OVER (ORDER BY …)` で表示ページの行だけを取る。ベンダー／施工会社の絞り込みは `TWTBM010`→`TWTBM080` の NOT EXISTS と EXISTS の OR で足す。コードの名称は `TWTZM040` を外部結合して引く |
| RDB（作業用。新規） | **`TWTGD050`（発行依頼書リバースデータ）**：60 列（実行ユーザーID・データ種別・処理順・計画基地局番号・枝番・項目1〜50・検索条件 4 列・処理順2）。**`TWTGD060`（発行依頼書フォーマット）**：実行ユーザーID（String 20）と CSV の 381 列（すべて String 500）。どちらも主キー・一意キー・索引・外部キー・共通列（会社コード・登録者・登録日時・更新者・更新日時・排他フラグ）を持たない。列名・型・桁は作業用テーブルとビューの定義のとおり（Q-DS-CD-002） |
| RDB（ビュー。新規） | **`VWTGM010`（発行依頼書リバースデータビュー）**：1基本情報（`TWTGM010` の全行。処理順2＝1）、2契約者（`TWTGM010` と `TWTGM020` を内部結合し、関係_地位に「旧」を含む行を除く。処理順2＝計画基地局番号＋枝番ごとに契約者区分・契約者番号の昇順の番号）、3支払情報（`TWTGM010` と `TWTGM030` を内部結合し、支払有効期間TO が空の行だけ。処理順2＝計画基地局番号＋枝番ごとに支払内容区分の昇順の番号）の 3 つの SELECT を UNION ALL する。コードの名称は `TWTZM040` を会社コード 'UQ' で引く。列はデータ種別ごとに意味が変わり、作業用テーブルとビューの定義のとおり（1基本情報の住居_字_地番・住居_建物_ビルは `TWTGM010` の `ADDRESS3`・`ADDRESS4`、登記_字_地番・登記_カナは `PLACE_ADDRESS3`・`PLACE_KANA` から取る。design-check 2 回目 #1）。表の「処理順_帳票用」の欄の式は使わず、上の処理順2 の式で作る（作業用テーブルとビューの定義の注記） |

#### 作業用テーブルとビューの定義

Q-DS-CD-002 の回答の別表。新しく作るのは次の 3 つ。

| 名前 | 種類 | 中身 |
|---|---|---|
| TWTGD050 発行依頼書リバースデータ | テーブル（作業用） | 選んだ契約の基本情報・契約者・支払情報を、VWTGM010 から 1 行ずつ写したもの（データ種別で列の意味が変わる） |
| TWTGD060 発行依頼書フォーマット | テーブル（作業用） | CSV の 1 行（契約 1 件）。実行ユーザーID（USER_ID、String 20）＋CSV の 381 列（全部 String 500）。列は 本書の `#### 出力 CSV の項目定義（381 列）` の「値を取る列（TWTGD060）」「物理名」のとおり |
| VWTGM010 発行依頼書リバースデータビュー | ビュー | TWTGM010・TWTGM020・TWTGM030 とコードマスタから、データ種別ごとに同じ列の形にそろえたもの |

- どれも主キー・一意キー・索引・外部キーを持たない。共通列（会社コード・登録者・登録日時・更新者・更新日時・排他フラグ）も持たない。
- 行は実行ユーザーID で分ける。

##### 出力ボタンを押したときの流れ
1. TWTGD050・TWTGD060 から、ログインユーザーの USER_ID の行を消す。
2. TWTGD050 を作る：VWTGM010 から、選んだ行（計画基地局番号＋枝番）の行を全部（1基本情報・2契約者・3支払情報）入れる。USER_ID はログインユーザー。
3. TWTGD060 を作る：TWTGD050 の「1基本情報」の行から 1 契約 1 行で入れる（実行ユーザーID と、契約基本の 46 列＝CSV の No 1〜46）。
4. TWTGD060 の契約者①〜⑤を埋める：TWTGD050 の「2契約者」の行のうち、処理順2（SYORI_JYUN2）が 1〜5 のものを、計画基地局番号＋枝番で突き合わせて更新する。
5. TWTGD060 の支払情報①〜④を埋める：TWTGD050 の「3支払情報」の行のうち、処理順2 が 1〜4 のものを同じように更新する。
6. TWTGD060 のログインユーザーの行を CSV の並び順で読み、CSV にする。
- 行は消さずに残し、次の出力のときに 1. で消す。

##### VWTGM010 の絞り込みと処理順2
- 1基本情報：TWTGM010 の全行。処理順2 は 1。
- 2契約者：TWTGM010 と TWTGM020 を内部結合。関係_地位（RELATION）に「旧」を含む行は除く。処理順2 は 計画基地局番号＋枝番ごとに 契約者区分・契約者番号 の昇順で振った番号。
- 3支払情報：TWTGM010 と TWTGM030 を内部結合。支払有効期間TO（PAY_EFFECTIVE_TO）が空の行だけ。処理順2 は 計画基地局番号＋枝番ごとに 支払内容区分 の昇順で振った番号。
- 下の列一覧の「処理順_帳票用」の欄は 3 つとも同じ式に見えるが、実際の式は上のとおり（ビューの DDL はこの式で作る）。
- 検索条件_確定局番 は 3 種類とも契約基本情報の基地局番号（KICHIKYOKU_NO）。

##### TWTGD050 発行依頼書リバースデータ（作業用。主キー・一意キー・索引なし）

| No | 論理名 | 列名 | 型 | 桁 | 備考 |
|---|---|---|---|---|---|
| 1 | 実行ﾕｰｻﾞｰID | USER_ID | 1:String | 20 |  |
| 2 | データ種別 | DATA_SHUBETSU | 1:String | 9 | 1基本情報 2契約者情報 3支払情報 |
| 3 | 処理順 | SYORI_JYUN | 1:String | 85 |  |
| 4 | 計画基地局番号 | KEIKAKU_KICHIKYOKU_NO | 1:String | 9 |  |
| 5 | 計画基地局枝番 | PLAN_SITEID_BRANCH | 1:String | 5 |  |
| 6 | 項目1 | FIELD_01 | 1:String | 120 | 項目1～項目50の保持する内容は、データ種別により異なる。 詳細は発行依頼書ﾘﾊﾞｰｽﾃﾞｰﾀビューを参照 |
| 7 | 項目2 | FIELD_02 | 1:String | 120 |  |
| 8 | 項目3 | FIELD_03 | 1:String | 40 |  |
| 9 | 項目4 | FIELD_04 | 1:String | 120 |  |
| 10 | 項目5 | FIELD_05 | 1:String | 120 |  |
| 11 | 項目6 | FIELD_06 | 1:String | 160 |  |
| 12 | 項目7 | FIELD_07 | 1:String | 160 |  |
| 13 | 項目8 | FIELD_08 | 1:String | 160 |  |
| 14 | 項目9 | FIELD_09 | 1:String | 50 |  |
| 15 | 項目10 | FIELD_10 | 1:String | 50 |  |
| 16 | 項目11 | FIELD_11 | 1:String | 50 |  |
| 17 | 項目12 | FIELD_12 | 1:String | 100 |  |
| 18 | 項目13 | FIELD_13 | 1:String | 100 |  |
| 19 | 項目14 | FIELD_14 | 1:String | 100 |  |
| 20 | 項目15 | FIELD_15 | 1:String | 160 |  |
| 21 | 項目16 | FIELD_16 | 1:String | 100 |  |
| 22 | 項目17 | FIELD_17 | 1:String | 100 |  |
| 23 | 項目18 | FIELD_18 | 1:String | 160 |  |
| 24 | 項目19 | FIELD_19 | 1:String | 50 |  |
| 25 | 項目20 | FIELD_20 | 1:String | 500 |  |
| 26 | 項目21 | FIELD_21 | 1:String | 160 |  |
| 27 | 項目22 | FIELD_22 | 1:String | 10 |  |
| 28 | 項目23 | FIELD_23 | 1:String | 240 |  |
| 29 | 項目24 | FIELD_24 | 1:String | 200 |  |
| 30 | 項目25 | FIELD_25 | 1:String | 200 |  |
| 31 | 項目26 | FIELD_26 | 1:String | 200 |  |
| 32 | 項目27 | FIELD_27 | 1:String | 200 |  |
| 33 | 項目28 | FIELD_28 | 1:String | 40 |  |
| 34 | 項目29 | FIELD_29 | 1:String | 40 |  |
| 35 | 項目30 | FIELD_30 | 1:String | 2 |  |
| 36 | 項目31 | FIELD_31 | 1:String | 50 |  |
| 37 | 項目32 | FIELD_32 | 1:String | 100 |  |
| 38 | 項目33 | FIELD_33 | 1:String | 100 |  |
| 39 | 項目34 | FIELD_34 | 1:String | 6 |  |
| 40 | 項目35 | FIELD_35 | 1:String | 50 |  |
| 41 | 項目36 | FIELD_36 | 1:String | 9 |  |
| 42 | 項目37 | FIELD_37 | 1:String | 6 |  |
| 43 | 項目38 | FIELD_38 | 1:String | 20 |  |
| 44 | 項目39 | FIELD_39 | 1:String | 50 |  |
| 45 | 項目40 | FIELD_40 | 1:String | 100 |  |
| 46 | 項目41 | FIELD_41 | 1:String | 100 |  |
| 47 | 項目42 | FIELD_42 | 1:String | 100 |  |
| 48 | 項目43 | FIELD_43 | 1:String | 200 |  |
| 49 | 項目44 | FIELD_44 | 1:String | 200 |  |
| 50 | 項目45 | FIELD_45 | 1:String | 200 |  |
| 51 | 項目46 | FIELD_46 | 1:String | 200 |  |
| 52 | 項目47 | FIELD_47 | 1:String | 4 |  |
| 53 | 項目48 | FIELD_48 | 1:String | 50 |  |
| 54 | 項目49 | FIELD_49 | 1:String | 30 |  |
| 55 | 項目50 | FIELD_50 | 1:String | 30 |  |
| 56 | 検索条件_登録状態 | STATUS_KIND | 1:String | 50 |  |
| 57 | 検索条件_代表契約局番 | REPRESENT_CONTRACT_NO | 1:String | 9 |  |
| 58 | 検索条件_代表契約枝番 | REPRESENT_CONTRACT_BRANCH_NO | 1:String | 5 |  |
| 59 | 検索条件_確定局番 | KICHIKYOKU_NO | 1:String | 9 |  |
| 60 | 処理順2 | SYORI_JYUN2 | 5:Currency | 5 |  |

##### VWTGM010 発行依頼書リバースデータビュー（3 つの SELECT を UNION ALL。データ種別で列の意味が変わる）

| No | 1基本情報：表示名 | 1基本情報：元 | 2契約者：表示名 | 2契約者：元 | 3支払情報：表示名 | 3支払情報：元 |
|---|---|---|---|---|---|---|
| 1 | データ種別 | 固定値：'1基本情報' | データ種別 | 固定値：'2契約者' | データ種別 | 固定値：'3支払情報' |
| 2 | 処理順 | 契約基本情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO \|\| '_' \|\| 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH \|\| '_' \|\| '1基本情報' | 処理順 | 契約者情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO \|\| '_'  \|\| 契約者情報ﾏｽﾀ.PLAN_SITEID_BRANCH  \|\| '_'  \|\| '2契約者' \|\| '_'  \|\| 契約者情報ﾏｽﾀ.CONSTRACT_KBN \|\| '_'  \|\| 契約者情報ﾏｽﾀ.CONSTRACT_CD | 処理順 | 契約支払情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO \|\| '_'  \|\| 契約支払情報ﾏｽﾀ.PLAN_SITEID_BRANCH \|\| '_'  \|\| '3支払情報' \|\|  '_'  \|\| 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND \|\|  '_'  \|\| 契約支払情報ﾏｽﾀ.PAY_CD \|\| '_'  \|\| 契約支払情報ﾏｽﾀ.PAY_CD_BRANCH |
| 3 | 計画基地局番号 | 契約基本情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO | 計画基地局番号 | 契約者情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO | 計画基地局番号 | 契約支払情報ﾏｽﾀ．KEIKAKU_KICHIKYOKU_NO |
| 4 | 計画基地局枝番 | 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH | 計画基地局枝番 | 契約者情報ﾏｽﾀ.PLAN_SITEID_BRANCH | 計画基地局枝番 | 契約支払情報ﾏｽﾀ.PLAN_SITEID_BRANCH |
| 5 | 計画基地局名 | 契約基本情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NAME | 契約者番号 | 契約者情報ﾏｽﾀ.CONSTRACT_CD | 支払番号 | 契約支払情報ﾏｽﾀ.PAY_CD |
| 6 | 計画基地局名_ｶﾅ | 契約基本情報ﾏｽﾀ.PLAN_STATION_KANA | 契約者区分 | 契約者情報ﾏｽﾀ.CONSTRACT_KBN を名称にする（1→「契約者」、2→「関係者」） | 支払番号枝番 | 契約支払情報ﾏｽﾀ.PAY_CD_BRANCH |
| 7 | 基地局番号 | 契約基本情報ﾏｽﾀ.KICHIKYOKU_NO | 関係_地位 | 契約者情報ﾏｽﾀ.RELATION | 支払内容区分 | 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND |
| 8 | 基地局名 | 契約基本情報ﾏｽﾀ.KICHIKYOKU_NAME | 法人_個人区分 | 契約者情報ﾏｽﾀ.CORP_PRIV_KBN を名称にする（1→「法人」、2→「個人」。P06 の名称と同じ） | 支払内容区分_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P17') |
| 9 | 基地局名_ｶﾅ | 契約基本情報ﾏｽﾀ.STATION_KANA | 法人名_個人名 | 契約者情報ﾏｽﾀ.NAME | 支払内容詳細区分 | 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND_SHOSAI |
| 10 | データ確定 | 契約基本情報ﾏｽﾀ.DATA_FIX_FLG (0:未確定、1:確定) | 法人名_個人名ｶﾅ | 契約者情報ﾏｽﾀ.NAME_KANA | 支払内容詳細区分_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',CODE,'C02') |
| 11 | 登録状態 | 契約基本情報ﾏｽﾀ.STATUS_KIND \|\| ':' \|\| ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P21') | 所属部署名 | 契約者情報ﾏｽﾀ.BELONGING_POST | 支払内容その他 | 契約支払情報ﾏｽﾀ.OTHER_PAYMENT_NAME |
| 12 | 転貸借 | 契約基本情報ﾏｽﾀ.MOVE_LEASE (0:転貸借以外、1:転貸借) | 所属部署名ｶﾅ | 契約者情報ﾏｽﾀ.BELONGING_POST_KANA | 案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 契約支払情報ﾏｽﾀ.ANKEN_DAI_GRP_CD |
| 13 | 住居_都道府県ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.ADDRESS_CD1 | 電話番号_固定 | 契約者情報ﾏｽﾀ.TEL1 | 案件大ｸﾞﾙｰﾌﾟ | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M10') |
| 14 | 住居_都道府県名 | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05') | 電話番号_携帯 | 契約者情報ﾏｽﾀ.TEL2 | 案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 契約支払情報ﾏｽﾀ.ANKEN_SYO_GRP_CD |
| 15 | 住居_市区町村ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.ADDRESS_CD2 | FAX番号 | 契約者情報ﾏｽﾀ.FAX | 案件小ｸﾞﾙｰﾌﾟ | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M11') |
| 16 | 住居_市区町村名 | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04') | メールアドレス | 契約者情報ﾏｽﾀ.MAIL | 採算管理区分 | 契約支払情報ﾏｽﾀ.PROFIT_MANAGE_KIND |
| 17 | 住居_字_地番 | 契約基本情報ﾏｽﾀ.ADDRESS3 | 郵便番号 | 契約者情報ﾏｽﾀ.ZIP1 \|\| '-' \|\| 契約者情報ﾏｽﾀ.ZIP2 | 支払先_契約先番号 | 契約支払情報ﾏｽﾀ.PAYMENT_PERSON |
| 18 | 住居_建物_ビル | 契約基本情報ﾏｽﾀ.ADDRESS4 | 都道府県 | 契約者情報ﾏｽﾀ.ADDRESS_CD1 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05')) | 支払方法 | 契約支払情報ﾏｽﾀ.PAYMENT_DDIVISION |
| 19 | 住居_カナ | 契約基本情報ﾏｽﾀ.KANA | 市区町村 | 契約者情報ﾏｽﾀ.ADDRESS_CD2 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04')) | 支払方法_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P18') |
| 20 | 登記_都道府県ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.PLACE_ADDRESS_CD1 | 字_地番 | 契約者情報ﾏｽﾀ.ADDRESS3 | 消費税扱い | 契約支払情報ﾏｽﾀ.TAX_KIND |
| 21 | 登記_都道府県名 | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05') | 建物_ビル | 契約者情報ﾏｽﾀ.ADDRESS4 | 消費税扱い_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P10') |
| 22 | 登記_市区町村ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.PLACE_ADDRESS_CD2 | カナ | 契約者情報ﾏｽﾀ.ADDRESS_KANA | 初回支払金額 | TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_FEE ) |
| 23 | 登記_市区町村名 | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04') | 書類 | 契約者情報ﾏｽﾀ.DOCUMENTS_KBN (1:送付先、2:送付禁止) | 初回支払消費税額 | TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_TAX ) |
| 24 | 登記_字_地番 | 契約基本情報ﾏｽﾀ.PLACE_ADDRESS3 | 電話 | 契約者情報ﾏｽﾀ.TEL_KBN (1:電話禁止) | 初回支払日 | TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_DATE ), 'YYYY/MM/DD' ) |
| 25 | 登記_カナ | 契約基本情報ﾏｽﾀ.PLACE_KANA | 詳細 | 契約者情報ﾏｽﾀ.DETAILS_KBN (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M01')) | 初回支払期間対象FROM | TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_FROM \|\| '01' ), 'YYYY/MM/DD' ) |
| 26 | 契約書の有無_賃貸借契約書 | 契約基本情報ﾏｽﾀ.CONTRACT_VALID1 (0:無、1:有) | ﾏｲﾅﾝﾊﾞｰ受領日 | 契約者情報ﾏｽﾀ.MY_NUMBER_DATE | 初回支払期間対象TO | TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_TO \|\| '01' ), 'YYYY/MM/DD' ) |
| 27 | 契約書の有無_転貸借契約書 | 契約基本情報ﾏｽﾀ.CONTRACT_VALID2 (0:無、1:有) | 備考 | 契約者情報ﾏｽﾀ.BIKO | 初回消費税調整額 | TO_CHAR(契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS ) |
| 28 | 契約書の有無_電気使用料覚書 | 契約基本情報ﾏｽﾀ.CONTRACT_VALID3 (0:無、1:有) | 予備項目1 | 契約者情報ﾏｽﾀ.YOBI_KOMOKU1 | 初回消費税調整理由 | 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_REASON |
| 29 | 契約書の有無_その他 | 契約基本情報ﾏｽﾀ.CONTRACT_VALID_OTHER | 予備項目2 | 契約者情報ﾏｽﾀ.YOBI_KOMOKU2 | 初回消費税調整理由_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') |
| 30 | 契約締結日 | TO_CHAR( TO_DATE(契約基本情報ﾏｽﾀ.CONTRACT_CONCLUSION_DATE ), 'YYYY/MM/DD' ) | 予備項目3 | 契約者情報ﾏｽﾀ.YOBI_KOMOKU3 | 初回消費税備考 | 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_MEMO |
| 31 | 契約開始日 | TO_CHAR( TO_DATE( 契約基本情報ﾏｽﾀ.CONTRACT_START_DATE ), 'YYYY/MM/DD' ) | 予備項目4 | 契約者情報ﾏｽﾀ.YOBI_KOMOKU4 | 継続支払金額 | TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_FEE ) |
| 32 | 契約終了日 | TO_CHAR( TO_DATE( 契約基本情報ﾏｽﾀ.CONTRACT_FINISH_DATE ), 'YYYY/MM/DD' ) | - | - | 継続支払消費税額 | TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_TAX ) |
| 33 | 解約日 | TO_CHAR( TO_DATE( 契約基本情報ﾏｽﾀ.CONTRACT_CALCELL_DATE ), 'YYYY/MM/DD' ) | - | - | 継続消費税調整額 | TO_CHAR( 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS ) |
| 34 | 更新年数_年単位 | 契約基本情報ﾏｽﾀ.UPDATE_YEAR | - | - | 継続消費税調整理由 | 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_REASON |
| 35 | 更新通知日_ヶ月前まで | 契約基本情報ﾏｽﾀ.UPDATE_NOTICE | - | - | 継続消費税調整理由_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') |
| 36 | 更新形態 | 契約基本情報ﾏｽﾀ.UPDATE_PATTERN (ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P07')) | - | - | 継続消費税備考 | 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_MEMO |
| 37 | 受電方法 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU4（予備項目4）に値があればその値。空なら ELECT_KIND を文字にする（1→「1:電力会社直受」、2→「2:テナント受電」、3→「3:ａｕ受電」） | - | - | 支払有効期間FROM | 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_FROM |
| 38 | 転貸借契約書ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.MOVE_LEASE_CONTRACT | - | - | 支払有効期間TO | 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_TO |
| 39 | 転貸借契約書名 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P15') | - | - | 月額契約金額_税抜 | TO_CHAR( 契約支払情報ﾏｽﾀ.MONTHLY_PAYMENT ) |
| 40 | 代表契約番号 | 契約基本情報ﾏｽﾀ.REPRESENT_CONTRACT_NO | - | - | 月額有効期間FROM | 契約支払情報ﾏｽﾀ. MONTHLY_PAY_EFFECTIVE_FROM |
| 41 | 代表契約枝番 | 契約基本情報ﾏｽﾀ. REPRESENT_CONTRACT_BRANCH_NO | - | - | 月額有効期間TO | 契約支払情報ﾏｽﾀ.MONTHLY_PAY_EFFECTIVE_TO |
| 42 | UQ押印者ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.UQ_SEALER | - | - | 請求方法区分 | 契約支払情報ﾏｽﾀ.CLAIM_INFOMATION_KIND |
| 43 | UQ押印者_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P24') | - | - | 支払種別 | 契約支払情報ﾏｽﾀ.PAYMENT_KIND |
| 44 | 予備項目1 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU1 | - | - | 支払種別_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P08') |
| 45 | 予備項目2 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU2 | - | - | 支払年 | 契約支払情報ﾏｽﾀ.PAYMENT_YEAR |
| 46 | 予備項目3 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU3 | - | - | 継続支払詳細_備考 | 契約支払情報ﾏｽﾀ.PAYMENT_MEMO |
| 47 | 予備項目4 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU4 | - | - | その他備考1 | 契約支払情報ﾏｽﾀ.MEMO1 |
| 48 | 予備項目5 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU5 | - | - | その他備考2 | 契約支払情報ﾏｽﾀ.MEMO2 |
| 49 | - | - | - | - | その他備考3 | 契約支払情報ﾏｽﾀ.MEMO3 |
| 50 | - | - | - | - | その他備考4 | 契約支払情報ﾏｽﾀ.MEMO4 |
| 51 | - | - | - | - | 請求予定月 | 契約支払情報ﾏｽﾀ.CLAIM_MONTH |
| 52 | - | - | - | - | 請求予定月_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P23') |
| 53 | - | - | - | - | 予備項目1 | 契約支払情報ﾏｽﾀ.YOBI_KOMOKU1 |
| 54 | - | - | - | - | 予備項目2 | 契約支払情報ﾏｽﾀ.YOBI_KOMOKU2 |
| 55 | 検索条件_登録状態 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P21') | 検索条件_登録状態 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P21') | 検索条件_登録状態 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P21') |
| 56 | 検索条件_代表契約局番 | 契約基本情報ﾏｽﾀ.REPRESENT_CONTRACT_NO | 検索条件_代表契約局番 | 契約基本情報ﾏｽﾀ.REPRESENT_CONTRACT_NO | 検索条件_代表契約局番 | 契約基本情報ﾏｽﾀ.REPRESENT_CONTRACT_NO |
| 57 | 検索条件_代表契約枝番 | 契約基本情報ﾏｽﾀ. REPRESENT_CONTRACT_BRANCH_NO | 検索条件_代表契約枝番 | 契約基本情報ﾏｽﾀ. REPRESENT_CONTRACT_BRANCH_NO | 検索条件_代表契約枝番 | 契約基本情報ﾏｽﾀ. REPRESENT_CONTRACT_BRANCH_NO |
| 58 | 検索条件_確定局番 | 契約基本情報ﾏｽﾀ.KICHIKYOKU_NO | 検索条件_確定局番 | 契約基本情報ﾏｽﾀ.KICHIKYOKU_NO | 検索条件_確定局番 | 契約基本情報ﾏｽﾀ.KICHIKYOKU_NO |
| 59 | 処理順_帳票用 | ROW_NUMBER() OVER  (PARTITION BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, GM30.PLAN_SITEID_BRANCH  ORDER BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH,  契約基本情報ﾏｽﾀ.FEE_MANAGE_KIND) | 処理順_帳票用 | ROW_NUMBER() OVER  (PARTITION BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, GM30.PLAN_SITEID_BRANCH  ORDER BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH,  契約基本情報ﾏｽﾀ.FEE_MANAGE_KIND) | 処理順_帳票用 | ROW_NUMBER() OVER  (PARTITION BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, GM30.PLAN_SITEID_BRANCH  ORDER BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH,  契約基本情報ﾏｽﾀ.FEE_MANAGE_KIND) |

#### 出力 CSV の項目定義（381 列）

Q-DS-CD-001 の回答の別表。

##### 書き方
- 1 行目は見出し行。見出しは下の表の「見出し」の文字そのまま（作業用テーブル TWTGD060 の列の表示名）。2 行目から、選んだ契約（契約基本情報 TWTGM010 の 計画基地局番号＋枝番）1 件につき 1 行。
- 文字コード MS932（Windows-31J）、カンマ区切り、全項目をダブルクォートで囲む、NULL は空文字（`CsvUtils.defaultCsvConfig()`）。
- 値はすべて文字列。日付は VWTGM010 の中で `YYYY/MM/DD` にしてある列だけがその形で、ほかの列（支払有効期間FROM/TO、月額有効期間FROM/TO、請求予定月など）は元の列の値そのまま。
- 0 件（選んだ行から 1 行も作れなかった）のときは見出し行だけを出す。
- 行の並び：今の申請（物件申請情報 TWTGM080 の 申請No）の基地局番号と同じ基地局番号の行を先頭にし、その中は枝番の降順。続けて残りの行を、基地局番号の昇順・枝番の降順・基地局名・契約者①の法人名/個人名・住居の都道府県コード・市区町村コード・字地番・建物ビルの昇順。今の申請の基地局番号の行が無ければ、全部を後半の順で並べる。

##### 契約者①〜⑤・支払情報①〜④の入れ方
- 契約者①〜⑤：その契約の契約者情報（TWTGM020）から、関係_地位（RELATION）に「旧」を含む行を除き、契約者区分（CONSTRACT_KBN）の昇順・契約者番号（CONSTRACT_CD）の昇順で 1〜5 番目を ①〜⑤ に入れる。6 番目以降は出さない。足りない枠は空。
- 支払情報①〜④：その契約の契約支払情報（TWTGM030）から、支払有効期間TO（PAY_EFFECTIVE_TO）が空の行だけを、支払内容区分（FEE_MANAGE_KIND）の昇順で 1〜4 番目を ①〜④ に入れる。5 番目以降は出さない。足りない枠は空。
- 契約支払金額（TWTGM040）・契約書（TWTGM050）・お客様番号（TWTGM060）は使わない。
- コード名称は、コードマスタ（TWTZM040）を会社コード 'UQ' で引いた名称（VWTGM010 の定義のとおり）。

##### 注意
- No 6 と No 44 は見出しが同じ「契約基本_基地局名_ｶﾅ」になる。No 6 の値は契約基本情報の基地局名_ｶﾅ（STATION_KANA）、No 44 の値は契約基本情報の予備項目3（YOBI_KOMOKU3）。
- 見出しの「ｶﾅ」と「カナ」は表のとおり混在している（例：No 17「契約基本_住居_カナ」、No 3「契約基本_計画基地局名_ｶﾅ」）。表の文字のとおりに出す。

##### 項目一覧
「取得元」の `\|\|` は SQL の文字列連結。「取込側の型・バイト数」は契約情報取込で受け取るときの型・バイト数で、参考。

| No | 見出し（CSV の 1 行目） | 値を取る列（TWTGD060） | 物理名 | 取得元（VWTGM010 の列 ← 元の表の列） | 出力項目名（参考。接頭辞の無い呼び方） | 取込側の型・バイト数 |
|---|---|---|---|---|---|---|
| 1 | 契約基本_計画基地局番号 | 契約基本_計画基地局番号 | KEIKAKU_KICHIKYOKU_NO | VWTGM010.計画基地局番号 ← 契約基本情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO（TWTGD050 の同名列を経由） | 計画基地局番号 | 半角英数 9 |
| 2 | 契約基本_計画基地局名 | 契約基本_計画基地局名 | KEIKAKU_KICHIKYOKU_NAME | VWTGM010.計画基地局名 ← 契約基本情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NAME | 計画基地局名 | ー ー |
| 3 | 契約基本_計画基地局名_ｶﾅ | 契約基本_計画基地局名_ｶﾅ | PLAN_STATION_KANA | VWTGM010.計画基地局名_ｶﾅ ← 契約基本情報ﾏｽﾀ.PLAN_STATION_KANA | 計画基地局名_ｶﾅ | ー ー |
| 4 | 契約基本_基地局番号 | 契約基本_基地局番号 | KICHIKYOKU_NO | VWTGM010.基地局番号 ← 契約基本情報ﾏｽﾀ.KICHIKYOKU_NO | 基地局番号 | 半角英数 9 |
| 5 | 契約基本_基地局名 | 契約基本_基地局名 | KICHIKYOKU_NAME | VWTGM010.基地局名 ← 契約基本情報ﾏｽﾀ.KICHIKYOKU_NAME | 基地局名 | ー ー |
| 6 | 契約基本_基地局名_ｶﾅ | 契約基本_基地局名_ｶﾅ | STATION_KANA | VWTGM010.基地局名_ｶﾅ ← 契約基本情報ﾏｽﾀ.STATION_KANA | 基地局名_ｶﾅ | ー ー |
| 7 | 契約基本_計画基地局枝番 | 契約基本_計画基地局枝番 | PLAN_SITEID_BRANCH | VWTGM010.計画基地局枝番 ← 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH（TWTGD050 の同名列を経由） | 計画基地局枝番 | 半角英数 5 |
| 8 | 契約基本_データ確定 | 契約基本_データ確定 | DATA_FIX_FLG | VWTGM010.データ確定 ← 契約基本情報ﾏｽﾀ.DATA_FIX_FLG (0:未確定、1:確定) | データ確定 | ー ー |
| 9 | 契約基本_登録状態 | 契約基本_登録状態 | STATUS_KIND | VWTGM010.登録状態 ← 契約基本情報ﾏｽﾀ.STATUS_KIND \|\| ':' \|\| ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P21') | 登録状態 | ー ー |
| 10 | 契約基本_転貸借 | 契約基本_転貸借 | MOVE_LEASE | VWTGM010.転貸借 ← 契約基本情報ﾏｽﾀ.MOVE_LEASE (0:転貸借以外、1:転貸借) | 転貸借 | ー ー |
| 11 | 契約基本_住居_都道府県ｺｰﾄﾞ | 契約基本_住居_都道府県ｺｰﾄﾞ | ADDRESS_CD1 | VWTGM010.住居_都道府県ｺｰﾄﾞ ← 契約基本情報ﾏｽﾀ.ADDRESS_CD1 | 住居_都道府県ｺｰﾄﾞ | 半角英数 2 |
| 12 | 契約基本_住居_都道府県名 | 契約基本_住居_都道府県名 | ADDRESS_CD1_NM | VWTGM010.住居_都道府県名 ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05') | 住居_都道府県名 | ー ー |
| 13 | 契約基本_住居_市区町村ｺｰﾄﾞ | 契約基本_住居_市区町村ｺｰﾄﾞ | ADDRESS_CD2 | VWTGM010.住居_市区町村ｺｰﾄﾞ ← 契約基本情報ﾏｽﾀ.ADDRESS_CD2 | 住居_市区町村ｺｰﾄﾞ | 半角英数 5 |
| 14 | 契約基本_住居_市区町村名 | 契約基本_住居_市区町村名 | ADDRESS_CD2_NM | VWTGM010.住居_市区町村名 ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04') | 住居_市区町村名 | 全角 50 |
| 15 | 契約基本_住居_字_地番 | 契約基本_住居_字_地番 | ADDRESS3 | VWTGM010.住居_字_地番 ← 契約基本情報ﾏｽﾀ.ADDRESS3 | 住居_字_地番 | 全角 100 |
| 16 | 契約基本_住居_建物_ビル | 契約基本_住居_建物_ビル | ADDRESS4 | VWTGM010.住居_建物_ビル ← 契約基本情報ﾏｽﾀ.ADDRESS4 | 住居_建物_ビル | 全角 100 |
| 17 | 契約基本_住居_カナ | 契約基本_住居_カナ | KANA | VWTGM010.住居_カナ ← 契約基本情報ﾏｽﾀ.KANA | 住居_カナ | ー ー |
| 18 | 契約基本_登記_都道府県ｺｰﾄﾞ | 契約基本_登記_都道府県ｺｰﾄﾞ | PLACE_ADDRESS_CD1 | VWTGM010.登記_都道府県ｺｰﾄﾞ ← 契約基本情報ﾏｽﾀ.PLACE_ADDRESS_CD1 | 登記_都道府県ｺｰﾄﾞ | 半角英数 2 |
| 19 | 契約基本_登記_都道府県名 | 契約基本_登記_都道府県名 | PLACE_ADDRESS_CD1_NM | VWTGM010.登記_都道府県名 ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05') | 登記_都道府県名 | ー ー |
| 20 | 契約基本_登記_市区町村ｺｰﾄﾞ | 契約基本_登記_市区町村ｺｰﾄﾞ | PLACE_ADDRESS_CD2 | VWTGM010.登記_市区町村ｺｰﾄﾞ ← 契約基本情報ﾏｽﾀ.PLACE_ADDRESS_CD2 | 登記_市区町村ｺｰﾄﾞ | 半角英数 5 |
| 21 | 契約基本_登記_市区町村名 | 契約基本_登記_市区町村名 | PLACE_ADDRESS_CD2_NM | VWTGM010.登記_市区町村名 ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04') | 登記_市区町村名 | 全角 50 |
| 22 | 契約基本_登記_字_地番 | 契約基本_登記_字_地番 | PLACE_ADDRESS3 | VWTGM010.登記_字_地番 ← 契約基本情報ﾏｽﾀ.PLACE_ADDRESS3 | 登記_字_地番 | 全角 100 |
| 23 | 契約基本_登記_カナ | 契約基本_登記_カナ | PLACE_KANA | VWTGM010.登記_カナ ← 契約基本情報ﾏｽﾀ.PLACE_KANA | 登記_カナ | ー ー |
| 24 | 契約基本_契約書の有無_賃貸借契約書 | 契約基本_契約書の有無_賃貸借契約書 | CONTRACT_VALID1 | VWTGM010.契約書の有無_賃貸借契約書 ← 契約基本情報ﾏｽﾀ.CONTRACT_VALID1 (0:無、1:有) | 契約書の有無_賃貸借契約書 | ー ー |
| 25 | 契約基本_契約書の有無_転貸借契約書 | 契約基本_契約書の有無_転貸借契約書 | CONTRACT_VALID2 | VWTGM010.契約書の有無_転貸借契約書 ← 契約基本情報ﾏｽﾀ.CONTRACT_VALID2 (0:無、1:有) | 契約書の有無_転貸借契約書 | ー ー |
| 26 | 契約基本_契約書の有無_電気使用料覚書 | 契約基本_契約書の有無_電気使用料覚書 | CONTRACT_VALID3 | VWTGM010.契約書の有無_電気使用料覚書 ← 契約基本情報ﾏｽﾀ.CONTRACT_VALID3 (0:無、1:有) | 契約書の有無_電気使用料覚書 | ー ー |
| 27 | 契約基本_契約書の有無_その他 | 契約基本_契約書の有無_その他 | CONTRACT_VALID_OTHER | VWTGM010.契約書の有無_その他 ← 契約基本情報ﾏｽﾀ.CONTRACT_VALID_OTHER | 契約書の有無_その他 | ー ー |
| 28 | 契約基本_契約締結日 | 契約基本_契約締結日 | CONTRACT_CONCLUSION_DATE | VWTGM010.契約締結日 ← TO_CHAR( TO_DATE(契約基本情報ﾏｽﾀ.CONTRACT_CONCLUSION_DATE ), 'YYYY/MM/DD' ) | 契約締結日 | ー ー |
| 29 | 契約基本_契約開始日 | 契約基本_契約開始日 | CONTRACT_START_DATE | VWTGM010.契約開始日 ← TO_CHAR( TO_DATE( 契約基本情報ﾏｽﾀ.CONTRACT_START_DATE ), 'YYYY/MM/DD' ) | 契約開始日 | ー ー |
| 30 | 契約基本_契約終了日 | 契約基本_契約終了日 | CONTRACT_FINISH_DATE | VWTGM010.契約終了日 ← TO_CHAR( TO_DATE( 契約基本情報ﾏｽﾀ.CONTRACT_FINISH_DATE ), 'YYYY/MM/DD' ) | 契約終了日 | ー ー |
| 31 | 契約基本_解約日 | 契約基本_解約日 | CONTRACT_CALCELL_DATE | VWTGM010.解約日 ← TO_CHAR( TO_DATE( 契約基本情報ﾏｽﾀ.CONTRACT_CALCELL_DATE ), 'YYYY/MM/DD' ) | 解約日 | ー ー |
| 32 | 契約基本_更新年数_年単位 | 契約基本_更新年数_年単位 | UPDATE_YEAR | VWTGM010.更新年数_年単位 ← 契約基本情報ﾏｽﾀ.UPDATE_YEAR | 更新年数_年単位 | ー ー |
| 33 | 契約基本_更新通知日_ヶ月前まで | 契約基本_更新通知日_ヶ月前まで | UPDATE_NOTICE | VWTGM010.更新通知日_ヶ月前まで ← 契約基本情報ﾏｽﾀ.UPDATE_NOTICE | 更新通知日_ヶ月前まで | ー ー |
| 34 | 契約基本_更新形態 | 契約基本_更新形態 | UPDATE_PATTERN | VWTGM010.更新形態 ← 契約基本情報ﾏｽﾀ.UPDATE_PATTERN (ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P07')) | 更新形態 | ー ー |
| 35 | 契約基本_受電方法 | 契約基本_受電方法 | ELECT_KIND | VWTGM010.受電方法 ← 契約基本情報ﾏｽﾀ.YOBI_KOMOKU4（予備項目4）に値があればその値。空なら ELECT_KIND を文字にする（1→「1:電力会社直受」、2→「2:テナント受電」、3→「3:ａｕ受電」） | 受電方法 | 全角 ー |
| 36 | 契約基本_転貸借契約書ｺｰﾄﾞ | 契約基本_転貸借契約書ｺｰﾄﾞ | MOVE_LEASE_CONTRACT | VWTGM010.転貸借契約書ｺｰﾄﾞ ← 契約基本情報ﾏｽﾀ.MOVE_LEASE_CONTRACT | 転貸借契約書ｺｰﾄﾞ | ー ー |
| 37 | 契約基本_転貸借契約書名 | 契約基本_転貸借契約書名 | MOVE_LEASE_CONTRACT_NM | VWTGM010.転貸借契約書名 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P15') | 転貸借契約書名 | ー ー |
| 38 | 契約基本_代表契約番号 | 契約基本_代表契約番号 | REPRESENT_CONTRACT_NO | VWTGM010.代表契約番号 ← 契約基本情報ﾏｽﾀ.REPRESENT_CONTRACT_NO | 代表契約番号 | 半角英数 9 |
| 39 | 契約基本_代表契約枝番 | 契約基本_代表契約枝番 | REPRESENT_CONTRACT_BRANCH_NO | VWTGM010.代表契約枝番 ← 契約基本情報ﾏｽﾀ. REPRESENT_CONTRACT_BRANCH_NO | 代表契約枝番 | 半角英数 5 |
| 40 | 契約基本_UQ押印者ｺｰﾄﾞ | 契約基本_UQ押印者ｺｰﾄﾞ | UQ_SEALER | VWTGM010.UQ押印者ｺｰﾄﾞ ← 契約基本情報ﾏｽﾀ.UQ_SEALER | UQ押印者ｺｰﾄﾞ | 半角英数 2 |
| 41 | 契約基本_UQ押印者_名称 | 契約基本_UQ押印者_名称 | UQ_SEALER_NM | VWTGM010.UQ押印者_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P24') | UQ押印者_名称 | ー ー |
| 42 | 契約基本_予備項目1 | 契約基本_予備項目1 | YOBI_KOMOKU1 | VWTGM010.予備項目1 ← 契約基本情報ﾏｽﾀ.YOBI_KOMOKU1 | 予備項目1 | 全角 100 |
| 43 | 契約基本_予備項目2 | 契約基本_予備項目2 | YOBI_KOMOKU2 | VWTGM010.予備項目2 ← 契約基本情報ﾏｽﾀ.YOBI_KOMOKU2 | 予備項目2 | 全角 100 |
| 44 | 契約基本_基地局名_ｶﾅ | 契約基本_基地局名_ｶﾅ | YOBI_KOMOKU3 | VWTGM010.予備項目3 ← 契約基本情報ﾏｽﾀ.YOBI_KOMOKU3 | 予備項目3_基地局名_ｶﾅ | ー ー |
| 45 | 契約基本_予備項目4 | 契約基本_予備項目4 | YOBI_KOMOKU4 | VWTGM010.予備項目4 ← 契約基本情報ﾏｽﾀ.YOBI_KOMOKU4 | 予備項目4 | ー ー |
| 46 | 契約基本_予備項目5 | 契約基本_予備項目5 | YOBI_KOMOKU5 | VWTGM010.予備項目5 ← 契約基本情報ﾏｽﾀ.YOBI_KOMOKU5 | 予備項目5 | ー ー |
| 47 | 契約者①_契約者番号 | 契約者①_契約者番号 | CONSTRACT_CD_1 | VWTGM010（2契約者・処理順2=1）.契約者番号 ← 契約者情報ﾏｽﾀ.CONSTRACT_CD | ①_契約者番号 | 全角 20 |
| 48 | 契約者①_契約者区分 | 契約者①_契約者区分 | CONSTRACT_KBN_1 | VWTGM010（2契約者・処理順2=1）.契約者区分 ← 契約者情報ﾏｽﾀ.CONSTRACT_KBN を名称にする（1→「契約者」、2→「関係者」） | ①_契約者区分 | 全角 2 |
| 49 | 契約者①_関係_地位 | 契約者①_関係_地位 | RELATION_1 | VWTGM010（2契約者・処理順2=1）.関係_地位 ← 契約者情報ﾏｽﾀ.RELATION | ①_関係_地位 | 全角 40 |
| 50 | 契約者①_法人_個人区分 | 契約者①_法人_個人区分 | CORP_PRIV_KBN_1 | VWTGM010（2契約者・処理順2=1）.法人_個人区分 ← 契約者情報ﾏｽﾀ.CORP_PRIV_KBN を名称にする（1→「法人」、2→「個人」。P06 の名称と同じ） | ①_法人_個人区分 | 全角 2 |
| 51 | 契約者①_法人名_個人名 | 契約者①_法人名_個人名 | NAME_1 | VWTGM010（2契約者・処理順2=1）.法人名_個人名 ← 契約者情報ﾏｽﾀ.NAME | ①_法人名_個人名 | 全角 120 |
| 52 | 契約者①_法人名_個人名ｶﾅ | 契約者①_法人名_個人名ｶﾅ | NAME_KANA_1 | VWTGM010（2契約者・処理順2=1）.法人名_個人名ｶﾅ ← 契約者情報ﾏｽﾀ.NAME_KANA | ①_法人名_個人名ｶﾅ | 半角 160 |
| 53 | 契約者①_所属部署名 | 契約者①_所属部署名 | BELONGING_POST_1 | VWTGM010（2契約者・処理順2=1）.所属部署名 ← 契約者情報ﾏｽﾀ.BELONGING_POST | ①_所属部署名 | 全角 160 |
| 54 | 契約者①_所属部署名ｶﾅ | 契約者①_所属部署名ｶﾅ | BELONGING_POST_KANA_1 | VWTGM010（2契約者・処理順2=1）.所属部署名ｶﾅ ← 契約者情報ﾏｽﾀ.BELONGING_POST_KANA | ①_所属部署名ｶﾅ | 半角 160 |
| 55 | 契約者①_電話番号_固定 | 契約者①_電話番号_固定 | TEL1_1 | VWTGM010（2契約者・処理順2=1）.電話番号_固定 ← 契約者情報ﾏｽﾀ.TEL1 | ①_電話番号_固定 | 数値 11 |
| 56 | 契約者①_電話番号_携帯 | 契約者①_電話番号_携帯 | TEL2_1 | VWTGM010（2契約者・処理順2=1）.電話番号_携帯 ← 契約者情報ﾏｽﾀ.TEL2 | ①_電話番号_携帯 | 数値 11 |
| 57 | 契約者①_FAX番号 | 契約者①_FAX番号 | FAX_1 | VWTGM010（2契約者・処理順2=1）.FAX番号 ← 契約者情報ﾏｽﾀ.FAX | ①_FAX番号 | 数値 10 |
| 58 | 契約者①_メールアドレス | 契約者①_メールアドレス | MAIL_1 | VWTGM010（2契約者・処理順2=1）.メールアドレス ← 契約者情報ﾏｽﾀ.MAIL | ①_メールアドレス | 半角英数 100 |
| 59 | 契約者①_郵便番号 | 契約者①_郵便番号 | ZIP_1 | VWTGM010（2契約者・処理順2=1）.郵便番号 ← 契約者情報ﾏｽﾀ.ZIP1 \|\| '-' \|\| 契約者情報ﾏｽﾀ.ZIP2 | ①_郵便番号 | 半角 8 |
| 60 | 契約者①_都道府県 | 契約者①_都道府県 | ADDRESS_CD1_1 | VWTGM010（2契約者・処理順2=1）.都道府県 ← 契約者情報ﾏｽﾀ.ADDRESS_CD1 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05')) | ①_都道府県 | 全角 50 |
| 61 | 契約者①_市区町村 | 契約者①_市区町村 | ADDRESS_CD2_1 | VWTGM010（2契約者・処理順2=1）.市区町村 ← 契約者情報ﾏｽﾀ.ADDRESS_CD2 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04')) | ①_市区町村 | 全角 50 |
| 62 | 契約者①_字_地番 | 契約者①_字_地番 | ADDRESS3_1 | VWTGM010（2契約者・処理順2=1）.字_地番 ← 契約者情報ﾏｽﾀ.ADDRESS3 | ①_字_地番 | 全角 100 |
| 63 | 契約者①_建物_ビル | 契約者①_建物_ビル | ADDRESS4_1 | VWTGM010（2契約者・処理順2=1）.建物_ビル ← 契約者情報ﾏｽﾀ.ADDRESS4 | ①_建物_ビル | 全角 100 |
| 64 | 契約者①_カナ | 契約者①_カナ | ADDRESS_KANA_1 | VWTGM010（2契約者・処理順2=1）.カナ ← 契約者情報ﾏｽﾀ.ADDRESS_KANA | ①_カナ | ー ー |
| 65 | 契約者①_書類 | 契約者①_書類 | DOCUMENTS_KBN_1 | VWTGM010（2契約者・処理順2=1）.書類 ← 契約者情報ﾏｽﾀ.DOCUMENTS_KBN (1:送付先、2:送付禁止) | ①_書類 | ー ー |
| 66 | 契約者①_電話 | 契約者①_電話 | TEL_KBN_1 | VWTGM010（2契約者・処理順2=1）.電話 ← 契約者情報ﾏｽﾀ.TEL_KBN (1:電話禁止) | ①_電話 | ー ー |
| 67 | 契約者①_詳細 | 契約者①_詳細 | DETAILS_KBN_1 | VWTGM010（2契約者・処理順2=1）.詳細 ← 契約者情報ﾏｽﾀ.DETAILS_KBN (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M01')) | ①_詳細 | ー ー |
| 68 | 契約者①_ﾏｲﾅﾝﾊﾞｰ受領日 | 契約者①_ﾏｲﾅﾝﾊﾞｰ受領日 | MY_NUMBER_DATE_1 | VWTGM010（2契約者・処理順2=1）.ﾏｲﾅﾝﾊﾞｰ受領日 ← 契約者情報ﾏｽﾀ.MY_NUMBER_DATE | ①_ﾏｲﾅﾝﾊﾞｰ受領日 | ー ー |
| 69 | 契約者①_備考 | 契約者①_備考 | BIKO_1 | VWTGM010（2契約者・処理順2=1）.備考 ← 契約者情報ﾏｽﾀ.BIKO | ①_備考 | ー ー |
| 70 | 契約者①_予備項目1 | 契約者①_予備項目1 | YOBI_KOMOKU1_1 | VWTGM010（2契約者・処理順2=1）.予備項目1 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU1 | ①_予備項目1 | ー ー |
| 71 | 契約者①_予備項目2 | 契約者①_予備項目2 | YOBI_KOMOKU2_1 | VWTGM010（2契約者・処理順2=1）.予備項目2 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU2 | ①_予備項目2 | ー ー |
| 72 | 契約者①_予備項目3 | 契約者①_予備項目3 | YOBI_KOMOKU3_1 | VWTGM010（2契約者・処理順2=1）.予備項目3 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU3 | ①_予備項目3 | ー ー |
| 73 | 契約者①_予備項目4 | 契約者①_予備項目4 | YOBI_KOMOKU4_1 | VWTGM010（2契約者・処理順2=1）.予備項目4 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU4 | ①_予備項目4 | ー ー |
| 74 | 契約者②_契約者番号 | 契約者②_契約者番号 | CONSTRACT_CD_2 | VWTGM010（2契約者・処理順2=2）.契約者番号 ← 契約者情報ﾏｽﾀ.CONSTRACT_CD | ②_契約者番号 | 全角 20 |
| 75 | 契約者②_契約者区分 | 契約者②_契約者区分 | CONSTRACT_KBN_2 | VWTGM010（2契約者・処理順2=2）.契約者区分 ← 契約者情報ﾏｽﾀ.CONSTRACT_KBN を名称にする（1→「契約者」、2→「関係者」） | ②_契約者区分 | 全角 2 |
| 76 | 契約者②_関係_地位 | 契約者②_関係_地位 | RELATION_2 | VWTGM010（2契約者・処理順2=2）.関係_地位 ← 契約者情報ﾏｽﾀ.RELATION | ②_関係_地位 | 全角 40 |
| 77 | 契約者②_法人_個人区分 | 契約者②_法人_個人区分 | CORP_PRIV_KBN_2 | VWTGM010（2契約者・処理順2=2）.法人_個人区分 ← 契約者情報ﾏｽﾀ.CORP_PRIV_KBN を名称にする（1→「法人」、2→「個人」。P06 の名称と同じ） | ②_法人_個人区分 | 全角 2 |
| 78 | 契約者②_法人名_個人名 | 契約者②_法人名_個人名 | NAME_2 | VWTGM010（2契約者・処理順2=2）.法人名_個人名 ← 契約者情報ﾏｽﾀ.NAME | ②_法人名_個人名 | 全角 120 |
| 79 | 契約者②_法人名_個人名ｶﾅ | 契約者②_法人名_個人名ｶﾅ | NAME_KANA_2 | VWTGM010（2契約者・処理順2=2）.法人名_個人名ｶﾅ ← 契約者情報ﾏｽﾀ.NAME_KANA | ②_法人名_個人名ｶﾅ | 半角 160 |
| 80 | 契約者②_所属部署名 | 契約者②_所属部署名 | BELONGING_POST_2 | VWTGM010（2契約者・処理順2=2）.所属部署名 ← 契約者情報ﾏｽﾀ.BELONGING_POST | ②_所属部署名 | 全角 160 |
| 81 | 契約者②_所属部署名ｶﾅ | 契約者②_所属部署名ｶﾅ | BELONGING_POST_KANA_2 | VWTGM010（2契約者・処理順2=2）.所属部署名ｶﾅ ← 契約者情報ﾏｽﾀ.BELONGING_POST_KANA | ②_所属部署名ｶﾅ | 半角 160 |
| 82 | 契約者②_電話番号_固定 | 契約者②_電話番号_固定 | TEL1_2 | VWTGM010（2契約者・処理順2=2）.電話番号_固定 ← 契約者情報ﾏｽﾀ.TEL1 | ②_電話番号_固定 | 数値 11 |
| 83 | 契約者②_電話番号_携帯 | 契約者②_電話番号_携帯 | TEL2_2 | VWTGM010（2契約者・処理順2=2）.電話番号_携帯 ← 契約者情報ﾏｽﾀ.TEL2 | ②_電話番号_携帯 | 数値 11 |
| 84 | 契約者②_FAX番号 | 契約者②_FAX番号 | FAX_2 | VWTGM010（2契約者・処理順2=2）.FAX番号 ← 契約者情報ﾏｽﾀ.FAX | ②_FAX番号 | 数値 10 |
| 85 | 契約者②_メールアドレス | 契約者②_メールアドレス | MAIL_2 | VWTGM010（2契約者・処理順2=2）.メールアドレス ← 契約者情報ﾏｽﾀ.MAIL | ②_メールアドレス | 半角英数 100 |
| 86 | 契約者②_郵便番号 | 契約者②_郵便番号 | ZIP_2 | VWTGM010（2契約者・処理順2=2）.郵便番号 ← 契約者情報ﾏｽﾀ.ZIP1 \|\| '-' \|\| 契約者情報ﾏｽﾀ.ZIP2 | ②_郵便番号 | 半角 8 |
| 87 | 契約者②_都道府県 | 契約者②_都道府県 | ADDRESS_CD1_2 | VWTGM010（2契約者・処理順2=2）.都道府県 ← 契約者情報ﾏｽﾀ.ADDRESS_CD1 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05')) | ②_都道府県 | 全角 50 |
| 88 | 契約者②_市区町村 | 契約者②_市区町村 | ADDRESS_CD2_2 | VWTGM010（2契約者・処理順2=2）.市区町村 ← 契約者情報ﾏｽﾀ.ADDRESS_CD2 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04')) | ②_市区町村 | 全角 50 |
| 89 | 契約者②_字_地番 | 契約者②_字_地番 | ADDRESS3_2 | VWTGM010（2契約者・処理順2=2）.字_地番 ← 契約者情報ﾏｽﾀ.ADDRESS3 | ②_字_地番 | 全角 100 |
| 90 | 契約者②_建物_ビル | 契約者②_建物_ビル | ADDRESS4_2 | VWTGM010（2契約者・処理順2=2）.建物_ビル ← 契約者情報ﾏｽﾀ.ADDRESS4 | ②_建物_ビル | 全角 100 |
| 91 | 契約者②_カナ | 契約者②_カナ | ADDRESS_KANA_2 | VWTGM010（2契約者・処理順2=2）.カナ ← 契約者情報ﾏｽﾀ.ADDRESS_KANA | ②_カナ | ー ー |
| 92 | 契約者②_書類 | 契約者②_書類 | DOCUMENTS_KBN_2 | VWTGM010（2契約者・処理順2=2）.書類 ← 契約者情報ﾏｽﾀ.DOCUMENTS_KBN (1:送付先、2:送付禁止) | ②_書類 | ー ー |
| 93 | 契約者②_電話 | 契約者②_電話 | TEL_KBN_2 | VWTGM010（2契約者・処理順2=2）.電話 ← 契約者情報ﾏｽﾀ.TEL_KBN (1:電話禁止) | ②_電話 | ー ー |
| 94 | 契約者②_詳細 | 契約者②_詳細 | DETAILS_KBN_2 | VWTGM010（2契約者・処理順2=2）.詳細 ← 契約者情報ﾏｽﾀ.DETAILS_KBN (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M01')) | ②_詳細 | ー ー |
| 95 | 契約者②_ﾏｲﾅﾝﾊﾞｰ受領日 | 契約者②_ﾏｲﾅﾝﾊﾞｰ受領日 | MY_NUMBER_DATE_2 | VWTGM010（2契約者・処理順2=2）.ﾏｲﾅﾝﾊﾞｰ受領日 ← 契約者情報ﾏｽﾀ.MY_NUMBER_DATE | ②_ﾏｲﾅﾝﾊﾞｰ受領日 | ー ー |
| 96 | 契約者②_備考 | 契約者②_備考 | BIKO_2 | VWTGM010（2契約者・処理順2=2）.備考 ← 契約者情報ﾏｽﾀ.BIKO | ②_備考 | ー ー |
| 97 | 契約者②_予備項目1 | 契約者②_予備項目1 | YOBI_KOMOKU1_2 | VWTGM010（2契約者・処理順2=2）.予備項目1 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU1 | ②_予備項目1 | ー ー |
| 98 | 契約者②_予備項目2 | 契約者②_予備項目2 | YOBI_KOMOKU2_2 | VWTGM010（2契約者・処理順2=2）.予備項目2 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU2 | ②_予備項目2 | ー ー |
| 99 | 契約者②_予備項目3 | 契約者②_予備項目3 | YOBI_KOMOKU3_2 | VWTGM010（2契約者・処理順2=2）.予備項目3 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU3 | ②_予備項目3 | ー ー |
| 100 | 契約者②_予備項目4 | 契約者②_予備項目4 | YOBI_KOMOKU4_2 | VWTGM010（2契約者・処理順2=2）.予備項目4 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU4 | ②_予備項目4 | ー ー |
| 101 | 契約者③_契約者番号 | 契約者③_契約者番号 | CONSTRACT_CD_3 | VWTGM010（2契約者・処理順2=3）.契約者番号 ← 契約者情報ﾏｽﾀ.CONSTRACT_CD | ③_契約者番号 | 全角 20 |
| 102 | 契約者③_契約者区分 | 契約者③_契約者区分 | CONSTRACT_KBN_3 | VWTGM010（2契約者・処理順2=3）.契約者区分 ← 契約者情報ﾏｽﾀ.CONSTRACT_KBN を名称にする（1→「契約者」、2→「関係者」） | ③_契約者区分 | 全角 2 |
| 103 | 契約者③_関係_地位 | 契約者③_関係_地位 | RELATION_3 | VWTGM010（2契約者・処理順2=3）.関係_地位 ← 契約者情報ﾏｽﾀ.RELATION | ③_関係_地位 | 全角 40 |
| 104 | 契約者③_法人_個人区分 | 契約者③_法人_個人区分 | CORP_PRIV_KBN_3 | VWTGM010（2契約者・処理順2=3）.法人_個人区分 ← 契約者情報ﾏｽﾀ.CORP_PRIV_KBN を名称にする（1→「法人」、2→「個人」。P06 の名称と同じ） | ③_法人_個人区分 | 全角 2 |
| 105 | 契約者③_法人名_個人名 | 契約者③_法人名_個人名 | NAME_3 | VWTGM010（2契約者・処理順2=3）.法人名_個人名 ← 契約者情報ﾏｽﾀ.NAME | ③_法人名_個人名 | 全角 120 |
| 106 | 契約者③_法人名_個人名ｶﾅ | 契約者③_法人名_個人名ｶﾅ | NAME_KANA_3 | VWTGM010（2契約者・処理順2=3）.法人名_個人名ｶﾅ ← 契約者情報ﾏｽﾀ.NAME_KANA | ③_法人名_個人名ｶﾅ | 半角 160 |
| 107 | 契約者③_所属部署名 | 契約者③_所属部署名 | BELONGING_POST_3 | VWTGM010（2契約者・処理順2=3）.所属部署名 ← 契約者情報ﾏｽﾀ.BELONGING_POST | ③_所属部署名 | 全角 160 |
| 108 | 契約者③_所属部署名ｶﾅ | 契約者③_所属部署名ｶﾅ | BELONGING_POST_KANA_3 | VWTGM010（2契約者・処理順2=3）.所属部署名ｶﾅ ← 契約者情報ﾏｽﾀ.BELONGING_POST_KANA | ③_所属部署名ｶﾅ | 半角 160 |
| 109 | 契約者③_電話番号_固定 | 契約者③_電話番号_固定 | TEL1_3 | VWTGM010（2契約者・処理順2=3）.電話番号_固定 ← 契約者情報ﾏｽﾀ.TEL1 | ③_電話番号_固定 | 数値 11 |
| 110 | 契約者③_電話番号_携帯 | 契約者③_電話番号_携帯 | TEL2_3 | VWTGM010（2契約者・処理順2=3）.電話番号_携帯 ← 契約者情報ﾏｽﾀ.TEL2 | ③_電話番号_携帯 | 数値 11 |
| 111 | 契約者③_FAX番号 | 契約者③_FAX番号 | FAX_3 | VWTGM010（2契約者・処理順2=3）.FAX番号 ← 契約者情報ﾏｽﾀ.FAX | ③_FAX番号 | 数値 10 |
| 112 | 契約者③_メールアドレス | 契約者③_メールアドレス | MAIL_3 | VWTGM010（2契約者・処理順2=3）.メールアドレス ← 契約者情報ﾏｽﾀ.MAIL | ③_メールアドレス | 半角英数 100 |
| 113 | 契約者③_郵便番号 | 契約者③_郵便番号 | ZIP_3 | VWTGM010（2契約者・処理順2=3）.郵便番号 ← 契約者情報ﾏｽﾀ.ZIP1 \|\| '-' \|\| 契約者情報ﾏｽﾀ.ZIP2 | ③_郵便番号 | 半角 8 |
| 114 | 契約者③_都道府県 | 契約者③_都道府県 | ADDRESS_CD1_3 | VWTGM010（2契約者・処理順2=3）.都道府県 ← 契約者情報ﾏｽﾀ.ADDRESS_CD1 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05')) | ③_都道府県 | 全角 50 |
| 115 | 契約者③_市区町村 | 契約者③_市区町村 | ADDRESS_CD2_3 | VWTGM010（2契約者・処理順2=3）.市区町村 ← 契約者情報ﾏｽﾀ.ADDRESS_CD2 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04')) | ③_市区町村 | 全角 50 |
| 116 | 契約者③_字_地番 | 契約者③_字_地番 | ADDRESS3_3 | VWTGM010（2契約者・処理順2=3）.字_地番 ← 契約者情報ﾏｽﾀ.ADDRESS3 | ③_字_地番 | 全角 100 |
| 117 | 契約者③_建物_ビル | 契約者③_建物_ビル | ADDRESS4_3 | VWTGM010（2契約者・処理順2=3）.建物_ビル ← 契約者情報ﾏｽﾀ.ADDRESS4 | ③_建物_ビル | 全角 100 |
| 118 | 契約者③_カナ | 契約者③_カナ | ADDRESS_KANA_3 | VWTGM010（2契約者・処理順2=3）.カナ ← 契約者情報ﾏｽﾀ.ADDRESS_KANA | ③_カナ | ー ー |
| 119 | 契約者③_書類 | 契約者③_書類 | DOCUMENTS_KBN_3 | VWTGM010（2契約者・処理順2=3）.書類 ← 契約者情報ﾏｽﾀ.DOCUMENTS_KBN (1:送付先、2:送付禁止) | ③_書類 | ー ー |
| 120 | 契約者③_電話 | 契約者③_電話 | TEL_KBN_3 | VWTGM010（2契約者・処理順2=3）.電話 ← 契約者情報ﾏｽﾀ.TEL_KBN (1:電話禁止) | ③_電話 | ー ー |
| 121 | 契約者③_詳細 | 契約者③_詳細 | DETAILS_KBN_3 | VWTGM010（2契約者・処理順2=3）.詳細 ← 契約者情報ﾏｽﾀ.DETAILS_KBN (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M01')) | ③_詳細 | ー ー |
| 122 | 契約者③_ﾏｲﾅﾝﾊﾞｰ受領日 | 契約者③_ﾏｲﾅﾝﾊﾞｰ受領日 | MY_NUMBER_DATE_3 | VWTGM010（2契約者・処理順2=3）.ﾏｲﾅﾝﾊﾞｰ受領日 ← 契約者情報ﾏｽﾀ.MY_NUMBER_DATE | ③_ﾏｲﾅﾝﾊﾞｰ受領日 | ー ー |
| 123 | 契約者③_備考 | 契約者③_備考 | BIKO_3 | VWTGM010（2契約者・処理順2=3）.備考 ← 契約者情報ﾏｽﾀ.BIKO | ③_備考 | ー ー |
| 124 | 契約者③_予備項目1 | 契約者③_予備項目1 | YOBI_KOMOKU1_3 | VWTGM010（2契約者・処理順2=3）.予備項目1 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU1 | ③_予備項目1 | ー ー |
| 125 | 契約者③_予備項目2 | 契約者③_予備項目2 | YOBI_KOMOKU2_3 | VWTGM010（2契約者・処理順2=3）.予備項目2 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU2 | ③_予備項目2 | ー ー |
| 126 | 契約者③_予備項目3 | 契約者③_予備項目3 | YOBI_KOMOKU3_3 | VWTGM010（2契約者・処理順2=3）.予備項目3 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU3 | ③_予備項目3 | ー ー |
| 127 | 契約者③_予備項目4 | 契約者③_予備項目4 | YOBI_KOMOKU4_3 | VWTGM010（2契約者・処理順2=3）.予備項目4 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU4 | ③_予備項目4 | ー ー |
| 128 | 契約者④_契約者番号 | 契約者④_契約者番号 | CONSTRACT_CD_4 | VWTGM010（2契約者・処理順2=4）.契約者番号 ← 契約者情報ﾏｽﾀ.CONSTRACT_CD | ④_契約者番号 | 全角 20 |
| 129 | 契約者④_契約者区分 | 契約者④_契約者区分 | CONSTRACT_KBN_4 | VWTGM010（2契約者・処理順2=4）.契約者区分 ← 契約者情報ﾏｽﾀ.CONSTRACT_KBN を名称にする（1→「契約者」、2→「関係者」） | ④_契約者区分 | 全角 2 |
| 130 | 契約者④_関係_地位 | 契約者④_関係_地位 | RELATION_4 | VWTGM010（2契約者・処理順2=4）.関係_地位 ← 契約者情報ﾏｽﾀ.RELATION | ④_関係_地位 | 全角 40 |
| 131 | 契約者④_法人_個人区分 | 契約者④_法人_個人区分 | CORP_PRIV_KBN_4 | VWTGM010（2契約者・処理順2=4）.法人_個人区分 ← 契約者情報ﾏｽﾀ.CORP_PRIV_KBN を名称にする（1→「法人」、2→「個人」。P06 の名称と同じ） | ④_法人_個人区分 | 全角 2 |
| 132 | 契約者④_法人名_個人名 | 契約者④_法人名_個人名 | NAME_4 | VWTGM010（2契約者・処理順2=4）.法人名_個人名 ← 契約者情報ﾏｽﾀ.NAME | ④_法人名_個人名 | 全角 120 |
| 133 | 契約者④_法人名_個人名ｶﾅ | 契約者④_法人名_個人名ｶﾅ | NAME_KANA_4 | VWTGM010（2契約者・処理順2=4）.法人名_個人名ｶﾅ ← 契約者情報ﾏｽﾀ.NAME_KANA | ④_法人名_個人名ｶﾅ | 半角 160 |
| 134 | 契約者④_所属部署名 | 契約者④_所属部署名 | BELONGING_POST_4 | VWTGM010（2契約者・処理順2=4）.所属部署名 ← 契約者情報ﾏｽﾀ.BELONGING_POST | ④_所属部署名 | 全角 160 |
| 135 | 契約者④_所属部署名ｶﾅ | 契約者④_所属部署名ｶﾅ | BELONGING_POST_KANA_4 | VWTGM010（2契約者・処理順2=4）.所属部署名ｶﾅ ← 契約者情報ﾏｽﾀ.BELONGING_POST_KANA | ④_所属部署名ｶﾅ | 半角 160 |
| 136 | 契約者④_電話番号_固定 | 契約者④_電話番号_固定 | TEL1_4 | VWTGM010（2契約者・処理順2=4）.電話番号_固定 ← 契約者情報ﾏｽﾀ.TEL1 | ④_電話番号_固定 | 数値 11 |
| 137 | 契約者④_電話番号_携帯 | 契約者④_電話番号_携帯 | TEL2_4 | VWTGM010（2契約者・処理順2=4）.電話番号_携帯 ← 契約者情報ﾏｽﾀ.TEL2 | ④_電話番号_携帯 | 数値 11 |
| 138 | 契約者④_FAX番号 | 契約者④_FAX番号 | FAX_4 | VWTGM010（2契約者・処理順2=4）.FAX番号 ← 契約者情報ﾏｽﾀ.FAX | ④_FAX番号 | 数値 10 |
| 139 | 契約者④_メールアドレス | 契約者④_メールアドレス | MAIL_4 | VWTGM010（2契約者・処理順2=4）.メールアドレス ← 契約者情報ﾏｽﾀ.MAIL | ④_メールアドレス | 半角英数 100 |
| 140 | 契約者④_郵便番号 | 契約者④_郵便番号 | ZIP_4 | VWTGM010（2契約者・処理順2=4）.郵便番号 ← 契約者情報ﾏｽﾀ.ZIP1 \|\| '-' \|\| 契約者情報ﾏｽﾀ.ZIP2 | ④_郵便番号 | 半角 8 |
| 141 | 契約者④_都道府県 | 契約者④_都道府県 | ADDRESS_CD1_4 | VWTGM010（2契約者・処理順2=4）.都道府県 ← 契約者情報ﾏｽﾀ.ADDRESS_CD1 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05')) | ④_都道府県 | 全角 50 |
| 142 | 契約者④_市区町村 | 契約者④_市区町村 | ADDRESS_CD2_4 | VWTGM010（2契約者・処理順2=4）.市区町村 ← 契約者情報ﾏｽﾀ.ADDRESS_CD2 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04')) | ④_市区町村 | 全角 50 |
| 143 | 契約者④_字_地番 | 契約者④_字_地番 | ADDRESS3_4 | VWTGM010（2契約者・処理順2=4）.字_地番 ← 契約者情報ﾏｽﾀ.ADDRESS3 | ④_字_地番 | 全角 100 |
| 144 | 契約者④_建物_ビル | 契約者④_建物_ビル | ADDRESS4_4 | VWTGM010（2契約者・処理順2=4）.建物_ビル ← 契約者情報ﾏｽﾀ.ADDRESS4 | ④_建物_ビル | 全角 100 |
| 145 | 契約者④_カナ | 契約者④_カナ | ADDRESS_KANA_4 | VWTGM010（2契約者・処理順2=4）.カナ ← 契約者情報ﾏｽﾀ.ADDRESS_KANA | ④_カナ | ー ー |
| 146 | 契約者④_書類 | 契約者④_書類 | DOCUMENTS_KBN_4 | VWTGM010（2契約者・処理順2=4）.書類 ← 契約者情報ﾏｽﾀ.DOCUMENTS_KBN (1:送付先、2:送付禁止) | ④_書類 | ー ー |
| 147 | 契約者④_電話 | 契約者④_電話 | TEL_KBN_4 | VWTGM010（2契約者・処理順2=4）.電話 ← 契約者情報ﾏｽﾀ.TEL_KBN (1:電話禁止) | ④_電話 | ー ー |
| 148 | 契約者④_詳細 | 契約者④_詳細 | DETAILS_KBN_4 | VWTGM010（2契約者・処理順2=4）.詳細 ← 契約者情報ﾏｽﾀ.DETAILS_KBN (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M01')) | ④_詳細 | ー ー |
| 149 | 契約者④_ﾏｲﾅﾝﾊﾞｰ受領日 | 契約者④_ﾏｲﾅﾝﾊﾞｰ受領日 | MY_NUMBER_DATE_4 | VWTGM010（2契約者・処理順2=4）.ﾏｲﾅﾝﾊﾞｰ受領日 ← 契約者情報ﾏｽﾀ.MY_NUMBER_DATE | ④_ﾏｲﾅﾝﾊﾞｰ受領日 | ー ー |
| 150 | 契約者④_備考 | 契約者④_備考 | BIKO_4 | VWTGM010（2契約者・処理順2=4）.備考 ← 契約者情報ﾏｽﾀ.BIKO | ④_備考 | ー ー |
| 151 | 契約者④_予備項目1 | 契約者④_予備項目1 | YOBI_KOMOKU1_4 | VWTGM010（2契約者・処理順2=4）.予備項目1 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU1 | ④_予備項目1 | ー ー |
| 152 | 契約者④_予備項目2 | 契約者④_予備項目2 | YOBI_KOMOKU2_4 | VWTGM010（2契約者・処理順2=4）.予備項目2 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU2 | ④_予備項目2 | ー ー |
| 153 | 契約者④_予備項目3 | 契約者④_予備項目3 | YOBI_KOMOKU3_4 | VWTGM010（2契約者・処理順2=4）.予備項目3 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU3 | ④_予備項目3 | ー ー |
| 154 | 契約者④_予備項目4 | 契約者④_予備項目4 | YOBI_KOMOKU4_4 | VWTGM010（2契約者・処理順2=4）.予備項目4 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU4 | ④_予備項目4 | ー ー |
| 155 | 契約者⑤_契約者番号 | 契約者⑤_契約者番号 | CONSTRACT_CD_5 | VWTGM010（2契約者・処理順2=5）.契約者番号 ← 契約者情報ﾏｽﾀ.CONSTRACT_CD | ⑤_契約者番号 | 全角 20 |
| 156 | 契約者⑤_契約者区分 | 契約者⑤_契約者区分 | CONSTRACT_KBN_5 | VWTGM010（2契約者・処理順2=5）.契約者区分 ← 契約者情報ﾏｽﾀ.CONSTRACT_KBN を名称にする（1→「契約者」、2→「関係者」） | ⑤_契約者区分 | 全角 2 |
| 157 | 契約者⑤_関係_地位 | 契約者⑤_関係_地位 | RELATION_5 | VWTGM010（2契約者・処理順2=5）.関係_地位 ← 契約者情報ﾏｽﾀ.RELATION | ⑤_関係_地位 | 全角 40 |
| 158 | 契約者⑤_法人_個人区分 | 契約者⑤_法人_個人区分 | CORP_PRIV_KBN_5 | VWTGM010（2契約者・処理順2=5）.法人_個人区分 ← 契約者情報ﾏｽﾀ.CORP_PRIV_KBN を名称にする（1→「法人」、2→「個人」。P06 の名称と同じ） | ⑤_法人_個人区分 | 全角 2 |
| 159 | 契約者⑤_法人名_個人名 | 契約者⑤_法人名_個人名 | NAME_5 | VWTGM010（2契約者・処理順2=5）.法人名_個人名 ← 契約者情報ﾏｽﾀ.NAME | ⑤_法人名_個人名 | 全角 120 |
| 160 | 契約者⑤_法人名_個人名ｶﾅ | 契約者⑤_法人名_個人名ｶﾅ | NAME_KANA_5 | VWTGM010（2契約者・処理順2=5）.法人名_個人名ｶﾅ ← 契約者情報ﾏｽﾀ.NAME_KANA | ⑤_法人名_個人名ｶﾅ | 半角 160 |
| 161 | 契約者⑤_所属部署名 | 契約者⑤_所属部署名 | BELONGING_POST_5 | VWTGM010（2契約者・処理順2=5）.所属部署名 ← 契約者情報ﾏｽﾀ.BELONGING_POST | ⑤_所属部署名 | 全角 160 |
| 162 | 契約者⑤_所属部署名ｶﾅ | 契約者⑤_所属部署名ｶﾅ | BELONGING_POST_KANA_5 | VWTGM010（2契約者・処理順2=5）.所属部署名ｶﾅ ← 契約者情報ﾏｽﾀ.BELONGING_POST_KANA | ⑤_所属部署名ｶﾅ | 半角 160 |
| 163 | 契約者⑤_電話番号_固定 | 契約者⑤_電話番号_固定 | TEL1_5 | VWTGM010（2契約者・処理順2=5）.電話番号_固定 ← 契約者情報ﾏｽﾀ.TEL1 | ⑤_電話番号_固定 | 数値 11 |
| 164 | 契約者⑤_電話番号_携帯 | 契約者⑤_電話番号_携帯 | TEL2_5 | VWTGM010（2契約者・処理順2=5）.電話番号_携帯 ← 契約者情報ﾏｽﾀ.TEL2 | ⑤_電話番号_携帯 | 数値 11 |
| 165 | 契約者⑤_FAX番号 | 契約者⑤_FAX番号 | FAX_5 | VWTGM010（2契約者・処理順2=5）.FAX番号 ← 契約者情報ﾏｽﾀ.FAX | ⑤_FAX番号 | 数値 10 |
| 166 | 契約者⑤_メールアドレス | 契約者⑤_メールアドレス | MAIL_5 | VWTGM010（2契約者・処理順2=5）.メールアドレス ← 契約者情報ﾏｽﾀ.MAIL | ⑤_メールアドレス | 半角英数 100 |
| 167 | 契約者⑤_郵便番号 | 契約者⑤_郵便番号 | ZIP_5 | VWTGM010（2契約者・処理順2=5）.郵便番号 ← 契約者情報ﾏｽﾀ.ZIP1 \|\| '-' \|\| 契約者情報ﾏｽﾀ.ZIP2 | ⑤_郵便番号 | 半角 8 |
| 168 | 契約者⑤_都道府県 | 契約者⑤_都道府県 | ADDRESS_CD1_5 | VWTGM010（2契約者・処理順2=5）.都道府県 ← 契約者情報ﾏｽﾀ.ADDRESS_CD1 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05')) | ⑤_都道府県 | 全角 50 |
| 169 | 契約者⑤_市区町村 | 契約者⑤_市区町村 | ADDRESS_CD2_5 | VWTGM010（2契約者・処理順2=5）.市区町村 ← 契約者情報ﾏｽﾀ.ADDRESS_CD2 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04')) | ⑤_市区町村 | 全角 50 |
| 170 | 契約者⑤_字_地番 | 契約者⑤_字_地番 | ADDRESS3_5 | VWTGM010（2契約者・処理順2=5）.字_地番 ← 契約者情報ﾏｽﾀ.ADDRESS3 | ⑤_字_地番 | 全角 100 |
| 171 | 契約者⑤_建物_ビル | 契約者⑤_建物_ビル | ADDRESS4_5 | VWTGM010（2契約者・処理順2=5）.建物_ビル ← 契約者情報ﾏｽﾀ.ADDRESS4 | ⑤_建物_ビル | 全角 100 |
| 172 | 契約者⑤_カナ | 契約者⑤_カナ | ADDRESS_KANA_5 | VWTGM010（2契約者・処理順2=5）.カナ ← 契約者情報ﾏｽﾀ.ADDRESS_KANA | ⑤_カナ | ー ー |
| 173 | 契約者⑤_書類 | 契約者⑤_書類 | DOCUMENTS_KBN_5 | VWTGM010（2契約者・処理順2=5）.書類 ← 契約者情報ﾏｽﾀ.DOCUMENTS_KBN (1:送付先、2:送付禁止) | ⑤_書類 | ー ー |
| 174 | 契約者⑤_電話 | 契約者⑤_電話 | TEL_KBN_5 | VWTGM010（2契約者・処理順2=5）.電話 ← 契約者情報ﾏｽﾀ.TEL_KBN (1:電話禁止) | ⑤_電話 | ー ー |
| 175 | 契約者⑤_詳細 | 契約者⑤_詳細 | DETAILS_KBN_5 | VWTGM010（2契約者・処理順2=5）.詳細 ← 契約者情報ﾏｽﾀ.DETAILS_KBN (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M01')) | ⑤_詳細 | ー ー |
| 176 | 契約者⑤_ﾏｲﾅﾝﾊﾞｰ受領日 | 契約者⑤_ﾏｲﾅﾝﾊﾞｰ受領日 | MY_NUMBER_DATE_5 | VWTGM010（2契約者・処理順2=5）.ﾏｲﾅﾝﾊﾞｰ受領日 ← 契約者情報ﾏｽﾀ.MY_NUMBER_DATE | ⑤_ﾏｲﾅﾝﾊﾞｰ受領日 | ー ー |
| 177 | 契約者⑤_備考 | 契約者⑤_備考 | BIKO_5 | VWTGM010（2契約者・処理順2=5）.備考 ← 契約者情報ﾏｽﾀ.BIKO | ⑤_備考 | ー ー |
| 178 | 契約者⑤_予備項目1 | 契約者⑤_予備項目1 | YOBI_KOMOKU1_5 | VWTGM010（2契約者・処理順2=5）.予備項目1 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU1 | ⑤_予備項目1 | ー ー |
| 179 | 契約者⑤_予備項目2 | 契約者⑤_予備項目2 | YOBI_KOMOKU2_5 | VWTGM010（2契約者・処理順2=5）.予備項目2 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU2 | ⑤_予備項目2 | ー ー |
| 180 | 契約者⑤_予備項目3 | 契約者⑤_予備項目3 | YOBI_KOMOKU3_5 | VWTGM010（2契約者・処理順2=5）.予備項目3 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU3 | ⑤_予備項目3 | ー ー |
| 181 | 契約者⑤_予備項目4 | 契約者⑤_予備項目4 | YOBI_KOMOKU4_5 | VWTGM010（2契約者・処理順2=5）.予備項目4 ← 契約者情報ﾏｽﾀ.YOBI_KOMOKU4 | ⑤_予備項目4 | ー ー |
| 182 | 支払情報①_支払番号 | 支払情報①_支払番号 | PAY_CD_1 | VWTGM010（3支払情報・処理順2=1）.支払番号 ← 契約支払情報ﾏｽﾀ.PAY_CD | ①_支払番号 | ー ー |
| 183 | 支払情報①_支払番号枝番 | 支払情報①_支払番号枝番 | PAY_CD_BRANCH_1 | VWTGM010（3支払情報・処理順2=1）.支払番号枝番 ← 契約支払情報ﾏｽﾀ.PAY_CD_BRANCH | ①_支払番号枝番 | ー ー |
| 184 | 支払情報①_支払内容区分 | 支払情報①_支払内容区分 | FEE_MANAGE_KIND_1 | VWTGM010（3支払情報・処理順2=1）.支払内容区分 ← 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND | ①_支払内容区分 | ー ー |
| 185 | 支払情報①_支払内容区分_名称 | 支払情報①_支払内容区分_名称 | FEE_MANAGE_KIND_NM_1 | VWTGM010（3支払情報・処理順2=1）.支払内容区分_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P17') | ①_支払内容区分_名称 | ー ー |
| 186 | 支払情報①_支払内容詳細区分 | 支払情報①_支払内容詳細区分 | FEE_MANAGE_KIND_SHOSAI_1 | VWTGM010（3支払情報・処理順2=1）.支払内容詳細区分 ← 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND_SHOSAI | ①_支払内容詳細区分 | 半角英数 2 |
| 187 | 支払情報①_支払内容詳細区分_名称 | 支払情報①_支払内容詳細区分_名称 | FEE_MANAGE_KIND_SHOSAI_NM_1 | VWTGM010（3支払情報・処理順2=1）.支払内容詳細区分_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',CODE,'C02') | ①_支払内容詳細区分_名称 | 全角 60 |
| 188 | 支払情報①_支払内容その他 | 支払情報①_支払内容その他 | OTHER_PAYMENT_NAME_1 | VWTGM010（3支払情報・処理順2=1）.支払内容その他 ← 契約支払情報ﾏｽﾀ.OTHER_PAYMENT_NAME | ①_支払内容その他 | ー ー |
| 189 | 支払情報①_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 支払情報①_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ANKEN_DAI_GRP_CD_1 | VWTGM010（3支払情報・処理順2=1）.案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ ← 契約支払情報ﾏｽﾀ.ANKEN_DAI_GRP_CD | ①_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ー ー |
| 190 | 支払情報①_案件大ｸﾞﾙｰﾌﾟ | 支払情報①_案件大ｸﾞﾙｰﾌﾟ | ANKEN_DAI_GRP_CD_NM_1 | VWTGM010（3支払情報・処理順2=1）.案件大ｸﾞﾙｰﾌﾟ ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M10') | ①_案件大ｸﾞﾙｰﾌﾟ | ー ー |
| 191 | 支払情報①_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 支払情報①_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ANKEN_SYO_GRP_CD_1 | VWTGM010（3支払情報・処理順2=1）.案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ ← 契約支払情報ﾏｽﾀ.ANKEN_SYO_GRP_CD | ①_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ー ー |
| 192 | 支払情報①_案件小ｸﾞﾙｰﾌﾟ | 支払情報①_案件小ｸﾞﾙｰﾌﾟ | ANKEN_SYO_GRP_CD_NM_1 | VWTGM010（3支払情報・処理順2=1）.案件小ｸﾞﾙｰﾌﾟ ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M11') | ①_案件小ｸﾞﾙｰﾌﾟ | ー ー |
| 193 | 支払情報①_採算管理区分 | 支払情報①_採算管理区分 | PROFIT_MANAGE_KIND_1 | VWTGM010（3支払情報・処理順2=1）.採算管理区分 ← 契約支払情報ﾏｽﾀ.PROFIT_MANAGE_KIND | ①_採算管理区分 | ー ー |
| 194 | 支払情報①_支払先_契約先番号 | 支払情報①_支払先_契約先番号 | PAYMENT_PERSON_1 | VWTGM010（3支払情報・処理順2=1）.支払先_契約先番号 ← 契約支払情報ﾏｽﾀ.PAYMENT_PERSON | ①_支払先_契約先番号 | ー ー |
| 195 | 支払情報①_支払方法 | 支払情報①_支払方法 | PAYMENT_DDIVISION_1 | VWTGM010（3支払情報・処理順2=1）.支払方法 ← 契約支払情報ﾏｽﾀ.PAYMENT_DDIVISION | ①_支払方法 | 半角英数 2 |
| 196 | 支払情報①_支払方法_名称 | 支払情報①_支払方法_名称 | PAYMENT_DDIVISION_NM_1 | VWTGM010（3支払情報・処理順2=1）.支払方法_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P18') | ①_支払方法_名称 | 全角 60 |
| 197 | 支払情報①_消費税扱い | 支払情報①_消費税扱い | TAX_KIND_1 | VWTGM010（3支払情報・処理順2=1）.消費税扱い ← 契約支払情報ﾏｽﾀ.TAX_KIND | ①_消費税扱い | 半角英数 2 |
| 198 | 支払情報①_消費税扱い_名称 | 支払情報①_消費税扱い_名称 | TAX_KIND_NM_1 | VWTGM010（3支払情報・処理順2=1）.消費税扱い_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P10') | ①_消費税扱い_名称 | 全角 60 |
| 199 | 支払情報①_初回支払金額 | 支払情報①_初回支払金額 | FIRST_PAY_FEE_1 | VWTGM010（3支払情報・処理順2=1）.初回支払金額 ← TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_FEE ) | ①_初回支払金額 | ー ー |
| 200 | 支払情報①_初回支払消費税額 | 支払情報①_初回支払消費税額 | FIRST_PAY_TAX_1 | VWTGM010（3支払情報・処理順2=1）.初回支払消費税額 ← TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_TAX ) | ①_初回支払消費税額 | ー ー |
| 201 | 支払情報①_初回支払日 | 支払情報①_初回支払日 | FIRST_PAY_DATE_1 | VWTGM010（3支払情報・処理順2=1）.初回支払日 ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_DATE ), 'YYYY/MM/DD' ) | ①_初回支払日 | ー ー |
| 202 | 支払情報①_初回支払期間対象FROM | 支払情報①_初回支払期間対象FROM | FIRST_PAY_FROM_1 | VWTGM010（3支払情報・処理順2=1）.初回支払期間対象FROM ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_FROM \|\| '01' ), 'YYYY/MM/DD' ) | ①_初回支払期間対象FROM | ー ー |
| 203 | 支払情報①_初回支払期間対象TO | 支払情報①_初回支払期間対象TO | FIRST_PAY_TO_1 | VWTGM010（3支払情報・処理順2=1）.初回支払期間対象TO ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_TO \|\| '01' ), 'YYYY/MM/DD' ) | ①_初回支払期間対象TO | ー ー |
| 204 | 支払情報①_初回消費税調整額 | 支払情報①_初回消費税調整額 | FIRST_TAX_ADJUSTMENTS_1 | VWTGM010（3支払情報・処理順2=1）.初回消費税調整額 ← TO_CHAR(契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS ) | ①_初回消費税調整額 | ー ー |
| 205 | 支払情報①_初回消費税調整理由 | 支払情報①_初回消費税調整理由 | FIRST_TAX_ADJUSTMENTS_REASON_1 | VWTGM010（3支払情報・処理順2=1）.初回消費税調整理由 ← 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_REASON | ①_初回消費税調整理由 | ー ー |
| 206 | 支払情報①_初回消費税調整理由_名称 | 支払情報①_初回消費税調整理由_名称 | FIRST_TAX_ADJUSTMENTS_REA_NM_1 | VWTGM010（3支払情報・処理順2=1）.初回消費税調整理由_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') | ①_初回消費税調整理由_名称 | ー ー |
| 207 | 支払情報①_初回消費税備考 | 支払情報①_初回消費税備考 | FIRST_TAX_ADJUSTMENTS_MEMO_1 | VWTGM010（3支払情報・処理順2=1）.初回消費税備考 ← 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_MEMO | ①_初回消費税備考 | ー ー |
| 208 | 支払情報①_継続支払金額 | 支払情報①_継続支払金額 | COUNT_PAY_FEE_1 | VWTGM010（3支払情報・処理順2=1）.継続支払金額 ← TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_FEE ) | ①_継続支払金額 | ー ー |
| 209 | 支払情報①_継続支払消費税額 | 支払情報①_継続支払消費税額 | COUNT_PAY_TAX_1 | VWTGM010（3支払情報・処理順2=1）.継続支払消費税額 ← TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_TAX ) | ①_継続支払消費税額 | ー ー |
| 210 | 支払情報①_継続消費税調整額 | 支払情報①_継続消費税調整額 | COUNT_TAX_ADJUSTMENTS_1 | VWTGM010（3支払情報・処理順2=1）.継続消費税調整額 ← TO_CHAR( 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS ) | ①_継続消費税調整額 | ー ー |
| 211 | 支払情報①_継続消費税調整理由 | 支払情報①_継続消費税調整理由 | COUNT_TAX_ADJUSTMENTS_REASON_1 | VWTGM010（3支払情報・処理順2=1）.継続消費税調整理由 ← 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_REASON | ①_継続消費税調整理由 | ー ー |
| 212 | 支払情報①_継続消費税調整理由_名称 | 支払情報①_継続消費税調整理由_名称 | COUNT_TAX_ADJUSTMENTS_REA_NM_1 | VWTGM010（3支払情報・処理順2=1）.継続消費税調整理由_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') | ①_継続消費税調整理由_名称 | ー ー |
| 213 | 支払情報①_継続消費税備考 | 支払情報①_継続消費税備考 | COUNT_TAX_ADJUSTMENTS_MEMO_1 | VWTGM010（3支払情報・処理順2=1）.継続消費税備考 ← 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_MEMO | ①_継続消費税備考 | ー ー |
| 214 | 支払情報①_支払有効期間FROM | 支払情報①_支払有効期間FROM | PAY_EFFECTIVE_FROM_1 | VWTGM010（3支払情報・処理順2=1）.支払有効期間FROM ← 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_FROM | ①_支払有効期間FROM | ー ー |
| 215 | 支払情報①_支払有効期間TO | 支払情報①_支払有効期間TO | PAY_EFFECTIVE_TO_1 | VWTGM010（3支払情報・処理順2=1）.支払有効期間TO ← 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_TO | ①_支払有効期間TO | ー ー |
| 216 | 支払情報①_月額契約金額_税抜 | 支払情報①_月額契約金額_税抜 | MONTHLY_PAYMENT_1 | VWTGM010（3支払情報・処理順2=1）.月額契約金額_税抜 ← TO_CHAR( 契約支払情報ﾏｽﾀ.MONTHLY_PAYMENT ) | ①_月額契約金額_税抜 | ー ー |
| 217 | 支払情報①_月額有効期間FROM | 支払情報①_月額有効期間FROM | MONTHLY_PAY_EFFECTIVE_FROM_1 | VWTGM010（3支払情報・処理順2=1）.月額有効期間FROM ← 契約支払情報ﾏｽﾀ. MONTHLY_PAY_EFFECTIVE_FROM | ①_月額有効期間FROM | ー ー |
| 218 | 支払情報①_月額有効期間TO | 支払情報①_月額有効期間TO | MONTHLY_PAY_EFFECTIVE_TO_1 | VWTGM010（3支払情報・処理順2=1）.月額有効期間TO ← 契約支払情報ﾏｽﾀ.MONTHLY_PAY_EFFECTIVE_TO | ①_月額有効期間TO | ー ー |
| 219 | 支払情報①_請求方法区分 | 支払情報①_請求方法区分 | CLAIM_INFOMATION_KIND_1 | VWTGM010（3支払情報・処理順2=1）.請求方法区分 ← 契約支払情報ﾏｽﾀ.CLAIM_INFOMATION_KIND | ①_請求方法区分 | ー ー |
| 220 | 支払情報①_支払種別 | 支払情報①_支払種別 | PAYMENT_KIND_1 | VWTGM010（3支払情報・処理順2=1）.支払種別 ← 契約支払情報ﾏｽﾀ.PAYMENT_KIND | ①_支払種別 | ー ー |
| 221 | 支払情報①_支払種別_名称 | 支払情報①_支払種別_名称 | PAYMENT_KIND_NM_1 | VWTGM010（3支払情報・処理順2=1）.支払種別_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P08') | ①_支払種別_名称 | ー ー |
| 222 | 支払情報①_支払年 | 支払情報①_支払年 | PAYMENT_YEAR_1 | VWTGM010（3支払情報・処理順2=1）.支払年 ← 契約支払情報ﾏｽﾀ.PAYMENT_YEAR | ①_支払年 | ー ー |
| 223 | 支払情報①_継続支払詳細_備考 | 支払情報①_継続支払詳細_備考 | PAYMENT_MEMO_1 | VWTGM010（3支払情報・処理順2=1）.継続支払詳細_備考 ← 契約支払情報ﾏｽﾀ.PAYMENT_MEMO | ①_継続支払詳細_備考 | ー ー |
| 224 | 支払情報①_その他備考1 | 支払情報①_その他備考1 | MEMO1_1 | VWTGM010（3支払情報・処理順2=1）.その他備考1 ← 契約支払情報ﾏｽﾀ.MEMO1 | ①_その他備考1 | ー ー |
| 225 | 支払情報①_その他備考2 | 支払情報①_その他備考2 | MEMO2_1 | VWTGM010（3支払情報・処理順2=1）.その他備考2 ← 契約支払情報ﾏｽﾀ.MEMO2 | ①_その他備考2 | ー ー |
| 226 | 支払情報①_その他備考3 | 支払情報①_その他備考3 | MEMO3_1 | VWTGM010（3支払情報・処理順2=1）.その他備考3 ← 契約支払情報ﾏｽﾀ.MEMO3 | ①_その他備考3 | ー ー |
| 227 | 支払情報①_その他備考4 | 支払情報①_その他備考4 | MEMO4_1 | VWTGM010（3支払情報・処理順2=1）.その他備考4 ← 契約支払情報ﾏｽﾀ.MEMO4 | ①_その他備考4 | ー ー |
| 228 | 支払情報①_請求予定月 | 支払情報①_請求予定月 | CLAIM_MONTH_1 | VWTGM010（3支払情報・処理順2=1）.請求予定月 ← 契約支払情報ﾏｽﾀ.CLAIM_MONTH | ①_請求予定月 | ー ー |
| 229 | 支払情報①_請求予定月_名称 | 支払情報①_請求予定月_名称 | CLAIM_MONTH_NM_1 | VWTGM010（3支払情報・処理順2=1）.請求予定月_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P23') | ①_請求予定月_名称 | ー ー |
| 230 | 支払情報①_予備項目1 | 支払情報①_予備項目1 | GM03_YOBI_KOMOKU1_1 | VWTGM010（3支払情報・処理順2=1）.予備項目1 ← 契約支払情報ﾏｽﾀ.YOBI_KOMOKU1 | ①_支払_予備項目1 | ー ー |
| 231 | 支払情報①_予備項目2 | 支払情報①_予備項目2 | GM03_YOBI_KOMOKU2_1 | VWTGM010（3支払情報・処理順2=1）.予備項目2 ← 契約支払情報ﾏｽﾀ.YOBI_KOMOKU2 | ①_支払_予備項目2 | ー ー |
| 232 | 支払情報②_支払番号 | 支払情報②_支払番号 | PAY_CD_2 | VWTGM010（3支払情報・処理順2=2）.支払番号 ← 契約支払情報ﾏｽﾀ.PAY_CD | ②_支払番号 | ー ー |
| 233 | 支払情報②_支払番号枝番 | 支払情報②_支払番号枝番 | PAY_CD_BRANCH_2 | VWTGM010（3支払情報・処理順2=2）.支払番号枝番 ← 契約支払情報ﾏｽﾀ.PAY_CD_BRANCH | ②_支払番号枝番 | ー ー |
| 234 | 支払情報②_支払内容区分 | 支払情報②_支払内容区分 | FEE_MANAGE_KIND_2 | VWTGM010（3支払情報・処理順2=2）.支払内容区分 ← 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND | ②_支払内容区分 | ー ー |
| 235 | 支払情報②_支払内容区分_名称 | 支払情報②_支払内容区分_名称 | FEE_MANAGE_KIND_NM_2 | VWTGM010（3支払情報・処理順2=2）.支払内容区分_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P17') | ②_支払内容区分_名称 | ー ー |
| 236 | 支払情報②_支払内容詳細区分 | 支払情報②_支払内容詳細区分 | FEE_MANAGE_KIND_SHOSAI_2 | VWTGM010（3支払情報・処理順2=2）.支払内容詳細区分 ← 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND_SHOSAI | ②_支払内容詳細区分 | 半角英数 2 |
| 237 | 支払情報②_支払内容詳細区分_名称 | 支払情報②_支払内容詳細区分_名称 | FEE_MANAGE_KIND_SHOSAI_NM_2 | VWTGM010（3支払情報・処理順2=2）.支払内容詳細区分_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',CODE,'C02') | ②_支払内容詳細区分_名称 | 全角 60 |
| 238 | 支払情報②_支払内容その他 | 支払情報②_支払内容その他 | OTHER_PAYMENT_NAME_2 | VWTGM010（3支払情報・処理順2=2）.支払内容その他 ← 契約支払情報ﾏｽﾀ.OTHER_PAYMENT_NAME | ②_支払内容その他 | ー ー |
| 239 | 支払情報②_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 支払情報②_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ANKEN_DAI_GRP_CD_2 | VWTGM010（3支払情報・処理順2=2）.案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ ← 契約支払情報ﾏｽﾀ.ANKEN_DAI_GRP_CD | ②_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ー ー |
| 240 | 支払情報②_案件大ｸﾞﾙｰﾌﾟ | 支払情報②_案件大ｸﾞﾙｰﾌﾟ | ANKEN_DAI_GRP_CD_NM_2 | VWTGM010（3支払情報・処理順2=2）.案件大ｸﾞﾙｰﾌﾟ ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M10') | ②_案件大ｸﾞﾙｰﾌﾟ | ー ー |
| 241 | 支払情報②_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 支払情報②_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ANKEN_SYO_GRP_CD_2 | VWTGM010（3支払情報・処理順2=2）.案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ ← 契約支払情報ﾏｽﾀ.ANKEN_SYO_GRP_CD | ②_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ー ー |
| 242 | 支払情報②_案件小ｸﾞﾙｰﾌﾟ | 支払情報②_案件小ｸﾞﾙｰﾌﾟ | ANKEN_SYO_GRP_CD_NM_2 | VWTGM010（3支払情報・処理順2=2）.案件小ｸﾞﾙｰﾌﾟ ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M11') | ②_案件小ｸﾞﾙｰﾌﾟ | ー ー |
| 243 | 支払情報②_採算管理区分 | 支払情報②_採算管理区分 | PROFIT_MANAGE_KIND_2 | VWTGM010（3支払情報・処理順2=2）.採算管理区分 ← 契約支払情報ﾏｽﾀ.PROFIT_MANAGE_KIND | ②_採算管理区分 | ー ー |
| 244 | 支払情報②_支払先_契約先番号 | 支払情報②_支払先_契約先番号 | PAYMENT_PERSON_2 | VWTGM010（3支払情報・処理順2=2）.支払先_契約先番号 ← 契約支払情報ﾏｽﾀ.PAYMENT_PERSON | ②_支払先_契約先番号 | ー ー |
| 245 | 支払情報②_支払方法 | 支払情報②_支払方法 | PAYMENT_DDIVISION_2 | VWTGM010（3支払情報・処理順2=2）.支払方法 ← 契約支払情報ﾏｽﾀ.PAYMENT_DDIVISION | ②_支払方法 | 半角英数 2 |
| 246 | 支払情報②_支払方法_名称 | 支払情報②_支払方法_名称 | PAYMENT_DDIVISION_NM_2 | VWTGM010（3支払情報・処理順2=2）.支払方法_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P18') | ②_支払方法_名称 | 全角 60 |
| 247 | 支払情報②_消費税扱い | 支払情報②_消費税扱い | TAX_KIND_2 | VWTGM010（3支払情報・処理順2=2）.消費税扱い ← 契約支払情報ﾏｽﾀ.TAX_KIND | ②_消費税扱い | 半角英数 2 |
| 248 | 支払情報②_消費税扱い_名称 | 支払情報②_消費税扱い_名称 | TAX_KIND_NM_2 | VWTGM010（3支払情報・処理順2=2）.消費税扱い_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P10') | ②_消費税扱い_名称 | 全角 60 |
| 249 | 支払情報②_初回支払金額 | 支払情報②_初回支払金額 | FIRST_PAY_FEE_2 | VWTGM010（3支払情報・処理順2=2）.初回支払金額 ← TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_FEE ) | ②_初回支払金額 | ー ー |
| 250 | 支払情報②_初回支払消費税額 | 支払情報②_初回支払消費税額 | FIRST_PAY_TAX_2 | VWTGM010（3支払情報・処理順2=2）.初回支払消費税額 ← TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_TAX ) | ②_初回支払消費税額 | ー ー |
| 251 | 支払情報②_初回支払日 | 支払情報②_初回支払日 | FIRST_PAY_DATE_2 | VWTGM010（3支払情報・処理順2=2）.初回支払日 ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_DATE ), 'YYYY/MM/DD' ) | ②_初回支払日 | ー ー |
| 252 | 支払情報②_初回支払期間対象FROM | 支払情報②_初回支払期間対象FROM | FIRST_PAY_FROM_2 | VWTGM010（3支払情報・処理順2=2）.初回支払期間対象FROM ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_FROM \|\| '01' ), 'YYYY/MM/DD' ) | ②_初回支払期間対象FROM | ー ー |
| 253 | 支払情報②_初回支払期間対象TO | 支払情報②_初回支払期間対象TO | FIRST_PAY_TO_2 | VWTGM010（3支払情報・処理順2=2）.初回支払期間対象TO ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_TO \|\| '01' ), 'YYYY/MM/DD' ) | ②_初回支払期間対象TO | ー ー |
| 254 | 支払情報②_初回消費税調整額 | 支払情報②_初回消費税調整額 | FIRST_TAX_ADJUSTMENTS_2 | VWTGM010（3支払情報・処理順2=2）.初回消費税調整額 ← TO_CHAR(契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS ) | ②_初回消費税調整額 | ー ー |
| 255 | 支払情報②_初回消費税調整理由 | 支払情報②_初回消費税調整理由 | FIRST_TAX_ADJUSTMENTS_REASON_2 | VWTGM010（3支払情報・処理順2=2）.初回消費税調整理由 ← 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_REASON | ②_初回消費税調整理由 | ー ー |
| 256 | 支払情報②_初回消費税調整理由_名称 | 支払情報②_初回消費税調整理由_名称 | FIRST_TAX_ADJUSTMENTS_REA_NM_2 | VWTGM010（3支払情報・処理順2=2）.初回消費税調整理由_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') | ②_初回消費税調整理由_名称 | ー ー |
| 257 | 支払情報②_初回消費税備考 | 支払情報②_初回消費税備考 | FIRST_TAX_ADJUSTMENTS_MEMO_2 | VWTGM010（3支払情報・処理順2=2）.初回消費税備考 ← 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_MEMO | ②_初回消費税備考 | ー ー |
| 258 | 支払情報②_継続支払金額 | 支払情報②_継続支払金額 | COUNT_PAY_FEE_2 | VWTGM010（3支払情報・処理順2=2）.継続支払金額 ← TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_FEE ) | ②_継続支払金額 | ー ー |
| 259 | 支払情報②_継続支払消費税額 | 支払情報②_継続支払消費税額 | COUNT_PAY_TAX_2 | VWTGM010（3支払情報・処理順2=2）.継続支払消費税額 ← TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_TAX ) | ②_継続支払消費税額 | ー ー |
| 260 | 支払情報②_継続消費税調整額 | 支払情報②_継続消費税調整額 | COUNT_TAX_ADJUSTMENTS_2 | VWTGM010（3支払情報・処理順2=2）.継続消費税調整額 ← TO_CHAR( 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS ) | ②_継続消費税調整額 | ー ー |
| 261 | 支払情報②_継続消費税調整理由 | 支払情報②_継続消費税調整理由 | COUNT_TAX_ADJUSTMENTS_REASON_2 | VWTGM010（3支払情報・処理順2=2）.継続消費税調整理由 ← 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_REASON | ②_継続消費税調整理由 | ー ー |
| 262 | 支払情報②_継続消費税調整理由_名称 | 支払情報②_継続消費税調整理由_名称 | COUNT_TAX_ADJUSTMENTS_REA_NM_2 | VWTGM010（3支払情報・処理順2=2）.継続消費税調整理由_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') | ②_継続消費税調整理由_名称 | ー ー |
| 263 | 支払情報②_継続消費税備考 | 支払情報②_継続消費税備考 | COUNT_TAX_ADJUSTMENTS_MEMO_2 | VWTGM010（3支払情報・処理順2=2）.継続消費税備考 ← 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_MEMO | ②_継続消費税備考 | ー ー |
| 264 | 支払情報②_支払有効期間FROM | 支払情報②_支払有効期間FROM | PAY_EFFECTIVE_FROM_2 | VWTGM010（3支払情報・処理順2=2）.支払有効期間FROM ← 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_FROM | ②_支払有効期間FROM | ー ー |
| 265 | 支払情報②_支払有効期間TO | 支払情報②_支払有効期間TO | PAY_EFFECTIVE_TO_2 | VWTGM010（3支払情報・処理順2=2）.支払有効期間TO ← 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_TO | ②_支払有効期間TO | ー ー |
| 266 | 支払情報②_月額契約金額_税抜 | 支払情報②_月額契約金額_税抜 | MONTHLY_PAYMENT_2 | VWTGM010（3支払情報・処理順2=2）.月額契約金額_税抜 ← TO_CHAR( 契約支払情報ﾏｽﾀ.MONTHLY_PAYMENT ) | ②_月額契約金額_税抜 | ー ー |
| 267 | 支払情報②_月額有効期間FROM | 支払情報②_月額有効期間FROM | MONTHLY_PAY_EFFECTIVE_FROM_2 | VWTGM010（3支払情報・処理順2=2）.月額有効期間FROM ← 契約支払情報ﾏｽﾀ. MONTHLY_PAY_EFFECTIVE_FROM | ②_月額有効期間FROM | ー ー |
| 268 | 支払情報②_月額有効期間TO | 支払情報②_月額有効期間TO | MONTHLY_PAY_EFFECTIVE_TO_2 | VWTGM010（3支払情報・処理順2=2）.月額有効期間TO ← 契約支払情報ﾏｽﾀ.MONTHLY_PAY_EFFECTIVE_TO | ②_月額有効期間TO | ー ー |
| 269 | 支払情報②_請求方法区分 | 支払情報②_請求方法区分 | CLAIM_INFOMATION_KIND_2 | VWTGM010（3支払情報・処理順2=2）.請求方法区分 ← 契約支払情報ﾏｽﾀ.CLAIM_INFOMATION_KIND | ②_請求方法区分 | ー ー |
| 270 | 支払情報②_支払種別 | 支払情報②_支払種別 | PAYMENT_KIND_2 | VWTGM010（3支払情報・処理順2=2）.支払種別 ← 契約支払情報ﾏｽﾀ.PAYMENT_KIND | ②_支払種別 | ー ー |
| 271 | 支払情報②_支払種別_名称 | 支払情報②_支払種別_名称 | PAYMENT_KIND_NM_2 | VWTGM010（3支払情報・処理順2=2）.支払種別_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P08') | ②_支払種別_名称 | ー ー |
| 272 | 支払情報②_支払年 | 支払情報②_支払年 | PAYMENT_YEAR_2 | VWTGM010（3支払情報・処理順2=2）.支払年 ← 契約支払情報ﾏｽﾀ.PAYMENT_YEAR | ②_支払年 | ー ー |
| 273 | 支払情報②_継続支払詳細_備考 | 支払情報②_継続支払詳細_備考 | PAYMENT_MEMO_2 | VWTGM010（3支払情報・処理順2=2）.継続支払詳細_備考 ← 契約支払情報ﾏｽﾀ.PAYMENT_MEMO | ②_継続支払詳細_備考 | ー ー |
| 274 | 支払情報②_その他備考1 | 支払情報②_その他備考1 | MEMO1_2 | VWTGM010（3支払情報・処理順2=2）.その他備考1 ← 契約支払情報ﾏｽﾀ.MEMO1 | ②_その他備考1 | ー ー |
| 275 | 支払情報②_その他備考2 | 支払情報②_その他備考2 | MEMO2_2 | VWTGM010（3支払情報・処理順2=2）.その他備考2 ← 契約支払情報ﾏｽﾀ.MEMO2 | ②_その他備考2 | ー ー |
| 276 | 支払情報②_その他備考3 | 支払情報②_その他備考3 | MEMO3_2 | VWTGM010（3支払情報・処理順2=2）.その他備考3 ← 契約支払情報ﾏｽﾀ.MEMO3 | ②_その他備考3 | ー ー |
| 277 | 支払情報②_その他備考4 | 支払情報②_その他備考4 | MEMO4_2 | VWTGM010（3支払情報・処理順2=2）.その他備考4 ← 契約支払情報ﾏｽﾀ.MEMO4 | ②_その他備考4 | ー ー |
| 278 | 支払情報②_請求予定月 | 支払情報②_請求予定月 | CLAIM_MONTH_2 | VWTGM010（3支払情報・処理順2=2）.請求予定月 ← 契約支払情報ﾏｽﾀ.CLAIM_MONTH | ②_請求予定月 | ー ー |
| 279 | 支払情報②_請求予定月_名称 | 支払情報②_請求予定月_名称 | CLAIM_MONTH_NM_2 | VWTGM010（3支払情報・処理順2=2）.請求予定月_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P23') | ②_請求予定月_名称 | ー ー |
| 280 | 支払情報②_予備項目1 | 支払情報②_予備項目1 | GM03_YOBI_KOMOKU1_2 | VWTGM010（3支払情報・処理順2=2）.予備項目1 ← 契約支払情報ﾏｽﾀ.YOBI_KOMOKU1 | ②_支払_予備項目1 | ー ー |
| 281 | 支払情報②_予備項目2 | 支払情報②_予備項目2 | GM03_YOBI_KOMOKU2_2 | VWTGM010（3支払情報・処理順2=2）.予備項目2 ← 契約支払情報ﾏｽﾀ.YOBI_KOMOKU2 | ②_支払_予備項目2 | ー ー |
| 282 | 支払情報③_支払番号 | 支払情報③_支払番号 | PAY_CD_3 | VWTGM010（3支払情報・処理順2=3）.支払番号 ← 契約支払情報ﾏｽﾀ.PAY_CD | ③_支払番号 | ー ー |
| 283 | 支払情報③_支払番号枝番 | 支払情報③_支払番号枝番 | PAY_CD_BRANCH_3 | VWTGM010（3支払情報・処理順2=3）.支払番号枝番 ← 契約支払情報ﾏｽﾀ.PAY_CD_BRANCH | ③_支払番号枝番 | ー ー |
| 284 | 支払情報③_支払内容区分 | 支払情報③_支払内容区分 | FEE_MANAGE_KIND_3 | VWTGM010（3支払情報・処理順2=3）.支払内容区分 ← 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND | ③_支払内容区分 | ー ー |
| 285 | 支払情報③_支払内容区分_名称 | 支払情報③_支払内容区分_名称 | FEE_MANAGE_KIND_NM_3 | VWTGM010（3支払情報・処理順2=3）.支払内容区分_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P17') | ③_支払内容区分_名称 | ー ー |
| 286 | 支払情報③_支払内容詳細区分 | 支払情報③_支払内容詳細区分 | FEE_MANAGE_KIND_SHOSAI_3 | VWTGM010（3支払情報・処理順2=3）.支払内容詳細区分 ← 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND_SHOSAI | ③_支払内容詳細区分 | 半角英数 2 |
| 287 | 支払情報③_支払内容詳細区分_名称 | 支払情報③_支払内容詳細区分_名称 | FEE_MANAGE_KIND_SHOSAI_NM_3 | VWTGM010（3支払情報・処理順2=3）.支払内容詳細区分_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',CODE,'C02') | ③_支払内容詳細区分_名称 | 全角 60 |
| 288 | 支払情報③_支払内容その他 | 支払情報③_支払内容その他 | OTHER_PAYMENT_NAME_3 | VWTGM010（3支払情報・処理順2=3）.支払内容その他 ← 契約支払情報ﾏｽﾀ.OTHER_PAYMENT_NAME | ③_支払内容その他 | ー ー |
| 289 | 支払情報③_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 支払情報③_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ANKEN_DAI_GRP_CD_3 | VWTGM010（3支払情報・処理順2=3）.案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ ← 契約支払情報ﾏｽﾀ.ANKEN_DAI_GRP_CD | ③_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ー ー |
| 290 | 支払情報③_案件大ｸﾞﾙｰﾌﾟ | 支払情報③_案件大ｸﾞﾙｰﾌﾟ | ANKEN_DAI_GRP_CD_NM_3 | VWTGM010（3支払情報・処理順2=3）.案件大ｸﾞﾙｰﾌﾟ ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M10') | ③_案件大ｸﾞﾙｰﾌﾟ | ー ー |
| 291 | 支払情報③_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 支払情報③_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ANKEN_SYO_GRP_CD_3 | VWTGM010（3支払情報・処理順2=3）.案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ ← 契約支払情報ﾏｽﾀ.ANKEN_SYO_GRP_CD | ③_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ー ー |
| 292 | 支払情報③_案件小ｸﾞﾙｰﾌﾟ | 支払情報③_案件小ｸﾞﾙｰﾌﾟ | ANKEN_SYO_GRP_CD_NM_3 | VWTGM010（3支払情報・処理順2=3）.案件小ｸﾞﾙｰﾌﾟ ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M11') | ③_案件小ｸﾞﾙｰﾌﾟ | ー ー |
| 293 | 支払情報③_採算管理区分 | 支払情報③_採算管理区分 | PROFIT_MANAGE_KIND_3 | VWTGM010（3支払情報・処理順2=3）.採算管理区分 ← 契約支払情報ﾏｽﾀ.PROFIT_MANAGE_KIND | ③_採算管理区分 | ー ー |
| 294 | 支払情報③_支払先_契約先番号 | 支払情報③_支払先_契約先番号 | PAYMENT_PERSON_3 | VWTGM010（3支払情報・処理順2=3）.支払先_契約先番号 ← 契約支払情報ﾏｽﾀ.PAYMENT_PERSON | ③_支払先_契約先番号 | ー ー |
| 295 | 支払情報③_支払方法 | 支払情報③_支払方法 | PAYMENT_DDIVISION_3 | VWTGM010（3支払情報・処理順2=3）.支払方法 ← 契約支払情報ﾏｽﾀ.PAYMENT_DDIVISION | ③_支払方法 | 半角英数 2 |
| 296 | 支払情報③_支払方法_名称 | 支払情報③_支払方法_名称 | PAYMENT_DDIVISION_NM_3 | VWTGM010（3支払情報・処理順2=3）.支払方法_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P18') | ③_支払方法_名称 | 全角 60 |
| 297 | 支払情報③_消費税扱い | 支払情報③_消費税扱い | TAX_KIND_3 | VWTGM010（3支払情報・処理順2=3）.消費税扱い ← 契約支払情報ﾏｽﾀ.TAX_KIND | ③_消費税扱い | 半角英数 2 |
| 298 | 支払情報③_消費税扱い_名称 | 支払情報③_消費税扱い_名称 | TAX_KIND_NM_3 | VWTGM010（3支払情報・処理順2=3）.消費税扱い_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P10') | ③_消費税扱い_名称 | 全角 60 |
| 299 | 支払情報③_初回支払金額 | 支払情報③_初回支払金額 | FIRST_PAY_FEE_3 | VWTGM010（3支払情報・処理順2=3）.初回支払金額 ← TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_FEE ) | ③_初回支払金額 | ー ー |
| 300 | 支払情報③_初回支払消費税額 | 支払情報③_初回支払消費税額 | FIRST_PAY_TAX_3 | VWTGM010（3支払情報・処理順2=3）.初回支払消費税額 ← TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_TAX ) | ③_初回支払消費税額 | ー ー |
| 301 | 支払情報③_初回支払日 | 支払情報③_初回支払日 | FIRST_PAY_DATE_3 | VWTGM010（3支払情報・処理順2=3）.初回支払日 ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_DATE ), 'YYYY/MM/DD' ) | ③_初回支払日 | ー ー |
| 302 | 支払情報③_初回支払期間対象FROM | 支払情報③_初回支払期間対象FROM | FIRST_PAY_FROM_3 | VWTGM010（3支払情報・処理順2=3）.初回支払期間対象FROM ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_FROM \|\| '01' ), 'YYYY/MM/DD' ) | ③_初回支払期間対象FROM | ー ー |
| 303 | 支払情報③_初回支払期間対象TO | 支払情報③_初回支払期間対象TO | FIRST_PAY_TO_3 | VWTGM010（3支払情報・処理順2=3）.初回支払期間対象TO ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_TO \|\| '01' ), 'YYYY/MM/DD' ) | ③_初回支払期間対象TO | ー ー |
| 304 | 支払情報③_初回消費税調整額 | 支払情報③_初回消費税調整額 | FIRST_TAX_ADJUSTMENTS_3 | VWTGM010（3支払情報・処理順2=3）.初回消費税調整額 ← TO_CHAR(契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS ) | ③_初回消費税調整額 | ー ー |
| 305 | 支払情報③_初回消費税調整理由 | 支払情報③_初回消費税調整理由 | FIRST_TAX_ADJUSTMENTS_REASON_3 | VWTGM010（3支払情報・処理順2=3）.初回消費税調整理由 ← 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_REASON | ③_初回消費税調整理由 | ー ー |
| 306 | 支払情報③_初回消費税調整理由_名称 | 支払情報③_初回消費税調整理由_名称 | FIRST_TAX_ADJUSTMENTS_REA_NM_3 | VWTGM010（3支払情報・処理順2=3）.初回消費税調整理由_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') | ③_初回消費税調整理由_名称 | ー ー |
| 307 | 支払情報③_初回消費税備考 | 支払情報③_初回消費税備考 | FIRST_TAX_ADJUSTMENTS_MEMO_3 | VWTGM010（3支払情報・処理順2=3）.初回消費税備考 ← 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_MEMO | ③_初回消費税備考 | ー ー |
| 308 | 支払情報③_継続支払金額 | 支払情報③_継続支払金額 | COUNT_PAY_FEE_3 | VWTGM010（3支払情報・処理順2=3）.継続支払金額 ← TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_FEE ) | ③_継続支払金額 | ー ー |
| 309 | 支払情報③_継続支払消費税額 | 支払情報③_継続支払消費税額 | COUNT_PAY_TAX_3 | VWTGM010（3支払情報・処理順2=3）.継続支払消費税額 ← TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_TAX ) | ③_継続支払消費税額 | ー ー |
| 310 | 支払情報③_継続消費税調整額 | 支払情報③_継続消費税調整額 | COUNT_TAX_ADJUSTMENTS_3 | VWTGM010（3支払情報・処理順2=3）.継続消費税調整額 ← TO_CHAR( 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS ) | ③_継続消費税調整額 | ー ー |
| 311 | 支払情報③_継続消費税調整理由 | 支払情報③_継続消費税調整理由 | COUNT_TAX_ADJUSTMENTS_REASON_3 | VWTGM010（3支払情報・処理順2=3）.継続消費税調整理由 ← 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_REASON | ③_継続消費税調整理由 | ー ー |
| 312 | 支払情報③_継続消費税調整理由_名称 | 支払情報③_継続消費税調整理由_名称 | COUNT_TAX_ADJUSTMENTS_REA_NM_3 | VWTGM010（3支払情報・処理順2=3）.継続消費税調整理由_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') | ③_継続消費税調整理由_名称 | ー ー |
| 313 | 支払情報③_継続消費税備考 | 支払情報③_継続消費税備考 | COUNT_TAX_ADJUSTMENTS_MEMO_3 | VWTGM010（3支払情報・処理順2=3）.継続消費税備考 ← 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_MEMO | ③_継続消費税備考 | ー ー |
| 314 | 支払情報③_支払有効期間FROM | 支払情報③_支払有効期間FROM | PAY_EFFECTIVE_FROM_3 | VWTGM010（3支払情報・処理順2=3）.支払有効期間FROM ← 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_FROM | ③_支払有効期間FROM | ー ー |
| 315 | 支払情報③_支払有効期間TO | 支払情報③_支払有効期間TO | PAY_EFFECTIVE_TO_3 | VWTGM010（3支払情報・処理順2=3）.支払有効期間TO ← 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_TO | ③_支払有効期間TO | ー ー |
| 316 | 支払情報③_月額契約金額_税抜 | 支払情報③_月額契約金額_税抜 | MONTHLY_PAYMENT_3 | VWTGM010（3支払情報・処理順2=3）.月額契約金額_税抜 ← TO_CHAR( 契約支払情報ﾏｽﾀ.MONTHLY_PAYMENT ) | ③_月額契約金額_税抜 | ー ー |
| 317 | 支払情報③_月額有効期間FROM | 支払情報③_月額有効期間FROM | MONTHLY_PAY_EFFECTIVE_FROM_3 | VWTGM010（3支払情報・処理順2=3）.月額有効期間FROM ← 契約支払情報ﾏｽﾀ. MONTHLY_PAY_EFFECTIVE_FROM | ③_月額有効期間FROM | ー ー |
| 318 | 支払情報③_月額有効期間TO | 支払情報③_月額有効期間TO | MONTHLY_PAY_EFFECTIVE_TO_3 | VWTGM010（3支払情報・処理順2=3）.月額有効期間TO ← 契約支払情報ﾏｽﾀ.MONTHLY_PAY_EFFECTIVE_TO | ③_月額有効期間TO | ー ー |
| 319 | 支払情報③_請求方法区分 | 支払情報③_請求方法区分 | CLAIM_INFOMATION_KIND_3 | VWTGM010（3支払情報・処理順2=3）.請求方法区分 ← 契約支払情報ﾏｽﾀ.CLAIM_INFOMATION_KIND | ③_請求方法区分 | ー ー |
| 320 | 支払情報③_支払種別 | 支払情報③_支払種別 | PAYMENT_KIND_3 | VWTGM010（3支払情報・処理順2=3）.支払種別 ← 契約支払情報ﾏｽﾀ.PAYMENT_KIND | ③_支払種別 | ー ー |
| 321 | 支払情報③_支払種別_名称 | 支払情報③_支払種別_名称 | PAYMENT_KIND_NM_3 | VWTGM010（3支払情報・処理順2=3）.支払種別_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P08') | ③_支払種別_名称 | ー ー |
| 322 | 支払情報③_支払年 | 支払情報③_支払年 | PAYMENT_YEAR_3 | VWTGM010（3支払情報・処理順2=3）.支払年 ← 契約支払情報ﾏｽﾀ.PAYMENT_YEAR | ③_支払年 | ー ー |
| 323 | 支払情報③_継続支払詳細_備考 | 支払情報③_継続支払詳細_備考 | PAYMENT_MEMO_3 | VWTGM010（3支払情報・処理順2=3）.継続支払詳細_備考 ← 契約支払情報ﾏｽﾀ.PAYMENT_MEMO | ③_継続支払詳細_備考 | ー ー |
| 324 | 支払情報③_その他備考1 | 支払情報③_その他備考1 | MEMO1_3 | VWTGM010（3支払情報・処理順2=3）.その他備考1 ← 契約支払情報ﾏｽﾀ.MEMO1 | ③_その他備考1 | ー ー |
| 325 | 支払情報③_その他備考2 | 支払情報③_その他備考2 | MEMO2_3 | VWTGM010（3支払情報・処理順2=3）.その他備考2 ← 契約支払情報ﾏｽﾀ.MEMO2 | ③_その他備考2 | ー ー |
| 326 | 支払情報③_その他備考3 | 支払情報③_その他備考3 | MEMO3_3 | VWTGM010（3支払情報・処理順2=3）.その他備考3 ← 契約支払情報ﾏｽﾀ.MEMO3 | ③_その他備考3 | ー ー |
| 327 | 支払情報③_その他備考4 | 支払情報③_その他備考4 | MEMO4_3 | VWTGM010（3支払情報・処理順2=3）.その他備考4 ← 契約支払情報ﾏｽﾀ.MEMO4 | ③_その他備考4 | ー ー |
| 328 | 支払情報③_請求予定月 | 支払情報③_請求予定月 | CLAIM_MONTH_3 | VWTGM010（3支払情報・処理順2=3）.請求予定月 ← 契約支払情報ﾏｽﾀ.CLAIM_MONTH | ③_請求予定月 | ー ー |
| 329 | 支払情報③_請求予定月_名称 | 支払情報③_請求予定月_名称 | CLAIM_MONTH_NM_3 | VWTGM010（3支払情報・処理順2=3）.請求予定月_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P23') | ③_請求予定月_名称 | ー ー |
| 330 | 支払情報③_予備項目1 | 支払情報③_予備項目1 | GM03_YOBI_KOMOKU1_3 | VWTGM010（3支払情報・処理順2=3）.予備項目1 ← 契約支払情報ﾏｽﾀ.YOBI_KOMOKU1 | ③_支払_予備項目1 | ー ー |
| 331 | 支払情報③_予備項目2 | 支払情報③_予備項目2 | GM03_YOBI_KOMOKU2_3 | VWTGM010（3支払情報・処理順2=3）.予備項目2 ← 契約支払情報ﾏｽﾀ.YOBI_KOMOKU2 | ③_支払_予備項目2 | ー ー |
| 332 | 支払情報④_支払番号 | 支払情報④_支払番号 | PAY_CD_4 | VWTGM010（3支払情報・処理順2=4）.支払番号 ← 契約支払情報ﾏｽﾀ.PAY_CD | ④_支払番号 | ー ー |
| 333 | 支払情報④_支払番号枝番 | 支払情報④_支払番号枝番 | PAY_CD_BRANCH_4 | VWTGM010（3支払情報・処理順2=4）.支払番号枝番 ← 契約支払情報ﾏｽﾀ.PAY_CD_BRANCH | ④_支払番号枝番 | ー ー |
| 334 | 支払情報④_支払内容区分 | 支払情報④_支払内容区分 | FEE_MANAGE_KIND_4 | VWTGM010（3支払情報・処理順2=4）.支払内容区分 ← 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND | ④_支払内容区分 | ー ー |
| 335 | 支払情報④_支払内容区分_名称 | 支払情報④_支払内容区分_名称 | FEE_MANAGE_KIND_NM_4 | VWTGM010（3支払情報・処理順2=4）.支払内容区分_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P17') | ④_支払内容区分_名称 | ー ー |
| 336 | 支払情報④_支払内容詳細区分 | 支払情報④_支払内容詳細区分 | FEE_MANAGE_KIND_SHOSAI_4 | VWTGM010（3支払情報・処理順2=4）.支払内容詳細区分 ← 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND_SHOSAI | ④_支払内容詳細区分 | 半角英数 2 |
| 337 | 支払情報④_支払内容詳細区分_名称 | 支払情報④_支払内容詳細区分_名称 | FEE_MANAGE_KIND_SHOSAI_NM_4 | VWTGM010（3支払情報・処理順2=4）.支払内容詳細区分_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',CODE,'C02') | ④_支払内容詳細区分_名称 | 全角 60 |
| 338 | 支払情報④_支払内容その他 | 支払情報④_支払内容その他 | OTHER_PAYMENT_NAME_4 | VWTGM010（3支払情報・処理順2=4）.支払内容その他 ← 契約支払情報ﾏｽﾀ.OTHER_PAYMENT_NAME | ④_支払内容その他 | ー ー |
| 339 | 支払情報④_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 支払情報④_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ANKEN_DAI_GRP_CD_4 | VWTGM010（3支払情報・処理順2=4）.案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ ← 契約支払情報ﾏｽﾀ.ANKEN_DAI_GRP_CD | ④_案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ー ー |
| 340 | 支払情報④_案件大ｸﾞﾙｰﾌﾟ | 支払情報④_案件大ｸﾞﾙｰﾌﾟ | ANKEN_DAI_GRP_CD_NM_4 | VWTGM010（3支払情報・処理順2=4）.案件大ｸﾞﾙｰﾌﾟ ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M10') | ④_案件大ｸﾞﾙｰﾌﾟ | ー ー |
| 341 | 支払情報④_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 支払情報④_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ANKEN_SYO_GRP_CD_4 | VWTGM010（3支払情報・処理順2=4）.案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ ← 契約支払情報ﾏｽﾀ.ANKEN_SYO_GRP_CD | ④_案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | ー ー |
| 342 | 支払情報④_案件小ｸﾞﾙｰﾌﾟ | 支払情報④_案件小ｸﾞﾙｰﾌﾟ | ANKEN_SYO_GRP_CD_NM_4 | VWTGM010（3支払情報・処理順2=4）.案件小ｸﾞﾙｰﾌﾟ ← ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M11') | ④_案件小ｸﾞﾙｰﾌﾟ | ー ー |
| 343 | 支払情報④_採算管理区分 | 支払情報④_採算管理区分 | PROFIT_MANAGE_KIND_4 | VWTGM010（3支払情報・処理順2=4）.採算管理区分 ← 契約支払情報ﾏｽﾀ.PROFIT_MANAGE_KIND | ④_採算管理区分 | ー ー |
| 344 | 支払情報④_支払先_契約先番号 | 支払情報④_支払先_契約先番号 | PAYMENT_PERSON_4 | VWTGM010（3支払情報・処理順2=4）.支払先_契約先番号 ← 契約支払情報ﾏｽﾀ.PAYMENT_PERSON | ④_支払先_契約先番号 | ー ー |
| 345 | 支払情報④_支払方法 | 支払情報④_支払方法 | PAYMENT_DDIVISION_4 | VWTGM010（3支払情報・処理順2=4）.支払方法 ← 契約支払情報ﾏｽﾀ.PAYMENT_DDIVISION | ④_支払方法 | 半角英数 2 |
| 346 | 支払情報④_支払方法_名称 | 支払情報④_支払方法_名称 | PAYMENT_DDIVISION_NM_4 | VWTGM010（3支払情報・処理順2=4）.支払方法_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P18') | ④_支払方法_名称 | 全角 60 |
| 347 | 支払情報④_消費税扱い | 支払情報④_消費税扱い | TAX_KIND_4 | VWTGM010（3支払情報・処理順2=4）.消費税扱い ← 契約支払情報ﾏｽﾀ.TAX_KIND | ④_消費税扱い | 半角英数 2 |
| 348 | 支払情報④_消費税扱い_名称 | 支払情報④_消費税扱い_名称 | TAX_KIND_NM_4 | VWTGM010（3支払情報・処理順2=4）.消費税扱い_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P10') | ④_消費税扱い_名称 | 全角 60 |
| 349 | 支払情報④_初回支払金額 | 支払情報④_初回支払金額 | FIRST_PAY_FEE_4 | VWTGM010（3支払情報・処理順2=4）.初回支払金額 ← TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_FEE ) | ④_初回支払金額 | ー ー |
| 350 | 支払情報④_初回支払消費税額 | 支払情報④_初回支払消費税額 | FIRST_PAY_TAX_4 | VWTGM010（3支払情報・処理順2=4）.初回支払消費税額 ← TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_TAX ) | ④_初回支払消費税額 | ー ー |
| 351 | 支払情報④_初回支払日 | 支払情報④_初回支払日 | FIRST_PAY_DATE_4 | VWTGM010（3支払情報・処理順2=4）.初回支払日 ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_DATE ), 'YYYY/MM/DD' ) | ④_初回支払日 | ー ー |
| 352 | 支払情報④_初回支払期間対象FROM | 支払情報④_初回支払期間対象FROM | FIRST_PAY_FROM_4 | VWTGM010（3支払情報・処理順2=4）.初回支払期間対象FROM ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_FROM \|\| '01' ), 'YYYY/MM/DD' ) | ④_初回支払期間対象FROM | ー ー |
| 353 | 支払情報④_初回支払期間対象TO | 支払情報④_初回支払期間対象TO | FIRST_PAY_TO_4 | VWTGM010（3支払情報・処理順2=4）.初回支払期間対象TO ← TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_TO \|\| '01' ), 'YYYY/MM/DD' ) | ④_初回支払期間対象TO | ー ー |
| 354 | 支払情報④_初回消費税調整額 | 支払情報④_初回消費税調整額 | FIRST_TAX_ADJUSTMENTS_4 | VWTGM010（3支払情報・処理順2=4）.初回消費税調整額 ← TO_CHAR(契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS ) | ④_初回消費税調整額 | ー ー |
| 355 | 支払情報④_初回消費税調整理由 | 支払情報④_初回消費税調整理由 | FIRST_TAX_ADJUSTMENTS_REASON_4 | VWTGM010（3支払情報・処理順2=4）.初回消費税調整理由 ← 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_REASON | ④_初回消費税調整理由 | ー ー |
| 356 | 支払情報④_初回消費税調整理由_名称 | 支払情報④_初回消費税調整理由_名称 | FIRST_TAX_ADJUSTMENTS_REA_NM_4 | VWTGM010（3支払情報・処理順2=4）.初回消費税調整理由_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') | ④_初回消費税調整理由_名称 | ー ー |
| 357 | 支払情報④_初回消費税備考 | 支払情報④_初回消費税備考 | FIRST_TAX_ADJUSTMENTS_MEMO_4 | VWTGM010（3支払情報・処理順2=4）.初回消費税備考 ← 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_MEMO | ④_初回消費税備考 | ー ー |
| 358 | 支払情報④_継続支払金額 | 支払情報④_継続支払金額 | COUNT_PAY_FEE_4 | VWTGM010（3支払情報・処理順2=4）.継続支払金額 ← TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_FEE ) | ④_継続支払金額 | ー ー |
| 359 | 支払情報④_継続支払消費税額 | 支払情報④_継続支払消費税額 | COUNT_PAY_TAX_4 | VWTGM010（3支払情報・処理順2=4）.継続支払消費税額 ← TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_TAX ) | ④_継続支払消費税額 | ー ー |
| 360 | 支払情報④_継続消費税調整額 | 支払情報④_継続消費税調整額 | COUNT_TAX_ADJUSTMENTS_4 | VWTGM010（3支払情報・処理順2=4）.継続消費税調整額 ← TO_CHAR( 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS ) | ④_継続消費税調整額 | ー ー |
| 361 | 支払情報④_継続消費税調整理由 | 支払情報④_継続消費税調整理由 | COUNT_TAX_ADJUSTMENTS_REASON_4 | VWTGM010（3支払情報・処理順2=4）.継続消費税調整理由 ← 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_REASON | ④_継続消費税調整理由 | ー ー |
| 362 | 支払情報④_継続消費税調整理由_名称 | 支払情報④_継続消費税調整理由_名称 | COUNT_TAX_ADJUSTMENTS_REA_NM_4 | VWTGM010（3支払情報・処理順2=4）.継続消費税調整理由_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') | ④_継続消費税調整理由_名称 | ー ー |
| 363 | 支払情報④_継続消費税備考 | 支払情報④_継続消費税備考 | COUNT_TAX_ADJUSTMENTS_MEMO_4 | VWTGM010（3支払情報・処理順2=4）.継続消費税備考 ← 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_MEMO | ④_継続消費税備考 | ー ー |
| 364 | 支払情報④_支払有効期間FROM | 支払情報④_支払有効期間FROM | PAY_EFFECTIVE_FROM_4 | VWTGM010（3支払情報・処理順2=4）.支払有効期間FROM ← 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_FROM | ④_支払有効期間FROM | ー ー |
| 365 | 支払情報④_支払有効期間TO | 支払情報④_支払有効期間TO | PAY_EFFECTIVE_TO_4 | VWTGM010（3支払情報・処理順2=4）.支払有効期間TO ← 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_TO | ④_支払有効期間TO | ー ー |
| 366 | 支払情報④_月額契約金額_税抜 | 支払情報④_月額契約金額_税抜 | MONTHLY_PAYMENT_4 | VWTGM010（3支払情報・処理順2=4）.月額契約金額_税抜 ← TO_CHAR( 契約支払情報ﾏｽﾀ.MONTHLY_PAYMENT ) | ④_月額契約金額_税抜 | ー ー |
| 367 | 支払情報④_月額有効期間FROM | 支払情報④_月額有効期間FROM | MONTHLY_PAY_EFFECTIVE_FROM_4 | VWTGM010（3支払情報・処理順2=4）.月額有効期間FROM ← 契約支払情報ﾏｽﾀ. MONTHLY_PAY_EFFECTIVE_FROM | ④_月額有効期間FROM | ー ー |
| 368 | 支払情報④_月額有効期間TO | 支払情報④_月額有効期間TO | MONTHLY_PAY_EFFECTIVE_TO_4 | VWTGM010（3支払情報・処理順2=4）.月額有効期間TO ← 契約支払情報ﾏｽﾀ.MONTHLY_PAY_EFFECTIVE_TO | ④_月額有効期間TO | ー ー |
| 369 | 支払情報④_請求方法区分 | 支払情報④_請求方法区分 | CLAIM_INFOMATION_KIND_4 | VWTGM010（3支払情報・処理順2=4）.請求方法区分 ← 契約支払情報ﾏｽﾀ.CLAIM_INFOMATION_KIND | ④_請求方法区分 | ー ー |
| 370 | 支払情報④_支払種別 | 支払情報④_支払種別 | PAYMENT_KIND_4 | VWTGM010（3支払情報・処理順2=4）.支払種別 ← 契約支払情報ﾏｽﾀ.PAYMENT_KIND | ④_支払種別 | ー ー |
| 371 | 支払情報④_支払種別_名称 | 支払情報④_支払種別_名称 | PAYMENT_KIND_NM_4 | VWTGM010（3支払情報・処理順2=4）.支払種別_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P08') | ④_支払種別_名称 | ー ー |
| 372 | 支払情報④_支払年 | 支払情報④_支払年 | PAYMENT_YEAR_4 | VWTGM010（3支払情報・処理順2=4）.支払年 ← 契約支払情報ﾏｽﾀ.PAYMENT_YEAR | ④_支払年 | ー ー |
| 373 | 支払情報④_継続支払詳細_備考 | 支払情報④_継続支払詳細_備考 | PAYMENT_MEMO_4 | VWTGM010（3支払情報・処理順2=4）.継続支払詳細_備考 ← 契約支払情報ﾏｽﾀ.PAYMENT_MEMO | ④_継続支払詳細_備考 | ー ー |
| 374 | 支払情報④_その他備考1 | 支払情報④_その他備考1 | MEMO1_4 | VWTGM010（3支払情報・処理順2=4）.その他備考1 ← 契約支払情報ﾏｽﾀ.MEMO1 | ④_その他備考1 | ー ー |
| 375 | 支払情報④_その他備考2 | 支払情報④_その他備考2 | MEMO2_4 | VWTGM010（3支払情報・処理順2=4）.その他備考2 ← 契約支払情報ﾏｽﾀ.MEMO2 | ④_その他備考2 | ー ー |
| 376 | 支払情報④_その他備考3 | 支払情報④_その他備考3 | MEMO3_4 | VWTGM010（3支払情報・処理順2=4）.その他備考3 ← 契約支払情報ﾏｽﾀ.MEMO3 | ④_その他備考3 | ー ー |
| 377 | 支払情報④_その他備考4 | 支払情報④_その他備考4 | MEMO4_4 | VWTGM010（3支払情報・処理順2=4）.その他備考4 ← 契約支払情報ﾏｽﾀ.MEMO4 | ④_その他備考4 | ー ー |
| 378 | 支払情報④_請求予定月 | 支払情報④_請求予定月 | CLAIM_MONTH_4 | VWTGM010（3支払情報・処理順2=4）.請求予定月 ← 契約支払情報ﾏｽﾀ.CLAIM_MONTH | ④_請求予定月 | ー ー |
| 379 | 支払情報④_請求予定月_名称 | 支払情報④_請求予定月_名称 | CLAIM_MONTH_NM_4 | VWTGM010（3支払情報・処理順2=4）.請求予定月_名称 ← ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P23') | ④_請求予定月_名称 | ー ー |
| 380 | 支払情報④_予備項目1 | 支払情報④_予備項目1 | GM03_YOBI_KOMOKU1_4 | VWTGM010（3支払情報・処理順2=4）.予備項目1 ← 契約支払情報ﾏｽﾀ.YOBI_KOMOKU1 | ④_支払_予備項目1 | ー ー |
| 381 | 支払情報④_予備項目2 | 支払情報④_予備項目2 | GM03_YOBI_KOMOKU2_4 | VWTGM010（3支払情報・処理順2=4）.予備項目2 ← 契約支払情報ﾏｽﾀ.YOBI_KOMOKU2 | ④_支払_予備項目2 | ー ー |

### データ契約と外部連携（Data Contracts & Integration）

> 外部とやり取りするデータの形と、その互換性の方針を決める節。

> _書き方_: API はリクエスト / レスポンスの schema・検証・シリアライズ形式、イベントは schema・バージョニング・互換性、サービス間は分散トランザクション（Saga / 2PC など）と整合性の方針を書く。

- **API**: 画面以外から呼ばれる API は持たない（`steering/api-standards.md` の本プロジェクトでの扱い）。画面の要求は `##### API 契約（API Contract）` のフォーム送信だけ
- **イベント**: 持たない。メッセージングを使わない（`steering/tech.md` の `## コアテクノロジ`）
- **サービス間**: 既存の契約情報は他の機能が書き換えうるが、本 feature は読むだけで、CSV は出力した時点の値で作る。作業用テーブルは実行ユーザーID で分け、同じ人が 2 つのウインドウで同時に出力した場合は防がない（後から実行した方が行を消して作り直す。Q-DS-CD-002 の 4）
- **物件基本情報登録変更との口**（pbi design、Q-DS-CD-008 の 1）：契約局DL ボタン（`/wtg070/keyakuDl`）が `/wtg100?FunctionID=WTG100` にパラメータ `applicationNo`（申請No）を足して（`/wtg100?FunctionID=WTG100&applicationNo=<申請No>`）ポップアップで開く。申請No は画面の隠し項目 `applicationNo` に `FunctionID` と同じ持ち方で持ち、検索・ページ送り・クリア・出力のフォームと一緒に送る（Q-DS-CD-009 の 5）。戻りの口は無い
- **契約情報取込との口**（ci design、Q-DS-CD-001 の 6）：出力する CSV は契約情報取込のリバースデータとして取り込む形。列の並びは出力 CSV の項目定義を正とし、取込側の表と同じであることを全機能をまたいだ確認で確かめる。値の形は、契約者区分・法人_個人区分・受電方法を名称（文字）で、消費税扱いをコードで渡し、取込はそれぞれ名称・キー3 で照合する。受電方法は取込側で先頭の「1:」「2:」を削るなどの成形をしてから照合する（ci design。横断確認 1 回目 #1）
- **CSV**（Q-DS-CD-001 の 5）：`TWTGD060` の 1 行を写す bean（`Pwtgo100CsvInfo`）に `@CsvEntity`、381 列すべてに `@CsvColumn(position = 出力 CSV の項目定義の No − 1, name = 見出し)` を付け、列の並びを出力 CSV の項目定義の No で固定する。No 6 と No 44 は見出しが同じなので position で区別する（design-check 1 回目 #2）。`CsvUtils.save(list, stream, "MS932", CsvUtils.defaultCsvConfig(), new CsvEntityListHandler<>(Pwtgo100CsvInfo.class))` で書く。見出し行は `CsvEntityListHandler` が `@CsvColumn` の position の順に name から出す。0 件のときは空の要素を 1 つ渡して見出し行だけにする。`CsvUtils` に引数は足さない。返し方は `Content-Disposition: attachment`・`application/octet-stream` のダウンロード。ファイル名はヘッダに入れるときに `Windows-31J` → `ISO-8859-1` に変える（`ServiceBase.java:252`〜`:277` と同じ）。出力管理（`TZZZM027`）は使わない

## コンポーネントとインターフェース（Components and Interfaces）

> 各コンポーネントの責務と、外部に公開する契約を確定させる節。契約は 5 種類ある。
>
> - **サービスインターフェース**: 他のコンポーネントから呼ばれる口
> - **API 契約**: 外部から HTTP で呼ばれる口
> - **イベント契約**: 非同期にやり取りするイベントの発行・購読
> - **バッチ / ジョブ契約**: 定期実行や一括処理
> - **状態管理**: 状態の持ち方と守り方
>
> _分担_: 物理配置は `## ファイル配置計画（File Structure Plan）`。全 API 共通の形式は `steering/api-standards.md` の `## リクエスト / レスポンス形式`、エラー表現は同ファイルの `## エラーハンドリング（API 契約）`。ここには論理的な責務と、このフィーチャー固有の契約を書く。

> _書き方_: まず一覧で全体像を示し、そのあと新しい境界を持つコンポーネントだけ詳細を書く。契約の種類は該当するものにチェックを入れ、同じ名前の小節だけを書く。実装上の注意やリスクは、判断に関わるものは `## 設計判断（Design Decisions）`、確認方法は `## テスト戦略（Testing Strategy）` に書く。
>
> - **ドメイン / レイヤの見出し**: ドメイン名で切るかレイヤ名で切るかはプロジェクトで決め、この節の中で揃える。複数あれば同じ形で繰り返す。`_N` は繰り返す印であり、配下のコンポーネントの `_N` と番号が対応するわけではない。
> - **サービスインターフェース**: メソッドごとに 1 行。型名は設計上の名前でよく、実装の型と一致していなくてよい。事前条件は呼ぶ側が満たしておくこと、事後条件は呼び出しが成功したときに保証されること、不変条件は処理の前後どちらでも常に成り立つことを書く。
> - **API 契約**: 1 行 1 エンドポイント。エラー列には返しうるステータスコードを列挙する。
> - **イベント契約**: 到達保証・順序保証は at-least-once / FIFO などの方式名で書く。
> - **バッチ / ジョブ契約**: 冪等性（同じ処理を何度実行しても結果が変わらない性質）をどう担保するかと、失敗時の復旧手順を書く。
> - **状態管理**: 状態が同時に更新されうる場合は、並行制御の方式まで書く。

- **監視**: 本 feature 固有の監視項目は無い。既存の WiNG の監視に任せる（`steering/non-functional.md` の `### 監視 / ヘルス`）

### コンポーネント一覧（Summary）

> このフィーチャーのコンポーネントを 1 行ずつ並べ、詳細を書くものを選ぶための節。

> _書き方_: 各行は下の詳細と対応し、コンポーネント名・ドメイン / レイヤ・目的・受け入れ基準ID は同じ値を書く。依存には主なものだけ、契約にはチェックした種類名を書く。

| コンポーネント | ドメイン / レイヤ | 目的 | 受け入れ基準ID | 依存 | 契約 |
|---|---|---|---|---|---|
| 契約情報ダウンロード Controller | 契約情報ダウンロード / Controller | 初期表示・検索・ページ送り・クリア・出力の要求を受け、同じ画面かファイルを返す | 1.1、1.5、1.6、3.1〜3.3 | 契約情報ダウンロード Service | API 契約 |
| 契約情報ダウンロード Service | 契約情報ダウンロード / Service | 検索条件の組立てとベンダー／施工会社の絞り込み、ページ、検索条件のセッション、未選択のチェック、今の申請の基地局番号の取得、作業用テーブルの作り直しと CSV の書き出し | 1.2〜1.6、2.1、2.2、3.1〜3.6 | 契約情報ダウンロード Mapper、`CodeMstService`、`CsvUtils` | サービスインターフェース |
| 契約情報ダウンロード Mapper | 契約情報ダウンロード / Mapper | 件数と表示ページの行の検索、`TWTGM080` の基地局番号の読取り、作業用テーブルの削除・登録・更新・読取り | 1.3〜1.5、2.1、2.2、3.1、3.5、3.6 | Oracle | — |
| 発行依頼書リバースデータビュー（`VWTGM010`） | 契約情報ダウンロード / DB | 契約基本・契約者・支払情報を、データ種別ごとに同じ列の形にそろえ、処理順2 を振る | 3.1 | `TWTGM010`〜`TWTGM030`、`TWTZM040` | — |
| 契約情報ダウンロード画面のテンプレートとスクリプト | 画面 / FE | 15 項目の検索条件（入力桁・IME）、一覧の 19 項目とチェック、ページ、ボタン（検索・クリア・全選択・全解除・出力）、ツールチップ、申請No の隠し項目 | 1.1、1.2、1.4、1.6、3.3 | Controller | — |

### 契約情報ダウンロード

#### 契約情報ダウンロード Controller

| 項目 | 内容 |
|---|---|
| 目的（Intent） | 初期表示・検索・ページ送り・クリア・出力の要求を受け、同じ画面かファイルを返す |
| 受け入れ基準ID | 1.1、1.5、1.6、3.1〜3.3 |
| 担当 / レビュアー | <DSN_COMPONENT_OWNER>（不要：体制（担当・レビュアー）は案件の計画書で管理する — 回答者 Junichi Noumi、2026-10-07（物件基本情報登録変更と同じ）） |

**責務と制約**:
- **主たる責務**: `@RequestMapping("/wtg100")`・`@FuncID("PWTGO100")` で 5 つの口を受ける。出力で未選択なら、セッションの条件で今のページを検索し直した一覧と `GEF-000057` を同じ画面に出し、CSV を返さない。出力が通ればファイルを返し、画面はそのまま（ブラウザーはダウンロードだけを受け、表示中の検索結果と選択が残る）
- **ドメイン境界 / トランザクションの範囲**: トランザクションを持たない（Service が持つ）
- **データ所有権 / 不変条件**: Mapper を直接呼ばない

**依存関係**:
- **呼び出し元（Inbound）**:
  - 契約情報ダウンロード画面のテンプレートとスクリプト — フォーム送信（重要度: 高）
  - 物件基本情報登録変更画面（契約局DL ボタン）— 初期表示（重要度: 高）
- **呼び出し先（Outbound）**:
  - 契約情報ダウンロード Service — すべての処理（重要度: 高）
- **外部（External）**:
  - なし — 外部システムと通信しない（重要度: —）

**契約の種類**（チェックリスト）
- [ ] サービスインターフェース（Service Interface）
- [x] API 契約（API Contract）
- [ ] イベント契約（Event Contract）
- [ ] バッチ / ジョブ契約（Batch / Job Contract）
- [ ] 状態管理（State Management）

##### API 契約（API Contract）

> 画面のフォーム送信の口であり、画面以外から呼ばれる API ではない。URL は既存の規約どおり `/wtg100/<アクション>` の 1 段にする（`steering/tech.md` の `## 命名規則`）。出力は `download` ではなく `csv`。どの口も業務の表を変えない要求で、CSRF の照合（URL の末尾が `regist`・`update`・`delete`・`approved`・`reset`・`execute`・`upload` のものだけ）に乗らない。照合の設定は変えない（Q-DS-CD-008 の 1）。Response の「画面」は契約情報ダウンロード画面（`pwtgo100.html`）を表示すること。エラーはどれも HTTP 200 で同じ画面にメッセージを出す。どの口も、申請No の隠し項目を受け取り、画面に持ち回す。

| Method | Endpoint | Request | Response | Errors |
|---|---|---|---|---|
| GET・POST | `/wtg100` | `FunctionID`（＝`WTG100`）、`applicationNo`（申請No。無くてもよい） | 画面（検索条件は空。検索条件のセッションを消す。一覧は出さない。申請No を隠し項目に置く）（1.1・1.2・1.6） | なし |
| POST | `/wtg100/search` | 15 項目の検索条件、申請No | 画面（1 ページ目の一覧。条件をセッションに置く。選択は空）（1.3〜1.5、2.1・2.2） | なし（0 件は「該当するデータはありません」） |
| POST | `/wtg100/page` | `selectPage`（表示するページ）、申請No | 画面（セッションの条件でそのページの一覧。選択は空）（1.5） | なし |
| POST | `/wtg100/clear` | 申請No | 画面（初期表示と同じ。セッションを消す。申請No は残す）（1.2） | なし |
| POST | `/wtg100/csv` | 表示中のページの行のチェックとキー（計画基地局番号＋枝番）、申請No | `WTG100_yyyyMMddHHmmss.csv` のダウンロード（`attachment`、`application/octet-stream`）（3.1〜3.6） | 入力（`GEF-000057`。画面にセッションの条件で今のページの一覧とメッセージを出し、CSV を出さない）（3.3） |

#### 契約情報ダウンロード Service

| 項目 | 内容 |
|---|---|
| 目的（Intent） | 検索条件の組立てとベンダー／施工会社の絞り込み、ページ、検索条件のセッション、未選択のチェック、今の申請の基地局番号の取得、作業用テーブルの作り直しと CSV の書き出し |
| 受け入れ基準ID | 1.2〜1.6、2.1、2.2、3.1〜3.6 |
| 担当 / レビュアー | <DSN_COMPONENT_OWNER>（不要：体制（担当・レビュアー）は案件の計画書で管理する — 回答者 Junichi Noumi、2026-10-07（物件基本情報登録変更と同じ）） |

**責務と制約**:
- **主たる責務**: コンボの選択肢を作る。検索条件（`Pwtgo100CondInfo`）から SQL に渡す条件（`Pwtgo100SearchCond`）を作り、ログイン会社コードとベンダー／施工会社の区分を足す。件数を数え、`selectListSize` の件数でページを作り、表示ページの行を一覧の値の形にする。出力では未選択を確かめ、作業用テーブルを作り直して CSV を書く
- **ドメイン境界 / トランザクションの範囲**: 検索・ページ送りは読み取りだけ。出力（`outputCsv`）は作業用テーブルの削除・登録・更新・読取りを 1 つのトランザクション（`@Transactional`。読み取り専用にしない）で行い、例外ならすべて取り消す（Q-DS-CD-002 の 3）
- **データ所有権 / 不変条件**: 書くのは作業用テーブルのログインユーザーの行だけ。絞り込みの区分と会社コードは、画面から送られた値ではなくログインユーザーから毎回作る

**依存関係**:
- **呼び出し元（Inbound）**:
  - 契約情報ダウンロード Controller — すべての処理（重要度: 高）
- **呼び出し先（Outbound）**:
  - 契約情報ダウンロード Mapper — 検索と作業用テーブル（重要度: 高）
  - `CodeMstService` — コンボの選択肢（`P21`・`C39`・`P15`）（重要度: 中）
  - `CsvUtils` — CSV の書き出し（重要度: 中）
- **外部（External）**:
  - なし — 外部システムと通信しない（重要度: —）

**契約の種類**（チェックリスト）
- [x] サービスインターフェース（Service Interface）
- [ ] API 契約（API Contract）
- [ ] イベント契約（Event Contract）
- [ ] バッチ / ジョブ契約（Batch / Job Contract）
- [ ] 状態管理（State Management）

##### サービスインターフェース（Service Interface）

| メソッド | 入力 | 出力 | エラー |
|---|---|---|---|
| 初期表示（`initDisplay`） | ログインユーザー、申請No | 空の検索条件、コンボの選択肢（どれも先頭は空）、申請No | なし |
| 検索（`search`） | 検索条件、表示するページ、ログインユーザー | 一覧の行（19 項目）と件数・ページ | なし |
| 出力（`outputCsv`） | 選んだ行のキー（計画基地局番号＋枝番）、申請No、ログインユーザー、出力先 | CSV（381 列、0 件は見出しだけ） | 未選択 → `GEF-000057`（{0}＝「対象」）を `BindingResult` に積み、作業用テーブルに触れない |

- **出力の手順**（3.1・3.5・3.6、Q-DS-CD-002 の 3・Q-DS-CD-009）:
  1. 選んだ行が 1 件も無ければ `GEF-000057` を積んで終わる
  2. 申請No があれば `TWTGM080`（会社コード＝ログイン会社、申請No）の `Kichikyoku_No` を取る。無ければ空
  3. `TWTGD050`・`TWTGD060` から、実行ユーザーID＝ログインのユーザーID の行を消す
  4. `VWTGM010` から、選んだ行（計画基地局番号＋枝番）の 1基本情報・2契約者・3支払情報の行を全部 `TWTGD050` に入れる（実行ユーザーID＝ログインのユーザーID）。このとき、選んだ行がログイン会社の `TWTGM010` にあり、検索と同じベンダー／施工会社の絞り込みに合うものだけを入れる（画面から送られたキーをそのまま信じない）。ビューと作業用テーブルは会社コードの列を持たないが、契約情報の会社は 'UQ' だけなので、他社の行が混ざることは扱わない（ビューのコード名称を会社コード 'UQ' で引くのと同じ前提。design-check 1 回目 #3）
  5. `TWTGD050` の 1基本情報の行から、1 契約 1 行で `TWTGD060` に入れる（契約基本の 46 列）
  6. `TWTGD050` の 2契約者の行のうち処理順2 が 1〜5 のものを、計画基地局番号＋枝番で突き合わせて `TWTGD060` の契約者①〜⑤に更新する
  7. `TWTGD050` の 3支払情報の行のうち処理順2 が 1〜4 のものを、同じように支払情報①〜④に更新する
  8. `TWTGD060` のログインユーザーの行を CSV の並び（`### ドメインモデル（Domain Model）`）で読み、CSV に書く
  - 作業用テーブルの行は消さずに残し、次の出力の 3. で消す
- **事前条件（Preconditions）**: ログインユーザーの会社コード・ユーザーID・ベンダー区分・施工会社区分がセッションにある。`P01` にこの画面の行がある。`TWTGD050`・`TWTGD060`・`VWTGM010` が作られている
- **事後条件（Postconditions）**: 検索の成功後、条件がセッション（"PWTGO100Form"）に置かれ、一覧は GWTG004 と同じ並びで表示ページの行だけ。出力の成功後、作業用テーブルにはログインユーザーの今回の行だけがあり、CSV はその `TWTGD060` の行を CSV の並びで書いたもの
- **不変条件（Invariants）**: ベンダー区分か施工会社区分に値のある利用者には、検索でも出力でも絞り込みが必ず付く。他の利用者の作業用テーブルの行に触れない

## 処理フロー（System Flows）

> このフィーチャーの主要な処理の流れを図で示す節。\
> _分担_: システム全体の主要ビジネスフローは `docs/architecture/system-overview.md` の `## 主要ビジネスフロー`。エラーコードの出し分けが複雑な場合は `## 機能固有のエラー処理（Error Handling）` の `### エラー時の分岐フロー`。

> _書き方_: プレースホルダは実際のコンポーネント名に置き換える。分岐・リトライ・例外時の扱いは、図に描くか図の下に文で補う。

```mermaid
sequenceDiagram
    participant U as 起案者・申請者・確認者
    participant W as 契約情報ダウンロード画面
    participant A as 契約情報ダウンロード Controller・Service
    participant D as Oracle
    U->>W: 物件基本情報登録変更画面の契約局DL ボタンでポップアップを開く（申請No）
    U->>W: 条件を入れて「検索」を押す
    W->>A: /wtg100/search（15 項目、申請No）
    A->>D: 会社コードとベンダー／施工会社の絞り込みを足し、件数を数え、1 ページ目の行を取る
    A-->>W: 一覧（19 項目、GWTG004 と同じ並び、100 件）
    U->>W: 表示中のページで行を選び「出力」を押す
    W->>A: /wtg100/csv（選んだ行のキー、申請No）
    A->>D: 今の申請の基地局番号を取り、作業用テーブルを消して作り直し、CSV の並びで読む（1 トランザクション）
    A-->>U: WTG100_yyyyMMddHHmmss.csv（画面はそのまま）
```
**フロー上の主要な判断**: 出力では画面から送られたキーを、ログイン会社と絞り込みで確かめ直してから作業用テーブルに入れる。今の申請の基地局番号は出力のときに引き、取れなければ先頭にする行が無いものとして並べる（Q-DS-CD-009）。出力の後に画面を描き直さないので、検索結果と選択は残る（Q-DS-CD-008 の 3）。

## 機能固有のエラー処理（Error Handling）

> このフィーチャー固有のエラーコードと復旧の流れを決める節。\
> _分担_: API のエラー契約は `steering/api-standards.md` の `## エラーハンドリング（API 契約）`、例外処理の方針は `steering/tech.md` の `## 例外処理`、ログ・リトライ・監視は `steering/non-functional.md` の `## 信頼性・観測性`。

- **返し方**: 未選択は既存の検索一覧と同じく `BindingResult` に積んで同じ画面に出す。画面にはセッションの条件で今のページを検索し直した一覧を出す（Q-DS-CD-008 の 3）
- **出力の失敗**: 作業用テーブルの作り直しか CSV の書き出しで例外が起きたら、トランザクションを取り消し、既存の `ExceptionResolver` に任せる（作業用テーブルは前回の行のまま残る）
- **ログ**: 本 feature 固有のログ項目は無い。契約者の氏名・住所・電話番号・メールアドレスはログに出さない（`steering/non-functional.md` の `#### 出力しない`）

### バリデーション設計

> 入力を受け付けるかどうかの判定条件を決める節。\
> _分担_: 入力検証と出力エスケープの全体方針は `steering/security.md` の `## 入力検証 / 出力エスケープ`、API 共通のバリデーション形式は `steering/api-standards.md` の `### 複数フィールドのバリデーション`。

> _書き方_: 全体方針と重複しない、このフィーチャー固有の条件だけを書く。

- サーバーで行う入力チェックは、出力のときの未選択チェックだけ（Q-DS-CD-005）
- 検索条件の桁は画面の入力桁（maxlength）と IME の入力モード（`### ドメインモデル（Domain Model）` の検索条件の表）で、桁を超えて入力させない。文字数かバイト数かは問わず、画面の maxlength で数える。形式は確かめない。`WTX-100012` は使わない（Q-DS-CD-005 の 1〜3）
- requirements 4.1（桁数・形式の条件を満たさない項目があればエラーメッセージを出して検索を止める）は、画面で桁を超えて入力させないことで満たし、サーバーでの桁・形式のチェックとメッセージは持たない。requirements 4.1 から意図して外れる。上流は Phase 5 の最後にまとめて直す（upstream-carryover）
- steering/security.md の `### 入り口 — 入力検証`（画面の層の桁数・形式のチェック）と `### 共通ルール` 1（入力はサーバー側で必ず検査する）からも意図して外れる。上流は Phase 5 の最後にまとめて直す（upstream-carryover。design-check 1 回目 #4）

| チェック対象 | 項目名 | 条件 / ルール | エラーコード | メッセージ例 | UI の対処 |
|---|---|---|---|---|---|
| 出力 | 対象（チェックボックス） | 表示中のページで 1 行以上選ばれている（3.3） | `GEF-000057`（既存。{0}＝「対象」） | 対象:対象を選択してください | 検索結果を残したまま同じ画面にメッセージを出し、CSV を返さない |

### 機能固有エラーコード

> このフィーチャーだけが返すエラーコードを一覧にする節。

> _書き方_: 例「`FEATURE_X_INVALID_STATE` / 409 / 状態遷移の不整合 / UI でステータスを取得し直す」「`FEATURE_X_DEPENDENCY_DOWN` / 503 / 外部依存が使えない / 自動リトライ後にフォールバック」。

新しく足すメッセージキーは無い（Q-DS-CD-010 の 3）。使うのは既存のキーだけ。

| エラーコード | HTTP | 意味 | 対応 |
|---|---|---|---|
| `GEF-000057`（既存。`wing/src/main/resources/messages.properties:365`） | 200（同じ画面） | 1 行も選ばずに出力した（3.3）。{0} は「対象」で、GWTG004 と同じ（`wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg002/service/Pwtgo004Service.java:706`） | 行を選んで出力し直す |

### エラー時の分岐フロー

> `### 機能固有エラーコード` で定めたコードを、どの条件で返すかを図で示す節。分岐が多く、表だけでは追いにくい場合に書く。\
> _分担_: 処理の主要な流れは `## 処理フロー（System Flows）`。

> _書き方_: 図の中の大文字の名前は実際の処理名・エラーコードに置き換える。分岐のラベル（成立 / 不成立 / 成功 / 失敗）も判定内容に合わせて書き換える。

```mermaid
flowchart TD
    A[出力の要求] --> B{表示中のページで<br/>1 行以上選ばれている}
    B -- いいえ --> X1[GEF-000057<br/>今のページの一覧を出し直す]
    B -- はい --> C[今の申請の基地局番号を取る<br/>取れなければ空]
    C --> D[作業用テーブルを消して作り直す<br/>ログイン会社と絞り込みで確かめ直す]
    D --> E{例外}
    E -- はい --> X2[取り消して ExceptionResolver]
    E -- いいえ --> F[CSV の並びで読み CSV を返す<br/>0 件なら見出しだけ]
```

## ファイル配置計画（File Structure Plan）

> このフィーチャーで追加・変更するファイルを、どのディレクトリに置くかを示す節。\
> _分担_: ディレクトリ構成の規約は `steering/architecture.md` の `## ディレクトリ構成`、ファイルやディレクトリの命名規則は `steering/tech.md` の `## 命名規則`。論理的な責務は `## コンポーネントとインターフェース（Components and Interfaces）`。ここには規約に従って置く実際のファイルだけを書く。

> _書き方_: 繰り返し現れる構造はパターンを 1 度だけ書く。個別ファイルは責務が読み取りにくいときだけ挙げる。

```
wing/src/main/
├── java/jp/co/kccs/wt/function/wtg/wtg100/       # 機能ID WTG100（Q-DS-CD-008）
│   ├── controller/Pwtgo100Controller.java        # /wtg100 の 5 つの口、@FuncID("PWTGO100")
│   ├── service/Pwtgo100Service.java
│   ├── mapper/Pwtgo100Mapper.java                # 検索、TWTGM080 の基地局番号、作業用テーブルの削除・登録・更新・読取り
│   ├── form/Pwtgo100Form.java                    # 検索条件・一覧・選択・申請No の隠し項目
│   └── bean/Pwtgo100CondInfo.java・Pwtgo100SearchCond.java・Pwtgo100SearchInfo.java・Pwtgo100CsvInfo.java   # 入力の条件・SQL の条件・一覧の 1 行・CSV の 1 行（@CsvEntity、381 列の @CsvColumn）
├── resources/jp/co/kccs/wt/function/wtg/wtg100/Pwtgo100Mapper.xml
└── webapp/WEB-INF/pages/wtg/wtg100/
    └── pwtgo100.html・pwtgo100Script.html          # 検索条件の入力桁・IME、全選択・全解除
```

DB の新しいオブジェクト（`TWTGD050`・`TWTGD060`・`VWTGM010`）の DDL と、`P01`・`ZMENUAUTH` の投入の文は、本 feature の tasks で作り、既存の DDL・投入の文と同じ置き場所に置く（Q-DS-CD-002 の 5・Q-DS-CD-007 の 3・Q-DS-CD-008 の 4）。

### 変更する既存ファイル（Modified Files）

> 新規追加ではなく、既存ファイルに手を入れる箇所を挙げる節。

> _書き方_: 何をどう変えるか、なぜ変えるかを 1 行で書く。

- <DSN_MODIFIED_FILE_N>（不要：既存のファイルは変えない。メッセージを足さず、CSRF の照合設定も変えない — Q-DS-CD-008 の 1・Q-DS-CD-010 の 3） — <DSN_MODIFIED_REASON_N>（不要：同上）

## 追加検討事項（Additional Considerations）

> 機能の振る舞いそのものではないが、実装前に決めておくことをまとめる節。配下の見出しのうち、このフィーチャーに関係するものを書く。\
> _分担_: 選択肢を比べて選んだ判断は `## 設計判断（Design Decisions）`。要件としての目標値は `requirements.md` の `## 非機能要件（Non-Functional Requirements）`。

### セキュリティ上の考慮（Security Considerations）

> 認証・機密データ・外部連携・権限を扱うフィーチャーで書く節。\
> _分担_: 横断的な防御は `steering/security.md` の `## 基本方針`、認証・認可の標準は同ファイルの `## 認証・認可`。要件としてのセキュリティ目標は `requirements.md` の `## 非機能要件（Non-Functional Requirements）`。ここには実現手段だけを書く。

> _書き方_: 想定する攻撃者と守る対象を先に決めてから、対策を書く。

- **脅威と対策**:
  - ベンダー／施工会社の利用者が他社の契約情報を探す → 絞り込みを画面の値でなくログインユーザーの区分から毎回作り、括弧でくくって AND で足す（2.2、`steering/security.md` の `#### 所有権・エンティティ境界`）。工事案件マスタに行が無い契約情報は出す（2.1。既存の WTB と違う点は `### ドメインモデル（Domain Model）`）
  - 画面から他社や範囲外の契約のキーを送って CSV に出す → 出力の手順 4. で、送られたキーをログイン会社の `TWTGM010` と同じ絞り込みで確かめ直し、合うものだけを作業用テーブルに入れる（`steering/security.md` の禁止「画面の表示だけで制御せず、サーバー側でも権限を判定する」）
  - 他の利用者の作業用テーブルの行を消す・読む → 削除・登録・更新・読取りの条件に、必ず実行ユーザーID＝ログインのユーザーID を付ける。実行ユーザーID は画面から受け取らない
  - 入力値による SQL インジェクション → SQL は `#{}` だけを使い、LIKE は `escapeSQLforLike` で逃がす（`steering/security.md` の `### 共通ルール`）
  - 一覧の値による XSS → 出力は `th:text`（同上）
- **認証・認可**: 画面を使えるかは既存の `AccessControlInterceptor` が、セッションのメニューID と `@FuncID("PWTGO100")` で `ZMENUAUTH` を引いて判定する（`wing/src/main/java/jp/co/kccs/wt/common/interceptor/AccessControlInterceptor.java:45`〜`:54`）。`PWTGO100` の行を、`PWTGO070` を登録するメニュー（［WTG070］と［WTG060］のメニュー。権限区分ごとに分かれていればそのすべて）すべてに、メニューID ごとに 1 行、`ZMENUAUTH` に足す（横断確認 1 回目 #4。Q-DS-CD-008 の 4）。渡された申請No の申請で使えるかは確かめず、社外ユーザーの範囲も当てない（Q-DS-CD-009 の 2・4）
- **データ保護 / プライバシー**: 一覧と CSV に契約者の氏名・住所・電話番号・メールアドレスが出る。出すのは絞り込みに合う契約だけで、ログに出さない。作業用テーブルには出力のたびに写しが残り、次の出力で消える（`requirements.md` の非機能要件のプライバシー、`steering/security.md` の `## 機密データ`）

### 性能とスケーラビリティ（Performance & Scalability）

> 性能・高負荷・拡張に懸念があるフィーチャーで書く節。\
> _分担_: 目標値は `requirements.md` の `## 非機能要件（Non-Functional Requirements）` を参照する。

> _書き方_: 数値は再定義せず、参照元を示す。

- **目標値の参照元と計測方法**: `requirements.md` の非機能要件（`steering/non-functional.md` 準拠。本 feature 固有の目標値は無い）。総合テストで確かめる
- **拡張の方針（水平 / 垂直）**: 既存 WiNG の構成に従い、本 feature では変えない（`steering/non-functional.md` の `### 性能・容量運用（方針）`）
- **キャッシュ / 最適化**: キャッシュは持たない。検索は件数を先に数え、表示ページの行だけを取る。出力は表示中のページで選んだ行（1 ページ 100 件まで）だけを作業用テーブルに写す。作業用テーブルは索引を持たない（Q-DS-CD-002 の 2）

### 移行方針（Migration Strategy）

> スキーマ移行やデータ移行が必要なフィーチャーで書く節。

> _書き方_: 各段階について、どこまで戻せるかを明記する。段階を図で示す場合は Mermaid のフローチャートを使う。

- **段階分け**:
  - 作業用テーブル `TWTGD050`・`TWTGD060` とビュー `VWTGM010` を作る。DDL は作業用テーブルとビューの定義（列名・型・桁、ビューの定義、絞り込みと処理順2）をもとに本 feature の tasks で作る（Q-DS-CD-002 の 5）
  - コードマスタ `WTZ/PARAM/P01` にこの画面の行（キー3＝`PWTGO100`、名称「[GWTG100]契約情報ﾀﾞｳﾝﾛｰﾄﾞ画面」、表示順 55、数値項目1＝100）を足す（Q-DS-CD-007 の 1）
  - `ZMENUAUTH` に、`PWTGO100` の行を、`PWTGO070` を登録するメニュー（［WTG070］と［WTG060］のメニュー。権限区分ごとに分かれていればそのすべて）すべてに、メニューID ごとに 1 行足す（Q-DS-CD-008 の 4、横断確認 1 回目 #4）
  - 投入の文と手順は本 feature の tasks で作り、投入は発注者が導入手順書に沿って行う（Q-DS-CD-007 の 3）
- **ロールバックを実施する条件**: <DSN_MIGRATION_ROLLBACK>（不要：既存データの移行は無く、新しいオブジェクトとマスタの行を足すだけで、ほかのコードマスタの行と同じ扱いで登録する — Q-DS-PBI-015 と同じ）
- **検証チェックポイント**: <DSN_MIGRATION_CHECKPOINT>（不要：既存データの移行は無く、テストの詳細は試験仕様書に書く — Q-DS-PBI-015 と同じ）

#### 移行対象ファイル一覧

> 移行するファイル・テーブルを漏れなく数え上げる節。\
> _分担_: ファイルごとの詳細仕様は `## コンポーネントとインターフェース（Components and Interfaces）` のバッチ / ジョブ契約と `## データモデル（Data Models）`。

> _書き方_: 処理区分は 新規 / 更新 / 廃止。移行後の扱いは 削除 / アーカイブ / 引き継ぎ先 などを書く。

| ファイル / テーブル名 | 処理区分 | レコード数見込み | 移行方法 | 移行後の扱い |
|---|---|---|---|---|
| `TWTGD050`（発行依頼書リバースデータ） | 新規（表） | 0 行（出力のたびに作り直す） | DDL を tasks で作り、発注者が導入手順書に沿って作る | ― |
| `TWTGD060`（発行依頼書フォーマット） | 新規（表） | 0 行（同上） | 同上 | ― |
| `VWTGM010`（発行依頼書リバースデータビュー） | 新規（ビュー） | ― | 同上 | ― |
| `TWTZM040`（WTZ/PARAM/P01 キー3 `PWTGO100`） | 更新（行の追加） | 1 行 | 投入の文を tasks で作り、発注者が導入手順書に沿って投入 | ― |
| `ZMENUAUTH`（`PWTGO100`） | 更新（行の追加） | `PWTGO070` を登録するメニューの数（メニューID ごとに 1 行。横断確認 1 回目 #4） | 同上 | ― |

### テスト体制 / テスト仕様

> 総合テストや受け入れテストで独立した仕様書が必要な場合に書く節。通常は `## テスト戦略（Testing Strategy）` で足りる。

> _書き方_: 連絡先は非機密の情報だけを書く。

- **テスト責任者 / 承認者**: <DSN_TEST_OWNER>（不要：体制・環境・期間・連絡先は案件の計画書で管理し、テストの詳細は試験仕様書に書くため。試験仕様書と計画書で扱う — Q-DS-PBI-015 と同じ）
- **テスト環境**: <DSN_TEST_ENVIRONMENT>（不要：体制・環境・期間・連絡先は案件の計画書で管理し、テストの詳細は試験仕様書に書くため。試験仕様書と計画書で扱う — Q-DS-PBI-015 と同じ）
- **テスト期間**: <DSN_TEST_PERIOD>（不要：体制・環境・期間・連絡先は案件の計画書で管理し、テストの詳細は試験仕様書に書くため。試験仕様書と計画書で扱う — Q-DS-PBI-015 と同じ）
- **問題発生時の連絡先**: <DSN_TEST_ESCALATION>（不要：体制・環境・期間・連絡先は案件の計画書で管理し、テストの詳細は試験仕様書に書くため。試験仕様書と計画書で扱う — Q-DS-PBI-015 と同じ）
- **詳細仕様書**: <DSN_TEST_SPEC_LINK>（不要：体制・環境・期間・連絡先は案件の計画書で管理し、テストの詳細は試験仕様書に書くため。試験仕様書と計画書で扱う — Q-DS-PBI-015 と同じ）

## テスト戦略（Testing Strategy）

> このフィーチャーで何をどの粒度で確認するかを決める節。\
> _分担_: 共通のテスト方針は `steering/tech.md` の `## テスト方針`。総合テストや受け入れテストで独立した仕様書が要る場合は `### テスト体制 / テスト仕様`。

> _書き方_: 各項目は外から確認できる期待結果とセットで書き、**受け入れ基準ID** と対応づける。受け入れ基準を確認できる分だけ書き、区分ごとに件数を揃えることは目的にしない。

- **単体（Unit）**:
  - 条件の組立て：入れた項目だけが条件に入り、前方一致（代表契約局番・代表契約枝番を含む）・部分一致の値が `escapeSQLforLike` で逃がされ、コンボの 3 項目は一致になる（1.3）
  - 絞り込み：ベンダー区分だけ・施工会社区分だけ・両方に値のある利用者で、値のある区分だけが条件に入り、工事案件マスタの行が無い契約を出す条件が OR で付く。両方空なら付かない（2.1・2.2）
  - 初期表示：検索条件が空で、申請No が隠し項目に入り、検索条件の初期値に使われない（1.1・1.2・1.6）
  - 件数：1 ページの件数が `P01` の `PWTGO100` の行（100）で、101 件なら 2 ページ。上限・警告のメッセージが出ない（1.5）
  - 出力：未選択で `GEF-000057`（{0}＝対象）が積まれ、作業用テーブルに触れない。選んだときは、削除 → `TWTGD050` の登録 → `TWTGD060` の登録・契約者の更新・支払の更新 → 読取りの順に、実行ユーザーID＝ログインのユーザーID で Mapper が呼ばれる。申請No が無いとき・物件申請情報に無いときは、先頭にする基地局番号が空で並ぶ（3.1・3.3・3.5・3.6）
  - CSV：見出し行が出力 CSV の項目定義の 381 の見出しのとおり（No 6・No 44 が同じ見出し）で、No 6 に基地局名_ｶﾅ、No 44 に予備項目3 の値が出る。全項目のダブルクォート、CRLF、MS932、ファイル名 `WTG100_yyyyMMddHHmmss.csv`、0 件で見出しだけ（3.1・3.2）
  - 自動テストは JUnit 4.12 と spring-test で書き、Mapper の代わりは手書きの代替クラスにする。結果は Maven Surefire の XML・HTML を使い、カバレッジは取らない（`steering/tech.md` の `## テスト方針`。物件基本情報登録変更と同じ。Q-DS-PBI-014）
- **結合（Integration）**:
  - Oracle を使う確認（15 項目の SQL、絞り込みの NOT EXISTS と EXISTS、ページング、ビュー `VWTGM010` の 3 つのデータ種別と処理順2、契約者①〜⑤・支払情報①〜④の入れ方、CSV の並び、送られたキーの確かめ直し）は開発端末では動かせないため、総合テスト（試験仕様書）で行う（1.3〜1.5、2.1・2.2、3.1・3.4〜3.6。物件基本情報登録変更と同じ。Q-DS-PBI-014）
- **E2E / UI**:
  - 画面の操作の確認（契約局DL ボタンからのポップアップ、検索、ページ送りで選択が消えること、クリア、全選択・全解除が表示中のページだけに効くこと、入力桁と IME、ツールチップ、出力の後に検索結果と選択が残ること、未選択のエラー）は総合テスト（試験仕様書）で行う（1.1・1.2・1.4、3.3。物件基本情報登録変更と同じ。Q-DS-PBI-014・Q-DS-PBI-015）
  - 出力した CSV を契約情報取込で取り込めることは、総合テスト（試験仕様書）で行う（3.1）
- **性能 / 負荷（Performance / Load）**:
  - <DSN_TEST_PERFORMANCE_N>（不要：本 feature 固有の性能目標値は無い — `requirements.md` の非機能要件。既存 WiNG の水準に従う）

## 設計判断（Design Decisions）

> このフィーチャーで下した技術判断を、結論とその理由で残す節。\
> _分担_: セキュリティ・性能・移行など、実装前に決めておく観点は `## 追加検討事項（Additional Considerations）`。比較表や調査資料そのものは `## 補足資料（Supporting References）`。ここには選択肢を比べて選んだことだけを書く。

> _書き方_: 1 つの判断につき 1 ブロック。判断 2 以降も同じ形で追加する。背景には「なぜ判断が必要になったか」を書く。判断は選んだ結論だけを言い切る。採用理由には、他の案ではなくこれを選んだ決め手だけを書く。代替案は実際に検討したものだけを不採用の理由とセットで挙げ、検討していない案は書かない。採用による影響には、引き受ける負担・残るリスク・後で見直す条件を書く。

### 判断 1: CSV は 381 列の値を持つ作業用テーブルで組み立てる

- **背景（Context）**: requirements 3.6 は、出力の前にログインユーザーの作業用テーブルの行を消して作り直すことを求める。1 契約に契約者・支払情報が複数行あり、381 列の 1 行に並べ替える必要がある
- **判断（Decision）**: ビュー `VWTGM010` でデータ種別ごとに列をそろえて `TWTGD050` に写し、`TWTGD060`（381 列）に基本 → 契約者 → 支払の順で 1 契約 1 行に組み立ててから読む（Q-DS-CD-002）
- **採用理由（Rationale）**: 回答者の決定に従う。CSV の 1 行と同じ形の表を読むだけで書き出せ、見出しも `TWTGD060` の列の表示名で決まる
- **代替案（Alternatives）**: 作業用テーブルにはキー（計画基地局番号＋枝番と出力順）だけを持ち、CSV を作るときに既存の表と結合する案（質問の下書きの案）— 回答者が 381 列の値をそのまま持つ形を選んだため採らない
- **採用による影響（Consequences）**: 新しい表 2 つとビュー 1 つを作る。作業用テーブルに契約者の個人情報の写しが次の出力まで残る。同じ人が同時に 2 つのウインドウで出力すると、後の方が先の方の行を消す（防がない。Q-DS-CD-002 の 4）

### 判断 2: ページをまたいだ選択は覚えない

- **背景（Context）**: 一覧は 1 ページ 100 件で、チェックの値は表示中のページの行だけが送られる（GWTG004 と同じ作り）
- **判断（Decision）**: 出力するのは表示中のページで選んだ行だけにし、検索し直し・ページの移動・クリアで選択を消す。全選択・全解除も表示中のページだけに効く（Q-DS-CD-006 の B）
- **採用理由（Rationale）**: 回答者の決定に従う。既存の GWTG004 と同じ作りで済み、サーバーに選択を持たなくてよい
- **代替案（Alternatives）**: ページをまたいで選択をセッションに覚える案（Q-DS-CD-006 の A）— 回答者が B を選んだため採らない
- **採用による影響（Consequences）**: 100 件を超える契約を 1 つの CSV にまとめることはできない（ページごとに出力する）

### 判断 3: 工事案件マスタに行が無い契約情報は絞り込みで落とさない

- **背景（Context）**: 既存の WTB の絞り込みは `EXISTS` だけで、工事案件マスタに行が無い契約情報は区分に値のある利用者に出ない。requirements 2.1 はそれらを出すことを求める
- **判断（Decision）**: 「工事案件マスタの行が無い、または値のある区分に合う行がある」を絞り込みの条件にする。計画マスタに無い契約情報も行が無いものとして出す（2.1・2.2、Q-DS-CD 冒頭の訂正 13）
- **採用理由（Rationale）**: requirements 2.1 と回答者の訂正に従う。比べる列と区分の扱いは既存の WTB と同じにする
- **代替案（Alternatives）**: 既存の WTB と同じ `EXISTS` だけにする案 — requirements 2.1 に合わないため採らない
- **採用による影響（Consequences）**: `steering/security.md` 285 行目の「既存の WTB と同じ方式」から意図して外れる。上流は Phase 5 の最後にまとめて直す（upstream-carryover）

## 補足資料（Supporting References）

> 本文に置くと長くなる資料の置き場所を示す節。\
> _分担_: 調査の結論は `## 設計判断（Design Decisions）` に要約だけを書く。ここには資料のありかだけを書く。

> _書き方_: 資料には巨大な型定義、製品比較、全カラム表などを挙げる。内容にはその資料を見ると何が分かるかを書く。参照先には変わりにくいパスまたは URL を書き、確定していなければ未定と書く。

| 資料 | 内容 | 参照先 |
|---|---|---|
| 出力の定義（CSV の 381 列） | 見出し、`TWTGD060` の列と物理名、取得元（`VWTGM010` の列と元の表の列）、契約者①〜⑤・支払情報①〜④の入れ方、並び、0 件のとき（回答者が渡した表のとおりに本文へ取り込んだもの。本書の正） | 本書「物理データモデル」の `#### 出力 CSV の項目定義（381 列）` |
| 作業用テーブルとビュー | `TWTGD050` の 60 列・`TWTGD060` の形・`VWTGM010` のデータ種別ごとの列、出力の流れ、絞り込みと処理順2（回答者が渡した表のとおりに本文へ取り込んだもの。本書の正。DDL の元） | 本書「物理データモデル」の `#### 作業用テーブルとビューの定義` |
| 既存の契約情報検索／一覧の手本 | 検索条件の列と一致の仕方、1 契約 1 行のまとめ方、並び、契約先の取り方、全選択・全解除、ページング | `wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg002/controller/Pwtgo004Controller.java`・`wing/src/main/resources/jp/co/kccs/wt/function/wtg/wtg002/Pwtgo004Mapper.xml`・`wing/src/main/webapp/WEB-INF/pages/wtg/wtg002/pwtgo004Script.html` |
| ベンダー／施工会社の絞り込みの手本 | 区分の取り方と、値のある区分だけで比べる形 | `wing/src/main/resources/jp/co/kccs/wt/function/wte/wte020/Pwteo021Mapper.xml`・`WTX/WEB-INF/src/jp/co/kccs/wt/wtb/wtb020/PWTBO021Action.java` |
| 件数の共通処理とダウンロード | 1 ページの件数（`P01`）、ページング、ファイル名のヘッダの入れ方 | `wing/src/main/java/jp/co/kccs/wt/common/service/ServiceBase.java` |
| CSV の共通部品と物件基本情報登録変更との口 | `CsvUtils`、契約局DL ボタン | `specs/property-basic-info/design.md` |
| 取り込む側のリバースの 381 列 | 取込側の表（並びが同じかは全機能をまたいだ確認で確かめる） | `specs/contract-info-import/design.md` |

---

_「どう作るか」を確定させる文書。_
