# 業務システム対応ギャップ — デジ庁調査結果と対応案（2026-08-25）

> 起票元: `tickets/2026-08-24-business-system-gaps.md`（GAP-01〜16）
> 検討方針（2026-08-24 決定）: まずデジ庁デザインシステム（DADS）に該当があるか確認し、
> あれば採取。無い・準備中なら独断で確定せず人間に方針案を提案し承認を得る。
> 調査日: 2026-08-25（DADS v2.17.1、コンポーネント 48 件）。
> 調査の生データはセッションのスクラッチパッドに保存（本ファイルには要点のみ転記）。
>
> **凡例**
> - **A（採取・着手済み）**: デジ庁に公開済みガイドラインがあり、そのまま採取した。承認不要（内容確認のみ）
> - **B（要承認）**: デジ庁に該当が無い／準備中のため自社翻案、またはトークン追加・パターン改定を伴う。
>   「推奨案」を提示するので、承認・修正を返してほしい
>
> **前提（2026-08-25 ユーザー回答）**: GAP-09 = ID / パスワード型のログイン画面が必要。
> GAP-10 = 印刷要件あり。GAP-16 = 承認画面（detail-page variant）+ 承認待ち一覧（inbox）まで対象。

---

## A. 採取・着手済み（3 件）

### GAP-03 FileUpload — spec 新設 ✅

- **デジ庁**: 公開済み（概要 / 使い方 / a11y、Rev002 2026-01-22。HTML / React 実装あり）
- **実施**: `components/FileUpload/FileUpload.component-spec.json` 新設。form-page の `components` に追加。
  does_not_exist_yet から除外
- **チケットの検討事項への回答**:
  1. 対応形式・サイズ上限はサポートテキストに明示必須（値の定義はアプリ側、表示作法は DS 側）— デジ庁準拠
  2. 状態は default / dragover / has-files / error。**アップロード進行・完了はデジ庁でも未定義**（部品は「選択」まで）。
     送信は form-page の submitting（Button loading）で表す。個別ファイル進捗は必要になれば起票
  3. 複数ファイル対応あり（multiple + 件数 / サイズ上限のクライアント検証）
- **a11y の例外**: ファイル選択結果は aria-live=polite、検証エラーは assertive（InputText の「aria-live 不使用」の例外。デジ庁実装準拠）

### GAP-05（前半）Table の行選択作法 ✅

- **デジ庁**: 行選択・全選択・indeterminate は公開済み（テーブル使い方 Rev002 2025-06-25 + selectable-table 実装）。
  一括操作 UI は「テーブルコントロール」が担う想定だが**ガイドライン準備中**（→ 後半は B）
- **実施**: Table spec に `row_selection_guidance` / `alignment_guidance`（数値・日付は右揃え）を新設、
  `never_use_when` に「行全体をクリック可能にしない」、a11y に全選択 / 行 Checkbox の aria 属性を追記。
  states に all-selected / header-indeterminate を追加
- **暫定**: 選択行ハイライトは専用トークン未登録のため暫定で `color.semantic.surface`。第二段でデジ庁 key-100 相当の淡色トークンを検討

### GAP-15 「※必須 / ※任意」表記の 5 spec 展開 ✅

- **デジ庁**: 公開済み（インプットテキスト使い方 + フォームコントロールラベル実装）。
  「※必須」= 赤 / 「※任意」= グレー、項目ラベルの右横。グループ（ラジオ / チェックボックス / 年月日）は
  fieldset の legend に付す。**required / aria-required はデジ庁は使わない**（可視テキスト方式 + 送信時 aria-invalid）
- **実施**: Select / DatePicker / RadioButton / Checkbox / RepeatingFieldGroup の a11y に追記。
  InputText / Textarea にも「※任意 = color.semantic.text-subtle」「required 属性不使用」を補記
- **部品特有の差分**（チケットの懸念どおり存在した）:
  - RadioButton / Checkbox グループ / DatePicker: legend に 1 回。各選択肢・各入力欄には付けない
  - Checkbox 単一項目（規約同意）: 項目ラベル右横
  - Checkbox: fieldset のみの aria-describedby では一部スクリーンリーダーが読まない既知問題 → 各 input にも付ける
  - RepeatingFieldGroup: グループの要否は legend、行内各項目の要否は各ラベル（テーブル状なら見出しセル）

---

## B. 要承認（13 件）

