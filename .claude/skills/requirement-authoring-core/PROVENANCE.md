# PROVENANCE — requirement-authoring-core（要求文書 authoring・契約済みコアパック）

- compiled_at: 2026-08-27 ／ compose 実行: 選定案 rev20 §2 S2・P1 フェーズ。frontmatter は Agent Skills 標準の
  `metadata.l2-compiled-from` / `l2-compiled-at` 形式（2026-08-27 一括移行後）。
  D1 compose_acceptance_receipt（`factory/ledgers/export-receipts/`・receipt commit C2）が gate 証跡（D1 v1.0.1＝dirsha 各行 LF 終端）
- 位置づけ: 要求・要件定義フェイズ Skill 一式（9本）の S2。**authoring（書く）側**の発動単位であり、
  同一カード群を共有する既存 `requirement-sparring-generic`（変更しない立場での検出側）とは発動単位が異なる
  ため統合しない（カードが SSOT＝二重管理は生じない）
- 再コンパイル条件: l2-compiled-from の各 id の version / status / supply_mode / contract が変わったら再生成。
  **本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）

## compiled 5列表（D1 突合の基準値。欠落値正規化: CT＝N/A・KA 明示 null＝null・不正欠落＝ERROR）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-001 | 0.5.0 | validated | authoritative | CT-REF-002 |
| KA-REF-009 | 0.1.0 | validated | authoritative | CT-REF-008 |
| KA-REF-010 | 0.1.0 | validated | authoritative | CT-REF-008 |
| KA-REF-021 | 0.1.1 | validated | authoritative | CT-REF-009 |
| CT-REF-002 | 0.3.0 | validated | N/A | N/A |
| CT-REF-008 | 0.3.0 | validated | N/A | N/A |
| CT-REF-009 | 0.3.0 | validated | N/A | N/A |

- バッジ判定（共通規律2）: `draft_badge = false`（全カード validated）／`pack_advisory = false`
  （全カード authoritative ∧ contract 紐付き・advisory カードなし）→ **DRAFT 印・advisory ブロックとも
  SKILL.md に置いていない**（期待値・実測値の照合は D1 receipt に記録）

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-001 SDD受入基準の記述規約 | 0.5.0 | validated | community-consensus | stable | 受入基準を書く | K-01〜K-09（SO-01〜10 は単独ツール由来につき非収載） |
| KA-REF-009 NFRタクソノミと定量化規律 | 0.1.0 | validated | community-consensus | stable | 非機能要求を書く | **K-01 は境界注記のみ**（「4カテゴリを網羅 taxonomy と誤認しない」。3流儀は正規化しない）＋K-02〜K-05 |
| KA-REF-010 対象/対象外の宣言様式 | 0.1.0 | validated | community-consensus | stable | 非機能要求を書く・スコープ境界を書く | K-01〜K-03（4カテゴリ採否明示宣言の出力様式は **CT-REF-008 INV-01 由来**と記録し、KA-REF-009 K-01 由来と記録しない） |
| KA-REF-021 スコープ記述規約 | 0.1.1 | validated | community-consensus | stable | スコープ境界を書く | K-01〜K-03（SO-01〜07 非収載） |

- validation 節 = CT-REF-002@0.3.0 / CT-REF-008@0.3.0 / CT-REF-009@0.3.0（いずれも status: validated・
  calibration 記録あり）の INV/DEV 要約。採点実務は Contract 本体が正。フル維持（D-4 裁定＝痩身の発効条件不成立）
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率等の評価数値を転記していない
- 本文の参照書換え: 同一パック内の相互参照は節アンカー/自然文へ展開済み。別パック参照は frontmatter `name` 値
  （requirement-sparring-generic / spec-change-proposal / canonical-terminology-authoring /
  edge-case-enumeration）で記載。K 番号は本表のみが保持し SKILL 本文には置かない

## 元 OSS ライセンス（帰属・NOTICE 引継ぎ）

| 上流 | ライセンス | NOTICE | 経由カード |
|---|---|---|---|
| github/spec-kit | MIT | 原文なし（凍結原本に NOTICE 不存在） | KA-REF-001 / 009 / 010 |
| gotalab/cc-sdd | MIT | 原文なし | KA-REF-001 / 009 / 010 / 021 |
| bmad-code-org/BMAD-METHOD (v6) | MIT | 原文なし | KA-REF-001 / 009 / 010 / 021 |
| github/awesome-copilot | MIT | 原文なし | KA-REF-001 / 021 |
| openai/skills define-goal | Apache-2.0（LICENSE.txt 同梱凍結） | 原文なし | KA-REF-001 / 021 |

- 全ライセンスは MIT / Apache-2.0＝互換・再配布可。版固定は factory/snapshots/oss/PROVENANCE.md
- snapshots/・corpus/ の凍結原本は本パックに複製していない（export-policy 規則2）

## 選定記録

- 選定基準: 選定案 rev19（d3b89e7）§2 S2 のとおり——契約済み（validated・authoritative・contract 紐付き）
  4枚のみで構成し、draft・advisory カードを混載しない（validated 核の advisory 巻き込み防止）
- **BY-SA 隔離（export-policy 規則1・完全 ID 列挙）**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 の12枚は本パックに**非選定**（テーマ適合の有無にかかわらず dist 収載不可・解除は法務確認のみ）
- 同一式の他 skill（S1/S3a/S3b/S4/S5/S6/S7/S8）へ割付済みのカード・draft カード（KA-REF-020/024/029/030/
  036/041/055・KA-EXP-002）は本パックに**非選定**（各 pack の PROVENANCE が記録を持つ）
- 既存 skill が保持: KA-REF-022（requirement-sparring-generic 観点4）・KA-REF-007/008（acceptance-review）は
  本パックに**非選定**
- 内部源泉（KA-REF-056〜059）は本一式の対象外＝**非選定**（内部供給トラックが担う）
