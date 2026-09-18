# 発行依頼書チュートリアル設定 ワイヤーフレーム

**これは要件定義段階のワイヤーフレームです**
画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを確約するものではありません。
色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

画面に並ぶ項目名・桁・必須の別は未確定です。この画面は 1 フォーム分の設定の型を示しています。26 フォーム相当の設定を 1 画面に集約するか複数画面に分けるかは基本設計で確定します。

## 生成条件

| 項目 | 値 |
|---|---|
| feature | `issue-request-tutorial` |
| デザインシステムのタグ | `v0.0.11` |
| デザインシステムの短縮 SHA | `78822dc` |
| トークンのプロファイル | `wireframe` |
| 根拠にした仕様 | `specs/issue-request-tutorial/requirements.md`（`status: approved`）、`steering/` 一式 |

## ページ一覧

| ファイル | 画面 | 状態 |
|---|---|---|
| `tutorial-form-new.html` | チュートリアル設定 | `default`（新規登録） |
| `tutorial-form-edit.html` | チュートリアル設定 | `default`（変更） |
| `tutorial-form-delete-confirm.html` | チュートリアル設定 | `default`（設定削除の確認ダイアログ） |
| `tutorial-form-min-reached.html` | チュートリアル設定 | `min-reached` |
| `tutorial-form-input-error.html` | チュートリアル設定 | `input-error`（行内の `row-error` を含む） |
| `tutorial-form-submitting.html` | チュートリアル設定 | `submitting` |
| `tutorial-form-loading.html` | チュートリアル設定 | `loading` |
| `tutorial-form-leave-confirm.html` | チュートリアル設定 | `leave-confirm` |
| `error-403.html` | エラー画面（権限なし） | `default` |

## 生成していない状態

| 状態 | 理由 |
|---|---|
| `save-success` / `save-error` | NotificationBanner の情報アイコンの SVG 実体が DS v0.0.11 に無いため。`unrealized[]` に DS 不足として記録（Requirement 2） |

## 画面に載せていない要件

| 要件 | 理由 |
|---|---|
| Requirement 2（26 フォーム相当の設定項目） | 設定項目の中身と全体構成が未確定 |
| Requirement 3（選択肢の種類・表示順序の決まり方） | 未確定事項 ④・⑤。順序を決める設定項目は未画面化 |

表示は `../wireframe-viewer.html` から確認してください。
