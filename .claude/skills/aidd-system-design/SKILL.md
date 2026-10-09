---
name: aidd-system-design
description: 画面設計工程（簡素版）の入口。配布ワークスペースを開いた開発者が呼び、案件ルートを解決して、成果物側の担体（STYLEGUIDE.md §1-2 の確定 / 画面マップ features[] 行の confirmed / 画面設計書の status / mockup-manifest.json の status と viewed）だけから進行状態を判定し、次の 1 手を同じスレッドで実行して人の確定が要る点で停止する。実行する相手は styleguide-authoring（SG・案件に 1 回）/ screen-map-authoring（SD-0・案件に 1 つ）/ screen-spec-authoring（SD-1・feature ごと）/ mockup-authoring（MU・feature ごと）の 4 つで、各 skill の内部手順は肩代わりせず、その SKILL.md を読んでその手順に従う。案件側に成果物の所在と状態を案内する .aidd/screen-design/README.md を書く。人の確定（STYLEGUIDE.md の確定 / 画面マップ行の confirmed / 画面設計書の status: confirmed / mockup の viewed）は代行せず、人から受け取った内容の転記だけを代行して recorded_by を残す。画面の切り出し・項目・見た目そのものは決めない（それぞれ SD-0 / SD-1 / SG の役割）。案件の specs/ steering/ .aidd/gates/ .aidd/phase-progress.json .aidd/wireframe/ Templates/ には書かない（読み取り専用の入力）。
disable-model-invocation: true
user-invocable: true
argument-hint: "[案件ルート] [feature]"
---

# 画面設計工程（簡素版）— 一連の駆動

> **本 SKILL.md が工程内の位置・実行順・人間停止点の正**（実行規約は本書で自己完結する）。
> 各成果物の作成規約と手順の正は**各 skill の SKILL.md**。本書はそれを肩代わりしない。
> 本工程は AIDD 本フロー（`/aidd-*` の各コマンド）に載せない側流で、その生成物（`steering/` / `specs/<feature>/requirements.md` /
> `design.md`）を**読み取り専用の入力**にする。

## 位置づけ

- **design 承認**（対象 feature の `design.md` が `status: approved`）の後・`tasks.md` 着手の前に、
  **UI を持つ feature だけ**で実施する。上流の承認ゲートは増やさない・動かさない
- **生成単位が skill ごとに違う**: SG = **案件に 1 回**（初回のみ。2 feature 目以降は版の確認だけ）/
  SD-0 = **案件に 1 つ**（以後は増分）/ SD-1・MU = **feature ごと**
- **状態ファイルを増やさない。** 進行状態の正は**成果物側の 4 つ**（→「進行状態の機械判定」）
- **1 回の呼び出しで進むのは次の 1 手だけ。** 停止点で止まり、人が確定したら再度 `/aidd-system-design` を呼ぶと
  続きから進む（状態は成果物側にあるので**再入できる**）
- 機械検査の実行に **Node.js** が要る（MU）

## ハード制約

- 【MUST】**各 skill を実行するときは、`<skill 名>` の SKILL.md（配布ワークスペースの
  `.claude/skills/<skill 名>/SKILL.md`）を読み、その手順に従う。** 何をどう作るかの判断は各 skill が持つ
- 【MUST】**次に実行する skill 名と、その skill に渡す入力を宣言してから実行する**
- 【MUST】**定義した停止点で必ず停止する**（→「停止点」）。これ以外の停止点を増やさない
- 【MUST】**feature を跨ぐ SD-1 / MU の 2 本目は同じスレッドで回さない。**
  1 feature 分が停止点に達したら、「**新しいスレッドで `/aidd-system-design` を呼ぶ**」と案内して停止する
  （文脈の分離。他 feature を起草した文脈を引き継ぐと隣接 feature の操作 UI を足す越境が増える）
