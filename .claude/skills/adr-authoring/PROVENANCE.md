# PROVENANCE — adr-authoring

- compiled_at: 2026-09-14 ／ compose: `/loop-compose operation adr-authoring`
- 再生成の根拠: `factory/docs/assessments/skills-practicality-review-20260914.md` F01と、利用者の修正指示。
  KA-ADR-002 0.2.0の方言B＋付随記録を反映し、既存K・SO・Contractの検査項目を維持した。
  本修正をカードの人間レビュー、Contract改訂・校正、正式受入の成立とは扱わない。
- **本ファイル・SKILL.md はビルド成果物。手編集禁止**（SSOTは `assets/` と選定・改善記録）。

## compiled 一覧（5列）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-ADR-001 | 0.1.0 | validated | authoritative | CT-ADR-001 |
| KA-ADR-002 | 0.2.0 | validated | advisory | null |
| KA-ART-001 | 0.1.0 | validated | advisory | CT-ADR-001 |
| CT-ADR-001 | 0.2.0 | validated | N/A | N/A |

## カード ↔ 節 対応表

| カード | 反映項目 | 反映先 | 接地と具体化の範囲 |
|---|---|---|---|
| KA-ADR-001 | K-01 | R-01・方言A/B・自己チェック | copilot cADR L52–96、codex ndb L35–41。4スロットを保持。方言Bは付随記録と参照先のRuleを合わせて確認 |
| KA-ADR-001 | K-02 | R-02・両方言のConsequences・INV-02 | cADR L24/L60–72、agen L104–108、ndb L40。決定固有の正負両記 |
| KA-ADR-001 | K-03 | R-03・Alternatives Considered・INV-03 | cADR L25/L74–84、agen L121–123、bmadS L21、ndb L39/L54。代替案と却下理由を付随記録でも省略しない |
| KA-ADR-001 | K-04 | R-04・付随記録のstatus・INV-04 | cADR L38/L50、ndb L11。5値を保持。spine全体のdraft/final・ADOPTEDタグへ代用しない |
| KA-ADR-001 | K-05 | R-05・新旧付随記録のリンク・INV-05 | cADR L42–43、ndb L11/L55。旧記録を保持し、旧Supersededと双方向参照を確認 |
| KA-ADR-001 | K-06 | R-06・spineのID列と付随記録・INV-06 | cADR L29、agen L28–30/L181、bmadS L35/L81、bmadL L119–134。決定IDを採番し、付随記録の同じIDは参照キーとして扱う |
| KA-ADR-001 | K-07 | R-07・両方言のauthors/stakeholders・INV-07 | cADR L15/L40、ndb L14–15。原型Aのauthorsだけで両役割を同一視せず、影響者欄を分ける |
| KA-ADR-001 | K-08 | R-08・関連/継承の参照・INV-08 | cADR L94、bmadS L31、ndb L16/L56。関連決定が存在するときの明示参照 |
| KA-ADR-001 | K-09 | R-09・両方言の構造化・INV-09 | cADR L26/L33–44、spine-template L1–14、ndb L7–16。付随記録はfrontmatterまたは同等の構造化エントリ |
| KA-ADR-001 | K-10 | R-10・組全体の確認・validation | agen L177–195、reviewer-gate L5/L11。欄の存在と内容を分け、確定前に既存の全項目を照合 |
| KA-ADR-002 | 方言A原型とK-07補足 | 単票テンプレ | cADR L35–97の様式を再構成。authors/stakeholdersの役割分離は0.2.0の補足から生成 |
| KA-ADR-002 | 方言B原型＋完成形 | ブロック・付随記録・共通ルール対応表 | spine-template L36–40とbmadS L17/L35の分離方針、KA-ADR-001の全Kを合成。原本の完全転記ではなく、本リポジトリが既存必須情報の記入先を具体化したもの。新しいINV/DEV・固定schemaではない |
| KA-ART-001 | 既存代表例 | examples/adr-0001-judge-model-pinning.md | runs/13/13-CT-ADR-001-1/output.mdの既存全文ビルドコピーを保持。今回の修正で本文・過去の証拠を改変しない |
| CT-ADR-001 | INV-01〜10・DEV-01〜04・採点/N-A条件 | validation | 0.2.0の全チェックリストを維持。自己チェックで正式採点を代行せず、正式判定が必要ならContract本体と独立verifierを別途使用する |

