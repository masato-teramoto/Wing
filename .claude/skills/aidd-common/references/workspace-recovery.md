# Windowsのパス長・書込みエラーから既存案件を復旧する

更新方法は、**最新版の配布一式への更新を優先して検討する**。11ファイルだけの部分更新は必須ではない。
案件のコード・成果物・履歴を保存したコピーで、更新時点と再検証の範囲を確認する。

## 最新版一式への更新

1. ホスト・検査コマンド・子プロセスを停止し、`.aidd`・`.claude`・仕様・コード・テスト・旧設定を含む
   案件全体を保存する。短い実パスの操作用コピーを別に作り、初期内容が一致することを確認する。
2. 旧構成の未完了dispatchやhost操作を確認する。元の操作ID・payloadと旧配布物で完結できるなら、
   更新前に完結させる。未完了dispatchの発行時から `command.yaml` / `flow.yaml` / `action.yaml` /
   `gate.yaml` の内容が変わった場合、rebaseは `an old-configuration dispatch is pending` で拒否される。
   この場合は停止し、保存した旧版コピーで
   原因を診断する。状態や操作記録を削除して先へ進めない。

   Claudeの応答終了だけでは、操作が完了したとは判断しない。「承認してください」「回答してください」と
   返して止まった場合も、発行済みの依頼は残り得る。通常は `.aidd/phase-progress.json` の
   `current.pending` に、Skillの結果待ち（`emit`）または人間待ち（`wait`）が記録される。
   旧配布物で結果提出・必要な検査・承認を処理し、次の依頼を発行する前の区切りを確認する。
   Phase 8では対象実行の `execution.json` の `event_complete` 等も確認する。
   案件全体の完成を意味しないが、依頼が無いことだけで安全とも判断せず、host操作・検査の未完了も確認する。

3. 更新する配布物の版を固定し、案件独自の資材・設定変更を比較する。ソースリポジトリから更新する場合は、
   リポジトリのルートで次を実行する。出力先は保存用ではなく操作用コピーに限る。

   ```powershell
   python -X utf8 -B layers/l0_platform_foundation/tool/main_flow_assembly/base/assemble_main_flow.py --output C:/w/project
   python -X utf8 -B layers/l0_platform_foundation/tool/main_flow_assembly/base/assemble_main_flow.py --output C:/w/project --check
   python -X utf8 -B -S C:/w/project/.claude/skills/aidd-common/bin/aidd.py --root C:/w/project validate --json
   ```

   すべて終了コード0であることを確認する。コード・仕様・テスト・旧証跡・利用者所有ファイルの
   更新前後の差分も確認する。配布対象の設定は新版になるため、独自変更を無条件に失わせない。
4. Phase 8を開始済みなら、下記の正規 `implement-rebase` を対象featureごとに実行する。
   旧完了表と実行はhistoryへ残るが、現行計画の完了表は空になり、再検証・再承認が必要になる。
   Phase 1〜7の承認・入力も不整合なら、この手順で解決したと扱わず影響範囲を診断する。
5. 完成済みの実コードを保持して再検証する。GREEN/VERIFYが成功しても、TDDタスクの完了に必要な
   同一実行のRED等が欠ければ完了できない。REDを作るために正常なコードを故意に壊したり、
   検証計画を免除へ書き換えたりしない。正規手順で完了できない場合はそこで停止し、必要な対応を検討する。

一式更新の成功と、更新後のPhase 8完了は別々に確認する。合成案件での成功だけでは、
完成済み実コードを変えない移行・実LLMの判断・実ユーザー承認まで確認したことにはならない。

## リンク経由で開いた案件のパス照合

案件ルートもstateと同じく実パスで扱う。新しい操作記録は両方が同じ基準になり、
案件全体を移した後に元のシンボリックリンク・junctionを残す必要はない。

修正前の記録にリンク側のrootと実パスのstateが混在している場合も、元の場所でリンクとstateから
同じ実体を確認できれば、自動的に照合して同じ操作ID・内容の再送を受け付ける。
このパス表記の違いだけを理由に、追加の移行操作や旧操作の完了を要求しない。
保存済みのrequest・回答・証跡は書き換えず、回答者・dispatch・内容の変更は引き続き拒否する。
外部stateは、同じ場所でリンク表記を解消しても外部の絶対位置との結び付きを保つ。

