---
name: schema-migration-task-coverage
description: design.mdのデータモデル変更が、tasks.md上でExpand-Contract（拡張→移行→縮小）のタスクとして分解されているかを検証する
disable-model-invocation: true
---

## 概要

`specs/<feature>/design.md` にスキーマ変更（列追加・型変更・テーブル分割等）を伴うデータ
モデルが含まれる場合、`specs/<feature>/tasks.md` がそれを安全な Expand-Contract パターン
（① 拡張: 新旧両対応で追加 → ② 移行: データ移行・書き込み切替 → ③ 縮小: 旧定義の削除）に
分解したタスクとして持っているかを検証する。

## 入力

| 項目 | 内容 | 指定例 |
|---|---|---|
| 対象 | スキーマ変更の記述元 | `specs/<feature>/design.md` のデータモデル部分 |
| 突合先 | タスク化の確認先 | `specs/<feature>/tasks.md` |

## 手順

1. `対象` からスキーマ変更を伴うデータモデルの記述を抽出する（新規テーブルの追加のみは対象外。
   既存データへの影響を伴う変更を対象とする）。
2. `突合先` に、その変更が Expand（拡張）・Migrate（移行）・Contract（縮小）に相当する
   タスクとして分解されているかを確認する。
3. 一括での破壊的変更（既存カラムの即時削除・型の即時変更等）としてしかタスク化されていない
   場合を指摘する。

steering / design が停止時間を設けた移行など別の方式を承認済みで定めている場合は、その方式に必要な手順の網羅を照合する。Expand-Contract を無条件に強制しない。方式自体が未決定なら tasks 内で決めず、design への確認候補を返す。

## 出力の形

```
{ id, location, finding, is_rollback_candidate }
```

| フィールド | 内容 |
|---|---|
| `id` | この Skill 内で一意な通し番号 |
| `location` | 該当するスキーマ変更箇所（design.md）とタスク（tasks.md） |
| `finding` | 未分解の事実（例: 「`design.md` の `users.email` の型変更が、`tasks.md` では一括更新タスクとしてのみ存在し、移行段階が無い」） |
| `is_rollback_candidate` | 通常 `false`（同一フェーズ内でのタスク分解で解消できるため） |

## 禁止

- 対象成果物を書き換えない（タスクを自動で分解・追加しない）
- 合否を出さない
- 具体的な移行手順の内容までは提案しない（未分解である事実の指摘に留める）
