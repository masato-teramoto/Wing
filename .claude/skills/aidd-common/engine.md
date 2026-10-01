# engine — L0 の実行プロトコル

L0 は L3・L4 の枠組みである。L3・L4 が L0 の設計に従って書いた定義ファイル（L3 の `command.yaml` / `flow.yaml` /
`action.yaml`、L4 の `gate.yaml`）を読み、定義に書かれた script をコマンドラインで、Skill を host agent への emit で実行し、
実行履歴から再開点を選ぶ。**L0 は L3・L4 を import せず、定義ファイル 4 つ以外の L3・L4 のファイルを読まない。**
L3・L4 は L0 を import してよい（`execution_context` / `project_state` / `engine_cli` / `host`）。
main_flow 固有の進捗・差戻し・承認規則の管理原本は L3・L4 に置く。配布では同じ aidd-common に合成する。

## 1. 実行構造

```text
Command → CommandResolver → Workflow Engine → FlowExecutor → ActionExecutor → Skill / script
                                                               └ HookPoint → GateResolver → GateExecutor → GateResult
```

| 部品（`bin/`） | 責務 |
|---|---|
| `definitions.py` | 定義ファイルを読み込んだ後のモデル（`CommandDefinition` / `FlowDefinition` / `StepDefinition` / `ActionDefinition` / `GateDefinition` / `HookDefinition` / `RunDefinition`） |
| `repositories.py` | 定義ファイル `command.yaml` / `flow.yaml` / `action.yaml` / `gate.yaml` の読込み・スキーマ検査・名前による検索（Command / Flow / Action / Gate の Repository） |
| `command_resolver.py` | CommandResolver。コマンドから呼出し先を解決する |
| `workflow_engine.py` | Workflow Engine。呼出しの開始・状態の保存・emit / wait / fail の解釈、report・redo・migrate-flow |
| `flow_executor.py` | FlowExecutor。flow の手順（アクション・入れ子の flow）を 1 周たどり、1 件ずつの境界を記録する |
| `action_executor.py` | ActionExecutor。1 アクションを HookPoint start → 本体 → HookPoint end でたどる。HookPoint ごとにゲートを解決して GateExecutor に渡し、本体の Run を実行する |
| `gate_executor.py` | GateResolver（適用するゲートを記述順に解決）・GateExecutor（1 ゲートを実行）・GateResult |
| `run_dispatcher.py` | Run（script / skill / command）の実行、状態への記録とログ。アクション本体とゲートが共用する |
| `aidd.py` | CLI 入口（validate / status / call / report / redo / migrate-flow）。`describe()` は `validate --json` の中身 |
| `host.py` | host の入口 advance / submit / respond。状態ストアの排他、操作の記録（`host_operations`）、dispatch の照合、報告。規則の段は、規則の層（L3）が渡す `stage_runner` で実行する（CLI は無い） |
| `execution_context.py` | 実行器の間で引き継ぐ文脈（今の Flow / Action / item / ゲート / 検査対象）、`target_review` による出力の選択、script の約束（終了コード・`AIDD-LOG:`）、定義の読込み `definitions()`。L3・L4 が import する |
| `project_state.py` | 状態ストアの案件欄の読み書き（ランナー欄は書かせない）。L3・L4 が import する |
| `engine_cli.py` | `aidd.py` を子プロセスで呼ぶ。host と L3・L4 の規則 script が使う |

ゲートも action と同じ Run を持つ。action は Flow 配下の実行単位であり、計画・横断検査のように 1 アクションだけを呼ぶ場合は、その場でアクション 1 本の flow として扱う。

action は任意で `inputs` / `outputs`（読む入力・書く出力のパスの配列）を持てる。L0 は形（空でない文字列の配列・重複なし）だけを検査し、`validate --json` の各アクション（受渡しの形式のためキーは `events`）に載せて返す。展開・存在・承認の確認は呼出し側の規則が行う。

`command.yaml` のコマンドは、順に呼ぶ呼出し先（`steps[].flow`。flow・action の名前）を持つ。コマンドの step に無い呼出し先も今までどおり呼べる。

`flow.yaml` の flow は手順 `steps` を持つ。各手順は `- action: <名前>`（ActionStep）か `- flow: <名前>`（FlowStep。入れ子の flow）。入れ子の深さは制限しない。循環は読込み時にエラー。実行記録のキーはアクションを直接持つ flow の名前（`<flow>/<action>[<item>]`）。

