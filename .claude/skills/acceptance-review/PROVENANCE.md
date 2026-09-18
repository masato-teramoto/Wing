# PROVENANCE — operation/acceptance-review

**本ファイル・SKILL.md の手編集禁止**（`assets/` が SSOT）。更新は資産カードを直して `/loop-compose` で再コンパイルする。
本ファイルは監査情報の隔離先であり、作業中のエージェントは読まない（実行知識は SKILL.md 側にある）。

- compiled_at: 2026-08-27（初版 2026-07-23。P2 execution 工作物1(b) で再 compose）／ compiled_from: `KA-REF-007@0.1.0` `KA-REF-008@0.1.0` `CT-REF-006@0.2.0` `CT-REF-007@0.2.0`
- 上流凍結: `snapshots/oss/PROVENANCE.md`（collected 2026-07-02〜07-05）

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-007 | 0.1.0 | validated | authoritative | CT-REF-006 |
| KA-REF-008 | 0.1.0 | validated | authoritative | CT-REF-007 |
| CT-REF-006 | 0.2.0 | validated | N/A | N/A |
| CT-REF-007 | 0.2.0 | validated | N/A | N/A |

（CT は supply_mode / contract を持たないため N/A。KA が contract を持たない場合は null と記す）

## カード ↔ 節 対応表

| SKILL.md | 由来 | 提示強度 | 接地の要点 |
|---|---|---|---|
| ルールA A-01〜A-11 | KA-REF-007 K-01〜K-11 | authoritative（CT-REF-006） | 5ツール横断収束（cc-sdd kiro-review / bmad code-review / superpowers code-reviewer / cursor pr-review / openhands code-review）。A-02 一次ソース自読・A-04 敵対的前提・A-09 スコープ監査ほか |
| ルールB B-01〜B-03 | KA-REF-007 K-12〜K-14 | authoritative（CT-REF-006） | severity 段階付与（4ツール）・実結果基準/インフレ禁止（bmad L31・superpowers L97）・ゼロ指摘懐疑（bmad L36 HALT） |
| ルールC C-01〜C-07 | KA-REF-007 K-15〜K-21 | authoritative（CT-REF-006） | file:line 引用は5ツール共通の最強コンセンサス（K-15）。単一 verdict・構造化出力・不確実性明示。**C-04 は CT-REF-006 INV-04 の字義（「自明でない指摘には」修正提案）を採用** — カード K-18 は「各指摘に」でより強いが、判定水準は Contract 側に揃えた（強度差はここに記録） |
| ルールC C-08 | CT-REF-006 INV-08 | authoritative（スコア項目・CF ではない） | superpowers L106（DON'T: 未読コードへの指摘）＋ P19 字義明確化（指摘位置と根拠言及の区別・2026-07-06 人間承認） |
| ルールD D-01 | KA-REF-008 K-01・K-02 ＋ CT-REF-007 not_applicable（差分スコープ） | authoritative（CT-REF-007） | cc-sdd L74-75・bmad quick-dev L22・copilot blueprint L38。**差分スコープ限定は SO 活性化ではなく Contract 自身の適用範囲規則**（CT-REF-007 not_applicable_when「既存コードの棚卸し」）。±10行コメント読取は **copilot 単独接地**（challenge_gate L22-23,76）だが、CT-REF-007「ハーネス帰属の注記」が INV-01/06 の正当化妥当性判定の入力として明記する規定を根拠に収載（下記 選定記録 (4)） |
| ルールD D-02 | KA-REF-008 K-03 | authoritative（CT-REF-007） | cc-sdd L98-99 Reality Check |
| ルールD D-03 | KA-REF-008 K-04 | authoritative（CT-REF-007） | copilot functional_tests L59-60・cc-sdd L120-122 |
| ルールD D-04 | KA-REF-008 SO-06 相当の記録経路 ＋ CT-REF-007 INV-06 | authoritative（CT-REF-007 INV-06 として契約化済み） | blueprint L16,38,61-65。**SO 活性化ではなく CT-REF-007 INV-06 の本文が根拠**（明示経路への正当化記録は契約の必須 invariant） |
| ルールD D-05 | CT-REF-006 INV-09 / DEV-06 | authoritative（CT-REF-006） | challenge_gate L35（scaffolding 値は欠陥でない）。**SO 活性化ではなく Contract 帰属済み**（completion-hygiene INV-7 を人間判断で CT-REF-006 に帰属・v0.1.0 revision_log） |
| ルールD D-06 | KA-REF-008 K-05（交差点のみ） | authoritative（CT-REF-007 INV-02 の報告形式） | cc-sdd L77-79,161-162。**委譲先の秘密規約カードは BY-SA 隔離対象のため非選定**（本文にはカード ID も内容も載せない） |
| 決定的検査 | KA-REF-007「決定的検査候補」＋ CT-REF-007「決定的検査語彙」 | — | マーカー regex・`CLEAN \| <count> matches`・setup error カウント。判定器は資産ではない |
| 適用範囲の限定 | CT-REF-007 not_applicable_when ＋ KA-REF-008 K-02 の適用 | — | テンプレ記入欄（`<UPPER_SNAKE>` 等）と TBD 許容欄の除外は、消費先テンプレートの明示宣言を K-02「正当化」に読み込んだ適用注記（新規 invariant ではない）。**消費先接地の版固定**: L1_Spec_Template @ `2757418`（2026-06-30）— TBD 許容宣言の実在箇所 `steering/non-functional.md`「運用手順書の正本」・`specs/_template/design.md`「テスト体制/テスト仕様（任意）」。**当該宣言が消費先で変更されたら本節は陳腐化する**（下記 鮮度契約の再コンパイル条件に追加） |
| validation 節 | CT-REF-006 INV-01〜09 / DEV-01〜06 ＋ CT-REF-007 INV-01〜06 / DEV-01〜02 | authoritative | フル維持（`/loop-compose` 既定。痩身は adr/0010 D-4 の条件付き保留により未発効）。N/A 規則の詳細は Contract 本体 |

