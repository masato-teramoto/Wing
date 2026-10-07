---
name: finding-reevaluation
description: 切り替え前の版（旧形式）で出た未判断の指摘を、指摘の共通ルールで見直し、新しい形の指摘として 1 実行ブロックに書く（再評価の回）。新しい検査は行わない。
disable-model-invocation: true
---

## 使う場面

改修前の版で検査した案件を新しい版に切り替え、人が切り替え前の未判断の指摘を「再評価する」と選んだとき、L3 は本文を変えない修正の回を予約する。
その回の検査で、context に `reevaluation`（再評価の対象の回 `run`・その回の実行した層 `layers`・旧形式の指摘 `findings`）がある。
このとき検査役は、合成 check の観点を実行せず、この手順で旧形式の指摘だけを見直す。

## 入力

- `reevaluation.findings`：旧形式の指摘（スコープ・回数・番号・観点・対象箇所・指摘内容）
- `.claude/skills/finding-rules/SKILL.md`（指摘の共通ルール）と、`confirmed_answers`・`learned`（前提）
- 検査対象（`review_targets`）と上流。findings_path の機械指摘（今回の回のもの）

## 手順

1. `.claude/skills/finding-rules/SKILL.md` を読む。
2. 旧形式の指摘を 1 件ずつ見直す。
   1. 指摘が指す問題が、今の検査対象に実在するかを確かめる。実在しない・取り違えている場合は除外する（除外の出典 `verify:<理由>`）。
   2. 前提に当たるもの（工程の境界の表・`confirmed_answers`・`learned`・`TBD（<工程> で確定）`）は除外する（出典 `rule:` / `answer:` / `learned:`）。
   3. 残ったものに、共通ルールの項目（location・subject・kind・summary・evidence・suggestion・recommendation・is_rollback_candidate）を付ける。
      evidence の先頭に、元の指摘を `旧 <回数>-<番号>：` で書き、続けて根拠を書く。kind は共通ルールの 6 つから選び、迷ったら業務に寄せる。
   4. 同じ問題を指す旧形式の指摘は 1 件にまとめ、evidence に元の番号をすべて書く。外した側は除外する（出典 `verify:重複（旧 <回数>-<番号> と同じ）`）。
3. 今回の回の機械指摘（findings_path）は、改変せずにそのまま含める（gate-report の決まりのとおり）。
4. 新しい問題を探さない。旧形式の指摘に無い問題は、この回では指摘しない（次の通常の検査で扱う）。
5. `.claude/skills/finding-verification/SKILL.md` の手順で確かめてから、`.claude/skills/gate-report/SKILL.md` で 1 実行ブロックを書く。
   実行した層は `reevaluation.layers`（再評価の対象の回と同じ）を書く。新しく検査を広げたのではなく、その回の検査の範囲を引き継ぐため。

## 禁止

- 検査対象・上流の本文を変えない（L3 は本文が再評価の対象の回から変わっていれば受け付けない）
- 判断・理由の欄を埋めない。重大度・同一性キーを書かない（L3 が決める）
- 旧形式の指摘を、理由を書かずに捨てない（除外には必ず出典を書く）
- 実行した層を `reevaluation.layers` と違う値にしない
