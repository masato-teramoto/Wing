---
name: wireframe-authoring
description: AIDD ワイヤーフレーム工程（MK1）の生成 Skill。requirements 承認後（Phase 4 ゲート通過後）・design（Phase 5）着手前に、当該 feature の承認済み requirements + steering 一式と DS（index.json → pattern.json → component-spec.json）から顧客確認用ワイヤーフレーム（使い捨て静的 HTML + wireframe-manifest.json）を .aidd/wireframe/<feature>/pages/ に生成する。JS なし・状態ごとに独立ページ・固定値ダミーデータ・トークンは CSS 変数参照のみ。トークン CSS は DS のトークン JSON からプロファイルの解決結果の全キーを出力する（使用の有無で絞らない）。生成のたびに監査（audit-tokens / audit-components）とトークン CSS の一致検査（同梱 scripts/check-tokens.mjs — 値の一致・全キー網羅・feature 間の同一性）を実行し exit 0 を完了条件とする（audit-ignore 使用禁止）。DS に無い型・部品は作らず・代用せず不足として記録する（DS への起票・改修は本工程のスコープ外）。画面内容の根拠は requirements + steering に置き（steering は業務の文脈・用語・状態遷移・ロール・制約値の根拠であって、他 feature の操作 UI を作ってよい根拠ではない）、Adjacent の隣接 feature が管理するデータは読み取り専用の参照表示までなら載せてよい。manifest には要件 ID を Requirement 単位（確定値）で記入する。requirements は承認済みのため本 Skill は一切改変せず、要件側の修正が要る気づきは要件変更の提案として報告する。画面にできなかった要件は黙って落とさず理由を分類して unrealized[] に申告し、開発者の承認（acknowledged）を得てから次フェーズへ進む（判定基準は「主要画面が生成できていれば進んでよい」）。wireframe プロファイルの場合は成果物の位置づけ注記をビューア外枠・README・manifest の wireframe_notice に出す（ワイヤーフレームページには書かない）。
disable-model-invocation: true
---

# MK1: ワイヤーフレーム生成（顧客確認用・使い捨て HTML）

> フロー内の位置・実行順・人間停止点・読み取り範囲の概要は **aidd-flow の
> 「ワイヤーフレーム工程」節が正**。本 SKILL.md が工程内の**生成規約と手順の正**。
> DS 詳細ルールの正本は **DS パッケージ内 `AGENTS.md`**（DS の版と一緒に配布される）。
> 複数 feature を生成する案件では、全 feature の生成・承認後に結合段
> （`wireframe-integration`）で統合してから MK2（顧客確認・人間）へ進む。

## 位置づけ（生成規約の前提）

- ワイヤーフレームは **`.aidd/wireframe/` に置く使い捨ての根拠資料**であり、仕様ではない。
  **根拠資料で正にしない**
- 生成は「変換」ではなく **DS データからの再導出**である。本実装は同じ DS データから
  再導出するため見た目が揃う — HTML はその見た目の「今回の描画」にすぎず、
  後工程でフロントエンド技術に変換する対象ではない
- 一致の保証レベルは**型・構成・状態・文言・トークン（色 / 余白 / 角丸 / 文字サイズ）**。
  pixel-perfect ではない（細部は本実装の部品が正）。MK2 の確認対象を
  「型・構成・文言」と定義するのはこのため
- 後工程（Phase 5 design-authoring）へ引き継がれるのは **wireframe-manifest.json
  （+ MK2 の指摘の記録）**。HTML 本体は MK2 後もそのまま参照資料として残す
- 不変条件は**「顧客が見たもの = DS で再現可能なもの」**。監査 exit 0 はこの運用形であり、
  fail が 1 件でも残るワイヤーフレームは顧客に提示しない

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

- 対象 feature・当該 feature の requirements の所在と **`status`（`approved` であること）**・
  参照ファイル（steering 一式 / DS の index.json / DS パッケージ内 `AGENTS.md` /
  雛形 `Templates/wireframe/wireframe-manifest.json`）・
  **DS の所在（既定 `ds/`）と版（タグ + 短縮 SHA）**・
  **出力ルート（既定 `.aidd/wireframe/`）**・
  **トークン CSS の作り方**（既定 = DS の `tokens/*.json` から生成 / DS が
  `dist/tokens.css` を同梱する版ならその複製）を宣言する。
