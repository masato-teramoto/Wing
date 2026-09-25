# 密度・レイアウト要望 9 件 — 現状調査と対応案（2026-08-25）

> 起票元: mock-trial（travel-expense）DS v0.0.4 反映版（コミット `bfa54b7`）のデザイン担当者レビューで
> 上がった要望 9 件（原文は各 REQ の冒頭に転記）。
> 検討方針（2026-08-24 決定・GAP 起票と同じ）: まずデジ庁デザインシステム（DADS）に該当があるか確認し、
> あれば採取。無い・準備中なら独断で確定せず人間に方針案を提案し承認を得る。
> 調査日: 2026-08-25（DADS 公開ページを参照。日付ピッカー使い方 2025-10-29 更新 / テーブル使い方 2025-06-25 更新 /
> ボタン 2024-09-10 更新 / レイアウト基本 2024-07-31 更新 / チップラベル = 準備中）。
> 対応表・数値の根拠は本ファイルに要点のみ転記し、モック側の状況は別リポジトリ mock-trial の
> `RESULT.md` / `screenshots/bfa54b7/` を参照（**デザイン担当者のローカルにあり、本リポジトリ
> からは参照できない** — 本ファイルへの転記が参照できる唯一の根拠）。
>
> **凡例**
> - **A（採取・着手可）**: デジ庁に公開済みガイドラインがあり、そのまま採取できる。承認不要（内容確認のみ）
> - **B（要承認）**: デジ庁に該当が無い／準備中のため自社翻案、またはトークン追加・パターン改定・既存規定の撤回を伴う。
>   「推奨案」を提示するので、承認・修正を返してほしい
>
> **全体の見立て**: 9 件のうち 6 件（REQ-02 / 04 / 05 / 06 / 08 / 09）は「PC 業務システムとして一画面に情報を詰めたい」
> という同じ動機から出ており、**REQ-02（PC 1 画面収容の原則）を上位方針として先に決めると残りの判断が揃う**。
> デジ庁 DADS は行政の対市民向け Web を主対象にしており、**密度・段組み・幅の使い方に関する規定はほぼ無い**
> （レイアウト基本は 12 カラムグリッドとガター幅の原則のみ。スペーシングトークンも「基準単位 8 CSS px」の原則のみ）。
> したがって本票の大半は自社翻案（B）になる。デジ庁の明文規定と衝突するのは REQ-06 の一部（日付の単一欄入力）のみ。

---

## A. 採取・着手可（0 件）

該当なし。REQ-01 / REQ-07 はデジ庁に「規定が無い」ことを確認済みのため、自社規定の改定として B に分類した。

---

## B. 要承認（9 件）

### REQ-01 Table の見出しセルは常に左揃え（数値列が右揃えでも）— ✅ 2026-08-25 承認・対応完了

> Table `alignment_guidance` を「見出しセルは常に左揃え」に改定。「ラベル = 左揃え / 数値 = 右揃え」を brand-principles.md
> レイアウト原則（揃えの原則）に置き、detail-page の dt・RepeatingFieldGroup の見出し行にも適用。

- **原文**: 「数値が右揃えのときはいいが、ラベルは左揃えにする」
- **発生箇所（モック）**: detail-normal / apply-confirm の旅費明細・経費負担・仮受金の各テーブルで、右揃えの数値・日付列の
  **見出しセル（「日付」「金額」「負担金額」「差額」）も右揃え**になっている
- **現行 DS 仕様（変更対象）**: `components/Table` の `alignment_guidance`
  「ヘッダセルは対応するデータセルと同じ揃え方にする」（2026-08-25 GAP-05 調査時に追記した**自社翻案**）
- **デジ庁**: テーブル使い方に「横方向は値によって左寄せまたは右寄せ。通常は左寄せだが数値や日付等の場合に右寄せとすることがある」
  とあるのみで、**見出しセルの揃えは規定なし**（「ヘッダーセルのテキストは太字」のみ）。→ 現行の「データセルと同じ揃え」は
  デジ庁準拠ではなく自社判断だったので、撤回してよい
- **推奨案**: `alignment_guidance` を「**見出しセルは列の揃え方に関係なく常に左揃え**。データセルは数値・日付・金額のみ右揃え」に改定。
  あわせて detail-page の dl（名前-値）と RepeatingFieldGroup の見出し行（REQ-09）も「ラベルは常に左揃え」を明記し、
  「ラベル＝左揃え、数値＝右揃え」を DS 横断の原則として brand-principles.md か Table spec の 1 か所に置く