## カードの属性（提示強度の判定根拠）

| 資産 | version | supply_mode | contract | evidence_strength | review_status | volatility / review_by | risk_if_wrong |
|---|---|---|---|---|---|---|---|
| KA-REF-007 | 0.1.0 | authoritative | CT-REF-006 | community-consensus | human-reviewed | stable ／ null | 無記載 |
| KA-REF-008 | 0.1.0 | authoritative | CT-REF-007 | community-consensus | human-reviewed | **volatile** ／ **2027-02-15**（マーカー語彙・scaffolding 名リスト） | 無記載 |
| CT-REF-006 | 0.2.0 | authoritative | — | — | — | — | — |
| CT-REF-007 | 0.2.0 | authoritative | — | — | — | **決定的検査語彙が volatile ／ 2027-01-31** | — |

- **パック最早 review_by = 2027-01-31**（CT-REF-007 の決定的検査語彙。マーカー regex・プレースホルダテスト検出パターン・
  setup error 検出形式）。期日超過時は語彙の再検証 → 再コンパイル。
- `status` は **内部judge校正済（未レビュー）** の意味に限る（adr/0006 決定2）。実務妥当性は意味しない。
- calibration（CT-REF-006・CT-REF-007 とも）: `judge_pool_n: 71` / `contract_n: 2`（2026-07-09）。
  **数値の解釈条件は adr/0006 の4条件が必要なため、SKILL.md 本文へは転記していない。**

## 元 OSS ライセンス

| 上流 | 経由 | ライセンス | 互換判定 |
|---|---|---|---|
| cc-sdd（kiro-review） | KA-REF-007 / 008・CT 両方 | MIT | 可（帰属を本表で引継ぎ） |
| BMAD-METHOD（code-review 3ファイル・review-adversarial・quick-dev） | KA-REF-007 / 008 | MIT | 可 |
| superpowers（code-reviewer・requesting/receiving-code-review） | KA-REF-007 ＋ CT-REF-006（INV-07 接地） | MIT | 可 |
| awesome-cursorrules（pr-review） | KA-REF-007 | CC0 1.0 | 可（帰属不要だが記録する） |
| OpenHands（code-review） | KA-REF-007 | MIT | 可 |
| awesome-copilot（blueprint-mode・quality-playbook 2ファイル） | KA-REF-008 ＋ CT-REF-006（INV-09 接地） | MIT | 可 |

- **NOTICE 保持義務のある上流は含まれない**（両カードの `license` 欄に NOTICE の語なし）。
- 上流 LICENSE 原文・凍結原本は `snapshots/` 配下にあり、`export-policy §2 規則2` により本パックへ複製していない。

## 除外の明記

