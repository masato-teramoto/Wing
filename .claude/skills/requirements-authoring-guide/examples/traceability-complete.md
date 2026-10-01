# 記入例: 文書間の被覆がそろった6表

**説明専用・non-final・未実行。** audit_mode=authoring、audit_edges=[REQ-TASK, REQ-CHECK]。
要求母集合は[要件例](requirements.md)、下流母集合は[実装計画](implementation-plan.md)と
[検証仕様](verification-spec.md)。全IDをそれぞれの一覧から確認して対応づけた合成例である。
文書内の計画・仕様を比較しており、実装や検証結果の被覆を主張していない。

## edge_manifest

| edge_id | requirement_universe | downstream_universe | requirement_input_state | downstream_input_state | requirement_count | downstream_count |
|---|---|---|---|---|---|---|
| REQ-TASK | requirements.md | implementation-plan.md | PRESENT | PRESENT | 5 | 2 |
| REQ-CHECK | requirements.md | verification-spec.md | PRESENT | PRESENT | 5 | 5 |

## requirement_coverage

| edge_id | requirement_id | downstream_ids[] | status | status_rationale |
|---|---|---|---|---|
| REQ-TASK | FR-01 | [TASK-01] | FULLY | 対象だけを既読にし、他の値を保持する実装と観測を記述 |
| REQ-TASK | FR-02 | [TASK-01] | FULLY | 既読への反復で値を変えない実装と観測を記述 |
| REQ-TASK | FR-03 | [TASK-01] | FULLY | 不明IDの理由表示と全値の保持を記述 |
| REQ-TASK | NFR-01 | [TASK-02] | FULLY | 指定条件の表示時間測定・必要な調整・個別値とp95の記録を記述 |
| REQ-TASK | NFR-02 | [TASK-01] | FULLY | 操作情報を外部へ送らず、通信を観測する範囲を記述 |
| REQ-CHECK | FR-01 | [CHECK-01] | FULLY | 対象と他の本・書名を操作前後で比較する仕様 |
| REQ-CHECK | FR-02 | [CHECK-02] | FULLY | 反復操作の前後で件数・書名・既読状態を比較する仕様 |
| REQ-CHECK | FR-03 | [CHECK-03] | FULLY | 不明IDの理由表示と全値保持を観測する仕様 |
| REQ-CHECK | NFR-01 | [CHECK-05] | FULLY | 環境・データ・回数・計測区間・p95集計・閾値を指定した仕様 |
| REQ-CHECK | NFR-02 | [CHECK-04] | FULLY | 操作中の外部送信の有無を通信一覧で観測する仕様 |

## mapping

| edge_id | requirement_id | downstream_id | evidence | mapping_status |
|---|---|---|---|---|
| REQ-TASK | FR-01 | TASK-01 | implementation-plan.md TASK-01の要求参照・対象だけを既読にする作業 | SUBSTANTIVE |
| REQ-TASK | FR-02 | TASK-01 | implementation-plan.md TASK-01の要求参照・反復時に値を保持する作業 | SUBSTANTIVE |
| REQ-TASK | FR-03 | TASK-01 | implementation-plan.md TASK-01の要求参照・不明IDの理由表示と値保持 | SUBSTANTIVE |
| REQ-TASK | NFR-01 | TASK-02 | implementation-plan.md TASK-02の要求参照・CHECK-05条件と性能記録 | SUBSTANTIVE |
| REQ-TASK | NFR-02 | TASK-01 | implementation-plan.md TASK-01の要求参照・非送信とCHECK-04への対応 | SUBSTANTIVE |
| REQ-CHECK | FR-01 | CHECK-01 | verification-spec.md CHECK-01の明示参照・対象と他の値の比較 | SUBSTANTIVE |
| REQ-CHECK | FR-02 | CHECK-02 | verification-spec.md CHECK-02の明示参照・反復の前後比較 | SUBSTANTIVE |
| REQ-CHECK | FR-03 | CHECK-03 | verification-spec.md CHECK-03の明示参照・理由と値保持の観測 | SUBSTANTIVE |
| REQ-CHECK | NFR-01 | CHECK-05 | verification-spec.md CHECK-05の明示参照・計測条件と期待値 | SUBSTANTIVE |
| REQ-CHECK | NFR-02 | CHECK-04 | verification-spec.md CHECK-04の明示参照・操作期間の通信観測 | SUBSTANTIVE |

evidence欄は説明用文書の記載箇所であり、実行結果の証跡ではない。

## orphan

| edge_id | downstream_id |
|---|---|

0行。方法: 各下流母集合の全IDから、mappingのSUBSTANTIVEな対応先ID集合を引く。
REQ-TASKは{TASK-01,TASK-02}−{TASK-01,TASK-02}=空、REQ-CHECKも全5件−対応先全5件=空。

## edge_summary

| edge_id | coverage_pct | uncovered_count | orphan_count | coverage_status |
|---|---|---|---|---|
| REQ-TASK | 100 | 0 | 0 | COMPLETE |
| REQ-CHECK | 100 | 0 | 0 | COMPLETE |

被覆率は各edgeで100×(FULLY 5件＋PARTIALLY 0件)/要求5件=100%。

## overall_summary

| overall_coverage_status | assessment_basis | artifact_conformance | core_score | assessment_ref | inv_breakdown |
|---|---|---|---|---|---|
| COMPLETE | SELF_CHECK | NOT_EVALUATED | null | null | [{"edge_id":"REQ-TASK","inv_id":"INV-01","score":null},{"edge_id":"REQ-TASK","inv_id":"INV-02","score":null},{"edge_id":"REQ-TASK","inv_id":"INV-03","score":null},{"edge_id":"REQ-TASK","inv_id":"INV-04","score":null},{"edge_id":"REQ-TASK","inv_id":"INV-05","score":null},{"edge_id":"REQ-TASK","inv_id":"INV-06","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-01","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-02","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-03","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-04","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-05","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-06","score":null}] |

6表の記入がそろった例でも、正式採点をしていないため成果物はnon-final。
COMPLETEはこの合成入力の文書間被覆だけを示し、実装完了・テスト成功・承認・工程遷移を意味しない。