### GAP-01 保存成功フィードバック（NotificationBanner 新設 / Toast 不採用）— ✅ 2026-08-25 承認・対応完了

> 推奨案 1〜5 をすべて実施（トークン 3 件追加、NotificationBanner spec 新設、form-page save-success / save-error、
> detail-page / list-page notice、ModalDialog・brand-principles.md 更新）。詳細は DECISIONS.md 同日ログ。

- **デジ庁**: ノティフィケーションバナー **公開済み**（Rev001 2025-01-09）。type = success / error / warning / info-1 / info-2、
  style = standard / color-chip。アイコン + タイトル必須、閉じる「× 閉じる」、アクション最大 2。
  **role=alert / status / aria-live は一切使わない。自動消滅の規定なし。Toast 相当の部品は無い**
- **推奨案**:
  1. **NotificationBanner を採取して spec 新設**。type = success / error / warning / info（info-1 / 2 は info に統合）、style = standard のみ
  2. **Toast は作らない**（デジ庁に無い。自動消滅は読み終える前に消える・支援技術に伝わらない問題）。
     does_not_exist_yet に残し、NotificationBanner の confusable_with で誘導
  3. **form-page の states に `save-success` を追加**: 「保存後に表示する画面（detail-page へ遷移 / form-page に留まる — 遷移先はアプリ側判断）の
     本体先頭に NotificationBanner type=success『保存しました』。自動消滅させない」。
     detail-page / list-page の states にも `notice`（操作結果バナーの配置位置 = ページヘッダ直下）を追加し、3 パターンの components に NotificationBanner を追加
  4. a11y: aria-live は付けない（デジ庁準拠）。動的に挿入する場合はバナーのタイトルへフォーカス移動（**自社翻案**）
  5. **トークン追加（要承認）**: `color.semantic.success` / `warning` / `info` が現状無い（danger のみ）。
     暫定値案: success → primitive `green.700` #15803d（白背景 約 5.1:1）、warning → `amber.600` #d97706（約 3.2:1 — アイコン・枠線用。文字は text トークン）、
     info → `blue.700` #1d4ed8（約 6.3:1）。第二段でデジ庁 `--color-semantic-success-2` / `warning-yellow-2` / key 系へ移植
- **判断してほしい点**: (a) Toast 不採用 (b) セマンティック色 3 件の追加と暫定値 (c) save-success / notice の規定

### GAP-02 Combobox 新設 — ✅ 2026-08-25 承認・対応完了

> 自社翻案で `components/Combobox/Combobox.component-spec.json` 新設。Select（目安 6〜30 件）との境界を両 spec に明記。form-page に追加。

- **デジ庁**: ページはあるが**ガイドライン準備中**。Figma v2 のみ（2026-04-15 初版）。HTML / React 実装は「提供予定」で未公開。
  用途・構成・キーボード・a11y は一切非公開。Select ガイドラインからの誘導も無し
- **推奨案**: ModalDialog と同じ扱いで**自社翻案の spec を新設**（source に「デジ庁準備中・公開後突合」と明記）。
  内容は WAI-ARIA APG の Combobox（入力支援型）準拠: input role=combobox + aria-expanded + aria-controls → listbox。
  ↓で候補へ、Enter で選択、Esc で閉じる。候補 0 件メッセージ。非同期検索はアプリ側責務、部品は候補取得中の表示のみ規定。
  **Select との境界**: 既定選択肢を全件眺めて選べる（目安 6〜30 件）→ Select。それを超える、または名称で探す
  マスタ参照（取引先・社員・勘定科目等）→ Combobox。両 spec の confusable_with に明記
- **判断してほしい点**: (a) 自社翻案の承認 (b) 件数境界「30 件」の目安

### GAP-04 error-page パターン新設 — ✅ 2026-08-25 承認・対応完了

> `patterns/error-page/pattern.json` 新設（403 / 404 / 500 は app-shell 内、maintenance はシェル無し）。セッション切れは login + info バナー方針を記載（login 昇格時に整合確認）。

