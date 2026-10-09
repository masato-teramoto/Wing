---
name: aidd-implement
description: 承認済みtasksから指定タスクを1件ずつ実装し、feature全体で品質検査と人間承認を行う。
---

# /aidd-implement <feature> [1,2,...]

## 手順

1. `.claude/skills/aidd-common/references/host-protocol.md` と
   `.claude/skills/aidd-common/references/implementation/contract.md` を読む。
   呼出し先の順の正は `.claude/skills/aidd-common/command.yaml` の `aidd-implement`。
   feature、指定タスクIDを解決する。階層IDを整数へ変換しない。
2. requirements/design/tasks、steeringとdocs、案件の実際の検証設定を読む。
   docs等に既存の検証用コマンド・実行手順があれば、設定を決める前に読む。
   検証計画を新規作成・変更する時は、`.claude/skills/aidd-common/references/implementation/verification-plan.md`を読み、
   `.aidd/implementation/config/<feature>.json`を用意する。新規コードタスクの仕様書生成は同ルールで設定する。
   task_reviewは同文書の「ACEの適用区分」を正とし、対象featureのtasksの作成・修正要求と履歴を確認する。
   tasksの新規作成・明示的な再作成ではACEを既定有効にし、局所修正・通常再開・VerUpのみでは既存の設定有無を維持する。
   検証計画の未作成や再承認だけで再作成と判断しない。明示的な非適用指示は尊重する。
   Phase 8開始後の変更は、全タスクの再検証・再承認への影響を事前に示して、契約の設定変更・rebase手順で切り替える。
   承認済み仕様と実環境から選べる値は判断して進める。仕様の矛盾・根拠不足・承認範囲の変更は質問／差戻しで扱う。
   必須検査を省略したり、便宜的な成功コマンドを作ったりしない。
   ツール導入は承認済みの準備タスクが扱う。実環境と計画を照合し、導入前に必要なタスクを選ぶ。
   既存環境が利用可能なら重複導入しない。導入対象・影響範囲が計画を超える場合は通常の計画見直しへ戻す。
   導入を検査コマンドへ混ぜず、契約の準備タスク手順に従う。
3. Feature 方式（`workflow.mode` が `feature`）では、選択の前に計画停止点 `implement-plan[S]` を通す（全件方式では呼ばない）。
   引数の feature が選択中の S と同じなら `advance --call implement-plan --item <S>`。違えば引数を人の指示として
   `select-scope`（`{"feature": "<引数>"}`）を呼び、許可されなければ理由を示して停止する。通れば新しい S で `implement-plan` へ進む。
   計画の wait では提示（切替元・対象タスク・検証計画・停止回数・未承認の利用側・依存先との変更範囲の重なり）を人へ示し、
   `accept-plan`（判断は note）か、別の feature の `select-scope` の実回答だけを受け取る。了承前にタスクを始めない。
   了承済みなら L0 が通過済みとして止まらない。検証計画や tasks を変えたときは再提示される。
   新規選択は保存済みrequest_idとtask_idsをpayloadへ書き、event=implement-gate-run、
   item=featureで `implement-select`。省略時はtask_idsキーを省く。
   通常の再開は保存したrequest_idで手順4へ進む。選択操作の再送が必要な時だけ、元と同じpayloadでimplement-selectを再送する。
   新しいIDで中断中の要求を置き換えない。
4. action=implement-gate-run、item=featureで `implement-next` を実行する（payloadは`{"request_id":"保存済みID"}`）。
   L3が依存順に1件を選び、flow.yamlに定義した正規flowを解決する。
   生成・選択修正はimplement、最終検査はimplement-reviewを既定とする。
   返却のcallを正とし、Skillがアクション名からcallを作り直したり、直接アクションを呼び出したりしない。
   タスクでは固定のtask_item、最終検査ではfeatureをitemとするL0 emitを返す。
