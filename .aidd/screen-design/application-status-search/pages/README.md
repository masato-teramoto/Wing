# mockup — application-status-search（物件契約情報申請状況検索/一覧）

> **これは画面設計書とスタイルガイドから生成した画面の具体形です**
> 構成・項目・状態・文言と、案件の見た目を確認するためのものです。
> 挙動は再現していません（JS なし・画面遷移はリンクのみ・表示データはすべて固定値のダミーです）。
> 正は**画面設計書**（構成・項目・操作・状態・文言）と**スタイルガイド**（見た目）であり、
> この HTML を実装のソースには使いません。
> 直したいところは、この HTML ではなく**入力（画面設計書・画面マップ・スタイルガイド）を直して再生成**します。

## 生成条件

| 入力 | 版・時点 |
|---|---|
| 画面設計書 `.aidd/screen-design/application-status-search/screen-spec.md` | status confirmed / 確定 2026-10-09T22:14+09:00 |
| 画面マップ `.aidd/screen-design/_app-shell/screen-map.md` | revision 1 |
| STYLEGUIDE.md / styleguide.css | version 0.3.10 |

生成の手段: `.aidd/screen-design/_tools/mockup/gen-application-status-search.mjs`（シェルは同じ場所の `shell.mjs`）。

## ページ（画面 × 状態 = 11）

| 状態 | ページ |
|---|---|
| 初期表示 | [s-01-initial.html](s-01-initial.html) |
| 通常 | [s-01-default.html](s-01-default.html) |
| 検索結果 0 件 | [s-01-zero.html](s-01-zero.html) |
| ローディング | [s-01-loading.html](s-01-loading.html) |
| 入力エラー | [s-01-input-error.html](s-01-input-error.html) |
| 上限件数超過 | [s-01-over-limit.html](s-01-over-limit.html) |
| 警告件数超過の確認 | [s-01-warning-confirm.html](s-01-warning-confirm.html) |
| 取込中の申請No を押した | [s-01-importing.html](s-01-importing.html) |
| 社外ユーザー | [s-01-external.html](s-01-external.html) |
| 長文 | [s-01-long-text.html](s-01-long-text.html) |
| 月次カレンダー | [s-01-calendar.html](s-01-calendar.html) |

## 見るときの観点

### A. 毎回同じ 3 観点

1. **読み込み切れ** — `tokens/styleguide.css` が当たっているか（素の HTML に見えるページが無いか）
2. **崩れ** — 部品の重なり・はみ出し・折り返し・間隔の詰まり
3. **シェルとナビの一致** — 全ページに同じシェルが載り、ナビ項目と現在地が画面マップ §4-1 / §4-2 と合っているか

代表ページ（A の 3 観点に共通）: [s-01-default.html](s-01-default.html)

### B. この回の観点（`missing[]` / `notes[]` から）

| # | 観点 | 代表ページ |
|---|---|---|
| 1 | **発送書類名・案件小ｸﾞﾙｰﾌﾟが候補なしの入力欄だけで描かれている**（データリストの器が無い — SGB-16）。見て許容できるか | [s-01-initial.html](s-01-initial.html) |
| 2 | **長い値が表示バイト数で切れたまま、全文を見る手段が無い**（ツールチップの器が無い — SGB-17）。切れ方が読めるか | [s-01-long-text.html](s-01-long-text.html) |
| 3 | **月次カレンダーに月送り・曜日見出し・閉じるが無い**（文言が STYLEGUIDE.md に無い — SGB-18 / SGB-19）。曜日が無くても日付が読めるか | [s-01-calendar.html](s-01-calendar.html) |
| 4 | **申請No がリンクの見た目だが押しても移らない**（行き先が画面マップに無い・pending）。取込中の行（申請No が文字だけ）と区別できるか | [s-01-default.html](s-01-default.html) / [s-01-importing.html](s-01-importing.html) |
| 5 | **ヘッダの「MENU」が未生成の入口を指し（pending）、「LOGOUT」が無効表示** | [s-01-initial.html](s-01-initial.html) |
| 6 | **一覧が 14 列で本文幅に入らず、表の中だけが横に流れる**（ページは横に動かない）。申請No を見ながら右端の列まで追えるか | [s-01-default.html](s-01-default.html) |
| 7 | **条件表 A の 3 組目の列・空けたセル**（7 行目の右端、社外ユーザーでは 6 行目の両端）が格子として読めるか。社外ユーザーの起案会社・所属①② の灰色の欄 | [s-01-external.html](s-01-external.html) |
| 8 | **条件表 B の日時の範囲（日付 + 時刻 〜 日付 + 時刻）が 1 つの値セルに収まっているか** | [s-01-input-error.html](s-01-input-error.html) |
| 9 | **起草した文言**（`DS-100024` / `DS-100025`。画面設計書に実文言が無い）の言い回し | [s-01-over-limit.html](s-01-over-limit.html) / [s-01-warning-confirm.html](s-01-warning-confirm.html) |

> 観点は「見る場所を示すもの」であって「漏れを防ぐもの」ではありません。生成側が気づいていない欠陥は上に載りません（機械検査 2 本も描画を見ません）。
