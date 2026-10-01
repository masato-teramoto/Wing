# PROVENANCE — release-migration-planning

- compiled_at: 2026-09-14 ／ compose: `/loop-compose operation release-migration-planning --include-draft`
- 選定正本: `factory/docs/proposals/design-development-phase-compose-selection-20260914.md` rev2 §2.1「release-migration-planning」。
  利用者の「補強を行う」という指示を、下記SOの選定承認根拠として再生成した。
  この選定をカードの人間レビュー、Contract新設・昇格、SOのContract活性化とは扱わない。
- **本ファイル・SKILL.md はビルド成果物。手編集禁止**（SSOTは `assets/` と選定正本）。

## compiled 一覧（5列）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-034 | 0.1.0 | draft | authoritative | null |

## カード ↔ 節 対応表

| カード | 反映項目 | 反映先 | 接地と具体化の範囲 |
|---|---|---|---|
| KA-REF-034 | K-01 | 入力確認・ロールバック経路と発動条件・自己確認 | `github-copilot/devops-rollout-plan-SKILL.md` L71–75/L110、`cc-sdd/steering-custom-deployment.md` L36–37、`github-copilot/github-actions-ci-cd-best-practices.instructions.md` L427/L489、`spec-kit/checklist.md` L211。安定版、手順、発動基準、復旧後確認、検証状態を記述する |
| KA-REF-034 | K-02 | デプロイ後検証・自己確認 | rollout-plan同 L65–69/L116–117、deployment同 L6/L8/L45–47、CI/CD同 L491/L594–595。観測対象・方法・期待値と失敗時のrollback接続を具体化。固定時間窓は追加しない |
| KA-REF-034 | K-03 | 入力のリスク確認・DB変更と切替の分離・自己確認 | deployment同 L32–33、`cursor/aws-rds.mdc` L224/L226–239/L377、rollout-plan同 L33–35。後方互換、add→backfill→切替、独立migration、切替前検証とgreen read-onlyを保持 |
| KA-REF-034 | K-04 | 戦略選択・自己確認 | deployment同 L7/L24–28、CI/CD同 L400/L408–421/L490、rollout-plan同 L102–106。リスクに応じた戦略と選択理由を記述 |
| KA-REF-034 | K-05 | 本番昇格経路・自己確認 | CI/CD同 L395–397/L401/L487–488、deployment同 L22、rollout-plan同 L48。本番の手動承認・環境保護・監査記録を計画する知識。実行時の新たな承認要求・承認取得・本番操作には転用しない |
| KA-REF-034 | K-06 | 検証環境と昇格順序・自己確認 | CI/CD同 L382–387、deployment同 L12。インフラ・データ・設定・セキュリティを本番へ近づけ、staging検証後に昇格。本番データをstagingへ補充する場合に匿名化する計画・手順を記す意味を保持。実データ操作は行わない |
| KA-REF-034 | SO-01（部分） | 展開の操作順・自己確認 | `github-copilot/devops-rollout-plan-SKILL.md` L59–63のStep-by-Step Rollout部分だけを採用。準備・適用・段階的検証の操作順、コマンドまたは具体的操作、各ステップの検証、所要見積を保持。固定10節テンプレと4分類入力定型は非採用 |
| KA-REF-034 | SO-05 | 全体ロールバックだけでは扱えない故障・自己確認 | rollout-plan同 L91–93。部分故障・性能劣化・データ不整合・依存先障害を対象変更へ当てはめ、該当する各シナリオに症状・対応・対応時機を記す。具体的な復旧方式や固定分数は創作しない |

接地ファイルは `factory/snapshots/oss/` 配下。カードに保持されたK全6項目と選定済みSOを作成手順へ再構成した。
本文の対応表は記入補助であり、新たな固定schemaではない。入力整理・未決事項・未検証と検証済みの区別・
自己確認・引継ぎは、選定した知識と選定正本の作成範囲に基づく。
ロールバック不能や手順未検証を確認済みと扱わず不足として引き継ぐが、未接地の復旧方式を創作しない。

## SO 選定状態（全7項目）

| SO-ID | 状態 | 反映先・適用条件・非収載理由 |
|---|---|---|
| SO-01 | 条件付き収載 | 部分採用。本文「展開を操作順に分解する」・自己確認へ、Step-by-Step Rolloutの操作順、各ステップのコマンドまたは操作・検証・所要見積だけを反映。デプロイ・移行・切替の操作を計画に含める場合に適用する。固定10節テンプレ・4分類入力定型は非採用。操作の記述を実行許可と扱わない |
| SO-02 | 非収載 | デプロイ後検証の4時間相と固定分数を追加しない |
| SO-03 | 非収載 | 自動rollback機構、runbook定期レビュー、非本番での診断、事後分析の手順を追加しない。K-01/K-02の復旧手順と発動条件は保持 |
| SO-04 | 非収載 | 通知時系列・stakeholder matrix・曜日や変更窓の慣行を採用しない |
| SO-05 | 条件付き収載 | 本文「全体ロールバックだけでは扱えない故障を整理する」・自己確認。対象変更・構成に関係する部分故障・性能劣化・データ不整合・依存先障害へ適用し、症状・対応・対応時機と順序を記す。該当しないシナリオは理由を残す。固定の時間や復旧方式は課さない |
| SO-06 | 非収載 | breaking changeの移行ガイド定型・before/after例・upgrade checklistを追加しない |
| SO-07 | 非収載 | デプロイ失敗時のログ・設定・依存・ネットワークの診断順序は追加しない |

