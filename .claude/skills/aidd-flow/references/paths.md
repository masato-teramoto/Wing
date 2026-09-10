# 出力レイアウトとパス規約

> 本ファイルは AIDD フロー実行時の **成果物パスの正** である。全 Skill・全サブエージェントはパスをここから引き、推測でパスを組み立てない。
> 出典: フロー設計 `00_全体フロー設計書.md` §2・§4（配置の確定内容は §9 の確定した設計判断を参照）。
> **本ファイルはリリース α2（Phase 1〜5）版である。** Phase 6 以降の成果物パスは記載しない。記載の無いパスに書き込んではならない。
> **α2 で design 以降のフェーズ番号が 1 つ繰り下がっている**（Phase 5 = 画面モック生成 / 6 = design / 7 = docs / 8 = tasks。対応表は `SKILL.md` §0）。

---

## 1. 実行前提

`.claude/`（Skills・サブエージェント）と `Templates/` を **対象プロジェクトのルートへ配置**し、**対象プロジェクトのルートを出力ルート**として実行する。本ファイルのパスはすべて出力ルート相対である。

- `Templates/` は **実行時に構造・形式の正として読む**。テンプレート項目を Skill 側に書き写さない。
- `フロー設計/` は設計の正だが **配布物ではない**。実行時に存在することを前提にしてはならない。
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
│   ├── gates/                   # ゲート記録（フェーズごとに 1 ファイル・追記のみ）
│   │   ├── phase-1-intake.md
│   │   ├── phase-2-steering.md
│   │   ├── phase-3-feature.md
│   │   ├── phase-4-requirements.md
│   │   └── phase-5-wireframe.md
│   └── wireframe/               # Phase 5 の成果物（§7。使い捨ての根拠資料であり仕様ではない）
│       ├── <feature-name>/
│       │   ├── wireframe-viewer.html   # 位置づけ注記帯 + iframe（監査対象外）
│       │   └── pages/                  # 監査対象ディレクトリ
│       │       ├── *.html              # 状態別の静的ページ
│       │       ├── wireframe-manifest.json  # Phase 5 の承認対象（status の担体）
│       │       ├── README.md           # 位置づけ注記の定型文 + 生成条件
│       │       ├── shell.css           # 結合段が置く共通シェル（全 feature に同一内容）
│       │       └── tokens/tokens.css   # トークン CSS（監査対象外）
│       └── _app-shell/          # 入口を新設した場合のみ（擬似 feature。要件 ID を持たない）
├── ds/                          # Phase 5 が参照するデザインシステム（§7。取得物・コミットしない）
├── steering/                    # Phase 2 の成果物（7ファイル）
│   ├── product.md
│   ├── tech.md
│   ├── architecture.md
│   ├── security.md
│   ├── non-functional.md
│   ├── database.md
│   └── api-standards.md
├── specs/                       # Phase 4 の成果物
│   └── <feature-name>/
│       └── requirements.md
└── Templates/                   # 構造・形式の正（読み取り専用）
```

`specs/<feature-name>/` に `design.md` / `tasks.md` を作らない。`docs/` も作らない（Phase 6 以降の成果物であり本リリースの対象外）。

**Phase 5 の成果物は `specs/<feature-name>/` に置かない。** `specs/` は仕様の置き場であり、ワイヤーフレームは使い捨ての根拠資料であるため `.aidd/` 側に置く（`specs/<feature-name>/` を `requirements.md` の 1 ファイル構成 = `Templates/` 準拠のまま保つ）。

---

## 3. 成果物 ↔ テンプレート対応表

| Phase | 成果物 | テンプレート |
|---|---|---|
| 1 | `.aidd/requirement-list.md` | `Templates/Flow/requirement-list.md` |
| 2 | `steering/<7ファイル>` | `Templates/steering/<同名ファイル>` |
| 3 | `.aidd/feature-list.md` | `Templates/Flow/feature-list.md` |
| 4 | `specs/<feature-name>/requirements.md` | `Templates/specs/_template/requirements.md` |
| 5 | `.aidd/wireframe/<feature-name>/pages/wireframe-manifest.json` | `Templates/wireframe/wireframe-manifest.json` |
| 全 | `.aidd/gates/phase-<N>-<名>.md` | `Templates/Flow/gate-record.md` |
| 全 | `.aidd/phase-progress.json` | `Templates/Flow/phase-progress.json` |

- `Templates/specs/_template/` は **雛形の置き場**であり、`specs/_template/` を出力ルートに作らない。`Templates/wireframe/` も同じ扱いで、`.aidd/wireframe/` 側に雛形ディレクトリを作らない。
- テンプレートに存在しないファイルを成果物として増やさない。増やす判断は人間に確認する。
- **Phase 5 の HTML（`*.html` / `shell.css` / `tokens.css`）はテンプレートを持たない。** 生成物の形の正は DS（`ds/`）と `wireframe-authoring` の生成規約であり、`Templates/` には書式雛形（manifest）のみを置く。

---

## 4. RFP の扱い

- RFP は **フロー外で作成済み**であることが前提であり、本フローは RFP を作成しない。
- 置き場は `.aidd/rfp/` を既定とするが、人間がパスを指定した場合はそれに従う。
- **自由形式**であり入力側テンプレートを持たない。したがって RFP に ① 機械チェックは適用できない。

---

## 5. 命名規約

| 対象 | 規約 |
|---|---|
| feature 名 | 小文字英数とハイフンのみ。`specs/<feature-name>/`・`.aidd/wireframe/<feature-name>/` のディレクトリ名と `.aidd/feature-list.md` の `feature 名` 列を **完全一致**させる |
| 要求ID | `REQ-` + 3桁以上の数字（`REQ-001`）。採番は追記のみ・欠番の再利用禁止 |
| 要件ID | **数値のみ**（`1`, `1.1`）。要求IDとは名前空間を分ける |
| ゲート記録 | `phase-<N>-<フェーズ略称>.md`。§2 の 5 ファイル名から増減させない |
| 擬似 feature | `_app-shell` のみ（結合段が入口を新設した場合）。**アンダースコア始まりは擬似 feature の印**であり、`.aidd/feature-list.md` に対応する行を持たない |

---

## 6. 参照してよい成果物

**`status: approved` でないドキュメントを下流フェーズの入力にしない。** 各フェーズの Input は次のとおり。

| Phase | 読む成果物 |
|---|---|
| 1 | RFP |
| 2 | `.aidd/requirement-list.md`、`Templates/steering/` |
| 3 | `.aidd/requirement-list.md`、`steering/` 一式 |
| 4 | `.aidd/requirement-list.md`、`steering/` 一式、`.aidd/feature-list.md` |
| 5 | 当該 feature の `specs/<feature-name>/requirements.md`、`steering/` 一式、`.aidd/feature-list.md`、`ds/` 一式、`Templates/wireframe/wireframe-manifest.json` |

- `steering/` は **全フェーズで一式（全文）**を参照する。該当章だけを選んで読むことはしない。
- **ゲート記録と `phase-progress.json` は、どのフェーズの生成入力にもしない**。
- **Phase 5 は `.aidd/requirement-list.md` を読まない。** 画面内容の根拠は当該 feature の `requirements.md` と `steering/` に限る（要求一覧まで根拠を広げると、requirements に落ちていない要求を画面で確定させてしまう）。
- **Phase 5 は結合段のみ全 feature の `requirements.md` を読むが、読んでよいのはタイトルと Introduction までである**（入口ラベルの業務名に使う。中身をもとに画面を足さない）。

---

## 7. Phase 5（画面モック生成）の成果物とデザインシステム

### 成果物（`.aidd/wireframe/`）

- **ワイヤーフレーム（使い捨ての根拠資料 — 仕様ではない）**: `.aidd/wireframe/<feature-name>/pages/`（監査対象。状態別 HTML + `wireframe-manifest.json`）、`.aidd/wireframe/<feature-name>/wireframe-viewer.html`（位置づけ注記ビューア）、入口を新設した場合のみ `.aidd/wireframe/_app-shell/`
- **承認対象（`status` の担体）**: `.aidd/wireframe/<feature-name>/pages/wireframe-manifest.json` の**トップレベル** `status` / `updated_at`（`status-protocol.md` §1・§4）
- **書式雛形**: `Templates/wireframe/wireframe-manifest.json`
- **Phase 6（design 作成）の入力**: `.aidd/wireframe/<feature-name>/pages/wireframe-manifest.json`（+ MK2 の指摘の記録）。**HTML 本体は参照資料であり、design の入力にしない**

### デザインシステム（`ds/`）

- 既定の所在は出力ルート直下の `ds/` である。**版（タグ）を固定して取得し、参照した版を manifest の `ds_version` に記録する**（`SKILL.md` §7 手順 0）。
- **取得物であり成果物ではない。** `.gitignore` に `ds/` を追加してコミットしない。
- **読み取り専用である。** `ds/` 配下のファイル（トークン JSON・監査スクリプト・`AGENTS.md`）を変更してはならない。
- DS 内の参照順序と詳細ルールの正は **`ds/index.json` と `ds/AGENTS.md`** である（DS の版と一緒に配布される）。本ファイルは DS 内部のパスを列挙しない。
