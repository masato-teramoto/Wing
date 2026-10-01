# main_flow の実行属性・記録の移行

実行方式は `command` / `script` / `skill` と実行属性に統一する。

| 旧設定 | 新設定 |
|---|---|
| `type: approval` | `type: script, requiresHuman: true` |
| `type: agent` | `type: skill, isAgent: true`。target は工程の合成 Skill |

新しい Skill の呼出先は `.claude/skills/<target>/SKILL.md`。`isAgent: true` の実行は `.claude/agents/check-runner.md` を別コンテキストで起動する。`calls` は手順内で読む観点 Skill の順序であり、同じ観点を異なるパラメータで使うときは重複を保持する。

旧型は自動変換しない。設定の型だけを変更しても、旧 agent 名は新合成 Skill 名にならず、ゲートの unit 名も変わる。新配布物を原本から合成して配置する。

既存案件では、作業を停止し、設定・phase-progress.json・ゲート記録・成果物を版管理または別ディレクトリへ保存する。新配布物の配置だけで過去の成功印を流用しない。実行記録を持つ旧状態は `engine_schema: 2` への移行が必要であり、数字だけを手で書き換えて続行しない。

移行時は旧 events と trace を履歴として残し、再確認する各 unit に無効化記録を追加する。承認済み成果物と人間の証跡を削除しない。新しい検査回に対応する確認が揃ってから再開する。案件ごとの既存成果物・承認の再利用範囲はホストの移行手順で明示する。

原本が分離されているため、ランナーの `validate` と実行は合成済みのパッケージに対して行う。Skill や script が欠けた構成を「検証済み」にしない。

## 既存案件を移す手順

移行は停止中の案件のコピーで行う。元案件は保持する。旧設定・状態・成果物・ゲートの
バイト列をバックアップし、旧記録を `.aidd/legacy-gates/` に同名で保存する。
`scripts/gate_record.py <旧記録>` は全行と SHA256 を表示する読取専用の棚卸しであり、
旧記録から指摘0件・承認済みを自動推定しない。

1. 空の移行先に新配布物を置き、RFP と既存の自成果物をコピーする。
2. `scripts/migrate_state.py --source <旧状態> --output <新状態>` で新しい状態を作る。
   出力が既存なら停止する。旧状態全体を legacy_state に保持し、旧成功印には
   invalidated を追記する。trace は旧状態内に残し、稼働中のものとして再利用しない。
3. 旧ゲート全ファイルを legacy-gates に保存する。新しい gates には旧形式を混在させない。
   移行先の成果物は移行対象として draft に戻す。本文・質問・回答・出典は維持する。
   旧 blocker と質問は legacy_state を人間が確認し、必要な待機・修正入力を新方式へ引き継ぐ。
4. Phase 1 から順に再検査する。過去の未解消は新しい指摘に再提示する。
   承認前に実際の人間確認を `host_operations.py --action <アクション> --actor <人>
   --payload <照合JSON> migration-review` に渡す。工程ごとに照合できる。
5. payload は `state_review`（旧質問・差戻し等の引継ぎ確認）と `records` の配列。
   各要素は `file`（旧記録名）、`sha256`、`review_summary`、`carried_findings`。
   未解消の対応は `legacy_location` と新しい `scope/run/number` の組で列挙する。
   残件がない場合も空配列と理由を実回答として記録する。旧文書の曖昧な表を
   自動変換したという扱いにはしない。
6. 対応する工程の照合前は approve が停止する。照合後も新しい検査・判断・承認が必要。

移行補助は状態の安全な新規出力と照合記録までを扱う。旧案件の意味的な残件対応や
質問の引継ぎは人間の確認が必要であり、自動移行完了とは報告しない。

## review 段階ガード導入版（2026-09-23）