- 【MUST】案件単位で共有する成果物（画面マップ・`STYLEGUIDE-backlog.md`）への書き込みは **1 スレッドずつ**
- 【MUST NOT】**人の確定を代行する。** `STYLEGUIDE.md` §1-2 の `確定`・画面マップ行の `confirmed`・
  画面設計書の `status: confirmed`・mockup の `viewed` は、**人が判断するまで先へ進めない**。
  **記入するのは人間の判断であり、転記だけを代行する** — 代筆したときは `recorded_by` に本 skill 名を残す
- 【MUST NOT】**各 skill の内部手順を肩代わりする**（起草・生成・自己確認の実体を本書に写さない）
- 【MUST NOT】**在るファイルに skill を初回として実行する**（改訂モードが要る — 人が通した確認が消える）
- 【MUST NOT】**案件の読み取り専用領域に書く**（→「読み取り範囲・書き込み範囲」）
- 【MUST NOT】**サブエージェントを並列に起動して同じ成果物を書かせる**（同じ担体を競合して書く）
- 【MUST】Markdown・表示文言は ja で記述する

## 案件ルートの解決（MUST）

1. 配布ワークスペース直下の **`project.local.json`** の `project_root` を読む
2. 無ければ**呼び出し時の引数**（`$ARGUMENTS` の 1 つ目）を案件ルートとして受ける
3. それも無ければ、**人に聞いて停止する**（→ 停止 A）。推測で案件ルートを組み立てない
4. `.claude/settings.local.json` の `permissions.additionalDirectories` に**同じパスが在るか**を確かめる。
   無ければ**書き足す設定行を提示して停止する**（無いと案件側の読み書きに毎回許可が要る）
5. 解決した案件ルートと、それが `steering/` `specs/` `.aidd/` を持つことを**宣言する**

以下に出てくる `steering/` `specs/` `.aidd/` `STYLEGUIDE.md` `styleguide.css` `STYLEGUIDE-backlog.md` は
**すべて案件ルート基準**の相対パスである。引数の 2 つ目が在れば**対象 feature** として受ける。

## 前提の確認

- **対象 feature が UI を持つ**こと。**判定するのは開発者**で、本 skill は宣言を受け取るだけである
  （判定の材料: `requirements.md` の業務フローに利用者の画面操作が在るか /
  `design.md` の技術スタックの Frontend 行・System Flows にフロントエンドが現れるか）。
  宣言が無ければ**聞いて停止する**（→ 停止 B）。mockup を省く場合は案件単位で宣言する（黙って省かない）
- 対象 feature の **`design.md` が `status: approved`**・`requirements.md` が承認済み・`steering/` 一式が記入済み
- 満たさないときは**何が欠けているかを挙げて停止する**（→ 停止 B）。欠けたまま skill を実行しない

## 停止点

**【人】の確定点は 5 つ、前提不足で返す停止は 4 つ**。これ以外で止まらない。

| # | 名 | 種別 | 人が見るもの / 確定の記入欄 |
|---|---|---|---|
| **人①** | STYLEGUIDE.md の確定 | 確定 | 案件の既存画面のキャプチャと突合 → `STYLEGUIDE.md` §1-2 改訂履歴の当該版の行を `確定: 済（by / recorded_by）` |
| **人②** | 画面マップの差分確認 | 確定 | SD-0 の確認 6 項目を差分で数え上げ → 画面マップ `features[]` の**行ごと**の `confirmed`（`by` / `at` / `recorded_by`） |
| **人③** | 画面設計書の確認 | 確定 | SD-1 の確認【人】の全項目を数え上げ → 画面設計書 frontmatter の `status: confirmed`（`confirmed.by` / `at` / `recorded_by`） |
| **人④** | mockup の目視 | 確定 | `pages/README.md` の「見るときの観点」に沿ってブラウザで開く → manifest の `viewed`（`by` / `at` / `recorded_by` / `pages[]` / `findings[]` ほか — **キーの正は雛形 `mockup-manifest.json` の `viewed`**） |
| **人⑤** | 画面設計書の鮮度の確認 | 判断 | `design.md` の `updated_at` と画面設計書 `inputs.design_md_updated_at` の差を示す → 改訂するか据え置くかを人が決める |
| **停止 A** | 案件ルートが解決できない | 前提 | `project.local.json` に書く案件ルート / `additionalDirectories` の設定行 |
| **停止 B** | 前提が満たされない | 前提 | UI を持つ feature かの宣言 / `design.md` の `status` / `requirements.md` / `steering/` |
| **停止 C** | 改訂の起点が特定できない | 前提 | 現状（版・`status`・`confirmed`）を報告 → 何を起点に直すかを人が示す |
| **停止 D** | feature を跨ぐ 2 本目 | 分離 | 1 feature 分が終わった旨 → **新しいスレッドで `/aidd-system-design` を呼ぶ** |

