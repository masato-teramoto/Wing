# 物件契約情報申請状況 ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `contract-application-status` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/contract-application-status/requirements.md`（`status: approved`）、`steering/` 一式 |

## 状態とファイルの対応

| ファイル | 画面 | 状態 |
|---|---|---|
| `status-list-initial.html` | 物件契約情報申請状況 検索／一覧 | default（条件未適用・検索前） |
| `status-list-result.html` | 物件契約情報申請状況 検索／一覧 | filters-applied（検索結果あり） |
| `status-list-limit-exceeded.html` | 物件契約情報申請状況 検索／一覧 | filters-applied（表示件数の上限を超過） |
| `status-list-empty.html` | 物件契約情報申請状況 検索／一覧 | empty（条件未適用で 0 件） |
| `status-list-filter-empty.html` | 物件契約情報申請状況 検索／一覧 | filter-empty（条件適用で 0 件） |
| `status-list-input-error.html` | 物件契約情報申請状況 検索／一覧 | input-error（検索条件の入力エラー） |
| `status-list-loading.html` | 物件契約情報申請状況 検索／一覧 | loading |
| `status-list-error.html` | 物件契約情報申請状況 検索／一覧 | error（インライン再試行） |
| `error-403.html` | エラー画面（権限なし） | default |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| list-page `notice` | デザインシステム v0.0.11 の icons/ に SVG の実体が無く、情報アイコンを要する NotificationBanner が使えないため、当該の状態のページを生成していない。 |
| list-page `rows-selected` / `bulk-action-done` | 参照のみの一覧であり行選択と一括操作を持たないため |
| list-page `page-changed` | 上限超過時にページ送りを設けるかどうかが未確定事項 ③ のため、ページングを画面で確定させない |

## 画面に載せていない要件

検索条件の項目そのもの（20 項目程度）・一覧の表示項目・1 行が表す単位は要件で確定しておらず（未確定事項 ②）、匿名のプレースホルダーで項目数と配置のみを示しています。表示件数の上限と既定の並び順も未確定です（未確定事項 ③）。

画面にできなかった要件は `wireframe-manifest.json` の `unrealized[]` を参照してください。

表示は `../wireframe-viewer.html` から確認してください。
