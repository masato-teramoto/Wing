# PROVENANCE — spec-change-proposal（仕様変更提案パック・S4）

- compiled_at: 2026-09-01 ／ compose 実行: /loop-compose operation spec-change-proposal --include-draft
- 位置づけ: 要求・要件定義フェイズ Skill 一式（選定案 rev78）の **S4**。P3 execution の対象で、
  **§3 P の2キー（`change_format_profile`・`deferred_slots_extended`）を両方持つ唯一のパック**。
- 再コンパイル条件: compiled_from の各カードの version・status が変わったら再生成（/loop-report が検出）。
  **本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）。

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-041 | 0.1.0 | draft | authoritative | null |
| KA-REF-055 | 0.1.0 | draft | advisory | null |

（KA が contract を持たない場合は null と記す。CT は本パックに無い＝Contract 未紐付け）

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-041 変更仕様のデルタマーカー規約 | 0.1.0 | draft | community-consensus | volatile / 2027-02-08 | 使い方・変更の分類・方言別の描画・変更の重大度・提案文書の構成 | K-01〜K-05、SO-09 を収載。SO-02〜SO-05 は `openspec` 条件、SO-08 は `bmad` 条件で advisory 収載 |
| KA-REF-055 変更提案の影響分析手順 | 0.1.0 | draft | community-single | volatile / 2027-03-08 | 使い方・変更の重大度・影響分析・提案文書の構成・BMAD profile の経路評価 | A-01・A-03・A-05〜A-09を収載。A-04 は `bmad` 条件で収載。A-02・A-10は非収載 |

### KA-REF-041 SO 全件の選定状態

| SO | 状態 | 反映先・条件または非収載理由 |
|---|---|---|
| SO-01 | 非収載 | archive 時のマージアルゴリズムは本パックの提案作成・レビュー範囲を越える |
| SO-02 | 条件付き収載 | `change_format_profile=openspec`。Scenario・見出し・task checkbox の厳密書式 |
| SO-03 | 条件付き収載 | `change_format_profile=openspec`。ADDED は新関心事、MODIFIED は既存挙動変更に限定 |
| SO-04 | 条件付き収載 | `change_format_profile=openspec`。名前だけの変更を FROM:/TO: で記述 |
| SO-05 | 条件付き収載 | `change_format_profile=openspec`。実装詳細だけの変更を delta spec へ入れない |
| SO-06 | 非収載 | proposal/spec/design/tasks の4成果物分離は本パック単体の成果物範囲を越える |
| SO-07 | 非収載 | Minor/Moderate/Major の固定分類と担当者 routing は案件体制に依存 |
| SO-08 | 条件付き収載 | `change_format_profile=bmad`。3経路を工数・リスクと Viable/Not viable で比較して選定 |
| SO-09 | 収載 | 変更の重大度。トリガと具体的証拠が無ければ影響分析へ進まない |
| SO-10 | 非収載 | sprint-status 固有の台帳同期は下流運用に依存 |

### KA-REF-055 の条件付き収載

| 項目 | 状態 | 反映先・条件または非収載理由 |
|---|---|---|
| A-04 | 条件付き収載 | `change_format_profile=bmad`。選定理由を5軸で走査し Hybrid を許容 |
| A-02 | 非収載 | 固定の変更トリガ5分類は提案作成の常設前提にしない |
| A-10 | 非収載 | Incremental/Batch のレビュー UI は案件の運用様式 |

- 条件付き収載は既存 dispatch の観測可能条件に接続するだけで、runtime selector を新設しない。
- SO-02〜SO-05、SO-08、A-04 は利用者指示 2026-09-01 と選定案 rev78 による advisory。

- **強度の境界（本パック固有）**: カード由来の知識は全項 **advisory＝【SHOULD】**。
  **project profile から解決した案件制約（`deferred_slots_extended` が effective のときの DEFERRED 拡張2欄）は当該成果物に対して必須**。
  SKILL.md 冒頭のバッジ節に同じ境界を明記している。
- **dispatch 節は選定案 §3 P v1.2.0 由来のローカル合成規則**であり、新しい資産カードを持たない
  （形式 signature の具体・profile の観測状態・緩和承認の A 案は P 契約が正）。
