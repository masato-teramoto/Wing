# PROVENANCE — requirement-clarification（明確化セッションパック・S1）

- compiled_at: 2026-09-01 ／ compose 実行: /loop-compose phase requirement-clarification --include-draft
- 位置づけ: 要求・要件定義フェイズ Skill 一式（選定案 rev78）の **S1**。**dispatch を持たない**
  （mode 分岐がなく、project profile も読まない）。
- 再コンパイル条件: compiled_from のカードの version・status が変わったら再生成（/loop-report が検出）。
  **本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）。

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-030 | 0.2.0 | draft | authoritative | null |

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-030 明確化セッション規約 | 0.2.0 | draft | community-consensus | volatile / 2027-01-25 | 実行フロー・ルールA〜C | K-01〜K-06に加え、人間承認済みの静的 advisory として SO-01（被覆走査）・SO-04（終了報告）・SO-07（分解優先）・SO-09（残余チェックと引き継ぎ）を収載 |

### SO 全件の選定状態

| SO | 状態 | 反映先・条件または非収載理由 |
|---|---|---|
| SO-01 | 収載 | 実行フロー2〜3。10観点を Clear / Partial / Missing で走査する静的 advisory |
| SO-02 | 非収載 | 固定質問数・選択肢数・回答語数は案件依存 |
| SO-03 | 非収載 | 方言固有の clarification log 様式は常設しない |
| SO-04 | 収載 | 実行フロー4。質問不要と打切りを区別し、残余を Deferred / Outstanding で報告 |
| SO-05 | 非収載 | 71手法のレジストリは具体・大規模で、汎用 Skill の常設知識にしない |
| SO-06 | 非収載 | 反復承認の具体手続きは案件・対話方式に依存 |
| SO-07 | 収載 | 実行フロー1。過大要求では詳細質問より分解と対象選択を先行 |
| SO-08 | 非収載 | 設計案数の固定は案件依存 |
| SO-09 | 収載 | 実行フロー4。placeholder・矛盾・スコープ・複数解釈を再走査し、未解決は質問または handoff。正式な仕様レビューは行わない |
| SO-10 | 非収載 | 固定質問数・選択肢数を含み SO-02 と同じ案件依存 |
| SO-11 | 非収載 | PR-ready plan は下流工程へ越境する |

- **承認根拠**: 利用者指示 2026-09-01。選定案 rev76 と rev78 §0／§2 に pack と SO-ID を固定した。
- 収載4件はすべて advisory。Contract なしで、正式な合否・採点・遷移ゲートには使わない。

- **参照の閉包**: 本パックの handoff 先は `requirement-authoring-core`（optional）のみ。選定案 §5 のとおり
  S1 は guard を持たず、受入判定への直接 handoff も持たない（要求成果物になってからの経路に委ねる）。
  C-01 の「最小反映・矛盾旧文の置換」と S2 の「正式な構造化・finalize」の境界を本文に明記した。
- **入力契約（カード由来ではない）**: `clarification_target`／`writeback_ref` の必須化と解決規則4項は
  **KA-REF-030 に由来しない**。同カードは明確化セッションの**進め方**（K-01〜K-06）を定めるが、
  **書き戻し先の特定**には触れていない（K-05 は「即時に書き戻す」までで、どこへ書くかを決めない）。
  したがって本節は advisory なカード知識ではなく、**利用者指示に基づく運用契約**として区別して記録する
  （由来: ユーザー指示 2026-08-28・第39回レビュー。選定案 §2 の S1 追補に収載）。
  バッジの全称形「本パックの**カード由来の知識**は全項が advisory」はこの追加後も成立する。
- **A-03 との関係を明記した理由**: 省略の許可（K-06）が書き戻し（K-05）の免除として読まれると、回答を
  受理しながら記録しない経路が開く。両者は別の規範であり、省略できるのは明確化の実施だけである。
- **確認は1問ずつ**: 不足入力が複数でも A-02（一度に一問）が優先するため、S3b のように1回のやり取りで
  まとめて確認しない。**対の S3b とは意図的に異なる**（各パックの既存規範を上書きしない）。