- 機能一覧（機能 ID F-xxx）が案件に存在する場合はその所在も宣言する
  （L1 の requirements ワークフローの出力には存在しないのが通常 — 無ければ「無し」と宣言）。
- **トークンのプロファイル**（wireframe = 要件定義工程 / project = 案件ブランド /
  base = 既定）も宣言する。手順 3b（位置づけ注記の生成）の要否がこれで決まる。
  DS 側の対応表は `tokens/HARVESTING.md` の「プロファイル」節。

## 前提

- **当該 feature の requirements.md が承認済み**（frontmatter `status: approved`、
  または requirements 承認ゲートの通過が人間により確認済み）である。
  本工程は **requirements 承認後・design（Phase 5）着手前**にある
- **steering 一式が記入済み**である（受領していない steering を新設しない）
- **DS が版（タグ）指定で取得され、その所在が開始時に宣言されている**
  （既定の取得は aidd-flow「ワイヤーフレーム工程」節の手順 0 — `ds/` へ clone し
  .gitignore に追記。取得手段は問わない）
- DS が v0.0.1 以降（監査スクリプトの `.html` 対応・対象ディレクトリ引数・
  監査対象ディレクトリ内 audit-ignore の違反化）
- ワイヤーフレームが参照するトークン CSS（tokens.json 由来の CSS 変数定義）は、
  **本 Skill が DS のトークン JSON から解決して `pages/tokens/tokens.css` を生成する**
  （`tokens` ディレクトリは監査対象外 — 代わりに同梱の `scripts/check-tokens.mjs` で
  DS の解決結果と突き合わせる。手順 3 ⑤）。DS のタグに `tokens/dist/` が同梱されない間の
  運用であり、**解決の定義の正は DS 側**（`tokens/config.wireframe.mjs` の source 順）。
  DS が `dist/tokens.css` をタグ同梱する形に確定したら、生成をやめて複製へ切り替える
  （手順 3 の分岐）。**DS 側のファイル（`tokens/*.json`・`tokens/dist/`）は編集しない**

## 入力

- **当該 feature の `requirements.md`**（画面内容の根拠。承認済み = 記載の要件 ID は確定値）
- **steering 一式**（画面内容の根拠その 2。業務の文脈・用語・状態遷移・ロール・制約値。
  動線・語彙の根拠として主に効くのは `product.md`）
- DS データ（参照順序: `index.json` → `patterns/<name>/pattern.json` →
  `components/<Name>/<Name>.component-spec.json`）+ `brand-principles.md`（文言トーン）+
  DS パッケージ内 `AGENTS.md`（DS 詳細ルールの正本）
- manifest 雛形: `Templates/wireframe/wireframe-manifest.json`
- （任意）機能一覧（機能 ID F-xxx + 機能名 + 概要。案件に存在する場合のみ）
- **読まないもの（MUST NOT — 画面内容の根拠にしない）**: requirements 承認までの
  ワークフロー内部資料 — FAQ（faq.md 等）・質問ログ・品質ゲートレポート・checkpoint・
  turn-ledger・improvement-cycle 一式、および `docs/` 配下（システム構成資料であり
  UI の根拠ではない）。requirements に落ちていない情報は要件として確定していない

## 手順

