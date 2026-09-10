# PROVENANCE — implementation-planning（実装計画パック・S5）

- compiled_at: 2026-08-28 ／ compose 実行: /loop-compose phase implementation-planning
- 位置づけ: 要求・要件定義フェイズ Skill 一式（選定案 rev33）の **S5**。P3 execution の対象で、
  dispatch は **mode-only**（project profile を読まない）。
- 再コンパイル条件: compiled_from のカードの version・status が変わったら再生成（/loop-report が検出）。
  **本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）。

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-029 | 0.1.0 | draft | authoritative | null |

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-029 実装計画・エピック分割規約 | 0.1.0 | draft | community-consensus | volatile / 2027-01-18 | 必須の文脈・ルールA〜C・review 時の出し方 | K-01（要求 ID の明記を含む）・K-02〜K-06。**具象は非収載**＝ステップ粒度の分数・タスク ID 書式（T001／[P]／[US1]）・Phase 構成 enum は「プロジェクトの決定事項」へ一般化した（賞味期限を持ち込まない）。SO-* は全件非収載 |

- **パス文脈の両 mode 必須**（不足時 authoring＝ブロッカー報告／review＝UNDETERMINED）は選定案 §2 の
  S5 規範（rev19 で復元）に由来する適用注記であり、新規 invariant ではない。
- `activate_specializations` による SO の選択的活性化は **P3 では未導入**（候補記録のみ）。
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率等の評価数値を転記していない。

## バッジ（共通規律2）

- `draft_badge` = **true**（KA-REF-029 は status: draft）。SKILL.md 冒頭に DRAFT 印あり。
- `pack_advisory` = **true**（authoritative かつ contract: null ＝未検証権威）。全称形の advisory 宣言に加え、
  **カード1枚1行の強度ブロック**を持つ（export-policy §2 規則4）。

### カード別の軸（status / review_status / supply_mode / contract）

| カード | status | review_status | supply_mode | contract | 本パックでの供給強度 |
|---|---|---|---|---|---|
| KA-REF-029 | draft | 未記載（schema 既定＝unreviewed） | authoritative | null | advisory（export-policy §2 規則4＝未検証権威の遮断） |

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
| obra/superpowers | MIT | KA-REF-029 |
| bmad-code-org/BMAD-METHOD (v6) | MIT | KA-REF-029 |
| github/spec-kit | MIT | KA-REF-029 |

- 全ライセンスは MIT＝互換・再配布可。NOTICE ファイルは**原文になし**。版固定は factory/snapshots/oss/PROVENANCE.md。
- **非選定（BY-SA 隔離12枚・export-policy 規則1）の完全 ID**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 —— いずれも本パックに含まれず、隔離解除は法務確認の完了のみ（adr/0007 §1）。
- snapshots/・corpus/ の凍結原本は本パックに複製していない（export-policy 規則2）。

## 選定記録

- 選定基準: テーマ「実装計画」に適合する1枚（KA-REF-029）。被覆の**監査成果物**は KA-REF-023 の領分に
  つき非収載——本文では `traceability-audit` への redirect と再監査 handoff として表現した。
- **`--include-draft` 相当**: status: draft のため DRAFT 印を付して収載（judge 校正前であることを明示）。
