# 設計判断の記録 — DECISIONS（なぜこう決めたか）

> 旧 `DESIGN.md`。2026-08-25 に改名 — L1 Spec Template では `specs/<feature>/design.md` が技術設計書の
> 固定名で、DS 側の DESIGN.md と混同するため。中身は DS の原則 + 土台（デジ庁 DADS）との対応 +
> 決定ログ（起票 → 承認 → 対応の経緯）。各チケットの「決定の経緯は DECISIONS.md に記録」はこのファイルを指す。

## 原則

- **正はコード**：`tokens/` 配下（primitive.json / semantic.json / semantic.wireframe.json /
  semantic.<project>.json、DTCG）と
  components/ が唯一の正。Figma・Claude Design・ドキュメントは派生物
- **セマンティック命名**：`color-primary-600` のように役割で命名する。`blue-600` のような見た目名は primitive 層に閉じ、参照は semantic 層経由
- **判別可能な選択肢**：Props は自由文字列より union 型。AI が迷わない API を優先する
- **機械で守れるルールだけをルールにする**：人間の目視が必要なルールは、スクリプトで検証できる形に再設計するまで暫定扱い

## 土台 DS: デジタル庁デザインシステム（2026-08-18 追記）

- **土台** = デジタル庁デザインシステムβ版（DADS）。参照バージョン:
  **design-tokens v2.0.1**（2026-05-28 リリース・MIT）/ 公式サイト参照日 **2026-08-18**
  （HANDOFF 設計判断 25）
- **取り込み方式**: git フォークではなく**自社スキーマへの移植（採取）**。第一弾は
  部品・パターンの使い方ルールのみ（component-spec.json / pattern.json）。
  トークン実値の移植・部品実装は第二段
- **更新追従**: 定点観測 + 必要時のみ再採取（自動追従しない）
- **トークン実値の出所**（2026-08-26 追記）: `primitive.json` の色値は**デジ庁由来ではない**。
  一般的な UI パレット（Tailwind CSS の既定パレットと同一の値）を土台に選定し、そこへ
  自社ブランド色（`brand` / `teal` 系）を足した構成。デジ庁から借りているのは
  **2 層構造（primitive / semantic）と Style Dictionary で配信する設計手法**であり、
  トークン実値そのものの再配布は発生していない（＝ MIT の表示義務は生じていない）。
  デジ庁の実値との突合は第二段 — そのとき「どこが借り物でどこが自前か」を
  迷わないための記録（採取手順は `tokens/HARVESTING.md`）
- **使わないもの**: サンプル実装（React 版は Tailwind ベース — 判断 16。Props 設計・
  状態・a11y の参照のみ）/ Figma データ（CC BY 4.0 — 第二段でアイコン指定値の突合にのみ参照）/
  **イラストレーション・アイコン素材**（別規約。行政手続きの説明コンテンツ用・線 / 塗り 60 種 —
  UI 部品のアイコンではない）
- **UI アイコン**: デジ庁 Figma データが UI アイコンとして同梱している **Material Symbols
  （Apache License 2.0）** を採用（2026-08-25 ICN-01。Outlined・SVG 配布。語彙・寸法・配置・a11y は
  `icons/ICON-MAP.md`）。従来の「アイコン素材は使わない」はイラストレーション素材を指す記述であり、
  UI アイコンまで除外するものではなかったため書き分けた

### 部品名の規約（デジ庁との名寄せ）

- デジ庁に存在する部品は**英語名を揃える**: InputText（インプットテキスト。
  **TextField という部品名は使わない** — 雛形 list-page が要求していた TextField は
  InputText への改名で解消）/ ModalDialog（モーダルダイアログ）/ Button / Select / Table
- デジ庁に該当が無い部品は**自社定義と割り切る**: EmptyState / Badge
  （Badge の近縁にチップラベルがあるがガイドライン準備中 — 公開後に名寄せ再検討）
- ガイドライン準備中の部品（ModalDialog / PageNavigation 等）の spec は**自社翻案** —
  各 spec の `source` フィールドに明記し、デジ庁公開後に突合して更新する

### 部品・パターン選定の記録（3 基準 = パターン要求 / 頻度 / 誤用リスク）

- **部品 8 個**: Button（既存・デジ庁ガイドラインで増補）/ Link（既存・据え置き）/
  InputText / Select / Table / ModalDialog / EmptyState / Badge
- 雛形の意図的な穴（list-page が要求する Table / TextField / EmptyState）は
  Table / InputText / EmptyState で解消（DS-GUIDE §2-3 完了ライン 1）
- **Pagination**（デジ庁名: ページナビゲーション — ガイドライン準備中）は部品化を見送り、
  list-page の layout で簡易構成（件数表示 + 前へ/次へ Button）を規定。
  does_not_exist_yet に登録（専用部品が必要になったら起票）
- **パターン 4 個**（PATTERN-CATALOG Tier 1）: list-page（改修）/ form-page /
  detail-page / confirm-flow。**app-shell は保留** — MK1 のモック体裁と合わせて
  要否判断（それまで does_not_exist_yet に登録）。Tier 2 / Tier 3 は
  does_not_exist_yet に名前のみ登録（捏造防止 — 昇格は MK1 / CHK の起票経由）

### トークン対応表（自社 semantic ↔ デジ庁 — 第二段の primitive 移植用メモ）

> デジ庁 design-tokens (v2.0.1) の重要な前提: 色の semantic トークンは
> **Error / Success / Warning / Key の 4 系統のみ**で、テキスト・ボーダー・面の
> 役割トークンは存在しない（役割対応はプリミティブから自社で選定する）。
> **スペーシングトークンも存在しない**（「基準単位 8 CSS px」の原則のみ）。
> 確定値の採取元: `examples/tokens.css`（v2.0.1 タグ）。変数形式は kebab-case
> （例: `--color-primitive-blue-900`）。hover 段の規定はデジ庁に無いため自社判断。

| 自社 semantic | 現プレースホルダ値 | デジ庁対応候補（v2.0.1） |
|---|---|---|
| color.semantic.primary | #1d4ed8 | `--color-key-900`（キーカラー = primitive blue-900 #0017c1 へのエイリアス。段の最終選定は第二段） |
| color.semantic.primary-hover | #1e40af | `--color-key-1000`（= blue-1000 #00118f。hover 段は自社判断） |
| color.semantic.text | #111827 | `--color-neutral-solid-gray-900`（#1a1a1a。役割トークン無し — プリミティブから選定） |
| color.semantic.text-subtle | #374151 | `--color-neutral-solid-gray-536`（#767676。コントラスト 4.5:1 境界用の特殊段） |
| color.semantic.border | #e5e7eb | `--color-neutral-solid-gray-420`（#949494・3:1 境界用）または `-200`（#cccccc）— 第二段で確定 |
| color.semantic.surface | #f9fafb | `--color-neutral-solid-gray-50`（#f2f2f2） |
| color.semantic.danger | #dc2626 | `--color-semantic-error-1`（= primitive red-800 #ec0000） |
| color.semantic.success | #15803d（2026-08-25 追加・暫定） | `--color-semantic-success-2`（NotificationBanner success で使用） |
| color.semantic.warning | #d97706（2026-08-25 追加・暫定） | `--color-semantic-warning-yellow-2`（NotificationBanner warning。文字色には使わない） |
| color.semantic.info | #1d4ed8（2026-08-25 追加・暫定） | キーカラー系（デジ庁 info-1 は primitive blue-900 直参照。semantic info 色はデジ庁に無い — 第二段で選定） |
| color.semantic.skeleton | #e5e7eb（= gray.200。2026-08-25 追加） | 対応トークン無し — `--color-neutral-solid-gray-200`（#cccccc）等から第二段で選定（border と別名で管理） |
| color.semantic.on-primary | #ffffff（= white。2026-08-25 REQ-03 追加・暫定） | 役割トークン無し — `--color-neutral-white`（#ffffff）相当から第二段で選定 |
| color.semantic.background | #ffffff（= white。2026-08-25 REQ-03 追加・暫定） | 役割トークン無し — `--color-neutral-white` 相当から第二段で選定（surface = gray.50 と役割分離） |
| color.semantic.surface-hover | #f3f4f6（= gray.100。2026-08-25 REQ-03 追加・暫定） | 役割トークン無し — `--color-neutral-solid-gray-50〜100` から第二段で選定（hover 段の規定はデジ庁に無い） |
| color.semantic.primary-subtle | #e6f6f7（= teal.50。brand #00a1ae の 10% ティント。2026-08-25 REQ-03 追加・暫定） | `--color-key-100`（キーカラー淡色）相当 — ブランド色確定後に第二段で選定 |
| color.semantic.danger-hover | #b91c1c（= red.700。2026-08-25 REQ-03 追加・暫定） | 役割トークン無し — `--color-primitive-red-900` 等から第二段で選定（hover 段の規定はデジ庁に無い） |
| color.semantic.danger-subtle | #fef2f2（= red.50。2026-08-25 REQ-03 追加・暫定） | `--color-primitive-red-50〜100` 相当（デジ庁 NotificationBanner error の背景色）から第二段で選定 |
| color.semantic.success-subtle | #f0fdf4（= green.50。2026-08-25 REQ-03 追加・暫定） | `--color-primitive-green-50〜100` 相当（同 success の背景色）から第二段で選定 |
| color.semantic.warning-subtle | #fffbeb（= amber.50。2026-08-25 REQ-03 追加・暫定） | `--color-primitive-yellow-50〜100` 相当（同 warning の背景色）から第二段で選定 |
| color.semantic.info-subtle | #eff6ff（= blue.50。2026-08-25 REQ-03 追加・暫定） | `--color-primitive-blue-50〜100` 相当（同 info の背景色）から第二段で選定 |
| color.semantic.neutral-subtle | #e5e7eb（= gray.200。border と別名。2026-08-25 REQ-03 追加・暫定） | 役割トークン無し — `--color-neutral-solid-gray-100〜200` から第二段で選定 |
| color.semantic.disabled-text | #9ca3af（= gray.400。2026-08-25 REQ-03 追加・暫定） | 役割トークン無し — `--color-neutral-solid-gray-420`（#949494）等から第二段で選定 |
| color.semantic.disabled-surface | #f3f4f6（= gray.100。surface-hover と別名。2026-08-25 REQ-03 追加・暫定） | 役割トークン無し — `--color-neutral-solid-gray-50〜100` から第二段で選定 |
| color.semantic.focus | #00818b（= teal.600。primary と同値のエイリアス。2026-08-25 REQ-03 追加・暫定） | デジ庁実装のフォーカス色（`--color-focus` 相当。専用色を持つ）を第二段で採取して置き換え |
| color.semantic.on-primary-subtle | #006971（= teal.700。primary-hover と別名。2026-08-25 REQ-03 前倒し追加・暫定） | `--color-key-1000` 相当（淡色面 key-100 上で 4.5:1 以上になる段を第二段で選定） |
| color.semantic.on-danger-subtle | #b91c1c（= red.700。danger-hover と別名。2026-08-25 REQ-03 前倒し追加・暫定） | `--color-primitive-red-900` 相当（error 淡色面上で 4.5:1 以上になる段を第二段で選定） |
| color.semantic.overlay | #11182780（gray.900 α50%・hex8。2026-08-25 REQ-03 追加・暫定） | 役割トークン無し — `--color-neutral-solid-gray-900` + alpha を第二段で選定（デジ庁モーダルのバックドロップ実装を採取） |
| print.margin | 15mm（2026-08-25 追加・暫定） | 対応トークン無し（デジ庁に印刷向けトークンは存在しない）— 自社定義を維持 |
| space.xxs / xs / sm / ms / md / lg / xl | 2/4/8/12/16/24/40px（xxs・ms は 2026-08-25 REQ-04 で追加） | 対応トークン無し（8px 基準の原則のみ。2px = 1/4、12px = 1.5 倍で同原則の範囲内）— 自社スケールを維持 |
| radius.sm / md | 4px / 8px | `--border-radius-4` / `--border-radius-8` |
| font.size.caption | 13px | 該当なし — 最近似 `--font-size-14`（第二段で 14px へ寄せるか判断） |
| font.size.body | 16px | `--font-size-16` |
| font.size.heading | 24px | `--font-size-24` |
| icon.size.sm / md / lg | 16 / 20 / 24px（2026-08-25 ICN-04 追加・暫定） | 対応トークン無し（デジ庁公開ページにアイコン寸法の規定は無い）— Material Symbols 既定 24px・opsz 20〜48 の範囲内で自社定義。Figma データ内の部品ごとの指定値を第二段で突合 |

参考（第二段で使う可能性）: `--font-family-sans`（Noto Sans JP 系）/
`--line-height-100〜175` / `--elevation-1〜8` / `--font-weight-400・700`

## モック検証ログ（起票 — 実装は未着手）

モック画面作成の検証中に見つかった不足をここに記録する。AGENTS.md のハード制約により、
記載の項目は自作しない。実装可否・優先順位は人間判断（CHK 経由の起票）待ち。

### 2026-08-18: 部品 4 件・パターン 1 件

- **部品 4 件（Textarea / DatePicker / RadioButton / Checkbox）** —
  index.json の does_not_exist_yet に名前のみ登録済みだった。各 component-spec.json の
  `never_use_when` / `confusable_with` でも「第一弾未提供 — 起票」として
  既に参照されていた、意図的に残していた穴。今回のモックで実際に必要になったことで、
  Tier 2/3 からの昇格候補として実需が確認された → **同日中に対応**。
  デジ庁ガイドライン（テキストエリア／日付ピッカー／ラジオボタン／チェックボックスの各
  概要ページ、参照日 2026-08-18）から component-spec.json を新設し、
  does_not_exist_yet.components から削除、index.json を再生成（`npm run ci` OK）。
  - **副次的な発見（DatePicker）**: デジ庁のアクセシビリティページによると、
    生年月日等の**特定可能な既知の日付にはカレンダー UI を使わない**方針
    （`<select>` / `<input type="date">` も避け、年/月/日を分けた `input type="text"` +
    autocomplete 属性を使う）。DatePicker は「前後を見ながら選ぶ日付」専用と判明したため、
    InputText / Select の `never_use_when` を合わせて更新した。
    年/月/日分割入力の専用部品・パターンは第一弾未定義のまま（必要になれば別途起票）。
- **繰り返し行入力 → 部品として設計し直し、対応完了** — 明細行のように「複数行を
  追加していく」入力。list-page / form-page / detail-page / confirm-flow のいずれにも
  該当パターンが無く、form-page（1 カラム積み）でもカバーできない新規の穴だった。
  当初はパターン（`line-items-input` 仮称）として does_not_exist_yet.patterns に
  名前のみ登録したが、実際の適用先（form-page）を検討したところ、form-page の
  `components` は InputText / Select / Button / ModalDialog という**単体部品**の並びで
  Table のような画面レベルの構造物は含まれておらず、Table を暫定転用する案は
  form-page パターンの無断改変（許可外部品の追加＋ 1 カラム原則の逸脱）に当たると判明。
  再検討の結果、独立したページ型パターンではなく、**form-page 内で使う複合部品**
  （行の追加・削除・エラー表示の挙動を規定し、行の中身は呼び出し側が選ぶ）と
  再分類する方が構造的に妥当と判断し、`RepeatingFieldGroup` として
  component-spec.json を新設。`does_not_exist_yet.patterns` から `line-items-input` を削除し、
  form-page の `components` に `RepeatingFieldGroup` を追加。`npm run ci` OK。