engine_schema が2でも、旧版の emit/wait には dispatch.id と検査証明がない。
旧版の payload と新しいCLIを混在させない。新しい試行はクリーンな配布を別フォルダへ配置する。
既存案件へは停止中のコピーで資材・状態・証跡を診断してから導入し、実行途中のフォルダへ上書きしない。
既にscope-checkより先に承認した案件を、この導入だけで正常化したとは扱わない。
判断や業務要求を復旧の口実で変えず、承認取消等の専用復旧は別途設計する。
導入後の通常操作と同一操作の再送は host-protocol.md に従う。

## 必須検査層ガード導入版（2026-09-24）

旧版では通常工程の①だけでも指摘を受容すると承認できた。導入後は各スコープの最新回に
status-protocol.md §6 の必須層が揃わない限り承認・横断確認・最終完了を認めない。
v2 記録の書式は維持し、過去の承認・判断・実行層を削除・書換えしない。
不足した層を旧記録へ追記して実施済みに見せず、正規の再検査回と人間の確認を残す。

実行途中の案件は停止中のコピーで診断する。旧版の prepared 承認も再送時に検査充足を
確認するため、部分検査であれば停止する。この場合は操作履歴を削除して迂回せず、旧状態を
保持して上記の移行手順で再検査する。指摘の「対応せず進める」は検査省略の承認にならない。

## 生成・修正アクション統合版（2026-09-24）

Phase 1–7 のアクション名は `<base>-generate` / `<base>-revise` に変更した。
入力証跡は `workflow.input_signature_version: 2` とし、status/updated_at と正規の
tasks 実績更新を除く保護内容で照合する。旧名の入力キーや版情報の無い既存入力証跡を
検出すると、書換えずに移行手順を案内して停止する。数字やアクション名だけの手修正はしない。
旧フローや修正ブランチ単体で進めた案件は、上記の「既存案件を移す手順」に従い、
停止中のコピーを移行・再検査する。過去の完了証明を新しい入力へ付け替えない。

## 工程契約廃止版（2026-09-30）

`contracts/main_flow.json` を廃止した。各アクションの入出力は `action.yaml` の `inputs` / `outputs`、
工程は flow.yaml の flow（flow 名が工程名）、生成か修正かは Skill の手順の宣言 `役割:` で決める（第 3 版）。
flow `requirements-init` を flow `intake` / `steering` / `feature` とそれをまとめる flows に分け、
Phase 8 のタスク flow `implement-task` を `implement` に改名した。L3 の完了記録・ゲート記録名・
進捗キー・指摘の `phase` 欄は変わらない。L0 の実行記録のキー（`<flow>/<action>[<item>]`）だけが変わる。

旧配布物で始めた案件は、次の手順で移す。

1. 案件を止め、設定・`phase-progress.json`・ゲート記録・成果物を保存する。
2. 保留中の emit / wait は旧配布物で終える。Phase 8 の実行中タスクも旧配布物で終える。
3. 新配布物を置き、L0 の `migrate-flow` を順に実行する。

   ```text
   aidd.py --root <案件> migrate-flow --from requirements-init --to intake --json
   aidd.py --root <案件> migrate-flow --from requirements-init --to steering --json
   aidd.py --root <案件> migrate-flow --from requirements-init --to feature --json
   aidd.py --root <案件> migrate-flow --from implement-task --to implement --json
   ```

   各 unit の最後の記録を新しいキーで履歴末尾へ追記する。旧記録は残す。
   無効化済みの unit は写さない。移行先に別の結果があれば停止する。
4. Phase 8 を始めていた feature は、保存済みの flow 設定が変わるため、`implement-rebase`
   （実 actor と `{operation_id, reason}`）で明示的に切り替える。全タスクの再検証が求められる。
5. `aidd.py validate` と `workflow progress` で、完了済みの工程が完了のままであることを確認してから再開する。

## 実行アーキテクチャ移行版（2026-09-30）

`AIDD_Harness_実行アーキテクチャ_スペック解説書_v1.pdf` に合わせ、入口をコマンド（`command.yaml`）で管理し、
イベントをアクションに改めた。定義ファイルとキーは次のとおり変わる。

