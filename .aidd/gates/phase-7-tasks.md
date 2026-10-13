---
format_version: 2
phase: tasks
created_at: 2026-10-09T23:31:46+09:00
---

# ゲート記録

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 2026-10-09T23:31:46+09:00 | ①② | ["specs/application-status-search/tasks.md"] | {"specs/application-status-search/tasks.md":"afa2de5e7a5a68130f521be7e70f213ed05dd075bd087cf90020e023a9dd8a59"} | 8 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | steering-conformance | 業務の欠落・矛盾 | 重大 | 4ef3d89000cc105a | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | WTG以外への波及 | タスク13がWTG以外のWiNG画面も改修し、steeringの改修対象外に反する | 違反。タスク13は common/header.html（WTG 以外を含む 32 のテンプレートが common_header を呼ぶ。実在を Grep で確認）、menu.html、error.html を画面設計書に合わせて改修するため、WTG 以外の WiNG 画面の表示が変わる。steering/product.md「位置づけ」は「改修対象は契約・管財管理（WTG）だけ」、同「対象外」は「WTG 以外の WiNG 機能は改修しない」（REQ-003）と定める。タスク13の注記は「人が Q-TK-AS-003 で A（…WTG 以外への波及を上流で許容する）を選んだ」とするが、質問の選択肢 A の文言は「既存 wing の共通ヘッダ・メニュー・エラー画面を、画面設計書に合わせて確認・改修する」で、WTG 以外への波及の許容も steering の例外化も含まない。注記は矛盾を自ら認めているが、steering 側は変更されていない。影響は、メニューのお知らせ欄・WTL 対応期限情報（menu.html の information、wtlTaiouLimitInfo）を置かない改修や、error.html の戻る(C) ボタンの削除にも及ぶ（いずれも WTG 以外の画面で使われる）。なお design.md・requirements.md が approved の上流で、本件の原因は上流（steering と画面設計書の食い違い）にあるため、差戻し候補として記す（下流の docs も再集約の対象になりうる）。 | 次のどれかを人が決める。(a) steering/product.md に共通ヘッダ・メニュー・エラー画面を改修対象に含める例外を明記する（Phase 2 の steering 変更）。(b) タスク13を WTG の機能配下に画面を新設する方式（質問 Q-TK-AS-003 の B）に改める。(c) 既存の共通シェルは変えず、画面設計書との差分を上流へ戻す（同 C）。決まるまでタスク13の注記の「許容を選んだ」の記述は、事実（選択肢 A の文言）に合わせて直す。 | 質問：steering の例外化か方式の選び直しかは業務の判断で、tasks だけでは決められない | 確認済み |  |  |
| 2 | steering-conformance | 業務のあいまい・不足 | 要判断 | 9fa18510a37b1fc0 | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | LOGOUT 無効表示 | タスク13にLOGOUT無効化でWiNG全体のログアウト導線が消える影響の明記なし | タスク13の本文は「画面設計書に合わせる内容」の中で「LOGOUT は全画面で無効表示」と書くだけで、既存 WiNG 全体でヘッダのリンク「LOG OUT」（common/header.html の Logout_lbl。/logout へ送信）が効かなくなることを、本文にも完了条件にも明示していない。事実：header.html は WTG 以外を含む 32 のテンプレートが共通で呼ぶ。現状の [TOP MENU]・[LOG OUT] も画面設計書どおりに直す対象に含まれる。完了条件は「ヘッダのリンクの有効・無効の表示が画面マップ §3 と §4-1 の表と一致する」だけで、LOGOUT を無効にした結果の確認がない。steering/security.md はログアウト（LogoutController）をセッションの失効トリガとしており、利用者がヘッダからログアウトできなくなる影響は、波及の注記（WTG 以外への波及）にも書かれていない。上流の根拠は画面マップ §3 ④・§6-2 #4（行き先のログイン画面が本案件の画面に無いため無効表示）。同じ箇所に steering の改修対象の指摘（#1）があるが、原因が別（ログアウト導線の消失）のため分けた。 | 質問：次を決めて本文と完了条件に書く。(a) 画面設計書どおり LOGOUT を全画面で無効にし、WiNG 全体でヘッダからログアウトできなくなることを注記に明記して完了条件に含める。(b) LOGOUT は有効のまま残し、画面設計書（画面マップ §4-1）の改訂を上流へ回す。 | 質問：ログアウト導線を無効にするかは業務・運用の判断が要る | 確認済み |  |  |
| 3 | traceability | 業務のあいまい・不足 | 要判断 | 2a2ae099e2a4c8f6 | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | メニュー項目の作り | タスク13のメニューが動的menuListか固定2項目か未決で実装手段が不明 | 意味判定：design・画面設計書の内容がタスクで満たせる形になっていない。タスク13は「メニュー項目はメニュー情報から menuList として渡る作りで、テンプレートだけでは項目の中身を決めない」と書く一方、「入口のリンクは権限で出し分けず、全項目を表示する」「ナビ項目は『物件基本情報登録変更』は無効表示、『物件契約情報申請状況検索/一覧』は /wtg060 へのリンク」とも書く。実コードでは MenuController が menuService.getChildMenuList で階層メニューを組み、権限は ZMENUAUTH 側で決まる（ソースで確認）。画面設計書（_app-shell/screen-spec.md §3-1-3）は見出し「契約・管財管理」と 2 項目の固定の一覧だけを定める。固定の 2 項目に置き換えるのか、既存の動的な menuList の上で表示を合わせるのか（その場合、無効表示の項目や出し分けなしをどう実現するのか）が書かれておらず、完了条件（レンダリングの件数と遷移先 /wtg060）では判定できない。他の WiNG 機能のメニューが消えるかどうかも読み取れない。 | 質問：入口画面の項目を (a) 画面設計書のとおり固定 2 項目にする（他機能のメニュー表示が無くなることを明記する）、(b) 既存の menuList を残し、契約・管財管理の部分だけ合わせる、のどちらにするかを決め、タスク13の本文と完了条件に書く。 | 質問：既存メニューの動的な作りと画面設計書の固定表示の食い違いは、人が選ぶ必要がある | 確認済み |  |  |
| 4 | traceability | 業務のあいまい・不足 | 要判断 | ece52c9e5eae1acd | 79f2ea1e04c3d861 | specs/application-status-search/tasks.md § 但し書き（未決のまま残す事項） / 16 | 全文のツールチップ | designの切り詰め値の全文ツールチップがタスク16で範囲外のまま | design.md は「長い値は表示バイト数で切り、ツールチップで全部を出す（基地局名 16・案件小グループ 15・起案会社名 22・エリア 15・起案担当者 10）」と定め、コンポーネント一覧のテンプレートにも「ツールチップ」を含める。画面設計書 §3-1-5「長文」の状態も「ポインタを載せるとツールチップで全文」とする。STYLEGUIDE-backlog.md SGB-17 は人が「design.md に従う（器を足す）」と判断済みで、器が未整備なだけである。一方、tasks.md の但し書きとタスク16は「切り詰めた値の全文を出すツールチップ」を部品が無いため描かず、完了条件にも含めないとしている。タスク10は切り詰め値と全文の両方を持たせるが、全文を画面に出すタスクは無い。結果として design の要素（2.1 の値の欠落を防ぐ全文表示）がどのタスクにも割り当てられない。範囲外にするのは人の指示（スコープ外）によるが、design.md との差は tasks にも design にも判断として残っていない。 | 質問：次のどれかにして、タスク16の本文・完了条件か design の扱いに反映する。(a) 器が整備されるまで全文表示を保留する旨を、design.md の変更管理で扱う判断として決定ログに残す。(b) タスク16に、全文を title 属性など既存の手段で出す範囲を足す。(c) SGB-17 の器の整備を待ってタスク16を着手させる。 | 質問：design の要素を範囲外にする判断が文書として残っていないため | 確認済み |  |  |
| 5 | traceability | 文書間の参照 | 軽微 | 354b5c49ce49d7fa | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | Boundary と Design の参照 | タスク13のBoundaryとDesignがdesign.mdのコンポーネント一覧に無い | 早見表は「_Boundary: …_ はdesign.md の ### コンポーネント一覧（Summary）にある名前」と定める。タスク13の Boundary は「_app-shell（共通シェル・入口・システムエラー。design.md のコンポーネント一覧に無い共通部…）」で、design.md の Summary に無い名前を書いている。_Design: ## コンポーネントとインターフェース_ も、その節に _app-shell の記述が無い（design.md は WiNG の共通ヘッダ・メニュー・エラー画面を扱わない。擬似 feature の _app-shell は design.md を持たない）。本タスクの実装先は人の回答 Q-TK-AS-003 A で決まっているため、実装先そのものは問わない。参照が切れていることだけを指す。 | _Boundary_ に書ける名前を置くか（design.md への追加が要る）、早見表の規約の例外として tasks.md の前提節に「_app-shell の Boundary は画面マップ §4 と _app-shell/screen-spec.md を根拠とし、design.md の Summary に無い」と明記する。 | 修正：参照先の書き方を前提節に明記する（修正案のとおり） | 確認済み |  |  |
| 6 | traceability | 業務のあいまい・不足 | 要判断 | 0ea9acf79f7430f6 | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | UI タスクのテスト先行 | タスク13・16にテスト先行とREDの記述が無く、13はgit diff条件と矛盾 | タスク13・16は通常の機能実装（テンプレートの改修・新規作成）だが、本文・完了条件に、対応する JUnit を先に作ること、意図した失敗（RED）の確認、実装、成功確認（GREEN）が同一タスクで完結する書き方が無い。タスク16の完了条件は「各状態のモデルを与えた出力を JUnit で確認し、11 件とも成功する」、タスク13は「各状態の出力を JUnit で確認し、2 件とも成功する」で、JUnit を作るのか既存のものを使うのかも不明。他のタスク（2〜12・14・15）は「同一タスク内の RED から GREEN を確認し」と書いていて、構成が揃っていない。さらにタスク13の完了条件「git diff --stat の変更ファイルが上の実装先に挙げたファイルだけである」は、JUnit のテストファイルの新規追加（上の実装先に挙げていない）と両立しない。タスク16（ほか 1 か所）も同じ。 | タスク13・16に、状態ごとの出力を確認する JUnit を先に作り、RED を確認してから実装し、GREEN と回帰（mvn test）を確認する旨を足す。タスク13の git diff の条件は「実装先のファイルと、本タスクで追加するテストファイル以外に変更が無い」に直す。 | 修正：タスク内で完結する書き方に揃える（修正案のとおり） | 確認済み |  |  |
| 7 | traceability | 業務のあいまい・不足 | 要判断 | df4f8882335a92b6 | d5a8e1da45c02a6a | specs/application-status-search/tasks.md § ドメイン / ビジネスロジック / 11 | AC 3.3 | AC3.3（CSVの範囲は検索と同じ）がタスク11の完了条件で確認されない | AC 3.3「CSV に出す範囲は、画面の検索と同じ条件・絞り込み・上限件数にしなければならない」は _Requirements に挙がり、タスク11の本文にも書かれている。しかし完了条件のケース（見出し 14 列・ダブルクォート・CRLF・ファイル名・0 件と上限超えで見出しだけ・入力エラーで出力しない）に、社外ユーザーの範囲（括弧付き）と同じ条件で CSV が絞られること、検索と同じ上限件数で打ち切られることを確かめる項目が無い。タスク9の完了条件も検索側（externalScope）だけを対象とする。ID 対応はあるが、完了条件による充足が無い（ID 対応あり・内容未充足）。 | タスク11の完了条件に「社外ユーザーの範囲と上限件数が検索と同じ条件で CSV にも掛かる」ケースを足す。 | 修正：完了条件にケースを足す（修正案のとおり） | 確認済み |  |  |
| 8 | traceability | 業務のあいまい・不足 | 要判断 | 2d4573ef1cec7d77 | 22f4c064a77db8e5 | specs/application-status-search/tasks.md § 本計画の前提と規約（画面設計工程の成果物の扱い） / 対象の範囲 | P01 行と メニュー登録 | P01行とメニュー・ZMENUAUTH登録の担当が未タスク化で不明 | design.md「責務境界」は「所有するデータ」に、コードマスタ WTZ/PARAM/P01 のこの画面の行（キー3＝PWTGO060、数値項目1＝50）を挙げ、「移行方針」の段階分けと「移行対象ファイル一覧」にも P01 の行とメニュー・ZMENUAUTH（PWTGO060）の行の追加（2 行）を書く。tasks.md は「ほかのコードマスタの行・ほかの画面と同じ扱いで行うため本計画のタスクにしない。Service の事前条件として扱う」とし、タスク1の確認対象にも P01・P02・メニュー・ZMENUAUTH の存在確認が含まれない。design 側も「同じ扱いで登録」と担当者・時期を書かず、Out of Boundary では委譲先を PJ45 としている。結果として、検索の 1 ページ件数 50 や画面を開くためのメニュー行が無い状態でタスク14・15 の動作確認や全体結合確認に進むおそれがある。tasks が外すこと自体は design の書き方に沿うが、誰がいつ登録し、確認がどのタスクにあるかが tasks から読み取れない。 | 質問：(a) 登録は PJ45 側が行うと確認でき、タスク1で P01・P02・メニュー・ZMENUAUTH の行の存在確認を足す。(b) 本 feature のタスクとして登録（または登録用の SQL の作成）を追加する。のどちらかを決める。 | 質問：登録の担当が design からも tasks からも決まらないため | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | 人間による確認（steering の例外化は Phase 2 の steering 変更、または質問 Q-TK-AS-003 の選び直し） | steering/product.md の改修対象の定めと、画面設計書に合わせて共通シェルを改修する方式の食い違いは、tasks だけでは解決できない。docs/ も再集約の対象になる（下流の無効化は L3 が行う） |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| verifiable-criteria-check | specs/application-status-search/tasks.md § 横断確認 / 17 | タスク17の起動完了判定と1経路を /menu の HTTP 200 とする点（DB・認証依存の有無は smoke 実行時に確認する旨の記載を含む） | answer:tasks-authoring-generate[application-status-search] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 5 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T23:38:14+09:00 |  |  |  |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 2026-10-09T23:50:48+09:00 | ①② | ["specs/application-status-search/tasks.md"] | {"specs/application-status-search/tasks.md":"afa2de5e7a5a68130f521be7e70f213ed05dd075bd087cf90020e023a9dd8a59"} | 8 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | steering-conformance | 業務の欠落・矛盾 | 重大 | 4ef3d89000cc105a | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | WTG以外への波及 | タスク13がWTG以外のWiNG画面も改修し、steeringの改修対象外に反する | 違反。タスク13は common/header.html を画面設計書に合わせて改修する。common_header を呼ぶテンプレートは Grep で 33 件（header.html 自身を除き 32）あり、wtz・wtl・wte など WTG 以外の画面を含む。menu.html（wtz/wtz001）と error.html、ExceptionResolver も WTG 以外の画面から使われる。steering/product.md「位置づけ」は「改修対象は契約・管財管理（WTG）だけ」、同「プロダクトレベルでやらないこと」は「契約・管財管理（WTG）以外の WiNG 機能は改修しない」（REQ-003）と定める。タスク13の注記は「人が Q-TK-AS-003 で A（…WTG 以外への波及を上流で許容する）を選んだ事実」とするが、confirmed_answers の選択肢 A の文言は「既存 wing の共通ヘッダ・メニュー・エラー画面を、画面設計書に合わせて確認・改修する」で、WTG 以外への波及の許容も steering の例外化も含まない（回答も「A。既存 wing の共通ヘッダ・メニュー・エラー画面を、画面設計書に合わせて確認・改修する」のみ）。注記は矛盾を自ら認めているが steering 側は変更されていない。影響はお知らせ欄（menu.html の information、wtlTaiouLimitInfo）を置かない改修や、error.html の戻る(C) ボタン削除にも及ぶ。原因は上流（steering と画面設計書の食い違い）にあるため差戻し候補として記す（design.md・requirements.md・docs/ も再集約の対象になりうる）。回答 Q-TK-AS-003 は「A を選ぶ」ことまでは決めているため回答での除外にはしない（許容は回答に無い）。 | 次のどれかを人が決める。(a) steering/product.md に共通ヘッダ・メニュー・エラー画面を改修対象に含める例外を明記する（Phase 2 の steering 変更）。(b) タスク13を WTG の機能配下に画面を新設する方式（Q-TK-AS-003 の B）に改める。(c) 既存の共通シェルは変えず、画面設計書との差分を上流へ戻す（同 C）。決まるまで、タスク13の注記の「許容を選んだ」の記述は事実（選択肢 A の文言）に合わせて直す。 | 質問：steering の例外化か方式の選び直しかは業務の判断で、tasks だけでは決められない | 確認済み |  |  |
| 2 | steering-conformance | 業務のあいまい・不足 | 要判断 | 9fa18510a37b1fc0 | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | LOGOUT 無効表示 | タスク13にLOGOUT無効化でWiNG全体のログアウト導線が消える影響の明記なし | タスク13は「画面設計書に合わせる内容」で「LOGOUT は全画面で無効表示」と書くだけで、既存 WiNG 全体でヘッダのリンク [LOG OUT]（common/header.html:54 の Logout_lbl。/logout へ送信、同 :69）が効かなくなることを、本文にも完了条件にも、波及の注記にも明示していない。header.html は 32 のテンプレートが共通で呼ぶ。完了条件は「ヘッダのリンクの有効・無効の表示が画面マップ §3 と §4-1 の表と一致する」だけで、LOGOUT を無効にした結果の確認が無い。steering/security.md はログアウト（LogoutController）をセッション失効のトリガとしており、利用者がヘッダからログアウトできなくなる影響が書かれていない。上流の根拠は画面マップ §3 ④・§6-2 #4（行き先のログイン画面が本案件の画面に無いため無効表示）。#1 とは原因が別（導線の消失）なので分けた。 | 質問：次を決めて本文と完了条件に書く。(a) 画面設計書どおり LOGOUT を全画面で無効にし、WiNG 全体でヘッダからログアウトできなくなることを注記に明記して完了条件に含める。(b) LOGOUT は有効のまま残し、画面設計書（画面マップ §4-1）の改訂を上流へ回す。 | 質問：ログアウト導線を無効にするかは業務・運用の判断が要る | 確認済み |  |  |
| 3 | traceability | 業務のあいまい・不足 | 要判断 | 2a2ae099e2a4c8f6 | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | メニュー項目の作り | タスク13のメニューが動的menuListか固定2項目か未決で実装手段が不明 | 意味判定：画面設計書の内容がタスクで満たせる形になっていない。タスク13は「メニュー項目はメニュー情報から menuList として渡る作りで、テンプレートだけでは項目の中身を決めない」と書く一方、「入口のリンクは権限で出し分けず、全項目を表示する」「ナビ項目『物件基本情報登録変更』は無効表示、『物件契約情報申請状況検索/一覧』は /wtg060 へのリンク」とも書く。実コードでは menu.html:35 が th:each="menu : ${menuList}" で描き、MenuController:102 が menuService.getChildMenuList で階層メニューを組み、権限は ZMENUAUTH 側で決まる（ソースで確認）。画面設計書（_app-shell/screen-spec.md §3-1 の通常状態）は見出し「契約・管財管理」と 2 項目の固定の一覧だけを定める。固定の 2 項目に置き換えるのか、既存の動的 menuList の上で表示を合わせるのか（その場合、無効表示と出し分けなしをどう実現するか）が書かれておらず、完了条件（レンダリング件数と遷移先 /wtg060）では判定できない。他の WiNG 機能のメニューが消えるかどうかも読み取れない。 | 質問：入口画面の項目を (a) 画面設計書のとおり固定 2 項目にする（他機能のメニュー表示が無くなることを明記する）、(b) 既存の menuList を残し、契約・管財管理の部分だけ合わせる、のどちらにするかを決め、タスク13の本文と完了条件に書く。 | 質問：既存メニューの動的な作りと画面設計書の固定表示の食い違いは、人が選ぶ必要がある | 確認済み |  |  |
| 4 | traceability | 業務のあいまい・不足 | 要判断 | ece52c9e5eae1acd | 79f2ea1e04c3d861 | specs/application-status-search/tasks.md § 但し書き（未決のまま残す事項） / 16 | 全文のツールチップ | designの切り詰め値の全文ツールチップがタスク16で範囲外のまま | design.md「一覧の 14 列」は「長い値は表示バイト数で切り、ツールチップで全部を出す（基地局名 16・案件小グループ 15・起案会社名 22・エリア 15・起案担当者 10）」と定め、コンポーネント一覧の画面テンプレートの目的にも「ツールチップ」を含め、テスト戦略 E2E にもツールチップを挙げる。画面設計書 §3-1-5「長文」の状態も「ポインタを載せるとツールチップで全文」とし、§5-1 #14 は STYLEGUIDE.md との食い違いを人の判断で design.md に従うと決着済み（STYLEGUIDE-backlog.md SGB-17、by toshiya-fukunaga、2026-10-09）。器が未整備なだけである。一方 tasks.md の但し書きとタスク16の範囲外の扱いは「切り詰めた値の全文を出すツールチップ」を部品が無いため描かず、完了条件にも含めないとし、スコープ外とする根拠を人の回答（confirmed_answers の Q-TK-AS-001〜003）に持たない。タスク10は切り詰め値と全文の両方を持たせるが、全文を画面に出すタスクは無い。結果として design の要素（2.1 の値の欠落を防ぐ全文表示）がどのタスクにも割り当てられず、design との差は tasks にも design にも判断として残っていない。 | 質問：次のどれかにして、タスク16の本文・完了条件か design の扱いに反映する。(a) 器が整備されるまで全文表示を保留する旨を、design.md の変更管理で扱う判断として決定ログに残す。(b) タスク16に、全文を title 属性など既存の手段で出す範囲を足す。(c) SGB-17 の器の整備を待ってタスク16を着手させる。 | 質問：design の要素を範囲外にする判断が文書として残っていないため | 確認済み |  |  |
| 5 | traceability | 文書間の参照 | 軽微 | 354b5c49ce49d7fa | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | Boundary と Design の参照 | タスク13のBoundaryとDesignがdesign.mdのコンポーネント一覧に無い | 早見表は「_Boundary: …_ は design.md の ### コンポーネント一覧（Summary）にある名前」と定める。タスク13の Boundary は「_app-shell（共通シェル・入口・システムエラー。design.md のコンポーネント一覧に無い共通部…）」で、design.md の Summary（Controller・Service・Mapper・画面テンプレートの 4 行）に無い名前を書いている。_Design: ## コンポーネントとインターフェース_ も、その節に _app-shell の記述が無い（design.md は共通ヘッダ・メニュー・エラー画面を扱わず、擬似 feature の _app-shell は design.md を持たない）。実装先そのものは人の回答 Q-TK-AS-003 A で決まっているため問わず、参照が切れていることだけを指す。 | _Boundary_ に書ける名前を置く（design.md への追加が要る）か、前提節に「_app-shell の Boundary は画面マップ §4 と _app-shell/screen-spec.md を根拠とし、design.md の Summary に無い」と、早見表の規約の例外として明記する。 | 修正：参照先の書き方を前提節に明記する（修正案のとおり） | 確認済み |  |  |
| 6 | traceability | 業務のあいまい・不足 | 要判断 | 0ea9acf79f7430f6 | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | UI タスクのテスト先行 | タスク13・16にテスト先行とREDの記述が無く、13はgit diff条件と矛盾 | タスク13・16は通常の機能実装（テンプレートの改修・新規作成）だが、本文・完了条件に、対応する JUnit を先に作ること、意図した失敗（RED）の確認、実装、成功確認（GREEN）が同一タスクで完結する書き方が無い。タスク16の完了条件は「各状態のモデルを与えた出力を JUnit で確認し、11 件とも成功する」、タスク13は「各状態の出力を JUnit で確認し、2 件とも成功する」で、JUnit を新規に作るのか既存を使うのかも不明。他のタスク（2〜12・14・15）は「同一タスク内の RED から GREEN を確認し」と書いており構成が揃っていない。さらにタスク13の完了条件「git diff --stat の変更ファイルが上の実装先に挙げたファイルだけである」は、JUnit のテストファイルの新規追加（実装先に挙げていない）と両立しない。ほか 1 か所（タスク16）も同じ。Phase 8 は同一 task_id・execution_id の RED→GREEN→VERIFY を要求する。 | タスク13・16に、状態ごとの出力を確認する JUnit を先に作り、RED を確認してから実装し、GREEN と回帰（mvn test）を確認する旨を足す。タスク13の git diff の条件は「実装先のファイルと、本タスクで追加するテストファイル以外に変更が無い」に直す。 | 修正：タスク内で完結する書き方に揃える（修正案のとおり） | 確認済み |  |  |
| 7 | traceability | 業務のあいまい・不足 | 要判断 | df4f8882335a92b6 | d5a8e1da45c02a6a | specs/application-status-search/tasks.md § ドメイン / ビジネスロジック / 11 | AC 3.3 | AC3.3（CSVの範囲は検索と同じ）がタスク11の完了条件で確認されない | AC 3.3「CSV に出す範囲は、…画面の検索と同じ条件・絞り込み・上限件数にしなければならない」は _Requirements に挙がり、タスク11の本文にも書かれている。しかし完了条件のケース（見出し 14 列・ダブルクォート・CRLF・ファイル名・0 件と上限超えで見出しだけ・入力エラーで出力しない）に、社外ユーザーの範囲（括弧付き）と同じ条件で CSV が絞られること、検索と同じ上限件数で打ち切られることを確かめる項目が無い。タスク9の完了条件は検索側（externalScope）だけ、タスク5の完了条件も SQL の定義の有無だけを対象とする。ID 対応はあるが完了条件による充足が無い（ID 対応あり・内容未充足）。 | タスク11の完了条件に「社外ユーザーの範囲と上限件数が検索と同じ条件で CSV にも掛かる」ケースを足す。 | 修正：完了条件にケースを足す（修正案のとおり） | 確認済み |  |  |
| 8 | traceability | 業務のあいまい・不足 | 要判断 | ad0d0650fac947dd | 22f4c064a77db8e5 | specs/application-status-search/tasks.md § 本計画の前提と規約（画面設計工程の成果物の扱い） / 対象の範囲 | P01 行とメニュー登録 | P01行とメニュー・ZMENUAUTH登録の担当が未タスク化で不明 | design.md「責務境界」の所有するデータに、コードマスタ WTZ/PARAM/P01 のこの画面の行（キー3＝PWTGO060、数値項目1＝50）を挙げ、「移行方針」の段階分けと「移行対象ファイル一覧」にも P01 の行とメニュー・ZMENUAUTH（PWTGO060）の行の追加（2 行）を書く。tasks.md は「ほかのコードマスタの行・ほかの画面と同じ扱いで行うため本計画のタスクにしない。Service の事前条件として扱う」とし、タスク1の確認対象にも P01・P02・メニュー・ZMENUAUTH の存在確認が含まれない。design 側も「同じ扱いで登録」と担当者・時期を書かず、Out of Boundary では委譲先を PJ45 としている。結果として、検索の 1 ページ件数 50 や画面を開くためのメニュー行が無い状態でタスク14・15 の動作確認や全体結合確認（タスク17）に進むおそれがある。tasks が外すこと自体は design の書き方に沿うが、誰がいつ登録し、確認がどのタスクにあるかが tasks から読み取れない。 | 質問：(a) 登録は PJ45 側が行うと確認でき、タスク1で P01・P02・メニュー・ZMENUAUTH の行の存在確認を足す。(b) 本 feature のタスクとして登録（または登録用の SQL の作成）を追加する。のどちらかを決める。 | 質問：登録の担当が design からも tasks からも決まらないため | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | 人間による確認（steering の例外化は Phase 2 の steering 変更、または質問 Q-TK-AS-003 の選び直し） | steering/product.md の改修対象の定めと、画面設計書に合わせて共通シェルを改修する方式の食い違いは、tasks だけでは解決できない。design・docs/ も再集約の対象になりうる（下流の無効化は L3 が行う） |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| verifiable-criteria-check | specs/application-status-search/tasks.md § 横断確認 / 17 | タスク17の起動完了判定と1経路を /menu の HTTP 200 とする点（DB・認証依存の有無は smoke 実行時に確認する旨の記載を含む） | answer:tasks-authoring-generate[application-status-search] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 5 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T23:56:23+09:00 |  |  |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 5 | feature:application-status-search | 2 | system（自動）：同じ指摘を 2 回目 #5 へ引き継ぎ | 2026-10-09T23:56:23+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 2026-10-10T00:12:50+09:00 | ①② | ["specs/property-basic-info/tasks.md"] | {"specs/property-basic-info/tasks.md":"cdb8225f3bca7310e8613e1e81869b1d932073f507d85110c0a832ca448d076c"} | 7 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | evidence-guard | 業務のあいまい・不足 | 要判断 | df370754f308d03a | 187ca34a5c69cb6b | specs/property-basic-info/tasks.md § DDL・投入文の置き場 / 4 | DDL の出力先 | DDL・投入文の出力先 deploy/property-basic-info/ に上流の根拠がない | 区分：根拠なし。探した範囲は design.md（`### ファイル配置計画` のツリーと `### 変更する既存ファイル`、`### 移行方針`）と steering/database.md（`## マイグレーション`）。design.md のファイル配置計画に deploy/ は無く、移行方針は「DDL を導入手順書に沿って発注者が適用する」とだけ書く。steering/database.md は「DDL は DB レイアウト設計書を元に作る」「適用は発注者」と定めるが置き場は定めない。tasks.md は「DDL・投入文の置き場」節で「定めが無く既存の置き場も無い。本計画は deploy/property-basic-info/ を出力先とする」と自ら仮定を明記し、タスク 4 の本文とタスク 34 の完了条件（git diff の許容範囲・TWTGM080 の DDL の 4 列確認）がそのパスに依存している。tasks にしか存在しない配置の設計判断である。なお、作成担当が前提節に仮定として記録した点は適切だが、記録しても上流の根拠が生じるわけではない。 | 質問：次のどれかを決めて design.md（ファイル配置計画）か tasks の前提に根拠を残す。(a) 出力先を deploy/property-basic-info/ とすると人が確定する（design のファイル配置計画に追記）。(b) 別の置き場（例：導入手順書の添付、_handoff 配下）にする。(c) DDL と投入文の作成を本 feature のタスクから外し、導入手順書側で扱う。 | 質問：DDL の置き場は design にも steering にも無く、人が決める事項のため | 確認済み |  |  |
| 2 | traceability | 業務の欠落・矛盾 | 重大 | 6f3f1498a81d90e4 | - | specs/property-basic-info/tasks.md § タスク一覧 基盤・準備 / 4 | TWTZM050 の MAX区分 | タスク4のMAX区分1は、wing上は回転ありを意味し設計意図と逆 | 意味判定：ID 対応あり・内容未充足。タスク4は採番マスタ TWTZM050 の行を「MAX区分 1」で作り、完了条件の DeployScriptsTest で「design.md と一致」を確かめる（tasks.md 127〜128 行目）。design.md（`### ドメインモデル` の申請No 採番）は MAX区分 1 を「ローテーションなし。上限を超えて 0001 へ戻り既存の申請No と重なるのを避ける」と説明する。しかし wing/src/main/java/jp/co/kccs/wt/common/service/NumberingService.java の 56〜60 行目は MAX_TYPE_NON_LOTATION＝"0"（ローテーション無し）、MAX_TYPE_LOTATION＝"1"（ローテーション有り）と定める。設計の意図（回転させない）と値（1）が逆で、タスク4のとおりに作ると上限超過で 0001 へ戻り申請No が重なる。.aidd/.engine/upstream-carryover.md 23 行目も「MAX区分を "0" に直す」を物件基本情報登録変更の design の開き直し項目に挙げているが、tasks.md の「上流との食い違い・不足の扱い」には載っていない（食い違いを記録した 10 件に含まれない）。原因は上流の design にあるため差戻し候補（docs/ も再集約の対象になる。下流の無効化は L3 が行う）。 | design.md の MAX区分を "0" に直したうえで、タスク4の投入文とテストの値を "0" にする。design の改訂まで待つ場合は、tasks.md の「上流との食い違い・不足の扱い」にこの件を足し、タスク4の MAX区分は design の改訂後の値に従うと書く。 | 差戻し：design の値が wing の実装と逆で、タスクだけでは直せないため | 確認済み |  |  |
| 3 | traceability | 業務の欠落・矛盾 | 重大 | 877e88350682d5e5 | 81ebca98c50b913a | specs/property-basic-info/tasks.md § 物件基本情報登録変更（データアクセスと業務ロジック） / 13 | 契約者区分の値 | タスク13の契約者区分 "01" は issue-request の設計（1・2）と食い違う | 意味判定：下流の値が上流の定義を満たしていない。タスク13は契約者を「関係者1〜5 のうち契約者区分が "01" で関係(地位) に「旧」を含まない人」とし、完了条件でも「契約者区分 "01" 以外の除外」を確かめる（tasks.md 221・223 行目）。この値は property-basic-info の design.md（契約局情報欄に出す列）に由来する。一方、発行依頼書の列を定義する specs/issue-request/design.md 231 行目は「契約者区分名は固定（1→"契約者"、2→"関係者"）」と定め、契約者区分の値は 1・2 である。upstream-carryover.md 99 行目も「契約者区分 "1"（1:契約者・2:関係者）に直す。"01" は回答者の取り違え」を物件基本情報登録変更の design の開き直し項目に挙げるが、tasks.md の前提節には記録がない。このまま実装すると契約者が 1 人も表示されない。原因は上流 design にあるため差戻し候補（docs/ も再集約の対象になる。下流の無効化は L3 が行う）。 | design.md の該当を "1"（1:契約者・2:関係者）に直したうえで、タスク13の本文と完了条件を "1" にする。design の改訂まで待つ場合は、前提節に食い違いとして記録し、タスク13は改訂後の値に従うと書く。 | 差戻し：issue-request の定義と食い違う値を design が持つため | 確認済み |  |  |
| 4 | traceability | 業務のあいまい・不足 | 要判断 | 832c64087799a9bd | 1bb8581b35fbbae8 | specs/property-basic-info/tasks.md § WTG 共通（WTG 申請状態サービス） / 9 | 発番日時と更新者名の書込み | TWTGM080の発番日時と更新者名を書く操作がタスクに足りない | 意味判定：ID 対応あり・内容未充足。(1) 発番日時：design.md の TWTGM080 の列 31（Hatsuban_Uketsuke_DateTime）は備考が「発番時のシステム日時を登録」。specs/issue-request/design.md 2504 行目は recordNumbering が発番日時と更新者名を入れると定め、upstream-carryover.md 26 行目も同旨で pbi design の開き直しを挙げる。タスク5の SQL の更新列の列挙にも、タスク9の recordNumbering の本文・完了条件にも発番日時が無く、DDL にある列の書き手がどのタスクにも無い。タスク34の公開契約の確認でも見ない。(2) 更新者名：タスク9は UpdatedPerson_Name の値の出所を transit・recordNumbering の文脈でだけ決める（179 行目）。更新（タスク16）と複製（タスク18）が TWTGM080 を書くときに UpdatedPerson_Name を入れるかは書かれていない。application-status-search の design（Q-DS-AS-002 の更新者名の検索）はこの列を読むので、書込みの契機が決まらないと検索の結果が揃わない。タスク34も UpdatedPerson_Name を確認対象の列に挙げながら完了条件では確認しない（432 行目は 4 つの日時列だけ）。なお「design が UpdatedPerson_Name の出所を明記しないため承認履歴の最終更新者名と同じにする」という記録（179 行目）は事実に合う（design.md 300 行目に出所の記述が無い）。原因は上流 design の書き漏れにあるため差戻し候補（docs/ も再集約の対象になる。下流の無効化は L3 が行う）。 | 質問：(a) 発番日時は recordNumbering が書くと決め、タスク5の SQL とタスク9の本文・完了条件に足す。(b) UpdatedPerson_Name は TWTGM080 を書く全操作（更新・複製・承認フロー・発番）でログインユーザー名を入れるか、承認フローと発番だけかを決め、タスク9・16・18 の完了条件に書く。決める内容はタスク34の確認対象にも反映する。 | 質問：書込みの契機は業務の判断が要り、design にも書かれていないため | 確認済み |  |  |
| 5 | traceability | 業務のあいまい・不足 | 要判断 | d2c809f8624ec4fd | 6d6fd863a620d485 | specs/property-basic-info/tasks.md § API / 入口 / 28 | returnList と deleteShinse の戻り先 | タスク28の完了条件が戻り先の値を固定せず、判定できない | 作成担当が前提節に記録した食い違いは事実である。design.md 572 行目は /wtg070/returnList の戻り先を /wtg060 とするが、specs/application-status-search/design.md 79・312・335 行目は /wtg060（検索条件を消す初期表示）ではなく /wtg060/return で受けると定め、upstream-carryover.md 65・66 行目が pbi design の修正（returnList の戻り先、deleteShinse の Response）を挙げる。その結果タスク28とタスク24の完了条件は「申請状況一覧への戻り先を返す」「実装時点の承認済み design に従う」とだけ書き、どちらの値を期待するかを決めていないため、完了条件でテストの期待値が定まらない。application-status-search 側の実装（/wtg060/return で前のページを再検索する）は pbi の戻り先に依存する。原因は上流 design の食い違いにあるため差戻し候補（docs/ も再集約の対象になる。下流の無効化は L3 が行う）。 | design.md の戻り先を /wtg060/return に直したうえで、タスク28・24の完了条件に「returnList と deleteShinse の後の戻り先が /wtg060/return である」を足す。改訂までは前提節の記録のとおり着手を止めるか、改訂後の値で期待値を決めるかを人が選ぶ。 | 差戻し：pbi と application-status-search の design の食い違いで、tasks では決められないため | 確認済み |  |  |
| 6 | traceability | 業務のあいまい・不足 | 要判断 | 99d804080a2c29a7 | - | specs/property-basic-info/tasks.md § UI / 表示 / 31 | AC 10.2 | AC 10.2 と 10.3 の動作がどの完了条件にも確認されない | 意味判定：ID 対応あり・内容未充足。requirements.md の 10.2「確認で取り消したとき、システムは画面を離れてはならない」と 10.3「了承したとき、編集中の内容を破棄し申請状況一覧の画面へ戻らなければならない」は、タスク31の _Requirements に挙がる。しかしタスク31の完了条件は「戻るの確認文言が『編集中の内容を破棄して戻ります。よろしいですか？』である」までで、取消で送信されないこと・了承で /wtg070/returnList へ送られることを確かめる項目が無い（10.3 の戻り先はタスク28が別に見るが、画面側の呼び出しは見ない）。前提節は画面の操作の確認を総合テストに回すとするが、タスク31 の完了条件も既知の制約への記録も、10.2 を総合テストで確認する対象として書いていない。 | タスク31の完了条件に、テンプレートの戻るボタンが確認で取消のとき送信しない記述と、了承で returnList を呼ぶ記述を出力で確かめるケースを足す。出力で確かめられない場合は、10.2 を総合テストの確認対象とすることを既知の制約に記録する旨を書く。 | 修正：完了条件の不足を足せば解消できる | 確認済み |  |  |
| 7 | traceability | 文書間の参照 | 軽微 | f688e2760644fb61 | b0d9afa4a52da78a | specs/property-basic-info/tasks.md § 基盤・準備 / 2 | Boundary の書き方 | タスク2・4のBoundaryにdesignのコンポーネント一覧に無い語が混じる | 早見表は「_Boundary: …_ は design.md の ### コンポーネント一覧（Summary）にある名前」と定める。タスク2の Boundary は「物件基本情報登録変更 Service（共通部品 CsvUtils。単独の行はコンポーネント一覧に無く、根拠は…）」、タスク4は「物件基本情報登録変更 Mapper（DDL・投入文。移行方針の成果物で、コンポーネント一覧に単独の行は無い）」で、Summary の名前に説明と存在しない名前を足している。CsvUtils は design.md の技術スタックとデータ契約に根拠があるが、Summary の行は無い。機械が名前を照合するため、括弧書きは本文へ移す。同種の指摘が application-status-search の tasks 1 回目 #5 にもある。 | _Boundary_ は Summary の名前だけ（例：「物件基本情報登録変更 Service」「物件基本情報登録変更 Mapper」）にし、括弧書きの説明は本文か前提節の注記へ移す。 | 修正：書き方の統一で、AI が直せるため | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 2 | specs/property-basic-info/design.md（Phase 5） | TWTZM050 の MAX区分が wing の NumberingService の定義と逆。docs/ も再集約の対象になる（下流の無効化は L3 が行う） |
| 3 | specs/property-basic-info/design.md（Phase 5） | 契約者区分の値 "01" が issue-request の design（1・2）と食い違う。docs/ も再集約の対象になる（下流の無効化は L3 が行う） |
| 4 | specs/property-basic-info/design.md（Phase 5） | 発番日時の書き手と更新者名の書込みの契機が design に無い。docs/ も再集約の対象になる（下流の無効化は L3 が行う） |
| 5 | specs/property-basic-info/design.md（Phase 5） | returnList・deleteShinse の戻り先が application-status-search の design と食い違う。docs/ も再集約の対象になる（下流の無効化は L3 が行う） |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| evidence-guard | specs/property-basic-info/tasks.md § 基盤・準備 / 2 | CsvUtils の呼び方（CsvEntityListHandler と、要素が null の 1 件のリストで見出し行だけを書く）が pbi の design に無い | answer:design-authoring-generate[application-status-search] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 7 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-13T09:25:41+09:00 |  |  |  |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase:property-basic-info | 1 | 2026-10-13T09:26:59+09:00 | ② | ["specs/property-basic-info/tasks.md"] | {"specs/property-basic-info/tasks.md":"cdb8225f3bca7310e8613e1e81869b1d932073f507d85110c0a832ca448d076c"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 1 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | masato-teramoto | 2026-10-13T09:33:05+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 2 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | masato-teramoto | 2026-10-13T09:33:22+09:00 | 対象外 |  | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 3 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | masato-teramoto | 2026-10-13T09:33:39+09:00 | 対象外 |  | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 4 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | masato-teramoto | 2026-10-13T09:33:55+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 5 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | masato-teramoto | 2026-10-13T09:34:12+09:00 | 対象外 |  | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 6 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | masato-teramoto | 2026-10-13T09:34:29+09:00 | 対象外 |  | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 7 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | masato-teramoto | 2026-10-13T09:35:33+09:00 | 対象外 |  | 不採用 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase:property-basic-info | 1 | specs/property-basic-info/tasks.md | masato-teramoto | 2026-10-13T09:36:18+09:00 | cdb8225f3bca7310e8613e1e81869b1d932073f507d85110c0a832ca448d076c |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 1 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | phase:property-basic-info | 1 |
| feature:property-basic-info | 1 | 2 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | phase:property-basic-info | 1 |
| feature:property-basic-info | 1 | 3 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | phase:property-basic-info | 1 |
| feature:property-basic-info | 1 | 4 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | phase:property-basic-info | 1 |
| feature:property-basic-info | 1 | 5 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | phase:property-basic-info | 1 |
| feature:property-basic-info | 1 | 6 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | phase:property-basic-info | 1 |
| feature:property-basic-info | 1 | 7 | 対応せず進める | 依存先 property-basic-info は対象外とし、application-status-search の承認を最優先とする（ユーザー指示） | phase:property-basic-info | 1 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 2026-10-13T09:42:34+09:00 | ①② | ["specs/application-status-search/tasks.md"] | {"specs/application-status-search/tasks.md":"afa2de5e7a5a68130f521be7e70f213ed05dd075bd087cf90020e023a9dd8a59"} | 8 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | steering-conformance | 業務の欠落・矛盾 | 重大 | 4ef3d89000cc105a | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | WTG以外への波及 | タスク13がWTG以外のWiNG画面も改修し、steeringの改修対象外に反する | 違反。タスク13は common/header.html を画面設計書に合わせて改修する。common_header を呼ぶテンプレートは Grep で 33 件（header.html 自身を除き 32）あり、wtz・wtl・wte など WTG 以外の画面を含む。menu.html（wtz/wtz001）と error.html、ExceptionResolver も WTG 以外の画面から使われる。steering/product.md「位置づけ」は「改修対象は契約・管財管理（WTG）だけ」、同「プロダクトレベルでやらないこと」は「契約・管財管理（WTG）以外の WiNG 機能は改修しない」（REQ-003）と定める。タスク13の注記は「人が Q-TK-AS-003 で A（…WTG 以外への波及を上流で許容する）を選んだ事実」とするが、confirmed_answers の選択肢 A の文言は「既存 wing の共通ヘッダ・メニュー・エラー画面を、画面設計書に合わせて確認・改修する」で、WTG 以外への波及の許容も steering の例外化も含まない（回答も「A。既存 wing の共通ヘッダ・メニュー・エラー画面を、画面設計書に合わせて確認・改修する」のみ）。注記は矛盾を自ら認めているが steering 側は変更されていない。影響はお知らせ欄（menu.html の information、wtlTaiouLimitInfo）を置かない改修や、error.html の戻る(C) ボタン削除にも及ぶ。原因は上流（steering と画面設計書の食い違い）にあるため差戻し候補として記す（design.md・requirements.md・docs/ も再集約の対象になりうる）。回答 Q-TK-AS-003 は「A を選ぶ」ことまでは決めているため回答での除外にはしない（許容は回答に無い）。今回の再検査でも tasks.md 本文・steering/product.md に変更は無く、header.html の呼び出し元 33 件（common_header の Grep）を再確認した。 | 次のどれかを人が決める。(a) steering/product.md に共通ヘッダ・メニュー・エラー画面を改修対象に含める例外を明記する（Phase 2 の steering 変更）。(b) タスク13を WTG の機能配下に画面を新設する方式（Q-TK-AS-003 の B）に改める。(c) 既存の共通シェルは変えず、画面設計書との差分を上流へ戻す（同 C）。決まるまで、タスク13の注記の「許容を選んだ」の記述は事実（選択肢 A の文言）に合わせて直す。 | 質問：steering の例外化か方式の選び直しかは業務の判断で、tasks だけでは決められない | 確認済み |  |  |
| 2 | steering-conformance | 業務のあいまい・不足 | 要判断 | 9fa18510a37b1fc0 | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | LOGOUT 無効表示 | タスク13にLOGOUT無効化でWiNG全体のログアウト導線が消える影響の明記なし | タスク13は「画面設計書に合わせる内容」で「LOGOUT は全画面で無効表示」と書くだけで、既存 WiNG 全体でヘッダのリンク [LOG OUT]（common/header.html:54 の Logout_lbl。/logout へ送信、同 :69）が効かなくなることを、本文にも完了条件にも、波及の注記にも明示していない。header.html は 32 のテンプレートが共通で呼ぶ。完了条件は「ヘッダのリンクの有効・無効の表示が画面マップ §3 と §4-1 の表と一致する」だけで、LOGOUT を無効にした結果の確認が無い。steering/security.md はログアウト（LogoutController）をセッション失効のトリガとしており、利用者がヘッダからログアウトできなくなる影響が書かれていない。上流の根拠は画面マップ §3 ④・§6-2 #4（行き先のログイン画面が本案件の画面に無いため無効表示）。#1 とは原因が別（導線の消失）なので分けた。 | 質問：次を決めて本文と完了条件に書く。(a) 画面設計書どおり LOGOUT を全画面で無効にし、WiNG 全体でヘッダからログアウトできなくなることを注記に明記して完了条件に含める。(b) LOGOUT は有効のまま残し、画面設計書（画面マップ §4-1）の改訂を上流へ回す。 | 質問：ログアウト導線を無効にするかは業務・運用の判断が要る | 確認済み |  |  |
| 3 | traceability | 業務のあいまい・不足 | 要判断 | 2a2ae099e2a4c8f6 | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | メニュー項目の作り | タスク13のメニューが動的menuListか固定2項目か未決で実装手段が不明 | 意味判定：画面設計書の内容がタスクで満たせる形になっていない。タスク13は「メニュー項目はメニュー情報から menuList として渡る作りで、テンプレートだけでは項目の中身を決めない」と書く一方、「入口のリンクは権限で出し分けず、全項目を表示する」「ナビ項目『物件基本情報登録変更』は無効表示、『物件契約情報申請状況検索/一覧』は /wtg060 へのリンク」とも書く。実コードでは menu.html:35 が th:each="menu : ${menuList}" で描き、MenuController:102 が menuService.getChildMenuList で階層メニューを組み、権限は ZMENUAUTH 側で決まる（ソースで再確認）。画面設計書（_app-shell/screen-spec.md §3-1 の通常状態）は見出し「契約・管財管理」と 2 項目の固定の一覧だけを定める。固定の 2 項目に置き換えるのか、既存の動的 menuList の上で表示を合わせるのか（その場合、無効表示と出し分けなしをどう実現するか）が書かれておらず、完了条件（レンダリング件数と遷移先 /wtg060）では判定できない。他の WiNG 機能のメニューが消えるかどうかも読み取れない。 | 質問：入口画面の項目を (a) 画面設計書のとおり固定 2 項目にする（他機能のメニュー表示が無くなることを明記する）、(b) 既存の menuList を残し、契約・管財管理の部分だけ合わせる、のどちらにするかを決め、タスク13の本文と完了条件に書く。 | 質問：既存メニューの動的な作りと画面設計書の固定表示の食い違いは、人が選ぶ必要がある | 確認済み |  |  |
| 4 | traceability | 業務のあいまい・不足 | 要判断 | ece52c9e5eae1acd | 79f2ea1e04c3d861 | specs/application-status-search/tasks.md § 但し書き（未決のまま残す事項） / 16 | 全文のツールチップ | designの切り詰め値の全文ツールチップがタスク16で範囲外のまま | design.md「一覧の 14 列」は「長い値は表示バイト数で切り、ツールチップで全部を出す（基地局名 16・案件小グループ 15・起案会社名 22・エリア 15・起案担当者 10）」と定め、コンポーネント一覧の画面テンプレートの目的にも「ツールチップ」を含め、テスト戦略 E2E にもツールチップを挙げる。画面設計書 §3-1-5「長文」の状態も「ポインタを載せるとツールチップで全文」とし、§5-1 #14 は STYLEGUIDE.md との食い違いを人の判断で design.md に従うと決着済み（STYLEGUIDE-backlog.md SGB-17、by toshiya-fukunaga、2026-10-09）。器が未整備なだけである。一方 tasks.md の但し書きとタスク16の範囲外の扱いは「切り詰めた値の全文を出すツールチップ」を部品が無いため描かず、完了条件にも含めないとし、スコープ外とする根拠を人の回答（confirmed_answers の Q-TK-AS-001〜003）に持たない。タスク10は切り詰め値と全文の両方を持たせるが、全文を画面に出すタスクは無い。結果として design の要素（2.1 の値の欠落を防ぐ全文表示）がどのタスクにも割り当てられず、design との差は tasks にも design にも判断として残っていない。 | 質問：次のどれかにして、タスク16の本文・完了条件か design の扱いに反映する。(a) 器が整備されるまで全文表示を保留する旨を、design.md の変更管理で扱う判断として決定ログに残す。(b) タスク16に、全文を title 属性など既存の手段で出す範囲を足す。(c) SGB-17 の器の整備を待ってタスク16を着手させる。 | 質問：design の要素を範囲外にする判断が文書として残っていないため | 確認済み |  |  |
| 5 | traceability | 文書間の参照 | 軽微 | 354b5c49ce49d7fa | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | Boundary と Design の参照 | タスク13のBoundaryとDesignがdesign.mdのコンポーネント一覧に無い | 早見表は「_Boundary: …_ は design.md の ### コンポーネント一覧（Summary）にある名前」と定める。タスク13の Boundary は「_app-shell（共通シェル・入口・システムエラー。design.md のコンポーネント一覧に無い共通部…）」で、design.md の Summary（Controller・Service・Mapper・画面テンプレートの 4 行）に無い名前を書いている。_Design: ## コンポーネントとインターフェース_ も、その節に _app-shell の記述が無い（design.md は共通ヘッダ・メニュー・エラー画面を扱わず、擬似 feature の _app-shell は design.md を持たない）。実装先そのものは人の回答 Q-TK-AS-003 A で決まっているため問わず（evidence-guard の「design に無い配置」としては出さない）、参照が切れていることだけを指す。 | _Boundary_ に書ける名前を置く（design.md への追加が要る）か、前提節に「_app-shell の Boundary は画面マップ §4 と _app-shell/screen-spec.md を根拠とし、design.md の Summary に無い」と、早見表の規約の例外として明記する。 | 修正：参照先の書き方を前提節に明記する（修正案のとおり） | 確認済み |  |  |
| 6 | traceability | 業務のあいまい・不足 | 要判断 | 0ea9acf79f7430f6 | 163c35e5512c8cbc | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | UI タスクのテスト先行 | タスク13・16にテスト先行とREDの記述が無く、13はgit diff条件と矛盾 | タスク13・16は通常の機能実装（テンプレートの改修・新規作成）だが、本文・完了条件に、対応する JUnit を先に作ること、意図した失敗（RED）の確認、実装、成功確認（GREEN）が同一タスクで完結する書き方が無い。タスク16の完了条件は「各状態のモデルを与えた出力を JUnit で確認し、11 件とも成功する」、タスク13は「各状態の出力を JUnit で確認し、2 件とも成功する」で、JUnit を新規に作るのか既存を使うのかも不明。他のタスク（2〜12・14・15）は「同一タスク内の RED から GREEN を確認し」と書いており構成が揃っていない。さらにタスク13の完了条件「git diff --stat の変更ファイルが上の実装先に挙げたファイルだけである」は、JUnit のテストファイルの新規追加（実装先に挙げていない）と両立しない。ほか 1 か所（タスク16）も同じ。Phase 8 は同一 task_id・execution_id の RED→GREEN→VERIFY を要求する。 | タスク13・16に、状態ごとの出力を確認する JUnit を先に作り、RED を確認してから実装し、GREEN と回帰（mvn test）を確認する旨を足す。タスク13の git diff の条件は「実装先のファイルと、本タスクで追加するテストファイル以外に変更が無い」に直す。 | 修正：タスク内で完結する書き方に揃える（修正案のとおり） | 確認済み |  |  |
| 7 | traceability | 業務のあいまい・不足 | 要判断 | df4f8882335a92b6 | d5a8e1da45c02a6a | specs/application-status-search/tasks.md § ドメイン / ビジネスロジック / 11 | AC 3.3 | AC3.3（CSVの範囲は検索と同じ）がタスク11の完了条件で確認されない | AC 3.3「CSV に出す範囲は、…画面の検索と同じ条件・絞り込み・上限件数にしなければならない」は _Requirements に挙がり、タスク11の本文にも書かれている。しかし完了条件のケース（見出し 14 列・ダブルクォート・CRLF・ファイル名・0 件と上限超えで見出しだけ・入力エラーで出力しない）に、社外ユーザーの範囲（括弧付き）と同じ条件で CSV が絞られること、検索と同じ上限件数で打ち切られることを確かめる項目が無い。タスク9の完了条件は検索側（externalScope）だけ、タスク5の完了条件も SQL の定義の有無だけを対象とする。ID 対応はあるが完了条件による充足が無い（ID 対応あり・内容未充足）。 | タスク11の完了条件に「社外ユーザーの範囲と上限件数が検索と同じ条件で CSV にも掛かる」ケースを足す。 | 修正：完了条件にケースを足す（修正案のとおり） | 確認済み |  |  |
| 8 | traceability | 業務のあいまい・不足 | 要判断 | ad0d0650fac947dd | 22f4c064a77db8e5 | specs/application-status-search/tasks.md § 本計画の前提と規約（画面設計工程の成果物の扱い） / 対象の範囲 | P01 行とメニュー登録 | P01行とメニュー・ZMENUAUTH登録の担当が未タスク化で不明 | design.md「責務境界」の所有するデータに、コードマスタ WTZ/PARAM/P01 のこの画面の行（キー3＝PWTGO060、数値項目1＝50）を挙げ、「移行方針」の段階分けと「移行対象ファイル一覧」にも P01 の行とメニュー・ZMENUAUTH（PWTGO060）の行の追加（2 行）を書く。tasks.md は「ほかのコードマスタの行・ほかの画面と同じ扱いで行うため本計画のタスクにしない。Service の事前条件として扱う」とし、タスク1の確認対象にも P01・P02・メニュー・ZMENUAUTH の存在確認が含まれない。design 側も「同じ扱いで登録」と担当者・時期を書かず、Out of Boundary では P01 の委譲先を PJ45 としている（メニュー・ZMENUAUTH は委譲先の記載が無い）。結果として、検索の 1 ページ件数 50 や画面を開くためのメニュー行が無い状態でタスク14・15 の動作確認や全体結合確認（タスク17）に進むおそれがある。tasks が外すこと自体は design の書き方に沿うが、誰がいつ登録し、確認がどのタスクにあるかが tasks から読み取れない。 | 質問：(a) 登録は PJ45 側が行うと確認でき、タスク1で P01・P02・メニュー・ZMENUAUTH の行の存在確認を足す。(b) 本 feature のタスクとして登録（または登録用の SQL の作成）を追加する。のどちらかを決める。 | 質問：登録の担当が design からも tasks からも決まらないため | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | 人間による確認（steering の例外化は Phase 2 の steering 変更、または質問 Q-TK-AS-003 の選び直し） | steering/product.md の改修対象の定めと、画面設計書に合わせて共通シェルを改修する方式の食い違いは、tasks だけでは解決できない。design・docs/ も再集約の対象になりうる（下流の無効化は L3 が行う） |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| verifiable-criteria-check | specs/application-status-search/tasks.md § 横断確認 / 17 | タスク17の起動完了判定と1経路を /menu の HTTP 200 とする点（DB・認証依存の有無は smoke 実行時に確認する旨の記載を含む。servlet-context.xml のセッション検査から /menu が外れていない点も、人の回答 B と同じ範囲） | answer:tasks-authoring-generate[application-status-search] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 5 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-13T09:48:02+09:00 |  |  |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 5 | feature:application-status-search | 3 | system（自動）：同じ指摘を 3 回目 #5 へ引き継ぎ | 2026-10-13T09:48:02+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase:application-status-search | 1 | 2026-10-13T09:49:21+09:00 | ② | ["specs/property-basic-info/tasks.md","specs/application-status-search/tasks.md"] | {"specs/property-basic-info/tasks.md":"cdb8225f3bca7310e8613e1e81869b1d932073f507d85110c0a832ca448d076c","specs/application-status-search/tasks.md":"afa2de5e7a5a68130f521be7e70f213ed05dd075bd087cf90020e023a9dd8a59"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務のあいまい・不足 | 要判断 | 4ca345ba48fbf250 | 722551a3a5f065c0 | specs/property-basic-info/tasks.md § 上流との食い違い・不足の扱い（タスクで吸収せず記録する事項） / タスク 28 | /wtg070/returnList の戻り先 | pbi の tasks は戻り先を固定せず、利用側の /wtg060/return と食い違う | 提供側 pbi の tasks（上記節・タスク 24・28）は returnList・deleteShinse 後の戻り先を「実装時点の承認済み design の記載に従う」とし、完了条件は「申請状況一覧への戻り先を返す」までで値を固定しない。承認済み pbi design（§ API 契約 /wtg070/returnList）は戻り先を `/wtg060` と書く。利用側 application-status-search の tasks はタスク 14（戻りは `/wtg060/return` 向け）・タスク 15（口 `/wtg060/return`）で `/wtg060/return` を前提にし、同 design は `returnList → /wtg060/return`、deleteShinse 後も `/wtg060/return` で受けるとする。pbi design の改訂は Phase 5 の最後に行う持ち越し（upstream-carryover）として両者に記録済みだが、改訂前は 2 つの tasks のどのタスクの完了条件も、戻り先が /wtg060/return であることを確かめない。pbi 側を /wtg060 のまま実装すると要件 2.10（戻ったとき前の検索条件で再検索）が満たされない恐れがある。両 feature の依存順（pbi が先）には矛盾なし。意味判定：ID 対応あり・契約内容は未整合。 | pbi design の戻り先を `/wtg060/return` に改訂した後、pbi タスク 28 の完了条件に「returnList と deleteShinse の戻り先が `/wtg060/return` である」を足す（改訂前は、実装時点の design に従うとの記載を維持）。 | 差戻し：原因は承認済み pbi design の戻り先の記載にあり、改訂（持ち越し済み）後に tasks の完了条件へ反映する | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | Phase 5 design（property-basic-info の `/wtg070/returnList` の戻り先） | 原因は承認済み pbi design が戻り先を `/wtg060` と書き、利用側 design の `/wtg060/return` と食い違っていること。 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 5 | 修正 | AI 推奨を採用: 参照先の書き方を前提節に明記する（修正案のとおり） | masato-teramoto | 2026-10-13T09:55:31+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 6 | 修正 | AI 推奨を採用: タスク内で完結する書き方に揃える（修正案のとおり） | masato-teramoto | 2026-10-13T09:55:48+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 7 | 修正 | AI 推奨を採用: 完了条件にケースを足す（修正案のとおり） | masato-teramoto | 2026-10-13T09:56:05+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 1 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | masato-teramoto | 2026-10-13T09:56:22+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 2 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | masato-teramoto | 2026-10-13T09:56:39+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 3 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | masato-teramoto | 2026-10-13T09:56:56+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 4 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | masato-teramoto | 2026-10-13T09:57:13+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 8 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | masato-teramoto | 2026-10-13T09:57:30+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| phase:application-status-search | 1 | 1 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | masato-teramoto | 2026-10-13T09:57:47+09:00 | 対象外 |  | 不採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 4 | 2026-10-13T10:03:11+09:00 | ①② | ["specs/application-status-search/tasks.md"] | {"specs/application-status-search/tasks.md":"9528a62453577fce9ec8b3d4ac45de0af705fdc0413183c4acbf6c1690ec87c3"} | 2 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 文書間の参照 | 軽微 | a423e68a14b7b975 | cc783d9e2fd59339 | specs/application-status-search/tasks.md § 共通（_app-shell） / 13 | Boundary の書き方 | タスク13の Boundary 行が前提節の「_app-shell とする」と不一致 | 前提節「UI タスクの単位と範囲」は「タスク 13 の `_Boundary:` は `_app-shell` とする」と定める。タスク13の実際の行は `_Boundary: _app-shell（共通シェル・入口・システムエラー。design.md のコンポーネント一覧に無く、前提節「_app-shell の Boundary の扱い」の例外のとおり、根拠は画面マップ §4 と _app-shell/screen-spec.md）_` で、名前の後ろに長い括弧書きが付き、前提節の記述と一致しない。前回の修正で前提節とタスク13を整えた際に残った食い違い。 | Boundary 行を `_Boundary: _app-shell_` のみにし、根拠の説明は前提節に任せる（説明は既に前提節にある）。 | 修正：前提節の規約どおり名前だけにすれば食い違いが無くなり、機械が読む注記の形も保てる | 確認済み |  |  |
| 2 | format-conformance | 書式 | 軽微 | 43ab9a3b71d3843b | cc783d9e2fd59339 | specs/application-status-search/tasks.md § 共通（_app-shell） / 14 | 章の見出し | タスク14〜16が章「共通（_app-shell）」に入り前提節の章分けと不一致 | 前提節「UI タスクの単位と範囲」は、状態管理・API 接続・ルーティングを「通常の実装タスクとして同じ章（画面）に並べる（タスク 14・15）」と書く。実際は章「共通（_app-shell）」（_app-shell の共通タスク 13 のための章）の下に、本 feature の Service（14）・Controller（15）・画面（16）が続き、章の名前と内容、前提節の「同じ章（画面）」と合わない。テンプレートの章は着手順の目安で、タスク番号は章をまたいで移しても変えない。依存の番号順（14 は 5〜10、15 は 11・12・14、16 は 13・15 に依存）は章を分けても崩れない。 | タスク 14 の前に章見出し（例「### 申請状況検索一覧（画面）」）を足し、14〜16 をそこへ移す。番号と依存は変えない。 | 修正：見出しの追加だけで直り、番号・依存・完了条件に影響しない | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 4 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-13T10:09:36+09:00 |  |  |  |
| feature:application-status-search | 4 | 2 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-13T10:09:36+09:00 |  |  |  |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase:application-status-search | 2 | 2026-10-13T10:11:00+09:00 | ② | ["specs/property-basic-info/tasks.md","specs/application-status-search/tasks.md"] | {"specs/property-basic-info/tasks.md":"cdb8225f3bca7310e8613e1e81869b1d932073f507d85110c0a832ca448d076c","specs/application-status-search/tasks.md":"9528a62453577fce9ec8b3d4ac45de0af705fdc0413183c4acbf6c1690ec87c3"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 5 | 2026-10-13T10:21:12+09:00 | ①② | ["specs/application-status-search/tasks.md"] | {"specs/application-status-search/tasks.md":"b6e72aeac74f8513920d8d76fbe4cfd0841afbbe6fd3eb4276e0a19f77e50862"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 文書間の参照 | 軽微 | 4227bc5fa76ce462 | 2173e89361e18b77 | specs/application-status-search/tasks.md § 申請状況検索一覧（画面） / 14 | Depends の書き方 | タスク14の完了条件が11・12の成否を含むが Depends に無い | タスク 14 の完了条件に「`mvn -f wing/pom.xml test -Dtest=Pwtgo060ServiceTest` が、タスク 6〜12 の分を含めて全件成功する」とあるが、タスク 14 の `_Depends: 5, 6, 7, 8, 9, 10_` にはタスク 11（outputCsv）・12（checkImporting）が無い。タスク 11 は 5・7・8・9・10 に、12 は 2 に依存するだけで、14 には依存されない。番号順では 11・12 が先に終わるが、Depends の記載だけでは 14 が 11・12 の完了を前提とすることが読み取れない。要件 AC の網羅（1.x〜4.1）や番号順・循環には影響しない。 | タスク 14 の完了条件の「タスク 6〜12 の分を含めて」を「タスク 6〜10 の分を含めて」に直す。または Depends に 11, 12 を足す（番号順・循環は崩れない）。 | 修正：どちらの直しも 1 行で済み、番号・要件 ID・他タスクの依存に影響しない | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 5 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-13T10:25:58+09:00 |  |  |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 5 | feature:application-status-search | 5 | system（自動）：再検査で再検出なし | 2026-10-13T10:25:58+09:00 |
| feature:application-status-search | 3 | 6 | feature:application-status-search | 5 | system（自動）：再検査で再検出なし | 2026-10-13T10:25:58+09:00 |
| feature:application-status-search | 3 | 7 | feature:application-status-search | 5 | system（自動）：再検査で再検出なし | 2026-10-13T10:25:58+09:00 |
| feature:application-status-search | 4 | 1 | feature:application-status-search | 5 | system（自動）：再検査で再検出なし | 2026-10-13T10:25:58+09:00 |
| feature:application-status-search | 4 | 2 | feature:application-status-search | 5 | system（自動）：再検査で再検出なし | 2026-10-13T10:25:58+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase:application-status-search | 3 | 2026-10-13T10:27:30+09:00 | ② | ["specs/property-basic-info/tasks.md","specs/application-status-search/tasks.md"] | {"specs/property-basic-info/tasks.md":"cdb8225f3bca7310e8613e1e81869b1d932073f507d85110c0a832ca448d076c","specs/application-status-search/tasks.md":"b6e72aeac74f8513920d8d76fbe4cfd0841afbbe6fd3eb4276e0a19f77e50862"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 6 | 2026-10-13T10:36:47+09:00 | ①② | ["specs/application-status-search/tasks.md"] | {"specs/application-status-search/tasks.md": "30ce9cd5893e48dac13b5f9cd277731a74a87cc9c81bbc8a5087074c0c916a28"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 5 | 1 | feature:application-status-search | 6 | system（自動）：再検査で再検出なし | 2026-10-13T10:40:19+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase:application-status-search | 4 | 2026-10-13T10:41:40+09:00 | ② | ["specs/property-basic-info/tasks.md","specs/application-status-search/tasks.md"] | {"specs/property-basic-info/tasks.md":"cdb8225f3bca7310e8613e1e81869b1d932073f507d85110c0a832ca448d076c","specs/application-status-search/tasks.md":"30ce9cd5893e48dac13b5f9cd277731a74a87cc9c81bbc8a5087074c0c916a28"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 1 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | masato-teramoto | 2026-10-13T10:46:55+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 2 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | masato-teramoto | 2026-10-13T10:47:16+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 3 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | masato-teramoto | 2026-10-13T10:47:33+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 4 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | masato-teramoto | 2026-10-13T10:47:50+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 8 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | masato-teramoto | 2026-10-13T10:48:08+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 6 | 対応せず進める | 同内容の指摘は 3 回目で修正済み（再検査で解消確認済み） | masato-teramoto | 2026-10-13T10:48:26+09:00 | 解釈で対応 |  | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 7 | 対応せず進める | 同内容の指摘は 3 回目で修正済み（再検査で解消確認済み） | masato-teramoto | 2026-10-13T10:48:44+09:00 | 解釈で対応 |  | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 1 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | masato-teramoto | 2026-10-13T10:49:01+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 2 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | masato-teramoto | 2026-10-13T10:49:18+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 3 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | masato-teramoto | 2026-10-13T10:49:35+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 4 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | masato-teramoto | 2026-10-13T10:49:52+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 8 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | masato-teramoto | 2026-10-13T10:50:08+09:00 | 対象外 |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 6 | 対応せず進める | 同内容の指摘は 3 回目で修正済み（再検査で解消確認済み） | masato-teramoto | 2026-10-13T10:50:25+09:00 | 解釈で対応 |  | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 7 | 対応せず進める | 同内容の指摘は 3 回目で修正済み（再検査で解消確認済み） | masato-teramoto | 2026-10-13T10:50:46+09:00 | 解釈で対応 |  | 不採用 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase:application-status-search | 4 | specs/application-status-search/tasks.md | masato-teramoto | 2026-10-13T10:51:35+09:00 | 30ce9cd5893e48dac13b5f9cd277731a74a87cc9c81bbc8a5087074c0c916a28 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 8 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10）。3 回目と同じ判断 | phase:application-status-search | 4 |
| feature:application-status-search | 3 | 1 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | phase:application-status-search | 4 |
| feature:application-status-search | 3 | 2 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | phase:application-status-search | 4 |
| feature:application-status-search | 3 | 3 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | phase:application-status-search | 4 |
| feature:application-status-search | 3 | 4 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | phase:application-status-search | 4 |
| feature:application-status-search | 3 | 8 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | phase:application-status-search | 4 |
| phase:application-status-search | 1 | 1 | 対応せず進める | 推奨が質問または差戻し先が他 feature・steering のため、対象外とする（ユーザー指示 2026-10-10） | phase:application-status-search | 4 |
