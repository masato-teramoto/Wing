---
status: approved
updated_at: 2026-09-28T13:54:57+09:00
---

# API 設計標準

> **目的**: 命名・URL 構造・リクエスト/レスポンス形式・ステータスコード・認証ヘッダ・バージョニング・エラー表現を統一する。
> API を扱うフィーチャーでは、`design.md` の API Contract セクションは本ファイルとの差分のみを書けばよい状態を目指す。
> エラーボディの詳細フィールド定義・分類は本ファイルの `## エラーハンドリング（API 契約）`、認証ヘッダ・認可（権限チェック）の詳細は `security.md`、
> ページネーションの DB 層方針は `database.md` を正とする。
> 個別フィーチャー固有のエンドポイント定義は `specs/<feature-name>/design.md` の API Contract に書き、
> ここには **全 API 共通の「形」** だけを書く。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

> **本ファイルが対象とする「API」**: 本システムはブラウザと Spring MVC の間の **画面遷移型（サーバサイドレンダリング）** の HTTP インタフェースであり、外部公開の REST API を持たない（UQ 様社内システムは改修対象外 — REQ-008）。したがって本ファイルは、**Controller のエンドポイント（URL とメソッド）・画面内の非同期通信・エラー表現の共通形**を固定する。記入根拠は既存実装（`servlet-context.xml` の interceptor マッピング、既存 Controller、`ExceptionResolver`）である（REQ-053）。

## 設計思想

> このプロジェクトの API 設計で何を優先するかの原則を列挙する。後続セクションの判断軸となる。

- 既存 WiNG の URL・アクション名の付け方に合わせる。既存の共通処理（interceptor のパスマッピング）が効く形を崩さない（REQ-009 / REQ-053）
- 更新系は POST で受ける。GET で状態を変えない
- 認証・認可・CSRF は Controller の手前（interceptor）で効かせ、Controller に判定を書かない
- 画面に返すエラーは利用者向けの文言に限り、内部情報を含めない
- 既存のエンドポイントの URL・パラメータ・戻り値を変更しない（REQ-052）

## エンドポイントのパターン

> URL の共通形式を固定する。エンドポイントカタログ（実体）はここに書かず、各 `design.md` の API Contract に書く。

```
/<画面ID小文字>[/<アクション>]
```

例:

- `GET /wtg004` — 画面の初期表示（`@RequestMapping(value = "", method = RequestMethod.GET)`）
- `POST /wtg004/execute` — 実行（バッチタスクの登録等）
- `POST /wtg004/clear` — クリア
- `POST /wtg004/return` — 戻る
- `POST /wtl010/fileUpload` — ファイルアップロード
- `GET /zoom/wait` — ZOOM 待機画面の表示（`ZoomWaitController`。**`@FuncID` を持たない**）
- `POST /zoom/zwtz002` — ZOOM 画面の初期表示・検索
- `POST /zoom/zwtz002/page` — ZOOM 画面のページング

| ルール | 内容 |
|---|---|
| 名詞・複数形 | 採用しない。第 1 セグメントは **画面ID（小文字）** とする（`@RequestMapping("/<画面ID小文字>")`）。画面IDの採番は既存体系に従う（REQ-051） |
| 階層 | `/<画面ID小文字>/<アクション>` の 2 階層を基本とする。**同じ画面IDに属する別の PGID は、サブパスの下にアクションを置く `/<画面ID小文字>/<サブパス>/<アクション>` の 3 階層とする**（既存 `Pwtgo006Controller` の `/wtg003/ref/executeDownLoad`、`Pwtgo026Controller` の `/wtg002/file/downLoad`。サブパスは `tech.md` の `## 命名規則` の Controller 行。人間が確定 / 2026-09-25）。同じ PGID の中で既定のアクション名（`downLoad` 等）を用途別に 2 つ以上持つ場合も、同じ形でサブパスの下に置く（例: `/wtg070/file/downLoad`。人間が確定 / 2026-09-25）。それ以上深くしない。ZOOM 画面は `/zoom/**` の配下に置く |
| ID | リソースIDを URL のパスに含めない。対象の特定は Form のパラメータで行う（既存の画面遷移方式に合わせる） |
| アクション系 | 動詞を第 2 セグメントに置く。共通処理が効く既定の名前を優先して使う: `regist` / `update` / `delete` / `approved` / `reset` / `execute` / `upload`（CSRF 検証の対象。**本行を対象アクション名の正本とする** — `security.md` の `## 攻撃対策（主要パターン）` CSRF 行から参照される）、`download` / `downLoad` / `executeDownLoad`（CSRF トークン生成の除外対象）。**新しいアクション名を作る場合は、`servlet-context.xml` の interceptor マッピングとの整合を必ず確認する**（更新系が CSRF 検証から漏れないようにする） |

## HTTP メソッド