ステータス: 部品 5 件（Textarea / DatePicker / RadioButton / Checkbox / RepeatingFieldGroup）
すべて spec 追加・昇格まで完了。パターンの新規追加・改変は無し。

### 2026-08-18: パターン 1 件（app-shell）

MK2（モック体裁レビュー）で「共通ヘッダー/ナビ枠が無い」との指摘。app-shell は
これまで「MK1 のモック体裁と合わせて要否判断」として保留し `does_not_exist_yet.patterns`
に登録していたが、MK2 で実需が確認されたため昇格に着手。

- **ナビゲーション形式**: 上部ヘッダー内に横並び Link（サイドバー型は Drawer 相当の
  未提供部品が必要になるため見送り。必要になれば別途起票）
- **パンくず**: Breadcrumb 部品は第一弾未提供のため部品化せず、list-page のページングと
  同様にレイアウト上のテキスト簡易表現で対応
- **ヘッダー**: スクロール中も画面上部に固定表示（sticky）。「スクロールが多い」という
  別指摘への対応も兼ねる

`patterns/app-shell/pattern.json` を新設し、`does_not_exist_yet.patterns` から
`app-shell` を削除。`npm run ci` OK。

ステータス: パターン 1 件（app-shell）新規追加・昇格完了。

### 2026-08-18: パターン 2 件改定（form-page / list-page の密度・横幅）

MK2 指摘「スクロールが多い・横幅を目いっぱい使いたい・業務システムは一画面の情報量を
優先したい」を受け、form-page / list-page の既存パターンを改定。

- **form-page**: 「1 カラムで垂直に積む」原則は維持しつつ、意味的に対をなす短い項目
  2 つ（例: 利用区間の発着、期間の開始/終了）に限り同一行への横並びを許容する例外を追加。
  3 項目以上の横並び・無関係な項目の横並び・Textarea 等長文入力の横並びは禁止のまま
  （`never_do` に明記）
- **list-page**: 行高密度を `md` → `sm` に変更し、一覧のスクロール量を削減

いずれもトークンは既存の `space.sm` / `space.md` の範囲内で対応でき、新規トークン追加は
不要だった。`npm run ci` OK。

ステータス: パターン改定 2 件（form-page / list-page）完了。

### 2026-08-18: トークン 1 件追加（必須表示用の色 `color.semantic.required`）

MK2 指摘「必須を黒色ではなく色を付けて分かるようにする」を受けて対応。
既存の semantic トークンは `primary`（主要アクション専用・1 画面原則 1 つ）と
`danger`（破壊的操作・エラー専用・強調目的で使わない）のみで、どちらも
必須表示への転用は各トークンの `$description` に反する。そのため新規に
別色相のトークンを追加した。

- primitive: `color.primitive.orange.600`（#ea580c）を追加
- semantic: `color.semantic.required`（primitive orange.600 のエイリアス）を追加。
  `$description` に「色のみに依存せずテキストラベルと併用する」ことを明記
- 適用先: InputText / Textarea の component-spec.json の a11y 記述に、
  「※必須」テキストを `color.semantic.required` で強調してよい旨を追記
  （テキスト自体を必ず表示する原則は維持 — 色だけで意味を伝えない）
- Select / DatePicker / RadioButton / Checkbox / RepeatingFieldGroup は
  「※必須」テキスト表記の作法自体が spec 未記載のままだったため今回は対象外
  （範囲外の既存ギャップとして別途起票候補）

`npm run generate:index -- --check` / `npm run audit` OK。
`npm run build:tokens`（tokens/dist/ 再生成）は今回未実行。第一弾（モック HTML 検証段階）では
トークン実値の移植・dist への反映は第二段（React 実装着手後）へ先送りの方針（GUIDE-for-designers.md
参照）のため、正の tokens.json 更新のみで完結しており、現時点では未実行のままで問題ない。

ステータス: トークン 1 件（color.semantic.required）追加完了。

### 2026-08-18: RepeatingFieldGroup にレイアウト推奨を追加（旅費明細まわり）

MK2 指摘「旅費明細はテーブルで表示が良い（今分かりにくい）」「旅費明細は基本一行で
表示した方がいい」を受けて対応。旅費明細は入力中の可変件数フォーム項目のため、
component-spec の `never_use_when` により Table への置き換えは不可（RepeatingFieldGroup
が正しい部品）。見た目をテーブルらしく・一行で見せたいという要望は、部品を差し替えず
行内レイアウトの推奨を明文化することで対応する方針とした。

- `RepeatingFieldGroup.component-spec.json` に `layout_guidance` フィールドを新設し、
  「同種の短い項目が並ぶ用途では列を揃えた横並び 1 行表示を推奨」「エラーで行が伸びても
  他行の列位置はずらさない」ことを明記（「エラー表示で段数がずれる」指摘にも対応）
- `anti_pattern_example` に縦積み表示のアンチパターンを追記

DS 側の対応はここまで。実際のモック（本リポジトリ外）側で本ガイダンスに沿って
RepeatingFieldGroup の行内実装を列整列に直す作業が別途必要。`npm run ci` OK。

ステータス: component-spec 1 件（RepeatingFieldGroup）にレイアウト推奨を追加完了。

### 2026-08-18: Table / Textarea にレイアウト推奨を追加

MK2 指摘の残り 2 件に対応。

- **「伝票一覧で基本改行しない」**: `Table.component-spec.json` に
  `text_overflow_guidance` を新設。セル内テキストは既定で折り返さず
  nowrap + ellipsis、業務上必須な列のみ個別に折り返し許容とした
- **「長文のテキストボックスを広げるときに横にも広げられた方がいい」**:
  `Textarea.component-spec.json` に `resize_guidance` を新設。縦方向は
  既定で許可、横方向は所属カラム幅を超えない範囲でのみ許可し
  form-page の 1 カラム原則と矛盾しないようにした

DS 側の対応はここまで。実装（本リポジトリ外のモック）側での反映が別途必要。
`npm run ci` OK。

ステータス: component-spec 2 件（Table / Textarea）にレイアウト推奨を追加完了。
MK2 指摘のうち DS 側で対応可能な項目はここで一巡。

### 2026-08-18: ブランドカラー #00a1ae の採用

brand-principles.md で「暫定・無ブランド運用」としていた状態から、ブランドカラー
#00a1ae の採用へ更新。適用前に白背景・白文字とのコントラスト比を確認したところ
約 3.13:1 で、通常サイズの文字に必要な WCAG AA 基準（4.5:1）を満たさないことが判明
（大きい文字・UI コンポーネント境界線の基準 3:1 は満たす）。

- `color.semantic.primary`（Button 背景等、文字を伴う操作要素に使用）は、
  #00a1ae を基準にコントラスト 4.5:1 以上になるよう暗めに調整した `#00818b` に変更。
  primitive `blue.600/700` は用途が無くなったため削除し `teal.600/700` に置き換え
- `color.semantic.brand`（新設）に #00a1ae をそのまま登録。文字を伴わない
  大面積・装飾用途（ヘッダー背景・ロゴ周り等）に限定する旨を `$description` に明記
- brand-principles.md のブランド資産セクションを更新

`npm run ci` OK。`tokens/dist/` への反映は他のトークン変更と同様、第二段（React 実装
着手後）で行う。

ステータス: ブランドカラー適用完了（primary 上書き + brand トークン新設）。

### 2026-08-24: mock-trial（travel-expense）検証の申し送り対応（チケット 1〜3 + 副次提案 A〜C）

mock-trial 側の起票下書き（別リポジトリ mock-trial の `ds-tickets-draft.md`
— デザイン担当者のローカルにあり、本リポジトリからは参照できない）を受けて対応。
チケット 1〜3 は選択肢をユーザーに確認のうえ決定、副次提案 A〜C は低コストで
他アプリの実装揺れを防げるため 3 件とも採用と判断した。

- **チケット 1（form-page の密度方針）**: 横並びの条件を「意味的に対をなす短い項目
  2 つまで」から「短い入力欄（InputText / Select / DatePicker / RadioButton / Checkbox）
  どうしであれば意味的関連を問わず 2 カラム許容」へ緩和（ユーザー決定: 選択肢 2）。
  意味的に対をなす項目を同じ行に揃えることは推奨として残す。3 カラム以上・
  Textarea 等長文入力の横並びは引き続き禁止（`never_do` 維持）
- **チケット 2（レスポンシブの土台）**: `breakpoint.sm/md/lg`（768/1024/1280px）を
  tokens.json に新設し、全 5 パターン（list-page / form-page / detail-page /
  confirm-flow / app-shell）に `responsive` フィールドを新設してレスポンシブ時の
  レイアウト方針を追記（ユーザー決定: トークン新設 + 各パターン方針追記）。
  form-page の 2 カラムは breakpoint.md 以上でのみ許容。app-shell のナビ折りたたみは
  Drawer 相当の未提供部品が必要なため折り返し表示とした（必要になれば別途起票）。
  breakpoint.sm 未満（モバイル）は主対象外と明記
- **チケット 3（必須表示の色）**: `color.semantic.required` をオレンジ（orange.600
  #ea580c）から赤系の `rose.600`（#e11d48・新設）へ変更（ユーザー決定: danger と
  別トーンの赤系新設）。「必須は赤」という一般的 Web 慣習に寄せつつ、エラー用
  danger（red.600 #dc2626）とは別トーンにして意味の混同を回避する意図を
  `$description` に明文化。白背景とのコントラスト比約 4.7:1（AA 4.5:1 充足）を確認。
  orange.600 は参照が無くなったため削除（blue.600/700 削除時と同じ運用）
- **副次提案 A（採用）**: RepeatingFieldGroup の `a11y` に、見出し行を伴うテーブル状
  レイアウト時の実装手法（見出し行は aria-hidden、各行に視覚的に隠したラベルを残す —
  clip-path:inset(50%) 相当、display:none 不可）を追記
- **副次提案 B（採用）**: InputText / Select / DatePicker に `implementation_notes`
  フィールドを新設し、Grid / Flexbox コンテナ内では `min-width: 0` を指定する旨を追記
  （CSS 初期値 min-width: auto によるはみ出しの既知問題。mock-trial で実際に発生）
- **副次提案 C（採用）**: Badge の `never_use_when` に「枠線付きの見た目にしない
  （常に単色塗り・枠線なし）」を追加し、`confusable_with.Button` にも視覚面の
  差別化ルールを追記（mock-trial で「ボタンと誤認しやすい」指摘があったため）
- **運用メモ（記録のみ）**: DS タグ配布のタイミング（部品・パターン追加後は速やかに
  タグを切る）は v0.0.3 以降すでに都度配布で運用改善済み — 申し送りとして記録

`tokens/dist/` への反映は従来どおり第二段で行う。DS 側の対応はここまで。
チケット 1〜3 はいずれもモックの見た目に影響するため、mock-trial 側での再生成が別途必要
（2 カラム化の適用・breakpoint 対応・必須表示色の変更）。

ステータス: パターン改定 5 件（responsive 追加、form-page は横並び条件も緩和）+
トークン追加 4 件（breakpoint 3 + rose.600）・変更 1 件（required）・削除 1 件（orange.600）+
component-spec 追記 5 件（RepeatingFieldGroup / Badge / InputText / Select / DatePicker）完了。

### 2026-08-24: 業務システム対応のギャップ棚卸し（起票のみ — 実装・仕様変更なし）

「業務システムを対応するにあたって足りない内容」の観点で現行カタログ
（部品 13 / パターン 5 / does_not_exist_yet）を棚卸しし、不足 16 件を
`tickets/2026-08-24-business-system-gaps.md` に一括起票した。AGENTS.md の
ハード制約に従い、本件では部品・パターン・トークンの追加/変更は一切行っていない。

- **高優先 5 件（GAP-01〜05）**: 保存成功フィードバック（Toast/NotificationBanner）/
  Combobox / FileUpload / error-page パターン / Table 行選択＋一括操作の作法
- **中優先 5 件（GAP-06〜10）**: Pagination 部品昇格 / advanced-search /
  Tabs・Accordion / login / print-preview・report
- **カタログ未登録の穴 5 件（GAP-11〜15）**: Skeleton 仕様の不在（states が参照する
  のに実現手段が未定義）/ 金額・数値入力の作法 / 年月日分割入力（DatePicker 禁止
  ケースの受け皿）/ Table 行操作列＋IconButton / 「※必須」表記作法の 5 部品への展開
  （GAP-13・15 は過去ログで「別途起票候補」としていた保留の正式化）
- **追加起票 1 件（GAP-16、同日追記）**: approval パターン。MK2 レビューの
  「承認機能は当面実装しない」は当時のお題（travel-expense）前提の判断であり、
  承認フローを持つ別お題を対応する可能性が出てきたため、当初の「起票対象外・
  記録のみ」から正式起票へ切り替えた

ステータス: 起票 16 件完了。採否・優先順位の確定は人間判断待ち。

### 2026-08-25: 業務システムギャップ起票の DS 反映（カタログ登録 + 検討方針の記録）

上記起票（`tickets/2026-08-24-business-system-gaps.md`）のうち、人間判断を要しない
帳簿的な反映のみを実施した。部品・パターン・トークンの追加/変更は引き続き行っていない。

- **検討方針の記録（2026-08-24 決定・全 GAP 共通）**: 各 GAP の対応は
  **基本デジタル庁デザインシステム（DADS）に則る**。まずデジ庁に対応する部品・
  パターン・ガイドラインが無いか確認し、あればそれを採取する。デジ庁に該当が無い・
  ガイドライン準備中の場合は、独断で自社翻案を確定せず、適切な方針案を人間に提案し
  承認を得て決める（決定の経緯は本ファイルに記録する）。これは既存の
  「土台 DS: デジタル庁デザインシステム」方針（採取方式・自社翻案は source に明記）の
  ギャップ対応への適用にあたる
- **does_not_exist_yet へ 3 件追記（捏造防止の名前のみ登録 — 採否の決定ではない）**:
  - `Skeleton`（GAP-11。list-page / form-page の states が既に参照しているのに
    実現手段が未定義という矛盾状態の解消は人間判断待ちだが、登録が無いと
    実装側の自作を止められないため先行登録）
  - `InputNumber`（GAP-12。金額・数値入力。InputText の拡張で足りる可能性あり —
    その場合は登録名のまま「作らない」判断で閉じる）
  - `DateFieldSet`（GAP-13。年/月/日分割入力。form-page ガイダンスで足りる可能性あり —
    同上）
  - GAP-14 の「Table 行操作列の作法」は部品名ではないため登録対象外
    （IconButton は登録済み）。GAP-01〜10・16 の関連名
    （Toast / NotificationBanner / Combobox / FileUpload / Pagination / Tabs /
    Accordion / error-page / advanced-search / login / print-preview / report /
    approval / inbox）はすべて登録済みであることを確認
- `scripts/generate-index.mjs` を更新し index.json を再生成（`npm run ci` OK）

