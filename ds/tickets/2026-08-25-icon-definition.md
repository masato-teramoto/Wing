# アイコン定義の新設（ICN-01〜06）— 現状調査と対応案（2026-08-25）

> 起票元: 密度・レイアウト要望 9 件（`tickets/2026-08-25-density-and-layout-requests.md`）の対応中に判明した
> 「各 spec がアイコンの存在を前提にしているのに、アイコンそのものの定義が DS のどこにも無い」構造上の穴。
> ユーザー指摘（2026-08-25「アイコンの定義ってあった方がよい？」）を受けて起票。
> 検討方針（2026-08-24 決定・GAP / REQ 起票と同じ）: まずデジ庁デザインシステム（DADS）に該当があるか確認し、
> あれば採取。無い・準備中なら独断で確定せず人間に方針案を提案し承認を得る。
> 調査日: 2026-08-25（DADS 基本デザイン「アイコン」概要 / アクセシビリティ = 2025-07-30 更新・v2.17.1、
> 「利用上の注意事項」「リソース」ページ、Material Symbols リポジトリ〔google/material-design-icons〕を参照）。
>
> **凡例**
> - **A（採取・着手可）**: デジ庁に公開済みガイドラインがあり、そのまま採取できる。承認不要（内容確認のみ）
> - **B（要承認）**: デジ庁に該当が無い／準備中のため自社翻案、またはトークン追加・既存規定の撤回を伴う。
>   「推奨案」を提示するので、承認・修正を返してほしい
>
> **全体の見立て**:
> 1. **アイコンセットはデジ庁と同じ Material Symbols（Apache License 2.0）を採用すれば、デジ庁準拠かつライセンスが明快**。
>    DADS「利用上の注意事項」に「デザインデータ（Figma）には一部 Material Symbols のアイコン素材が含まれ、当該素材には
>    Apache License 2.0 が適用される」と明記されている。一方 DECISIONS.md:18 で「使わない」としている「イラストレーション・
>    アイコン素材」（別規約・行政手続きの説明コンテンツ用・線/塗り 60 種）は **UI 部品用のアイコンとは別カテゴリ**であり、
>    UI アイコンまで除外する必要はなかった → DECISIONS.md の記述を分けて書き直す（ICN-01）
> 2. デジ庁の「アイコン」基本デザインは **a11y と配置の 4 型（フロント / リード / テール / エンド）のみ公開**。サイズ（px）・
>    weight / fill・色・ラベルとの間隔・語彙（どのアイコンを何に使うか）は公開ページに無い（Figma データ内の指定値は第二段で採取）
>    → a11y・配置は採取（A）、サイズ・スタイル・語彙・トークン・置き場所は自社翻案（B）
> 3. 本票は **IconButton 不採用（GAP-14）を再開しない**。「アイコンは必ずラベルと組み合わせる」は維持し、その前提で
>    「どのアイコンを・どの大きさで・どう置くか」を定める

---

## 0. 現状（調査結果）

### DS 内でアイコンを前提にしている箇所（少なくとも 10 部品 + 2 パターン）

| 部品・パターン | 記述 | 定義済み | 未定義 |
|---|---|---|---|
| NotificationBanner | 「type に対応するアイコン（必須）」、role="img" + aria-label、色は type の semantic 色、タイトルとの間 space.sm | a11y・色・間隔 | **どのアイコンか**・サイズ |
| Disclosure | 「開閉アイコン（必須。タイトルの左・開で 180 度回転）」、aria-hidden | a11y・回転 | どのアイコンか・サイズ・色 |
| Table | 「ソート操作はヘッダセル内の button で行い、テキストとアイコンの両方を操作領域にする」 | 操作領域 | どのアイコンか（未ソート / 昇順 / 降順）・サイズ |
| Button | 「表示領域の都合でアイコンを添える場合もラベルは省略しない」 | ラベル必須 | 位置（左/右）・サイズ・間隔 |
| Pagination | 「前へ」「次へ」テキストラベル必須、aria-hidden | ラベル必須 | 矢印アイコンの有無・種類 |
| Tabs | タブラベルをアイコンのみにしない | ラベル必須 | 併用時の位置・サイズ |
| DatePicker | カレンダーボタン、aria-hidden | a11y | どのアイコンか・サイズ |
| Combobox / Select | 開閉・クリア | — | 矢印・クリアのアイコン |
| ModalDialog / NotificationBanner | 閉じる「× 閉じる」（SVG は aria-hidden） | a11y | どのアイコンか・サイズ |
| Link | 外部リンク | — | 外部リンクの印（アイコン）の有無 |
| RepeatingFieldGroup | 「+ 行を追加」、削除ボタン | — | 「+」を記号文字で書くのかアイコンか |
| list-page | 検索・一括操作 | — | 検索アイコンの有無 |

