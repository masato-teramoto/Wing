---
doc: styleguide
product: "契約書発行依頼業務対応"
version: "0.3.10"
extracted_at: "2026-09-09"
route: "preset"
preset_origin:                      # プリセットから複製したときだけ持つ（SG が `copied_at` を埋める）
  name: "wing"
  version: "0.3.10"
  copied_at: "2026-10-09"
sources:
  captures:                           # ファイル名だけ（実体は同梱しない）。所在と入手方法は → `note`
    - "照会画面(一覧)_検索.png"
    - "編集画面(詳細)_エラー.png"
    - "メニュー.png"
    - "ZOOM_初期表示.png"
    - "システムエラー.png"
  code:
    - "wing/src/main/webapp/static/vender/kccs/css/commons.css"
    - "wing/src/main/webapp/static/vender/kccs/css/custom.css"
    - "wing/src/main/webapp/static/vender/kccs/css/geframe.commons.css"
    - "wing/src/main/webapp/static/vender/kccs/css/login.css"
    - "wing/src/main/webapp/static/vender/kccs/css/wtg/wtg.css"
    - "wing/src/main/webapp/static/vender/kccs/css/wtg/wtg003/wtgo004.css"
    - "wing/src/main/webapp/static/vender/kccs/css/wtz/wtz001/menu.css"
    - "wing/src/main/webapp/static/vender/kccs/css/zzz/zzz010/zzz010.css"
    - "wing/src/main/webapp/WEB-INF/pages/common/header.html"
    - "wing/src/main/webapp/WEB-INF/pages/common/errorArea.html"
    - "wing/src/main/webapp/WEB-INF/pages/common/pager.html"
    - "wing/src/main/webapp/WEB-INF/pages/common/pageCount.html"
    - "wing/src/main/webapp/WEB-INF/pages/common/emptyMsg.html"
    - "wing/src/main/webapp/WEB-INF/pages/common/waitMsg.html"
    - "wing/src/main/webapp/WEB-INF/pages/common/link.html"
    - "wing/src/main/webapp/WEB-INF/pages/wtg/wtg004/pwtgo008.html"
    - "wing/src/main/webapp/WEB-INF/pages/wtz/wtz001/menu.html"
    - "wing/src/main/webapp/WEB-INF/pages/error.html"
    # --- 実マークアップ 4 本（ボタンの枠の実体を見るため） ---
    - "wing/src/main/webapp/WEB-INF/pages/wtg/wtg002/pwtgo004.html"
    - "wing/src/main/webapp/WEB-INF/pages/wtg/wtg002/pwtgo005.html"
    - "wing/src/main/webapp/WEB-INF/pages/wtg/wtg003/pwtgo006.html"
    - "wing/src/main/webapp/WEB-INF/pages/zoom/zwtz064/zwtz064.html"
    # --- 挙動側の 1 本（カレンダーの開き方の確認。様式の抽出元ではない） ---
    - "wing/src/main/webapp/static/vender/kccs/js/calendar.js  # 参照のみ（挙動の確認・様式の抽出元ではない）"
    # --- 参照した jQuery UI（日付入力の範囲だけ） ---
    - "wing/src/main/webapp/static/plugins/jquery-ui-1.14.1/jquery-ui.css  # 参照のみ（プラグインの既定テーマ・案件の様式ではない）— .ui-datepicker の骨組みだけ"
    - "wing/src/main/webapp/static/plugins/jquery-ui-1.14.1/jquery-ui.theme.css  # 参照のみ（プラグインの既定テーマ・案件の様式ではない）— 色は採らず、面と文字の役割の並びだけ"
  note: "出どころは既存システム **WiNG（建設業務支援システム）** の画面ソース抜粋（上の `captures` / `code` が読んだ範囲。所在は案件側で記録する）。**`captures` は実体を同梱せずファイル名だけを持つ。実体はプリセット（WiNG）に属する資産であり、案件ルート配下にも配布ワークスペース配下にも置かない（生成には使わず、【人】の突合と改訂の起点①でしか引かないため）。所在と入手方法は `README.md`（複製先では `preset_origin.name` から `<配布ワークスペース>/.claude/skills/styleguide-authoring/presets/<preset_origin.name>/README.md`）の「抽出元のキャプチャ（同梱しない）」の節が正である — ファイル名だけを見て案件ルート配下を探さないこと。****方針は既存画面の再現**。コードもキャプチャも在るため §2〜§6 の値は近似ではなく抽出値である。**例外は状態色の補完 3 組**（success / warning / info）— 既存 UI はエラーしか持たないため、**既に在るエラーの 3 値が Bootstrap 3 の alert 系そのもの**（#A94442 / #F2DEDE / #EBCCD1 = alert-danger）である事実に基づき、**同じ体系の残り 3 組をそのまま補完した**（§2 に明示）。jQuery UI はプラグインの既定テーマであり案件の様式ではないため抽出元にしていない（**月次カレンダー本体の様式を書くときに限り `jquery-ui.theme.css` を参照してよい。参照した時点で本欄と sources.code に『参照のみ（プラグインの既定テーマ・案件の様式ではない）』と印を付けて列挙する**）。`help_box.css` は読んだうえで抽出元にしないと判断した（インフォメーション画面専用の表で §2 に無い別パレットを使う）。**複製したら、この欄に案件側で読んだ範囲と、案件の既存画面との突合の結果を書き足す。**"
tokens:
  color:
    brand:
      primary: "#0088CC"            # 見出し・ラベルの面（条件表のラベルセル / 一覧の見出し行）
      primary_hover: "#26A0DA"      # 入力欄の hover 枠（login.css）— 唯一の hover 用の青
      on_primary: "#FFFFFF"         # ブランド面の上の文字
      required: "#FFD700"           # 必須ラベルの文字（labelE の gold）
      accent: "#000080"             # Z ボタン面・リンク（navy）
    surface:
      canvas: "#FFFFFF"             # ページの下地（body に背景指定が無く白）
      card: "#FFFFFF"               # 入力欄・別窓の面
      header: "#FFFFFF"             # グローバルヘッダの面（下辺に border.strong の二重線）
      subtle: "#FFFDDC"             # 条件表・明細表の値のセルの面
      row_odd: "#EEEEFF"            # 一覧のゼブラ（奇数行）
      row_even: "#FFFEFE"           # 一覧のゼブラ（偶数行）
      readonly: "#C0C0C0"           # 読み取り専用の入力欄
      disabled: "#E5E5E5"           # 使用不可の入力欄
      button: "#C0C0C0"             # ボタンの面
      button_disabled: "#DCDCDC"    # 使用不可のボタンの面
      calendar: "#D2691E"           # 既存 UI の INPUT.calendar_button の面（chocolate）。起動ボタンを廃止したため当てる器は無いが、抽出値なので残す（→ §1-1 の「残したキー」）
    text:
      body: "#000000"               # BODY color:black
      muted: "#808080"              # 読み取り専用の複数行入力の文字（gray）
      on_dark: "#FFFFFF"
      link: "#000080"               # a:link / a:visited
      link_hover: "#C71585"         # a:hover / a:active
      disabled: "#6D6D6D"           # 使用不可のボタン・リンクの文字
      current: "#DC143C"            # ページ送りの現在ページ（crimson）— 状態ではない
      watermark: "#BCBCBC"          # 印刷の透かしの文字 — 値は border.disabled と同じ淡い灰（既存 UI 由来）だが役割が違うので別に持つ
      error_title: "#FF0000"        # システムエラー画面の見出し文字（red。抽出元は error.html の `<font color="red">System Error</font>`）
    border:
      default: "#707070"            # 入力欄・select・textarea の枠
      strong: "#4B0082"             # ヘッダ下辺の 4px 二重線
      grid: "#0000FF"               # 表の格子
      subtle: "#E6E6E6"             # 節（fieldset）の枠
      rule: "#696969"               # 区切り線（hr）
      focus: "#000000"              # focus 時の枠
      disabled: "#BCBCBC"           # 使用不可の入力欄の枠
      button: "#F0F0F0"             # ボタンの枠（custom.css の INPUT[type="button"] — 面より明るい色で、立体の光る側を作る）
      button_disabled: "#6C6C6C"    # 使用不可のボタンの枠 — commons.css の INPUT[type="button"].button_disabled
    status:                         # 状態にだけ使う（→ §2 の禁止）。error は抽出値・他の 3 組は補完
      error: "#A94442"
      error_surface: "#F2DEDE"
      error_border: "#EBCCD1"
      error_field: "#FFE4E1"        # エラーのある入力欄の面（mistyrose）
      success: "#3C763D"            # 補完
      success_surface: "#DFF0D8"    # 補完
      success_border: "#D6E9C6"     # 補完
      warning: "#8A6D3B"            # 補完
      warning_surface: "#FCF8E3"    # 補完
      warning_border: "#FAEBCC"     # 補完
      info: "#31708F"               # 補完
      info_surface: "#D9EDF7"       # 補完
      info_border: "#BCE8F1"        # 補完
      error_detail_surface: "#EEE8AA"  # システムエラー画面の明細行の面（palegoldenrod。抽出元は geframe.commons.css の `TD.error_body { background: palegoldenrod }`。§2 の禁止〔状態色を表の本体に使わない〕に対する明示の例外 — §1-1b の #11）
    overlay:
      backdrop: "rgba(30,30,30,0.9)"   # モーダルの背景
  typography:
    family:
      sans: "'ＭＳ ゴシック', 'MS Gothic', monospace"
      ui: "system-ui"               # ログインボタンだけが使う
    size:                           # 既存 UI に在る 3 段だけ（同値埋めをしない → §3）
      body: "10pt"
      subtitle: "12pt"
      title: "18px"
    weight:                         # 既存 UI に在る 2 段だけ（medium は持たない → §3）
      regular: 400
      bold: 700
    line_height:
      body: "normal"                # 既存 UI に指定が無い
      heading: "normal"
      control: "15px"               # ボタン
      confirmation: "22px"          # 確認表示のラベル
    letter_spacing:
      body: "-0.5px"
      label: "-0.8px"
  spacing:
    xxs: "1px"                      # 表の格子
    xs: "2px"                       # セルの内側・小ボタンの左右
    sm: "5px"                       # 区切り線の上下・アイコンの右
    md: "10px"                      # 節の内側・別窓の内側
    lg: "20px"                      # アクション行の上・本文の余白
    xl: "30px"                      # 別窓の左右
  radius:
    none: "0"                       # 既定（入力欄・ボタン・表は角を丸めない）
    sm: "2px"
    md: "4px"                       # 通知だけが持つ
  elevation:
    none: "none"                    # 既定
    inset: "inset 1px 1px 2px 1px rgba(0,0,0,0.5)"   # 入口画面のお知らせ欄
  control:
    height: "22px"                  # ラベルセル・小ボタン・一覧の見出し行
    button_height: "23px"
    button_width: "23mm"            # 既存 UI が mm で持っている（→ §1）。既定の段
    button_width_wide: "30mm"       # 長いラベルの段 — 既存 UI が長いラベルのボタンにインラインで当てている値
    select_height: "19px"
    icon_button: "22px"             # 小ボタン（Z）の高さ
    icon_button_width: "40px"       # 小ボタン（Z）の幅（抽出値は 40×22。22×22 に丸めると根拠を失う）
    icon_menu: "18px"               # 入口画面のリンクの先頭に置く矢印（18×18）
    row_height: "22px"              # 一覧の行
    focus_ring: "1px solid {color.border.focus}"
    button_border: "2px outset {color.border.button}"                    # ボタンの枠 — 既存 UI は border-style を書かず、ブラウザ既定の outset がそのまま立体感になっている
    button_border_disabled: "1px groove {color.border.button_disabled}"  # 使用不可のボタンの枠 — 既存 UI が唯一明示している border-style
    calendar_width: "227px"         # 月次カレンダーの幅 — jquery-ui.css `.ui-datepicker { width: 17em }` を size.body（10pt ≒ 13.3px）で px に換算
    watermark_size: "72pt"          # 印刷の透かしの文字の大きさ — §3 の本文の段ではない（印刷の装飾の寸法）
    error_title_size: "24px"        # システムエラー画面の見出しの大きさ — §3 の本文の段ではない。抽出元 `<font size="5">` の近似値（HTML フォントサイズは実寸を持たないため近似）
    error_detail_height: "400px"    # システムエラー画面の詳細欄の高さの目安 — キャプチャの実測近似値。error.html の静的マークアップに対応する要素が無く、キャプチャだけが根拠
    label_width: "120px"            # ラベルセルの幅の既定の目安（固定はせず内容相応にする — §4-4 A。段は残すが上限としては使わない）
    header_logo_width: "90px"       # ヘッダのロゴの枠の幅 — **固定**。**最終的にロゴ画像（`asset.logo`）が入る幅**で、既存 UI の `<img id="Logo">` と同値。`asset.logo` が `none` の間はシステム名の文字が仮に入り 2 行に折り返すが、**枠は先に確保しておく**（差し替えても本文側のレイアウトが動かないようにするため）。**文字が収まらないことを理由に広げない**（→ §4-10）
    width:                          # 1 行入力欄の幅の段（既存 UI の size 属性由来）
      xs: "37px"
      sm: "81px"
      md: "142px"                   # 既定
      lg: "275px"
      xl: "564px"
    textarea_width: "524px"
    textarea_height: "217px"
  layout:
    viewport_base: "1024x768"       # ヘッダ表の 980px 幅から
    content_width: "980px"          # 本文幅の**既定の段**（ヘッダ表の幅・抽出値）。「上限」とは役割を分けている
    content_max_width: "1480px"     # 本文幅の**上限の段** — **980px に収まらないと画面設計書が判断した画面だけ**ここまで広げてよい。**いちばん広い一覧の表が節の中に収まる幅**まで上げてよい（§4-4 B-3 に値の出し方）
    pairs_per_row: 4                # 条件表の 1 行に置くラベル+値の最大組数（上限。実際の組数は値の幅の段で下げる — §4-4 A）
    column:                         # 一覧の表（§4-4 B）の**列幅の段**。**`control.width`（入力欄の 5 段）とは別の軸**で、列は入力欄より広いことも狭いこともある。**`narrow` / `default` / `wide` は抽出値そのもの**（既存 UI の一覧が列ヘッダのセルごとに割り付けている 105 / 125 / 250px）。**`ordinal` だけは抽出値 25px を使えない**（下）。**段は px で持つ。比率（%）では持てない** — `.list-table` は `width: 100%` なので**合計が 100% でない表はブラウザが比率を保ったまま正規化**し、**同じ段名が表ごとに違う幅になる**（同じ段が表をまたぐと 2 倍以上ちがい、段の大小が逆転することもある）。**px が成立するには `.list-scroll`（表の入れ物）と「余りを吸う列」が対で要る**（§4-4 B）
      ordinal: "42px"               # 序数・チェックボックスなど最も細い列。右寄せの序数は `.list-cell-num`（§4-4 B）。**抽出値は 25px だが、そのままでは使えないことが多い**— **抽出元の見出しは半角 3 文字の `No.` で 25px に収まる**が、**全角混じりの見出しにするとそれ以上要る**。**`.list-header` は `white-space: nowrap`（これも抽出値）なので、25px のままだと見出しが隣の列に食い込んで地続きに読める**。**段は「最も細い列の見出しが `.list-header` の左右の余白 2px × 2 を含めて収まる最小値」を実測して決める**（見出しを折り返す＝25px を保つ案は見出し行の高さが変わり、一覧のある全ページの密度が変わるので採らない）
      narrow: "105px"               # 短いコード・区分・日付・金額（抽出値）
      default: "125px"              # 既定（抽出値）
      wide: "250px"                 # 氏名・名称・備考など長い値（抽出値）
      xwide: "620px"                # 1 セルに入力欄 2 つ + ボタンが入る列（§4-4 B）。**抽出値ではない** — `.field-input-lg` 275px × 2 + 区切り + `.btn-icon` 40px で約 610px 要り、`wide`（250px）の 2.4 倍で既存 4 段のどれにも入らないため**上に 1 段足した**形（4 段の間は作らない）
    gutter: "{spacing.xxs}"
    print_page: "A4 portrait"       # 印刷の用紙
    print_margin: "10mm"            # 印刷の余白
    viewport_target: "1280x800"     # 13 インチノート PC の目安 — **努力目標ではなく「上限の段の根拠」である**（`content_max_width` の初期値はこの値から取っている）。§5 / §8 を見よ
  asset:                            # 既存 UI の画像。値は出どころのパスで、styleguide.css が data: URI に埋め込む（→ §4-10）
    logo: "none"                    # 【差し替え点】WiNG のロゴは在るが別案件のものなので流用しない。**この案件のロゴ**を用意してここにパスを入れる（→ §1-1 の #11）。**枠は `control.header_logo_width`（90px）で先に確保してある**ので、パスを入れるだけで本文側のレイアウトは動かない。**それまでヘッダに見えているシステム名の文字は仮の中身である**
    header_band: "wing/src/main/webapp/static/vender/kccs/img/back_ground.gif"
    menu_arrow: "wing/src/main/webapp/static/vender/kccs/img/menu.gif"
---

# 契約書発行依頼業務対応 — STYLEGUIDE.md

> 位置づけ: **この案件の見た目の正。** 画面設計書・mockup・実装は、色・余白・書体・部品の様式を
> 本書だけから引く。本書は**画面の構成・項目・挙動を決めない**（それは design.md と画面設計書）。
> **版は frontmatter の `version` が正**（ここに数字を書かない — **突合される欄の外に書いた版番号は
> 誰も更新しない**）。変更は版を上げ、mockup の manifest に使用版を記録する。

## 1. 視覚テーマと雰囲気（Visual Theme & Atmosphere）

**本書は既存システム WiNG（建設業務支援システム）から抽出したプリセット `wing` の複製である。**
**この案件自身の既存 UI から起こしたものではない。** よって「この案件に相応しいか」は本書だけでは
判断できず、**突合先は WiNG のキャプチャ**、および**この案件の既存画面**である（複製後に人が突合する）。
**方針は既存画面の再現。**

- **一言で**: **1990〜2000 年代の業務端末の様式をそのまま保っている、表で組んだ高密度・高彩度の管理画面。**
  角丸・影・余白による階層を使わず、**面の色と 1px の格子線だけで構造を見せる**
- **密度**: 一覧・条件表とも**1 行 22px**（`control.row_height`・ラベルセルも同じ 22px）。
  本文は 10pt（≈13px）で、字送りを `-0.5px` 詰めている。条件表は**1 行にラベル+値を最大 4 組**並べ、
  1 画面に 20 項目以上を収める（照会画面のキャプチャは条件 40 項目 + 一覧 14 行が縦スクロールなしで入る）
- **色の使い方**: **ラベルと見出しが面色を持つ**（`brand.primary` = `#0088CC` の面 + 白文字）。
  値のセルは `surface.subtle`（`#FFFDDC` のクリーム）、一覧の行は `#EEEEFF` / `#FFFEFE` の**ゼブラ**。
  表の格子は**青**（`border.grid`）。**面が主役で、文字色で意味を運ばない**