ステータス: カタログ登録 3 件 + 方針記録完了。各 GAP の採否・優先順位・具体案は
引き続き人間判断待ち（確定後、上記検討方針に沿って対応する）。

### 2026-08-25: 業務システムギャップの実質対応に着手（デジ庁調査 → 採取 3 件 + 提案 13 件）

ユーザー指示「各 GAP の実質的な対応を進めたい」を受け、検討方針どおり全 16 GAP について
デジ庁 DADS（v2.17.1・コンポーネント 48 件、参照日 2026-08-25）の該当有無を調査した。
調査結果と対応案は `tickets/2026-08-25-business-system-gaps-proposal.md` に集約。

- **調査で判明した主な事実**:
  - デジ庁には**テンプレート / パターンの章そのものが無い**（error-page / login / report /
    approval / advanced-search はいずれもデジ庁側に該当無し → 自社定義が必要）
  - **公開済み**で採取できるもの: ファイルアップロード / ノティフィケーションバナー /
    アコーディオン / ディスクロージャー / テーブルの行選択・全選択・indeterminate /
    要否ラベルの作法 / 日付ピッカーの分割入力（既知日付はカレンダーボタン無しの同一部品）
  - **ガイドライン準備中**（実装または Figma のみ）: コンボボックス（Figma のみ・仕様非公開）/
    タブ / ページナビゲーション / プログレスインジケーター / テーブルコントロール
  - **存在しないもの**: Toast / Skeleton / IconButton / エラーページ / 印刷ガイドライン /
    数値・金額入力の作法。デジ庁は動的通知の読み上げに慎重（NotificationBanner に
    aria-live を付けない、role=alert 不使用）
  - ページナビゲーションの現行 v2 実装は「前へ / 次へ + カウンター」のみで番号リストが無く、
    現行 list-page の簡易構成とほぼ一致（番号付きは旧 v1 のみ）
- **採取して着手済み（デジ庁公開済み・承認不要）**:
  - **GAP-03**: `FileUpload` component-spec 新設。form-page の components に追加、
    does_not_exist_yet から除外。アップロード進行はデジ庁でも未定義（部品の責務は選択まで）
    のため form-page の submitting で表す方針を spec に明記。ファイル選択結果の aria-live 使用は
    InputText の原則の例外としてデジ庁実装に準拠
  - **GAP-05 前半**: Table spec に行選択作法（`row_selection_guidance`）・揃え方
    （`alignment_guidance`: 数値・日付は右揃え）・「行全体をクリック可能にしない」・
    Checkbox の aria 属性を追記。全ページ選択は非対応と明記。選択行ハイライトは専用トークン
    未登録のため暫定 surface（第二段で淡色トークン検討）
  - **GAP-15**: Select / DatePicker / RadioButton / Checkbox / RepeatingFieldGroup の a11y に
    要否表示の作法を展開。デジ庁準拠で「※任意」は text-subtle、required / aria-required は
    使わず可視テキスト + 送信時 aria-invalid。グループ部品は legend に 1 回付す等の
    部品特有の差分を反映。InputText / Textarea にも同内容を補記
- **提案のみ（要承認・13 件）**: GAP-01 / 02 / 04 / 05 後半 / 06 / 07 / 08 / 09 / 10 / 11 / 12 / 13 /
  14 / 16。トークン追加 5 件（success / warning / info / skeleton / print.margin）を含む。
  詳細は上記提案書
- **ユーザー回答（2026-08-25）**: GAP-09 = ID / パスワード型ログイン画面あり、GAP-10 = 印刷要件あり、
  GAP-16 = approval（detail-page variant）+ inbox まで対象 — 提案に反映済み

`npm run ci` OK（部品 14 件 / パターン 5 件）。

ステータス: 採取 3 件（spec 新設 1 + spec 追記 8 + パターン改定 1）完了。13 件は承認待ち。

### 2026-08-25: GAP-01 保存成功フィードバック — 承認を受けて対応（NotificationBanner 新設 / Toast 不採用）

提案書 GAP-01 の推奨案をユーザーが承認（2026-08-25）。以下を実施した。

- **判断の経緯**: デジ庁にはノティフィケーションバナー（公開済み）があり Toast 相当は無い。
  デジ庁の設計は「aria-live / role=alert を付けない」「自動消滅の規定なし」で、動的通知の
  読み上げに慎重な姿勢。自動消滅する通知は読み終える前に消える・支援技術に伝わらない
  問題があるため、**Toast は作らず NotificationBanner に一本化**した（Toast は
  does_not_exist_yet に残し、NotificationBanner の confusable_with で誘導）
- **トークン 3 件追加（暫定値）**: `color.semantic.success`（green.700 #15803d、約 5.1:1）/
  `warning`（amber.600 #d97706、約 3.2:1 — 文字色には使わない旨を $description に明記）/
  `info`（blue.700 #1d4ed8、約 6.3:1。primary と別色相で押せる要素と混同させない）。
  第二段でデジ庁 `--color-semantic-success-2` / `warning-yellow-2` / キーカラー系へ移植
  （トークン対応表に行を追加）
- **NotificationBanner spec 新設**: type = success / error / warning / info（デジ庁の
  info-1 / info-2 は info に統合）、style = standard のみ（color-chip は不採用）。
  アイコン + タイトル必須、アクション Button は secondary 最大 2、閉じるは追従表示時に必須。
  a11y はデジ庁準拠で aria-live 無し、動的挿入時のタイトルへのフォーカス移動のみ自社翻案
- **パターン改定 3 件**: form-page に `save-success`（保存後に表示する画面の本体先頭に
  type=success。遷移先はアプリ側判断。自動消滅させない）と `save-error`（処理失敗は
  type=error、入力は保持）を新設、never_do に Toast 的表示を追加。detail-page / list-page に
  `notice`（操作結果・告知の配置 = ページヘッダ直下。取得失敗の error 状態はバナーにしない）
  を新設。3 パターンの components に NotificationBanner を追加
- **周辺更新**: ModalDialog の confusable_with から「第一弾未提供」を除去。brand-principles.md の
  文言トーンに「操作完了の通知: 結果を短く言い切る（保存しました）」を追加

`npm run ci` OK（部品 15 件 / パターン 5 件）。`tokens/dist/` への反映は従来どおり第二段。

ステータス: GAP-01 完了（トークン 3 + spec 新設 1 + パターン改定 3 + 周辺 2）。

### 2026-08-25: GAP-02 Combobox — 承認を受けて自社翻案で新設

- **判断の経緯**: デジ庁にコンボボックスのページはあるが**ガイドライン準備中**で Figma のみ
  （2026-04-15 v2.13.0 初版。HTML / React 実装は提供予定・用途や a11y は非公開）。
  検討方針「準備中なら独断せず提案 → 承認」に従い提案し、ユーザー承認（2026-08-25）。
  ModalDialog と同じ扱いで **WAI-ARIA APG の Combobox（Editable Combobox With List
  Autocomplete）に基づく自社翻案**とし、source に「公開後に突合」を明記
- **Select との境界（自社判断）**: 全件を眺めて選べる目安 6〜30 件 → Select、30 件超または
  名称・コードで探すマスタ参照 → Combobox。デジ庁のセレクトボックス方針「長いリストは
  事前の質問で選択肢を減らせないか検討」も併記。Select の purpose / never_use_when /
  confusable_with、InputText の confusable_with を更新
- **責務境界**: 候補の取得（API・絞り込みロジック・debounce）はアプリ側。部品は候補配列・
  loading・選択値を受け取って表示する。第一弾は単一選択・候補からの選択のみ
  （自由入力許容型・複数選択型は未提供 — 必要になれば起票）
- **a11y**: role=combobox + aria-autocomplete=list + aria-expanded / controls /
  activedescendant、候補は listbox / option。候補件数の変化は role=status（polite）で伝え、
  role=alert は使わない（デジ庁の読み上げ姿勢を踏襲）。エラーは送信時にまとめて
- form-page の components と横並び許容の短い入力欄に Combobox を追加

`npm run ci` OK（部品 16 件）。

### 2026-08-25: GAP-04 error-page — 承認を受けてパターン新設

- **判断の経緯**: デジ庁にはテンプレート / パターンの章そのものが無く、エラーページの
  型・文言ガイドラインも存在しない（2026-08-25 確認）。自社定義として提案し承認
- **構成**: variant = 403 / 404 / 500 / maintenance。403 / 404 / 500 は **app-shell の内側**
  （ナビで復帰できる）、maintenance は**シェル無し**。本体 = 見出し（何が起きたか 1 文）→
  説明 1〜2 文 → 復帰アクション 1 つ（Link appearance=button。500 のみ「再試行」Button
  primary + 補助 Link）→ 補助情報（エラーコード・時刻・問い合わせ先・参照番号）
- **セッションタイムアウトは error-page にしない**: login パターンへ遷移し NotificationBanner
  type=info で伝える方針（login は GAP-09 承認待ち。昇格時に整合を確認）
- **EmptyState は転用しない**（spec でエラー状態の代用を禁止済み）。Link / Button のみで
  組めるため部品追加なし。文言は brand-principles.md（復帰手段を先に、詫びは短く）
- app-shell の use_when に error-page（403 / 404 / 500）を追加。does_not_exist_yet.patterns
  から error-page を除外

### 2026-08-25: GAP-05 後半 一括操作 — 承認を受けて list-page 改定

- **判断の経緯**: 行選択・全選択はデジ庁公開済み（前半で採取済み）だが、一括操作の UI は
  「テーブルコントロール」が担う想定で**ガイドライン準備中**。自社翻案として提案し承認
- **選択アクションバー**: 行選択を使う一覧で 1 行以上選択時のみ、フィルタ行と Table の間に
  出現。「n 件を選択中」+ 一括操作 Button secondary（最大 3）+「選択を解除」。破壊的操作は
  danger + ModalDialog で件数を明記して確認
- **「主アクション 1 つまで」との整合**: 一括操作は secondary / danger のみで primary を
  使わない → 既存ルールを維持したまま配置場所を確保（never_do に明記）
- **選択の範囲**: 表示中ページ内に限る（全ページ選択は非対応 — Table spec と整合）。
  ページ移動・再検索・並び替えで選択解除。完了 / 一部失敗は notice 状態の
  NotificationBanner で件数を含めて伝える（GAP-01 に依存）
- list-page の components に Checkbox / ModalDialog を追加、states に rows-selected /
  bulk-action-done を新設

`npm run ci` OK（部品 16 件 / パターン 6 件）。

### 2026-08-25: GAP-06 Pagination — 提案を保留（ユーザー指示: 自社定義を後日相談）

提案は「デジ庁 v2 実装が前へ / 次へ + カウンターのみのため専用部品化を見送り、list-page の
簡易構成をデジ庁 v2 の作法に揃える」だったが、ユーザーより「方針は納得だが、番号ジャンプ等が
どうしても必要な場面があるため **Pagination 部品を自社定義しておきたい**。後日相談」との
回答（2026-08-25）。**見送り案は取り下げ、部品の自社定義を前提に保留**。list-page の
ページング規定の改定も、部品設計と整合させるため部品化の相談時に併せて行う。
Pagination / PageNavigation は does_not_exist_yet に残したまま。

ステータス: GAP-01 / 02 / 04 / 05 完了。GAP-06 保留（後日相談）。

### 2026-08-25: GAP-07 / 08 / 09 / 10 / 11 / 12 / 14 / 16 — 承認を受けて一括対応

いずれも提案書の推奨案どおりユーザー承認（2026-08-25。GAP-09 は「パスワード表示切替あり」の
条件付き）。判断の経緯と差分を GAP ごとに記録する。

- **GAP-07 advanced-search → list-page 拡張 + Disclosure 採取**: デジ庁に詳細検索のパターンは
  無いが、検索ボックス実装の「詳細検索パネル」（details / summary の折りたたみ + 下部に
  検索 / 条件をクリア）と**公開済みのディスクロージャー**が使えると判断。独立パターンにせず
  list-page のフィルタ行に「詳細検索」Disclosure トグルを追加し、展開時の条件パネル
  （form-page の項目作法・2 カラム許容）、「検索」「条件をクリア」Button は secondary
  （primary は主アクション用に温存）、適用中条件のテキスト要約（チップ部品はデジ庁も
  準備中のため使わない）、filters-applied / filter-empty 状態を規定。
  `Disclosure` component-spec を新設（デジ庁公開済みから採取。a11y は details / summary 推奨 +
  カスタム時 aria-expanded の自社翻案）。advanced-search は does_not_exist_yet から除外し
  「list-page で提供」と明記
- **GAP-08 Tabs 新設（自社翻案）/ Accordion 見送り**: タブはデジ庁ガイドライン準備中だが、
  実装 3 型のうち「矢印キー型・APG 準拠（ウェブアプリ・管理画面で使用）」が業務画面に合致する
  ため、そのキーボード操作・ARIA 属性・activation 既定 auto を採取し、用途・禁止事項・見た目は
  WAI-ARIA APG に基づく自社翻案で `Tabs` spec を新設。選択中タブの下線は primary ではなく
  text（primary は主要アクション専用）。detail-page の関連情報セクションの「タブ」を Tabs に
  紐付け。**Accordion は見送り**: デジ庁アコーディオンは公開済みだが「同種セクションの連続
  （FAQ 等）」用で「スペース節約目的で使わない・重要情報を隠さない・テーブルを入れない」と
  明記されており、業務の詳細画面の情報分割には不適合。does_not_exist_yet に残し理由を注記
- **GAP-09 login 新設**: デジ庁にログイン画面のパターンは無し。ID / パスワード型・
  パスワード表示切替あり（ユーザー回答）で `login` pattern を新設。**app-shell の外側に置く
  初のシェル無しパターン**（error-page の maintenance と同列。app-shell の use_when に明記）。
  認証失敗は NotificationBanner type=error でどちらが誤りか特定しない、セッションタイムアウトは
  type=info（error-page の方針と整合）、パスワード表示切替はテキストラベル付き Button +
  aria-pressed（自社翻案。IconButton は不採用のためアイコンのみにしない）。フォーム作法は
  デジ庁インプットテキストに準拠（maxlength・コピー禁止・自動入力抑止は不可）
- **GAP-10 report 新設 / print-preview 見送り**: デジ庁に印刷・帳票のガイドライン・トークンは
  無し（design-tokens は Color / Typography / Size のみ）。印刷要件あり（ユーザー回答）のため
  `report` pattern を自社定義で新設: シェル無し、portrait / landscape、帳票ヘッダ（帳票名・
  出力日時・ページ番号を各ページで繰り返し）、本体は dl + Table（ellipsis 解除・thead 繰り返し・
  行の途中で改ページしない）、ステータスは Badge を使わずテキスト、画面表示時のみ「印刷」
  Button。**print-preview は見送り**（ブラウザの印刷プレビューに委ねる。does_not_exist_yet に
  残す）。トークン `print.margin`（15mm・暫定）を新設
