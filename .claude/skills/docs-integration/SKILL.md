---
name: docs-integration
description: AIDD Phase 6（docs 作成）の作成 Skill。specs の design / requirements からエンティティ・業務コード・フロー・コンポーネントを feature 単位で抽出し、feature 横断で突き合わせて競合を一覧化し、code-design → data-model → system-overview の順に docs/ を確定する。競合の正否確認の質問化を含む。
disable-model-invocation: true
---

# docs-integration（Phase 6: docs 作成）

各 feature の spec に散在する情報を統合し、**プロジェクト全体の実態ドキュメント**を確定する。

| 成果物 | 内容 | テンプレート |
|---|---|---|
| `docs/code-design.md` | **業務コード・区分値・採番ルール**（ソースコード設計ではない） | `Templates/docs/code-design.md` |
| `docs/architecture/data-model.md` | ER 図・主要エンティティ一覧 | `Templates/docs/architecture/data-model.md` |
| `docs/architecture/system-overview.md` | システム全体像・主要ビジネスフロー | `Templates/docs/architecture/system-overview.md` |

**`docs/` の所有者は本フェーズのみである。** 上流フェーズは暫定版も作らない。

---

## 入力

| 項目 | 内容 |
|---|---|
| specs | `specs/*/requirements.md` / `specs/*/design.md`（**ともに `approved`**） |
| steering | `steering/` 一式（全文） |

- **`tasks.md` は入力にならない。** 本フェーズの実行時点で `tasks.md` はまだ存在しない。
- したがって「tasks にしか設計情報が書かれていない」ケースは本フェーズでは検出できない。**Phase 7 のゲートが検出して design へ戻す。**

---

## 集約方針

| フェーズ | 業務コード / エンティティの扱い |
|---|---|
| Phase 2 | **設計ルールのみ**を `steering/` に確定（コード体系・採番方式・命名規則・型の指針）。値は書かない |
| Phase 5 の各 design | 必要になった feature の `design.md` 内で、steering のルールに従って**実体を設計する** |
| **Phase 6（本フェーズ）** | 全 design の実体を **集約**し、`docs/` を確定する |

---

## 手順

### 1. 抽出（feature 単位で独立して実行する）

`specs/*/design.md` および `requirements.md` から次を機械的に列挙する。

- エンティティ / 属性 / 関連
- 業務コード・区分値・採番対象
- 主要フロー（ビジネスフロー候補）
- コンポーネントと接続

> **全 feature の spec を一度に読み込まない。** feature ごとに抽出し、結果を積み上げる。実体の抽出元は各 `design.md`、主要ビジネスフローなどの補完は `requirements.md` である。

### 2. 統合（競合を一覧化する）

抽出結果を feature 横断で突き合わせ、**同じコード値 / エンティティが複数の design で別形状に定義されている箇所**を一覧化する。

- 競合は **どちらが正かを人間に確認してから**反映する。**推測で寄せない。**
- **本フェーズで `design.md` を直接修正しない。** 競合が見つかった場合は次の手順を取る。
  1. 正とした形状を人間に確定させる。
  2. **不一致の design を `review` へ戻す**（Phase 5 の人間承認をやり直させる）。
  3. **docs 統合を保留する。**
  4. 競合が解消し、該当 design が再度 `approved` になってから Phase 6 に戻る。
  5. 再開時は **該当 feature の抽出のみやり直す**（全 feature の再抽出は不要）。

### 3. 作成順に最終化する

依存の少ない順で確定する。**順序を入れ替えない。**

| 順 | ファイル | 前提 |
|---|---|---|
| 1 | `docs/code-design.md` | 各 design のコード定義を集約 |
| 2 | `docs/architecture/data-model.md` | code-design を前提に確定 |
| 3 | `docs/architecture/system-overview.md` | 上記 2 つを前提に確定 |

### 4. 品質ゲートを通す

`docs-check-subagent` を **別コンテキストで**起動する（起動時の制約は `.claude/skills/aidd-flow/SKILL.md` §5 Step 3）。**指摘の要約は呼び出し元へ返す。③ の提示と人間の判断の反映は呼び出し元が行うため、本 Skill が人間へ承認を求めない。**

---

## steering との書き分け

| 内容 | 所在 |
|---|---|
| **方針・ルール**（コード体系の作り方、命名規則、型の指針、採番方式の選び方） | `steering/` |
| **実態**（個々のコード値・区分値・採番対象、テーブル・カラム・ER、実際のフロー） | `docs/` |

- **同じ事実を steering と docs の両方に書かない。** docs から steering のルールを引用する場合は「準拠」として参照に留める。
- **設計ルール自体が欠落していた**（各 design が独自解釈していた）と判明した場合は、**Phase 2 への差戻し候補**として人間に提示する。影響 design の洗い出しが必要である旨も伝える。

---

## 競合の正否確認の質問化

1. 競合を **要素単位**（エンティティ名・業務コード名）で一覧化する。
2. 各競合について、**どの design がどの形状で定義しているか**を並べて提示する。
3. 提示は「どちらが正か」を問う形にする。**推測でどちらかに寄せた案を既定として示さない。**
4. 回答を得るまで **当該要素を docs に書かない。** 両形状の並記や未解決の `TBD` を docs に残してはならない（ゲートで指摘される）。
5. **埋める必要がないプレースホルダーは、人間が明記した不要理由を記載して保持する。削除しない。**
6. 未回答が残る場合は `phase-progress.json` の `waiting_for` を `human_answer` に更新して停止する。

---

## 禁止

- 全 feature の spec を一度に読み込むこと。
- **`design.md` を本フェーズで修正すること。**
- 競合を推測でどちらかに寄せること。
- 両形状の並記・未解決の `TBD` を docs に残すこと。
- 作成順（code-design → data-model → system-overview）を入れ替えること。
- `tasks.md` を入力にすること。
- steering と同じ事実を docs に定義すること。
- `approved` でない requirements / design を入力にすること。
- 自ら `status: approved` にすること。

---

## Phase 7 から差戻された場合

Phase 7 で「tasks にしか存在しない設計判断」が見つかり design が更新された場合、**本フェーズの `docs/` を `review` へ引き下げる**。docs は design の派生物であり、design の変更で無効化される。再開時は **該当 feature の抽出のみやり直す**。