**停止のたびに次の 3 つを出す**: ① **何を人が見るか**（対象ファイルと観点）② **確定の記入欄**（担体とキー）
③ **次に `/aidd-system-design` を呼べば続きから進む**こと。あわせて `.aidd/screen-design/README.md` を更新する。

## 進行状態の機械判定（状態ファイルを増やさない — 正は成果物側）

| 成果物 | 状態の担体 |
|---|---|
| スタイルガイド `STYLEGUIDE.md` | **§1-2 改訂履歴の最新行の `確定`** |
| 画面マップ `screen-map.md` | frontmatter `features[]` の**行単位** `confirmed` |
| 画面設計書 `screen-spec.md` | frontmatter `status` |
| mockup `mockup-manifest.json` | **トップレベル** `status` / `checks` / `viewed` |

上から順に見て、最初に当たった行のアクションを取る。

| 状態 | 次のアクション |
|---|---|
| `STYLEGUIDE.md` が無い | **SG を実行**（案件初回のみ）→ 手順 1 |
| `STYLEGUIDE.md` が在り、§1-2 最新行が `確定: 未` | **人①** STYLEGUIDE.md の確定 |
| `STYLEGUIDE.md` が在り、改訂の起点が在る | **SG を改訂モードで実行**（初回として実行しない） |
| `screen-map.md` が無い / design 承認済みで行が無い feature が在る | **SD-0 を実行**（初回 / 増分）→ 手順 3 |
| 該当行の `confirmed` が未記入 | **人②** 画面マップの差分確認 |
| 行が `confirmed`・`screen-spec.md` が無い | **SD-1 を実行**（初回）→ 手順 5 |
| `screen-spec.md` が在り、改訂の起点が在る | **SD-1 を改訂モードで実行**（初回として実行すると `confirmed` が消える） |
| `screen-spec.md` が `status: draft` | **人③** 画面設計書の確認 |
| **`design.md` の `updated_at` が画面設計書の `inputs.design_md_updated_at` より新しい** | **人⑤** 画面設計書の鮮度の確認（据え置くなら次の行へ） |
| `status: confirmed`・manifest が無い / `checks` が pass でない | **MU を実行**（再生成）→ 手順 7 |
| **`STYLEGUIDE.md` の版が上がった** — 検出: `manifest.inputs.styleguide_version` ≠ `STYLEGUIDE.md` の `version` | **全 feature の mockup を再生成**（目視は見た目の変化だけ） |
| **画面マップ §4（入口とシェル）が変わった** — 検出: `manifest.inputs.screen_map_revision` < 画面マップの `revision` **かつ** §6-3 改訂履歴のその revision の行に §4 の改訂が在る | **全 feature の mockup を再生成**（本文の入力は不変 — 目視はシェルだけ） |
| **無効表示のリンク先が生成された** — 検出: `cross_feature_links[].status = pending` の相手 feature に `pages/` が出来た | **その項目を無効表示で持つ全 feature の mockup を再生成**（ナビ項目の増減が無いので上の行に該当しない。目視はシェルだけ） |
| 検査 pass・`viewed` 未記入 | **人④** mockup の目視 |
| 上のどれにも当たらない | **完了確認**（→ 手順 10） |

## 実行手順

