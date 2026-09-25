# ブランド原則 — travel-expense-demo 案件オーバーライド【参考実装例】

> 位置づけ: `brand-principles.md`（ベースDS・無ブランド既定値）に対する travel-expense-demo
> 案件固有の上書き分のみを記録する。禁止リスト・文言トーン・レイアウト原則はベース側が汎用的な
> 内容のため、この案件も `brand-principles.md` をそのまま使う（重複記載しない）。
> 対応する tokens 側の差分は `examples/travel-expense-demo/semantic.travel-expense-demo.json`
> （ビルドは `npm run build:tokens:example:travel-expense-demo`）。
>
> **本ファイルは `examples/` 配下の参考実装例**。実案件では `brand-principles.<project>.md`
> としてリポジトリ直下に置く（`examples/travel-expense-demo/README.md` 参照）。

## 経緯

- **2026-08-18**: ブランドカラー #00a1ae を先行適用。`color.semantic.primary` はこのブランドカラーを
  白文字コントラスト基準（4.5:1）を満たすよう暗めに調整した値（`#00818b`）へ上書き。#00a1ae そのものは
  `color.semantic.brand` として登録し、文字を伴わない大面積・装飾用途（ヘッダー背景・ロゴ周り等）に
  限定して使う
- **2026-08-24**: ブランドヒアリング工程が定義された（DS-GUIDE.md §2-4 — フェーズ 0 の工程 0 / 2A で
  1 回実施。実施タイミングはモック A/B テストの B アーム生成前）。上記 #00a1ae の採用はヒアリング前の
  先行適用であり、**ヒアリング（質問 1: 色見 / 質問 2: ブランド資産）の回答で確定または置き換えられる
  までの暫定値**として扱う
- **2026-08-26**: この #00a1ae は travel-expense-demo 案件固有の値と判明したため、共有のベースDS
  （`brand-principles.md` / `tokens/semantic.json`）から本ファイル・
  `semantic.travel-expense-demo.json` へ切り出した（値そのものは変更なし）。
  他プロジェクトの既定には影響しない
- **2026-08-26（同日）**: 一式を `examples/travel-expense-demo/` へ移し、**参考実装例**と
  位置づけた（ベースDS 本体と案件サンプルを取り違えないようにするため）

## ブランド資産（この案件の回答）

- コーポレートカラー: #00a1ae を先行適用（**ヒアリングで確定するまで暫定**）。適用先は
  `color.semantic.primary`（コントラスト調整版 `#00818b`）と `color.semantic.brand`（原色。
  大面積・装飾用途限定）
- ロゴ: 未適用（ヒアリング質問 2 で有無・利用条件を確認）
- 既存ブランドガイド: 未確認（同上）