略記はすべて `factory/snapshots/oss/` 配下:
- cADR = github-copilot/create-architectural-decision-record-SKILL.md
- agen = github-copilot/adr-generator.agent.md
- bmadS = bmad-method/bmad-architecture-SKILL.md
- bmadL = bmad-method/bmad-architecture-lint_spine.py
- spine-template = bmad-method/bmad-architecture-spine-template.md
- reviewer-gate = bmad-method/bmad-architecture-reviewer-gate.md
- ndb = openai-codex/notion-knowledge-capture/decision-log-database.md

方言Bのrationaleを付随記録へ分ける方針はbmadS L17、共通必須情報はKA-ADR-001の各Kへ接地する。
付随記録のファイル名・欄名はこの合成での記入補助であり、BMADの固定形式として帰属させない。
参照を読めない場合・別IDを指す場合は不足とし、方言差を理由に既存検査項目を免除しない。

## SO 選定状態（KA-ADR-001 全9項目）

既存packの追加観点を維持し、観測できる条件を本文へ明示した。新たなSOの選定は行っていない。
SO-06以外の追加観点をContractの正式な検査へ活性化したとは扱わない。

| SO-ID | 状態 | 反映先・条件・強度の境界 |
|---|---|---|
| SO-01 | 条件付き収載 | A-01・方言A。方言Aのコード体系を使う場合の項目コード。一般のADR全てへ固定しない |
| SO-02 | 条件付き収載 | A-02・方言A。方言Aの配置を使う場合の命名・保存先。案件が選んだ様式として使う |
| SO-03 | 条件付き収載 | A-03。必須入力が確定できないとき、捏造せず不足を要求する既存観点 |
| SO-04 | 条件付き収載 | A-04・方言B。方言Bを使うときのBinds/Prevents/Rule。付随記録と合わせて使う |
| SO-05 | 条件付き収載 | A-05。方言Bへ記録する決定を選ぶときの非互換選択・非自明・トレードオフの確認。新しい正式採点ではない |
| SO-06 | 条件付き収載 | A-06・継承参照・DEV-04。親/継承決定への明示参照があるときの矛盾の表面化。既存CT-ADR-001 DEV-04の条件を維持。packの自己チェックだけで正式判定しない |
| SO-07 | 条件付き収載 | A-07・Deferred。意図的に先送りする事項がある場合に理由を記録。無言の未決定を残さない |
| SO-08 | 条件付き収載 | A-08。決定時の即時記録と、古い決定を保守するときの見直し。自動スケジュールや新たなゲートは作らない |
| SO-09 | 条件付き収載 | A-09。分類別に参照する運用を採る場合のImpact/Domain。全案件への必須欄にしない |

## SO 選定状態（KA-ART-001 全4項目）

| SO-ID | 状態 | 反映先・条件・強度の境界 |
|---|---|---|
| SO-01 | 条件付き収載 | 代表例とexamples案内。最初のADRを読む場面で、採番起点と関連/置換なしの明示を示す。案件のIDを固定しない |
| SO-02 | 条件付き収載 | 代表例とexamples案内。代替案と却下理由を記述する場面の参考。過去の実測値を新規案件の証拠にしない |
| SO-03 | 条件付き収載 | 代表例とexamples案内。負の帰結を記す場面の参考。例のリスクを全決定へ複写しない |
| SO-04 | 条件付き収載 | 代表例とexamples案内。将来の置換を記述する場面の参考。例の人間承認手順を全案件の規則へ移植しない |

