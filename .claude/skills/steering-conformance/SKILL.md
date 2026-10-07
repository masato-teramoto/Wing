---
name: steering-conformance
description: 対象成果物が steering（方針・設計ルール）に違反していないか、粒度が適切かを検証する
disable-model-invocation: true
---

## 概要

対象成果物が `steering/` の方針・設計ルール（技術選定・アーキテクチャ・セキュリティ方式・
非機能方針・API規約等）に違反していないか、また steering 自身の粒度（原則の記述に実体を混入
させていないか）を検証する。呼び出し元が対象と参照する steering ファイルを指定することで、
Phase 2（自己参照の粒度検証）・Phase 3（分割のsteering整合）・Phase 4（steering違反）・
Phase 5（技術選定・security方式の反映）・Phase 7（tech.mdとの矛盾）に使い回せる。

## 入力

| 項目 | 内容 | 指定例 |
|---|---|---|
| 対象 | 検証する成果物 | `specs/<feature>/design.md` |
| 参照する steering | 違反判定の正 | `steering/` 7ファイル一式（全フェーズで一式を参照する） |
| 検証観点 | 何を見るか | `技術選定の逸脱` / `security方式の逸脱` / `粒度・実体混入` |
| 報告単位 | 何を1件の指摘にするか（任意） | `feature × セクション` / `feature × タスク番号` |

## 手順

1. `参照する steering` を一式（該当章だけでなく全文）読み、制約として機能する記述（方針・規約・禁止・
   必須・準拠）を把握する。
2. `対象` を読み、`検証観点` に該当する箇所を steering の方針と突き合わせる。
3. 次の2種を検出し、種別を `evidence` に書く。

   | 種別 | 内容 |
   |---|---|
   | 違反 | steering が禁止・限定していることを対象が行っている（未承認の技術選定、方針で禁止された設計等） |
   | 矛盾 | steering の記述と対象の記述が両立しない |

   steering に無い前提を対象が独自に導入している（無断の拡張）ものは、上流に根拠のない追記として
   evidence-guard が出すので、ここでは出さない（finding-rules の持ち主の表）。

4. 各指摘の `evidence` に steering 側の根拠（ファイル名とセクション）を書く。根拠を示せないものは指摘にしない。
5. `検証観点` に「粒度・実体混入」が含まれる場合、steering の設計ルール（業務コード・DB エンティティ等）を次で検証する。

   | 検査 | 判定 |
   |---|---|
   | ルールの粒度 | 各 `design.md` がそのルールを参照するだけで設計できるか。粒度が足りず feature ごとに独自解釈が生じうる箇所を指摘する |
   | 実体の混入 | 個々のコード値・区分値・採番対象・テーブル定義など、個別実装の実体が steering に書かれていないか（steering は方針、spec は実体） |
   | 判定基準 | 全 feature に等しく適用されるならルール（steering）、feature ごとに異なるなら実体（`design.md`） |

## この工程で指摘しない事項

- `.claude/skills/finding-rules/SKILL.md` の工程の境界の表・`confirmed_answers`・`learned` に当たる事項
- `TBD（<工程> で確定）` と書いてある値
- steering に無い前提の導入（無断の拡張）。evidence-guard が出す

当たるものは指摘にせず、除外として返す（除外の出典を付ける。書き方は finding-rules）。

## 出力の形

指摘ごとに次を返す。書き方は `.claude/skills/finding-rules/SKILL.md`（検査の最初に読む）に従う。重大度は出さない（L3 が `kind` から決める）。

```
{ location, subject, kind, summary, evidence, suggestion, recommendation, is_rollback_candidate }
```

| フィールド | 内容 |
|---|---|
| `location` | steering 違反・粒度不足が見つかった箇所（対象側。steering 側の箇所は `evidence`）。`<案件相対パス> § <節見出し> / <ID>` の形。複数箇所なら代表 1 か所＋「ほか n か所」（全件は `evidence`） |
| `subject` | 対象の語（例: `ORM 方針`） |
| `kind` | `.claude/skills/finding-rules/SKILL.md` の種類から 1 つ選ぶ。迷ったら上の行。違反・矛盾は `業務の欠落・矛盾`。ルールの粒度不足は `業務のあいまい・不足`。steering への実体の混入は `工程・文書の分担` |
| `summary` | 60 字以内。結論を先に、何が・どこで（例: 「design.md が tech.md で禁止された ORM を使っている」） |
| `evidence` | 違反／矛盾の別と事実、steering 側の根拠（ファイル名とセクション） |
| `suggestion` | 修正案（差分・書き換え文）。業務の新しい事実が要るときは、修正案ではなく「何を決めればよいか」と選べる案 |
| `recommendation` | `修正：理由` / `差戻し：理由` / `対応せず進める：理由` / `質問：理由` のどれか。業務の新しい事実が要るときは `質問：…` |
| `is_rollback_candidate` | steering自体の不備が原因の場合は `true`（差戻し先は Phase 2） |

## 禁止

- 対象成果物・steeringを書き換えない
- 合否を出さない
- steeringに明記の無い「一般的なベストプラクティス」を根拠に指摘しない（steeringが正）
- steering 自身の方針の妥当性を評価しない（③ 人間レビューの観点）。粒度・実体混入の検査は役割分担の確認に留める
- steering の記述不足を対象成果物の違反として断定しない。steering に無い前提の導入（無断の拡張）は出さない（evidence-guard が出す）
