# 生成／修正 Skill の共通契約

この契約は成果物を作る Skill のためのもの。進捗・差戻し・承認の規則は独立した L3 進行制御が持ち、実行仲介は L0 が行う。

## event と Skill

Phase 1–7 は生成 event `<base>-generate` と修正 event `<base>-revise` を持つ。修正 event は毎回、生成 event の直後に実行される。
Phase 8 は [実装契約](../implementation/contract.md) に従い、タスク1件ごとの生成と、選択されたタスクの修正を実行する。

| base | 生成 Skill（`<base>-generate`） | 修正 Skill（`<base>-revise`） |
|---|---|---|
| `requirement-intake` | requirement-intake | intake-revision |
| `steering-authoring` | steering-authoring | steering-revision |
| `feature-decomposition` | feature-decomposition | feature-revision |
| `requirements-authoring` | requirements-authoring | requirements-revision |
| `design-authoring` | design-authoring | design-revision |
| `docs-integration` | docs-integration | docs-revision |
| `tasks-authoring` | tasks-authoring | tasks-revision |

## 共通規則

- ホストが解決した event / item / targets / authoring_inputs / 質問回答 / 修正要求（repair）を受け取る。入力・対象が欠ける、別の所有物を指す、必要入力がapprovedでない場合はfailedで返す。RFPだけは自由形式でstatusを要求しない。
- 実行時に対象のL1テンプレートと該当する作成規則を読む。steering は全工程で一式（全文）を読み、該当章だけを選んで読まない。入力は `paths.md` §6 と解決後の一覧に従い、ゲート記録・phase-progress・docs（Phase 7）を生成の根拠にしない。
- 生成は未作成または同じ作業のdraftへの再入。review/approvedの既存文書を生成Skillで変更しない。
- ファイルの存在や質問0件だけを完了条件にしない。必要な対象・項目が揃い、受け取った回答を反映し、根拠のない必須値が残っていないことを確認する。
- 根拠のない値を書かない。上流成果物や人間の実回答に根拠が無い、または判断に迷う値は推測で補完せず質問として返す。
- tasksの実装メモにある3つの実績用スロットだけは着手時に空でよく、未記入数・質問から除外する。具体的な名前と範囲はauthoring/tasks.mdを参照し、他工程・計画本文へこの例外を広げない。
- phase-progress、features JSON、ゲート記録、上流statusを編集しない。ゲート起動、承認依頼、差戻し確定、別featureの実行を行わない。

## プレースホルダー

- 記入前に `.claude/skills/aidd-common/references/status-protocol.md` §7 を読む。判定・可変個数・不要理由・テンプレート由来の注記の扱いは同節を正とする。
- `<UPPER_SNAKE>` は人間の値（壁打ちの実回答で埋める）、`{{UPPER_SNAKE}}` は上流と実行時情報から導く値。`{{...}}` は導出元が上流に無い場合だけ質問する。
- どちらの系統も削除しない。埋める必要がないものは、人間が明記した不要理由を添えて保持する。省略できるのはテンプレートが任意と明示したセクションだけ。回答が得られない欄はプレースホルダーを残したまま（削除も空欄化もせず）返す。
- `TBD` / `未定` / `_(未記入)_` はプレースホルダーではない。テンプレート由来ならそのまま残してよいが、記入欄へ新たに書き込まない（根拠のない値と同じ扱い）。

## 停止して返す場面

次に当たれば作業を進めず、編集で吸収せずにホストへ返す。

- 上流が approved でない、入力・対象が欠ける → failed。
- テンプレートを埋める根拠が上流・回答に無い → questions を付けて waiting。
- テンプレートと実成果物（既存の自成果物・上流成果物）のあいだで前提が矛盾している → 推測でどちらかへ寄せず、両方の位置と矛盾点を questions または return_candidates に示して waiting。
- 不備の所在の判断が必要 → 当該工程内の修正を既定とする。上流を疑う前に、自成果物の記述と自工程の質問で解消できないかを先に確認し、解消できない場合だけ return_candidates を返す。
- 新規要求と思われる内容（どの既存要求の詳細化でもないもの）が下流で出た → 要求一覧を編集せず、所有工程 intake（`.aidd/requirement-list.md`）への return_candidates として waiting。Phase 1 で確定・追記・再承認されるまで自成果物に採用しない。
- 上流契約・設計の不足 → その所有工程への return_candidates として waiting。その工程で新たに決める質問にすり替えない。

## 質問・差戻し候補の粒度

ホストが人間に提示できるよう、対象パスに加えて次の単位を明示する。
複数の未記入欄を一つの質問にまとめても、各位置と未確定事項を省略しない。

