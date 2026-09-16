# 発行依頼書 ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `issue-request` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/issue-request/requirements.md`（`status: approved`）、`steering/` 一式 |

## 状態とファイルの対応

| ファイル | 画面 | 状態 |
|---|---|---|
| `issue-form-new-single.html` | 発行依頼書 登録・変更 | default（新規登録・単独局モード） |
| `issue-form-edit-multi.html` | 発行依頼書 登録・変更 | default（変更・複数局モード） |
| `issue-form-approve.html` | 発行依頼書 登録・変更 | default（承認者として開いた状態） |
| `issue-form-tutorial-empty.html` | 発行依頼書 登録・変更 | default（チュートリアルの設定なし） |
| `issue-form-input-error.html` | 発行依頼書 登録・変更 | input-error / row-error |
| `issue-form-submitting.html` | 発行依頼書 登録・変更 | submitting |
| `issue-form-loading.html` | 発行依頼書 登録・変更 | loading |
| `issue-form-leave-confirm.html` | 発行依頼書 登録・変更 | leave-confirm |
| `barcode-popup-default.html` | バーコードの生成（ポップアップ） | default |
| `barcode-popup-rows-selected.html` | バーコードの生成（ポップアップ） | rows-selected |
| `barcode-popup-delete-confirm.html` | バーコードの生成（ポップアップ） | rows-selected（削除の確認ダイアログ） |
| `barcode-popup-empty.html` | バーコードの生成（ポップアップ） | empty |
| `barcode-popup-loading.html` | バーコードの生成（ポップアップ） | loading |
| `error-403.html` | エラー画面（権限なし） | default |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| form-page `save-success` / `save-error` | NotificationBanner の情報アイコンの SVG 実体がデザインシステム v0.0.11 に無いため |
| list-page `notice` / `bulk-action-done` | 同上 |
| list-page `page-changed` / `filters-applied` / `filter-empty` | バーコード一覧は検索条件・ページングを持つ要件が無いため |

## 画面に載せていない要件

発行依頼書の入力項目の名称・桁・必須は要件で確定しておらず（未確定事項 ②）、匿名のプレースホルダーで項目数と配置のみを示しています。複数局モードで制御する項目（未確定事項 ⑧）・サンプル入力ボタンの数と対象範囲（未確定事項 ⑤）・金額の算式（未確定事項 ⑦）・発番の採番定義（未確定事項 ④）・ステータスの値の一覧と遷移（未確定事項 ⑩）・バーコードの規格と桁（未確定事項 ⑪）も確定していないため、いずれも画面で確定させていません。

画面にできなかった要件は `wireframe-manifest.json` の `unrealized[]` を参照してください。

表示は `../wireframe-viewer.html` から確認してください。