- **デジ庁**: **無し**（テンプレート / パターンの章そのものが存在しない）。近縁は NotificationBanner の error / メンテナンス告知用途と緊急時バナー
- **推奨案**: pattern `error-page` を新設（自社定義）。
  - variant: `403`（権限なし）/ `404`（見つからない）/ `500`（システムエラー）/ `maintenance`
  - 403 / 404 / 500 は **app-shell の内側**（ナビで復帰できる）、maintenance は**シェル無し**
  - **session-timeout はエラーページを作らない**: login 画面へ遷移し NotificationBanner type=info「一定時間操作がなかったためログアウトしました。再度ログインしてください」（GAP-09 依存）
  - 本体 = 見出し（何が起きたか）+ 説明 1〜2 文 + 復帰アクション 1 つ（Link appearance=button「一覧へ戻る」等。500 は「再試行」Button 可）
    + 補助情報（エラーコード・発生時刻・問い合わせ先、text-subtle）
  - **EmptyState は転用しない**（spec の never_use_when で「エラー状態の代用」を禁止済み）。Link / Button のみで組めるため部品追加なし
  - 文言は brand-principles.md（復帰手段を先に、詫びは短く）。never_do: 技術詳細（スタックトレース）の表示、長い詫び文、案内なしの自動リダイレクト、ヒーロー画像
- **判断してほしい点**: 承認。session-timeout を login 画面 + バナーで扱う方針

### GAP-05（後半）一括操作の作法（list-page 改定）— ✅ 2026-08-25 承認・対応完了

> list-page に選択アクションバー（rows-selected / bulk-action-done 状態）を追加。一括操作は secondary / danger のみで主アクション 1 つルールを維持。

- **デジ庁**: 一括操作・選択時アクションバーの記述**無し**（テーブルコントロール準備中）
- **推奨案**: list-page の layout に**選択アクションバー**を追加（自社翻案）。
  1 行以上選択時にフィルタ行と Table の間に出現。内容 = 「n 件を選択中」テキスト + 一括操作 Button variant=secondary（最大 3 つ）+ 「選択を解除」Button/Link。
  破壊的な一括操作は Button variant=danger + ModalDialog で件数を明記して確認。
  **「主アクション 1 つまで」との整合**: 一括操作は secondary / danger のみで primary を使わない → 既存ルールを維持。
  全ページ選択は非対応（Table spec に記載済み）。完了通知は NotificationBanner（GAP-01 依存）
- **判断してほしい点**: 承認

### GAP-06 Pagination — ✅ 2026-08-25 自社定義案を承認・対応完了（当初の見送り案は取り下げ）

> ユーザー回答「方針は納得だが必要な場面があるため自社定義したい」を受け、同日に自社定義案を提示し承認。
> `components/Pagination/` 新設（variant=simple はデジ庁 v2 採取、numbered は v1 参考の自社翻案。番号は現在 ±2、
> 総ページ数 6 以上で numbered、表示件数切替は第一弾では非提供）。list-page のページングを Pagination に差し替え、page-changed 状態を新設。

- **デジ庁**: ページナビゲーションは**引き続きガイドライン準備中**。ただし現行 v2 HTML 実装は **「前へ / 次へ + カウンター（5 / 9,999）」のみ**で
  番号リスト・省略記号・先頭 / 末尾は無い（番号付きは旧 v1 React のみ）。= 現行 list-page の簡易構成とほぼ一致
- **推奨案**: **専用部品化は見送り**、list-page のページング規定をデジ庁 v2 に揃えて改定:
  nav + aria-label は文脈名（「検索結果」等）/ カウンター「現在ページ / 総ページ数」+ 総件数 / **1 ページなら非表示** /
  **先頭・末尾では該当ボタンを非出力（disabled にしない）** / URL が変わるなら Link appearance=button、変わらないなら Button。
  番号ジャンプはデジ庁 v2 が廃止した構成のため提供しない（大量データは検索・絞り込みで対処）。Pagination / PageNavigation は does_not_exist_yet に残す
- **判断してほしい点**: 部品化見送りの承認

### GAP-07 advanced-search（list-page 拡張 + Disclosure 採取）— ✅ 2026-08-25 承認・対応完了

> `components/Disclosure/` 新設、list-page に詳細検索パネル（filters-applied / filter-empty）追加。advanced-search は does_not_exist_yet から除外。

- **デジ庁**: パターン**無し**。近縁: 検索ボックス（準備中）の実装に「詳細検索パネル」= details/summary の折りたたみ。
  **ディスクロージャー部品は公開済み**（メイン情報への追加情報の折りたたみ。タイトルは内容要約型、開閉で文言不変）