- **GAP-11 Skeleton 部品化**: デジ庁にスケルトン相当は無し。プログレスインジケーター
  （準備中・実装のみ）から読み上げ作法（role=status polite「読み込み中です」）と
  prefers-reduced-motion での停止を採取して踏襲し、`Skeleton` spec を自社定義で新設。
  ガイダンスでなく部品にした理由: 各パターンの states が既に参照しており、index.json
  未登録のまま実装すると audit-components が捏造扱いするため。トークン
  `color.semantic.skeleton`（gray.200 のエイリアス。border と同値だが意味を分けて別名）を新設。
  list-page / form-page / detail-page / report の loading と EmptyState の参照を「Skeleton 部品」に
  書き換え、3 パターンの components に追加。「スピナー単体禁止」は維持
- **GAP-12 数値入力 → InputText ガイダンス / InputNumber 不採用**: デジ庁に数値入力の作法は
  無いが、インプットテキストの「文字種を限定しない・変換は送信時または確認画面表示時・
  maxlength 不可・幅は内容相応・単位の添え方」と日付ピッカー実装の `type=text
  inputmode=numeric` を組み合わせて `numeric_input_guidance` を InputText に新設。type=number
  不可・入力中の書き換え不可を never_use_when に追加。表示側は 3 桁区切り + 単位。InputNumber は
  「作らない」と決定し、捏造防止のため名前は does_not_exist_yet に残す
- **GAP-14 行操作列を設けない / IconButton 不採用**: デジ庁に行操作列の作法・IconButton は
  無く、「アイコンは必ずラベルと組み合わせる」（基本デザイン アイコン a11y Rev001 2025-07-30）
  が原則。チケット案 1 を採用し、Table の never_use_when に「行ごとの操作ボタン列」を追加、
  list-page に「主キー列 Link → detail-page で操作。複数行は一括操作」を明記。Button の
  confusable_with に IconButton 不採用を記載。IconButton は名前のみ does_not_exist_yet に残す
- **GAP-16 approval / inbox 新設**: デジ庁に承認業務のパターンは無し（チップラベルも準備中の
  まま）。ユーザー回答（承認画面 = detail-page variant、inbox まで対象）に従い、
  `approval`（detail-page 準拠: ヘッダ操作を承認 primary + 差戻し secondary に置換、承認履歴
  Table、ModalDialog + Textarea で確定〔差戻し理由 ※必須・danger にしない〕、承認不可時は
  Button 非表示）と `inbox`（list-page 準拠: 既定条件 = 自分の承認待ち、主アクション無し、
  一括承認のみ〔一括差戻しは提供しない〕、申請番号 Link → approval）を**独立 pattern.json**
  として新設（index.json での発見性のため。中身は既存パターン準拠 + 差分の記述）。
  MK2 の「承認機能は当面実装しない」は travel-expense 限定の判断であり、本パターンは別お題
  向けの型として追加

`npm run ci` OK（部品 19 件 / パターン 10 件）。`tokens/dist/` への反映は従来どおり第二段。

ステータス: GAP-01 / 02 / 03 / 04 / 05 / 07 / 08 / 09 / 10 / 11 / 12 / 14 / 15 / 16 完了。

### 2026-08-25: GAP-13 年/月/日分割入力 — 承認を受けて DatePicker spec を拡張（DateFieldSet 不採用）

- **判断の経緯**: デジ庁の日付ピッカーは年月日 3 分割の `input type="text"` の複合部品で、
  使い方ページに「特定可能な既知の日付にはカレンダーボタンを置かない」と明記されている
  （= 同じ部品をカレンダー無しで使う）。従来の自社 spec は「既知の日付には DatePicker を
  使わない」としており、正しい実現手段が未定義の矛盾状態だった。ユーザーに「既知日付」の
  定義（入力前から決まっていて、記憶や手元の書類からそのまま打ち込める日付 — 生年月日・
  経歴年月・有効期限・契約日・伝票の日付。対して開催日・宿泊期間・出張予定日は前後を見て
  決める日付）を説明のうえ承認を得た（2026-08-25）
- **変更**: DatePicker の purpose を「年 / 月 / 日を分けたテキスト入力による日付入力。
  前後を見ながら選ぶ日付にのみカレンダーボタンを付ける」に改め、`variants.calendar`
  （false 既定 / true）と `variants.layout`（Consolidated / Separated・年月のみ・月日のみ）を
  新設。never_use_when を「既知の日付に calendar=true を使わない」に書き換え。autocomplete
  （bday-* / cc-exp-*）はアプリ側が付与する旨、半角化・ゼロ埋めは送信時または確認時、
  和暦は未対応（デジ庁も今後対応予定 — 表示側で併記）を明記
- **周辺更新**: InputText の never_use_when / confusable_with と Select の never_use_when の
  日付に関する参照先を「DatePicker calendar=false / true」に変更。**DateFieldSet は作らない**
  と決定し、捏造防止のため名前は does_not_exist_yet に残す

`npm run ci` OK（部品 19 件 / パターン 10 件）。

ステータス: 業務システム対応ギャップ 16 件のうち **15 件完了**（GAP-01〜05 / 07〜16）。

### 2026-08-25: GAP-06 Pagination — 保留を解除し自社定義で新設

- **判断の経緯**: 当初提案は「デジ庁 v2 実装が前へ / 次へ + カウンターのみのため部品化見送り」
  だったが、ユーザーより「番号ジャンプ等がどうしても必要な場面があるため自社定義したい」との
  指示で保留にしていた。同日、自社定義案（下記）を提示し、3 つの判断点 — (a) simple /
  numbered の 2 variant 構成・番号は現在 ±2 の最大 5 個、(b) 切り替え目安「総ページ数 6 以上
  で numbered」、(c) 表示件数の切替は第一弾では含めない — をすべて承認
- **spec の構成**: `Pagination` を新設。variant=simple はデジ庁 v2 HTML 実装の作法を採取
  （総ページ数 1 なら非出力、端では disabled ではなく非出力、nav の aria-label は文脈名、
  URL が変わるなら Link・変わらないなら Button）。variant=numbered は旧 v1 React 実装
  （先頭 / 前へ / 番号 / 次へ / 末尾、aria-current=page、モバイルは番号非表示）を参考にした
  自社翻案で、番号は現在 ±2 に調整し、ラベルは aria-label でなく可視テキスト（IconButton
  不採用と整合）。ページ移動後は Table の caption / 見出しへフォーカスを移して位置の変化を
  伝える（aria-live は使わない）。表示件数の切替 UI は非提供（デジ庁テーブルコントロール
  〔準備中〕の担当 — 必要になれば起票）
- **list-page 改定**: ページング欄を簡易構成から Pagination 部品に差し替え（総ページ数で
  variant を選ぶ）、`page-changed` 状態を新設、never_do に無限スクロール・総ページ数 1 での
  表示・端での disabled を追加。inbox は list-page 準拠のため自動的に適用
- **カタログ**: Pagination を does_not_exist_yet から除外。PageNavigation はデジ庁名の英訳で
  同一物のため捏造防止に残し、Pagination spec の confusable_with で誘導

`npm run ci` OK（部品 20 件 / パターン 10 件）。

ステータス: 業務システム対応ギャップ **16 件すべて完了**。does_not_exist_yet に残る名前の
うち Toast / Accordion / IconButton / InputNumber / DateFieldSet / PageNavigation /
print-preview は「作らない・見送り・別名」と決定済み（各 spec の confusable_with と
generate-index.mjs のコメント参照）。

### 2026-08-25: REQ-03 部品の色役割トークン — 承認を受けて対応

mock-trial デザインレビューの要望 9 件（`tickets/2026-08-25-density-and-layout-requests.md`）のうち
REQ-03「部品ごとに必要な色トークンの不足」を、推奨案 1〜4・判断点 (a)〜(d) すべて承認どおりに対応した
（他の REQ は並行対応中のため本節では触れない）。

- **判断の経緯**: モック側で `white` キーワード直書き 7 か所・Badge 背景に border 流用・disabled を
  opacity で代用・ModalDialog 遮蔽を text + opacity で代用、といった「役割トークンが無いための代用」が
  積み重なっていた。デジ庁 design-tokens の semantic 色は Error / Success / Warning / Key の 4 系統のみで
  面・文字・hover・disabled の役割トークンは存在しないため、体系は**自社設計**（暫定値は既存と同じ
  Tailwind 系プリミティブ、第二段でデジ庁プリミティブへ移植）
- **トークン 14 件追加（semantic）**: `on-primary`（white）/ `background`（white。**surface = gray.50 は
  「一段沈んだ面」として役割分離** — surface の $description にも追記）/ `surface-hover`（gray.100）/
  `primary-subtle`（teal.50 = **#e6f6f7。本 DS の teal はブランド #00a1ae 基準の自社色相で Tailwind teal と
  別物のため、Tailwind teal-50 ではなく brand を白で 90% 希釈した 10% ティントを 50 段として自分で選定**）/
  `danger-hover`（red.700）/ `danger-subtle` / `success-subtle` / `warning-subtle` / `info-subtle`
  （各色相の 50 段）/ `neutral-subtle`（gray.200。border と同値・別名 — skeleton と同じ運用）/
  `disabled-text`（gray.400）/ `disabled-surface`（gray.100。surface-hover と同値・別名）/
  `focus`（**primitive teal.600 を直接参照** — semantic → semantic の参照はファイル内の慣例に無く、
  Style Dictionary での解決も第二段まで検証できないため。$description に「primary と同値のエイリアス」と
  明記。第二段でデジ庁実装のフォーカス色へ）/ `overlay`（**hex8 `#11182780`** = gray.900 α50%。DTCG の
  color は hex8 で不透明度を表現できるため primitive を参照せず直接値。primitive 層に alpha 段は設けない）。
  primitive 層に white / gray.100・400 / red.50・700 / green.50 / amber.50 / blue.50 / teal.50 の 9 段を追加
- **`tokens/ROLE-MAP.md` 新設**: 「部品・箇所 → 必要な色の役割 → semantic トークン」の唯一の対応表
  （面 / 文字 / 罫線・フォーカス / 部品別早見表: Button・Badge・Table・NotificationBanner・ModalDialog・
  エラーサマリー・入力欄・app-shell ヘッダ）。新しい色が必要になったらまず本表を確認し、無ければ起票
- **Badge spec**: `variants.color`（neutral / primary / danger / success / warning。背景 = 各 `*-subtle`、
  文字 = 各 semantic 色、warning のみ文字は text）と `how_to_choose`（状態の意味 → color）を新設。
  枠線なし維持、塗りチップ禁止、info 系 color は設けない（案内は NotificationBanner）。チップラベルは
  デジ庁準備中のため自社定義で先行、公開後に名寄せ（source.note）
- **Button spec**: `color_map`（primary / secondary / danger × default / hover / disabled / focus）を新設。
  根拠はデジ庁ボタンの「塗り = キーカラー + 白文字 / アウトライン = 白背景 + キーカラー枠線・文字、
  hover は濃くなる + 下線」。disabled の opacity 代用を never_use_when に追加
- **Table / NotificationBanner / ModalDialog spec**: 選択行 = `primary-subtle`（GAP-05 の暫定 surface を
  解消）・行 hover = `surface-hover` / type 別背景 = 各 `*-subtle` / オーバーレイ = `overlay` を追記。
  form-page の input-error（エラーサマリー背景 = `danger-subtle`）は REQ-05 / 08 の form-page 改定と
  合わせて反映するため今回は pattern.json を触らず ROLE-MAP.md に記載のみ
- **audit-tokens.mjs 強化**: CSS 色キーワード（white / black / red / gray ... 主要な named color）を
  **CSS の値位置に限定**して検出（`: 〜 値` が `;` `}` 行末で終わる区間のみ。`{` を含む区間 = セレクタ側、
  クラス名 `.bg-white`、コメント、カスタムプロパティ名 `--color-white:`、`var(--...)` の変数名、
  URL / ファイル名 `/white.png` は誤検出しない）。transparent / currentColor / inherit は許容。
  `rgb() / rgba() / hsl() / hsla()`（+ hwb / lab / lch / oklab / oklch）の色関数も検出。
  fixture（NG 11 件 / OK 12 件）で確認、DS リポジトリ自身は exit 0
- **コントラストの既知課題 → 同日前倒しで解消**: 当初案（Badge の文字 = 600 段の primary / danger）では
  primary × primary-subtle 約 4.2:1、danger × danger-subtle 約 4.4:1 で **AA 4.5:1 をわずかに下回った**
  （primary は白背景でも 4.65:1 のため淡色面では原理的に届かない）。第二段送りかを確認したところ
  ユーザーから「前倒してよい」（2026-08-25）→ **淡色面上の文字専用トークン `on-primary-subtle`
  （teal.700・約 5.8:1）/ `on-danger-subtle`（red.700・約 5.9:1）を追加**して解消。hover 用の
  primary-hover / danger-hover と同じ primitive だが役割が異なるため別名（skeleton / neutral-subtle と同じ運用）。
  success は success-subtle 上で 4.8:1 を満たすため専用トークンは作らない。form-page エラーサマリーの
  見出し（danger-subtle 上）も on-danger-subtle に揃えた。Badge spec の a11y から既知課題の記述を除去し、
  全 variant が AA を満たす旨に更新

`npm run ci` OK。`tokens/dist/` への反映は従来どおり第二段。モック側は v0.0.5 で再生成が必要
（white 直書きの置換・Badge 色 variant・Button 状態色・バナー背景・オーバーレイ）。

ステータス: REQ-03 完了（トークン 16 + primitive 9 / ROLE-MAP.md 新設 / spec 5 件 / audit 強化。既知課題なし）。

### 2026-08-24: 静的 HTML 検証（第一弾）の再現範囲を明確化（方針決定）

第二段（React 実装 + トークン実値移植 + tokens/dist 生成）未着手の現状において、
静的 HTML モックで再現するのは **tokens.json の実値に基づく色・余白・レイアウトの
見た目のみ**とする前提をユーザー決定として確定した。

- **第一弾で保証する**: 画面の型（パターン準拠）・密度・部品選定・色・余白・レイアウト
- **第一弾で保証しない（第二段の対象）**:
  - 状態表現の挙動（focus / loading / エラー表示等の動的な振る舞い、aria 属性の網羅）
  - 最終確定色（text / text-subtle / border / surface 等はデジ庁プリミティブ移植待ちの
    暫定値 — トークン対応表参照。第二段で色が変わりうる）
  - 複数アプリ間の一貫した再現（部品実装が無いため各モックの手組みに依存する）
- **運用への含意**: モックへのレビュー指摘は「見た目（第一弾で対応可）」と
  「挙動・一貫性（第二段送り）」に仕分けて扱う

ステータス: 方針決定を記録（仕様変更なし）。

### 2026-08-24: ブランドヒアリング工程の定義を受けた整合対応

ブランドヒアリング工程がワークスペース側 `docs/DS-GUIDE.md` §2-4 として正式定義された
（フェーズ 0 の工程 0 / 2A で 1 回実施・質問 5 件と回答の落とし先・実施タイミングは
モック A/B テストの B アーム生成前・第一弾縮退の例外としてブランド色のみ実値化）。
これを受け、DS 側の記述をヒアリング定義と整合させた。

- **位置づけの変更**: 2026-08-18 に採用したブランドカラー #00a1ae（primary #00818b /
  brand）は「確定」ではなく**ヒアリング前の先行適用 = 暫定値**に位置づけ直し。
  ヒアリング（質問 1 / 2）の回答で確定または置き換えられる
