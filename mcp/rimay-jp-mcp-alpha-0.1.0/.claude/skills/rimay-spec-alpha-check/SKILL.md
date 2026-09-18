---
name: rimay-spec-alpha-check
description: Specテンプレートの指定セクションで日本語要件文を追加・変更・壁打ちするとき、変更行または対話中の1要件をRimay-JPの日本語品質検査と固定Repository Grammar候補検査へ通す軽量なalpha工程。未登録語・未登録動詞は重複を抑えて警告し、対話と編集を継続する。正式Canonical化、manifest管理、承認処理には使わない。
---

# Rimay Spec Alpha Check & Kabeuchi

Specテンプレートの変更行検査と、日本語要件1件の壁打ちを行う。このSkillは単独で
動作し、他のSkillやサブエージェントを起動しない。

## 前提と境界

- 必須の外部依存は、接続済みの`rimay-jp` MCPだけとする。
- 使用するMCPツールは次の3つに限定する。
  - `get_repository_parser_capabilities`
  - `get_repository_rule_details`
  - `inspect_japanese_requirement_alpha`
- 固定Repository Grammar、辞書、mapping、Canonical、manifestを変更しない。
- `rimay: managed`マーカーの追加、正式Canonicalへの昇格、承認、Store保存を行わない。
- Parser受理を、日本語との意味同値、製品対応済み、review_ready、approvedと扱わない。

MCPまたは固定Grammarを利用できない場合は、検査を通過したとは表示しない。
依頼済みのSpec編集は維持し、`CHECK_NOT_RUN`と不足している前提を報告する。

## 利用形態

依頼内容から次の形態を選ぶ。併用する場合は、変更した各要件を壁打ち対象にする。

- **Spec編集検査**: Specファイルの指定セクションで、今回追加・変更した要件を一括検査する。
- **壁打ち**: 貼り付けられた日本語要件、またはSpec内で指定された1要件を対話で明確化する。

Spec編集では、セクション省略時に`Requirements`または`Requirements（要件）`を対象とする。
今回Claudeが追加・本文変更した番号付き要件文だけを検査し、未変更行、削除行、見出し、
User Story、説明文、HTMLコメント、NFR表は除外する。変更履歴が会話から確定できない場合だけ
差分を読み、対象セクション内の追加・変更行を抽出する。文書全体の番号付きリストを
無条件に対象にしない。

## セッション状態

MCPはstatelessなので、Claude側で要件ごとの状態を保持する。managed IDがあればそれを使い、
なければ現在のセッション内で安定した`ALPHA-REQ-<n>`を割り当てる。状態は会話コンテキスト、
または利用可能なhost scratchpadに置き、リポジトリへ保存しない。

各要件について次を保持する。

- 現在の日本語意図と、直前に検査した日本語文
- `japanese_analysis.input_signature`
- 現在の完全なRimay候補
- `fixed_grammar_evaluation.input_signature`（評価済みの場合）
- 現在有効な警告fingerprint
- 利用者が回答済みの確認事項と、未解決の質問

警告は`japanese_quality.findings`と
`japanese_analysis.native_analysis.findings`の両方から収集する。fingerprintは
`normalized_issue_code`または`code`、先頭の`target_paths`または`path`、
`source_span.text`または`evidence.surface_form`、`evidence.expected_types`の組で作る。

- 同じ日本語・候補・signatureなら、明示的な再検査依頼がない限り結果を再利用する。
- 初出警告は詳細表示する。同じfingerprintの継続警告は再掲せず、継続件数と対象要件だけ示す。
- 解消した警告は一度だけ解消済みと示す。解消後の再発、path・期待型・表層の変化は再表示する。
- `JP-OMISSION`、`syntax_rejected`、linking／projection失敗は省略しない。
- MCP再接続、Grammar／profile変更、またはセッション終了時にcacheを無効化する。

この重複抑制は表示制御だけであり、findingのblocking状態や正式工程の判定を変更しない。

## 検査ループ

1. セッションで初めて検査するとき、`get_repository_parser_capabilities`を一度呼び、
   固定Grammarが利用可能か確認する。返されたrule数やAction数を固定値で決めつけない。
