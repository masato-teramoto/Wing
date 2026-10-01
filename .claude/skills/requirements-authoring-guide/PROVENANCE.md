# PROVENANCE — requirements-authoring-guide

compiled_at: 2026-09-14。`/loop-compose operation requirements-authoring-guide --include-draft` 相当の合成。
選定記録: [実務性改善 F07](../../../../docs/proposals/skills-practicality-improvement-20260914.md)。
選定承認は補助パック・部分SO・合成例の作成範囲に対するもので、カード本文のhuman reviewや正式校正ではない。
SSOTはassets/。本文の規範を変えるときはカードを、例を直すときはartifact正本を直して再Composeする。

## compiled 一覧（5列）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-060 | 0.1.0 | draft | advisory | null |
| KA-ART-004 | 0.1.0 | draft | advisory | null |

KA-REF-001等は派生・例示の出典であり、元カード全体やContractを構成資産へ追加したものではない。
既存authoritative packの強度、Contract、判定条件は変更しない。

## カードと反映先

| 資産・項目 | 反映先 | 範囲・根拠 |
|---|---|---|
| KA-REF-060 SO-01 | SKILL.md「成果・証拠・境界を具体化する」 | KA-REF-001@0.5.0 SO-05から成果・証拠・境界だけを選択。define-goal凍結本文L20–26、L58–61。質問を不足箇所へ限定する根拠はL37–38、L91 |
| KA-REF-060 SO-02 | SKILL.md「測定の種類と条件を選ぶ」 | KA-REF-001 SO-08。define-goal L29–34、L84、L99。measurement methodを環境・データ・計測区間・集計へ具体化。固定値は追加しない |
| KA-ART-004 SO-01 | examples/requirements.md、implementation-plan.md、verification-spec.md、traceability-complete.md | assets/artifact/examples/KA-ART-004/の同名ファイルから相対リンクを維持してコピー。既存記述規則を架空題材へ適用した説明例 |
| KA-ART-004 SO-02 | examples/traceability-gaps.md、traceability-missing.md | 同artifact正本の変種。部分被覆・未被覆・孤児・MISSINGを数値と6表で示す |

例の要件・計画の規則参照はKA-REF-001@0.5.0、KA-REF-009@0.1.0、KA-REF-010@0.1.0、
KA-REF-029@0.1.0。被覆例の意味規則はKA-REF-023@0.1.0とCT-REF-011@0.4.2、6表・canonical列・
入力状態・集計・SELF_CHECK等の物理形式は[要求Compose選定案 §3 D2 v1.8.0](../../../../docs/proposals/requirements-phase-compose-selection-20260826.md)のローカル合成規則に合わせる。
CT-REF-011を本パックへ接続・同梱しておらず、例の採点・正式判定を実施したという意味ではない。

## 構成資産のSO選定状態（全件）

| SO-ID | 状態 | 反映先・適用条件または非収載理由 |
|---|---|---|
| KA-REF-060/SO-01 | 条件付き収載 | 成果や確認方法・境界が曖昧な箇所がある場合、「成果・証拠・境界を具体化する」を任意の質問補助として使う |
| KA-REF-060/SO-02 | 条件付き収載 | 証拠・成功境界が決められない場合、「測定の種類と条件を選ぶ」を使う。性能4点セットは性能を数値で扱う場合、二値候補は妥当な数値指標が立たない場合 |
| KA-ART-004/SO-01 | 条件付き収載 | 一連の記入例が必要な場合、本文から該当する例だけを読む。全例の読取りは要求しない |
| KA-ART-004/SO-02 | 条件付き収載 | 部分被覆・未被覆・孤児・入力欠落の扱いを参照する場合、該当変種を読む |

## 派生元SOの選択範囲（KA-REF-001の全10項目）