- **トークン**: `font.size`（body 16 / caption 13 / heading 24）のみ。アイコン寸法の段は無い（`tokens/tokens.json`）
- **色**: `tokens/ROLE-MAP.md` §2「文字・アイコン」で色役割は定義済み（意味色のアイコン = NotificationBanner のみ）。
  「アイコンは親の文字色を継承する（currentColor）」という横断規則は無い
- **a11y**: 装飾 = aria-hidden / 情報 = role="img" + aria-label が **各 spec にバラバラに書かれている**（NotificationBanner・
  Disclosure・Pagination・DatePicker・RepeatingFieldGroup・Skeleton）。横断規則としては未定義
- **禁止事項**: brand-principles.md:13「絵文字を UI 文言に使わない」のみ。記号文字（✓ ✕ ▼ ×）をアイコン代わりに使うことの
  可否は未規定で、`scripts/audit-tokens.mjs` も検出しない

### モック側で起きていること（別リポジトリ mock-trial の `.../mock`、コミット bfa54b7 — デザイン担当者のローカルにあり本リポジトリからは参照不可）

- NotificationBanner の type アイコンを **Unicode 記号 `✓` `✕` のテキスト**で実装（`detail-notice.html:40` ほか 4 画面）。
  `.ds-notificationbanner-icon { font-weight: bold }` のみで、サイズ規定なし（本文フォントサイズに追従）。
  記号文字はフォント・OS で字形と太さが変わり、warning / info のアイコンは表現手段が無いため未実装。
  → REQ-03 の `white` 直書きと同じ「規定が無いので代用で凌ぐ」構造。**定義を置かないと部品ごと・画面ごとにばらつく**

### デジ庁 DADS の該当

| 項目 | DADS | 分類 |
|---|---|---|
| アイコンセット | Figma デザインデータに **Material Symbols** を含む（Apache License 2.0 明記 — 利用上の注意事項） | 採取可（採用判断は要承認 → ICN-01） |
| 配置の型 | 基本デザイン「アイコン」概要（2025-07-30・v2.17.1）: **フロント / リード / テール / エンド** の 4 仕様（ブロック / インラインの位置に対応） | A |
| a11y | 同「アクセシビリティ」（2025-07-30）: ①ラベル必須 ②ラベル併用時は代替テキスト不要（alt=""）、単体ならラベル相当の代替テキスト ③コントラスト 4.5:1（テキスト列内）/ 非テキスト単体は 3:1 ④ラベルがリンクならアイコンもリンク範囲に含める（別 a 要素にしない） ⑤単体使用時は 44×44 CSS px 以上 | A |
| サイズ（px）・weight / fill・色・間隔 | 公開ページに **規定なし**（Figma データ内の指定値は第二段で採取） | B |
| 語彙（用途 → アイコン名） | 規定なし | B |
| 「イラストレーション・アイコン素材」 | 別規約・行政手続き説明用（線 / 塗り 60 種）。UI 部品用ではない | 使わない（現行どおり） |

---

## A. 採取・着手可（1 件）

### ICN-02 デジ庁「アイコン」a11y・配置規定の採取 — ✅ 2026-08-25 対応完了

> `icons/ICON-MAP.md` §4（配置 4 型）/ §5（a11y ①〜⑤の採取 + 運用形）に採取。NotificationBanner の role="img" 維持は ICN-05 で承認。

