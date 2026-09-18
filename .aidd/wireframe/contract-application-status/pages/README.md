# 物件契約情報申請状況 ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

検索条件・表示項目・申請状況の値はいずれも未確定です。「検索条件 1〜20」「項目 1〜3」は件数と配置のイメージを示すもので、条件の項目そのもの・桁・書式・必須は基本設計で確定します。申請状況の値は本フィーチャーでは決めません。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `contract-application-status` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/contract-application-status/requirements.md`（`status: approved`）、`steering/` 一式 |

## ページ一覧

| ファイル | 画面 | 状態 |
|---|---|---|
| `status-list-initial.html` | 物件契約情報申請状況 検索／一覧 | `default`（条件未適用・検索前） |
| `status-list-result.html` | 物件契約情報申請状況 検索／一覧 | `filters-applied`（検索結果あり） |
| `status-list-limit-exceeded.html` | 物件契約情報申請状況 検索／一覧 | `filters-applied`（表示件数の上限を超過） |
| `status-list-empty.html` | 物件契約情報申請状況 検索／一覧 | `empty` |
| `status-list-filter-empty.html` | 物件契約情報申請状況 検索／一覧 | `filter-empty` |
| `status-list-input-error.html` | 物件契約情報申請状況 検索／一覧 | `input-error` |
| `status-list-loading.html` | 物件契約情報申請状況 検索／一覧 | `loading` |
| `status-list-error.html` | 物件契約情報申請状況 検索／一覧 | `error` |
| `error-403.html` | エラー画面（権限なし） | `default` |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| `notice` | NotificationBanner の情報アイコンの SVG 実体が DS v0.0.11 に無いため。上限超過は件数表示の近くのテキストで代替。`unrealized[]` に記録（Requirement 1 の受入基準 11） |
| `rows-selected` / `bulk-action-done` | 本画面は参照専用で行選択・一括操作を持たないため |
| `page-changed` | 固定値ダミーが 3 件で総ページ数 1 のため Pagination を非出力にしている（`never_do`） |

表示は `../wireframe-viewer.html` から確認してください。
