# PROVENANCE — edge-case-enumeration（エッジケース列挙パック・S7）

- compiled_at: 2026-09-01 ／ compose 実行: /loop-compose operation edge-case-enumeration --include-draft
- 位置づけ: 要求・要件定義フェイズ Skill 一式（選定案 rev78）の **S7**。dispatch は **mode-only**
  （project profile を読まない）。
- 再コンパイル条件: compiled_from のカードの version・status が変わったら再生成（/loop-report が検出）。
  **本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）。

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-036 | 0.1.0 | draft | authoritative | null |

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-036 エッジケース列挙規約 | 0.1.0 | draft | community-consensus | volatile / 2027-03-08 | 起動時の明確化戻し・ルールA〜C・review 時の出し方 | K-01〜K-05に加え、SO-02（列挙値の残余）・SO-03（削除・置換二次パス）・SO-04（diff 範囲）・SO-07（曖昧要求の finding 化）を advisory 収載 |

### SO 全件の選定状態

| SO | 状態 | 反映先・条件または非収載理由 |
|---|---|---|
| SO-01 | 非収載 | 固定 JSON フィールドと語数上限は案件の出力契約に依存 |
| SO-02 | 収載 | ルールA。enum・status 等で変更されていない残余値も暗黙分岐として列挙 |
| SO-03 | 収載 | ルールA。削除・置換時に契約再確立、孤立参照、dead path を専用二次パスで走査 |
| SO-04 | 条件付き収載 | diff が与えられた場合、hunk と直接到達する未防護境界へ範囲を限定 |
| SO-05 | 非収載 | severity・risk の固定語彙は受入判定と案件規約に依存 |
| SO-06 | 非収載 | confidence の固定語彙・閾値は案件規約に依存 |
| SO-07 | 条件付き収載 | 要求が曖昧で列挙基準を一意に置けない場合、先に finding 化して明確化へ redirect |
| SO-08 | 非収載 | 要求 refinement の固定スロットは明確化パックと案件成果物に依存 |

- 収載4件は利用者指示 2026-09-01 と選定案 rev78 による advisory。固定スキーマ・severity 語彙は持ち込まない。

- `activate_specializations` による SO の選択的活性化は **P3 では未導入**。上表は静的または観測可能条件つきの
  advisory 収載であり、runtime selector・project profile 読取りを追加しない。
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率等の評価数値を転記していない。

## バッジ（共通規律2）

- `draft_badge` = **true**（status: draft）。SKILL.md 冒頭に DRAFT 印あり。
- `pack_advisory` = **true**（authoritative かつ contract: null ＝未検証権威）。全称形の advisory 宣言に加え、
  **カード1枚1行の強度ブロック**を持つ（export-policy §2 規則4）。

### カード別の軸（status / review_status / supply_mode / contract）

| カード | status | review_status | supply_mode | contract | 本パックでの供給強度 |
|---|---|---|---|---|---|
| KA-REF-036 | draft | 未記載（schema 既定＝unreviewed） | authoritative | null | advisory（export-policy §2 規則4＝未検証権威の遮断） |

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
| bmad-code-org/BMAD-METHOD (v6) | MIT | KA-REF-036 |
| github/awesome-copilot | MIT | KA-REF-036 |

- 全ライセンスは MIT＝互換・再配布可。NOTICE ファイルは**原文になし**。版固定は factory/snapshots/oss/PROVENANCE.md。
- **非選定（BY-SA 隔離12枚・export-policy 規則1）の完全 ID**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 —— いずれも本パックに含まれず、隔離解除は法務確認の完了のみ（adr/0007 §1）。
- snapshots/・corpus/ の凍結原本は本パックに複製していない（export-policy 規則2）。

## 選定記録

- 選定基準: テーマ「エッジケース列挙」に適合する1枚。テスト設計そのもの（KA-REF-039/044）は既存の
  test-design パックの領分につき非収載。
- **`--include-draft`**: status: draft の構成資産を含むため DRAFT 印を付して収載。DRAFT は元資産の
  校正ライフサイクルを示し、Skill の出荷検査や実務妥当性の判定を表さない。
