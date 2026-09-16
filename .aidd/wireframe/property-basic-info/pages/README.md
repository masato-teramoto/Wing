# 物件基本情報 登録・変更／承認 ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `property-basic-info` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/property-basic-info/requirements.md`（`status: approved`）、`steering/` 一式 |

## 状態とファイルの対応

| ファイル | 画面 | 状態 |
|---|---|---|
| `property-form-new.html` | 物件基本情報 登録・変更 | default（新規登録） |
| `property-form-edit.html` | 物件基本情報 登録・変更 | default（変更） |
| `property-form-input-error.html` | 物件基本情報 登録・変更 | input-error |
| `property-form-submitting.html` | 物件基本情報 登録・変更 | submitting |
| `property-form-loading.html` | 物件基本情報 登録・変更 | loading |
| `property-form-leave-confirm.html` | 物件基本情報 登録・変更 | leave-confirm |
| `property-approval-pending.html` | 物件基本情報の承認 | pending |
| `property-approval-approve-dialog.html` | 物件基本情報の承認 | pending（承認の確定ダイアログ） |
| `property-approval-reject-dialog.html` | 物件基本情報の承認 | pending（差戻しの確定ダイアログ） |
| `property-approval-action-error.html` | 物件基本情報の承認 | action-error |
| `property-approval-not-actionable.html` | 物件基本情報の承認 | not-actionable |
| `property-approval-history-empty.html` | 物件基本情報の承認 | history-empty |
| `property-approval-loading.html` | 物件基本情報の承認 | loading |
| `error-403.html` | エラー画面（権限なし） | default |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| form-page `save-success` / `save-error` | NotificationBanner の情報アイコンの SVG 実体がデザインシステム v0.0.11 に無いため |
| approval `action-done` | 同上 |
| approval `approving` | ModalDialog の確定ボタンの loading 状態であり、部品側の状態のためページを分けていない |

## 画面に載せていない要件

入力項目の名称・桁・必須は要件で確定していないため（未確定事項 ②）、匿名のプレースホルダーで項目数と配置のみを示しています。
そのほか画面にできなかった要件は `wireframe-manifest.json` の `unrealized[]` を参照してください。

表示は `../wireframe-viewer.html` から確認してください。
