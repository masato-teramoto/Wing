# MCPサーバー セットアップ手順（別紙）

[README](README.md)のAIDDワークフロー登録の前提手順。

## 0. 結論: 事前起動は不要

本サーバーは**stdioトランスポート**であり、`.mcp.json` に登録した `command` を
**Claude Codeがセッション開始時に子プロセスとして自動起動**する
（`command`/`args` がそのまま起動コマンド）。利用者が常駐サーバーを
立てておく必要はない。必要な準備は下記の環境整備のみ。

## 1. 前提環境の整備（初回のみ）

1. **Python 3.12以上** が `python` で解決されること:

   ```bash
   python --version
   ```

   Windowsで `where python` の先頭が
   `...\AppData\Local\Microsoft\WindowsApps\python.exe`（Store誘導スタブ）の
   場合は、実体のパス（例 `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`）
   を `.mcp.json` の `command` に絶対パスで指定する。

2. **依存パッケージ**（CIと同一）:

   ```bash
   python -m pip install pyyaml jsonschema "mcp<2"
   ```

   `mcp` は 2.x で `mcp.server.fastmcp` が削除されているため `<2` を固定する
   （SDK 2.x対応はBacklog）。

3. **Lexical Analysis capability（optional。改善計画 v0.3 P1）**:

   ```bash
   python -m pip install "sudachipy==0.6.11" \
       "sudachidict_core==20260723" "sudachidict_small==20260723"
   ```

   - 文書用語抽出の `provider="sudachipy"` 経路が使用する。**未導入でも
     既定（`provider="regex"`）の全機能は動作する**。
   - `sudachipy` 指定時に未導入なら fail-closed で明示エラーになる
     （silent fallbackしない。§7.3）。
   - 版は評価baselineへpinしている（評価期間中は変更しない）。更新時は
     `corpus/lexical/` fixtureの再評価と
     `scripts/evaluate_lexical_analysis.py` の再実行が必要。
   - 辞書はwheel同梱でオフライン動作する（実行時ネットワーク不要。
     `core`辞書は約200MB/`small`は約70MBのdisk footprint）。

## 2. 動作確認（登録前の検証。ワンコマンド）

```bash
python prototype/rimay-jp/adapters/mcp/smoke_test.py
```

サーバーをstdioで起動し、initialize → tools/list（44ツール）→
tools/call（lookup_term、Repository capability、日本語alpha一括検査、redacted observation）まで実施して
`SMOKE TEST PASS` を表示する。Repository部分も同梱固定Grammarを用いて常に検査する。
失敗する場合は §4 トラブルシュート参照。

### 推奨配布セットの生成

別環境へ持ち出す場合は、配布境界の正本`alpha-distribution.yaml`からBuilderで生成する。
出力先はリポジトリ外の新規ディレクトリを指定する（既存先は上書きしない）。

```bash
python prototype/rimay-jp/scripts/build_mcp_alpha_distribution.py \
  --output /path/outside/repository/rimay-jp-alpha
```

生成物には、MCP runtime allowlist、同梱固定Grammar、単独完結する手動Skill
`rimay-spec-alpha-check`、`.mcp.json`、最小依存一覧、利用手順、file hash manifestを含む。
テスト・corpus・reports・Builder自身は含めない。受け渡し後の完全性は次で再検証できる。

```bash
python prototype/rimay-jp/scripts/build_mcp_alpha_distribution.py \
  --verify /path/outside/repository/rimay-jp-alpha
```

## 3. Claude Codeへの登録

リポジトリ直下の `.mcp.json`（プロジェクト共有）または利用者設定に追加:

```json
{
  "mcpServers": {
    "rimay-jp": {
      "command": "python",
      "args": ["prototype/rimay-jp/adapters/mcp/rimay_jp_mcp.py"]
    }
  }
}
```

- `args` の相対パスはプロジェクトルート基準（Claude Codeはプロジェクト
  ディレクトリでサーバーを起動する）。
- 登録後、Claude Codeを再起動（または新セッション開始）し、`/mcp` で
  `rimay-jp` が接続済み・44ツールが見えることを確認する。
- alpha内部検証では`adapters/mcp/assets/Dsl_rimay.xtext`を既定で使用する。
  別実体の検証が必要な場合だけ`env.RIMAY_FIXED_GRAMMAR`を指定する。相対パスは
  リポジトリルート基準で解決し、読込不能・hash不一致はいずれもfail-closedで拒否する。
