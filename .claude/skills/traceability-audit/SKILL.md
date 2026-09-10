---
name: traceability-audit
description: 要求→下流（タスク／実装／テスト）の被覆関係を監査し、被覆マトリクスと被覆報告を成果物として出すとき、または提出された被覆成果物の品質を判定するときに使う。文書間の被覆関係に限定する——文書単体の完成度判定、要求記述そのものの品質、タスク分割の妥当性は対象外。
metadata:
  l2-compiled-from: "KA-REF-023@0.1.0, CT-REF-011@0.4.2"
  l2-compiled-at: "2026-08-27"
---

> 本ファイルはビルド成果物（SSOT は `assets/`）。**手編集禁止** — 直すときは資産カードを直して再コンパイルする。
> 構成カード・Contract は**内部judge校正済（未レビュー）**（`/loop-calibrate` 二層ゲート充足）。カード本文は人間レビュー済み。
> **実務妥当性・実案件での有効性は保証しない。**
> 末尾の validation は**成果物の自己チェック専用**であり、消費先のドキュメント状態（`status` 等）に影響しない。
> **判定ハーネス（verifier）と Contract 本体は同梱されない。**

# traceability-audit — 要求↔下流の被覆監査

## 使い方

被覆の両端（要求側の ID 一覧・下流側の項目一覧）を自分で読み、対応関係を作るか検査して、**被覆マトリクスと
被覆報告**を成果物として出す。散文で「カバーできている」と述べるのではなく、表として物質化する。
未被覆・孤児が見つかった場合は最高重大度で正直に報告し、**要求に接続しない埋め草の下流項目を発明して
塞がない**——上流（要求・設計・計画）へ差し戻す。

被覆の対応づけは**安定 ID による明示参照**だけを認める。別名の発明・記述的ラベル・訳語つき参照は写像として
数えない。ID を持たない要求は写像不能として上流に差し戻す。

## 起動時に確定する2項目（dispatch）

以下は依頼者の明示指定を優先し、明示がなければ対象成果物から一意に判定できる場合のみ自動で決める。
**一意に判定できないときは質問して停止する**（推測で走らない）。

- **audit_mode** — `authoring`（被覆成果物をこれから作る）／`review`（提出済みの被覆成果物を判定する）。
- **audit_edges** — 監査する要求→下流の対（例: 要求→実装タスク・要求→受入テスト）。複数指定できる。
  各 edge について、両端入力の状態を次の3値のいずれかで宣言する:
  - **PRESENT** — 入力が得られ、内容がある
  - **CONFIRMED_EMPTY** — 存在しないことを確認した（「無いと確認した」）
  - **MISSING** — 入力が得られていない（「まだ手元にない」）

  この2つは相互に代替しない。**MISSING を宣言した edge について、写像・被覆率・完了状態のいずれかを主張しては
  ならない**（宣言と主張の自己矛盾は虚偽報告として扱われる）。状態宣言と実際に観測できる入力が食い違う場合も
  同様に虚偽報告として扱われる。

## 監査の規範

- **全数被覆**: すべての要求（機能要求・受入基準・シナリオ）が、最低1つの下流項目に明示 ID 参照で対応づく。
  複数の下流項目が部分的に触れるだけでどれも完結しない要求も gap として検出する。
- **双方向**: 要求→下流だけでなく、逆方向（どの要求にも対応しない下流項目＝孤児）も検査する。被覆率が
  100% でも孤児は独立の gap である。報告には検査の**方法**（例: 下流の全 ID − 被参照 ID）または
  **該当リスト**を必ず含める。「点検した」「問題は見当たらない」だけの言明は方法の明示に当たらない。
- **実質性**: 「被覆」と計上する各対応は、下流項目が当該要求の挙動を明示的に扱っていること。関連領域への
  傍論的な言及・暗黙の含意・同一ファイルの別側面をもって被覆と数えない。
- **物質化**: 要求 ID × 下流 ID の対応表を独立した表・ファイルとして生成する。必須要素は要求キー・対応する
  下流項目・被覆状態。
- **数値報告**: 被覆率（%）・未被覆件数・孤児件数を数値で報告し、その数値がマトリクスの実態と一致すること。
  比率は被覆率だけでなく孤児率も分母を明示し、再計算して突合する。
- **正直な gap 報告**: 未被覆・孤児は最高重大度相当の所見として明示する。完全被覆を装わない。修復は反復
  上限つきで回し、上流の実質的な欠落が露呈した場合は埋め草を発明せず差し戻す（反復上限の具体値は
  プロジェクトで決める）。

## 出力（被覆成果物の物理形式）

