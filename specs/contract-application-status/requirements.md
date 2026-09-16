---
feature: contract-application-status
status: approved
updated_at: 2026-09-16T13:08:57+09:00
---

# 要件定義書

> このファイルは **「何を作るか」「完了の判定基準は何か」** の正です。
> 自律エージェントが解釈ぶれを起こさないよう、受け入れ基準は **EARS 形式** で記述してください。
> このフィーチャーが承認 (`status: approved`) されてから `design.md` の作成に進みます。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

## Introduction（概要）

> このフィーチャーが何のために、誰のためにあるかを 2〜3 段落で書く。`背景` はなぜ今このフィーチャーが必要か、`対象ユーザー` は想定する利用者像、`期待する変化` はこのフィーチャーがあると何が変わるか。

物件契約情報申請状況の検索／一覧は、契約書発行依頼の進み具合を確認するための画面を新規に作成する機能である（REQ-012）。検索項目は 20 項目程度を想定し（REQ-013）、絞り込んだ結果を一覧に表示したうえで CSV として出力できるようにする（REQ-014）。

表示の対象になるのは、`property-basic-info` が登録・申請した物件基本情報と、`issue-request` が登録・申請した発行依頼書の申請状況である。本フィーチャーはそれらを**参照して見せる側**であり、申請状況そのものを作り出さない。

担当者が申請状況を検索・一覧・CSV 出力して確認を終えられるため User Feature である（`.aidd/feature-list.md`）。表示対象のデータを生成する `property-basic-info`（優先度 2）と `issue-request`（優先度 4）に依存するため、優先度 5 に置かれている。

- **背景**: 契約書発行依頼業務が WiNG の WTG 機能で管理されておらず（REQ-001）、申請がどこまで進んでいるかを確認する手段が WiNG 上に無い。誤入力による不備指摘のやり取りが契約書発行までの納期を延ばしており（REQ-003）、進み具合の把握は納期短縮の前提になる
- **対象ユーザー**: 契約書発行依頼業務を担当する社員（`steering/product.md` の対象ユーザー）、および権限制御の対象となるベンダー・施工会社（REQ-046）
- **期待する変化**: 契約書発行依頼の進み具合を WiNG 上の検索・一覧で確認でき、必要に応じて CSV として取り出せるようになる（REQ-012 / REQ-014。`steering/product.md` の主要ユースケース 1）

> プロダクトレベルの目的・価値は steering の `product.md` を参照。ここではこのフィーチャー固有の文脈を書く。

## 業務フロー（任意）

> 業務システムなど人とシステムの責務境界を整理する必要がある場合のみ記述する。
> 承認フロー・今まで紙で行っていた作業をシステムが担う場合など、人の判断が介在するステップを明示したいときに有効。
> 不要なフィーチャーではこのセクションごと削除してよい。
> `対象業務` はこのフィーチャーが自動化・支援する業務名、`Before` は現在の手順（紙・口頭・別システムでの対応方法を含む）、`After` はシステム稼働後の手順、`人が介在するステップ` は承認・確認・例外処理などシステム外の人的操作。

> **不要（記入者: 人間 / 2026-09-16）**: 本フィーチャーは申請状況を検索して見せる参照系であり、承認フローを持たず（承認フローは `property-basic-info` の REQ-018）、紙で行っていた作業の置き換えも含まない。テンプレートが本セクションを有効とする条件に当たらないため、以下のスロットを未記入のまま残す。

- **対象業務**: <BUSINESS_FLOW_TARGET>
- **Before（現状の業務手順）**: <BUSINESS_FLOW_BEFORE>
- **After（システム導入後）**: <BUSINESS_FLOW_AFTER>
- **人が介在するステップ**: <BUSINESS_FLOW_HUMAN_STEPS>

> **記法**: Mermaid `sequenceDiagram`（スイムレーン形式）。人とシステムの責務境界が図で追える形にする。図が不要なら本スロットを残して直後に不要理由を書く。

<BUSINESS_FLOW_DIAGRAM>

<!-- 不要理由: 人の判断が介在するステップを持たず、検索・一覧・CSV 出力のみで完結するため図を作成しない。 -->

> システム全体の主要ビジネスフローは `docs/architecture/system-overview.md §主要ビジネスフロー` を参照。

## Boundary Context（境界文脈）

