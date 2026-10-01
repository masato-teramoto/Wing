# PROVENANCE — api-contract-design

- compiled_at: 2026-09-14 ／ compose: `/loop-compose operation api-contract-design --include-draft`
- 選定正本: `factory/docs/proposals/design-development-phase-compose-selection-20260914.md` rev2 §2.1「api-contract-design」。
  利用者の「補強を行う」という指示を、下記SOの選定承認根拠として再生成した。
  この選定をカードの人間レビュー、Contract新設・昇格、SOのContract活性化とは扱わない。
- 実務補正: `factory/docs/assessments/skills-practicality-review-20260914.md` F02と利用者の修正承認に基づき、
  KA-REF-028を0.2.0へ更新して再生成した。SO-01のHTTP再試行判断を一次RFCへ再接地し、選定済みSOの範囲を維持した。
- **本ファイル・SKILL.md はビルド成果物。手編集禁止**（SSOTは `assets/` と選定正本）。

## compiled 一覧（5列）

| id | compiled_version | compiled_status | compiled_supply_mode | compiled_contract |
|---|---|---|---|---|
| KA-REF-028 | 0.2.0 | draft | authoritative | null |

## カード ↔ 節 対応表

| カード | 反映項目 | 反映先 | 接地と具体化の範囲 |
|---|---|---|---|
| KA-REF-028 | K-01 | 入力確認・操作ごとの入出力と条件・自己確認 | `cc-sdd/specs-design-template.md` L182–195、`steering-custom-api-standards.md` L7、`github-copilot/aspnet-rest-apis.instructions.md` L75、`openai-codex/cli-creator/SKILL.md` L50/L68。Request/Response/Errors、事前・事後・不変条件を操作単位に記述する |
| KA-REF-028 | K-02 | エラーの共通形式・自己確認 | `cc-sdd/steering-custom-error-handling.md` L16–27、copilot同 L68–69、cli-creator同 L68。安定したコードの許容列挙集合（enum）・人間可読説明・追跡情報・秘密非含有を保持し、各操作のコードと集合を照合する。固定コード値・JSON形は転写しない |
| KA-REF-028 | K-03 | 認証と認可・自己確認 | `cc-sdd/steering-custom-api-standards.md` L8/L54、`steering-custom-authentication.md` L6–14/L41–44、copilot同 L55–61、cli-creator同 L72–78。方式と理由、認証と認可の分離、最小権限・fail closed、入口とdomainでの強制位置を記述側に限定 |
| KA-REF-028 | K-04 | バージョンと互換性・自己確認 | `cc-sdd/steering-custom-api-standards.md` L56–60、copilot同 L71–77。変更前後を照合し、新版・廃止周知期間の扱いを明文化 |
| KA-REF-028 | K-05 | 一覧・検索応答・自己確認 | `cc-sdd/steering-custom-api-standards.md` L62–66、cli-creator同 L61。ページ方式・上限または既定値・応答メタデータ・提供するフィルタとソートを記述 |
| KA-REF-028 | SO-01 | 再試行と冪等性・自己確認 | RFC 9110 §9.2.2/§10.2.3/§15.5.9、RFC 6585 §4。失敗条件と再送の安全性を分け、408・429・一般の4xx、クライアントとプロキシ、Retry-Afterを条件別に記述する。キーは採用APIの重複防止契約へ限定。`cc-sdd/steering-custom-error-handling.md` L49–52のbackoff・揺らぎ・有限上限は設計助言として区別し、旧版の4xx全面禁止とキー一律必須を置換した |
| KA-REF-028 | SO-02 | HTTPエラーの分類と応答・自己確認 | error-handling同 L10–14、`steering-custom-api-standards.md` L43–47。入力・業務・システム・外部の4分類と4xx/5xxの対応を保持。外部障害は文脈で選び、具体的なステータス値・フィールド名は固定しない |
| KA-REF-028 | SO-03 | 層をまたぐエラーの変換責任・自己確認 | error-handling同 L29–33。APIの応答変換、型付き業務エラー、providerエラーの安全なラップ、未知エラーの共通処理を保持。HTTPの扱いはHTTP APIへ限定し、層・型名・frameworkを新設する指示にはしない |