- **トレードオフ（判断材料）**: 一般的な DS（Material / Atlassian 等）は数値列の見出しも右揃えにして値との対応を取る流儀が多い。
  左揃え固定にすると幅の広い数値列で見出しと値が離れて見える。列幅を内容相応に絞る（Table `text_overflow_guidance` と併用）ことで緩和できる
- **判断してほしい点**: 見出し左揃え固定の承認

### REQ-02 PC 利用時は「スクロールせず 1 画面に収める」努力をする原則の新設 — ✅ 2026-08-25 承認・対応完了

> brand-principles.md に「レイアウト原則（PC 業務画面）」節を新設（(a) DS に書く (b) 1366×768 第一目標 / 1280×720 最低
> (c) 優先順・禁止手段は推奨案どおり (d) sticky アクション行を許容）。AGENTS.md のハード制約に参照 1 行を追加。

- **原文**: 「もっと一画面に情報を詰めたい。原則 PC 利用の場合はスクロールせずに 1 画面に納まる努力をする」
- **現状**: 各パターンに `density` フィールド（例: form-page「項目間 space-md / セクション間 space-lg」）はあるが、
  **「1 画面に収める」という目標そのものは DS のどこにも書かれていない**。2026-08-18 MK2 指摘（スクロール過多）を受けて
  list-page 行高 md→sm、form-page 2 カラム許容と個別対応してきたが、上位原則が無いため要望が繰り返し上がる構造になっている。
  モック実測（1280px 幅）: form-new は縦約 2,580px（約 3.5 画面分）、detail-normal 約 1,440px、apply-input 約 1,470px
- **デジ庁**: 該当規定なし（レイアウト基本は 12 カラムグリッド・ガター幅「本文文字サイズの 2 倍以上」のみ。1 画面収容の考え方は無い）
- **推奨案**（自社定義。brand-principles.md か新設の横断ガイダンスに置き、各パターンの `density` から参照する）:
  1. **原則文**: 「PC（breakpoint.md 以上）では、1 業務画面の入力・閲覧対象をスクロール無しで 1 画面に収めることを目標にする。
     基準ビューポートは **1366×768（実効高 約 650px）** を第一目標、1280×720 を最低ライン」← 数値は判断点
  2. **収容のために取ってよい手段（優先順）**: ① 余白の縮小（REQ-04 のトークン）→ ② 段組み（REQ-08、最大 4 段）→
     ③ 幅の活用（REQ-05）→ ④ サポートテキストの簡略化（項目ラベルへの統合）→ ⑤ セクションの Tabs 分割（detail-page のみ。
     form-page は Tabs で入力項目を隠さない）
  3. **収容のために取ってはいけない手段**: 文字サイズの縮小（font.size.body 16px を下回らない）、入力欄の高さ縮小による
     ターゲット領域 44px 未満化（デジ庁 Button a11y 準拠）、必須項目の折りたたみ（Disclosure / Accordion で隠す）、
     Textarea の 1 行化、Table の省略表示による情報欠落
  4. **収まらない場合の扱い**: 「収める努力」であり never_do ではない。長大な申請書（旅費精算のように明細 + 報告文を含む）は
     セクション単位でスクロールを許容し、**アクション行（保存 / 確認へ進む）は画面下部に sticky で常時表示**する案を併記
     （sticky アクション行はデジ庁に規定無し → 自社翻案。判断点）
- **判断してほしい点**: (a) 原則を DS に書くこと自体（見た目の正は DS、という運用と整合する） (b) 基準ビューポート値
  (c) 収容手段の優先順と禁止手段 (d) sticky アクション行の採否

### REQ-03 部品ごとに必要な色トークンの不足（ボタン背景・チップ背景ほか） — ✅ 2026-08-25 承認・対応完了

> 推奨案 1〜4・判断点 (a)〜(d) をすべて承認どおり実施。semantic トークン 14 件（on-primary / background / surface-hover /
> primary-subtle #e6f6f7 / danger-hover / danger・success・warning・info-subtle / neutral-subtle / disabled-text / disabled-surface / focus / overlay hex8）
> + `tokens/ROLE-MAP.md` 新設、Badge `variants.color`、Button `color_map`、Table 選択行・hover / NotificationBanner 背景 / ModalDialog オーバーレイの追記、
> audit-tokens の色キーワード・色関数検出を追加。詳細は DECISIONS.md「2026-08-25: REQ-03」。
> Badge primary / danger の文字 × 淡色背景が AA 4.5:1 をわずかに下回る件（約 4.2 / 4.4:1）は、ユーザー承認「前倒してよい」を受けて同日解消 —
> 淡色面上の文字専用トークン `on-primary-subtle`（teal.700・約 5.8:1）/ `on-danger-subtle`（red.700・約 5.9:1）を追加（計 16 件）

