# PROVENANCE — requirement-sparring-generic（T1-generic 観点パック）

- compiled_at: 2026-08-27（初版 2026-07-14。P2 execution 工作物1(a) で再 compose → CT-REF-011 v0.4.2 昇格に伴い再々 compose）／ compose 実行: /loop-compose phase requirement-sparring-generic
- 位置づけ: **Track A（requirements 壁打ち）B0/T1 評価の T1-generic アーム供給物**（adr/0002 D2 交点(a):
  「①の compose 出力を③の対照アームが消費」）。generic 観点のみ＝案件固有（specific）観点は含まない。
- 再コンパイル条件: compiled_from の各カード version / status が変わったら再生成（/loop-report が検出）。
  **本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）。

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-001 | 0.5.0 | validated | authoritative | CT-REF-002 |
| KA-REF-009 | 0.1.0 | validated | authoritative | CT-REF-008 |
| KA-REF-010 | 0.1.0 | validated | authoritative | CT-REF-008 |
| KA-REF-021 | 0.1.1 | validated | authoritative | CT-REF-009 |
| KA-REF-022 | 0.1.0 | validated | authoritative | CT-REF-010 |
| KA-REF-023 | 0.1.0 | validated | authoritative | CT-REF-011 |
| CT-REF-002 | 0.3.0 | validated | N/A | N/A |
| CT-REF-008 | 0.3.0 | validated | N/A | N/A |
| CT-REF-009 | 0.3.0 | validated | N/A | N/A |
| CT-REF-010 | 0.1.0 | validated | N/A | N/A |
| CT-REF-011 | 0.4.2 | validated | N/A | N/A |

（CT は supply_mode / contract を持たないため N/A。KA が contract を持たない場合は null と記す）

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-001 SDD受入基準の記述規約 | 0.5.0 | validated | community-consensus | stable | 観点1 | K-01〜K-09（SO-01〜10 は単独観点につき非収載） |
| KA-REF-009 NFRタクソノミと定量化規律 | 0.1.0 | validated | community-consensus | stable | 観点2 | K-02〜K-05（K-01 の3流儀は正規化せず「4カテゴリ宣言」のみ反映） |
| KA-REF-010 対象/対象外の宣言様式 | 0.1.0 | validated | community-consensus | stable | 観点2・観点3 | K-01〜K-03（K-01 は KA-REF-021 K-01 と統合記載） |
| KA-REF-021 スコープ記述規約 | 0.1.1 | validated | community-consensus | stable | 観点3 | K-01〜K-03＋INV-04/05 相当（SO-01〜07 非収載） |
| KA-REF-022 完成度ゲート | 0.1.0 | validated | community-consensus | volatile / 2027-02-08 | 観点4・使い方 | K-01〜K-06（severity 語彙等の具象 enum は非収載＝賞味期限を持ち込まない） |
| KA-REF-023 トレーサビリティ実務 | 0.1.0 | validated | community-consensus | volatile / 2027-02-15 | 観点5 | K-01〜K-06（ID regex・反復上限等の具象は非収載） |

- validation 節 = CT-REF-002@0.3.0 / CT-REF-008@0.3.0 / CT-REF-009@0.3.0 / CT-REF-010@0.1.0 /
  CT-REF-011@**0.4.2**（いずれも status: validated・calibration 記録あり）の INV/DEV 要約。採点実務は Contract
  本体が正。CT-REF-011 は 2026-08-27 に v0.4.1（multi-edge 集約規則の追加・孤児検査の「方法」・比率の分母突合の操作化）→
  **v0.4.2**（WARN 出口の明文化。cycle23 で全13件を再判定し validated 再昇格）と改訂——本パックの観点5 と validation 要約に反映済み。複数 edge の集約規則そのものは
  監査成果物を出す traceability-audit の領分であり、本パックには収載しない。
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率等の評価数値を転記していない。引用する場合は
  4条件（単一評価者・非盲検・verdict 二値粒度・opus-4-8 条件）の併記が必須。

## 元 OSS ライセンス（帰属・NOTICE 引継ぎ）

| 上流 | ライセンス | 経由カード |
|---|---|---|
| github/spec-kit | MIT | KA-REF-001/009/010/022/023 |
| gotalab/cc-sdd | MIT | KA-REF-001/009/010/021/022/023 |
| bmad-code-org/BMAD-METHOD (v6) | MIT | KA-REF-001/009/010/021/022/023 |
| github/awesome-copilot（prd / refine-issue / spec-driven-workflow-v1） | MIT | KA-REF-001/021/022/023 |
| github/awesome-copilot quality-playbook-requirements_pipeline | **Apache-2.0**（skill 直下 LICENSE.txt 凍結） | KA-REF-023 |
| openai/skills define-goal | **Apache-2.0**（LICENSE.txt 同梱凍結） | KA-REF-001/021 |
| Fission-AI/OpenSpec | MIT | KA-REF-023 |

- 全ライセンスは MIT / Apache-2.0＝互換・再配布可。版固定は factory/snapshots/oss/PROVENANCE.md。
- **除外（export-policy 規則1）**: CC BY-SA 4.0 接地カードは本テーマに合致しないため**非選定**であり、仮に
  合致しても法務確認完了まで dist 収載不可（adr/0007 §1）。**本パックに BY-SA 接地カードは含まれていない**。
- **非選定（BY-SA 隔離12枚・export-policy 規則1）の完全 ID**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 —— いずれも本パックに含まれず、隔離解除は法務確認の完了のみ（adr/0007 §1）。
- snapshots/・corpus/ の凍結原本は本パックに複製していない（export-policy 規則2）。

## バッジ（共通規律2）

- `draft_badge` = false（構成カード・Contract とも status: validated）。DRAFT 印なし。
- `pack_advisory` = false（全構成カードが supply_mode: authoritative かつ contract を持つ）。advisory 表記なし。

## 選定記録

- 選定基準: status: validated のみ（--include-draft 不使用・DRAFT 印なし）＋テーマ適合
  （改善計画 §1.2 の「要件品質直結」5テーマ: 受入基準 EARS・NFR・スコープ境界・完成度・トレーサビリティ）。
- validated 17枚中、テーマ外につき非選定: KA-ADR-001/002（ADR記述）・KA-ART-001/002/003（代表例 artifact）・
  KA-REF-002（コミット規約）・KA-REF-003（シークレット。BY-SA 隔離対象でもある）・KA-REF-004/005（完了主張ゲート＝実装工程側）・
  KA-REF-007（コードレビュー）・KA-REF-008（完成度衛生＝成果物マーカー検査。要件文書には KA-REF-022 K-03 の
  placeholder 検査で被覆されるため重複回避）。
- 単独観点（SO-*）は全カードで非収載＝invariant 未昇格の1ツール由来知識を generic パックに混ぜない
  （必要時は案件プロファイルの activate_specializations で活性化）。