OSSの接地ファイルは `factory/snapshots/oss/` 配下。一次RFCの追加凍結は下記「一次標準の参照と権利」を参照。
上記はカードに保持された全Kと選定済みSOの再構成であり、
凍結原本の未収穫部分を追加採用していない。本文の対応表は記入補助で、新たな固定schemaではない。
入力確認・未決事項の分離・自己確認・引継ぎは選定正本の作成範囲に沿う適用手順であり、新しいINV/DEVではない。

## SO 選定状態（全8項目）

| SO-ID | 状態 | 反映先・適用条件・非収載理由 |
|---|---|---|
| SO-01 | 条件付き収載 | 本文「再試行と冪等性を対にして記述する」・自己確認。ネットワーク越しの呼出しで再試行を検討する操作に適用し、採用可否を含める。HTTPでは408・429などの条件、client/proxyの違い、再送の安全性、Retry-After、待機・打切りを記す。キーは採用時の重複防止契約へ限定し、全操作へ強制しない。非HTTPへHTTP条件を課さず、固定回数・時間・実装方式は課さない |
| SO-02 | 条件付き収載 | 本文「HTTPエラーを分類して応答へ対応づける」・自己確認。HTTP APIのエラー応答を設計する場合に、4分類を4xx/5xxと共通形式へ対応づける。非HTTPのサービスI/FへHTTPを強制せず、固定ステータス値は課さない |
| SO-03 | 条件付き収載 | 本文「層をまたぐエラーの変換責任を記す」・自己確認。API・業務サービス・データ/外部接続の対応する境界がある場合に、実在する境界の変換責任と未知エラー処理を記す。新しい層やframeworkを一律導入しない |
| SO-04 | 非収載 | ログの項目・禁止項目・レベル語彙は追加しない。K-02のエラー応答の秘密非含有のみ保持 |
| SO-05 | 非収載 | 監視・ヘルスエンドポイントの契約欄や固定パスは追加しない |
| SO-06 | 非収載 | Service/API/Event/Batch/Stateの選択様式と型別の追加欄は採用しない。K-01が保持するサービス/APIの入出力と条件のみ反映 |
| SO-07 | 非収載 | CLI固有のコマンド分離、doctor、書込みの可視性はCLI設計テーマに分ける |
| SO-08 | 非収載 | token/sessionの保存・期限・refresh・失効スロットは追加しない |

選定したSOは本文全体と同じSHOULD相当の静的な作成助言であり、Contract活性化ではない。
authoring単一発動とし、review切替・共通dispatch・runtime selector・project profile読取りを追加していない。

## 属性・バッジ・検証経路

| id | status | review_status | supply_mode | contract | evidence_strength | volatility / review_by |
|---|---|---|---|---|---|---|
| KA-REF-028 | draft | 未記載（schema既定: unreviewed） | authoritative | null | community-consensus | volatile / 2027-01-11 |

- `DRAFT = true`。host Contractによる校正済み状態にはなく、judge実行有無や人間レビュー状態は表さない。
- `ADVISORY = true`。原因はKA-REF-028のauthoritative × contract:null。全項をSHOULD相当とし、原因資産1行を記載。
- Contract未接続のため正式なINV/DEVチェックリスト・採点・合否・工程遷移ゲートは生成しない。
  本文の自己確認はKと選定済みSOに由来する作成者向け照合。構成・出荷検査、独立内容確認、D1 receiptの成立はそれぞれ別に記録する。
  本ファイルはこれらの完了証跡を代替しない。
- 実質の接地はcc-sddに偏り、copilotは横断部だけ、cli-creatorは隣接参考である。単一ツール内の複数文書を
  複数独立ツールとして数えない。校正の一致率など評価数値は転記していない。

## 不足と境界