- **原文**: 「ボタン背景の色、チップ背景の色など、各部品に必要な色が足りてない」
- **現状（tokens.json の semantic 色 13 件）**: primary / primary-hover / brand / text / text-subtle / border / surface / danger /
  required / success / warning / info / skeleton。**部品の状態・面を表す色が不足**しており、モック側は次の代用で凌いでいる
  （`mock/style.css` 実測）:

  | 部品・箇所 | 本来必要な色の役割 | モックの代用（問題） |
  |---|---|---|
  | Button primary 文字 / 入力欄・ヘッダ・モーダルの背景 | 白（on-primary / 基底面） | `white` キーワード直書き **7 か所**（audit-tokens は hex / px しか検出しないため素通り） |
  | Button secondary 背景・hover | 白面 / hover 面 | surface（灰）を背景に流用。hover 色なし |
  | Button danger hover | danger の濃色 | 規定なし（hover 変化なし） |
  | Button disabled | 無効の文字色・面色 | `opacity: 0.6` で代用（コントラスト非管理） |
  | フォーカスリング | focus 色 | primary を流用（デジ庁実装は専用のフォーカス色を持つ — 第二段で要確認） |
  | Badge（チップ）背景 | variant 別の淡色面 | **border（灰 gray.200）を背景に流用**。primary / danger は文字色のみで背景は同一 |
  | Table 選択行ハイライト | primary 淡色 | 暫定 surface（GAP-05 で第二段送りと明記済み） |
  | Table 行 hover | hover 面 | surface を流用（選択行と区別できない） |
  | NotificationBanner 背景 | type 別の淡色面 | 背景なし（枠線色のみ）— デジ庁 standard スタイルは淡色背景を持つ |
  | ModalDialog オーバーレイ | 半透明の遮蔽色 | text に `opacity: 0.5` |
  | エラーサマリー背景 | danger 淡色 | surface を流用 |

- **デジ庁**: 色の semantic トークンは **Error / Success / Warning / Key の 4 系統のみ**で、面・文字・hover・disabled の役割トークンは
  存在しない（DECISIONS.md トークン対応表に記録済み）。ボタンは「塗り = キーカラー背景 + 白文字 / アウトライン = 白背景 + キーカラー枠線・文字 /
  テキスト = 透明背景 + 下線付きキーカラー文字」で hover・active は「背景・文字が濃くなる + 下線」。チップラベルは**ガイドライン準備中**
  （Figma + 実装のみ）。→ 役割トークンの体系はデジ庁に無いため**自社設計が必要**（プリミティブ選定は第二段でデジ庁へ移植）
- **推奨案**:
  1. **「部品 → 必要な色の役割」対応表を DS に新設**（`tokens/ROLE-MAP.md` 等）し、以下を semantic トークンとして追加（暫定値は既存と同じ
     Tailwind 系プリミティブ。第二段でデジ庁 primitive へ移植）:

     | 追加トークン | 暫定値 | 用途 |
     |---|---|---|
     | `color.semantic.on-primary` | white #ffffff（primitive `white` 新設） | primary Button・塗りチップの文字色 |
     | `color.semantic.background` | white #ffffff | 基底面（入力欄・ヘッダ・モーダル・secondary Button の背景）。surface（gray.50）は「一段沈んだ面」として役割を分離 |
     | `color.semantic.surface-hover` | gray.100 #f3f4f6（新設） | secondary Button hover / Table 行 hover |
     | `color.semantic.primary-subtle` | teal.50 相当（新設・要選定） | Table 選択行 / Badge primary 背景 / info 系の面。デジ庁 key-100 相当 |
     | `color.semantic.danger-hover` | red.700 #b91c1c（新設） | danger Button hover |
     | `color.semantic.danger-subtle` / `success-subtle` / `warning-subtle` / `info-subtle` | 各色相の 50 段（新設） | Badge 背景 / NotificationBanner 背景 / エラーサマリー背景 |
     | `color.semantic.neutral-subtle` | gray.200（= border と同値・別名） | Badge neutral 背景（現状 border を流用している箇所の正規化） |
     | `color.semantic.disabled-text` / `disabled-surface` | gray.400 / gray.100（新設） | Button disabled（opacity 代用を廃止） |
     | `color.semantic.focus` | 要選定（デジ庁実装のフォーカス色を第二段で確認。暫定は primary を明示的にエイリアス） | フォーカスリング |
     | `color.semantic.overlay` | gray.900 の alpha 50%（`$type: color` に alpha を含む表記で可か要確認） | ModalDialog 遮蔽 |

  2. **Badge spec に色 variant を規定**（neutral / primary / danger / success / warning — 背景 = `*-subtle`、文字 = 各 semantic 色。
     枠線なしは維持）。チップラベルはデジ庁準備中のままなので Badge を自社定義で先行させ、公開後に名寄せ
  3. **Button spec に variant × state の色対応表を追記**（primary / secondary / danger × default / hover / disabled / focus）
  4. **運用**: `audit-tokens.mjs` に **色キーワード（white / black / transparent 以外の named color）と rgba()/hsl() 直書きの検出**を追加
     （今回 `white` が 7 か所素通りしていた。transparent は許容）
