> **原本とワークスペースの対応**
>
> このワークスペースの Skill の原本は genpon の `layers/` にあります。本文の手順は **ワークスペース側のパス**（`.claude/…`）で書かれています。
>
> | 原本（genpon） | ワークスペース `releases/alpha3.2/ds_mock/` |
> | --- | --- |
> | `layers/l3_generation_quality/workflow/orchestrator/phase/aidd-system-design/` | `.claude/skills/aidd-system-design/` |
> | `layers/l3_generation_quality/workflow/process/{styleguide,screen-map,screen-spec,mockup}-authoring/` | `.claude/skills/{styleguide,screen-map,screen-spec,mockup}-authoring/` |
> | （このワークスペースにだけある） | `.claude/hooks/`・`.claude/settings.json`・`.gitignore`・`project.example.json`・`HOW-TO-USE.md`・`README.md` |

# 画面設計工程（簡素版）— 配布ワークスペース

design 承認の後・`tasks.md` 着手の前に、**UI を持つ feature の画面設計（スタイルガイド → 画面マップ →
画面設計書 → mockup）を回すための skill 一式**です。AIDD ワークフローに載せない独立の側流で、その生成物
（`steering/` / `requirements.md` / `design.md`）を**読み取り専用の入力**にします。成果物は案件側に出るので、
このワークスペース自体は案件の状態を持ちません（複数案件を 1 つのワークスペースで回せます）。

## 前提

- **Claude Code** または **Cursor**（本ワークスペースを開いて使う。Cursor は `.claude/skills/` を互換読み込みするため、
  skill 一覧・呼び出しは追加改修なしで使える。ただし下記「初回セットアップ」手順 3〜5 の書き込み範囲の機械担保
  〔`.claude/settings.json` の deny・PreToolUse hook・`additionalDirectories`〕は Claude Code 専用形式で、
  Cursor 側には効かない）
- **Node.js**（mockup の機械検査 2 本に要る）
- **AIDD ワークフローの案件**で、対象 feature の `design.md` が `status: approved`・`requirements.md` が
  承認済み・`steering/` 一式が記入済み
- 案件は **git 管理**されていること（成果物を別コミットにするため）
- （任意）**wireframe 工程**を実施した案件は、`.aidd/wireframe/<feature>/pages/wireframe-manifest.json` を
  SD-0 / SD-1 が**種と突合先**に使う（根拠にしない。**HTML・CSS は読まない**。無くても成立する）

用語: **案件ルート** = **AIDD のワークスペースのパス**（`steering/` `specs/` `.aidd/` を持つ、AIDD ワークフローの
出力ルートのディレクトリ）。**配布ワークスペース** = 本ディレクトリ。

## 初回セットアップ

**手順 2〜5 は、いずれも自分でコマンドを打つ必要はありません。開いている Claude Code / Cursor 自身に
文章でそのまま頼んでください。**「作って」と「追記して」を区別しているのは、**手順 3 でファイルを新規作成し、
手順 4・5 はその同じ 1 つのファイルに内容を足していく**（別ファイルを作るわけではない）ことを示すためです。

1. 本ワークスペース（`releases/alpha3.2/ds_mock/`）をフォルダごと作業場所へコピーし、**Claude Code または Cursor で開く**
2. 案件ルートの絶対パス（`/` 区切り。例 `C:/Work/my-project`）を用意し、次のように**頼む**:

   > `project.example.json` を `project.local.json` としてコピーし、`project_root` を
   > `C:/Work/my-project` に書き換えて

   `project.example.json` は雛形として git 管理されたまま残ります。**新しく作る `project.local.json` だけが
   実物**で、`.gitignore` によって git 管理外です（案件の絶対パスは開発者・案件ごとに違うため、コミットしない）。
   本ワークスペースを新しい版に差し替えるときも、雛形は差し替え後の `project.example.json` からもう一度
   同じ名前でコピーし直してください（`project.local.json` は差し替えで消えるので、書いていた値を写します）
