# 上流をまとめて開き直すときに直す項目（Phase 5 の最後に 1 回で行う。回答者 Junichi Noumi の指示）

## steering
- security.md 285 行目「ログインユーザーのグループ」→「権限区分（TWTZM010.Kengen_Kbn）」（Q-DS-PBI-009）
- security.md 権限モデル：TWTGM170 の権限ID は専用の値（1:稟議依頼-申請者〜5:再製本-承認者）。番の判定は TWTGM170、P82 は承認履歴の審査権限（pbi design 検査 5-3）
- security.md 攻撃対策：CSRF は servlet-context.xml の末尾一致の対象だけを照合する（pbi design 判断 4、検査 3-3）
- tech.md：開発端末のテスト実行は JDK 1.8 で -source/-target 1.7（検査 2-7）
- tech.md：画面の業務エラー・排他は BindingResult で返してよい場合（検査 3-2）
- database.md：依頼内容は名称の文字列（"稟議依頼"・"再製本依頼"）で持つ例外（検査 2-11）
- database.md：判定・権限ID は DB レイアウトの備考で管理、連番・SEQ・審査回・通番は Int の例外（検査 2-12）

## requirements（property-basic-info）
- 1.3・6.7・14.5 に「稟議依頼・修正稟議依頼の起案済・回覧中を除く」を足す（検査 5-1）
- 14.5 に「契約局情報追加は複数局のときだけ」を足す（検査 5-2）
- 前提（106 行目）の「P82 の 02〜04」を TWTGM170 専用の権限ID に書き換える（検査 5-3）

## Phase 4 からの持ち越し（2026-10-07 回答者の指示で一覧に追加）
- steering non-functional.md：「出力しない」項目に担当者の氏名を足す（security.md の機密データの扱いとそろえる）
- feature 一覧：TWTGM100 の注記に、契約情報取込が発行依頼書を洗い替えすること（全削除→再登録）を足す（Phase 4 contract-info-import 2 回目 #13 で C にしたもの）

## 物件基本情報登録変更の design（承認済み。開き直して直す。2026-10-07 回答者の指示と調査）
- 採番マスタの申請No の行の MAX区分を "0"（ローテーション無し。NumberingService.java:56-60 のとおり）に直す（Q-DS-IR-012 の回答）
- 発行依頼書登録変更への遷移：GET で applicationNo・renban・transitionSource（1＝基地局番号リンク、2＝発行依頼書編集、3＝契約局情報追加）を渡す。戻りは物件基本情報登録変更の初期表示へ申請No を渡す入口（Q-DS-IR-002）
- 修正稟議・再製本の複製で TWTGM100 の申請者（Application_Name）にログインユーザーのユーザーID を入れる（issue-request 7.5、Q-DS-IR の「他の feature に関わる点」）
- recordNumbering は発番日時（システム日時）と更新者名も入れる。承認履歴は判定 "11"・審査権限 "02"（Q-DS-IR-012）
- WTX-100011・WTX-100012・WTX-100005・WTG-100018 は wing の messages.properties に無い（既存と書いた誤り）
- WTX-100005：pbi design の「既存」を「新規（Warning。チュートリアルと共通で 1 回だけ足す）」に直し、pbi の変更する既存ファイル（messages.properties）で追加する（tutorial design-check 1 回目 #3 の判断、2026-10-08）
- /wtg072/search の入力を 3 つ（hdnApplicationNo・hdnBrowseBtnClickFlag（"1"＝閲覧、それ以外＝印刷）・hdnSingleDepSwitchClickFlag（単独複数局フラグ））にし、GET と POST の両方を受ける。閲覧は /zoom/wait を "zoom" のウインドウで開いて target 指定で送る（ZOOM_DEFINE.zwtz072=1100px,600px）、印刷は target なしで送る（Q-DS-PR-009、2026-10-08 に置き換え）
- 申請情報欄の基地局番号の初期表示：発行依頼書（TWTGM100）がある申請では、契約局情報の連番 1 の基地局番号を表示する。無い申請は今までどおり TWTGM080 の値。更新でその値が TWTGM080 に入り WTG-100019 も通る（Q-DS-IR-021、2026-10-08）
- getApplication の出力に単独複数局ﾌﾗｸﾞ（Tandoku_Fukusu_Flg）と申請依頼日時（Application_Req_DateTime）を明記する（Q-DS-IR-022 の 2.、2026-10-08）
- WTG 申請状態サービスに読み取りの口 getApplicantName を足す。入力：会社コード・申請No。出力：TWTGM180 の行のうち審査回＝今の申請回数・判定 "02" で最終更新日時がいちばん新しい行の Last_UpdatedPerson_Name（無ければ空。ZM010 と結合しない）（Q-DS-IR-022 の 3.、2026-10-08）

