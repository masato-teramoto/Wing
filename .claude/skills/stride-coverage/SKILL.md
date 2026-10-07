---
name: stride-coverage
description: セキュリティ方針がSTRIDEの6脅威カテゴリを網羅しているかを検証する
disable-model-invocation: true
---

## 概要

`steering/security.md` が、STRIDE の6つの脅威カテゴリ（なりすまし: Spoofing / 改ざん:
Tampering / 否認: Repudiation / 情報漏洩: Information Disclosure / サービス拒否:
Denial of Service / 権限昇格: Elevation of Privilege）それぞれについて、対応方針を
持っているかを検証する網羅性検証である。

## 入力

| 項目 | 内容 | 指定例 |
|---|---|---|
| 対象 | 検証する成果物 | `steering/security.md` |
| カテゴリ一覧 | 網羅を確認する基準（既定でSTRIDEの6カテゴリ） | なりすまし・改ざん・否認・情報漏洩・サービス拒否・権限昇格 |

## 手順

1. `対象` を通読し、`カテゴリ一覧` の各脅威カテゴリに対応する対応方針（検知・防御・記録の
   いずれか）が記述されているかを1カテゴリずつ確認する。
2. 記述が全く無いカテゴリ、または該当しないと明記された上で理由が無いカテゴリを洗い出す。

## この工程で指摘しない事項

- `.claude/skills/finding-rules/SKILL.md` の工程の境界の表・`confirmed_answers`・`learned` に当たる事項
- `TBD（<工程> で確定）` と書いてある値
- 該当しないと明記され、理由もあるカテゴリ

当たるものは指摘にせず、除外として返す（除外の出典を付ける。書き方は finding-rules）。

## 出力の形

指摘ごとに次を返す。書き方は `.claude/skills/finding-rules/SKILL.md`（検査の最初に読む）に従う。重大度は出さない（L3 が `kind` から決める）。

```
{ location, subject, kind, summary, evidence, suggestion, recommendation, is_rollback_candidate }
```

| フィールド | 内容 |
|---|---|
| `location` | 記述が欠落しているカテゴリ名（対象ファイルの箇所）。`<案件相対パス> § <節見出し> / <ID>` の形。複数箇所なら代表 1 か所＋「ほか n か所」（全件は `evidence`） |
| `subject` | 対象の語（例: `否認`） |
| `kind` | `.claude/skills/finding-rules/SKILL.md` の種類から 1 つ選ぶ。迷ったら上の行。通常 `業務の欠落・矛盾`（セキュリティ） |
| `summary` | 60 字以内。結論を先に、何が・どこで（例: 「STRIDE の『否認』への対応方針が security.md に無い」） |
| `evidence` | 欠落の事実と、確認した対象の範囲 |
| `suggestion` | 追記する対応方針（検知・防御・記録）の文案。方針の中身が業務の新しい事実なら「何を決めればよいか」と選べる案 |
| `recommendation` | `修正：理由` / `差戻し：理由` / `対応せず進める：理由` / `質問：理由` のどれか。業務の新しい事実が要るときは `質問：…` |
| `is_rollback_candidate` | 通常 `false`（同一フェーズ内での追記で解消できるため） |

## 禁止

- 対象成果物を書き換えない（方針を自動で追記しない）
- 合否を出さない
- 方針の技術的妥当性までは判断しない（有無の網羅性のみ）