- **推奨案**: 独立パターンではなく **list-page の拡張**。
  - フィルタ行の右端に「詳細検索」**Disclosure**（開閉トグル）。展開時にフィルタ行の下へ詳細条件パネル（項目の作法は form-page 準拠・2 カラム許容）
  - パネル下部に「検索」Button variant=secondary + 「条件をクリア」Button variant=secondary（primary はページヘッダの主アクション用に温存）
  - 適用中の条件は件数表示の横にテキストで要約（チップ部品はデジ庁も準備中のため使わない）
  - **Disclosure spec を新設（デジ庁公開済みから採取）**。list-page の components に Disclosure / Select / DatePicker / Checkbox / RadioButton を追加
- **判断してほしい点**: (a) list-page 拡張案（独立パターンにしない） (b) Disclosure 採取 (c) 検索 Button = secondary

### GAP-08 Tabs 新設（自社翻案）/ Accordion 見送り — ✅ 2026-08-25 承認・対応完了

> `components/Tabs/` 新設（APG 準拠）、detail-page の関連情報に紐付け。Accordion は does_not_exist_yet に残し理由を注記。

- **デジ庁**: タブ = **準備中**（実装のみ。3 型のうち②「矢印キー型 APG 準拠 role=tablist」が「ウェブアプリ・管理画面で使用」とされる）。
  アコーディオン = **公開済み**だが用途は FAQ 等「同種セクションの連続」で、**「スペース節約目的で使わない」「重要な情報を隠さない」「テーブルを入れない」**と明記
- **推奨案**:
  1. **Tabs を自社翻案で spec 新設**（デジ庁実装②準拠: role=tablist / tab / tabpanel、←→↑↓ + Home / End、activation は auto、親見出し必須、URL を変えない表示切替専用。遷移なら Link 群）。
     detail-page layout の「関連情報セクション（見出し区切りまたはタブ）」の「タブ」を Tabs に紐付け、components に追加
  2. **Accordion は見送り**（業務の詳細画面の情報分割はデジ庁の禁止事項に該当。does_not_exist_yet に残す）。
     補足情報の折りたたみは GAP-07 で採取する Disclosure で対応
- **判断してほしい点**: (a) Tabs 自社翻案の承認 (b) Accordion 見送り

### GAP-09 login パターン新設（ID / パスワード型）— ✅ 2026-08-25 承認（パスワード表示切替あり）・対応完了

> `patterns/login/` 新設（シェル無し）。表示切替はテキストラベル付き Button + aria-pressed。

- **デジ庁**: **無し**。フォーム作法（ラベル / 要否 / エラー）は転用可
- **推奨案**: pattern `login` を新設。**app-shell の外側に置く初のシェル無しパターン**。
  - layout: 中央寄せ 1 カラム（幅は breakpoint.sm 未満に収める）。システム名（テキスト。color.semantic.brand のヘッダー帯を置いてよい）→
    NotificationBanner 領域（セッション切れ info / 認証失敗 error）→ ID InputText（autocomplete=username）→
    パスワード InputText（type=password、autocomplete=current-password、「パスワードを表示」切替 Button variant=secondary — **自社翻案**）→
    ログイン Button variant=primary → 「パスワードを忘れた場合」Link（任意）
  - states: auth-error（NotificationBanner type=error「ID またはパスワードが正しくありません」— どちらが誤りかは特定しない）/ submitting / session-timeout（type=info）
  - never_do: ID / PW のどちらが誤りかの明示、項目別リアルタイム検証、グローバルナビの表示、プレースホルダーのラベル代用、ヒーロー画像・マーケ文言
  - 責務境界: 認証処理・SSO 連携・ロックアウトはアプリ側
- **判断してほしい点**: (a) 承認 (b) パスワード表示切替の要否

### GAP-10 report パターン新設 / print-preview 見送り — ✅ 2026-08-25 承認・対応完了

> `patterns/report/` 新設、トークン `print.margin`（15mm）追加。print-preview は does_not_exist_yet に残す。

