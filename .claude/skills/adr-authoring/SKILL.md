---
name: adr-authoring
description: アーキテクチャ上の決定を ADR（単票文書または AD-n 決定ブロック）として記録・レビューするとき — 既存テンプレを転用して書き起こす場合も、書かれた ADR が「あとから判断根拠を追える」構造要件（必須スロット・帰結両記・代替案+却下理由・ID 安定性・機械可読構造）を満たすか照合する場合も、この skill を使う。対象は記録の書式規約に限る（アーキテクチャ設計内容の良し悪しは対象外）。
metadata:
  l2-compiled-from: "KA-ADR-001@0.1.0, KA-ADR-002@0.2.0, KA-ART-001@0.1.0, CT-ADR-001@0.2.0"
  l2-compiled-at: "2026-09-14"
---

> 本ファイルはビルド成果物（SSOT は `assets/`）。**手編集禁止** — 直すときは資産カードを直して再コンパイルする。
>
> **利用上の位置づけ: ADVISORY** — カード由来の知識は【SHOULD】相当の助言として、案件の前提・規約・制約と
> 照合して利用する。【MUST】／【MUST NOT】や、校正済み Contract に基づく正式な合否判定の根拠にはしない。
> カード別の Contract・レビュー状態・検証経路は同梱の `PROVENANCE.md` を参照する。
>
> - KA-ADR-002: advisory（カードの supply_mode に従い、本パックでは助言として供給。検証経路は PROVENANCE.md を参照）
> - KA-ART-001: advisory（カードの supply_mode に従い、本パックでは助言として供給。検証経路は PROVENANCE.md を参照）

# adr-authoring — ADR の書き方と検収規約

作成するか、提出された記録を確認するかを依頼から確かめる。作成時は案件で選んだ方言を使い、
末尾の validation 節で記入内容を自己チェックする。確認時は提出物を読み、欠落を補って元の記録が
充足していたことにせず、所在と不足を返す。自己チェックを正式判定や決定の承認と扱わない。

## ルール（全 ADR に適用）

- **R-01 必須スロット構造**: Context（なぜ必要か）/ Decision（何を決めたか）/
  Alternatives Considered（代替案+却下理由）/ Consequences（帰結）の4スロットを必ず全て書く。
- **R-02 帰結の正負両記**: Consequences に positive / negative の両方を書く。利点のみで終わらせない
  （トレードオフ・技術的負債・リスクを隠さない）。
- **R-03 代替案≥1+却下理由**: 代替案を最低1件（推奨2-3件、該当するなら "do nothing" を含む）記録し、
  各案に却下理由を付す。理由なしの列挙はしない。
- **R-04 Status 制御語彙**: 状態は Proposed / Accepted / Rejected / Superseded / Deprecated の
  閉じた5値で表す。自由記述の状態語を作らない。
- **R-05 supersedes / superseded_by 双方向リンク**: 置き換えた旧 ADR は削除せず Superseded に更新し、
  新旧を双方向リンクする（決定の系譜を消さない）。
- **R-06 ID 安定性**: 決定 ID は連番・昇順で払い出す。改番・退役 ID の再利用をしない。
  修正は同一 ID の内容改訂で行い、新決定には次の番号を振る。
- **R-07 決定者/影響者の記録**: deciders/authors と stakeholders を記録する。無記名の決定を残さない。
- **R-08 決定間リンク**: 関連決定を明示参照（ID 参照・relation）で結ぶ。決定を孤立させない。
- **R-09 機械可読の構造化**: frontmatter（title/status/date/authors/tags/supersedes）または
  スキーマ化された定型項目で持つ。散文のみで書かない。
- **R-10 検収ゲート**: 確定（finalize）前に必須項目の充足をチェックリストで機械的に走査する。
  書きっぱなしで確定しない（本 skill では validation 節がそのチェックリスト）。

### 案件に合わせて使う追加観点

- **A-01 項目コード体系**: 方言Aのコード体系を使う場合、複数項目の節は POS-nnn / NEG-nnn / ALT-nnn / IMP-nnn / REF-nnn の
  コード付き箇条書きにする。
- **A-02 ファイル命名規約**: 方言Aの配置を使う場合、`adr-NNNN-[title-slug].md`（NNNN=4桁連番、slug は小文字ハイフン区切り3-5語）を
  `/docs/adr/` に保存する。
