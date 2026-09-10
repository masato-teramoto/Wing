# Rimay-JP MCP ツール仕様（利用者向け）

Rimay-JP MCP サーバー（サーバー名 `rimay-jp`）が公開する **44 ツール**の一覧と用途です。
起動・登録・動作確認は [SERVER-SETUP.md](SERVER-SETUP.md)、Adapter の設計方針は [README.md](README.md) を参照してください。

## 前提（すべてのツールに共通）

- **Adapter は状態を持ちません。** 各ツールは Core／Orchestrator／Generator の関数へ委譲する薄い入口で、CLI・CI・Library と同じ辞書・ルール・プロファイルを使います。
- **更新は `apply_canonical_patch` だけ。** Canonical を書き換える正規の手段はこの 1 ツールに限られ、根拠検査を通った差分のみ適用されます。
- **`project_id` が必要なツールがあります。** 用語・語彙に依存する処理は毎回 `project_id` を受け取り、サーバー側の案件レジストリが辞書スナップショットを固定します。ファイルパスやルートはクライアントから渡しません。
- **人間の承認が要る操作があります。** 受入基準・テストの生成は承認済み（approved）Canonical のみ、用語の承認・公開は人間の明示操作が必須です。

## 用途別ツール一覧

### 1. サーバーの能力を確認する

| ツール | 用途 |
| --- | --- |
| `get_supported_profile()` | 対応する条件・モダリティ・Action・Schema 版など、サーバーが扱える範囲の要約を返す。まず最初に呼ぶ。 |

### 2. 日本語要求を書き始める・壁打ちする（Repository Grammar alpha）

日本語の要求文をそのまま入口にして、スメル検査と固定 Grammar 候補の検査を行うツール群です。

| ツール | 用途 |
| --- | --- |
| `analyze_japanese_requirement(source_text_ja, ...)` | 日本語 Normalizer を第一入口にし、English Rimay への lossless 変換可否を返す。 |
| `inspect_japanese_requirement_alpha(source_text_ja, rimay_candidate=None, ...)` | 任意の日本語要求のスメルと固定 Grammar 候補を一括検査する。候補を省略すると自動生成を試みる。 |
| `get_repository_parser_capabilities()` | 固定 Repository Grammar で実行できる Rule と権限境界を返す。 |
| `get_repository_rule_details(literals=None, rule_ids=None, max_results=5)` | 候補生成に必要な Rule の要約だけを返す。 |
| `evaluate_rimay_candidate(rimay_candidate, candidate_origin, ...)` | 完成した Repository Rimay 候補を parse・link・project する。 |
| `build_repository_demo_observation(session_id, turn_id, analysis_response, evaluation_response, ...)` | 壁打ちの観測ログを、既定で秘匿化した形で組み立てる。 |

### 3. Canonical 化と検証

| ツール | 用途 |
| --- | --- |
| `normalize(text, project_id, requirement_id="REQ-MCP")` | Rimay-JP 文から Canonical 候補を生成する。 |
| `validate_core(canonical, project_id)` | Schema・格フレーム・品質規則を検査する。 |
| `validate_terminology(canonical, project_id)` | 用語辞書への適合（未登録・承認待ち・多義・廃止語）を検査する。 |
| `validate_domain(canonical, project_id)` | 業務ルール・状態モデルとの整合を検査する。 |
| `validate_sidecar(canonical, views)` | sidecar の完全性と manifest 整合を検査する。 |
| `validate_all_layers(canonical, project_id)` | 9 層検証を一括実行し、Validation Report（正本）と検証状態を返す。 |

### 4. English Rimay の解析・等価/適合チェック

| ツール | 用途 |
| --- | --- |
| `render_requirement_views(canonical)` | Canonical から Rimay-JP 文・English Rimay・sidecar を manifest 付きで生成する。 |
| `parse_english_rimay(text)` | クリーンルーム Parser を実行し AST を返す。 |
| `check_equivalence(canonical, english_rimay)` | Canonical と AST の意味等価を検査する。 |
| `check_conformance(canonical, english_rimay)` | Rule ID 束縛・operator 集合・full consumption を英語適合プロファイルで検査する。 |

### 5. Canonical を更新する（唯一の更新手段）

