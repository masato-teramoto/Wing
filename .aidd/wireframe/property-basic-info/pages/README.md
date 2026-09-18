# 物件基本情報 ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

画面に並ぶ項目名・桁・必須の別は未確定です。入力項目は「項目 1〜10」の匿名のプレースホルダーで、項目数と配置のイメージのみを示しています。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `property-basic-info` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/property-basic-info/requirements.md`（`status: approved`）、`steering/` 一式 |

## ページ一覧

| ファイル | 画面 | 状態 |
|---|---|---|
| `property-form-new.html` | 物件基本情報 登録・変更 | `default`（新規登録） |
| `property-form-edit.html` | 物件基本情報 登録・変更 | `default`（変更） |
| `property-form-input-error.html` | 物件基本情報 登録・変更 | `input-error` |
| `property-form-submitting.html` | 物件基本情報 登録・変更 | `submitting` |
| `property-form-loading.html` | 物件基本情報 登録・変更 | `loading` |
| `property-form-leave-confirm.html` | 物件基本情報 登録・変更 | `leave-confirm` |
| `property-approval-pending.html` | 物件基本情報の承認 | `pending` |
| `property-approval-approve-dialog.html` | 物件基本情報の承認 | `pending`（承認の確定ダイアログ） |
| `property-approval-reject-dialog.html` | 物件基本情報の承認 | `pending`（差戻しの確定ダイアログ） |
| `property-approval-action-error.html` | 物件基本情報の承認 | `action-error` |
| `property-approval-not-actionable.html` | 物件基本情報の承認 | `not-actionable` |
| `property-approval-history-empty.html` | 物件基本情報の承認 | `history-empty` |
| `property-approval-loading.html` | 物件基本情報の承認 | `loading` |
| `error-403.html` | エラー画面（権限なし） | `default` |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| `save-success` / `save-error`（form-page） | NotificationBanner の情報アイコンの SVG 実体が DS v0.0.11 に無いため。`unrealized[]` に DS 不足として記録（Requirement 1） |
| `action-done`（approval） | 同上。`unrealized[]` に記録（Requirement 4） |
| `approving`（approval） | ModalDialog の確定 Button の loading 表現であり、部品の挙動であって画面の型ではないため |

## 画面に載せていない要件

| 要件 | 理由 |
|---|---|
| Requirement 8 | requirements 起因（未確定事項） |
| Requirement 9（稟議資料の帳票 3 種） | 出力される帳票そのものは画面化していない。起点操作（「帳票を出力」）は画面にある |
| Requirement 10（出力情報の PDF 別ウインドウ表示） | DS に該当する型が無い。起点操作は画面にある |
| Requirement 2 の受入基準 2（権限に応じた活性・非活性・非表示） | どの要素をどの権限で制御するかが未確定 |

表示は `../wireframe-viewer.html` から確認してください。
