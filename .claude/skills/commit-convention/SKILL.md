---
name: commit-convention
description: git のコミットメッセージを書く／レビューするとき、または「コミット規約」をプロジェクト標準として記入するときに使う。Conventional Commits v1.0.0 に基づく記述形式（ヘッダ形式・type 語彙・破壊的変更表示・body/footer 構造）の規約に限定する。コミット内容と diff の意味的整合（type が変更実体に合っているか）は対象外。
metadata:
  l2-compiled-from: "KA-REF-002@0.2.0, CT-REF-003@0.1.0"
  l2-compiled-at: "2026-09-14"
---

> 本ファイルはビルド成果物（SSOT は `assets/`）。**手編集禁止** — 直すときは資産カードを直して再コンパイルする。
> 構成資産のContract・レビュー状態・検証経路は同梱の `PROVENANCE.md` を参照する。
> 末尾の validation は**成果物の自己チェック専用**であり、消費先のドキュメント状態（`status` 等）に影響しない。
> **判定ハーネス（verifier）と Contract 本体は同梱されない。**

# commit-convention — コミットメッセージの記述規約

## 使い方

コミットメッセージを書く直前、レビューする時、またはプロジェクトの「コミット規約」欄を記入する時に、下記ルールで照合する。
指摘は対象箇所を引用し、どのルールに反するかを名指しして、修正形を1行添える。

## ルール

- **R-01 ヘッダ形式**: ヘッダを `<type>[(scope)]: <description>` で書く。type（名詞）は必須、scope は任意、
  破壊的変更の `!` は任意。その後に**コロン＋半角スペースを必ず置き**、続けて非空の description を書く。
- **R-02 type 語彙**: type は小文字の規約語彙から選ぶ。`feat`（新機能＝MINOR）と `fix`（バグ修正＝PATCH）が中核で、
  `docs` / `style` / `refactor` / `perf` / `test` / `build` / `ci` / `chore` / `revert` を慣例的に許可する。
  大文字（`Update:`）・非規約語（`misc:`・`WIP`）を使わない。
- **R-03 命令法・現在形**: description は命令法・現在形で簡潔に書く（`add` であって `added` / `adds` ではない）。
- **R-04 破壊的変更の明示**: 破壊的変更は type/scope 直後の `!`、または footer の**大文字** `BREAKING CHANGE:` で示す。
  両者は同義。footer 形式を使う場合は**大文字必須**（小文字は誤形式）。
- **R-05 body の分離**: body を書く場合は、ヘッダとの間に**空行を1行**置く。body には変更の背景・理由（なぜ）を書く。
- **R-06 scope**: scope は任意。付ける場合はコードベースの区画を表す**名詞を括弧内**に置く（例 `fix(parser):`）。
- **R-07 footer**: footer を書く場合は body の後に空行を1行置く。トークンは空白を `-` に置換する（`Acked-by` 等）。
  issue 参照は `Closes` / `Fixes` / `Refs` ＋ `#<番号>` の形式で書く。

## 決定的検査（judge を呼ぶ前に機械で落とす）

R-01 / R-02 / R-04 / R-06 / R-07 は regex と集合メンバーシップで機械判定できる。先に機械検査を通す。

```
^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9\-]+\))?(!)?: .+
```

R-03（命令法）と R-05（body が「なぜ」を語るか）は意味判断であり、機械検査の対象にしない。

## プロジェクトで決める項目（本パックは既定値を持たない）

次の2点は上流ソース間で不一致があり、**本パックは値を固定しない**。プロジェクト側で確定して記録すること。

- **subject の長さ上限** — 上流で 50字 / 72字 の2説がある。どちらを採るかはプロジェクトの判断。
- **type 許可集合** — 既定は上記 R-02 の11種。部分集合しか許さない運用に**締める**のは可（緩める方向は要判断）。

## validation（CT-REF-003 の INV/DEV チェックリスト）

成果物の自己チェックに使う。**本判定は消費先のドキュメント状態に影響しない。判定ハーネスは同梱されない。**

- [ ] **INV-01** ヘッダが `<type>[(scope)]: <description>` 形式（コロン＋半角スペース、非空 description）
- [ ] **INV-02** type が規約語彙の小文字トークン
- [ ] **INV-03** description が命令法・現在形
- [ ] **INV-04** 破壊的変更がある場合、`!` または大文字 `BREAKING CHANGE:` で明示（無ければ自動充足）
- [ ] **INV-05** body を含む場合、ヘッダとの間に空行1行があり、変更の理由を述べている
- [ ] **INV-06** scope を付す場合、名詞を括弧内に置いている
- [ ] **INV-07** footer を含む場合、body の後に空行1行を置き、トークンが `-` 区切り形式

**DEV（該当すれば Critical Fail）**:

- **DEV-01** ヘッダが `type: description` の基本形式を満たさない（type 接頭辞なし／コロン＋スペースなし＝素の一文）
- **DEV-02** type が規約語彙に無い、または大文字・非規約語（`Update:` / `misc:` / `WIP`）
- **DEV-03** 破壊的変更があるのに `!`／大文字 `BREAKING CHANGE:` で示されていない、または小文字など誤形式

採点は各 INV を 0 / 5 / 10。DEV が1件でも該当すれば Critical Fail（当該 INV を 0 とし不合格）。
Critical Fail が無い場合、全 INV の平均 7.0 以上で PASS。詳細な採点規則は Contract 本体（同梱されない）を参照。

## 適用範囲外

- コミットメッセージ以外（PR 説明文・issue 本文・任意のログ）
- merge コミット、vendor / 生成物の自動コミットなど規約適用外と明示された種類
- コミット内容と diff の意味的整合（type の妥当性判断）— 本パックは**記述形式の適合のみ**を見る
- Conventional Commits を採用していないリポジトリ

---

provenance: KA-REF-002@0.2.0 / CT-REF-003@0.1.0 ｜ 元 OSS ライセンス: CC0（awesome-cursorrules） / MIT（awesome-cursor-rules-mdc） / MIT（conventionalcommits.org） ｜ compiled_at: 2026-09-14
