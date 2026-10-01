# PROVENANCE — systematic-debugging

- compiled_at: 2026-09-14
- compose: /loop-compose operation systematic-debugging --include-draft
- 選定根拠: [設計・開発工程Compose計画](../../../../docs/proposals/design-development-phase-compose-selection-20260914.md) rev2 §2.1。利用者が具体的な補強案を受けて「補強を行う」と指示したことを、SO-01／SO-07の静的advisory収載の根拠とする。初回に収載したK全件を維持し、選定SOを条件付きの作業手順へ再構成した。カード本文の人間レビュー、Contract活性化・新設・昇格を行ったことにはしない。
- 追加の選定・適用根拠（2026-09-14）: [全20 Skillの実務レビュー](../../../../docs/assessments/skills-practicality-review-20260914.md)と[実務改善・選定記録](../../../../docs/proposals/skills-practicality-improvement-20260914.md)に対する利用者の修正指示。デバッグのSO-05／09を条件付き部分採用する。観測で外部・環境・タイミング起因が確定した場合に、変更権限・必要な対処・引渡しと未解決を分ける。固定enum、源泉の自己申告成功率、retry・監視等の自動追加は非採用。資産0.1.1の適用条件とSO-01／07の既存選定を保持する。 この指示はカード本文のhuman-reviewed化・Contract改訂・正式受入を意味しない。
- 本ファイルとSKILL.mdは資産カードから再構成した生成物。SSOTはassets/。source versionの更新は再コンパイル対象とし、status・supply_mode・contractの変更も構成整合を再確認する。
- 構成・静的確認と正式D1受入を分ける。本文生成をもって正式D1受入や実consumer供給の完了とは扱わない。

## compiled 一覧（5列）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-026 | 0.1.1 | draft | authoritative | null |

## カード別の軸と検証経路

| カード | status | review_status | supply_mode | contract | evidence_strength | volatility / review_by | 本pack |
|---|---|---|---|---|---|---|---|
| KA-REF-026 | draft | 未記載（schema既定: unreviewed） | authoritative | null | community-consensus | volatile / 2027-03-08 | advisory |

source contract 欄の検証経路はエンジン還元（loop-cycle の停止・エスカレーション規律への外部接地）。原因分析・修正報告用の正式 Contract は接続されていない。

- DRAFT式はtrue（構成資産status=draft）。ADVISORY式はtrue（authoritativeかつcontract=null）。冒頭の定型をDRAFT→ADVISORYの順で置き、原因資産を1行で明記した。
- statusは校正ライフサイクル、review_statusはカード本文のレビュー状態。DRAFTを「人間レビュー未実施」や「judge未実行」と読み替えない。
- カード由来の知識はpack全体でSHOULD相当。新しいINV／DEV、正式採点、合否、工程遷移ゲートは作らない。案件に既にある制約・承認を弱める根拠にはしない。
- 校正・実務妥当性の評価数値は転記していない。

## カード ↔ 手順 ↔ 凍結source

SSOTは `assets/reference/KA-REF-026.md`。下表のsourceはすべて `factory/snapshots/oss/` からの相対パス。
収穫時の版固定・ライセンス記録は `factory/snapshots/oss/PROVENANCE.md` を参照する。