`authoring` では次の6表を **canonical な列名で**出力する。値が無いことを表すときは空文字でなく literal `null`
を置く。`review` では提出物が同等の情報を持つかを見る（列名の一致までは求めず、同等名を許容する）。

| 表 | キーと必須列 |
|---|---|
| `edge_manifest` | `(edge_id)`＋`requirement_universe`・`downstream_universe`（各母集合への参照）・`requirement_input_state`・`downstream_input_state`（`PRESENT` / `CONFIRMED_EMPTY` / `MISSING`）・`requirement_count`・`downstream_count`。**件数は各側の状態に従う**（`PRESENT` → `> 0` ／ `CONFIRMED_EMPTY` → `0` ／ `MISSING` → `null`）。宣言した全 edge が必ず1行 |
| `requirement_coverage` | `(edge_id, requirement_id)`＋`downstream_ids[]`・`status`（`FULLY` / `PARTIALLY` / `UNCOVERED`）・`status_rationale` |
| `mapping` | `(edge_id, requirement_id, downstream_id)`＋`evidence`・`mapping_status`（`SUBSTANTIVE` / `TANGENTIAL_REJECTED`） |
| `orphan` | `(edge_id, downstream_id)` |
| `edge_summary` | `(edge_id)`＋`coverage_pct`・`uncovered_count`・`orphan_count`・`coverage_status` |
| `overall_summary` | `overall_coverage_status`・`assessment_basis`・`artifact_conformance`・`core_score`・`assessment_ref`・`inv_breakdown` |

**`coverage_pct`（上から順に評価し、最初に該当した値。0〜100 のパーセント値）**:

```
① requirement_input_state = MISSING ∨ downstream_input_state = MISSING           → null
② requirement_input_state = CONFIRMED_EMPTY                                       → null（分母0＝意味上の N/A）
③ requirement_input_state = PRESENT ∧ downstream_input_state = CONFIRMED_EMPTY    → 0
④ 両側 PRESENT → 100 × (FULLY 件数 ＋ PARTIALLY 件数) / requirement_count
```

`uncovered_count` は `UNCOVERED` 件数、`orphan_count` は `orphan` 表の行数。**`PARTIALLY` は被覆率の分子に
算入するが `COMPLETE` を阻む**。孤児率を併記する場合は分母（全下流件数か写像済み件数か）を明示する。

**`coverage_status`（上から順に評価し、最初に該当した値）**:

```
① requirement_input_state = MISSING ∨ downstream_input_state = MISSING
   ∨ (両側とも CONFIRMED_EMPTY)                                    → UNDETERMINED
② requirement_count > 0 ∧ 全要求 status = FULLY ∧ orphan_count = 0 → COMPLETE
③ それ以外                                                          → INCOMPLETE
overall_coverage_status: INCOMPLETE ＞ UNDETERMINED ＞ COMPLETE
```

**MISSING を含む edge の扱い**: `requirement_coverage`・`mapping`・`orphan` に当該 edge の行を作らない（空）。
`uncovered_count`・`orphan_count`・`coverage_pct` は `null`（**入力側の件数は各側の状態に従うので、
観測できている側の件数は消さない**）。下記の整合検査は**両端が non-MISSING の edge にのみ**適用する。

**`assessment_basis`（成果物適合をどの根拠で出したか。必須）**:

- `SELF_CHECK` — 本パックの validation を自己チェックとして適用しただけの状態。**`artifact_conformance` は
  `NOT_EVALUATED`**、`core_score` は `null`、`assessment_ref` は `null`、成果物は **non-final** と明示し、
  **工程遷移ゲートを開かない**。判定ハーネス（verifier）と Contract 本体が手元に無い場合は必ずこちらになる。
- `FORMAL` — Contract 本体と判定ハーネスによる 0/5/10/N/A の採点と正式 verdict がある状態。
  `artifact_conformance` に正式 verdict（`PASS` / `WARN` / `FAIL` / `NOT_APPLICABLE`）を入れる。
  **FORMAL を名乗れるのは次をすべて満たすときに限る**: (a) 出力が本節の形式に適合し整合検査が PASS
  (b) `assessment_ref` が解決可能で、`verifier_run_ref` が**当該成果物**を採点した run に対応している
  （別成果物・Contract の校正 run の流用は不可） (c) `contract_ref` の version が判定時の現行 Contract version と
  一致し、その Contract が `status: validated` である（draft の Contract で FORMAL は名乗れない）。
  FORMAL で全セルが N/A の場合は `artifact_conformance = NOT_APPLICABLE`・`core_score = null`。

