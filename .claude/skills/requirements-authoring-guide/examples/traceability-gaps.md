# 記入例: 部分被覆・未被覆・孤児を残す6表

**説明専用・non-final・未実行。** audit_mode=authoring、audit_edges=[REQ-TASK, REQ-CHECK]。
要求は[要件例](requirements.md)の全5件。下流は下記の変種だけを使い、完成例の項目を黙って補わない。

## タスク母集合

- **TASK-01-P**（参照: FR-01、FR-02、NFR-02）: b1を既読にし、既読対象への反復で全値を維持し、
  操作情報を外部へ送らない。FR-01の「他の本の状態と全書名を保持する」実装・確認は記述がない。
  FR-03の不明IDへの応答も記述がない。
- **TASK-02**（参照: NFR-01）: [元のTASK-02](implementation-plan.md)と同じ性能計測・調整・記録を行う予定。
- **TASK-X**（要求参照なし）: 見出し色を青へ変更する。これに対応する要求は入力にない。

## 検証仕様母集合

- **CHECK-01**（FR-01）、**CHECK-02**（FR-02）、**CHECK-04**（NFR-02）、**CHECK-05**（NFR-01）は
  [検証仕様](verification-spec.md)の同名項目と同じ内容。
- **CHECK-03-P**（FR-03）: 存在しないIDに対して理由が表示されることだけを確認する。
  操作前後のリストが不変かは確認しない。

## edge_manifest

| edge_id | requirement_universe | downstream_universe | requirement_input_state | downstream_input_state | requirement_count | downstream_count |
|---|---|---|---|---|---|---|
| REQ-TASK | requirements.md | traceability-gaps.md#タスク母集合 | PRESENT | PRESENT | 5 | 3 |
| REQ-CHECK | requirements.md | traceability-gaps.md#検証仕様母集合 | PRESENT | PRESENT | 5 | 5 |

## requirement_coverage

| edge_id | requirement_id | downstream_ids[] | status | status_rationale |
|---|---|---|---|---|
| REQ-TASK | FR-01 | [TASK-01-P] | PARTIALLY | 対象の既読化はあるが他の本と書名を保持する内容がない |
| REQ-TASK | FR-02 | [TASK-01-P] | FULLY | 反復時の全値保持を記述 |
| REQ-TASK | FR-03 | [] | UNCOVERED | 不明IDの理由表示・値保持を実装するタスクがない |
| REQ-TASK | NFR-01 | [TASK-02] | FULLY | 元のTASK-02と同じ測定・調整・記録の予定 |
| REQ-TASK | NFR-02 | [TASK-01-P] | FULLY | 操作情報を外部へ送らない作業を記述 |
| REQ-CHECK | FR-01 | [CHECK-01] | FULLY | 元のCHECK-01と同じ前後比較 |
| REQ-CHECK | FR-02 | [CHECK-02] | FULLY | 元のCHECK-02と同じ反復の前後比較 |
| REQ-CHECK | FR-03 | [CHECK-03-P] | PARTIALLY | 理由表示だけを扱いリストの値保持を確認しない |
| REQ-CHECK | NFR-01 | [CHECK-05] | FULLY | 元のCHECK-05と同じ性能観測 |
| REQ-CHECK | NFR-02 | [CHECK-04] | FULLY | 元のCHECK-04と同じ通信観測 |

## mapping

| edge_id | requirement_id | downstream_id | evidence | mapping_status |
|---|---|---|---|---|
| REQ-TASK | FR-01 | TASK-01-P | 本文のTASK-01-PにFR-01と対象の既読化の明示あり。保持の側面は欠ける | SUBSTANTIVE |
| REQ-TASK | FR-02 | TASK-01-P | 本文のTASK-01-PにFR-02と反復時の全値保持の明示あり | SUBSTANTIVE |
| REQ-TASK | NFR-01 | TASK-02 | 本文のTASK-02がNFR-01と元の性能計測・調整・記録を明示参照 | SUBSTANTIVE |
| REQ-TASK | NFR-02 | TASK-01-P | 本文のTASK-01-PにNFR-02と非送信の明示あり | SUBSTANTIVE |
| REQ-CHECK | FR-01 | CHECK-01 | 本文のCHECK-01がFR-01と元の前後比較を明示参照 | SUBSTANTIVE |
| REQ-CHECK | FR-02 | CHECK-02 | 本文のCHECK-02がFR-02と元の反復比較を明示参照 | SUBSTANTIVE |
| REQ-CHECK | FR-03 | CHECK-03-P | 本文のCHECK-03-PにFR-03と理由表示の明示あり。値保持は欠ける | SUBSTANTIVE |
| REQ-CHECK | NFR-01 | CHECK-05 | 本文のCHECK-05がNFR-01と元の性能観測を明示参照 | SUBSTANTIVE |
| REQ-CHECK | NFR-02 | CHECK-04 | 本文のCHECK-04がNFR-02と元の通信観測を明示参照 | SUBSTANTIVE |

SUBSTANTIVEは実際に要求の側面を扱う対応である。要求全体が満たされるかはrequirement_coverageで分ける。
記述のない対応を完成例から借りて加算しない。

## orphan

| edge_id | downstream_id |
|---|---|
| REQ-TASK | TASK-X |

方法: 下流全IDからSUBSTANTIVEな対応先を引く。タスクは3件−{TASK-01-P,TASK-02}={TASK-X}、
検証仕様は全5件−対応先全5件=空。

## edge_summary

| edge_id | coverage_pct | uncovered_count | orphan_count | coverage_status |
|---|---|---|---|---|
| REQ-TASK | 80 | 1 | 1 | INCOMPLETE |
| REQ-CHECK | 100 | 0 | 0 | INCOMPLETE |

REQ-TASKは100×(FULLY 3件＋PARTIALLY 1件)/5=80%。REQ-CHECKは100×(4＋1)/5=100%でも、
PARTIALLYが残るためINCOMPLETE。未被覆件数はUNCOVEREDだけを数え、部分被覆を黙って完了へ変えない。

## overall_summary

| overall_coverage_status | assessment_basis | artifact_conformance | core_score | assessment_ref | inv_breakdown |
|---|---|---|---|---|---|
| INCOMPLETE | SELF_CHECK | NOT_EVALUATED | null | null | [{"edge_id":"REQ-TASK","inv_id":"INV-01","score":null},{"edge_id":"REQ-TASK","inv_id":"INV-02","score":null},{"edge_id":"REQ-TASK","inv_id":"INV-03","score":null},{"edge_id":"REQ-TASK","inv_id":"INV-04","score":null},{"edge_id":"REQ-TASK","inv_id":"INV-05","score":null},{"edge_id":"REQ-TASK","inv_id":"INV-06","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-01","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-02","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-03","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-04","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-05","score":null},{"edge_id":"REQ-CHECK","inv_id":"INV-06","score":null}] |

最高重大度のgapとして、FR-03の未被覆、TASK-Xの孤児、FR-01とFR-03の不足側面を上流へ返す。
TASK-Xに存在しない要求を付けず、足りない作業を実施済みとも扱わない。正式採点なしのnon-finalであり、工程遷移を開かない。
