# PROVENANCE — operation/commit-convention

**本ファイル・SKILL.md の手編集禁止**（`assets/` が SSOT）。更新は資産カードを直して `/loop-compose` で再コンパイルする。
本ファイルは監査情報の隔離先であり、作業中のエージェントは読まない（実行知識は SKILL.md 側にある）。

- compiled_at: 2026-09-14 ／ compiled_from: `KA-REF-002@0.2.0` `CT-REF-003@0.1.0`
- 上流凍結: `snapshots/oss/PROVENANCE.md`（collected 2026-07-02）／一次標準は `snapshots/standards/PROVENANCE.md`

## compiled 一覧（5列）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-002 | 0.2.0 | validated | authoritative | CT-REF-003 |
| CT-REF-003 | 0.1.0 | validated | N/A | N/A |

構成資産は全てvalidatedで、助言供給の資産もContract未接続の権威的資産も含まない。
`draft_badge=false`／`pack_advisory=false`。資産のreview_statusとContract校正は別軸であり、実案件での有効性を表さない。

## カード ↔ 節 対応表

| SKILL.md | カード | 提示強度 | 接地の要点 |
|---|---|---|---|
| R-01 ヘッダ形式 | KA-REF-002 K-01 | authoritative（CT-REF-003） | cursor CC-spec L35 "Commits MUST be prefixed with a type ... REQUIRED terminal colon and space" / L39。公式仕様 #1・#5（spec-en.md L100-101, L106） |
| R-02 type 語彙 | KA-REF-002 K-02 | authoritative（CT-REF-003） | cursor CC-spec L36-37,48 "The type feat MUST be used ... Types other than feat and fix MAY be used" ＋ L25 Angular 集合 / git-mdc L45（11種）。公式仕様 #2・#3・#14 |
| R-03 命令法・現在形 | KA-REF-002 K-03 | authoritative（CT-REF-003） | cursor git-mdc L47 "Concise, imperative, present tense."。**公式仕様に対応なし＝Angular 慣行由来**（一次接地なし） |
| R-04 破壊的変更 | KA-REF-002 K-04 | authoritative（CT-REF-003） | cursor CC-spec L45-47,49-50。公式仕様 #11〜#13・#15・#16（BREAKING-CHANGE 同義規則 #16 は OSS 転記側に無かった補強） |
| R-05 body | KA-REF-002 K-05 | authoritative（CT-REF-003） | cursor CC-spec L40-41 "The body MUST begin one blank line after the description" / git-mdc L48。公式仕様 #7・#8。※「なぜを書く」の内容規範は仕様に無く OSS 実践知由来 |
| R-06 scope | KA-REF-002 K-06 | authoritative（CT-REF-003） | cursor CC-spec L38 "A scope MUST consist of a noun ... surrounded by parenthesis" / git-mdc L46。公式仕様 #4 |
| R-07 footer | KA-REF-002 K-07 | authoritative（CT-REF-003） | cursor CC-spec L42-43 "A footer's token MUST use - in place of whitespace"。公式仕様 #9・#10 |
| 決定的検査 | KA-REF-002「決定的検査（harness）候補」 | — | CT-REF-003 ハーネス帰属注記も同旨（判定器は資産ではない） |
| validation 節 | CT-REF-003 INV-01〜07 / DEV-01〜03 | authoritative | フル維持（`/loop-compose` 既定。痩身は adr/0010 §D-4 の条件付き保留により未発効） |

## カードの属性（提示強度の判定根拠）

| カード | version | supply_mode | contract | 提示強度 | evidence_strength | review_status | volatility / review_by | risk_if_wrong |
|---|---|---|---|---|---|---|---|---|
| KA-REF-002 | 0.2.0 | authoritative | CT-REF-003 | **権威**（contract 実在） | community-consensus | human-reviewed | 行なし（schema 既定 stable）／review_by なし | 無記載 |
| CT-REF-003 | 0.1.0 | N/A（compiled表） | N/A | Contract | — | — | — | — |

- `status: validated` はContractの校正ライフサイクルを示す。資産本文のreview_statusや実務妥当性の保証を意味しない。
- CT-REF-003 の calibration: `judge_pool_n: 71` / `contract_n: 2`（2026-07-09）。**数値の解釈条件は adr/0006 の4条件が必要なため、SKILL.md 本文へは転記していない。**

## 元 OSS ライセンス

