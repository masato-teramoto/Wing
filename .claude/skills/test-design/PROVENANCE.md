# PROVENANCE — phase/test-design

- compiled_at: 2026-09-14
- compose: /loop-compose phase test-design --include-draft
- SSOTは`assets/`。本ファイルとSKILL.mdは資産カードから再構成した生成物であり、修正は資産側から行う。
- 選定・適用根拠: [全20 Skillの実務レビュー](../../../../docs/assessments/skills-practicality-review-20260914.md) F05と、利用者の修正指示を記録した[実務改善・選定記録](../../../../docs/proposals/skills-practicality-improvement-20260914.md)。KA-REF-039 SO-01／02／04／06を項目単位で条件付き部分採用し、KA-REF-039@0.1.3とKA-REF-044@0.1.1のモック境界の適用整理を再構成した。
- 初回の一般K全6件・ブラウザK全6件と、KA-EXP-001 FM全6件・KA-EXP-003 FM-01を維持する。SOの追加選定はカード本文のhuman-reviewed化・Contract活性化・新設・昇格を意味しない。
- 本文生成・静的確認と正式D1受入を分ける。生成しただけで実consumerへの供給・実案件の検証を済ませたことにはしない。

## compiled 一覧（5列）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-039 | 0.1.3 | draft | authoritative | null |
| KA-REF-044 | 0.1.1 | draft | authoritative | null |
| KA-EXP-001 | 0.1.0 | draft | advisory | null |
| KA-EXP-003 | 0.1.0 | draft | advisory | null |

## カード別の軸と検証経路

| カード | status | review_status | supply_mode | contract | evidence_strength | volatility / review_by | 本pack |
|---|---|---|---|---|---|---|---|
| KA-REF-039 | draft | 未記載（schema既定: unreviewed） | authoritative | null | community-consensus | volatile / 2027-01-25 | advisory |
| KA-REF-044 | draft | 未記載（schema既定: unreviewed） | authoritative | null | community-consensus | volatile / 2027-03-01 | advisory |
| KA-EXP-001 | draft | 未記載（schema既定: unreviewed） | advisory | null | community-single | volatile / 2027-01-25 | advisory |
| KA-EXP-003 | draft | 未記載（schema既定: unreviewed） | advisory | null | community-single | volatile / 2027-02-01 | advisory |

- DRAFT式はtrue（構成資産status=draft）。ADVISORY式はtrue（authoritativeかつcontract=null、またはsupply_mode=advisory）。冒頭にDRAFT→ADVISORYの定型と、全原因資産の各行を置く。
- DRAFTは校正ライフサイクルを示し、カード本文の人間レビュー・judge実行・本packの構成検査結果とは別軸。評価数値・内部judge校正済という表示を転記しない。
- KA-REF-039／044は文書成果物系のCT化キューでcontract=null。KA-EXP-001／003はfailure_modeの助言資産でContract対象外、evidence_strengthと案件回帰が検証経路。これらは正式採点・PASS/FAIL・工程遷移ゲートの根拠を供給しない。
- 本文での自己確認はSHOULD相当の助言。実際のテストrunnerの成功・失敗と、本packの正式な品質判定を区別する。

## カード ↔ 手順 ↔ 凍結source

sourceパスは`factory/snapshots/oss/`からの相対。版固定・ライセンス記録は`snapshots/oss/PROVENANCE.md`（collected 2026-07-02、frozen 2026-07-08）を参照する。