3. **`.claude/settings.local.json`**（配布ワークスペース直下・git 管理外。**Claude Code 専用の設定 — Cursor では
   この手順は不要**）を**新規作成**するよう、次のように**頼む**（`手順 2` と同じ絶対パスを使う）:

   > `.claude/settings.local.json` を新しく作って、次の内容にして:
   > `{ "permissions": { "additionalDirectories": ["C:/Work/my-project"] } }`

   `project_root`（手順 2）と `additionalDirectories`（本手順）は**役割が別**です。`project_root` は本工程の
   skill が「案件ルートをどこと見るか」を判断するための設定、`additionalDirectories` は **Claude Code 自身の
   権限設定**で「配布ワークスペースの外にあるこのディレクトリに触ってよい」と Claude Code に伝えるものです。
   同じ絶対パスを**両方**に書く必要があり、`additionalDirectories` が無いと案件側のファイルを読み書きするたびに
   毎回許可を確認されます。

4. **書き込み禁止の初回確認（1 度だけ）**。「案件ルートの `specs/` 配下のファイルに 1 行足して」と頼み、
   **拒否される**ことを確かめます。書き込み禁止は `.claude/settings.json` の **`deny`** と **PreToolUse hook**
   （`.claude/hooks/block-protected-dirs.mjs`）の二重です。環境によって現れ方が 2 通りあり、**どちらも正常**です:
   - `deny` が先に発火し、確認プロンプトなしで拒否される
   - `deny` が発火せず一度 ask（確認プロンプト）になった後、承認すると hook が
     `ブロック: … は保護領域（specs/ …）への書き込みを禁じられている` という exit code 2 のメッセージで拒否する

   **拒否メッセージが一度も出ない**（ask のまま普通に書き込めてしまう）場合だけ異常です。その場合は次のように
   **頼んで**、**手順 3 で作った同じファイルに** `deny` の絶対パス形を**追記**してもらいます（新しいファイルは
   作りません）:

   > `.claude/settings.json` の `_comment_pattern_form_2` に書かれている絶対パス形の `deny` を、
   > `.claude/settings.local.json` の `permissions.deny` に追記して（`additionalDirectories` は残したまま）

   あわせて、`.claude/hooks/block-protected-dirs.mjs` が `.claude/settings.json` の `hooks.PreToolUse` に
   配線されているか（本ワークスペースを改変していないか）を確認してください。

   この確認が調べているのは**案件の違いではなく環境の違い**です（hook は案件ルートの絶対パスに依存しないため、
   案件を切り替えても再確認は不要）。再確認が要るのは、① `deny` が発火せず絶対パス形に切り替えた場合
   （案件を切り替えるたびにパスを書き直すので、そのたびに確かめ直す）と、② Claude Code を更新した・
   別マシンで開いた場合（環境が変わったとき）の 2 つだけです。`deny` が additionalDirectories 配下で発火しない
   環境が実際にあることが分かっている（申し送り 2026-09-16）ため、**この手順で最終的に確かめるべきは
   deny ではなく hook のブロックメッセージが出ること**です。
5. **（任意）配布物自身を凍結する**。本ワークスペースで**案件を回すだけ**（skill を直さない）なら、次のように
   **頼んで**、**手順 3 で作った同じファイルに** 4 行を**追記**してもらうと、案件を回している最中に skill が
   書き換わることを防げます（先頭の `/` は本ワークスペース直下に解決されるので、案件側には掛かりません）:

   > `.claude/settings.local.json` の `permissions.deny` に次の 4 行を追記して（`additionalDirectories` は
   > 残したまま）:
   > `"Edit(/.claude/skills/**)"` / `"Write(/.claude/skills/**)"` /
   > `"MultiEdit(/.claude/skills/**)"` / `"NotebookEdit(/.claude/skills/**)"`

## 使い方 A — 一連（`/aidd-system-design`）

