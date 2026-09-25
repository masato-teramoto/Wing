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

## 出力の形

```
{ id, location, finding, is_rollback_candidate }
```

| フィールド | 内容 |
|---|---|
| `id` | この Skill 内で一意な通し番号 |
| `location` | 記述が欠落しているカテゴリ名 |
| `finding` | 欠落の事実（例: 「STRIDEの『否認』（Repudiation）への対応方針が `security.md` に無い」） |
| `is_rollback_candidate` | 通常 `false`（同一フェーズ内での追記で解消できるため） |

## 禁止

- 対象成果物を書き換えない（方針を自動で追記しない）
- 合否を出さない
- 方針の技術的妥当性までは判断しない（有無の網羅性のみ）