- **既存 UI の癖**（キャプチャとコードから読み取れたもの）:
  - **必須項目はラベルの文字を金色にする**（`brand.required` = `#FFD700`・コードの `labelE`）。
    記号 `*` も「必須」の文言も使わない
  - **ボタンのラベルにアクセスキーを括弧で書く** — `検索(F)` `ｸﾘｱ(R)` `更新(S)` `戻る(C)` `処理状況(L)`
  - **ボタンに階層が無い**。主・副・破壊的の区別がなく**すべて同じ灰色**（`surface.button`）。
    色を持つのは用途が決まった小ボタンだけ（コード検索の `Z` = navy / カレンダー = chocolate）
  - **半角カナを表示文言に使う** — `ﾕｰｻﾞｰ名` `ｸﾞﾙｰﾌﾟ` `ｸﾘｱ` `ﾒｯｾｰｼﾞ` `ｺｰﾄﾞ` `ﾒﾆｭｰ`
  - **書体は 'ＭＳ ゴシック' 固定**で、サイズは pt、ボタンの幅は **mm**（`23mm`）で持っている
  - **参照用の副画面は別のブラウザ窓で開く**（コード検索の ZOOM。画面内のモーダルではない）
  - **グローバルナビが無い。** 画面遷移は**入口画面（メニュー）のリンク一覧**と、各画面のヘッダに置く
    入口へ戻るリンクで行い、現在地はヘッダの `画面名 : [画面番号]画面名` で示す
  - **状態色相当の色が構造に流用されている** — 値のセルのクリーム（`#FFFDDC`）・必須ラベルの金
    （`#FFD700`）・カレンダーボタンの橙（`#D2691E`）。**いずれも状態ではないので `status.*` に入れず、
    役割名で別に持った**（§2 の禁止）
  - **地紋とアイコンを GIF 画像で持つ** — ヘッダ左の淡い水色のグラデーション（`back_ground.gif`）と、
    入口画面のリンクの先頭に置く青い矢印（`menu.gif`・18×18）。**この 2 点は流用する**（`tokens.asset`）

### 1-1. 決めなかったこと・扱いを変えたこと

**本工程が様式を要求するが WiNG に対応物が無かったもの**（11 件・すべて決着済み）。
扱いは SKILL.md「決められない項目の扱い（両ルート共通）」に従う（**skill が決めず、選択肢と推奨を添えて人に返した**）。
**ここに載っているのは WiNG の側の判断**である。**複製した案件でも同じ問いが立つので、そのまま引き継いでよいかを人が確かめる。**

| # | 箇所 | WiNG の状況 | 扱い（決定） |
|---|---|---|---|
| 1 | **グローバルナビ** | **無い**（入口画面 + ヘッダのリンクで遷移する） | **持たせない**（【人】判断・既存画面の再現）。**feature 間の導線は入口画面が担う**（§4-10） |
| 2 | **ナビ項目の現在地** | **無い**（現在地はヘッダの「画面名」） | **持たせない**（同）。現在地はヘッダの `画面名` で示す |
| 3 | **ナビ項目の無効** | **無い** | ナビは持たせないため不要。**入口画面のリンクの無効**（`.app-menu-item-disabled`）で代替する — WiNG の `linkedlabel_disabled` / `*_disabled` の慣行が出どころ |
| 4 | **パンくず** | **無い**（画面名で示す） | **持たせない**（同） |
| 5 | **状態チップ（Badge）** | **無い**（状態は「承認済」「データ変更中」「ドラフト」の文字列をセルにそのまま出す） | **部品を作らない**（§4-6）。状態は文字列で出す |
| 6 | **タブ** | **無い**（照会と編集は同じ画面を URL の `FunctionID` で切り替える） | **部品を作らない**（§4-9） |
| 7 | **成功・警告・情報の通知** | **無い**（`.alert-danger` だけが定義されている） | **補完した**（【人】判断）。既存のエラー 3 値と**同じ体系**から取った（§2 の脚注） |
| 8 | **本文より小さい文字の段 / 24px の段** | **無い**（10pt より小さい指定・18px より大きい指定が無い） | **段を減らした** — `caption` と `display` を落とし、`body` / `subtitle` / `title` の 3 段にした（§3） |
| 9 | **中間の太さ（medium）** | **無い**（normal と bold だけ） | **落とした** — `regular` / `bold` の 2 段にした（§3） |
| 10 | **操作対象の最小寸法** | **無い**（実測 19〜23px で、一般的な下限 44px を大きく下回る） | **持たせない**（既存画面の再現。下限を持ち込むと §1 の密度が崩れる） |
| 11 | **ロゴ** | **既存 UI のロゴは在る** — `vender/kccs/img/greenearth_logo.gif`（608 bytes）を `common/header.html:26` が `<img id="Logo">` で参照している | **置かない。** 在るのは**WiNG のロゴ**であり、**この案件のロゴではない**。地紋（`back_ground.gif`）と矢印（`menu.gif`）を流用したのは**様式に属する装飾**だからで、**ロゴは案件の識別そのものなので流用できない**。`asset.logo` を**差し替え点**として `none` で持ち、**システム名の文字で代替する**（§4-10）。**この案件のロゴを用意できたら `asset.logo` にパスを入れて版を上げる** |

**落としたキー 2 件**（後に §4-13 の新設で役割名のまま戻した）: `text.error_title`（red）と
`status.error_detail_surface`（palegoldenrod）。**出どころが framework のシステムエラー画面
（`geframe.commons.css` / `error.html`）だけ**で、業務画面の様式ではなく、palegoldenrod は警告色相当の色を
表の本体に使った例であるため（§2 の禁止に触れる）と判断した。**システムエラー画面を mockup で表す必要が出たので戻した**（§4-13 / §1-1b の #11）。

**残したキー 4 件**（自己確認 #8 で「当てる器が無い」と分かったが**残す**と判断したもの）:
`layout.pairs_per_row` / `layout.viewport_base`（**器ではなく組み方と基準の値**で、読むのは画面設計書と生成側）/
`radius.sm`（出どころは `wtg/wtg.css` の別系統のボタン）/ `typography.family.ui`（出どころはログインボタン。
対象 feature にログイン画面が無い場合に器が無くなる）。
**原則: 既存 UI から取ってきた値は、案件で使う器が無くても残す**（【人】判断）。
落とすのは**出どころが業務画面の様式でない**と言えるときだけである。
**帰結として次回以降の #8 でもこの 4 件が挙がるが、再検出は誤りではない**（`STYLEGUIDE-backlog.md`）。

**残したキー 5 件目**: **`color.surface.calendar`**（`#D2691E` の chocolate）。
**カレンダーの起動ボタンを廃止した**ため当てる器が無くなったが、
**既存 UI の `INPUT.calendar_button` から取ってきた値なので上の原則どおり残す**。
**次回以降の #8 では参照 0 の 5 件目として挙がるが、これも再検出であって誤りではない。**

**残した「器」1 件目**（**上の原則の初めての器への適用**）: **`.select-readonly`**（§4-3）。
**「編集不可の状態では入力欄の器ごと外す」（`.field-flat`）に変えた**結果、
**`.select-readonly` を当てる場面が無くなりうる**（`.field-input-readonly` /
`.field-textarea-readonly` のほうは**編集できる画面の中の個別の readonly 欄**に残る — §4-2 / §4-3 の「使う場面」）。
**残す**。理由は 2 つ: ① **`.field-input-readonly` と対の段**であり、片方だけ落とすと §4-2 と §4-3 の
状態の並びが食い違う ② **面の値 `surface.readonly`（`#C0C0C0`）は抽出値**で、上の原則により値は残るため、
**値だけ在って器が無い形を新たに作らない**。
**次回以降の #8 では「参照はされるが当てる場面が無い器」として挙がりうる**が、これも誤りではない。

> **台帳（`STYLEGUIDE-backlog.md`）は「反映したが使わなくなった」区分を持たない**ため、
> **本節（値の側の「残したキー」）に器の段を足して受けている。**

### 1-1b. 方針（既存画面の再現）の適用を変えた記録

> **§1-1 は抽出時点の記録**（WiNG に対応物が無かったものをどう扱ったか）で、
> **目視で方針そのものが問われたときの枠が無かった**。**本節がその枠**である。
> **方針を変えたのは人**で、本書は決着を写しているだけである。
> **ここに載っているのは WiNG の側の決着**で、**複製した案件でも同じ問いが立つ**。
> **案件で方針を変えたときは、同じ形で行を足す。**

| # | 件 | 方針に対する向き | 決着（【人】） | 帰結 |
|---|---|---|---|---|
| 1 | **ボタンの立体感** | **再現の強化** | **戻す。** 抽出で `border-style` が落ちていた（§4-1） | ボタンのある全ページの見え方が変わる |
| 2 | **横スクロールをやめる** | **再現の放棄 → 実は再現だった** | **1 行を 2 段に折り返す。** 本文の最大幅をヘッダと同じ 980px に揃えた（§4-4 B / §5 / §8） | 一覧のある全ページ。**読み直しで、2 段折り返しの様式は抽出元の CSS に在ることが分かった**（`custom.css` の `TABLE.list TR.rows2:nth-child(4n+1…4n+4)` = **1 件 2 行のゼブラ** / `pwtgo005` の `ContractList` = **明細 1 件を節 + 入れ子の条件表で段に畳む**）。**放棄ではなく、抽出していなかった様式の追加である** |
| 3 | **0 件でも見出し行を残す** | **再現の是正** | **見出し行だけの表を残し、その外に `.empty-state`**（§4-4 B） | 空の一覧のあるページ |
| 4 | **印刷の A4 様式** | **例外（元に無いものを足す）** | **持つ。**「あった方が親切」（§8） | 印刷ビューの状態ページ |
| 5 | **Draft の透かし** | **例外（元に無いものを足す）** | **持つ**（§4-12）。**§7 の「装飾を作らない」に対する明示の例外**で、色は既存 UI に在る淡い灰と同値を役割名で持つ | 印刷ビューの状態ページ |
| 6 | **月次カレンダーの中身** | **例外（プラグインの既定を参照する）** | **骨組みだけ jQuery UI を参照し、色は案件のトークンに置き換える**（§4-11） | カレンダーモーダルの状態ページ |
| 7 | **小ボタンの寸法** | **再現の是正** | **抽出値 40×22 に戻す**（22×22 は根拠なく丸めた値だった。§4-1） | `Z` を置く全ページ |
| 8 | **ボタンの幅の段** | **再現の是正** | **23mm / 30mm の 2 段にする**（30mm は既存 UI がインラインで当てていた実在の値。§4-1） | 長いラベルのボタンがあるページ |
| 9 | **カレンダーの起動ボタン** | **再現の是正** | **廃止し、日付欄から開く形にする**（既存 UI に起動ボタンの実体が無かった。§4-2 / §4-11） | 日付欄のある全ページ |
| 10 | **並べ替えの印** | **見送り（器を持たせない）** | **入れない。** 画面設計書の AC が並べ替えの印を求めても、**抽出元に実体が無い**（キャプチャの列見出しは素の文字で、リンクでも印付きでもない。CSS・テンプレートの `sort` は jQuery UI の `.ui-sortable`〔ドラッグでの並べ替え〕だけで業務画面では未使用）。**器を作らず、`missing[]` に残したまま次の要求まで持ち越す**（`STYLEGUIDE-backlog.md`） | 並べ替えの操作は画面設計書側の AC には残るが、**mockup は様式を持たないため印を描けない** |
| 11 | **システムエラー画面** | **例外（§2 の禁止への明示の例外）** | **持つ。** 一度落とした `text.error_title`（red）と `status.error_detail_surface`（palegoldenrod）を**役割名のまま戻す**（§4-13）。**抽出元に実物が在る**（`error.html` の赤い見出し + `geframe.commons.css` の `TD.error_label`〔navy/白〕・`TD.error_body`〔palegoldenrod〕+ キャプチャ `システムエラー.png`）。**Draft の透かし（#5）に続く §2 禁止の明示の例外の 2 件目** | シェルのシステムエラー画面の見た目が別物になる |
| 12 | **条件表の `colspan`** | **画面によって答えが違う**（**5 つ目の類型**） | **やめる。** 正確には**「列の格子を行ごとに崩さない」という条件の側で書き直した**（§4-4 A）。**`colspan` そのものを禁じてはいない** | 条件表のある全ページ。**組数の多い条件表では読みにくかった**一方、**組数の少ない画面では同じ組み方が OK だった** — **「抽出元に在る」は採用の十分条件ではない** |
| 13 | **本文幅の上限** | **例外（元に無いものを足す）** | **「既定 980 / 上限」の 2 段にする**（§5 / §8 / §4-4 B-3）。**`content_width`〔980px〕は抽出値のまま既定として残し、上限だけを足した** | 広げると画面設計書が判断した画面。**列の多い一覧がここで収まる** |
| 14 | **編集不可の入力欄** | **方針の変更** | **器（枠と面）ごと外し、値を素の文字で背景に載せる**（`.field-flat`・§4-2）。**新規部品は 0**（`.field-flat` は抽出時から在る） | 編集不可の各状態 + ReadOnly + 印刷ビュー |
| 15 | **ヘッダのロゴ枠** | **前の決着を別の目的で覆す**（**6 つ目の類型**） | **`width: 90px` 固定に戻す**（§4-10）。**前の決着「幅を内容相応にする」を、「将来ロゴを入れても本文側が動かないようにする」という別の目的で覆したもの**で、**どちらの決着も前提の上では正しい**（**前の行と後の行が互いを参照していないと、次に読む人は矛盾する 2 つの決着を見ることになる** — §4-10 に相互参照を張ってある） | 全ページのヘッダ。**システム名の文字が 90px で折り返す**（**承知のうえで選ばれた** — §4-10） |
| 16 | **一覧の列幅** | **再現の是正**（**対の宣言の片落ちを戻す**） | **列ごとに幅の段を割り付ける**（`<colgroup>` + `<col class="list-col-*">`・§4-4 B）。**`table-layout: fixed` を入れたとき、抽出元が対で持っていた「列ごとの幅の割り付け」を見ていなかった** — **`fixed` は列幅を明示するための宣言で、明示しなければ等分される**。**段の 4 値はすべて抽出値**（`pwtgo004` の一覧の 25 / 105 / 125 / 250px） | 一覧のある全ページ。**細い列が等分で広く取られ、広いはずの入力欄の列が潰れる**状態が解消する。**セルを折り返す点だけは抽出元と違える**（抽出元は `nobr` + 横スクロール — #2 の帰結） |
| 17 | **モーダルの中の幅** | **再現の是正** | **パネルの中身の幅（440px）を基準にして段を選ぶ**（§4-7 / §4-2）。**§4-2 の 5 段は本文幅 980px を前提に決めた値**で、**器がモーダルのときの基準が無かった**。**器の保険（`table-layout: fixed`）も抽出元と同じ形**（`pwtgo005` の条件表） | モーダルのある全ページ。**本文幅前提の段を当てると器からはみ出していた** |
| 18 | **モーダルの閉じるの居場所** | **案件側の追加物の是正**（**抽出元に対応物が無い**） | **パネルの上の内側の余白だけを `spacing.lg`（20px）に 1 段上げる**（§4-7）。**`.dialog-close` は「mockup が別窓を開けないから置いた」案件側の追加物**で、**抽出元の参照用副画面は別窓なので閉じるを持たない**（窓の × で閉じる）。**追加物のぶんの居場所を器が確保していなかった** | モーダルのある全ページ。**閉じるが中身に重なっていた** |
| 19 | **一覧の列幅の段の持ち方** | **前の決着の前提が誤りだった**（**7 つ目の類型**） | **段を抽出値の px で持ち**（25 / 105 / 125 / 250px）、**表を `.list-scroll` に入れ、余りを吸う列を 1 本置く**（§4-4 B-1b）。**「px だとページに横スクロールが出るので % にする」という判断**は、**その「横スクロールが出る」という前提が抽出元の読み違いだった** — **抽出元が横に流していたのは表の入れ物（`#freezingDiv` > `.SearchList_list_block`）であって、ページではない**。**【人】判断の文言も「ページごとの横スクロールをやめる」であって、表専用のスクロールを禁じていない**。**「px か横スクロール禁止か」というトレードオフは存在しなかった** | 一覧のある全ページ。**% では同じ段名が表ごとに 2 倍以上ちがい、段が語彙として機能しない**。**px なら段がどの表でも宣言どおりになる**。**ただし `ordinal` だけは抽出値 25px を捨てる**（下の #20） |
| 20 | **`ordinal` の段の値** | **抽出値どうしがぶつかり、人がどちらを捨てるか選んだ**（**8 つ目の類型**） | **段を 25px から上げる**（§4-4 B）。**抽出元の `No.` 列 25px は「見出しが半角 3 文字」の上に成り立つ値**で、**見出しを日本語にすると 25px には収まらない**。**`.list-header` の `white-space: nowrap` も抽出値**なので、**25px と nowrap は両立しない** — **25px のままだと見出しが隣の列に食い込み、隣の見出しと地続きに読める**。**【人】判断は「段を上げる」側** — **見出しを折り返す案（25px を保つ）は見出し行の高さが変わり、一覧のある全ページの密度が変わる**ため。**衝突を生んだのは「見出しを日本語にしたこと」**で、**それ自体は §7 の Do に沿った選択**である。**どちらを捨てても再現から 1 歩離れる**ので、**人が選ぶ以外に決め方が無い** | 一覧のある全ページ。**#16 / #19 と違い、これは「どちらの抽出値を残すか」の選択**である。**#12（画面によって答えが違う）や #15（前の決着を別の目的で覆す）とも別** — **2 つの抽出値が同じ画面で同時に成り立たない**形である |

**#5 / #6 は `sources` に印が要る**（#6 は `sources.code` に「参照のみ」と書いた。#5 は抽出元が無いので本節が唯一の根拠である）。

**#21 — 抽出元に無い作りを足したとき、その作りの器を用意していなかった**:
**① 条件表の入れ物**: **抽出元は溢れたらページごと横に流す作り**だが、**#2 でそれをやめた**。
**一覧には `.list-scroll` を足したが、条件表には足していなかった** — **#12 の `colspan` 撤回で
条件表が横に広がり、節から溢れてページに横スクロールが出ていた**。
**② セルの中の横並び**: **抽出元は `nobr` + 溢れを刈る作り**だが、**#2 で「セルは折り返す」に変えた**。
**折り返しは長い自由文のための決着だったのに、入力欄とボタンにも効いてしまい、狭い列で縦に積まれていた。**
**`.control-group` を足して群の中だけ折り返さないようにした。**
**どちらも「再現をやめた判断」の対の器を作っていなかった形**である（**#16 の「対の宣言の片落ち」と同型**）。
**再現をやめる判断をしたら、その判断が壊す器を対で探すこと。**

### 1-2. 改訂履歴

> **本書は frontmatter に確定の担体を持たない**（画面マップは行の `confirmed`、画面設計書は `status`、
> mockup は `viewed` を持つが、本書には無い）。**この表が担体**である。
> **`確定` は人が `済` に直す。skill は `未` のまま置く。**