1. `/aidd-system-design` を呼ぶ（引数で案件ルートと feature を渡してもよい）
2. 成果物側の担体だけから**進行状態が判定**され、**次の 1 手**（4 skill のどれか）がそのまま実行される
3. **人が確定する点で停止**する（何を見るか・どこに記入するかが提示される）
4. 人が確定を記入する（スタイルガイドの確定 / 画面マップ行の `confirmed` / 画面設計書の `status: confirmed` /
   mockup の `viewed`）
5. **もう一度 `/aidd-system-design` を呼ぶ**と続きから進む
6. **2 feature 目の画面設計書・mockup は新しいスレッドで**呼ぶ（文脈を分けるため。入口 skill が案内します）

## 使い方 B — 単独（4 skill を直接呼ぶ）

| skill | 何を作るか | 単独で呼ぶときの前提 |
|---|---|---|
| `/styleguide-authoring` | `STYLEGUIDE.md` / `styleguide.css` / `STYLEGUIDE-backlog.md`（案件に 1 回） | 初回: `STYLEGUIDE.md` が無い / 改訂: 在って改訂の起点が示されている / ルート C: プリセットが在る |
| `/screen-map-authoring` | 画面マップ `screen-map.md`（案件に 1 つ・以後は増分） | 対象 feature の `design.md` が `status: approved`。`STYLEGUIDE.md` の最新版が確定済み |
| `/screen-spec-authoring` | 画面設計書 `screen-spec.md`（feature ごと） | 画面マップの自 feature 行が `confirmed`。`STYLEGUIDE.md` の最新版が確定済み |
| `/mockup-authoring` | mockup（`pages/*.html` + `mockup-manifest.json`。feature ごと） | 画面設計書が `status: confirmed`・§5-5 の改訂依頼に区分「改訂を要する」が 0 件・画面マップ行が `confirmed`・シェルを含む revision が確定済み・Node.js |

前提を満たさないときは、各 skill は**生成せず停止**します。詳しい前提は各 `SKILL.md` の
「単独起動時の前提」節が正です。

## 案件側に何ができるか

```
<案件ルート>/
├── STYLEGUIDE.md / styleguide.css / STYLEGUIDE-backlog.md   … 見た目の正 3 点（ルート直下）
├── steering/  specs/<feature>/…                             … 読み取り専用（本工程は書かない）
└── .aidd/screen-design/                                      … 本工程の成果物
    ├── README.md                    … 成果物の所在・状態・tasks.md からの参照の仕方・再生成の契機
    ├── _app-shell/                  … 画面マップ screen-map.md ＋ 入口・シェルの画面設計書と mockup
    ├── <feature>/                   … screen-spec.md / pages/ / presented/
    └── _tools/                      … mockup 生成の手段の既定の置き場
```

## 書かないもの

`specs/` / `steering/` / `.aidd/gates/` / `.aidd/phase-progress.json` / `.aidd/wireframe/` / `Templates/`。
`.claude/settings.json` の **deny と PreToolUse hook**（`.claude/hooks/block-protected-dirs.mjs`）の二重で
機械的に塞いでいますが、**規約としても各 skill が守ります**。`deny` が `additionalDirectories` 配下で発火しない
環境が実在するため（申し送り 2026-09-16）、hook が実際の歯止めです。
案件の `Templates/` には本工程の雛形を複製しません（雛形は各 skill の `templates/` に同梱してあります）。

## 成果物は別コミットにする

上流のゲートは「実行前後の git 差分で本文改変を目視確認する」運用を前提にしています。本工程の生成物が
その差分に混ざると確認のノイズになるので、**本工程の成果物は上流のゲート実行とは別のコミット**にしてください。

## プリセット（同系システムの案件）

`.claude/skills/styleguide-authoring/presets/<名前>/` に、`STYLEGUIDE.md` / `styleguide.css` /
`STYLEGUIDE-backlog.md` の 3 点を組にしたプリセットを同梱しています（WiNG 版 = `presets/wing/`）。
同系システムの案件では `styleguide-authoring` の**ルート C「プリセットの取り込み」**で 3 点を案件ルート直下に
複製し、`product` を案件名に直して取り込みます。**確定は人**が行い、確定なしに画面マップへ進めません。
既存 UI からの抽出はルート A、既存 UI が無い新規案件はルート B です。