5. emitされたSkillだけを実行し、返されたevent/item/dispatchで `submit` する。
   task-specification-v1のemitはcheck-runnerへcontextを渡して資料生成を行う。仕様書内容の追加レビューはしない。
   implementation-task-review-v1（reverify の子 execution では implementation-task-reverify-v1）のemitはcheck-runnerへcontextを渡し、当該タスクと関連入力を3観点で1回検査する。
   task-specification-reviewのwaitでは存在する仕様書と差分、統合コードレビュー結果、実MCP状態・未完了理由を人へ提示し、
   実回答だけをrespondへ渡す。続行前は次タスクへ進まない。この時点で
   `.claude/skills/aidd-common/references/implementation/task-specification.md`の生成・提示以降を参照する。
   タスク内のメモ・検証は契約の専用actionを使用する。通常のSkill結果で完了を推測しない。
   タスク末尾の生成・レビュー結果または回答が不正としてfailになったら、理由を確認して`implement-retry`で新しいdispatchへ進み、訂正した内容を提出する。
   旧dispatchへの内容変更や保存済みの回答・検証証跡の上書きはしない。コードを変更した場合は従来の再検証条件を適用する。
   保存途中の中断は`advance`で再開する。通信応答が不明な場合はhost-protocolの同一操作再送で成否を確定してから判断する。
   doneになったら親の `implement-next` を再実行する。partialなら残件を示して終了する。
6. 最終検査emitはcheck-runnerへ渡す。コードprofile、snapshot、ツール実績、全観点を渡す。
   最終検査の前に、`references/implementation/reporting.md` に従いfeature別のレポート設定を用意する。
   タスク分割・check_ids・既存テストの用途は変えず、スイート／モジュール単位で出力を追加する。
   検査対象の実コードと可読レポートを読ませる。submit後の実review waitで、
   `report_summary`の入口とOSSレポート一式を人間へ提示する。
7. 実際の判断・解消・承認はhost-protocolのrespondで受け取る。修正が選ばれた場合だけ
   `implement-repair` に元指摘とタスク対応・実指示・review_context・実回答者を渡す。
   分解不能ならtasksの見直しを提案して停止する。新しい親request_idで4へ戻る。
8. 全修正後の再検査と実際の解消確認を経て、feature全体を承認する。
   検査未実施・失敗・timeout・観点不足を人間の指摘受容で免除しない。
9. 全 feature の実装承認の後（L3 の返却の `next_action` が案内する。両方式）に、案件レベルの確認へ進む。
   `.claude/skills/aidd-common/references/implementation/integration.md` を読み、案件の検証計画
   `.aidd/implementation/config/_project.json` を用意する（build と smoke の checks。smoke は wrapper の 1 経路。
   owner は L3 が `workflow.smoke_owner`（tasks の計画停止点で選んだ値）と照合するので、その値を写す）。
   `advance --call implement-integration-run --item build`、続いて `--item smoke` を呼ぶ。失敗したら受領証とログを示し、
   コードか _project.json を直して同じ group を呼び直す。成功を推測で報告しない。
10. smoke の合格の返却 `chunks` のチャンク ID ごとに `advance --call implement-cross-ace-run --item <チャンク ID>` を呼ぶ。
   失敗の返却は L3 が分割・送り直しを決めて新しい `chunks` を返すので、そのとおりに呼ぶ。停止の返却は理由を人へ示して止まる。
11. `chunks` が空になったら `advance --call implement-cross-gate` を呼ぶ（item なし）。emit は check-runner へ
   profile=implementation-cross-v1 で渡し、review wait では指摘・全体結合確認の結果・ACE 対象外の一覧を人へ示して、
   実回答だけを respond へ渡す。承認されるまで Phase 8 は完了にならない（両方式）。

承認済み feature の入力（依存先・docs の固定版・検証計画・steering・Templates・共有コード）が変わって照合が落ちたときは、
`implement-rebase` の前に `implement-reverify`（action=implement-gate-run、item=feature、payload `{"operation_id","reason"}`）で
3 段に仕分ける。(2) の親要求は `implement-next` で進め、emit の context に `reverify` があるタスクでは作成 Skill を呼ばず、
コードを編集せずに `implement-check`（green・verify）と completed の submit だけを行う。(1) は `implement-select` で再生成する。
配布の更新で定義・`.claude` 資材が変わって止まったときは、静止境界で `implement-repin`（payload `{"operation_id","reason"}`）を
呼ぶ。再検査要の差分が返れば、その feature で `implement-reverify` を呼ぶ。Phase 8 の定義が変わった場合は `implement-rebase`。

タスクの繰り返し（依存順の 1 件ずつ）はこの手順と L3 の `implement-next` が持つ。L0 は呼ばれた 1 件だけを実行する。
生成直後の修正emitがnoopなら無変更でcompletedを返す。実修正は人の要求に対応づく場合だけ行う。
TDD内の修復は同じ作業アクション内で行う。
工程選択はこの入口とL3、flow内の順序と各start/run/endの実行・再開はL0が担当する。
設定変更・旧形式の実行により停止した場合は、実装契約の切り替え手順に従う。