| version | 日付 | 起点 | 直した節 | 確定 |
|---|---|---|---|---|
| 0.3.7 | 2026-09-14 | プリセット wing の元版（WiNG から抽出。検証案件で 0.3.0〜0.3.7 の改訂を経て確定） | 全節 | 済（プリセットとして） |
| 0.3.8 | 2026-09-15 | 是正 — frontmatter の 2 値（`layout.content_max_width` 1280 → 1480px / `layout.column.ordinal` 32 → 42px）を本文・`styleguide.css` の値に揃えた（【人】判断。CSS の宣言は不変） | frontmatter・§4-4 B-3 | 済（プリセットとして） |
| 0.3.9 | 2026-09-15 | 是正 — frontmatter に `layout.column.xwide`（620px）を追記し、§4-4 B の `<colgroup>` クラス列挙に `.list-col-xwide` を足した（本文・CSS に在って frontmatter に無かった 3 件目。CSS の宣言は不変） | frontmatter・§4-4 B | 済（プリセットとして） |
| 0.3.10 | 2026-09-15 | 起点① — `sources.captures` の絶対パス（抽出した人の PC 基準で他の環境から解決できない）をファイル名だけに直し、実体の所在と入手方法を `README.md` に移した（台帳 SGB-15 の選択肢②。**同梱はしない**。CSS の宣言は不変） | frontmatter | 済（プリセットとして） |
| 0.3.10 | 2026-10-09 | 初回（プリセット wing 0.3.10 から複製） | 全節 | 済（by: toshiya-fukunaga / recorded_by: aidd-system-design） |

> **複製したら、この表に初回の 1 行を積む** — `| <version> | <日付> | 初回（プリセット wing 0.3.10 から複製） | 全節 | 未 |`。
> 以後の改訂も 1 行ずつ積み、**消さない・上書きしない**。

## 2. カラーパレットと役割（Color Palette & Roles）

| 役割 | トークン | 値 | 使う場面 | 禁止 |
|---|---|---|---|---|
| ブランド | `color.brand.primary` | `#0088CC` | 条件表のラベルセルの面・一覧の見出し行の面 | 状態の意味表示に使わない |
| ブランド（hover） | `color.brand.primary_hover` | `#26A0DA` | 入力欄の hover 時の枠 | 面色に使わない |
| 反転文字 | `color.brand.on_primary` | `#FFFFFF` | ブランド面の上の文字 | — |
| 必須 | `color.brand.required` | `#FFD700` | **必須項目のラベルの文字**（ブランド面の上） | 本文・値に使わない。**警告の意味に使わない**（`status.warning` と役割が違う） |
| 副ブランド | `color.brand.accent` | `#000080` | コード検索（Z）ボタンの面・リンク | 広い面に使わない |
| 下地 | `color.surface.canvas` | `#FFFFFF` | ページ背景 | — |
| 面 | `color.surface.card` | `#FFFFFF` | 入力欄・別窓の面 | — |
| ヘッダ | `color.surface.header` | `#FFFFFF` | グローバルヘッダ（下辺に `border.strong` の二重線） | — |
| 淡面 | `color.surface.subtle` | `#FFFDDC` | 条件表・明細表の**値のセル**の面 | 一覧の行に使わない（そちらはゼブラ）。**警告の意味に使わない**（`status.warning_surface` と役割が違う） |
| ゼブラ（奇） | `color.surface.row_odd` | `#EEEEFF` | 一覧の奇数行 | — |
| ゼブラ（偶） | `color.surface.row_even` | `#FFFEFE` | 一覧の偶数行 | — |
| 読み取り専用 | `color.surface.readonly` | `#C0C0C0` | 読み取り専用の入力欄 | 使用不可と同じ色にしない |
| 使用不可 | `color.surface.disabled` | `#E5E5E5` | 使用不可の入力欄・Select | — |
| ボタン面 | `color.surface.button` | `#C0C0C0` | すべてのボタン | 主・副の区別に色を使わない（§1 の癖） |
| ボタン面（不可） | `color.surface.button_disabled` | `#DCDCDC` | 使用不可のボタン | — |
| カレンダー | `color.surface.calendar` | `#D2691E` | 既存 UI の `INPUT.calendar_button` の面。**起動ボタンを廃止したため当てる器は無い**（値は残す — §1-1 の「残したキー」） | 他の用途に使わない。**警告の意味に使わない** |
| 本文 | `color.text.body` | `#000000` | 本文・値・表のセル | — |
| 補助 | `color.text.muted` | `#808080` | 読み取り専用の複数行入力の文字 | 本文に使わない |
| 反転文字 | `color.text.on_dark` | `#FFFFFF` | 濃い面の上の文字 | — |
| リンク | `color.text.link` | `#000080` | リンク・一覧のリンク列（下線あり） | — |
| リンク（hover） | `color.text.link_hover` | `#C71585` | リンクの hover / active | 面色に使わない |
| 文字（不可） | `color.text.disabled` | `#6D6D6D` | 使用不可のボタン・リンクの文字 | — |
| 現在ページ | `color.text.current` | `#DC143C` | **ページ送りの現在ページの数字だけ** | **エラーの意味に使わない**（状態色ではない） |
| 透かし | `color.text.watermark` | `#BCBCBC` | **印刷の透かしの文字だけ**（§4-12） | 画面の本文・枠に使わない。**状態の意味に使わない** |
| システムエラー見出し | `color.text.error_title` | `#FF0000` | **システムエラー画面（§4-13）の見出しだけ** | 業務エラー（`status.error`）と混同しない。他の見出しに使わない |
| 境界 | `color.border.default` | `#707070` | 入力欄・Select・複数行入力の枠 | — |
| 境界（強） | `color.border.strong` | `#4B0082` | **ヘッダ下辺の 4px 二重線**（画面で最も強い区切り） | 他に使わない |
| 格子 | `color.border.grid` | `#0000FF` | 表の格子線（1px） | 文字色に使わない |
| 境界（淡） | `color.border.subtle` | `#E6E6E6` | 節（`.section`）の枠 | — |
| 区切り線 | `color.border.rule` | `#696969` | 横罫 | — |
| focus | `color.border.focus` | `#000000` | focus 時の枠・outline | — |
| 境界（不可） | `color.border.disabled` | `#BCBCBC` | 使用不可の入力欄の枠 | — |
| ボタン枠 | `color.border.button` | `#F0F0F0` | ボタンの枠。**面（`#C0C0C0`）より明るく、`control.button_border` の `outset` と対で立体感を作る**（§4-1） | 平面の 1px 枠として使わない（立体感が消える — 目視の指摘） |
| ボタン枠（不可） | `color.border.button_disabled` | `#6C6C6C` | **使用不可のボタンの枠**（`control.button_border_disabled` の `groove` と対） | 入力欄に使わない（そちらは `border.disabled`） |
| **エラー** | `color.status.error` / `error_surface` / `error_border` | `#A94442` / `#F2DEDE` / `#EBCCD1` | エラー通知（文字 / 面 / 枠） | **状態以外に使わない** |
| エラー（欄） | `color.status.error_field` | `#FFE4E1` | **エラーのある入力欄の面** | 通知の面に使わない |
| **成功**（補完） | `color.status.success` / `success_surface` / `success_border` | `#3C763D` / `#DFF0D8` / `#D6E9C6` | 完了通知（文字 / 面 / 枠） | **状態以外に使わない** |
| **警告**（補完） | `color.status.warning` / `warning_surface` / `warning_border` | `#8A6D3B` / `#FCF8E3` / `#FAEBCC` | 注意喚起（文字 / 面 / 枠） | **状態以外に使わない**。`surface.subtle` / `brand.required` / `surface.calendar` と混同しない |
| **情報**（補完） | `color.status.info` / `info_surface` / `info_border` | `#31708F` / `#D9EDF7` / `#BCE8F1` | 案内・ヒント（文字 / 面 / 枠） | **状態以外に使わない** |
| システムエラー明細面 | `color.status.error_detail_surface` | `#EEE8AA` | **システムエラー画面（§4-13）の明細行の面だけ** | 業務エラーの面（`status.error_surface`）と混同しない。表の本体〔`.list-table` / `.condition-table`〕に使わない（§4-13 以外は §2 の禁止のまま） |
| 背景（別窓） | `color.overlay.backdrop` | `rgba(30,30,30,0.9)` | モーダルの背景 | — |

**状態色の補完について**（`status.success` / `warning` / `info` の 9 値）: 既存 UI はエラーしか持たない。
ただし**そのエラーの 3 値は Bootstrap 3 の `alert-danger` そのもの**（`#A94442` / `#F2DEDE` / `#EBCCD1`）で、
既存 UI がこの体系から取っていることが特定できる。よって**同じ体系の `alert-success` / `alert-warning` /
`alert-info` の 3 組をそのまま補完した**。**既存 UI の他の色は流用していない**（流用すると色に意味が二重になる）。

- **配色の原則**: **面の色で構造を示し、文字色で意味を運ばない。**
  ラベルは必ず `brand.primary` の面 + 白文字、必須だけラベルの文字を `brand.required` にする。
  値のセルは `surface.subtle`、一覧の行はゼブラで、この 2 つを混ぜない
- **`error` と `warning` の使い分けは「処理を止めるか」で決める**:
  **`error` = 保存・送信を止めるもの**（入力値が条件を満たしていない・取得や更新に失敗した）/
  **`warning` = 止めないもの**（値としては受け付けるが人に確かめてほしい）。
  **入力欄が条件を満たしていないときは `error`（赤）**であり、欄の面も `status.error_field` にする（§4-2）。
  `success` は完了、`info` は案内・ヒントで、どちらも処理の可否を表さない。
  **どの事象がどちらかは画面設計書が決める**（本書は基準だけを持つ）
- **状態色（`status.*`）は状態にだけ使う。** 表のセルの面・ラベル・ページの背景・区切り・用途別ボタン・
  装飾に**状態色を使わない**。逆に、**構造や用途の色を状態の意味に使わない** —
  この既存 UI は `surface.subtle`（クリーム）・`brand.required`（金）・`surface.calendar`（橙）という
  **警告色に似た色を構造と用途に使っている**が、これらは状態ではない。
  **値が似ているだけの別の役割なので、取り違えない**

## 3. タイポグラフィ（Typography Rules）

| 段 | トークン | サイズ / 太さ / 行間 | 使う場面 |
|---|---|---|---|
| 画面タイトル | `size.title` | 18px / bold / `line_height.heading` | **入口画面のメニューの見出し**（`.app-menu-title` — システム名・親メニュー名）。出どころは `linkedlabel_large_menuitem` |
| 小見出し | `size.subtitle` | 12pt / regular / normal | 入口画面のメニュー項目（`.app-menu-item`） |
| 本文 | `size.body` | 10pt / regular / `line_height.body` | 本文・ラベル・表の値・ボタン・ヘッダ・件数表示 |

**行間の段は 4 つ**（`line_height`）:

| 段 | 値 | 使う場面 |
|---|---|---|
| `body` | normal | 本文の既定（`body` セレクタ） |
| `heading` | normal | 入口画面のメニューの見出し（`.app-menu-title`） |
| `control` | 15px | ボタンのラベル（`.btn` / `.btn-disabled` — 高さ 23px の中で 1 行に収める） |
| `confirmation` | 22px | **値を文字として見せるとき**（`.field-flat`）。出どころは既存 UI の `SPAN.label_text_confirmation`（確認画面のラベル）で、**入力欄より行間を広く取る**のが既存 UI の作り |

- **書体**: `'ＭＳ ゴシック', 'MS Gothic', monospace`（既存 UI が全画面で固定している。**等幅の和文ゴシック**）。
  例外は 1 つだけ — ログインボタンが `system-ui`（`family.ui`）
- **段は 3 つだけ。** 既存 UI に 10pt より小さい段と 18px より大きい段が無いため、
  雛形の `caption` と `display` を**落とした**（同値で埋めない）。**本文より小さい段は作らない**
- **太さは 2 段だけ。** 既存 UI に中間の太さが無いため `medium` を**落とした**
- **字送り**: 本文は `-0.5px`、ラベルセルは `-0.8px` 詰める（`letter_spacing`）
- **禁止**: 本文を `size.body` 未満にしない / 明朝体 / 装飾目的の大文字・字間調整 / 段を増やす
- **数値**: 書体が等幅なので桁は自然に揃う。`font-variant-numeric` は使わない（既存 UI に指定が無い）

## 4. 部品の様式（Component Stylings）

> **この節の部品名が、画面設計書と mockup の「部品の語彙」になる。** ここに無い部品は、画面設計書・
> mockup で作らず「STYLEGUIDE.md への追記候補」として記録する。

### 4-1. Button（`class: .btn` / `.btn-wide` / `.btn-disabled` / `.btn-icon` / `.button-area`）

> **ラベルを折り返さない（`white-space: nowrap`）。**
> **`.btn` は幅と高さを固定で持つ**（23mm / 30mm × 23px）**ので、`white-space` が既定の `normal` のままだと、
> 幅に入らないラベルが 2 行に折り返し、`line-height: 15px` × 2 行 = 30px が 23px の箱に入らず、文字が箱の外にはみ出す。**
> **`nowrap` は「折り返さない」ことだけを保証する** — **横にはみ出すかどうかは幅の段の選択の責任**である（下の「幅の段」）。
> **`.btn-wide`（30mm）は抽出値だが、長いラベルが入るかどうかは段の側では保証されない。**
> **文言を決めるのは画面設計書**なので、**入る段が無い文言が来たら段を足すか文言を短くするかを人に返す**
> （**幅の段を 3 つ目に増やすのではなく、文言を短くする側に決着させた例が在る**）。
> **入る文字数の実測**を、ここに残す（**全角 1 文字 = 13.9px**・`ＭＳ ゴシック` 13.3333px）:
> **`.btn`（23mm = 86.9px・中身 83.7px）は全角 6 文字**（83.4px。**余裕 0.3px なので実用は 5 文字**）、
> **`.btn-wide`（30mm = 113.4px・中身 110.2px）は全角 7 文字**（97.3px。**8 文字 = 111.2px で 1.0px 足りない**）。
> **括弧つきのアクセラレータ（半角 3 文字 = 20.1px）を足すなら、その分だけ本体を短くする。**

> **`.btn-icon` はズーム専用ではない。**
> **セルの中に入力欄と並べる短いラベル（1〜2 文字）のボタンはすべてこれを使う。**
> **`<<` / `>>` のような送り操作に `.btn`（23mm = 86.9px）を使うと、狭い列では入力欄と並べられない**
> （**40px なら 入力欄 81px + 40 + 40 = 161px に収まる**）。**ラベルは文字**（アイコンだけのボタンは作らない）という規定は変わらない。

- **形**: 面 `surface.button`、文字 `text.body`、**枠 `control.button_border`（`2px outset` の立体の枠）**、
  **角は丸めない**（`radius.none`）。高さ `control.button_height`、
  ラベルは `size.body` / regular、行間 `line_height.control`、
  **ラベルは箱の中で縦にも横にも中央にそろえる**（**`display: inline-flex` +
  `align-items: center` + `justify-content: center` で寄せる**。`.btn` / `.btn-disabled` / `.btn-icon` の
  **3 つすべて**に持たせる。**§9 #11 の (8) にも挙げてある**）、
  **下線を引かない**（`text-decoration: none` — 遷移を `<a class="btn">` で描いてもボタンの見た目を保つ）、
  **`vertical-align: middle`**（**`.btn` / `.btn-wide` / `.btn-disabled` / `.btn-icon` の
  すべてに持たせる**。mockup の遷移を `<a>`、画面内の操作を `<button>` で描き分けるため、同じ `.btn` でも要素によって
  ベースラインの取り方が違い並べたときに縦がそろわず、`.btn-icon`（22px）は隣の入力欄（22px）より 3px 下にずれて
  下辺からはみ出していた。§4-2 の入力欄・§4-3 の Select にも同じ段を持たせる。§9 #11 の (7) にも挙げてある）
- **幅の段は 2 つ**（**既存 UI が実際に持っていた 2 値**で、どちらも mm である）:
  **既定 = `control.button_width`（`23mm`）/ 長いラベル = `control.button_width_wide`（`30mm`・`.btn-wide`）**
  - **判断基準**: **ラベルが `23mm` に収まらないときだけ `.btn-wide` にする。**
    目安は**全角 5 文字（アクセスキーの括弧を含めて 8 文字）を超えるとき**で、既存 UI の 23mm 側は
    `検索(F)` `ｸﾘｱ(R)` `更新(S)` `戻る(C)`、30mm 側は `契約支払情報変更` `文書ﾌｧｲﾙ登録` `契約支払情報参照` である
  - **中間の幅・内容相応の幅を作らない**（段は 2 つだけ。§4-2 の幅の段と同じ考え方）。
    **それでも収まらないラベルは、幅ではなく文言を短くする**（**文言の正は画面設計書**）
  - **アクション行の中では段を混ぜてよい**（既存 UI も 23mm と 30mm を同じ行に並べている）
- **立体感は `border-style` が持つ。** **既存 UI はボタンに `border-style` も `border-width` も書いておらず、
  `input[type="button"]` のブラウザ既定（`2px outset`）がそのまま立体感になっている**
  （`commons.css` の `INPUT.button` は面・寸法・行間だけ、`custom.css` 側の上書きも `border-color` だけ）。
  **枠の色が面より明るい**（`border.button` = `#F0F0F0` に対し面は `#C0C0C0`）ため、
  **光る側と影の側が自動で分かれる**。**平面の 1px 枠に置き換えない**
- **種類は 1 つだけ。** **主・副・破壊的の区別を色で表さない**（§1 の癖 — 既存 UI に階層が無い）。
  どのボタンを目立たせるかは**並び順**で表す（`.button-area` の左から）
- **用途が決まった小ボタンは 1 つだけ**（**`control.icon_button_width` × `control.icon_button` = 40×22**・bold・白文字・
  **枠は `.btn` と同じ `control.button_border`**・**内側は左右 `spacing.xs`（2px）**（
  抽出元の `INPUT.zoom_button_open` の `padding-right/left: 2px` に合わせる）:
  **`.btn-icon`** = **参照・照会の副画面の起動**（面 `brand.accent`・**ラベルは `Z`**）。
  マスタのコード検索だけでなく、**外部への照会を別画面で開く場合も同じボタンで表す**
  （既存 UI は参照系の副画面を 1 種類の起動ボタンで開いており、**新しい部品を作らない**）
- **カレンダーの起動ボタンは持たない。** **既存 UI に実体が無かった** —
  `INPUT.calendar_button`（chocolate・40×22）は CSS に定義だけ在り**テンプレート 34 本のどこからも使われておらず**、
  **カレンダーは日付欄そのものから開く**（日付の入力欄に `calendar` の印を付け、focus で開く — `calendar.js`）。
  **日付欄の様式は §4-2（`.field-input-date`）・カレンダー本体は §4-11** に置いた。
  **`surface.calendar`（chocolate）は使う器が無くなったが、既存 UI から取った値なので残す**（§1-1 の「残したキー」）
- **状態**: focus（`control.focus_ring` の outline）/ disabled（`.btn-disabled` — 面 `surface.button_disabled`・
  文字 `text.disabled`・**枠 `control.button_border_disabled`（`1px groove`）**・カーソル既定・押下不可）。
  **既存 UI が `border-style` を明示しているのは使用不可だけ**で、`groove` はへこんだ見え方になる。
  **hover は持たない**（既存 UI に無い）