- **A-03 入力欠落時は生成せず質問**: 必須入力（Context/Decision/Alternatives/Stakeholders）が
  確定できないときは、捏造で埋めずユーザに不足分を要求する。
- **A-04 Binds/Prevents/Rule 3欄**: 方言Bを使う場合、各決定ブロックに Binds（何を拘束）/ Prevents（どの発散を防ぐ）/
  Rule（下流が従う規則）を書く。決定を「何を防ぐか」で書く。
- **A-05 固定判定テスト**: 方言Bへ記録する決定を選ぶ場合、「1段下の2ユニットが独立に作ったら非互換な選択を
  し得るか？」で判定する。Yes かつ非自明かつ実トレードオフのときだけ固定し、それ以外は Deferred に送る。
- **A-06 conflict 表面化**: 親から継承した決定と矛盾する新決定は、ローカル上書きせず「衝突」として
  表面化する。継承分は元 ID のまま read-only で列挙し、再導出も改番もしない（→ validation 節 DEV-04・Critical Fail）。
- **A-07 Deferred の明示**: 意図的な先送りは理由付きで Deferred 節に書く。無言の未決定を残さない。
- **A-08 即時記録・定期見直し**: 決定したときは文脈が新鮮なうちに記録し、古い決定を保守するときは有効性を見直す。
- **A-09 Impact/Domain 分類**: 分類別に参照する運用を採る場合、決定に Impact（High/Medium/Low）と Domain（Architecture/Product/Business/
  Design/Operations）を付与し、横断ビューで参照可能にする。

rationale（選定理由）の置き場は方言選択（本文に含める / 別ログに分離）であり、validation の採点に関与しない。
案件の指定で選択する。これらの追加観点を使うこと自体で、新しい正式な採点条件を作らない。

## テンプレ/様式

テンプレは規約から導出される具象。**テンプレと規約が矛盾したら規約が勝つ**
（例: Negative 小節を削る改変は R-02 違反なので不可）。

### 方言A: 単票テンプレ

````md
---
title: "ADR-NNNN: [Decision Title]"
status: "Proposed"
date: "YYYY-MM-DD"
authors: ["[決定者の氏名または役割]"]
stakeholders: ["[影響を受ける関係者の氏名または役割]"]
tags: ["architecture", "decision"]
supersedes: ""
superseded_by: ""
---

# ADR-NNNN: [Decision Title]

## Status

**Proposed** | Accepted | Rejected | Superseded | Deprecated

## Context

[Problem statement, technical constraints, business requirements, and environmental factors requiring this decision.]

## Decision

[Chosen solution with clear rationale for selection.]

## Consequences

### Positive

- **POS-001**: [Beneficial outcomes and advantages]
- **POS-002**: [Performance, maintainability, scalability improvements]

### Negative

- **NEG-001**: [Trade-offs, limitations, drawbacks]
- **NEG-002**: [Technical debt or complexity introduced]

## Alternatives Considered

### [Alternative 1 Name]

- **ALT-001**: **Description**: [Brief technical description]
- **ALT-002**: **Rejection Reason**: [Why this option was not selected]

## Implementation Notes

- **IMP-001**: [Key implementation considerations]
- **IMP-002**: [Migration or rollout strategy if applicable]

## References

- **REF-001**: [Related ADRs]
- **REF-002**: [External documentation]
````

付随規約: 保存先 `/docs/adr/`・命名 `adr-NNNN-[title-slug].md`（A-02）。

### 方言B: AD-n ブロック様式（spine 内決定ブロック）

提出単位は **spineの決定ブロックと、その決定を指す付随記録の組**。ブロックは下流が従う決定に絞り、
背景・選定理由・代替案・帰結は付随記録へ置く。付随記録は既存memlog内の構造化エントリでも別ファイルでも
よいが、決定IDと解決できる参照で相互に辿れるようにする。短い3欄のブロックだけを完成したADRと扱わない。

以下のパス・欄名は記入補助であり、同じ情報と参照可能性を保って案件に合わせられる。例の `AD-1` を
そのまま採番せず、既存の決定IDと履歴を確認する。spineでは決定1件につき1ブロックを昇順に並べる。

