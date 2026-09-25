# 部品 → 色の役割 → semantic トークン 対応表（ROLE-MAP）

> **位置づけ**: 本ファイルは「部品・箇所 → 必要な色の役割 → `color.semantic.*` トークン」の
> **唯一の対応表**。部品仕様（component-spec.json）・パターン（pattern.json）・モック実装が
> 色を選ぶときはまずここを見る。正のトークン値は `tokens/primitive.json`（共有プリミティブ）+
> `tokens/semantic.json`（ベースDSの既定値）/ `tokens/semantic.wireframe.json`（wireframe
> プロファイル = 要件定義工程のワイヤーフレーム用の無彩色差分）/ `tokens/semantic.<project>.json`
> （プロジェクト別のブランド色上書き。例: `semantic.travel-expense-demo.json`）
> （本表はキー名の参照先一覧であり値を持たない — **キー名はどのプロファイル・テーマでも共通**。
> 本表の「使う箇所 / 使わない箇所」の規律も共通で、無彩色プロファイルでも変わらない）。
>
> **運用ルール**
> - 新しい面・状態の色が必要になったら、**まずこの表に無いか確認**する。表にあればそのトークンを使う
> - 表に無い場合は**自分でトークンを追加せず、代用（別役割トークンの流用・opacity・色キーワード直書き）も
>   せずに人間へ起票**する（AGENTS.md ハード制約。`scripts/audit-tokens.mjs` が hex / px / 色キーワード /
>   rgb()・hsl() の直書きを検出する）
> - トークンの追加・変更が承認されたら本表も同じコミットで更新する（表とトークンの二重管理を防ぐ）
> - 各値はすべて**暫定**（第一弾。第二段でデジ庁 DADS プリミティブへ移植 — DECISIONS.md「トークン対応表」参照）
>
> 起票元: `tickets/2026-08-25-density-and-layout-requests.md` REQ-03（2026-08-25 承認）。
> 2026-08-25 追記: `tickets/2026-08-25-column-rules-and-visual-requests.md` REQ-17（ページ地 `canvas` の新設・
> Table ヘッダ専用の面 `table-header` の分離）/ REQ-19（形での操作可能性の区別 — §5）を反映。

## 1. 面（基底面・沈んだ面・淡色面）

| 役割 | トークン | 使う箇所 | 使わない箇所 |
|---|---|---|---|
| ページ地 | `color.semantic.canvas` | `body` の背景（ページの地）— この上に白い面が載って階層が出る | 面（入力欄・Table・ヘッダ・モーダル本体 → background）/ 選択・強調などの状態表現 / 文字色 |
| 基底面（白） | `color.semantic.background` | 入力欄（InputText・Textarea・Select・Combobox・DatePicker）の背景 / Table の面 / app-shell ヘッダ / ModalDialog 本体 / Button secondary の背景 | ページの地（→ canvas）/ 濃い面の上の文字（→ on-primary） |
| 一段沈んだ面 | `color.semantic.surface` | セクション区切り / 読み取り専用領域 | Table ヘッダ行（→ table-header）/ 入力欄・ヘッダ・モーダル本体の背景（→ background）/ Table 選択行・行 hover |
| ヘッダ行の面 | `color.semantic.table-header` | Table のヘッダ行 / RepeatingFieldGroup の見出し行 | ヘッダ以外の面 / 行 hover（→ surface-hover）/ 選択行（→ primary-subtle） |
| hover 面 | `color.semantic.surface-hover` | Button secondary hover / Table 行 hover（row-hover） | 静的な面 / 無効面（→ disabled-surface） |
| primary 淡色面 | `color.semantic.primary-subtle` | Table 選択行（row-selected）/ Badge color=primary 背景 | 白文字の背景 / 文字色 |
| danger 淡色面 | `color.semantic.danger-subtle` | Badge color=danger 背景 / NotificationBanner type=error 背景 / form-page input-error のエラーサマリー背景 | エラー以外の注意・強調 |
| success 淡色面 | `color.semantic.success-subtle` | Badge color=success 背景 / NotificationBanner type=success 背景 | — |
| warning 淡色面 | `color.semantic.warning-subtle` | Badge color=warning 背景 / NotificationBanner type=warning 背景 | 上に warning 色の文字を置く（文字は text） |
| info 淡色面 | `color.semantic.info-subtle` | NotificationBanner type=info 背景 | Badge（info variant は設けない） |
| 無彩色の淡色面 | `color.semantic.neutral-subtle` | Badge color=neutral 背景 | 罫線（→ border）/ 読み込み中表示（→ skeleton） |
| 無効面 | `color.semantic.disabled-surface` | Button disabled の背景 | 無効以外 |
| 遮蔽 | `color.semantic.overlay` | ModalDialog の背後（バックドロップ） | 他の面・装飾 |
| 読み込み中 | `color.semantic.skeleton` | Skeleton 部品 | 面・罫線の代用 |