- **アクション行（`.button-area`）**: ボタンを横に並べる行。**左寄せ**・上に `spacing.lg` の間隔
  （**どのボタンを置くかは画面設計書が決める**。本書は並べ方の様式だけを持つ）
- **使う場面**: ラベルに**アクセスキーを括弧で付ける**（`更新(S)` の形 — §1 の癖）。
  **ラベルが `23mm` を超えるときは `.btn-wide`**（それでも収まらなければ**文言を短くする** — 操作名の正は画面設計書）
- **禁止**: 押下時の scale・transform / 角を丸める / 色で主副を表す / アイコンだけのボタン（`Z` は文字ラベル）/
  **下線を引く** / **幅の段を増やす**（2 つだけ）/ **カレンダーの起動ボタンを作る**

> **「要素どうしの縦位置」と「要素の中の文字の縦位置」は別物である。**
> **`vertical-align: middle` が揃えるのは前者**で、**後者は `height` と `line-height` の関係**である。
> **実測**: `.btn` / `.btn-disabled` は**高さ 23px に対し行間 15px**、`.btn-icon` は**高さ 22px に対し行間の宣言が無い**
> （`body` の `normal` を継承）。**`display: inline-block` は行ボックスを箱の上端に置く**ので、**余りが下に残る**。
> **既存 UI では起きない** — `<input type="button">` の値の文字は**ブラウザが縦中央に置く**ため、
> 抽出元の `INPUT.button { line-height: 15px }` は**位置を決めていなかった**。
> **mockup は遷移を `<a>`、画面内の操作を `<button>` で描く**（§9 #11 の (7)）ので、**宣言しないと寄らない**。
> **`line-height` の抽出値（15px）はそのまま残す** — 中央寄せにすると行ボックスの位置を決めなくなるので、
> **抽出元と同じく「位置を決めない値」に戻る**だけである。
> **「ボタンががたがた」「`[Z]` が下にずれる」は `vertical-align` と行ボックスの 2 つの原因を持つ** —
> **同じ見え方をする別の原因が残りうるので、原因の特定を「1 つ見つけたら終わり」にしない。**

> **抽出元を読み直したときに、寸法のずれが 3 件見つかり、3 件とも【人】判断で「抽出元に合わせる」側に決まった**:
> ① **小ボタンを 22×22 → 40×22 に戻した**（正方形は根拠なく丸めた値だった）
> ② **幅の段を 23mm / 30mm の 2 つにした**（30mm は既存 UI がインラインで当てていた実在の値）
> ③ **カレンダーの起動ボタンを廃止した**（既存 UI に実体が無く、日付欄から開くのが元の作り）。
> **①は `.btn-icon` の内側の余裕も同時に解消する**（`2px outset` で 4px 狭くなっていた分）。

### 4-2. 入力欄 Field（`class: .field-input` / `.field-input-xs` / `.field-input-sm` / `.field-input-lg` / `.field-input-xl` / `.field-input-error` / `.field-input-readonly` / `.field-input-disabled` / `.field-input-date` / `.field-flat` / `.field-textarea` / `.field-textarea-readonly`）

- **形**: 面 `surface.card`、枠 1px `border.default`、**角は丸めない**、内側 `spacing.xs`、
  書体は `family.sans` / `size.body`、**`vertical-align: middle`**（§4-1 の参照）。
  **ラベルは入力欄の上に置かない** — 表のラベルセルが左隣に来る（§4-4）
- **幅の段（`control.width` の 5 段）**: 内容相応にする。既定は `md`（142px・`.field-input`）、
  `xs`（37px・枝番・区分などの短いコード）/ `sm`（81px・日付・金額）/ `lg`（275px・氏名・名称）/
  `xl`（564px・住所・長い名称）。**段は 5 つだけで、中間の値を作らない**
  - **この 5 段は `layout.content_width`（980px）の本文に置くことを前提に決めた値である。**
    **器が本文より狭いところ — §4-7 のパネル（中身 440px）— では、入る段までしか当てない。**
    **`xl`（564px）と複数行入力（`control.textarea_width` 524px）はパネルに入らない**（§4-7 の「中身の幅」）
  - **`table-layout: fixed` の表の中では、`max-width: 100%` がセル幅まで縮める**（`.list-table` / パネルの中の
    `.condition-table`）。**`auto` の表の中では効かない** — **セルのほうが中身に合わせて先に広がるため、
    `100%` の基準そのものが広がる**。**縮んだ見え方は「段を選び違えた」印であって、
    段の代わりではない**
- **状態**:
  - focus — 枠を `border.focus` にする（`outline: none`）
  - **error（`.field-input-error`）— 面を `status.error_field` にする**（枠は変えない。既存 UI の `errors-control`）。
    **このクラスは面の色だけを持つので、複数行入力（`.field-textarea`）にも併記して当てる**
    （専用のクラスを作らない。既存 UI の `errors-control` も要素を選ばない）
  - readonly（`.field-input-readonly`）— 面を `surface.readonly` にする。
    **当てるのは「編集できる画面の中の、その欄だけ入力できない」場合だけ**（下の「使い分け」）
  - disabled（`.field-input-disabled`）— 面 `surface.disabled` + 枠 `border.disabled`
  - hover — 枠を `brand.primary_hover` にする
- **値の表示（`.field-flat`）**: 枠なし・面は透明、**行間は `line_height.confirmation`（22px）**。
  **入力できない値を文字として見せる**ときに使う
  （既存 UI の `flat_label` + 確認表示の行間 `SPAN.label_text_confirmation`。
  読み取り専用の入力欄とは見た目で区別する）
  - **使う場面**: **画面ぜんぶが編集できない状態**では、
    **入力欄の器（枠と面）を外し、値を素の文字として背景に載せる。**
    対象は**編集不可の状態・ReadOnly・印刷ビュー**で、**Select も同じく `.field-flat` にする**
    （選べないものを選択欄の形で見せない）。**新しい部品は増えない**

> **「編集不可」と「readonly」の使い分け（【人】判断による方針変更）**
>
> | | 当てるもの | 見え方 | 例 |
> |---|---|---|---|
> | **画面ぜんぶが編集できない** | **`.field-flat`** | **器ごと無い。値が素の文字で背景に載る** | 申請後・承認後などの編集不可の状態 / ReadOnly / 印刷ビュー |
> | **同上・ただし Checkbox** | **`.checkbox` のまま + `disabled`** | **器（□）は残る**（**真偽値を文字で見せる器が無い**） | 同上（**印刷ビューを外さない**） |
> | **編集できる画面の中の、その欄だけ入力できない** | **`.field-input-readonly` / `.field-textarea-readonly` / `.select-readonly`** | **器は残り、面が灰色になる** | 他の操作（検索・読み込み）の結果として値が入る欄 |
>
> **見分けの基準は「その画面に、いま入力できる欄が他に在るか」である。**
> **他に入力できる欄が在るなら器を残す** — **器を外すと「ここは欄だが今は入れられない」という情報が消える**ためで、
> **§4-2 が元から「読み取り専用の入力欄とは見た目で区別する」と書いていた区別がこれである**。
> **他に 1 つも入力できないなら器を外す** — **画面ぜんぶが灰色の欄で埋まると、何が値で何が器か読めなくなる**。
>
> **この区別は目視で方向そのものが変わった決着である**（**当初はどちらも `.field-input-readonly` 系で描いていた**）。
> **`.select-readonly` は当てる場面が無くなることがあるが残す**（§1-1 の「残した器 1 件目」）。
- **複数行（`.field-textarea`）**: 幅 `control.textarea_width`、高さ `control.textarea_height`、
  **縦スクロールを常に出し、リサイズさせない**（既存 UI の `overflow-y: scroll; resize: none`）。
  読み取り専用（`.field-textarea-readonly`）は文字を `text.muted` にする
- **参照ボタンの置き場**: **`.btn-icon` は入力欄と同じセルに、入力欄の直後に置く**
  （§4-4 A の値セルの中）。**新しい器は作らない** — 既存 UI も入力欄と同じ親要素に置いており、
  ズームの起動は親をたどって対の入力欄を見つける作りである（`common/zoomForm.html`）
- **日付欄（`.field-input-date`）**: **見た目は `.field-input` と同じで、幅の段も変えない。**
  違いは**押すと月次カレンダー（§4-11）が開く**ことだけで、**起動ボタンを横に置かない**
  （既存 UI は日付の入力欄に `calendar` の印を付け、**focus でカレンダーを開く**）。
  カーソルは指し手（`cursor: pointer`）にして、押せることを見せる。
  **書式は `yyyy/MM/dd`**（§7 の表記）。**幅の段は内容相応** — 既存 UI は日付欄だけ 4px 広く取っているが、
  **本書は 5 段に丸めているので段を増やさない**（§4-2 の禁止）。
  **ダイアログ・モーダルの中では当てない**（直接入力にする。§4-11 の「使う場面」を参照）。
  **静的な mockup での表し方は §9 #11 の (6) / #14**
- **禁止**: 角を丸める / エラーを入力欄の外にだけ出す（面色も変える）/ 幅の段を増やす /
  **参照ボタンを入力欄と別のセル・別の行に置く**

### 4-3. Select / Checkbox / Radio（`class: .select` / `.select-readonly` / `.select-disabled` / `.checkbox` / `.radio`）

- **形**: Select は高さ `control.select_height`（**19px — 入力欄の 22px より 1 段低い。既存 UI がそうなっている**）、
  枠 1px `border.default`、幅は §4-2 の段に従う（既定 `md`）、**`vertical-align: middle`**（§4-1 の参照）。
  Checkbox / Radio は**ブラウザ既定の寸法のまま**（既存 UI に寸法の指定が無い）
- **状態**: focus（Select は枠を `border.focus`・Checkbox / Radio は `control.focus_ring` の outline）/
  readonly（`.select-readonly` — 面 `surface.readonly`。**当てるのは「編集できる画面の中の、その欄だけ選べない」場合だけ**
  — §4-2 の「使い分け」を見よ）/
  disabled（`.select-disabled` — 面 `surface.disabled` + 枠 `border.disabled`）
- **使う場面**: 選択肢が固定されるものは Select、行ごとの真偽は Checkbox、二者択一の対は Radio。
  **画面ぜんぶが編集できない状態では Select も `.field-flat` にする**（選べないものを選択欄の形で見せない）
- **画面ぜんぶが編集できない状態の Checkbox**: **器（□）のまま残し、`disabled` を当てる。**
  **`.field-flat` には合流させない** — **`.field-flat` は値を文字で見せる器で、真偽値の表し方を持たない**ためである。
  **対象は編集不可の状態・ReadOnly・印刷ビューのすべて**（**印刷ビューを外さない**）。
  - **Select を `.field-flat` にした理由〔選べないものを選択欄の形で見せない〕は Checkbox にも当てはまるが、
    人は「器のまま」を選んだ** — **真偽値は「□ か ☑ か」でしか読めず、文字にすると別の語彙が要る**ためである
  - **見え方はブラウザの既定に任せる**（§4-3 の形 —「Checkbox / Radio はブラウザ既定の寸法のまま」）。
    **`.checkbox` に無効の段のクラスを作らない**（**新しい部品は増やさない**）
  - **画面設計書側にも書く**: **§4-3 に書くだけでは mockup に届かない** — **印刷ビューだけ `disabled` が
    当たっていない、という取りこぼしが実際に起きた**。**状態ごとの適用は画面設計書 §3-x-5 が書く**
- **禁止**: **操作対象の寸法の下限を持ち込まない**（§1 の #10 — 既存 UI が 19〜22px で組んでおり、
  下限を入れると §1 の密度が崩れる。**既存画面の再現を採る**）/ Select を入力欄と同じ高さにする

### 4-4. 表 — 2 種（`class: .condition-scroll` / `.condition-table` / `.condition-label` / `.condition-label-required` / `.condition-value` / `.list-table` / `.list-scroll` / `.list-caption` / `.list-header` / `.list-row` / `.list-row-2` / `.list-cell` / `.list-cell-num` / `.list-col-ordinal` / `.list-col-narrow` / `.list-col-default` / `.list-col-wide` / `.list-col-xwide` / `.control-group`）

> **この案件の「フォーム」は表である。** 入力項目はラベルセルと値セルの対を表に並べて作る（§4-2 参照）。

**A. 条件・入力の表（`.condition-table`）** — 検索条件・入力フォームの器

- **形**: 面を `border.grid` にし `border-spacing: {spacing.xxs}` を取ることで**青の格子線**を見せる
  （枠線ではなくセル間の隙間で線を作る、既存 UI の作り）
- **ラベルセル（`.condition-label`）**: 面 `brand.primary`、文字 `brand.on_primary`、
  高さ `control.height`、折り返さない、字送り `letter_spacing.label`。
  **幅は内容相応**（**既存 UI はラベルごとに幅をインラインで割り付けている**
  〔`TD.label { width:120px }` は既定のクラスだが、実マークアップは `110px` / `120px` などラベルの文言に応じて違う〕。
  `control.label_width`（120px）は**既定の目安**として残すが、固定はしない
- **必須のラベルセル（`.condition-label-required`）**: 上と同じで**文字を `brand.required`（金）**にする。
  **必須はこれだけで示す**（記号 `*` も「必須」の文言も使わない — §1 の癖）
- **値セル（`.condition-value`）**: 面 `surface.subtle`、内側 `spacing.xs`。
  **幅は内容相応**（既存 UI は値セルも項目ごとに幅を割り付けている
  〔`150px` / `180px` / `210px` など〕。**§4-2 の入力欄の幅の段（`xs`〜`xl`）に合わせて広げる**）
- **列の格子を行ごとに崩さない**（**「列をぶち抜く」という一度入れた様式を撤回したもの**）:
  **同じ表の中で、行によって列の境目の位置が変わる組み方をしない。**
  **長い値（`lg` / `xl`）を含む行は、`colspan` で残りをぶち抜くのではなく、その行に置く組数を減らす**
  （**右側は空けたままにする**）。**行の高さも列の位置もそろったまま、組数だけが行ごとに変わる**形になる
  - **`colspan` そのものを禁じてはいない。** **表のどの行も同じ格子になるなら使ってよい**
    （例: **1 行 1 組で組んだ表**）。**禁じるのは「ある行だけ境目が消える」こと**である
  - **撤回の理由**: **「抽出元が実際にこの形で組んでいる」ことを確かめて一度は入れた**
    （1 ファイルに 17 箇所・`TD.label` の隣に `colspan="3"` の値セルを置く形）。
    **方針〔既存画面の再現〕には忠実だった**が、**組数の多い条件表では読みにくく、組数の少ない画面では
    同じ組み方が OK だった**ので、**「やめる」ではなく条件の側で書いた**。**§1-1b の #12（画面によって答えが違う）**
- **並べ方**: **1 行に置く組数は、値の幅の段の合計が
  その画面の本文幅に収まる範囲で決める。** **基準の幅は `layout.content_width`（980px）で、
  収まらない画面は `layout.content_max_width`（1480px）まで広げてよい**（§4-4 B-3 / §5）。
  目安 — `xl` を含む行は 1 組 / `lg` を含む行は 2 組 / `md` 以下だけの行は最大 `layout.pairs_per_row`（4）組。
  **`pairs_per_row` は上限として残すが、下回ってよい。**
  **どの項目を同じ行に置くか・組の順序・1 行に何組並べるかは画面設計書のレイアウト節（§3-x-2）が決める**
  （本書は「入る範囲」の基準だけを持つ）

**A-1b. 表の入れ物（`.condition-scroll`）**

- **条件表は `<div class="condition-scroll">` に入れる。** `.condition-scroll` は `overflow-x: auto` だけを持つ。
  **§4-4 B の一覧には `.list-scroll` が在るのに、条件表の側には入れ物が無かった**
- **なぜ要るか**: **`.condition-table` は `table-layout: auto` で幅の宣言を持たない**ので、**中身の最小幅まで広がる**。
  **しかも列幅は行をまたいで共有される** — **`xl`（564px）を 1 組だけ置いた行が在ると、`colspan` を使わない限り
  その `xl` は 2 列目に居座り、同じ表の 4 組の行の 2 列目まで 564px にされる**
  - **帰結**: **1 組しか置いていない行の `xl` が、同じ表の他の行の 2 列目の幅を決める。**
    **表は節の内側を超え、節を突き抜けてページに横スクロールが出る**（**狭いビューポートほど溢れが大きい**）
  - **この溢れは `colspan` を撤回したときに入った** — **`colspan` を使っていた間は `xl` の行が行の残りをぶち抜いており、
    2 列目は広がらずに済んでいた。** **同じ改訂で本文幅の上限も広げたため溢れが小さく見え、目視を 2 回通り抜けた** —
    **「別の変更が症状を隠す」形なので、撤回と同時に対の器を探すこと**（§1-1b の #21）
  - **§4-5 の `.section` の `min-width: 0` は節が中身の幅まで膨らむのを止めるが、
    表そのものが節から溢れるのは止めない**
- **§4-4 A の「並べ方」の目安は 1 行ずつで考える基準**（`xl` を含む行は 1 組 / `lg` は 2 組 / `md` 以下は 4 組）で、
  **この列の共有を考慮していない** — **目安どおりに組んでも溢れる。** **溢れたぶんは入れ物の中だけで流す**
  （**ページは動かさない** — §5 の但し書き / §9 #13）
- **モーダルの中の条件表は溢れない**（§4-7 が `width: 100%` + `table-layout: fixed` に固定している）が、
  **入れ物は同じに包む**（包んでも挙動は変わらず、条件表の描き方を 1 つに保てる）
- **どの項目を同じ行に置くか・組数をいくつにするかは画面設計書のレイアウト節（§3-x-2）が決める**（本書は入れ物だけを持つ）。
  **溢れを減らしたければ組み方の側でも減らせる**（`xl` を単独の表に分ける・組数を減らす）

**B. 一覧の表（`.list-table`）** — 明細の表示

- **形**: `.condition-table` と同じ格子の作り。行高 `control.row_height`。
  **幅は器いっぱい**（`width: 100%` + `table-layout: fixed`）— **横スクロールをやめた帰結**