- **brand-principles.md**: 冒頭に 2026-08-24 追記を追加し、「ブランド資産」節に
  暫定である旨とヒアリング落とし先（質問 2: ロゴ・既存ブランドガイドの確認項目）を明記。
  「文言トーン」（質問 3）「禁止リスト」（質問 4）も回答受領時に更新する旨を記載
- **tokens.json**: `color.semantic.primary` / `brand` の `$description` に
  「ヒアリングで確定するまでの暫定値」を追記（値の変更はなし。エージェントが
  読む説明文にも暫定であることが伝わるようにする趣旨）
- **確認結果**: ヒアリング質問リストの落とし先（tokens.json semantic 層 /
  brand-principles.md の 3 節 / DECISIONS.md メモ）はいずれも DS 側に既存 —
  受け皿の新設は不要。質問リスト自体の正は DS-GUIDE.md §2-4 側にあり、
  本リポジトリへは複製しない（正の二重化を避ける）
- **既存方針との整合**: 「現状の色は全面的に暫定・色味指摘は第一弾で追わない」
  （同日上記ログ）の確定工程が、本ヒアリング＋第二段（デジ庁プリミティブ移植）として
  具体化された。グレー系（text / border / surface 等）はヒアリング対象外で、
  従来どおり第二段のデジ庁プリミティブ移植で確定する

ステータス: 整合対応完了（brand-principles.md 1 件 + tokens.json $description 2 件 +
本ログ）。ヒアリング実施・回答反映は人間工程待ち。

### 2026-08-25: 密度・レイアウト要望 9 件（REQ-01〜09）— 承認を受けて対応

mock-trial（travel-expense）DS v0.0.4 反映版のデザイン担当者レビューで上がった要望 9 件
（`tickets/2026-08-25-density-and-layout-requests.md`）。デジ庁 DADS に密度・段組み・幅の規定は
ほぼ無く（レイアウト基本は 12 カラムグリッドとガター幅のみ・スペーシングトークン無し）、
全件が自社翻案（B）だったため推奨案を提示し、ユーザー承認（2026-08-25「起票内容の対応を」）を受けて
**推奨案どおり**実施した。判断点はすべて推奨側で確定。色（REQ-03）は件数が多いため並行作業し、
同じ変更セットに統合（REQ-03 の経緯は上記「2026-08-25: REQ-03 部品の色役割トークン」節）。

- **REQ-02（上位原則・先に決定）**: brand-principles.md に「レイアウト原則（PC 業務画面）」節を新設。
  PC（breakpoint.md 以上）は 1 画面収容を目標（基準 1366×768・実効高約 650px、最低 1280×720）、
  収容手段の優先順（余白縮小 → 段組み → 幅の活用 → サポートテキスト簡略化 → detail-page のみ Tabs）、
  禁止手段（文字縮小・44px 未満化・必須項目の折りたたみ・Textarea 1 行化・Table の情報欠落）、
  収まらない場合はセクション単位のスクロール + **sticky アクション行を許容**（自社翻案・採用）。
  AGENTS.md のハード制約に 1 行追加してエージェントが必ず参照するようにした。
  2026-08-18 以降「密度を上げたい」要望が 3 回繰り返された構造（上位原則の不在）をここで閉じる
- **REQ-01**: Table `alignment_guidance` を「見出しセルは常に左揃え」に改定（GAP-05 時の
  「データセルと同じ揃え」はデジ庁準拠ではなく自社判断だったため撤回）。「ラベル = 左揃え /
  数値 = 右揃え」を brand-principles.md 揃えの原則に置き、detail-page の dt・RepeatingFieldGroup の
  見出し行にも適用。トレードオフ（Material 等は数値列見出しも右揃え）は列幅を内容相応に絞って緩和
- **REQ-04**: (1) トークン追加なしで全パターンの density を 1 段詰め — form-page 項目間 md → sm・
  セクション間 lg → md・行内 sm → xs、detail-page lg → md・dl 行間 sm → xs、list-page lg → md、
  app-shell md → sm、confirm-flow / approval / inbox は準拠元に追従。report（印刷）・login・error-page は
  対象外（画面収容の問題が無い）。(2) `space.xxs`（2px）/ `space.ms`（12px）を追加 —
  命名は t-shirt 体系を維持（数値名への全面移行は既存参照の改名とモック側 CSS 変数名の変更を伴うため見送り。
  `ms` = medium-small）。(3) comfortable / compact の二系統トークン化は見送り（PC 既定 = compact 一本）
- **REQ-05 / 08（同一規定）**: form-page の PC を「**4 列の共通グリッド**」に改定（横並び上限 2 → 4。
  対象 = InputText / Select / Combobox / DatePicker / RadioButton / Checkbox。Textarea / FileUpload /
  RepeatingFieldGroup は常に全幅）。入力欄の幅は列の割当数で表現し、単独の短い欄を伸ばさない
  （デジ庁 InputText「幅は内容相応」と整合 — 幅は段組みで埋める）。列位置は全行で揃える。
  RadioButton / Checkbox は選択肢 3 つ以下で 1 列、4 つ以上は 2 列以上か全幅。中間段（md〜lg で 2 列）は
  設けず md 以上一律 4 列。never_do を「5 項目以上」「長文・添付・明細の横並び」「列位置のずれ」
  「単独欄の引き伸ばし」「Tabs / Disclosure で入力項目を隠す」に書き換え。app-shell の本体は
  **幅いっぱい（最大幅の上限なし）**。detail-page の dl は md 以上で 2 列許容。list-page の詳細検索パネルは
  form-page に自動追従。Textarea `resize_guidance` の「1 カラム原則」参照を更新
- **REQ-06 / 07**: DatePicker の layout 既定を **breakpoint.md 以上 = Consolidated / 未満 = Separated** に
  （デジ庁の 2 レイアウトの範囲内で「PC では 1 欄に見せる」に応える 2 段構えの第 1 段。単一欄
  〔yyyy/mm/dd〕variant はデジ庁逸脱のため未提供 — Consolidated 版モックの評価で不足が残る場合に再起票）。
  単位ラベル「年」「月」「日」は**接尾**（「2026 年 08 月 22 日」の読み順）に固定 — デジ庁に明文規定無し、
  実装サンプルのラベル位置は第二段で突合し、接頭だった場合も読み順を理由に接尾を優先する。
  `responsive` フィールドを spec に新設。「PC」の境界 = breakpoint.md（1024px）
- **REQ-09**: RepeatingFieldGroup の `layout_guidance` を「枡なし・罫線（border-bottom）区切り・
  角丸と行 padding なし・セル padding xs〜sm・見出し行は Table の th と同じ見た目」に改定。
  削除ボタンは最右列（Table の行操作列禁止は閲覧一覧の規定 — confusable_with に明記）、
  「+ 行を追加」は最終行直下・左端。`states` フィールドを新設し row-error を「該当欄の枠線 danger +
  行直下のエラーテキスト（行背景の強調は danger-subtle で任意）」に（枡が無いため枠色変更は不可）。
  2026-08-18 MK2「旅費明細はテーブルで表示が良い」の残件をここで解消
- **REQ-03**: 上記節のとおり（色役割トークン 14 件・`tokens/ROLE-MAP.md`・Badge 色 variant・Button 状態色・
  audit-tokens の色キーワード検出）。Badge 文字の AA 未満 2 件はユーザー承認で同日前倒し解消
  （`on-primary-subtle` / `on-danger-subtle` 追加 — 計 16 件）

`npm run ci` OK（部品 20 件 / パターン 10 件 — 件数変更なし）。`tokens/dist/` への反映は従来どおり第二段。
mock-trial 側は v0.0.5 配布後に再生成する（REQ-06 は Consolidated 版で一度評価してから単一欄 variant の
要否を判断する）。

ステータス: REQ-01〜09 の 9 件すべて完了（REQ-06 は第 1 段。第 2 段〔単一欄〕はモック評価待ち）。

### 2026-08-25: アイコン定義の新設を起票（ICN-01〜06 — 起票のみ・実装・仕様変更なし）

REQ 対応中に「各 spec がアイコンの存在を前提にしている（NotificationBanner の type アイコン必須・
Disclosure の開閉アイコン・Table のソートアイコン・閉じる・カレンダー等、少なくとも 10 部品 + 2 パターン）
のに、アイコンセット・サイズ・語彙・横断の a11y 規則が DS のどこにも無い」ことが判明し、ユーザー指摘を
受けて `tickets/2026-08-25-icon-definition.md` に起票した。モック側は NotificationBanner の type アイコンを
Unicode 記号 `✓` `✕` のテキストで代用しており（warning / info は未実装）、REQ-03 の `white` 直書きと同じ
「規定が無いので代用で凌ぐ」構造。

- **デジ庁調査**: 基本デザイン「アイコン」は概要（配置 4 型: フロント / リード / テール / エンド）と
  アクセシビリティ（ラベル必須・併用時 alt=""・コントラスト 4.5:1 / 3:1・リンク範囲・単体 44×44）のみ公開
  （2025-07-30・v2.17.1）。サイズ・weight・語彙の規定は無い。**DADS の Figma データは UI アイコンとして
  Material Symbols（Apache License 2.0）を同梱**していることを「利用上の注意事項」で確認 — 本ファイル上記
  「使わないもの: イラスト・アイコン素材（MIT と別条件）」は別規約の**イラストレーション・アイコン素材**
  （行政手続き説明用 60 種）を指しており、UI アイコンまで除外する必要はなかった（承認後に書き分ける）
- **提案の骨子**: ICN-01 Material Symbols Outlined を SVG 配布で採用 / ICN-02 デジ庁 a11y・配置の採取（A）/
  ICN-03 spec 逆算の語彙 16 種を `icons/ICON-MAP.md` に固定し語彙外は起票制 / ICN-04 `icon.size` sm 16 ・
  md 20 ・ lg 24（weight 400・fill 0 固定）/ ICN-05 リード配置既定・間隔 space.xs・currentColor 既定・
  装飾 aria-hidden / 情報 role="img" の二分・記号文字・絵文字・アイコンフォント・自作 SVG の禁止 + audit 追加 /
  ICN-06 部品（Icon）ではなく基盤定義として `icons/` に置き、AGENTS.md の参照順序に追加
- IconButton 不採用（GAP-14）は再開しない。「アイコンは必ずラベルと組み合わせる」の前提で定義する

ステータス: 起票完了 → 同日承認・対応完了（次節）。

### 2026-08-25: アイコン定義 ICN-01〜06 — 承認を受けて対応（`icons/ICON-MAP.md` 新設）

上記起票をユーザーが**推奨案どおり承認**（2026-08-25「推奨の B で。起票してもらった内容で承認するので
進めてほしい」）。判断点はすべて推奨側で確定し、ICN-03 (b) の `external` は **B（装飾扱い + 隠しテキスト）**。

- **ICN-01 アイコンセット**: Material Symbols **Outlined**・weight 400 / fill 0 / grade 0 固定・**SVG 配布**
  （可変フォント版はリガチャ露出と外部フォント依存のため不採用）。Apache 2.0 — 第一弾は SVG 実体を
  同梱していないため再配布は未発生。第二段で SVG を同梱する時点で LICENSE / NOTICE を `icons/` に置く。
  本ファイル「使わないもの」を「イラストレーション・アイコン素材（別規約）」と「UI アイコン = Material
  Symbols 採用」に書き分けた
- **ICN-02 デジ庁 a11y・配置の採取（A）**: 配置 4 型（フロント / リード / テール / エンド）と a11y 5 項目
  （ラベル必須・併用時 alt=""・4.5:1 / 3:1・リンク範囲・単体 44×44）を ICON-MAP §4 / §5 に採取。
  NotificationBanner の type アイコンは role="img" + aria-label を維持（alt="" 原則からの自社翻案 —
  タイトル文だけでは種別が伝わらないため。デジ庁実装との突合は第二段の判断点）
- **ICN-03 語彙 16 種**: spec から逆算した `status-success / -error / -warning / -info / close / expand /
  sort-none / -asc / -desc / prev / next / calendar / add / remove / external / search` を役割名で固定
  （実体の Material Symbols 名は第二段の突合で差し替え可・役割名は不変）。語彙外は起票制
  （does_not_exist_yet と同じ運用。ICON-MAP §6 に候補欄）。**external は装飾扱い**: 「新しいタブで開く」は
  挙動の予告であり WCAG G201 が文字での告知を前提にするため、情報はリンク内の隠しテキスト
  「（新しいタブで開きます）」が担い、`open_in_new` アイコンは aria-hidden（デジ庁 alt="" 原則に準拠。
  デジ庁サイト自身の外部リンク表記「新規タブで開きます」とも一致）。判定規則「アイコンが唯一の担い手なら情報、
  文字で書けるなら文字に書いてアイコンは装飾」で NotificationBanner（情報）との違いを説明できる
- **ICN-04 寸法**: `icon.size.sm / md / lg` = 16 / 20 / 24px を tokens.json に追加（t-shirt 命名で space /
  radius と揃える）。width / height 両方に当て、font-size 継承に任せない。44px ターゲットは操作要素側の規定
- **ICN-05 横断規則**: 既定リード配置・間隔 space.xs・文字中央揃え・**currentColor 既定**（アイコン専用の色
  トークンは作らない。独立色は NotificationBanner の type アイコンのみ — ROLE-MAP §2 に追記）・装飾
  aria-hidden / 情報 role="img" の二分・記号文字（✓ ✕ × ▼ + 等）/ 絵文字 / アイコンフォント / 自作 SVG /
  語彙外アイコンの禁止（brand-principles.md 禁止リストに並記、AGENTS.md ハード制約に追加）。
  `audit-tokens.mjs` に記号文字アイコンの検出 3 種（icon 要素内テキスト / 記号文字のみの要素内容 /
  CSS content: の記号文字）を追加 — モックの `✓` `✕` はこれで CI 検出される
- **ICN-06 置き場所**: `icons/ICON-MAP.md`（ROLE-MAP と同層・同書式）。`components/Icon` は作らず、
  does_not_exist_yet にも載せない（部品ではなく部品の内部要素。IconButton 不採用と整合）。AGENTS.md の
  参照順序に 5 番目として追加
- **spec 反映（11 部品 + list-page）**: NotificationBanner（status-* lg・close md・記号文字禁止を
  never_use_when に追加）/ Disclosure（expand md）/ Table（sort-* sm・aria-hidden・状態は aria-sort）/
  Button（`icon_guidance` 新設。a11y 欄の「アイコンのみのボタンは隠しラベル」は GAP-14 と矛盾していたため削除）/
  Pagination（prev / next。先頭・末尾は語彙未登録）/ Tabs / DatePicker（カレンダーボタン = calendar アイコン +
  可視テキスト「カレンダー」— デジ庁実装のアイコンのみ + 隠しラベルとは異なり可視ラベルで統一）/
  Combobox（expand テール。選択解除ボタンは設けない）/ Select（`icon_guidance` — OS 既定でも expand でも可）/
  ModalDialog（close + 「閉じる」）/ Link（`external_guidance` 新設・`source` 新設）/ RepeatingFieldGroup
  （「+ 行を追加」→ add アイコン + 「行を追加」）/ list-page（search）。`purpose` / `use_when` は変更していない
  ため index.json の再生成は不要