**繰り返しは L0 に無い。** 呼ばれた呼出し先（flow・action）を、呼出しの `--item` の item で 1 周だけたどる。
入れ子の flow は呼び出し元の item を引き継ぐ。feature ごと・修正の回の繰り返しは L3 の入口 Skill の手順が持ち、
繰り返しの 1 回ごとに `--item` を付けて呼ぶ。修正の次の回は、`redo` で修正アクションの印を無効にしてから呼ぶ。
L0 は 1 回ぶんの前後のゲートを実行するため、検査・人間レビューは繰り返しの 1 回ごとに行われる。

**host の段。** 定義ファイルに hook は無い。`host.Host` は、規則の層（L3）の入口が段を実行する関数（`stage_runner`）を渡して使う。
advance / submit / respond の各段（`resolve` / `guard` / `advance-before` / `advance-after` / `submit-prepare` /
`submit-apply` / `respond-prepare` / `respond-apply` / `respond-output` / `respond-reported`）で、段の名前と材料（案件ルート・状態ストアを含む）を渡し、
JSON object を受け取る。`stage_runner` の無い host は動かない（規則の無い実行をさせない）。

**L4 の規則はゲートの中だけで動く。** L4 は hook を持たず、L0 の GateExecutor が gate.yaml から実行するゲート
（script・Skill・人間待ち）だけが L4 を実行する。L0 も L3 も L4 の script・Skill を import しない。
`advance-after` の段が `{complete: "ok", note}` を返せるのは、今の emit / wait がゲートの unit で、理由の `note` があるときだけである
（ゲート自身が「該当なし」と決めたものを記録する。段が勝手に完了させる入口にはしない）。


状態ストア・ログ・JSON 出力の項目名（`event` / `::event` / `events` / `target_event` / `event_id` など）は保存・受渡しの形式であり、アクションへの改名後も変えない。

L0 は設定で渡された名前の業務上の意味を解釈しない。Spec の status、feature の順序、承認条件、差戻しの影響範囲は L3 の規則確認 script が扱う。L4 の指摘を解釈して自動修正・承認する機能を L0 に加えない。

## 2. 実行前提

Python 3 を使用する。子 Python は親の sys.executable で起動する。PyYAML は任意で、無ければ同梱の YAML サブセットパーサを使う。原本に正式な対応 OS / 最低 Python 版の定義はなく、今回の開発環境から正式サポート範囲を追加しない。

設定は --config、案件ルートは --root、状態は --state で指定できる。同一案件を操作するランナーとホストは直列に実行する。設定に参照された script / Skill / agent が無い場合は停止する（ファイルがあることだけを確かめ、中身は読まない）。

## 3. 呼出しと外部実行

**host agent の入口は規則の層（L3）の `scripts/aidd_entry.py` だけである。** 入口は L0 の CommandResolver（`bin/command_resolver.py`）で
コマンドと呼出し先を解決し、advance / submit / respond を L0 の host に L3 の規則を渡して実行する。status / report / redo / migrate-flow は
`aidd.py`、それ以外は L3 の操作へ渡す。`bin/command_resolver.py` の CLI は規則の要らない操作（validate / doctor / status / report / redo /
migrate-flow）だけを受ける。`--call` / `--action` はそのコマンドの呼出し先に限る。案件ルート・状態・定義の置き場はファイルの場所に固定される。以下の `aidd.py` は内部の CLI である（試験と、定義・状態の直接の確認に使う）。

```text
python .claude/skills/aidd-common/bin/command_resolver.py /aidd-requirements advance --call requirements-plan
python .claude/skills/aidd-common/bin/command_resolver.py /aidd-requirements status --call requirements-plan --json
python .claude/skills/aidd-common/bin/command_resolver.py validate --json
python .claude/skills/aidd-common/bin/command_resolver.py doctor [--runtime-only]
```

```text
python .claude/skills/aidd-common/bin/aidd.py --root <案件> validate --json
python .claude/skills/aidd-common/bin/aidd.py --root <案件> call <設定中の名前> --json
python .claude/skills/aidd-common/bin/aidd.py --root <案件> report --call <同じ名前> --dispatch-id <返されたdispatch.id> --result ok --json
python .claude/skills/aidd-common/bin/aidd.py --root <案件> redo --call <名前> --action <アクション> --item <対象> --json
python .claude/skills/aidd-common/bin/aidd.py --root <案件> migrate-flow --from <旧 flow> --to <新 flow> --json
```

| 戻り値 | ホストの処理 |
|---|---|
| 0 | 当該 call または report の完了。次に呼ぶ工程はフロー側の定義に従う |
| 20 / emit | 返された unit を実行して結果を report する |
| 10 / wait | 提示内容を人間へ伝え、実際の回答を得る。無回答を成功として報告しない |
| 1 / fail | 理由を提示して停止する |