- **再 compose 入力**: 本パックの再生成入力は **`assets/`（KA-REF-030）＋ 選定案 rev38・rev76・rev78 §2 の S1 追補**である。
  カード由来でない運用契約は assets/ 側に存在しないため、`assets/` だけを入力にすると失われる。
- `activate_specializations` による runtime selector は未導入。本再 compose は人間が名指しした4件を
  `ADVISORY` pack へ静的収載したもので、dispatch・project profile 読取り・Contract の合否条件を追加しない。
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率等の評価数値を転記していない。

## バッジ（共通規律2）

- `draft_badge` = **true**（status: draft）。SKILL.md 冒頭に DRAFT 印あり。
- `pack_advisory` = **true**（authoritative かつ contract: null ＝未検証権威）。全称形の advisory 宣言に加え、
  **カード1枚1行の強度ブロック**を持つ（export-policy §2 規則4）。

### カード別の軸（status / review_status / supply_mode / contract）

| カード | status | review_status | supply_mode | contract | 本パックでの供給強度 |
|---|---|---|---|---|---|
| KA-REF-030 | draft | 未記載（schema 既定＝unreviewed） | authoritative | null | advisory（export-policy §2 規則4＝未検証権威の遮断） |

- **4軸は独立**（asset.schema.md・2026-07-09 人間裁定）: `status`＝カードの校正ライフサイクル／
  `review_status`＝カード本文の人間レビュー（**無記載＝unreviewed** が schema 既定）／`supply_mode`＝利用時の
  強度／`evidence_strength`・案件回帰＝実務上の根拠。SKILL.md の DRAFT 印は **status 軸だけ**を示す。
- **draft のままである理由**: カードの `draft→validated` の**唯一のトリガは host Contract の validated 昇格**
  （PROFILE.md「カード昇格規則」2026-07-08 人間裁定）。`contract: null` の間は昇格の契機が無い。
  Contract 接続の予定が無いカードは実質的に draft が継続する——**カード本文の不備を意味しない**。
- **`validated` でも実務妥当性は保証されない**（CLAUDE.md「validated の意味」2026-07-09 明文化。judge 運用上の
  自律可能性のみを意味する）。したがって実務妥当性の留保は DRAFT 固有の警告ではなく、SKILL.md では
  **ADVISORY の位置づけ**として利用者の行動（案件の前提・規約・制約と照合／正式な合否判定の根拠にしない）へ
  翻訳して示す。

## 元 OSS ライセンス（帰属・NOTICE 引継ぎ）

| 上流 | ライセンス | 経由カード |
|---|---|---|
| github/spec-kit | MIT | KA-REF-030 |
| bmad-code-org/BMAD-METHOD (v6) | MIT | KA-REF-030 |
| obra/superpowers | MIT | KA-REF-030 |
| All-Hands-AI/OpenHands | MIT | KA-REF-030 |

- 全ライセンスは MIT＝互換・再配布可。NOTICE ファイルは**原文になし**。版固定は factory/snapshots/oss/PROVENANCE.md。
- **非選定（BY-SA 隔離12枚・export-policy 規則1）の完全 ID**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 —— いずれも本パックに含まれず、隔離解除は法務確認の完了のみ（adr/0007 §1）。
- snapshots/・corpus/ の凍結原本は本パックに複製していない（export-policy 規則2）。

## 選定記録

- 選定基準: テーマ「明確化セッション」に適合する1枚。要求記述の規約（KA-REF-001/009/010/021）は
  `requirement-authoring-core` の領分につき非収載——本文では handoff として一般化表現で記述した。
- **静的 advisory の選定基準**: 薄い明確化を直接補う「走査観点」「残余を区別する終了報告」「過大要求の
  分解判断」「終了直前の残余検出と handoff」に限定した。数値・方言・下流工程への依存が強い SO は非収載とした。
- **`--include-draft`**: status: draft の構成資産を含むため DRAFT 印を付して収載。DRAFT は元資産の
  校正ライフサイクルだけを表し、Skill の出荷検査や実務妥当性の判定を表さない。