## issue-request の design で意図して外れたもの（2026-10-07、回答 answer-ds-ir-20261007-1959.txt による）
- requirements（issue-request）1.3・1.5：起案済・回覧中の申請者が発番で 担当エリア・契約区分・代表局番号・枝番 を保存する
- requirements（issue-request）9.3：「起案済の申請を更新するとき」を「起案済の申請で発番するとき」と読む
- requirements（issue-request）9.6：所属①②の必須は、社内ユーザーで社内の会社を選んだときだけ
- requirements（issue-request）2.1：「本人が登録した発行依頼書」は TWTGM080.RegisteredPerson で比べる
- requirements（issue-request）1.9：契約局情報追加は発行依頼書が登録済みの申請だけ（design-check 4 回目 #1 の判断、2026-10-08）
- requirements（issue-request）8.1：ログインユーザーのグループ→権限区分（文言は steering security.md 285 行目と一緒に直す。design-check 1 回目 #3 の判断、2026-10-08）
- steering database.md：トランの表の種別 V（TWTGV030・TWTGV050。既存 wing にも TWTDV021 などがある）
- steering database.md：金額・調整額を文字列で持つ（データリストの「無償」など）

## requirements（issue-request-tutorial）で意図して外れたもの（2026-10-08、回答 answer-ds-tu-20261008-1138.txt による）
- 1.3：画面は 14 ではなく 11。設置設備のRRH数・設置設備のSystem構成・UPS工事の 3 画面は使わない（業務の見直しで廃止）
- 1.8：「鋼管柱」は KDDI⇒UQ のときだけ出す（OCT⇒UQ・UQ⇒KDDI・UQ⇒OCT では出さない）。「エントランス増設工事・UPS工事のみ」は 1.8 のとおり
- 1.9：UPS工事の画面が無いので削る
- 1.10：ブラウザーの × で閉じることは防げない（Q-DS-TU-001）
- 2.1：入れる項目に「転貸情報の有無」を足す（8 項目。Q-DS-TU-005）
- 2.2：設計で「空にする」と決めた操作（設置設備・電気料を消す）は「入れる値が空なら変えない」の例外（Q-DS-TU-005）
- ir design（issue-request）：チュートリアルとの受け渡しに「空にする」の印 json.clear（項目名の配列）を足す。入れる先が入力できないときは入れない。契約種別を受け取ったときは契約種別の変更時の処理（リストの入れ直し・ラベル・入力可否）を先に動かしてから残りの値を入れる（今は値を入れた後にリストを入れ直す）。契約種別の変更時の電気料のリスト・ラベル・入力可否の切替と、賃料のカンマ・着工予定日の保存の形への変換を親画面が行うことも書く。コールバック名は pwtgo081callback（tutorial design、Q-DS-TU-005・Q-DS-TU-007、2026-10-08）
- steering api-standards.md：画面内で JSON を返す口が増える（/wtg081/next。issue-request の /wtg080/calcTaxAdjustment・/wtg080/changeKeiyakuSyubetsuTutorial も同じ）（Q-DS-TU-002・Q-DS-TU-008、2026-10-08）

## requirements（print-report）・steering で意図して外れたもの（2026-10-08、回答 answer-ds-pr-20261008-1225.txt による）
- requirements（print-report）1.10：製本の情報と添付資料は発行依頼書のページに出さない（その行は隠す）。表紙に出す（Q-DS-PR-005）
- requirements（print-report）3.3：代表局の稟議バーコードNo が万一空のときは、ファイル名を「申請No.pdf」にする（Q-DS-PR-010）
- steering tech.md の zxing 3.4.1 は変えない。本番の Java の版で動くかは導入のときに発注者の環境で確かめる（Q-DS-PR-015）
- steering tech.md：帳票のテンプレートは .xlsx としているが、原本は利用者が今使っている .xlsm（BaseStationRentContractIssuingOrderForm.xlsm）を POI 3.17 で開いて使う（print-report design、Q-DS-PR-001、2026-10-08）

