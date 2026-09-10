# PROVENANCE — canonical-terminology-authoring（用語集の作成パック・S3a）

- compiled_at: 2026-09-01 ／ compose 実行: /loop-compose operation canonical-terminology-authoring --include-draft
- 位置づけ: 要求・要件定義フェイズ Skill 一式（選定案 rev78）の **S3a**。**dispatch を持たない**
  （project profile も読まない）。対になる S3b（terminology-consistency-audit）と**相互 redirect**の関係。
- 再コンパイル条件: compiled_from のカードの version・status が変わったら再生成（/loop-report が検出）。
  **本ファイル・SKILL.md の手編集禁止**（assets/ が SSOT）。

## compiled 一覧（5列・D1 receipt の突合対象）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-024 | 0.1.0 | draft | authoritative | null |

## カード ↔ 節 対応表

| カード | version | status | evidence_strength | volatility / review_by | 反映先の節 | 反映項目 |
|---|---|---|---|---|---|---|
| KA-REF-024 用語の正準化規約 | 0.1.0 | draft | community-consensus | volatile / 2027-02-22 | ルールA〜C | K-01・K-02・K-04に加え、SO-02（新語の同一変更内登録）・SO-03（改名の全成果物への波及）を静的 advisory として収載。K-03 は対の S3b が所有 |

### SO 全件の選定状態

| SO | 状態 | 反映先・条件または非収載理由 |
|---|---|---|
| SO-01 | 非収載 | 関係・多重度を持つ軽量オントロジー化は案件の用語モデルに依存 |
| SO-02 | 収載 | ルールC。新しいドメイン名詞を導入と同じ変更内で用語集へ登録 |
| SO-03 | 収載 | ルールC。正準語の改名を全成果物へ波及し、必要な旧称注記だけを1回残す |
| SO-04 | 非収載 | 実装前後の申告ゲートは工程と Contract に依存 |
| SO-05 | 非収載 | 配置・整列・参照方法を含む用語集の読み物設計は案件固有 |

- 収載2件は利用者指示 2026-09-01 と選定案 rev78 による静的 advisory。正式な合否・採点には使わない。

- **S3a／S3b の分割**は選定案 §1 の設計（作成＝S3a／read-only 監査＝S3b）に従う。同一カードから2パックを
  compose し、**K-03 を S3b に、K-01/K-02/K-04 を S3a に**割り当てた（重複収載をしない）。
- `activate_specializations` による SO の選択的活性化は **P3 では未導入**。SO-02・SO-03 は上表の
  人間承認に基づく静的 advisory であり、runtime selector・Contract の合否条件を追加しない。
- 校正数値の転記規律（adr/0006）: 本パックには judge 一致率等の評価数値を転記していない。

- **監査への引き継ぎ内容（カード由来ではない）**: S3b が必須入力とする `canonical_glossary_ref`／
  `audit_targets` を明示して渡す旨の1項は **KA-REF-024 に由来しない**（同カードは用語集の内容規約であり、
  パック間の受け渡し様式に触れていない）。**利用者指示に基づく運用契約**として記録する
  （由来: ユーザー指示 2026-08-28・第37回レビュー。選定案 §2 の S3a/S3b 追補に収載）。
  バッジの全称形「本パックの**カード由来の知識**は全項が advisory」はこの追加後も成立する。
- **再 compose 入力**: `assets/`（KA-REF-024）＋選定案の S3a/S3b 入力契約追補＋rev78 の SO 選定。

## バッジ（共通規律2）

- `draft_badge` = **true**（status: draft）。SKILL.md 冒頭に DRAFT 印あり。
- `pack_advisory` = **true**（authoritative かつ contract: null ＝未検証権威）。全称形の advisory 宣言に加え、
  **カード1枚1行の強度ブロック**を持つ（export-policy §2 規則4）。

### カード別の軸（status / review_status / supply_mode / contract）

| カード | status | review_status | supply_mode | contract | 本パックでの供給強度 |
|---|---|---|---|---|---|
| KA-REF-024 | draft | 未記載（schema 既定＝unreviewed） | authoritative | null | advisory（export-policy §2 規則4＝未検証権威の遮断） |

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
| bmad-code-org/BMAD-METHOD (v6) | MIT | KA-REF-024 |
| github/spec-kit | MIT | KA-REF-024 |
| github/awesome-copilot | MIT | KA-REF-024 |
| Fission-AI/OpenSpec | MIT | KA-REF-024 |

- 全ライセンスは MIT＝互換・再配布可。NOTICE ファイルは**原文になし**。版固定は factory/snapshots/oss/PROVENANCE.md。
- **非選定（BY-SA 隔離12枚・export-policy 規則1）の完全 ID**: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015, KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038 —— いずれも本パックに含まれず、隔離解除は法務確認の完了のみ（adr/0007 §1）。
- snapshots/・corpus/ の凍結原本は本パックに複製していない（export-policy 規則2）。

## 選定記録

- 選定基準: テーマ「用語の正準化」に適合する1枚を、作成側の観点だけで収載した。
- **`--include-draft`**: status: draft の構成資産を含むため DRAFT 印を付して収載。DRAFT は元資産の
  校正ライフサイクルを示し、Skill の出荷検査や実務妥当性の判定を表さない。
