# travel-expense-demo — 案件テーマの参考実装例

> **これはサンプルです。** ベースDS の一部ではなく、新規案件のひな形でもありません。
> 「案件固有のブランド色をベースDS に重ねる」しくみが実際にどう書かれるかを
> 1 件だけ実物で残したものです。**この案件のためにこのDSを使う人以外は、
> 中身の値をコピーしないでください**（色はこの案件固有です）。

## しくみ（ここで示していること）

ベースDS は無ブランドの既定値を持ち、案件はその **差分だけ** を上書きします。
トークンは 3 段に積まれます。

```
tokens/primitive.json                     ← 共有スウォッチ（全案件共通）
tokens/semantic.json                      ← ベースDS の既定値（無ブランド）
examples/travel-expense-demo/semantic.travel-expense-demo.json   ← 案件の差分だけ
```

上書きするのは `color.semantic.primary` 系の数キーのみで、primitive 層と部品仕様は
共有のまま触りません（設計判断 14 — DS パッケージは分割しない）。

## ファイル

| ファイル | 役割 |
|---|---|
| `semantic.travel-expense-demo.json` | ブランド色の差分（上書きするキーだけを書く） |
| `config.travel-expense-demo.mjs` | Style Dictionary の設定。上記 3 ファイルを順に重ねる |
| `brand-principles.travel-expense-demo.md` | 案件固有の「らしさ」。ベースの `brand-principles.md` に対する差分のみ |

ビルド:

```bash
npm run build:tokens:example:travel-expense-demo
```

## 実案件で作るときの置き場所【重要】

**この例は `examples/` 配下にありますが、実案件のファイルはここに置きません。**
規約どおりの場所に置いてください（AGENTS.md / `tokens/HARVESTING.md`）。

| 種類 | この例の場所（サンプル） | 実案件での場所（正しい規約） |
|---|---|---|
| トークン差分 | `examples/travel-expense-demo/semantic.travel-expense-demo.json` | `tokens/semantic.<project>.json` |
| ビルド設定 | `examples/travel-expense-demo/config.travel-expense-demo.mjs` | `tokens/config.<project>.mjs` |
| ブランド原則 | `examples/travel-expense-demo/brand-principles.travel-expense-demo.md` | `brand-principles.<project>.md`（リポジトリ直下） |

`config.<project>.mjs` の `source` / `buildPath` は**実行時のカレントディレクトリ
（リポジトリルート）からの相対パス**です。ファイル自身の位置からの相対ではないため、
置き場所を変えたら `source` の記述も合わせて直してください。

## 値について

色値は**すべて暫定**です。ブランドヒアリング（DS-GUIDE.md §2-4）の回答で確定または
置き換えられるまでの先行適用であり、第二段でデジタル庁のプリミティブへ移植する前提で
登録されています。経緯は `brand-principles.travel-expense-demo.md` の「経緯」を参照。