- **デジ庁**: 印刷スタイル・帳票レイアウト・印刷用トークンは**無し**
- **推奨案**:
  1. pattern `report` を新設（自社定義）: 帳票専用の印刷向けページ型。A4 縦 / 横 variant。
     ヘッダ（帳票名・出力日時・ページ番号）→ 本体（dl による名前-値 + Table）→ フッタ（注記）。
     `@media print` の方針を明記: app-shell / Button / Link / Disclosure トグルは非表示、Table はセル折り返し許可（ellipsis 解除）、
     色は text / border のみ（白黒印刷前提）、Badge は「［承認済］」のようなテキスト表現に置換
  2. **print-preview は見送り**: ブラウザの印刷プレビューに委ね、画面内プレビューの型は作らない（does_not_exist_yet に残す）
  3. **トークン追加（要承認）**: `print.margin`（暫定 15mm）。色は既存トークンで足りる
- **判断してほしい点**: (a) report のみ新設 (b) print-preview 見送り (c) print.margin 追加

### GAP-11 Skeleton 部品新設 + トークン追加 — ✅ 2026-08-25 承認・対応完了

> `components/Skeleton/` 新設、トークン `color.semantic.skeleton` 追加。各パターンの loading 参照を書き換え。

- **デジ庁**: スケルトン**無し**。プログレスインジケーター（スピナー / リニア + ラベル、role=status polite で「読み込み中です」、
  prefers-reduced-motion でアニメーション停止）が**準備中・実装のみ**
- **推奨案**: **Skeleton を部品として spec 新設**（自社定義）。ガイダンス扱いではなく部品にする理由: 現行の states が既に参照している +
  `audit-components.mjs` が index.json 未登録の `ds-skeleton` クラスを捏造扱いするため、登録が無いと実装できない。
  - 最終表示の形（見出し・行・セル）に合わせた矩形プレースホルダ。スピナー単体禁止は維持（ラベル付きスピナーは Button の loading のみ）
  - **トークン追加（要承認）**: `color.semantic.skeleton`（暫定 gray.200 のエイリアス。border と同値だが意味を分離）
  - アニメーション: 明滅（pulse）は任意、prefers-reduced-motion で停止（デジ庁準拠）
  - a11y: スケルトン本体は aria-hidden、置換対象のコンテナに aria-busy=true、視覚的に隠した「読み込み中です」（role=status polite — デジ庁プログレスインジケーター準拠）
- **判断してほしい点**: (a) 部品化 (b) トークン追加

### GAP-12 金額・数値入力（InputText ガイダンス追記 / InputNumber 不採用）— ✅ 2026-08-25 承認・対応完了

> InputText に `numeric_input_guidance` 新設。InputNumber は「作らない」と決定（名前は捏造防止で残す）。

- **デジ庁**: 専用部品・作法**無し**。近縁規定: 文字種を UI で制限しない / 必要な変換は**送信時または確認画面表示時**に自動で（入力直後・フォーカスアウト時の書き換えは混乱を招くので避ける）/
  maxlength 不可 / 幅は内容相応 / 単位「歳」の添え方可。日付ピッカー実装で `type=text inputmode=numeric` を採用
- **推奨案**: **InputNumber は作らない**。InputText spec に `numeric_input_guidance` を追加:
  `type=text` + `inputmode=numeric`（小数は decimal）、`type=number` 不可（スピン操作・スクロール誤入力）、金額・数量は右寄せ許容（Table の右揃えと整合）、
  単位は入力欄の右外にテキスト、**全角→半角・カンマ除去は送信時 / 確認時に自動変換（入力中・blur 時に書き換えない — デジ庁準拠）**、
  表示側（detail-page / Table / confirm-flow）は 3 桁区切り + 単位、幅は桁数相応、maxlength 不可
- **判断してほしい点**: 承認（InputNumber 不採用）

### GAP-13 年/月/日分割入力（DatePicker spec の拡張 / DateFieldSet 不採用）— ✅ 2026-08-25 承認・対応完了

> DatePicker に `variants.calendar`（false 既定 / true）と `variants.layout` を新設し「既知の日付は calendar=false」に書き換え。InputText / Select の参照先を更新。DateFieldSet は作らない。

- **デジ庁**: 日付ピッカー自体が**年月日 3 分割の input type=text の複合部品**で、既知日付には**同じ部品をカレンダーボタン無しで使う**
  （a11y ページ Rev002 に autocomplete bday-* / cc-exp-* 推奨。和暦は未提供・今後対応予定）
