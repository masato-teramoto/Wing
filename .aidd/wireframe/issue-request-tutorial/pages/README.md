# チュートリアル設定 ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `issue-request-tutorial` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/issue-request-tutorial/requirements.md`（`status: approved`）、`steering/` 一式 |

## 状態とファイルの対応

| ファイル | 画面 | 状態 |
|---|---|---|
| `tutorial-form-new.html` | チュートリアル設定 | default（新規登録） |
| `tutorial-form-edit.html` | チュートリアル設定 | default（変更） |
| `tutorial-form-min-reached.html` | チュートリアル設定 | min-reached（行数が最小） |
| `tutorial-form-input-error.html` | チュートリアル設定 | input-error / row-error |
| `tutorial-form-submitting.html` | チュートリアル設定 | submitting |
| `tutorial-form-loading.html` | チュートリアル設定 | loading |
| `tutorial-form-leave-confirm.html` | チュートリアル設定 | leave-confirm |
| `tutorial-form-delete-confirm.html` | チュートリアル設定 | default（設定削除の確認ダイアログ） |
| `error-403.html` | エラー画面（権限なし） | default |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| form-page `save-success` / `save-error` | NotificationBanner の情報アイコンの SVG 実体がデザインシステム v0.0.11 に無いため |

## 画面に載せていない要件

現行の設定用ウインドウ 26 フォームそれぞれの設定項目は要件で確定しておらず（未確定事項 ②）、26 フォーム相当を 1 画面に集約するか複数画面に分けるかも確定していません（未確定事項 ③）。この画面は 1 フォーム分の設定の型のみを示しています。

画面にできなかった要件は `wireframe-manifest.json` の `unrealized[]` を参照してください。

表示は `../wireframe-viewer.html` から確認してください。