| ツール | 用途 |
| --- | --- |
| `apply_canonical_patch(canonical, patch)` | Patch を検査し、許可された差分だけを適用する。**Canonical を書き換える唯一の手段。** |

### 6. 知識照会・情報分類・対話

| ツール | 用途 |
| --- | --- |
| `classify_information(text)` | 文を Context・Rule・Issue・Requirement Candidate 等へ分類する。 |
| `extract_requirement_candidates(segment, project_id, requirement_id="REQ-MCP")` | 分類済みセグメントから要求候補を抽出する。 |
| `lookup_term(surface, project_id)` | 表層語を標準用語 ID へ解決する。 |
| `get_case_frame(family)` | Action Class と必須 Role を返す。 |
| `lookup_state_model(property_id)` | 状態・イベント・遷移を照会する。 |
| `lookup_business_rule(keyword="")` | 業務ルール・規制・既存仕様を照会する。 |
| `route_knowledge(canonical)` | スロットと finding から必要な知識源を選ぶ。 |
| `plan_questions(canonical)` | 不足・曖昧性に対する質問を優先順位付きで返す。 |
| `apply_answer(canonical, question, answer_text)` | 利用者回答を根拠付き Patch へ変換する（適用は `apply_canonical_patch`）。 |

### 7. 下流生成・還流

いずれも承認済み Canonical が前提です（`generate_*` は approved 以外を拒否）。

| ツール | 用途 |
| --- | --- |
| `generate_acceptance_criteria(canonical)` | 承認済み Canonical から受入基準を生成する。 |
| `generate_test_candidates(canonical, criteria=None)` | 承認済み Canonical と受入基準からテスト候補を生成する。 |
| `record_feedback(feedback)` | 下流の問題を要求スロット・知識・Validator・Generator へ関連付ける。 |

### 8. 修復・分割・Free-text 診断

| ツール | 用途 |
| --- | --- |
| `plan_repairs(canonical, report=None, extra_findings=None)` | Validation Report の finding を修復アクションへ振り分ける（Patch は含まない）。 |
| `accept_split_proposal(canonical, proposal)` | **人間が分割提案を承諾した後にのみ呼ぶ。** 各 part を通常抽出経路へ入れ親子 trace を張る。 |
| `diagnose_raw_text(text, language="ja", case_id="RAW")` | Free-text の Pre-Canonical 診断。finding は質問・分割提案を起こすのみで要求を遮断しない（恒久 Advisory）。 |

### 9. 用語・語彙形成ループ

未知語を「候補化 → 承認待ち → 承認・公開 → 伝播確定」で案件語彙へ育てるループです。すべて `project_id` を受け取り、書き込み系は楽観ロック（`base_revision`）を使います。

| ツール | 用途 |
| --- | --- |
| `extract_document_terms(text, document_id, project_id)` | 文書から用語候補を決定論・無副作用で抽出する（未知語のみ候補化）。 |
| `observe_term_occurrence(project_id, observation, document_id, requirement_id, ...)` | 未知語を不変 Occurrence として記録し候補を起票する（idempotent）。 |
| `resolve_term_surface(surface, project_id)` | 表層語を多値解決する（exact / synonym / ambiguous / not_found / deprecated）。 |
| `get_term_candidate(candidate_id, project_id)` | 語彙候補の現在状態（revision 含む）を返す。 |
| `propose_term_candidate(candidate_id, base_revision, proposed_term, project_id, evidence=None)` | 候補に定義案（ID・表記・type・定義・根拠）を記録する。 |
| `submit_term_candidate_for_review(candidate_id, base_revision, project_id)` | 候補を審査中（under_review）へ進める。 |
| `approve_term_candidate(candidate_id, base_revision, reviewer, approved_at, project_id, ...)` | **人間のみ。** 承認し Approval Receipt を発行する。 |
| `reject_term_candidate(candidate_id, base_revision, reviewer, decided_at, project_id, ...)` | 候補を却下する（記録は残る）。 |
| `publish_vocabulary_snapshot(snapshot_id, candidate_ids, operation_id, published_at, project_id, ...)` | 承認済み候補を immutable Snapshot として公開し伝播 Saga を起票する（Receipt 必須）。 |
| `analyze_vocabulary_impact(operation_id, project_id)` | 公開 operation の影響計画と伝播未完了の Requirement 集合を返す（read-only）。 |
| `propagate_vocabulary_operation(operation_id, canonicals, applied_at, project_id)` | 影響 Requirement へ Saga 伝播する（idempotent・部分完了は retry_required で可視）。 |