- **推奨案**: **DateFieldSet は作らず DatePicker spec を拡張**（デジ庁公開済みからの採取だが、既存 spec の意味が変わるため要承認）:
  purpose を「年/月/日を分けたテキスト入力による日付入力。前後を見ながら選ぶ日付にのみカレンダーボタンを付ける」に改め、
  variant `calendar: true | false` を明記。never_use_when の「既知日付には使わない」を「既知日付にはカレンダーボタンを付けない（calendar=false）」に修正。
  InputText / Select の参照先も DatePicker(calendar=false) に修正。autocomplete はアプリ側が付与する旨と和暦未対応を明記
- **判断してほしい点**: 承認

### GAP-14 行操作列は設けない / IconButton 不採用 — ✅ 2026-08-25 承認・対応完了

> Table / list-page / Button spec に反映。IconButton は名前のみ does_not_exist_yet に残す。

- **デジ庁**: 行操作列の作法**無し**。IconButton 部品**無し**。「アイコンは必ずラベルと組み合わせる」が原則。行全体クリック禁止（遷移先が 1 つならセル全体を Link 領域にしてよい）
- **推奨案**: チケット案 1 を採用 — **第一弾は行操作列を設けない**。list-page では各行の主キー列（番号・名称）を Link にして detail-page へ遷移し、
  編集・削除は detail-page ヘッダで行う。複数行への操作は GAP-05 の一括操作。**IconButton は作らない**（does_not_exist_yet 維持）。
  Table の never_use_when に「行ごとの操作ボタン列」を追加
- **判断してほしい点**: 承認

### GAP-16 approval / inbox パターン新設（既存パターンの variant として記述）— ✅ 2026-08-25 承認・対応完了

> `patterns/approval/` と `patterns/inbox/` を独立 pattern.json として新設。

- **デジ庁**: **無し**（チップラベルも準備中のまま）
- **推奨案**: `patterns/approval/pattern.json` と `patterns/inbox/pattern.json` を**独立ファイルとして新設**し、中身は既存パターン準拠 + 差分で記述
  （confirm-flow が form-page を参照する形式と同じ。index.json での発見性を確保し does_not_exist_yet から昇格）
  - **approval** = detail-page 準拠 + 差分: ヘッダ操作を「承認 Button primary + 差戻し Button secondary」に置換（編集 / 削除は置かない）。
    ステータス Badge。承認履歴セクション（見出し + Table: 日時・操作者・操作・コメント。単票の履歴に限る — 横断的な audit-log とは別）。
    差戻しは ModalDialog + Textarea（理由 ※必須）。承認は ModalDialog で確認（取り消せない旨）。完了後は inbox へ戻り NotificationBanner success（GAP-01 依存）。
    never_do: 承認と差戻しを同じ見た目にする、理由なしの差戻し、承認画面への編集フィールド混在
  - **inbox** = list-page 準拠 + 差分: 既定フィルタ「自分が承認者の承認待ち」、ステータス列 Badge、行選択 + 一括承認（GAP-05 依存。ModalDialog で件数確認）、主アクション（新規登録）なし
  - 権限モデル（誰が承認できるか）はアプリ側責務
- **判断してほしい点**: 承認（独立 pattern.json として登録する形式を含む）

---

## トークン追加のまとめ（要承認・すべて暫定値。第二段でデジ庁プリミティブへ移植）

| トークン | 暫定値 | 用途 | GAP |
|---|---|---|---|
| `color.semantic.success` | green.700 #15803d | NotificationBanner success | 01 |
| `color.semantic.warning` | amber.600 #d97706 | NotificationBanner warning（アイコン・枠線） | 01 |
| `color.semantic.info` | blue.700 #1d4ed8 | NotificationBanner info | 01 |
| `color.semantic.skeleton` | gray.200（border と同値・別名） | Skeleton プレースホルダ面 | 11 |
| `print.margin` | 15mm | report の用紙余白 | 10 |

（選択行ハイライト用の淡色トークンは第二段送り — Table spec に暫定 surface と明記済み）

## 対応状況（2026-08-25 時点）

- ✅ 完了 16 件: GAP-01〜16 すべて
- 新設: 部品 7（FileUpload / NotificationBanner / Combobox / Disclosure / Tabs / Skeleton / Pagination）、
  パターン 5（error-page / login / report / approval / inbox）、トークン 5（success / warning / info / skeleton / print.margin）
- 「作らない・見送り・別名」と決定して does_not_exist_yet に名前を残すもの: Toast / Accordion / IconButton / InputNumber / DateFieldSet / PageNavigation / print-preview
- 決定の経緯は DECISIONS.md の 2026-08-25 ログ参照