- 同梱Grammarはライセンス未設定の原典とbyte一致するため、private repository内の
  内部検証に限定する。外部公開・再配布は行わず、beta以降は外部提供MCPへ置換して
  ローカルMCPサーバーとGrammarを除去する。境界の正本は
  [alpha-distribution.yaml](alpha-distribution.yaml)。

## 4. トラブルシュート

| 症状 | 原因と対処 |
|---|---|
| `ModuleNotFoundError: mcp` | 依存未導入。§1-2 を実行（`.mcp.json`のcommandと同じpythonへ導入すること） |
| `ImportError: mcp.server.fastmcp` | mcp SDK 2.x が入っている。`pip install "mcp<2"` で固定 |
| smoke testで応答なし | stderr出力を確認（スクリプトが表示する）。多くはpython実体の不一致 |
| `/mcp` に出ない | `.mcp.json` の置き場所（プロジェクトルート）と、初回のプロジェクトMCP承認プロンプトを確認 |
| Repository demo toolが固定Grammarを読めない | 同梱`assets/Dsl_rimay.xtext`の存在・hashを確認する。上書き指定中なら`env.RIMAY_FIXED_GRAMMAR`を除去するか正しい実体へ直してセッションを再起動 |

## 5. 対話利用（壁打ち）とライブAPI実測の関係

**Claude Codeでの対話壁打ちに `ANTHROPIC_API_KEY` は不要。**
2つの利用形態を区別する:

| 形態 | LLM | 必要なもの | 用途 |
|---|---|---|---|
| **対話利用（壁打ち）** | Claude Code内のClaude自身がMCPクライアント経由でツールを呼ぶ | 本書§1〜3のみ | 要求形成ループの実運用（分類→抽出→検証→質問→回答Patch→生成） |
| **ライブAPI実測** | runner_llm の AnthropicApiBackend がAPIを直接呼ぶ | `ANTHROPIC_API_KEY` | §22.4指標（トークンusage等）の再現可能な定点測定（モデル・温度・プロンプト版を固定記録） |

対話利用時も統制は同一（Adapterを透過）: 確定（confirmed）は
`apply_canonical_patch` の根拠検査（user_answer／knowledge_asset／rule）のみが
通し、LLM候補はproposedに固定、生成はapproved限定。

対話壁打ちの進行規則は**スキル [`rimay-kabeuchi`](../../../.claude/skills/rimay-kabeuchi/SKILL.md)**
として同梱している（説明文トリガーで自動起動する準・常時適用。確実に適用したい
場合はセッション冒頭で `/rimay-kabeuchi` を明示起動）。既存の要件定義工程
コマンドとは独立で、工程コマンド側からの明示起動でも共存できる。
配布時は本書§2のBuilderで生成した推奨セットを用いる。alphaの既定手動入口は
単独完結する`rimay-spec-alpha-check`であり、正式Canonical工程まで必要な場合だけ
`rimay-kabeuchi`等を別途追加する。

### Repository Grammar日本語alphaの推奨フロー

```text
1. get_repository_parser_capabilities … 178 rules / 50 Action / 14 mapping面
2. inspect_japanese_requirement_alpha  … 任意の日本語を入力。スメルと候補を一括検査
3. candidate_requiredならget_repository_rule_detailsで必要なRuleだけ照会
4. LLMまたは利用者が完全な候補を作り、rimay_candidate付きで2を再実行
5. 確認済み事項と日本語意味の推論を分離して質問・修正し、2へ戻る
6. build_repository_demo_observation   … 任意。default-redactedで別工程へexport
```

alpha入口は特定シナリオやSENDに限定しない。決定的bridgeが作れない日本語でも、
host supplied candidateを固定Grammarの全Action分岐に対して検査できる。ただし
日本語と候補の意味同値は検証せず、`not_checked_by_rimay_jp`として返す。

詳細なsystem prompt、質問bundle、再試行上限、表示templateは
[Repository Grammar日本語壁打ちデモ host runbook](../../demo/repository-dialogue-host-runbook.md)
を正とする。

### 正式Canonical工程の推奨フロー（既存）

```text
1. get_supported_profile          … 対応範囲の確認（常時注入コアの代替）
2. classify_information           … 入力文の分類
3. extract_requirement_candidates … Canonical候補の抽出（unknown保持）
4. validate_all_layers            … 9層検証（Validation Report・blocking確認）
5. plan_questions / plan_repairs  … 不足への質問・修復計画（分割提案等）
6. （利用者が回答）→ apply_answer → apply_canonical_patch
7. validate_all_layers（再検証）→ render_requirement_views（表層再生成）
8. 人間承認後: generate_acceptance_criteria / generate_test_candidates
9. 下流で問題発見時: record_feedback
```