- **列幅は列ごとに割り付ける**（**段は px で持つ**）:
  **`table-layout: fixed` は「列幅を明示するための宣言」**であり、**明示しなければ列数で等分される**。
  **`<colgroup>` に列の数だけ `<col>` を置き、`layout.column` の段のクラスを当てる**
  （`.list-col-ordinal` / `.list-col-narrow` / `.list-col-default` / `.list-col-wide` / `.list-col-xwide`）。
  - **段は 5 つで、中間の値を作らない**（§4-2 の入力欄の 5 段と同じ考え方。**ただし別の軸**である —
    列は入力欄より広いことも狭いこともある）
    - **`xwide`（620px）は 5 つ目の段**で、**抽出値ではない** —
      **1 つのセルに入力欄が 2 つ + ボタンが 1 つ入る列**（`.field-input-lg` 275px × 2 + 区切りの記号 +
      `.btn-icon` 40px）が **横並びに約 610px 要り、`wide`〔250px〕の 2.4 倍で既存の 4 段のどれにも入らなかった**ため。
      **中間の値ではなく上に 1 段足した形**である（**4 段の間は今も作らない**）。
      **セルの中を横並びにしたら、横に広がったぶんの幅も段で確保すること**（§4-4 B の `.control-group`）
  - **`narrow` / `default` / `wide` は抽出値の px そのもの**（105 / 125 / 250）。
    **序数の列は `ordinal`** で、**右寄せ**（`.list-cell-num`）
  - **`ordinal`（42px）だけは抽出値ではない**:
    **抽出元の `No.` 列は 25px** だが、**それは見出しが半角 3 文字（`No.` ≈ 24px）であることの上に成り立つ値**である。
    **見出しを日本語（全角混じり）にすると 25px には入らず**、
    **`.list-header` の `white-space: nowrap`（これも抽出値）と噛み合わない** —
    **25px のままだと見出しが隣の列に食い込み、隣の見出しと地続きの 1 語に読める**。
    - **段の決め方**: **最も細い列の見出しの実測幅に `.list-header` の左右の余白 2px × 2 を足し、切り上げる。**
      **全角・半角・空白が混じる見出しは字数から見積もらず、必ず実測する**
      （**「全角 2 文字ぶん」と見積もって段を決め、実際には 7px はみ出していた**という誤りが実際に起きた）。
      **他の細い列に余りが出ても、段は中間を作らないので同じ段に留める**
    - **抽出値と抽出値がぶつかった**（段の 25px と見出しの `nowrap`）。**どちらかを捨てるしかなく、
      人は「段を上げる」側を選んだ**（**見出しを折り返す案は、見出し行の高さが変わり
      一覧のある全ページの密度が変わる**ため）。**§1-1b の #19 / #20 を見よ**
    - **`ordinal` は最も細い列の段**であり、**序数の列のほかチェックボックスの列にも当てる**
      （**真偽値の列に固有の段は持たない** — §4-3 の `.checkbox` は幅を持たない）
  - **宣言した列幅は、見出しの長さに関わらず常に保たれる。**
    **見出しが段を超える分は、セルの外（隣の列の面の上）に視覚的にはみ出すだけ**で、
    **列の境目・隣の列の位置・表の幅のいずれも動かない**
    - **`.list-header` が `white-space: nowrap` で、列幅は `<col>` の宣言で確定している**ためである
    - **実測（極端な場合で確かめた）**: **`narrow`（105px）の列に 15 文字の見出し（220.5px 必要）を当てても、
      列は 105px のまま**（`clientWidth` 105 / `scrollWidth` 223）で、**隣の列の左端は 1px も動かない**
      （895.4px のまま）。**表の幅もページの横スクロールも変わらない**。**はみ出しは描画だけの問題**である
    - **器を取り違えない**: **`min-width: 100%` + `width: max-content` の器なら列は見出しの幅まで広がる**が、
      **本書が採っているのは `width: 100%` の器**で、**列は動かない**。**器を差し替えたら本文の記述も対で直すこと**
    - **はみ出すと読めなくなる**: **見出しの面色は隣と同じ `brand.primary` なので境目が見えず、
      隣の見出しと地続きの 1 語に読める**。**桁溢れより気づきにくい**
    - **全角 7 文字（106.9px）は `narrow`（105px）にぎりぎり収まらない**（右の内側の余白が 0 まで詰まる）。
      **1 文字でも増えると同じはみ出しが起きる**
    - **段を選ぶときは見出しの文字数も見る**こと — **入らなければ 1 つ上の段にする**（**画面設計書の判断**）。
      **列の中身（入力欄の幅の段）も同じように見る** — **`control.width.md`（142px）の入力欄は
      `layout.column.default`（125px）に入らない**（セルの内側の余白 2px × 2 を足すと 146px 要る）。
      **入らない入力欄は `max-width: 100%` でセル幅まで縮む**（**実測: 142px の入力欄が 125px の列で 121px になる**）
  - **セルの中の入力欄とボタンは横並びにする** — **`.control-group`**。
    **`.list-cell` は `white-space: normal`（長い値を折り返すため）なので、
    セルが狭いと入力欄とボタンが縦に積まれる**（**狭い列では 1 セルが 3 段になり、行の高さが 3 倍以上になる**）。
    **`入力欄と、その入力欄に付くボタン` を `<span class="control-group">` で包む**と、
    **`inline-flex` + `nowrap` で群の中では折り返さなくなる**（**群の外は従来どおり折り返す**ので長い自由文の折り返しは壊れない）
    - **群の幅が列に入るかは段の選択の責任**である（本クラスは折り返さないことだけを保証する）。
      **入らなければセルの外に視覚的にはみ出す** — **列の境目・表の幅・ページの横スクロールはいずれも動かない**
      （上の「宣言した列幅は見出しの長さに関わらず常に保たれる」と同じ挙動）
    - **段を選ぶときは、見出しの文字数・入力欄の幅に加えて「群の幅」も見る**
      （**入力欄 81 + 小ボタン 40 × 2 = 161px** なら、**`narrow`〔105px〕には入らず `wide`〔250px〕が要る**）。
      **器（本クラス）だけを入れて段の割り当てを直さないと、群はセルからはみ出したままになる** —
      **器と段の割り当ては対で入れること**（段の割り当ては画面設計書の領分）
    - **短いラベル（1〜2 文字）のボタンは `.btn`（23mm）ではなく `.btn-icon`（40×22）を使う**（§4-1）
  - **段を当てた表は `.list-scroll` に入れる** — **下の B-1b**。
    **px の段は `.list-scroll` /「吸う列」/ `.section` の `min-width: 0` が揃って初めて成立する**（**4 つで 1 組**）
  - **どの列にどの段を当てるか・どの列を「吸う列」にするかは画面設計書のレイアウト節（§3-x-2）が決める**
    （本書は段と器だけを持つ）。**宣言が無ければ従来どおり等分される** —
    **様式を足しただけでは 1 ページにも効かない**（§9 #13）。
    **宣言の無い表は `.list-scroll` にも入れない**ので、**段を導入する前と同じ見え方のまま残る**
  - **出どころ**: 抽出元は**列ごとに幅を割り付けている** — `pwtgo004` の一覧は
    `<table class="list" style="width: 1280px">` に**列ヘッダのセルごとの `width`**（**25 / 105 / 125 / 250px**）、
    `pwtgo005` の明細の表は **`<colgroup>` の `<col style="width: …">` で 12 列を個別に**（15〜115px）、
    別の一覧も `table-layout: fixed` + セルごとの幅（50 / 145 / 100 / 145px）。
    **`fixed` だけを採り、対になるこの割り付けを落としていた**ことが在る（**対の宣言の片落ち** — §1-1b の #16）
  - **抽出元と違えている点**: **セルは折り返す**（`.list-cell` の `white-space: normal`）。
    **抽出元は `nobr` + `td { overflow: hidden }` で溢れを刈る**が、**本書は値を欠落させない**（§5 の禁止）ので、
    **ここは再現しない**

**B-1b. 表の入れ物と「余りを吸う列」（`.list-scroll`）**

> **段を px で持つための器である。** **【人】の申し出**「**デザインシステムのトークンを利用するという原則だと
> 多少の横スクロールを許容しても px で宣言した方がよい**」**に沿って入れた**が、
> **確かめた結果、譲歩（横スクロールの許容）は要らなかった**（下の「なぜ % をやめたか」）。

- **段を当てた表は `<div class="list-scroll">` に入れる。** `.list-scroll` は `overflow-x: auto` だけを持ち、
  **表は `width: 100%` のまま**である（`.list-table` の宣言をそのまま使う。**`max-width: none` だけを足す**）。
  **効いているのは `table-layout: fixed` の 2 つの性質**である:
  - **① 表の使用幅は「宣言した列幅の合計」より狭くならない** — **合計が器を超える表は器を超えて広がり、
    入れ物がその差を横に流す**（**列は 1 本も縮まない**）
  - **② 幅を宣言していない列が 1 本あると、余りをその列に全部渡す** —
    **他の列は宣言どおりの px のまま**になる（下の「余りを吸う列」）
  - **表の幅が確定しているので、長い値は列を広げずに折り返す**（`.list-cell` の `overflow-wrap: anywhere` が効く）
  - **`.section`（§4-5）に `min-width: 0` が要る（対の宣言）**: **`fieldset` はブラウザの既定で
    `min-width: min-content` を持つ**ため、**これを戻さないと入れ物が横に流れる代わりに `.section` 自身が
    中身の幅まで広がり、`.app-main` を突き抜けて「ページ」に横スクロールが出る**。
    **その間 `.list-scroll` の `scrollWidth − clientWidth` は 0 のまま**なので、**入れ物だけを見ても気づけない** —
    **ページ側を見て初めて出る**。**`min-width: 0` を足すと `.section` は器の幅に留まり、入れ物が正しく横に流れる**。
    **`.condition-table` は `width: 100%` なので影響を受けない**
- **段の px の合計が器に満たない表は、「余りを吸う列」を 1 本置く。**
  **既存の列 1 本について `<col>` にクラスを書かないだけ**で、**列は増やさない・項目定義も変えない**
  - **置かないと、余りが全列に比例配分され、px 列がまた正規化される**（**器と合計の差が大きいほど倍率が上がる**）。
    **1 本置くと余りがその列に全部行き、他の列は宣言どおりの px のまま**になる
  - **段の px の合計が器を超える表には置かない**（**表が器を超えて広がり、余りが出ない** — 入れ物が横に流す）
  - **吸う列は「自然に長くなる自由文の列」を選ぶ**（備考・コメント・名称・組織など）。
    **数値・日付・コード・行操作の列は固定したいので選ばない**
  - **吸う列だけは固定値を持たない**（器しだいで幅が変わる。**これが px で持つことの唯一の代償**である）
  - **長い値が入っても吸う列は広がらない。折り返して行が高くなる**:
    **表の幅が確定している**ので、**`.list-cell` の `white-space: normal` / `overflow-wrap: anywhere` が効く**。
    **文字数を増やしても列の幅は動かず、行の高さだけが増える**。**入れ物のスクロールもページのスクロールも 0 のまま**
    - **`width: max-content` は使わない** — **max-content は「折り返しが起きない前提」で幅を測る**ので、
      **`overflow-wrap: anywhere` が効かず**（**anywhere が縮めるのは min-content であって max-content ではない**）、
      **長い自由文で列がそのまま横に伸び、入れ物が流れる**。
      **`width: 100%` は「表の幅がデータの中身で変わらない」ことも同時に保証している**
- **これはページの横スクロールではない。** **流れるのは表の入れ物の中だけ**で、
  **ページと本文は動かない**（§5 の但し書き・§9 #13）
- **なぜ % をやめたか**: **段を比率（2 / 8 / 10 / 20%）で持たせると、
  `.list-table` は `width: 100%` なので、合計が 100% でない表はブラウザが比率を保ったまま正規化する。**
  **帰結として同じ段名が表ごとに違う幅になる** — **同じ `narrow` が表をまたぐと 2 倍以上ちがい、
  宣言値と実幅も一致せず、段の大小が表をまたぐと逆転する**（**ある表の `narrow` が別の表の `default` より広い**）。
  **「同じ段 = 同じ幅」が立たないので、`layout.column` は語彙として機能しない**
- **なぜ横スクロールの許容が要らなかったか**: **「px だとページに横スクロールが出る」という前提が誤りだった。**
  **抽出元が横に流していたのは表の入れ物であって、ページではない** —
  `pwtgo004` の一覧は **47 列 / 列幅の合計 7500px** を `<table class="list" style="width: 1280px">` に入れ、
  **`#freezingDiv` > `.SearchList_list_block`（見出し固定のスクロールペイン）**に置いている。
  **【人】判断の文言は「ページごとの横スクロールをやめる」**であって、**表専用のスクロールを禁じていない**。
  **「px か横スクロール禁止か」というトレードオフは、そもそも存在しなかった**
- **同時に立つもの**: **段は抽出値そのもの** / **同じ段はどの表でも同じ幅** / **表は常に画面横幅いっぱい** /
  **ページの横スクロールは 0** / **列が多い表だけその表の入れ物が横に流れる**（抽出元の再現）。
  **「ページごとの横スクロールをやめる」という【人】判断を下ろす必要は無い**

**表ごとの当て方（判断の順）**

| 段の px の合計と器 | 吸う列 | 起きること |
|---|---|---|
| **合計 > 器** | **置かない** | **表が器を超えて広がり、`.list-scroll` がその差を横に流す**（列は 1 本も縮まない） |
| **合計 < 器** | **自由文の列 1 本**に段を当てない | **余りがその列に全部行き、他の列は宣言どおりの px** |
| **合計 < 器で吸う列を置かない** | — | **余りが全列に比例配分され、px が px でなくなる**（**この形にしない**） |

- **器の幅は入れ物の親で決まる**ので、**表ごとに数える** — **節（`.section`）の中の表と、
  `.app-main` の直下に置いた表では器が違う**（**節の枠と内側の余白のぶんだけ節の中が狭い**）。
  **どちらに置くかは画面設計書のレイアウト節（§3-x-2）が決める**ので、**器の幅もそこで数える**
- **段を当てていない表は従来どおり等分される**（**`.list-scroll` に入れないため、段を導入する前と同じ** —
  **既存のページは壊れない**）

- **件数（`.list-caption`）**: 表の**上に右寄せ**で `1-14件目/14件` の形（bold・`size.body`）
- **見出し行（`.list-header`）**: 面 `brand.primary`、文字 `brand.on_primary`、
  高さ `control.height`、折り返さない。**見出しは常に左揃え**
- **行（`.list-row`）**: **ゼブラ** — 奇数行 `surface.row_odd` / 偶数行 `surface.row_even`
- **セル（`.list-cell`）**: 文字 `text.body`、内側 `spacing.xs`、**収まらない値は折り返す**
  （**抽出元の「折り返さない」から変えている** — 幅が固定配分になったため）。
  **数値・日付・金額のセル（`.list-cell-num`）は右寄せ・折り返さない**（桁が割れると読めなくなるため）
- **状態**:
  - **空（0 件）— 見出し行だけの表を残し、その外に `.empty-state` を 1 行置く。**
    **表ごと消さない** — 既存 UI は 0 件でも見出し行を出しており、**列の語彙が 0 件でも見える**
  - 選択行（**既存 UI に無い** — 作らない）

**B-2. 列が多い表の畳み方（`.list-row-2`）**

> **【人】判断**: **横スクロールを原則なしにする。1 行を 2 段に折り返し、表は画面横幅いっぱいを使う。**
> **これは既存画面の再現からの離脱ではない** — 抽出元は**1 件を 2 行で描く一覧のゼブラの段**を
> CSS に持っており（`custom.css` の `TABLE.list TR.rows2:nth-child(4n+1…4n+4)`）、
> **明細の編集では 1 件を節 + 入れ子の条件表に畳んで固定幅に収めている**（`pwtgo005` の `ContractList`）。
> **初版が抽出していなかった様式である**（§1-1b の #2）。

- **いつ畳むか**: **列が `.app-main` の幅（`layout.content_max_width`）に収まらず、
  かつ画面設計書が「入れ物を横に送らせたくない」と判断したとき**（
  **収まらないだけなら既定は `.list-scroll` が横に流すほう**である。B-3 の「収まらないときの順序」）。
  **列を削らない・省略しない・文字を縮めない**（§5 の禁止）
- **畳み方**: **1 件を 2 つの `<tr>` に分け、両方に `.list-row-2` を付ける。**
  見出し行も同じ分け方で 2 行にする（**どの列を 2 段目に送るかは画面設計書のレイアウト節が決める**）。
  **3 段以上にはしない**（段が増えると 1 件の境目が読めなくなる）
- **ゼブラは 1 件を単位にする**: `.list-row-2` は**2 行で 1 件**なので、
  **4 行ごとに色を替える**（1・2 行目 = `surface.row_odd` / 3・4 行目 = `surface.row_even`）。
  **1 件の途中で色が変わってはならない。** 出どころは `custom.css` の `TR.rows2` の `4n` のゼブラ
- **数え方の前提**: **見出し行は `thead`・明細行は `tbody` に置く**（§9 #11 の (5)）。
  **見出し行が明細行と同じ親に居るとゼブラの数えが 1 つずれる**
- **禁止**: 1 件を 3 行以上に分ける / 2 段目だけ行高を変える / 段の境目に罫線を足す

**B-3. 横に溢れる場合**

- **ページごとの横スクロールは持たない。**
  **器（`.app-main`）は幅を持ち、表はその中で `width: 100%` を使う**。
  **横スクロールを消しているのはこの幅である**（**上限を `none` にすると本文がいくらでも広がり、
  ページごと横に動く**）。
  **溢れたものを隠す指定は持たない**（隠すと情報が欠落し、下の禁止に触れる）。
  **禁じているのは「ページごと」の横スクロールである** —
  **一覧の表の入れ物（`.list-scroll`）が中で横に流れることは禁じていない**（B-1b。**抽出元も同じ形**）
- **本文幅は 2 段**:
  - **既定 = `layout.content_width`（980px）**。**ヘッダと同じ幅**で、**抽出元の
    `<table class="header" width="980">` そのもの**である。**既定の段では何も足さない**（`.app-main`）
  - **上限 = `layout.content_max_width`（1480px）**。
    **980px では一覧が読めないと画面設計書が判断した画面だけ**、**`.app-main-wide` を当てて広げてよい**
    - **`max-width` なので「器が在れば使い、無ければそこまで」である。** **1480px という値は breakpoint ではない** —
      **画面が広ければ表がまるごと出て、狭ければ本文はビューポート幅までしか広がらず、溢れは `.list-scroll` が表の中だけで流す**
    - **【人】の求めは「広い画面ではスクロールなしで出す（スクロールは該当の表のみ）」**である。
      **後半は `.list-scroll` が満たす**ので、**満たすべきは前半だけ**である。
      **しきい値（メディアクエリ）は作らない** — **上限を上げるだけで両方が満たせる**ので、
      **段は 2 つのままで中間の幅も breakpoint も増えない**
    - **値の出し方**: **いちばん広い一覧の表の幅**（列幅の段の合計 + `border-spacing`）を測り、
      これが `.section` の中に収まる幅 — **表 + 節の枠 1px × 2 + 節の内側 `spacing.md` × 2 +
      `.app-main` の `padding-left` `spacing.lg`** — を切り上げる。
      **段の値（`layout.column`）を変えたら、この値も測り直す**
    - **切り替え点を「そのとき見ていた画面の実効幅」にしない** — **それは切り替え点ではない**。
      **上限を表の幅から出しておけば、それより広い画面すべてで恩恵が出る**
    - **上限を超える表は在ってよい。** **上限より広い表は、入れ物（`.list-scroll`）が常に横に流す**
      （**ページは動かない**）。**「広い画面ではスクロールなしで出す」は表ごとに成り立ったり成り立たなかったりする** —
      **いちばん広い表に合わせて上限を上げ続けることはしない**（**ヘッダ〔980px 固定〕との差が開きすぎ、
      本文がほぼ画面幅いっぱいになる**ため）
    - **`layout.viewport_target`（1280×800）の画面では挙動が変わらない**
      （**実効表示幅が上限より狭いので、本文はビューポート幅までしか広がらない**）
  - **広げるのは本文だけで、ヘッダは広げない**（**幅は常に 980px で固定** — 下の但し書き）
  - **どの画面を広げるかは画面設計書のレイアウト節（§3-x-2）が決める**（本書は段だけを持つ）。
    **中間の幅を作らない**（段は 2 つだけ。§4-1 のボタンの幅・§4-2 の入力欄の幅と同じ考え方）