KA-ADR-002自体にはSO-ID節を持たない。上記SOは既存本文・既存代表例の収載状態を記録したもの。

## 属性・バッジ・検証経路

| id | status | review_status | supply_mode | contract | evidence_strength | volatility / review_by |
|---|---|---|---|---|---|---|
| KA-ADR-001 | validated | 未記載（schema既定: unreviewed） | authoritative | CT-ADR-001 | community-consensus | volatile / 2027-01-11 |
| KA-ADR-002 | validated | 未記載（schema既定: unreviewed） | advisory | null | community-consensus | volatile / 2027-01-18 |
| KA-ART-001 | validated | 未記載（schema既定: unreviewed） | advisory | CT-ADR-001 | project-confirmed | stable / null |

- `DRAFT = false`。構成資産のstatusは全てvalidatedであり、今回の内容変更で元statusを変更していない。
- `ADVISORY = true`。原因はKA-ADR-002とKA-ART-001のsupply_mode。KA-ART-001はContract接続済みでもadvisoryであり、「Contract対象外」と記さない。
- weakest-link規則によりpack全体をSHOULD相当として扱う。KA-ADR-001やCT由来の部分だけ強い側へ戻さない。
- validationは記録の自己チェックとしてフル維持。正式判定にはContract本体・独立したverifierとその実行結果が別途必要であり、自己チェックから架空のPASSや受入済みを作らない。
- 既存代表例の過去の判定はruns/13/13-CT-ADR-001-1/judgement.md（PASS 10.0、CFなし、INV-05/08 N/A）。これは当該過去成果物の証拠であり、再生成したpackや新しく書いたADRの正式判定ではない。
- 新しいContract・人間ラベル・receiptは作成していない。代表例をこの修正の評価ケースへ転用していない。

## 元 OSS ライセンス（帰属・NOTICE）

| カード | 上流・凍結LICENSE | ライセンス・帰属 | NOTICE | 互換判定 |
|---|---|---|---|---|
| KA-ADR-001 / KA-ADR-002 | github/awesome-copilot — github-copilot/LICENSE-github-copilot.txt | MIT / Copyright GitHub, Inc. | 凍結収録範囲になし | 互換 |
| KA-ADR-001 / KA-ADR-002 | bmad-code-org/BMAD-METHOD — bmad-method/LICENSE-bmad-method.txt | MIT / Copyright (c) 2025 BMad Code, LLC | LICENSE末尾の商標通知を下記へ全文継承 | 互換 |
| KA-ADR-001 | openai/skills notion-knowledge-capture — openai-codex/notion-knowledge-capture/LICENSE.txt | MIT / Copyright 2025 Notion Labs, Inc. | skill凍結ディレクトリにNOTICEなし | 互換 |
| KA-ART-001 | origin: synthetic | 本リポジトリ生成物 | 上流NOTICEなし | 同梱の既存代表例を維持 |

版固定は `factory/snapshots/oss/PROVENANCE.md`（collected 2026-07-02 / frozen 2026-07-07）。
snapshots/・corpus/の複製は出荷しない。以下はBMADの凍結LICENSE末尾の通知である。

```text
TRADEMARK NOTICE:
BMad™, BMad Method™, and BMad Core™ are trademarks of BMad Code, LLC, covering all
casings and variations (including BMAD, bmad, BMadMethod, BMAD-METHOD, etc.). The use of
these trademarks in this software does not grant any rights to use the trademarks
for any other purpose. See [TRADEMARK.md](TRADEMARK.md) for detailed guidelines.
```

- 非選定（BY-SA隔離）: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015
- 非選定（BY-SA隔離）: KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038
- 非選定（内部源泉・今回の出荷範囲外）: KA-REF-056, KA-REF-057, KA-REF-058, KA-REF-059

## 再コンパイル条件

構成資産のversion・status・供給属性、方言と付随記録の選定・対応が変わったら再生成する。
版の差分は /loop-report、statusを含む依存整合はcompose gateで確認する。