> スコープの誤読が起こりやすい場合や、隣接するシステム / スペックに影響する場合は必ず記述する。
> `_N` の行を項目の数だけ増やす。`Out of Scope` は扱わない振る舞いに加えて理由または委譲先を書く。`Adjacent` は前提として動いている他フィーチャー / API / バッチ、およびこのフィーチャーが依頼している外部側の責務を書く。

- **In Scope（このフィーチャーで扱う）**:
  - 物件契約情報申請状況の検索／一覧画面を新規に作成する（REQ-012）
  - 20 項目程度の検索条件で絞り込む（REQ-013）
  - 絞り込んだ結果を一覧に表示する（REQ-012）
  - 一覧の内容を CSV として出力する（REQ-014）
  - ログインユーザーの会社コードによるデータ範囲の絞り込み（`steering/security.md` の所有権・エンティティ境界）
- **Out of Scope（扱わない）**:
  - 申請状況そのものを作り出す処理（物件基本情報・発行依頼書の登録・変更、申請・承認、ステータスと履歴の更新）。`property-basic-info`（REQ-015〜REQ-022）と `issue-request`（REQ-026〜REQ-034）が持つ。**本フィーチャーは参照のみを行う**
  - **申請状況の値を本フィーチャーが決めること**。本フィーチャーは `property-basic-info` と `issue-request` が持つデータを参照して表示する参照系であり、表示する値の内容を自ら生み出さない。参照の実現手段としてテーブルを設けるかどうかは、参照の経路（未確定事項 ⑥）の確定に伴う設計判断であり、**本項の対象外／対象内の区別とは別の話である**
  - 承認フローの段階・承認者・ステータスの値の定義。`property-basic-info` が持つ（REQ-018 / REQ-019）
  - 進捗管理DBインポート用出力（CSV）。`property-basic-info` が持つ（REQ-021）。本フィーチャーの CSV 出力（REQ-014）は申請状況の一覧を出力するものであり、用途と出力先が異なる
  - 契約情報のダウンロード用 CSV。`contract-info-download` が持つ（REQ-044 / REQ-045 / REQ-047）
  - 稟議資料の帳票出力・PDF 表示。`property-basic-info` が持つ（REQ-023 / REQ-024 / REQ-025）
  - 権限制御の方式そのものの定義。方式の正は `steering/security.md` であり、本フィーチャーはそれに従う（REQ-046 は `制約` 分類のため feature 割当の分母外 — `.aidd/feature-list.md`）
- **Adjacent（隣接システム / 隣接スペックへの期待）**:
  - `property-basic-info`: 物件基本情報とそのステータス・履歴を登録・更新する。本フィーチャーはそれを検索・表示の対象とする（REQ-015 / REQ-019 / `.aidd/feature-list.md` の `依存` 列）
  - `issue-request`: 発行依頼書とその申請・承認の状態を登録・更新する。本フィーチャーはそれを検索・表示の対象とする（REQ-026 / REQ-034 / `.aidd/feature-list.md` の `依存` 列）
  - 既存 WiNG の共通基盤: 認証・セッション（`LoginService` / `SessionCheckInterceptor`）、権限制御（`AccessControlInterceptor` + `@FuncID`）、コードマスタ取得（`CodeMstService`）、ファイルダウンロード（`DownLoadFileInfo`）を提供する（`steering/architecture.md` の共通基盤 / `steering/security.md`）

## Requirements（要件）

> 要件 ID は **数値**（`1`, `1.1`, `2`, `2.1` ...）のみ。`A`, `B` などのアルファベット ID は使わない。
> 各要件は **User Story** + **Acceptance Criteria（EARS 形式）** で構成する。
> **`### Requirement` のブロックを要件の数だけ複製する。** 要件領域名は、その要件がどの範囲を扱うかが分かる名前にする。

### Requirement 1: 物件契約情報申請状況の検索／一覧画面の提供

> 由来する要求ID: REQ-012

**User Story**: 契約書発行依頼業務の担当者として、物件契約情報の申請状況を WiNG 上で一覧したい。なぜなら契約書発行依頼がどこまで進んでいるかを確認する手段が今は無いから。

#### Acceptance Criteria（EARS 形式）

> 1 項目 = 1 基準。`_N` の行を基準の数だけ増やす。下の早見表のいずれかのパターンに当てはめて書く。