**次の 1 手を同じスレッドで実行し、停止点で止まる。** 判定で当たった行から入る（毎回 1 から回さない）。

- [ ] 1. **案件初回のみ** `styleguide-authoring` の SKILL.md（配布ワークスペースの
      `.claude/skills/styleguide-authoring/SKILL.md`）を読み、その手順に従う。出力は案件ルート直下の
      `STYLEGUIDE.md` / `styleguide.css` / `STYLEGUIDE-backlog.md`。**既存 UI から読み取れない項目・
      ヒアリングで決まらない項目は skill が決めず、選択肢と影響差と推奨案を添えて停止する**
- [ ] 2. **人①** STYLEGUIDE.md の確定を待って停止する。デザイン担当の確認は任意・非ブロッキング。
      **確定なしに先へ進めない**
- [ ] 3. `screen-map-authoring` の SKILL.md を読み、その手順に従う（初回 = その時点で design 承認を
      通過している UI feature をまとめて切り出す / 以後 = 通過した feature の行を**増分で足す**。作り直さない）
- [ ] 4. **人②** 画面マップの差分確認を待って停止する。初回は全行、以後は足した・直した行だけ。
      **入口を新設した場合は、擬似 feature `_app-shell` に対しても手順 5 を回す**
- [ ] 5. **feature ごとに** `screen-spec-authoring` の SKILL.md を読み、その手順に従う
      （**自 feature の行が `confirmed` になってから**。**他 feature の `requirements.md` / `design.md` を入力にしない**）。
      **再入時は先に鮮度を見る** — `design.md` の `updated_at` が `inputs.design_md_updated_at` より新しければ
      起草せず **人⑤ 画面設計書の鮮度の確認**で停止する。**2 feature 目は停止 D**（新しいスレッドで呼ぶ）
- [ ] 6. **人③** 画面設計書の確認を待って停止する。**画面設計書 §5-5 の改訂依頼のうち区分「改訂を要する」が
      残っているうちは先へ進まない**（画面マップの改訂 → 差分確認 → 影響 feature の画面設計書の修正、の順に戻る。
      区分「上流が既に扱うと記録済み」はブロックしない）
- [ ] 7. **feature ごとに** `mockup-authoring` の SKILL.md を読み、その手順に従う（完了条件は skill 側 —
      **機械検査 2 本 exit 0**・画面 × 状態と manifest の `pages[]` が 1:1・`missing[]` の申告）。
      **2 feature 目は停止 D**
- [ ] 8. **人④** mockup の目視を待って停止する。**機械での見た目確認は工程に持ち込まない**
- [ ] 9. **再生成の契機に当たったら、既存 feature の mockup も再生成する**（判定表の下 3 行。
      本文の入力は不変なので目視の範囲は契機ごとに違う）。再生成のたびに手順 8 へ戻る
- [ ] 10. **完了確認**（→「完了確認」）

**確定後に文書を直す場合**（目視の指摘・`design.md` の変更管理・画面マップの改訂）:
**`styleguide-authoring` と `screen-spec-authoring` を改訂モードで実行する**（初回として実行しない）。
**在るファイルに初回として実行すると、人が通した確認（`STYLEGUIDE.md` の確定 / `status: confirmed`）が消える。**
改訂の起点が特定できなければ、**現状を報告して停止する**（→ 停止 C）。

## 読み取り範囲・書き込み範囲

**読む**（読み取り専用）: `steering/` / `specs/<feature>/requirements.md` / `specs/<feature>/design.md` /
案件ルート直下の `STYLEGUIDE.md` `styleguide.css` `STYLEGUIDE-backlog.md` / `.aidd/screen-design/` /
（在れば）`.aidd/wireframe/` の **`wireframe-manifest.json` だけ**（HTML・CSS・`tokens/` は読まない。
読むのは SD-0 / SD-1 で、**種と突合先**に使う — 根拠にしない。SG / MU は manifest も読まない）。
skill ごとに読んでよい範囲の詳細は**各 SKILL.md の「入力」節が正**。

