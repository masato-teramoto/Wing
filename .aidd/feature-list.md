---
status: review
updated_at: 2026-09-11T13:22:04+09:00
---

# フィーチャー一覧

> このファイルは **実装順序の根拠（優先度・依存）の正**です。Phase 4 / 5 は優先度順に feature を選び、Phase 6 は依存先を推論せず本ファイルの `依存` 列から引きます。
> **スコープ・完了条件はここに書きません。** それらは `specs/<feature>/requirements.md`（`Boundary Context` / `Acceptance Criteria`）が正です。本ファイルは「どの順で、何を根拠に作るか」だけを持ちます。
> `status: approved` になってから Phase 4 以降の入力にしてください。
>
> **テンプレート**: 山括弧で囲んだ大文字の項目は、プロジェクト確定時に実値へ置換する。

## フィーチャー一覧

> 優先度の昇順に並べる（表の並び自体を実装順とする）。1 行 = 1 feature。`_N` の行を feature の数だけ増やす。各項目の取りうる値は下の `### 項目の定義` を正とする。

| feature 名 | 種別 | 目的 | 依存 | 優先度 | 想定規模 | 対応要求ID |
|---|---|---|---|---|---|---|
| access-control | Platform | 新規機能に対するベンダー／施工会社の権限制御を、既存 WTB（計画・工程管理）と同様の方式で提供する | なし | 1 | 小 | REQ-046 |
| organization-search-zoom | Platform | 作成組織を 3 項目のプルダウンで検索する ZOOM 画面を提供し、呼び出し元画面から利用できるようにする | なし | 2 | 小 | REQ-048, REQ-049, REQ-050 |
| contract-application-status | User | 物件契約情報の申請状況を検索・一覧表示し、CSV として出力する | access-control | 3 | 中 | REQ-012, REQ-013, REQ-014 |
| property-basic-info | User | 物件基本情報を登録・変更し、承認フローとステータス・履歴・契約稟議ファイルを管理したうえで、稟議資料となる帳票を出力する | access-control, organization-search-zoom | 4 | 大 | REQ-015, REQ-016, REQ-017, REQ-018, REQ-019, REQ-020, REQ-021, REQ-022, REQ-023, REQ-024, REQ-025 |
| issue-request | User | 発行依頼書を登録・変更して契約書に対する発番を行い、チュートリアルによる入力補助とバーコード生成を提供する | access-control, organization-search-zoom | 5 | 大 | REQ-026, REQ-027, REQ-028, REQ-029, REQ-030, REQ-031, REQ-032, REQ-033, REQ-034, REQ-035, REQ-036, REQ-037, REQ-038, REQ-039 |
| contract-info-import | User | 契約情報の取込バッチを画面から実行し、新規・変更・削除の取込と洗替更新を行う | access-control | 6 | 中 | REQ-040, REQ-041, REQ-042, REQ-043 |
| contract-info-download | User | 既存の契約情報検索と同一の条件・表示項目で契約情報を検索し、取込で使える形式の CSV としてダウンロードする | access-control, contract-info-import | 7 | 中 | REQ-044, REQ-045, REQ-047 |

### 項目の定義

| 項目 | 内容 |
|---|---|
| feature 名 | `specs/<feature-name>/` に対応する識別子 |
| 種別 | `User` / `Platform` |
| 目的 | この feature が満たす要求 |
| 依存 | 前提となる feature（**方向つき**。先に出来ていなければならない側を書く） |
| 優先度 | 実装順の根拠となる値 |
| 想定規模 | `大` / `中` / `小`（分割判断に使う） |
| **対応要求ID** | 要求一覧の要求ID（複数可）。**トレーサビリティの突合キー** |

## 種別の判定

| 種別 | 定義 | 例 |
|---|---|---|
| **User Feature** | それ単体で、利用者が目的を最後まで済ませられる機能の塊 | 注文作成、請求確認 |
| **Platform Feature** | それ単体では誰の目的も終わらず、他の feature に使われて働く共通の仕組み | 認証基盤、通知基盤、監査ログ基盤 |

判定は次の一問で行う。

> **この feature だけが出来上がった状態で、誰かが用事を済ませて終われるか。**
> 終われる → User Feature / 終われない（他の feature の中で使われる）→ Platform Feature

- 利用者には **運用者・管理者も含む**。社内向けの管理機能も User になりうる。
- **画面の有無では決めない**。主目的で決める（ログインは操作を伴うが、用事はその先にあるため Platform）。
- 同じ題材でも切り口で変わる。監査ログを記録する仕組みは Platform、監査担当が検索して確認を終えられる機能は User。
- **「前提かどうか」は種別ではなく `依存` 列が持つ**。先に作る必要があることを理由に Platform としない。

### 本プロジェクトでの判定結果