`call` の emit/wait は `dispatch`（id、call、unit、event、item、status、設定ハッシュ、detail）を返す。
status の pending は次の候補、dispatch は実際に発行済みの依頼で、未発行なら null。
report は発行された dispatch.id が必須。同じ ID・call/item・result/note/detail の再送は
保存済み結果を返し、次の unit を完了扱いにしない。内容の変更や未発行・古い ID は拒否する。
redo は未報告の依頼を失効させる。報告済み ID の再送は履歴の読出しであり、redo 後の実行を進めない。

L0 とホストアダプタは公開 `lib/aidd_lock.py` で同じ state へのコマンドを直列化する。
処理中の別ホストからの操作は拒否し、OS のロックはプロセス終了時に解放される。
ホストから同期呼出しした子コマンドは親のロックを引き継ぐ。同一案件で複数ホストを
同時運転しない。中断後は子プロセスの終了も確認してから再開する。
L0 は review や業務承認の意味を解釈せず、固有の段階ガードはフロー側が実装する。
main_flow の通常ホストは references/host-protocol.md の L3 入口を使用する。

`--item` は対象を識別する不透明な文字列。同じ呼出しの call/status/report/redo で同じ値を使う。L0 はその集合や順序を決めない。

| 実行属性 | 実行仲介 |
|---|---|
| type: command | 設定された command を実行する |
| type: script | Python script を実行し、終了コードで結果を決める |
| type: script, requiresHuman: true | target の script を実行して人間待ちにする。target は必須。回答を生成しない |
| type: skill | target の SKILL.md をホストが読み、指定された unit を実行する |
| type: skill, isAgent: true | ホストが check-runner を別コンテキストで起動し、target の合成 Skill を渡す |

検査 agent の実行仲介はこの L0 プロトコルに集約する。L3 の規則 script や生成 Skill は検査 agent を直接起動しない。現行の check-runner という名前は実行仲介の接続点であり、L0 に検査観点を持たせるものではない。

アクション・ゲートの定義は適用の条件（`when`）を持たない（書けば読込み時にエラー）。修正が無いときは、入口 Skill の手順が
修正アクションを呼ばない。ゲートの中で判断が要るものはゲート script 自身が行う。

`target_action` の各要素は任意で `target_review: [<パス>, ...]` を持てる。案件ルートからの相対パスで、ファイル・
`<dir>/`・`<dir>/**`、単独の `**` を書ける。空の配列・絶対パス・`..`・末尾以外のワイルドカード・重複は読込み時にエラー。
L0 は `{item}` などを展開した値を dispatch の `targetReview` と環境変数 `AIDD_TARGET_REVIEW`（JSON、省略時は空）に載せ、
全ゲートの宣言を `AIDD_GATE_TARGETS` と `validate` の `target_review` に出す。どのファイルが出力か・省略時に何を対象にするかは
呼出し側の規則が決め、L0 は解釈しない。

`calls` は合成 Skill が順に読む Skill 名。L0 は参照実体があることだけを確認する（`## 手順` 内の参照順序との一致は L4 の `scripts/check_calls.py` が確認する）。品質上その観点が適切かは判断しない。ホストは実際に実行できた結果を report する。通常 script / command の成功をホストが report で代筆することはできない。

検査 Skill の report ok は検査の実行完了だけを示す。指摘判断・人間承認が揃ったかは、その後の規則確認アクションの結果で制御する。ホストは工程ごとの別ループを追加せず、emit/wait/report の同じ手順に戻る。

## 4. 状態と再実行

L0 の書込み所有欄は events / trace / engine_schema / engine_reports / host_operations / current.call / current.return_to_call / current.pending。その他の案件欄は保存直前に再読込して保持する。ランナー所有欄が外部で変わった場合は停止する。未知の案件欄を削除しない。

redo は対象 unit の無効化を履歴末尾へ追記する。過去の実行記録を削除しない。どこまで無効化するかは呼出し側の規則が指定し、L0 は対象を実行履歴へ反映する。実行中の script が別のランナーを再帰起動して同じ状態を書き換えない。

migrate-flow は flow を分けた・改名したときに、旧 flow 名の実行記録を新 flow 名へ写す。`--to` の flow が直接持つアクションについて、キーが `<旧>/<アクション>[` で始まる各 unit の最後の記録を、新しいキーで履歴末尾へ追記する。旧記録は残す。最後の記録が無効化済みの unit は写さない。移行先に同じ結果があれば何もせず、別の結果があれば停止する。発行済みの emit/wait がある間は停止する。current.call / current.return_to_call が旧 flow 名を指し、旧 flow 名が設定に無ければ新 flow 名へ置き換える。どの flow をどこへ写すかは呼出し側の移行手順が決める。