`npm run ci` OK（index.json 最新・DS 自身の audit 違反 0 — 部品 20 件 / パターン 10 件、件数変更なし）。追加ルールの
実効性はモック（mock-trial bfa54b7）に対する `audit-tokens.mjs` 実行で確認: NotificationBanner の `✓` `✕` 4 画面 8 件を
「アイコン用要素内テキスト」「記号文字アイコン」の両ルールで検出（v0.0.5 反映時の再生成で解消する対象）。
`tokens/dist/` への反映は従来どおり第二段。mock-trial 側の `✓` `✕` 置き換え・Link.tsx への隠しテキスト実装は
v0.0.5 以降。

ステータス: ICN-01〜06 の 6 件すべて完了。第二段への申し送り = デジ庁 Figma のアイコン指定値の突合・
NotificationBanner 代替テキスト方針の突合・SVG 同梱時の LICENSE 配置。

### 2026-08-25: 段組みルール・揃え・面の色・チップ形状 要望 10 件（REQ-10〜19）— 承認を受けて全件対応

mock-trial（travel-expense）**DS v0.0.5 反映版（コミット `a827ffc`）**のデザイン担当者レビューで上がった
要望 10 件（`tickets/2026-08-25-column-rules-and-visual-requests.md`）。前票（REQ-01〜09）から REQ 番号を継続。
起票時の見立てどおり、**10 件のうち 6 件（REQ-10 / 13 / 14 / 15 / 16 / 18）が「規定が"範囲"や定性表現で
書かれていて一意に決まらない」ことに起因**していた（前票 REQ-05 / 08 で入れた 4 列グリッドは
「DatePicker は 1〜2 列」「無理に詰め込まず折り返す」のように**同じ規定から違う絵が出る**状態だった）。
ユーザーが 1 件ずつ確認・承認する形で進め、**10 件すべてを反映**（REQ-10〜19。判断点はすべて推奨側で確定 —
例外は REQ-17 の色相〔ブランド寄りの淡色〕と Table ヘッダの扱い〔専用トークン〕の 2 点で、いずれもユーザー選択）。

- **REQ-16a（区分 A・採取）**: Table `text_overflow_guidance` に「表に内容相応の列幅の合計（最小幅）を持たせ、
  領域幅がそれを下回る場合は列を縮めずスクロールさせる」を具体化。デジ庁の明文（モバイルでは領域内の
  横スクロールで構造を崩さない）は既に spec に入っていたが、**モックは `overflow-x: auto` のラッパを
  持ちながら `width: 100%` + `table-layout: fixed` のためスクロールが一度も発生せず**、列が均等に潰れて
  ellipsis になっていた（ブランド原則「Table の省略表示による情報欠落」に実質抵触）。
  「`width: 100%` だけではスクロールしない」という実装条件の欠落が原因だったため、規定の変更ではなく条件の補記
- **REQ-10（段組みの一意化・他の前提）**: form-page に **`column_allocation`** を新設し、
  「DatePicker は 1〜2 列」等の**範囲指定を「部品 → 列数」の対応表に置き換え**た。原則は
  「**その部品の実効幅が収まる最小の列数。余白を埋めるために列を余分に割り当てず、余った列は行の右側に空ける（左詰め）**」。
  DatePicker = 1 列（実効幅 214px < 1 列 330px）に確定したことで、要望の「出発日・帰着日の間に約 450px の
  余白が空く」が解消し、出張スケジュール 1 行目は 出発日 + 帰着日 + 出発時刻 + 帰着時刻 の 4 項目が左から詰まる。
  表に無い部品・想定外に長い値は**実装裁量で広げず起票**（AGENTS.md ハード制約と同じ運用）。
  トレードオフ（ラベルが長い項目でラベルが折り返す）は「ラベルの折り返しは許容し、入力欄の幅を
  ラベル長に合わせて広げない」で確定
- **REQ-13（行内の段揃え）**: form-page に **`row_alignment`** を新設。従来は「エラー表示で高さが伸びても
  他項目をずらさない」だけで**サポートテキストの有無による差の規定が抜けていた**ため、
  「**ラベル / サポートテキスト / 入力欄 / エラーテキストの 4 段の上端を行内で揃える**」と要因非限定に一般化。
  実装手法はユーザー選択で **① subgrid を既定**（②「サポートテキストの有無を行単位で統一」は
  「必要のない補足を書く動機になる」ため不採用と明記）。トレードオフは行高 +最大 23px で、
  1 画面収容の原則との衝突は軽微と判断
- **REQ-12（dl の揃え）**: brand-principles.md 揃えの原則に「**右揃えは"値が縦に並ぶ列"がある場合に限る**」を追加。
  Table のデータ列 / RepeatingFieldGroup の入力列は右揃え（現行どおり）、**dl・確認画面の名前-値ペアは
  dt・dd とも左揃え**（1 レコードのみで比較対象が縦に無い）。detail-page から「dd は数値・日付・金額のみ右揃え」を
  削除。従来の緩和策「列幅を内容相応に絞る」が dl では機能しない（dd は 2 列グリッドの残り幅を取るため
  絞る先の列幅が無く、ラベルから値まで最大 451px 離れていた）ことが撤回の理由。
  代替案（右揃え + `max-width`）は「値の右端が項目ごとにばらつき揃えの意味が薄れる」ため不採用。
  デジ庁の右揃え規定は**テーブルの列**についてのもので dl の揃えは規定が無い（自社定義）
- **REQ-14 / 15 / 16b（明細行の幅を取り合う 3 件・セットで判断）**:
  - **14**: DatePicker `a11y` の 2 択のうち「可視テキストは装飾（aria-hidden）」が RepeatingFieldGroup の
    「視覚的に隠したラベルを残す」と重なり、**単位ラベル（年 / 月 / 日）まで隠す実装**を生んでいた
    （画面上は枠内に数字 3 つが並ぶだけ）。**単位ラベルの可視を固定**し（隠す実装を `never_use_when` へ）、
    2 択は支援技術への伝え方だけであることを明示。RepeatingFieldGroup `a11y` に「視覚的に隠すのは
    **項目ラベル（見出し行と重複するもの）だけ**」を明記
  - **15**: RepeatingFieldGroup `layout_guidance` の「**1 行に収まらない項目数の場合は 2 段目へ折り返す」を撤回**し、
    「1 行 1 レコードを崩さず行内の項目は折り返さない / **列幅は列ごとの内容相応の固定幅（auto-fit の
    均等割りを使わない）**」に改定。原因は `auto-fit minmax(7rem, 1fr)` で列数によって 1 列幅が変わり、
    form-new（8 列 = 159px）では Consolidated の日付欄 164px が**5px 超過して折り返す**一方、
    apply-input（4 列 = 327px）では折り返さない — **同じ部品が画面の項目数によって見た目が変わる**状態だった。
    DatePicker `implementation_notes` に折り返し禁止（nowrap 相当）+ 最小幅を追記
  - **16b**: RepeatingFieldGroup に **`responsive`** を新設。「全ブレークポイントで 1 行 1 レコードを維持し、
    領域幅が列幅の合計を下回る場合は**部品領域内の横スクロール**で対応（縦積み・縮小・折り返しはしない）」。
    デジ庁に入力側の該当部品は無いが、閲覧テーブルの明文（領域内の横スクロールで構造を崩さない）を
    入力側へ翻案。スクロール領域の a11y 作法（`role="region"` + `aria-label` + `tabindex="0"` 相当）を
    Table `a11y` に追記して共通化。**トレードオフとして挙げた「見落ち」リスクへの対策を、ユーザー判断で
    規定に含めた**（エラー時に該当列までスクロール位置を移動 + エラーサマリーから該当セルへリンク）。
    横スクロールを避けたい場合の代替は「**列を減らす**」で、縦積みは選択肢にしない。
    form-page `responsive` に「1 カラムに積むのは単項目のみ」を追記して両者の関係を明示
- **REQ-17（面の色）**: **案 1（ページ地だけを薄い色にする）** を採用。色相は**推奨（無彩色 gray.50）ではなく
  ブランド寄りの淡色をユーザーが選択**し、Table ヘッダは**専用の色を持つ**ことを選択（`surface` の値を
  落とす案は不採用）。
  - `color.primitive.teal.25` = #f2fafb（ブランド #00a1ae の 5% ティント = `primary-subtle` の半分の濃度）
  - `color.semantic.canvas`（= teal.25）を新設し `body` 専用に。`background`（白）の用途から「ページ本体」を外した
    → 入力欄・Table・app-shell ヘッダ・ModalDialog が地から浮いて**面の階層**が出る
  - `color.semantic.table-header`（= gray.100）を新設し `surface` の用途から Table ヘッダ行を分離。
    地に色が入っても「見出しの段」と読めるよう `surface`（gray.50）より 1 段濃くした
  - ROLE-MAP §1 に「ページ地」「ヘッダ行の面」、§4 に app-shell の地を追加。app-shell `layout` に
    「地と面の境界は色差だけに依存させず罫線を併せ持つ」を明記
  - **申し送り**: `canvas` は `primary-subtle`（選択行・Badge = 意味を持つ淡色面）と同色相のため、
    濃度差（5% / 10%）だけが区別になる。起票時に指摘した意味衝突のリスクは残るため、`$description` に
    「canvas を選択・強調・状態表現に使わない / 淡色面の代用に canvas を使わない」を明記して運用で担保した。
    モックで選択行の見分けが弱いと出た場合は `primary-subtle` の濃度を再起票する
- **REQ-19（チップ形状）**: 前票 REQ-03 で Badge に色 variant を規定した際に**spec へ「角丸 radius.sm」と
  書いたことが原因**で、v0.0.4 のほぼピル形（`calc(radius-md * 2)` = 16px 相当）が v0.0.5 で
  Button と同値の 4px になり、角丸・padding・文字サイズ・面の色がすべて Button と揃って「ボタンに見える」状態を作った。
  - `radius.full` = 9999px を新設（旧モックの `calc()` による代用を正式なトークンに。演算での代用を禁止と明記）
  - Badge を `radius.full` に改定し、左右 padding を `space.sm` → `space.ms`（ピル形は左右が視覚的に詰まる）
  - **Button の角丸が spec 未規定だった**（モックが `radius.sm` を選んでいた）ため `shape_guidance` を新設して明記
  - brand-principles.md に「**形（角丸）でも操作可能性を区別する**」、ROLE-MAP に §5（形の対応表）を新設 —
    色・padding・文字サイズは近づくことがあるため**形を最後の識別子として残す**
  - **申し送り**: 将来 Chip / Tag（操作可能チップ）を追加する場合は「操作可能チップは全周丸 + アイコン、
    Badge は全周丸のみ」の区別が必要（Badge spec の source に記録）
- **REQ-11 / 18（区分 C = DS 変更ほぼ不要・モック実装側の不備。推奨内容で対応）**:
  - **REQ-11**（日付が接頭ラベル「年 2026 月 08 日 20」のまま）: DS 側は前票 REQ-07 で**既に接尾を規定済み**で、
    mock-trial 側の実装漏れ。取り違えの原因は「項目ラベル（前・上）と単位ラベル（後・接尾）の 2 種類の区別が
    DatePicker spec の中だけにあること」だったため、brand-principles.md 揃えの原則に横断原則として 1 行追記
    （「項目ラベルは入力欄の前〔上〕、単位ラベル〔年 / 月 / 日・円・個・％ 等〕は値の直後〔接尾〕」）。
    DatePicker spec 自体は変更なし。mock-trial 側で全画面の DatePicker を接尾に修正する
  - **REQ-18**（セクションごとに横幅の使い方が違う）: DS 規定は「Textarea は常に全幅」で一意だったが、
    モックは Textarea だけのセクションをグリッドで包まず素の `.mk-field`（`max-width: 40rem` / Textarea を含む場合
    `48rem`）が効いて 768px で止まっていた実装不備。統一の方向は**推奨の「全幅に揃える」を採用**
    （「長文入力に行長上限を設ける」案は現行規定「Textarea は常に全幅」の改定と 1 画面収容の原則との調整が
    必要になるため不採用）。form-page `layout` に「**4 列グリッドはセクション単位で必ず適用する**
    （項目が 1 つだけのセクションも同じグリッドに載せる）。部品側の `max-width` で幅を止めない —
    幅は列の割当数だけで表現する」を追記し、never_do に 2 行追加。
    表示側の可読性（detail-page の長文値の行長）は本票では扱わず、必要になれば別途起票する
- **追加起票（ユーザー判断）**: 調査中に見つかった副次的な穴のうち 2 件を
  `tickets/2026-08-25-date-display-format-and-choices-in-table-rows.md`（REQ-20 / 21）として起票。
  1 = 日付の**表示**形式の規定が無い（入力「2026 年 08 月 20 日」/ 表示「2026-08-18」で食い違う）、
  3 = テーブル状の行に選択肢群を置く場合の規定が無い（3 択が縦積みで行高 3 行分）。
  起票にあたりデジ庁側を新規調査し、**スタイルガイドに日付・時刻の表記規定は無い**ことと、
  **「リストが 5 つ以下の場合はラジオボタンの使用を推奨」の明文がある**ことを確認。後者により、
  前票に書いた方針案「テーブル状の行では選択肢群を Select にする」は**デジ庁逸脱になるため主案から外し**、
  「ラジオを横並びで維持し列幅で収める（縦積み禁止）」に差し替えた

`npm run ci` OK（index.json 最新・DS 自身の audit 違反 0 — 部品 20 件 / パターン 10 件、件数変更なし。
`purpose` / `use_when` は変更していないため index.json の再生成は不要）。`tokens/dist/` への反映は従来どおり第二段。
mock-trial 側（REQ-11 / 18 の実装不備・単位ラベルの可視化・列幅の固定幅化・地の色・チップ形状）は
承認済み分を含めた次回配布で再生成する。

### 2026-08-25: 日付の表示形式・テーブル状の行の選択肢群（REQ-20 / 21）— 承認を受けて対応

上記 REQ-10〜19 の調査中に見つかった副次的な穴のうち、ユーザー判断で追加起票した 2 件
（`tickets/2026-08-25-date-display-format-and-choices-in-table-rows.md`）。**推奨案どおり承認**を受けて実施。
本票は前票と違い**デジ庁側を新規に調査**した（前票の調査範囲は部品ガイドラインで、本票は表記ルールと
ラジオ / セレクトの使い分けが対象のため）。その調査結果が方針を 1 件変えている（下記 REQ-21）。