- **判断してほしい点**: (a) 役割トークンを上記の粒度で追加すること（多すぎる / 足りない） (b) `background`（白）と `surface`（灰）の
  役割分離 (c) Badge の色 variant 化 (d) audit の検出強化

### REQ-04 より狭いスペーシングトークンの追加 — ✅ 2026-08-25 承認・対応完了

> (a) 全パターンの density を 1 段詰め（form-page md→sm / lg→md / sm→xs、detail-page lg→md / sm→xs、list-page lg→md、
> app-shell md→sm、confirm-flow / approval / inbox は追従。report / login / error-page は対象外）(b) `space.xxs` 2px /
> `space.ms` 12px を追加、命名は t-shirt 維持 (c) 二系統化は見送り。

- **原文**: 「もっと一画面に情報を詰めたい。スペーシングの token もっと狭いものも用意すればどうか」
- **現状**: `space.xs/sm/md/lg/xl` = 4 / 8 / 16 / 24 / 40px の 5 段。12px と 2px の段が無く、**sm(8) と md(16) の間が 2 倍飛び**のため
  「md では広い・sm では窮屈」な箇所（項目間・行 padding・セクション見出し下）で選択肢が無い。モック実測で余白が積み上がる箇所:
  ページ padding lg(24) + ヘッダ margin lg(24) + padding md(16) + セクション間 lg(24) + 項目間 md(16) + RepeatingFieldGroup 行 padding md(16)
- **デジ庁**: **スペーシングトークンは存在しない**（「基準単位 8 CSS px」の原則のみ。DECISIONS.md 対応表に記録済み）。
  ただし 8px 基準の半分 4px、1.5 倍 12px は同原則の範囲内
- **推奨案**（2 段構え）:
  1. **まずトークン追加なしで各パターンの `density` を 1 段詰める**（既存トークンで可能。REQ-02 の原則に従い PC 既定を compact 側へ）:
     form-page「項目間 space-md → **space-sm** / セクション間 space-lg → **space-md** / 横並び内 space-sm → **space-xs**」、
     detail-page「セクション間 lg → md / dl 行間 sm → xs」、list-page「セクション間 lg → md」、app-shell「ヘッダと本体 md → sm」、
     RepeatingFieldGroup の行 padding「md → xs（REQ-09 のテーブル状に合わせる）」
  2. **中間段 2 件を追加**: `space.xxs` = **2px**（罫線とテキストの間・チップ内上下）、`space.ms` = **12px**（項目間・セル padding の
     「sm では窮屈、md では広い」箇所）。命名は t-shirt 体系を維持（`xxs` / `ms`）か、デジ庁式の数値名（`space.2` / `space.12`）へ
     全面移行するかは判断点（数値名は将来の追加に強いが既存参照 5 件の改名が必要）
  3. **やらないこと**: density の「comfortable / compact」二系統トークン化（第一弾では PC 既定 = compact 一本にし、必要になれば起票）
- **判断してほしい点**: (a) 既存 density の一律 1 段詰め (b) 2px / 12px 追加と命名 (c) 二系統化を見送ること

### REQ-05 ブレークポイントで規定した幅いっぱいに情報・部品を詰める — ✅ 2026-08-25 承認・対応完了

> (a) app-shell の本体は幅いっぱい・最大幅の上限なし (b) form-page を 4 列グリッドで規定し、単独の短い欄は伸ばさない
> (c) detail-page の dl は md 以上で 2 列許容（confirm-flow ② / approval も追従）。