| SO-ID | 状態 | 反映先・部分選択の範囲または非収載理由 |
|---|---|---|
| KA-REF-001/SO-01 | 非収載 | EARSの固定5類型・具体主語形式は採らない。例は条件→応答の既存Kを適用 |
| KA-REF-001/SO-02 | 非収載 | Independent Test・Success Criteriaの独立必須節を追加しない |
| KA-REF-001/SO-03 | 非収載 | デルタ様式・Lite/Full・特定validatorは対象外 |
| KA-REF-001/SO-04 | 非収載 | BMADのTask/AC番号書式は採らない。被覆例は既存被覆形式を適用 |
| KA-REF-001/SO-05 | 条件付き収載 | KA-REF-060 SO-01経由で成果・証拠・境界のみ。本文の曖昧な箇所への補助。5問すべての事前ゲート、停止条件、goal起動は非収載 |
| KA-REF-001/SO-06 | 非収載 | 活動目標を拒否する新しいDEVやゲートを追加しない |
| KA-REF-001/SO-07 | 非収載 | 証拠をobjective文字列自体へ必須で内蔵する形式は採らない |
| KA-REF-001/SO-08 | 条件付き収載 | KA-REF-060 SO-02経由。測定方法が必要な場合の4類型、性能4点セット、数値化が不適切な場合の二値候補。固定閾値・証拠数・正式採点条件は非収載 |
| KA-REF-001/SO-09 | 非収載 | 技術言及の二値litmusを追加しない |
| KA-REF-001/SO-10 | 非収載 | P1/P2等の優先度・MVP成立条件を固定しない |

## 例の形式を参照した資産のSO選定状態

この表は例に持ち込む範囲の監査記録であり、元カードのSOを新しい判定規則として活性化しない。

| SO-ID | 状態 | 反映先・部分選択の範囲または非収載理由 |
|---|---|---|
| KA-REF-009/SO-01 | 非収載 | requirements/designの技術言及litmusを新たに教示しない |
| KA-REF-009/SO-02 | 非収載 | feature/横断NFRの配置を固定しない |
| KA-REF-010/SO-01 | 非収載 | Clear/Partial/Missingによる明確化走査は対象外。被覆例のMISSINGはD2の入力状態で別概念 |
| KA-REF-010/SO-02 | 非収載 | Adapt-Inカテゴリメニューは対象外 |
| KA-REF-029/SO-01 | 非収載 | 固定分数・TDD5手順・固定実行コマンドは採らない |
| KA-REF-029/SO-02 | 非収載 | Goal/Architecture等の必須ヘッダ定型を追加しない |
| KA-REF-029/SO-03 | 条件付き収載 | 実装計画例を読む場合のConsumes/Produces。既存implementation-planningで選定済みの様式の説明例に限定 |
| KA-REF-029/SO-04 | 条件付き収載 | 同例で受取・提供の名前と型を一致させる部分のみ。inline修正後に再レビューしない手順は非収載 |
| KA-REF-029/SO-05 | 非収載 | 計画を実行する際の停止規則は新設しない |
| KA-REF-029/SO-06 | 非収載 | spec-kitの採番・チェックリスト厳格書式は固定しない |
| KA-REF-029/SO-07 | 非収載 | 固定PhaseやMVP実行戦略は対象外 |
| KA-REF-029/SO-08 | 非収載 | file churnによるエピック統合は対象外 |
| KA-REF-029/SO-09 | 非収載 | starter templateやエンティティ作成時期は対象外 |
| KA-REF-023/SO-01 | 非収載 | 特定多欄の要求×設計表・省略条件は対象外。6表はD2の既存出力形式を例示 |
| KA-REF-023/SO-02 | 非収載 | 抽出・導出の分業パイプラインと上流実測数値は対象外 |
| KA-REF-023/SO-03 | 非収載 | 検証3次元の分類は追加しない |
| KA-REF-023/SO-04 | 非収載 | buildableだけに母集合を絞らない。渡された要求全IDを確認する |
| KA-REF-023/SO-05 | 非収載 | 要求5特性のゲートを追加しない |
| KA-REF-023/SO-06 | 非収載 | 要求見出しの固定書式を追加しない |
| KA-REF-023/SO-07 | 非収載 | 他品質成果物によるCOMPLETE更新の新規条件は追加しない |
| KA-REF-023/SO-08 | 非収載 | 判定衝突を検証プローブで解消する手順は対象外 |

## 状態・強度と検証の限界