| 工程 | 提示単位 |
|---|---|
| intake | 要求ID。採番前の受入確認は RFP の出典位置・確認論点を示す |
| steering | ファイル × セクション。上位の未確定事項を先に扱う |
| feature | 要求ID。優先度の質問では、順序が決まらない feature 同士を明示する |
| requirements / design | feature × セクション。該当する要件ID・AC・公開契約も示す |
| docs | エンティティ名・業務コード名などの要素。競合する design と各形状を併記する |
| tasks | タスク番号 × セクション。設計不足なら対応する design、検証不能な AC なら requirements への差戻し候補とする |

- 根拠不足は安定した質問ID、対象パス、位置、質問、未回答理由を返す。推測した回答を選択肢にしない。未回答を完成・成功とみなさない。回答後は同じdraftと質問IDから再入する。
- return_candidates の各要素は `owner`（所有工程: intake / steering / feature / requirements / design / docs / tasks、RFP 自体なら `rfp`）、`target`（対象パス）、`location`（不足位置）、`reason`（根拠）を持つ。実際の差戻しは人間とホストに委ねる。
- 上流の修正を要する return_candidates は、質問への回答だけで解消扱いにしない。再入時は所有者が修正・再承認した上流の実内容で判定し直す。

## 修正 Skill（`<base>-revise`）

修正 event は修正対象が無くても毎回実行される。修正要求（repair）は次のいずれか。

| 種別 | 内容 | changed_findings |
|---|---|---|
| 修正対象なし | repair が null・空、または targets が0件 | `[]` |
| ゲート指摘由来 | findings の各要素が phase / scope / run / number / instruction を持つ | 選択された指摘の phase / scope / run / number を過不足なく |
| 指摘なしの人間指示 | origin（plan-change / reopen / rfp-change / edited-outside-flow / rollback-from-downstream 等）と instruction を持ち、findings は空 | `[]` |

- 修正対象なしならどのファイルも編集せず、次の JSON だけを返す。失敗や待機にしない。

  ```json
  {"status":"completed","targets":[],"questions":[],"open_placeholders":0,"changed_findings":[],"return_candidates":[],"summary":"修正対象 0 件"}
  ```

- 修正対象があれば、編集前に指定対象がすべて存在し、L3 進行制御によってdraftに戻されていることを確認する。対象欠落・draft以外の対象・修正指示（instruction）の欠落があれば何も変更せずfailedで返す。draftへの引下げはL3進行制御が行う。
- 指定された自分のdraftだけを、修正指示に関係する箇所だけ修正する。下流ファイルや指定外の対象を編集しない。既存の履歴（廃止済み要求・改版の記録など）を消さず、プレースホルダーを削除しない。
- 修正Skillはstatusを変更せず、他のSkillを起動しない。質問への回答後は同じdraftへ再入する。

## 戻り値

ホストへJSONで返す。出力先へ勝手に別の結果ファイルを作らない。

```json
{"status":"completed","targets":[],"questions":[],"open_placeholders":0,"changed_findings":[],"return_candidates":[],"summary":""}
```

statusはcompleted / waiting / failed。targetsには実際に扱った自分の対象、questionsには未回答質問、changed_findingsには修正した指摘キー（phase / scope / run / number。生成と指摘なしの修正では `[]`）、return_candidatesには上流の不足と根拠を記す。completed時は全対象がdraftで、未回答の必須質問と差戻し候補が無いこと。修正済みの報告は指摘の解消・承認を意味しない。ホストが再検査と人間確認を行う。summaryには工程固有の自己診断結果（design の要件トレーサビリティ等）も記す。

`open_placeholders` は今回の対象に残る `<UPPER_SNAKE>` の未記入欄のうち、
人間の不要理由が明記されていない数を、記入位置ごとに数えた非負整数とする。
`{{...}}`、小文字を含む山括弧、テンプレート由来の注記は含めない。
未作成の必須対象も、そのテンプレートから必要な未記入欄を確認する。
数えられない入力欠落・読取り失敗では `failed` と `open_placeholders: null` を返す。
null は failed の場合だけ許され、未確認を0件の完成扱いにしない。
質問数とは独立した値であり、質問1件が複数欄を扱う場合や、プレースホルダーのない
設計判断を質問する場合がある。未記入箇所は `questions` または `return_candidates` の
位置情報から辿れるようにする。`completed` には0が必要だが、0だけで完成とは判断しない。
回答を受け取っただけで減算せず、成果物へ反映した後に数え直す。
保存・待機管理は L3 ホストが行い、Skill が状態ストアを直接更新しない。