1. The system shall 物件契約情報申請状況を検索・一覧する画面を新規に作成し、画面ID・PGID を既存の体系（`GWTG` + 3 桁 / `PWTGO` + 3 桁）に従って採番する（REQ-051 / `steering/tech.md` の命名規則）。採番の具体値と、画面を何本のプログラムに分割するかは基本設計で確定する（未確定事項 ①）。
2. When 担当者が検索を実行したとき、the system shall 条件に合致する申請状況を一覧として画面に表示する（REQ-012）。
3. The system shall 一覧の 1 行が表す単位（物件基本情報 1 件か、発行依頼書 1 件か、両者を紐づけた 1 件か）を定め、その単位を識別するキーを一覧に含める。**単位と、`property-basic-info` のステータス（REQ-019）と `issue-request` の申請・承認の状態（REQ-034）をどう合成して「申請状況」として見せるかは基本設計で確定する**（未確定事項 ②）。
4. If 条件に合致する申請状況が 1 件も無い場合、then the system shall 一覧を空にし、該当が無いことをメッセージIDに対応する文言で知らせる（`steering/security.md` の共通ルール 2 / `steering/api-standards.md` のエラーハンドリング）。
5. If ログインしていないセッションから本画面のリクエストが行われた場合、then the system shall 画面を表示せずログイン画面へ遷移させる（`steering/security.md` の認証フロー）。
6. If ログインユーザーが本画面の機能ID（PGID）に対する権限を持たない場合、then the system shall 画面を表示せずエラー画面にメッセージIDに対応する文言を表示する（`steering/security.md` の認可 / `InvalidAccessErrorException`）。
7. The system shall 検索の SQL の `WHERE` 条件に、ログインユーザーの会社コードを必ず含める（`steering/security.md` の所有権・エンティティ境界 / `steering/database.md` のクエリパターン）。
8. The system shall ベンダー／施工会社に対するデータ範囲の制御を、既存 WTB（計画・工程管理）と同様の方式に従って行う（REQ-046 / `steering/security.md` の認可）。「既存 WTB と同様の方式」の実体は要求一覧・steering のいずれからも決まらないため、基本設計で確定する（未確定事項 ⑤）。
9. The system shall 申請状況を参照のみで扱い、本画面から物件基本情報・発行依頼書の内容を更新しない（`## Boundary Context` の `Out of Scope`）。
10. The system shall 一覧の表示件数の上限と並び順を SQL 側で確定させ、全件をメモリに読み込んでからの絞り込みを行わない（`steering/database.md` のクエリパターン）。上限値と既定の並び順は基本設計で確定する（未確定事項 ③）。
11. If 条件に合致する件数が一覧の表示件数の上限を超えた場合、then the system shall **上限までを表示したうえで、件数が上限を超えたため絞り込みが必要であることをメッセージIDに対応する文言で知らせる**（`steering/api-standards.md` の一覧取得節は共通のページネーション形式を持たないため、本フィーチャーで振る舞いを定める）。上限超過時にページ送りを設けるかどうかは基本設計で確定する（未確定事項 ③）。
12. The system shall 一覧に表示する項目を、基本設計で確定した内容に従う（未確定事項 ②）。

### Requirement 2: 20 項目程度の検索条件

> 由来する要求ID: REQ-013

**User Story**: 担当者として、多くの条件を組み合わせて申請状況を絞り込みたい。なぜなら対象が多く、見たい範囲を特定しないと確認が終わらないから。

#### Acceptance Criteria（EARS 形式）

1. The system shall 物件契約情報申請状況の検索条件として **20 項目程度**を備える（REQ-013）。条件の項目そのものは基本設計で確定する（未確定事項 ②）。
2. The system shall 入力された条件のみを検索に用い、未入力の条件は絞り込みに影響させない（`steering/database.md` のクエリパターンの「検索条件の可変長」。MyBatis の動的 SQL で条件の有無により分岐させる）。
3. The system shall 検索条件を Form のフィールドとして POST で受け取る（`steering/api-standards.md` の一覧取得の注記）。
4. If 検索条件の入力チェックでエラーが検出された場合、then the system shall 検索を行わず元の画面を再表示し、`BindingResult` に積んだ全件のエラーを該当項目の近くに表示する（`steering/api-standards.md` のエラーハンドリング）。各条件の桁・書式・必須の定義は基本設計で確定する（未確定事項 ②）。
5. The system shall 選択式の検索条件のうち区分値にあたるものを、コードマスタ（`CodeMstService` が参照するコードマスタ）から取得し、ソースに区分値を直書きしない（`steering/database.md` の業務コード・区分値・採番の設計ルール / `steering/tech.md` のコード規約）。どの条件が区分値にあたるかは基本設計で確定する（未確定事項 ②）。

