# AIDD main_flow — Claude Code 実行環境

このフォルダをそのまま Claude Code で開き、RFP から要求整理・タスク文書作成・実装
（Phase 1–8）を実行できます。このフォルダのほかに必要なリポジトリはありません。

## 必要な環境

- Claude Code の利用可能なアカウントと通信環境。認証情報はこの配布物に含みません。
- Python **3.9 以上**。Python パッケージの追加インストール、Node.js、MCP サーバーは
  AIDD ランナーの実行に不要です。PyYAML がなければ同梱パーサを使用します。
- このフォルダへの読取り・書込み権限。
- 実行環境は Claude Code。Cursor は `.claude/` の Skill・agent を読むが、検査役（check-runner）を別コンテキストで
  起動することと Python の実行が必要で、この配布では動作を確認していない。

ランナーと配布資材は macOS / Python 3.9.6 と Windows / Python 3.12.10 で確認しています。
Claude Code CLI の確認記録は macOS / 2.1.211 です。Windows の確認では CLI を使わず、
Python の実行資材・配布・初回の実行依頼までを検証しています。
doctor は資材・Python 構文・L0 設定・RFP・CLI の有無を確認します。
ログイン、Skill の実セッションでの読込み、LLM の生成・意味検査の品質は doctor の確認範囲外です。
`--runtime-only` は CLI の確認も省略します。Windows / Linux の実ホスト受入は別途必要です。