> 採用するメソッドごとに用途・冪等性・安全性を固定する。リトライ設計・キャッシュ設計の根拠になる。

| メソッド | 用途 | 冪等性 | 安全性 |
|---|---|---|---|
| GET | 画面の初期表示（**ZOOM 画面を除く**）、ZOOM 待機画面の表示 | 冪等 | 安全（状態を変えない） |
| POST | 検索・登録・更新・削除・承認・実行・アップロード・ダウンロード（すべての更新系と、Form の値を送る参照系）、**ZOOM 画面の初期表示・ページング** | 非冪等（登録・更新は二重送信を防ぐ） | 安全でない |

- 画面（ZOOM 画面を除く）の初期表示は、メニューから新規に開く場合を GET、遷移元から業務キー（申請No 等）を受け取って開く場合を POST とし、同じ空パスに 2 本のメソッドを置く（既存 `Pwtgo008Controller`（`/wtg004`、GET）/ `Pwtgo006Controller`（`/wtg003/ref`、POST）。人間が確定 / 2026-09-24）
- PUT / DELETE / PATCH は使用しない（既存の画面遷移方式に合わせる）
- 二重送信の防止は CSRF トークン（`CSRFTokenCheckInterceptor`）と画面側のボタン制御で行う

**ZOOM 画面（`/zoom/**`）の初期表示・ページングは POST とする。** 一般の画面の初期表示が GET であるのと異なる。

理由は ZOOM の開き方にある。呼び出し元は共通フラグメント `pages/common/zoomForm.html` を使い、**① `window.open` で `/zoom/wait` を開き、② hidden フォーム（`#zoomForm`）を `target` にそのウインドウを指定して `/zoom/<ZOOM ID 小文字>` へ submit する**。呼び出し元から渡すパラメータをフォームの値として送るため、受け口は POST になる。GET で受ける ZOOM 画面を作ると、この共通フラグメントに分岐を足すことになり既存 ZOOM に影響する（REQ-052）。

**待機画面だけは例外で GET である。**

| 対象 | メソッド | 実装 | `@FuncID` |
|---|---|---|---|
| ZOOM 待機画面 `/zoom/wait` | **GET** | `jp.co.kccs.wt.common.controller.ZoomWaitController` | **持たない**（権限判定の対象にしない） |
| ZOOM 画面の初期表示 `/zoom/<ZOOM ID 小文字>` | **POST** | `@RequestMapping(value = "", method = RequestMethod.POST)` | ZOOM ID（`@FuncID("ZWTZ<3 桁>")`） |
| ZOOM 画面のページング `/zoom/<ZOOM ID 小文字>/page` | **POST** | `@RequestMapping(value = "page", method = RequestMethod.POST)` | 同上（Controller 単位で付与） |

> 記入根拠は既存実装である（REQ-053）。`wing` の ZOOM 画面 17 本はいずれも初期表示・ページングとも `RequestMethod.POST` で実装されており、`ZoomWaitController` のみ `RequestMethod.GET` で `@FuncID` を持たない。**ZOOM は ZOOM ID 自体が機能IDであり、`PWTGOxxx` を別に採番しない**（命名規則は `tech.md` の `## 命名規則` を正とする）。

## リクエスト / レスポンス形式

> JSON の外側のラッパー構造を統一する。成功とエラーでトップキーを分け、成功レスポンスに `error` を含めない。

- リクエスト形式: `application/x-www-form-urlencoded`（Form クラスへバインド）。ファイルを伴う場合は `multipart/form-data`（`CommonsMultipartResolver`。上限値は `tech.md` の `## 主要ライブラリ`「ファイルアップロード」を正とする）
- レスポンス形式（成功）: Thymeleaf による HTML（`ModelAndView`。ビュー名は `<サブシステム小文字>/<画面ID小文字>/<PGID小文字>`、モデル属性名は `<PGID小文字>Form`）。画面内の非同期通信のみ JSON（Jackson / Gson）。ファイル出力は `Content-Disposition` 付きのバイナリ（CSV / PDF）
- レスポンス形式（エラー）: `error` ビュー（モデル属性は本ファイルの `### 共通エラー形式` を正とする）。入力チェックのエラーは元の画面を再表示し、`BindingResult` の内容を画面に表示する

エラーボディのフィールド定義・分類は本ファイルの `## エラーハンドリング（API 契約）` に従う（上記の `error` はそのサブセット）。

### パラメータ配置

