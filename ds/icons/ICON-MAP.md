# アイコン定義（ICON-MAP）— 語彙・サイズ・配置・a11y・禁止事項

> **位置づけ**: 本ファイルは「部品・箇所 → アイコンの役割名 → 実体（Material Symbols 名）」の
> **唯一の対応表**であり、アイコンの使い方（サイズ・配置・色・a11y・禁止）の横断規則。
> 部品仕様（component-spec.json）・パターン（pattern.json）・モック実装がアイコンを使うときは
> まずここを見る。寸法の正は `tokens/tokens.json` の `icon.size`、色の正は `tokens/ROLE-MAP.md`。
> アイコンは **UI 部品ではなく基盤定義**（`components/Icon` は作らない — 部品の内部要素として使う）。
>
> **運用ルール**
> - アイコンが必要になったら、**まず §2 の語彙表に無いか確認**する。表にあればその役割名で使う
> - 表に無い場合は**自分で追加せず、代用（記号文字・絵文字・アイコンフォント・自作 SVG・語彙外の
>   Material Symbols）もせずに人間へ起票**する（AGENTS.md ハード制約）
> - ただし**起票は作業の停止を意味しない**。語彙に無いときは**アイコンを付けずに（可視ラベルのみで）
>   組んで続行**し、§6「候補」欄に記録して起票する。**アイコンの不足は画面を作らない理由にならない**
>   （既定と唯一の例外は §6「代替の既定」）
> - 語彙の追加・変更が承認されたら本表を同じコミットで更新する。追加は Material Symbols の範囲内で選ぶ
> - 各値はすべて**暫定**（第一弾。デジ庁 Figma データ内のアイコン指定値〔サイズ・weight・部品ごとの
>   使用アイコン〕は第二段で採取して突合する）
>
> 起票元: `tickets/2026-08-25-icon-definition.md` ICN-01〜06（2026-08-25 承認）

## 1. アイコンセット（ICN-01）

| 項目 | 決定 |
|---|---|
| セット | **Material Symbols**（Google。デジ庁 DADS の Figma デザインデータが UI アイコンとして同梱しているものと同一） |
| スタイル | **Outlined** に固定（Rounded / Sharp は使わない） |
| 軸 | **weight 400 / fill 0（線）/ grade 0** に固定。optical size は寸法に一致させる（16 → opsz 20、20 → 20、24 → 24）。状態（選択・アクティブ）を fill の切り替えで表さない — 状態は色トークンと aria 属性で伝える |
| 配布形態 | **SVG**（インライン `<svg>` またはスプライト）。**可変フォント版（リガチャ）は使わない** — フォント未ロード時に `check_circle` 等の文字列が露出する、静的 HTML 検証が外部フォントに依存する、の 2 点 |
| ライセンス | **Apache License 2.0**（商用可・改変可）。第一弾（仕様データのみ）では SVG 実体を同梱していないため再配布は発生していない。第二段で SVG を同梱する時点で `icons/LICENSE-material-symbols.txt`（Apache 2.0 全文）と NOTICE を同じディレクトリに置く |
| 使わないもの | デジ庁「イラストレーション・アイコン素材」（別規約。行政手続きの説明コンテンツ用・線 / 塗り 60 種）— UI 部品のアイコンではない |

## 2. 語彙（ICN-03）— カタログに無いアイコンは存在しない

役割名（左列）が spec で使う正式な呼び名。実体（Material Symbols 名）は第二段のデジ庁突合で差し替わりうるが、
役割名は変えない（spec 側を書き換えなくてよいようにする）。