旧 agent / approval 設定は新方式へ明示的に移行する。旧状態の成功印を新構成に自動流用しない。main_flow の移行手順は配布の references/migration.md を参照する。

## 5. main_flow での利用

フロー固有の入力・記録・人間判断・承認・差戻しは配布の references/runtime-boundary.md と L3 のホスト手順に従う。L0 はこれらを import しない。設定された script をプロセスとして呼び、終了コードと結果を受け取る。

## 6. 保存とログの範囲

状態保存の原子的な置換は、複数ランナーの同時実行を保証するものではない。呼出しを直列化する。ログの業務情報は呼出し側が detail として渡す。以下のログ項目の例は、進行判断の規則を L0 に移すものではない。

## 7. ログ

**全ログが同じ 7 フィールドである。** 種別は「どの ID まで埋まっているか」で決まり、
ログの型は 1 つしかない。空のフィールドはキーごと省略する。

> **拡張子は `.log` だが、中身は JSONL（1 行 1 JSON）である。**
> ファイル名から中身が読めないため、ここに明記しておく。`jq` などでそのまま読める。

| フィールド | 内容 |
|---|---|
| `timestamp` | 発生時刻（ISO 8601）。システムが打つ |
| `level` | `info` / `warn` / `error` / `debug`。**重大度であり階層ではない** |
| `orchestrator_id` | トレース ID。`call` 1 回につき 1 つ発行し、**全ログが必ず持つ** |
| `phase_id` | flow 単位（`call` が束ねた flow ごと） |
| `sub_phase_id` | アクション 1 件（その アクション本体と、そこに差さったゲート）。**`--item` を伴えば feature 1 件と同じ意味になる** |
| `event_id` | 単発の実行単位（アクション本体 1 回、またはゲート 1 本） |
| `detail` | 実行内容。先頭語は **開始 / 終了 / 失敗** の 3 語に固定 |

4 つの ID はすべて ULID（26 桁・時刻順にソートできる）。**発行するのはその ID を書く層**であり、
上位の ID は渡されたものをそのまま持ち回る。**下の層が上の ID を書き足すことはない。**
親子を辿らせず祖先をすべて並べて持つため、1 行だけで所属が確定し、集計に結合が要らない。
**短縮するなら末尾 8 桁**にする。先頭 10 桁は時刻部のため、同じミリ秒に発行した ID は
先頭が一致して衝突する。保存と突合には全 26 桁を使う。

`修正主体`（AI 再生成か人手か）だけは、`detail` が自由文で機械集計できないため
**専用のキー `fix_by` としても持つ**。

### 7.1 detail の書き方

先頭語は **開始 / 終了 / 失敗** の 3 語に固定する。以降は `キー=値` を半角空白区切りで並べ、自由文は最後に置く。

| 書く層 | タイミング | テンプレート |
|---|---|---|
| Workflow Engine | `call` 受理の直後 | `開始 call(<名前>) model=<model> version=<version>` |
| Workflow Engine | 呼び出しの終了 | `終了 call(<名前>) 結果=<完了\|人間待ち\|中断> 所要=<m:s>` |
| Workflow Engine | 呼び出しの失敗 | `失敗 call(<名前>) 理由=<短文>` |
| Workflow Engine | flow を渡す直前 | `開始 <flow> アクション=<n>` |
| Workflow Engine | 結果を受け取った時点 | `終了 <flow> 結果=<成功\|失敗\|人間待ち> 残り=<n>` |
| FlowExecutor | アクションに入る時 | `開始 <action> type=<type> item=<feature 名\|空> ゲート=<start 本数>+<end 本数>` |
| FlowExecutor | そのアクションが確定した時点 | `終了 <action> 結果=<…> status=<…> 指摘=<n> 回数=<n>` |
| ActionExecutor | 実行の直前 | `開始 <target> type=<type> 契機=<event\|start\|end>` |
| ActionExecutor | 呼び出しが返った時点 | `終了 <target> 結果=<成功\|失敗\|人間待ち> <type 固有キー>` |
| ActionExecutor | 例外で落ちた時点 | `失敗 <target> 理由=<短文>` |

`契機` は必ず書く。無いとアクション本体の実行とゲートが同じ形で並び、後から区別できない。

| `type` / フラグ | `終了` に付けるキー |
|---|---|
| `skill`（`isAgent: false`） / `command` | `出力=<path>` |
| `skill`（`isAgent: true`） | `指摘=<n> 回数=<n>` |
| `script`（`requiresHuman: false`） | `終了コード=<n>` |
| `script`（`requiresHuman: true`） | `判断=<…> 判断者=<名前> 修正主体=<AI\|人手> 理由=<短文>` |

