# 契約情報ダウンロード ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

検索条件・表示項目は未確定です。「検索条件 1〜8」「キー / 項目 1〜4」は件数と配置のイメージを示すもので、既存の [GWTG004] 契約情報検索／一覧と同一にする範囲・条件の項目そのもの・桁・書式・必須は基本設計で確定します。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `contract-info-download` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/contract-info-download/requirements.md`（`status: approved`）、`steering/` 一式 |

## ページ一覧

| ファイル | 画面 | 状態 |
|---|---|---|
| `download-list-initial.html` | 契約情報ダウンロード | `default`（条件未適用・検索前） |
| `download-list-result.html` | 契約情報ダウンロード | `filters-applied`（検索結果あり） |
| `download-list-empty.html` | 契約情報ダウンロード | `empty` |
| `download-list-filter-empty.html` | 契約情報ダウンロード | `filter-empty` |
| `download-list-input-error.html` | 契約情報ダウンロード | `input-error` |
| `download-list-loading.html` | 契約情報ダウンロード | `loading` |
| `download-list-error.html` | 契約情報ダウンロード | `error` |
| `error-403.html` | エラー画面（権限なし） | `default` |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| `notice` | NotificationBanner の情報アイコンの SVG 実体が DS v0.0.11 に無いため。対応する受入基準が requirements に無いため `missing[]` のみに記録 |
| `rows-selected` / `bulk-action-done` | 本画面は参照専用で行選択・一括操作を持たないため |
| `page-changed` | 固定値ダミーが 3 件で総ページ数 1 のため Pagination を非出力にしている（`never_do`） |

表示は `../wireframe-viewer.html` から確認してください。