- **収まらないときの順序**: **① 1 行に置く組数を減らす**（条件表 — §4-4 A）→
  **①' 列幅の段を列ごとに割り付ける**（一覧 — 上の「列幅は列ごとに割り付ける」。
  **等分をやめるだけで読める幅が出る場合がある**ので、**広げる前にこちらを先に見る**）→
  **①'' 段の px の合計が器を超えるぶんは、表の入れ物（`.list-scroll`）が横に流す**
  （一覧 — B-1b。**ページは動かさない**）→
  **② 1 行を 2 段に折り返す**（一覧 — B-2。縦に伸ばす。**入れ物を横に送らせたくない画面で選ぶ**）→
  **③ それでも読めないなら `.app-main-wide` で上限まで広げる**
  - **①'' と ② は同じ問題への 2 つの答えで、選ぶのは画面設計書である**
    （**①'' は横に送る操作が要る / ② は縦に伸びて 1 件の境目が読みにくくなる**）。
    **①'' が既定**で、**② を選ぶ画面は §3-x-2 でそう宣言する**

> **①' を ② / ③ より先に置いた理由**: **③（本文を広げる）を先に採っても、列が等分のままなら
> 広げたぶんが細い列にも等しく行き、広いはずの入力欄の列は届かない**（**足りないのは幅ではなく配分**である）。
> **①' は器の幅を変えずに効く**ので、**費用（本文幅の変更 = 全ページの見え方の変更）が最も小さい。**

> **ヘッダは広げない（【人】判断）**: **ヘッダの幅は常に `layout.content_width`（980px）で固定する。**
> **本文を上限まで広げた画面では、ヘッダだけ 980px で残り、右端がそろわない。**
>
> **「本文の最大幅はヘッダと同じ 980px」という前提を、この判断が明示的に外している。**
> **外したのは人**で、本書は決着を写している。
> **起草の時点では逆の案を出していた** — **ヘッダにも `.app-header-wide` を対で当てて幅をそろえる**案で、
> **「ヘッダと本文は同じ幅」を保つことを優先していた**。**人は「ヘッダは幅固定にしたい」を選んだ。**
>
> **選ばれた側の理由**: **ヘッダの 980px は抽出値**（`<table class="header" width="980">` そのもの）で、
> **広げると「既存画面の再現」から離れる**。**ヘッダは全ページに載る**ので、
> **画面によって幅が変わると、そこだけ揺れて見える**。
> **右端がそろわない見え方は目視の観点に挙げる。**
- **禁止**: 省略表示で情報を欠落させる / 行高を行ごとに変える / ゼブラと `surface.subtle` を混ぜる /
  **本文やページを横にスクロールさせる**（**`.list-scroll` の中だけは流れてよい** — B-1b）

### 4-5. Section（`class: .section` / `.section-title`）

- **形**: 枠 1px `border.subtle`、内側 `spacing.md`、**角は丸めない**、影は持たない（`elevation.none`）。
  見出し（`.section-title`）は**枠線の上に重ねて**置き、`size.body` / `text.body`
  （既存 UI の `fieldset` + `legend`）
- **使う場面**: 1 画面の中で入力・表示のまとまりを区切る（`作成条件` `更新項目` `基本情報` の形）。
  節の間は `spacing.lg` 空ける
- **幅は器いっぱいで、中身では広がらない**: **`min-width: 0` を持つ。**
  **`fieldset` はブラウザの既定で `min-width: min-content` を持ち、そのままだと中身の幅まで節が広がる** —
  **§4-4 B-1b の `.list-scroll` が「入れ物の中で横に流れる」代わりに「節ごと横に伸びてページが横スクロールする」**
  ことになる。
  **節は常に `.app-main` の幅に留まり、横に溢れるものは溢れる側の器（`.list-scroll`）が引き受ける**
- **禁止**: 入れ子にしない / 影を付けない / **中身の幅で節を広げる**

### 4-6. 状態の表示 — **部品を作らない**

- **既存 UI に状態チップ（Badge）が無い。** 業務状態は `承認済` `データ変更中` `ドラフト` のように
  **文字列をそのままセルに出す**（`.list-cell`）。面色も枠も付けない
- **状態色（`status.*`）を業務状態の表示に使わない。** `status.*` は通知（§4-8）と
  入力エラーの欄（§4-2）だけのものである（§2 の禁止）
- **状態名の語彙は画面設計書・画面マップが正**で、本書は持たない
- mockup で状態を色や形で区別したくなった場合は、**作らずに「追記候補」として報告する**（§9-7）

### 4-7. Dialog（`class: .dialog-backdrop` / `.dialog-panel` / `.dialog-close`）

- **既存 UI の参照用副画面は別のブラウザ窓**で、ヘッダを持たず「条件表 → アクション行 → 一覧 → ページ送り」だけを置く
  （コード検索 ZOOM のキャプチャ）。**mockup は窓を開けないため、同じ中身を画面内に重ねて表す**
- **形**: 背景（`.dialog-backdrop`）は `overlay.backdrop`。
  面（`.dialog-panel`）は `surface.card`、最大幅 500px、
  **内側は 上 `spacing.lg` / 左右 `spacing.xl` / 下 `spacing.md`**（**上だけ 1 段広い** — 下の「閉じるの居場所」）、
  **角は丸めず影も持たない**（背景の暗さで階層を作る）。
  閉じる（`.dialog-close`）は右上に置く
- **閉じるの居場所を上の余白で空ける**: **`.dialog-close` は `position: absolute` で
  `top: spacing.sm`（5px）に置かれ、高さが 12.8px あるので、パネルの上端から 17.8px を占める。**
  **上の内側の余白が `spacing.md`（10px）だと 7.8px 足りず、閉じるが中身に重なる**（**モーダルのある全ページ**）。
  **上の余白だけを 1 段上げて `spacing.lg`（20px）にする**（**段は増やさない**。余裕 2.2px で重なりが解消する）。
  - **`.dialog-close` を絶対配置のまま残した理由**: **流し込み（`position: static`）に変えると 1 行ぶん
    パネルが縦に伸び、中身の始まる位置が全モーダルで動く**。**上の余白を 1 段上げるほうが影響が小さい**
  - **中身の先頭が何であっても効く**（条件表・素の `p`・`.calendar-panel` のいずれでも同じ 20px から始まる）
- **中の文**: 確認の問いかけなどの文は**素の `p` に置き、専用のクラスを作らない**。
  書体・サイズ・字送りは地の規定（`body`）が持つので見た目は揃う。
  **既存 UI の参照用副画面は「条件表 → アクション行 → 一覧」だけで文を持たない**ため、抽出元に対応物が無い
- **中身の幅**: **パネルの中に置けるのは 440px までである。**
  **`.dialog-panel` は `max-width: 500px`、左右の内側の余白が `spacing.xl`（30px）ずつ**なので、
  **中身が使える幅は 500 − 30 × 2 = 440px**（実測で一致）。**この 440px が、パネルの中の部品の幅の基準である。**
  - **§4-2 の幅の段（`xs`〜`xl`）と `control.textarea_width` は `layout.content_width`（980px）を前提に決めた値**で、
    **パネルの中に入る前提を持たない** — **`xl`（564px）と複数行入力（524px）はそもそも 440px に入らない**
  - **原則: 表の 1 行が 440px に収まるように、値の幅の段を選ぶ**（**ラベルセルの幅も足して数える**）。
    **収まらないときに初めて、その項目だけラベルと値を 2 行に分ける**（`.condition-table` の中で `<tr>` を 2 本にし、
    ラベルの行の下に値の行を置く）。**【人】判断**:
    「**原則テーブルは 1 行 → 1 行で納まるよう横幅を調整 → それでも無理なら 2 行を検討**」
  - **どの段を当てるかは画面設計書が決める**（部品名は画面設計書 §3-x-3 が書く）。
    **本書が段を狭めても、画面設計書が `xl` と書いている限り mockup は `xl` を描く**
  - **器の側の保険**: **パネルの中の `.condition-table` は `width: 100%` + `table-layout: fixed`、
    ラベルセルは `control.label_width`（120px）**にしてある。**段を選び違えても値が器を突き破らない**
    （**`table-layout: fixed` の下でだけ `max-width: 100%` が効く** — §4-2）。
    **これは「はみ出さないこと」を器で保証するためのもので、段を選ぶ責任を消すものではない**
  - **抽出元**: `pwtgo005` の条件表も **`table-layout: fixed` + `<colgroup>`** で組んでおり、
    **「表の幅を決めてから中身を割り付ける」のが既存 UI の作り**である（§4-4 B の列幅の割り付けと同じ出どころ）
- **使う場面**: コードの検索・参照選択（`Z` ボタンから開く）/ **月次カレンダー**（§4-11 を中に置く）/
  操作の確認（文 + `.button-area`）
- **禁止**: 背景のスクロール / ダイアログの入れ子 / 影を付ける /
  **パネルの中身を横にはみ出させる**（**§5 の「横スクロールを持たない」はパネルの中にも効く**）

### 4-8. Banner（通知・`class: .banner-error` / `.banner-success` / `.banner-warning` / `.banner-info` / `.banner-list`）

- **形**: 面 `status.*_surface`、枠 1px `status.*_border`、文字 `status.*`、
  **角丸 `radius.md`**（既存 UI で角を丸めている唯一の部品）、内側 `spacing.md`
- **4 種**: `.banner-error`（抽出値）/ `.banner-success` `.banner-warning` `.banner-info`
  （**補完** — §2 の脚注。既存 UI にはエラーしか無い）
- **どれを使うか**: **処理を止めるものが `.banner-error`、止めないものが `.banner-warning`**（§2）。
  完了は `.banner-success`、案内・ヒントは `.banner-info`。**どの事象がどちらかは画面設計書が決める**
- **位置と中身**: **画面の最上部**（ヘッダの直下・アクション行より上）に置き、
  `.banner-list` の箇条書きで**1 件 1 行**にする。エラーの 1 行は
  `WTG-000002：計画基地局名:入力して下さい` の形（**コード + 項目名 + 内容**）
- **1 行の書式は持っている要素だけで組む**（**値を消さずに適用範囲を明記する**）:
  - **メッセージコードの体系がある案件** — `コード：項目名:内容`（上の既存 UI の形）
  - **コードを持たない案件** — `項目名:内容` の 2 要素。**識別子（`FORM_VALIDATION_FAILED` の類）をコードとして描かない**
  - **コードも項目名も持たないもの**（取得失敗・システムの失敗）— **内容だけを 1 行で**出す
- **入力値のエラーは Banner と入力欄の両方に出す** — Banner に 1 行、該当欄は `.field-input-error`（面を桃色に）。
  **複数行入力にも同じクラスを当てる**（§4-2）。これが既存 UI の作りである（片方だけにしない）
- **文言トーン**: §7 に従う
- **禁止**: 通知以外の場所で `status.*` を使う（§2 の禁止）/ 通知に `surface.subtle` などの構造の面色を使う

### 4-9. ページ送り / 空状態 / 処理中（`class: .pagination` / `.pagination-current` / `.pagination-link` / `.pagination-side` / `.empty-state` / `.wait-message`）

- **タブは持たない**（§1 の #6 — 既存 UI に無い）
- **ページ送り（`.pagination`）**: **表の下・中央寄せ**。上に `spacing.md` の間隔。
  ページ番号を並べ、**現在ページ（`.pagination-current`）は `text.current`（crimson）の bold・リンクにしない**、
  他は `.pagination-link`（`text.link` の下線リンク）。両端に `.pagination-side` = `＜前へ` / `次へ＞`
- **番号を出せない場合**: **両端（`.pagination-side`）だけを置く。**
  総件数・総ページ数が取れない取り方（カーソル送り）では現在ページの番号が決まらないため、
  **`.pagination-current` と `.pagination-link` を置かない**。**新しい部品は作らない**
- **空状態（`.empty-state`）**: 表の外に 1 行で `該当するデータはありません`
  （**既存 UI の既定の文言**。`size.body` / `text.body`）。
  **画面設計書に文言があればそちらが正**（§9 #3 の優先順をここにも明記した）。
  **表そのものは見出し行だけ残す**（§4-4 B）
- **処理中（`.wait-message`）**: `処理中です。しばらくお待ちください。` を 1 行で出す
  （**既存 UI の既定の文言**。画面設計書に文言があればそちらが正）。
  **枠 1px `border.default` と面 `surface.card` を持つ。**
  **mockup は JS を書かないため、処理中は独立した状態ページで表す**
- **禁止**: 空状態に絵柄・アイコンを置く / 現在ページをリンクにする /
  **現在ページの色（`text.current`）をエラーの意味に使う**

### 4-10. アプリシェル（`class: .app-header` / `.app-header-logo` / `.app-header-meta` / `.app-header-links` / `.app-header-link-disabled` / `.app-main` / `.app-main-wide` / `.app-menu` / `.app-menu-title` / `.app-menu-item` / `.app-menu-item-disabled`）

> **全画面に載る部品。** ナビ項目の文言・並び・グルーピング・**入口の表示文言**・どの画面が入口かは
> **画面マップ §4 が正**で、ここには書かない（**様式だけを持つ**）。
> **この節に無いクラスでシェルを描くとパレット検査が全ページで fail する。**
>
> **グローバルナビ・ナビ項目の現在地・無効・パンくずは持たない**（【人】判断・既存画面の再現。
> §1 の #1〜#4）。**feature 間の導線は入口画面（`.app-menu`）が担い**、各画面のヘッダには
> **共通のリンクの段を置く**（`.app-header-links` — 既存 UI の `[MENU]` 相当）。
> 現在地はヘッダの `画面名` の表示で示す。

- **ヘッダ（`.app-header`）**: 面 `surface.header`、幅 `layout.content_width`（980px）、
  **下辺に 4px `border.strong` の二重線**（画面で最も強い区切り）。文字は `size.body` / bold。
  **幅は常に 980px で固定する — 本文を `.app-main-wide` で広げた画面でもヘッダは広げない**
  （【人】判断・§4-4 B-3 の但し書き。**980px は抽出値で、広げると「既存画面の再現」から離れるため**）。
  **2 行の表で組む** — **列は 左 = ロゴ（2 行にまたがる）/ 中 = 利用者情報 /
  右 = リンク**で、**利用者情報とリンクは 1 行目と 2 行目にそれぞれセルを持つ**。
  **出どころは既存 UI の `common/header.html` の実マークアップ**（`<table class="header" width="980">` の
  2 行組み・ロゴのセルが `rowSpan="2"`・右端の列が 1 行目と 2 行目に 1 つずつ）。
  **flex や float で組まない**（右のリンクを右端に寄せると 2 行目に落ちる、が実測で起きた）。
  **要素の選び方が様式の前提になる箇所**なので §9 #11 にも挙げてある
- **ロゴ（`.app-header-logo`）**: ヘッダの左端の列で、**2 行にまたがる**。上端揃え。
  **この 90px の枠は、最終的にロゴ画像が入る場所である**（**下の但し書き「この枠は何のために在るか」を先に読むこと**）。
  **幅は `control.header_logo_width`（90px）で固定する**（**「内容相応にする」という前の決着を覆したもの** — 下の比較）。
  既存 UI はこの位置に `<img id="Logo">`（90px）を置く。**WiNG のロゴは流用しない**ので、
  **`asset.logo` が `none` の間だけ、システム名の文字が仮に入る**（`size.body` / bold）。
  **このセルだけ折り返しを許す**（`white-space: normal` — **ヘッダの他のセルは折り返さない**）。
  **文字は 90px に収まらないので 2 行に折り返す。折り返したまま置く**
  （**全角 10 文字前後のシステム名は `size.body` で 140〜150px 要る。**
  **折り返しを許さないと `width: 90px` は効かず、セルが内容の最小幅まで広がる** — **枠を確保できない**。
  **折り返しても 2 行に収まり、ヘッダの高さは増えない** — **右隣の `.app-header-meta` が元から 2 行あるため、
  ロゴの 2 行がその行送りの中に収まる**〔増分 **0px**〕）。
  **ここが差し替え点** — **この案件のロゴを用意できたら `asset.logo` にパスを入れて版を上げる**（§1-1 の #11）。
  **枠の幅はそのときも 90px のまま**なので、**差し替えても本文側のレイアウトは動かない**

> **この枠は何のために在るか（読み違えないための但し書き）**
>
> **90px は「文字を入れる幅」ではなく、「ロゴ画像が入る幅」である。**
> **いま見えている 2 行に折り返したシステム名の文字は、ロゴが用意できるまでの仮の中身**である。
>
> | | いま（`asset.logo` = `none`） | ロゴを用意した後 |
> |---|---|---|
> | 枠の幅 | **90px** | **90px**（**変わらない**） |
> | 中身 | **システム名の文字**（2 行に折り返す） | **ロゴ画像**（90px 幅・折り返しは起きない） |
> | 本文側のレイアウト | — | **動かない**（**枠を先に確保したのはこのため**） |
>
> **だから「文字が 2 行になって窮屈だ」を理由に枠を広げてはならない。** 広げると、
> **ロゴを入れた日に枠が 90px へ縮んで、ヘッダと本文のレイアウトがもう一度動く**
> （**それが「幅を内容相応にする」という前の決着で起きていたこと**である — 下の比較）。
> **文字の見え方を良くしたいなら、枠ではなく文字の側を短くする**（**短い表示名を画面マップ §4 に持たせる**。
> **文言の正は画面マップ §4 なので、本書では決めない**）。

> **この 1 行は逆向きに 2 度決まっている**（§1-1b の #15）。
> **どちらも前提の上では正しい**ので、**片方を誤りとして消さない**:
>
> | | 何を守ったか | 決着 |
> |---|---|---|
> | **前の決着** | **文字が折り返さないこと**（`asset.logo` が `none` の間の見え方） | **幅を内容相応にする**（`min-width: 90px` + `width: auto`） |
> | **いまの正** | **将来ロゴを入れても本文側のレイアウトが動かないこと**（差し替え点の安定） | **`width: 90px` 固定に戻す。折り返しは受け入れる** |
>
> **人は後者を選んだ**（**折り返す旨を提示したうえで選ばれている**）。
> **折り返した見え方そのものは目視の観点に挙げる。**
>
> **対で要る 1 行**: **`width: 90px` を書くだけでは枠は確保できない。**
> **`.app-header-logo` が `white-space: nowrap` を持っていると、
> 折り返せないセルは指定幅を無視して内容の最小幅まで広がる。**
> **`white-space: normal` を対で足して初めて 90px になる**（**「折り返す」という決着そのものは人が選んだもの**）。
>
> **足したうえで実測した結果**: **セルは 90px の指定どおりに収まり**（96px = 90px + 左の `spacing.sm`）、
> **文字は 2 行に折り返し、`.app-header` の全体幅は 980px のまま、ヘッダの高さの増分は 0px**。
> **「折り返して縦に伸びる」という懸念は起きない** — **右隣の利用者情報が元から 2 行ある**ためである。