| カード項目 | SKILL反映先 | 保持した意味 | 凍結sourceの接地箇所 |
|---|---|---|---|
| K-01 | 証拠を集めて再現する／発生源を追って一つの仮説にする | 原因調査前の推測修正を避け、観測と原因のつながりを示す | superpowers/systematic-debugging-SKILL.md L12・19・22、cc-sdd/kiro-debug-SKILL.md L12・22、github-copilot/debug.agent.md L72・80 |
| K-02 | 手順1〜4 | 調査→分析→修正→検証を順に実行し、緊急・単純を理由に飛ばさない | superpowers/systematic-debugging-SKILL.md L41–48、github-copilot/debug.agent.md L9、cc-sdd/kiro-debug-SKILL.md L50–114 |
| K-03 | 証拠を集めて再現する | エラー全文・再現手順・直近差分／履歴／依存／設定の確認、再現不能なら追加調査 | superpowers/systematic-debugging-SKILL.md L54–70、github-copilot/debug.agent.md L19–28・37、cc-sdd/kiro-debug-SKILL.md L52–66 |
| K-04 | 発生源を追って一つの仮説にする／原因に対応する最小修正 | 一仮説を明記し一変数を最小変更、効かない修正へ積み増さない | superpowers/systematic-debugging-SKILL.md L149–162、cc-sdd/kiro-debug-SKILL.md L118、github-copilot/debug.agent.md L47・74 |
| K-05 | 発生源を追って一つの仮説にする／原因に対応する最小修正 | 呼出し・値・状態を遡り、症状箇所だけの抑止を避けて源流を直す | superpowers/systematic-debugging-root-cause-tracing.md L7・154、superpowers/systematic-debugging-SKILL.md L110–120、github-copilot/debug.agent.md L33–35 |
| K-06 | コード変更で対応する場合の最小修正／修正後の元症状・回帰検証／結果表 | コード修正前の失敗テスト、元手順の再実行、広い回帰、テスト追加・更新、コマンド記録。外部対応待ちを修正済みとしない | superpowers/systematic-debugging-SKILL.md L174–178・187–190、github-copilot/debug.agent.md L52–56・61、cc-sdd/kiro-debug-SKILL.md L43・148 |
| K-07 | 調査の対象と反復の上限を確認する／修正が効かない場合 | 試行を数え、新情報を持って調査へ戻り、規定上限で停止・設計前提を判断経路へ返す | superpowers/systematic-debugging-SKILL.md L192–213、cc-sdd/kiro-debug-SKILL.md L106–114・122–128 |
| SO-01 | 症状が複数のコンポーネントを通る場合／結果表 | 各境界の入出力・環境や設定の伝播・状態を観測し、同じ再現実行で最初の破綻層を絞る。多層の症状に限るadvisory手順 | superpowers/systematic-debugging-SKILL.md L72–87・108 |
| SO-07 | 依存・ランタイムに関わる障害の場合／結果表 | 正確なエラー・技術と症状・実バージョンを用い、web利用時は公式かつ対象版の情報を優先して観測と照合する。依存・ランタイム障害に限るadvisory手順 | cc-sdd/kiro-debug-SKILL.md L59–79・137 |
| SO-05（対応可能範囲と引渡し部分） | 原因が分かったら対応できる範囲を分ける／結果表 | 外部要因に必要な権限・前提がない場合の具体的な引渡し、repo内で対応できる原因の早すぎる委譲を避ける | cc-sdd/kiro-debug-SKILL.md L94–128。固定NEXT_ACTION enumは非収載 |
| SO-09（外部・環境起因確定後の処理部分） | 原因が分かったら対応できる範囲を分ける／結果表 | 裏付けた環境・タイミング・外部要因、調査記録、必要な対処・観測、未確認事項を整理する | superpowers/systematic-debugging-SKILL.md L267–276。源泉の自己申告成功率、無条件のretry等は非収載 |

### 再構成上の境界

- K-07の「規定回数」は案件の既存上限を確認する。未設定なら有限の上限を案件の運用に沿って確定してから修正反復を始める。これは初回Composeの適用境界であり、新しい固定値・runtime selector・承認フローではない。
- sourceの「3回」はsuperpowers単独の具象例なので、本packの共通上限にはしない。既存エンジンの停止条件を置換・延長しない。
- 報告表はK-01／03／04／06／07を実作業で残すための整理であり、SO-04の固定schema・enumではない。正式な合否判定や機械状態遷移へ使わない。
- SO-01／07の条件をSKILLの証拠収集内の分岐へ明示し、該当時の結果を報告表へ残す。runtime selector・別trigger・正式判定は追加しない。
- SO-01の凍結source L89–105にある固定シェル・署名ツールの例は転写しない。観測は案件の診断手段に合わせ、秘密値の出力を避ける。観測できない層を未確認とする扱いは、証拠を推測で補わない適用境界。
- SO-07でwebが使えない場合は外部情報を未確認とし、実バージョンが不明なら資料との版一致を確認済みとしない。利用不能を成功へ読み替えず、既存のローカル証拠収集を進める。固定検索ツールや現在の推奨版は指定しない。
- SO-05／09は観測で環境・タイミング・外部要因を裏付けた場合に使う。原因未特定・再現不能だけでは外部起因としない。権限不足なら証拠・必要な対応・再確認条件を既存の担当経路へ渡し、引渡しを解決と混同しない。必要な対処・観測を検討するが、本packだけを理由にretry・timeout・監視を実装しない。コード変更で対応する場合はK-06の失敗テストと回帰確認を維持する。
- 資産0.1.1のK-01／06はコード修正と外部対応の境界を明示したもの。調査→原因分析を飛ばさず、変更しない引渡しで未実施のコード検証を実施済みとしない。独立の実行dispatch・新承認フローを追加していない。
- source volatility はSO-04／05の固定語彙に属する。今回その具象を転写していない。