| feature 名 | 判定 | 根拠 |
|---|---|---|
| access-control | Platform | 権限制御だけが出来上がっても誰の用事も終わらない。各機能の中で働く共通の仕組みである（REQ-046 は「新規機能の権限制御」と全機能を対象にしている） |
| organization-search-zoom | Platform | 作成組織検索は呼び出し元画面（物件基本情報登録変更画面・発行依頼書登録変更画面）の入力を助けるために使われる。それ単体では用事が終わらない（REQ-050） |
| contract-application-status | User | 担当者が申請状況を検索・一覧・CSV 出力して確認を終えられる（REQ-012〜REQ-014） |
| property-basic-info | User | 担当者が物件基本情報を登録・変更し、承認に回して帳票を出すところまで終えられる（REQ-015〜REQ-025） |
| issue-request | User | 担当者が発行依頼書を登録・変更し、発番まで終えられる（REQ-026〜REQ-039） |
| contract-info-import | User | 担当者が取込バッチを実行して契約情報の反映を終えられる（REQ-040〜REQ-043） |
| contract-info-download | User | 担当者が契約情報を検索して CSV を取得し終えられる（REQ-044・REQ-045・REQ-047） |

## 優先度の決定方針

1. **依存に基づく必須先行を機械的に決定**する（AI が算出）
2. 必須先行で順序が決まらない範囲は、**`steering/product.md` の主要ユースケース・提供価値と要求一覧を根拠に AI が並べる**。根拠が無い場合は推測で並べず、**質問して停止**する
3. Phase 4 以降の微修正は可。ただし **依存の逆転は禁止**

- **優先度は AI が決定する**。人間による並べ替えは必須工程としない。
- **feature の確定（分割の採否）と `status: approved` は人間**が行う。優先度に異議がある場合はレビューで指摘し、修正して再承認する。

### 本プロジェクトでの算出根拠

| 優先度 | feature 名 | 根拠 |
|---|---|---|
| 1 | access-control | 依存を持たず、REQ-046 により新規機能すべてが前提とする |
| 2 | organization-search-zoom | 依存を持たない。REQ-050 により property-basic-info・issue-request の呼び出し先となるため、両者より先行させる |
| 3 | contract-application-status | 必須先行の制約なし。`steering/product.md` の主要ユースケース 1（申請状況の確認）に対応するため、ユースケースの並び順に従って先頭に置く |
| 4 | property-basic-info | organization-search-zoom の後（REQ-050）。主要ユースケース 2（契約稟議の起票）およびユースケース 4（稟議資料の帳票出力）に対応する |
| 5 | issue-request | organization-search-zoom の後（REQ-050）。主要ユースケース 3（契約書の発行依頼）に対応し、ユースケースの並びで property-basic-info の次に置く |
| 6 | contract-info-import | 主要ユースケース 5（契約情報の取込・ダウンロード）に対応する。REQ-047 により contract-info-download が「取込で使える形式」を出力するため、取込の形式が確定する本 feature を先に置く |
| 7 | contract-info-download | contract-info-import の後（REQ-047: 契約情報取込で使える形式の CSV を出力する） |

依存に循環はない（access-control と organization-search-zoom はいずれも依存を持たず、他の 5 feature は両者または contract-info-import のみを参照する）。

## 分割案（採否は人間が決める）

> 想定規模が「大」の feature について分割案を提示する。**本 Skill は提案までで、採否は人間が決める。** 採用する場合は上記の表を分割後の feature で書き直し、優先度と依存を付け直す。

### property-basic-info（規模: 大 / 対応要求ID 11 件）

| 分割案 | feature 名 | 対応要求ID | 分割の根拠 |
|---|---|---|---|
| A-1 | property-basic-info（登録・変更） | REQ-015〜REQ-022 | 登録・変更画面と承認フロー・履歴・ファイル登録 |
| A-2 | property-basic-info-report（帳票） | REQ-023, REQ-024, REQ-025 | RFP §4-2 の想定される構成が「登録・変更画面」と「印刷・閲覧用帳票」を別に挙げており、出力先（画面 / 帳票・PDF）が異なる |

### issue-request（規模: 大 / 対応要求ID 14 件）

| 分割案 | feature 名 | 対応要求ID | 分割の根拠 |
|---|---|---|---|
| B-1 | issue-request（登録・変更） | REQ-026〜REQ-034 | 登録・変更画面、発番、単独局／複数局、金額計算、履歴 |
| B-2 | issue-request-tutorial（チュートリアル設定） | REQ-035, REQ-036 | RFP §4-3 の想定される構成が「チュートリアル設定画面」を別画面として挙げており、現行の設定用ウインドウ 26 フォーム相当を新規に実現するため規模が独立して大きい |
| B-3 | issue-request-barcode（バーコード生成） | REQ-037, REQ-038, REQ-039 | RFP §4-3 の想定される構成が「バーコード生成（ポップアップ）画面」を別画面として挙げている |

## 依存関係図（任意）

> 依存が複雑で表だけでは追えない場合のみ記述する。循環が無いことの確認にも使う。
> **記法**: Mermaid `flowchart`。feature をノード、`依存` 列の関係を矢印で表す。

<FEATURE_DEPENDENCY_DIAGRAM>

<!-- 不要理由: feature が 7 件、依存関係は access-control（全 User feature の前提）・organization-search-zoom（property-basic-info / issue-request の前提）・contract-info-import（contract-info-download の前提）の 3 系統のみであり、上記の表で追える。循環も表から確認できるため図を作成しない。分割案が採用されて依存が増えた場合は本スロットに図を記述する。 -->

---

_実装順序の根拠を持つ正のドキュメントです。スコープ・受け入れ基準は `specs/<feature>/requirements.md`、設計は `design.md` に書いてください。要求ID の正は要求一覧です。_