| ルール | 内容 |
|---|---|
| Content-Type | リクエストは `application/x-www-form-urlencoded`（ファイルを伴う場合は `multipart/form-data`）。文字エンコーディングは `security.md` の `## ヘッダ / トランスポート` を正とする |
| パラメータ配置 | 画面の入力値は Form クラスのフィールドにバインドする。Controller のメソッド引数で個別に受け取る形を新規に増やさない。配列・明細行のバインド上限は `security.md` の `### 入り口 — 入力検証` を正とする（`ControllerBase.configureWebDataBinder`） |
| 大量データ | 一覧の CSV 出力・帳票出力は、生成したファイルを既存のファイルダウンロードの仕組みに載せる（`DownLoadFileInfo` でファイルパスとファイル名を受け取り、`FileInfo` を `executeDownLoad` へ forward して `Content-Disposition` 付きで返す。既存実装 `Pwtgo006Controller#doDownLoad` — REQ-053）。取込のような時間のかかる処理は同期で返さず、バッチタスクとして登録し実行状況を別画面で確認させる（REQ-041） |

## ステータスコード方針

> 「**結果を最も適切に表すコードを選ぶ**」を原則とする。ただし画面遷移型の既存実装に合わせ、アプリケーションが検出したエラーは下表のとおり `error` ビューを 200 で返す（人間が確定 / 2026-09-24）。

| 区分 | コード | 用途 |
|---|---|---|
| 成功（画面表示） | 200 | 画面の表示、入力チェックエラーを含む画面の再表示（画面遷移型のため、入力チェックエラーも画面として 200 で返す） |
| 成功（ファイル出力） | 200 | CSV / PDF のダウンロード（`Content-Disposition` を付与） |
| リダイレクト | 302 | ログイン画面への遷移、`RedirectController` による遷移 |
| エラー（アプリケーション） | 200（`error` ビュー） | 業務エラー・権限エラー・CSRF エラー。`ExceptionResolver` が `error` ビューへ遷移させる（渡すモデル属性は本ファイルの `### 共通エラー形式` を正とする） |
| エラー（サーバ） | 500 | コンテナまで到達した想定外の例外 |
| <STATUS_CATEGORY_N> | <STATUS_CODE_N> | <STATUS_USAGE_N>（不要 / 人間 2026-09-11: 既存 WiNG の実装に従う） |

> **注記**: 既存実装ではアプリケーションが検出したエラーを `error` ビュー（200）で返しており、HTTP のステータスコードでは区別していない。画面内の非同期通信（JSON）でエラーを返す場合の扱いは既存実装から確定できていない。

## 認証情報

> 認証情報の渡し方と実行順を固定する。認証 → 認可 → ビジネスロジックの順を守る。

- 認証情報の標準位置: `JSESSIONID` クッキー（サーバサイドセッション）。Authorization ヘッダは使用しない（詳細は `security.md` の `## 認証・認可`）
- 未認証時の扱い: `SessionCheckInterceptor` がリクエストを止め、ログイン画面へ遷移させる（除外パス: `/`・`/login`・`/logout`・`/static/**`・`/error`・`/error/**`）
- 認可（権限チェック）の方針: `security.md` の `## 認証・認可` > `### 認可` を正とする（本ファイルに再掲しない）。画面側の表示制御はこれと二重に効かせる

## 一覧取得（ページネーション / フィルタ / ソート）

> DB 層の方針（カーソル優先等）は `database.md`。ここでは **HTTP クエリと `meta` の契約** のみを固定する。

> **不要（記入者: 人間 / 2026-09-11）**: 既存 WiNG の画面遷移方式に従う。検索条件・並び順・ページングはクエリ文字列ではなく Form の値として POST で送るため、HTTP クエリと `meta` の共通形式を本プロジェクトで定義しない。以下のプレースホルダーはこの理由で未記入のまま残す。

| 機能 | クエリ（既定） | `meta` に含める |
|---|---|---|
| オフセットページ | <PAGINATION_OFFSET_QUERY> | <PAGINATION_OFFSET_META> |
| カーソルページ | <PAGINATION_CURSOR_QUERY> | <PAGINATION_CURSOR_META> |
| ソート | <SORT_QUERY_FORMAT> | — |
| フィルタ | <FILTER_QUERY_FORMAT> | — |
| 全文検索 | <FULLTEXT_QUERY_FORMAT> | — |

- プロジェクトの既定ページネーション方式: <PAGINATION_DEFAULT_CHOICE>（両方許容する場合は `design.md` に明記）
- フィーチャー固有の検索条件は `design.md` の API Contract に差分のみ

> **注記**: 一覧の検索条件は Form のフィールドとして POST で送る（クエリ文字列の共通形式を持たない）。物件契約情報申請状況の検索項目は 20 項目程度を想定する（REQ-013）。契約情報検索画面は既存の [GWTG004] 契約情報検索／一覧と同一の検索条件・表示項目とする（REQ-045）。

## バージョン管理

> API の変更がクライアントに与える影響をコントロールするルールを固定する。

