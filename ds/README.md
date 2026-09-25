# aidd-ds-poc-digital-go-jp-based

AI 駆動開発検証用のデザインシステム（**検証用リポジトリ**）。
デジタル庁デザインシステム（DADS）を土台に、部品・パターンの使い方ルールを
自社スキーマ（component-spec.json / pattern.json / index.json）へ移植したもの。

- 名称の由来: poc = 検証 / digital-go-jp = デジタル庁 DS の GitHub org 名 /
  based = 派生・非公式。検証を終えて本採用する際にリネームを判断する
- バージョン規約: **v0.0.x = 仕様データのみ** / v0.1〜 = 実装入り
- 中身の解説: [GUIDE-for-designers.md](GUIDE-for-designers.md)（デザイナー向け）/
  [AGENTS.md](AGENTS.md)（エージェント向けハード制約・参照順序）
- 設計判断の記録・土台 DS の参照バージョン・トークン対応表: [DECISIONS.md](DECISIONS.md)

## NOTICE — 出典とライセンス

本リポジトリの部品仕様・パターンは、**デジタル庁デザインシステムβ版**
（https://design.digital.go.jp/dads/）の公開ガイドラインを加工して作成したものです。
トークン設計は [digital-go-jp/design-tokens](https://github.com/digital-go-jp/design-tokens)
（**MIT License**）を参照しています。

- 出典: デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/
  のコンテンツを加工して作成
- デジタル庁の利用条件: https://design.digital.go.jp/introduction/notices/
- トークン: https://github.com/digital-go-jp/design-tokens（MIT License）
- 参照バージョン: **design-tokens v2.0.1**（2026-05-28 リリース）/
  公式サイト参照日 **2026-08-18**
- デジタル庁の Figma データ・イラスト・アイコン素材は別条件のため **使用していません**
- 本リポジトリは**デジタル庁の公式成果物ではありません**（非公式の派生）

### 案件で使うときに引き継ぐ表示【必須】

本DSはデジタル庁デザインシステム（DADS）を翻案しているため、DADS の利用条件が求める
出典表示と加工の明示は、**本DSを使って生成した成果物にも引き継ぐ**必要があります。
成果物を顧客へ納品する際は、以下を成果物側（README / NOTICE / アバウト画面など）に
記載してください。

> 出典：デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/
> のコンテンツを加工して作成。本成果物はデジタル庁の公式成果物ではありません。

Material Symbols の SVG 実体を成果物に同梱する場合は、Apache License 2.0 の全文と
NOTICE を成果物に含めてください（詳細は [icons/ICON-MAP.md](icons/ICON-MAP.md) §1）。
SVG を含めず、アイコン名の参照のみであれば不要です。

なお DADS が示すアクセシビリティ適合（WCAG 達成基準への適合性等）は**改変前の状態に
限られます**。本DSは改変済みのため、本DSを使うことで適合が自動的に満たされるわけでは
ありません。顧客への適合表明は案件側で検証のうえ行ってください。

### やってはいけないこと

- デジタル庁の公式成果物であるかのような表示・示唆
- 本DS単体を製品・サービスとして販売・ライセンス供与すること

> 現時点ではチーム内利用を前提とし、独立した `LICENSE` は置いていません。
> 全社・組織横断へ展開する際に、利用範囲と社外提供の可否を含めて LICENSE 化します。
