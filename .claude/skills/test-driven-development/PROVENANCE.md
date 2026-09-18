# PROVENANCE — test-driven-development

- compiled_at: 2026-09-14
- compose: /loop-compose operation test-driven-development --include-draft
- 選定根拠: [設計・開発工程Compose計画](../../../../docs/proposals/design-development-phase-compose-selection-20260914.md) rev2 §2.1。利用者が具体的な補強案を受けて「補強を行う」と指示したことを、SO-06のAAA・挙動命名部分の静的advisory収載の根拠とする。初回に収載したK全件を維持し、選定部分を条件付きの作業手順へ再構成した。カード本文の人間レビュー、Contract活性化・新設・昇格を行ったことにはしない。
- 追加の選定・適用根拠（2026-09-14）: [全20 Skillの実務レビュー](../../../../docs/assessments/skills-practicality-review-20260914.md)と[実務改善・選定記録](../../../../docs/proposals/skills-practicality-improvement-20260914.md)に対する利用者の修正指示。TDDの初回成功について、要求を既存実装が満たす場合の適用境界を資産0.1.1へ記録し、RED結果表と報告へ反映した。新SO選定はなく、SO-06の既存選定を維持する。 この指示はカード本文のhuman-reviewed化・Contract改訂・正式受入を意味しない。
- 本ファイルとSKILL.mdは資産カードから再構成した生成物。SSOTはassets/。source versionの更新は再コンパイル対象とし、status・supply_mode・contractの変更も構成整合を再確認する。
- 構成・静的確認と正式D1受入を分ける。本文生成をもって正式D1受入や実consumer供給の完了とは扱わない。

## compiled 一覧（5列）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-025 | 0.1.1 | draft | authoritative | null |

## カード別の軸と検証経路

| カード | status | review_status | supply_mode | contract | evidence_strength | volatility / review_by | 本pack |
|---|---|---|---|---|---|---|---|
| KA-REF-025 | draft | 未記載（schema既定: unreviewed） | authoritative | null | community-consensus | volatile / 2027-03-01 | advisory |

source contract 欄の検証経路はエンジン還元（loop-implementer の TDD プロセス規律）。最終コードだけから実行順序を判定する正式 Contract は接続されていない。

- DRAFT式はtrue（構成資産status=draft）。ADVISORY式はtrue（authoritativeかつcontract=null）。冒頭の定型をDRAFT→ADVISORYの順で置き、原因資産を1行で明記した。
- statusは校正ライフサイクル、review_statusはカード本文のレビュー状態。DRAFTを「人間レビュー未実施」や「judge未実行」と読み替えない。
- カード由来の知識はpack全体でSHOULD相当。新しいINV／DEV、正式採点、合否、工程遷移ゲートは作らない。案件に既にある制約・承認を弱める根拠にはしない。
- 校正・実務妥当性の評価数値は転記していない。

## カード ↔ 手順 ↔ 凍結source

SSOTは `assets/reference/KA-REF-025.md`。下表のsourceはすべて `factory/snapshots/oss/` からの相対パス。
収穫時の版固定・ライセンス記録は `factory/snapshots/oss/PROVENANCE.md` を参照する。

| カード項目 | SKILL反映先 | 保持した意味 | 凍結sourceの接地箇所 |
|---|---|---|---|
| K-01 | 対象と確認事項を揃える／RED | TDD採用範囲を限定し、失敗の観測前に対応実装を書かない | superpowers/test-driven-development-SKILL.md L12・34・366–367、github-copilot/tdd-red.agent.md L30、cc-sdd/kiro-impl-SKILL.md L18、spec-kit/constitution-template.md L17–19 |
| K-02 | REDの結果別表 | 未実装による失敗と構文・準備エラー、初回成功、実行不能を分ける。初回成功は要求未観測と既に達成済みを分離 | superpowers/test-driven-development-SKILL.md L113–128、github-copilot/tdd-red.agent.md L32・57、cc-sdd/kiro-impl-SKILL.md L221–222 |
| K-03 | GREEN | 最小実装、要求外変更の抑制、テストの弱化・削除による成功の禁止 | superpowers/test-driven-development-SKILL.md L132・166・181、github-copilot/tdd-green.agent.md L8・19・50、cc-sdd/kiro-impl-SKILL.md L191 |
| K-04 | REFACTOR | 全テスト成功後の小さい構造変更、頻繁な再実行、挙動追加を分離 | superpowers/test-driven-development-SKILL.md L185–192、github-copilot/tdd-refactor.agent.md L75・77・91、cc-sdd/kiro-impl-SKILL.md L192 |
| K-05 | 対象と確認事項を揃える／REFACTOR | 一周一テスト・一テスト一挙動、次の挙動を次周へ分ける | github-copilot/tdd-red.agent.md L31・56、superpowers/test-driven-development-SKILL.md L73・108–110・202、cc-sdd/kiro-impl-SKILL.md L190 |
| K-06 | REDの記録が無い場合／実装結果を報告する | 実出力の添付、欠落・空・無関係の識別、修正前後の赤緑再確認 | cc-sdd/kiro-review-SKILL.md L86–88、superpowers/verification-before-completion-SKILL.md L87–91、superpowers/test-driven-development-SKILL.md L327–340 |
| SO-06（AAA・挙動命名部分） | REDの一テスト作成 | 前提・入力の準備→操作→観測可能な期待結果の確認、条件と期待する挙動を表す命名。新しい一挙動のテスト作成時のadvisory | github-copilot/tdd-red.agent.md L37–38。L37の固定起票番号、L44–47のフレームワーク指定は非収載 |