- **REQ-20（日付の表示形式）**: 入力側は前票 REQ-11 / 14 で「yyyy 年 MM 月 dd 日」の読み順・単位ラベル可視を
  規定したのに、**表示側の形式が DS のどこにも無い**ため、モックは同じ画面で入力「2026 年 08 月 20 日」/
  確認「2026-08-20」と表記が食い違っていた。数値・金額には表示側の規定（InputText `numeric_input_guidance`
  「3 桁区切りのカンマ + 単位」）があるのに日付には対応する規定が無い、という純粋な抜け。
  - **デジ庁の該当は無い**ことを確認（スタイルガイドのページはデザインシステムとスタイルガイドの定義・
    作成手順の解説で、数字・年月日の書き方を扱っていない。日付ピッカーのガイドラインも入力についてのみ）→ 自社定義
  - brand-principles.md に **「表記の原則（数値・日付）」節を新設**: 日付の既定は `yyyy年MM月dd日`（入力側の
    読み順と一致）/ **Table では `yyyy/MM/dd` を許容**（日付列が複数あると表の最小幅を押し上げて横スクロールが
    出やすくなるため。ただし同一画面内はどちらか一方に統一）/ 時刻付きは `yyyy年MM月dd日 HH:mm`（秒は原則非表示）/
    年月のみ・月日のみは `yyyy年MM月`・`MM月dd日`（DatePicker の省略形 variant と対応）/ 数値は 3 桁区切り + 単位 /
    和暦は入力・保存とも西暦のままで表示側で併記
  - **集約先を 1 か所にしたのが要点**: 日付は複数の部品・パターンに跨るため、InputText
    `numeric_input_guidance`・detail-page・confirm-flow・report・Table `alignment_guidance` の各所を
    同節への参照に統一した（REQ-11 の「項目ラベルと単位ラベルが 1 か所に書かれていないために取り違えた」のと
    同じ構図を避ける）
- **REQ-21（テーブル状の行の選択肢群）**: form-page の「選択肢 3 つ以下なら 1 列」は**単項目のフォーム行**を
  前提にした規定で、RepeatingFieldGroup のテーブル状の行（列幅を列ごとに決める）には当てる先が無かった。
  結果、モックの明細行で「入力区分」（3 択）が縦に積まれ行高が約 3 行分になっていた（REQ-15 と同じ原因の別症状）。
  - **デジ庁調査で方針を差し替えた**: **「リストが 5 つ以下の場合はラジオボタンの使用を推奨」という明文がある**
    （ラジオボタン / セレクトボックスの概要ページ。セレクトボックスは「あまりに長いリストは使い勝手を下げる」立場）。
    したがって前票の「副次的な穴」欄に書いた方針案「テーブル状の行では選択肢群を Select にする」は**デジ庁逸脱**であり、
    起票時に主案から外した。**主案は「ラジオを横並びで維持し、列幅で収める（縦積み禁止）」**
  - RepeatingFieldGroup `layout_guidance` に追記: 選択肢が 1 行に横並びで収まる列幅を確保（3 択で実測約 260〜300px）/
    収まらない場合は**列を減らす**かその項目を明細行の外（明細群全体の設定）へ出す / 選択肢は 3 つ以下・
    ラベルは 2〜4 文字 / **選択肢 4 つ以上を明細行に置かない** — 必要な場合はこの文脈に限り Select への
    置き換えを許容し、**デジ庁「5 つ以下はラジオ推奨」からの意図的な逸脱として spec と source に明記**した
    （推奨であって禁止ではなく、表形式では行高の増加という別の不利益があるため）。`never_use_when` に縦積み禁止を追加
  - form-page `column_allocation` に **`scope`** を追加し、「本対応表は単項目のフォーム行の規定。
    テーブル状の行は RepeatingFieldGroup spec の `layout_guidance` / `responsive` に従う」と適用範囲を明示
  - **申し送り（トレードオフの帰結）**: REQ-21 の選択肢列（約 260〜300px）と REQ-14 の日付列（約 285px）を
    合わせると、明細 8 項目の行の最小幅は**約 1,400〜1,500px** になり、1366px のビューポートでも横スクロールが出る。
    これを避ける手段は「明細行の項目数を業務側で見直す（列を減らす）」であり、DS 側で縮小・折り返し・縦積みは
    許さない（REQ-15 / 16b の決定と整合）。ユーザーはこの帰結を了承済み

`npm run ci` OK（index.json 最新・DS 自身の audit 違反 0 — 部品 20 件 / パターン 10 件、件数変更なし。
トークン追加なし — 2 件とも既存トークンで表現できた）。mock-trial 側（表示側の日付形式・明細行の入力区分列）は
次回配布で再生成する。

### 2026-08-26: 複数プロジェクトで使うベースDSへの再編（トークン・brand-principles のプロジェクト分離）

第一弾検証（v0.0.6）を「どのプロジェクトでも使えるベースDS」として運用する方針が決まったことを受けての再編。
きっかけは、モック A/B トライアル（`.cursor/skills/mock-ab-trial/SKILL.md`）のブランドヒアリング手順を
どう git 管理するか相談したところ、現行の `tokens.json` に**先行適用済みのブランドカラー #00a1ae が
特定案件（travel-expense-demo）に紐づく値**であり、これを「ベースDSの既定値」のまま残すと他プロジェクトの
既定が汚染される、と判明したこと。

- **既存の設計判断を発掘・適用**: HANDOFF 設計判断14（2026-08-05）「サービス別の分岐が必要になったら
  セマンティック層のテーマファイル追加 + テーマ別 dist 出力で対応し、DS パッケージは分割しない」と、
  `tokens/config.mjs` のコメント・`tokens/HARVESTING.md` 末尾に**すでにスタブとして書かれていた**手順を
  今回実装した（新規の設計方針ではなく、先送りにしていたものの実行）
- **git 構成**: 単一リポジトリ・単一 master・単一 v0.0.x タグ列のまま。別リポジトリ・別ブランチには
  分割しない（[[no_separate_branches]] と同方針）。将来クライアント間の機密分離等が必要になったら、
  案件別ファイル（`semantic.<project>.json` 等）が独立性の高い単位のため、その時点で切り出しは容易
- **tokens/ の再編**: `tokens/tokens.json`（単一ファイル）を廃止し、
  - `tokens/primitive.json` — 共有プリミティブ（色スウォッチ・space・radius・font 等。teal / brand.600 の
    プリミティブ自体は残置 — HARVESTING.md の記載どおり primitive 層は特定案件に紐づく意味を持たないため）
  - `tokens/semantic.json` — ベースDSの既定セマンティック値。ブランド色（primary / primary-hover /
    primary-subtle / on-primary-subtle / canvas / brand / focus）は **indigo 系のプレースホルダ**に変更
    （汎用UIキットの定番色。info トークンが blue 系のため、primary と色相が衝突しないよう選定）
  - `semantic.travel-expense-demo.json` — travel-expense-demo 案件のブランド色上書き（teal /
    #00a1ae。値は変更せず旧 tokens.json から移設のみ）
  - `tokens/config.mjs`（既定ビルド）/ `config.travel-expense-demo.mjs`（案件別ビルド）
- **brand-principles.md の再編**: 「禁止リスト」「文言トーン」はプロジェクト非依存の内容だったためベース側に
  残置。「ブランド資産」節のみ無ブランドへリセットし、travel-expense-demo 固有の内容は
  `brand-principles.travel-expense-demo.md` へ切り出した（tokens と同じオーバーレイの考え方）
- **案件ファイルの置き場所（2026-08-26 同日に追補）**: 上記 travel-expense-demo の 3 ファイルは
  `examples/travel-expense-demo/` へ移し、**ベースDS 本体ではなく参考実装例**と位置づけた。
  ベースDS を受け取った人が「travel-expense-demo がひな形／既定値」と誤解する経路を断つのが目的。
  ビルドは `npm run build:tokens:example:travel-expense-demo`。
  **実案件のファイルは examples/ ではなく規約どおりの場所**（`tokens/semantic.<project>.json` /
  `tokens/config.<project>.mjs` / 直下の `brand-principles.<project>.md`）に置く
  — 対応表は `examples/travel-expense-demo/README.md`
- **今後の運用**: 新しいプロジェクトでブランドヒアリングを行ったら、`tokens/semantic.json` /
  `brand-principles.md`（ベース）は直接編集せず、`semantic.<project>.json` /
  `brand-principles.<project>.md` を新設して差分のみ書く。汎用的な部品・パターン・トークンの改善
  （今までの REQ / GAP 対応と同じ性質のもの）は引き続き共有側に直接コミットする
- **見送った選択肢**: プロジェクトごとに別リポジトリ・別 fork にする案は、①設計判断14と矛盾する
  ②一人運用の現段階ではオーバーヘッドが大きい、の 2 点で見送り。将来プロジェクト数が増え、
  クライアント間の機密分離や独立したリリースサイクルが必要になった時点で再検討する

参照が更新箇所: `tokens/ROLE-MAP.md`（正のトークン値の参照先）/ `AGENTS.md`（ハード制約の参照先）/
`GUIDE-for-designers.md`（フォルダマップ・§3-1・§3-3・コマンド表・依存表）/ `tokens/HARVESTING.md`
（サービス別テーマ節を「今はやらない」から実運用の手順へ更新）。

検証: `node scripts/generate-index.mjs --check` / `node scripts/audit-tokens.mjs` /
`node scripts/audit-components.mjs` いずれも OK（`tokens/` はハード制約により audit 対象外のため
影響なし）。primitive.json → semantic.json → semantic.travel-expense-demo.json の参照解決は
手動スクリプトで全 30 参照を検証し破損なし（`style-dictionary` 本体は未インストールのため
`npm run build:tokens` 自体は今回未実行 — 第一弾がデータのみ運用のため dist/ 生成は従来どおり第二段）。

---

### 2026-08-26: 組織共有に向けたリポジトリ整備（構成・ライセンス表示・CI）

チーム外へ共有する前提でリポジトリを点検し、**「受け取った人が誤解する / 動かない」経路**を
潰す整備を行った。DS の設計判断そのものは変えていない（部品・パターン・トークンの中身は無変更）。

- **実装 `.tsx` を v0.0.x から取り下げ**: `Button.tsx` / `Button.stories.tsx` / `Link.tsx` を削除。
  理由は **CSS が同梱されておらず（リポジトリ内に `.css` が 0 件）、`tokens/dist/tokens.css` も
  生成物で Git 管理外のため、import しても素の HTML にしかならない**こと。README のバージョン規約
  「v0.0.x = 仕様データのみ」とも矛盾していた。「動きそうに見えて動かない」状態が、コピーして
  使おうとする人の時間を最も奪うと判断。v0.1 で実装層とセットで入れ直す（履歴には残っている）。
  Props を union 型に閉じる方針は `GUIDE-for-designers.md` §4-1 に「v0.1 で守ること」として存置
- **案件ファイルを `examples/` へ**: 上記の travel-expense-demo 3 ファイルを移設（同節に詳細）
- **`tokens/dist/` を .gitignore へ追加**: AGENTS.md が「生成物・直接編集禁止」と宣言しながら
  ignore されておらず、誰かが `npm run build:tokens` を実行した瞬間に未追跡ファイルが出る状態だった
- **CI を実在させた**: AGENTS.md は「違反は CI で自動検出される」と宣言していたが
  `.github/workflows/` が無く、宣言だけの状態だった。`.github/workflows/ci.yml` を追加して
  push / PR で検査 3 本を実行する。**検査スクリプトは `node:` 標準モジュールのみで動くため
  依存インストール不要**（`style-dictionary` は `build:tokens` 専用の devDependency）。
  そのため lockfile が無くても CI は成立する
- **package.json の整理**: 存在しない `index.ts` を指していた `main` を削除（v0.0.x に
  エントリポイントは無い）。`private: true` + `license: "UNLICENSED"` を追加して
  公開レジストリへの誤 publish を防ぎ、README の社内限定方針と一致させた。`engines.node >= 18` を明記
- **style-dictionary をキャレット無しの完全固定へ**（`^4.0.0` → `4.0.0`）:
  **package-lock.json が作れない**ため（開発端末の Cylance Script Control が npm の実行を
  ブロックする。本リポジトリの制約であり npm 側の問題ではない）、キャレットのままだと
  4.x のどのバージョンが入るかが人と時期で変わる。トークンの**値**は固定されているのに
  値を CSS へ変換する**機械**が固定されていない状態で、DS の原則「正はコード（同じ入力 →
  同じ出力）」と噛み合わない。さらに `tokens/dist/` を Git 管理外にしたため、
  **変換結果のドリフトは diff に現れず発見できない**。完全固定なら lockfile 無しでも
  この経路は塞げる（integrity ハッシュによる検証は得られないままなので、供給網の固定は未解決）。
  なお第一弾では `npm run build:tokens` を一度も実行していないため、現時点の実害は無い
  — 効いてくるのは dist/ を実際に生成・配布する第二段から
- **未対応として残した項目（v0.1 に入る前に判断する）**:
  ① lockfile を **CI 上で生成**する（`npm install --package-lock-only` はパッケージを
  ダウンロードせず解決結果だけを書くため、GitHub Actions 上なら手元の制約を迂回できる）／
  ② Cylance の除外申請／③ `tokens/dist/` をコミットする案の再検討
  （ドリフトが diff で見える・利用側がビルド不要・Claude Design 用 CSS をタグから直接取れる、
  の 3 点と、生成物が履歴に乗る代償を天秤にかける。AGENTS.md の「直接編集禁止」は編集の話であり
  コミットの可否とは別論点）。**v0.1 で React / Storybook が入ると依存ツリーが増えるため、
  lockfile 不在のまま依存を増やす順序は避ける**
- **ローカル絶対パスの表現を修正**: `C:\Work\mock-trial\...` という記述が DECISIONS.md 1 か所と
  tickets 4 か所にあり、受け取った人には解決できない参照だった。**「別リポジトリ mock-trial
  （デザイン担当者のローカル・本リポジトリからは参照不可）」**と分かる表現に統一し、
  各票に転記済みの実測値が唯一の根拠であることを明示した
- **ドキュメントを実態に一致**: `GUIDE-for-designers.md` のフォルダマップに実在する `tickets/` /
  `icons/` / `examples/` / `.github/` が無く、逆に**このリポジトリに無い `handoff/` が載っていた**
  （§11 では「含まれない」と書かれており、マップと本文が矛盾）。タイトルも旧構成の
  「design-system/ 中身ガイド」のままだった。マップ・タイトル・§3-3・§4・§7・§12・§13・§14・§15 を修正

**ライセンス表示（README NOTICE）**: 上流 3 系統の条件を確認して整理した。
①デジ庁 DADS 本体 = デジタル庁ウェブサイトのコピーライトポリシー準拠（現行は公共データ利用規約
第1.0版・CC BY 4.0 互換）で翻案・商用可。**義務は出典表示・加工の明示・公式成果物と誤認させない
の 3 点**で、出典 URL を規約の記載例どおり `https://design.digital.go.jp/dads/` に修正し、
文言を「加工して作成」に寄せた。②Material Symbols = Apache 2.0。**現状 SVG 実体を同梱していない
ため再配布が発生しておらず義務は無い**（`icons/ICON-MAP.md` §1 の判断は規約上正しい）。
Google の README は attribution 不要と書いているが Apache 2.0 §4 を上書きするものではないため、
第二段で SVG を同梱する時点でライセンス全文と NOTICE を置く方針は維持。③design-tokens（MIT）=
**トークン実値の再配布が発生していない**ため表示義務なし（上記「トークン実値の出所」参照）。

**案件で使う際の引き継ぎ義務**を README に明記した — 成果物を顧客へ納品するときは出典表示を
成果物側にも引き継ぐ。あわせて **DADS が示すアクセシビリティ適合は改変前の状態に限られ、
本DSは改変済み**であることを注記した（「デジ庁DSベースだから WCAG 準拠」という誤った説明を防ぐ）。