- **利用者情報と現在地（`.app-header-meta`）**: **1 セルに 1 項目**を `見出し : 値` の形で置き、
  **利用者・所属・画面名を 2 行に分ける**（**行の分け方は表の行が決める** — §9 #11 の (4)。
  **格子ではなく表の行で分ける**）。
  **割り方は 1 行目 = 利用者 + 画面名 / 2 行目 = 所属 + 空セル**（抽出元の
  `common/header.html` の実マークアップに合わせている。
  あわせて抽出元の画面名の値は `[画面番号]画面名` の形〔`[GWTG004]契約情報検索/一覧`〕だったが、
  **この形を画面マップ §4 に返すかは別途**（本節は割り方の様式だけを持つ））。
  **この割り方は人が「現状を正とする」と確定したものである。**
  **変えるときは、確定の場でまとめてではなく、単独で人に聞く** — 下の但し書き。
  折り返さない・上端揃え。**`画面名` が現在地の表示**である（§1 の癖）。
  **見出しの文言と画面名の値は画面マップ §4 と画面設計書が正**で、ここには書かない

> **ヘッダは、確定の場でまとめて通さない。**
> **ヘッダの割り方は 3 版続けて動いた** — **格子から 2 行の表へ**、**次に 1 行目と 2 行目を入れ替え**。
> **どちらも「抽出元に合わせる」という根拠で agent 側が起案し、
> 人の確認は確定の場でまとめてしか通っていなかった**。
> **ヘッダは全ページに載る**ので、**まとめて通すと実質的に確認されないまま全ページが変わる**。
>
> **よって、`.app-header-meta` の内容と `asset.logo` の有無を変えるときは、確定の場に出す前に単独で人に聞く。**
> **これはこの案件限りの取り決めではなく、本工程を回すときは常に同じである**（人からの要求）。
- **ヘッダのリンク（`.app-header-links`）**: ヘッダの右端の列のセル。`text.link` の下線リンクを
  **角括弧付きで**並べる。右寄せ・折り返さない・上端揃え。**段は 2 つ**（既存 UI の作り）:
  - **1 行目 = その画面から直接飛ぶ具体的な機能への遷移**（**本数は画面によって変わる。
    0 本の画面ではセルを空で残す** — 段の並びが画面によって変わらないようにするため）
  - **2 行目 = 全画面に共通のリンク**（戻る・入口へ・ログアウトの類）
  - **文言と行き先、どの画面でどれが無効になるかは画面マップ §4 が正**で、ここには書かない。
    **本書が持つのは段の分け方と無効の見せ方だけ**である
- **ヘッダのリンク・無効（`.app-header-link-disabled`）**: `text.disabled`・**下線なし**・カーソル既定・押下不可。
  **入口画面のリンク一覧の無効（`.app-menu-item-disabled`）と同じ 3 点で揃えてある** —
  出どころも同じ既存 UI の `linkedlabel_disabled` と `*_disabled` の色の慣行である。
  **行き先が無いリンクと、いま居る画面を指すリンクに使う**（§4-9 が現在ページをリンクにしないのと同じ考え方）。
  **リンクを消さずに無効で残す**のは、**段の並びが画面によって変わらないようにする**ためである
- **本文領域（`.app-main`）**: 左 `spacing.lg`、上 `spacing.lg`、下地 `surface.canvas`、
  **最大幅 `layout.content_width`（980px）で左寄せ**。**ヘッダと同じ幅に揃えてある**
（**上限を `none` にしない**）。**広い表は横スクロールさせず、2 段に折り返す**（§4-4 B-2）
- **広げた本文領域（`.app-main-wide`）**: **最大幅を
  `layout.content_max_width` にする。** **980px では一覧が読めないと画面設計書が判断した画面だけ**に当て、
  **ヘッダは広げない**（§4-4 B-3 の但し書き）。**中間の幅を作らない**（段は 2 つだけ）
- **入口画面のメニューの見出し（`.app-menu-title`）**: リンク一覧の**上に 1 つ**置く見出し。
  `size.title`（18px）/ bold / `line_height.heading`、上端揃え（`vertical-align: top`）。
  **入っている位置を示す**ためのもので、既存 UI は**システム名**（`WiNGｼｽﾃﾑ`）か**親メニュー名**を出す
  （出どころ `SPAN.linkedlabel_large_menuitem` / `A.linkedlabel_large_menuitem`。
  親メニューが在るときはリンク、無いときは素の文字）。**文言は画面マップ §4「入口の表示文言」が正**
- **入口画面のリンク一覧（`.app-menu` / `.app-menu-item`）**: **入口画面の本文に置く縦のリンク一覧で、
  これが feature 間の導線である。** 1 項目 25px、`size.subtitle`（12pt）の `text.link` 下線リンク。
  **先頭に矢印（`asset.menu_arrow`・`control.icon_menu` = 18×18）を繰り返さずに敷く**（既存 UI の青い矢印）。
  **項目の文言・並び・行き先は画面マップ §4 が正**
- **入口のリンク・無効（`.app-menu-item-disabled`）**: `text.disabled`・下線なし・カーソル既定・押下不可。
  **リンク先が無い項目に使う**（mockup 未生成 feature の項目）。
  出どころは既存 UI の `linkedlabel_disabled` と `*_disabled` の色の慣行

### 4-11. 月次カレンダー（`class: .calendar-panel` / `.calendar-header` / `.calendar-nav` / `.calendar-title` / `.calendar-table` / `.calendar-weekday` / `.calendar-day` / `.calendar-day-today` / `.calendar-day-selected` / `.calendar-day-outside`）

> **【人】判断**: **静的に 1 か月を描く。**
> **骨組みだけ jQuery UI 1.14.1 の datepicker を参照し（`sources.code` に「参照のみ」と印を付けて列挙した）、
> 色・書体・寸法は本書のトークンに置き換える。** プラグインの既定テーマの色（`#5c9ccc` の帯・`#dfeffc` のセル・
> `#fbec88` の今日・`#e17009` の文字）と**背景の画像は 1 つも採っていない** — 採ると
> **§2 の体系に無い色と、§7 が禁じるグラデーションが入る**ためである。
> **既存 UI 自身はこの部分を JS（`calendar.js` + jQuery UI）で持っており、様式を書いていない。**

- **器（`.calendar-panel`）**: 面 `surface.card`、枠 1px `border.default`、**角は丸めない**、影は持たない、
  内側 `spacing.xs`、幅 `control.calendar_width`（227px）。**§4-7 の `.dialog-panel` の中に置く**
- **月の帯（`.calendar-header`）**: 面 `brand.primary`、文字 `brand.on_primary`、高さ `control.height`、
  **左右に月送り・中央に年月**（`.calendar-title` — bold・中央寄せ・折り返さない）。
  **面色を持つ見出し**という点で §4-4 の `.condition-label` / `.list-header` と同じ扱いである
- **月送り（`.calendar-nav`）**: **リンクで表す**（`brand.on_primary` の下線リンク・帯の左右の端）。
  **ボタンにしない** — `.btn` は `23mm` あり帯に収まらないためで、**一覧の操作をリンクで表す既存 UI の作りと揃う**
- **曜日の見出し（`.calendar-weekday`）**: 面 `brand.primary`、文字 `brand.on_primary`、
  高さ `control.height`、bold、**中央寄せ**、折り返さない
- **日のセル（`.calendar-day`）**: 面 `surface.card`、文字 `text.body`、高さ `control.row_height`、
  **右寄せ**（数字なので §5 の揃えに従う）、内側 `spacing.xs`
- **状態**:
  - **今日（`.calendar-day-today`）** — **文字を bold にし、枠を 1px `border.focus` にする。**
    **面色を使わない**（`status.warning_surface` を当てると §2 の禁止に触れる）
  - **選択中（`.calendar-day-selected`）** — 面 `brand.primary` + 文字 `brand.on_primary`
  - **当月外（`.calendar-day-outside`）** — 文字 `text.disabled`・押下不可
- **使う場面**: **日付欄（`.field-input-date`）そのものから開く**（§4-2）。**起動ボタンは無い**
  （既存 UI の作り）。**どの月を出すか・どの日を選択中にするかは画面設計書が決める**。
  **ダイアログ・モーダルの中の日付欄には当てない**（**直接入力にする**。§4-7 の
  ダイアログの入れ子の禁止から導ける帰結。カレンダーは `.dialog-panel` の中に置く部品なので、
  日付欄自身がすでにダイアログの中に居ると開けない）
- **静的な mockup での表し方**: **カレンダーは独立した状態ページとして持ち、日付欄からそこへ遷移させる。**
  **遷移元は日付欄で、欄の横の何かではない**（起動ボタンが無いため）。要素の選び方は §9 #11 の (6)
- **禁止**: **JS で動かす前提の様式を書く**（mockup は JS を書かない — §9-4。**固定の 1 か月を HTML で描く**）/
  プラグインの既定テーマの色・画像を持ち込む / 角を丸める / 週末・祝日に色を付ける（既存 UI に根拠が無い）/
  **日付欄の横に起動ボタンを置く**

### 4-12. 印刷の透かし（`class: .watermark`）

> **【人】判断**: **持つ。**「あった方が親切」。
> **抽出元に対応物が無く、§7 の「装飾を作らない」に対する明示の例外**である（§1-1b の #5）。

- **形**: **本文領域（`.app-main`）の上に重ねて**置く 1 語。文字 `text.watermark`、
  大きさ `control.watermark_size`（72pt — **§3 の本文の段ではない。印刷の装飾の寸法である**）、bold、
  **中央に置き、斜めに傾ける**。**面色・枠・影を持たない**（文字だけ）。**重ねる基準は `.app-main`**
- **使う場面**: **印刷のときだけ**（§8）。**画面では出さない**
- **文言は画面設計書が正**（本書は様式だけを持つ — 何を透かすかは画面の状態で決まる）
- **禁止**: 画面表示で出す / 状態色を使う / 画像で描く / 本文を読めなくするほど濃くする

### 4-13. システムエラー画面（`class: .system-error-title` / `.system-error-table` / `.system-error-label` / `.system-error-body` / `.system-error-detail`）

> **【人】判断**: **新設し、一度落としたキー 2 件（`text.error_title` = red /
> `status.error_detail_surface` = palegoldenrod）を役割名で戻す。** 方針は「既存画面の再現」で、
> **抽出元にキャプチャとテンプレートの両方が在る**（`error.html` / `geframe.commons.css` / キャプチャ
> `システムエラー.png`）。**§2 の禁止（状態色を表の本体に使わない）に対する明示の例外**である（§1-1b の #11）。
> **業務エラー（`.banner-error` — §4-8）とは別物**で、**フレームワークが処理を継続できない回復不能なエラー**を表す
> （業務エラーは入力値・処理結果に対する通知で、処理を止めるかどうかを人が判断できるものである — §2）。

- **見出し（`.system-error-title`）**: 文字 `text.error_title`（赤）、大きさ `control.error_title_size`
  （24px — §3 の本文の段ではない）、bold。**抽出元は `<font size="5" color="red">System Error</font>`**
- **表（`.system-error-table`）**: **3 列**（種別 / コード / メッセージ）。**格子線は持たない**
  （`.list-table` / `.condition-table` の `border.grid` とは異なり、既存 UI は行の面色だけで区切っている）。
  **列幅は内容相応**（目安 — 種別 : コード : メッセージ ≈ 5 : 20 : 75。抽出元 `error.html` の
  `width=5%` / `width=20%` / `width=75%`）
  - **見出し行（`.system-error-label`）**: 面 `brand.accent`（navy — **通常の一覧・条件表の `brand.primary` とは違う色**）、
    文字 `text.on_dark`（白）
  - **明細行（`.system-error-body`）**: 面 `status.error_detail_surface`（palegoldenrod）、文字 `text.body`
- **詳細欄（`.system-error-detail`）**: `.field-textarea-readonly`（§4-2）を流用し、
  **高さを `control.error_detail_height`（400px）に広げ、幅を表と揃える**。**縦横スクロール付き**
  （`.field-textarea` の `overflow-y: scroll` に加え、横方向のスクロールも持たせる — `.system-error-detail` 固有の指定）。
  **静的テンプレート（`error.html`）には対応するマークアップが無く、キャプチャだけが根拠**（近似 — フレームワーク側が
  実行時に足している可能性がある）
- **区切り・戻る**: 素の `hr`（`border.rule`）と `.btn` をそのまま使う。**新しい部品は作らない**。
  **ボタンの文言はここに書かない**（**文言の正は画面マップ §4 と画面設計書**である。
  **新設した節では、この作法が適用されず文言を例示してしまいがちなので注意する**）
- **使う場面**: **シェル（アプリ共通部）のシステムエラー画面専用。** 業務画面では使わない
- **禁止**: 業務のバナー・通知（§4-8）にこの様式を使う / この様式を業務エラーに流用する（役割が違う） /
  見出し行の面を `brand.primary` にする（システムエラーだけ `brand.accent` を使う様式である）

## 5. レイアウトの原則（Layout Principles）

- **基準**: PC `layout.viewport_base`（1024×768 — ヘッダ表の 980px 幅から）。
  **1 業務画面をスクロール無しで収めることを目標**にする（努力目標。既存 UI は条件 40 項目 + 一覧 14 行を収めている）。
- **本文の幅は 2 段**: **既定 = `layout.content_width`（980px・抽出値・ヘッダと同じ幅）/
  上限 = `layout.content_max_width`（`layout.viewport_target` = 13 インチのノート PC 相当から起こした値）。**
  **980px では読めないと画面設計書が判断した画面だけ、上限まで広げてよい**
  （`.app-main-wide` を当てる。**ヘッダは広げない** — §4-4 B-3）。
  **中間の幅を作らない**（段は 2 つだけ。§4-1 のボタンの幅・§4-2 の入力欄の幅と同じ考え方）。**上限を超えない**
  - **「980px 固定 + 目標のビューポートで横スクロールしないことを努力目標にする」という形は採らない。**
    **努力目標は「980px に詰め込む」向きに効き、列の多い一覧が読めなくなる**（目視で 1 回で覆った）。
    **「詰め込まず、必要なら広げる」向きにし、上限をその歯止めにする**
  - **`content_width`（980px）は抽出値なので既定として動かさない。** 広げるのは**画面ごとの判断**であって、
    **既定が変わったのではない**
- **余白**: `spacing` の段だけを使う。段は詰めても飛ばさない。
  **縦に積む要素の間隔は器が持つ** — 本文領域は `.app-main`、節の内側は `.section` が与える
- **段組み**: 入力・条件は**表で組む**（§4-4 A）。1 行にラベル+値を最大 `layout.pairs_per_row`（4）組
  （**値の幅の段に応じて減らす** — §4-4 A の並べ方を見よ）
- **アクション行**: **本体の上か下に左寄せ**（`.button-area`）。既存 UI は
  条件表の下（検索画面）と本文の最上部（編集画面）の両方に置いており、**どちらに置くかは画面設計書が決める**
- **揃え**: 見出し・ラベルは左揃え。右揃えは数値・日付・金額の列だけ（`.list-cell-num`・§4-11 の日のセル）
- **ラベルと単位**: 項目ラベルは**入力欄の左**（表のラベルセル）。単位は値の直後に文字で置く
- **幅と溢れ**:
  **本文の幅は既定 980px で、ヘッダと同じ幅である。**
  **ページごと横に動かさない** — **一覧は列幅の段を割り付け**（§4-4 B）、
  **段の合計が器を超えるぶんは表の入れ物（`.list-scroll`）が中で横に流す**（§4-4 B-1b）。
  **入れ物を横に送らせたくない画面は、代わりに 1 行を 2 段に折り返す**（§4-4 B-2）。
  **それでも読めない画面だけ上限まで広げる**（§4-4 B-3 の「収まらないときの順序」）。
  **縦スクロールは許す**（§5 の「1 画面に収める」は努力目標である）
- **禁止**: 文字サイズの縮小で収める / 必須項目の折りたたみ / 本文を中央寄せの狭幅にする /
  **ラベルを入力欄の上に置く**（既存 UI は左）/ **ページを横にスクロールさせる** / 列を削って収める
  > **但し書き**: **禁じているのは「ページごと」の横スクロールである。**
  > **`.list-scroll`（一覧の表の入れ物）が中で横に流れることは禁じていない**（§4-4 B-1b）。
  > **出どころは【人】判断の文言そのもの** — **「ページごとの横スクロールをやめる」**であって、
  > **表専用のスクロールには触れていない**。**抽出元も同じ形**（`pwtgo004` の一覧は 47 列・合計 7500px を
  > `#freezingDiv` > `.SearchList_list_block` という見出し固定のスクロールペインに入れている）。
  > **この 1 語を広く読んで段を px から % に落とすと、段が語彙として機能しなくなる**（§4-4 B-1b）

## 6. 奥行きと階層（Depth & Elevation）

| 段 | トークン | 使う場面 |
|---|---|---|
| なし | `elevation.none` | **既定 — 表・入力欄・節・ボタン・ダイアログのすべて** |
| 内側の影 | `elevation.inset` | 入口画面のお知らせ欄（読み取り専用の複数行入力）だけ |

- **この案件は影で階層を作らない。** **面の色と 1px の格子線だけで構造を見せる**（§1）。
  ダイアログの階層は背景の暗さ（`overlay.backdrop`）で作る
- 禁止: 色付きの影 / 落ち影（`box-shadow` の外側）/ ガラス風（backdrop-blur）/ 角丸で階層を示す

## 7. Do / Don't（Do's and Don'ts）

**Don't（禁止 — 全画面共通）**

- 絵文字を UI 文言に使わない / 記号文字（✓ ✕ ▼ + 等）をアイコン代わりに使わない
- **新しいグラデーション・写真・イラスト・テクスチャ・独自の装飾色を作らない。**
  ただし**既存 UI が持つ画像は流用する** — ヘッダの地紋（`asset.header_band`）と入口画面の矢印
  （`asset.menu_arrow`）は既存 UI のものをそのまま使う（§4-10）。
  **例外は 1 つだけ — 印刷の透かし（§4-12）**（【人】判断。§1-1b の #5）。
  **文字だけで描き、色は既存 UI に在る淡い灰と同じ値を役割名で持つ**（`text.watermark`）。
  **これ以外の装飾を「あった方が親切」で足さない**（足すなら §1-1b に記録し、人が決める）。
  **ロゴは流用しないので置かない** — WiNG のロゴは在るが**別案件のもの**である
  （この案件のロゴを用意できたら差し替える — §1-1 の #11）
- マーケ調の見出し・ヒーローセクションを業務画面に入れない
- **状態色（`status.*`）を状態以外に使わない** — 表のセルの面・ラベル・ページの背景・区切り・
  用途別ボタン・装飾に使わない。**この既存 UI は警告色に似た色を構造に使っている**
  （`surface.subtle` のクリーム・`brand.required` の金・`surface.calendar` の橙）が、
  **それらは状態ではないので取り違えない**（§2 の禁止）。
  **例外は 1 つだけ — システムエラー画面（§4-13）**（§1-1b の #11）。
  **`status.error_detail_surface` はそこだけで使い、業務画面の表には使わない**