| 旧 | 新 |
|---|---|
| （なし） | `command.yaml`（`- command: { id, command, steps: [{ flow }] }`） |
| `events.yaml`（`- event:`） | `action.yaml`（`- action:`） |
| `flows.yaml`（`event_order`、`- flows:`） | `flow.yaml`（`steps: [{action} \| {flow}]`。flow の並びは入れ子の flow で書く） |
| `gates.yaml`（`target_event`、要素の `event`） | `gate.yaml`（`target_action`、要素の `action`） |
| run の `{event}` | `{action}` |
| 環境変数 `AIDD_EVENT` / `AIDD_EVENT_UNIT` | `AIDD_ACTION` / `AIDD_ACTION_UNIT` |
| host の CLI `--event`、L0 の `redo --event` | `--action` |

`phase-progress.json`（L0 の `event` 欄・`::event` の印を含む）、ゲート記録、Phase 8 の記録、ログの項目、
L0 と host の JSON 出力のキーは変えていない。既存案件の状態はそのまま読める。

1. 未回答の emit / wait は旧配布物で終える（設定ハッシュが変わるため、report が拒否される）。
2. 新配布物を置く。利用者が定義ファイルを変更していた場合は、上の表のとおりファイル名とキーを改め、
   コマンドを `command.yaml` に書く。
3. Phase 8 を始めていた feature は、今までどおり `implement-rebase`（実 actor と `{operation_id, reason}`）で切り替える。
4. `aidd.py validate` で定義を確認してから再開する。

### 第 2 版（繰り返しを Skill が決める）

- `flow.yaml` は `steps`（`- action:` / `- flow:`）で書く。`action_order` と `- flows:` は読込み時にエラー。
- `gate.yaml` の `when` は廃止（読込み時にエラー）。`scripts/repair_pending.py` を削除した。
- `command.yaml` の `per_feature` は廃止。feature ごとかは Skill の `metadata.aidd-per-feature` が持つ。
- 入口 Skill は flow を `--item` 無しで呼び、L0 が問う next に Skill（または host の自動）が答える。
- 実行記録のキーは変わらない。旧配布物で済んだアクションは、そのまま済みとして飛ばされる。

### 第 3 版（L0 は枠組み。繰り返しは入口 Skill の手順）

- L0 は next を問わない。`report --next` と状態ストアの `loops` は廃止（`loops` は保存時に落とす）。
  繰り返しは入口 Skill の手順が持ち、1 回ごとに `--item` を付けて生成・修正のアクションを呼ぶ。
- Skill の frontmatter の `metadata.aidd-role` / `metadata.aidd-per-feature` は廃止。`## 手順` の冒頭に
  `役割: 生成（generate）` / `役割: 修正（repair）`、`繰り返し: feature ごと（per-feature）` を書く。
- `gate.yaml` の原本は L4（`l4_governance/main_flow/workflow/gate.yaml`）。配布物では今までどおり `aidd-common/gate.yaml`。
- advance / submit / respond の入口は L3 の `scripts/aidd_entry.py`。L0 の CommandResolver で呼出し先を解決し、
  L0 の `host.Host` に L3 の規則を渡す。`command.yaml` と `gate.yaml` の `- hook:`、`bin/host.py` の CLI は廃止。
  `bin/command_resolver.py` は規則が必要な操作を拒否する。host の操作の記録は `workflow.host_operations`
  から状態ストアの `host_operations`（L0 所有）へ移る。旧配布物の途中の操作は旧配布物で終える。
- L3 の `scripts/execution_context.py` は `scripts/phase_rules.py`（工程の規則）と L0 の `bin/execution_context.py`
  （実行器の間の文脈）に分かれた。`project_state.py` は L0 の `bin/` へ移った。
- 合成 Skill の手順と `calls` の一致は L4 の `scripts/check_calls.py` が確かめる。
- タスクgateの公開記録と完了証跡も実行・retry世代へ固定する。旧形式の途中executionや回答を自動変換しない。
  旧配布物で完了させるか、明示的な再検証・移行を行い、証跡欠落を承認として補わない。