| 役割名 | Material Symbols 名（暫定） | 使う部品・箇所 | 種別 | 寸法 |
|---|---|---|---|---|
| `status-success` | `check_circle` | NotificationBanner type=success | 情報 | lg |
| `status-error` | `error` | NotificationBanner type=error / form-page input-error のエラーサマリー見出し | 情報 | lg（サマリーは md） |
| `status-warning` | `warning` | NotificationBanner type=warning | 情報 | lg |
| `status-info` | `info` | NotificationBanner type=info | 情報 | lg |
| `close` | `close` | NotificationBanner・ModalDialog の閉じるボタン（可視テキスト「閉じる」と組で使う） | 装飾 | md |
| `expand` | `expand_more` | Disclosure の開閉（開いた状態で 180 度回転）/ Select・Combobox の開閉矢印 | 装飾 | md |
| `sort-none` | `swap_vert` | Table ソート可能列のヘッダ（未ソート） | 装飾 | sm |
| `sort-asc` | `arrow_upward` | Table ソート中（昇順） | 装飾 | sm |
| `sort-desc` | `arrow_downward` | Table ソート中（降順） | 装飾 | sm |
| `prev` | `chevron_left` | Pagination「前へ」（リード配置） | 装飾 | md |
| `next` | `chevron_right` | Pagination「次へ」（テール配置） | 装飾 | md |
| `calendar` | `calendar_today` | DatePicker calendar=true のカレンダーボタン | 装飾 | md |
| `add` | `add` | RepeatingFieldGroup「行を追加」Button（従来の記号文字「+」を置き換え） | 装飾 | md |
| `remove` | `delete` | RepeatingFieldGroup の行「削除」Button / detail-page ヘッダの「削除」Button | 装飾 | md |
| `external` | `open_in_new` | Link external（テール配置。「（新しいタブで開きます）」の隠しテキストと組で使う） | 装飾 | md（インラインでは 1em 相当 = 隣接文字サイズに合わせてよい） |
| `search` | `search` | list-page フィルタ行の「絞り込み」Button / 詳細検索パネルの「検索」Button | 装飾 | md |

- **種別の判定規則**: 「アイコンが唯一の担い手なら情報、文字で書けるなら文字に書いてアイコンは装飾」。
  - **情報** = 隣接するラベルだけでは伝わらない分類そのものを担う（NotificationBanner の type）。`role="img"` + `aria-label`
  - **装飾** = ラベル（可視または視覚的に隠したテキスト）が意味を担う。`aria-hidden="true"`
  - `external` は「新しいタブで開く」という**挙動の予告**であり、WCAG 達成方法 G201 が文字での告知を前提にするため、
    情報はリンクテキスト側（隠しテキスト）に持たせてアイコンは装飾にする（ICN-03 (b) — 2026-08-25 承認）
- `edit` / `download` / `print` / `filter` / `menu` 等は spec に登場しないため**未登録**（必要になった時点で起票 → §6。
  **承認まではアイコンを付けずにラベルのみで組む** — §6「代替の既定」）

## 3. 寸法（ICN-04）— `tokens/tokens.json` の `icon.size`

| トークン | 暫定値 | 用途 |
|---|---|---|
| `icon.size.sm` | 16px | `font.size.caption`（13px）の文字に隣接 / Table ソート / Badge 内（使う場合） |
| `icon.size.md` | 20px | `font.size.body`（16px）の文字に隣接 / Button・Link・Tabs・Disclosure・Pagination・閉じる |
| `icon.size.lg` | 24px | NotificationBanner の type アイコン / ModalDialog 見出し横（使う場合） |

- 44×44 CSS px のターゲット領域は**アイコンではなく操作要素（Button 等）側の規定**。アイコンを拡大して満たさない
- 寸法は `width` / `height` 両方にトークンを当て、`font-size` 継承に任せない（記号文字時代の「本文サイズに追従」を廃止）

## 4. 配置・間隔・色（ICN-05）

デジ庁 基本デザイン「アイコン」概要（2025-07-30・v2.17.1）の配置 4 型を採用する:
**フロント**（ブロックの先頭）/ **リード**（行内・ラベルの直前）/ **テール**（行内・ラベルの直後）/ **エンド**（ブロックの末尾）。

