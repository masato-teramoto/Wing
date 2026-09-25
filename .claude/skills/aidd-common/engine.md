# engine — L0 の実行プロトコル

L0 は設定されたイベントを実行し、実行履歴から再開点を選ぶ。main_flow 固有の進捗・差戻し・承認規則の管理原本は L3 に置く。配布では両者を同じ aidd-common に合成する。

## 1. 実行構造

Orchestrator が call と状態を管理し、Flow Executor がイベント順序を展開し、Event Executor が start ゲート → event → end ゲートを直列に処理する。ゲートも event と同じ Run を持つ。

L0 は設定で渡された名前の業務上の意味を解釈しない。Spec の status、feature の順序、承認条件、差戻しの影響範囲は L3 の規則確認 script が扱う。L4 の指摘を解釈して自動修正・承認する機能を L0 に加えない。

## 2. 実行前提

Python 3 を使用する。子 Python は親の sys.executable で起動する。PyYAML は任意で、無ければ同梱の YAML サブセットパーサを使う。原本に正式な対応 OS / 最低 Python 版の定義はなく、今回の開発環境から正式サポート範囲を追加しない。

設定は --config、案件ルートは --root、状態は --state で指定できる。同一案件を操作するランナーとホストは直列に実行する。設定に参照された script / Skill / agent が無い場合は停止する。

## 3. 呼出しと外部実行

```text
python .claude/skills/aidd-common/bin/aidd.py --root <案件> validate --json
python .claude/skills/aidd-common/bin/aidd.py --root <案件> call <設定中の名前> --json
python .claude/skills/aidd-common/bin/aidd.py --root <案件> report --call <同じ名前> --dispatch-id <返されたdispatch.id> --result ok --json
python .claude/skills/aidd-common/bin/aidd.py --root <案件> redo --call <名前> --event <イベント> --item <対象> --json
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

gates.yaml の `target_event` の各要素は任意で `when: <script>` を持てる。その差し口では gate の実行前に
条件 script を実行し、終了コード 0 なら gate を実行、11 なら省略して成功として記録する（detail とログに
「条件により省略」を残す）。それ以外・起動失敗・既定600秒のタイムアウトは失敗。
条件の実行は人間回答待ちではなく、requiresHuman のゲートでも時間制限を適用する。
省略の判断は呼出し側の規則 script が持ち、L0 は意味を解釈しない。
main_flow では `-revise` イベントの検査・人間レビュー等の gate に「人が修正を選んでいるときだけ適用」の条件を付ける。
イベント単位の SKIP は持たない（イベント本体は常に実行する）。

`calls` は合成 Skill が順に読む Skill 名。L0 は参照実体と `## 手順` 内の参照順序との一致を確認する。品質上その観点が適切かは判断しない。ホストは実際に実行できた結果を report する。通常 script / command の成功をホストが report で代筆することはできない。

検査 Skill の report ok は検査の実行完了だけを示す。指摘判断・人間承認が揃ったかは、その後の規則確認イベントの結果で制御する。ホストは工程ごとの別ループを追加せず、emit/wait/report の同じ手順に戻る。

## 4. 状態と再実行

L0 の書込み所有欄は events / trace / engine_schema / current.call / current.return_to_call / current.pending。その他の案件欄は保存直前に再読込して保持する。ランナー所有欄が外部で変わった場合は停止する。未知の案件欄を削除しない。

redo は対象 unit の無効化を履歴末尾へ追記する。過去の実行記録を削除しない。どこまで無効化するかは呼出し側の規則が指定し、L0 は対象を実行履歴へ反映する。実行中の script が別のランナーを再帰起動して同じ状態を書き換えない。

旧 agent / approval 設定は新方式へ明示的に移行する。旧状態の成功印を新構成に自動流用しない。main_flow の移行手順は配布の references/migration.md を参照する。

## 5. main_flow での利用

フロー固有の入力・記録・人間判断・承認・差戻しは配布の references/runtime-boundary.md と L3 のホスト手順に従う。これらは L0 の内部実装から import しない。設定された script をプロセスとして呼び、終了コードと結果を受け取る。

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
| `sub_phase_id` | event 1 件（その event 本体と、そこに差さったゲート）。**`--item` を伴えば feature 1 件と同じ意味になる** |
| `event_id` | 単発の実行単位（event 本体 1 回、またはゲート 1 本） |
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
| Orchestrator | `call` 受理の直後 | `開始 call(<名前>) model=<model> version=<version>` |
| Orchestrator | 呼び出しの終了 | `終了 call(<名前>) 結果=<完了\|人間待ち\|中断> 所要=<m:s>` |
| Orchestrator | 呼び出しの失敗 | `失敗 call(<名前>) 理由=<短文>` |
| Orchestrator | flow を渡す直前 | `開始 <flow> イベント=<n>` |
| Orchestrator | 結果を受け取った時点 | `終了 <flow> 結果=<成功\|失敗\|人間待ち> 残り=<n>` |
| Flow Executor | イベントに入る時 | `開始 <event> type=<type> item=<feature 名\|空> ゲート=<start 本数>+<end 本数>` |
| Flow Executor | そのイベントが確定した時点 | `終了 <event> 結果=<…> status=<…> 指摘=<n> 回数=<n>` |
| Event Executor | 実行の直前 | `開始 <target> type=<type> 契機=<event\|start\|end>` |
| Event Executor | 呼び出しが返った時点 | `終了 <target> 結果=<成功\|失敗\|人間待ち> <type 固有キー>` |
| Event Executor | 例外で落ちた時点 | `失敗 <target> 理由=<短文>` |

`契機` は必ず書く。無いとイベント本体の実行とゲートが同じ形で並び、後から区別できない。

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
- **途中で失敗しても、そのイベントの `終了` 行は必ず出す**（終了の無い開始＝中断 の判定を保つため）。

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
| `scripts/*.py` | 標準出力に `AIDD-LOG: キー=値 …` を 1 行出す（`aidd_paths.log_keys()`）。ランナーは中身を解釈しない |
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
