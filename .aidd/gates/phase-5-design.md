---
format_version: 2
phase: design
created_at: 2026-10-07T16:53:31+09:00
---

# ゲート記録

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 2026-10-07T16:53:31+09:00 | ① | ["specs/property-basic-info/design.md"] | {"specs/property-basic-info/design.md":"bf76c5452e71699c3cc67e086e580a5d74bc94e3a607ea9dd3250c1387fcd125"} | 4 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | format-conformance | specs/property-basic-info/design.md `## 設計判断（Design Decisions）`〜`## 補足資料（Supporting References）`（行878〜917） | 見出し構造がテンプレートと一致しない。`## 設計判断` の `_分担_` 注記（行881）が「比較表や調査資料そのものは `」の位置で途切れ、その続きに `### 判断 4: 更新系の要求の URL を CSRF の照合に乗る末尾にそろえる` が注記の文として入っているため、判断 4 は見出しになっていない（行883〜887 の本文は見出しを持たない）。行889 にテンプレートに無い見出し「## 補足資料（Supporting References）`。ここには選択肢を比べて選んだことだけを書く。」があり、`## 補足資料（Supporting References）` 相当の見出しが2回（行889・行917）現れる。その結果、`### 判断 1`〜`### 判断 3`（行893・901・909）とテンプレートの `_書き方_` 注記（行891）が `## 設計判断` ではなく行889 の見出しの下に位置している |  |  |
| 2 | format-conformance | specs/property-basic-info/design.md `### 移行方針（Migration Strategy）`（行831・832） | プレースホルダー削除: テンプレートの `&lt;DSN_MIGRATION_ROLLBACK&gt;`・`&lt;DSN_MIGRATION_CHECKPOINT&gt;` が残置されず、「不要：…」の文だけに置き換わっている。不要理由は書かれているが、プレースホルダーを不要理由付きで残す規約（status-protocol §7「どちらの系統も削除しない」）を満たしていない（同書の行143・441・510・598・876 はプレースホルダーを残して不要理由を併記している） |  |  |
| 3 | format-conformance | specs/property-basic-info/design.md `### テスト体制 / テスト仕様`（行852〜856） | プレースホルダー削除: テンプレートの `&lt;DSN_TEST_OWNER&gt;`・`&lt;DSN_TEST_ENVIRONMENT&gt;`・`&lt;DSN_TEST_PERIOD&gt;`・`&lt;DSN_TEST_ESCALATION&gt;`・`&lt;DSN_TEST_SPEC_LINK&gt;` が残置されず、「不要：試験仕様書と計画書で扱う（Q-DS-PBI-015）」の文だけに置き換わっている。不要理由付きでプレースホルダーを残す規約（status-protocol §7）を満たしていない |  |  |
| 4 | format-conformance | specs/property-basic-info/design.md `### コンポーネント一覧（Summary）` の「文書バーコード Controller・Service・Mapper」行（行430）と `### 物件基本情報登録変更` 配下の `#### 文書バーコード Controller・Service・Mapper`（行502・592） | 一覧ではドメイン / レイヤを「文書バーコード / Controller・Service・Mapper」としているが、詳細は `### 物件基本情報登録変更` の見出しの下に置かれ、`### 文書バーコード` のドメイン見出しが無い。テンプレートの「各行は下の詳細と対応し、コンポーネント名・ドメイン / レイヤ・目的・受け入れ基準ID は同じ値を書く」と、一覧と詳細の見出し構造が対応していない |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 1 | 修正 |  | Junichi Noumi | 2026-10-07T17:00:12+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 2 | 修正 |  | Junichi Noumi | 2026-10-07T17:00:17+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 3 | 修正 |  | Junichi Noumi | 2026-10-07T17:00:21+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 4 | 修正 |  | Junichi Noumi | 2026-10-07T17:00:26+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 2026-10-07T17:02:28+09:00 | ①② | ["specs/property-basic-info/design.md"] | {"specs/property-basic-info/design.md":"8baf4038930aff546bc3e25c728487f1d47a5ef18e3e2d4de77a4b7d2c317951"} | 14 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | traceability | specs/property-basic-info/design.md `### 論理データモデル（Logical Data Model）` の参照整合性のルール（行249）／ specs/property-basic-info/requirements.md 15.1・15.2 | ID対応あり・内容未充足（意味判定）。15.2 は「再製本依頼の起案済・差戻しの申請を、文書バーコードが未生成なら削除する」ことを求めるが、design は「削除ボタンは起案者の番の未起案・下書きのときだけ出す（15.2、Q-DS-PBI-007）」としており、再製本依頼の起案済・差戻しで削除する経路が design のどこにも無い。あわせて、15.1 は未起案・下書きの削除に条件を付けていないが、design は「稟議依頼・修正稟議依頼は受付No が NULL のときだけ」「再製本依頼は文書バーコードが 0 件のときだけ」という 15.1 に無い条件を未起案・下書きの削除にも掛けている |  |  |
| 2 | traceability | specs/property-basic-info/design.md `### ドメインモデル（Domain Model）` の複製の不変条件（行230）・`### データ契約と外部連携` の稟議バーコードNo の注記（行390）・`## 処理フロー` の主要な判断（行662）／ requirements.md 7.3・3.7 | ID対応あり・内容未充足（意味判定）。7.3 は「契約局情報の全行と発行依頼書を新しい申請No で複製し、受付No と稟議バーコードNo は再製本では引き継ぎ、修正稟議では空にする」ことを求めるが、design が複製の内容を書いているのは物件申請情報（`TWTGM080`）の列だけで、本 feature が定義を持つ契約局情報（`TWTGM140`）の全行を新しい申請No で登録すること、その `Ringi_Barcode_No` を再製本では引き継ぎ修正稟議では空にすることが書かれていない。再製本が元の稟議の稟議バーコードを使う（3.7）ことの実現手段も、この複製に依存したまま示されていない |  |  |
| 3 | traceability | specs/property-basic-info/design.md `#### WTG 申請状態サービス` の `canOperate`（行473）・`##### API 契約` の `/wtg070/stationKind/update`（行550）・他画面への遷移（行561〜563）・単独局か複数局か（行585）／ requirements.md 14.5 | ID対応あり・内容未充足（意味判定）。14.5 は「単独局・複数局の切替、契約局取込、契約局DL、契約局情報追加は、稟議依頼・修正稟議依頼で起案者・申請者・確認者が自分の番のときだけ受け付け、それ以外（再製本依頼を含む）は受け付けない」ことを求めるが、design にはこの条件（特に再製本依頼では受け付けないこと）の記述が無い。`canOperate` の操作の一覧にもこれらの操作は無く、該当 API の Errors は「業務、排他」だけで、どの条件で拒否するかが示されていない |  |  |
| 4 | traceability | specs/property-basic-info/design.md `##### API 契約` の `/wtg070/station/update`・`/wtg070/station/delete`（行551・552）・契約局情報欄の列（行586）／ requirements.md 14.2 | ID対応あり・内容未充足（意味判定）。14.2 は「契約局情報の並替え・削除は、稟議依頼・修正稟議依頼の複数局の申請で起案者・申請者・確認者が自分の番のときだけ使え、それ以外は使わせない」ことを求めるが、design に書かれている制約は 1 行目（代表局）を並べ替え・削除できないこと（14.3）だけで、依頼内容（再製本依頼を除く）・単独局か複数局か・番による制限の記述が無い |  |  |
| 5 | traceability | specs/property-basic-info/design.md `## コンポーネントとインターフェース（Components and Interfaces）`・`## 機能固有のエラー処理（Error Handling）`／ steering/non-functional.md `## 信頼性・観測性` 冒頭の分担・`### ログ方針` | 可観測性のうち「ログ」の柱が未反映。steering/non-functional.md は「フィーチャー固有のログ項目は design の Components と Error Handling」に書くとし、ERROR は `ExceptionResolver`、INFO は `LoggingInterceptor` で出す方針を定めているが、design にはこの feature のログ出力（既存のインターセプタとハンドラに任せるのか、承認フローの操作・ファイル登録・CSV 出力などで固有に出す項目があるのか）の記述が無い。ログに関する記述は「担当者の氏名と連絡先をログに出さない」（行808）だけである |  |  |
| 6 | traceability | specs/property-basic-info/design.md `## コンポーネントとインターフェース（Components and Interfaces）`／ steering/non-functional.md `### 監視 / ヘルス` の分担 | 可観測性のうち「メトリクス」の柱が未反映。steering/non-functional.md は「機能固有の監視項目は design の Components and Interfaces」に書くとしているが、design には本 feature の監視項目の有無（無いならその旨）の記述が無い |  |  |
| 7 | steering-conformance | specs/property-basic-info/design.md `### 技術スタック（Technology Stack）` の Infrastructure / Runtime 行（行186）／ steering/tech.md `### 必須ツール`・`## コアテクノロジ` | 矛盾。steering/tech.md は必須ツールの JDK を「1.7（1.7.0.55）／コンパイルと実行」と定めているが、design は「開発端末の JDK 1.8（-source/-target 1.7）。1.7 系の JDK は開発端末に入れない（Q-DS-PBI-014）」としており両立しない。steering と design のどちらを直すかの確認が要る |  |  |
| 8 | steering-conformance | specs/property-basic-info/design.md `### 技術スタック（Technology Stack）`（行185）・`### データ契約と外部連携` の CSV の形（行394）・`## ファイル配置計画`（行770）／ steering/architecture.md `### 共通基盤（shared）` | 矛盾。design は orangesignal-csv を「本 feature だけで使う」とする一方、それを使う `CsvUtils` を共通基盤 `jp.co.kccs.wt.common.utils` に新しく置くとしている。steering/architecture.md の共通基盤は「複数の機能で使う処理」に限り、「特定の画面や業務にだけ使う処理」は `function/<サブシステム>/<機能ID>/` か `function/<サブシステム>/common/` に置くと定めている。複数機能で使う前提なのか、本 feature だけで使うのかが steering の配置条件と食い違う |  |  |
| 9 | steering-conformance | specs/property-basic-info/design.md `#### 物件基本情報登録変更 Controller` と `#### 文書バーコード Controller・Service・Mapper` の `##### API 契約（API Contract）`（行537〜558・行637〜641）、`## 設計判断` 判断 4（行909〜915）／ steering/tech.md `## 命名規則` の URL | 逸脱。steering/tech.md の URL の規約は「`/<機能ID小文字>` ＋ `/<アクション>`」だが、design は `/wtg070/request/execute`・`/wtg070/station/update` など機能ID の後に 2 段のパスを置き、文書バーコードのポップアップは機能ID WTG070 のパッケージに置きながら URL を `/wtg073` としている。steering に無い URL の組み立て方であり、steering と design のどちらを直すかの確認が要る |  |  |
| 10 | steering-conformance | specs/property-basic-info/design.md `#### WTG 申請状態サービス` の `transit`・`recordNumbering` のエラー（行474・475）、`### 機能固有エラーコード` の `WTG-100030`・既存の排他エラー（行719・722）／ steering/tech.md `### 例外処理フロー`・`### グローバルハンドラ` | 矛盾。design は業務エラーを `ApplicationException`、排他を `ExclusiveException` として投げ、いずれも「200（同じ画面に戻す）」としている。steering/tech.md は Controller では例外を個別に捕まえずグローバルハンドラ（`ExceptionResolver`）に任せ、Controller から出た例外はエラー画面へ遷移させると定めており、例外で同じ画面に戻す扱いと両立しない |  |  |
| 11 | steering-conformance | specs/property-basic-info/design.md `### ドメインモデル（Domain Model）` の依頼内容の不変条件（行226）／ steering/database.md `## 設計思想`・`## 型の指針` | 矛盾。steering/database.md は区分値をコードマスタ `TWTZM040` で管理し、区分値・フラグは「文字列のコード」で持ち意味は `TWTZM040` に持つと定めているが、design は依頼内容（`P29`）を「コード値ではなく名称の文字列で持つ」としている（Q-DS-PBI-002）。steering と design のどちらを直すかの確認が要る |  |  |
| 12 | steering-conformance | specs/property-basic-info/design.md `### 物理データモデル（Physical Data Model）` の `TWTGM180` の判定（行342）・`TWTGM170` の権限ID（行351）・`TWTGM140` の連番（行308）・`TWTGM090` の SEQ（行328）・`TWTGM180` の審査回・通番（行337・338）／ steering/database.md `## 設計思想`・`## 型の指針` | 矛盾。steering/database.md は区分値をコードマスタ `TWTZM040` で管理し、ID・番号は「0 詰めの文字列」とすると定めているが、design は判定（`Hantei`）と権限ID（`Kengen_ID`）を「コードマスタは作らず、値は DB レイアウトの備考に書く」とし、連番・SEQ・審査回・通番を Int としている。steering と design のどちらを直すかの確認が要る |  |  |
| 13 | steering-conformance | specs/property-basic-info/design.md `### セキュリティ上の考慮（Security Considerations）` の組織の判定（行807）・`#### WTG 申請状態サービス` の `getExternalScope`（行476）／ steering/security.md `#### 所有権・エンティティ境界`・`### 認証 → 認可の契約（AuthContext）` | 矛盾。steering/security.md は `P71` の「キー3 がログインユーザーのグループ」とし、AuthContext では権限区分（`Kengen_Kbn`）と所属グループ（グループID・既定区分・事業所コード）を別の項目として定めている。design は「グループ」を権限区分と読み替え、所属グループ（`TWTZM020`）は使わないとしている。steering の「グループ」の記述と design の判定方法のどちらを直すかの確認が要る |  |  |
| 14 | external-integration-contract-explicitness | specs/property-basic-info/design.md `### データ契約と外部連携` の進捗管理DB インポート用 CSV の形（行391〜395）・`### このスペックが持たない責務` の後のフェーズに回す作業（行92） | 進捗管理DB へ渡す CSV のインターフェース仕様が明示されていない。文字コード・区切り・囲み・改行・ファイル名は書かれているが、1 行目 188 項目・2 行目以降 228 項目の項目の並びと各項目の出し方（名称への変換を含む）は「Phase 8 で回答者から受け取る」とされ design に無い。並びは「契約情報取込の取込レイアウトと同じ」とする一方、contract-info-import の design が「本書のこの形に合わせる」としており、項目定義の正がどこにも書かれていない |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 7 | 人間による確認（steering/tech.md の修正、または本 design の修正） | 開発端末の JDK について design（Q-DS-PBI-014 の回答）と steering が食い違っており、steering 側を直す場合は Phase 2 が宛先になる |
| 11 | 人間による確認（steering/database.md の修正、または本 design の修正） | 依頼内容を名称で持つ扱い（Q-DS-PBI-002 の回答）が steering の型の指針と食い違っており、steering 側を直す場合は Phase 2 が宛先になる |
| 12 | 人間による確認（steering/database.md の修正、または本 design の修正） | コードマスタを作らない区分値と Int の番号列（Q-DS-PBI-005・006 ほかの回答）が steering の設計思想・型の指針と食い違っており、steering 側を直す場合は Phase 2 が宛先になる |
| 13 | 人間による確認（steering/security.md の修正、または本 design の修正） | P71 のキー3 の「グループ」の意味（Q-DS-PBI-009 の回答）が steering の記述と食い違っており、steering 側を直す場合は Phase 2 が宛先になる |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 1 | 修正 |  | Junichi Noumi | 2026-10-07T17:44:03+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 2 | 修正 |  | Junichi Noumi | 2026-10-07T17:44:06+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 3 | 修正 |  | Junichi Noumi | 2026-10-07T17:44:09+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 4 | 修正 |  | Junichi Noumi | 2026-10-07T17:44:11+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 5 | 修正 |  | Junichi Noumi | 2026-10-07T17:44:14+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 6 | 修正 |  | Junichi Noumi | 2026-10-07T17:44:16+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 8 | 修正 |  | Junichi Noumi | 2026-10-07T17:44:19+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 9 | 修正 |  | Junichi Noumi | 2026-10-07T17:44:22+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 10 | 修正 |  | Junichi Noumi | 2026-10-07T17:44:24+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 14 | 修正 |  | Junichi Noumi | 2026-10-07T17:44:27+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 7 | 対応せず進める | steering の JDK 1.7 は、本番の実行環境とビルドの指定（-source/-target 1.7）を指すものと読みます。開発端末でテストを動かす JDK は、steering の対象外です。steering の追記（開発端末のテスト実行は JDK 1.8 で -source/-target 1.7）は、次に steering を開き直すときにまとめて行います。 | Junichi Noumi | 2026-10-07T17:44:32+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 11 | 対応せず進める | 依頼内容は、既存の稟議関連の作りに合わせて名称の文字列（"稟議依頼"・"再製本依頼"）で持ちます。steering の型の指針の例外として、次に steering を開き直すときにまとめて追記します。 | Junichi Noumi | 2026-10-07T17:44:37+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 12 | 対応せず進める | 判定・権限ID はこの feature の中だけで使う値で、コードマスタを足すと発注者の投入作業が増えるため、DB レイアウトの備考で管理します。連番・SEQ・審査回・通番は、並べ替えや MAX＋1 の計算に使う数値なので Int で持ちます。どちらも steering の例外として、次に steering を開き直すときにまとめて追記します。 | Junichi Noumi | 2026-10-07T17:44:42+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 13 | 対応せず進める | steering の「グループ」は権限区分（TWTZM010.Kengen_Kbn）を指す、と読みます（Q-DS-PBI-009 の回答のとおり）。steering の文言は、次に開き直すときに直します。 | Junichi Noumi | 2026-10-07T17:44:47+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 3 | 2026-10-07T18:12:06+09:00 | ①② | ["specs/property-basic-info/design.md"] | {"specs/property-basic-info/design.md":"e37fe9423d910cf5c3dfedad5bc83a7907f25111f5e381e6c7ca0b7c59b4a9a8"} | 4 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | traceability | specs/property-basic-info/design.md `#### WTG 申請状態サービス` の `canOperate`（行476）・`##### API 契約` の `/wtg070/henshu`（行563）・契約局情報の操作の条件（行598）・`### 機能固有エラーコード` の `WTG-100022`（行733）／ specs/property-basic-info/requirements.md 14.11 | ID対応あり・内容未充足（意味判定）。14.11 は「発行依頼書編集ボタンを、稟議依頼・修正稟議依頼の申請で起案者・申請者・確認者が自分の番のときだけ使えるようにし（複数局で契約局情報が無い場合を除く）、それ以外は使わせない」ことを求めている。しかし design に書かれているのは、複数局で契約局情報が無いときの `WTG-100022`（14.12）だけである。依頼内容（再製本依頼を除く）・番・担当による制限の記述が無い。`canOperate` の操作の一覧にも発行依頼書編集が無く、`/wtg070/henshu` の Errors に挙げた `WTG-100030` をどの条件で返すかが示されていない |  |  |
| 2 | steering-conformance | specs/property-basic-info/design.md `##### サービスインターフェース` の `transit`・`recordNumbering`（行477・478）、`##### 状態管理` の並行制御（行503）、文書バーコードの `generate`・`update`（行639・640）、`### 機能固有エラーコード` の表の後の注記（行739）／ steering/tech.md `### 例外処理フロー`（画面：業務ロジック の行）・`## コード規約` の排他制御、steering/database.md `## 整合性` | 矛盾。steering/tech.md は、業務上の失敗を `ApplicationException` の派生（排他は `ExclusiveException`）としてメッセージキー付きで投げると定めている。排他制御も「`ExclusiveFG` が一致しなければ `ExclusiveException` を投げる」としている（`BindingResult` に積む方式は入力チェックの行だけ）。一方 design は、業務エラーと排他エラーを例外にせず `BindingResult` に積み（`WTG-100030` は `result.reject`、`GEF-000027` は `rejectValue`）、`ApplicationException`・`ExclusiveException` は使わないとしている。design はこれを「`steering/tech.md` の方式」「`steering/tech.md` の排他制御」として引いているが、引いた steering の記述とは両立しない。steering と design のどちらを直すかの確認が要る |  |  |
| 3 | steering-conformance | specs/property-basic-info/design.md `##### API 契約` の注記（行538）と API の一覧（行545〜566・652〜654）、`## 設計判断` の判断 4（行926〜932）、`### セキュリティ上の考慮（Security Considerations）` の CSRF の対策（行821）／ steering/security.md `## 攻撃対策（主要パターン）` の CSRF の行、steering/architecture.md `### フロントエンド（FE）` の境界 | 違反（design 自身も食い違いを書いている）。steering/security.md は更新系の要求で `_csrf` を照合するとし、architecture.md は更新系のフォーム送信に `_csrf` を付けるとしている。しかし design は、`/wtg070/shinseIrai`・`/wtg070/check`・`/wtg070/shinse`・`/wtg070/sashimodoshi`・`/wtg070/cancel`・`/wtg070/deleteShinse`・`/wtg070/Shusei`・`/wtg070/Saisehon`・`/wtg070/tandokuFukusu`・`/wtg070/sort`・`/wtg070/deleteContract`・`/wtg070/insertFile`・`/wtg070/commitFile`・`/wtg070/deleteFile`・`/wtg073/create` などの更新系の URL を照合なしで進めるとしている。また、同じ design の `### セキュリティ上の考慮` は「更新系の要求はすべて既存の `_csrf` トークンを照合する URL 名に置く」と書いており、判断 4 と API 契約の注記に対して design の中で矛盾している。steering と design のどちらを直すかの確認が要る |  |  |
| 4 | evidence-guard | specs/property-basic-info/design.md `#### WTG 申請状態サービス` の `canOperate` の「処理状況」（行476）、`##### API 契約` の `/wtg070/taskList`・`/wtg070/return`（行566・567） | 根拠の飛躍。処理状況のボタンと操作（バッチ処理状況一覧 `/zzz010/` への遷移と、そこからの戻り）は、requirements.md の受け入れ基準にも扱う範囲にも無い。それなのに `canOperate` では、14.2・14.5 を根拠に挙げた操作の一覧に含めている。14.2・14.5 が挙げる操作は単独局・複数局の切替、契約局取込、契約局DL、契約局情報追加、契約局情報の並替え・削除で、処理状況は含まれない。API の 2 行には出典の記載が無く、出典として示されているのは `canOperate` の「設計検査 2 回目の指示」だけである |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 2 | 人間による確認（steering/tech.md の修正、または本 design の修正） | 業務エラー・排他エラーの扱い（設計検査 2 回目の指示）が steering の例外処理フロー・排他制御と食い違っている。steering 側を直す場合は Phase 2 が宛先になる |
| 3 | 人間による確認（steering/security.md の修正、または本 design の修正） | CSRF の照合の範囲（設計検査 2 回目の指示）が steering の攻撃対策と食い違っている。steering 側を直す場合は Phase 2 が宛先になる |
| 4 | 人間による確認（requirements.md への受け入れ基準の追加、または本 design の修正） | 処理状況のボタンが要件に無いまま design で追加されている。要件側に足す場合は Phase 4 が宛先になる |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 3 | 1 | 修正 |  | Junichi Noumi | 2026-10-07T18:39:18+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 3 | 2 | 修正 |  | Junichi Noumi | 2026-10-07T18:39:21+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 3 | 3 | 修正 |  | Junichi Noumi | 2026-10-07T18:39:24+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 3 | 4 | 対応せず進める | 処理状況は、契約局取込（14.5）で起動したバッチの進み具合を、既存のバッチ処理状況一覧で見るための遷移です。この feature の業務ルールや更新は持たないので、requirements には足さず、design だけに置きます。canOperate の根拠は「14.5 の契約局取込に付随する遷移（requirements に受け入れ基準なし）」と書き直してください。 | Junichi Noumi | 2026-10-07T18:39:29+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 4 | 2026-10-07T18:41:07+09:00 | ①② | ["specs/property-basic-info/design.md"] | {"specs/property-basic-info/design.md":"8321bb52caba74def9b670e46ed2b60f71681f87a00cfed9334056c3327c008b"} | 2 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | traceability | specs/property-basic-info/design.md `### ドメインモデル（Domain Model）` の「発番後」「発番済」の判定（行238）・複製の不変条件（行230）・`### セキュリティ上の考慮` の組織の判定（行824）／ specs/property-basic-info/requirements.md 6.9・3.7・11.2・7.3 | ID対応あり・内容未充足（意味判定）。6.9 は、再製本依頼では起案者・申請者・承認者の番で、契約局情報と発行依頼書が登録済みかつ発番済みなら閲覧・印刷ボタンを出すことを求めている。しかし design は「発番済」を「審査フェーズが受付済（02）以降」で判定するとしている。再製本依頼の審査フェーズは未起案 00 → 起案済 01 → 申請済 03 → 承認済 05 と進み、受付済 02 を通らない（遷移表）。このため、起案者の番（未起案・下書き、起案済・差戻し）と申請者の番の起案済・回覧中では、この判定が成り立たず、ボタンが出ない。また design は「受付No が NULL でないこと」と「受付済（02）以降」は「どちらで見ても結果は同じ」としている。しかし再製本では、複製のときに受付No を元の申請から引き継ぐ（行230、7.3）。そのため未起案・起案済の段階でも受付No は NULL でなく、二つの判定の結果が分かれる。11.2 は再製本依頼を発番後として扱うとしており、6.9 の「発番済み」を再製本でどう判定するかが design に書かれていない（判定方法は Q-DS-PBI-007 の回答による） |  |  |
| 2 | traceability | specs/property-basic-info/design.md `##### API 契約` の `/wtg070/addKeyaku`・`/wtg070/henshu`・`/wtg070/hakkoLink` の行（行563）、`#### WTG 申請状態サービス` の `canOperate`（行476）、番の表の稟議・修正稟議 起案済 01・回覧中 02 の行（行495）、他の画面への遷移（行574）／ specs/property-basic-info/requirements.md 14.13 | ID対応あり・内容不整合（意味判定）。行563 の Errors は、基地局番号リンクを「`canOperate` の条件を満たさずに要求したとき」に `WTG-100030` で止めるとしている。しかし `canOperate` の操作の一覧（行476）に基地局番号リンクは無く、どの条件で受け付けるかが定義されていない。仮に契約局情報追加・発行依頼書編集と同じ条件（14.5 の番）を当てはめると、申請者の番の起案済・回覧中は条件に含まれない。一方で行495 は、申請者がこの状態で基地局番号リンクから発行依頼書登録変更画面へ行って発番するとしているため、同じ design の中で両立しない。14.13 は、基地局番号リンクを押したらその契約局の発行依頼書登録変更画面へ遷移することを求めており、番や依頼内容による制限は書かれていない |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 4 | 1 | 修正 |  | Junichi Noumi | 2026-10-07T18:48:37+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 4 | 2 | 修正 |  | Junichi Noumi | 2026-10-07T18:48:40+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 5 | 2026-10-07T18:50:42+09:00 | ①② | ["specs/property-basic-info/design.md"] | {"specs/property-basic-info/design.md":"0829e28f5d3a4e0db44e191b174e2518eb0af483f10814026003e86d90d8c7df"} | 3 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | traceability | specs/property-basic-info/design.md `##### 状態管理（State Management）` の番の表の「稟議・修正稟議 起案済 01・回覧中 02」の行（行495）・`#### WTG 申請状態サービス` の `canOperate`（行476）・`##### API 契約` の `/wtg070/update`・`/wtg070/tandokuFukusu`・`/wtg070/addKeyaku`・`/wtg070/keyakuTorikomi`・`/wtg070/keyakuDl`（行545・555・563・565・566）／ specs/property-basic-info/requirements.md 1.3・6.7・14.5 | ID対応あり・内容不整合（意味判定）。design は、稟議依頼・修正稟議依頼の起案済・回覧中を申請者の番としている。そのうえで、この状態では本画面に更新ボタンを出さないとしている（行495）。また `canOperate` の単独局と複数局の切替・契約局取込・契約局DL・契約局情報追加の条件でも、申請者の番を受付済・回覧中、受付済・確認中、申請済・差戻しだけとし、この状態を外している（行476）。一方 requirements は次のことを求めている。1.3 は、起案者・申請者・確認者が自分の番なら物件基本情報の項目と契約局情報の変更を許すこと。6.7 は、申請者の番（稟議依頼・修正稟議依頼）で更新ボタンを表示すること。14.5 は、申請者が自分の番なら切替・契約局取込・契約局DL・契約局情報追加を受け付けること。どれにも起案済・回覧中を除く記述は無く、この状態を除外しているのは 4.3・4.5（差戻し・取下げ）だけである。design の扱いは Q-DS-PBI-011 の回答（起案済・回覧中ではどの担当にも更新などのボタンを出さない）と設計検査 2 回目の指示に基づくが、承認済みの requirements とは両立しない |  |  |
| 2 | traceability | specs/property-basic-info/design.md `#### WTG 申請状態サービス` の `canOperate`（行476「契約局情報追加・並替え・削除は、さらに複数局のときだけ可」）・契約局情報の操作の条件（行599）・`##### API 契約` の `/wtg070/addKeyaku`（行563）／ specs/property-basic-info/requirements.md 14.5・14.7 | ID対応あり・内容不整合（意味判定）。14.5 は、稟議依頼・修正稟議依頼で起案者・申請者・確認者が自分の番なら契約局情報追加を受け付けることを求めており、単独局か複数局かの条件を付けていない（複数局に限るのは 14.2 の並替え・削除だけ）。一方 design は、契約局情報追加を複数局のときだけ可とし、単独局では拒否する（ボタンを出さず、要求が来たら `WTG-100030`）。この扱いは設計検査 2 回目の指示（「契約局情報追加は、さらに複数局モードのときだけ」）に基づくが、requirements 14.5 とは両立しない |  |  |
| 3 | steering-conformance | specs/property-basic-info/design.md `### 物理データモデル（Physical Data Model）` の `TWTGM170` の権限ID（行351）・`#### WTG 申請状態サービス` の `getAuthorities`（行475）・`### セキュリティ上の考慮（Security Considerations）` の認証・認可（行824）／ steering/security.md `#### 権限モデル`（定義の置き場・禁止）、specs/property-basic-info/requirements.md `## 前提と依存（Dependencies / Assumptions）` の前提 1 | 矛盾。steering/security.md の権限モデルは、承認フローの申請者・確認者・承認者の権限の定義の置き場を「`TWTGM170`（審査権限マスタ）とその権限コード `P82`」とし、番の判定を `TWTGM170` と `P82` 以外の仕組みで作らないと定めている。requirements の前提も、`TWTGM170` に申請者・確認者・承認者の権限（`P82` の 02〜04）が登録されているとしている。一方 design は、`TWTGM170` の権限ID を `P82` とは別の、このテーブル専用の値（1:稟議依頼-申請者〜5:再製本-承認者）とし、番の判定はこの値で行うとしている。`P82` は承認履歴の審査権限にだけ使う（Q-DS-PBI-006）。2 回目の指摘 12 が扱ったのは、権限ID のコードマスタを作らない点（steering/database.md）である。`P82` を権限コードとする security.md と requirements の前提との食い違いは扱っていない。steering・requirements と design のどちらを直すかの確認が要る |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | 人間による確認（requirements.md 1.3・6.7・14.5 の修正、または本 design の修正） | 起案済・回覧中の扱い（Q-DS-PBI-011 の回答・設計検査 2 回目の指示）が承認済みの requirements と食い違っている。requirements 側を直す場合は Phase 4 が宛先になる |
| 2 | 人間による確認（requirements.md 14.5 の修正、または本 design の修正） | 契約局情報追加を複数局に限る扱い（設計検査 2 回目の指示）が承認済みの requirements と食い違っている。requirements 側を直す場合は Phase 4 が宛先になる |
| 3 | 人間による確認（steering/security.md・requirements.md の前提の修正、または本 design の修正） | `TWTGM170` の権限ID を `P82` と別の体系にする扱い（Q-DS-PBI-006 の回答）が steering と requirements の前提と食い違っている。steering 側を直す場合は Phase 2、requirements 側を直す場合は Phase 4 が宛先になる |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 5 | 1 | 対応せず進める | requirements 1.3・6.7・14.5 の「自分の番」は、状態遷移表でその担当の操作が定義されている状態を指す、と読みます。稟議依頼・修正稟議依頼の 起案済・回覧中 は申請者の番ですが、定義されている操作は発行依頼書登録変更の画面での発番だけです。本画面の更新・切替・契約局取込・契約局DL・契約局情報追加は、定義されていないので受け付けません（4.3・4.5 の除外と同じ考え方）。requirements の文言（1.3・6.7・14.5 に「稟議依頼・修正稟議依頼の起案済・回覧中を除く」を足す）は、次に物件基本情報登録変更の requirements を開き直すときにまとめて直します。 | Junichi Noumi | 2026-10-07T19:04:54+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 5 | 2 | 対応せず進める | 契約局情報追加は、契約局を複数持つ申請に行を足す操作です。単独局モードでは、契約局は1行だけで、発行依頼書編集から登録します。そのため、ボタンは複数局モードのときだけ出します。requirements 14.5 に「契約局情報追加は複数局のときだけ」を足すのは、次に開き直すときにまとめて行います。 | Junichi Noumi | 2026-10-07T19:05:00+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 5 | 3 | 対応せず進める | TWTGM170 の権限ID は、DB レイアウトで定めた、このテーブル専用の値（1:稟議依頼-申請者〜5:再製本-承認者）です。稟議依頼と再製本依頼で権限を分けて持つ必要があり、P82（01〜04）では表せないためです。番の判定は TWTGM170 で行い、P82 は承認履歴の審査権限に使う、という役割分担は変えません。steering/security.md の権限モデルと、requirements の前提（P82 の 02〜04）の書き換えは、次に開き直すときにまとめて行います。 | Junichi Noumi | 2026-10-07T19:05:05+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 1 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:05:10+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 2 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:05:16+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 3 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:05:22+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 1 | 4 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:05:27+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 1 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:05:33+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 2 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:05:40+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 3 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:05:47+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 4 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:05:53+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 5 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:06:00+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 6 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:06:07+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 8 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:06:14+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 9 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:06:20+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 10 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:06:26+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 2 | 14 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:06:33+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 3 | 1 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:06:39+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 3 | 2 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:06:46+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 3 | 3 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:06:52+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 4 | 1 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:06:59+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 4 | 2 | feature:property-basic-info | 5 | Junichi Noumi | 2026-10-07T19:07:06+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:property-basic-info | 5 | specs/property-basic-info/design.md | Junichi Noumi | 2026-10-07T19:13:15+09:00 | 0829e28f5d3a4e0db44e191b174e2518eb0af483f10814026003e86d90d8c7df |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 5 | 1 | 対応せず進める | requirements 1.3・6.7・14.5 の「自分の番」は、状態遷移表でその担当の操作が定義されている状態を指す、と読みます。稟議依頼・修正稟議依頼の 起案済・回覧中 は申請者の番ですが、定義されている操作は発行依頼書登録変更の画面での発番だけです。本画面の更新・切替・契約局取込・契約局DL・契約局情報追加は、定義されていないので受け付けません（4.3・4.5 の除外と同じ考え方）。requirements の文言（1.3・6.7・14.5 に「稟議依頼・修正稟議依頼の起案済・回覧中を除く」を足す）は、次に物件基本情報登録変更の requirements を開き直すときにまとめて直します。 | feature:property-basic-info | 5 |
| feature:property-basic-info | 5 | 2 | 対応せず進める | 契約局情報追加は、契約局を複数持つ申請に行を足す操作です。単独局モードでは、契約局は1行だけで、発行依頼書編集から登録します。そのため、ボタンは複数局モードのときだけ出します。requirements 14.5 に「契約局情報追加は複数局のときだけ」を足すのは、次に開き直すときにまとめて行います。 | feature:property-basic-info | 5 |
| feature:property-basic-info | 5 | 3 | 対応せず進める | TWTGM170 の権限ID は、DB レイアウトで定めた、このテーブル専用の値（1:稟議依頼-申請者〜5:再製本-承認者）です。稟議依頼と再製本依頼で権限を分けて持つ必要があり、P82（01〜04）では表せないためです。番の判定は TWTGM170 で行い、P82 は承認履歴の審査権限に使う、という役割分担は変えません。steering/security.md の権限モデルと、requirements の前提（P82 の 02〜04）の書き換えは、次に開き直すときにまとめて行います。 | feature:property-basic-info | 5 |