- **`screen-spec-authoring` に他 feature の `requirements.md` / `design.md` を渡さない**
  （他 feature の情報は画面マップ経由でだけ入る）
- **`mockup-authoring` に `requirements.md` / `design.md` を渡さない**（画面と状態は画面設計書で、繋ぎは画面マップで確定済み）
- 上流のワークフロー内部資料（FAQ・質問ログ・ゲートレポート・checkpoint 等）を画面内容の根拠として渡さない

**書く**（これだけ）:

```
<案件ルート>/
├── STYLEGUIDE.md / styleguide.css / STYLEGUIDE-backlog.md   … SG が書く
└── .aidd/screen-design/                                     … 本工程の成果物
    ├── README.md                                            … 本 skill が書く
    ├── _app-shell/ … <feature>/ …                           … SD-0 / SD-1 / MU が書く
    └── _tools/                                              … 生成の手段の既定の置き場
```

- 【MUST NOT】**`.aidd/gates/` / `.aidd/phase-progress.json` / `.aidd/wireframe/` / `specs/` / `steering/` /
  `Templates/` に書く。** 配布ワークスペースの `.claude/settings.json` が deny で担保するが、
  **機械担保が効かない環境でも規約で守る**
- 本工程の成果物は**上流のゲート実行とは別のコミット**にする（上流は「実行前後の git 差分で本文改変を目視確認する」
  運用を前提にしており、混ざると差分のノイズになる）

## `.aidd/screen-design/README.md` の生成

**初回に作り、停止のたびに更新する**（案件側で実装に引き継ぐときの入口になる）。中身は次の 4 つ:

1. **成果物の所在** — 上の木（`_app-shell/` と feature ごとのディレクトリ・`pages/` の入口ページ）
2. **状態** — 各担体の**値を表で**:

   | 成果物 | 担体 | 値 |
   |---|---|---|
   | `STYLEGUIDE.md` | §1-2 最新行の `確定` | 済 / 未（版・日付・`by` / `recorded_by`） |
   | 画面マップ | `features[]` 行ごとの `confirmed` | feature ごとに 済 / 未 |
   | 画面設計書 | frontmatter `status` | feature ごとに draft / confirmed |
   | mockup | `status` / `checks` / `viewed` | feature ごとにページ数・pass / fail・目視の有無 |

3. **`tasks.md` からの参照の仕方** — UI タスクの参照先は**画面設計書と mockup**（`.aidd/screen-design/<feature>/screen-spec.md`
   の画面 ID・`pages/<画面 ID>-<状態>.html`）。`STYLEGUIDE.md` / `styleguide.css` は実装時の見た目の正
4. **再生成の契機** — 判定表の下 3 行と、画面設計書の改訂・機械検査 fail の修正

## 完了確認

対象 feature について次を数え上げて報告する。

- 全対象 feature の画面設計書が `status: confirmed`
- manifest の `checks` がパレット・動線ともに pass / `viewed` 記入済み
- **`missing[]` と、未生成 feature への pending の一覧**（それぞれ件数と行き先）
- **`STYLEGUIDE-backlog.md` の未処理件数**
- 画面マップの未確定行が 0 件であること
- `.aidd/screen-design/README.md` が最新の状態を映していること

## ガードレール

- **やらない**: 画面の切り出し・所有（SD-0）/ 画面の項目・操作・状態・文言（SD-1）/ 見た目（SG）/
  mockup の描画（MU）を本書で決めること。**判断は各 skill が持つ**
- **やらない**: 指摘がゼロになるまで自動で回すこと。自動修正・自動ループを行わない
- **やらない**: 人の確定を先取りして次の手に進むこと。**確定の担体が空なら止まる**
- **やらない**: 停止点を勝手に増やす / 減らすこと
- **やらない**: 案件ルートを推測で組み立てること（宣言が無ければ聞いて停止する）
- **迷ったら**: 現状（4 つの担体の値）と、次の 1 手の候補を挙げて**人に返す**
