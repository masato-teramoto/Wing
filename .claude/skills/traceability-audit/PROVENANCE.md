# PROVENANCE — traceability-audit（要求↔下流の被覆監査パック）

- compiled_at: 2026-09-14 ／ compose 実行: /loop-compose operation traceability-audit
- 位置づけ: 要求・要件定義フェイズ Skill 一式（選定案 rev82）の **S6**。P2 entry（工作物1(e)＝CT-REF-011 の
  multi-edge 意味規則追補 → 境界 fixture の人間ラベル → 再 calibration gate PASS → validated）の完了後にのみ
  compose する fail-closed 対象であり、その完了後に生成したパックを現行 CT-REF-011@0.4.2 のまま再 compose した。
  今回は rev78 で残した被覆母集合確認の手順を、既存 K・Contract・D2 の範囲で具体化した。
- 再コンパイル条件: compiled_from の各カード／Contract の version・status が変わったら再生成。
  版の差分は /loop-report、status を含む依存整合は compose gate で確認する。
  **本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）。

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-023 | 0.1.0 | validated | authoritative | CT-REF-011 |
| CT-REF-011 | 0.4.2 | validated | N/A | N/A |

（CT は supply_mode / contract を持たないため N/A。KA が contract を持たない場合は null と記す）

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-023 上流↔設計トレーサビリティ実務 | 0.1.0 | validated | community-consensus | volatile / 2027-02-15 | 使い方・被覆母集合の確認・監査の規範・出力・二層の出力 | K-01〜K-06。母集合確認は K-01/K-02 の全数照合と K-03 の原本安定 ID 参照を具体化。ID regex・反復上限・被覆分類 enum 等の具象は非収載＝賞味期限を持ち込まない。K-06 の反復上限は「プロジェクトで決める」へ一般化 |
| CT-REF-011 トレーサビリティ成果物適合契約 | 0.4.2 | validated | — | — | validation・複数 edge をまとめて監査するとき・dispatch の入力状態・被覆母集合の確認 | INV-01〜06／DEV-01〜03 の要約＋verdict 優先順（DEV→FAIL ＞ 全 N/A→NOT_APPLICABLE ＞ 7.0以上→PASS ＞ その他→WARN・v0.4.2）＋multi-edge 集約規則（量化正規化・per-INV min・N/A の2理由・全 N/A＝非適用・any edge DEV＝束の Critical Fail・分母0／入力欠落の区別）。v0.4.1 の操作化2件（孤児検査の「方法」の要件・比率の分母突合）と v0.4.2 の WARN 出口を規範文へ反映。母集合確認は既存の両端参照・入力状態照合・ID 集合差分の適用手順 |

- **出力節（6表・canonical 列名・coverage_pct の排他定義・MISSING edge の扱い・`assessment_basis`／
  `assessment_ref`／`inv_breakdown`・工程遷移条件・整合検査）は選定案 §3 D2 v1.8.0 由来のローカル合成規則**であり、
  新しい資産カード・別 schema ファイルを持たない（物理形式は D2 の領分・意味規則は CT-REF-011 の領分という
  責務分離に従う）。
- **今回の具体化の根拠**: 2026-09-11 の利用者による「Skill 内容と Compose 基盤を整える」という依頼を受け、
  選定案 rev82 で rev78 の残題を具現化した。「被覆母集合の確認」は KA-REF-023 K-01〜03、
  CT-REF-011 の applicable_when（両端の参照可能性）、INV-01/02/04、multi-edge 規則0（実入力と状態宣言の照合）、
  決定論検査1/2/4、および D2 v1.8.0 の母集合参照・集合一致・差集合に基づく。
  監査対象として渡された両端一覧を、写像済み ID だけに縮めず確認する手順であり、全リポジトリからの発見の
  悉皆性を保証する検査や、buildable／KPI による対象選別を加えたものではない。
- **変更境界**: 資産・Contract の version、INV/DEV・採点・工程遷移条件、D2 の6表と整合検査、validation 本文は
  変更していない。SO の活性化・Contract なしの advisory 混在も行っていない。`review` の非補完・非改変を維持する。
- **KA-ART-002（代表例 artifact）は非収載**（選定案 §6-1 の既定＝当面 S6 から外す）。
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率等の評価数値を転記していない。引用する場合は
  4条件（単一評価者・非盲検・verdict 二値粒度・opus-4-8 条件）の併記が必須。

## SO 選定状態（KA-REF-023 の全8項目）

| SO-ID | 状態 | 非収載理由 |
|---|---|---|
| SO-01 | 非収載 | 複雑さに応じた多欄表・省略条件は D2 の6表へ追加しない |
| SO-02 | 非収載 | 抽出／導出の分業と発見の悉皆性は生成側プロセスであり、CT の適用外。実測数値も収載しない |
| SO-03 | 非収載 | 3次元の検証分類は文書間の被覆監査を超える |
| SO-04 | 非収載 | buildable／KPI による選別基準の当否は CT の適用外であり、母集合を自動で絞らない |
| SO-05 | 非収載 | 要求5特性の記述品質は要求記述側の領分 |
| SO-06 | 非収載 | 固定見出し形式は方言依存であり、D2 の物理形式に追加しない |
| SO-07 | 非収載 | 他の品質成果物との整合を新たな COMPLETE 条件に加えない |
| SO-08 | 非収載 | 検証プローブによる判定衝突解消は今回の被覆成果物の作成／レビュー手順に加えない |

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

## 任意の完成例への案内（2026-09-14）

[実務改善選定F07](../../../../docs/proposals/skills-practicality-improvement-20260914.md)を再生成の運用入力として追加した。独立のrequirements-authoring-guideへの任意の案内だけを加え、構成資産・規範・既存の選定・入力解決・判定の強度は維持する。guideの助言・合成artifactを本packに混載せず、未導入を新たな停止理由にしない。旧版のreceiptは今回の再生成の正式受入を示さない。
