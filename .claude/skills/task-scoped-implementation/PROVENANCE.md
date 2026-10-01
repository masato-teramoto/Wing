# PROVENANCE — task-scoped-implementation

- compiled_at: 2026-09-14
- compose: /loop-compose phase task-scoped-implementation --include-draft
- 選定根拠: [設計・開発工程Compose計画](../../../../docs/proposals/design-development-phase-compose-selection-20260914.md) rev2 §2.1。利用者が具体的な補強案を受けて「補強を行う」と指示したことを、SO-02／SO-04の静的advisory収載の根拠とする。初回に収載したK全件を維持し、選定SOを条件付きの作業手順へ再構成した。カード本文の人間レビュー、Contract活性化・新設・昇格を行ったことにはしない。
- 追加の選定・適用根拠（2026-09-14）: [全20 Skillの実務レビュー](../../../../docs/assessments/skills-practicality-review-20260914.md)と[実務改善・選定記録](../../../../docs/proposals/skills-practicality-improvement-20260914.md)に対する利用者の修正指示。F04に対し凍結sourceから新しく明示したK-06を資産0.1.1に収穫し、完了条件→新規・変更挙動→確認方法・期待・実結果を既存機能の回帰と分けた。SO-02／04の既存選定は維持する。 この指示はカード本文のhuman-reviewed化・Contract改訂・正式受入を意味しない。
- 本ファイルとSKILL.mdは資産カードから再構成した生成物。SSOTはassets/。source versionの更新は再コンパイル対象とし、status・supply_mode・contractの変更も構成整合を再確認する。
- 構成・静的確認と正式D1受入を分ける。本文生成をもって正式D1受入や実consumer供給の完了とは扱わない。

## compiled 一覧（5列）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-027 | 0.1.1 | draft | authoritative | null |

## カード別の軸と検証経路

| カード | status | review_status | supply_mode | contract | evidence_strength | volatility / review_by | 本pack |
|---|---|---|---|---|---|---|---|
| KA-REF-027 | draft | 未記載（schema既定: unreviewed） | authoritative | null | community-consensus | stable / null | advisory |

source contract 欄の検証経路はエンジン還元（loop-implementer の編集スコープ規律）。実装系 Contract の設計時にCT化を再判断する記録であり、本pack用の正式 Contract は接続されていない。

- DRAFT式はtrue（構成資産status=draft）。ADVISORY式はtrue（authoritativeかつcontract=null）。冒頭の定型をDRAFT→ADVISORYの順で置き、原因資産を1行で明記した。
- statusは校正ライフサイクル、review_statusはカード本文のレビュー状態。DRAFTを「人間レビュー未実施」や「judge未実行」と読み替えない。
- カード由来の知識はpack全体でSHOULD相当。新しいINV／DEV、正式採点、合否、工程遷移ゲートは作らない。案件に既にある制約・承認を弱める根拠にはしない。
- 校正・実務妥当性の評価数値は転記していない。

## カード ↔ 手順 ↔ 凍結source

SSOTは `assets/reference/KA-REF-027.md`。下表のsourceはすべて `factory/snapshots/oss/` からの相対パス。
収穫時の版固定・ライセンス記録は `factory/snapshots/oss/PROVENANCE.md` を参照する。

| カード項目 | SKILL反映先 | 保持した意味 | 凍結sourceの接地箇所 |
|---|---|---|---|
| K-01 | 要求に必要な変更だけを作る／納品前の確認 | 全変更を明示要求・承認済みタスクに対応づける | cursor/anti-overengineering.mdc L8・10、cursor/codequality.mdc L27、bmad-method/bmad-dev-story-SKILL.md L337、cc-sdd/kiro-review-SKILL.md L149 |
| K-02 | 要求に必要な変更だけを作る／納品前の確認 | 不要な抽象化・依存・全書換・条件処理・追加機能の抑制 | cursor/anti-overengineering.mdc L10、bmad-method/bmad-dev-story-SKILL.md L365、cc-sdd/kiro-review-SKILL.md L149 |
| K-03 | 着手前に編集境界を宣言する／納品前の確認 | 事前のファイル・領域宣言と実変更集合の包含照合 | bmad-method/bmad-dev-story-SKILL.md L13、bmad-method/bmad-dev-story-checklist.md L15・56、cc-sdd/kiro-review-SKILL.md L37・81–83、cursor/anti-overengineering.mdc L12 |
| K-04 | 要求に必要な変更だけを作る／納品前の確認 | 無関係なコード・機能・構造を保全し既存テストで回帰確認 | cursor/codequality.mdc L33、bmad-method/bmad-dev-story-SKILL.md L352、bmad-method/bmad-dev-story-checklist.md L46、cc-sdd/kiro-review-SKILL.md L69–71 |
| K-05 | 境界の外に出る必要が生じたら | 境界外の必要・要求不明・所有権不明を黙って迂回せず、既存の判断経路へ返す | cursor/anti-overengineering.mdc L8、bmad-method/bmad-dev-story-SKILL.md L333・335、cc-sdd/kiro-review-SKILL.md L141–142 |
| K-06 | 着手時の達成検証／納品前の達成表／実装結果の引渡し | 完了条件と新規・変更挙動の具体的確認を結び、既存機能の回帰と分離。方法・入力・期待・実結果・未確認を残す | bmad-method/bmad-dev-story-SKILL.md L344–347・352–355・365–367、cc-sdd/kiro-review-SKILL.md L101–106・120–122 |
| SO-02 | 隣接する責務に関わる変更を自己確認する／納品前の確認 | 隠れた越境調整、下流固有処理の上流への押込み、隠れ依存・共有所有・未宣言結合、暗黙の統合作業を実装者の自己確認へ再構成。隣接責務に関わる変更時のadvisory | cc-sdd/kiro-review-SKILL.md L84・114–118。L130のCritical判定は非収載 |
| SO-04 | 実装結果を引き渡す | 今回新規作成・変更・削除した全ファイルをrepo相対パスと種別で列挙し、実変更集合と照合する。ファイル変更がある引渡し時のadvisory | bmad-method/bmad-dev-story-SKILL.md L387、bmad-method/bmad-dev-story-checklist.md L52 |