| カード項目 | SKILL反映先 | 保持した意味 | 凍結sourceの接地箇所 |
|---|---|---|---|
| KA-REF-039 K-01 | A-01、前提状態、検査候補 | 決定性、ランダム性・タイミング・共有状態への依存を避ける | github-copilot/qa-engineering-best-practices.instructions.md L18、superpowers/condition-based-waiting-SKILL.md L13–14 |
| KA-REF-039 K-02 | A-02、B-03 | 実条件を待ち、タイミング自体を調べる場合は条件待機先行・既知タイミング・WHYを残す | github-copilot/qa-engineering-best-practices.instructions.md L114・170、superpowers/condition-based-waiting-SKILL.md L16・39–40・105–115 |
| KA-REF-039 K-03 | A-03、層と境界の設計 | mockの存在ではなく観測できる実挙動を確かめる | superpowers/testing-anti-patterns-SKILL.md L12・15・21、github-copilot/qa-engineering-best-practices.instructions.md L112、superpowers/test-driven-development-SKILL.md L105・111 |
| KA-REF-039 K-04 | A-04、層と境界の設計 | 依存・副作用を理解し境界で必要な隔離を行う。完全な応答構造を保つ | github-copilot/qa-engineering-best-practices.instructions.md L91–95、superpowers/testing-anti-patterns-SKILL.md L23・159–174・202 |
| KA-REF-039 K-05 | A-05 | シナリオ・操作・期待を単独で読めるテスト名 | github-copilot/qa-engineering-best-practices.instructions.md L41・48–50・55、superpowers/test-driven-development-SKILL.md L203 |
| KA-REF-039 K-06 | A-06 | 一テスト一挙動、無関係な複数の確認を混ぜない | github-copilot/qa-engineering-best-practices.instructions.md L15・61、superpowers/test-driven-development-SKILL.md L202 |
| KA-REF-044 K-01 | B-01 | ユーザ可視・テスト用の安定したセレクタを使う | cursor/playwright-e2e-testing.mdc L23・31、cursor/cypress-e2e-testing.mdc L22・30、cursor/playwright.mdc L34–45、cursor/cypress.mdc L74–83、claude-code/webapp-testing/SKILL.md L88 |
| KA-REF-044 K-02 | B-02、層と境界の設計 | UI応答処理の隔離と、管理できる自前backendまでの実結合確認を分ける | cursor/playwright-e2e-testing.mdc L25・33、cursor/cypress-e2e-testing.mdc L24・32、cursor/playwright.mdc L173–195、cursor/cypress.mdc L101–113・203。0.1.1の補助接地: claude-code/webapp-testing/SKILL.md L44–60 |
| KA-REF-044 K-03 | B-03、A-02 | 固定時間でなく準備完了条件、準備前DOM検査を避ける | cursor/playwright.mdc L50–64、cursor/cypress.mdc L128–147、cursor/playwright-e2e-testing.mdc L32、cursor/cypress-e2e-testing.mdc L31、claude-code/webapp-testing/SKILL.md L60・80–81 |
| KA-REF-044 K-04 | B-04 | 重要利用経路で成功・失敗、遷移・状態更新・エラー処理を確かめる | cursor/playwright-e2e-testing.mdc L21–22・34・82–92、cursor/cypress-e2e-testing.mdc L20–21・33・68–74 |
| KA-REF-044 K-05 | B-05 | 観測→操作、参照が変わる画面遷移等の後に再観測 | claude-code/webapp-testing/SKILL.md L28–32・65–76、openai-codex/playwright/SKILL.md L65–69・82–89・141–142 |
| KA-REF-044 K-06 | B-06、結果の引渡し | 診断証拠と規約に沿った保存、実際の保存先の報告 | cursor/playwright.mdc L200・208–210、openai-codex/playwright/SKILL.md L69・104–111・146、openai-codex/screenshot/SKILL.md L11–13・267、claude-code/webapp-testing/SKILL.md L3・96 |
| KA-REF-039 SO-01（層の用途） | 層の用途表、設計表 | 単体のロジック、結合の契約・DB/API、E2Eの重要利用経路を対象に合わせ選ぶ | github-copilot/qa-engineering-best-practices.instructions.md L27–35 |
| KA-REF-039 SO-02（状態隔離） | 前提状態の準備と自己確認 | 状態を持つ依存の準備・後始末、任意順序・単独実行、状態漏れを調べる | github-copilot/qa-engineering-best-practices.instructions.md L19・85・94・173 |
| KA-REF-039 SO-04（具体的期待） | 期待の準備、設計表 | 要求に対応した具体値・状態・表示を確認し、存在確認だけで代用しない | github-copilot/qa-engineering-best-practices.instructions.md L62–75 |
| KA-REF-039 SO-06（意味ある被覆） | 優先順位、設計表、自己確認 | 重要経路・複雑箇所・過去の不具合を優先し、未確認を残す | github-copilot/qa-engineering-best-practices.instructions.md L147–150 |
| KA-EXP-001 FM-01〜06 | pitfalls: mock濫用 | mock存在、test-only、依存不明、部分mock、テスト後回し、mock複雑化の症状・気づき方 | superpowers/testing-anti-patterns-SKILL.md L26–66・68–121・123–180・182–231・233–254・256–266・289–296 |
| KA-EXP-003 FM-01 | pitfalls: 期待値の現在状態依存 | 時間・環境・可変データで期待が腐る失敗。固定時間窓などで絶縁する | claude-code/mcp-builder/reference/evaluation.md L314–326 |
| KA-REF-039／044 検査候補 | 自己確認に使う検査候補 | 固定待機・mock・名前・selectorの候補抽出と実行検査。正式な判定器は生成しない | 各カードの決定的検査候補。具象APIは案件で確定 |

