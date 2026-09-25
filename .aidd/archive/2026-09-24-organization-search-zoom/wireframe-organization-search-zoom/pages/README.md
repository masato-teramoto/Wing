# 作成組織検索（ZOOM）ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `organization-search-zoom` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/organization-search-zoom/requirements.md`（`status: approved`）、`steering/` 一式 |

## ページ一覧

| ファイル | 画面 | 状態 |
|---|---|---|
| `zoom-search-default.html` | 作成組織検索 | `default`（条件未適用の初期表示・1 ページ目） |
| `zoom-search-filters-applied.html` | 作成組織検索 | `filters-applied`（詳細条件が適用されている） |
| `zoom-search-page-changed.html` | 作成組織検索 | `page-changed`（ページ移動後・最終ページ） |
| `zoom-search-empty.html` | 作成組織検索 | `empty`（条件未適用で該当 0 件） |
| `zoom-search-filter-empty.html` | 作成組織検索 | `filter-empty`（詳細条件で 0 件） |
| `zoom-search-loading.html` | 作成組織検索 | `loading`（読み込み中） |
| `zoom-search-error.html` | 作成組織検索 | `error`（読み込み失敗・インライン再試行） |
| `error-403.html` | エラー画面（権限なし） | `default` |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| `notice` | NotificationBanner の情報アイコン（種別が情報）の SVG 実体が DS v0.0.11 に無いため。`wireframe-manifest.json` の `missing[]` に記録 |
| `rows-selected` / `bulk-action-done` | 本 feature は一覧からの単一選択のみで一括操作を持たない（Requirement 3） |

表示は `../wireframe-viewer.html` から確認してください。