既にリンク先が失われ、元の対応関係を確認できない混在記録の移動後再開は、修正前からの復旧限界である。
stateのファイル名から案件ルートを推測したり、対応関係を手編集したりしない。
また、このパス照合の互換処理は配布資材のハッシュを互換扱いにするものではない。
上記の一式更新・Phase 8の再検証条件は従来どおり確認する。

## 未完了dispatchのためrebaseを拒否された場合

`an old-configuration dispatch is pending` が出た場合は、次の順で扱う。

1. 更新後の案件はエラー・ログを含めて保存し、操作を止める。
2. 更新前に保存した案件コピーを、当時の配布一式で開く。更新後の状態ファイルだけを旧版へ移植しない。
3. 残っている依頼を通常の手順で処理する。結果提出待ちなら提出と検査を完了し、
   質問・承認待ちなら内容を確認して正規の回答操作を行う。承認が妥当かは利用者が判断する。
4. システム上の完了を確認し、次の依頼を発行する前に停止する。この状態を再度保存してから、
   上記の一式更新と `implement-rebase` をやり直す。

旧版でもエラーが出て操作を完結できない場合は、その原因の復旧を先に行う。
更新前のコピーが無い場合は、使っていた配布版と残存状態を診断してから復旧方法を決める。
最新版の再上書きだけで回避しようとしたり、`pending` の削除・完了フラグの手編集を行ったりしない。
この拒否は旧依頼を新構成で誤処理しないための保護であり、拒否自体が案件破損を示すものではない。

## 局所復旧が必要な場合だけ使う旧版専用候補

旧構成の操作を完結できず、最新版一式への切り替え条件を満たさない場合の候補。
通常の更新にこの11ファイルを事前適用する必要はない。

局所復旧候補の対象は、基点 `206b031976c94fd8473a0a501f458692d6864a09` の原本から合成したalpha3系203資材に
バイト単位で一致し、同じflow定義・Phase 8の状態形式（`flow_contract.schema=3`）を持つ案件コピー。
alpha3.1、PR #16導入済み、独自に配布資材を変更した案件には、この旧版専用候補を適用しない。
復旧修正の適用で実行資材が変わった場合は、履歴と実装コードを残し、Phase 8を正規の手順で
再検証・再承認する。旧資材のハッシュを新資材のハッシュとして扱う互換処理は行わない。

## 再検証する範囲

| 状態 | 対応 |
|---|---|
| 本対応を導入済みで、場所だけを移した | 停止確認と残留markerの復旧後、同じ操作を再試行する |
| 旧版案件へ今回の復旧修正を適用した | `implement-rebase` 後、新しいrequestで対象featureのPhase 8全タスクと最終検査をやり直す |
| 旧形式の公開ハッシュだけが残り、元の公開本文が無いまま移動した | 本文を推測せず、同じくPhase 8をrebaseする |
| Phase 1〜7の承認・入力も不整合、flow定義が異なる、未完了操作を再送できない | この手順では進めない。影響を診断し、局所復旧と広い範囲の再検証を比較してから選択する |

実行資材は案件内で共通なので、既にPhase 8を開始した他featureも再検証が必要になり得る。
依存元featureから順に扱う。Phase 1〜7の承認・入力が有効な案件を、自動的に全工程の移行へ戻さない。
全工程の再検証が必要な場合は、対象工程・保持できる成果物・作業量を利用者と比較検討する。

## 局所復旧の操作順

1. ホスト、検査コマンドと子プロセスを止める。案件全体をバックアップする。
   `.aidd`・`.claude`・コード・成果物・旧設定・操作履歴を含め、元案件は起動しない。
2. 案件全体のコピーを `C:\w\project` など短い**実パス**へ置き、そのコピーで復旧する。
   レジストリ変更は前提としない。feature名・check ID・内部階層も含めて長さを確認する。
   絶対パスを含む検査コマンド、外部設定、仮想環境は移動後にも使えるか確認する。