### 再構成上の境界

- SO-01／02／04／06は、選定記録と利用者の修正指示に基づく条件付きの静的advisory。条件は通常の設計作業内で確認し、runtime selector・新しいtrigger・正式gateを追加しない。
- QA source L27–35は実コンポーネント間の結合とUI+backendのE2Eを対象に含み、cursor L173はUI試験のbackend不安定性からの隔離を説明する。自分たちの制御可能な検証用backendまでの接続を全てmockにする一般化はしない。資産039@0.1.3／044@0.1.1の適用整理として実物で通す範囲と隔離する依存を明示した。claude-codeの固定helper・ブラックボックス利用規律は採らない。
- 既存環境の無差別な初期化を指示しない。状態の準備・後始末は対象テストが管理する範囲で設計する。新しい環境の操作権限を本packは与えない。
- 層表・設計表・引渡し表現は、選定した層・状態・具体期待・優先箇所を実行可能な作業へ接続したもの。例中の空一覧応答とbackend保存は合成した用途説明であり、実案件の成功例・Contractの評価素材ではない。要求にない閾値・期待値は補わない。
- SO-04の特定matcher・例外型と全文メッセージ一致の一律義務、SO-01の数量比・実行時間、SO-06の固定coverage・branch/mutation測定義務を非収載とする。表の未確認を件数・率だけで達成済みへ読み替えない。
- KA-EXP-001 FM-02／06由来の兆候は維持するが、同義の039 SO-03／07の独立採用ではない。FM-06の50%閾値は転写しない。FM-05は失敗兆候のままで、TDD実行手順の二重供給はしない。
- KA-EXP-003はFM-01のみ。FM-02／03は文字列比較オラクルを前提にする評価QA固有の失敗知であり、テスト設計へ一般化しない。
- 境界値分析・状態遷移・デシジョンテーブルの体系はsource不足のため供給しない。テストデータ管理全般も今回の選定範囲外。既存の`test-driven-development`／`edge-case-enumeration`への案内を更新したが、構成依存・自動起動・必須併用にはしない。

## SO選定状態

### KA-REF-039（全10項目）