## requirements（application-status-search）で意図して外れたもの（2026-10-08、回答 answer-ds-as-20261008-1504.txt による）
- 1.1：進捗検索(選択) の初期値は「以上」。社外ユーザーの起案会社は自社の名前を入れて表示する（1.6 の「変更させない」に合わせた初期値）
- 2.3：「他n局」は基地局名だけでなく基地局番号にも付ける（Q-DS-AS-006）
- 3.1：CSV の 13 列目の見出しは「発注希望日」（画面の列見出しは「発送希望日」のまま。Q-DS-AS-010）
- pbi design：「既存の WTG-100018」を「application-status-search で新規追加する WTG-100018」に直す（Q-DS-AS-009）
- pbi design：/wtg070/returnList の戻り先を /wtg060 から /wtg060/return に直す（/wtg060 は検索条件のセッションを消す初期表示。application-status-search design-check 1 回目 #1、2026-10-08）

## contract-info-import の design で意図して外れたもの（2026-10-08、回答 answer-ds-ci-20261008-1551.txt による）
- pbi design（391 行目付近）：「契約情報取込で読める形」を「2 行目以降の 228 列が取込の 228 列と同じ並び（1 行目の 188 列は見出し行に置き換える必要がある）」と直す。取込の側は requirements 2.1 のとおり（Q-DS-CI-002）
- pbi design：「契約文書情報（TWTGM110）の行は物理削除しない」に、契約情報取込は例外（稟議バーコードNo が TWTGM140 に無くなった行を物理削除する）と並べて書く（Q-DS-CI-009）
- steering non-functional.md（ログに住所を出さない）：取込の警告 WTG-200009・WTG-000072 は行番号と郵便番号・都道府県・市区町村・字、番地の値をバッチ処理状況の詳細に出す（Q-DS-CI-012）
- steering security.md（担当者の氏名は機密）：取込のタスクのパラメータに申請者と起案者の氏名を入れ、バッチ処理状況一覧に出る（Q-DS-CI-015 の 6）
- requirements（contract-info-import）2.6：受付No が空のときとリバースデータのときは稟議バーコードNo を付けない（Q-DS-CI-004、design-check 1 回目 #1）
- steering non-functional.md・security.md（契約者の連絡先をログに出さない）：取込の WTG-200011 は行番号と電話番号の値をバッチ処理状況の詳細に出す（Q-DS-CI-012 の 3、design-check 1 回目 #5）
- 回答 Q-DS-CI-012 の 5 の「警告だけのときは正常終了」は「警告終了を受け入れる」に変わった（design-check 1 回目 #7。上流の文書の直しは無いが、記録として）

## contract-info-download の design で意図して外れたもの（2026-10-08、回答 answer-ds-cd-20261008-1845.txt による）
- requirements（contract-info-download）1.3：検索条件の「代表契約局番号」と「代表契約枝番」は、GWTG004 の一致ではなく前方一致にする。「転貸借契約書名」は GWTG004 に無いので、Q-DS-CD-004 で定める（コンボボックス、`WTG/PARAM/P15`、`TWTGM010.MOVE_LEASE_CONTRACT` と一致）
- requirements（contract-info-download）2.1・2.2：「計画マスタ（`TWTBM080`）」は「工事案件マスタ（`TWTBM080`）」の書き誤り。条件は「工事案件マスタに行が無い、または値のある区分に合う行がある」
- requirements（contract-info-download）4.1：サーバーでは検索条件の桁と形式のチェックをしない。画面の入力桁（maxlength）と IME の入力モードで、桁を超えて入力させないことで満たす（Q-DS-CD-005）
- steering security.md 285 行目（既存の契約情報の絞り込み「既存の WTB と同じ方式」）：比べる列と、値のある区分だけで絞る点は既存の WTB と同じ。ただし工事案件マスタ（`TWTBM080`）に行が無い契約情報は出す点が既存の WTB（`EXISTS` だけ）と違う
- 全機能をまたいだ確認で：契約情報ダウンロードの出力の定義（specs/contract-info-download/csv-layout-wtg100.md）と契約情報取込のリバースの表の列の並びが同じであることを確かめる（取込の design は直さない。Q-DS-CD-001 の 6）
- steering security.md の `### 入り口 — 入力検証`（画面の層の桁数・形式のチェック）と `### 共通ルール` 1（入力はサーバー側で必ず検査する）：契約情報ダウンロードはサーバーで検索条件の桁・形式を確かめない（Q-DS-CD-005、design-check 1 回目 #4）
- pbi design（576 行目付近「/wtg100 を別ウインドウで開き、申請No だけを渡す」）：`/wtg100?FunctionID=WTG100&applicationNo=<申請No>` で開くと直す（FunctionID とパラメータ名 applicationNo を足す。契約情報ダウンロード design-check 1 回目 #6）