- **内容**: 上表の a11y ①〜⑤ と配置 4 型を横断規則として 1 か所（ICN-06 の置き場所）に書き、各 spec の個別記述はそこへの参照に揃える
- **既存 spec との整合**:
  - ①ラベル必須 → Button / Pagination / Tabs / GAP-14 の規定と一致（変更なし）
  - ②「ラベル併用時は alt=""」→ Disclosure / Pagination / DatePicker / ModalDialog 閉じるの aria-hidden と一致。
    **NotificationBanner だけ** type アイコンに role="img" + aria-label「成功」等を付けており、デジ庁原則（ラベル = タイトルがあるので
    alt=""）と厳密には異なる。タイトル文（「保存しました」）だけでは種別〔成功 / エラー / 警告 / 案内〕が伝わらないケースがあるため
    現行の自社翻案を維持する案を推奨（→ 判断点は B の ICN-05 に置く）
  - ③コントラスト → 意味色トークンは白背景で success 5.1 / info 6.3 / danger 4.6 を満たす。**warning（amber.600・約 3.2:1）は
    「非テキスト単体 3:1」は満たすが「テキスト列内 4.5:1」は満たさない** → warning アイコンはタイトル文字列の一部にせず独立要素として置く
    （現行 NotificationBanner の構成〔アイコン + タイトル〕で成立。追記のみ）
  - ④リンク範囲 → Link の外部リンク印（ICN-03）に適用
  - ⑤44×44 → 単体使用は原則禁止のため該当なし（明記のみ）

---

## B. 要承認（5 件）

### ICN-01 UI アイコンセットの確定 — Material Symbols（Outlined・Apache License 2.0）— ✅ 2026-08-25 承認・対応完了

> (a)(b)(c) すべて推奨どおり。`icons/ICON-MAP.md` §1 に確定、DECISIONS.md「使わないもの」を書き分け。LICENSE 全文は SVG を同梱する第二段で配置
> （第一弾は SVG 実体を配布していないため再配布は未発生）。

- **現状**: DECISIONS.md:18「使わないもの: Figma データ・イラスト・アイコン素材（MIT と別条件のため）」— イラストレーション素材と
  UI アイコンを区別せず一括で除外しており、代わりが決まっていない
- **デジ庁**: UI 部品のアイコンは Material Symbols（Figma データに同梱、Apache 2.0）。イラストレーション・アイコン素材は別規約
- **推奨案**:
  1. **Material Symbols を UI アイコンセットとして採用**（デジ庁と同一セット = デジ庁部品の見た目と揃う。Apache 2.0 は商用可・
     改変可・帰属表示は LICENSE / NOTICE の同梱で足りる）。スタイルは **Outlined** 1 種に固定（Rounded / Sharp は使わない）
  2. **配布形態は SVG**（npm `@material-symbols/svg-400` 等の個別 SVG をインライン or スプライト化）。**可変フォント版は使わない**
     — フォント未ロード時にリガチャ名（`check_circle`）がテキストとして露出する、静的 HTML 検証で外部フォント依存になる、の 2 点
  3. DECISIONS.md:18 を「**Figma データ・イラストレーション・アイコン素材（別規約）は使わない。UI アイコンは Material Symbols
     （Apache 2.0）を採用**」に書き分け、パッケージに Apache 2.0 の LICENSE を同梱する
  4. 語彙外のアイコンが必要になったときも Material Symbols の範囲内で選び、無ければ起票（自作 SVG は作らない）
- **判断してほしい点**: (a) Material Symbols 採用と Apache 2.0 同梱 (b) Outlined 固定 (c) SVG 配布（フォント版不採用）

### ICN-03 アイコン語彙（カタログ）の固定 — 「カタログに無いアイコンは存在しない」— ✅ 2026-08-25 承認・対応完了

> (a) 16 種を `icons/ICON-MAP.md` §2 に固定 (b) **`external` は B = 装飾扱い**（aria-hidden。「（新しいタブで開きます）」の隠しテキストが
> 情報を担う — Link spec `external_guidance`。判定規則「アイコンが唯一の担い手なら情報、文字で書けるなら装飾」を §2 に明記）(c) 起票制を採用
> （§6 候補欄）。Combobox のクリアは第一弾で設けないため `close` の使用箇所から除いた。

- **現状**: 部品と同じ「index.json に無いものは存在しない」原則がアイコンには無い。spec は「開閉アイコン」「ソートアイコン」と
  役割名で書くだけで、実装者（エージェント）が毎回アイコンを選ぶ
