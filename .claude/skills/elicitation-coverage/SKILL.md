---
name: elicitation-coverage
description: 要件定義前段（現状調査〜外部設計）で、議事録や要件ドラフトから未決事項を洗い出すとき使う。社内標準の成果物定義38件とヒアリング観点177問を全件走査し、covered/uncovered/not_applicable の3値と根拠・問い・処理経路（顧客確認／資料依頼／社内判断／下書き）を機械照合可能な形式で出力する。
compiled_from: [Q07A22-C02@2.0.3(38), IMS12A41-F09-01@1.0.1(39), IMS12A41-F09-02@1.0.1(45), IMS12A41-F09-03@1.0.1(64), IMS12A41-F09-04@1.0.1(29)]
compiled_at: 2026-08-03
---

# elicitation-coverage — 要件定義の引き出し観点パック

**機密: 社外秘・本リポジトリ内利用可（ゲート2 H-4）＋2026-08-03 裁定2 により社内管理下の供給先へ限定。**
社外露出・再配布は禁止。撤収は本ディレクトリの削除のみで完了する。

## 何をするか

入力文書（議事録 または Before要件ドラフト）を読み、**観点ファイルの全件**について
「その観点が入力文書で扱われているか」を判定し、扱われていなければ**顧客への確認質問**を起こす。

憶測で埋めない。入力文書に書かれていないことは未決として扱う。
**出力は認定レビュアー承認用ドラフト**であり、確定判断ではない（IMS12A33-G02 制約）。

## 手順

1. **入力文書の工程を判定**し、下表から注入する観点ファイルを選ぶ（非対応工程のファイルは読まない）。
2. 選んだファイルを**1ファイル＝1パス**として順に処理する。パスをまたいで観点を混ぜない。
3. 各パスごとに §出力契約 の YAML を出力する。**そのパスの全件**を必ず含める。
4. 全パス完了後、`scripts/check-coverage-report.sh` で R1〜R7 を機械照合する。

## 観点ファイルと工程対応

| ファイル | ブロック | 件数 | 鮮度 | 対応工程 |
|---|---|---|---|---|
| `viewpoints/A-c02-deliverables.md` | A（成果物定義） | 38 | current | 全工程で注入 |
| `viewpoints/B1-f09-01-current-analysis.md` | B | 39 | frozen-suspect-H5 | 現状調査・分析 |
| `viewpoints/B2-f09-02-concept.md` | B | 45 | frozen-suspect-H5 | 構想立案 |
| `viewpoints/B3-f09-03-definition-p1.md` | B | 22 | frozen-suspect-H5 | 注入対象外（どの工程でも読まない） |
| `viewpoints/B4-f09-03-definition-p2.md` | B | 42 | frozen-suspect-H5 | 調査・定義（後半） |
| `viewpoints/B5-f09-04-system-design.md` | B | 29 | frozen-suspect-H5 | システム設計 |

合計 **215観点**（A=38 ＋ B=177）。うち注入対象は **193観点**（B3 の 22観点は注入対象外）。

- **ブロックA と ブロックB を同一パスに混載しない**（鮮度が異なるため）。
- ブロックB は **H-5割引＝参考質問扱い**。`question` に「（参考質問・H-5割引）」を付記する。
- 現状調査〜要件定義なら A＋B1＋B4 の3パス、外部設計前段なら A＋B5 の2パスが目安。

## 出力契約

パスごとに、次の YAML **のみ**を契約対象として出力する（散文の講評は任意の付録）。

```yaml
coverage_report:
  input_doc: "<入力文書の識別子（ファイル名＋版/日付）>"
  pack: "elicitation-coverage"
  pack_compiled_from: "<本ファイル frontmatter の compiled_from をそのまま転記>"
  pass: "k/m"
  items:
    - item_id: "C02-DEL-001"     # 観点IDに完全一致（発明・改変禁止）
      verdict: covered           # covered | uncovered | not_applicable の3値のみ
      evidence: "議事録 L34-38（新業務フローは営業部案で合意）"  # covered で必須
      question: null             # uncovered で必須
      na_reason: null            # not_applicable で必須
      routing: null              # uncovered で必須（下表の4値）
      source_block: c02          # c02 | f09
```