## スメル検出の観点

要求スメル検出は reqsmell エンジン（Layer 2）が担い、MCP からは **2 つの段階**で使えます。

### 検出の 2 段階

| 段階 | 対象 | 担当 | 呼び出すツール | 性質 |
| --- | --- | --- | --- | --- |
| **Raw Text（Pre-Canonical）** | 自由文（未構造化の日本語/英語） | raw-text-quality-gate（reqsmell 委譲） | `diagnose_raw_text`（正本）、`inspect_japanese_requirement_alpha`、`analyze_japanese_requirement` | 表層スメル。**恒久 Advisory＝非遮断**（質問・並べ替え・分割を促すのみ） |
| **Canonical 段** | 構造化された Canonical | Core Validator | `validate_core` / `validate_all_layers` | 構造スメル（欠落・非原子性など）。検証結果として扱う |

同じ「非原子（1文に複数の主要動作）」でも、自由文の分割候補は Raw Text 段（`diagnose_raw_text`）、構造化後の検査は Canonical 段（`validate_*`）と役割が分かれます。

### Raw Text 段が返すスメル（サポート範囲）

`diagnose_raw_text` などの戻り値は 3 種類です。

- **findings（このゲートが所有する 4 コード）** — 正規化済みで、推奨アクションが付く。いずれも `blocking:false`。

  | スメル | 正規化コード | 推奨アクション |
  | --- | --- | --- |
  | 語順不正 | `INCORRECT_SEGMENT_ORDER` | normalize（表層再生成で自動修復） |
  | 受身表現 | `PASSIVE_VOICE` | clarify（主体を質問） |
  | 並列の曖昧さ | `COORDINATION_AMBIGUITY` | split（分割提案） |
  | 非原子（複数の主要動作） | `MULTIPLE_PRIMARY_ACTIONS` | split（分割提案） |

- **cross_signals（他コンポーネントが所有。照合ログのみ）** — `not_a_requirement`（→ `NOT_A_REQUIREMENT`、情報分類器の所有）、`not_precise_verb`（→ `IMPRECISE_ACTION_VERB`、候補抽出器の所有）。
- **raw_smells** — エンジンが検出した生のスメル名の全リスト。上記 4 コード以外（完全性・用語定義・メトリクス有無など）もここに現れますが、構造化 finding には昇格しません（Canonical 段との二重判定を避けるため）。

### 日本語対応と、それ以外の違い

- **言語判定**: 明示指定が最優先。未指定なら、CJK 文字を含めば日本語、ラテン文字なら英語、どちらでもなければ **UNDETERMINED（アナライザ無し＝検出不可）**。
- **サポートされる言語は日本語と英語の 2 つ**。専用アナライザがあるのはこの 2 言語だけで、その他の言語は解析器が無く検出されません。
- **検出の定義（criteria）は共通**（論文ベース、FR-020）ですが、**判定の基盤は言語ごとに別実装**です。
  - 日本語: 決定論的なパターンベース（受身の助動詞、義務表現「〜しなければならない」、助詞で標識される主語、日本語の曖昧動詞辞書）。オプションで Sudachi 品詞ベースへ切替可（`configure_japanese_analyzer("sudachi")`。未導入環境は fail-closed）。既定は regex。
  - 英語: 決定論的な軽量辞書＋形態処理（modal・be 動詞・動詞辞書）。
- **MCP ツールからの到達性**: `analyze_japanese_requirement` と `inspect_japanese_requirement_alpha` は **日本語専用**の入口です。英語のスメル検出は汎用の `diagnose_raw_text(text, language="en")` から利用できます（既定は `language="ja"`）。

## 典型的な流れ

1. `get_supported_profile` で対応範囲を確認
2. 日本語入力を `inspect_japanese_requirement_alpha` / `normalize` で Canonical 化
3. `validate_all_layers`（または個別の `validate_*`）で検証
4. `plan_questions` → `apply_answer` → `apply_canonical_patch` で不足を補う
5. 承認後に `generate_acceptance_criteria` / `generate_test_candidates` で下流生成
6. 未知語が出たら §9 の語彙ループで案件辞書を更新