| 規則 | 内容 |
|---|---|
| 既定の配置 | **リード**（ラベルの直前・左） |
| テールにするもの | `external`（Link）/ `next`（Pagination）/ `expand`（Select・Combobox の入力欄右端。Disclosure は部品規定どおりタイトル左 = リード） |
| フロント / エンド | NotificationBanner の type アイコン（フロント）のみ |
| ラベルとの間隔 | **`space.xs`（4px）**。NotificationBanner の type アイコンとタイトルの間は `space.sm`（8px。ブロック配置のため広め） |
| 縦位置 | **文字の中央揃え**（`vertical-align: middle` 相当・flex なら `align-items: center`）。ベースライン揃えにしない |
| 色（既定） | **親要素の文字色を継承する（`currentColor`）**。アイコン専用の色トークンは作らない。Button 内なら Button の文字色（`on-primary` / `primary` / `disabled-text`）、本文中なら `text` にそのまま追従する |
| 色（例外） | 独立して色を持つのは **NotificationBanner の type アイコンのみ**（`tokens/ROLE-MAP.md` §2「意味色の文字（白背景上）」— success / danger / info は semantic 色、warning は `warning`〔非テキスト 3:1 は満たす〕） |
| コントラスト | テキスト列内に置くアイコンは 4.5:1、独立した非テキスト要素は 3:1（デジ庁 a11y ③）。`warning`（約 3.2:1）はタイトル文字列の一部にせず独立要素として置く |
| 回転・反転 | `expand` の 180 度回転（Disclosure open）のみ許容。他のアイコンを回転・反転して別の意味に流用しない |

## 5. アクセシビリティ（ICN-02 / 05）— デジ庁「アイコン」a11y（2025-07-30）の採取 + 運用形

| # | デジ庁規定 | 本 DS の運用 |
|---|---|---|
| ① | アイコンは必ずラベルと組み合わせる | **ラベル必須**（GAP-14 IconButton 不採用と同じ）。可視ラベルが既定。視覚的に隠したラベルで代替できるのは、本表で明示した箇所（`external` の告知）のみ。アイコンのみのボタン・タブ・リンクは作らない |
| ② | ラベルと組み合わせたアイコンには代替テキスト不要（alt=""）。単体ならラベル相当の代替テキスト | **装飾** = `<svg aria-hidden="true" focusable="false">`。**情報** = `<svg role="img" aria-label="…">`。NotificationBanner の type アイコンは情報扱いで aria-label「成功」「エラー」「警告」「インフォメーション」を維持する（デジ庁原則〔alt=""〕からの**自社翻案** — タイトル文だけでは種別が伝わらないため。デジ庁実装が alt="" だった場合に合わせるかは第二段の判断点） |
| ③ | コントラスト比 4.5:1（テキスト列内）/ 3:1（非テキスト単体） | §4 コントラスト参照 |
| ④ | ラベルがリンクならアイコンもリンク範囲に含める（別の a 要素にしない） | `external` は `<a>` の内側に置く。Button 内のアイコンも同様に button の内側 |
| ⑤ | アイコン単体で使う場合はターゲット 44×44 CSS px 以上 | 単体使用は原則禁止のため該当なし（ターゲット領域は操作要素側の規定） |

**視覚的に隠したテキストの手法**（`external` の告知、RepeatingFieldGroup の行内隠しラベル等で共通）:
`position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap` 相当。
`display: none` / `visibility: hidden` / `aria-hidden` は読み上げからも消えるため使わない。

## 6. 禁止事項（ICN-05）と起票

**アイコンとして使わないもの**
- 記号文字（✓ ✔ ✕ ✗ × ▼ ▲ ▶ ◀ → ← ↑ ↓ + − ⚠ ⓘ ● ■ ◆ ★ 等）— フォント・OS で字形と太さが変わり、寸法・色・a11y を管理できない
- 絵文字（`brand-principles.md` 禁止リスト）
- アイコンフォント（リガチャ・Web フォント版 Material Symbols を含む）
- 自作 SVG・他セット（Font Awesome / Heroicons / Lucide 等）の混在
- 語彙表（§2）に無い Material Symbols

**検出**: `scripts/audit-tokens.mjs` が .html / .tsx / .css のアイコン用要素（class に `icon` を含む）内のテキスト、
記号文字のみの要素内容、CSS `content:` の記号文字を検出する（REQ-03 の色キーワード検出と同じ「代用の芽を CI で摘む」運用）。