**wireframe プロファイル（無彩色）での面の見分け**: ベースでは Table 選択行（`primary-subtle`）を
**色相差**で hover 行（`surface-hover`）・ヘッダ行（`table-header`）と区別しているが、無彩色化すると
色相が消えるため輝度差だけになる（`semantic.wireframe.json` は `primary-subtle` を gray.200 に置いて
hover 行と 1.13:1 の段を作っている）。**淡色面が 3 役で近接するため、無彩色のモックでは
「面の色だけで状態を伝える」設計を避ける**（選択は行頭の罫線・チェックボックス等と併用する）。
この段が読めるかは検証中（MOCK-A1-AB-TRIAL.md 観点 10）— 読めなければ起票して primitive に中間段を足す。

## 2. 文字・アイコン

| 役割 | トークン | 使う箇所 |
|---|---|---|
| 本文 | `color.semantic.text` | 本文 / Badge neutral・warning の文字 / 淡色面の上の本文（NotificationBanner 本文） |
| 補助 | `color.semantic.text-subtle` | サポートテキスト / 「※任意」/ Table ヘッダ文字 |
| 濃い面の上 | `color.semantic.on-primary` | Button primary・danger のラベル |
| 無効 | `color.semantic.disabled-text` | Button disabled のラベル |
| 必須表示 | `color.semantic.required` | 「※必須」テキスト |
| 意味色の文字（白背景上） | `color.semantic.primary` / `danger` / `success` / `info` | Badge color=success の文字 / NotificationBanner のアイコン・タイトル・枠線（type 別）/ Button secondary の文字・枠線（primary）/ 入力欄直下のエラーテキスト（danger） |
| 意味色の文字（淡色面上） | `color.semantic.on-primary-subtle` / `on-danger-subtle` | Badge color=primary / danger の文字 / form-page エラーサマリー（danger-subtle 上）の見出し。600 段の primary / danger は淡色面上で AA 4.5:1 未満（約 4.2 / 4.4:1）のため 700 段の文字専用トークンを使う。success は success-subtle 上でも 4.8:1 を満たすため専用トークンなし |

`warning` は文字色に使わない（白背景・warning-subtle 上とも 4.5:1 未満）。

**アイコンの色（2026-08-25 ICN-05）**: アイコン専用の色トークンは設けない。既定は**親要素の文字色を継承（currentColor）**
— Button 内なら Button の文字色、本文中なら `text`、Table ヘッダなら `text-subtle`、disabled なら `disabled-text` に追従する。
独立して色を持つのは NotificationBanner の type アイコン（上表「意味色の文字（白背景上）」— warning は非テキスト 3:1 を満たす
`warning` を使う）のみ。語彙・寸法・配置・a11y は `icons/ICON-MAP.md`。

## 3. 罫線・フォーカス

| 役割 | トークン | 使う箇所 |
|---|---|---|
| 罫線 | `color.semantic.border` | Table 罫線 / 入力欄の枠線（default）/ セクション区切り線 / RepeatingFieldGroup 行区切り |
| エラー枠線 | `color.semantic.danger` | 入力欄の枠線（error）/ NotificationBanner type=error 枠線 |
| フォーカスリング | `color.semantic.focus` | 全部品共通の outline（Button / Link / 入力欄 / Checkbox / RadioButton / Tabs / Pagination 等）。outline 幅 2px 相当 + background 色の隙間 |

