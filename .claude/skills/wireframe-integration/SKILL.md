---
name: wireframe-integration
description: AIDD ワイヤーフレーム工程（MK1）の結合段 Skill。feature ごとに独立生成したワイヤーフレーム（wireframe-authoring の成果物）を、共通シェル（ヘッダ・グローバルナビ・パンくず）・システム全体の入口・feature 間リンクの後付けで 1 本のプロトタイプへ統合する。触ってよいのは共通シェル・入口・リンクのパスだけで、各 feature の画面本文・項目・状態は変更しない。参照してよい案件情報は全 feature の requirements のタイトル / Introduction・feature-list.md・steering 全文に限り、入口・ナビの並び順とグルーピングは steering の業務プロセスの前後関係とロールを根拠に決めて根拠を報告する。入口は受領 feature に入口相当があれば新設せず流用し、新設分は .aidd/wireframe/_app-shell/ に擬似 feature として置く。統合後も監査 exit 0 と動線チェック（同梱 scripts/check-links.mjs — リンク切れ 0 件・入口から全 feature 到達）を完了条件とする。入口の tokens.css は feature 側からの複製で用意し、複製の前後に wireframe-authoring 同梱の scripts/check-tokens.mjs で全 feature の同一性を確認する（exit 0 が条件）。DS に無い型・部品が要る場合は作らず不足として記録する（起票・改修はスコープ外）。1 feature のみの案件では本 Skill は不要。
disable-model-invocation: true
---

# MK1 結合段: ワイヤーフレーム統合（共通シェル・入口・feature 間リンク）

> フロー内の位置・実行順・人間停止点は **aidd-flow の「ワイヤーフレーム工程」節が正**。
> 本 SKILL.md が結合段の**結合規約と手順の正**。DS 詳細ルールの正本は
> **DS パッケージ内 `AGENTS.md`**。
> **1 feature だけの案件では本 Skill は不要**（wireframe-authoring で完結）。
> **feature 間の動線は結合段の担当**であり、結合で触るのは共通シェル・入口・リンクの
> パスだけ（画面本文は変更しない）。

## 共通不変条件（wireframe-authoring / wireframe-integration で同一に保つ）

3 原則:

1. **画面への手直しで応急処置しない** — 見た目・部品の不備は記録し、画面で継ぎ接ぎしない
   （監査 fail の修正だけは再生成で行う）
2. **挙動・要件は L1 の仕様（承認済み requirements + steering）が正。見た目・部品は DS が正**
3. **DS に無いものは作らず記録** — 近いもので代用しない（DS への起票・改修は本工程のスコープ外）。
   **「作らない」の対象は不足しているもの自身であって画面ではない**。停止するものとしないものは
   DS 側で書き分けられている（正は DS の `AGENTS.md` ハード制約と `icons/ICON-MAP.md` §6
   「代替の既定」— v0.0.11 以降）:
   - **部品・パターンが `index.json` に無い** → 画面の骨格が作れないので**該当箇所を作らず記録**する
   - **アイコンが `ICON-MAP.md` の語彙に無い** → **画面を作らない理由にならない**。
     語彙外のアイコンは定義上すべて**装飾**（可視ラベルが意味を担う）なので、
     **アイコンを付けずにラベルのみで組んで続行**し、不足として記録する。
     停止するのは種別が**情報**（アイコンだけが分類を担う = NotificationBanner の `status-*`）の
     場合のみ
   - **語彙にはあるが SVG の実体が DS に無い**場合も同じ線で判断する（**装飾**なら付けずに続行 /
     **情報**なら該当する状態のページを作らず記録）。**SVG 実体を自作して埋めない**
     （`ICON-MAP.md` §6 の禁止 — 記号文字・絵文字・自作 SVG・語彙外の Material Symbols）。
     v0.0.11 時点の DS は `icons/` に SVG 実体を同梱していない（同梱は第二段の予定）ため、
     **NotificationBanner を要する状態は生成せず `missing[]` に記録する**のが現行の扱いである
     （2026-09-01 決定。装飾アイコン〔ModalDialog の閉じる・Pagination の前へ / 次へ・
     list-page の絞り込み〕は非配置で成立する）

ハード制約:

- 【MUST】UI 部品は導入済みの DS パッケージのみ使用。**新規 UI 部品の自作は禁止**
- 【MUST】DS は**版（タグ）を固定して参照**し、参照した版を wireframe-manifest.json の
  `ds_version` に記録する（取得手段は規約にしない — 満たすべきはこの 2 条件のみ）
