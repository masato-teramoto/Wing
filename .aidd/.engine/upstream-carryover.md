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
- /wtg072/search が閲覧か印刷かを受け取れない（Q-DS-PR-009）

## issue-request の design で意図して外れたもの（2026-10-07、回答 answer-ds-ir-20261007-1959.txt による）
- requirements（issue-request）1.3・1.5：起案済・回覧中の申請者が発番で 担当エリア・契約区分・代表局番号・枝番 を保存する
- requirements（issue-request）9.3：「起案済の申請を更新するとき」を「起案済の申請で発番するとき」と読む
- requirements（issue-request）9.6：所属①②の必須は、社内ユーザーで社内の会社を選んだときだけ
- requirements（issue-request）2.1：「本人が登録した発行依頼書」は TWTGM080.RegisteredPerson で比べる
- steering database.md：トランの表の種別 V（TWTGV030・TWTGV050。既存 wing にも TWTDV021 などがある）
- steering database.md：金額・調整額を文字列で持つ（データリストの「無償」など）