**独立した LICENSE ファイルは置かない**（2026-08-26 判断）。現時点の利用範囲がチーム内に
限られ、免責・社外提供可否まで書くと法務確認が必要になるため。**全社・組織横断へ展開する
時点で LICENSE として切り出す**。それまでは README NOTICE が利用条件の正。

検証: `node scripts/generate-index.mjs --check` / `node scripts/audit-tokens.mjs` /
`node scripts/audit-components.mjs` いずれも OK。

---

### 2026-08-26: wireframe（無彩色）プロファイルの新設 — トークンを「案件別」に加えて「工程別」に分ける

要件定義工程で作るモック（ワイヤーフレーム / ローファイプロトタイプ）を**ブランド色抜き**で
生成できるようにするための追加。起票元は別リポジトリ（デザイン担当者のローカル・本リポジトリからは
参照不可）の検証計画 `docs/MOCK-A1-AB-TRIAL.md` §4。**DS の構成判断としての意味は
「オーバーレイの軸が 1 本（案件）から 2 本（案件 × 工程）になった」こと**。

- **追加物**: `tokens/semantic.wireframe.json`（無彩色差分・6 キー）+ `tokens/config.wireframe.mjs`
  （source: primitive.json → semantic.json → semantic.wireframe.json / 出力 `dist/wireframe/`）+
  `npm run build:tokens:wireframe`。**ベースの `tokens/semantic.json` は直接編集していない**
  （v0.0.7 で確立した「ベースDS の既定値は共有・差分はオーバーレイ」の踏襲）
- **置き場所は `tokens/` 直下**（案件テーマの `examples/` ではない）。wireframe は特定案件の資産ではなく
  **案件をまたいで使うベースDS 側のプロファイル**であり、「実案件のファイルは examples/ に置かない」
  という 2026-08-26 の規約とは別物。この区別は `tokens/HARVESTING.md` の「プロファイル」節に明記した
- **プロファイルは 3 種・重ねない**（base 既定 / wireframe = 要件定義 / project = 設計以降）。
  wireframe と project を同時に積む運用は禁止 — 「色が無いこと」がシグナルである以上、
  中途半端に色が入ると意味が壊れる
- **無彩色の定義 = 操作要素とブランドの色だけを抜く**。上書きは 6 キー
  （primary → gray.700 / primary-hover → gray.900 / primary-subtle → gray.200 /
  on-primary-subtle → gray.900 / brand → gray.900 / focus → gray.900）。
  **意味色（danger / success / warning / info / required）は無彩色化しない** — 状態・エラーの伝達が
  「色 + テキスト併用」のアクセシビリティ規約に依存しており、無彩色にすると規約自体の見直しが要る。
  `canvas` はベースが既に gray.50 のため上書き不要、text / border / surface / table-header /
  surface-hover / neutral-subtle / disabled-* / overlay / skeleton も元から gray 系
- **primitive の追加は不要**（既存の gray 50 / 100 / 200 / 400 / 700 / 900 で足りた）
- **計画案から 1 か所変更（primary-subtle: gray.100 → gray.200）**。計画どおり gray.100 にすると
  **Table 選択行・行 hover（surface-hover）・ヘッダ行（table-header）が完全一致（1.00:1）して
  選択状態が消える**。原因は、ベースDS が選択行を**色相差**で区別していたこと（indigo.50 と gray.100 の
  輝度差は 1.02:1 しかない）— 無彩色化で色相が消えると輝度で作り直すほかない。gray.200 で
  hover 行と 1.13:1・基底面（白）と 1.24:1 の段を付けた。**帰結として Badge の primary と neutral が
  同値（gray.200）になり色分けが消える**が、どちらも意味色を持たない灰であり損失は小さいと判断して
  受け入れた（意味を持つ danger / success / warning の Badge は有彩色のまま残る）
- **コントラスト比（実測・WCAG 2.x 相対輝度）**: primary 面 × 白文字 **10.3:1**（ベースの indigo.600 は
  6.3:1 なので向上）/ primary-hover・brand 面 × 白文字 **17.7:1** / primary-subtle × text **14.3:1** /
  focus × 背景（白）**17.7:1**・× canvas **17.0:1**。focus が primary 面に隣接する場合の差は 1.74:1 で
  非文字 3:1 に届かないが、これは**ベース（focus = primary の同値エイリアスで 1.00:1）と同じ構造**で、
  面とリングの間に background 色の隙間 2px を置く既存規約でコントラストを確保する。無彩色化で
  新たに発生した問題ではない
- **厳密な無彩色（R=G=B）ではない**: primitive の gray 段は一般的な UI パレット由来のクールグレー
  （わずかに青みを含む。gray.900 の HSL 彩度は約 39%、gray.700 は約 19%）。ただしこれらは
  ベースでも text / border / surface が参照している共通の地の色であり、wireframe が持ち込んだ
  逸脱ではない。「操作要素・ブランドの色を抜く」という定義に対しては十分
- **観測対象として残した点（検証で判断する）**: ①選択行の 1.13:1 が実際に読めるか
  （読めなければ primitive に中間段を追加、または色に依存しない併用表現〔行頭の罫線・チェックボックス〕を
  起票）②brand = gray.900 のヘッダ帯が「作り込まれた完成品」に見えてローファイの位置づけを
  損なわないか。①の申し送りは `tokens/ROLE-MAP.md` §1 の末尾に記載した
  （**無彩色のモックでは「面の色だけで状態を伝える」設計を避ける**）

参照を更新した箇所: `AGENTS.md`（ハード制約 — プロファイルの選び方・キー名は共通）/
`tokens/ROLE-MAP.md`（正の参照先 + 面の見分けの申し送り）/ `tokens/HARVESTING.md`（「プロファイル」節を新設）/
`GUIDE-for-designers.md`（フォルダマップ・§3-3・コマンド表・原則）/ `package.json`（v0.0.9・build script）。

検証: `node scripts/generate-index.mjs --check` / `node scripts/audit-tokens.mjs` /
`node scripts/audit-components.mjs` いずれも OK（`tokens/` はハード制約により audit 対象外のため
トークン追加の影響なし）。**参照解決は手動スクリプトで検証**（style-dictionary 未インストール —
開発端末の Cylance Script Control が npm をブロックする既知の制約。base / wireframe /
travel-expense-demo の 3 プロファイルとも token 76 件・semantic 色 31 件で未解決 0 件）。
コントラスト比も同様に手計算スクリプトで算出した。`npm run build:tokens:wireframe` 自体は未実行
（v0.0.x はデータのみ運用のため dist/ 生成は第二段）。

---

### 2026-09-01: audit-ignore 違反化の判定を「mock」ディレクトリ名依存から引数基準へ修正

起票元は L1_Spec_Template 組み込み準備側（別ワークスペース `l1-ds-ui-extraction` の
L1-PLACEMENT.md 残課題①）。L1 の合意でモック出力先が `.aidd/wireframe/<feature>/pages/` に
改名された（mock → wireframe / pages）ため、「audit-ignore 違反化がディレクトリ名『mock』への
名前一致に依存していないか」の確認依頼を受けて調査・修正した。

- **調査結果: 依存していた**。判定は `rel.split(sep).includes("mock")`（検査対象ディレクトリからの
  相対パス中の「mock」セグメント一致）。同一内容のテストファイルで 3 ケースを実行検証した:
  - `pages/` 配下（改名後の呼び出し形）→ **exit 0**。audit-ignore が行単位除外として効き、
    同じ行の hex 直書きも見逃す = audit-ignore と書くだけで合格を偽装できる抜け穴
  - mock/ を含む親ディレクトリを指定 → exit 1（違反化が発火。設計どおり）
  - mock/ 自体を直接指定（スクリプト冒頭コメントが案内していた呼び出し形）→ **exit 0**。
    `relative(target, p)` に target 自身の名前は含まれないため、**改名以前から文書どおりの
    呼び出し方では一度も発火していなかった潜在バグ**（名前一致方式そのものの欠陥）
- **修正（案 A を採用 — 引数の有無で判定）**: 検査対象ディレクトリ引数が渡されたら常に
  strict（audit-ignore の出現自体を違反化）。引数省略 = DS リポジトリ自己監査のときだけ
  従来どおり行単位の除外を許す。DS 自身の監査対象ファイルに audit-ignore の使用実績は
  0 件のため、切り替えによる既存監査への影響は無い。CI（引数なし実行）も無影響。
  代替案だった `--strict` フラグ新設は「フラグを付け忘れると抜け穴が復活する」ため不採用
  （外部監査 = 常時 strict のほうがフェイルセーフ）。実装工程で正当な行単位除外が
  必要になったらフラグ方式を再検討する
- **audit-components.mjs は無影響**（audit-ignore 判定を持たない。解体済み MOCK-STAGE への
  参照コメントのみ更新）

参照を更新した箇所: `scripts/audit-tokens.mjs`（判定ロジック + 冒頭コメント — MOCK-STAGE 参照を
削除し呼び出し例を `.aidd/wireframe/<feature>/pages/` に更新）/ `scripts/audit-components.mjs`
（コメントのみ）/ `GUIDE-for-designers.md` §10（「audit-ignore で個別除外できる」の適用範囲を
DS 自己監査のみと明記）。

検証: 上記 3 ケースを修正後に再実行し、`pages/` 配下・mock/ 直接指定とも exit 1
（audit-ignore 使用 + hex の 2 件検出）に変わることを確認。`npm run ci`
（generate-index --check + DS 自己監査）OK — 自己監査は従来どおり exit 0。

---

### 2026-09-01: アイコン語彙の不足で「画面を作らない」判断が起きた — 起票制に「代替の既定」を明記

利用側（モック生成）で**語彙に無いアイコンが必要になったことを理由に画面の作成そのものを見送る**
判断が発生したという報告を受けて、規定の書き方を修正した。**この判断は妥当ではない**（アイコンを
自作しなかったのは正しいが、停止は過剰適用）。DS 自身の規定から、アイコン不足は画面を止める理由に
なり得ないことが言える:

- **語彙外のアイコンは定義上すべて「装飾」**。ICON-MAP §5 ①がラベル必須（アイコンのみの操作要素を
  作らない）を課し、§2 の判定規則が「文字で書けるなら文字に書いてアイコンは装飾」であるため、
  語彙外のアイコンが欲しくなる場面は必ず可視ラベルが意味を担っている場面 = `aria-hidden` の飾り。
  **省略しても情報は 1 つも落ちない**
- **spec が「必須」にしているアイコンは 2 つだけで、両方すでに登録済み** — Disclosure の `expand`
  と NotificationBanner の `status-*`。Button / Tabs / Pagination はいずれも「アイコンを添える場合は」
  という条件付きの書き方で、Pagination は「先頭・末尾は語彙未登録なのでアイコンを付けない」と
  **「無いなら付けずに作る」を先例として既に書いていた**
- **CI もそれを許している** — `audit-tokens.mjs` が検出するのは記号文字・絵文字による代用のみで、
  アイコンの不在は検出対象外。ラベルのみで組めば違反 0 で通る

**原因は AGENTS.md の文言**（規定の内容ではなく書き方）。ハード制約でアイコンの不足（旧 18 行目）と
部品・パターンの不足（旧 21 行目）が**同一の「作らずに人間へ起票する」で並んでいた**ため、「作らず」の
目的語が画面まで拡大解釈され、`does_not_exist_yet`（捏造防止 = 停止）と同じ強度で読まれた。ICON-MAP §6 も
「使わないもの」の列挙と「起票」だけで、**その場をどう凌ぐかを一言も書いていなかった** — 逃げ道を
明記しない禁止は停止として読まれる、という教訓（REQ-03 の `white` 直書き・ICN 起票時の `✓` 代用が
「規定が無いので代用で凌ぐ」構造だったのと対になる失敗形。**規定はあるが逃げ道が無いので止まる**）。

- **ICON-MAP §6 に「代替の既定」を新設**（種別ごとの表）: **装飾** = アイコンを付けず可視ラベルのみで
  組んで**続行**し「候補」欄に記録して起票（画面の作成・生成を止めない）。**情報**（アイコンだけが分類を
  担う）= 停止して起票 — ただし該当は `status-*` の 4 種のみで全て登録済みであり、新たに該当が出たら
  まず情報をテキスト側へ移せないか §2 の判定規則に立ち返る。「アイコンが無いと成立しない画面は
  §5 ①違反を疑う」も明記した
- **ICON-MAP 冒頭の運用ルールに「起票は作業の停止を意味しない」を追記** — 実際に読まれるのは冒頭の
  3 行なので、§6 だけに書いても同じ事故が起きる
- **AGENTS.md のハード制約を書き分け** — アイコン: 「そのアイコンを作らず、アイコン無し（可視ラベルのみ）で
  組んで作業を続行し起票する。**アイコン不足は画面を作らない理由にならない**」／部品・パターン:
  「作らずに**作業を止めて**人間へ起票する（画面の骨格が作れないため。アイコン不足とは扱いが違う）」。
  停止するものとしないものを同じ文で並べない
- **語彙追加そのものは本ログの対象外**（`edit` / `download` / `print` / `filter` / `menu` 等の正式起票は
  別途。承認までは上記の代替の既定でラベルのみで組む）

参照を更新した箇所: `AGENTS.md`（ハード制約 2 か所の書き分け）/ `icons/ICON-MAP.md`（冒頭の運用ルール・
§2 末尾の未登録リスト・§6 に「代替の既定」新設）/ `GUIDE-for-designers.md` §13-5（AI が画面を 1 枚作る
流れに「語彙に無ければ付けずに続行」を追記）。

**併せて GUIDE の旧記述を修正**（本件の調査中に発見。同じ論点の記述が実態と逆になっていた）:
`GUIDE-for-designers.md` §4-2 の Button spec 紹介表が、a11y 欄を**「アイコンのみのボタンは視覚的に
隠したラベルを必ず含める」と旧文のまま引用していた** — この記述は 2026-08-25 の ICN-05 反映時に
GAP-14（アイコンのみのボタンは作らない）と矛盾するとして spec 本体から削除済みで、**デザイナー向けの
入口ドキュメントだけに 1 年近く残っていた**。現行 spec に合わせて「アイコンのみのボタンは作らない
（可視ラベル必須）+ 44×44・コントラスト 4.5:1・disabled 回避・outline を消さない」に差し替えた。
あわせて同表の「実際に書かれている内容（**全項目**）」という前置きが偽になっていた（spec が起票のたびに
増え、`shape_guidance` / `icon_guidance` / `color_map` / `source` の 4 項目と `never_use_when` の 4 件・
`confusable_with` の 2 件が表に無い）ため「主な項目の抜粋」に改め、載せていない項目を表の直後に列挙した。
**教訓**: spec 本体を直したとき、それを引用している解説ドキュメントは追随しない。引用は全文コピーせず
「最新は spec 本体」と書いておく方が壊れにくい。

検証: `node scripts/generate-index.mjs --check` / `node scripts/audit-tokens.mjs` /
`node scripts/audit-components.mjs` いずれも OK（文書のみの変更で spec・トークンは無変更 —
index.json の再生成不要）。**申し送り**: 配布（v0.0.11）は未実施。利用側リポジトリへ反映するときに
`package.json` のバージョンを上げる。