- 【MUST】DS の参照順序: `index.json` → `patterns/<name>/pattern.json` →
  `components/<Name>/<Name>.component-spec.json`。存在確認は index.json で行い、
  **index.json に無い部品・パターンは存在しない**（不足は作らず・代用せず記録して報告）
- 【MUST】色・余白・角丸・タイポはトークン（CSS 変数）経由のみ。生値（hex / px）の直書き禁止
- 【MUST】部品の用途・禁止事項は各 component-spec の `never_use_when`、画面の組み方は
  pattern.json の `layout` / `states` / `never_do` に従う。requirements に文言が無い状態
  （空・エラー等）は DS の `brand-principles.md` のトーンで起草する
- 【MUST】監査（audit-tokens / audit-components）exit 0 を完了条件とし、audit-ignore は使用禁止
- 【MUST NOT】requirements.md を編集する（承認済み文書。要件側の手当てが要る気づきは
  「要件変更の提案」として報告し、変更の要否・実施は人間と L1 の変更管理に委ねる）
- 【MUST NOT】requirements 承認までのワークフロー内部資料（FAQ・質問ログ・品質ゲート
  レポート・checkpoint 等）を画面内容の根拠に使う（requirements に落ちていない情報は
  要件として確定していない — 根拠にすると正が二重になる）
- 【MUST NOT】生成済みワイヤーフレームを手で磨かない・部分修正しない（修正は再生成で行う。
  MK2〔顧客確認〕後は作り直さない）
- 【MUST NOT】承認行為（requirements の `status` 変更・`acknowledged` 記入・`confirmed_at`
  記入）を skill が行う — いずれも人間の担当
- 【MUST NOT】wireframe-manifest に視覚仕様を書かない（見た目の正は DS。
  例外: `wireframe_notice` は成果物の位置づけの宣言であり視覚仕様ではない）
- 【MUST】Markdown・表示文言は ja で記述する

## 開始時の宣言（MUST）

- 対象 feature の一覧と各ワイヤーフレームの所在（`<出力ルート>/<feature>/pages/` —
  既定 `.aidd/wireframe/`）・feature-list.md と steering の所在・
  **DS の所在（既定 `ds/`）と版（タグ + 短縮 SHA）**・トークンのプロファイル
  （wireframe / project / base）を宣言する。
- **受領 feature の中に入口相当（ホーム・ポータル・お知らせ一覧など）があるか**を宣言する
  （あれば新設せず流用する — requirements 由来の入口のほうが実運用に近い）。

## 前提

- 対象の全 feature が `wireframe-authoring` で生成済みで、**feature 単位で監査 exit 0** に
  到達している
- 各 feature の未画面化要件（`unrealized[]`）の承認は feature 側の工程で済んでいる
  （本 Skill では扱わない）。**`unrealized` が空配列 `[]` の feature は承認不要**であり、
  `acknowledged` の `by` / `at` / `decision` が未記入のままでも先へ進んでよい

## 入力

- 各 feature のワイヤーフレーム一式（`pages/` の HTML / wireframe-manifest.json）
- 全 feature の requirements の**タイトルと Introduction のみ**
  （入口のラベルに業務名を付けるために使う。**requirements の中身をもとに
  画面を足したり直したりしない**）
- **feature-list.md**（**案件に存在する場合のみ**。対象 feature の一覧・優先度・依存の
  SSoT — ナビの並び順の**補助**根拠。主たる根拠は steering であり、feature-list.md が
  無くても本 Skill は成立する。無い場合は steering と各 requirements のタイトル /
  Introduction だけで並び順を決め、**無かったことを報告に書く**）
- **steering 全文**（入口・グローバルナビの並び順とグルーピングの根拠。
  業務プロセスの前後関係・状態遷移・ロールが主に効く）
- DS データ（`index.json` → `pattern.json` → `component-spec.json`）+ `brand-principles.md`
- **読まないもの**: requirements 承認までのワークフロー内部資料（FAQ・質問ログ・
  品質ゲートレポート等）と `docs/` 配下（共通不変条件と同じ理由 — requirements に
  落ちていない情報を根拠にしない）

## 手順

