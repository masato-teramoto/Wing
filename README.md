# intelligence_asset — 知識アセット ワークスペース（alpha3）

| 項目 | 内容 |
| --- | --- |
| 対象リリース | `alpha3` |
| 位置づけ | L2 知識レイヤー（要求・要件定義ほかの支援 Skill と Rimay-JP MCP）を**実配置済み**のワークスペース |
| 収録内容 | Skill 23本（L2 22 + MCP サンプル 1）／ Rimay-JP MCP alpha `0.1.0` |
| 実行環境 | Cursor / Claude Code |
| 原本 | [`layers/l2_knowledge/`](../../../layers/l2_knowledge/README.md)（Skill は `knowledge/quality/`、MCP は `service/provider/knowledge_service/rimay-jp/`） |
| MCP の利用範囲 | **private 環境での内部検証のみ** |

要求・要件定義を支援する Skill 群と、日本語要件の品質検査・壁打ちに使う MCP の内部検証 bundle を、
そのまま開いて使える形に配置したものです。

> **⚠️ Rimay-JP MCP は private 環境での内部検証に限定します。**
> 同梱の固定 Grammar にライセンス許諾の明示がないため、公開・第三者配布・一般配布を行わないでください
> （[alpha-distribution.yaml](mcp/rimay-jp-mcp-alpha-0.1.0/prototype/rimay-jp/adapters/mcp/alpha-distribution.yaml)）。
> MCP を使わない場合は `mcp/` と `.mcp.json`、`.claude/skills/rimay-spec-alpha-check/` を削除してください。
>
> **⚠️ `.claude/skills/elicitation-coverage/` は社外秘です。**
> 社内の管理下にあり、社外に露出せず、撤収可能なプロジェクトに限って保持してください。
> 条件を満たさない場合は当該ディレクトリを削除します（削除のみで撤収完了）。

## 1. フォルダ構成

```text
intelligence_asset/
├── README.md                       … 本ファイル
├── .gitignore                      … Python 生成物を除外
├── .mcp.json                       … Rimay-JP MCP の stdio 設定（このルート起点にパス調整済み）
├── .claude/
│   └── skills/                     … Skill 23本
│       ├── <L2 skill>/             … 22本。各 SKILL.md + PROVENANCE.md
│       └── rimay-spec-alpha-check/ … MCP を使う alpha 検査スキル（サンプル）
└── mcp/
    └── rimay-jp-mcp-alpha-0.1.0/   … Rimay-JP MCP 内部検証 bundle（配布時のまま・hash 検証可）
```

## 2. 使い方

### 2.1 単体のワークスペースとして開く

```bash
cp -r releases/alpha3/intelligence_asset <自分の作業場所>/<名前>
cd <自分の作業場所>/<名前>
```

Cursor または Claude Code で開くと、`.claude/skills/` の Skill をそのまま呼び出せます。

### 2.2 既存プロジェクトに Skill だけを足す

AIDD main_flow（Phase 1〜8：Spec 生成と実装）の案件（[`main_flow/`](../main_flow/README.md) 由来のプロジェクト）で併用する場合は、
`.claude/skills/` から必要な Skill ディレクトリを案件の `.claude/skills/` へコピーします。
`SKILL.md` と `PROVENANCE.md` はセットで保持し、ディレクトリ名は変更しないでください。

> **⚠️ 名前の似た L1 Skill を上書きしないでください。** `traceability-audit`（L2）と `traceability`（L1）、
> `requirement-authoring-core`（L2）と `requirements-authoring` / `requirement-intake`（L1）は別物です。

### 2.3 Rimay-JP MCP を使う場合（任意）

日本語要件の品質検査・壁打ちに使います。**Skill の利用には必須ではありません。**

```bash
python -m pip install -r mcp/rimay-jp-mcp-alpha-0.1.0/requirements.txt
python mcp/rimay-jp-mcp-alpha-0.1.0/prototype/rimay-jp/adapters/mcp/smoke_test.py
```

- Python 3.12 以上が必要です。
- このルートの [`.mcp.json`](.mcp.json) により `rimay-jp` サーバーが自動起動します
  （bundle 同梱の `.mcp.json` は bundle 単体で開く場合用にそのまま残してあります）。
- 検査・壁打ちは `/rimay-spec-alpha-check` を手動実行します。
- 詳細は [BUNDLE-README.md](mcp/rimay-jp-mcp-alpha-0.1.0/BUNDLE-README.md) を参照してください。

### 2.4 MCP を外す

```bash
rm -rf .claude/skills/rimay-spec-alpha-check mcp .mcp.json
```

PowerShell の場合:

```powershell
Remove-Item -Recurse -Force .claude/skills/rimay-spec-alpha-check, mcp, .mcp.json -ErrorAction SilentlyContinue
```

## 3. Skill の状態

`requirement-authoring-core` と `traceability-audit` は validated／authoritative、その他は advisory です。
状態・根拠・再配布条件は各 Skill の `PROVENANCE.md` を確認してください。
Skill ごとの用途は各 Skill の `SKILL.md` を参照してください（原本は [`layers/l2_knowledge/knowledge/quality/`](../../../layers/l2_knowledge/README.md)）。

## 4. 完全性と配布上の注意

- MCP bundle の収録内容は
  [`bundle-manifest.json`](mcp/rimay-jp-mcp-alpha-0.1.0/bundle-manifest.json) と
  [`SHA256SUMS`](mcp/rimay-jp-mcp-alpha-0.1.0/SHA256SUMS) に記録されています。
- beta 以降は外部提供 MCP へ切り替え、このローカル MCP サーバーと固定 Grammar bundle を除去する予定です。
- 顧客固有情報・機密情報を追加する場合は、配布範囲と保存先の規程を別途確認してください。