Claude Code が未導入の場合は [公式セットアップ](https://code.claude.com/docs/en/setup) を参照してください。
プロジェクトの [CLAUDE.md](CLAUDE.md)、[Skills](https://code.claude.com/docs/en/skills)、
[カスタム agent](https://code.claude.com/docs/en/sub-agents) の標準的な配置を使います。
専用プラグインや権限確認を無効にする設定は必要ありません。

## 最初の実行

1. **この README と CLAUDE.md があるフォルダ**を Claude Code の作業フォルダにします。
   コピーするときは `.claude` と `.aidd` を含めたフォルダ全体をコピーしてください。
2. 案件の RFP（要求書）を **`.aidd/rfp/`** に置きます。この配布では空です（詳しくは[要求の入力](#要求の入力)）。
3. ターミナルで環境を確認します（macOS / Linux）。

   ```sh
   python3 -X utf8 -B .claude/skills/aidd-common/scripts/aidd_entry.py doctor
   claude
   ```

   Windows は `python --version` で Python 3.9 以上が表示されることを確認し、
   `python3` を `python` に置き換えます。`python` が使えない場合は
   `py -3 --version` を確認し、動作した場合だけ `py -3` を使ってください。
   `py -3` が「No installed Python found!」になる環境でも、`python` で起動できる場合があります。
   VS Code の Claude Code 拡張からこのフォルダを開く場合、CLI が未導入なら
   `python3 -X utf8 -B .claude/skills/aidd-common/scripts/aidd_entry.py doctor --runtime-only` で実行資材だけを確認できます。
4. Claude Code が求めるログインと、このフォルダの信頼確認を済ませます。
5. Claude Code の入力欄に **`/aidd-requirements-init`** を入力します。
6. 質問・検査結果・承認依頼に回答します。Phase 1–3 の完了後、以下の順に進みます。

| 入力するコマンド | 作成・確認する内容 |
|---|---|
| `/aidd-requirements-init` | 要求一覧、steering、feature 一覧（Phase 1–3） |
| `/aidd-requirements` | feature 別 requirements と横断確認（Phase 4） |
| `/aidd-design` | feature 別 design、横断確認、統合 docs（Phase 5–6） |
| `/aidd-tasks` | feature 別 tasks と全体確認・承認（Phase 7） |
| `/aidd-implement <feature> [1,2,...]` | タスク1件ずつ実装し、全体検査とfeature単位の人間承認（Phase 8）。全 feature の実装承認の後に、全体結合確認と実コードの横断確認 |
| `/aidd-mode-switch` | 全件方式から Feature 方式への切替（1 回限り。確認表示を見てから確定） |

Phase 8の開始前に、実在するテスト・検査コマンドとBoundaryに基づく編集範囲を
`.aidd/implementation/config/<feature>.json` に設定します（基本的に AI が設定します。不足があれば対話で確認します）。
形式と再開・修正手順は [.claude/skills/aidd-common/references/implementation/contract.md](.claude/skills/aidd-common/references/implementation/contract.md)。
必要な開発ツール・言語ランタイムは、案件に合わせて AI が準備タスクとして導入します。未設定の検査は承認できません。

最終検査の可読レポートは、別の`.aidd/implementation/reporting/<feature>.json`で設定します（基本的に AI が設定します）。
[レポート契約](.claude/skills/aidd-common/references/implementation/reporting.md)に従い、
AI が OSSのテスト結果・coverageと仕様説明を用意します。タスクの分割やcheck_idsは変更せず、
スイート／モジュール単位で出力を追加します。選択した静的解析の結果も別ファイルで含められます。

実行を中断した後は同じフォルダで同じ入口コマンドを使います。
途中の状態を初期化したり、完了済みの文書を手動で削除したりする必要はありません。
生成後の質問・指摘・承認には実際の回答が必要です。テスト題材でも自動承認は行いません。
通常の Claude Code のファイル／コマンド実行権限確認と、AIDD の業務承認は別です。

必要な検査がすべて完了するまで成果物を承認できません。形式不備で意味検査から外した節がある場合、
指摘を「対応せず進める」としても承認は止まります。修正して再検査を行い、必要な検査を揃えて
から承認します（形式の指摘を人が「指摘の誤り」と判断した場合は止まりません）。
過去版の検査・承認履歴がある案件は、同梱の移行手順に従って診断してください。

### 進め方の方式（alpha3.2）

最初の `/aidd-requirements` の計画停止点で、進め方を選びます。

- **全件方式**：全 feature の requirements を作ってから design へ、と工程ごとに全件を進めます（alpha3.1 までと同じ）。
- **Feature 方式**：1 feature ずつ選んで requirements → design → docs → tasks → 実装まで進めます。
  各工程の計画停止点で対象の feature（`select-scope`）を確かめます。共通機能（種別 Platform）の feature の番では、
  利用側と合わせた横断確認を行います。Phase 8 にも計画停止点 `implement-plan[<feature>]` があり、
  対象タスク・検証計画・停止回数・依存先との変更範囲の重なりを確かめてから実装に入ります。
- 全件方式で始めた案件は、Phase 4 以降で 1 回だけ `/aidd-mode-switch` で Feature 方式へ切り替えられます（戻せません）。

どちらの方式でも、全 feature の実装承認の後に次の 2 つを通すまで Phase 8 は完了になりません
（[統合確認の参照](.claude/skills/aidd-common/references/implementation/integration.md)）。

- **全体結合確認**：案件の検証計画 `.aidd/implementation/config/_project.json` の build と smoke（起動→共通機能を通る 1 経路→停止）を実行します。
  smoke の 1 経路を実行する wrapper は、tasks の計画停止点で選ぶ owner feature の「結合確認タスク」で作ります。
- **実コードの横断確認**（`implement-cross-gate`）：feature をまたいだ依存境界・要求の実装網羅・重複などを検査し、
  ACE で案件全体のコードを静的レビューした結果と合わせて 1 回で承認します。

### 指摘への判断（alpha3.1）

検査の指摘は、種類から決まる重大度で分けて示します。人が判断するのは **重大**（業務の欠落・矛盾、1 件ずつ）と
**要判断**（業務のあいまい・不足、似たものを束にして）だけです。

- **軽微**（工程・文書の分担・文書間の参照・出典・書式）は system が「修正」と判断し、修正の回で AI が修正案のとおり直します。レビューでは「見なくてよいもの」に一覧で示します。
- 人が確定した回答・工程の境界・同じ工程で「今後も同じ扱い」とした却下に当たる指摘は、出典を付けて除外します（除外も一覧で見られます）。
- 前回の検査から変わっていない節の判断は引き継ぎ、修正した節で同じ指摘が出なくなったものは自動で解消を記録します。
- 判断・修正・承認は選択肢から選んで答えます（Claude Code の選択式の質問）。選択肢に無い答えは「その他」で入力できます。
- alpha3 以前の版で検査した案件を途中から切り替えた場合、旧形式の未判断の指摘は「切り替え前の指摘」として 1 つにまとめて示します。
  「再評価する」を選ぶと、AI が新しい決まりで見直し、残った指摘だけを判断します。

## 要求の入力

入力先は **`.aidd/rfp/`** です。この配布では空なので、`/aidd-requirements-init` の前に
案件の RFP（要求書）を置いてください。`.aidd/rfp/` にあるファイルはすべて要求入力になります。
成果物・進捗・検査・承認は未作成なので、そのまま最初から始められます。

案件ごとに新しいコピーを用意してください。
実行済みの環境で RFP を差し替えると入力変更検出と再承認の対象になり、初回実行には戻りません。
最初からやり直すときは、このフォルダを別の場所へコピーし直して始めます。

## 配置されるファイル

```text
CLAUDE.md                 Claude Code への開始手順とホストの責務
README.md                 この開始ガイド
.claude/skills/           入口、生成・修正・検査、L0/L3/L4 の実行資材（CLI 入口は aidd-common/scripts/aidd_entry.py）
.claude/agents/           check-runner（検査用の別コンテキスト）
Templates/                成果物・状態・記録のひな型
.aidd/logging.yaml        ログの出力設定
.aidd/rfp/                要求書の入力先
.main-flow-assets.json    配布資材と管理原本の対応表
.gitignore                ローカル設定・キャッシュ等の除外
```

開発用のテスト・モック・報告書・作業ログ・Git 履歴・依存ライブラリのキャッシュは含みません。
実行すると `.aidd/` に要求一覧・feature 一覧・進捗・検査記録・ログ、`steering/` に方針、
`specs/` に feature 別文書、`docs/` に統合文書が生成されます。
Phase 8 では、承認済みタスクごとの実コード・テストが案件内に作られ、実装の設定・検査記録・レポートが
`.aidd/implementation/` に残ります。
記録は監査と再開に必要なので、実行開始後は保存してください。

## 問題が起きたとき

### Windowsのパス長エラー・案件フォルダの移動

本対応を導入済みのα版では、進捗を含む案件フォルダ全体を短い場所へ移して継続できます。
検査と子プロセスを停止してバックアップし、`.aidd`・`.claude`を含めて、例えば `C:\w\project`
へ移動します。移動先を開き直して同じ入口コマンドを実行してください。実行資材を変えず、
配置場所だけを変える場合は承認を引き継げます。元のコピーと同時には実行しないでください。

旧版で開始した案件は、コード・成果物・履歴を保存したコピーで、最新版の配布一式への更新を優先して検討します。
11ファイルだけの部分更新は必須ではありません。旧構成の未完了操作がある場合は更新後のrebaseが拒否されるため、
旧版で完結させるか、停止したコピーで復旧方法を診断します。更新できた場合も、Phase 8の
`implement-rebase` と必要な再検証・再承認を行います。旧実行と完了情報は履歴に残ります。
完成済みコードを故意に壊してREDを作らず、正規手順が成立しない場合は停止してください。
[既存案件の復旧手順](.claude/skills/aidd-common/references/workspace-recovery.md)で一式更新の条件と操作順を確認してください。

旧版の失敗で「verification may still be running」が残る場合は、Windowsのターミナルで
案件ルートから次を実行します。

```powershell
python -B .claude/skills/aidd-common/scripts/aidd_entry.py recover-checks
# 表示された検査と子プロセスがすべて停止していることを確認した後だけ実行
python -B .claude/skills/aidd-common/scripts/aidd_entry.py recover-checks --processes-stopped
```

処理中の記録を`.aidd/recovery/`へ退避して再試行を許可します。ログと既存の完了証跡は保持します。
検査コマンドが実行済みなら、再試行前に部分導入や外部への更新の状態も確認してください。
長いパス設定を有効化する必要はありませんが、feature名・check ID・レポート階層も短くしてください。
コマンド内の絶対パスや仮想環境は別途確認が必要です。

α版の緩和は配置場所の照合に限ります。実行ID・回答内容・ファイルのハッシュは照合を続けます。
案件全体のコピーも同じ案件として扱う制約があります。詳細は[実装契約](.claude/skills/aidd-common/references/implementation/contract.md#α版の配置場所変更)。

### その他

- コマンドが見えない: `.claude/skills/` があるフォルダで Claude Code を再起動し、
  `/aidd-requirements-init` を確認してください。`--safe-mode` ではプロジェクト資材が読み込まれません。
  個人設定・組織設定に同名 Skill がある場合は、実際に読み込まれたファイルを確認してください。
- check-runner が使えない: `.claude/agents/check-runner.md` を確認してセッションを再起動します。
- doctor が失敗: JSON の `ok: false` と `detail` を確認します。RFP なしなら配置して再実行します。
- workflow の終了コードは0/1で、次の状態は `result.status` にあります。
  L0 直接 CLI の `20` はホストへの実行依頼、`10` は人間待ちです。
- 検査途中の承認は拒否されます。ホストは `advance / submit / respond` を使い、
  実際の review 待ちで回答します。応答が不明なら保存済みの同一操作ID・payloadを再送します。
- 続きの工程へ進めない: [ホスト手順](.claude/skills/aidd-common/references/host-protocol.md) に従い、
  最新の質問・指摘・承認状況を確認します。進捗 JSON に成功印を手入力しないでください。

既存案件のデータを持ち込む場合は [移行手順](.claude/skills/aidd-common/references/migration.md) を
先に確認してください。この配布は main_flow 用であり、新規／変更の複数ワークフロー選択機能は含みません。
Phase 8 で実装した後のアプリの実行・デプロイは別の作業です。
