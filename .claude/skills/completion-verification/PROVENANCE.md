# PROVENANCE — completion-verification

- compiled_at: 2026-09-14
- compose: /loop-compose operation completion-verification（validatedのみ）
- 選定: `docs/proposals/design-development-phase-compose-selection-20260914.md` rev1 開発1。
- 本ファイルとSKILL.mdは資産と選定計画から生成する成果物。資産がSSOTであり、手編集を恒常的な更新経路にしない。
- 再生成条件: 構成資産・Contractの版やstatusが変わったとき。版の差はloop-report、statusを含む整合はcompose gateで確認する。

## compiled 一覧（5列）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-004 | 0.2.0 | validated | authoritative | CT-REF-005 |
| KA-REF-005 | 0.1.0 | validated | authoritative | CT-REF-005 |
| CT-REF-005 | 0.2.0 | validated | N/A | N/A |

CTのsupply_mode・contractはD1受入契約の正規化に従いN/Aとする。

## 資産と本文の対応

| 資産・項目 | 反映先 | 接地と範囲 |
|---|---|---|
| KA-REF-004 K-01/K-04 | 証拠を確かめてから主張する | 現在状態・同一報告内の新規実行。superpowers verification-before-completion L22–25、cc-sdd kiro-verify-completion L59–63。verified/attemptedの区別はcursor anti-sycophancy R17 |
| KA-REF-004 K-02/K-06 | 同節の5手順・照合結果 | superpowers L32–40、cc-sdd L59–65の順序、exit code・失敗数・skipped scope |
| KA-REF-004 K-03/K-05 | 対象を確定する・範囲一致・照合結果 | 主張前の使用場面を示す。全工程の各チェックポイント履歴を単一報告から採点するINVは追加しない |
| KA-REF-005 K-01/K-03 | 主張に合う証拠を選ぶ | superpowers L45–53、cc-sdd L67–95の対応表。lintとbuildを分離。sourceのlinter行も保持 |
| KA-REF-005 K-02 | 委譲の独立確認 | superpowers L105–108、cc-sdd L21/L115。diffを確認し、自己申告を証拠に代用しない |
| KA-REF-005 K-04/K-05 | 修正と要件の行・照合結果 | 元症状と回帰の両方、要件単位の突合。traceability-auditは別packへの引継ぎであり自動実行ではない |
| CT-REF-005 applicable_when / not_applicable_when | 対象を確定する・個別N/A | 完了報告と添付証拠が対象。進捗・早期計画・テスト品質を除外。実行可能な未実行と実行不能を区別 |
| CT-REF-005 INV-01〜08 / DEV-01〜04 / scoring | validation | 全項目・個別N/A・Critical Fail優先・適用平均7.0の判定を保持。Contract本体とverifierは非同梱 |
| 選定計画の合成上の境界 | 提出済み報告の扱い・照合結果 | 追加検証で元の証拠欠落を遡及充足しない。報告適合を権限・工程遷移に拡張しない。新規INV・出力enumではない |

superpowersとcc-sddの接地元はカードに記載された`corpus/seed/completion-verification/`の2原本。
同名内容の凍結コピーは`snapshots/oss/superpowers/verification-before-completion-SKILL.md`と
`snapshots/oss/cc-sdd/kiro-verify-completion-SKILL.md`にあり、今回の入口確認でbyte一致を確認した。
cursorの接地元は`snapshots/oss/cursor/anti-sycophancy-code-discipline-cursorrules-prompt-file.mdc`。
凍結原本・評価ケースはdistへ複製しない。新しいContract評価やcalibrationは実行していない。

## SOの全件記録

| 資産/SO | 状態 | 反映先・範囲または非収載理由 |
|---|---|---|
| KA-REF-004/SO-01 | 非収載 | 固定の成功示唆語彙は禁止リスト化しない。証拠のない完了主張は既存INV-01/DEV-01で扱う |
| KA-REF-004/SO-02 | 非収載 | 言い換え全般へ対象を広げる新規規則は追加しない。契約に従い報告内の完了系主張を照合する |
| KA-REF-004/SO-03 | 非収載 | 合理化への反論表は本パックの照合手順へ追加しない |
| KA-REF-004/SO-04 | 収載 | 早期計画・推測的進捗の除外は、CT-REF-005自身のnot_applicable_whenに吸収済み。その契約を根拠に保持し、新たなSO活性化ではない |
| KA-REF-005/SO-01 | 非収載 | TASK等の固定4分類は導入しない。K-01の対応表で主張を照合する |
| KA-REF-005/SO-02 | 非収載 | FEATURE_GO固有の6要素を必須化しない。主張と証拠の範囲一致を既存契約で確認する |
| KA-REF-005/SO-03 | 非収載 | runtime固有の失敗例・検証ゲートは追加しない。証拠を超える主張は既存INV-03の対象 |

KA-REF-006は非選定。VERIFIED/NOT_VERIFIED/MANUAL_VERIFY_REQUIREDという固定3値形式は
CT-REF-005自身が形式仕様として不採用としている。INV-08の実行不能明示だけを保持する。

## バッジと資産の軸

- draft_badge = false。構成資産・ContractにdraftはないためDRAFTは0件。
- pack_advisory = false。2カードともauthoritativeかつContract接続済みのためADVISORYは0件、原因行も0件。
- KA-REF-004/005: status validated、review_status human-reviewed、evidence_strength community-consensus、volatility stable、review_by null。
- statusは校正ライフサイクルを表し、生成packのD1受入や案件の完了を代替しない。新たな人間承認は記録していない。
- judge一致率・サンプル数などの校正数値は転記していない。

## ライセンス・出荷境界

| 元OSS | ライセンス | 反映元 | NOTICE |
|---|---|---|---|
| obra/superpowers-skills | MIT | KA-REF-004/005、CT-REF-005 | 当該凍結原本に追加NOTICEなし |
| gotalab/cc-sdd | MIT | KA-REF-004/005、CT-REF-005 | 当該凍結原本に追加NOTICEなし |
| PatrickJS/awesome-cursorrules | CC0-1.0 | KA-REF-004 K-01の追加接地 | 当該凍結原本に追加NOTICEなし |

版と原本の保持先は`snapshots/oss/PROVENANCE.md`。SKILL本文は資産から再構成し、snapshots/・corpus/は同梱しない。
未選定の常時読み側・別テーマへの参照は本文へ転写しない。
非選定（BY-SA隔離）: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015。
非選定（BY-SA隔離）: KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038。
内部源泉は非選定。実consumerへの供給・activationは本Composeの範囲外。
