# 発行依頼書 ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

画面に並ぶ項目名・桁・必須の別は未確定です。入力項目・明細行の列はいずれも「項目 1〜8」「項目 1〜3」の匿名のプレースホルダーで、項目数と配置のイメージのみを示しています。ステータスの値、採番の書式、金額の算式も未確定です。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `issue-request` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/issue-request/requirements.md`（`status: approved`）、`steering/` 一式 |

## ページ一覧

| ファイル | 画面 | 状態 |
|---|---|---|
| `issue-form-new-single.html` | 発行依頼書 登録・変更 | `default`（新規登録・単独局モード） |
| `issue-form-edit-multi.html` | 発行依頼書 登録・変更 | `default`（変更・複数局モード） |
| `issue-form-tutorial-empty.html` | 発行依頼書 登録・変更 | `default`（チュートリアルの設定なし） |
| `issue-form-min-reached.html` | 発行依頼書 登録・変更 | `min-reached` |
| `issue-form-input-error.html` | 発行依頼書 登録・変更 | `input-error`（行内の `row-error` を含む） |
| `issue-form-submitting.html` | 発行依頼書 登録・変更 | `submitting` |
| `issue-form-loading.html` | 発行依頼書 登録・変更 | `loading` |
| `issue-form-leave-confirm.html` | 発行依頼書 登録・変更 | `leave-confirm` |
| `issue-form-approve.html` | 発行依頼書 登録・変更 | `default`（承認者として開いた状態） |
| `issue-form-approve-dialog.html` | 発行依頼書 登録・変更 | `default`（承認の確定ダイアログ） |
| `barcode-popup-default.html` | バーコードの生成 | `default` |
| `barcode-popup-rows-selected.html` | バーコードの生成 | `rows-selected` |
| `barcode-popup-delete-confirm.html` | バーコードの生成 | `rows-selected`（削除の確認ダイアログ） |
| `barcode-popup-empty.html` | バーコードの生成 | `empty` |
| `barcode-popup-loading.html` | バーコードの生成 | `loading` |
| `barcode-popup-error.html` | バーコードの生成 | `error` |
| `error-403.html` | エラー画面（権限なし） | `default` |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| `save-success` / `save-error`（form-page） | NotificationBanner の情報アイコンの SVG 実体が DS v0.0.11 に無いため。`unrealized[]` に記録（Requirement 1 / 3 / 9） |
| `notice` / `bulk-action-done`（list-page） | 同上。`unrealized[]` に記録（Requirement 11） |

## 承認の画面構成

承認者として開いた状態は独立画面に分離せず、本画面（`form-page`）の状態の 1 つとして組んでいます。差戻しの操作は画面に置いていません（`Requirement 9` 受入基準 1 は「申請の操作」と「承認の操作」のみを定め、`In Scope` は「フローの定義は本フィーチャーで定めない」としているため）。`requirements.md` の Requirement 9 受入基準 1 と `In Scope` が「本画面で受け付ける」と明記しているためです（2026-09-17 に人間が確定）。`approval` パターンが構えとして持つ承認履歴のセクションは本構成では置いていません。

## 画面に載せていない要件

| 要件 | 理由 |
|---|---|
| Requirement 2 の受入基準 2（権限に応じた活性・非活性・非表示） | 未確定事項 ③ |

表示は `../wireframe-viewer.html` から確認してください。