- **原文**: 「もっと一画面に情報を詰めたい。レスポンシブのために規定している幅いっぱいに情報や部品を詰めてほしい」
- **現状**: `breakpoint.sm/md/lg`（768 / 1024 / 1280px）は v0.0.4 で新設したが、**本体の最大幅・列幅の使い方は未規定**。
  form-page は「1 カラムまたは 2 カラム」までで、モックは単項目 `max-width: 40rem`、ペアも 40rem に収めているため
  1280px 幅では**右側 約 55% が空白**（form-new のスクリーンショット参照）。ページ本体は `max-width: 90rem`（1440px）で中央寄せ
- **デジ庁**: レイアウト基本は 12 カラムグリッド・ガター「本文文字サイズの 2 倍以上」・ブレークポイント 768px のみ。
  コンテンツ最大幅・デスクトップでの幅の使い方の規定なし。InputText 使い方に「入力欄の幅は内容（想定桁数）相応」の原則あり
  （→ 単独の短い入力欄を行いっぱいに伸ばす対応はデジ庁原則に反する。**幅は段組みで埋める**のが整合的）
- **推奨案**:
  1. **本体の最大幅を規定**: app-shell に「本体は breakpoint.lg までは画面幅いっぱい（左右 padding のみ）。lg 以上でも上限を置かず
     幅いっぱいに使う（業務システム前提。中央寄せの余白を作らない）」を追記。上限を置く場合の値（例 1600px）は判断点
  2. **form-page にセクション内グリッドを規定**: 「PC（breakpoint.md 以上）では各セクションを **4 列の共通グリッド**として扱い、
     短い入力欄はグリッドの列に割り付ける（REQ-08）。入力欄の幅は列幅に従う（内容相応の幅 = 列の割当数で表現。金額は 1 列、
     DatePicker 分割入力は 1〜2 列、Textarea / FileUpload は全列）。単項目を 1 列だけ使って残りを空ける場合も列位置は揃える」
  3. **list-page / detail-page**: Table は既に 100% 幅。dl は breakpoint.md 以上で **2 列（名前-値 × 2）** を許容（REQ-08 と同じ動機）
- **判断してほしい点**: (a) 本体最大幅を撤廃（幅いっぱい）とするか上限値を置くか (b) 4 列グリッドで幅を埋める方式（単項目を伸ばさない）
  (c) dl の 2 列化

### REQ-06 PC 想定では日付を年/月/日に分けない — ✅ 2026-08-25 承認・第 1 段対応完了（Consolidated 既定）

> (a) 2 段構えを採用: DatePicker の layout 既定を breakpoint.md 以上 = Consolidated / 未満 = Separated に改定（spec に `responsive`
> 新設）(b) 単一欄 variant はデジ庁逸脱のため今回は追加せず — Consolidated 版モックの評価で不足が残る場合に再起票 (c) PC 境界 = breakpoint.md。

- **原文**: 「PC を想定しているときは、日付を年/月/日で分けない」
- **現状**: `components/DatePicker` は 2026-08-25 GAP-13 で「年 / 月 / 日を分けたテキスト入力」を部品定義そのものとし、
  `never_use_when`「年月日を 1 つの InputText に自由記述させる」、`confusable_with.InputText`「日付は常に DatePicker（3 分割）」と規定。
  v0.0.4 反映でモックの全日付欄を 3 分割へ作り直した結果、**PC で幅と操作数が増えた**（出発日・帰着日・明細日付。明細行では 3 欄が折り返す）
- **デジ庁**: 日付ピッカーは年月日 3 分割の複合部品で、`Consolidated`（**視覚的にはひとつにまとまった年月日フィールド**。キャレットが欄端の
  とき ← → で隣接欄へ移動）と `Separated`（独立した 3 欄）の 2 レイアウト。**PC / モバイルで入力形式を変える規定は無く、単一欄
  （yyyy/mm/dd）入力についての記述も無い**（使い方 2025-10-29 更新）。→ 「分けない」を文字どおり単一欄にするとデジ庁からの逸脱、
  Consolidated なら準拠内
- **推奨案**（2 段構え。まず 1 で要望の意図〔1 欄に見える・素早く打てる・横幅を取らない〕を満たし、不足なら 2）:
  1. **PC（breakpoint.md 以上）の既定レイアウトを `Consolidated` にする**（デジ庁準拠）: 3 欄を 1 つの枠内に「2026 年 08 月 22 日」と
     連続配置し、欄間は ← → と自動でない Tab で移動。視覚的には 1 欄。横幅は単一欄とほぼ同じ。`variants.layout` の既定値を
     「md 以上 Consolidated / md 未満 Separated」に改め、モックはこれで再生成して評価する
  2. **それでも要望が残る場合に限り、自社翻案の `layout: Single`（単一欄）を追加**: input type=text + inputmode=numeric、
     表記例をサポートテキストに明示（「2026/08/22」）、区切り記号の自動挿入はしない（入力中の書き換え禁止と整合）、
     全角・区切り揺れの正規化は送信時 / 確認時。`never_use_when` の「1 つの InputText に自由記述」は「**DatePicker 以外の InputText で**
     日付を打たせない」に書き換え。source に「デジ庁逸脱（PC 業務入力の効率優先）」と明記。calendar=true との併用は不可
     （カレンダーボタンは分割レイアウトのみ）