### 再構成上の境界

- 資産0.1.1のK-02適用整理を反映。元sourceの初回成功→テスト修正は未実装の期待が残る前提であり、要求を既に満たす場合の追加実装不要という出口は、K-03の要求外変更を避ける規律（superpowers L166、github-copilot/tdd-green.agent.md L19）と今回のレビュー・修正指示を接続したもの。凍結sourceに同じ出口の明文があるとは主張しない。要求・入力・期待・実結果を照合し、正常なコードを壊したり別要求を発明したりしない。この出口を新しいRED/GREENやTDD時系列の証拠にしない。

- K-06の再構成は、現在の変更を保持する使い捨て比較環境で「修正あり成功→修正だけなし失敗→修正復元成功」を確認する。作業中の未commit変更を自動破棄・revertしない適用境界は初回Composeの作業条件であり、SO-01の採用ではない。
- 事後の赤緑は回帰テストの検出力の証拠であり、元の実装順序の証拠として扱わない。再構成不能なら不足を残す。
- GREEN中にテスト自体の誤りを発見した場合はREDへ戻して正しい失敗を観測し直す。GREENのままテストを弱める例外は作らない。
- SO-06は新しい一挙動のテストを作るときに、既存のRED手順内で使う。AAAの骨格と条件・期待が分かる名前だけを収載し、固定起票番号・名前の固定構文・言語別フレームワーク指定は採用しない。新しい依存導入、runtime selector、別trigger、正式なテスト品質判定は追加しない。
- source volatility はSO-06のフレームワーク列挙に属する。今回その具象は転写せず、K-01〜06とSO-06の抽象的な作成手順を供給する。

## SO選定状態（全7項目）

rev2 §2.1で選定したSO-06の一部だけを条件付きの静的advisoryとして収載する。条件は本文のRED作業で判断し、Contractの活性化や正式な合否条件には使わない。

| SO-ID | 状態 | 反映先 | 観測可能な適用条件 | 非収載部分・理由／advisory境界 |
|---|---|---|---|---|
| SO-01 | 非収載 | なし | なし（未選定） | 先行実装の全削除は選定していない。作業中の変更の破棄を指示しない |
| SO-02 | 非収載 | なし | なし（未選定） | 合理化対照表と全削除を伴うred flagsは今回の選定外 |
| SO-03 | 非収載 | なし | なし（未選定） | TDD適用除外の一律追加承認フローは導入しない。採用済みの挙動変更に適用を限定する |
| SO-04 | 非収載 | なし | なし（未選定） | Feature Flag Protocolによる実装・フラグ導入は今回の選定外 |
| SO-05 | 非収載 | なし | なし（未選定） | RED／GREEN／REFACTORの3役エージェント分離は導入しない |
| SO-06 | 条件付き収載 | REDの一テスト作成 | 新しい一挙動のテストを作るとき | AAAと挙動命名だけを収載。固定起票番号・固定命名構文・言語別フレームワーク指定は非収載。テスト作成の助言であり正式品質判定ではない |
| SO-07 | 非収載 | なし | なし（未選定） | 独立SOとしての追加選定なし。元症状を再現するテストと修正前後の確認はK-01／K-06の範囲から保持 |

## 元OSSライセンス・帰属・NOTICE

LICENSEのパスは `factory/snapshots/oss/` からの相対。以下の帰属表示とMIT許諾・免責文を引き継ぐ。

| 上流 | license | 著作権・帰属 | 凍結LICENSE | NOTICE |
|---|---|---|---|---|
| obra/superpowers | MIT | Copyright (c) 2025 Jesse Vincent | superpowers/LICENSE-superpowers.txt | 凍結資料に独立NOTICEなし |
| obra/superpowers-skills（完了前検証の補助源） | MIT | Copyright (c) 2025 Jesse Vincent | superpowers/LICENSE-superpowers-skills.txt | 凍結資料に独立NOTICEなし |
| github/awesome-copilot | MIT | Copyright GitHub, Inc. | github-copilot/LICENSE-github-copilot.txt | 凍結資料に独立NOTICEなし |
| gotalab/cc-sdd | MIT | Copyright (c) 2025 gotalab | cc-sdd/LICENSE-cc-sdd.txt | 凍結資料に独立NOTICEなし |
| github/spec-kit | MIT | Copyright GitHub, Inc. | spec-kit/LICENSE-spec-kit.txt | 凍結資料に独立NOTICEなし |


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

- 隔離解除は既存export-policy・adr/0007の条件に従う。本Composeは解除しない。
- 内部源泉のカードは構成依存に含めない。
- snapshots/・corpus/の凍結原本はdistへ複製しない。上記のsource対応とlicense表示は監査情報であり、原本の複製ではない。
- sourceは接地用seed。同一Contractのeval-only素材に流用しない。
