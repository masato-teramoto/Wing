---
name: design-authoring
description: AIDD Phase 5（design 作成）の作成 Skill。feature-list.md の優先度順に 1 feature ずつ specs/<feature>/design.md を作成し、参照範囲を制御する（依存先は feature-list から引き、設計の根拠にできるのは公開された契約のみ）。新規の業務コード・区分値・エンティティを design 内に定義し、要件トレーサビリティの自己診断と未記入箇所の質問化を行う。
disable-model-invocation: true
---

# design-authoring（Phase 5: design 作成）

承認済み `requirements.md` に対して「**どう作るか**」を確定する。あわせて feature 間で **契約**（API / イベント / データ所有）が衝突しないことを担保する。

- 成果物: `specs/<feature-name>/design.md`
- テンプレート: `Templates/specs/_template/design.md`

---

## 入力

| 項目 | 内容 |
|---|---|
| 対象 feature の requirements | `specs/<feature-name>/requirements.md`（**`approved`**） |
| steering | `steering/` 一式（全文） |
| feature-list | `.aidd/feature-list.md`（**`approved`**。生成順と依存先の参照元） |
| 依存 feature の design | `specs/<依存先>/design.md`（下記 §参照範囲ルール） |

---

## 参照範囲ルール

**依存 feature の全 requirements を積み上げてはならない。** 依存先について必要な情報は、当該 feature の `design.md` 側にある。

| # | 参照するもの | 範囲 |
|---|---|---|
| 1 | 対象 feature の `requirements.md` | **全文（必須）** |
| 2 | `.aidd/feature-list.md` | 対象 feature の行（**依存先の特定に使う**）。生成順の決定時のみ `優先度` 列を全行参照 |
| 3 | 依存 feature の `design.md` | **全文**（直接依存を起点に、必要なら間接依存も辿る） |
| 4 | `steering/` | 一式（全文） |

### 読む範囲と、根拠にしてよい範囲は別である

- 依存先 `design.md` は **全文を読んでよい。**
- ただし **設計の前提にできるのは公開された契約のみ**である。

| 依存先の記述 | 根拠にしてよいか |
|---|---|
| API Contract / Event Contract / Data Contracts / Service Interface / Batch Contract | **よい**（公開された契約） |
| Design Decisions / Architecture / File Structure Plan / Implementation Notes | **禁止**（内部設計） |
| 内部メソッド、実装の応答速度、所有データへの直接アクセス | **禁止** |

- 契約が不足している場合は **推測で埋めず**、依存先の design を `review` へ戻して契約を追記させる。自 feature は `draft` 維持である。この判断は ③ 人間レビューに提示する。
- **依存先の `design.md` を参照できるのは、優先度順に生成することで依存先が先に確定しているためである。** 順序を崩すと、この参照そのものが成立しない。

---

## 手順

### 1. 優先度順に対象 feature を選ぶ

**本フェーズでは優先度順であること自体が要件である。** 優先度は依存の必須先行を満たす順序として決まっているため、優先度順に生成すれば依存先の `design.md` が必ず先に存在する。

### 2. テンプレートを埋める形で作成する

- **新しい業務コード・区分値・エンティティが発生した場合、当該 `design.md` 内に定義する**（`steering/` の設計ルールに従う）。
- **既に他 feature が定義済みのものは再定義せず参照する。**
- **`docs/` には書かない。** 集約は Phase 6 が行う。`docs/` を本フェーズで作成・更新してはならない。

### 3. 壁打ちで未記入箇所を埋める

下記 §未記入箇所の質問化 に従う。

### 4. 要件トレーサビリティの自己診断を行う

1. 対象 feature の `requirements.md` から **すべての要件ID を抽出**する。
2. 作成した `design.md` をスキャンし、各要件ID が設計のどこで満たされるかを確認する。
3. **設計で見つからない要件ID を人間へフィードバックする。**

> 自己診断は作成側の工程であり、**品質ゲートの代わりにならない**。ゲートは別コンテキストで同じ突合をやり直す。

### 5. feature スコープの品質ゲートを通す

`design-check-subagent` を **別コンテキストで**、スコープ `成果物単位（<feature 名>）` を指定して起動する（起動時の制約は `.claude/skills/aidd-flow/SKILL.md` §5 Step 3）。**指摘の要約は呼び出し元へ返す。③ の提示と人間の判断の反映は呼び出し元が行うため、本 Skill が人間へ承認を求めない。**

### 6. 繰り返す

1〜5 を feature の数だけ繰り返す。**当該 feature の `design.md` が `approved` になるまで次の feature の生成に進まない。**

依存先の `design.md` を設計の根拠にできるのは、**それが `approved` である**ことが前提である（参照範囲ルール）。`draft` の契約を根拠に後続を設計すると、依存先が ③ で修正された時点で、その契約を参照した全 feature を巻き込んで作り直しになる。生成を分割しながらゲートを一括にすると、この巻き込みが最後まで判明しない。

### 7. 全 feature が `approved` になってから横断スコープの品質ゲートを通す

`design-check-subagent` を **別コンテキストで**、スコープ `横断` を指定して起動する。契約衝突と業務コード・エンティティの重複定義を検査する。**横断スコープは承認対象の文書を持たないため `status` を遷移させない。** 指摘の要約を呼び出し元へ返し、`approved` の引き下げが必要かは ③ が判断する。

---

## 未記入箇所の質問化

1. テンプレートから **`<UPPER_SNAKE>` 系統**のプレースホルダー（記法と扱いは `.claude/skills/aidd-flow/references/status-protocol.md` §7 を正とする）を抽出し、**セクション単位**で人間に提示する。`{{...}}` 系統は機械的に埋めるため質問化しない。
2. 提示は「この設計判断の根拠が requirements / steering / 依存先の契約に無い」という形にする。**推測した候補を選択肢として並べない。**
3. **依存先の契約が不足していて埋められない箇所は、質問ではなく差戻し候補として提示する**（人間が判断する）。
4. **埋める必要がないプレースホルダーは、人間が明記した不要理由を記載して保持する。削除しない。**
5. テンプレートが「任意」「必要時」「省略可」と明記しているセクションは、不要なら削除してよい（テンプレートの指示に従う）。
6. 未回答が残る場合は `phase-progress.json` の `waiting_for` を `human_answer`、`open_placeholders` を **不要理由が明記されていない未記入数**に更新して停止する。

---

## 業務コード・エンティティの定義（steering のルールに従う）

| 区分 | 所在 |
|---|---|
| 設計**ルール**（コード体系・採番方式・命名規則・型の指針） | `steering/`（Phase 2 が確定。**読むだけ**） |
| **実体**（個々のコード値・区分値・採番対象・テーブル・カラム） | 当該 `design.md`（**本フェーズで設計する**） |
| 全 feature の実体の**集約** | `docs/`（Phase 6 が所有） |

- steering の設計ルールが不足していて実体を設計できない場合、**独自解釈で進めない。** Phase 2 への差戻し候補として人間に提示する（独自解釈は Phase 6 の集約時に衝突する）。

---

## 禁止

- 依存先の **内部設計に依存した設計**をすること。
- 依存先の契約不足を **推測で補完**すること。
- 優先度順を崩して生成すること。
- 他 feature が定義済みの業務コード・エンティティを再定義すること。
- `docs/` を作成・更新すること。
- プレースホルダーを削除すること（テンプレートが任意と明記したセクションを除く）。
- `approved` でない requirements / feature-list を入力にすること。
- 自ら `status: approved` にすること。