- バージョニング方式: 採用しない。外部公開 API を持たず、画面とサーバが同一の WAR として同時にリリースされるため（REQ-008 / REQ-053）
- 破壊的変更: 既存のエンドポイント（URL・パラメータ・戻り値）を変更しない。変更が必要な場合は新規エンドポイントを追加する（REQ-052）
- 非破壊的変更: 既存の画面・機能に影響しない範囲であれば、同一エンドポイントへの項目追加を許容する
- 旧バージョンの非推奨化: <API_VERSIONING_DEPRECATION_POLICY> — **不要（記入者: 人間 / 2026-09-11）**: 外部公開 API を持たずバージョニングを行わないため（REQ-008 / REQ-053）

## エラーハンドリング（API 契約）

> **目的**: エラーの分類・共通レスポンス形式・フィールド規約を統一する。
> 個別フィーチャー固有のエラーコード一覧は `specs/<feature-name>/design.md` の Error Handling に書き、ここには **全 API 共通のエラー契約** だけを書く。
> 例外処理フロー・例外クラス命名・グローバルハンドラ（実装部）は `tech.md` の `## 例外処理`、
> ログ・アラート・リトライ・監視（観測部）は `non-functional.md` の `## 信頼性・観測性` を参照する。
> アラート発火時の **対応手順・当番・エスカレーション** は `non-functional.md` の `## 運用・障害対応` を参照する。

### 基本方針（API エラー部分）

> プロジェクトのエラーハンドリング原則を列挙する。採用しない行は削除する。

- 利用者に返すエラーはメッセージID（`messages.properties`）で管理された文言とし、ソースに直書きしない
- 入力チェックのエラーは画面を再表示して該当項目の近くに表示する。`error` ビューへ飛ばさない
- 業務エラー・権限エラー・CSRF エラーは例外として投げ、`ExceptionResolver` に一元処理させる
- 利用者に返す内容にスタックトレース・SQL・内部パス・内部IDを含めない。詳細はログに出す

### 分類

> ハンドリング方針は **エラー区分（Client / Business / Server / External 等）** で決める。
> _分担_: フィーチャー固有のエラーコードと HTTP マッピングの詳細は `specs/<feature-name>/design.md` の Error Handling に書く。

| 区分 | 例 | レスポンス |
| --- | --- | --- |
| 入力エラー（Client） | 必須未入力、書式不正、桁超過 | 元の画面を再表示し、`BindingResult` のメッセージを表示する（200） |
| 業務エラー（Business） | 排他エラー、採番失敗、状態が変更されている、取込対象が存在しない | `ApplicationException` 系を投げ、`error` ビューにメッセージIDの文言を表示する |
| 権限エラー（Authorization） | 権限の無い機能へのアクセス | `InvalidAccessErrorException` → `error` ビュー。ユーザーID・メニューID・機能IDをログに残す |
| セキュリティエラー（Security） | CSRF トークン不一致、セッション切れ | `CSRFTokenErrorException` → `error` ビュー／セッション切れはログイン画面へ遷移 |
| サーバエラー（Server） | 想定外の例外 | 既定のエラーコード（本ファイルの `### 共通エラー形式` を正とする）の文言を表示し、スタックトレースをログに出力する |
| 外部エラー（External） | 取込ファイルの不正、外部から受領したデータの不整合 | 業務エラーとして扱い、対象と理由が分かるメッセージを返す（REQ-042 / REQ-043） |

### 共通エラー形式

> _分担_: エラーコードの一覧は `specs/<feature-name>/design.md` の Error Handling に書く。ここは **レスポンス形式とフィールド規約** のみを定義する。

- レスポンス形式: `error` ビュー（HTML）に次のモデル属性を渡す（`ExceptionResolver`）。画面内の非同期通信（JSON）でも同じフィールド名を用いる。

| 項目 | 必須 | ルール |
| --- | --- | --- |
| `errorKind` | 必須 | エラーの種別を表す文字列（既定値 `warning`）。**本節をモデル属性・既定値の正本とする**（`tech.md` の `### グローバルハンドラ` および本ファイルの他節から参照される） |
| `errorCode` | 必須 | メッセージID（`<3 文字の区分>-<6 桁の連番>`）。不明な例外の既定値は `GEF-000000` |
| `errorMessage` | 必須 | `messages.properties` から取得した利用者向けの文言。内部情報を含めない |

### 複数フィールドのバリデーション

| # | ルール |
| --- | --- |
| 1 | 入力チェックは最初のエラーで打ち切らず、`BindingResult` に全件を積んでから画面に返す |
| 2 | 明細行のエラーは、どの行のどの項目かが分かる形で示す |
| 3 | 相関チェック（項目間の整合、複数局モード時の必須など — REQ-032）は Service で行い、結果を `BindingResult` に積む |

---

_API の「形」を統一するためのファイルです。エンドポイントカタログ（実体）はここに書かず、各 `design.md` の API Contract に書いてください。_