| 資産 | status | review_status | supply_mode | contract | evidence_strength | volatility / review_by |
|---|---|---|---|---|---|---|
| KA-REF-060 | draft | unreviewed | advisory | null | community-single | stable / null |
| KA-ART-004 | draft | unreviewed | advisory | null | internal-single | stable / null |

DRAFTとADVISORYはどちらもtrue。原因資産2枚の一般形を本文へ逐語で記載した。
上流カードのhuman-reviewedやvalidatedを派生カード・合成例へ引き継がない。
静的検査と独立レビューは、実案件での効果や正式採点の実施を示さない。
例はSELF_CHECK・NOT_EVALUATED・採点null・証跡参照null・non-finalを維持し、工程遷移を開かない。
新しいINV/DEV・Contract・runtime selector・project profile読取りは追加していない。

生成用の例はeval-onlyの正解へ転用しない。別題材による今後の試行では、固有値のコピー、無用な事前質問、
未確定値の補完、COMPLETEと実行成功の混同を確認する。例の期待性能値は合成入力であり、測定値ではない。

## 元 OSS ライセンス（帰属・NOTICE引継ぎ）

| 上流 | ライセンス・帰属 | 経由資産・反映 | NOTICE・保持事項 |
|---|---|---|---|
| openai/skills define-goal | Apache-2.0（凍結LICENSE.txt） | KA-REF-060の部分選択・再構成 | 凍結範囲に別NOTICEなし |
| gotalab/cc-sdd | MIT、Copyright (c) 2025 gotalab | KA-ART-004が参照する要件・被覆形式 | 別NOTICEなし |
| github/spec-kit | MIT、Copyright GitHub, Inc. | KA-ART-004が参照する要件・計画・被覆形式 | 別NOTICEなし |
| bmad-code-org/BMAD-METHOD | MIT、Copyright (c) 2025 BMad Code, LLC | KA-ART-004が参照する要件・計画・被覆形式 | LICENSE内の商標通知を下記に保持 |
| obra/superpowers | MIT、Copyright (c) 2025 Jesse Vincent | KA-ART-004の計画・受取/提供の形式 | 別NOTICEなし |
| Fission-AI/OpenSpec | MIT、Copyright (c) 2024 OpenSpec Contributors | KA-ART-004が参照する被覆形式 | 別NOTICEなし |
| github/awesome-copilot spec-driven-workflow | MIT、Copyright GitHub, Inc. | KA-ART-004が参照する被覆形式 | 別NOTICEなし |
| github/awesome-copilot quality-playbook-requirements_pipeline | Apache-2.0（凍結LICENSE-quality-playbook-apache2.txt） | KA-ART-004が参照する被覆形式 | 凍結範囲に別NOTICEなし |

上流は既存凍結版を参照し変更していない。Apache-2.0/MITの既存供給経路に従い、出典を保持して助言・
合成例へ再構成した。凍結原本の本文・実測データ・評価runを複製していない。例の題材と文面は新規合成。

BMADのLICENSE内商標通知:

```text
TRADEMARK NOTICE:
BMad™, BMad Method™, and BMad Core™ are trademarks of BMad Code, LLC, covering all
casings and variations (including BMAD, bmad, BMadMethod, BMAD-METHOD, etc.). The use of
these trademarks in this software does not grant any rights to use the trademarks
for any other purpose. See [TRADEMARK.md](TRADEMARK.md) for detailed guidelines.
```

## 出荷境界

- 非選定（BY-SA隔離）: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015。
- 非選定（BY-SA隔離）: KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038。
- 社内源泉・snapshots/・corpus/の原本は非選定。internal-singleは本リポジトリ作成の単一合成例という根拠区分であり、社内文書を含まない。
- 利用時に読む6例はすべてpack内にある。assets/・supplier側Contract・別packを導入しなければ例を読めない参照は置かない。

## 再Composeの条件

構成カードの版・状態・供給モード・Contract接続、選定範囲、artifact正本、参照した被覆形式が変わった場合は
本文・例・本表・metadataを同時に再生成する。親タスクが管理する一覧・選定記録・用途台帳の更新と照合する。