- **デジ庁**: 規定なし（Figma データの部品ごとの使用アイコンは第二段で突合）
- **推奨案**: 現行 spec から逆算した **必要最小の語彙 16 種**を `icons/ICON-MAP.md` に「役割 → Material Symbols 名 → 使う部品」で固定。
  役割名（左列）を spec 側の正式な呼び名にし、アイコン名の差し替え（第二段のデジ庁突合）で spec を書き換えなくてよいようにする

  | 役割（spec で使う名） | Material Symbols 名（案） | 使う部品・箇所 | 種別 |
  |---|---|---|---|
  | `status-success` | `check_circle` | NotificationBanner type=success | 情報 |
  | `status-error` | `error` | NotificationBanner type=error / form-page エラーサマリー | 情報 |
  | `status-warning` | `warning` | NotificationBanner type=warning | 情報 |
  | `status-info` | `info` | NotificationBanner type=info | 情報 |
  | `close` | `close` | NotificationBanner・ModalDialog の「× 閉じる」/ Combobox のクリア | 装飾 |
  | `expand` | `expand_more` | Disclosure 開閉（開で 180 度回転）/ Select・Combobox の開閉矢印 | 装飾 |
  | `sort-none` / `sort-asc` / `sort-desc` | `swap_vert` / `arrow_upward` / `arrow_downward` | Table ソート可能列のヘッダ（状態は aria-sort で伝える） | 装飾 |
  | `prev` / `next` | `chevron_left` / `chevron_right` | Pagination「前へ」「次へ」 | 装飾 |
  | `calendar` | `calendar_today` | DatePicker のカレンダーボタン | 装飾 |
  | `add` | `add` | RepeatingFieldGroup「+ 行を追加」（記号文字「+」を置き換え） | 装飾 |
  | `remove` | `delete` | RepeatingFieldGroup 行削除 / detail-page 削除 | 装飾 |
  | `external` | `open_in_new` | Link の外部リンク（テール配置） | 情報（代替テキスト「外部リンク」または aria-hidden + 可視注記 — 判断点） |
  | `search` | `search` | list-page 検索ボタン | 装飾 |

  - 「情報」= 隣接ラベルだけでは伝わらない意味を持つ（type / 外部遷移）。「装飾」= ラベルが意味を担うので aria-hidden
  - **語彙に無いアイコンが必要になったら追加せず起票**（does_not_exist_yet と同じ運用。ICON-MAP に「候補」欄を設けて溜める）
  - edit / download / print / filter / menu 等はまだ spec に登場しないため**今回は入れない**（必要になった時点で起票）
- **判断してほしい点**: (a) 16 種の語彙とアイコン名 (b) `external` を情報扱い（代替テキスト）にするか装飾扱いにするか
  (c) 起票制の採用

### ICN-04 サイズ・スタイルのトークン化 — `icon.size` 3 段 + weight / fill 固定 — ✅ 2026-08-25 承認・対応完了

> (a)(b)(c) すべて推奨どおり。`tokens/tokens.json` に `icon.size.sm / md / lg` = 16 / 20 / 24px を追加（t-shirt 命名）。DECISIONS.md トークン対応表に行を追加。

- **現状**: アイコン寸法のトークン無し。モックは本文フォントサイズに追従（結果的に 16px 相当）
- **デジ庁**: 公開規定なし。Material Symbols 既定は 24px（optical size 20〜48、weight 100〜700、fill 0 / 1）
- **推奨案**（暫定値。第二段でデジ庁 Figma の指定値へ突合）:

  | トークン | 暫定値 | 用途 |
  |---|---|---|
  | `icon.size.sm` | 16px | caption（13px）文字に隣接 / Table ソート / Badge 内（使う場合） |
  | `icon.size.md` | 20px | body（16px）文字に隣接 / Button・Link・Tabs・Disclosure・Pagination・閉じる |
  | `icon.size.lg` | 24px | NotificationBanner の type アイコン / ModalDialog 見出し横（使う場合） |

  - **weight 400・fill 0（線）・grade 0 に固定**。状態（選択・アクティブ）を fill 切り替えで表さない（状態は色トークンと aria で伝える。
    REQ-03 の「色役割」と同じ規律 — 表現軸を増やさない）
  - optical size は寸法に一致させる（16 → 20 opsz、20 → 20、24 → 24。SVG 配布なら `@material-symbols/svg-400` の該当ファイルをそのまま）
  - 44px ターゲット領域は**アイコンではなく操作要素（Button 等）側の規定**とし、アイコンを拡大して満たさない
- **判断してほしい点**: (a) 3 段の値（16 / 20 / 24） (b) weight 400・fill 0 固定 (c) 命名（t-shirt で space / radius と揃える）

### ICN-05 横断規則（配置・間隔・色・a11y・禁止事項）— ✅ 2026-08-25 承認・対応完了