- **判断してほしい点**: (a) まず Consolidated で評価する 2 段構えの承認 (b) 単一欄 variant をデジ庁逸脱として持つことの可否
  (c) 「PC」の境界 = breakpoint.md（1024px）でよいか

### REQ-07 タブレットで年/月/日に分ける場合は「yyyy年MM月dd日」の順にラベルを付ける — ✅ 2026-08-25 承認・対応完了

> DatePicker spec の `layout` / `a11y` に単位ラベルの接尾配置（Consolidated / Separated 共通）と実装手法（label で包む or aria-label）を追記。
> タブレット（sm 以上 md 未満）は Separated 既定を REQ-06 の切り替えに組み込み。デジ庁実装のラベル位置は第二段で突合（接頭でも接尾を優先）。

- **原文**: 「タブレットのときは日付を年/月/日で分けていいが yyyy 年 MM 月 dd 日のラベル順になるようにする」
- **現状**: DatePicker spec の `layout` に「Separated は各欄に『年』『月』『日』の可視ラベルを持つ」とあるが、**ラベルを欄の前に置くか
  後ろに置くかは未規定**。モックは `年 [2026] 月 [08] 日 [22]`（ラベルが接頭）で実装しており、読み順が「年 2026 月 08 日 22」になっている
  （apply-input-normal のスクリーンショット参照）。要望は `[2026] 年 [08] 月 [22] 日`（ラベルが接尾 = 日本語の日付の読み順）
- **デジ庁**: 使い方ページに並び順は「年 → 月 → 日」の図示のみで、**ラベル位置の明文規定なし**。実装サンプル（Consolidated /
  Separated）でのラベル位置は第二段で HTML 実装を採取して確認する（本票では未確認）
- **推奨案**: DatePicker spec の `layout` に「**単位ラベル『年』『月』『日』は各入力欄の直後（接尾）に置き、全体が
  『yyyy 年 MM 月 dd 日』の読み順になるようにする**。Consolidated / Separated とも同じ。label 要素で入力欄と単位テキストを包む
  （`<label><input …><span>年</span></label>`）か、単位を aria-label に含めて可視テキストは装飾とする」を追記。
  加えて「タブレット（breakpoint.sm 以上 md 未満）は Separated 既定」を REQ-06 の layout 既定に組み込む
- **判断してほしい点**: 接尾ラベル固定の承認（デジ庁実装が接頭だった場合にどちらを優先するか — 推奨は要望どおり接尾。読み順の自然さが理由）

### REQ-08 フォームは PC 利用時に 4 段組みまで許容 — ✅ 2026-08-25 承認・対応完了

> (a) form-page の横並び上限を 2 → 4 項目（4 列の共通グリッド）に改定 (b) md 以上一律 4 列・中間段なし (c) RadioButton / Checkbox は
> 選択肢 3 つ以下 1 列・4 つ以上は 2 列以上か全幅。never_do を「5 項目以上」等へ書き換え。list-page 詳細検索 / confirm-flow ① は自動追従。

- **原文**: 「フォームのときにもっと一画面に情報を詰めたい。PC 利用のときは 4 段組みまで許容。テキストボックス、チェックボックス、Select 等の
  部品を対象とする」
- **現状**: form-page `layout` / `never_do`「3 カラム以上の項目配置（横並びは短い入力項目 2 つまで）」。2026-08-18 MK2 で「意味的な対 2 つ」→
  2026-08-24 チケット 1 で「短い入力欄どうし 2 つ」へ緩和済み。**今回は 2 → 4 への再緩和**（同じ要望が 3 回目。REQ-02 の原則を置いて
  打ち止めにしたい）