| SO-ID | 状態 | 反映先 | 観測可能な適用条件 | 非収載部分・理由／advisory境界 |
|---|---|---|---|---|
| SO-01 | 条件付き収載 | 層の用途表、設計表 | テスト方針を作る、または対象挙動の確認層を検討するとき | 層の対象・用途だけを採用。数量比・実行時間の固定値は非収載。どの層も一律義務にしない |
| SO-02 | 条件付き収載 | 前提状態の準備、自己確認 | テスト間にDB・ファイル・キャッシュ・認証・mock履歴などの状態が残る場合 | 状態隔離・準備・後始末と独立実行を採用。特定DB方式・runnerや既存環境の一律初期化を指定しない |
| SO-03 | 非収載 | なし | なし（未選定） | productionのtest-onlyメソッドに関する追加規範・gateは選定外。対応する失敗兆候はEXP-001 FM-02として既存収載 |
| SO-04 | 条件付き収載 | 期待の準備、設計表 | アサーション・期待結果を書く／見直すとき | 具体的な値・状態・表示を採用。特定matcher・全文メッセージ一致・固定の肯定形を一律に課さない |
| SO-05 | 非収載 | なし | なし（未選定） | factory/builder・一意ID・PIIの運用規範は今回の選定外。状態隔離だけをSO-02から採用 |
| SO-06 | 条件付き収載 | 優先順位、設計表、自己確認 | 試験範囲・優先順位を決めるとき | 重要経路・複雑箇所・過去バグの意味ある被覆を採用。固定率・branch/mutation測定を共通義務にしない |
| SO-07 | 非収載 | なし | なし（未選定） | 数値閾値やintegration切替の独立規範は選定外。対応する失敗兆候はEXP-001 FM-06として既存収載 |
| SO-08 | 非収載 | なし | なし（未選定） | waitForの実装方式・poll間隔・timeout既定値は選定外 |
| SO-09 | 非収載 | なし | なし（未選定） | CIの自動retry・実行タイミングは選定外。状態漏れの自己確認をCI義務にしない |
| SO-10 | 非収載 | なし | なし（未選定） | テストコード一般の品質基準の追加は選定外。名前・粒度は既存Kから維持 |

### KA-REF-044（全8項目）

| SO-ID | 状態 | 反映先 | 観測可能な適用条件 | 非収載部分・理由／advisory境界 |
|---|---|---|---|---|
| SO-01 | 非収載 | なし | なし（未選定） | Playwrightの固定framework・selector・assertion APIは選定外 |
| SO-02 | 非収載 | なし | なし（未選定） | Cypress固有API・フォルダ・retry値は選定外 |
| SO-03 | 非収載 | なし | なし（未選定） | 認証再利用・リソース遮断による高速化は選定外 |
| SO-04 | 非収載 | なし | なし（未選定） | Page Object Modelへの構造固定は選定外 |
| SO-05 | 非収載 | なし | なし（未選定） | 固定件数・describe/setup様式は選定外。重要利用経路はK-04と039 SO-06の採用範囲で扱う |
| SO-06 | 非収載 | なし | なし（未選定） | 固定サーバhelper・スクリプトを読まない規律・headless既定は選定外。管理可能なbackendの利用は改訂K-02から保持 |
| SO-07 | 非収載 | なし | なし（未選定） | CLI-firstや固有ref語彙、run-code制限は選定外。観測→操作はK-05から保持 |
| SO-08 | 非収載 | なし | なし（未選定） | キャプチャ手段の固定優先順位は選定外。診断証拠はK-06から保持 |

## 元OSSライセンス・帰属・NOTICE

| 上流 | 経由 | ライセンス | NOTICE | 互換判定 |
|---|---|---|---|---|
| github-copilot（qa-engineering-best-practices） | KA-REF-039 | MIT | なし | 可 |
| superpowers（testing-anti-patterns・condition-based-waiting・test-driven-development） | KA-REF-039・KA-EXP-001 | MIT | なし | 可 |
| awesome-cursorrules / awesome-cursor-rules-mdc（playwright/cypress 4規約） | KA-REF-044 | CC0 1.0 | なし | 可（帰属不要だが記録） |
| claude-code（webapp-testing） | KA-REF-044 | Apache-2.0（skill 単位 LICENSE.txt 同梱凍結） | なし | 可 |
| **openai-codex（playwright）** | KA-REF-044 | Apache-2.0 | **あり — Microsoft 帰属。下記 NOTICE 節に全文引継ぎ** | 可（NOTICE 維持を本書で履行） |
| openai-codex（screenshot） | KA-REF-044 | Apache-2.0 | なし | 可 |
| anthropics/skills（mcp-builder/reference/evaluation.md） | KA-EXP-003 | Apache-2.0 | なし | 可 |

