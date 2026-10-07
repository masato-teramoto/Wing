---
name: gate-report
description: スナップショットに対応する1回の検査結果を、ゲート記録へ追記するための1実行ブロックとして inspection_path に書き出す（追記は L3 が1回だけ行う）。
disable-model-invocation: true
---

## 入力

当該実行の snapshot、gate_record_path（読むだけ）、inspection_path（書き出し先）、実行した層、finding-verification が確かめた指摘一覧（gate / kind / location / subject / summary / evidence / suggestion / recommendation / verification / is_rollback_candidate）、findings_path から取り込んだ機械指摘、除外一覧（gate / location / summary / 除外の出典）、差戻し候補の宛先と理由。指摘の採否や人間回答は受け取らない。

## 手順

1. `Templates/Flow/gate-record-format.md` と既存のゲート記録を読む（読むだけで編集しない）。ファイルは snapshot ゲートが初期化済みである。無い、旧形式、対象が不一致の場合はfailedで戻る。
   コードprofileのハッシュはコード在庫と証跡を束ねたmanifestのSHA256で、成果物status更新は行わない。
2. inspection_path のファイルを**上書きで**作り、`## 実行` の表を1行書く（中断後にもう一度実行しても同じファイルを書き直すだけで、記録は二重にならない）。スコープ・回数・実行日時・対象成果物・原本SHA256はsnapshotから転記する。実行した層は実績、指摘件数は今回の指摘表の行数を使う。
3. 同じファイルの直後に `### 指摘` の固定12列表を書く。

   | # | 観点 | 種類 | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |

   - 番号は今回の中で1から連番。観点＝gate、種類＝kind、対象箇所＝location、対象の語＝subject、要約＝summary、指摘内容＝evidence、修正案＝suggestion、推奨＝recommendation、確かめ役＝verification。修正案・推奨・確かめ役が無いときは `-`。判断・理由は必ず空欄。
   - 機械指摘は指摘内容に本文をそのまま書く。種類は検査の種類で決まる（format-conformance → 書式（ID の重複・参照の不整合なら文書間の参照）、revision-diff-validity／sequence-consistency → 文書間の参照、dependency-cycle-detection → 業務の欠落・矛盾。観点の名前は機械検査が findings_path に書いた名前のまま）。要約は本文を60字以内に縮めたもの（60字以内ならそのまま）、対象の語は本文が指すIDや語（無ければ `-`）、修正案・推奨・確かめ役は `-`。
   - 0件でも見出しと区切りだけの表を追加する。旧形式の6列表は書かない。
4. 差戻し候補があれば `### 差戻し先候補`（指摘番号 / 宛先 / 理由）を続けて書き、今回の指摘番号・候補の宛先・理由を記す。候補先を確定できなければ「人間による確認」と記す。機械指摘の本文に候補文字列を混ぜて改変しない。
5. 除外があれば `### 除外`（観点 / 対象箇所 / 要約 / 除外の出典）を最後に書く。除外の出典は `rule:` / `answer:` / `learned:` / `verify:` / `unchecked:` のどれかで始める（`unchecked:` は形式不備で意味検査から外した節）。
6. scope / run / findings_count / layers を返す。ステージの指摘がすべて元の観点・対象箇所・本文のまま含まれることを確認する。

## 禁止

- フロントマターの更新、途中の表への挿入、既存の改行・文字コード・行順の変更。
- 重大度・同一性キー・節ハッシュの列の記入（L3 が scope-check で足し、同じ指摘をまとめる）。
- 判断・理由の記入、承認の空行やプレースホルダーの追加、解消・承認・確認ブロックの作成。
- 以前の未解消指摘を今回件数へ加えること、指摘を勝手に採否判定して削ること（外すのは確かめ役だけで、必ず除外に残る）。
- inspection_path 以外への書込み（ゲート記録・成果物・進捗を含む）。ゲート記録への追記と成果物の draft → review 遷移は、次の scope-check で L3 が1回だけ行う。

表の各セルに `|` が含まれる場合は `&#124;`、改行は `&#10;` とし、固定列数を壊さない。実行表の対象一覧とハッシュ辞書はJSONとして記す。空の値で検査完了を作らない。