| 上流 | 経由カード | ライセンス | 互換判定 |
|---|---|---|---|
| awesome-cursorrules（conventional-commit-spec.mdc） | KA-REF-002 | CC0 1.0 | 可（帰属不要だが記録する） |
| awesome-cursor-rules-mdc（git.mdc） | KA-REF-002 | MIT | 可（帰属を本表で引継ぎ） |
| conventionalcommits.org v1.0.0（spec-en.md・commit 7d293dc59e88） | KA-REF-002 | MIT | 可（帰属を本表で引継ぎ） |

- **NOTICE 保持義務のある上流は含まれない**（本パック構成カードの `license` に NOTICE の語なし）。
- 上流 LICENSE 原文は `snapshots/` 配下にあり、`export-policy §2 規則2` により本パックへ複製していない。

## 除外の明記

- **BY-SA 隔離（export-policy 規則1・非選定）**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 は本パックに含めない。
  KA-REF-002 の `license` は CC0 / MIT / MIT のみで、`related_knowledge` は空＝隔離対象カードへの参照も持たない。
- **社内源泉（規則3）**: 本パックに `snapshots/internal/` 接地カードは**含まれていない**（KA-REF-002 の接地は
  `corpus/seed/conventional-commits/` 2件と `snapshots/standards/conventional-commits/` 1件）。
- **snapshots/・corpus/ の常時除外（規則2）**: 凍結原本・コーパスを本パックに複製していない。接地元はパス参照のみ。

## 選定記録

- 選定基準: テーマ「コミット規約」に適合し、かつ供給ゲート（BY-SA 非該当・社内源泉非該当）を通過するカード。
  該当は KA-REF-002 の1枚。同カードは `related_knowledge: []` で他カードへの依存がなく、単独で発動単位が閉じる。
- **非収載（既定）**: KA-REF-002「助言的・版差あり（invariant に固定しない項目）」節の全項目。
  単独ツール由来または版差ありの項目は**既定で非収載**とし、K 項目と区別不能な平坦な規範箇条に落とさない。
  ただし *subject 長さ上限* と *type 許可集合* の2点は、プロジェクト側が値を決める必要がある事項のため、
  **値を持たない「決める項目」として SKILL.md に残した**（規範として押し付けない形）。
  「末尾ピリオドなし／コロン後小文字始まり／body 行100字以内」「atomic commit / WIP を commit しない」は完全非収載。
- **examples/ は作成しない**（`export-policy §3 規則6` の評価数値転記リスクを構造的に避ける。出荷ゲートも既定除外）。

## 鮮度契約

鮮度管理（`review_by` 監視・再検証・カード更新）は factory 側（`assets/` が SSOT）に帰属する。
本パックの更新は**再コンパイルのみ**で行い、供給先での手修正・独自鮮度管理は禁止（`export-policy §4 規則7`）。

- 構成カードは `volatility` 行を持たない（schema 既定 `stable`）＝ **review_by による期限切れの対象外**。
- 再コンパイル条件: `compiled_from` の version 差分、または **status 変化**（`draft→validated` は version を上げないため
  version 差分検出に掛からない。status も再コンパイル対象として扱う）。

## adr/0006 の遵守

本パックには judge 一致率・PASS 率等の**評価数値を転記していない**（4条件の併記が必要になる記述を持ち込まない）。
`status`を単独の品質保証として表示せず、SKILL冒頭から本書のContract・レビュー状態・検証経路を参照する。校正ライフサイクルと人間レビューを別軸で記録する。

## 供給の位置づけ（adr/0010）

本パックは **PoC 供給（第1スライス）** として消費先へ出荷される。維持条件は
`adr/0010-l1-supply-poc-and-gate4-deferral.md`、撤収手順は `factory/docs/consumer-supply-withdrawal.md` を参照。
供給先は verbatim コピーを保つため、撤収手順を供給先に同梱しない（同梱するとハッシュ照合が成立しない）。

## 生成記録の現行化（2026-09-14）

[実務改善の選定記録](../../../../docs/proposals/skills-practicality-improvement-20260914.md)の全体照合で旧形式の出典表を検出したため、同じ資産・版・選定内容から5列表とバッジの説明を現行化した。本文規則とvalidationのINV/DEVは変更していない。今回の再生成の正式受入は未実施。

| 助言的項目（元カードにSO番号なし） | 状態 | 理由 |
|---|---|---|
| subject長さ上限 | 非収載 | 値を固定せず、案件で決める事項としてだけ案内 |
| 末尾ピリオド・小文字始まり・body行長 | 非収載 | 単独ツール由来の追加規則を混載しない |
| atomic commit・WIP禁止 | 非収載 | メッセージの記述形式の範囲外 |
