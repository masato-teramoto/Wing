# 出力レイアウトとパス規約

> 本ファイルは AIDD フロー実行時の **成果物パスの正** である。全 Skill・全サブエージェントはパスをここから引き、推測でパスを組み立てない。

---

## 1. 実行前提

`.claude/`（Skills・サブエージェント）と `Templates/` を **対象プロジェクトのルートへ配置**し、**対象プロジェクトのルートを出力ルート**として実行する。本ファイルのパスはすべて出力ルート相対である。

- `Templates/` は **実行時に構造・形式の正として読む**。テンプレート項目を Skill 側に書き写さない。
- 配置先を `.claude/` とするのは、**Cursor と Claude Code の両方が読む唯一のディレクトリ**だからである（Cursor は `.claude/skills/` と `.claude/agents/` を互換読み込みし、Claude Code は `.cursor/` を読まない）。`.cursor/` へ複製しない。Cursor は名前衝突時に `.cursor/` を優先するため、複製は二重管理と不整合の原因になる。

---

## 2. ディレクトリ構成

```
<出力ルート>/
├── .aidd/                       # フロー管理ファイル（仕様ではない）
│   ├── rfp/                     # RFP の置き場（自由形式・テンプレートを持たない）
│   ├── requirement-list.md      # Phase 1 の成果物（要求一覧）
│   ├── feature-list.md          # Phase 3 の成果物（優先度・依存の SSoT）
│   ├── phase-progress.json      # フェーズ進捗（status の集約スナップショット）
│   └── gates/                   # ゲート記録（フェーズごとに 1 ファイル・追記のみ）
│       ├── phase-1-intake.md
│       ├── phase-2-steering.md
│       ├── phase-3-feature.md
│       ├── phase-4-requirements.md
│       ├── phase-5-design.md
│       ├── phase-6-docs.md
│       └── phase-7-tasks.md
├── steering/                    # Phase 2 の成果物（7ファイル）
│   ├── product.md
│   ├── tech.md
│   ├── architecture.md
│   ├── security.md
│   ├── non-functional.md
│   ├── database.md
│   └── api-standards.md
├── specs/                       # Phase 4 / 5 / 7 の成果物
│   └── <feature-name>/
│       ├── requirements.md
│       ├── design.md
│       └── tasks.md
├── docs/                        # Phase 6 の成果物
│   ├── code-design.md
│   └── architecture/
│       ├── data-model.md
│       └── system-overview.md
└── Templates/                   # 構造・形式の正（読み取り専用）
```

---

## 3. 成果物 ↔ テンプレート対応表

| Phase | 成果物 | テンプレート |
|---|---|---|
| 1 | `.aidd/requirement-list.md` | `Templates/Flow/requirement-list.md` |
| 2 | `steering/<7ファイル>` | `Templates/steering/<同名ファイル>` |
| 3 | `.aidd/feature-list.md` | `Templates/Flow/feature-list.md` |
| 4 | `specs/<feature-name>/requirements.md` | `Templates/specs/_template/requirements.md` |
| 5 | `specs/<feature-name>/design.md` | `Templates/specs/_template/design.md` |
| 6 | `docs/code-design.md` | `Templates/docs/code-design.md` |
| 6 | `docs/architecture/data-model.md` | `Templates/docs/architecture/data-model.md` |
| 6 | `docs/architecture/system-overview.md` | `Templates/docs/architecture/system-overview.md` |
| 7 | `specs/<feature-name>/tasks.md` | `Templates/specs/_template/tasks.md` |
| 全 | `.aidd/gates/phase-<N>-<名>.md` | `Templates/Flow/gate-record.md` |
| 全 | `.aidd/phase-progress.json` | `Templates/Flow/phase-progress.json` |

- `Templates/specs/_template/` は **雛形の置き場**であり、`specs/_template/` を出力ルートに作らない。
- テンプレートに存在しないファイルを成果物として増やさない。増やす判断は人間に確認する。

---

## 4. RFP の扱い

- RFP は **フロー外で作成済み**であることが前提であり、本フローは RFP を作成しない。
- 置き場は `.aidd/rfp/` を既定とするが、人間がパスを指定した場合はそれに従う。
- **自由形式**であり入力側テンプレートを持たない。したがって RFP に ① 機械チェックは適用できない。

---

## 5. 命名規約

| 対象 | 規約 |
|---|---|
| feature 名 | 小文字英数とハイフンのみ。`specs/<feature-name>/` のディレクトリ名と `.aidd/feature-list.md` の `feature 名` 列を **完全一致**させる |
| 要求ID | `REQ-` + 3桁以上の数字（`REQ-001`）。採番は追記のみ・欠番の再利用禁止 |
| 要件ID | **数値のみ**（`1`, `1.1`）。要求IDとは名前空間を分ける |
| ゲート記録 | `phase-<N>-<フェーズ略称>.md`。§2 の 7 ファイル名から増減させない |

---

## 6. 参照してよい成果物

**`status: approved` でないドキュメントを下流フェーズの入力にしない。** 各フェーズの Input は次のとおり。

| Phase | 読む成果物 |
|---|---|
| 1 | RFP |
| 2 | `.aidd/requirement-list.md`、`Templates/steering/` |
| 3 | `.aidd/requirement-list.md`、`steering/` 一式 |
| 4 | `.aidd/requirement-list.md`、`steering/` 一式、`.aidd/feature-list.md` |
| 5 | 対象 feature の `requirements.md`、`steering/` 一式、`.aidd/feature-list.md`、依存 feature の `design.md` |
| 6 | `specs/*/requirements.md`、`specs/*/design.md`、`steering/` 一式 |
| 7 | 対象 feature の `requirements.md` / `design.md`、`steering/` 一式、`.aidd/feature-list.md` |

- `steering/` は **全フェーズで一式（全文）**を参照する。該当章だけを選んで読むことはしない。
- **`docs/` は Phase 7 の入力にしない**（docs は design の派生物であり、feature 単位の設計の正は `design.md`）。
- **ゲート記録と `phase-progress.json` は、どのフェーズの生成入力にもしない**。