### Requirement 3: 申請状況の CSV 出力

> 由来する要求ID: REQ-014

**User Story**: 担当者として、絞り込んだ申請状況を CSV として取り出したい。なぜなら画面の外で集計・共有したいから。

#### Acceptance Criteria（EARS 形式）

1. When 担当者が CSV 出力の操作を行ったとき、the system shall **一覧と同じ SQL の結果**を CSV として出力する（REQ-014 / `steering/database.md` のクエリパターンの「CSV 出力」。出力のためだけに別条件の SQL を作らない）。
2. The system shall CSV 出力を、一覧の検索を実行した後にのみ行えるようにする。検索を実行していない状態で CSV 出力の操作が行われた場合は出力せず、検索が必要であることをメッセージIDに対応する文言で知らせる。**「検索を実行した後」であることをどう判定するか（検索条件を Form で再送するか、画面間で引き渡すか）は基本設計で確定する**（未確定事項 ⑦）。画面間で引き渡す構成を採る場合は、セッションキーの有効時間（`wing-web.properties` の `PARAM_SESSION_KEY_PERIOD` = 10 秒）の制約を受ける（`steering/security.md` のセッション / トークンの保管・転送）。
3. The system shall CSV の出力にも**一覧と同じ表示件数の上限と並び順を SQL 側で適用する**（`steering/database.md` のクエリパターン「CSV 出力は一覧と同じ SQL の結果を用いる」/ `steering/non-functional.md` の性能・容量運用「一覧・CSV 出力は表示件数の上限と並び順を SQL 側で確定させる」）。**上限を超える件数を取り出す必要がある場合の扱い（CSV のみ上限を別に設けるか、絞り込みを促すか）は基本設計で確定する**（未確定事項 ③）。
4. The system shall CSV を `Content-Disposition` を付けたレスポンスとして返す。**ファイル名の規約（固定名か、出力日時や検索条件を含めるか）は基本設計で確定する**（未確定事項 ④）。`steering/api-standards.md` はファイル名の共通規約を持たない。
5. The system shall CSV の文字コードを既存の設定（`wing-web.properties` の `CHARSET`）に従わせ、区切り・引用符の扱いを機能ごとに変えない（`steering/security.md` の出口 — 出力エスケープ）。
6. The system shall CSV 出力を Requirement 1 の受入基準 6・7・8 と同じ権限判定・会社コードの絞り込み・データ範囲の制御の対象とする（`steering/security.md` の機密データ「帳票・CSV の出力も同じ権限判定に従う」）。
7. The system shall CSV のファイル出力を既存のファイルダウンロードの仕組み（`DownLoadFileInfo`）に載せ、機能側で独自のダウンロード経路を作らない（`steering/architecture.md` の `### 外部 API / 外部システム` の配置「受け渡しファイルの入出力は既存のファイルアップロード／ダウンロードの仕組み（`FileUploadService` / `DownLoadFileInfo`）に載せる」）。
8. The system shall CSV に出力する項目と、一覧の表示項目との対応（同一とするか、CSV のみ項目を増減するか）を、基本設計で確定した内容に従う（未確定事項 ④）。
9. The system shall 大量件数の CSV 出力をレスポンスのストリームで返す（`steering/api-standards.md` のパラメータ配置の「大量データ」）。
10. The system shall 検索と CSV 出力のアクション名に、`steering/api-standards.md` のエンドポイントのパターンが挙げる既定の名前を用いる（CSV 出力は CSRF トークン生成の除外対象である `download` / `downLoad` / `executeDownLoad`）。**既定以外の名前を用いる場合は `servlet-context.xml` の interceptor マッピングとの整合を確認する**。本フィーチャーは参照系でありデータを更新しないため、CSRF 検証の対象となる更新系リクエストを持たない。

## Non-Functional Requirements（非機能要件）

> 当該フィーチャーで成立させるべき非機能要件のみ記述（steering で固定済みのものは引用に留める）。
> 共通 SLO・障害フロー・当番は `non-functional.md`、ログ・監視の実装標準は `non-functional.md`（観測部）を参照。
> `要件` は steering の該当ファイルへの準拠を示したうえで、このフィーチャー固有の値を書く（例: パフォーマンスなら `non-functional.md` 準拠 + p95 200ms、アクセシビリティなら WCAG 2.1 AA、プライバシーなら扱う PII と保持期間）。`計測 / 検証方法` は負荷試験・SLO ダッシュボード・スキャン・監査ログなど、その要件を確認する手段を書く。区分の行は増減してよい。