> (a)〜(d) すべて推奨どおり。`icons/ICON-MAP.md` §4〜§6、`tokens/ROLE-MAP.md` §2 に currentColor 既定を追記、`brand-principles.md` 禁止リストに
> 記号文字を並記、`AGENTS.md` ハード制約に追加、`scripts/audit-tokens.mjs` に検出 3 種（icon 要素内テキスト / 記号文字のみの要素内容 / CSS content:）を追加。

- **現状**: 各 spec に断片的に書かれており、横断規則が無い。記号文字・絵文字の転用禁止も未規定（brand-principles.md は絵文字のみ）
- **デジ庁**: 配置 4 型と a11y は採取（ICN-02）。間隔・色は規定なし
- **推奨案**（ICN-06 の置き場所に 1 か所で書く）:
  1. **ラベル必須**（既定・GAP-14 維持）。例外は NotificationBanner の type アイコン（タイトルが隣接するため単体ではない）のみ
  2. **配置**: 既定は**リード**（ラベルの直前・左）。**テール**（直後・右）は「外部リンク」「開閉（Select / Combobox / Disclosure の矢印は
     部品の既存規定に従う）」のみ。フロント / エンド（ブロック端）は NotificationBanner の type アイコンのみ
  3. **間隔**: アイコンとラベルの間は `space.xs`（4px）。NotificationBanner の type アイコンとタイトルは現行 `space.sm`（8px）を維持
     （ブロック配置のため広め）。**縦位置は文字の中央揃え**（`vertical-align: middle` 相当。ベースライン揃えにしない）
  4. **色**: **親要素の文字色を継承する（currentColor）を既定**にし、アイコン専用の色トークンは作らない。独立して色を持つのは
     NotificationBanner の type アイコン（ROLE-MAP §2「意味色の文字」）のみ。disabled は disabled-text を継承する
  5. **a11y 二分**（ICN-02 ①②の運用形）: 装飾 = `aria-hidden="true"` + focusable="false"。情報 = `role="img"` + `aria-label`（語彙表の
     「情報」列）。NotificationBanner の type アイコンは**現行どおり role="img" + aria-label「成功 / エラー / 警告 / インフォメーション」を維持**
     （デジ庁原則〔ラベル併用時 alt=""〕からの自社翻案。理由: タイトル文だけでは種別が伝わらない場合がある。デジ庁実装の
     NotificationBanner が alt="" だった場合に合わせるかは第二段の判断点として記録）
  6. **禁止**: 記号文字（✓ ✕ × ▼ ▲ → + −）・絵文字・アイコンフォント（リガチャ）・自作 SVG・語彙外アイコンを**アイコンとして使わない**。
     `brand-principles.md:13` の「絵文字を UI 文言に使わない」に「記号文字をアイコン代わりに使わない」を並記
  7. **audit**: `scripts/audit-tokens.mjs` に、モック HTML のアイコン用要素（`*-icon` クラス）内のテキストノード・記号文字を検出する
     ルールを追加（REQ-03 の色キーワード検出と同じ「代用の芽を CI で摘む」運用）。汎用検出は難しいため対象は記号文字 12 種程度の
     許容リスト方式（判断点）
- **判断してほしい点**: (a) currentColor 既定 (b) 間隔 space.xs / 中央揃え (c) NotificationBanner の role="img" 維持 (d) audit 追加の範囲

### ICN-06 置き場所と参照経路 — 部品ではなく「基盤定義」として置く — ✅ 2026-08-25 承認・対応完了

> (a)(b) 推奨どおり。`icons/ICON-MAP.md` 新設、AGENTS.md 参照順序 5 番目に追加、11 部品 spec + list-page を語彙名 + ICON-MAP 参照に書き換え
> （`purpose` / `use_when` は不変 — index.json 再生成不要）。Button の a11y にあった「アイコンのみのボタンは隠しラベル」は GAP-14 と矛盾していたため削除。