### 代替の既定 — 語彙に無いアイコンが必要になったとき（2026-09-01 追加）

| 種別（§2 の判定規則） | 対応 |
|---|---|
| **装飾**（ラベルが意味を担う = 語彙外はほぼ全てこちら） | **アイコンを付けず、可視ラベルのみで組んで作業を続行する。画面の作成・生成を止めない**。下の「候補」欄に役割名・用途・置きたい箇所を記録して起票する |
| **情報**（アイコンだけが分類を担う） | **停止して起票する**（ラベルで代替できないため）。該当は NotificationBanner の type = `status-*` のみで 4 種すべて登録済み。新たに該当が出たら、まず §2 の判定規則「文字で書けるなら文字に書いてアイコンは装飾」に立ち返り、情報をテキスト側へ移せないか検討する |

- **アイコンの不足は画面を作らない理由にならない**。装飾アイコンは `aria-hidden` の飾りであり、
  §5 ①「アイコンは必ずラベルと組み合わせる」の帰結として**省略しても情報は失われない**
  （逆に、アイコンが無いと成立しない画面は、その時点で ①違反を疑う）
- `audit-tokens.mjs` が検出するのは記号文字・絵文字による**代用**のみ。**アイコンの不在は違反ではない**
  ため、ラベルのみで組んだ画面は検査を通る
- **先例**: Pagination の「先頭」「末尾」は語彙未登録のため**アイコンを付けずに実装する**と部品仕様が
  規定している（`Pagination.component-spec.json` の `layout_guidance`）。§2 末尾の
  `edit` / `download` / `print` / `filter` / `menu` も同じ扱い
- **停止して起票するのは部品・パターンが index.json に無い場合**（画面の骨格が作れない）。
  アイコンを `does_not_exist_yet` と同じ強度で扱わない（AGENTS.md ハード制約に書き分けあり）

**候補（未承認 — 起票待ち）**: なし

## 7. 部品別の早見表

| 部品・箇所 | 役割名 | 配置 | 寸法 | 色 | a11y |
|---|---|---|---|---|---|
| NotificationBanner type アイコン | `status-*` | フロント | lg | type の semantic 色（独立色） | role="img" + aria-label |
| NotificationBanner / ModalDialog 閉じる | `close` | リード（「閉じる」の左） | md | currentColor | aria-hidden |
| Disclosure 開閉 | `expand` | リード（タイトル左・open で 180 度） | md | currentColor | aria-hidden（状態は aria-expanded / open） |
| Select / Combobox 開閉矢印 | `expand` | テール（入力欄右端） | md | currentColor | aria-hidden（Combobox の状態は aria-expanded） |
| Table ソート | `sort-none` / `sort-asc` / `sort-desc` | テール（見出しテキストの右） | sm | currentColor（`text-subtle`） | aria-hidden（状態は aria-sort） |
| Pagination 前へ / 次へ | `prev` / `next` | prev = リード / next = テール | md | currentColor | aria-hidden（可視テキスト必須） |
| DatePicker カレンダーボタン | `calendar` | リード（「カレンダー」の左） | md | currentColor | aria-hidden（可視テキスト必須） |
| RepeatingFieldGroup 行を追加 / 削除 | `add` / `remove` | リード | md | currentColor | aria-hidden（可視テキスト必須） |
| detail-page 削除 | `remove` | リード | md | currentColor | aria-hidden |
| Link external | `external` | テール | md（インラインは 1em 相当可） | currentColor | aria-hidden + 隠しテキスト「（新しいタブで開きます）」 |
| list-page 絞り込み / 検索 | `search` | リード | md | currentColor | aria-hidden |
| form-page エラーサマリー見出し | `status-error` | リード | md | `on-danger-subtle`（見出し文字色を継承） | aria-hidden（見出しテキストが意味を担う） |
| Button 全般（アイコンを添える場合） | 語彙表の範囲 | リード | md | currentColor | aria-hidden（ラベル省略不可） |
| Tabs（アイコンを添える場合） | 語彙表の範囲 | リード | md | currentColor | aria-hidden（ラベル省略不可） |