## 4. 部品別の早見表

### Button（詳細は `components/Button/Button.component-spec.json` の `color_map`）

| variant \ state | default | hover | disabled | focus |
|---|---|---|---|---|
| primary | 背景 `primary` / 文字 `on-primary` | 背景 `primary-hover` / 文字 `on-primary` | 背景 `disabled-surface` / 文字 `disabled-text` | リング `focus` |
| secondary | 背景 `background` / 枠線・文字 `primary` | 背景 `surface-hover` / 枠線・文字 `primary-hover` | 背景 `disabled-surface` / 枠線・文字 `disabled-text` | リング `focus` |
| danger | 背景 `danger` / 文字 `on-primary` | 背景 `danger-hover` / 文字 `on-primary` | 背景 `disabled-surface` / 文字 `disabled-text` | リング `focus` |

disabled を `opacity` で代用しない。Link appearance="button" は Button secondary と同じ対応。

### Badge（詳細は `components/Badge/Badge.component-spec.json` の `variants.color`）

| color | 背景 | 文字 |
|---|---|---|
| neutral | `neutral-subtle` | `text` |
| primary | `primary-subtle` | `on-primary-subtle`（約 5.8:1） |
| danger | `danger-subtle` | `on-danger-subtle`（約 5.9:1） |
| success | `success-subtle` | `success` |
| warning | `warning-subtle` | `text` |

枠線なし（単色塗り）。

### Table

| 状態 | トークン |
|---|---|
| ヘッダ行 | 背景 `table-header` / 文字 `text-subtle` / 罫線 `border` |
| row-hover | 背景 `surface-hover` |
| row-selected | 背景 `primary-subtle` |
| 罫線 | `border` |

### NotificationBanner

| type | 背景 | アイコン・タイトル・枠線 | 本文 |
|---|---|---|---|
| success | `success-subtle` | `success` | `text` |
| error | `danger-subtle` | `danger` | `text` |
| warning | `warning-subtle` | 枠線・アイコン `warning` / タイトル `text` | `text` |
| info | `info-subtle` | `info` | `text` |

### ModalDialog

| 箇所 | トークン |
|---|---|
| バックドロップ | `overlay` |
| 本体 | 背景 `background` / 枠線 `border` |

### form-page input-error（エラーサマリー）

| 箇所 | トークン |
|---|---|
| サマリー背景 | `danger-subtle` |
| サマリー枠線 | `danger` |
| サマリー見出し（danger-subtle 上の文字） | `on-danger-subtle` |
| 各項目のエラーテキスト | `danger` / 入力欄の枠線 `danger` |

（form-page pattern.json の `states.input-error` にも同内容を反映済み — 2026-08-25）

### 入力欄（InputText / Textarea / Select / Combobox / DatePicker）

| 箇所 | トークン |
|---|---|
| 背景 | `background` |
| 枠線 default / error | `border` / `danger` |
| 文字 / プレースホルダ相当の補助 | `text` / `text-subtle` |
| フォーカス | リング `focus` |

### app-shell ヘッダ

| 箇所 | トークン |
|---|---|
| ページの地（`body`） | `canvas`（ヘッダ・本体の面はこの上に載る — 2026-08-25 REQ-17） |
| ヘッダ背景 | `background`（ブランド面にする場合のみ `brand` — 文字を載せない大面積に限る） |
| 下罫線 | `border` |
| ナビ Link 文字 | `text`（現在地は `primary` ではなく下線 + 太字で示す） |

## 5. 形（角丸）— 操作可能性の区別（2026-08-25 REQ-19）

色ではないが、同じ「取り違えを防ぐ対応表」として本ファイルで持つ。

| 種別 | トークン | 対象 |
|---|---|---|
| 押せる要素 | `radius.sm` | Button（全 variant）/ Link appearance="button" / 入力欄 |
| 押せない表示要素 | `radius.full` | Badge（状態チップ）— 全周丸（ピル形） |

上位原則は `brand-principles.md`「形（角丸）でも操作可能性を区別する」。
角丸トークンの演算による代用（`calc(radius.md * 2)` 等）はせず、必要な段が無ければ起票する。