### 再構成上の境界

- K-06はF04に基づき同じ凍結sourceから未収穫だった達成検証を明示した資産0.1.1の新規収穫。BMADの既存テスト／新しい挙動のテスト／受入条件を分ける手順とcc-sddの具体的・観測可能な受入挙動の確認を接続した。内容・設定変更等への手動照合は今回の修正指示に沿う適用整理であり、凍結sourceの一律要件とは主張しない。既存テストが達成を直接示せれば利用し、不足時に変更に適した追加確認を選ぶ。全変更への新規テスト・TDD義務を加えない。
- 入力拒否の短い例はK-06の「正常系の回帰だけでは新しい拒否挙動を示さない」という対応を説明する合成例。実案件の結果・正式評価ケース・評価数値ではない。

- パスの実在／新規予定場所の確認はK-03の事前境界宣言を具体化したもの。既存未commit変更と今回の変更を区別し、他の変更を破棄する根拠にしない。
- K-05は既存の要求・承認を先に確認し、それを超える部分だけ案件の既存経路で扱う。既に認められた範囲について新たな承認を一律に要求しない。
- 着手記録と納品前照合はK-01／03／04／05の実行用整理。SO-04は別に、今回の全作成・変更・削除パスを成果物へ残す部分を収載する。BMADの固定File List欄・文書更新手順・新しい機械schemaは採用しない。
- SO-02の4観点は、隣接責務に関わる変更を作る側の自己確認へ再構成する。sourceのreviewerによる棄却・Critical severity・正式採点は収載しない。既に承認された統合や連携は越境と断定せず、未宣言の追加責務をK-05の既存確認経路へ戻す。
- SO-02／04の条件は本文の作業内で判断する。新しいreview trigger・runtime selector・承認フローは追加しない。ファイル一覧では既存の作業変更を今回の成果に混ぜず、削除対象も省略しない。
- コード品質・文書同期（KA-REF-040／KA-REF-053）、実装計画、受入レビューは構成依存に混ぜていない。本文の別pack参照は責任分担の案内であり自動起動や必須導入ではない。

## SO選定状態（全5項目）

rev2 §2.1の選定SOだけを条件付きの静的advisoryとして収載する。条件は本文の実装・引渡し作業で判断し、Contractの活性化や正式な合否条件には使わない。

| SO-ID | 状態 | 反映先 | 観測可能な適用条件 | 非収載部分・理由／advisory境界 |
|---|---|---|---|---|
| SO-01 | 非収載 | なし | なし（未選定） | discovery/design/tasks/review固有の境界語彙の4段連鎖は今回の選定外 |
| SO-02 | 条件付き収載 | 隣接責務の自己確認、納品前の確認 | 変更が呼出し・データ受渡し・共有状態などを通じ隣接責務に関わる場合 | 4種の未宣言越境を作業者の自己確認へ収載。reviewerの棄却・Critical判定は非収載。明示された統合作業は一律に越境としない |
| SO-03 | 非収載 | なし | なし（未選定） | ファイル単位・単一チャンクという編集提示形式は強制しない |
| SO-04 | 条件付き収載 | 実装結果の全変更ファイル一覧 | 新規作成・変更・削除したファイルがあり、実装結果を引き渡す場合 | 全ファイルのrepo相対パス・種別・実変更集合との照合を収載。BMAD固定欄・新しい機械schemaは非収載 |
| SO-05 | 非収載 | なし | なし（未選定） | 全タスクの固定順序・先行着手禁止を共通の実行制御にしない |

## 元OSSライセンス・帰属・NOTICE

LICENSEのパスは `factory/snapshots/oss/` からの相対。以下の帰属表示とMIT許諾・免責文を引き継ぐ。

| 上流 | license | 著作権・帰属 | 凍結LICENSE | NOTICE |
|---|---|---|---|---|
| PatrickJS/awesome-cursorrules | CC0-1.0 | CC0 1.0 Universal dedication | cursor/LICENSE-awesome-cursorrules-cc0.txt | 凍結資料に独立NOTICEなし |
| gotalab/cc-sdd | MIT | Copyright (c) 2025 gotalab | cc-sdd/LICENSE-cc-sdd.txt | 凍結資料に独立NOTICEなし |
| bmad-code-org/BMAD-METHOD | MIT | Copyright (c) 2025 BMad Code, LLC | bmad-method/LICENSE-bmad-method.txt | 独立NOTICEなし／LICENSE内商標通知を下記継承 |

BMADのLICENSE追補: “This project incorporates contributions from the open source community. See [CONTRIBUTORS.md](CONTRIBUTORS.md) for contributor attribution.” 当該CONTRIBUTORS参照は上流リポジトリの帰属情報を指す。本pack内への原本複製を意味しない。

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

### BMADのLICENSE内商標通知（全文）

TRADEMARK NOTICE:
BMad™, BMad Method™, and BMad Core™ are trademarks of BMad Code, LLC, covering all
casings and variations (including BMAD, bmad, BMadMethod, BMAD-METHOD, etc.). The use of
these trademarks in this software does not grant any rights to use the trademarks
for any other purpose. See [TRADEMARK.md](TRADEMARK.md) for detailed guidelines.

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