| フィールド | 値域 | 必須条件 |
|---|---|---|
| `item_id` | 注入観点ID集合の元 | 全件必須。**注入集合との完全一致**（過不足・発明ID・表記改変を禁止） |
| `verdict` | `covered` / `uncovered` / `not_applicable` | 3値のみ。それ以外の語は契約違反 |
| `evidence` | 入力文書の行/節＋短い引用 | `covered` で必須非空 |
| `question` | 未決事項に対する問い・依頼・タスク文 | `uncovered` で必須非空 |
| `na_reason` | 対象外理由1行 | `not_applicable` で必須非空（無理由の対象外を禁止） |
| `routing` | 下表の4値 | `uncovered` で必須。**それ以外は null** |
| `source_block` | `c02` / `f09` | 全件必須 |

### routing — 未決事項の宛先を分ける

**uncovered を一律「顧客への質問」に整形してはならない。** 弊社内で決める事項や、既存材料から
下書きできる事項まで顧客質問として数えると、件数が実態から乖離し優先順位がつけられなくなる。

| 値 | 意味 | 例 |
|---|---|---|
| `ask-customer` | 顧客しか答えられない | 予算、決定権者、現行ネットワーク構成、コード体系、他社との連携方式の意向 |
| `request-material` | 資料提供を依頼すれば済む（問いではない） | 会社概要、現行システムの入出力一覧、現行業務フロー |
| `internal-decide` | 弊社内で決められる（顧客に聞く筋ではない） | 成果物の作成要否・作成時期、レビュー実施時期、図面の粒度 |
| `draft-then-confirm` | 入力材料から下書きでき、人間は確認のみ | 用語集、機能一覧・帳票一覧・画面一覧の初版、主要エンティティの洗い出し |

- **判定に迷ったら `ask-customer` を選ぶ**（顧客確認を省く方向へ倒さない＝保守側）。
- `ask-customer` かつ F09 由来のときのみ、`question` に「（参考質問・H-5割引）」を付記する。
- `draft-then-confirm` でも**本パックは下書きを生成しない**。宛先の表明にとどめる（引き出し支援の範囲を超えないため）。

**判定基準（ブロックA）**: `covered` は「当該成果物の**内容が入力文書中で議論・決定されているか**」で判定する
（成果物ファイルが作成済みかではない）。`uncovered` は内容未決、`not_applicable` は案件スコープ外の場合のみ。

**排他規則**: verdict に対応しないフィールドは null。`uncovered` に evidence を書くのは可
（部分的言及ありだが未決の根拠）。`covered` に question は違反。

## 機械照合（R1〜R7）— 同梱の検証器で必ず実行する

パスごとに出力 YAML を保存し、次を実行する（依存は bash と perl のみ）。

```bash
scripts/check-coverage-report.sh \
  -i ids/<パスと同名>.txt \
  -c "$(cat ids/compiled-from.txt)" \
  [-m <入力材料ファイル>] \
  <出力した report.yaml>
```

終了コード 0=全適合 / 1=違反あり / 2=入力エラー。**exit 0 を確認するまで結果を採用しない。**
`-m` を付けると evidence 中の節参照が入力材料に実在するかも検査する。

| # | 検査 |
|---|---|
| R1 全件性 | `items` 数 ＝ 当該パスの注入観点数（欠落・重複は違反） |
| R2 ID整合 | 全 `item_id` が注入ID集合と**集合として一致** |
| R3 enum | `verdict` が3値のいずれか |
| R4 条件必須 | covered→evidence／uncovered→question／not_applicable→na_reason が非空 |
| R5 排他 | verdict に対応しないフィールドは null |
| R6 層別 | `source_block` が観点IDの由来と一致（C02-\*→c02／F09-\*→f09） |
| R7 転記 | `pack_compiled_from` が frontmatter と一致 |
| R8 処理経路 | uncovered→`routing` が4値のいずれか。uncovered 以外は null |

## してはいけないこと

- 観点の**省略・要約・統合**（全件走査が本パックの唯一の保証）
- 観点IDの**発明・改変**
- 入力文書に無い事実の補完（未決は未決のまま出す）
- 本パックの出力を**確定判断として扱う**こと（認定レビュアー承認用ドラフト）
