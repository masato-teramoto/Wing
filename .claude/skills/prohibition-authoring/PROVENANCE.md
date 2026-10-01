# PROVENANCE — prohibition-authoring（規範文の書き方パック・S8）

- compiled_at: 2026-09-01 ／ compose 実行: /loop-compose operation prohibition-authoring --include-draft
- 位置づけ: 要求・要件定義フェイズ Skill 一式（選定案 rev78）の **S8**。dispatch は **mode-only**
  （project profile を読まない）。
- 再コンパイル条件: compiled_from の各カードの version・status が変わったら再生成（/loop-report が検出）。
  **本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）。

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-020 | 0.1.1 | draft | authoritative | null |
| KA-EXP-002 | 0.1.0 | draft | advisory | null |

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-020 禁止事項の定式化規約 | 0.1.1 | draft | community-consensus | stable / null | ルールA〜C・review 時の出し方 | K-01〜K-05。K-05 の規律違反型を SO-03 の回避策・letter/spirit・rationalization table と red flags まで復元し、SO-06 の template/rules 分離を advisory 収載 |
| KA-EXP-002 規範文の失敗モード | 0.1.0 | draft | community-single | stable / null | 落とし穴 | FM-01〜FM-04（形状問題への禁止の逆効果・nuance 一節での劣化・例外条項の非スコープ・好意/返報性の誤用）。実測数値は非収載 |

### KA-REF-020 SO 全件の選定状態

| SO | 状態 | 反映先・条件または非収載理由 |
|---|---|---|
| SO-01 | 非収載 | prohibition 逆効果の実測数値は adr/0006 に従い転記しない。機序は Experience 由来の落とし穴に収載済み |
| SO-02 | 非収載 | nuance clause の実測数値は転記しない。機序は落とし穴に収載済み |
| SO-03 | 条件付き収載 | ルールC。失敗型が規律違反の場合だけ、回避策・letter/spirit・rationalization table を追加。K-05 の red flags も復元 |
| SO-04 | 非収載 | 説得7原則は規範文の中核から外れ、Liking/Reciprocity の注意だけが Experience に一般化済み |
| SO-05 | 非収載 | 例数・行数の固定値は案件規約に依存 |
| SO-06 | 収載 | ルールC。template は構造、rules は判断基準として配置を分離 |
| SO-07 | 非収載 | NON-NEGOTIABLE の固定マーキングは方言依存 |
| SO-08 | 非収載 | Sync Impact Report の固定様式は変更管理パックの領分 |
| SO-09 | 非収載 | severity と修復期限の固定語彙は Contract・案件規約に依存 |
| SO-10 | 非収載 | 8フィールド監査報告様式は監査側・案件出力契約に依存 |

- SO-03・SO-06 は利用者指示 2026-09-01 と選定案 rev78 による advisory。正式な違反判定や severity には使わない。

- `activate_specializations` による SO の選択的活性化は **P3 では未導入**。上表は静的または失敗型条件つきの
  advisory 収載であり、runtime selector・project profile 読取りを追加しない。
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率・実測比較値等を転記していない。失敗モードは
  機序の記述としてのみ収載した。

## バッジ（共通規律2）

- `draft_badge` = **true**（両カードとも status: draft）。SKILL.md 冒頭に DRAFT 印あり。
- `pack_advisory` = **true**（KA-EXP-002 が supply_mode: advisory ／ KA-REF-020 は authoritative かつ
  contract: null ＝未検証権威）。全称形の advisory 宣言に加え、**カード1枚1行の強度ブロック**を持つ
  （export-policy §2 規則4）。

### カード別の軸（status / review_status / supply_mode / contract）

| カード | status | review_status | supply_mode | contract | 本パックでの供給強度 |
|---|---|---|---|---|---|
| KA-REF-020 | draft | 未記載（schema 既定＝unreviewed） | authoritative | null | advisory（export-policy §2 規則4＝未検証権威の遮断） |
| KA-EXP-002 | draft | 未記載（schema 既定＝unreviewed） | advisory | null | advisory（カード宣言のまま） |

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
| obra/superpowers | MIT | KA-REF-020 / KA-EXP-002 |
| github/spec-kit | MIT | KA-REF-020 |
| Fission-AI/OpenSpec | MIT | KA-REF-020 |
| gotalab/cc-sdd | MIT | KA-REF-020 |
| github/awesome-copilot（security-and-owasp） | MIT | KA-REF-020 |
| openai/skills security-best-practices | **Apache-2.0**（LICENSE.txt 同梱凍結） | KA-REF-020 |

- 全ライセンスは MIT / Apache-2.0＝互換・再配布可。NOTICE ファイルは**原文になし**。版固定は
  factory/snapshots/oss/PROVENANCE.md。
- **非選定（BY-SA 隔離12枚・export-policy 規則1）の完全 ID**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 —— いずれも本パックに含まれず、隔離解除は法務確認の完了のみ（adr/0007 §1）。
- snapshots/・corpus/ の凍結原本は本パックに複製していない（export-policy 規則2）。

## 選定記録

- 選定基準: テーマ「禁止事項の定式化」に適合する2枚。KA-REF-020 が規約の SSOT、KA-EXP-002 が同一凍結原本
  由来の失敗モード（規範が逆効果になる機序）で、対で収載した。
- **`--include-draft` 相当**: 両カードとも status: draft のため DRAFT 印を付して収載。