```
- [ ] 0. 開始宣言
- [ ] 1. 共通シェル（ヘッダ・グローバルナビ・パンくず）を DS の範囲で定義し、
        全 feature の全ページに適用する。
        **新設する共通 CSS（shell.css 等）には、シェル内で使う ds-* クラス
        （ds-link・ds-button 等）の基本の色・背景定義（color / background 等）も
        必ず含める**（各 feature の CSS に定義済みの同名クラスと同じ値の複製で構わない。
        色定義が漏れると、そのクラスを使う共通シェル単独のページ——特に入口——で
        ブラウザ既定色が出るが、生値を書いていないため監査では検出されない）。
        **置き場所は各 feature の `<出力ルート>/<feature>/pages/` 直下（+ 入口を新設した
        場合は `_app-shell/pages/`）に同一内容で置く** — 監査対象ディレクトリの外に 1 本
        置いて相対参照すると `audit-tokens` / `audit-components` に掛からないまま
        全ページの見た目を決めることになる（tokens.css を feature ごとに置くのと同じ理由）。
        各 feature の styles.css より後に読み込ませ、**上書きしてよいのは共通シェルが
        規定する範囲（本体の幅・余白など app-shell の layout が定めるもの）だけ**にする
        （画面本文の見た目を上書きしない — ガードレール「画面本文を変更しない」と同じ線）
- [ ] 2. システム全体の入口を用意する。**受領 feature に入口相当があれば新設せず流用する**。
        新設する場合は `<出力ルート>/_app-shell/pages/` に擬似 feature として置く
        （監査・キャプチャの仕組みを feature と同じ形で使うため）。
        **`_app-shell` の wireframe-manifest.json は雛形の形のまま出力し、埋めるのは
        `ds_version` / `token_profile` / `wireframe_notice` / `audit` / `screens[]` /
        `missing[]` だけ**にする: `screens[].requirements` は空配列（requirements 由来では
        ないため要件 ID を持たない）、`unrealized` は空配列、`acknowledged` は未記入、
        `confirmed_at` は `null` のまま（要件を持たない = 未画面化要件の承認対象が無い）。
        `notes` に「requirements 由来でない共通物」であることと、入口・ナビの並び順の
        根拠（手順 4）を明記する。
        **`_app-shell/pages/tokens/tokens.css` は feature 側から複製する**
        （生成し直さない）。全 feature の tokens.css は同一内容になる —
        wireframe-authoring 手順 3 ② が「プロファイルの解決結果の全キーを出力する」
        （使用の有無で絞らない）と定めているため、feature ごとに使う部品が違っても
        キー集合は割れない。**複製の前に同一性を機械確認する**（exit 0 が条件。
        割れている feature があれば手直しせず報告する — 直すのは feature 側の再生成）:
              node .claude/skills/wireframe-authoring/scripts/check-tokens.mjs \
                   <DS所在> <出力ルート> --profile <プロファイル>
        複製後は `_app-shell` を含めた状態で同じコマンドを再実行し exit 0 を確認する。
        入口の形（ポータル / メニュー一覧 / いずれかの一覧画面の兼用 / ヘッダのナビだけ）は
        本 Skill の判断 — **DS に入口相当のパターンが無くて形を妥協した場合は、
        不足として記録・報告する**（起票・改修はスコープ外）
- [ ] 3. feature 間の相互リンク・各 feature から入口へ戻る動線を、素の <a href> の
        相対パスで張る。各 feature の終端画面（完了画面等）には、業務プロセス上自然な
        次の行き先が 1 つある場合のみリンクを張ってよい（wireframe-authoring の報告に
        「次に進むのが自然な行き先」があれば参考にする）。ただし **DS の confirm-flow
        パターンの never_do「完了画面に次の行動を複数並べる」に従い、複数は並べない**
- [ ] 4. **入口とグローバルナビの並び順・グルーピングを、steering に書かれた業務プロセスの
        前後関係とロール（+ feature-list.md の優先度・依存）に沿って決める**。
        機能名を根拠なく並列に並べない — 「利用者が業務のどの位置にいるか」が
        読み取れる形にする。どの並び順・グルーピングにしたか、それを
        **どのファイルのどの記述から導いたか**を報告に含める
        （根拠なく並べた場合はその旨を書く）
- [ ] 5. 監査を再実行し exit 0 を確認する（対象: 全 feature の pages/ +
        入口を新設した場合は _app-shell/pages/）。各 manifest の audit ブロックを更新する:
        node <DS所在>/scripts/audit-tokens.mjs <出力ルート>/<feature>/pages
        node <DS所在>/scripts/audit-components.mjs <出力ルート>/<feature>/pages
- [ ] 6. 動線の機械チェック: すべての <a href> の相対パスがファイルに解決すること
        （リンク切れ 0 件）と、入口から全 feature の入口画面へ到達できることを確認する。
        チェッカーは本 Skill 同梱（数えるだけ・判定はしない — 合否は本手順で下す）:
        node .claude/skills/wireframe-integration/scripts/check-links.mjs \
             <統合後のルート> --entry <入口の相対パス>
        状態バリエーション（error / loading / empty 等）はどこからもリンクされないのが
        正常 — ページ単位の到達率は判定に使わない
```