```
- [ ] 0. 開始宣言。requirements（要件 / 受け入れ基準）から画面候補を洗い出す。
        画面内容の根拠は requirements + steering に置く（→ 画面に載せる情報の根拠）。
        steering を根拠に載せた情報は、どのファイルのどの節を根拠にしたかを
        手順 4 で notes に残す
- [ ] 1. index.json を読み、各画面のパターンを use_when 照合で選ぶ（近似で当てない）。
        画面 × 状態の一覧を作る（states は pattern.json の states を網羅 + 長文などの品質状態）
- [ ] 2. 不足（パターン・部品・トークン）を does_not_exist_yet と突合して確定する。
        不足があれば**不足として記録**し（manifest の missing[] — 手順 4）、該当画面は
        近い部品や自作部品で仮組みしない（未画面化になる場合は手順 4c の申告に載せる）
- [ ] 3. **トークン CSS を `pages/tokens/tokens.css` に用意する**。DS が
        `tokens/dist/<プロファイル>/tokens.css` を同梱する版ならそれを複製する。
        同梱しない版（現行）は、DS の `tokens/config.wireframe.mjs` の source 順
        （`primitive.json` → `semantic.json` → `semantic.<プロファイル>.json`）で
        解決して書き出す。**書式は次に固定する**（feature ごとに割れさせない）:
        ① 変数名は DS のキーをケバブに落とす
           （`color.semantic.background` → `--color-semantic-background`）
        ② **プロファイルの解決結果に現れる全キーを出力する**（使用の有無で絞らない —
           画面で使っていない semantic キー・primitive も漏れなく含める）。
           理由: feature ごとにキー集合が割れると `wireframe-integration` 手順 2 の
           「全 feature の tokens.css は同一内容」という前提が仕様上満たされず、
           同一性の機械検査もできなくなる。
           そのうえで **semantic は primitive を `var(--...)` で参照する形を保つ**
           （値を展開しない — オーバーレイの層が読めなくなる）
        ③ 冒頭コメントに出所を記録する（DS のタグ・source にした JSON・解決方法）
        ④ **DS の JSON に無い値を足さない・値を変えない**（不足は手順 2 の記録へ）。
           DS 側のファイル（`tokens/*.json`・`tokens/dist/`）は編集しない
        ⑤ **生成直後に一致検査を実行し exit 0 を確認する**（監査 2 本と同じ扱い = 完了条件。
           失敗したら手直しせず生成し直す）。`tokens.css` は監査スクリプトの
           `SKIP_DIRS` に入っており audit-tokens / audit-components では検出できないため、
           この検査が唯一の機械検査になる:
              node .claude/skills/wireframe-authoring/scripts/check-tokens.mjs \
                   <DS所在> <出力ルート>/<feature>/pages/tokens/tokens.css \
                   --profile <プロファイル>
        そのうえで、状態ごとに独立した静的 HTML を `<出力ルート>/<feature>/pages/` に
        生成する（全ページからこの tokens.css を相対参照する。プロファイルの見た目
        〔無彩色化・意味色の残し方〕はこの CSS の値が全て担う）:
        JS なし / 表示データはすべて固定値ダミー（実在の人名・社名を転記しない）/
        画面間の遷移は素の <a href> / 部品は ds-<name> クラス /
        色・余白・角丸・文字サイズは var(--...) のみ / 文言トーンは brand-principles.md
- [ ] 3b. wireframe プロファイル（要件定義工程）で生成した場合のみ、位置づけ注記の
        置き場所を作る（project プロファイルでは作らない）:
        ① 監査対象ディレクトリの外に `<出力ルート>/<feature>/wireframe-viewer.html` を 1 枚
           — 注記帯 + <iframe src="pages/<入口ページ>.html">。定型文は下の
           「注記の定型文」から**逐語で**引く（言い換えない）。ビューアは成果物の梱包物で
           あり製品 UI ではないため、DS 部品・ds- クラスを使わない。
           色・余白は pages/tokens/tokens.css の var() を使う
        ② `pages/README.md` に同じ定型文 + 生成条件（DS タグ・プロファイル名）
        ③ manifest の `wireframe_notice` に雛形が持つ圧縮済み定型文をそのまま記録
           （言い換えない — 手順 4）
        ワイヤーフレームページ側の HTML は変更しない（注記を画面に混在させない）
- [ ] 4. wireframe-manifest.json を雛形どおり `pages/` に生成する:
        ds_version = 参照した DS のタグ、token_profile = 宣言したプロファイル、
        screens[] = screen × pattern × components × states × requirements
        （**要件 ID を Requirement 単位で配列**。AC 単位では書かない —
        1 つの画面群が複数 AC にまたがるのが通常で、AC ごとの 1:1 割り付けは恣意的になる。
        承認済み requirements の ID = 確定値）
        × functions（機能一覧が存在する場合のみ。無ければ空配列）、
        missing = 手順 2 の結果。confirmed_at は null のまま（MK2 で人間が記入）。
        wireframe プロファイルの場合は `wireframe_notice` に雛形が持つ圧縮済み定型文を
        そのまま記録する（言い換えない。他プロファイルは null）
- [ ] 4b. 被覆の自己確認: **UI に関わる要件 ID がすべて screens[] のどこかに現れているか**を
        突合し、現れていない要件 ID を出力に列挙する。
        **① 否定形の受け入れ基準（「〜しない」等 — 不在は画面要素として指し示せない）
        ② バックエンド専用処理**（非同期送信・ログの記録／非記録・バッチ処理等 —
        UI に現れないことが仕様）は「UI に関わる要件」から外し、分母に入れない
        （外した要件 ID と類型を notes に列挙する — 見落としと区別できる形で残す）。
        埋め合わせの画面をひねり出さない — 落ちている要件は MK2 実施・設計着手の
        判断材料として報告する（要件側の手当てが要る場合は要件変更の提案として報告する）
- [ ] 4c. **未画面化要件の申告**: 手順 4b で落ちていた要件と、DS 不足で作らないと判断した
        画面を manifest の `unrealized[]` に記録する
        （`requirements`〔Requirement 単位〕/ `screen`〔未定なら null〕/ `reason` /
        `category` = **DS 不足 / requirements 起因 / UI 対象外 / その他**）。
        **`unrealized[]` と手順 4b の未被覆一覧を突合し、片方にしか現れない要件 ID を残さない**。
        該当が無ければ `unrealized` は空配列 `[]` にする（`null` にしない）。
        `acknowledged` は雛形の形のまま `by` / `at` / `decision` を未記入（`null`）で出力する
        （オブジェクト自体を `null` にしない。記入するのは開発者 — 「完了後」節）
- [ ] 5. 監査を実行し、結果を manifest の audit ブロック（ran_at / scripts / result）へ
        機械記録する（<DS所在>・<出力ルート> は開始宣言の値。既定 ds/ と .aidd/wireframe/）:
        node <DS所在>/scripts/audit-tokens.mjs <出力ルート>/<feature>/pages
        node <DS所在>/scripts/audit-components.mjs <出力ルート>/<feature>/pages
- [ ] 6. exit 0 を確認する。fail は 2 分岐: 対応するトークン・部品が DS にあるのに
        生値・誤クラスを書いた → HTML を再生成して修正 / 合うトークン・部品が DS に無い →
        不足として記録し該当箇所は作らない（勝手にトークン・部品を追加しない）。
        audit-ignore は使わない。
        **アイコンの不足はここに当てはめない** — 3 原則の書き分けのとおり、装飾アイコンは
        付けずにラベルのみで組んで続行し記録する（監査はアイコンの不在を違反にしない。
        検出するのは記号文字・絵文字による代用のみ）
- [ ] 7. 完了条件の自己確認: 全画面 × 全状態のページが manifest の screens[] と一致 /
        監査 exit 0（audit ブロック記録済み）/ **トークン CSS の一致検査 exit 0**（手順 3 ⑤）/
        不足（missing[]）の一覧と
        **未被覆の要件 ID**（手順 4b）/ **`unrealized[]` の一覧と、そのうち主要画面に
        当たるものの有無**（手順 4c）を出力に明示
```

## 画面に載せる情報の根拠（生成規約）

画面内容の根拠は**当該 feature の requirements** に置き、根拠の無い情報・操作を画面に
足さない（顧客は画面から要件を読み取るため、足した情報はそのまま合意事項として扱われる）。
**requirements に書かれていない項目・制約・採番規則を画面上で確定させない**（仕様の先取り。
「業務上あって自然だから」は根拠にしない）。

- **例外 1 — DS パターンが規定する構造要素は requirements の根拠を要しない。**
  pattern.json の `layout` / `states` が構えとして定める要素（一覧のフィルタ行・ページング、
  承認画面の承認履歴セクションなど）は、**画面の型であって内容の主張ではない**。
  構えを requirements 根拠が無いことを理由に外すと、パターン準拠が崩れ `never_do` に
  抵触する組み方へ流れる。構えが業務に合わないと判明した場合は**外さず、DS 側の課題として
  記録・報告する**
- **例外 2 — Adjacent の参照表示。** requirements の **Adjacent に列挙された隣接 feature /
  隣接システムが管理するデータは、読み取り専用の参照情報として表示してよい**
  （どのフィールドを・どの粒度で見せるかは本 Skill の生成判断 — 本来この粒度は設計工程が
  埋めるが、MK1 は設計工程を挟まずに生成するため生成規約としてここに置く）。
  参照してよいのは**読み取りまで**。隣接 feature が担う操作（登録・更新・承認など）の
  UI を作ることは越境であり、Adjacent に挙がっていない feature / システムのデータも足さない
- **steering は他 feature の操作 UI を作ってよい根拠にはならない**。steering に他 feature の
  業務が書かれていても、作ってよいのは当該 feature の requirements が担う操作の画面だけ
- **feature 横断で共有する識別子（管理番号・申請番号等）のダミーデータは、書式が
  requirements にも steering にも無い場合、汎用的な数値のみの形式を既定とする**。
  独自のプレフィックス（`DEV-`・`REQ-` 等）を feature ごとに創作しない
  （複数 feature が同じ識別子を別書式で創作すると結合段で不整合になる）

## 注記の定型文（wireframe プロファイル — 逐語で使う・言い換えない）

> **これは要件定義段階のワイヤーフレームです**
> 画面の型・構成・情報量のイメージを掴むためのものです。この機能・この UI で実装することを
> 確約するものではありません。
> 色・書体・細部の見た目は未確定です。ブランドの色は基本設計の工程で決めます。

置き場所は **① 提示時の口頭説明 ② pages/README.md ③ manifest の `wireframe_notice`
（圧縮形 — 雛形 `Templates/wireframe/wireframe-manifest.json` が持つ値を逐語で使う）
④ ビューア外枠の帯** の 4 か所。**ワイヤーフレームページの HTML には
書かない**（「顧客が見たもの = DS で再現可能なもの」の不変条件に反し、DS に無い注記表現は
監査対象にもならないまま実装物と誤解されるため）。開発者向けの一時的な補足も HTML に
書かず manifest の `notes` に記録する。
（project プロファイル〔設計工程の顧客確認用〕でのビューアの要否は未決 — 確約する立場が
異なるため、この定型文を流用しない）

## 出力

```
<出力ルート>/<feature>/                       … 既定 .aidd/wireframe/<feature>/
├── wireframe-viewer.html   … wireframe プロファイルのみ（注記帯 + iframe。監査対象外）
└── pages/                  … 監査対象ディレクトリ
    ├── *.html              … 状態別ページ（使い捨て。MK2 後は作り直さない）
    ├── wireframe-manifest.json（audit ブロック記入済み）
    ├── README.md           … wireframe プロファイルのみ（定型文 + 生成条件）
    └── tokens/tokens.css   … トークン CSS（監査対象外）
```

報告に必ず含める:

- 不足（missing[]）の一覧
- **未画面化要件の申告一覧**（`unrealized[]` の内容 + 主要画面に当たるものの有無 + 承認依頼）。
  **画面が 1 枚も作れなかった場合も、この申告を出して終わる**（何も出さずに終わらない）
- **要件変更の提案**（あれば）: 生成の過程で見つかった、requirements 側の手当てが
  要りそうな点の一覧（本 Skill では requirements を直さない — 変更は L1 の変更管理に従う）

## ガードレール（本 Skill 固有 — 共通不変条件に加えて）

- 【MUST NOT】**承認済みでない requirements からワイヤーフレームを生成する**
  （`status: approved` を確認できない場合は停止して人間に確認する。
  承認ゲートを本 Skill で代行・省略しない）
- 【MUST NOT】JS を書く（バリデーション・遷移分岐・データ引き継ぎ・部品挙動の再現を含む。
  挙動の正は DS の部品実装 — 挙動を見せる必要があれば DS の Storybook を使う。
  JS が実行時に組むスタイルは監査〔文字列検査〕に掛からない）
- 【MUST NOT】**requirements にも steering にも書かれていない項目・制約・採番規則を
  画面上で確定させる**（→ 画面に載せる情報の根拠）
- 【MUST NOT】**steering に他 feature の業務が書かれていることを、その操作 UI を作って
  よい根拠として扱う**（越境）
- 【MUST】**識別子のダミー書式は汎用的な数値のみを既定とする**（プレフィックスを創作しない）
- 【MUST NOT】**終端画面（完了画面等）から他 feature の画面への案内リンクを張る**。
  feature 間の動線は結合段（`wireframe-integration`）の担当であり、MK1 の時点では
  リンク先の実在もパスも分からない。requirements の Adjacent / Out of Scope が明示的に
  「次にこの画面へ進む」と定めている場合を除く
- 【MUST】**pattern.json の `layout` / `states` が定める構造要素は、requirements に根拠が
  無くても外さない**（合わない場合は外さず DS 側の課題として記録・報告する）
- 【MUST】wireframe-manifest の screens[] に**要件 ID を Requirement 単位で記入する**
  （AC 単位では書かない。機能 ID F-xxx は機能一覧が存在する場合のみ併記）
- 【MUST NOT】位置づけ注記をワイヤーフレームページの HTML に書く（置き場所は
  「注記の定型文」の 4 か所）。ビューア外枠に DS 部品・`ds-` クラスを使わない
- 【MUST NOT】**画面にできなかった要件を黙って落とす・埋め合わせの画面をひねり出す**
  （理由を分類して `unrealized[]` に申告する）
- 【MUST NOT】MK2 実施済みの一式（manifest の confirmed_at 記入済み）に手を入れる

## 完了後

- **未画面化要件の承認**: 開発者が `unrealized[]` を確認し `acknowledged`
  （by / at / decision）を記入する。**承認なしに結合段・MK2 へ進まない**。
  ただし **`unrealized` が空配列 `[]` の feature では承認は不要**（`by` / `at` / `decision` は
  未記入のまま結合段・MK2 へ進んでよい）。承認待ちになるのは
  **「`unrealized[]` あり・`acknowledged` 未記入」のときだけ**であり、
  aidd-flow「ワイヤーフレーム工程」節の進行状態の機械判定表と同じ線である。
  判定基準はワイヤーフレーム段階では「**主要画面が生成できていれば進んでよい**」
  （主要画面 = 当該 feature の in_scope の中心となる操作の画面）。未画面化が主要画面に
  当たる場合は進めず、人間が扱いを判断する（DS 側の課題として別途扱う・要件変更を
  検討する等 — 本工程では解消しない）
- **複数 feature を生成した案件では、全 feature の生成・承認後に `wireframe-integration`
  （結合段）で統合する**（共通シェル・入口・feature 間リンク。1 feature の案件では不要）
- MK2（顧客確認・人間）へ。**実施の前提 = 監査 exit 0 + 未画面化要件の承認済み**
  （fail が 1 件でも残るワイヤーフレームは顧客に提示しない）
- **提示前に人がブラウザでビューア（無いプロファイルではページ）を開き、表示を確認する**
  — tokens.css の読み込み切れ・色定義漏れは生値を書いていないため監査では検出できず、
  レンダリングしないと分からない。**機械での見た目確認（ヘッドレスブラウザ等）は
  工程に持ち込まない**（実行環境・フォントに依存し案件ごとに結果が変わるため）
- MK2 の指摘は記録するにとどめ、**ワイヤーフレームは作り直さない**（使い捨て）。
  指摘の反映先は Phase 5（design-authoring）。MK2 実施後は開発者が manifest の
  `confirmed_at` を記入し、以後一式に手を入れない
