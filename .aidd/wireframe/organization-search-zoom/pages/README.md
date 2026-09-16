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
| `zoom-search-default.html` | 作成組織検索 | 検索結果あり（先頭ページ・条件適用中） |
| `zoom-search-page2.html` | 作成組織検索 | 検索結果あり（末尾ページ） |
| `zoom-search-empty.html` | 作成組織検索 | 該当なし |
| `zoom-search-loading.html` | 作成組織検索 | 読み込み中 |
| `zoom-search-error.html` | 作成組織検索 | 読み込み失敗（インライン再試行） |
| `error-403.html` | エラー画面 | 権限なし |

表示は `../wireframe-viewer.html` から確認してください。
