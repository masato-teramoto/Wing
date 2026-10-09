# 契約情報ダウンロード（WTG100）作業用テーブルとビュー

> 回答者 Junichi Noumi が渡した作業用テーブルとビュー（`_handoff/work-tables-wtg100.md`、Q-DS-CD-002 の回答の別表。design-check 1 回目・2 回目の判断と design 横断確認 1 回目 #1 の判断のときに差し替え）を、本 feature の補足資料として写したもの。design.md が参照する正。

Q-DS-CD-002 の回答の別表。新しく作るのは次の 3 つ。

| 名前 | 種類 | 中身 |
|---|---|---|
| TWTGD050 発行依頼書リバースデータ | テーブル（作業用） | 選んだ契約の基本情報・契約者・支払情報を、VWTGM010 から 1 行ずつ写したもの（データ種別で列の意味が変わる） |
| TWTGD060 発行依頼書フォーマット | テーブル（作業用） | CSV の 1 行（契約 1 件）。実行ユーザーID（USER_ID、String 20）＋CSV の 381 列（全部 String 500）。列は `csv-layout-wtg100.md` の「値を取る列」「物理名」のとおり |
| VWTGM010 発行依頼書リバースデータビュー | ビュー | TWTGM010・TWTGM020・TWTGM030 とコードマスタから、データ種別ごとに同じ列の形にそろえたもの |

- どれも主キー・一意キー・索引・外部キーを持たない。共通列（会社コード・登録者・登録日時・更新者・更新日時・排他フラグ）も持たない。
- 行は実行ユーザーID で分ける。

## 出力ボタンを押したときの流れ
1. TWTGD050・TWTGD060 から、ログインユーザーの USER_ID の行を消す。
2. TWTGD050 を作る：VWTGM010 から、選んだ行（基地局番号＋枝番）の行を全部（1基本情報・2契約者・3支払情報）入れる。USER_ID はログインユーザー。
3. TWTGD060 を作る：TWTGD050 の「1基本情報」の行から 1 契約 1 行で入れる（実行ユーザーID と、契約基本の 46 列＝CSV の No 1〜46）。
4. TWTGD060 の契約者①〜⑤を埋める：TWTGD050 の「2契約者」の行のうち、処理順2（SYORI_JYUN2）が 1〜5 のものを、計画基地局番号＋枝番で突き合わせて更新する。
5. TWTGD060 の支払情報①〜④を埋める：TWTGD050 の「3支払情報」の行のうち、処理順2 が 1〜4 のものを同じように更新する。
6. TWTGD060 のログインユーザーの行を CSV の並び順で読み、CSV にする。
- 行は消さずに残し、次の出力のときに 1. で消す。

## VWTGM010 の絞り込みと処理順2
- 1基本情報：TWTGM010 の全行。処理順2 は 1。
- 2契約者：TWTGM010 と TWTGM020 を内部結合。関係_地位（RELATION）に「旧」を含む行は除く。処理順2 は 計画基地局番号＋枝番ごとに 契約者区分・契約者番号 の昇順で振った番号。
- 3支払情報：TWTGM010 と TWTGM030 を内部結合。支払有効期間TO（PAY_EFFECTIVE_TO）が空の行だけ。処理順2 は 計画基地局番号＋枝番ごとに 支払内容区分 の昇順で振った番号。
- 下の列一覧の「処理順_帳票用」の欄は 3 つとも同じ式に見えるが、実際の式は上のとおり（ビューの DDL はこの式で作る）。
- 検索条件_確定局番 は 3 種類とも契約基本情報の基地局番号（KICHIKYOKU_NO）。

## TWTGD050 発行依頼書リバースデータ（作業用。主キー・一意キー・索引なし）

