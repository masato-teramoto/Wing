# PROVENANCE — implementation-planning（実装計画パック・S5）

- compiled_at: 2026-09-14 ／ compose 実行: /loop-compose phase implementation-planning
- 位置づけ: 要求・要件定義フェイズ Skill 一式（選定案 rev82）の **S5**。P3 execution で生成したパックを、
  rev78 で残したタスク間インターフェースの具体化として再 compose した。
  dispatch は **mode-only**（project profile を読まない）。
- 再コンパイル条件: compiled_from のカードの version・status が変わったら再生成。
  版の差分は /loop-report、status を含む依存整合は compose gate で確認する。
  **本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）。

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-029 | 0.1.0 | draft | authoritative | null |

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-029 実装計画・エピック分割規約 | 0.1.0 | draft | community-consensus | volatile / 2027-01-18 | 必須の文脈・ルールA〜C・タスク間の受け渡しを具体化する・review 時の出し方 | K-01（要求 ID の明記を含む）・K-02〜K-06。SO-03 と SO-04 の型整合部分を K-02/K-05 の具体化として静的 advisory 収載。ステップ粒度の分数・タスク ID 書式（T001／[P]／[US1]）・Phase 構成 enum は非収載とし、「プロジェクトの決定事項」へ一般化した |

- **パス文脈の両 mode 必須**（不足時 authoring＝ブロッカー報告／review＝UNDETERMINED）は選定案 §2 の
  S5 規範（rev19 で復元）に由来する適用注記であり、新規 invariant ではない。
- **今回の選定根拠**: 2026-09-11 の利用者による「Skill 内容と Compose 基盤を整える」という依頼を受け、
  選定案 rev82 で rev78 の残題を具体化した。SO-03 の受取／提供様式と SO-04 の型整合部分のみを選定し、
  新たな人間裁定や項目別の独立承認があったとは記録しない。
- **接地と範囲**: SO-03 は `assets/reference/KA-REF-029.md` の当該項目と
  `snapshots/oss/superpowers/writing-plans-SKILL.md` L89–93、SO-04 の型整合は同 L152 に接地する。
  K-02（先行出力への依存）・K-05（追加文脈なしの自己完結記述）を実行時に使える形へ具体化した。
  本文は pack 全体の【SHOULD】相当を維持し、【MUST】／【MUST NOT】・PASS／FAIL・正式採点・遷移ゲートの
  根拠にしない。Contract は追加せず、`activate_specializations`・runtime selector・dispatch・project profile
  の読取りも追加していない。`authoring` の記述修正と `review` の指摘のみという既存境界を維持する。
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率等の評価数値を転記していない。

## SO 選定状態（KA-REF-029 の全9項目）

| SO-ID | 状態 | 反映先・範囲または非収載理由 |
|---|---|---|
| SO-01 | 非収載 | 固定分数・TDD 5ステップは今回のタスク間インターフェースの具体化に含めない |
| SO-02 | 非収載 | 計画ヘッダ定型・Global Constraints の逐語転記は今回の対象外 |
| SO-03 | 収載 | 「タスク間の受け渡しを具体化する」の Consumes／Produces。先行から受け取り、後続へ提供する名前・型を静的 advisory として記す |
| SO-04 | 収載 | 同節の型・シグネチャ・プロパティ名の整合部分のみ。spec coverage と placeholder は既存 K-01/K-05 に反映済み。SO 固有の inline 修正手順・再レビュー不要という指示は非収載 |
| SO-05 | 非収載 | 計画の実行側の停止規律は本パックの計画作成／レビューの範囲外 |
| SO-06 | 非収載 | タスク ID・チェックリストの厳格書式は spec-kit 方言であり、プロジェクトで決める |
| SO-07 | 非収載 | 固定 Phase 構成・MVP first は方言依存であり、共通基盤の前倒しには源泉間の差がある |
| SO-08 | 非収載 | file churn を根拠にしたエピック統合は今回の対象外 |
| SO-09 | 非収載 | エンティティ作成時期・starter template の位置固定は今回の対象外 |

## バッジ（共通規律2）

- `draft_badge` = **true**（KA-REF-029 は status: draft）。SKILL.md 冒頭に DRAFT 印あり。
- `pack_advisory` = **true**（authoritative かつ contract: null ＝未検証権威）。全称形の advisory 宣言に加え、
  **カード1枚1行の強度ブロック**を持つ（export-policy §2 規則4）。

### カード別の軸（status / review_status / supply_mode / contract）

| カード | status | review_status | supply_mode | contract | 本パックでの供給強度 |
|---|---|---|---|---|---|
| KA-REF-029 | draft | 未記載（schema 既定＝unreviewed） | authoritative | null | advisory（export-policy §2 規則4＝未検証権威の遮断） |

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
| obra/superpowers | MIT | KA-REF-029 |
| bmad-code-org/BMAD-METHOD (v6) | MIT | KA-REF-029 |
| github/spec-kit | MIT | KA-REF-029 |

- 全ライセンスは MIT＝互換・再配布可。NOTICE ファイルは**原文になし**。版固定は factory/snapshots/oss/PROVENANCE.md。
- **非選定（BY-SA 隔離12枚・export-policy 規則1）の完全 ID**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 —— いずれも本パックに含まれず、隔離解除は法務確認の完了のみ（adr/0007 §1）。
- snapshots/・corpus/ の凍結原本は本パックに複製していない（export-policy 規則2）。

## 選定記録

- 選定基準: テーマ「実装計画」に適合する1枚（KA-REF-029）。被覆の**監査成果物**は KA-REF-023 の領分に
  つき非収載——本文では `traceability-audit` への redirect と再監査 handoff として表現した。
- **`--include-draft` 相当**: status: draft のため DRAFT 印を付して収載。host Contract による校正済み状態に
  ないことを示すものであり、judge の実行有無やカード本文のレビュー状態は表さない。

## 任意の完成例への案内（2026-09-14）

[実務改善選定F07](../../../../docs/proposals/skills-practicality-improvement-20260914.md)を再生成の運用入力として追加した。独立のrequirements-authoring-guideへの任意の案内だけを加え、構成資産・規範・既存の選定・入力解決・判定の強度は維持する。guideの助言・合成artifactを本packに混載せず、未導入を新たな停止理由にしない。旧版のreceiptは今回の再生成の正式受入を示さない。
