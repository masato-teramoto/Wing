# 記入例: 下流入力がMISSINGの6表

**説明専用・non-final・未実行。** audit_mode=authoring、audit_edges=[REQ-CHECK]。
この変種で利用できるのは[要件例](requirements.md)の5件だけで、対象の検証仕様は未入手という入力設定である。
同梱の完成例の検証仕様は別の例であり、この変種の入力を代用しない。
「未入手」は、確認した結果「検証仕様が存在しない」と判明した状態とは異なる。

## edge_manifest

| edge_id | requirement_universe | downstream_universe | requirement_input_state | downstream_input_state | requirement_count | downstream_count |
|---|---|---|---|---|---|---|
| REQ-CHECK | requirements.md | null | PRESENT | MISSING | 5 | null |

## requirement_coverage

| edge_id | requirement_id | downstream_ids[] | status | status_rationale |
|---|---|---|---|---|

0行。MISSINGを含むedgeの要求をUNCOVEREDやFULLYと決めない。

## mapping

| edge_id | requirement_id | downstream_id | evidence | mapping_status |
|---|---|---|---|---|

0行。対応を推測しない。

## orphan

| edge_id | downstream_id |
|---|---|

0行。ただし孤児0件を確認した意味ではない。下流母集合が未入手なので計数不能。

## edge_summary

| edge_id | coverage_pct | uncovered_count | orphan_count | coverage_status |
|---|---|---|---|---|
| REQ-CHECK | null | null | null | UNDETERMINED |

## overall_summary

| overall_coverage_status | assessment_basis | artifact_conformance | core_score | assessment_ref | inv_breakdown |
|---|---|---|---|---|---|
| UNDETERMINED | SELF_CHECK | NOT_EVALUATED | null | null | [{"edge_id":"REQ-CHECK","inv_id":"INV-01","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-02","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-03","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-04","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-05","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-06","score":null}] |

観測できた要求件数5は残す。被覆率を0%・100%へ、未被覆・孤児を0件へ置き換えない。
不足入力は検証仕様の全IDと実内容。入手後に母集合を確認して対応を作る。現時点では被覆完了も工程遷移も主張しない。
