# PROVENANCE — traceability-audit（要求↔下流の被覆監査パック）

- compiled_at: 2026-08-27 ／ compose 実行: /loop-compose operation traceability-audit
- 位置づけ: 要求・要件定義フェイズ Skill 一式（選定案 rev24）の **S6**。P2 entry（工作物1(e)＝CT-REF-011 の
  multi-edge 意味規則追補 → 境界 fixture の人間ラベル → 再 calibration gate PASS → validated）の完了後にのみ
  compose する fail-closed 対象であり、本パックはその完了（v0.4.1・2026-08-27 昇格）を受けて生成した。
- 再コンパイル条件: compiled_from の各カード／Contract の version・status が変わったら再生成
  （/loop-report が検出）。**本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）。

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-023 | 0.1.0 | validated | authoritative | CT-REF-011 |
| CT-REF-011 | 0.4.2 | validated | N/A | N/A |

（CT は supply_mode / contract を持たないため N/A。KA が contract を持たない場合は null と記す）

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-023 上流↔設計トレーサビリティ実務 | 0.1.0 | validated | community-consensus | volatile / 2027-02-15 | 使い方・監査の規範・出力・二層の出力 | K-01〜K-06（ID regex・反復上限・被覆分類 enum 等の具象は非収載＝賞味期限を持ち込まない。K-06 の反復上限は「プロジェクトで決める」へ一般化） |
| CT-REF-011 トレーサビリティ成果物適合契約 | 0.4.2 | validated | — | — | validation・複数 edge をまとめて監査するとき・dispatch の入力状態 | INV-01〜06／DEV-01〜03 の要約＋verdict 優先順（DEV→FAIL ＞ 全 N/A→NOT_APPLICABLE ＞ 7.0以上→PASS ＞ その他→WARN・v0.4.2）＋multi-edge 集約規則（量化正規化・per-INV min・N/A の2理由・全 N/A＝非適用・any edge DEV＝束の Critical Fail・分母0／入力欠落の区別）。v0.4.1 の操作化2件（孤児検査の「方法」の要件・比率の分母突合）と v0.4.2 の WARN 出口を規範文へ反映 |

- **出力節（6表・canonical 列名・coverage_pct の排他定義・MISSING edge の扱い・`assessment_basis`／
  `assessment_ref`／`inv_breakdown`・工程遷移条件・整合検査）は選定案 §3 D2 v1.8.0 由来のローカル合成規則**であり、
  新しい資産カード・別 schema ファイルを持たない（物理形式は D2 の領分・意味規則は CT-REF-011 の領分という
  責務分離に従う）。
- 単独観点（SO-01〜SO-08）は全件**非収載**＝invariant 未昇格の1ツール由来知識を汎用パックに混ぜない
  （必要時は案件プロファイルの activate_specializations で活性化）。多欄トレーサビリティ表・抽出/導出
  パイプライン・3次元分解・buildable 選別・要求5特性・見出し形式の統一・成果物間整合・検証プローブが該当。
- **KA-ART-002（代表例 artifact）は非収載**（選定案 §6-1 の既定＝当面 S6 から外す）。
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率等の評価数値を転記していない。引用する場合は
  4条件（単一評価者・非盲検・verdict 二値粒度・opus-4-8 条件）の併記が必須。

## 元 OSS ライセンス（帰属・NOTICE 引継ぎ）

| 上流 | ライセンス | 経由カード |
|---|---|---|
| gotalab/cc-sdd | MIT | KA-REF-023 |
| bmad-code-org/BMAD-METHOD (v6) | MIT | KA-REF-023 |
| github/spec-kit | MIT | KA-REF-023 |
| Fission-AI/OpenSpec | MIT | KA-REF-023 |
| github/awesome-copilot（spec-driven-workflow-v1） | MIT | KA-REF-023 |
| github/awesome-copilot quality-playbook-requirements_pipeline | **Apache-2.0**（skill 直下 LICENSE.txt 凍結） | KA-REF-023 |

- 全ライセンスは MIT / Apache-2.0＝互換・再配布可。NOTICE ファイルは**原文になし**。版固定は
  factory/snapshots/oss/PROVENANCE.md。
- **除外（export-policy 規則1）**: CC BY-SA 4.0 接地カードは本パックに含まれていない。
- **非選定（BY-SA 隔離12枚・export-policy 規則1）の完全 ID**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 —— いずれも本パックに含まれず、隔離解除は法務確認の完了のみ（adr/0007 §1）。
- snapshots/・corpus/ の凍結原本は本パックに複製していない（export-policy 規則2）。

## バッジ（共通規律2）

- `draft_badge` = false（構成カード・Contract とも status: validated）。DRAFT 印なし。
- `pack_advisory` = false（KA-REF-023 は supply_mode: authoritative かつ contract: CT-REF-011 を持つ）。
  advisory 表記なし。

## 選定記録

- 選定基準: status: validated のみ＋テーマ適合（トレーサビリティ＝要件品質直結5テーマの1つ）。
- 本パックは KA-REF-023 の全 invariant（K-01〜K-06）を収載し、host Contract CT-REF-011 を validation として
  紐づける authoritative パック。隣接する KA-REF-022（文書単体の完成度ゲート）は非収載——境界は
  「ゲート＝文書単体 / 本パック＝文書間の被覆関係」であり、完成度ゲートの言及は
  requirement-sparring-generic へ redirect する。
