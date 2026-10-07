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

steering / design が停止時間を設けた移行など別の方式を承認済みで定めている場合は、その方式に必要な手順の網羅を照合する。Expand-Contract を無条件に強制しない。方式自体が未決定なら tasks 内で決めず、design への確認候補（`recommendation` は `差戻し：…`）を返す。

## この工程で指摘しない事項

- `.claude/skills/finding-rules/SKILL.md` の工程の境界の表・`confirmed_answers`・`learned` に当たる事項
- `TBD（<工程> で確定）` と書いてある値
- 新規テーブルの追加のみの変更

当たるものは指摘にせず、除外として返す（除外の出典を付ける。書き方は finding-rules）。

## 出力の形

指摘ごとに次を返す。書き方は `.claude/skills/finding-rules/SKILL.md`（検査の最初に読む）に従う。重大度は出さない（L3 が `kind` から決める）。

```
{ location, subject, kind, summary, evidence, suggestion, recommendation, is_rollback_candidate }
```

| フィールド | 内容 |
|---|---|
| `location` | 該当するタスク（tasks.md）の箇所（design.md 側の箇所は `evidence`）。`<案件相対パス> § <節見出し> / <ID>` の形。複数箇所なら代表 1 か所＋「ほか n か所」（全件は `evidence`） |
| `subject` | 対象の語（例: `users.email`） |
| `kind` | `.claude/skills/finding-rules/SKILL.md` の種類から 1 つ選ぶ。迷ったら上の行。既存データを失う一括の破壊的変更は `業務の欠落・矛盾`。段階の分け方の不足は `業務のあいまい・不足` |
| `summary` | 60 字以内。結論を先に、何が・どこで（例: 「`users.email` の型変更が一括更新タスクのみで移行段階が無い」） |
| `evidence` | design.md のスキーマ変更の記述と、tasks.md の該当タスク |
| `suggestion` | Expand・Migrate・Contract（または承認済みの方式）に分けたタスクの案 |
| `recommendation` | `修正：理由` / `差戻し：理由` / `対応せず進める：理由` / `質問：理由` のどれか。業務の新しい事実が要るときは `質問：…` |
| `is_rollback_candidate` | 通常 `false`（同一フェーズ内でのタスク分解で解消できるため） |

## 禁止

- 対象成果物を書き換えない（タスクを自動で分解・追加しない）
- 合否を出さない
- 業務の新しい事実が要る値を自分で決めない。`suggestion` に「何を決めればよいか」と選べる案を書き、`recommendation` を `質問：…` にする
