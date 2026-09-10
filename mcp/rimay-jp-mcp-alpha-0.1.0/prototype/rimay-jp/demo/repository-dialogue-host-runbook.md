# Repository Grammar 日本語alpha host runbook

## 1. デモの完成条件

このalphaでは、任意の日本語要求を対象にLLM hostが対話履歴・日本語意図・
Rimay候補を保持し、Rimay-JPは各候補をstatelessに再検証する。固定シナリオや
特定Actionへ対象を限定しない。実行中にGrammar、Normalizer、辞書、Canonical、
mapping、Validatorを更新しない。

Rimay-JPが確認するのは次の範囲である。

- 現行日本語Normalizerの候補とfinding
- 固定Repository Grammarによるfull matchとambiguity
- same-document linking
- Repository文書へのfact保持
- 現行14 mapping面のactive／residual
- 到達可能な場合だけ現行Canonical Schema／Validator

LLMが行う日本語との意味解釈、質問、修正文候補は推論であり、Rimay-JP確認済みと
分けて表示する。

## 2. 起動前確認

固定Grammarへの絶対パスをMCP processへ渡す。

```bash
export RIMAY_FIXED_GRAMMAR=/absolute/path/to/Dsl_rimay.xtext
python prototype/rimay-jp/adapters/mcp/smoke_test.py
python prototype/rimay-jp/scripts/run_repository_dialogue_replay.py
```

期待値はMCP 44 tools、Repository 178 rules／50 actions、Replay 4/4 PASSである。
Grammar source hashが固定値と違う場合、Rimay-JPは起動時にfail-closedにする。

## 3. LLM host system prompt

次をhostのsystem promptまたは同等の進行規則へ追加する。

```text
あなたは日本語要求の壁打ちを行う。対話状態はあなたが保持し、Rimay-JPを
statelessな検証器として使う。

1. 利用者とは日本語で対話する。
2. session開始時に get_repository_parser_capabilities を一度呼ぶ。
3. 初回と日本語意図を変更した時は inspect_japanese_requirement_alpha を
   rimay_candidateなしで呼ぶ。
4. native bridge候補があればalpha入口が固定Grammarで自動再検証する。
5. fallback時だけ、必要な範囲を get_repository_rule_details で照会し、
   LLM推論として完全なRepository Rimay候補を作る。Grammar全文は要求しない。
6. 候補を新規作成または修正したら、必ず全文をrimay_candidateとして
   inspect_japanese_requirement_alphaへ渡す。
7. Rimay-JP応答前にParser成功、link成功、Canonical成功を断定しない。
8. 表示では「Rimay-JP確認済み」と「LLM推論」を分ける。
9. parser acceptedを日本語意味同値、approved、製品対応済み、公式Xtext Parser同値と
   言い換えない。
10. toolが返すRule ID、assignment、mapping statusを改変しない。
11. 未採用Actionを現行product Actionへ丸めず、Repository residualのまま説明する。
12. 同一turnのParser再試行は最大2回、比較候補は最大2件とする。収束しなければ
    利用者へ質問する。
13. 独立した不足は最大3問までまとめてよい。Action選択、AND/OR、Scope、Triggerなど
    後続構造を変える質問は1問ずつ聞く。部分回答を許し、未回答を推測しない。
14. 意味を変える候補修正は、変更点を利用者へ明示する。
15. デモ中はRimay-JP資産を変更しない。改善用observationの採取は対話応答と分離する。
16. observationが必要な場合だけ build_repository_demo_observation を別に呼ぶ。
    defaultのredactedを使い、export失敗をParser応答の失敗へ変換しない。
```

## 4. turnの実行順

初回turn:

1. `inspect_japanese_requirement_alpha(detail="compact")`
2. `checked`なら一括応答内のスメル・Parser・Linking結果を表示する。
3. `candidate_required`ならfindingと`grammar_queries`を確認し、必要なliteral／Ruleだけ
   `get_repository_rule_details`で照会する。
4. LLM候補を最大2件作り、それぞれ全文をalpha入口の`rimay_candidate`へ渡す。
5. 日本語意図、候補、Rimay-JP確認済み、LLM推論、次の質問の順で表示する。

後続turn:

1. 利用者回答をhost上の日本語意図へ反映する。
2. 日本語意図が変わった場合はalpha入口を再実行する。
3. 現在のRimay候補を修正し、候補全文をalpha入口で再検証する。
4. 旧候補との差と意味変更を説明する。

Rimay-JP内へdraft、approval、会話履歴を書き込まない。

observation exportはturn応答を利用者へ返した後の任意処理とする。通常は`redacted`を
使い、raw日本語、Rimay候補、質問本文を保持しない。`synthetic`はreview後のfixture候補、
`restricted_raw`は明示同意・利用目的・アクセス主体・削除条件が揃った制限領域だけで
使用し、repository commitは禁止する。

## 5. 表示template

```text
現在の理解:
  <日本語意図。LLM推論>

Rimay候補:
  <候補全文>

Rimay-JP確認済み:
  - Parser: accepted/rejected/ambiguous
  - Action Rule: <exact IDs>
  - Linking: succeeded/failed
  - Repository: succeeded/not_run
  - Canonical: valid/partial/unavailable/not_run

LLM推論:
  - <日本語との意味対応、残余assignmentの読み方>

確認:
  1. <依存関係に従った質問。不要なら省略>
```

## 6. Replayとliveの境界

`repository-dialogue-replay.yaml`はLLMが作った候補と日本語表示だけを記録する。
Parser応答は保存済み結果を再生せず、毎回現在のRimay-JPで再計算する。このためReplayは
host進行とtool接続の回帰例に使えるが、alphaの対応範囲をこの4ケースへ限定する
ものではなく、LLMモデル自体の品質評価でもない。

Replayの4ケース:

- TriggerなしSEND: Normalizer → bridge → SEND_11_1_1 → Canonical valid
- SEND-001: Trigger／property boundaryを保持してfallback
- Migrate: DS_Migrateを50 Action分岐から選びRepository保持、Canonical partial
- Calculate: CREATE_26_4とDS_CALCULATEの両受理候補を利用者へ意味確認

## 7. 既知の非claim

- `fixed_repository_grammar_recognizer`は公式生成Xtext Parserとの同値をclaimしない。
- cross-resource linkingとXtext validatorは未実行である。
- `semantic_alignment_with_japanese`はRimay-JPでは検査しない。
- Canonical partialでも、Repository factが保持されていれば壁打ちは継続できる。
- デモ中に集めたobservationは、別工程でレビュー後に改善へ使う。
