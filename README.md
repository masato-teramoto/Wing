# AIDD main_flow — Claude Code 実行環境

このフォルダをそのまま Claude Code で開き、RFP から要求整理・タスク文書作成・実装
（Phase 1–8）を実行できます。配布元のソースリポジトリや引継ぎ ZIP は不要です。

## ZIPを展開して開始する

Python **3.10以上**、Git、利用可能なClaude Codeを用意し、ZIP全体を新しい作業フォルダへ展開します。
`.claude`、`.aidd`などの隠しフォルダも必要です。展開後は **Windowsなら `START.cmd` をダブルクリック**してください。
起動スクリプトが環境を確認し、Claude Code CLIがあればこのフォルダで開きます。
CLIがない場合は、表示されたフォルダをVS CodeのClaude Code拡張で開きます。
初回は案件専用のローカルGitを初期化します。コミット、リモートの登録、プッシュは行いません。

| ZIP内の構成 | 起動時の動作 | Claude Codeでの初回入力 |
|---|---|---|
| `.aidd/rfp/meeting-room-reservation.md` がある通常版 | 題材のRFPと実行資材を確認 | `/aidd-requirements-init` |
| `phase8-sample/` がある実装開始版 | 展開先でPhase 1〜7の題材を自動準備（初回は数分） | 合成入力で試行する旨を伝えてから `/aidd-implement reservation-window 1` |

実装開始版の詳細は、同梱されている場合の **`phase8-sample/README.md`** を参照してください。
上流の検査・承認はテスト専用の合成データです。Phase 8は準備1件＋業務4件の計5タスクが未実施で、
実装コードはありません。最初の準備タスクが専用`.venv`へ固定版の検証ツールを導入するため、初回はネットワーク接続が必要です。

macOS/Linuxでは `python3 -X utf8 -B -S start.py` を実行します。
起動準備だけを行う場合やClaude Code拡張を使う場合は、次を実行してから同じフォルダを開きます。

```powershell
python -X utf8 -B -S start.py --prepare-only
```

準備後のフォルダは移動せず、そのまま利用します。再実行しても実装中の状態を初期化しません。
最初からやり直す場合は、元ZIPを別の新しい場所へ展開してください。

## 最初の実行

1. **この README と CLAUDE.md があるフォルダ**を Claude Code の作業フォルダにします。
   ZIP を展開した場合も `.claude` と `.aidd` を含めたフォルダ全体を使ってください。
2. ターミナルで環境を確認します（macOS / Linux）。

   ```sh
   python3 -X utf8 -B aidd-run.py doctor
   claude
   ```

   Windows は `python --version` で Python 3.9 以上が表示されることを確認し、
   `python3` を `python` に置き換えます。`python` が使えない場合は
   `py -3 --version` を確認し、動作した場合だけ `py -3` を使ってください。
   `py -3` が「No installed Python found!」になる環境でも、`python` で起動できる場合があります。
   VS Code の Claude Code 拡張からこのフォルダを開く場合、CLI が未導入なら
   `python3 -X utf8 -B aidd-run.py doctor --runtime-only` で実行資材だけを確認できます。
3. Claude Code が求めるログインと、このフォルダの信頼確認を済ませます。
4. 通常版はClaude Codeの入力欄に **`/aidd-requirements-init`** を入力します。
   実装開始版は上の手順を使い、Phase 1からやり直さず実装工程へ進みます。
5. 質問・検査結果・承認依頼に回答します。Phase 1–3 の完了後、以下の順に進みます。

| 入力するコマンド | 作成・確認する内容 |
|---|---|
| `/aidd-requirements-init` | 要求一覧、steering、feature 一覧（Phase 1–3） |
| `/aidd-requirements` | feature 別 requirements と横断確認（Phase 4） |
| `/aidd-design` | feature 別 design、横断確認、統合 docs（Phase 5–6） |
| `/aidd-tasks` | feature 別 tasks と全体確認・承認（Phase 7） |
| `/aidd-implement <feature> [1,2,...]` | タスク1件ずつ実装し、全体検査とfeature単位の人間承認（Phase 8） |

Phase 8の開始前に、実在するテスト・検査コマンドとBoundaryに基づく編集範囲を
`.aidd/implementation/config/<feature>.json` に設定します。
形式と再開・修正手順は [.claude/skills/aidd-common/references/implementation/contract.md](.claude/skills/aidd-common/references/implementation/contract.md)。
必要な開発ツール・言語ランタイムは案件に合わせて準備してください。未設定の検査は承認できません。

最終検査の可読レポートは、別の`.aidd/implementation/reporting/<feature>.json`で設定します。
[レポート契約](.claude/skills/aidd-common/references/implementation/reporting.md)に従い、
OSSのテスト結果・coverageと仕様説明を用意してください。タスクの分割やcheck_idsは変更せず、
スイート／モジュール単位で出力を追加します。選択した静的解析の結果も別ファイルで含められます。

実行を中断した後は同じフォルダで同じ入口コマンドを使います。
途中の状態を初期化したり、完了済みの文書を手動で削除したりする必要はありません。
生成後の質問・指摘・承認には実際の回答が必要です。テスト題材でも自動承認は行いません。
通常の Claude Code のファイル／コマンド実行権限確認と、AIDD の業務承認は別です。

必要な検査がすべて完了するまで成果物を承認できません。形式不備で意味検査を省略した場合、
指摘を「対応せず進める」としても承認は止まります。修正して再検査を行い、必要な検査を揃えて
から承認します。過去版の検査・承認履歴がある案件は、同梱の移行手順に従って診断してください。

## 要求の入力

入力先は **`.aidd/rfp/`** です。テスト題材付きの配布には
`meeting-room-reservation.md` を1件配置しています。架空の30人規模のオフィスを題材に、
空き検索、予約、競合防止、取消、管理、履歴と受入観点を記載した要求書です。
成果物・進捗・検査・承認は未作成なので、そのまま最初から試行できます。

本番案件を始める場合は新しい配布コピーを用意し、**開始前にテスト RFP を取り除いて**
実際の RFP に差し替えてください。混在させると両方が要求入力になります。
試行済み環境を使い回す場合は入力変更検出と再承認の対象になり、初回実行には戻りません。
新しい試行は ZIP を別フォルダへ展開することで始められます。

## 必要な環境

- Claude Code の利用可能なアカウントと通信環境。認証情報はこの配布物に含みません。
- Python **3.9 以上**。Python パッケージの追加インストール、Node.js、MCP サーバーは
  AIDD ランナーの実行に不要です。PyYAML がなければ同梱パーサを使用します。
- このフォルダへの読取り・書込み権限。
- Git。要求IDの改版比較に必要。`start.py`が初回に案件専用のローカルGitを用意します。
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

## 配置されるファイル

```text
CLAUDE.md                 Claude Code への開始手順とホストの責務
README.md                 この開始ガイド
aidd-run.py               環境確認とプロジェクト固定の CLI 入口
START.cmd / start.py       ZIP展開先での準備とClaude Code起動
.claude/skills/           5つの入口、生成・修正・検査、L0/L3 の実行資材
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
記録は監査と再開に必要なので、実行開始後は保存してください。

## 問題が起きたとき

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
Phase 8でアプリの実装・検査を行います。実サービスへのデプロイは別途指示してください。