- **デジ庁**: フォームの段組みに関する規定なし（1 カラム原則はデジ庁の明文ではなく自社規約 — form-page source に明記済み）
- **推奨案**（form-page 改定。REQ-05 の 4 列グリッドと同一の規定にする）:
  1. **PC（breakpoint.md 以上）: 1 行あたり最大 4 項目**。対象部品 = InputText / Select / Combobox / DatePicker / RadioButton / Checkbox
     （短い入力欄。**Textarea / FileUpload / RepeatingFieldGroup は常に全幅**を維持）。breakpoint.md 未満は 1 カラム（現行維持）。
     中間段（md 以上 lg 未満で 2 列に落とす）を設けるかは判断点 — 推奨は設けず md 以上は一律 4 列（境界を増やさない）
  2. **配置ルール**: セクション内は 4 列の共通グリッドに割り付け、行ごとに列位置がずれないようにする（左揃えの列に沿う）。
     意味的に対をなす項目（発着・期間）は同じ行に隣接させる推奨は維持。1 項目が 2 列以上を占めてよい（DatePicker 分割入力・長めの InputText）。
     RadioButton / Checkbox は選択肢が 3 つ以下なら 1 列、4 つ以上は 2 列以上を占めるか全幅にする（選択肢の折り返しで行が伸びるのを防ぐ）
  3. **エラー表示**: 各項目直下の静的テキストが行の高さを伸ばしても同じ行の他項目の位置はずらさない（RepeatingFieldGroup と同じ規定）
  4. `never_do` を「**5 項目以上の横並び**」「長文入力・添付の横並び」「グリッドの列位置を行ごとにずらす」へ書き換え
  5. **list-page 詳細検索パネル / confirm-flow ① 入力** は form-page 準拠のため自動的に 4 列許容になる（明記のみ）
- **判断してほしい点**: (a) 4 列上限の承認 (b) md 以上一律 4 列（中間段なし） (c) RadioButton / Checkbox の列占有ルール

### REQ-09 旅費明細（RepeatingFieldGroup）の行は枠で囲まずテーブルの行として見せる — ✅ 2026-08-25 承認・対応完了

> (a) `layout_guidance` を枡なし・罫線区切り・見出し行は Table の th と同じ見た目に改定 (b) 削除ボタン最右列（Table の行操作列禁止は
> 閲覧一覧の規定と confusable_with に明記）(c) `states` を新設し row-error = 該当欄の枠線 danger + 行直下のエラーテキスト。

- **原文**: 「旅費明細の 1 行を四角で囲むのでなく、テーブルのように 1 行と明確に分かるデザインがよいのではないか」
- **現状**: `components/RepeatingFieldGroup` の `layout_guidance` は「列を揃えた横並び 1 行表示を推奨（見出し行を伴うテーブルのような見た目に
  なってよい）」まで。**行の枡取り（枠線 / 罫線）の規定が無い**ため、モックは各行を `border + radius + padding md` の**カード状の枡**で
  実装しており（form-new / apply-input のスクリーンショット参照）、見出し行との対応が読みにくく、行 padding が密度も下げている
  （2026-08-18 MK2 の「旅費明細はテーブルで表示が良い」指摘の残件）
- **デジ庁**: 該当部品なし（自社定義部品）。テーブル使い方の「ヘッダーとデータセルは黒いボーダーで明確に区切る / ヘッダーは太字」を
  見た目の参考として転用できる
- **推奨案**（layout_guidance の改定 + states の表現追記）:
  1. **テーブル状レイアウトを既定にし、見た目を Table に揃える**: 各行を枠で囲まず、**行間を罫線（border-bottom = color.semantic.border）
     で区切る**。角丸・行 padding は付けない（セル padding は space-xs〜sm。REQ-04 の詰めと整合）。見出し行は Table の th と同じ見た目
     （太字・caption サイズ・text-subtle・下罫線）。見出しラベルは左揃え、金額列の入力値は右揃え（REQ-01 と整合）
  2. **削除ボタンは最右列**（Table の行操作列禁止は「閲覧一覧」の規定であり、入力中の RepeatingFieldGroup には適用しないことを
     confusable_with に明記）。「+ 行を追加」は最終行の直下・左端
  3. **row-error の表現**: 枠色の変更（枡が無いため不可）に代えて、**該当入力欄の枠線 = danger + 行直下にエラーテキスト**（行の内側で
     高さを吸収）とする。行全体の背景色による強調は danger-subtle（REQ-03）が入ったら任意で許容
  4. **1 行に収まらない場合**: 現行「2 段目へ折り返す」を維持するが、PC では DatePicker を Consolidated（REQ-06）にして折り返しを減らす
  5. 「テーブル状」と Table の境界（読み取り専用 = Table / 入力中 = RepeatingFieldGroup）は現行どおり。見た目が似ても部品は替えない