| No | 論理名 | 列名 | 型 | 桁 | 備考 |
|---|---|---|---|---|---|
| 1 | 実行ﾕｰｻﾞｰID | USER_ID | 1:String | 20 |  |
| 2 | データ種別 | DATA_SHUBETSU | 1:String | 9 | 1基本情報 2契約者情報 3支払情報 |
| 3 | 処理順 | SYORI_JYUN | 1:String | 85 |  |
| 4 | 計画基地局番号 | KEIKAKU_KICHIKYOKU_NO | 1:String | 9 |  |
| 5 | 計画基地局枝番 | PLAN_SITEID_BRANCH | 1:String | 5 |  |
| 6 | 項目1 | FIELD_01 | 1:String | 120 | 項目1～項目50の保持する内容は、データ種別により異なる。 詳細は発行依頼書ﾘﾊﾞｰｽﾃﾞｰﾀビューを参照 |
| 7 | 項目2 | FIELD_02 | 1:String | 120 |  |
| 8 | 項目3 | FIELD_03 | 1:String | 40 |  |
| 9 | 項目4 | FIELD_04 | 1:String | 120 |  |
| 10 | 項目5 | FIELD_05 | 1:String | 120 |  |
| 11 | 項目6 | FIELD_06 | 1:String | 160 |  |
| 12 | 項目7 | FIELD_07 | 1:String | 160 |  |
| 13 | 項目8 | FIELD_08 | 1:String | 160 |  |
| 14 | 項目9 | FIELD_09 | 1:String | 50 |  |
| 15 | 項目10 | FIELD_10 | 1:String | 50 |  |
| 16 | 項目11 | FIELD_11 | 1:String | 50 |  |
| 17 | 項目12 | FIELD_12 | 1:String | 100 |  |
| 18 | 項目13 | FIELD_13 | 1:String | 100 |  |
| 19 | 項目14 | FIELD_14 | 1:String | 100 |  |
| 20 | 項目15 | FIELD_15 | 1:String | 160 |  |
| 21 | 項目16 | FIELD_16 | 1:String | 100 |  |
| 22 | 項目17 | FIELD_17 | 1:String | 100 |  |
| 23 | 項目18 | FIELD_18 | 1:String | 160 |  |
| 24 | 項目19 | FIELD_19 | 1:String | 50 |  |
| 25 | 項目20 | FIELD_20 | 1:String | 500 |  |
| 26 | 項目21 | FIELD_21 | 1:String | 160 |  |
| 27 | 項目22 | FIELD_22 | 1:String | 10 |  |
| 28 | 項目23 | FIELD_23 | 1:String | 240 |  |
| 29 | 項目24 | FIELD_24 | 1:String | 200 |  |
| 30 | 項目25 | FIELD_25 | 1:String | 200 |  |
| 31 | 項目26 | FIELD_26 | 1:String | 200 |  |
| 32 | 項目27 | FIELD_27 | 1:String | 200 |  |
| 33 | 項目28 | FIELD_28 | 1:String | 40 |  |
| 34 | 項目29 | FIELD_29 | 1:String | 40 |  |
| 35 | 項目30 | FIELD_30 | 1:String | 2 |  |
| 36 | 項目31 | FIELD_31 | 1:String | 50 |  |
| 37 | 項目32 | FIELD_32 | 1:String | 100 |  |
| 38 | 項目33 | FIELD_33 | 1:String | 100 |  |
| 39 | 項目34 | FIELD_34 | 1:String | 6 |  |
| 40 | 項目35 | FIELD_35 | 1:String | 50 |  |
| 41 | 項目36 | FIELD_36 | 1:String | 9 |  |
| 42 | 項目37 | FIELD_37 | 1:String | 6 |  |
| 43 | 項目38 | FIELD_38 | 1:String | 20 |  |
| 44 | 項目39 | FIELD_39 | 1:String | 50 |  |
| 45 | 項目40 | FIELD_40 | 1:String | 100 |  |
| 46 | 項目41 | FIELD_41 | 1:String | 100 |  |
| 47 | 項目42 | FIELD_42 | 1:String | 100 |  |
| 48 | 項目43 | FIELD_43 | 1:String | 200 |  |
| 49 | 項目44 | FIELD_44 | 1:String | 200 |  |
| 50 | 項目45 | FIELD_45 | 1:String | 200 |  |
| 51 | 項目46 | FIELD_46 | 1:String | 200 |  |
| 52 | 項目47 | FIELD_47 | 1:String | 4 |  |
| 53 | 項目48 | FIELD_48 | 1:String | 50 |  |
| 54 | 項目49 | FIELD_49 | 1:String | 30 |  |
| 55 | 項目50 | FIELD_50 | 1:String | 30 |  |
| 56 | 検索条件_登録状態 | STATUS_KIND | 1:String | 50 |  |
| 57 | 検索条件_代表契約局番 | REPRESENT_CONTRACT_NO | 1:String | 9 |  |
| 58 | 検索条件_代表契約枝番 | REPRESENT_CONTRACT_BRANCH_NO | 1:String | 5 |  |
| 59 | 検索条件_確定局番 | KICHIKYOKU_NO | 1:String | 9 |  |
| 60 | 処理順2 | SYORI_JYUN2 | 5:Currency | 5 |  |

