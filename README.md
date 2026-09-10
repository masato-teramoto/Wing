# release — ユーザープロジェクト雛形（alpha1.1）

| 項目 | 内容 |
| --- | --- |
| 対象リリース | `alpha1.1` |
| 位置づけ | L1 / L2 のアセットを**実配置済み**の、そのまま使えるプロジェクト雛形 |
| 収録内容 | Skill 23本（L1 13 + L2 9 + MCP サンプル 1）／ サブエージェント 5本 ／ テンプレート 13点 ／ Rimay-JP MCP alpha `0.1.0` |
| 実行環境 | Cursor / Claude Code |

このフォルダは、[`l1_spec/`](../l1_spec/README.md) と [`l2_intelligence_assets/`](../l2_intelligence_assets/README.md)
の配置手順を**あらかじめ適用した状態**の雛形です。各レイヤーの README を読んで手作業でコピーする代わりに、
**このフォルダごと自分の作業場所へコピーして**利用します。

> **⚠️ Rimay-JP MCP は private 環境での内部検証に限定します。**
> 同梱の固定 Grammar にライセンス許諾の明示がないため、公開・第三者配布・一般配布を行わないでください
> （[alpha-distribution.yaml](mcp/rimay-jp-mcp-alpha-0.1.0/prototype/rimay-jp/adapters/mcp/alpha-distribution.yaml)）。
> MCP を使わない場合は `mcp/` と `.mcp.json`、`.claude/skills/rimay-spec-alpha-check/` を削除してください
> （L2 アセットごと外す手順は [2.6](#26-l2-アセットを使わない場合l1-のみで構成する) を参照）。

## 1. フォルダ構成

```text
release/
├── README.md                       … 本ファイル
├── .gitignore                      … ds/ と Python 生成物を除外
├── .mcp.json                       … Rimay-JP MCP の stdio 設定（プロジェクトルート起点にパス調整済み）
├── .claude/
│   ├── skills/                     … Skill 23本
│   │   ├── aidd-flow/              … L1: オーケストレータ（フローの入口）
│   │   ├── requirement-intake/ … wireframe-integration/   … L1: 作成 Skill 6本
│   │   ├── format-conformance/ … gate-report/             … L1: 品質ゲート共通 Skill 6本
│   │   ├── requirement-clarification/ … prohibition-authoring/  … L2: 要求・要件定義 Skill 9本
│   │   └── rimay-spec-alpha-check/ … MCP を使う alpha 検査スキル（サンプル）
│   └── agents/                     … 品質ゲートのサブエージェント5本
├── Templates/                      … 成果物のひな形13点（Flow 4 / steering 7 / specs 1 / wireframe 1）
├── .aidd/
│   └── rfp/                        … ここに RFP を置く（自由形式・テンプレートは無い）
└── mcp/
    └── rimay-jp-mcp-alpha-0.1.0/   … Rimay-JP MCP 内部検証 bundle（配布時のまま・hash 検証可）
```

実行時に増えるもの（いずれも Skill が生成します。あらかじめ用意する必要はありません）:
`.aidd/requirement-list.md` ／ `.aidd/feature-list.md` ／ `.aidd/gates/` ／ `.aidd/phase-progress.json` ／
`.aidd/wireframe/<feature-name>/` ／ `steering/` 7ファイル ／ `specs/<feature-name>/requirements.md` ／
`ds/`（Phase 5 で取得。コミットしない）

## 2. 使い方

### 2.1 コピーして開く

```bash
cp -r alpha1.1/release <自分の作業場所>/<プロジェクト名>
cd <自分の作業場所>/<プロジェクト名>
git init && git add -A && git commit -m "init from alpha1.1 release"
```

**対象プロジェクトは必ず git 管理してください。** ゲートは検査した成果物のフロントマター
（`status` / `updated_at`）まで書き換えるため、**それ以外が変わっていないか**を差分で確認できる必要があります
（本文の書き換えは規約で禁止していますが、ツール権限では縛れません）。

**Claude Code のエージェントチームは有効にしないでください。** サブエージェントが teammate として並列起動されると、
フロントマターや `phase-progress.json` を競合して書きます。

### 2.2 RFP を置く

`.aidd/rfp/` に RFP を配置します。書式は自由で、テンプレートはありません。

### 2.3 フローを実行する

プロジェクトを Cursor または Claude Code で開き、`/aidd-flow` を起動します。
オーケストレータが実ファイルの `status` から再開点を判定し、
**フェーズ開始（Step 0）と ③ 人間レビュー（Step 4）で停止します。**

| Phase | フェーズ | 生成される成果物 |
| --- | --- | --- |
| 1 | 要求受入 | `.aidd/requirement-list.md` |
| 2 | Steering 作成 | `steering/` 7ファイル |
| 3 | Feature 分割 | `.aidd/feature-list.md` |
| 4 | requirements 作成 | `specs/<feature-name>/requirements.md` |
| 5 | 画面モック生成 | `.aidd/wireframe/<feature-name>/` |

各フェーズの詳細・人間が判断すべきこと（修正 / 差戻し / 対応せず進める / 承認）は
[`l1_spec/README.md`](../l1_spec/README.md#53-人間が判断すること) を参照してください。

### 2.4 Phase 5 の追加準備（Phase 1〜4 では不要）

| 準備 | 内容 |
| --- | --- |
| **Node.js** | 監査（`audit-tokens` / `audit-components`）・トークン一致検査・動線チェックの実行に必要 |
| **デザインシステム（DS）** | **版（タグ）を人間が指定**し、タグ固定の `git clone` で `ds/` へ配置する。`ds/` は `.gitignore` 済み |

`ds/` は読み取り専用です。監査スクリプト・トークン JSON を含めて変更しません。

### 2.5 Rimay-JP MCP を使う場合（任意）

日本語要件の品質検査・壁打ちに使います。**AIDD Spec 生成フロー（Phase 1〜5）の実行には必須ではありません。**

```bash
python -m pip install -r mcp/rimay-jp-mcp-alpha-0.1.0/requirements.txt
python mcp/rimay-jp-mcp-alpha-0.1.0/prototype/rimay-jp/adapters/mcp/smoke_test.py
```

- Python 3.12 以上が必要です。
- このプロジェクトルートの [`.mcp.json`](.mcp.json) により `rimay-jp` サーバーが自動起動します
  （bundle 同梱の `.mcp.json` は bundle 単体で開く場合用にそのまま残してあります）。
- 検査・壁打ちは `/rimay-spec-alpha-check` を手動実行します。
- 詳細は [BUNDLE-README.md](mcp/rimay-jp-mcp-alpha-0.1.0/BUNDLE-README.md) を参照してください。

### 2.6 L2 アセットを使わない場合（L1 のみで構成する）

AIDD Spec 生成フロー（Phase 1〜5）だけを使い、L2 知識レイヤーを配布・利用しない場合は、
コピー後に L2 由来のアセットを削除できます。**L1 の Skill・サブエージェント・テンプレートは
L2 に依存しないため、削除してもフローはそのまま動作します。**
Rimay-JP MCP を private 環境の外へ持ち出さないために、この構成を選ぶこともできます。

削除対象は次の4区分です。

| 区分 | パス | 本数 |
| --- | --- | --- |
| L2 Skill | `.claude/skills/` 配下の9本（下記コマンド参照） | 9 |
| MCP サンプルスキル | `.claude/skills/rimay-spec-alpha-check/` | 1 |
| MCP bundle | `mcp/rimay-jp-mcp-alpha-0.1.0/` | 1 |
| MCP 設定 | `.mcp.json`（プロジェクトルート） | 1 |

```bash
cd <プロジェクトルート>

# L2 Skill 9本
rm -rf .claude/skills/canonical-terminology-authoring \
       .claude/skills/edge-case-enumeration \
       .claude/skills/implementation-planning \
       .claude/skills/prohibition-authoring \
       .claude/skills/requirement-authoring-core \
       .claude/skills/requirement-clarification \
       .claude/skills/spec-change-proposal \
       .claude/skills/terminology-consistency-audit \
       .claude/skills/traceability-audit

# MCP サンプルスキル・bundle・設定
rm -rf .claude/skills/rimay-spec-alpha-check mcp/ .mcp.json
```

PowerShell の場合:

```powershell
cd <プロジェクトルート>

'canonical-terminology-authoring','edge-case-enumeration','implementation-planning',
'prohibition-authoring','requirement-authoring-core','requirement-clarification',
'spec-change-proposal','terminology-consistency-audit','traceability-audit',
'rimay-spec-alpha-check' |
  ForEach-Object { Remove-Item -Recurse -Force ".claude/skills/$_" -ErrorAction SilentlyContinue }

Remove-Item -Recurse -Force mcp, .mcp.json -ErrorAction SilentlyContinue
```

> **⚠️ 名前の似た L1 Skill を消さないでください。**
> `traceability-audit`（L2）と `traceability`（L1）、`requirement-authoring-core`（L2）と
> `requirements-authoring` / `requirement-intake`（L1）は別物です。
> ワイルドカード（`rm -rf .claude/skills/requirement*` など）ではなく、上記のとおり**名前を明示して**削除してください。

削除後に残る構成は以下のとおりです。

| 項目 | 削除前 | 削除後 |
| --- | --- | --- |
| Skill | 23本（L1 13 + L2 9 + MCP サンプル 1） | **13本（L1 のみ）** |
| サブエージェント | 5本 | 5本（変更なし） |
| テンプレート | 13点 | 13点（変更なし） |

削除の確認:

```bash
ls .claude/skills | wc -l   # → 13
```

あわせて任意で実施できること:

- `.gitignore` の `# Python（Rimay-JP MCP の実行時に生成される）` 以下の4行は不要になります（残しても害はありません）。
- 本 README の [2.5](#25-rimay-jp-mcp-を使う場合任意) と冒頭の Rimay-JP MCP 注意書きは、自分のプロジェクトでは削除して構いません。

**後から L2 を戻す場合**は、リリースパッケージの
[`l2_intelligence_assets/skills/`](../l2_intelligence_assets/README.md) の9本を `.claude/skills/` へ、
[`l2_intelligence_assets/mcp/rimay-jp-mcp-alpha-0.1.0/`](../l2_intelligence_assets/README.md) を `mcp/` へコピーし、
`.mcp.json` を復元します（`alpha1.1/release/` から再コピーするのが確実です）。

## 3. 注意事項

- **`wireframe-authoring` / `wireframe-integration` の `SKILL.md` を書き換えないでください。**
  外部パッケージ由来の配布物であり、パッケージ更新時に追記が失われます。
- **成果物に残る未記入プレースホルダー**（`<PRODUCT_NAME>` のような山括弧の大文字項目）は、
  埋める必要がないものを**不要理由を添えたまま保持する**規約であり、消し忘れではありません。
- 本リリースのスコープは **Phase 5 まで**です。`design.md`（Phase 6）／ `docs/`（Phase 7）／
  `tasks.md`（Phase 8）は含まれません。
- 顧客固有情報・機密情報を追加する場合は、配布範囲と保存先の規程を別途確認してください。