- タイムアウト値・SLOをI/F契約に明記する様式は、元カード自身が供給不足と明示する。監視側のSLI言及を
  契約側の根拠へ代用せず、本文では案件要件への引継ぎと推測補完の回避に留める。
- エラー分類と4xx/5xxの関係を保持し、408・429は一次標準が定義する意味と再試行条件を記す。
  案件固有のエラーコード、JSONフィールド名、ページ用パラメータ名、認証ヘッダ、ヘルスパス、回数・時間は
  固定せず案件で決める。キーの重複防止契約は再送の安全性を具体化する設計上の推論であり、RFCによる
  全API共通のキー規格や必須化ではない。
- K-03は認証・認可の契約記述に限定。隔離された実装規律への参照を転写しない。要求の記述、実装計画、
  被覆監査、受入レビューの本文を複製せず、必要な成果物を既存packまたは依頼元へ引き継ぐ。

## 元 OSS ライセンス（帰属・NOTICE）

| カード | 上流・凍結LICENSE | ライセンス・帰属 | NOTICE | 互換判定 |
|---|---|---|---|---|
| KA-REF-028 | gotalab/cc-sdd — `cc-sdd/LICENSE-cc-sdd.txt` | MIT / Copyright (c) 2025 gotalab | 凍結収録範囲になし | 互換 |
| KA-REF-028 | github/awesome-copilot — `github-copilot/LICENSE-github-copilot.txt` | MIT / Copyright GitHub, Inc. | 凍結収録範囲になし | 互換 |
| KA-REF-028 | openai/skills cli-creator — `openai-codex/cli-creator/LICENSE.txt` | Apache-2.0。Kの隣接参考として使用 | skill凍結ディレクトリにNOTICEなし | 互換 |

OSSの版固定は `factory/snapshots/oss/PROVENANCE.md`（カード記載: collected 2026-07-02 / frozen 2026-07-07）。
転記すべきNOTICE本文は確認したOSS凍結範囲に存在しない。snapshots/・corpus/の複製は含めない。

## 一次標準の参照と権利

| 一次資料 | 使用箇所 | 追加凍結・権利 |
|---|---|---|
| [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)（2022-06） | §9.2.2、§10.2.3、§15.5.9 | `factory/snapshots/standards/ietf/rfc9110/2022-06/`。原文・IETF TLP 5全文・取得証跡を保存 |
| [RFC 6585 — Additional HTTP Status Codes](https://www.rfc-editor.org/rfc/rfc6585.html)（2012-04） | §4 | `factory/snapshots/standards/ietf/rfc6585/2012-04/`。原文・IETF TLP 4全文・取得証跡を保存 |

RFCは機能的な意味を独立要約して参照し、原文やライセンス文書を本パックへ複製していない。
IETF Trust・原著者の著作権、BCP 78と適用TLPに関する原文の通知は凍結原本に保持した。
RFC本文全体をMIT/Apache/BSDとして扱わない。Code Componentsに関するBSD条項と文書本文の権利を区別する。
各凍結のPROVENANCEに出典、SHA-256、実取得時刻と作業日を記録し、既存snapshotは変更していない。
一次標準の追加をOSSの独立ツール数や校正・人間レビューの追加として数えていない。

- 非選定（BY-SA隔離）: KA-REF-003, KA-REF-011, KA-REF-012, KA-REF-013, KA-REF-014, KA-REF-015
- 非選定（BY-SA隔離）: KA-REF-016, KA-REF-017, KA-REF-032, KA-REF-033, KA-REF-037, KA-REF-038
- 非選定（内部源泉・今回の出荷範囲外）: KA-REF-056, KA-REF-057, KA-REF-058, KA-REF-059

隔離対象の本文・ID参照をSKILLへ転写していない。隔離解除はexport-policyの所定手続による。

## 再コンパイル条件

構成資産のversion・status・供給属性または選定規則が変わったら再生成する。
版の差分は /loop-report、statusを含む依存整合はcompose gateで確認する。今回の元資産の意味変更は上記0.2.0に記録した。