- **現状**: 該当する置き場所が無い。`components/` は UI 部品、`tokens/` は値、`ROLE-MAP.md` は色役割
- **推奨案**:
  1. **`icons/ICON-MAP.md` を新設**（`tokens/ROLE-MAP.md` と同じ層・同じ書式）: ICN-02〜05 の規則 + 語彙表 + 候補欄。
     「アイコンを選ぶときはまずここを見る／無ければ起票」の運用ルールを冒頭に置く
  2. **`tokens/tokens.json` に `icon.size` を追加**（ICN-04）。`tokens/dist/` への反映は従来どおり第二段
  3. **`components/Icon` は作らない**（Icon は画面に単独で置く UI 部品ではなく、部品の内部要素。index.json の部品数を増やさず
     `does_not_exist_yet` にも載せない。IconButton 不採用と整合）。第二段で `.tsx` 実装を持つ際は内部ユーティリティとして持つ
  4. **AGENTS.md の参照順序に 1 行追加**（「アイコンは `icons/ICON-MAP.md` の語彙のみ。無ければ起票」）— ハード制約に「記号文字・
     絵文字・自作 SVG のアイコン転用禁止」を追記
  5. **各 spec の書き換え**（承認後）: NotificationBanner / Disclosure / Table / Button / Pagination / Tabs / DatePicker / Combobox /
     ModalDialog / Link / RepeatingFieldGroup のアイコン記述を語彙名（`status-success` 等）+ ICON-MAP 参照に揃える。
     list-page の検索・RepeatingFieldGroup の「+ 行を追加」の「+」を `add` アイコンに置き換え
  6. DECISIONS.md:18 の書き分け（ICN-01）と決定経緯の記録
- **判断してほしい点**: (a) 基盤定義として置く（Icon 部品を作らない） (b) AGENTS.md への追記

---

## トークン追加のまとめ（要承認・暫定値。第二段でデジ庁 Figma の指定値へ突合）

| トークン | 暫定値 | 用途 | ICN |
|---|---|---|---|
| `icon.size.sm` | 16px | caption 隣接 / Table ソート | 04 |
| `icon.size.md` | 20px | body 隣接 / Button・Link・Tabs・Disclosure・Pagination・閉じる | 04 |
| `icon.size.lg` | 24px | NotificationBanner type アイコン | 04 |

（色トークンの追加は不要 — currentColor 既定 + 既存の意味色。間隔は既存 `space.xs` / `space.sm`）

## 新設・改定のまとめ

| 対象 | 変更 | ICN |
|---|---|---|
| `icons/ICON-MAP.md`（新設） | 語彙 16 種・配置・間隔・色・a11y・禁止事項・起票運用 | 02 / 03 / 05 / 06 |
| `tokens/tokens.json` | `icon.size` 3 段 | 04 |
| DECISIONS.md:18 | 「イラストレーション・アイコン素材は使わない / UI アイコンは Material Symbols」に書き分け、LICENSE 同梱 | 01 |
| AGENTS.md | 参照順序 1 行 + ハード制約（記号文字・絵文字・自作 SVG のアイコン転用禁止） | 05 / 06 |
| brand-principles.md | 「記号文字をアイコン代わりに使わない」を絵文字禁止に並記 | 05 |
| scripts/audit-tokens.mjs | アイコン用要素内の記号文字検出 | 05 |
| 各 component-spec.json（11 部品）/ list-page | アイコン記述を語彙名 + ICON-MAP 参照へ | 06 |

## 対応状況（2026-08-25 更新）

- ✅ 完了 6 件: ICN-01〜06 — いずれも推奨案どおり承認（ユーザー指示「推奨の B で。起票してもらった内容で承認するので進めてほしい」2026-08-25）。
  ICN-03 (b) `external` = B（装飾扱い + 隠しテキスト）
- 変更ファイル: icons/ICON-MAP.md（新設）/ tokens/tokens.json（`icon.size` 3 件）/ tokens/ROLE-MAP.md / AGENTS.md / brand-principles.md /
  scripts/audit-tokens.mjs / DECISIONS.md / components: NotificationBanner・Disclosure・Table・Button・Pagination・Tabs・DatePicker・Combobox・Select・
  ModalDialog・Link・RepeatingFieldGroup / patterns: list-page
- `npm run ci` OK（DS 自身の違反 0）。追加ルールはモック（bfa54b7）に対して実行し、NotificationBanner の `✓` `✕`（4 画面 8 件）を検出することを確認
- mock-trial 側の `✓` `✕` 置き換え・Link.tsx の隠しテキスト実装は v0.0.5 以降の再生成時
- 第二段への申し送り: デジ庁 Figma データのアイコン指定値（サイズ・weight・部品ごとの使用アイコン）と NotificationBanner 実装の
  代替テキスト方針を突合し、ICN-03 / 04 / 05 の暫定値を確定する。SVG 同梱時に Apache 2.0 LICENSE / NOTICE を `icons/` に置く
- 決定の経緯は DECISIONS.md「2026-08-25: アイコン定義 ICN-01〜06 — 承認を受けて対応」に記録
