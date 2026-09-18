# Rimay-JP MCP Adapter（Phase 5）

[llm-backend-design v0.5 §6](../../llm-backend-design.md)のツール群をMCPとして公開する。
**Adapterは状態・独自正本を持たない**（ADR-0012 D2）。全ツールは
rimay-jp-core／orchestrator／generatorsへの薄い委譲で、CLI・CI・Library・MCPの
全経路が同一のSSOT（Supported Profile・辞書・Rule）を使う。

## ツール（44）

- **コア・検証（§6.1）**: get_supported_profile / normalize / validate_core /
  validate_terminology / validate_domain / validate_sidecar /
  render_requirement_views / parse_english_rimay / check_equivalence /
  check_conformance / apply_canonical_patch
- **Repository Grammar日本語alpha**: inspect_japanese_requirement_alpha
  （任意の日本語についてスメル検査と候補の固定Grammar検査を一括実行）/
  analyze_japanese_requirement /
  get_repository_parser_capabilities / get_repository_rule_details /
  evaluate_rimay_candidate / build_repository_demo_observation
- **知識・対話（§6.2）**: classify_information / extract_requirement_candidates /
  lookup_term / get_case_frame / lookup_state_model / lookup_business_rule /
  route_knowledge / plan_questions / apply_answer
- **下流・還流（§6.3）**: generate_acceptance_criteria / generate_test_candidates /
  record_feedback
- **統合拡張（Step 4/5）**: validate_all_layers（9層検証＋Validation Report）/
  plan_repairs（repair_disposition振り分け。Patchは含まない）/
  accept_split_proposal（人間承諾後の分割実行。親子traceability付き）/
  diagnose_raw_text（Free-text Import診断=Pre-Canonical。ADR-0013の境界で
  reqsmell日本語Analyzerを使う正本経路。alpha入口も同じ経路へ委譲し、恒久Advisory）
- **語彙形成ループ（ADR-0014／ADR-0016）**: 語彙依存呼出しは毎回
  `project_id` を受け、サーバー側案件レジストリが案件＋組織Snapshotをpinする。
  root／ファイルパスはクライアント入力にしない。extract_document_terms（文書からの決定論
  抽出。未知語のみ候補化・resolved/ambiguous/deprecated分類・span根拠）/
  observe_term_occurrence（未知語の明示記録・
  idempotent）/ resolve_term_surface（5種多値Resolution）/ get_term_candidate /
  propose_term_candidate / submit_term_candidate_for_review /
  approve_term_candidate（**人間のみ**。Receipt発行）/ reject_term_candidate /
  publish_vocabulary_snapshot（Receipt必須・immutable・伝播Saga起票）/
  analyze_vocabulary_impact / propagate_vocabulary_operation
  （knowledge_asset Patch伝播・idempotent。壁打ち中の未知語は
  「候補化→承認待ちblocking→承認・公開→伝播確定」で案件語彙が成長する）

統制はツールの内側で担保される（§8）: 確定はapply_canonical_patchの根拠検査のみ、
LLM候補はproposed、表層はSerializerが再生成、生成はapproved限定。

## AIDDワークフローへの登録（Claude Code）

**サーバーの事前起動は不要**（stdio型。`.mcp.json`のcommandをClaude Codeが
セッション開始時に自動起動する）。前提環境の整備（Python 3.12・依存導入）・
ワンコマンド動作確認（smoke_test.py）・登録・トラブルシュートは
**[SERVER-SETUP.md](SERVER-SETUP.md)（別紙）**参照。登録スニペット:

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

対話壁打ち（Claude Code内のClaudeがツールを呼ぶ形態）に`ANTHROPIC_API_KEY`は
不要。Repository Grammar日本語alphaは、private repository内に固定した
`assets/Dsl_rimay.xtext`を既定で使う。別実体を検証するときだけ
`RIMAY_FIXED_GRAMMAR`で上書きでき、読込不能またはhash不一致はfail-closedにする。
この同梱は内部検証限定で、外部への公開・再配布を許可するものではない。
alpha配布境界は[alpha-distribution.yaml](alpha-distribution.yaml)、host promptと実行手順は
[repository-dialogue-host-runbook.md](../../demo/repository-dialogue-host-runbook.md)、
一般セットアップは[SERVER-SETUP.md §5](SERVER-SETUP.md)参照。
別環境向けの推奨セットは`build_mcp_alpha_distribution.py`で生成できる
（[SERVER-SETUP.md §2](SERVER-SETUP.md)）。生成物はリポジトリ外へ置き、
同梱`SHA256SUMS`またはBuilderの`--verify`で受け渡し後の完全性を確認する。

## 検査

`rimay_jp_cli.py corpus` の `mcp adapter` セクション（runner_mcp）が
ツール網羅（§6対応）・Adapter同値・JSON直列化可能性・統制の透過・
FastMCP登録を機械検査する。旧 `prototype/requirement-smells-mcp` の互換ツールは
[quality/adapters/mcp_adapter.py](../../quality/adapters/mcp_adapter.py)（サーバ名
`rimay-jp-quality`）が提供する（互換期間満了後にarchive予定）。