## SO選定状態（全10項目）

rev2 §2.1のSO-01／07と実務改善・選定記録のSO-05／09部分を条件付きの静的advisoryとして収載する。条件は本文の証拠収集・原因確定後の対応で判断し、Contractの活性化や正式な合否条件には使わない。

| SO-ID | 状態 | 反映先 | 観測可能な適用条件 | 非収載部分・理由／advisory境界 |
|---|---|---|---|---|
| SO-01 | 条件付き収載 | 複数コンポーネントの証拠収集、結果表 | 症状が複数のコンポーネントを通る場合 | 境界計装と同一実行の照合を収載。固定シェル・署名ツールの例は非収載。修正前の診断助言であり合否条件ではない |
| SO-02 | 非収載 | なし | なし（未選定） | JavaScriptのstack注入・console.error・汚染テスト探索スクリプトは今回の選定外 |
| SO-03 | 非収載 | なし | なし（未選定） | 全経路へのdefense-in-depth追加は今回の選定外。K-05の源流修正まで |
| SO-04 | 非収載 | なし | なし（未選定） | 固定フィールド・CATEGORY 10値・NEXT_ACTION 3値の報告プロトコルは導入しない |
| SO-05 | 条件付き収載 | 原因確定後の対応範囲表、引渡しと結果表 | 観測で外部・環境起因を確かめ、対応に権限・前提の不足がある場合 | 証拠・必要な対応・再確認条件の引渡しを収載。repo内で直せる原因を早々に委譲しない。固定enum・機械状態遷移・共通承認手続きは非収載 |
| SO-06 | 非収載 | なし | なし（未選定） | fresh-contextの別エージェント調査は今回の選定外 |
| SO-07 | 条件付き収載 | 依存・ランタイムの情報確認、結果表 | 依存・ランタイム障害を調べる場合。web利用可なら外部調査を実行 | 正確なエラー・実バージョン・公式情報の照合を収載。固定検索ツールは指定しない。web不可・版不明は未確認として残す |
| SO-08 | 非収載 | なし | なし（未選定） | 固定red flags・合理化対照表・人間の信号リストは今回の選定外 |
| SO-09 | 条件付き収載 | 原因確定後の対応範囲表、引渡しと結果表 | 環境・タイミング・外部要因が観測で裏付けられた場合 | 調査・裏付け・不明点、必要な対処・観測と権限を整理する。自己申告成功率やretry・timeout・監視の自動追加は非収載。原因不明を外部確定としない |
| SO-10 | 非収載 | なし | なし（未選定） | 所要時間・成功率の源泉自己申告値を一般的な効果として転写しない |

## 元OSSライセンス・帰属・NOTICE

LICENSEのパスは `factory/snapshots/oss/` からの相対。以下の帰属表示とMIT許諾・免責文を引き継ぐ。

| 上流 | license | 著作権・帰属 | 凍結LICENSE | NOTICE |
|---|---|---|---|---|
| obra/superpowers | MIT | Copyright (c) 2025 Jesse Vincent | superpowers/LICENSE-superpowers.txt | 凍結資料に独立NOTICEなし |
| gotalab/cc-sdd | MIT | Copyright (c) 2025 gotalab | cc-sdd/LICENSE-cc-sdd.txt | 凍結資料に独立NOTICEなし |
| github/awesome-copilot | MIT | Copyright GitHub, Inc. | github-copilot/LICENSE-github-copilot.txt | 凍結資料に独立NOTICEなし |


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