- `activate_specializations` による選択的活性化は P3 では未導入。上表の収載は静的または既存 dispatch に
  よる条件付き advisory であり、Contract の合否条件を増やさない。
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率等の評価数値を転記していない。

## バッジ（共通規律2）

- `draft_badge` = **true**（KA-REF-041・KA-REF-055 とも status: draft）。SKILL.md 冒頭に DRAFT 印あり。
- `pack_advisory` = **true**（KA-REF-055 が supply_mode: advisory ／ KA-REF-041 は authoritative かつ
  contract: null ＝未検証権威）。全称形の advisory 宣言に加え、**カード1枚1行の強度ブロック**を持つ
  （export-policy §2 規則4）。

### カード別の軸（status / review_status / supply_mode / contract）

| カード | status | review_status | supply_mode | contract | 本パックでの供給強度 |
|---|---|---|---|---|---|
| KA-REF-041 | draft | 未記載（schema 既定＝unreviewed） | authoritative | null | advisory（export-policy §2 規則4＝未検証権威の遮断） |
| KA-REF-055 | draft | 未記載（schema 既定＝unreviewed） | advisory | null | advisory（カード宣言のまま） |

- **4軸は独立**（asset.schema.md・2026-07-09 人間裁定）: `status`＝カードの校正ライフサイクル／
  `review_status`＝カード本文の人間レビュー（**無記載＝unreviewed** が schema 既定）／`supply_mode`＝利用時の
  強度／`evidence_strength`・案件回帰＝実務上の根拠。SKILL.md の DRAFT 印は **status 軸だけ**を示す。
- **draft のままである理由**: カードの `draft→validated` の**唯一のトリガは host Contract の validated 昇格**
  （PROFILE.md「カード昇格規則」2026-07-08 人間裁定）。`contract: null` の間は昇格の契機が無い。
  Contract 接続の予定が無いカードは実質的に draft が継続する——**カード本文の不備を意味しない**。
- **`validated` でも実務妥当性は保証されない**（CLAUDE.md「validated の意味」2026-07-09 明文化。judge 運用上の
  自律可能性のみを意味する）。したがって実務妥当性の留保は DRAFT 固有の警告ではなく、SKILL.md では
  **ADVISORY の位置づけ**として利用者の行動（案件の前提・規約・制約と照合／正式な合否判定の根拠にしない）へ
  翻訳して示す。

## 元 OSS ライセンス（帰属・NOTICE 引継ぎ）

| 上流 | ライセンス | 経由カード |
|---|---|---|
| Fission-AI/OpenSpec | MIT | KA-REF-041 |
| bmad-code-org/BMAD-METHOD (v6) | MIT | KA-REF-041 / KA-REF-055 |

- 全ライセンスは MIT＝互換・再配布可。NOTICE ファイルは**原文になし**。版固定は factory/snapshots/oss/PROVENANCE.md。
- **非選定（BY-SA 隔離12枚・export-policy 規則1）の完全 ID**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 —— いずれも本パックに含まれず、隔離解除は法務確認の完了のみ（adr/0007 §1）。
- snapshots/・corpus/ の凍結原本は本パックに複製していない（export-policy 規則2）。

## 選定記録

- 選定基準: テーマ「仕様変更提案」に適合する2枚。KA-REF-041 が中核ゲート（分類・完全形・理由随伴・影響分析の
  存在要求）の SSOT、KA-REF-055 がその手順詳細（影響評価の被覆リスト・提案構成）。両者は `related_knowledge` で
  相互参照する対のため同梱した。
- **`--include-draft`**: status: draft の構成資産を含むため DRAFT 印を付して収載している。DRAFT は元資産の
  校正ライフサイクルを表し、Skill の出荷検査や実務妥当性の判定を表さない。
- 隣接カードの扱い: 要求記述側の規範（KA-REF-021 等）は `requirement-authoring-core` の領分につき非収載。
  被覆への影響は `traceability-audit` へ redirect（本文に ID を載せない一般化表現で記述）。