- **構造・用途の色を状態の意味に使わない**（上の逆向き。`text.current` の crimson をエラーに使う等）
- **必須を記号 `*` や「必須」の文言で示さない**（ラベルの文字色 `brand.required` で示す — §1 の癖）
- **ボタンの主副を色で表さない**（すべて同じ灰色 — §1 の癖）
- 押下時の scale・transform / 明朝体 / 角丸（`.banner-*` を除く）/ 落ち影
- **グローバルナビ・パンくず・現在地の帯・状態チップ・タブを作らない**（§1 の #1〜#6）

**Do（推奨）**

- 文言は敬体（です・ます）。命令形にしない。専門用語は要件の用語集に従う
- **ボタンのラベルにアクセスキーを括弧で付ける** — `更新(S)` `ｸﾘｱ(R)` `戻る(C)` の形（§1 の癖）
- 空状態: `該当するデータはありません`（**既存 UI の既定**。**画面設計書に文言があればそちらが正** — §4-9 / §9 #3）
- 処理中: `処理中です。しばらくお待ちください。`（**既存 UI の既定**。同上）
- 入力エラー: **画面上部の `.banner-error` に 1 行**（`コード：項目名:内容` の形。
  **コードを持たない案件は `項目名:内容` の 2 要素** — §4-8）**と、該当欄の面を桃色**にする（両方）
- 操作完了: `.banner-success` に結果を短く言い切る（「保存しました」）。装飾語・感嘆符・詫びを付けない
- **表記**: 日付は `yyyy/MM/dd`、数値・金額は 3 桁区切り + 単位
- **半角カナは既存 UI の文言をそのまま使う場合だけ**にとどめ、新しい文言では使わない
  （既存 UI の癖だが、新規の文言に広げる根拠は無い）

## 8. レスポンシブ（Responsive Behavior）と印刷

- **対象**: PC のみ（`layout.viewport_base` = 1024×768 基準）。**タブレット以下は対象外**と宣言する。
  **13 インチのノート PC（`layout.viewport_target` = 1280×800 相当）までを見る**
  （**努力目標ではなく、本文幅の上限の根拠として持つ**）
- **本文の幅は 2 段**（**既定 980px / 上限 = `layout.content_max_width`**。§5 / §4-4 B-3）。
  **`content_width`〔980px〕は抽出値のまま変えない。**
  **上限は `max-width` として持つ**ので、**ビューポートが狭ければ本文もそのぶん狭くなる**
  （**実測**: 1280×800 で縦スクロールバーが **15px** 取るため実効の表示幅は **1265px**。
  **`width: 1280px` と固定すると 15px ぶん横スクロールが出て §5 の禁止に触れる** — **`max-width` で持つのはこのためである**）
- 崩し方は定義しない（既存 UI に指定が無い）。
  **広い表は列を削らず、ページを横スクロールさせない**（§4-4 B-2）。
  **列幅の段を割り付けたうえで、器を超えるぶんは表の入れ物（`.list-scroll`）が中で横に流す**
  （§4-4 B-1b）。**入れ物を横に送らせたくない画面は 1 行を 2 段に折り返す**（§4-4 B-2）。
  **条件表はセル幅を内容相応にし、長い値を含む行は組数を減らす**（§4-4 A）。
  対応が必要になった時点で版を上げて本節を書く

### 8-1. 印刷

> **【人】判断**: **持つ。**「A4 の様式はあった方が親切」。
> **抽出元に `@media print` が無く、元に無いものを足した例外**である（§1-1b の #4）。

- **用紙**: `layout.print_page`（A4 縦）/ 余白 `layout.print_margin`（10mm）
- **出さないもの**: **ヘッダのリンク（`.app-header-links`）・アクション行（`.button-area`）・
  ページ送り（`.pagination`）・ダイアログ（`.dialog-backdrop` / `.dialog-panel`）。**
  **操作するためのものは紙に出さない**
- **出すもの**: ヘッダのロゴと利用者情報・本文・表・通知。
  **面の色と格子線はそのまま出す**（§1 の「面の色と 1px の格子線だけで構造を見せる」が紙でも成り立つため）
- **折り返しは画面と同じ**（§4-4 B-2）。**印刷のためだけに列を削らない**
- **広げた本文（`.app-main-wide`）も紙では A4 縦に収める**（
  **A4 縦の刷り幅は余白 10mm を引いて約 190mm ≒ 718px** で、**980px も上限の幅も入らない**。
  **紙では器の幅ではなく §4-4 B-2 の 2 段折り返しで収める**）。
  **印刷のために幅の段を切り替えない**（画面で `.app-main-wide` を当てた画面は、紙でも同じ内容を出す）
- **透かし**: §4-12（`.watermark`）。**印刷のときだけ出す**
- **禁止**: 印刷のために文字サイズの段を変える / 色を落として白黒にする / 1 ページに詰めるために行高を変える

## 9. エージェント向け指示（Agent Prompt Guide）

> mockup・実装を生成するエージェントは、次を守る。

1. **見た目は本書と `styleguide.css` だけから引く。** 色・余白・書体・角丸・影は CSS 変数（`var(--...)`）と
   §4 の部品クラスで指定し、**hex / rgb / px の生値をページ側に書かない**
2. **部品は §4 にあるものだけ**を使う。無い部品・状態は作らず・代用せず、`missing[]` に記録して報告する。
   **とくに Badge・タブ・選択行・グローバルナビ・パンくず・現在地の帯は本書に無い**（§1 の #1〜#6）。
   **カレンダーの起動ボタン（`.btn-icon-calendar`）は無い** — 日付欄から開く（§4-2 / #14）。
   **列ヘッダの並べ替えの印・複数選択の器も本書に無い**（抽出元に実体が無い / 単一選択で足りる。
   画面設計書が並べ替え・複数選択の操作を求めていても、印や器を代用で作らず `missing[]` に記録する）。
   **「システムエラー画面」（§4-13）はシェルのシステムエラー画面専用の様式**で、業務画面には使わない。
   **`.app-main-wide` は本文だけに当てる。ヘッダは広げない**（§4-10）。
   **`.condition-scroll` は条件表を必ず包む**（一覧の `.list-scroll` と違い、**包む・包まないの判断は無い**）。
   **`.control-group` は「入力欄と、その入力欄に付くボタン」を包む**（**横並びを保つ**）。
   **`.btn-icon` はズーム専用ではない** — **セルの中に入力欄と並べる短いラベル（1〜2 文字）のボタンはすべてこれ**である。
   **`.list-scroll` は列幅の段を当てた一覧の表だけを包む**（**段を当てていない表は包まない** — §4-4 B-1b）。
   **`layout.column` の段は px で持つ**（**`ordinal` だけは抽出値 25px を使えない** — §4-4 B / §1-1b #20）。
   **編集不可の状態の入力欄は `.field-flat` である**（**`.field-input-readonly` 系を当てるのは
   「編集できる画面の中の、その欄だけ入力できない」場合だけ**。§4-2 の「使い分け」を必ず読む）
3. **画面の構成・項目・操作・状態・文言は画面設計書に従う。** 本書を根拠に画面へ情報や操作を足さない。
   **ヘッダの見出しの文言・入口の表示文言・ナビ項目の文言は画面マップ §4 が正**（本書は様式だけを持つ）
4. **JS を書かない。** 状態は状態ごとに独立した静的ページで表す
5. 文言は §7 のトーンで。空・失敗など画面設計書に文言が無い状態は §7 の型で起草し、起草した旨を報告する
6. §7 の Don't に触れる表現が要件側にある場合は、実装せず報告する（本書を勝手に変えない）
7. 本書に足りない要素に気づいたら**「STYLEGUIDE.md への追記候補」として報告**する（本書を直接編集しない）
8. **本書は WiNG の既存 UI から抽出した**（§1）。**方針は既存画面の再現**なので、
   **案件に合わせて値を勝手に変えない**（差異は追記候補として報告する）
9. **`status.*` は通知（§4-8）と入力エラーの欄（§4-2）だけに使う。** 構造・装飾に使わない。
   逆に、値が似ている `surface.subtle` / `brand.required` / `surface.calendar` / `text.current` を
   **状態の意味に使わない**（§2・§7 の禁止）。**例外は 1 つだけ — システムエラー画面（§4-13）の
   `status.error_detail_surface`**。**そこだけの例外**で、他の表には広げない
10. **feature 間の導線は入口画面（`.app-menu`）である。** 各画面のヘッダには入口へ戻るリンクを 1 本置く。
    **ナビの帯を作らない**（§4-10）
11. **要素の選び方・描き方が様式の前提になっている箇所が 11 個ある。**
    (1) **§4-5 の Section は `fieldset` + `legend` で描く**（見出しが枠線の上に重なるのはブラウザの
    ネイティブ挙動で、`div` + `span` で描くと重ならず規定が成立しない）
    (2) **§4-4 の表は `table` で描く**（格子は `border-spacing` で作るため）
    (3) **§4-10 の入口画面のリンク一覧は `ul` / `li` で描き、リンクは `li` の中の素の `a` にする**
    （`.app-menu-item` を `a` に当てると inline になり、1 項目 25px も矢印の敷き込みも効かない）
    (4) **§4-10 のヘッダは 2 行の `table` で描く。**
    **`.app-header` を `table` に、ロゴのセルを `rowspan="2"` にし、利用者情報とリンクは 1 行目・2 行目に
    それぞれ `td` を置く**（`.app-header-meta` / `.app-header-links` は**セルに当てる**）。
    出どころの `common/header.html` がこの形（`<table class="header" width="980">`・ロゴが `rowSpan="2"`・
    右端の列が 2 行）で、**flex や float では右のリンクが行から落ちる**。
    **利用者情報の「2 行」は表の行が作る**ので、`.app-header-meta` 側に行の格子を持たせない
    (5) **§4-4 B の一覧は見出し行を `thead`・明細行を `tbody` に置く**（
    ゼブラは `:nth-child` で数えるため、見出し行が明細行と同じ親に居ると 1 つずれる。
    **2 段折り返し（`.list-row-2`）では 4 行ごとに数えるので、ずれると 1 件の途中で色が変わる**）
    (6) **§4-2 の日付欄（`.field-input-date`）は、mockup では素の `a`（`<a href>`）で描く。**
    **`input` の中に遷移は書けず、`input` を `a` で包んでも欄を押したときに遷移しない**ため、
    **欄そのものを `a` にする**（`.field-input` + 幅の段 + `.field-input-date` を当てると見た目は入力欄と同じになる）。
    **実装では入力欄（`input`）に戻る** — mockup が JS を持たないための描き方である
    (7) **§4-1 / §4-2 / §4-3 のボタン・入力欄・Select は `vertical-align: middle` を持つ。**
    **同じ `.btn` でも `<a>` と `<button>` でベースラインの取り方が違い、揃えないと縦がそろわない**
    （実測: `<a class="btn">` top 76.0px / `<button class="btn">` top 73.6px）。
    **とくに `.btn-icon` は隣の入力欄より下にずれやすい**ため、必ず付ける
    (8) **§4-1 のボタンは `display: inline-flex` + `align-items: center` + `justify-content: center` で
    ラベルを箱の中央に寄せる。** **(7) とは別物である** — **(7) は要素どうしの縦位置、
    (8) は要素の中の文字の縦位置**で、**(7) だけでは文字が箱の上に張り付いたまま残る**。
    **原因は `height` と `line-height` の差**（`.btn` は 23px に対し 15px）で、
    **既存 UI の `<input type="button">` ではブラウザが中央に置くので起きない**。
    **実測（修正前 → 修正後の「文字の上下の余白の差」）**: `<a class="btn">` **5.4px → 0.6px** /
    `<span class="btn-disabled">` **7.0px → 0.6px** / `<a class="btn-icon">` **6.0px → 0.0px** /
    `<button class="btn">` は**元から 0.6px**（ブラウザが寄せていた）。
    **`inline-flex` にしても寸法・`vertical-align`・入力欄との縦位置はいずれも変わらない**（実測で確認済み）
    (9) **§4-4 B の一覧の列幅は `<colgroup>` + `<col>` で割り付ける。**
    **`thead` の前に `<colgroup>` を置き、列の数だけ `<col class="list-col-*">` を並べる**。
    **セル側に幅を書かない** — **`table-layout: fixed` は「最初の行のセル幅」も見るが、
    `<col>` に寄せておくと 2 段折り返し（`.list-row-2`）でも見出しの分割に引きずられない**。
    **抽出元の `pwtgo005` がこの形**（`<colgroup>` の `<col style="width: …">` で 12 列を個別に割り付ける）。
    **`<col>` は幅だけを持つ要素で、面色も罫線も持てない**（面と罫線はセル側の `.list-header` / `.list-cell` のまま）
    (10) **段を当てた一覧は `<div class="list-scroll">` で包み、「余りを吸う列」を 1 本置く。**
    **4 つで 1 組である** — (1) **`<colgroup>` の段** (2) **`.list-scroll` の入れ物**
    (3) **余りを吸う列 1 本** (4) **`.section` の `min-width: 0`**（§4-5）。
    - **(3) が無いと**、余りが全列に比例配分されて px が正規化される（**段が宣言どおりの幅にならない**）
    - **(4) が無いと**、`fieldset` が中身の幅まで広がり、**入れ物が横に流れる代わりに「ページ」に横スクロールが出る**。
      **`.list-scroll` 側の `scrollWidth − clientWidth` はその間 0 のままなので、
      入れ物だけを見ても気づけない** — **はみ出しはページ（`documentElement`）で測る**
    **吸う列は「その列の `<col>` にクラスを書かない」だけ**で、**`<col>` そのものは出す**
    （**列数と `<col>` の本数は必ず一致させる**）。
    **どの列を吸う列にするかは画面設計書のレイアウト節（§3-x-2）が正**で、
    **段の px の合計が器を超える表には置かない**（§4-4 B-1b）。
    **段を当てていない表は `.list-scroll` に入れない**（**包む理由が無い** — 従来どおり等分される）
    (11) **条件表は `<div class="condition-scroll">` で包み、セルの中の入力欄とボタンは `<span class="control-group">` で包む。**
    **どちらも「判断」を伴わない** — **条件表は必ず包み、入力欄 + そのボタンは必ず群にする。**
    - **`.condition-scroll` が無いと**、**`.condition-table` が `table-layout: auto` で中身の最小幅まで広がり、
      節から溢れて「ページ」に横スクロールが出る**（**ビューポートが狭いほど溢れが大きい**）。**列幅は行をまたいで共有される**ので、
      **`xl` を 1 組だけ置いた行が在ると 4 組の行の 2 列目まで広がる** — **§4-4 A の「並べ方」の目安では防げない**
    - **`.control-group` が無いと**、**セルが狭いときに入力欄とボタンが縦に積まれる**
      （**1 セルが 3 段になり、行の高さが 3 倍以上になる**）
    - **群の幅が列に入るかは段の選択の責任**である（§4-4 B）。**入らなければセルの外に視覚的にはみ出す**が、
      **列の境目・表の幅・ページの横スクロールはいずれも動かない**
    - **短いラベル（1〜2 文字）のボタンは `.btn`（23mm）ではなく `.btn-icon`（40×22）**（§4-1）
12. **画像は `styleguide.css` の `--asset-*` から引く**（`background-image: var(--asset-...)`）。
    **ページ側に画像ファイルへのパスを書かない**（`<img src>` を使わない）— 相対パスは案件直下の正と
    `pages/tokens/` の写しで解決先が変わり、検査 A-2 の同一性が壊れる。
    **`asset.logo` は `none`** なので、ロゴの位置には**システム名の文字を仮に置く**（§4-10）。
    **その 90px の枠は「最終的にロゴ画像が入る場所」**で、**文字は差し替わるまでの仮の中身**である
    **文字が 2 行に折り返すのは想定どおり**なので、**窮屈に見えても枠を広げない**
    （広げるとロゴを入れた日にレイアウトがもう一度動く — §4-10 の但し書き）。
    **新しい画像を作らない・足さない**（要ると気づいたら追記候補として報告する）
13. **ページごとの横スクロールを作らない**（§4-4 B-3 / §5 / §8。**禁じているのは「ページごと」である** —
    **一覧の表の入れ物 `.list-scroll` が中で横に流れるのは禁止ではない**。§4-4 B-1b）。
    **本文の幅は 2 段** — **既定 980px（ヘッダと同じ）/
    上限 `layout.content_max_width`**（
    **`max-width` なので breakpoint ではない** — **画面が広ければ使い、狭ければビューポート幅までしか広がらない**）。**広げてよいのは画面設計書が「980px では読めない」と判断した画面だけ**で、
    **そのときは `.app-main-wide` を本文だけに当てる**（**ヘッダは広げない** — 幅は常に 980px で固定）。
    **収まらないときの順序は ① 条件表の組数を減らす → ①' 一覧の列幅の段を割り付ける →
    ①'' 入れ物（`.list-scroll` / `.condition-scroll`）が横に流す → ② 一覧を 2 段に折り返す → ③ 上限まで広げる**（§4-4 B-3）。
    **条件表にも入れ物が在る**（§4-4 A-1b）。
    **一覧では列を削らない**（`.list-row-2`・§4-4 B-2）。
    **2 段にしたらゼブラは 4 行ごと**で、**1 件の途中で色が変わっていないかを目で確かめる**。
    **条件表はセル幅を内容相応にし、長い値（`lg` / `xl`）を含む行は組数を減らす**
    （§4-4 A — **1 行に置く組数はラベル幅を固定せず、値の幅の合計で決める**）。
    **`colspan` で列をぶち抜かない**（**行によって列の境目が動く組み方をしない**。
    表のどの行も同じ格子になるなら `colspan` を使ってよい）
14. **月次カレンダー（§4-11）は固定の 1 か月を HTML で描く。** JS を書かず、日付のセルはただの表示にする。
    **プラグインの既定テーマの色・画像を持ち込まない**（色は本書のトークンだけ）。
    **開く導線は日付欄である**（**起動ボタンは無い**）:
    **カレンダーは独立した状態ページとして持ち、日付欄（`.field-input-date`）からそのページへ遷移させる。**
    **遷移元は日付欄そのもので、欄の横の何かではない**（#11 の (6) の描き方）。
    **画面設計書 §3-x-4 の操作表に「日付欄を押す → カレンダー」の行が無い場合は、リンクを張らずに
    `missing[]` に記録して報告する**（**部品だけが在って操作と状態が無い食い違い**は、
    リンク先が実在するせいで動線検査を通り抜ける — 目視が実際にこれを拾ったことが在る）
15. **印刷の透かし（§4-12）は印刷のときだけ出す。** 画面の状態ページでは出さない（§8-1）
16. **システムエラー画面（§4-13）はシェル（アプリ共通部）専用。** **業務エラーの `.banner-error`（§4-8）と
    混同しない** — フレームワークが処理を継続できない回復不能なエラーの様式で、業務画面のバナー・通知には使わない。
    **`.system-error-table` は `.list-table` / `.condition-table` と違って格子線を持たない**