## NOTICE（再配布時の保持義務 — export-policy §3 規則5・越境供給の追補 2026-07-23）

`snapshots/oss/openai-codex/playwright/NOTICE.txt` より全文引継ぎ:

```
This skill includes material derived from the Microsoft playwright-cli repository.

Source:
- Repository: microsoft/playwright-cli
- Path: skills/playwright-cli/SKILL.md

Copyright (c) Microsoft Corporation.

Licensed under the Apache License, Version 2.0.
See LICENSE.txt in this directory.

Modifications:
- Adapted for the Codex skill collection.
- Added a wrapper script and local reference guides.
```

本パックにおける追加改変: 上記由来の規律（KA-REF-044 K-05/K-06 の一部接地）を日本語の抽象規範として再構成した。
NOTICE 原文中の「See LICENSE.txt in this directory.」が指す上流 LICENSE 原文は `snapshots/oss/openai-codex/playwright/`
配下に凍結されており、`export-policy §2 規則2` により本パックへは複製していない。

### 凍結ライセンスの所在と帰属

以下は`factory/snapshots/oss/`からの相対パス。Apache-2.0の由来部分は日本語の手順へ改変した旨を本書で示す。

| 上流 | 帰属 | 凍結LICENSE |
|---|---|---|
| github/awesome-copilot | Copyright GitHub, Inc. | github-copilot/LICENSE-github-copilot.txt |
| obra/superpowers / obra/superpowers-skills | Copyright (c) 2025 Jesse Vincent | superpowers/LICENSE-superpowers.txt / superpowers/LICENSE-superpowers-skills.txt |
| awesome-cursorrules / awesome-cursor-rules-mdc | CC0 1.0 Universal dedication | cursor/LICENSE-awesome-cursorrules-cc0.txt / cursor/LICENSE-awesome-cursor-rules-mdc-cc0.txt |
| anthropics/skills webapp-testing / mcp-builder | skill単位のApache-2.0 | claude-code/webapp-testing/LICENSE.txt / claude-code/mcp-builder/LICENSE.txt |
| openai/skills playwright / screenshot | skill単位のApache-2.0。playwright由来のMicrosoft帰属は上記NOTICE全文 | openai-codex/playwright/LICENSE.txt / openai-codex/screenshot/LICENSE.txt |

### MIT許諾・免責文（上表のMIT由来部分）

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 出荷境界と非選定

- 非選定: KA-REF-003 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-011 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-012 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-013 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-014 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-015 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-016 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-017 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-032 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-033 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-037 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。
- 非選定: KA-REF-038 — BY-SA 接地の出荷隔離。本文と構成依存へ転写しない。

- 隔離解除は既存export-policy・adr/0007の条件に従う。本Composeは解除しない。039のrelated_knowledgeから隔離資産を推移的に収載しない。
- 社内源泉カードは構成依存に含めない。snapshots/・corpus/の凍結原本はdistへ複製しない。NOTICEの引継ぎとsource対応は監査情報。
- sourceは接地用seed。同一凍結原本を同一Contractのeval-only素材へ転用しない。説明例に評価数値・正式結果を付けない。

## 再コンパイルと供給の位置づけ

版・status・supply_mode・contractの変更時は資産から再構成し、構成の整合を確認する。版の差分は`/loop-report`、statusを含む依存整合はcompose gateで確認する。最早review_byは2027-01-25。供給先で独自に書き換えず、鮮度管理はfactory側に帰属する。

既存PoCの維持条件は`adr/0010-l1-supply-poc-and-gate4-deferral.md`、撤収手順は`factory/docs/consumer-supply-withdrawal.md`。今回の再Composeを、既存PoCの正式再受入・新しい供給receipt・実consumerでの確認済みと読み替えない。