`NOT_EVALUATED`（**採点していない**）と `NOT_APPLICABLE`（採点した結果、適用可能な検査項目が一つも
無かった）は別の値であり、相互に代替しない。

**`assessment_ref`** は `{contract_ref, verifier_run_ref}` の構造を持つ（`SELF_CHECK` では `null`）。
**`inv_breakdown`** は `(edge_id, inv_id)` をキーとし `score`（`0`/`5`/`10`/`null`）を必須列とする。行は
`FORMAL` では **audit_edges × Contract の検査項目集合**、`SELF_CHECK` では **audit_edges × 本パックの
validation 項目集合**を**過不足・重複なく**満たすこと（評価しなかったセルも `score = null` の行として置く。
行の欠落による暗黙の除外を禁じる）。`score = null` の意味は `assessment_basis` に依存し、`FORMAL` では
採点結果の N/A、`SELF_CHECK` では未採点（`NOT_EVALUATED`）を表す。

**工程遷移条件（論理積）**:

```
遷移可 ⇔ assessment_basis = FORMAL ∧ artifact_conformance = PASS ∧ overall_coverage_status = COMPLETE
```

**整合検査（両端 non-MISSING の edge ごと・決定的）**: `requirement_coverage` の要求 ID 集合＝
`requirement_universe`／`mapping` の両 ID が当該 edge の母集合に属する／`requirement_coverage.downstream_ids[]`
＝`mapping_status = SUBSTANTIVE` の集合／`UNCOVERED` ⇔ `SUBSTANTIVE` が空／`orphan`＝`downstream_universe` −
`SUBSTANTIVE` な対応先／全表の主キーに重複なし／`edge_manifest` の edge 集合＝宣言した audit_edges／
件数と `input_state` の対応（`PRESENT`→`>0`・`CONFIRMED_EMPTY`→`0`・`MISSING`→`null`）／
`coverage_pct`・`coverage_status`・集計の再計算が一致。

## review mode の成果物（補完しない）

`review` では、提出された被覆成果物を**判定するだけ**であり、欠けている表を埋めたり、写像を作り直したり、
成果物を再生成したりしない。返すのは次の3つに限る。

- `overall_summary`（`overall_coverage_status`・`assessment_basis`・`artifact_conformance`・`core_score`）
- edge × 検査項目の判定（`inv_breakdown`）
- 欠落・不整合の一覧（どの表・どの列・どの edge が欠けているか、整合検査のどれに違反したか）

**提出値を書き換えない**——`status_rationale` を含め、判定者の見解が提出値と食い違う場合は上書きせず
**不整合として一覧に返す**。不足を補って判定を成立させることは、提出物の品質を偽装することにあたる。

## 二層の出力（混同しない）

- **成果物適合（artifact_conformance）** — 被覆成果物そのものが監査に耐える品質かの判定（下記 validation の
  Contract 由来）。**gap の存在は不合格事由ではない**。正直に報告された未被覆・孤児は適合を損なわない。
  `assessment_basis = SELF_CHECK` のときは正式判定を出さず `NOT_EVALUATED` とする。
- **被覆状態（coverage_status）** — 対象プロジェクトの被覆の実態（COMPLETE／INCOMPLETE／UNDETERMINED）。

工程遷移の判断材料に使うのは後者であり、**COMPLETE 以外は遷移不可の材料**として扱う。前者が PASS でも
後者が INCOMPLETE ならゲートは開かない。逆に後者が INCOMPLETE でも、正直に報告されていれば前者は PASS たりうる。

## 複数 edge をまとめて監査するとき

- 検査項目の「全要求」「全対応」は **edge 単位**で評価する。
- 検査項目ごとに、適用可能な edge の中で**最も低いスコアを採る**（平均ではない。最弱の edge が律速する）。
- 評価対象が存在しないセル（入力欠落による評価不能／確認済み空集合による構造的非適用）は採点母数から
  除外する。ある検査項目の適用 edge がすべて除外なら、その項目自体を母数から外す。
- **すべての検査項目が母数から外れた場合、判定は「非適用」で終える**（合格を出さない・中立終端）。
- **いずれか1つの edge で重大逸脱（虚偽報告・被覆偽装・不物質化）が該当すれば、束全体を不合格**とする。
  他の edge が良好でも希釈されない。重大逸脱の判定は非適用の集計に**先行**する。

## 関連パックへの引き継ぎ

- 要求・受入基準・NFR・スコープの**記述そのもの**を作る／直す作業は本パックの範囲外。作成側の規範は
  `requirement-authoring-core` が持つ。未導入の場合は、被覆監査の所見として「要求記述側の欠落」を報告し、
  記述の代筆はしない。