```md
### AD-1 — [決定の短い名称]

- **Binds:** [拘束する能力・ユニット・要求・領域]
- **Prevents:** [独立実装で起こり得る不整合]
- **Rule:** [下流が従う決定の具体的な内容]
- **Record:** [AD-1の付随記録](decisions/AD-1.md)
```

付随記録 `decisions/AD-1.md` を次のように記す。既存memlogを使う場合も同じ情報を決定ID単位で保持する。

````md
---
decision_id: "AD-1"
title: "[決定の短い名称]"
status: "Proposed"
date: "YYYY-MM-DD"
authors: ["[決定者の氏名または役割]"]
stakeholders: ["[影響を受ける関係者の氏名または役割]"]
decision_ref: "../ARCHITECTURE-SPINE.md#決定ブロックの実在アンカー"
supersedes: null
superseded_by: null
related_decisions: []
---

# AD-1 の付随記録

## Context
[決定が必要になった背景、前提、制約]

## Decision
[spineの該当ブロック](../ARCHITECTURE-SPINE.md#決定ブロックの実在アンカー) のRuleを決定本文とする。

## Rationale
[その決定を選ぶ理由。spineのRuleには埋め込まない]

## Alternatives Considered
- [代替案の具体的内容] — [この案を採らない理由]

## Consequences
### Positive
- [この決定に固有の利点]
### Negative
- [この決定に固有の不利益・負債・リスク]

## References
[関連決定・親決定への参照。存在しない場合はその事実]

## Deferred
[意図的に先送りする事項と理由。無い場合はその事実]
````

付随記録の `decision_id` は同じ決定への参照キーであり、新しい決定の再採番ではない。
両方の参照を実際に開き、同じ決定を指すことと、Ruleの内容が確認できることを確かめる。
「ログを参照」だけの記述、読めないリンク、別IDを指すリンクは未解決として残す。

`Proposed` はテンプレの初期値である。記入が終わっただけで `Accepted` へ進めず、案件で実際に決まった
状態を記す。確定済みの決定へ付す `[ADOPTED]` タグやspine全体のdraft/finalを、決定の5値statusに代用しない。
決定者と影響者が同じ場合も、それぞれの役割を明示する。

置換・関連決定の有無を確認し、存在するときは空値を残さず実在IDと参照先を記す。置換時は旧記録を保持し、
旧側の `Superseded` と双方向参照も整える。親spineから継承する決定は「Inherited Invariants」表へ元ID・
元参照のまま読み取り専用で列挙し、矛盾を新しいRuleで隠さず表面化する。

| 共通ルール | 方言Bで確認する場所 |
|---|---|
| R-01の4スロット | 付随記録のContext・Decision参照・Alternatives Considered・Consequences。参照先のRuleも読む |
| R-02の正負両記 | 付随記録のPositiveとNegative |
| R-03の代替案と却下理由 | 付随記録のAlternatives Considered |
| R-04の状態 | 付随記録のstatus |
| R-05の置換履歴 | 新旧付随記録のsupersedes／superseded_byと旧status。置換がある場合に確認 |
| R-06のID | spineの決定ID列・履歴と、同じIDに対応する付随記録 |
| R-07の決定者・影響者 | 付随記録のauthorsとstakeholders |
| R-08の関連決定 | related_decisions・References・Inherited Invariants。関連決定がある場合に確認 |
| R-09の構造化 | 付随記録のfrontmatterまたは同等の構造化エントリ |
| R-10の確定前確認 | 組全体を対象に末尾のチェックリストを適用し、未充填・未解決参照・継承矛盾も確認 |

ブロックだけ、または付随記録だけで自己チェックを済ませない。欠けた情報を方言差として免除せず、
不足を報告する。確認する側で付随記録を補完し、元の提出物が充足していたことにしない。

### 使い分け

- 決定を**独立文書として配布・参照**したい（レビュー単位=決定1件）→ 方言A
- 決定を**下流ビルダーの一貫性契約**として束ねたい（レビュー単位=spine 全体、決定論 lint をかけたい）→ 方言B
- どちらでも R-01〜R-10 が上位規約。

## validation — ADR記録の自己チェック

下記の全INV/DEVを記録の自己チェックに使い、確認できた箇所と不足を返す。方言Bではブロックと付随記録の
組を対象にする。自己チェックの一致を正式なPASSや決定の承認へ読み替えない。

正式判定が必要な場合は、Contract本体と独立した判定ハーネスを別途利用できるか確認する。利用できなければ
正式判定は未実施として不足を返す。このpackの助言だけで合否・工程遷移を確定しない。
以下の採点説明はContractに既存の条件を示すものであり、自己チェック時に採点を代行する指示ではない。

Contractでは各 INV は0/5/10採点、適用対象INVの平均70%（7.0/10）以上でPASS。
INV-05 / INV-08は適用条件不成立なら採点母数から除外する。
DEV-01〜04は該当条件を満たすものが1件でもあればCritical Failとなる。

確定前チェックリスト（required_invariants）:

- [ ] **INV-01** Context / Decision / Alternatives Considered / Consequences の4スロットが全て実質的記載を持つ
  （見出しのみ・1行未満の形骸は減点、欠落は 0）。
- [ ] **INV-02** 帰結が正負両記で、負側が決定固有の内容（一般論のみは減点）。
- [ ] **INV-03** 代替案1件以上（推奨2-3件、該当なら現状維持案を含む）全てに却下理由。
- [ ] **INV-04** status が制御語彙5値（Proposed/Accepted/Rejected/Superseded/Deprecated）のいずれか。
- [ ] **INV-05** 置換が観測できる場合: 旧決定は Superseded 更新＋supersedes/superseded_by 双方向リンク
  （置換なしの成果物は非適用）。
- [ ] **INV-06** 決定 ID が連番・昇順・重複なし・改番/再利用なし。採番自体が無い場合: 単票 ADR は中間帯（5）、
  複数決定のブロック集合は 0。
- [ ] **INV-07** 決定者と影響関係者の両方を記録（片方のみは減点、無記名は 0）。
- [ ] **INV-08** 関連決定が存在する場合: ID/relation で明示参照（存在しない場合は非適用）。
- [ ] **INV-09** frontmatter またはスキーマ化された定型項目で機械パース可（散文のみは 0）。
- [ ] **INV-10** 確定 status の ADR に placeholder（TBD/TODO/FIXME/XXX）・未充填トークン・未解決相互参照が
  残存しない（理由付きで Deferred へ明示退避されていれば中間帯）。

Critical Fail（unacceptable_deviations — 1件で即不合格）:

- **DEV-01** 帰結が正のみ（「特になし」「リスクは想定されない」等の無内容な充足を含む）。
- **DEV-02** 代替案ゼロ、または全代替案が却下理由を欠く（「他の案も検討したが本案が最良」の一文のみ等）。
- **DEV-03** 決定 ID の重複・非単調（改番）・退役 ID の再利用。
- **DEV-04** 継承決定との矛盾の非表面化（ローカル上書き・再導出・改番による隠蔽）。
  昇格条件: 成果物が親/継承決定への明示参照を持つ場合のみ適用。継承構造を持たない単票 ADR には非適用。

運用注記: placeholder 残存・ID 重複/非単調・status 語彙・4スロット見出しの有無は決定論検査で先に落とせる
（lint 先行→judge は意味半分の二段構え。詳細は CT-ADR-001「決定論検査」節）。

## examples/

- [examples/adr-0001-judge-model-pinning.md](examples/adr-0001-judge-model-pinning.md) —
  記録の組み立て方を読むための過去の代表例。判定の履歴はPROVENANCE.mdに記録する。
  方言A + A-01/A-02 適用の実例で、次の型を示す:
  - 「最初の ADR」での連番起点の払い出しと、関連決定・置換が存在しないことの明示
  - 実測・構造的理由に接地した代替案3件（do nothing 案を含む）の却下理由
  - 「リスクなし」型の見かけ充足でない、決定に固有の負の帰結（NEG-001〜003）
  - 将来の置換手順の自己記述（IMP-003: Superseded 更新＋双方向リンク＋再校正）

---

provenance: KA-ADR-001@0.1.0 / KA-ADR-002@0.2.0 / KA-ART-001@0.1.0 / CT-ADR-001@0.2.0 ｜
元 OSS ライセンス: MIT（github/awesome-copilot・BMAD-METHOD・openai/skills notion-knowledge-capture）｜
compiled_at: 2026-09-14