## VWTGM010 発行依頼書リバースデータビュー（3 つの SELECT を UNION ALL。データ種別で列の意味が変わる）

| No | 1基本情報：表示名 | 1基本情報：元 | 2契約者：表示名 | 2契約者：元 | 3支払情報：表示名 | 3支払情報：元 |
|---|---|---|---|---|---|---|
| 1 | データ種別 | 固定値：'1基本情報' | データ種別 | 固定値：'2契約者' | データ種別 | 固定値：'3支払情報' |
| 2 | 処理順 | 契約基本情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO \|\| '_' \|\| 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH \|\| '_' \|\| '1基本情報' | 処理順 | 契約者情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO \|\| '_'  \|\| 契約者情報ﾏｽﾀ.PLAN_SITEID_BRANCH  \|\| '_'  \|\| '2契約者' \|\| '_'  \|\| 契約者情報ﾏｽﾀ.CONSTRACT_KBN \|\| '_'  \|\| 契約者情報ﾏｽﾀ.CONSTRACT_CD | 処理順 | 契約支払情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO \|\| '_'  \|\| 契約支払情報ﾏｽﾀ.PLAN_SITEID_BRANCH \|\| '_'  \|\| '3支払情報' \|\|  '_'  \|\| 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND \|\|  '_'  \|\| 契約支払情報ﾏｽﾀ.PAY_CD \|\| '_'  \|\| 契約支払情報ﾏｽﾀ.PAY_CD_BRANCH |
| 3 | 計画基地局番号 | 契約基本情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO | 計画基地局番号 | 契約者情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NO | 計画基地局番号 | 契約支払情報ﾏｽﾀ．KEIKAKU_KICHIKYOKU_NO |
| 4 | 計画基地局枝番 | 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH | 計画基地局枝番 | 契約者情報ﾏｽﾀ.PLAN_SITEID_BRANCH | 計画基地局枝番 | 契約支払情報ﾏｽﾀ.PLAN_SITEID_BRANCH |
| 5 | 計画基地局名 | 契約基本情報ﾏｽﾀ.KEIKAKU_KICHIKYOKU_NAME | 契約者番号 | 契約者情報ﾏｽﾀ.CONSTRACT_CD | 支払番号 | 契約支払情報ﾏｽﾀ.PAY_CD |
| 6 | 計画基地局名_ｶﾅ | 契約基本情報ﾏｽﾀ.PLAN_STATION_KANA | 契約者区分 | 契約者情報ﾏｽﾀ.CONSTRACT_KBN を名称にする（1→「契約者」、2→「関係者」） | 支払番号枝番 | 契約支払情報ﾏｽﾀ.PAY_CD_BRANCH |
| 7 | 基地局番号 | 契約基本情報ﾏｽﾀ.KICHIKYOKU_NO | 関係_地位 | 契約者情報ﾏｽﾀ.RELATION | 支払内容区分 | 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND |
| 8 | 基地局名 | 契約基本情報ﾏｽﾀ.KICHIKYOKU_NAME | 法人_個人区分 | 契約者情報ﾏｽﾀ.CORP_PRIV_KBN を名称にする（1→「法人」、2→「個人」。P06 の名称と同じ） | 支払内容区分_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P17') |
| 9 | 基地局名_ｶﾅ | 契約基本情報ﾏｽﾀ.STATION_KANA | 法人名_個人名 | 契約者情報ﾏｽﾀ.NAME | 支払内容詳細区分 | 契約支払情報ﾏｽﾀ.FEE_MANAGE_KIND_SHOSAI |
| 10 | データ確定 | 契約基本情報ﾏｽﾀ.DATA_FIX_FLG (0:未確定、1:確定) | 法人名_個人名ｶﾅ | 契約者情報ﾏｽﾀ.NAME_KANA | 支払内容詳細区分_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',CODE,'C02') |
| 11 | 登録状態 | 契約基本情報ﾏｽﾀ.STATUS_KIND \|\| ':' \|\| ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P21') | 所属部署名 | 契約者情報ﾏｽﾀ.BELONGING_POST | 支払内容その他 | 契約支払情報ﾏｽﾀ.OTHER_PAYMENT_NAME |
| 12 | 転貸借 | 契約基本情報ﾏｽﾀ.MOVE_LEASE (0:転貸借以外、1:転貸借) | 所属部署名ｶﾅ | 契約者情報ﾏｽﾀ.BELONGING_POST_KANA | 案件大ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 契約支払情報ﾏｽﾀ.ANKEN_DAI_GRP_CD |
| 13 | 住居_都道府県ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.ADDRESS_CD1 | 電話番号_固定 | 契約者情報ﾏｽﾀ.TEL1 | 案件大ｸﾞﾙｰﾌﾟ | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M10') |
| 14 | 住居_都道府県名 | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05') | 電話番号_携帯 | 契約者情報ﾏｽﾀ.TEL2 | 案件小ｸﾞﾙｰﾌﾟｺｰﾄﾞ | 契約支払情報ﾏｽﾀ.ANKEN_SYO_GRP_CD |
| 15 | 住居_市区町村ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.ADDRESS_CD2 | FAX番号 | 契約者情報ﾏｽﾀ.FAX | 案件小ｸﾞﾙｰﾌﾟ | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M11') |
| 16 | 住居_市区町村名 | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04') | メールアドレス | 契約者情報ﾏｽﾀ.MAIL | 採算管理区分 | 契約支払情報ﾏｽﾀ.PROFIT_MANAGE_KIND |
| 17 | 住居_字_地番 | 契約基本情報ﾏｽﾀ.ADDRESS3 | 郵便番号 | 契約者情報ﾏｽﾀ.ZIP1 \|\| '-' \|\| 契約者情報ﾏｽﾀ.ZIP2 | 支払先_契約先番号 | 契約支払情報ﾏｽﾀ.PAYMENT_PERSON |
| 18 | 住居_建物_ビル | 契約基本情報ﾏｽﾀ.ADDRESS4 | 都道府県 | 契約者情報ﾏｽﾀ.ADDRESS_CD1 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05')) | 支払方法 | 契約支払情報ﾏｽﾀ.PAYMENT_DDIVISION |
| 19 | 住居_カナ | 契約基本情報ﾏｽﾀ.KANA | 市区町村 | 契約者情報ﾏｽﾀ.ADDRESS_CD2 (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04')) | 支払方法_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P18') |
| 20 | 登記_都道府県ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.PLACE_ADDRESS_CD1 | 字_地番 | 契約者情報ﾏｽﾀ.ADDRESS3 | 消費税扱い | 契約支払情報ﾏｽﾀ.TAX_KIND |
| 21 | 登記_都道府県名 | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M05') | 建物_ビル | 契約者情報ﾏｽﾀ.ADDRESS4 | 消費税扱い_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P10') |
| 22 | 登記_市区町村ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.PLACE_ADDRESS_CD2 | カナ | 契約者情報ﾏｽﾀ.ADDRESS_KANA | 初回支払金額 | TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_FEE ) |
| 23 | 登記_市区町村名 | ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M04') | 書類 | 契約者情報ﾏｽﾀ.DOCUMENTS_KBN (1:送付先、2:送付禁止) | 初回支払消費税額 | TO_CHAR(契約支払情報ﾏｽﾀ.FIRST_PAY_TAX ) |
| 24 | 登記_字_地番 | 契約基本情報ﾏｽﾀ.PLACE_ADDRESS3 | 電話 | 契約者情報ﾏｽﾀ.TEL_KBN (1:電話禁止) | 初回支払日 | TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_DATE ), 'YYYY/MM/DD' ) |
| 25 | 登記_カナ | 契約基本情報ﾏｽﾀ.PLACE_KANA | 詳細 | 契約者情報ﾏｽﾀ.DETAILS_KBN (ｺｰﾄﾞﾏｽﾀ.名称('WTZ',MASTER,'M01')) | 初回支払期間対象FROM | TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_FROM \|\| '01' ), 'YYYY/MM/DD' ) |
| 26 | 契約書の有無_賃貸借契約書 | 契約基本情報ﾏｽﾀ.CONTRACT_VALID1 (0:無、1:有) | ﾏｲﾅﾝﾊﾞｰ受領日 | 契約者情報ﾏｽﾀ.MY_NUMBER_DATE | 初回支払期間対象TO | TO_CHAR(TO_DATE( 契約支払情報ﾏｽﾀ. FIRST_PAY_TO \|\| '01' ), 'YYYY/MM/DD' ) |
| 27 | 契約書の有無_転貸借契約書 | 契約基本情報ﾏｽﾀ.CONTRACT_VALID2 (0:無、1:有) | 備考 | 契約者情報ﾏｽﾀ.BIKO | 初回消費税調整額 | TO_CHAR(契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS ) |
| 28 | 契約書の有無_電気使用料覚書 | 契約基本情報ﾏｽﾀ.CONTRACT_VALID3 (0:無、1:有) | 予備項目1 | 契約者情報ﾏｽﾀ.YOBI_KOMOKU1 | 初回消費税調整理由 | 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_REASON |
| 29 | 契約書の有無_その他 | 契約基本情報ﾏｽﾀ.CONTRACT_VALID_OTHER | 予備項目2 | 契約者情報ﾏｽﾀ.YOBI_KOMOKU2 | 初回消費税調整理由_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') |
| 30 | 契約締結日 | TO_CHAR( TO_DATE(契約基本情報ﾏｽﾀ.CONTRACT_CONCLUSION_DATE ), 'YYYY/MM/DD' ) | 予備項目3 | 契約者情報ﾏｽﾀ.YOBI_KOMOKU3 | 初回消費税備考 | 契約支払情報ﾏｽﾀ. FIRST_TAX_ADJUSTMENTS_MEMO |
| 31 | 契約開始日 | TO_CHAR( TO_DATE( 契約基本情報ﾏｽﾀ.CONTRACT_START_DATE ), 'YYYY/MM/DD' ) | 予備項目4 | 契約者情報ﾏｽﾀ.YOBI_KOMOKU4 | 継続支払金額 | TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_FEE ) |
| 32 | 契約終了日 | TO_CHAR( TO_DATE( 契約基本情報ﾏｽﾀ.CONTRACT_FINISH_DATE ), 'YYYY/MM/DD' ) | - | - | 継続支払消費税額 | TO_CHAR( 契約支払情報ﾏｽﾀ.COUNT_PAY_TAX ) |
| 33 | 解約日 | TO_CHAR( TO_DATE( 契約基本情報ﾏｽﾀ.CONTRACT_CALCELL_DATE ), 'YYYY/MM/DD' ) | - | - | 継続消費税調整額 | TO_CHAR( 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS ) |
| 34 | 更新年数_年単位 | 契約基本情報ﾏｽﾀ.UPDATE_YEAR | - | - | 継続消費税調整理由 | 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_REASON |
| 35 | 更新通知日_ヶ月前まで | 契約基本情報ﾏｽﾀ.UPDATE_NOTICE | - | - | 継続消費税調整理由_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P16') |
| 36 | 更新形態 | 契約基本情報ﾏｽﾀ.UPDATE_PATTERN (ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P07')) | - | - | 継続消費税備考 | 契約支払情報ﾏｽﾀ. COUNT_TAX_ADJUSTMENTS_MEMO |
| 37 | 受電方法 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU4（予備項目4）に値があればその値。空なら ELECT_KIND を文字にする（1→「1:電力会社直受」、2→「2:テナント受電」、3→「3:ａｕ受電」） | - | - | 支払有効期間FROM | 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_FROM |
| 38 | 転貸借契約書ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.MOVE_LEASE_CONTRACT | - | - | 支払有効期間TO | 契約支払情報ﾏｽﾀ.PAY_EFFECTIVE_TO |
| 39 | 転貸借契約書名 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P15') | - | - | 月額契約金額_税抜 | TO_CHAR( 契約支払情報ﾏｽﾀ.MONTHLY_PAYMENT ) |
| 40 | 代表契約番号 | 契約基本情報ﾏｽﾀ.REPRESENT_CONTRACT_NO | - | - | 月額有効期間FROM | 契約支払情報ﾏｽﾀ. MONTHLY_PAY_EFFECTIVE_FROM |
| 41 | 代表契約枝番 | 契約基本情報ﾏｽﾀ. REPRESENT_CONTRACT_BRANCH_NO | - | - | 月額有効期間TO | 契約支払情報ﾏｽﾀ.MONTHLY_PAY_EFFECTIVE_TO |
| 42 | UQ押印者ｺｰﾄﾞ | 契約基本情報ﾏｽﾀ.UQ_SEALER | - | - | 請求方法区分 | 契約支払情報ﾏｽﾀ.CLAIM_INFOMATION_KIND |
| 43 | UQ押印者_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P24') | - | - | 支払種別 | 契約支払情報ﾏｽﾀ.PAYMENT_KIND |
| 44 | 予備項目1 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU1 | - | - | 支払種別_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P08') |
| 45 | 予備項目2 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU2 | - | - | 支払年 | 契約支払情報ﾏｽﾀ.PAYMENT_YEAR |
| 46 | 予備項目3 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU3 | - | - | 継続支払詳細_備考 | 契約支払情報ﾏｽﾀ.PAYMENT_MEMO |
| 47 | 予備項目4 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU4 | - | - | その他備考1 | 契約支払情報ﾏｽﾀ.MEMO1 |
| 48 | 予備項目5 | 契約基本情報ﾏｽﾀ.YOBI_KOMOKU5 | - | - | その他備考2 | 契約支払情報ﾏｽﾀ.MEMO2 |
| 49 | - | - | - | - | その他備考3 | 契約支払情報ﾏｽﾀ.MEMO3 |
| 50 | - | - | - | - | その他備考4 | 契約支払情報ﾏｽﾀ.MEMO4 |
| 51 | - | - | - | - | 請求予定月 | 契約支払情報ﾏｽﾀ.CLAIM_MONTH |
| 52 | - | - | - | - | 請求予定月_名称 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P23') |
| 53 | - | - | - | - | 予備項目1 | 契約支払情報ﾏｽﾀ.YOBI_KOMOKU1 |
| 54 | - | - | - | - | 予備項目2 | 契約支払情報ﾏｽﾀ.YOBI_KOMOKU2 |
| 55 | 検索条件_登録状態 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P21') | 検索条件_登録状態 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P21') | 検索条件_登録状態 | ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P21') |
| 56 | 検索条件_代表契約局番 | 契約基本情報ﾏｽﾀ.REPRESENT_CONTRACT_NO | 検索条件_代表契約局番 | 契約基本情報ﾏｽﾀ.REPRESENT_CONTRACT_NO | 検索条件_代表契約局番 | 契約基本情報ﾏｽﾀ.REPRESENT_CONTRACT_NO |
| 57 | 検索条件_代表契約枝番 | 契約基本情報ﾏｽﾀ. REPRESENT_CONTRACT_BRANCH_NO | 検索条件_代表契約枝番 | 契約基本情報ﾏｽﾀ. REPRESENT_CONTRACT_BRANCH_NO | 検索条件_代表契約枝番 | 契約基本情報ﾏｽﾀ. REPRESENT_CONTRACT_BRANCH_NO |
| 58 | 検索条件_確定局番 | 契約基本情報ﾏｽﾀ.KICHIKYOKU_NO | 検索条件_確定局番 | 契約基本情報ﾏｽﾀ.KICHIKYOKU_NO | 検索条件_確定局番 | 契約基本情報ﾏｽﾀ.KICHIKYOKU_NO |
| 59 | 処理順_帳票用 | ROW_NUMBER() OVER  (PARTITION BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, GM30.PLAN_SITEID_BRANCH  ORDER BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH,  契約基本情報ﾏｽﾀ.FEE_MANAGE_KIND) | 処理順_帳票用 | ROW_NUMBER() OVER  (PARTITION BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, GM30.PLAN_SITEID_BRANCH  ORDER BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH,  契約基本情報ﾏｽﾀ.FEE_MANAGE_KIND) | 処理順_帳票用 | ROW_NUMBER() OVER  (PARTITION BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, GM30.PLAN_SITEID_BRANCH  ORDER BY 契約基本情報ﾏｽﾀ. KEIKAKU_KICHIKYOKU_NO, 契約基本情報ﾏｽﾀ.PLAN_SITEID_BRANCH,  契約基本情報ﾏｽﾀ.FEE_MANAGE_KIND) |