3. 旧版の場合、コピーへ今回の復旧修正一式を適用する。`command.yaml` / `flow.yaml` /
   `action.yaml` / `gate.yaml`、案件の仕様、検証計画、レビュー規則を同時に変更しない。
   資材は固定PR #25 `43fd3463f1ed99a5d91cdeffc1bbdbefe65d4a1e` から生成した11ファイルに限定する。
   最新の `layers/` から同名ファイルを抜き出すと、旧版にない `human_choices` 等の依存が混ざる。
   リポジトリのルートで、未使用の短い出力先へ候補を生成し、案件コピーを読み取り照合する。

   ```powershell
   python -X utf8 -B tests/regression/main_flow/recovery_assets.py --output C:/w/recovery25
   python -X utf8 -B tests/regression/main_flow/recovery_assets.py --check-project C:/w/project
   ```

   両方が終了コード0で、後者が `base_assets_match: true` の場合だけ次を検討する。
   これは資材の一致確認であり、状態・停止確認・未完了操作・外部依存・実案件受入の代わりではない。
   `recovery-manifest.json` の基点・適用元・11ファイルのSHA256を記録し、候補の同名ファイルを
   操作用コピーだけへ配置する。生成ツール自体は案件を更新しない。元ファイルは保存用コピーに残す。
   `.main-flow-assets.json`、設定、仕様、旧証跡は候補のものへ差し替えない。
   適用対象の実行ファイルは以下のとおり。

   | `.claude/skills/aidd-common/` 以下 | ファイル |
   |---|---|
   | `bin/` | `host.py` |
   | `lib/` | `location_identity.py` |
   | `scripts/` | `aidd_entry.py`, `gate_exchange.py`, `host_session.py`, `implementation_completion.py`, `implementation_tools.py`, `implementation_task_review.py`, `review_gate.py`, `review_operations.py`, `recover_checks.py` |

4. 残留markerを確認する。表示された検査と子プロセスが**すべて停止したことを確認した後**だけ退避する。

   ```powershell
   python -B .claude/skills/aidd-common/scripts/aidd_entry.py recover-checks
   python -B .claude/skills/aidd-common/scripts/aidd_entry.py recover-checks --processes-stopped
   ```

   これは再実行を妨げるmarkerの退避であり、検査を合格扱いにする操作ではない。
   ログ・旧証跡は残る。コマンドの副作用が途中まで適用されていれば、再実行前に確認する。
5. 実行資材を更新した場合は、実際の操作者と理由でfeatureごとに `implement-rebase` を実行する。
   例として `.aidd/recovery-rebase.json` に次を保存する。操作IDはfeatureごとに一意にし、再送時は同じ内容を使う。

   ```json
   {"operation_id":"path-recovery-provider-1","reason":"Windowsのパス長エラー。停止したコピーを短い場所へ移し、復旧修正を適用したためPhase 8を再検証する"}
   ```

   ```powershell
   python -B .claude/skills/aidd-common/scripts/aidd_entry.py /aidd-implement --action implement-gate-run --item provider --actor "実際の操作者名" --payload .aidd/recovery-rebase.json implement-rebase
   ```

   旧完了表・実行・証跡は履歴として残り、対象featureの全タスクが未検証へ戻る。
   コードを削除して作り直す操作ではない。旧requestは無効になり、旧回答で新しい実行を承認できない。
6. 新しい `request_id` で `implement-select` → `implement-next` を行い、通常のPhase 8を続行する。
   タスクの再検証、必要なレビューと実際の人間承認、featureの最終検査を完了する。
   完成済み実コードを故意に壊してREDを作らない。コードを保持した正規の再検証が成立しない場合は
   そこで停止し、必要な手順・変更を検討する。合成fixtureの成功は実コードの無変更移行を証明しない。

局所復旧と最新配布一式への更新は別の段階として扱う。旧構成の未完了dispatch/host操作を
完結できるまで一式更新しない。最新一式へ切り替える際も、コード・成果物・旧証跡の保持と
再検証・再承認範囲を別途確認する。旧承認の資材ハッシュを書き換えて引き継がない。

未完了のhost操作がある場合は、元の操作ID・payloadで再送してからrebaseする。
再送が資材変更や証跡不整合で拒否される場合は、操作履歴の削除や成功印の手入力で解除しない。
停止したコピーを保持して原因と再検証範囲を診断する。全工程の移行は、この手順の自動的な次の処理ではない。