## 複数案件の切り替え

`project.local.json` の `project_root` と `.claude/settings.local.json` の `additionalDirectories` を
**同時に**書き換えます。案件ごとに**別のスレッド**で作業してください（成果物は案件側にあるので、
切り替えても進行状態は失われません）。1 回だけ別案件を触るなら `/aidd-system-design <案件ルート> <feature>` と
引数で渡すこともできます（`project.local.json` より引数が優先されます）。

## 更新のしかた

本ワークスペースを**新しい配布物で差し替える**だけです（案件側には何も置いていないため）。
`project.local.json` と `.claude/settings.local.json` は git 管理外なので、差し替え後に作り直してください。
**skill・雛形・プリセットをこの場で直さないでください** — 差し替えで消えるうえ、下の改訂の起点 ④ は
根拠の所在を**配布元の改訂記録**としているためです。直す必要があるときは配布元に返してください
（機械的に防ぎたい場合は「初回セットアップ」の手順 5）。
**配布物の版が上がったら、それは `STYLEGUIDE.md` の改訂の起点 ④ です。** 改訂の起点は 4 つ
（① mockup の目視・顧客提示で出た見た目の指摘 / ② 画面設計書からの部品の語彙の不足 / ③ 実装からの申告 /
**④ 本 skill の規約が改訂された＝配布物の版が上がり、雛形・生成規約が変わった**）で、これ以上は増やしません。
差し替えただけでは案件の成果物は変わりません。**④ のときは `styleguide-authoring` を改訂モードで呼び、
直す節を規約の差分から導いて版を上げます**（案件側の申告はありません）。

**入口 skill の改名（`screen-design` → `aidd-system-design`）。** 旧名 `/screen-design` で使っていた場合は、
`.claude/skills/` を差し替えたうえで旧フォルダ `.claude/skills/screen-design/` を削除してください（残すと旧名も候補に出ます）。
変わったのは名前だけで、雛形・生成規約は変わっていないため改訂の起点 ④ には当たりません。
案件側の成果物ディレクトリ `.aidd/screen-design/` は改名していないので、旧名で作った成果物はそのまま続きから使えます。

## 代替の起動形

- **(B) 案件を開いて `--add-dir <配布ワークスペース>`** — skill は読まれますが、雛形と検査スクリプトの所在を
  毎回渡す必要があります
- **(C) plugin として配る** — `--plugin-dir` で読み、所在は `${CLAUDE_PLUGIN_ROOT}` で解けます（将来の包装形）

## 構成

| パス | 中身 |
|---|---|
| `README.md` | 本ファイル（実務手順の正） |
| `HOW-TO-USE.md` | 使い方ガイド（人間向け）— 全体の流れと SKILL の要点 / STYLEGUIDE.md の 3 ルートの選び方 / feature ごとのスレッド分割 / コマンド / ディレクトリ構成 / 人間判断のコツ / **tasks.md 工程（AIDD フロー）との接続点**（工程を検討する人向け） / 注意事項 |
| `project.example.json` | 案件ルートの宣言の雛形（実物は `project.local.json`） |
| `.gitignore` | `project.local.json` / `.claude/settings.local.json` |
| `.claude/settings.json` | 書き込み禁止の deny ルールと PreToolUse hook の配線 |
| `.claude/hooks/block-protected-dirs.mjs` | deny のバックストップ（`additionalDirectories` 配下で deny が発火しない環境向け） |
| `.claude/skills/aidd-system-design/` | 入口 skill（一連） |
| `.claude/skills/styleguide-authoring/` | SG。`templates/STYLEGUIDE.md` / `presets/<名前>/` |
| `.claude/skills/screen-map-authoring/` | SD-0。`templates/screen-map.md` |
| `.claude/skills/screen-spec-authoring/` | SD-1。`templates/screen-spec.md` |
| `.claude/skills/mockup-authoring/` | MU。`templates/mockup-manifest.json` / `scripts/check-palette.mjs` / `scripts/check-links.mjs` |