- **`skill`（`isAgent: false`）/ `command` の `終了` はほぼ常に `結果=成功`** になる。LLM の
  ターンが返っても成果物の正しさは判定できない。合否は差さった `isAgent: true` のゲートと
  `requiresHuman: true` のゲートが決める。`失敗` になるのは呼び出し自体が例外で落ちたときだけである。
- **`requiresHuman: true` の `script` の `終了` は 2 回出る。** 提示した時点で `結果=人間待ち`、回答を受け取った時点
  （`report`）でもう 1 行。**2 行目は別の `event_id` を採番する**（同じ ID で 2 回 `終了` が出ると
  所要時間の算出が壊れる）。
- **リトライは 1 回ごとに `開始` と `終了` を出す。`event_id` も毎回別。** まとめると回数が消え、
  「リトライして成功した」を warn で拾えなくなる。
- **途中で失敗しても、そのアクションの `終了` 行は必ず出す**（終了の無い開始＝中断 の判定を保つため）。

### 7.2 level の使い分け

| `level` | 判断基準 |
|---|---|
| `info` | 予定どおり進んだ（開始と終了・指摘 0 件でのゲート通過・`draft` → `review`・承認・**承認待ちでの停止**） |
| `warn` | 止まっていないが人が見るべき（**① / ② で指摘を検出**・判断が `差戻し` / `対応せず進める` / `未対応`・同一 feature のゲートが 2 回目以降・リトライして成功した・上流へ戻った） |
| `error` | **実行が止まった**（Refuse・作成 Skill / サブエージェントの実行失敗・ゲート記録の解析失敗・ログ書き込み自体の失敗） |
| `debug` | 調査用。**既定では出さない**（`--log-level debug` で有効） |

- **① / ② の指摘は `warn` とする。** ① / ② は合否を出さずフローも止めないため、`error` にすると
  停止と区別できなくなる。**`error` の件数＝止まった回数**という関係を崩さない。承認待ちも同じ理由で `info`。
- `終了` 行を `warn` にするのは、`結果=失敗` / `指摘` が 1 件以上 / `回数` が 2 以上 /
  `判断` が `差戻し`・`対応せず進める`・`未対応` のいずれかのときである。
- **`error` にするのは `失敗` 行だけ**である。

### 7.3 案件側の値をログへ渡す

出力パスや指摘件数は**案件側の知識**であり、ランナーは組み立てない。次の 2 経路で渡す。

| 経路 | 使うもの |
|---|---|
| `scripts/*.py` | 標準出力に `AIDD-LOG: キー=値 …` を 1 行出す（`execution_context.log_keys()`）。ランナーは中身を解釈しない |
| `type: skill`（`isAgent` の値に関わらず）／ `requiresHuman: true` の `script` | `report --detail "キー=値 …"`（§3） |

### 7.4 設定ファイル `.aidd/logging.yaml`

出力先と閾値は**設定ファイルが持つ**（`Templates/Flow/logging.yaml` が構造の正）。

```yaml
# .aidd/logging.yaml
output:
  dir: .aidd/logs
  filename: "{trace_id}.log"
  level: info
```

| キー | 内容 |
|---|---|
| `dir` | 案件ルートからの**相対パス**。**絶対パスは使わない**（案件を移すと壊れる）。無ければ作り、**作れなければ実行を止める** |
| `filename` | 使える変数は `{trace_id}` / `{date}` / `{command}` の **3 つだけ**。`{trace_id}` は 1 実行 1 ファイルになり、探すのに grep が要らない。`{date}` は並行実行で行が混ざる |
| `level` | **閾値であり配列ではない。** 配列にすると warn だけ出して error を落とす設定が書けてしまう |

**設定の誤りは実行前に止める。** 絶対パス・配列の `level`・未知の変数・未知のキーは、
いずれもエラーにしてフローを進めない。ファイルが無い場合は上の既定値で動く。

| その他 | 既定 | 変え方 |
|---|---|---|
| 設定ファイルの場所 | `.aidd/logging.yaml` | `--log-config <path>` / `AIDD_LOG_CONFIG` |
| 閾値の一時的な上書き | `output.level` | `--log-level debug\|info\|warn\|error` / `AIDD_LOG_LEVEL` |
| `model=` | 空 | `AIDD_MODEL` |
| `version=` | 状態ストアの `release` | `AIDD_VERSION` |

`status` / `redo` / `validate` は実行しないためログを書かない。
**ログ書き込み自体の失敗は握りつぶさず** stderr に出す。