- **判断してほしい点**: (a) 枡なし・罫線区切りを既定とすること (b) 削除ボタン最右列の扱い (c) row-error の表現変更

---

## トークン追加のまとめ（要承認・すべて暫定値。第二段でデジ庁プリミティブへ移植）

| トークン | 暫定値 | 用途 | REQ |
|---|---|---|---|
| `color.semantic.on-primary` | white #ffffff | primary Button / 塗りチップの文字 | 03 |
| `color.semantic.background` | white #ffffff | 基底面（入力欄・ヘッダ・モーダル・secondary Button 背景） | 03 |
| `color.semantic.surface-hover` | gray.100 #f3f4f6 | secondary Button hover / Table 行 hover | 03 |
| `color.semantic.primary-subtle` | teal 50 段（要選定） | 選択行 / Badge primary 背景（GAP-05 の第二段送り分を前倒し） | 03 |
| `color.semantic.danger-hover` | red.700 #b91c1c | danger Button hover | 03 |
| `color.semantic.{danger,success,warning,info}-subtle` | 各 50 段 | Badge / NotificationBanner / エラーサマリーの背景 | 03 |
| `color.semantic.neutral-subtle` | gray.200（border と同値・別名） | Badge neutral 背景 | 03 |
| `color.semantic.disabled-text` / `disabled-surface` | gray.400 / gray.100 | Button disabled | 03 |
| `color.semantic.focus` | 暫定 primary エイリアス（第二段で確定） | フォーカスリング | 03 |
| `color.semantic.overlay` | gray.900 α50%（表記方法は要確認） | ModalDialog 遮蔽 | 03 |
| `space.xxs` | 2px | 罫線-テキスト間・チップ内上下 | 04 |
| `space.ms` | 12px | 項目間・セル padding の中間段 | 04 |

（`breakpoint` の追加は不要 — 既存 sm/md/lg で REQ-05〜08 の境界は表現できる）

## パターン・spec 改定のまとめ

| 対象 | 変更 | REQ |
|---|---|---|
| Table `alignment_guidance` | 見出しセルは常に左揃え | 01 |
| brand-principles.md（または横断ガイダンス新設） | PC 1 画面収容の原則・手段の優先順・禁止手段 | 02 |
| tokens/ROLE-MAP.md（新設）/ Badge / Button spec | 部品→色役割の対応表、Badge 色 variant、Button 状態色 | 03 |
| scripts/audit-tokens.mjs | 色キーワード・rgba()/hsl() 直書きの検出追加 | 03 |
| 全パターン `density` | 1 段詰め（md→sm / lg→md 等） | 04 |
| app-shell `layout` / `responsive` | 本体の最大幅（幅いっぱい or 上限値） | 05 |
| form-page `layout` / `never_do` / `responsive` | 4 列グリッド・対象部品・列占有・エラー時の行高 | 05 / 08 |
| detail-page `layout` / `responsive` | dl の 2 列許容（md 以上） | 05 |
| DatePicker `variants.layout` / `never_use_when` / `confusable_with` | ブレークポイント別の既定（md 以上 Consolidated / 未満 Separated）、接尾ラベル、（判断次第で）Single 追加 | 06 / 07 |
| RepeatingFieldGroup `layout_guidance` / `states` / `confusable_with` | 枡なし・罫線区切り、削除ボタン最右列、row-error 表現 | 09 |

## 対応状況（2026-08-25 更新）

- ✅ 完了 9 件: REQ-01〜09 — いずれも推奨案どおり承認（ユーザー指示「起票内容の対応を」2026-08-25）。REQ-06 は第 1 段（Consolidated）まで。
  REQ-03（色）は並行作業のうえ同じ変更セットに統合
- 変更ファイル: brand-principles.md（レイアウト原則 新設）/ AGENTS.md（参照 1 行）/ tokens.json（色 semantic 16 件 + primitive 9 段、space.xxs / ms、
  breakpoint.md 説明）/ tokens/ROLE-MAP.md（新設）/ scripts/audit-tokens.mjs / patterns: form-page・detail-page・list-page・app-shell・confirm-flow・approval・inbox /
  components: Table・DatePicker・RepeatingFieldGroup・Textarea・Badge・Button・NotificationBanner・ModalDialog / DECISIONS.md
- 残る判断待ち: REQ-06 第 2 段（単一欄 variant）— Consolidated 版モックの評価後に要否を判断（REQ-03 の Badge コントラストは前倒し解消済み）
- mock-trial 側は v0.0.5 配布後に再生成
- 決定の経緯は DECISIONS.md「2026-08-25: 密度・レイアウト要望 9 件」に記録
