# 契約情報ダウンロード ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `contract-info-download` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/contract-info-download/requirements.md`（`status: approved`）、`steering/` 一式 |

## 状態とファイルの対応

| ファイル | 画面 | 状態 |
|---|---|---|
| `download-list-initial.html` | 契約情報ダウンロード | default（条件未適用・検索前） |
| `download-list-result.html` | 契約情報ダウンロード | filters-applied（検索結果あり） |
| `download-list-empty.html` | 契約情報ダウンロード | empty（条件未適用で 0 件） |
| `download-list-filter-empty.html` | 契約情報ダウンロード | filter-empty（条件適用で 0 件） |
| `download-list-input-error.html` | 契約情報ダウンロード | input-error（検索条件の入力エラー） |
| `download-list-loading.html` | 契約情報ダウンロード | loading |
| `download-list-error.html` | 契約情報ダウンロード | error（インライン再試行） |
| `error-403.html` | エラー画面（権限なし） | default |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| list-page `notice` | デザインシステム v0.0.11 の icons/ に SVG の実体が無く、情報アイコンを要する NotificationBanner が使えないため、当該の状態のページを生成していない。 |
| list-page `rows-selected` / `bulk-action-done` | 参照のみの一覧であり行選択と一括操作を持たないため |
| list-page `page-changed` | 表示件数の上限と並び順が未確定事項 ② のため、ページングを画面で確定させない |

## 画面に載せていない要件

検索条件と表示項目は既存の [GWTG004] 契約情報検索／一覧と同一にする要件ですが、その現物は要件・steering のいずれからも決まらず未確定事項 ② に送られています。既存画面へ寄せずデザインシステムで素直に描くことを人間が確定したため（2026-09-16）、匿名のプレースホルダーで型のみを示しています。並べた項目数は件数を示すものではありません。

画面にできなかった要件は `wireframe-manifest.json` の `unrealized[]` を参照してください。

表示は `../wireframe-viewer.html` から確認してください。