## 出力（報告に必ず含める）

- **入口を何として作ったか**（受領 feature の流用 / 新設 — ポータル / メニュー一覧 /
  一覧画面の兼用 / ヘッダのナビだけ）と**その理由**（DS に該当パターンがあったか）、
  **入口のファイルパス**
- **入口・グローバルナビの並び順とグルーピング、およびその根拠**
  （steering・feature-list のどのファイルのどの節から導いたか。根拠が無い場合はその旨）
- 触った箇所の種類別一覧: ① 共通シェルの適用 ② リンクパスの追加
  ③ 画面名・入口の不一致解消 ④ パンくず追加 ⑤ **画面本文の修正
  （原則 0 件。発生した場合はファイル名・箇所・理由を必ず書く）**
- 足した共通物（入口・ナビ・パンくず・shell.css 等）の一覧
  （requirements 由来でない追加物の明示）
- DS 不足の記録一覧（結合段で出たもの — 入口・グローバルナビ・パンくず相当の
  パターン不足など。起票・改修はスコープ外 — 記録が設計工程・DS 側検討の材料になる）
- 動線チェック（手順 6）の結果（リンク切れ件数・入口からの feature 到達）
- **トークン CSS の一致検査（手順 2）の結果**（全 feature の同一性・値の一致・全キー網羅。
  割れている feature があった場合はその一覧と差分キー — 本 Skill では直さず報告する）
- 監査 fail で修正した場合は、回数・落ちた監査・原因

## ガードレール（本 Skill 固有 — 共通不変条件に加えて）

- 【MUST NOT】**各 feature の画面本文・項目・状態を変更する**（触ってよいのは共通シェル・
  入口・リンクのパスだけ）。やむを得ず直した場合はファイル名・箇所・理由を必ず報告する。
  「統合成果物だから直してよい」を feature 画面本文に拡大解釈しない。
  feature 画面本文側の問題を見つけた場合は手直しせず報告する（扱いは人間の判断）
- 【MUST NOT】requirements の中身を根拠に画面を足す・直す（結合段が読んでよいのは
  タイトル / Introduction まで。画面内容の根拠づけは wireframe-authoring の担当）
- 【MUST NOT】steering に他 feature の業務が書かれていることを根拠に操作 UI を足す
  （wireframe-authoring と同じ線 — steering はナビの並び・グルーピング・ラベルの根拠に使う）
- 【MUST】新設した共通シェル・入口も監査対象とし、ds-* クラスと var(--...) のみで組む
  （JS なし・生値の直書き禁止は wireframe-authoring と同じ）
- 【MUST】wireframe プロファイルの場合、位置づけ注記の原則を維持する
  （注記をワイヤーフレームページの HTML に書かない — 置き場所は wireframe-authoring の
  「注記の定型文」の 4 か所）
- 【MUST NOT】MK2 実施済みの一式（manifest の confirmed_at 記入済み）に手を入れる

## 完了後

- 統合済みプロトタイプで MK2（顧客確認・人間）へ（**実施の前提 = 監査 exit 0 +
  各 feature の未画面化要件の承認済み**）
- **提示前に人がブラウザで入口から開き、表示を確認する** — 共通シェルの色定義漏れ
  （手順 1）・tokens.css の読み込み切れは生値を書いていないため監査では検出できず、
  レンダリングしないと分からない。**機械での見た目確認（ヘッドレスブラウザ等）は
  工程に持ち込まない**（実行環境・フォントに依存し案件ごとに結果が変わるため）
- MK2 の指摘は記録するにとどめ、ワイヤーフレームは作り直さない（使い捨て —
  反映先は Phase 5 design-authoring）
- feature 側を再生成した場合（MK2 前の監査 fail 修正等）は本 Skill を再実行する
  （シェル適用が再生成で消えるため）
