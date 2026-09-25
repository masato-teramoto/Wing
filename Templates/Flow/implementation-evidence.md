# Phase 8 コード証跡契約 v1

Phase 7のtasks承認は計画、チェック欄はタスクの実装・検証、Phase 8はfeature実装結果の承認を表す。
これらを相互に代用しない。

- `plans/<feature>/active.json`：承認原本の完全なバイト列・plan_ref・タスク構造・許可更新履歴。
- `requests/<request-id>.json`：選択集合と依存順、計画・検証方針・子実行の対応。
- `runs/<execution-id>/execution.json`：親ID・単一task_id・開始時基点・許可範囲・修正元。
- `runs/<execution-id>/verify.json`：当該taskの現在コード・必須check ID・実行結果・完全ログ参照。
- `features/<feature>/review.json`：コードprofileの現在コード在庫、上流ハッシュ、全タスク証跡、検証計画。
- `features/<feature>/inspections/<run>/`：最終ツール検査と意味観点の実施証跡。
- `reporting/<feature>.json`：タスク計画とは独立したfeature最終レポートの設定。
- `features/<feature>/inspections/<run>/reports/` と `reporting/reports/`：試行別の可読概要・仕様コピー・OSS出力一式。

パスは `.aidd/implementation/` 以下。各JSONはschema=1。
コードprofileは `implementation-code-v1`。v2ゲート記録の対象成果物はreview.json、原本SHA256は
その完全バイト列のSHA256とする。L3はmanifestの内部参照を現在の実ファイルと再照合する。
文書profileのprotected_digestと混同しない。検査中も実コード・tasks・manifestは読取り専用。

ハッシュがあるだけでは完了しない。単一taskのL0末尾完了、全必須ツールの最新実施・成功、
全意味観点の実績と、同じ検査回に対する人間の実回答が揃ったfeatureだけを承認できる。
旧チェック済みタスクや旧コード記録は自動移行で承認証跡に変換せず、再検証する。

レポートの単位はスイート／モジュールでありtaskではない。タスクのチェック欄やcheck_idsは増やさない。
最終検査ではreporting設定・入力版もreview.jsonへ固定し、出力一覧・付属ファイルのハッシュをtools.jsonに残す。
意味検査はtools.jsonのハッシュを返し、scope-check後の検査証跡にも結び付ける。
詳細は配布先の`references/implementation/reporting.md`。旧タスク証跡は保持するが、
旧形式の最終承認を新しいレポート取得済みとみなさず、新しい検査回で報告と実承認を行う。