- 要件定義文書の**壁打ち・観点レビュー**（受入基準・NFR・スコープ・完成度の検出）は
  `requirement-sparring-generic` が持つ。本パックが文書単体の完成度ゲート判定に触れる必要が生じたときは
  そちらへ redirect する。未導入の場合は、被覆に関する所見のみを出し、完成度判定は行わない。
- 監査結果を受けて**受入判定（承認／差し戻し）**を出す工程は `acceptance-review` へ handoff する。本パックの
  成果物は被覆マトリクス・被覆報告・被覆状態であり、受入 verdict ではない。未導入の場合は、判定に必要な
  材料（所見・重大度・被覆状態）を揃えて明示的に引き渡し、承認の可否は依頼元の人間に委ねる。
- 正式な採点（0/5/10・Critical Fail・合格閾値）が必要で、判定ハーネス（verifier）と Contract 本体が
  未導入の場合は、**採点を代行せず導入要求を出して停止する**。

## validation（CT-REF-011 の INV/DEV チェックリスト）

成果物の自己チェックに使う。**本判定は消費先のドキュメント状態に影響しない。判定ハーネスと Contract 本体は
同梱されない。**

- [ ] **INV-01** 要求側の全 ID が、下流項目の安定 ID による明示参照で最低1件に写像されている
      （別名・記述ラベル・訳語参照は写像と認めない）
- [ ] **INV-02** 逆方向（孤児）検査が実施され、結果（有無＋方法または該当リスト）が報告に明示されている
      （「点検した」等の曖昧な言明は方法に当たらない。孤児0でも方法・リストを欠けば減点）
- [ ] **INV-03** 被覆マトリクスが散文でなく独立の表・成果物として物質化され、必須要素を持つ
- [ ] **INV-04** 被覆率・未被覆件数・孤児件数が数値で報告され、マトリクスの実態と一致している
      （比率は分母を再計算して突合する。孤児率の分母取り違えは軽微不整合）
- [ ] **INV-05** 「被覆」と計上した各対応が実質を持つ（傍論的言及・暗黙の含意・別側面の被覆を数えていない）
- [ ] **INV-06** 未被覆・孤児がある場合、最高重大度相当で明示し、埋め草で塞いでいない（gap がなければ非適用）

**DEV（該当すれば Critical Fail）**: マトリクス上に写像が無い要求が実在するのに完全被覆を主張（DEV-01・
分母0 や入力欠落を「100%」と報告する場合を含む）／形式上の写像はあるが実質を欠く計上（DEV-02）／
対応表が存在せず散文の主張のみ（DEV-03）

採点は各 INV を 0 / 5 / 10（適用外の INV は N/A として分母から除外）。複数 edge では検査項目ごとに
適用 edge の最小値を採り、その平均を採点値（`core_score`）とする。**verdict は次の優先順で決める**:

```
DEV あり → FAIL ＞ 全 INV が N/A → NOT_APPLICABLE ＞ 平均 7.0 以上 → PASS ＞ その他 → WARN
```

`WARN` は「重大逸脱は無いが合格水準に達していない」出口であり、`PASS` としても `FAIL` としても扱わない。
詳細な採点規則・N/A 規則・複数 edge の集約規則は Contract 本体（同梱されない）を参照。
**正式な採点が必要で Contract 本体と判定ハーネスが未導入の場合は、`assessment_basis = SELF_CHECK` として
`artifact_conformance = NOT_EVALUATED` を返し、採点を代行しない。**

## 適用範囲外

- 文書単体の完成度判定（ゲートレポートの品質）— 別 Contract の領分。境界: ゲート＝文書単体 / 本パック＝文書間の被覆関係
- 要求記述そのものの品質（受入基準・NFR・スコープの書き方）— `requirement-authoring-core` の領分
- タスク分割の粒度・実装計画の妥当性 — 別資産の領分
- 被覆修復ループの反復上限・収束条件の具体値 — プロジェクトの決定事項
- 被覆対象の選別基準（何を被覆母数に入れるか）— 既定では母数を絞らない。選別が必要な案件は明示的に決める
- 抽出／導出の分業パイプライン等、被覆成果物を作る**プロセス**の設計 — 本パックは成果物のみを見る

---

provenance: KA-REF-023@0.1.0 / CT-REF-011@0.4.2 ｜ 元 OSS ライセンス: MIT（cc-sdd・BMAD-METHOD・spec-kit・
OpenSpec・awesome-copilot spec-driven-workflow） / Apache-2.0（awesome-copilot quality-playbook-requirements_pipeline）
｜ compiled_at: 2026-08-27。詳細は同梱 PROVENANCE.md。
