# 契約情報インポート ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

画面で指定する項目・要否は未確定です。取込の対象をこの画面からのアップロードで受け取るか所定の配置場所から読むかも確定していないため、ファイルを選ぶ欄は置いていません。取込の処理そのものはバッチが行い、この画面は実行の指示と受付の確認のみを扱います。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `contract-info-import` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/contract-info-import/requirements.md`（`status: approved`）、`steering/` 一式 |

## ページ一覧

| ファイル | 画面 | 状態 |
|---|---|---|
| `import-input.html` | 契約情報インポート実行 | `① 入力` |
| `import-input-error.html` | 契約情報インポート実行 | `input-error` |
| `import-cancel-confirm.html` | 契約情報インポート実行 | `cancel-confirm`（中断の確認） |
| `import-confirm.html` | 契約情報インポート実行 | `② 確認` |
| `import-submitting.html` | 契約情報インポート実行 | `submitting` |
| `import-submit-error.html` | 契約情報インポート実行 | `submit-error` |
| `import-done.html` | 契約情報インポート実行 | `③ 完了` |
| `error-403.html` | エラー画面（権限なし） | `default` |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| NotificationBanner を要する通知 | 情報アイコンの SVG 実体が DS v0.0.11 に無いため。`missing[]` に記録 |

## 画面に載せていない要件

| 要件 | 理由 |
|---|---|
| Requirement 2 の受入基準 5 / Requirement 3 の受入基準 6（実行結果の確認手段・エラー件数の提示） | 未確定事項 ④。DS にも `job-monitor` パターンが無い |
| Requirement 1 / 2（取込対象の受け取り方） | 未確定事項 ⑤ |

表示は `../wireframe-viewer.html` から確認してください。