2. 初回と日本語意図の変更時は、`inspect_japanese_requirement_alpha`を
   `rimay_candidate`なしで呼び、決定的bridgeを優先する。
3. `candidate_required`の場合だけ、`candidate_guidance.grammar_queries`に必要な
   literalまたはRule IDを`get_repository_rule_details`で照会する。Grammar全文は要求しない。
4. 照会結果から完全なRepository Rimay候補を1件生成し、同じ日本語要件文とともに
   `inspect_japanese_requirement_alpha`へ再度渡す。候補を変更したら必ず全文を再検査する。
5. Parser起因の候補修正は1要件・1ラウンドにつき最大2回とする。収束しない場合は
   `UNRESOLVED`として、意味上必要な確認だけを利用者へ尋ねる。
6. 未採用Actionを似た別Actionへ丸めたり、辞書にない値を推測で置換したりしない。
   候補と日本語の意味対応はClaudeの推論として分け、不確かな対応は未解決にする。

ファイル書き込みのたびには実行せず、意味のまとまった編集単位または利用者回答の反映後に
再検査する。日本語意図が変わっていなければ、不足情報への回答だけを候補へ勝手に追加しない。

## 壁打ちの進め方

1. 日本語要件、Rimay-JP確認済み結果、Claudeによる意味理解、未解決点を分けて示す。
2. 未登録語・未登録動詞だけなら警告して対話を継続する。辞書登録やAction追加は行わない。
3. 主語・必須Role・modalityなどを推測できない場合は質問する。
4. 独立した不足は1ラウンド最大3問までまとめてよい。Action選択、AND／OR、Scope、Triggerなど
   後続構造を変える確認は1問ずつ尋ねる。部分回答を許し、未回答を推測しない。
5. 利用者回答で日本語意図を更新したら、変更点を示して検査ループを最初から回す。
6. `syntax_rejected`は生成したRimay候補の構文拒否であり、それだけを根拠に日本語要件を
   構文エラーと断定しない。候補を先に自己修正し、意味選択が必要な場合だけ質問する。
7. 利用者が検査または壁打ちだけを依頼した場合はSpecを書き換えない。追加・変更の依頼が
   ある場合だけ、確認済みの日本語表現を対象行へ反映する。

一つの要件に独立した主要求が複数ある場合はスメルとして報告する。分割案は提示できるが、
利用者の同意なく分割・意味変更しない。

## 結果の扱い

MCPレスポンスを変更せず、Skillの表示上だけ次の区分へ要約する。

- `PASS`: 固定Grammar候補が`checked`で、日本語側に報告対象がない。
- `PASS_WITH_WARNINGS`: 候補は検査済みで、スメル、`JP-LEXICAL`、
  `RIMAY-ACTION`などが残る。警告を表示して対話と編集を継続する。
- `UNRESOLVED`: `candidate_required`が解消しない、`syntax_rejected`、
  linking／projection失敗、`JP-OMISSION`、または意味対応が不確か。
- `CHECK_NOT_RUN`: MCPまたは固定Grammarを利用できず、検査結果がない。

未登録語・未登録動詞では、表層、finding code、path、期待型を可能な範囲で表示する。
正式工程ではblockingになり得ることを明記するが、このalpha工程を即停止しない。

## 利用者への報告

各ラウンドは次の順で簡潔に示す。

1. 現在の日本語意図
2. `PASS`／`PASS_WITH_WARNINGS`／`UNRESOLVED`／`CHECK_NOT_RUN`
3. Rimay候補
4. Rimay-JP確認済み: Parser status、Action Rule ID、linking、projection
5. 新規・継続・解消した警告
6. Claude推論: 日本語と候補の意味対応
7. 次の質問または次の一手

複数行を検査した場合は、最後に対象件数と各区分の件数を集計する。未変更行や対象外
セクションについて検査済みと主張しない。

## 手動起動例

- `/rimay-spec-alpha-check specs/example/requirements.md Requirements`
- `/rimay-spec-alpha-check 通知システムは監査ログを管理者に送信しなければならない。`

このSkillはalpha検査と壁打ちだけで完結する。正式Canonical化や承認まで必要になった場合は、
結果を自動昇格せず、利用者に別工程として明示的な開始を求める。
