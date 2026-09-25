# α2 → α3 データ変換済み環境

α3実行資材は読み込み元と同一です。移行先の案件データだけを変換しています。
既存本文・質問・判断は保持しました。旧承認は履歴であり、新しい検査・承認・完了は未実施です。
旧 approved / review の成果物は、本文を保ったまま移行先で draft にしています。

## CCで最初に入力する文

> MIGRATION.md を読み、旧次アクションと未回答事項を確認してから、下記の順に既存α3で再検査・再開してください。既存本文・回答・判断を引き継ぎ、必要な箇所だけ変更してください。検査・承認を代行せず、実際のユーザー回答を待ってください。

このフォルダで START.cmd を使って起動できます。汎用起動案内より、この移行手順の入口を使ってください。
外部リポジトリ・MCP・独自Skill等は移行元に含まれるファイルだけが保存されています。旧設定は自動で有効にしません。

## 実行順（各行を完了してから次へ）

`.claude/skills/aidd-common/references/host-protocol.md` に従い、advance / submit / respond を使います。
イベント単位の既存入口を使います。Phase 1〜3の再検査で requirements-init 全体を開始し直さないでください。
再実行時は completion で有効な完了証跡を確認し、完了済みの行を繰り返さず、未完了行の同じ event/item を再開します。
単に L0 の done だけで次へ進まず、成果物の工程は completion の complete=true、横断は人間確認まで確認します。
計画（-plan）は成果物のcompletionではなく、実際の了承とworkflow.accepted_plansの現行feature一覧への対応を確認します。

旧 current.phase=5 の上流に、修正・レビュー中の工程があります。
再確認対象: Phase 2 / Phase 3 / Phase 4。
旧申し送りは最初の未完了上流工程（Phase 2 / steering）で確認します。
一覧が draft/review の場合、旧 feature の対応付けだけに使用しています。Phase 3 の再承認と既存α3による同期までは、下流の実行計画・承認済みfeatureとして使用しません。

1. 再検査・確認: Phase 1 / intake

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event requirement-intake-revise advance
   ```

2. 未完了上流の修正・再検査・再承認: Phase 2 / steering

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event steering-authoring-revise advance
   ```

3. 未完了上流の修正・再検査・再承認: Phase 3 / feature

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event feature-decomposition-revise advance
   ```

4. 未完了上流の修正・再検査・再承認: Phase 4 / requirements / property-basic-info

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event requirements-authoring-revise --item property-basic-info advance
   ```

5. 再検査・確認: Phase 4 / requirements / issue-request-tutorial

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event requirements-authoring-revise --item issue-request-tutorial advance
   ```

6. 未完了上流の修正・再検査・再承認: Phase 4 / requirements / issue-request

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event requirements-authoring-revise --item issue-request advance
   ```

7. 再検査・確認: Phase 4 / requirements / contract-application-status

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event requirements-authoring-revise --item contract-application-status advance
   ```

8. 再検査・確認: Phase 4 / requirements / contract-info-import

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event requirements-authoring-revise --item contract-info-import advance
   ```

9. 再検査・確認: Phase 4 / requirements / contract-info-download

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event requirements-authoring-revise --item contract-info-download advance
   ```

10. 再検査・確認: Phase 4 / requirements

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event requirements-cross-gate advance
   ```

11. 再検査・確認: Phase 5 / design / property-basic-info

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event design-authoring-revise --item property-basic-info advance
   ```

12. 再検査・確認: Phase 5 / design

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event design-plan advance
   ```

13. 元の工程への復帰: Phase 5 / design / issue-request-tutorial

   ```text
   python -X utf8 -B -S aidd-run.py workflow --event design-authoring-generate --item issue-request-tutorial advance
   ```

最後の行は再開入口です。以後、残るfeature・後続工程を既存α3の順に進めます。
Phase 1〜3内で再開した場合は、残りを個別イベント（requirement-intake-generate / steering-authoring-generate / feature-decomposition-generate と各 -revise）で完了し、Phase 3後に /aidd-requirements へ進んでください。
Phase 4/5では既存の計画確認とfeature順序・横断確認が必要です。修正でfeature一覧が変わった場合は、この旧順序を使わず計画を見直してください。

## 旧記録との照合

各工程の検査結果が出たら、承認前に既存の migration-review で旧記録を照合します。
照合JSONは state_review と records（file、sha256、review_summary、carried_findings）です。
旧残指摘は現在の scope/run/number へ対応付けます。未対応・再検査省略・過去の人間判断を消さず、「残件なし」と回答を自動生成しないでください。詳細は既存 references/migration.md を参照します。
旧ゲートがない工程でも、旧状態の質問・残作業を確認してから新しい検査・承認を進めます。
workflow.waiting に保存した旧申し送りは原文です。人間の回答が必要な事項を提示し、実際の回答だけを既存 answer 操作で記録します。
blockers の resume_event / resume_item が戻り先です。再承認後に既存処理で解除されます。未解除なら upstream-approved で確認します。全上流と必要な横断確認が整うまで下流へ進みません。

## 旧環境での次の行動（原文）

【2026-09-25T12:54:34+09:00】#28: steering 7 回目（最後の回）のゲートを実行した（① / ②。③ の指定により ① の指摘 2 件（#74 / #75）があっても ② まで実行）。指摘 16 件（① 2 件 #74〜#75 / ② 14 件 #76〜#89）をゲート記録へ追記し、steering 7 ファイルを draft → review に遷移させた。③ で #74〜#89 の判断を聞き取って転記する。そのあと feature-list（4 回目）→ requirements property-basic-info（9 回目）→ issue-request（7 回目）。

## 保存場所

- .aidd/phase-progress.json: 既存α3が読む再検査依頼、戻り先、待機事項、旧状態
- .aidd/alpha2-migration/resume-plan.json: この順序と元の再開位置（補助資料）
- .aidd/legacy-gates/: 旧ゲート原本。新しい記録は .aidd/gates/ に生成
- .aidd/alpha2-migration/source-snapshot.zip: 移行元原本。ZIP入力なら input.zip に添付全体も保存
- .aidd/alpha2-migration/manifest.json: 原本・実行資材のハッシュ、status変換の明細

Phase 1開始〜Phase 5完了・Phase 6/7未着手が対象です。再開後にPhase 6へ進む通常操作は可能です。