| 区分 | 要件 | 計測 / 検証方法 |
|---|---|---|
| パフォーマンス | <NFR_PERFORMANCE_REQUIREMENT>（不要 / 人間 2026-09-11: `non-functional.md` に準拠し、feature 固有の値を設けない）。**本表が設けないのは応答時間・スループット等の非機能の目標値であり、一覧の表示件数の上限と出力の扱いは機能要件として `## Requirements` 側で扱う**（`steering/non-functional.md` の性能・容量運用は方針のみを定め、値を各機能の設計に委ねている） | <NFR_PERFORMANCE_VERIFICATION>（不要 / 人間 2026-09-11: 同区分の要件を設けないため検証方法も設けない） |
| 可用性 | <NFR_AVAILABILITY_REQUIREMENT>（不要 / 人間 2026-09-11: `non-functional.md` に準拠し、feature 固有の値を設けない） | <NFR_AVAILABILITY_VERIFICATION>（不要 / 人間 2026-09-11: 同区分の要件を設けないため検証方法も設けない） |
| 運用・監視 | <NFR_OPERATIONS_REQUIREMENT>（不要 / 人間 2026-09-11: `non-functional.md` に準拠し、feature 固有の値を設けない） | <NFR_OPERATIONS_VERIFICATION>（不要 / 人間 2026-09-11: 同区分の要件を設けないため検証方法も設けない） |
| セキュリティ | `steering/security.md` 準拠。`@FuncID` と `AccessControlInterceptor` による毎リクエストの権限判定、ベンダー／施工会社に対する既存 WTB と同様のデータ範囲の制御（REQ-046。方式の実体は未確定事項 ⑤ の確定後に定める）、ログインユーザーの会社コードによる検索対象の絞り込み、CSV 出力にも同じ権限判定を適用すること、Thymeleaf の自動エスケープによる出力、MyBatis の `#{...}` による SQL 組み立て | 権限を持たないユーザーでのアクセス確認、他社の会社コードの申請状況が一覧・CSV のいずれにも現れないことの確認、ベンダー／施工会社の利用者でデータ範囲の外の申請状況が現れないことの確認、権限エラー時にユーザーID・メニューID・機能IDがログに記録されることの確認 |
| アクセシビリティ | <NFR_ACCESSIBILITY_REQUIREMENT>（不要 / 人間 2026-09-11: `non-functional.md` に準拠し、feature 固有の値を設けない） | <NFR_ACCESSIBILITY_VERIFICATION>（不要 / 人間 2026-09-11: 同区分の要件を設けないため検証方法も設けない） |
| i18n / l10n | <NFR_I18N_REQUIREMENT>（不要 / 人間 2026-09-11: `non-functional.md` に準拠し、feature 固有の値を設けない） | <NFR_I18N_VERIFICATION>（不要 / 人間 2026-09-11: 同区分の要件を設けないため検証方法も設けない） |
| プライバシー | <NFR_PRIVACY_REQUIREMENT>（不要 / 人間 2026-09-11: `non-functional.md` に準拠し、feature 固有の値を設けない） | <NFR_PRIVACY_VERIFICATION>（不要 / 人間 2026-09-11: 同区分の要件を設けないため検証方法も設けない） |
| 監査 | <NFR_AUDIT_REQUIREMENT>（不要 / 人間 2026-09-11: `non-functional.md` に準拠し、feature 固有の値を設けない） | <NFR_AUDIT_VERIFICATION>（不要 / 人間 2026-09-11: 同区分の要件を設けないため検証方法も設けない） |

## Out of Scope（明示的に対象外）

> Boundary Context だけで誤読を防ぎきれないとき、追加でここに書く。
> 1 項目 = 1 件。`_N` の行を件数だけ増やす。対象外にするものと、なぜ対象外か、どこで扱う予定かを書く。

- 既存 WTG 機能（契約情報変更・参照、支払実績データ作成／変更／参照、電力会社直受支払実績変更、契約支払情報インポート、契約基本情報インポート、インボイス情報インポート）の仕様変更。デグレードを発生させない対象であり、新規の Controller / Service / Mapper / Form を追加する形で実装する（REQ-052 / REQ-073 / `steering/tech.md` の新規機能の追加方針）
- 既存の [GWTG004] 契約情報検索／一覧との条件・表示項目の一致。REQ-045 は `contract-info-download` の要求であり、本フィーチャーの検索条件（REQ-013）はそれとは別に定める