- **非選定（BY-SA 隔離12枚・export-policy 規則1）の完全 ID**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 —— いずれも本パックに含まれず、隔離解除は法務確認の完了のみ（adr/0007 §1）。
- **BY-SA 隔離（export-policy 規則1）**: 本パックの構成カード自体に BY-SA 接地はない。とりわけ
  KA-REF-008 K-05 が委譲するシークレット取り扱い規約カードは **BY-SA 隔離対象のため非選定** —
  秘密パターンの本体規約は本パックに含めず、SKILL.md 本文には当該カードの ID も内容も載せていない（D-06 は交差点のみ）。
- **社内源泉（規則3）**: 本パックに `snapshots/internal/` 接地カードは含まれていない。
- **snapshots/・corpus/ の常時除外（規則2）**: 凍結原本・コーパスを本パックに複製していない。
- **eval-only 分離**: copilot/code-review-generic は CT-REF-006 の逸脱ケース素材専用（リーク分離）であり、本パックの接地に不使用。

## 選定記録

- 選定基準: テーマ「受入レビュー」に適合し供給ゲートを通過するカード。KA-REF-007（レビュー実施・出力品質）と
  KA-REF-008（完成度衛生）は `related_knowledge` で相互参照し、Contract も INV-08/09 の帰属で交差する対のため同梱。
- **SO-\* は全カード既定で非収載**（KA-REF-007 SO-01〜18・KA-REF-008 SO-01〜09）。単独ツール由来の特化項目を
  規約と区別不能な形で本文に混ぜない。本文に現れる次の4点は SO 活性化**ではない**:
  (1) 差分スコープ限定（D-01）= CT-REF-007 の適用範囲規則 (2) 明示記録経路（D-04）= CT-REF-007 INV-06
  (3) scaffolding 誤検知抑制（D-05）= CT-REF-006 INV-09
  (4) ±10行コメント読取（D-01 後段）= CT-REF-007「ハーネス帰属の注記」が INV-01/06 の正当化妥当性判定の入力として
  明記する規定（**copilot 単独接地**である事実は D-01 行に併記）。いずれも Contract 本文が根拠。
- 特記: bmad の「最低10指摘ノルマ」（KA-REF-007 SO-18）は**非収載**。dismiss トリアージとのセット運用限定であり、
  単独では B-02（インフレ禁止）と正面衝突する（カード自身の注意書きどおり）。
- **examples/ は作成しない**（`export-policy §3 規則6` の評価数値転記リスクを構造的に避ける。出荷ゲートも既定除外）。

## バッジ（共通規律2）

- `draft_badge` = false（構成カード・Contract とも status: validated）。DRAFT 印なし。
- `pack_advisory` = false（両カードが supply_mode: authoritative かつ contract を持つ）。advisory 表記なし。

## 引き継ぎ元との境界（2026-08-27 追補）

本パックは選定案 rev24 の9本（S1〜S8）と既存パックからの **handoff 先**である（S3b・S4・S5・S6・S7・S8 →
acceptance-review）。SKILL.md の「引き継ぎ元との境界」節はこの位置づけを本文化したもので、新規 invariant では
なく、CT-REF-006 の単一 verdict 規律（INV-05）と B-03（ゼロ指摘懐疑）を handoff 文脈へ適用した注記である。
被覆状態（COMPLETE／INCOMPLETE／UNDETERMINED）は `traceability-audit` が出す別軸の値であり、本パックの
verdict と混同しない旨を明記した。

## 鮮度契約

鮮度管理は factory 側（`assets/` が SSOT）に帰属する。本パックの更新は**再コンパイルのみ**で行い、
供給先での手修正・独自鮮度管理は禁止（`export-policy §4 規則7`）。

- 再コンパイル条件: `compiled_from` の version 差分・**status 変化**・**review_by 期限超過**（最早 2027-01-31）・
  **消費先テンプレートの TBD 許容宣言の変更**（「適用範囲の限定」節の接地。L1_Spec_Template @ `2757418` に版固定）。

## adr/0006 の遵守

本パックには judge 一致率・PASS 率等の**評価数値を転記していない**。`status` 語は単独の品質語として使わず、
「内部judge校正済（未レビュー）」と表示している（決定2）。

## 供給の位置づけ（adr/0010）

本パックは **PoC 供給（第2スライス）** として消費先へ出荷される。維持条件は
`adr/0010-l1-supply-poc-and-gate4-deferral.md`、撤収手順は `factory/docs/consumer-supply-withdrawal.md` を参照。
供給先は verbatim コピーを保つため、撤収手順を供給先に同梱しない（同梱するとハッシュ照合が成立しない）。
