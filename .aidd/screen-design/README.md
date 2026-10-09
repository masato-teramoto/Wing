# 画面設計工程（簡素版）— 成果物の所在と状態

> 本ファイルは `aidd-system-design` が書く。停止のたびに更新する。
> 進行状態の正は各成果物の担体であり、本ファイルはその写しである（食い違ったら担体が正）。

最終更新: 2026-10-09（_app-shell の mockup 目視 済 — 今回の対象〔application-status-search・_app-shell〕は完了確認まで済）

## 1. 成果物の所在

```
<案件ルート>/
├── STYLEGUIDE.md / styleguide.css / STYLEGUIDE-backlog.md   … 見た目の正（SG。案件に 1 枚）
└── .aidd/screen-design/
    ├── README.md                                            … 本ファイル
    ├── _app-shell/screen-map.md                             … 画面マップ（SD-0。案件に 1 つ）— revision 1・確定済み
    ├── _app-shell/screen-spec.md                            … 入口（メニュー）とシステムエラーの画面設計書 — confirmed（2 画面 × 各 1 状態）
    ├── _app-shell/pages/                                    … 入口の mockup（MU）— 2 ページ。案件の入口は pages/s-01-default.html
    ├── application-status-search/screen-spec.md             … 画面設計書（SD-1）— confirmed
    ├── application-status-search/pages/                     … mockup（MU）— 11 ページ。入口は pages/README.md
    ├── <feature>/screen-spec.md                             … 画面設計書（SD-1。feature ごと）
    ├── <feature>/pages/                                     … mockup（MU。feature ごと）— 未作成
    └── _tools/mockup/                                       … 生成の手段（shell.mjs = 共通シェル / gen-<feature>.mjs）
```

UI を持つと宣言された feature: `application-status-search`（mockup も作る。2026-10-09 開発者の宣言）。
今回の対象はこの 1 feature に絞った（残る design 承認済み 6 feature は未判定 — 画面マップ §1・§6-2 #1）。入口を新設したため擬似 feature `_app-shell` も対象。

## 2. 状態

| 成果物 | 担体 | 値 |
|---|---|---|
| `STYLEGUIDE.md` | §1-2 最新行の `確定` | **済**（版 0.3.10・2026-10-09・ルート C — プリセット wing 0.3.10 から複製・by: toshiya-fukunaga / recorded_by: aidd-system-design） |
| 画面マップ | `features[]` 行ごとの `confirmed` | revision 1 — application-status-search: **済** / _app-shell: **済**（by: toshiya-fukunaga / at: 2026-10-09T21:52+09:00 / recorded_by: aidd-system-design） |
| 画面設計書 | frontmatter `status` | application-status-search: **confirmed**（by: toshiya-fukunaga / at: 2026-10-09T22:14+09:00 / recorded_by: aidd-system-design。所有 1 画面 × 11 状態）/ _app-shell: **confirmed**（by: toshiya-fukunaga / at: 2026-10-09T22:38+09:00 / recorded_by: aidd-system-design。所有 2 画面 × 各 1 状態。§5-5 改訂依頼 0 件・§5-4 確認事項 3 件〔宛先 steering〕） |
| mockup | `status` / `checks` / `viewed` | application-status-search: **11 ページ・パレット pass・動線 pass（pending 0 — _app-shell 生成で解消。HTML は不変）・目視 済（by: toshiya-fukunaga / recorded_by: aidd-system-design。範囲の申告なし）** / _app-shell: **2 ページ・パレット pass・動線 pass（broken 0 / pending 0・入口から 2 feature 到達）・目視 済（by: toshiya-fukunaga / at: 2026-10-09T22:47+09:00 / recorded_by: aidd-system-design。範囲の申告なし）** |

`STYLEGUIDE-backlog.md` の未処理: 6 件 — 1-1 直す・未反映 SGB-17（【人】判断済み）/ 1-3 未判断 SGB-11・12（プリセット由来）・SGB-16・18・19（application-status-search 由来）。

## 3. `tasks.md` からの参照の仕方

- UI タスクの参照先は**画面設計書と mockup** — `.aidd/screen-design/<feature>/screen-spec.md` の画面 ID と、
  `.aidd/screen-design/<feature>/pages/<画面 ID>-<状態>.html`
- `STYLEGUIDE.md` / `styleguide.css`（案件ルート直下）は実装時の見た目の正

## 4. 再生成の契機

- `STYLEGUIDE.md` の版が上がった（`manifest.inputs.styleguide_version` ≠ `STYLEGUIDE.md` の `version`）→ 全 feature の mockup を再生成
- 画面マップ §4（入口とシェル）が変わった → 全 feature の mockup を再生成
- 無効表示のリンク先（`cross_feature_links[].status = pending` の相手 feature）に `pages/` が出来た → その項目を持つ全 feature の mockup を再生成
- 画面設計書の改訂・機械検査 fail の修正 → その feature の mockup を再生成