選定したSOは本文全体と同じSHOULD相当の静的な作成助言であり、Contract活性化ではない。
authoring単一発動とし、review切替・共通dispatch・runtime selector・project profile読取りを追加していない。

## 属性・バッジ・検証経路

| id | status | review_status | supply_mode | contract | evidence_strength | volatility / review_by | risk_if_wrong |
|---|---|---|---|---|---|---|---|
| KA-REF-034 | draft | 未記載（schema既定: unreviewed） | authoritative | null | community-consensus | volatile / 2027-02-22 | high |

- `DRAFT = true`。host Contractによる校正済み状態にはなく、judge実行有無や人間レビュー状態は表さない。
- `ADVISORY = true`。原因はKA-REF-034のauthoritative × contract:null。全項をSHOULD相当とし、原因資産1行を記載。
- Contract未接続のため正式なINV/DEVチェックリスト・採点・合否・工程遷移ゲートは生成しない。
  本文の自己確認はKと選定済みSOに由来する作成者向け照合。K-05の本番保護ゲートは対象案件の計画内容であり、Composeの
  新ゲートでも、このpackを使うための新たな承認要求でもない。案件で明示された制約は維持する。
- 構成・出荷検査、独立内容確認、D1 receiptの成立はそれぞれ別に記録する。本ファイルは完了証跡を代替しない。
- 実質の接地はcopilotとcc-sddが中心。spec-kitはrollback要件の1項、cursorは切替規律の補強であり、
  4ツールが全項目に等しく合意したとは扱わない。校正の一致率など評価数値は転記していない。

## 不足と境界

- 元カードはdual-write期間、cutover窓の運用、移行前後のrow count／checksum照合の供給が薄いと明記する。
  本文は後方互換・分離・切替前検証の骨格までとし、詳細な移行設計は依頼元へ引き継ぐ。
- 固定10節、時間窓、T-24h、AWS製品固有の設定は転写しない。K-03が保持するBlue/Greenの切替規律は残す。
- CI構造・権限・サプライチェーン統制、データモデルとスキーマ版管理は別テーマ。タスク分割・受入レビューは
  既存packへ引き継ぎ、本文を複製しない。新しい承認取得・デプロイ実行の能力を持つとは記さない。

## 元 OSS ライセンス（帰属・NOTICE）

| カード | 上流・凍結LICENSE | ライセンス・帰属 | NOTICE | 互換判定 |
|---|---|---|---|---|
| KA-REF-034 | github/awesome-copilot — `github-copilot/LICENSE-github-copilot.txt` | MIT / Copyright GitHub, Inc. | 凍結収録範囲になし | 互換 |
| KA-REF-034 | gotalab/cc-sdd — `cc-sdd/LICENSE-cc-sdd.txt` | MIT / Copyright (c) 2025 gotalab | 凍結収録範囲になし | 互換 |
| KA-REF-034 | github/spec-kit — `spec-kit/LICENSE-spec-kit.txt` | MIT / Copyright GitHub, Inc. | 凍結収録範囲になし | 互換 |
| KA-REF-034 | sanjeed5/awesome-cursor-rules-mdc aws-rds — `cursor/LICENSE-awesome-cursor-rules-mdc-cc0.txt` | CC0 1.0 Universal | 凍結収録範囲になし | 互換 |

版固定は `factory/snapshots/oss/PROVENANCE.md`（カード記載: collected 2026-07-02 / frozen 2026-07-08）。
転記すべきNOTICE本文は確認した凍結範囲に存在しない。snapshots/・corpus/の複製は含めない。

- 非選定（BY-SA隔離）: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015
- 非選定（BY-SA隔離）: KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038
- 非選定（内部源泉・今回の出荷範囲外）: KA-REF-056, KA-REF-057, KA-REF-058, KA-REF-059

隔離対象の本文・ID参照をSKILLへ転写していない。隔離解除はexport-policyの所定手続による。

## 再コンパイル条件

構成資産のversion・status・供給属性または選定規則が変わったら再生成する。
版の差分は /loop-report、statusを含む依存整合はcompose gateで確認する。元資産は変更していない。