## Dependencies / Assumptions（前提と依存）

> `前提` はこのフィーチャーが成立するために真でなければならない事項、`依存` は他フィーチャー / 既存システム / 外部 API / データ、`未確定事項` は調査・確認待ちのトピック（design に進む前に解消する）。

- **前提**: 既存 WiNG の認証・セッション・権限制御の仕組み（`LoginService` / `SessionCheckInterceptor` / `AccessControlInterceptor`）がそのまま利用できること（REQ-009 / REQ-053）。`property-basic-info` と `issue-request` が申請状況として表示できるデータ（ステータス・履歴・申請/承認の状態）を保持していること（REQ-019 / REQ-034）
- **依存**: `.aidd/feature-list.md` の `依存` 列は `property-basic-info`・`issue-request`。両 feature が登録・申請したデータを表示対象とするため、表示対象を生成する側が先行する必要がある。既存 WiNG の共通基盤（認証・セッション・権限制御・コードマスタ・ファイルダウンロード）にも依存する
- **未確定事項**: 次の 7 件は **いずれも基本設計で確定する**（REQ-010。Phase 4 の共通の扱いとして人間が確定 / 2026-09-11）。
  - ① **画面ID・PGID の採番の具体値**と、画面を何本のプログラムに分割するか（REQ-010 / REQ-051）
  - ② **「申請状況」の単位と構成**、**検索条件の 20 項目程度の内訳**（各条件の項目・桁・書式・必須、どの条件が区分値にあたるか）、および**一覧の表示項目**（REQ-012 / REQ-013）。要求一覧は「物件契約情報申請状況」の中身を定義しておらず、「20 項目程度を想定する」までしか述べていない。単位については、一覧の 1 行が物件基本情報 1 件を表すのか、発行依頼書 1 件を表すのか、両者を紐づけた 1 件を表すのかと、その識別キー、および `property-basic-info` のステータス（REQ-019）と `issue-request` の申請・承認の状態（REQ-034）をどう合成して 1 つの「申請状況」として見せるかを確定する
  - ③ **一覧の表示件数の上限と既定の並び順**、**上限を超えた場合にページ送りを設けるかどうか**、および **上限を超える件数を CSV で取り出す必要がある場合の扱い**（CSV のみ上限を別に設けるか、絞り込みを促すか）（REQ-014 / `steering/database.md` のクエリパターン。`steering/api-standards.md` の一覧取得節は共通のページネーション形式を持たない）
  - ④ **CSV に出力する項目と、一覧の表示項目との対応**（同一とするか、CSV のみ項目を増減するか）、および **CSV のファイル名の規約**（固定名か、出力日時や検索条件を含めるか）（REQ-014）。`steering/api-standards.md` はファイル名の共通規約を持たない
  - ⑤ **「既存 WTB（計画・工程管理）と同様の権限制御方式」の実体**（ベンダー／施工会社に対してどのデータ範囲をどう制御するか）（REQ-046 / `steering/security.md` の認可）。要求一覧は方式を既存 WTB に合わせるとだけ述べ、steering も同じ表現に留まっているため、既存 WTB の実装を調査して確定する（REQ-073）
  - ⑥ **申請状況を表示するためのデータの取り方**（`property-basic-info` と `issue-request` のテーブルを直接参照するか、`jp.co.kccs.wt.common` に共通サービスを置くか、申請状況の集約用テーブルを新設するか）。`steering/architecture.md` の `## レイヤーと依存ルール` は機能パッケージ間の直接依存（`function.wtg.wtgXXX` → `function.wtg.wtgYYY`）を禁止し、共有が必要な処理は `common` に置くと定めているため、この禁止に抵触しない経路を選ぶ
  - ⑦ **「検索を実行した後」であることの判定方法**（検索条件を Form で再送するか、画面間で引き渡すか）（REQ-014）。画面間で引き渡す構成を採る場合は、セッションキーの有効時間（`wing-web.properties` の `PARAM_SESSION_KEY_PERIOD` = 10 秒）の制約を受ける（`steering/security.md` のセッション / トークンの保管・転送）

---

_「何を作るか」を契約する正のドキュメントです。実装方法 / コンポーネント設計は `design.md`、タスクの分解は `tasks.md` に書いてください。_
