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

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 2026-10-08T09:04:10+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md":"78d7c33b8829b5bb833580aed2aa2e7d8b43dc35be70ab055c35f978fac50b27"} | 9 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務の欠落・矛盾 | 重大 | 67eb5805a4333aa9 | 9ecb8ef99e8941e8 | specs/issue-request/design.md § ドメインモデル（Domain Model） / 発番 ほか 2 か所 | 発番時の保存と 1.3・1.5・9.3 | 発番で担当エリア等を保存する扱いが要件1.3・1.5・9.3と食い違う | ID対応あり・内容不整合（意味判定）。requirements 1.3 は申請者が登録・変更できる状態を受付済・回覧中、受付済・確認中、申請済・差戻しに限り、1.5 は「1.2〜1.4 以外の場合、システムは発行依頼書の登録・変更を受け付けてはならない」とする。一方 design は、起案済・回覧中の申請者が発番で担当エリア・担当エリア名・契約区分・代表局番号・枝番を画面から受け取って TWTGM100 に保存するとしている（§ ドメインモデル の「発番」、§ 設計判断 の判断 1、§ API 契約 の /wtg080/issue）。また 9.3 の「起案済の申請を更新するとき」を「起案済の申請で発番するとき」と読み替え、未起案では担当エリア・契約区分を必須にしないとしている（§ バリデーション設計）。design 自身が「requirements の 1.3・1.5 から意図して外れる」「9.3 の文言から意図して外れる読み方」と書き、根拠を Q-DS-IR-001 としている。Q-DS-IR-001 は今回の confirmed_answers（Q-DS-IR-016〜023）に含まれない | requirements 1.5（または 1.3）に「稟議依頼・修正稟議依頼の起案済・回覧中の申請者は、発番で担当エリア・契約区分・代表局番号・枝番だけを登録・変更できる」を足し、9.3 の「起案済の申請を更新するとき」を「起案済の申請で発番するとき」に直す（Phase 4 への差戻し、または upstream-carryover での一括修正） | 対応せず進める：人の回答（Q-DS-IR-001 の C）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため。ただし承認済み requirements と両立しない状態は残る | 確認済み |  |  |
| 2 | traceability | 業務の欠落・矛盾 | 重大 | e17190fd0145116a | bde9fd56df38ec37 | specs/issue-request/design.md § セキュリティ上の考慮（Security Considerations） / 2.1 | 2.1 の本人が登録した発行依頼書 | 2.1の本人が登録した発行依頼書を申請の登録者で比べており要件と食い違う | ID対応あり・内容不整合（意味判定）。requirements 2.1 は社外ユーザーの対象を「契約稟議起案会社が自社である発行依頼書と、その社外ユーザー本人が登録した発行依頼書」とする。design は「申請の登録者（TWTGM080.RegisteredPerson）が本人」で比べ、発行依頼書がまだ無い申請は物件申請情報の範囲（pbi design の 6.5）で見るとしている。design 自身が「requirements の文言から意図して外れる読み方」と書き、根拠を Q-DS-IR-014 としている（今回の confirmed_answers に含まれない） | requirements 2.1 の「その社外ユーザー本人が登録した発行依頼書」を「その社外ユーザー本人が登録した申請（物件申請情報の登録者）の発行依頼書」に直す | 対応せず進める：人の回答（Q-DS-IR-014）に従った読み方として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | 確認済み |  |  |
| 3 | traceability | 業務の欠落・矛盾 | 重大 | 1377e525037c59e9 | 21e11bb8d735f31b | specs/issue-request/design.md § 発行依頼書登録変更 Service / 作成組織 | 8.1 のログインユーザーのグループ | 8.1のログインユーザーのグループを権限区分と読み替えており要件と食い違う | ID対応あり・内容不整合（意味判定）。requirements 8.1 と steering/security.md `#### 所有権・エンティティ境界` は「P71 で、キー3 がログインユーザーのグループである行」とし、security.md `### 認証 → 認可の契約（AuthContext）` は権限区分（Kengen_Kbn）と所属グループ（グループID ほか）を別の項目としている。design は LoginUserUtils.getAuthority()（権限区分）をキー3 にして P71 を引くとし、「steering/security.md の『ログインユーザーのグループ』から意図して外れる読み方」と書いている。同じ読み替えは property-basic-info の設計検査 2 回目の指摘 13 で「対応せず進める」（steering の文言は次に開き直すときに直す）とされている | requirements 8.1 と steering/security.md の「ログインユーザーのグループ」を「ログインユーザーの権限区分（TWTZM010.Kengen_Kbn）」に直す | 対応せず進める：property-basic-info で同じ読み方が判断済みで、上流の文言は Phase 5 の最後にまとめて直す方針とされているため | 確認済み |  |  |
| 4 | traceability | 業務の欠落・矛盾 | 重大 | 808cd6d6c3aee4b1 | ed91e2366e415e60 | specs/issue-request/design.md § バリデーション設計 / 9.6 | 9.6 の所属①②の必須 | 9.6の所属必須に「選んだ会社が社内」の条件を足しており要件と食い違う | ID対応あり・内容不整合（意味判定）。requirements 9.6 は「社内ユーザーが所属①または所属②を空にして更新した場合、システムはエラーメッセージを表示し、更新を止めなければならない」とし、選んだ会社による条件を持たない。design の検査表（作成組織 所属①・所属②の行）は「社内ユーザー（かつ選んだ会社が社内）で空ならエラー」とし、「requirements の 9.6 から意図して外れる」と書いている。根拠は item-rules.md の 5 | requirements 9.6 に「選んだ作成組織の会社が社内のとき」の条件を足す。または design の条件を 9.6 のとおり社内ユーザーだけに戻す | 対応せず進める：item-rules.md（回答者が渡した資料）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | 確認済み |  |  |
| 5 | traceability | 業務の欠落・矛盾 | 重大 | 59f785e1e0f1c327 | 4b622b75d1350476 | specs/issue-request/design.md § コンポーネントとインターフェース（Components and Interfaces） | 機能固有の監視項目 | 機能固有の監視項目（無いならその旨）がdesignに書かれていない | 可観測性のうちメトリクス（監視）の柱が未反映。steering/non-functional.md の冒頭の分担と `### 監視 / ヘルス` は「機能固有の監視項目は design の Components and Interfaces」に書くとしているが、design には本 feature の監視項目の有無の記述が無い（ログの柱は `## 機能固有のエラー処理` の「ログ」で反映済み。トレースは non-functional.md が専用の ID を発行しないと定めており、feature 固有に書く事項は無い）。依存先の pbi design は同じ節に「監視：本 feature 固有の監視項目は無い。既存の WiNG の監視に任せる」と書いている | `## コンポーネントとインターフェース（Components and Interfaces）` の冒頭の注記の後に「- **監視**: 本 feature 固有の監視項目は無い。既存の WiNG の監視に任せる（`steering/non-functional.md` の `### 監視 / ヘルス`）」を足す | 修正：steering が置き場を design に指定しており、既存の運用に任せる旨を 1 行書けば足りるため | 確認済み |  |  |
| 6 | steering-conformance | 業務の欠落・矛盾 | 重大 | 0ec33d53f3ba11d6 | a42e5f847c13d726 | specs/issue-request/design.md § 機能固有エラーコード ほか 2 か所 | 業務エラー・排他エラーの扱い | 業務・排他エラーを例外にせずBindingResultに積む方式がtech.mdと食い違う | 矛盾。steering/tech.md `### 例外処理フロー` は「画面：業務ロジック（Service）」で業務上の失敗を ApplicationException の派生（排他は ExclusiveException）としてメッセージキー付きで投げるとし（BindingResult に積むのは入力チェックの行だけ）、`## コード規約` の排他制御も「ExclusiveFG が一致しなければ ExclusiveException を投げる」と定める。design は WTG-100030 と GEF-000027 を例外にせず BindingResult に積んで同じ画面に戻すとしている（§ 機能固有エラーコード の表の後の注記、§ サービスインターフェース の update・saveDraft・issueNumber のエラー、§ 状態管理 の並行制御、§ 設計判断 の判断 4）。design 自身が「steering/tech.md の方式から意図して外れる」と書いている | steering/tech.md の `### 例外処理フロー` と `## コード規約` の排他制御に「入力を残す必要がある画面は、業務エラー・排他エラーも BindingResult に積んで同じ画面に戻してよい」を足す（Phase 2 への差戻し、または upstream-carryover での一括修正） | 対応せず進める：pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | 確認済み |  |  |
| 7 | steering-conformance | 業務の欠落・矛盾 | 重大 | 7dceae9061457785 | 8386e642b72fcab9 | specs/issue-request/design.md § 技術スタック（Technology Stack） / Infrastructure / Runtime | 開発端末の JDK | 開発端末のJDK 1.8がtech.mdの必須ツールJDK 1.7と食い違う | 矛盾。steering/tech.md `### 必須ツール` は JDK を「1.7（1.7.0.55）／コンパイルと実行」と定めているが、design の技術スタックは「開発端末の JDK 1.8（-source/-target 1.7）」を開発端末でのコンパイルと自動テストの実行に使うとしている。design 自身が「steering/tech.md から意図して外れる」と書き、根拠を Q-DS-PBI-014（物件基本情報登録変更と同じ）としている | steering/tech.md の `### 必須ツール` に「開発端末は JDK 1.8（-source/-target 1.7）でもよい」を足す（Phase 2 への差戻し、または upstream-carryover での一括修正） | 対応せず進める：pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | 確認済み |  |  |
| 8 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | da7a68a3f377cd0c | 7d9b88c52d0fa35f | specs/issue-request/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 物件基本情報登録変更との口 ほか 1 か所 | pbi design の公開契約に無い前提 | pbi designの公開契約に無い前提（戻りの入口・発番日時・複製の申請者）に依存 | 依存先 specs/property-basic-info/design.md（approved）の公開契約に無い要素を前提にしている。(1) 戻り：/wtg080/return から /wtg070/ へ申請No を渡して forward するとしているが、pbi の API 契約の /wtg070 は「なし（メニューからの新規）」で、申請No を受けて開く口は /wtg070/pushApplicationNo（申請状況一覧から）だけ。遷移元の値（1・2・3）と GET の形も pbi には無い（pbi は「申請No・連番・遷移元を渡す」だけ）。(2) recordNumbering：pbi の入出力・事後条件は「受付済・回覧中にし、承認履歴に発番の行が 1 行増える」だけで、発番日時（Hatsuban_Uketsuke_DateTime）と更新者名を入れること、承認履歴の行の値（判定 "11"・審査権限 "02" ほか）は書かれていない。requirements 3.3 の発番日時の記録はこれに依存する。(3) 複製：申請者（Application_Name）にログインユーザーのユーザーID を入れる決まり（§ ドメインモデル の複製）は pbi の複製の記述に無い。design 自身が 3 点とも「pbi design にまだ書かれていない。Phase 5 の最後にまとめて直す（upstream-carryover）」と書いている | pbi design に (1) 申請No を受けて開く初期表示の口（または /wtg080/return の戻り先を /wtg070/pushApplicationNo にする）と遷移元の値 1・2・3、(2) recordNumbering が発番日時・更新者名を入れることと承認履歴の行の値、(3) 発行依頼書の複製で申請者にユーザーID を入れることを足す | 対応せず進める：design に明記され、pbi design は Phase 5 の最後にまとめて直す方針とされているため。直すまでは pbi の実装がこの前提を満たさない | 確認済み |  |  |
| 9 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | 91d9e0de67c515b8 | 0e981b6baf2f1604 | specs/issue-request/design.md § 状態管理（State Management） / 並行制御 ほか 3 か所 | TWTGM080 のロックと ExclusiveFG の照合 | 更新・一時保存でTWTGM080を自Mapperでロック・照合し公開契約を通らない | 依存先の内部に直接依存している。design は更新・一時保存・発番の最初に、本 feature の Mapper で物件申請情報（TWTGM080）の行を SELECT … FOR UPDATE でロックして ExclusiveFG を照合するとしている（§ 状態管理 の並行制御、§ ドメインモデル の集約とトランザクション境界、§ 依存してよい対象 の依存の制約、§ コンポーネント一覧 の発行依頼書登録変更 Mapper）。TWTGM080 は pbi design が持つ表で、pbi の公開契約（WTG 申請状態サービスの getApplication・resolveTurn・getAuthorities・transit・recordNumbering・getExternalScope と、データ契約の TWTGM100 から読む列）には、他の feature が TWTGM080 の行をロックし ExclusiveFG を照合する口・取り決めが無い。confirmed_answers の Q-DS-IR-022 1. は「TWTGM080 の排他用の値は、発番の recordNumbering が扱います」とするだけで、更新・一時保存での扱いは design が「その確認への回答」として引く回答によるが、その回答は今回の confirmed_answers に含まれない | 次のどちらかを決める。A：WTG 申請状態サービスに申請の行をロックして ExclusiveFG を照合する口（例 lockApplication）を足し、本 feature はそれを呼ぶ（pbi design を upstream-carryover に入れる）。B：本 feature の Mapper から TWTGM080 をロック・照合（書き換えない）することを pbi design のデータ契約に明記する | 質問：pbi の公開契約に口を足すか、直接のロックと照合を公開の取り決めにするかは、依存先の設計に関わる人の判断が要るため | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | 人間による確認（requirements.md 1.3・1.5・9.3 の修正、または本 design の修正） | 発番時の保存と 9.3 の読み方（Q-DS-IR-001 の回答）が承認済みの requirements と食い違っている。requirements 側を直す場合は Phase 4 が宛先になる |
| 2 | 人間による確認（requirements.md 2.1 の修正、または本 design の修正） | 社外ユーザーの範囲の比べ方（Q-DS-IR-014 の回答）が承認済みの requirements と食い違っている。requirements 側を直す場合は Phase 4 が宛先になる |
| 3 | 人間による確認（requirements.md 8.1 と steering/security.md の修正、または本 design の修正） | P71 のキー3 の「グループ」の意味が requirements・steering の記述と食い違っている。steering 側は Phase 2、requirements 側は Phase 4 が宛先になる |
| 4 | 人間による確認（requirements.md 9.6 の修正、または本 design の修正） | 所属①②の必須の条件（item-rules.md の 5）が承認済みの requirements と食い違っている。requirements 側を直す場合は Phase 4 が宛先になる |
| 6 | 人間による確認（steering/tech.md の修正、または本 design の修正） | 業務エラー・排他エラーの扱いが steering の例外処理フロー・排他制御と食い違っている。steering 側を直す場合は Phase 2 が宛先になる |
| 7 | 人間による確認（steering/tech.md の修正、または本 design の修正） | 開発端末の JDK（Q-DS-PBI-014 の回答）が steering の必須ツールと食い違っている。steering 側を直す場合は Phase 2 が宛先になる |
| 8 | 人間による確認（specs/property-basic-info/design.md の修正） | 依存先 pbi design の公開契約に、本 design が前提にする戻りの入口・recordNumbering の記録内容・複製の申請者が無い。pbi design を開き直す場合は Phase 5（property-basic-info）が宛先になる |
| 9 | 人間による確認（specs/property-basic-info/design.md の修正、または本 design の修正） | TWTGM080 のロックと ExclusiveFG の照合を他の feature が行う取り決めが pbi design の公開契約に無い。pbi design を開き直す場合は Phase 5（property-basic-info）が宛先になる |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| steering-conformance | specs/issue-request/design.md § セキュリティ上の考慮（Security Considerations） / CSRF ほか（§ API 契約 の注記、§ 設計判断 の判断 5） | 一時保存・発番の URL が CSRF の照合に乗らず steering/security.md の攻撃対策と食い違う | answer:design-authoring-generate[issue-request] |
| steering-conformance | specs/issue-request/design.md § API 契約（API Contract） / /zoom/zwtz074〜076 | ズームの URL が tech.md の URL の規約（/&lt;機能ID小文字&gt;/&lt;アクション&gt;）と違う形になる | answer:design-authoring-generate[issue-request] |
| steering-conformance | specs/issue-request/design.md § API 契約（API Contract） / /wtg080/calcTaxAdjustment・/wtg080/changeKeiyakuSyubetsuTutorial | 画面内で JSON を返す口を新しく 2 つ置く（api-standards.md の「JSON を返すのは既存の 2 か所だけ」） | answer:design-authoring-generate[issue-request] |
| traceability | specs/issue-request/design.md § ドメインモデル（Domain Model） / 複数局の更新 | 複数局を発行依頼書編集で更新したとき金額を合計せず入力値で上書きする（5.3） | answer:design-authoring-generate[issue-request] |
| dependency-boundary-conformance | specs/issue-request/design.md § 依存してよい対象（Allowed Dependencies） / getApplication・getApplicantName | getApplication の単独複数局ﾌﾗｸﾞ・申請依頼日時と getApplicantName が pbi design の公開契約にまだ無い | answer:design-authoring-generate[issue-request] |
| dependency-boundary-conformance | specs/issue-request/design.md § ドメインモデル（Domain Model） / 基地局番号 | 申請情報欄の基地局番号を連番 1 で初期表示することが pbi design にまだ無い | answer:design-authoring-generate[issue-request] |
| dependency-boundary-conformance | specs/issue-request/design.md § 依存してよい対象（Allowed Dependencies） / WTKeikakuJudgeUtils | 契約区分の自動設定で共通部品 WTKeikakuJudgeUtils.chkKichikyoku を直接呼ぶ | answer:design-authoring-generate[issue-request] |
| evidence-guard | specs/issue-request/design.md § 移行方針（Migration Strategy） / TWTZM370 の 4 行 | 税率マスタの投入する行（資料では「案」）を確定値として書いている | answer:design-authoring-generate[issue-request] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 1 | 対応せず進める | AI 推奨を採用: 人の回答（Q-DS-IR-001 の C）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため。ただし承認済み requirements と両立しない状態は残る | Junichi Noumi | 2026-10-08T10:13:52+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 2 | 対応せず進める | AI 推奨を採用: 人の回答（Q-DS-IR-014）に従った読み方として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | Junichi Noumi | 2026-10-08T10:13:55+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 3 | 対応せず進める | グループは権限区分と読むのが業務の決まりで、物件基本情報で判断済みです。上流をまとめて直す一覧に「requirements（issue-request）8.1：ログインユーザーのグループ→権限区分」を足してください。文言は security.md 285行目と一緒に Phase 5 の最後に直します。 | Junichi Noumi | 2026-10-08T10:13:58+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 4 | 対応せず進める | AI 推奨を採用: item-rules.md（回答者が渡した資料）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | Junichi Noumi | 2026-10-08T10:14:01+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 5 | 修正 | AI 推奨を採用: steering が置き場を design に指定しており、既存の運用に任せる旨を 1 行書けば足りるため | Junichi Noumi | 2026-10-08T10:14:04+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 6 | 対応せず進める | AI 推奨を採用: pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | Junichi Noumi | 2026-10-08T10:14:07+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 7 | 対応せず進める | AI 推奨を採用: pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | Junichi Noumi | 2026-10-08T10:14:10+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 8 | 対応せず進める | AI 推奨を採用: design に明記され、pbi design は Phase 5 の最後にまとめて直す方針とされているため。直すまでは pbi の実装がこの前提を満たさない | Junichi Noumi | 2026-10-08T10:14:13+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 9 | 修正 | 更新・一時保存では TWTGM080 をロックも照合もしないでください。排他は TWTGM100・TWTGM140 の ExclusiveFG だけで行います。申請の状態が変わったかどうかは、更新・一時保存・発番の処理の最初に WTG 申請状態サービスの getApplication で申請を取り直し、canOperate で今もその操作ができるかを判定します。できなければ WTG-100030 を積んで同じ画面に戻します。pbi の公開契約に口は足しません。 | Junichi Noumi | 2026-10-08T10:14:16+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 2 | 2026-10-08T10:22:32+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md":"ebb788e7b5bfae8509a0d1aa684b52616398093df6a8d9ff9ba4dec750d7c7d9"} | 6 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務の欠落・矛盾 | 重大 | 67eb5805a4333aa9 | 54b9a21760679b8a | specs/issue-request/design.md § ドメインモデル（Domain Model） / 発番 ほか 2 か所 | 発番時の保存と 1.3・1.5・9.3 | 発番で担当エリア等を保存する扱いが要件1.3・1.5・9.3と食い違う | ID対応あり・内容不整合（意味判定。節が変わったため再検査し、残っていることを確かめた。1 回目 #1 と同じ指摘）。requirements 1.3 は申請者が登録・変更できる状態を受付済・回覧中、受付済・確認中、申請済・差戻しに限り、1.5 は「1.2〜1.4 以外の場合、システムは発行依頼書の登録・変更を受け付けてはならない」とする。design は、起案済・回覧中の申請者が発番で担当エリア・担当エリア名・契約区分・代表局番号・枝番を画面から受け取って TWTGM100 に保存するとしている（§ ドメインモデル の「発番」、§ 設計判断 の判断 1、§ API 契約 の /wtg080/issue）。また 9.3 の「起案済の申請を更新するとき」を「起案済の申請で発番するとき」と読み替えている（§ バリデーション設計）。design 自身が「requirements の 1.3・1.5 から意図して外れる」と書き、根拠を Q-DS-IR-001 としている（confirmed_answers の Q-DS-IR-016〜023 には含まれない） | requirements 1.5（または 1.3）に「稟議依頼・修正稟議依頼の起案済・回覧中の申請者は、発番で担当エリア・契約区分・代表局番号・枝番だけを登録・変更できる」を足し、9.3 の「起案済の申請を更新するとき」を「起案済の申請で発番するとき」に直す（Phase 4 への差戻し、または upstream-carryover での一括修正） | 対応せず進める：人の回答（Q-DS-IR-001 の C）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため。ただし承認済み requirements と両立しない状態は残る | 確認済み |  |  |
| 2 | traceability | 業務の欠落・矛盾 | 重大 | 1377e525037c59e9 | 08a82d52e971259e | specs/issue-request/design.md § 発行依頼書登録変更 Service / 作成組織 | 8.1 のログインユーザーのグループ | 8.1のログインユーザーのグループを権限区分と読み替えており要件と食い違う | ID対応あり・内容不整合（意味判定。節が変わったため再検査し、残っていることを確かめた。1 回目 #3 と同じ指摘）。requirements 8.1 と steering/security.md `#### 所有権・エンティティ境界` は「P71 で、キー3 がログインユーザーのグループである行」とする。design は LoginUserUtils.getAuthority()（権限区分）をキー3 にして P71 を引くとし、「steering/security.md の『ログインユーザーのグループ』から意図して外れる読み方」と書いている。1 回目の判断の理由は、上流をまとめて直す一覧に「requirements（issue-request）8.1：ログインユーザーのグループ→権限区分」を足すとしている | requirements 8.1 と steering/security.md の「ログインユーザーのグループ」を「ログインユーザーの権限区分（TWTZM010.Kengen_Kbn）」に直す（upstream-carryover での一括修正） | 対応せず進める：グループを権限区分と読むことは物件基本情報と 1 回目の判断で決まっており、上流の文言は Phase 5 の最後にまとめて直す方針とされているため | 確認済み |  |  |
| 3 | steering-conformance | 業務の欠落・矛盾 | 重大 | 0ec33d53f3ba11d6 | 01dd68755c9cd4e3 | specs/issue-request/design.md § 機能固有エラーコード ほか 2 か所 | 業務エラー・排他エラーの扱い | 業務・排他エラーを例外にせずBindingResultに積む方式がtech.mdと食い違う | 矛盾（節が変わったため再検査し、残っていることを確かめた。1 回目 #6 と同じ指摘）。steering/tech.md `### 例外処理フロー` は「画面：業務ロジック（Service）」で業務上の失敗を ApplicationException の派生（排他は ExclusiveException）としてメッセージキー付きで投げるとし、`## コード規約` の排他制御も「ExclusiveFG が一致しなければ ExclusiveException を投げる」と定める。design は WTG-100030 と GEF-000027 を例外にせず BindingResult に積んで同じ画面に戻すとしている（§ 機能固有エラーコード の表の後の注記、§ サービスインターフェース の update・saveDraft・issueNumber のエラー、§ 状態管理 の並行制御、§ 設計判断 の判断 4）。design 自身が「steering/tech.md の方式から意図して外れる」と書いている | steering/tech.md の `### 例外処理フロー` と `## コード規約` の排他制御に「入力を残す必要がある画面は、業務エラー・排他エラーも BindingResult に積んで同じ画面に戻してよい」を足す（Phase 2 への差戻し、または upstream-carryover での一括修正） | 対応せず進める：pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | 確認済み |  |  |
| 4 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | 2a924414f3d86424 | 327b095a744627d8 | specs/issue-request/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 物件基本情報との口 ほか 1 か所 | pbi design の公開契約に無い前提 | pbi designの公開契約に無い前提（戻りの入口・発番日時・複製の申請者）に依存 | 節が変わったため再検査し、残っていることを確かめた（1 回目 #8 と同じ指摘）。依存先 specs/property-basic-info/design.md（approved）の公開契約に無い要素を前提にしている。(1) 戻り：/wtg080/return から /wtg070/ へ申請No を渡して forward するとしているが、pbi の API 契約に申請No を受けて初期表示する /wtg070/ の口は無く、遷移元の値（1・2・3）と GET の形も pbi には無い。(2) recordNumbering：pbi の入出力・事後条件（サービスインターフェースの表と事後条件）は「受付済・回覧中にし、承認履歴に発番の行が 1 行増える」だけで、発番日時（Hatsuban_Uketsuke_DateTime）と更新者名を入れること、承認履歴の行の値（判定 "11"・審査権限 "02" ほか）は書かれていない。(3) 複製：申請者（Application_Name）にログインユーザーのユーザーID を入れる決まり（§ ドメインモデル の修正稟議・再製本の複製）は pbi の複製の記述に無い。design 自身が 3 点とも「pbi design にまだ書かれていない。Phase 5 の最後にまとめて直す（upstream-carryover）」と書いている | pbi design に (1) 申請No を受けて開く初期表示の口と遷移元の値 1・2・3、(2) recordNumbering が発番日時・更新者名を入れることと承認履歴の行の値、(3) 発行依頼書の複製で申請者にユーザーID を入れることを足す | 対応せず進める：design に明記され、pbi design は Phase 5 の最後にまとめて直す方針とされているため。直すまでは pbi の実装がこの前提を満たさない | 確認済み |  |  |
| 5 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | 3418bc68d5ec2871 | 08a82d52e971259e | specs/issue-request/design.md § 発行依頼書登録変更 Service / 発番の手順 ほか 5 か所 | canOperate の一時保存・発番 | canOperateに一時保存・発番の操作が無く、公開契約に無い判定に依存している | 1 回目 #9 の修正で、更新・一時保存・発番の最初に getApplication で申請を取り直し、canOperate で「今もその操作ができるか」を判定するとした（§ 発行依頼書登録変更 Service の発番の手順 1・更新の手順・一時保存の手順、§ サービスインターフェース の saveDraft・issueNumber のエラー「canOperate で一時保存できない／発番できない → WTG-100030」、§ ドメインモデル の集約とトランザクション境界、§ 依存してよい対象 の依存の制約、§ 状態管理 の並行制御、§ エラー時の分岐フロー）。一方 pbi design の canOperate の入力の「操作」は、申請依頼・確認・申請・承認・差戻し・取下げ・更新・削除・単独局と複数局の切替・契約局取込・契約局DL・処理状況・契約局情報追加・発行依頼書編集・契約局情報の並替え・契約局情報の削除だけで、一時保存と発番は無い（pbi design § サービスインターフェース の canOperate の行）。また pbi の番の表は、起案済・回覧中の申請者について「定義されている操作は発行依頼書登録変更画面での発番だけ」とするが、canOperate の可否の条件に発番は含まれない。requirements 1.8（起案者以外に一時保存を使わせない）と 3.5（申請者でない場合は発番を受け付けない）のサーバー側の拒否はこの判定に頼っており、recordNumbering は状態（起案済・回覧中か）だけを照合し、申請者の権限は見ない（pbi design の recordNumbering の行）。design には、一時保存・発番をどの canOperate の操作（またはほかの判定）で決めるかが書かれていない | 次のどちらかを決める。A：pbi の口は変えず、本 feature の Service で、一時保存は「canOperate（更新）が可で、resolveTurn が起案者」、発番は「依頼内容が稟議依頼・修正稟議依頼、起案済・回覧中、resolveTurn が申請者、getAuthorities に権限ID 1」で判定すると書く（ボタンの表の条件と同じ）。B：pbi design の canOperate の操作に一時保存・発番と、その可否の条件を足す（pbi design を upstream-carryover に入れる） | 質問：1 回目 #9 の判断は「canOperate で今もその操作ができるかを判定する」「pbi の公開契約に口は足さない」としており、canOperate の操作を足すことが口の追加に当たるかは人の判断が要るため | 確認済み |  |  |
| 6 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | 3e8af617bc971299 | d3e32e45de8cf114 | specs/issue-request/design.md § 状態管理（State Management） / 並行制御 ほか 1 か所 | 照合する行が無いときの排他 | 照合する行が無い新規・消えた行の更新を排他で止めず、連番の重複などが起きうる | 1 回目 #9 の修正で TWTGM080 のロック・照合をやめ、更新・一時保存の排他を開いている TWTGM100・TWTGM140 の行の ExclusiveFG だけで行うとした（§ 状態管理 の並行制御、§ ドメインモデル の集約とトランザクション境界）。並行制御は「行がまだ無い新規の登録では照合しない」とし、次の場合を止める手段が書かれていない。(1) 契約局情報追加（遷移元 3）の連番は物件基本情報登録変更から受け取った「件数＋1」（§ ドメインモデル の新しい契約局）なので、2 人が同時に追加すると同じ連番の行が 2 行できる。一意キー AK_TWTGM140_1 は計画基地局番号を含むため、基地局番号が違えば DB でも止まらない。同じ申請No の基地局番号の重複チェック（WTG-100043）も、同時の登録では互いの行を見ない。(2) 発行依頼書が無い申請で 2 人が同時に更新・一時保存すると、両方が TWTGM100 を新しく登録しようとし、AK_TWTGM100_1 の一意制約違反が業務エラー（GEF-000027）でなく予期しない例外になる。(3) 画面を開いた後に、物件基本情報登録変更の契約局情報の並替え・削除や契約情報取込の洗替で、開いている行が消える・連番が変わると、古い画面からの更新は照合する行が無いため新規として登録され、削除した行が戻る・連番が重なるおそれがある（§ データ契約と外部連携 のサービス間は、取込が行を書き換えて ExclusiveFG を新しくする場合だけを前提にしている）。前回までは申請の TWTGM080 の行のロックでこれらが直列になっていた | 次のどれかを決める。A：新しい行の登録と、開いていた行が見つからないときは、同じトランザクションで同じ申請No の行（連番・基地局番号）を読み直し、連番か基地局番号が既にある、または画面が既存の行として開かれていた（排他用の値を持っていた）なら GEF-000027 にする。B：新しい行の登録では、その申請No の TWTGM100 の行（無ければ連番 1 の TWTGM140）をロックして直列にする（TWTGM100・TWTGM140 だけで排他するという判断の範囲で行う）。C：起こりにくいとして許容し、重なった連番は物件基本情報登録変更の並替えで直す運用にする（その旨を design に書く） | 質問：1 回目 #9 の判断（排他は TWTGM100・TWTGM140 の ExclusiveFG だけで行う）の範囲で、照合する行が無いときの扱いをどうするかは人の判断が要るため | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | 人間による確認（requirements.md 1.3・1.5・9.3 の修正、または本 design の修正） | 発番時の保存と 9.3 の読み方（Q-DS-IR-001 の回答）が承認済みの requirements と食い違っている。requirements 側を直す場合は Phase 4 が宛先になる |
| 2 | 人間による確認（requirements.md 8.1 と steering/security.md の修正） | P71 のキー3 の「グループ」の意味が requirements・steering の記述と食い違っている。steering 側は Phase 2、requirements 側は Phase 4 が宛先になる |
| 3 | 人間による確認（steering/tech.md の修正、または本 design の修正） | 業務エラー・排他エラーの扱いが steering の例外処理フロー・排他制御と食い違っている。steering 側を直す場合は Phase 2 が宛先になる |
| 4 | 人間による確認（specs/property-basic-info/design.md の修正） | 依存先 pbi design の公開契約に、本 design が前提にする戻りの入口・recordNumbering の記録内容・複製の申請者が無い。pbi design を開き直す場合は Phase 5（property-basic-info）が宛先になる |
| 5 | 人間による確認（specs/property-basic-info/design.md の修正、または本 design の修正） | pbi design の canOperate の操作に一時保存・発番が無い。canOperate に操作を足す場合は Phase 5（property-basic-info）が宛先になる |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/issue-request/design.md § ドメインモデル（Domain Model） / 複数局の更新 | 複数局を発行依頼書編集で更新したとき金額を合計せず入力値で上書きする（5.3） | answer:design-authoring-generate[issue-request] |
| traceability | specs/issue-request/design.md § ドメインモデル（Domain Model） / コードと (ﾌﾘｰﾌｫｰﾑ) の組の金額の項目 | コードの列は合計せず連番 1 の値を入れ、合計は (ﾌﾘｰﾌｫｰﾑ) の列に入れる（5.3） | answer:design-authoring-generate[issue-request] |
| dependency-boundary-conformance | specs/issue-request/design.md § 依存してよい対象（Allowed Dependencies） / getApplication・getApplicantName | getApplication の単独複数局ﾌﾗｸﾞ・申請依頼日時と getApplicantName が pbi design の公開契約にまだ無い | answer:design-authoring-generate[issue-request] |
| dependency-boundary-conformance | specs/issue-request/design.md § ドメインモデル（Domain Model） / 基地局番号 | 申請情報欄の基地局番号を連番 1 で初期表示することが pbi design にまだ無い | answer:design-authoring-generate[issue-request] |
| dependency-boundary-conformance | specs/issue-request/design.md § 依存してよい対象（Allowed Dependencies） / WTKeikakuJudgeUtils | 契約区分の自動設定で共通部品 WTKeikakuJudgeUtils.chkKichikyoku を直接呼ぶ | answer:design-authoring-generate[issue-request] |
| steering-conformance | specs/issue-request/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / チュートリアルとの受け渡し | 画面内で JSON を返す口 /wtg080/changeKeiyakuSyubetsuTutorial を新しく置く（api-standards.md） | answer:design-authoring-generate[issue-request] |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 5 | feature:issue-request | 2 | system（自動）：再検査で再検出なし | 2026-10-08T10:27:30+09:00 |
| feature:issue-request | 1 | 9 | feature:issue-request | 2 | system（自動）：再検査で再検出なし | 2026-10-08T10:27:30+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 2 | 1 | 対応せず進める | AI 推奨を採用: 人の回答（Q-DS-IR-001 の C）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため。ただし承認済み requirements と両立しない状態は残る | Junichi Noumi | 2026-10-08T10:40:46+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 2 | 2 | 対応せず進める | AI 推奨を採用: グループを権限区分と読むことは物件基本情報と 1 回目の判断で決まっており、上流の文言は Phase 5 の最後にまとめて直す方針とされているため | Junichi Noumi | 2026-10-08T10:40:49+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 2 | 3 | 対応せず進める | AI 推奨を採用: pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | Junichi Noumi | 2026-10-08T10:40:52+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 2 | 4 | 対応せず進める | AI 推奨を採用: design に明記され、pbi design は Phase 5 の最後にまとめて直す方針とされているため。直すまでは pbi の実装がこの前提を満たさない | Junichi Noumi | 2026-10-08T10:40:55+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 2 | 5 | 修正 | pbi の口は変えません。canOperate は使わず、この feature の Service で判定します。処理の最初に getApplication で申請を取り直し、resolveTurn で番を、getAuthorities で審査権限を取ります。そのうえで、画面を開いたときの入力可否と同じ規則（requirements 1.2〜1.4）で、今もその操作ができるかを判定します。一時保存は、さらに起案者の番のときだけです。発番は、起案済・回覧中で申請者の番のときだけです。最後の確定は recordNumbering の状態の検査に任せます。できなければ WTG-100030 を積んで同じ画面に戻します。1回目 #9 の「canOperate で判定」はこの内容に置き換えます。 | Junichi Noumi | 2026-10-08T10:40:58+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 2 | 6 | 修正 | 次のとおりにします。・開いていた行（TWTGM100 か TWTGM140）が見つからないときは、排他エラー（GEF-000027）にします。・契約局情報追加では、TWTGM100 の行をロック（FOR UPDATE）して照合します。これで同じ申請への追加・更新は1本ずつになります。そのうえで、登録しようとする連番が既にあれば GEF-000027 にします。・発行依頼書の新規登録（TWTGM100 がまだ無い）では、登録の直前に同じ申請No の行があれば GEF-000027 にします。同時に登録されて一意キー違反になったときも GEF-000027 にします。いずれも例外を投げず、BindingResult に積んで同じ画面に戻します。 | Junichi Noumi | 2026-10-08T10:41:02+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 3 | 2026-10-08T10:43:26+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md":"41e170fb392d988435f2305347d8ee630842c501856776f86c941b0b7c1760d6"} | 2 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | dependency-boundary-conformance | 業務のあいまい・不足 | 要判断 | 0477f6815a155c24 | c813334142ba1b07 | specs/issue-request/design.md § 状態管理（State Management） / 並行制御 ほか 2 か所 | 契約局情報追加の排他用の値 | 遷移元3の追加で照合するTWTGM100の排他用の値と、発行依頼書が無いときの扱いが無い | 2 回目 #6 の修正（判断「契約局情報追加では、TWTGM100 の行をロック（FOR UPDATE）して照合します」）の反映が一部足りない。(1) § 発行依頼書登録変更 Service の「照合する行が無いときの扱い」は「契約局情報追加（遷移元 3 の新しい連番の登録）では、TWTGM100 の行を SELECT … FOR UPDATE でロックして照合する」とする。一方 § 状態管理 の並行制御は、画面に持たせる排他用の値を「開いている発行依頼書（2 は TWTGM100）か契約局（1・3 はその連番の TWTGM140）の行の ExclusiveFG」とし、§ サービスインターフェース の後の事前条件も「画面を表示したときの開いている行（TWTGM100 か TWTGM140）の排他用の値」とする。遷移元 3 の新しい連番の TWTGM140 の行はまだ無いので、TWTGM100 と照合する値を画面がいつ受け取り持つのかが書かれていない。(2) 物件基本情報登録変更の design は契約局情報追加ボタンを canOperate の条件だけで出し、発行依頼書（TWTGM100）が無い申請での契約局情報追加を止める記述が無い（pbi design の契約局情報の操作の条件、/wtg070/addKeyaku の行。WTG-100022 は発行依頼書編集だけ）。requirements 1.9 も発行依頼書が無い申請での遷移を新規の登録として開くとする。TWTGM100 が無い申請で遷移元 3 から更新・一時保存したとき、ロックして照合する TWTGM100 の行が無く、どう直列にするか（GEF-000027 にするか、発行依頼書の新規登録と同じ扱いにするか）が書かれていない | (1) は § 状態管理 の並行制御と事前条件に「遷移元 3 では、TWTGM100 の行の ExclusiveFG を画面に持たせ、更新・一時保存で照合する」を足す。(2) は次のどれかを決める。A：TWTGM100 が無い申請での契約局情報追加は、発行依頼書の新規登録と同じく、登録の直前に同じ申請No・同じ連番の行があれば GEF-000027 にする（一意キー違反も GEF-000027）。B：TWTGM100 が無い申請では遷移元 3 の更新・一時保存を受け付けず、発行依頼書編集から先に発行依頼書を登録させる（エラーのキーも決める）。C：その他 | 質問：(1) は判断のとおり書き足せば足りるが、(2) の TWTGM100 が無いときの扱いは 2 回目 #6 の判断に含まれておらず、人の判断が要るため | 確認済み |  |  |
| 2 | traceability | 業務のあいまい・不足 | 要判断 | 51087d5948b921f3 | c813334142ba1b07 | specs/issue-request/design.md § 状態管理（State Management） / 並行制御 | 複数局の金額の合計の同時更新 | 契約局の同時更新で、複数局のTWTGM100の金額の合計が古い値のまま残りうる | requirements 5.3 は「申請が複数局の場合、発行依頼書の金額を、この画面の値とほかの契約局の金額の合計にしなければならない」とする。design は契約局（1・3）の更新で、その連番の TWTGM140 を書いた後に全契約局の合計で TWTGM100 を入れ直すとし（§ ドメインモデル の契約局の更新）、更新の手順では開いている TWTGM140 の行だけをロックして照合する（§ 発行依頼書登録変更 Service の更新の手順）。§ 状態管理 の並行制御は「同じ申請の別の契約局を 2 人が同時に開いて順に更新しても、開いている行が違えば排他エラーにならない（複数局の TWTGM100 の合計は、後から更新した契約局のときに入れ直される）」とする。2 つの更新が重なると、後の更新はほかの契約局の金額を先の更新の確定前に読んで合計し、TWTGM100 を上書きしうる。この場合、先の更新の金額が合計に入らないまま残り、次に契約局を更新するまで 5.3 を満たさない。TWTGM100 の行のロックは契約局情報追加でだけ行う（§ 発行依頼書登録変更 Service の照合する行が無いときの扱い）。2 回目 #6 の判断理由は「これで同じ申請への追加・更新は1本ずつになります」としているが、契約局の更新どうしは 1 本ずつにならない（意味判定：ID 対応あり・同時更新の異常系が未充足） | 次のどれかを決める。A：契約局（1・3）の更新・一時保存でも、最初に同じ申請No の TWTGM100 の行を SELECT … FOR UPDATE でロックしてから合計を読み、同じ申請への契約局の更新を 1 本ずつにする（TWTGM100 の ExclusiveFG は照合しない）。B：重なったときは合計が次の契約局の更新まで古いままになることを許し、§ 状態管理 の「後から更新した契約局のときに入れ直される」をその旨に直す | 質問：同時更新での合計の正しさをどこまで保証するかは人の判断が要るため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/issue-request/design.md § ドメインモデル（Domain Model） / 複数局の更新 | 複数局を発行依頼書編集で更新したとき金額を合計せず入力値で上書きする（5.3） | answer:design-authoring-generate[issue-request] |
| traceability | specs/issue-request/design.md § ドメインモデル（Domain Model） / コードと (ﾌﾘｰﾌｫｰﾑ) の組の金額の項目 | コードの列は合計せず連番 1 の値を入れ、合計は (ﾌﾘｰﾌｫｰﾑ) の列に入れる（5.3） | answer:design-authoring-generate[issue-request] |
| dependency-boundary-conformance | specs/issue-request/design.md § 依存してよい対象（Allowed Dependencies） / getApplication・getApplicantName | getApplication の単独複数局ﾌﾗｸﾞ・申請依頼日時と getApplicantName が pbi design の公開契約にまだ無い | answer:design-authoring-generate[issue-request] |
| dependency-boundary-conformance | specs/issue-request/design.md § ドメインモデル（Domain Model） / 基地局番号 | 申請情報欄の基地局番号を連番 1 で初期表示することが pbi design にまだ無い | answer:design-authoring-generate[issue-request] |
| dependency-boundary-conformance | specs/issue-request/design.md § 依存してよい対象（Allowed Dependencies） / WTKeikakuJudgeUtils | 契約区分の自動設定で共通部品 WTKeikakuJudgeUtils.chkKichikyoku を直接呼ぶ | answer:design-authoring-generate[issue-request] |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 2 | 5 | feature:issue-request | 3 | system（自動）：再検査で再検出なし | 2026-10-08T10:46:59+09:00 |
| feature:issue-request | 2 | 6 | feature:issue-request | 3 | system（自動）：再検査で再検出なし | 2026-10-08T10:46:59+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 3 | 1 | 修正 | (1)はそのとおり。(2)はB。TWTGM100 が無い申請では、遷移元3の更新・一時保存を受け付けません。キーは WTG-100040（発行依頼書がありません。先に発行依頼書を登録してください。）で、BindingResult に積んで同じ画面に戻します。 | Junichi Noumi | 2026-10-08T10:58:25+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 3 | 2 | 修正 | 。ただし、ロックした TWTGM100 の ExclusiveFG も画面の隠し項目の値と照合し、違えば GEF-000027 にします。合計を入れ直した TWTGM100 の ExclusiveFG は新しい値にします。別々の契約局を同時に更新したときは後の人が排他エラーになりますが、それでよいです。 | Junichi Noumi | 2026-10-08T10:58:28+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 4 | 2026-10-08T11:04:22+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md":"2ab455e0ee5bd12555dcafe902df613bc1419c86ff176833ffddca100b7c9bb1"} | 2 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務の欠落・矛盾 | 重大 | 09ada52e20fba285 | d2fe22132fbae0a8 | specs/issue-request/design.md § サービスインターフェース（Service Interface） / 照合する行が無いときの扱い ほか 2 か所 | 発行依頼書が無い複数局の申請の登録 | 発行依頼書が無い複数局の申請は、契約局情報追加も発行依頼書編集も使えず画面から登録できない | 3 回目 #1 の判断（B）の反映で、§ サービスインターフェース の「照合する行が無いときの扱い」は「TWTGM100 が無い申請では、遷移元 3 の更新・一時保存を受け付けず、WTG-100040 を積んで同じ画面に戻す。先に発行依頼書編集から発行依頼書を登録させる」とし、§ 機能固有エラーコード の WTG-100040 の対応も「発行依頼書編集から先に発行依頼書を登録する」、更新の手順も「TWTGM100 が無い申請の 3 は WTG-100040」とする。一方、pbi design（approved）は「複数局の申請で契約局情報が 1 件も無いのに発行依頼書編集ボタンを押した」ときに WTG-100022（文言「複数局を取り扱う場合は、先に契約局情報を登録して下さい。(契約局取込または発行依頼書情報編集)」）で止め、発行依頼書登録変更画面へ遷移させない（pbi design の /wtg070/addKeyaku・/wtg070/henshu の行と § 機能固有エラーコード の WTG-100022。pbi requirements 14.11・14.12）。このため、複数局の申請で TWTGM100 も TWTGM140 も無いとき、発行依頼書編集（遷移元 2）は pbi が WTG-100022 で止め、契約局情報追加（遷移元 3）は本 design が WTG-100040 で止める。2 つのメッセージは互いに相手の操作を先に行うよう案内しており、画面からは発行依頼書も契約局も登録できない（残る道は契約局取込か、単独局で登録してから複数局へ切り替えることだが、design にその案内は無い）。また requirements 1.9「発行依頼書が登録されていない申請でこの画面へ遷移したとき、システムは新規の登録として画面を開き、更新で発行依頼書を新しく登録しなければならない」に対し、遷移元 3 では新規の登録を受け付けないが、design はほかの逸脱と違い 1.9 から意図して外れる旨（upstream-carryover）を書いていない。3 回目 #1 の指摘は 1.9 と B の案を示したが、pbi の WTG-100022 と合わせたときに複数局で登録の道が無くなることは示していなかった（意味判定：ID 対応あり・内容未充足。複数局の新規の申請で 1.9・5.8 の登録ができない） | 次のどれかを決める。A：複数局で TWTGM100 が無い申請の遷移元 3 の更新・一時保存では、TWTGM100 も新規の登録として作る（発行依頼書の新規登録と同じく、登録の直前に同じ申請No の行があれば GEF-000027、一意キー違反も GEF-000027）。B：WTG-100040 で止めるままとし、複数局の申請は契約局取込か、単独局で発行依頼書を登録してから複数局へ切り替える運用とする。WTG-100040 の対応の文と「照合する行が無いときの扱い」をその案内に直し、1.9 から意図して外れる旨と upstream-carryover を書く。C：pbi 側で、複数局で TWTGM100 が無い申請では発行依頼書編集を使わせる（pbi requirements 14.12・pbi design を Phase 5 の最後にまとめて直す一覧に入れる）。D：その他 | 質問：3 回目 #1 の判断（B）と pbi の WTG-100022 を合わせると複数局の申請の登録の道が無くなり、どの道を開けるかは人の判断が要るため | 確認済み |  |  |
| 2 | traceability | 文書間の参照 | 軽微 | 6e2a1a6e76b2800a | d2fe22132fbae0a8 | specs/issue-request/design.md § サービスインターフェース（Service Interface） / 更新（update）・一時保存（saveDraft） ほか 2 か所 | WTG-100040 | WTG-100040がServiceの更新・一時保存のエラー欄とAPI契約・分岐フローに載っていない | WTG-100040 は § 機能固有エラーコード に「発行依頼書（TWTGM100）が無い申請で、契約局情報追加（遷移元 3）から更新・一時保存した」として追加され、§ サービスインターフェース の表の後の「照合する行が無いときの扱い」と更新の手順にも書かれている。しかし次の 3 か所には載っていない。(1) § サービスインターフェース の表の 更新（update）・一時保存（saveDraft）の行のエラーの列（WTG-100030・GEF-000027・入力チェックだけ。また遷移元 1・3 で先に TWTGM100 の ExclusiveFG を照合して GEF-000027 にすることも、エラーの列には無い）。(2) § API 契約（API Contract） の POST /wtg080/update・/wtg080/tempSave の行の Errors（業務は WTG-100030 だけ）。(3) § エラー時の分岐フロー の図（§ 機能固有エラーコード で定めたコードをどの条件で返すかを示す節だが、WTG-100040 の分岐が無い） | (1) 更新・一時保存の行のエラーの列に「遷移元 3 で TWTGM100 が無い → WTG-100040。遷移元 1・3 で TWTGM100 の排他用の値の不一致 → GEF-000027」を足す。(2) API 契約の /wtg080/update・/wtg080/tempSave の Errors の業務に WTG-100040 を足す。(3) 分岐フローの「できる」の後に「遷移元 3 で TWTGM100 が無い → WTG-100040」の分岐を足す（指摘 1 の判断で扱いが変わるときは、その結果に合わせる） | 修正：3 回目 #1 の判断で決まったキーを、同じ文書のエラーの一覧に書き足すだけで足りるため | 確認済み |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 4 | 2 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-08T11:07:41+09:00 |  |  |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 3 | 1 | feature:issue-request | 4 | system（自動）：再検査で再検出なし | 2026-10-08T11:07:41+09:00 |
| feature:issue-request | 3 | 2 | feature:issue-request | 4 | system（自動）：再検査で再検出なし | 2026-10-08T11:07:41+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 4 | 1 | 修正 | 修正案の B を採ります。WTG-100040 で止めるままにします。複数局の申請は、契約局取込か、単独局のまま発行依頼書編集で発行依頼書を登録してから複数局へ切り替える運用です（物件基本情報の WTG-100022 の文言「(契約局取込または発行依頼書情報編集)」と同じ案内）。WTG-100040 の対応の文と「照合する行が無いときの扱い」をこの案内に直してください。requirements 1.9 から意図して外れること（契約局情報追加は発行依頼書が登録済みの申請だけ）を design に書き、upstream-carryover に「requirements（issue-request）1.9：契約局情報追加は発行依頼書が登録済みの申請だけ」を足してください。 | Junichi Noumi | 2026-10-08T11:12:04+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 5 | 2026-10-08T11:13:47+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md":"ed74523c78ab3b23a08ddc6b79449f15f1528985bfb8bd46d364c61cd75db7ac"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 文書間の参照 | 軽微 | 21fff20428e7a320 | 71fffc79200c4f55 | specs/issue-request/design.md § エラー時の分岐フロー / 発番 ほか 2 か所 | 発番のチェックの順 | 発番のWTG-000002とWTG-100030の判定順が、発番の手順と分岐フローで逆になっている | 今回変わった § エラー時の分岐フロー の図は、更新・一時保存・発番の要求をまず「取り直した申請が…その操作ができる」（できない → WTG-100030）で判定し、発番は「一致・発番」の枝から「区分1 の入力チェック 必須・桁・形式」（エラー → WTG-000002 ほか）へ進む。つまり発番では WTG-100030 の判定が先で、担当エリア・契約区分の必須（WTG-000002。§ バリデーション設計 の「発番」：担当エリアと契約区分の必須だけ）が後。一方、§ 発行依頼書登録変更 Service の「発番の手順」1. は「担当エリア・契約区分が空なら WTG-000002。getApplication で申請を取り直し、操作の可否の判定で発番できるかを確かめる（できなければ WTG-100030）」で、必須の検査が先。§ サービスインターフェース（Service Interface） の 発番（issueNumber）のエラーの列も WTG-000002 → WTG-100030 の順に書いている。更新・一時保存は図と「更新の手順」（操作の可否 → TWTGM100 の照合・WTG-100040 → 開いている行の照合 → 入力チェック）が一致しており、食い違うのは発番だけ。番でない人が担当エリアを空にして発番を送ったときに、どちらのキーが返るかが文書の中で 2 通りに読める（意味判定：要件 3.5・9.3 の実現の記述の対応が取れていない） | § エラー時の分岐フロー の図で、発番は最初に「担当エリア・契約区分が空」→ WTG-000002 の分岐を置いてから C（操作の可否）へ進むようにし、D の「一致・発番」の枝は更新・一時保存だけにする（発番の手順 1. とサービスインターフェースのエラーの列に合わせる）。あるいは発番の手順 1. を図に合わせて「getApplication で取り直して操作の可否を判定 → 担当エリア・契約区分の必須」の順に直し、エラーの列の順も入れ替える。どちらか一方にそろえる | 修正：同じ文書の中の記述の順をそろえるだけで、業務の新しい事実は要らないため | 確認済み |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 5 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-08T11:17:09+09:00 |  |  |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 4 | 1 | feature:issue-request | 5 | system（自動）：再検査で再検出なし | 2026-10-08T11:17:09+09:00 |
| feature:issue-request | 4 | 2 | feature:issue-request | 5 | system（自動）：再検査で再検出なし | 2026-10-08T11:17:09+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 6 | 2026-10-08T11:25:54+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md":"a543916db8517b94bdbefb90769055130c7b2e00eeb99f9027bf9f66402a5d63"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 5 | 1 | feature:issue-request | 6 | system（自動）：再検査で再検出なし | 2026-10-08T11:28:37+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:issue-request | 6 | specs/issue-request/design.md | Junichi Noumi | 2026-10-08T11:30:08+09:00 | a543916db8517b94bdbefb90769055130c7b2e00eeb99f9027bf9f66402a5d63 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 2 | 対応せず進める | AI 推奨を採用: 人の回答（Q-DS-IR-014）に従った読み方として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 6 |
| feature:issue-request | 1 | 4 | 対応せず進める | AI 推奨を採用: item-rules.md（回答者が渡した資料）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 6 |
| feature:issue-request | 1 | 7 | 対応せず進める | AI 推奨を採用: pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 6 |
| feature:issue-request | 1 | 8 | 対応せず進める | AI 推奨を採用: design に明記され、pbi design は Phase 5 の最後にまとめて直す方針とされているため。直すまでは pbi の実装がこの前提を満たさない | feature:issue-request | 6 |
| feature:issue-request | 2 | 1 | 対応せず進める | AI 推奨を採用: 人の回答（Q-DS-IR-001 の C）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため。ただし承認済み requirements と両立しない状態は残る | feature:issue-request | 6 |
| feature:issue-request | 2 | 2 | 対応せず進める | AI 推奨を採用: グループを権限区分と読むことは物件基本情報と 1 回目の判断で決まっており、上流の文言は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 6 |
| feature:issue-request | 2 | 3 | 対応せず進める | AI 推奨を採用: pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 6 |
| feature:issue-request | 2 | 4 | 対応せず進める | AI 推奨を採用: design に明記され、pbi design は Phase 5 の最後にまとめて直す方針とされているため。直すまでは pbi の実装がこの前提を満たさない | feature:issue-request | 6 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 1 | 2026-10-08T11:48:29+09:00 | ①② | ["specs/issue-request-tutorial/design.md"] | {"specs/issue-request-tutorial/design.md":"e60159c5ba0df1765e79d89beaf9cb5416f0640da5bf8e5455869481ea98639a"} | 3 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | steering-conformance | 業務の欠落・矛盾 | 重大 | 8495912cc088b0e0 | 8386e642b72fcab9 | specs/issue-request-tutorial/design.md § 技術スタック（Technology Stack） / Infrastructure / Runtime | 開発端末の JDK | 開発端末のJDK 1.8がtech.mdの必須ツールJDK 1.7と食い違う | 矛盾。steering/tech.md `### 必須ツール` は JDK を「1.7（1.7.0.55）／コンパイルと実行」と定めているが、design の技術スタックは「開発端末の JDK 1.8（-source/-target 1.7）」を開発端末でのコンパイルと自動テストの実行に使うとしている。design 自身が「steering/tech.md から意図して外れる」と書き、根拠を Q-DS-PBI-014（物件基本情報登録変更と同じ）としている。Q-DS-PBI-014 は今回の confirmed_answers に含まれない（pbi design の技術スタックに同じ行がある）。issue-request の設計検査 1 回目の指摘 7 と同じ事項 | steering/tech.md の `### 必須ツール` に「開発端末は JDK 1.8（-source/-target 1.7）でもよい」を足す（Phase 2 への差戻し、または upstream-carryover での一括修正） | 対応せず進める：pbi design・ir design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | 確認済み |  |  |
| 2 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | c5bdd8e143b40eb7 | 0198483d572d81b7 | specs/issue-request-tutorial/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 親画面がするとき ほか 1 か所 | ir design の受け渡しの公開契約に無い前提 | 親画面に求める入力不可の扱い・電気料等の入れ直し・整形がir designの公開契約に無い | 依存先 specs/issue-request/design.md（approved）の公開契約（§ データ契約と外部連携 の「チュートリアル（GWTG081）との受け渡し」、§ API 契約 と § サービスインターフェース の `/wtg080/changeKeiyakuSyubetsuTutorial`）に無い振る舞いを前提にしている。(1) 入れる先の項目が入力できない状態なら入れない（本書 § データ契約 の「親画面がするとき」、§ このスペックが持たない責務）。ir の受け渡しは「値が空のものは入れない」だけで、入力できない項目の扱いは書かれていない。(2) 契約種別を受け取ったときの処理を「`/wtg080/changeKeiyakuSyubetsuTutorial` による局種別・設置設備・電気料のリストの入れ直し、ラベルの変更、入力可否の切替」としているが、ir の `/wtg080/changeKeiyakuSyubetsuTutorial` は「局種別と設置設備のプルダウンの選択肢（2 つのリスト）を返す」だけで、電気料のリスト・ラベル・入力可否は返さない（本書 § 依存してよい対象 も「局種別・設置設備のリストを返す」と書いており、本書の中でも食い違う）。(3) 賃料のカンマと着工予定日の保存の形への変換を親画面に任せている（§ このスペックが持たない責務、§ ドメインモデル の入力値のまま入れる項目）が、ir の受け渡しに無い。本書が upstream-carryover として明記しているのは `json.clear` の印と入れる順の 2 点だけで、(1)〜(3) は書かれていない。振る舞いそのものは回答 Q-DS-TU-007 と対応表（mapping の 0・1）による | § データ契約と外部連携 の「親画面がするとき」の注記を「`json.clear` の印、入れる順、入力できない項目に入れないこと、契約種別の変更時の電気料のリスト・ラベル・入力可否の切替（`/wtg080/changeKeiyakuSyubetsuTutorial` の戻りにはまだ無い）、賃料・着工予定日の整形は、ir design の公開契約にまだ無い。ir design は Phase 5 の最後にまとめて直す（upstream-carryover）」に直す。あわせて「`/wtg080/changeKeiyakuSyubetsuTutorial` による局種別・設置設備・電気料のリストの入れ直し」を、ir の公開契約に合わせた書き方（戻りは局種別・設置設備の 2 つ。電気料・ラベル・入力可否は親画面の契約種別の変更時の処理）に直す | 修正：振る舞いは回答 Q-DS-TU-007 で決まっており、ir design へ足す事項を upstream-carryover の記述に加え、本書の中の食い違いを直せば足りるため | 確認済み |  |  |
| 3 | evidence-guard | 業務の欠落・矛盾 | 重大 | 053145c130f70f3b | 420e68a14e3e788d | specs/issue-request-tutorial/design.md § 変更する既存ファイル（Modified Files） / messages.properties ほか 1 か所 | WTX-100005 | WTX-100005を新規とするがpbi designは既存キーとして追加しておらず食い違う | 上流と食い違う。本書は `WTX-100005`（数字で入力してください）を「新規」とし、「物件基本情報登録変更の電話番号のチェックでも使うので、messages.properties には 1 回だけ足す」として本 feature の変更する既存ファイルに追加を書いている（§ 機能固有エラーコード の表の前の注記と表、§ 変更する既存ファイル）。これは回答 Q-DS-TU-008 の 2 のとおりで、実際に wing/src/main/resources/messages.properties には `WTX-100005` が無い（`WTX-100013` は 401 行にある）。一方、依存先の specs/property-basic-info/design.md（approved）は § 設計判断 で「既存のキー（`WTG-000002`・`GEF-000003`・`WTG-000003`・`WTX-100012`・`WTX-100011`・`WTX-100005`・`WTG-000029`）を使い」と既存のキーとして扱い、§ 変更する既存ファイル の messages.properties の追加に `WTX-100005` を含めていない。本書は pbi design を直すことを upstream-carryover に書いていない。pbi と本 feature のどちらの実装で足すかが決まっていないため、本 feature より先に pbi を実装するとキーが無いまま使われる | 次のどちらかを決める。A：pbi design の `WTX-100005` を「新規（Warning。チュートリアルと共通で 1 回だけ足す）」に直し、pbi の変更する既存ファイルで追加する。本書は「物件基本情報登録変更が追加する（無ければ本 feature が足す）」に直す。B：本書のまま本 feature が追加し、pbi design には「既存」を「issue-request-tutorial が追加する新規のキー」に直す注記だけを足す。どちらの場合も pbi design の修正を upstream-carryover に記録する | 質問：どの feature の実装で追加するかは実装の順番に関わる人の判断が要り、承認済みの pbi design の記述も直す必要があるため | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | 人間による確認（steering/tech.md の修正、または本 design の修正） | 開発端末の JDK（Q-DS-PBI-014 の回答）が steering の必須ツールと食い違っている。steering 側を直す場合は Phase 2 が宛先になる |
| 2 | 人間による確認（specs/issue-request/design.md の修正） | 依存先 ir design の受け渡しの公開契約に、本 design が前提にする入力できない項目の扱い・契約種別の変更時の電気料等の切替・整形が無い。ir design を開き直す場合は Phase 5（issue-request）が宛先になる |
| 3 | 人間による確認（specs/property-basic-info/design.md の修正） | pbi design が WTX-100005 を既存のキーとして扱い、追加していない。pbi design を開き直す場合は Phase 5（property-basic-info）が宛先になる |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/issue-request-tutorial/design.md § ドメインモデル（Domain Model） / 画面と進む先 | 画面を 11 にし、RRH数・System構成・UPS工事の 3 画面を使わない（requirements 1.3・1.9 から外れる） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § ドメインモデル（Domain Model） / 局種別の出し分け | 鋼管柱を KDDI⇒UQ だけに出す（requirements 1.8 から外れる） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § 設計判断（Design Decisions） / 判断 1 | ブラウザーの × で閉じることを防がない（requirements 1.10 から外れる） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § ドメインモデル（Domain Model） / 入れる値 | 入れる先に転貸情報の有無を足して 8 項目にする（requirements 2.1 から外れる） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § 設計判断（Design Decisions） / 判断 3 | 「空にする」操作で値を消す（requirements 2.2 の例外） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § このスペックが持たない責務（Out of Boundary） / 1.2 | 開ける人と状態はチュートリアル設定ボタンの表示だけで決め、/wtg081 では確かめない（1.2） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § 補足資料（Supporting References） / 画面の表示文言 | 1.12 の「例」の文言を持つ画面が一部だけ（flow の 4 を正とする） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § バリデーション設計 / 桁 | 桁（12・10）を入力欄の最大桁で止め、検査とメッセージを持たない（3.2・3.3） | answer:design-authoring-generate[issue-request-tutorial] |
| steering-conformance | specs/issue-request-tutorial/design.md § 機能固有のエラー処理（Error Handling） / 返し方 | 入力チェックの結果を BindingResult でなく JSON の result・messages で返す（tech.md の例外処理フロー） | answer:design-authoring-generate[issue-request-tutorial] |
| steering-conformance | specs/issue-request-tutorial/design.md § API 契約（API Contract） / /wtg081/next | 画面内で JSON を返す口が 1 つ増える（api-standards.md の「JSON を返すのは既存の 2 か所だけ」） | answer:design-authoring-generate[issue-request-tutorial] |
| steering-conformance | specs/issue-request-tutorial/design.md § セキュリティ上の考慮（Security Considerations） / 脅威と対策 | 開ける人と状態をサーバー側で判定しない（security.md の禁止「画面の表示だけで制御しない」） | answer:design-authoring-generate[issue-request-tutorial] |
| dependency-boundary-conformance | specs/issue-request-tutorial/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 「空にする」の印・入れる順 | json.clear の印と、契約種別を先に処理する順が ir design の公開契約にまだ無い（本書に upstream-carryover と明記） | answer:design-authoring-generate[issue-request-tutorial] |
| evidence-guard | specs/issue-request-tutorial/design.md § ファイル配置計画（File Structure Plan） / function/wtg/wtg081 | 機能ID WTG081 の自分のパッケージ・pwtgo081ZoomForm.html・ZOOM_DEFINE.pwtgo081=1000px,600px | answer:design-authoring-generate[issue-request-tutorial] |
| evidence-guard | specs/issue-request-tutorial/design.md § API 契約（API Contract） / 画面のスクリプトの動き | 着工予定日の初期値を利用者の PC の今日の日付にする | answer:design-authoring-generate[issue-request-tutorial] |
| evidence-guard | specs/issue-request-tutorial/design.md § 移行方針（Migration Strategy） / ZMENUAUTH | PWTGO081 の行を PWTGO080 を登録するメニューと同じものすべてに発注者が投入する | answer:design-authoring-generate[issue-request-tutorial] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 1 | 1 | 対応せず進める | AI 推奨を採用: pbi design・ir design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | Junichi Noumi | 2026-10-08T11:59:48+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 1 | 2 | 修正 | AI 推奨を採用: 振る舞いは回答 Q-DS-TU-007 で決まっており、ir design へ足す事項を upstream-carryover の記述に加え、本書の中の食い違いを直せば足りるため | Junichi Noumi | 2026-10-08T11:59:52+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 1 | 3 | 修正 | 案A。WTX-100005 は物件基本情報登録変更の電話番号のチェックで使い、Phase 8 で先に実装されるので、pbi の変更する既存ファイルで追加します。（pbi design の「既存」を「新規（Warning。チュートリアルと共通で1回だけ足す）」に直す。carryover に記録済みの「WTX-100011・WTX-100012・WTX-100005・WTG-100018 は wing に無い」と同じ件）本書は「物件基本情報登録変更が追加する」に直してください。 | Junichi Noumi | 2026-10-08T11:59:55+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 2 | 2026-10-08T12:02:27+09:00 | ①② | ["specs/issue-request-tutorial/design.md"] | {"specs/issue-request-tutorial/design.md":"c7f8713531fc963780c2491a50671b52e4cf15f36cb990cd416b9352b2d8c831"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/issue-request-tutorial/design.md § バリデーション設計 / 桁 | 桁（12・10）を入力欄の最大桁で止め、検査とメッセージを持たない（3.2・3.3） | answer:design-authoring-generate[issue-request-tutorial] |
| steering-conformance | specs/issue-request-tutorial/design.md § 機能固有のエラー処理（Error Handling） / 返し方 | 入力チェックの結果を BindingResult でなく JSON の result・messages で返す（tech.md の例外処理フロー・security.md の入力検証） | answer:design-authoring-generate[issue-request-tutorial] |
| dependency-boundary-conformance | specs/issue-request-tutorial/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 親画面がするとき | json.clear の印・入れる順・入力できない項目に入れないこと・電気料等の切替・整形が ir design の公開契約にまだ無い（本書に upstream-carryover と明記） | answer:design-authoring-generate[issue-request-tutorial] |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 1 | 2 | feature:issue-request-tutorial | 2 | system（自動）：再検査で再検出なし | 2026-10-08T12:05:02+09:00 |
| feature:issue-request-tutorial | 1 | 3 | feature:issue-request-tutorial | 2 | system（自動）：再検査で再検出なし | 2026-10-08T12:05:02+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:issue-request-tutorial | 2 | specs/issue-request-tutorial/design.md | Junichi Noumi | 2026-10-08T12:08:27+09:00 | c7f8713531fc963780c2491a50671b52e4cf15f36cb990cd416b9352b2d8c831 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 1 | 1 | 対応せず進める | AI 推奨を採用: pbi design・ir design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request-tutorial | 2 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:print-report | 1 | 2026-10-08T12:42:12+09:00 | ①② | ["specs/print-report/design.md"] | {"specs/print-report/design.md":"f01227da7fec7ce6647d3c4897813b3804ee48da42af3fc3049743229219ddc3"} | 6 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務のあいまい・不足 | 要判断 | 61ba48f73810fea2 | 859d831ba33d9ab1 | specs/print-report/design.md § サービスインターフェース（Service Interface） / deleteTempFiles ほか 1 か所 | PDF の一時ファイルの削除 | PDF の一時ファイルを誰がいつ消すかが、Service と Controller の記述で食い違う | 意味判定（3.6・3.1・3.2。ID 対応あり・記述が両立しない）。Service の帳票の作成の手順 9 は「成功でも失敗でも、作った編集用 Excel・PDF・QR の画像を finally の Files.deleteIfExists で消す。PDF は Controller が応答に書き出したあとで消す」、createReport の出力は「PDF の一時ファイルと、利用者に見せるファイル名」、deleteTempFiles は別のメソッド。一方 § 印刷・閲覧用帳票 Controller の データ所有権 / 不変条件 は「PDF を書き出したあとの一時ファイルの削除は Service の finally に任せる」。deleteTempFiles を誰がいつ呼ぶかが書かれておらず、createReport の finally で PDF を消すと Controller が書き出せない。全箇所：§ サービスインターフェース（Service Interface）の手順 9 と deleteTempFiles の行、§ 印刷・閲覧用帳票 Controller の データ所有権 / 不変条件 | 「createReport は途中で失敗したら作ったファイルをすべて消して例外を投げ、成功したら PDF・編集用 Excel・QR の画像のパスを返す。Controller は PDF を応答に書き出す処理を try で囲み、finally で Service の deleteTempFiles を呼ぶ」と、Service の手順 9 と Controller の データ所有権 / 不変条件 を同じ書き方に揃える | 修正：回答（Q-DS-PR-012 の 4）の範囲で、呼ぶ側と時期を書き分ければ揃うため | 確認済み |  |  |
| 2 | traceability | 業務のあいまい・不足 | 要判断 | 47ef94c4b21fa26e | b93b2b4ec03350af | specs/print-report/design.md § 機能固有エラーコード / WTG-100030 ほか 1 か所 | WTG-100030 の差し込み値 | WTG-100030 の {0}〜{2} に入れる値が無く、申請が無いときなどの表示が定まらない | 意味判定（3.4・3.5 の拒否の表示）。pbi design § 機能固有エラーコード の WTG-100030 の文言は「ステータス、状態区分、操作の組み合わせが不正です。ステータス：{0}、状態区分：{1}、操作：{2}」。本書の § バリデーション設計 のメッセージ例は「（物件基本情報登録変更で決めた文言）」、§ サービスインターフェース（Service Interface） は「ApplicationException を投げる：WTG-100030」だけで、{0}〜{2} に入れる値（申請が無い・社外ユーザーの範囲外・発行依頼書か代表局が無いときを含む）が書かれていない。回答 Q-DS-PR-011 の 2・3 と Q-DS-PR-014 は「WTG-100030 で止める」「既存の文言」までで、差し込む値は決めていない。全箇所：§ 機能固有エラーコード の WTG-100030 の行、§ バリデーション設計 の出力の条件の行 | 次のどれにするか決める。A：{0}・{1} に申請の審査フェーズ・状態の名称（申請が無ければ空）、{2} に「閲覧」または「印刷」を入れる。B：{0}〜{2} をすべて空にする。C：その他 | 質問：エラー画面に出る文言は利用者に見える値で、回答に無いため | 確認済み |  |  |
| 3 | traceability | 業務のあいまい・不足 | 要判断 | 3362d24f09544b85 | d3fae9fe30928f88 | specs/print-report/design.md § 機能固有のエラー処理（Error Handling） / ログ | 一時ファイルの削除失敗のログ | 一時ファイルの削除に失敗したときのログのレベルとメッセージID が決まっていない | 非機能方針の反映を突合（上流→下流）。steering/non-functional.md の ### ログ方針 / #### ログレベル は ERROR（処理を続けられない例外）・INFO（処理の開始・終了と件数）・DEBUG の 3 つで、#### ログフィールド標準 の禁止事項 1 は「文言を直接書かず、メッセージID から文言を取得してログに出す」。本書は「一時ファイルを消すのに失敗したときはログに出すだけ」（§ 機能固有のエラー処理（Error Handling）のログ、§ サービスインターフェース（Service Interface）の deleteTempFiles）で、レベルとメッセージID が無い。変換・接続の失敗の「ログに ERROR とスタックトレース」も、どのメッセージID の文言を出すか（DS-100015 か）が書かれていない | 次を決めて § 機能固有のエラー処理（Error Handling）のログに足す。削除の失敗：A：INFO で既存のキーの文言とファイルのパスを出す。B：ERROR で出す（処理は止めない）。C：その他。あわせて、変換・接続の失敗の ERROR ログは DS-100015 の文言とスタックトレースを出す、でよいか | 質問：削除の失敗は処理を止めない事象で、steering のレベルの用途にそのまま当てはまるものが無いため | 確認済み |  |  |
| 4 | traceability | 業務のあいまい・不足 | 要判断 | 7197d19d1fbb262f | 0c7e61b124a43333 | specs/print-report/design.md § エラー時の分岐フロー ほか 1 か所 | 原本の写し・POI の失敗 | 原本の写し・POI での読込みと保存・QR 生成に失敗したときのキーとログが決まっていない | 意味判定（要件 4 の異常系）。§ サービスインターフェース（Service Interface）の帳票の作成の手順 4〜7（原本を一時ファイルの置き場へ写す、POI で開いて値を入れる、数式を計算して写す、QR の画像を貼る、保存）に失敗したときの扱いが無く、§ エラー時の分岐フロー の F（原本を写して値を入れ…保存）にも失敗の分岐が無い。§ 機能固有エラーコード は WTG-100030・DS-000084・GEF-000058・DS-100015 の 4 つで、DS-100015 は「PDF への変換、または OpenOffice への接続に失敗した（4.1）」に限っている。写しの失敗（書込みの権限・容量）、POI での原本の読込みの失敗、POI が計算できない関数（判断 2 の採用による影響）での失敗が、どのキー・ログで止まるかが読めない。全箇所：§ エラー時の分岐フロー、§ サービスインターフェース（Service Interface）の手順 4〜8 | 次のどれにするか決める。A：変換の失敗と同じく ERROR とスタックトレースを出し DS-100015 で止める（一時ファイルは finally で消す）。B：原本の読込みの失敗は GEF-000058（{0}＝「原本エクセルファイル」）、それ以外は DS-100015。C：その他 | 質問：利用者に見せるメッセージの選択で、回答（Q-DS-PR-013・Q-DS-PR-014）は変換・接続の失敗までしか決めていないため | 確認済み |  |  |
| 5 | evidence-guard | 業務のあいまい・不足 | 要判断 | 1c7c3de48098e208 | a941944ce223685d | specs/print-report/design.md § このスペックが持たない責務（Out of Boundary） / ZMENUAUTH ほか 2 か所 | ZMENUAUTH の行の投入 | ZMENUAUTH の行の投入を発注者に任せているが、回答は tasks に INSERT 文を入れるとしている | 根拠の飛躍。本書 § このスペックが持たない責務（Out of Boundary）は「コードマスタ P89 の行と、ZMENUAUTH の PWTGO072 の行の投入、原本の配備 → 発注者」。回答 Q-DS-PR-011 の 4 は「足す行はリリースのデータ投入（INSERT 文）として tasks に入れます。PWTGO073 も同じ扱いです」で、§ 移行方針（Migration Strategy）も「リリースのデータ投入（INSERT 文）として投入する」と書く。INSERT 文を本 feature の成果物として作るのかが § このスペックが持つ責務（This Spec Owns）に無く、委譲の記述と読み分けられない。P89 の行の投入と原本の配備を発注者が行う根拠も requirements・回答に無い（回答 Q-DS-PR-012 の 1 は「この行は新しく追加します」、Q-DS-PR-001 の 3 は「配備のときに 2. のフォルダへ写します」まで）。探した根拠：specs/print-report/requirements.md、steering/*.md、confirmed_answers。全箇所：§ このスペックが持たない責務（Out of Boundary）、§ このスペックが持つ責務（This Spec Owns）、§ 移行方針（Migration Strategy）の段階分け | § このスペックが持つ責務（This Spec Owns）に「ZMENUAUTH の PWTGO072・PWTGO073 の行を足す INSERT 文（リリースのデータ投入。tasks で作る）」を足し、§ このスペックが持たない責務（Out of Boundary）は投入の実施だけを発注者に任せる形に直す。P89 の行の投入と原本の配備を誰が行うかは、回答者に確かめる（A：発注者が導入手順書に沿って行う。B：本 feature のリリース作業に含める。C：その他） | 修正：ZMENUAUTH は回答どおりに書き分けられる。P89 と原本の配備の担い手は回答者への確認が要る | 確認済み |  |  |
| 6 | evidence-guard | 出典・根拠 | 軽微 | 248476f525f4a1b1 | b73ecf080b587c1e | specs/print-report/design.md § ドメインモデル（Domain Model） / 発行依頼書のページ（RWTG071） | 発行依頼書のページの隠す行 | 隠す行の番号が項目一覧 3 章の行番号と違い、原本から読み直した旨が書かれていない | 出典不明。本書は「次の行は隠す：タイトルの行 2、UQ担当者入力欄から案件G までの行 4〜13、その他事項…の行 86〜102、添付資料の行 107〜112。原本で隠してある行（1・27・32・40・48・56・64・68）は隠したまま。契約者区分が空の関係者の欄（行 r〜r＋7）も隠す」。本書が正とする項目一覧（_handoff/phase5-print-report-items.md）3 章「印刷・閲覧用帳票(入力フォーム (契約情報))」の特記事項は「4行目～12行目」「85行目～101行目」「106行目～111行目」「27行目～66行目（関係者①〜⑤）」「26・67・31・39・55・63 行目を非表示」。本書の入力フォームのセル（D86・D108・関係者の先頭行 28 など）とは合っているが、項目一覧と行番号が違う理由（原本から読み直したこと）が書かれていない。原本（.xlsm）の中身は今回の検査では開いて確かめていない | 発行依頼書のページの項目に「行番号は原本から読み取った。項目一覧 3 章の特記事項の行番号（4〜12・85〜101・106〜111・27〜66・26/31/39/55/63/67）は帳票設計の資料の行で、原本の行とは違う」と出典を足す | 修正：出典の追記で直せるため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| steering-conformance | specs/print-report/design.md § 技術スタック（Technology Stack） / Backend / Service | 原本を .xlsm のまま POI で使い、tech.md の「テンプレートは .xlsx」から外れる（本書に upstream-carryover と明記） | answer:design-authoring-generate[print-report] |
| steering-conformance | specs/print-report/design.md § 技術スタック（Technology Stack） / Infrastructure / Runtime | zxing 3.4.1 が本番の JDK 1.7 で動くかを導入時の確認に回し、steering の版を変えない | answer:design-authoring-generate[print-report] |
| steering-conformance | specs/print-report/design.md § 技術スタック（Technology Stack） / Infrastructure / Runtime | 開発端末の JDK 1.8 が tech.md の必須ツール JDK 1.7 から外れる | verify:重複（property-basic-info の design で判断済みの同じ食い違い。pbi design 技術スタック Q-DS-PBI-014、upstream-carryover 記載済み） |
| steering-conformance | specs/print-report/design.md § 印刷・閲覧用帳票 Controller / Cache-Control | PDF の応答に no-cache を付けず、security.md のキャッシュ no-cache と食い違う | answer:design-authoring-generate[print-report] |
| dependency-boundary-conformance | specs/print-report/design.md § 依存してよい対象（Allowed Dependencies） / 6.9 の判定 | 物件基本情報登録変更 Service の 6.9 の判定は pbi design の公開のサービスインターフェースに口が無い（pbi design は変えないと回答） | answer:design-authoring-generate[print-report] |
| dependency-boundary-conformance | specs/print-report/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 物件基本情報登録変更との口 | /wtg072/search の入力 3 つと GET が pbi design の API 契約（入力は申請No だけ・POST）と食い違う（本書に upstream-carryover と明記） | answer:design-authoring-generate[print-report] |
| traceability | specs/print-report/design.md § ドメインモデル（Domain Model） / 発行依頼書のページ（RWTG071） | 1.10 の製本の情報と添付資料を発行依頼書のページに出さない（表紙に出す） | answer:design-authoring-generate[print-report] |
| traceability | specs/print-report/design.md § ドメインモデル（Domain Model） / ファイル名 | 3.3 と違い、代表局の稟議バーコードNo が空なら申請No.pdf にする | answer:design-authoring-generate[print-report] |
| external-integration-contract-explicitness | specs/print-report/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / サービス間 | OpenOffice への接続に待ち時間の上限・再試行・順番待ちを持たない | answer:design-authoring-generate[print-report] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:print-report | 1 | 6 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-08T12:51:47+09:00 |  |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:print-report | 1 | 1 | 修正 | AI 推奨を採用: 回答（Q-DS-PR-012 の 4）の範囲で、呼ぶ側と時期を書き分ければ揃うため | Junichi Noumi | 2026-10-08T13:40:49+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:print-report | 1 | 2 | 修正 | 。{0} は審査フェーズの名称、{1} は状態の名称（申請が無ければどちらも空）、{2} は「閲覧」か「印刷」。物件基本情報登録変更の WTG-100030 と同じ並び | Junichi Noumi | 2026-10-08T13:40:52+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:print-report | 1 | 3 | 修正 | 修正案の B。削除の失敗は ERROR でファイルのパスを出し、処理は止めない（個人情報を含むファイルが残るので運用で気づけるようにする）。変換・接続の失敗は DS-100015 の文言とスタックトレースを ERROR で出す、でよい | Junichi Noumi | 2026-10-08T13:40:56+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:print-report | 1 | 4 | 修正 | 修正案の B。原本の読込みの失敗は GEF-000058（{0}＝「原本エクセルファイル」。requirements 1.2 と同じ扱い）、原本の写し・保存・QR の生成の失敗は DS-100015。どちらも ERROR とスタックトレースを出し、一時ファイルは finally で消す | Junichi Noumi | 2026-10-08T13:40:59+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:print-report | 1 | 5 | 修正 | 。ZMENUAUTH は修正案のとおり。P89 の行と原本の配備は、INSERT 文と配備の手順を本 feature の tasks で作り、投入と配備の実施は発注者が導入手順書に沿って行う（ZMENUAUTH と同じ分担） | Junichi Noumi | 2026-10-08T13:41:02+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:print-report | 2 | 2026-10-08T13:46:36+09:00 | ①② | ["specs/print-report/design.md"] | {"specs/print-report/design.md":"fe46c6c62298ab15dfad252f528e51e2c9724f9505c168d8fd9a9445cc0af11e"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | evidence-guard | 出典・根拠 | 軽微 | 248476f525f4a1b1 | d716544dc7ea9a9a | specs/print-report/design.md § ドメインモデル（Domain Model） / 発行依頼書のページ（RWTG071） | 発行依頼書のページの隠す行 | 隠す行の出典の注記が項目一覧の行番号をすべて1ずれとするが、4〜12行目などは合わない | 区分：出典不明（出典の書き方の誤り）。前回 #6 の修正で足した注記は「項目一覧 3 章の特記事項の行番号（4〜12・85〜101・106〜111・27〜66・26／31／39／55／63／67）は帳票設計の資料の行の数え方（0 始まり）で、原本の行とは 1 ずれる」と書く。原本（入力フォーム）と照らすと、85〜101→86〜102（その他事項 B86〜）、106〜111→107〜112（添付資料 B107〜X112）、27〜66→28〜67（関係者① B28〜関係者⑤ AC67）、26／31／39／55／63／67→27／32／40／56／64／68（原本の隠し行）は 1 ずれで合う。一方、4〜12 は 1 ずらすと 5〜13 になるが、design が隠すのは 4〜13（UQ担当者入力欄 B4・申請日 AL4 は行 4、案件小グループ名 J13 は行 13。Q-DS-PR-002 の 2「UQ担当者入力欄から案件Gまでの行」）。また項目一覧の「1行目：隠しタイトル」「2行目：契約情報入力フォームの文言」は原本の行 1（B1「契約情報」）・行 2（B2「契約情報入力フォーム」）とずれずに合い、design も行 2 をそのまま隠している。注記のとおりに読むと 4〜12 は 5〜13 となり、design の 4〜13 と食い違って見える（隠す行そのものは原本と回答に合っている）。なお原本の隠し行 48 は項目一覧に無い（design は原本のとおり隠したままにしている）。 | 注記を「項目一覧 3 章の特記事項の行番号のうち、85〜101・106〜111・27〜66・26／31／39／55／63／67 は原本の行より 1 小さい（帳票設計の資料の数え方）。1・2 行目は原本と同じ。4〜12 行目は、Q-DS-PR-002 の 2（UQ担当者入力欄から案件G まで）に従い原本の 4〜13 行とした。原本の隠し行 48 は項目一覧に無いが、原本のとおり隠したままにする」に書き換える | 修正：隠す行の番号は原本と回答に合っており、出典の注記だけを直せば足りるため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| evidence-guard | specs/print-report/design.md § ドメインモデル（Domain Model） / 発行依頼書のページ（RWTG071） | 製本の情報と添付資料を発行依頼書のページに出さない（requirements 1.10 と異なる） | answer:design-authoring-generate[print-report] |
| evidence-guard | specs/print-report/design.md § ドメインモデル（Domain Model） / ファイル名 | 稟議バーコードNo が空なら申請No.pdf にする（requirements 3.3 と異なる） | answer:design-authoring-generate[print-report] |
| traceability | specs/print-report/design.md § ドメインモデル（Domain Model） / 契約局情報のページ（RWTG072） | 光インフラのとき物件名の列を出す（1.8 は No・基地局番号・基地局名）、40 局ごとにページを分ける（1.5・1.7 のページ数） | answer:design-authoring-generate[print-report] |
| dependency-boundary-conformance | specs/print-report/design.md § サービスインターフェース（Service Interface） / 帳票の作成の手順 1 | 物件基本情報登録変更 Service の 6.9 の判定を同じパッケージの部品として直接呼ぶ | answer:design-authoring-generate[print-report] |
| steering-conformance | specs/print-report/design.md § 機能固有のエラー処理（Error Handling） / ログ | 一時ファイルの削除の失敗を処理を止めずに ERROR で出す（non-functional の ERROR は処理を続けられない例外） | verify:1 回目 #3 で人が決めた扱い（ERROR でパスを出し処理は止めない）を書いたもので、指摘の根拠にならない |
| external-integration-contract-explicitness | specs/print-report/design.md § サービスインターフェース（Service Interface） / 帳票の作成の手順 8 | OpenOffice への接続に待ち時間の上限・再試行・順に並べる仕組みを持たない | answer:design-authoring-generate[print-report] |
| evidence-guard | specs/print-report/design.md § 移行方針（Migration Strategy） / P89・原本の配備 | P89 の INSERT 文と原本の配備の手順は本 feature の tasks で作り、実施は発注者が行う | verify:1 回目 #5 で人が決めた分担（判断の理由）を書いたもので、根拠のない追記ではない |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:print-report | 2 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-08T13:50:38+09:00 |  |  |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:print-report | 1 | 1 | feature:print-report | 2 | system（自動）：再検査で再検出なし | 2026-10-08T13:50:38+09:00 |
| feature:print-report | 1 | 2 | feature:print-report | 2 | system（自動）：再検査で再検出なし | 2026-10-08T13:50:38+09:00 |
| feature:print-report | 1 | 3 | feature:print-report | 2 | system（自動）：再検査で再検出なし | 2026-10-08T13:50:38+09:00 |
| feature:print-report | 1 | 4 | feature:print-report | 2 | system（自動）：再検査で再検出なし | 2026-10-08T13:50:38+09:00 |
| feature:print-report | 1 | 5 | feature:print-report | 2 | system（自動）：再検査で再検出なし | 2026-10-08T13:50:38+09:00 |
| feature:print-report | 1 | 6 | feature:print-report | 2 | system（自動）：同じ指摘を 2 回目 #1 へ引き継ぎ | 2026-10-08T13:50:38+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:print-report | 3 | 2026-10-08T14:18:42+09:00 | ①② | ["specs/print-report/design.md"] | {"specs/print-report/design.md":"8fe912a89899ff69c775554dbe57be4851ca76517f63aef7563ed447cdcb4250"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | evidence-guard | 業務の欠落・矛盾 | 重大 | 80769fff7538b57d | 5560f2b674d5eead | specs/print-report/design.md § ドメインモデル（Domain Model） / 発行依頼書のページ（RWTG071） | 発行依頼書のページの行 1（隠しタイトル） | 発行依頼書のページで行 1 の隠しタイトルを隠したままにしており、項目一覧の「表示」と食い違う | 区分：根拠の飛躍（正とされた資料と食い違う）。design は「原本で隠してある行（1・27・32・40・48・56・64・68）は隠したまま」とし、タイトルの行 2 も隠すので、発行依頼書のページにタイトルが出ない。項目一覧（回答 Q-DS-PR-002 の 2 が「一覧の 3 章『入力フォーム (契約情報)』の特記事項」として参照し、回答者の指示で design の正とされた資料）の 3 章「(2) 入力フォームシートから帳票イメージ(入力フォーム (契約情報))になるまでの流れ」は、「① 印刷前（印刷準備）の表示／非表示項目」に「1行目：隠しタイトル表示」「2行目：契約情報入力フォームの文言を非表示」とし、「② 印刷後の表示／非表示項目」で「1行目：隠しタイトル非表示」に戻す（`_handoff/phase5-print-report-items.md` の 827〜842 行）。つまり出力の間は行 1 を表示して行 2 の代わりのタイトルにする。原本（入力フォーム）の行 1 は B1「契約情報」で、原本では隠し行（HIDDENROWS に 1）、行 2 は B2「契約情報入力フォーム」。注記の「1・2 行目は原本と同じ」は行番号の対応としては合っている（今回の修正の注記そのものは原本と項目一覧に合う。2 回目 #1 の修正指示どおり）。行 1 を隠したままにする根拠は requirements・回答・項目一覧のどこにも無い。2 回目の指摘内容も行 1 の表示の扱いには触れていない。 | 発行依頼書のページの隠す行の文を「次の行は隠す：タイトルの行 2、UQ担当者入力欄から案件G までの行 4〜13、その他事項（契約に関する特記事項と製本の情報）の行 86〜102、添付資料の行 107〜112。原本で隠してある行 1（B1「契約情報」。隠しタイトル）は表示にする（項目一覧 3 章の特記事項「1行目：隠しタイトル表示」）。ほかの原本で隠してある行（27・32・40・48・56・64・68）は隠したまま」に書き換える | 修正：正とされた項目一覧が出力の間は行 1 を表示すると明記しており、業務の新しい事実は要らないため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| evidence-guard | specs/print-report/design.md § ドメインモデル（Domain Model） / 発行依頼書のページ（RWTG071） | 製本の情報と添付資料を発行依頼書のページに出さない（requirements 1.10 と異なる） | answer:design-authoring-generate[print-report] |
| evidence-guard | specs/print-report/design.md § ドメインモデル（Domain Model） / ファイル名 | 稟議バーコードNo が空なら申請No.pdf にする（requirements 3.3 と異なる） | answer:design-authoring-generate[print-report] |
| traceability | specs/print-report/design.md § ドメインモデル（Domain Model） / 契約局情報のページ（RWTG072） | 光インフラのとき物件名の列を出す（1.8 は No・基地局番号・基地局名）、40 局ごとにページを分ける（1.5・1.7 のページ数） | answer:design-authoring-generate[print-report] |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:print-report | 2 | 1 | feature:print-report | 3 | system（自動）：再検査で再検出なし | 2026-10-08T14:21:56+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:print-report | 3 | 1 | 修正 | AI 推奨を採用: 正とされた項目一覧が出力の間は行 1 を表示すると明記しており、業務の新しい事実は要らないため | Junichi Noumi | 2026-10-08T14:27:16+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:print-report | 4 | 2026-10-08T14:29:40+09:00 | ①② | ["specs/print-report/design.md"] | {"specs/print-report/design.md":"0290e7db58d30e25be4cb376978f5783a22fdb69718de5ba0c38ad157aad2f80"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| evidence-guard | specs/print-report/design.md § ドメインモデル（Domain Model） / 発行依頼書のページ（RWTG071） | 製本の情報と添付資料を発行依頼書のページに出さない（requirements 1.10 と異なる） | answer:design-authoring-generate[print-report] |
| evidence-guard | specs/print-report/design.md § ドメインモデル（Domain Model） / ファイル名 | 稟議バーコードNo が空なら申請No.pdf にする（requirements 3.3 と異なる） | answer:design-authoring-generate[print-report] |
| traceability | specs/print-report/design.md § ドメインモデル（Domain Model） / 契約局情報のページ（RWTG072） | 光インフラのとき物件名の列を出す（1.8 は No・基地局番号・基地局名）、40 局ごとにページを分ける（1.5・1.7 のページ数） | answer:design-authoring-generate[print-report] |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:print-report | 3 | 1 | feature:print-report | 4 | system（自動）：再検査で再検出なし | 2026-10-08T14:32:56+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:print-report | 4 | specs/print-report/design.md | Junichi Noumi | 2026-10-08T14:39:02+09:00 | 0290e7db58d30e25be4cb376978f5783a22fdb69718de5ba0c38ad157aad2f80 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 2026-10-08T15:11:22+09:00 | ①② | ["specs/application-status-search/design.md"] | {"specs/application-status-search/design.md":"dbc3ae3dd9fd0b13694789254f887e2f759a143053b1c2e2c48f5eb6883c6f17"} | 4 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | c999756d5b30879f | ee51cc3b4b154c55 | specs/application-status-search/design.md § データ契約と外部連携（Data Contracts &amp; Integration） ほか 2 か所 | `/wtg070/returnList` の戻り先 | returnList の戻り先が pbi design（/wtg060）と本書（/wtg060/return）で食い違う | 本書は、物件基本情報登録変更画面の戻るが `/wtg070/returnList` から `/wtg060/return` に戻り、セッションの条件で再検索すると書く（§ データ契約と外部連携、§ このスペックが持たない責務（Out of Boundary）の「`/wtg070/returnList` で `/wtg060/return` へ戻す → `specs/property-basic-info/design.md`」、§ アーキテクチャ方式と境界図の図）。また § API 契約では `/wtg060` を「初期値。検索条件のセッションを消す。一覧は出さない」としている。&#10;依存先の pbi design（approved）の API 契約は、`/wtg070/returnList` の Response を「申請状況一覧（GWTG060、`/wtg060`）へ戻り、セッションに置いた一覧の検索条件で再検索する」と定めている。pbi design の公開契約どおり `/wtg060` に戻ると、本書の `/wtg060` がセッションを消して初期表示になるため、2.10（前の検索条件を残して、もう一度検索する）を満たさない。&#10;回答 Q-DS-AS-001 は `/wtg060/return` を戻りの口に決めたが、pbi design を直すことには触れていない。本書は WTG-100018 と違い、この点を「上流から意図して外れる（upstream-carryover）」と書いておらず、`.aidd/.engine/upstream-carryover.md` にも記録が無い。本書は pbi design が `/wtg060/return` へ戻すと書いているが、依存先の公開契約にその記述は無い。 | § このスペックが持たない責務（Out of Boundary）と § データ契約と外部連携に「pbi design は `/wtg070/returnList` の戻り先を `/wtg060` と書いているが、本書の `/wtg060/return` に直す。pbi design は Phase 5 の最後にまとめて直す（upstream-carryover）」と足す。`.aidd/.engine/upstream-carryover.md` にも同じ行を足す | 修正：戻りの口は回答 Q-DS-AS-001 で決まっており、食い違いの原因は pbi design 側の記述。本書に意図した逸脱として書き、上流を Phase 5 の最後にまとめて直す流れに乗せれば解消できる | 確認済み |  |  |
| 2 | traceability | 業務のあいまい・不足 | 要判断 | cfdc835e83689d21 | b3d53772fac02b98 | specs/application-status-search/design.md § バリデーション設計 | 文字種の入力チェック | 申請No・稟議ﾊﾞｰｺｰﾄﾞNo・基地局番号で、文字種（半角英数）を検査するかが決まっていない | 上流：requirements 4.1「検索条件に桁数・形式の条件を満たさない項目がある場合、システムはエラーメッセージを表示し、検索を止めなければならない（項目ごとの条件は design の画面設計で定める）」。&#10;下流：本書 § ドメインモデルは「38 項目の入力の形（桁・文字種・コンボの元）…は、検索条件の表を正とする」と書く。検索条件の表（`_handoff/phase5-application-status-search-conditions.md`）では、No.1 申請No が「半角英数」、No.2 稟議ﾊﾞｰｺｰﾄﾞNo が「半角英数（「-」を含む）」、No.3 基地局番号が「半角英数」。一方 § バリデーション設計の表は、これらの文字項目に桁の検査（`GEF-000003`）だけを置く。文字種の誤り（全角・記号）を検査するのか、検査しないのかが書かれていない。&#10;回答 Q-DS-AS-007 の 4 は、日付・時刻・数字のキーと「新しいキーは作らない」を決めているが、文字種には触れていない。&#10;意味判定：上流→下流。4.1 との ID 対応はあるが、形式の条件の一部（文字種）が決まっておらず、内容が足りない。 | 次のどちらかを決める。A：文字種もサーバーで検査し、既存のキーで止める（例：`WTE-000004`「{0}:半角英数以外が入力されています」。稟議ﾊﾞｰｺｰﾄﾞNo は「-」を許す既存のキー、たとえば `WTE-000011`「半角英数記号以外が入力されています」）。B：文字種は検査しない（前方一致で 0 件になるだけ）と、§ バリデーション設計に書く | 質問：検査するかどうかと使うキーは業務上の決めごとで、回答と上流からは決められない | 確認済み |  |  |
| 3 | traceability | 業務のあいまい・不足 | 要判断 | 68c8afa723211227 | 01ab50e7261ab0cf | specs/application-status-search/design.md § ドメインモデル（Domain Model） ほか 1 か所 | 社外ユーザーの所属①②・進捗の条件 | 社外ユーザーから所属①②・進捗の値が送られても、条件から外すことが書かれていない | 上流：requirements 1.6「ログインユーザーが社外ユーザーの場合、システムは検索条件の起案会社と所属を変更させず、進捗の検索条件を表示してはならない」。回答 Q-DS-AS-004「社外ユーザーには日数・以上/以下の 2 項目を出さない（条件にもならない）」。回答 Q-DS-AS-005「所属①②は空で変更不可」。steering/security.md の `#### 権限モデル` の禁止「画面の表示だけで制御せず、サーバー側でも権限を判定する」。&#10;下流：本書 § ドメインモデルの社外ユーザーの項は「所属①②は空で変更不可、進捗検索(日数)・(選択) は出さない」と、画面の扱いだけを書く。起案会社については、§ セキュリティ上の考慮で「起案会社は条件に使わない（変更不可の値を書き換えて送っても効かない）」と書いている。しかし、所属①②と進捗検索(日数)・(選択) について、Service が送られた値を条件から外すことは書いていない（§ サービスインターフェースの search と、§ テスト戦略の単体の社外ユーザーも同じ）。&#10;意味判定：1.6 との ID 対応はあるが、回答の「条件にもならない」が設計に反映されておらず、内容が足りない。 | § ドメインモデルの社外ユーザーの項に「社外ユーザーのときは、Service が所属①②・進捗検索(日数)・(選択) の値を空として扱い、条件に入れない（画面から送られても効かない）」と足す。§ テスト戦略の単体の社外ユーザーにも同じ確認を足す | 修正：進捗は回答 Q-DS-AS-004 が「条件にもならない」と決めており、所属①②も回答で空と決まっている。書き足すだけで済む | 確認済み |  |  |
| 4 | evidence-guard | 業務のあいまい・不足 | 要判断 | cffc53cab3f09d7a | 269ccc49c4eca9ac | specs/application-status-search/design.md § セキュリティ上の考慮（Security Considerations） | 更新者の氏名 | 一覧と CSV に更新者の氏名が出ると書くが、14 列に更新者は無い | 区分：根拠の飛躍。&#10;本書の「データ保護 / プライバシー」は「一覧と CSV に起案担当者と更新者の氏名が出る」と書く。根拠にあたる requirements の非機能要件（プライバシー）は「個人情報として起案担当者と更新者の氏名を扱い」（Q-RQ-AS-006「扱う個人情報は、起案担当者と更新者の氏名である」）で、扱うと書いているだけである。&#10;本書の一覧の 14 列（§ ドメインモデル）、CSV の見出し、requirements 2.1・3.1 のどこにも更新者は無い。更新者名は検索条件（部分一致、`TWTGM080.UpdatedPerson_Name`）として比べるだけである。探した根拠：requirements.md、steering/security.md の `## 機密データ`、回答 Q-DS-AS-006・Q-DS-AS-010。 | 「一覧と CSV に起案担当者の氏名が出る。更新者の氏名は検索条件として比べるだけで、画面にも CSV にも出さない。出すのは範囲内の申請だけで、ログに出さない」に直す | 修正：本書の一覧の列と食い違う記述で、本書の中の事実に合わせて直せる | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | specs/property-basic-info/design.md（Phase 5、upstream-carryover でまとめて直す） | `/wtg070/returnList` の戻り先が `/wtg060` と書かれており、回答 Q-DS-AS-001 で決めた戻りの口 `/wtg060/return` と食い違う |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 初期値 | 進捗検索(選択) の初期値「以上」と社外ユーザーの起案会社の初期値が、1.1 の「初期値を空」から外れる（回答で意図して外れると決まり、本書にも明記） | answer:design-authoring-generate[application-status-search] |
| traceability | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 一覧の 14 列 | 「他n局」を基地局番号にも付けるのは 2.3 から外れる（回答 Q-DS-AS-006 で決まり、本書にも明記） | answer:design-authoring-generate[application-status-search] |
| traceability | specs/application-status-search/design.md § ドメインモデル（Domain Model） / CSV | CSV の見出し（13 列目「発注希望日」、半角カナの表記）が一覧の列名と違う（回答 Q-DS-AS-010 で決まり、本書にも明記） | answer:design-authoring-generate[application-status-search] |
| dependency-boundary-conformance | specs/application-status-search/design.md § 機能固有エラーコード | pbi design の「既存の WTG-100018」と食い違い、本 feature で新しく足す（回答 Q-DS-AS-009 で決まり、upstream-carryover に記録済み） | answer:design-authoring-generate[application-status-search] |
| evidence-guard | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 検索の範囲 | 社外ユーザーの絞り込みを、検索条件の表の「会社名」ではなく会社コードで比べる（回答 Q-DS-AS-005 の 2 で決まる） | answer:design-authoring-generate[application-status-search] |
| steering-conformance | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 社外ユーザー | P71 のキー3 を、security.md の「ログインユーザーのグループ」ではなく権限区分とする（回答 Q-DS-AS-005 で決まる） | answer:design-authoring-generate[application-status-search] |
| steering-conformance | specs/application-status-search/design.md § API 契約（API Contract） | アクション名 csv・page・clear・return・detail が tech.md の URL の例に無い（回答 Q-DS-AS-001・Q-DS-AS-010 で決まり、例は「など」で限定していない） | answer:design-authoring-generate[application-status-search] |
| evidence-guard | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 検索条件 | 38 項目の入力の形・一致の仕方・比べる列を、回答者が渡した検索条件の表に委ねる（回答 Q-DS-AS-002「その表のとおりにしてください」） | answer:design-authoring-generate[application-status-search] |
| steering-conformance | specs/application-status-search/design.md § 技術スタック（Technology Stack） | 開発端末の JDK 1.8 が、tech.md の JDK 1.7 と食い違う | verify:pbi design（approved）の Q-DS-PBI-014 で人が決めた同じ逸脱で、本書にも意図して外れると明記し、upstream-carryover.md（tech.md の行）に記録済み。原因は上流の 1 か所で、重複になる |
| dependency-boundary-conformance | specs/application-status-search/design.md § 依存してよい対象（Allowed Dependencies） | feature-list の依存の列に無い issue-request の TWTGM100 を読む | verify:issue-request design（approved）が「下流が読む形：TWTGM100・TWTGM140 の全列」を公開契約にしており、内部実装への依存ではない |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 1 | 修正 | AI 推奨を採用: 戻りの口は回答 Q-DS-AS-001 で決まっており、食い違いの原因は pbi design 側の記述。本書に意図した逸脱として書き、上流を Phase 5 の最後にまとめて直す流れに乗せれば解消できる | Junichi Noumi | 2026-10-08T15:27:12+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 2 | 修正 | 修正案の B。文字種は検査しません（前方一致で 0 件になるだけ）。桁は入力欄の最大桁で抑え、日付・時刻・進捗の日数の形式は Q-DS-AS-007 のとおり検査します。バリデーション設計にそう書いてください | Junichi Noumi | 2026-10-08T15:27:15+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 3 | 修正 | AI 推奨を採用: 進捗は回答 Q-DS-AS-004 が「条件にもならない」と決めており、所属①②も回答で空と決まっている。書き足すだけで済む | Junichi Noumi | 2026-10-08T15:27:19+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 4 | 修正 | AI 推奨を採用: 本書の一覧の列と食い違う記述で、本書の中の事実に合わせて直せる | Junichi Noumi | 2026-10-08T15:27:23+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 2 | 2026-10-08T15:29:28+09:00 | ①② | ["specs/application-status-search/design.md"] | {"specs/application-status-search/design.md":"4644f42d210af2d852c7456f3387ac7540ec0fee02a5a0909a66dab3b7ca9b39"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| dependency-boundary-conformance | specs/application-status-search/design.md § データ契約と外部連携（Data Contracts &amp; Integration） ほか 1 か所 | `/wtg070/returnList` の戻り先を pbi design の `/wtg060` ではなく `/wtg060/return` とする（回答 Q-DS-AS-001 で決まり、本書に意図した逸脱と upstream-carryover を明記） | answer:design-authoring-generate[application-status-search] |
| traceability | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 初期値 | 進捗検索(選択) の初期値「以上」と社外ユーザーの起案会社の初期値が、1.1 の「初期値を空」から外れる（回答で意図して外れると決まり、本書にも明記） | answer:design-authoring-generate[application-status-search] |
| traceability | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 一覧の 14 列 | 「他n局」を基地局番号にも付けるのは 2.3 から外れる（回答 Q-DS-AS-006 で決まり、本書にも明記） | answer:design-authoring-generate[application-status-search] |
| traceability | specs/application-status-search/design.md § ドメインモデル（Domain Model） / CSV | CSV の見出し（13 列目「発注希望日」、半角カナの表記）が一覧の列名と違う（回答 Q-DS-AS-010 で決まり、本書にも明記） | answer:design-authoring-generate[application-status-search] |
| evidence-guard | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 検索の範囲 | 社外ユーザーの絞り込みを、検索条件の表の「会社名」ではなく会社コードで比べる（回答 Q-DS-AS-005 の 2 で決まる） | answer:design-authoring-generate[application-status-search] |
| steering-conformance | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 社外ユーザー | P71 のキー3 を、security.md の「ログインユーザーのグループ」ではなく権限区分とする（回答 Q-DS-AS-005 で決まる） | answer:design-authoring-generate[application-status-search] |
| evidence-guard | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 検索条件 | 38 項目の入力の形・一致の仕方・比べる列を、回答者が渡した検索条件の表に委ねる（回答 Q-DS-AS-002「その表のとおりにしてください」） | answer:design-authoring-generate[application-status-search] |
| evidence-guard | specs/application-status-search/design.md § バリデーション設計 | 桁の検査・日付・時刻・数字のキー（`GEF-000003`・`WTG-000003`・`GEF-000025`・`WTL-000007`・`GEF-000014`）と、範囲の逆転を検査しないこと（回答 Q-DS-AS-007 で決まり、キーは既存の messages.properties に実在） | answer:design-authoring-generate[application-status-search] |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 1 | 1 | feature:application-status-search | 2 | system（自動）：再検査で再検出なし | 2026-10-08T15:33:02+09:00 |
| feature:application-status-search | 1 | 2 | feature:application-status-search | 2 | system（自動）：再検査で再検出なし | 2026-10-08T15:33:02+09:00 |
| feature:application-status-search | 1 | 3 | feature:application-status-search | 2 | system（自動）：再検査で再検出なし | 2026-10-08T15:33:02+09:00 |
| feature:application-status-search | 1 | 4 | feature:application-status-search | 2 | system（自動）：再検査で再検出なし | 2026-10-08T15:33:02+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:application-status-search | 2 | specs/application-status-search/design.md | Junichi Noumi | 2026-10-08T15:44:50+09:00 | 4644f42d210af2d852c7456f3387ac7540ec0fee02a5a0909a66dab3b7ca9b39 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 2026-10-08T16:00:03+09:00 | ①② | ["specs/contract-info-import/design.md"] | {"specs/contract-info-import/design.md":"66017e8bc9c054721ddb1eff881806e043fd711c2d975c9d5af8191faea0898a"} | 10 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務の欠落・矛盾 | 重大 | 7dfcbcd311148df7 | 7a95fcbaef3ea20b | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 2.6 | 2.6 稟議バーコードNo | 2.6 を満たさない場合（リバースデータ・受付No 空）が逸脱として書かれていない | 意味判定：ID対応あり・内容未充足。requirements 2.6「取込を行うとき、システムは物件基本情報登録変更画面から渡された受付No と契約区分で、契約局ごとに稟議バーコードNo を付けなければならない」は条件を持たない。design の「稟議バーコードNo（2.6）」は「受付No が空（発番の前）なら NULL。リバースデータのときは NULL」とし、リバースデータの取込では全契約局に付けない（あわせて 2.9 で TWTGM110 の行が全部消える）。値の決め方は Q-DS-CI-004 の 2・3 で確定しているが、design の出典の表記・上流との関係の注記と、回答の「上流から意図して外れる点」（pbi design 391 行目付近・non-functional.md・security.md の 3 点）のどちらにも requirements 2.6 から外れることが無く、承認済み requirements と両立しない状態が記録されていない（pbi design の出力 CSV・TWTGM110 の物理削除は upstream-carryover と明記している） | ドメインモデルの「稟議バーコードNo（2.6）」の末尾に「受付No が空のときとリバースデータのときに稟議バーコードNo を付けないことは、requirements 2.6 から意図して外れる（Q-DS-CI-004）。上流は Phase 5 の最後にまとめて直す（upstream-carryover）」を足し、upstream-carryover に requirements（contract-info-import）2.6 を足す | 修正：値は人の回答で確定しており、逸脱の明記と持ち越しの記録だけが欠けているため | 確認済み |  |  |
| 2 | traceability | 業務のあいまい・不足 | 要判断 | 673337991fe89133 | 7a95fcbaef3ea20b | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 2.7 ほか 1 か所 | 取込中の申請へのバッチのエラー | バッチ開始時にすでに取込中だったときのエラーのメッセージが無い | 意味判定：1.8・4.7 に対応する処理はあるが内容が不足。ドメインモデルの「取込中」は「すでに取込中（06）なら何も変えずにエラーで終わる（元に戻す更新もしない）」、エラー時の分岐フローの E0 は「エラーで終わる 何も変えない」とだけ書き、バッチ処理状況に何のキー・文言を出すか、件数のメッセージを出すか、終了の状態が無い。機能固有エラーコードの表（WTG-200008〜200012・WTG-100030）とバリデーション設計の表にもこの場合の行が無い。Q-DS-CI-006 は「エラーで終わります」までで、キーを定めていない（新しいキーを作らないのは画面の WTG-100030 について） | 決めること：E0 でバッチ処理状況に出すメッセージ。案 A：既存の WTG-100030 を logError で出す（新しいキーを作らない方針に合う）。案 B：JAVA-KIT に新しいキーを足す（Q-DS-CI-012 の 2 の範囲が増える）。あわせて件数のメッセージを出すかを決める | 質問：利用者がバッチ処理状況で見る内容で、回答に無い業務の値のため | 確認済み |  |  |
| 3 | traceability | 業務のあいまい・不足 | 要判断 | d744476992f3ff3e | 0a475ec7d75cc969 | specs/contract-info-import/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 4.6・4.8 ほか 1 か所 | エラー時の警告と件数 | エラーで取り消したときに警告を出すかと、件数の {2} が決まっていない | 意味判定：4.6・4.8 に対応する記述はあるが境界の場合が不足。データ契約の「バッチ処理状況」は「エラーで取り消したときは {0}・{1} を 0、{3} をエラーのあった行の数にする」とし、ワーニング {2} の値が無い。エラー時の分岐フローは区分 3 にエラーが無いときだけ「警告 WTG-200009・WTG-000072 を出す」へ進むので、エラーがあると警告を出さないと読めるが、検査表の 1-3（「【ﾁｪｯｸ区分3】＜ﾜｰﾆﾝｸﾞ＞」）は警告を区分 3 の中の検査として置いており、ドメインモデルの「警告」にもエラーのときの扱いが無い。Q-DS-CI-012 の 4 も {2} のエラー時の値を定めていない | 決めること：エラーで取り消したときに警告を詳細に出すか、{2} に何を入れるか。案 A：警告も出し、{2} は警告の件数。案 B：警告は出さず、{2} は 0（分岐フローのとおり）。決めた内容をデータ契約の「バッチ処理状況」とエラー時の分岐フローの両方に書く | 質問：利用者に出す件数と警告の業務の値で、回答に無いため | 確認済み |  |  |
| 4 | traceability | 業務のあいまい・不足 | 要判断 | 1c960550a706ed28 | 7a95fcbaef3ea20b | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 2.5 | 担当エリアの引き継ぎ | 洗替の前に発行依頼書が無い申請での担当エリア・担当エリア名が決まっていない | 意味判定：2.5 に対応する記述はあるが境界の場合が不足。ドメインモデルの「洗替の前から引き継ぐ値」は「TWTGM100 は担当エリア・担当エリア名を洗替の前の TWTGM100 から」とし、対応表 2 の No.10・11 も「(40)GM100．担当ｴﾘｱ」「(40)GM100．担当ｴﾘｱ名」だけ。取込は 14.5 の起案者（未起案・下書き）の番でも実行でき、pbi design は発行依頼書を「読取りと削除・複製だけ」とするので、取込の時点で TWTGM100 の行が無い申請がありうる。そのときの担当エリア・担当エリア名（NULL にするか、渡された担当エリア g_AreaCd とその名称を入れるか）が書かれていない。稟議バーコードNo のエリア接頭語は渡された担当エリアで引くと書いており、同じ申請で両者が食い違いうる | 決めること：洗替の前の TWTGM100 が無いときの担当エリア・担当エリア名。案 A：NULL にする。案 B：渡された担当エリア（g_AreaCd）と、そのコードで引いた名称を入れる。案 C：洗替の前の行の有無によらず、渡された担当エリアを入れる | 質問：発行依頼書に残る業務の値で、回答・対応表に無いため | 確認済み |  |  |
| 5 | steering-conformance | 業務の欠落・矛盾 | 重大 | b34da98e86a4a79f | e5f5930e8e1610a9 | specs/contract-info-import/design.md § 機能固有のエラー処理（Error Handling） ほか 1 か所 | WTG-200011 の電話番号 | 契約者の電話番号の値をバッチ処理状況に出すが steering からの逸脱と書いていない | 矛盾。steering/non-functional.md の「#### 出力しない」#3「契約者の個人情報（氏名、住所、連絡先）」、steering/security.md の「## 機密データ」の「契約者の個人情報（氏名・住所・連絡先）…ログに出さない」。design の「ログ」は「各メッセージの {2} には検査表の『置換文字』の値（…郵便番号・都道府県と市区町村・金額・電話番号など）を入れる」とし、バリデーション設計の WTG-200011「行数[{0}]:{1}[{2}]:固定電話は10桁、IP電話は11桁で入力してください。」の対象は検査表の契約者・関係者①〜⑤_TEL（固定）（携帯）（1-2 の No.39・40 ほか、2-2 の No.55・56 ほか）。電話番号を入れること自体は Q-DS-CI-012 の 3 で決まっているが、design は住所（WTG-200009・WTG-000072）と担当者の氏名（タスクのパラメータ）だけを「steering から意図して外れる」と書き、連絡先（電話番号）は書いていない。回答の「上流から意図して外れる点」にも電話番号は無い。セキュリティ上の考慮の「ログからの個人情報の漏れ」も氏名・メールアドレス・マイナンバーを受け取った日だけを挙げる | 機能固有のエラー処理の「ログ」と、セキュリティ上の考慮の「データ保護 / プライバシー」に「WTG-200011 は、行番号と一緒に契約者・関係者の電話番号の値を出す。steering/non-functional.md・security.md の『契約者の連絡先をログに出さない』から意図して外れる（Q-DS-CI-012 の 3）。上流は Phase 5 の最後にまとめて直す（upstream-carryover）」を足し、upstream-carryover に足す。電話番号を出さない方に変えるなら、WTG-200011 の {2} を空にする | 修正：出す値は人の回答で確定しており、steering との食い違いの明記と持ち越しの記録が欠けているため | 確認済み |  |  |
| 6 | evidence-guard | 業務のあいまい・不足 | 要判断 | 4172a48175b71d02 | d08a2bdf1338340b | specs/contract-info-import/design.md § 取込画面 Service / 依存関係 ほか 2 か所 | 同じ申請No のタスクの確認 | STaskList の確認を BatchCommonService で行うとするが、その口が既存に無い | 根拠の飛躍。取込画面 Service の呼び出し先に「BatchCommonService — STaskList の確認とタスクの登録」、実行の手順 3 に「同じ申請No（パラメータ g_ApplicationNo）の、待機中・処理中の取込のタスクが STaskList にあれば WTG-100030」とある。既存の wing/src/main/java/jp/co/kccs/wt/common/service/BatchCommonService.java は insertTask（:50〜:63）と private の toTSVString（:73）だけで、STaskList を読む口が無い。パラメータは「キー=値」のタブ区切り 1 列（:66〜:92）に入るので、申請No で探す条件（列と比べ方）が要る。待機中・処理中に当たる STaskList の状態の値も書かれていない（既存の一覧は STaskList.status と STaskListEx.Process_Status を持つ。Pzzzo011Mapper.xml:57・:69）。一方、ファイル配置計画の wtg090 は controller・service・form だけで Mapper が無く、変更する既存ファイルは「既存のファイルは変えない」としているので、この確認の SQL を置く場所が無い（手本の wtg040 にも Mapper は無い） | ファイル配置計画に wtg090 の Mapper（例 mapper/Pwtgo090Mapper.java と resources の Pwtgo090Mapper.xml）を足し、取込画面 Service の呼び出し先を「Pwtgo090Mapper — STaskList の確認」に直す。実行の手順 3 に、対象のタスク（タスクID A8B36D2BB98F419FB0718303BCA2C9B6）、待機中・処理中に当たる状態の値、パラメータ列での申請No の比べ方（例 g_ApplicationNo=申請No とタブで囲んだ文字列を含む）を書く。既存の BatchCommonService に口を足すなら、変更する既存ファイルにその旨を書く | 修正：既存コードで決められる実装の置き場と条件の記述が欠けているため | 確認済み |  |  |
| 7 | evidence-guard | 業務のあいまい・不足 | 要判断 | ead6e63443eeefbe | 0a475ec7d75cc969 | specs/contract-info-import/design.md § データ契約と外部連携（Data Contracts &amp; Integration） ほか 1 か所 | 警告だけのときの終了の状態 | 警告を logWarn で出すと既存の基盤では警告終了になり、正常終了と両立しない | 根拠の飛躍。design は「警告は 1 件ずつ logWarn」（データ契約の「バッチ処理状況」）と「警告だけなら正常終了（警告終了にはしない）」（機能固有のエラー処理の「返し方」、Q-DS-CI-012 の 5）を並べている。既存の WTX_Batch/src/jp/co/kccs/greenearth/javakit/frame/batch/engine/WTBatchJob.java:152〜:174 の logWarn は SBatchLog に LOG_TYPE_WARNNING の行を書き、WTActiveTask.java:350〜:355 は「existsWarningError(getObjectID())」が真なら STATUS_WARNING を返す（:350 の注記は警告・エラーがあれば警告終了にする旨）。existsWarningError の本体は作業ツリーに無い（基盤のクラス）が、名前と注記からは logWarn を 1 件でも書くとタスクが警告終了になると読め、design の 2 つの記述が両立するかを示す根拠が無い | 決めること：警告の出し方と終了の状態。案 A：logWarn で出し、警告終了を受け入れる（Q-DS-CI-012 の 5 を直す）。案 B：正常終了を保つため、警告を logWarn ではなく writeCustomLog の INFO で出す（バッチ処理状況の詳細での見え方が変わる）。案 C：existsWarningError の判定を確かめてから決める | 質問：回答の正常終了と既存の基盤の動きが食い違い、どちらを優先するかは人が決めるため | 確認済み |  |  |
| 8 | evidence-guard | 出典・根拠 | 軽微 | 1e700ea75056bb76 | 72ba07015e1ca370 | specs/contract-info-import/design.md § API 契約（API Contract） | CSRF の照合の出典 | CSRF の照合の出典の行が servlet-context.xml:68 で、照合の設定の行と違う | 出典不明。API 契約の注記は「/wtg090/execute は URL の末尾が execute なので CSRF の照合に乗る（wing/src/main/resources/servlet-context.xml:68）」とするが、:68 は multipartResolver の maxUploadSize（1048576000）の行。CSRF の照合は :121〜:130 の CSRFTokenCheckInterceptor で、/**/execute は :127 | 出典を「wing/src/main/resources/servlet-context.xml:121〜:130（/**/execute は :127）」に直す。アップロードの上限の文には「servlet-context.xml:68」を出典として付ける | 修正：出典の行番号の誤りで、正しい行が既存コードで決まるため | 確認済み |  |  |
| 9 | evidence-guard | 工程・文書の分担 | 軽微 | 70729629f4ba0b8f | e4d589d6175021b6 | specs/contract-info-import/design.md § 依存してよい対象（Allowed Dependencies） | chkKichikyoku | 契約区分の判定の部品を使えるかを tasks に回しているが、既存コードで決まる | 依存先に「共通部品 WTKeikakuJudgeUtils.chkKichikyoku（契約区分の判定。ir design と同じ）。WTX_Batch から使えない場合は、同じ判定（局種別判定マスタ WTZ/MASTER/M09）を WTX_Batch の側に置く（tasks で決める）」とある。ir design の chkKichikyoku は wing の wing/src/main/java/jp/co/kccs/wt/common/utils/WTKeikakuJudgeUtils.java:36（BindingResult と CodeMstService を受ける）で、WTX_Batch からは使えない。一方 WTX_Batch には既存の WTX_Batch/src/jp/co/kccs/wt/util/WTKeikakuJudgeUtils.java があり、:98 に chkKichikyoku(String)（M09 を引く。:128）がある。使う部品は design で決められ、tasks の工程の境界（B-04 はタスクの分割・実装の順番）に当たらない | 依存先を「WTX_Batch の既存の共通部品 WTKeikakuJudgeUtils.chkKichikyoku(String)（WTX_Batch/src/jp/co/kccs/wt/util/WTKeikakuJudgeUtils.java:98。局種別判定マスタ M09 を引く。ir design が使う wing の同名の部品と同じ判定）」に直し、「使えない場合は…tasks で決める」を消す | 修正：既存コードで決まる設計の判断を後の工程に残さないため | 確認済み |  |  |
| 10 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | 5bea7a0034e82084 | 1c723623a42db099 | specs/contract-info-import/design.md § セキュリティ上の考慮（Security Considerations） / 脅威と対策 ほか 1 か所 | 社外ユーザーの範囲 | 社外ユーザーの範囲外の申請を getApplication・canOperate が拒否するとするが公開契約に無い | design は「社外ユーザーの範囲外の申請 → getApplication・canOperate が範囲外を拒否する（pbi design）」とし、取込画面 Service の実行の手順 2 も「申請No で getApplication を引き、canOperate（契約局取込）で番と状態を判定する」だけ。pbi design の公開契約（WTG 申請状態サービスのサービスインターフェース）では getApplication は「会社コード、申請No → 申請。無ければ null」で範囲の条件を持たず、canOperate は依頼内容・番・状態・審査権限（起案者は常に含む）で可否を返し、会社の範囲を見ない。範囲は getExternalScope（社外ユーザーなら自社の会社コードと本人のユーザーID）として別に公開され、pbi の画面は「申請を取り出す SQL の条件に社外ユーザーの範囲を加え、範囲外は無いものとして扱う」（pbi design のセキュリティ上の考慮）と自分の SQL で絞っている。/wtg090 は 9 項目を POST で受けるので、社外ユーザーが他社の申請No を送ると、この design の手順では範囲で止まらない（steering/security.md の「#### 所有権・エンティティ境界」、requirements 1.7） | 実行の手順 2 に「getExternalScope で社外ユーザーの範囲を取り、申請（getApplication の結果と発行依頼書の契約稟議起案者_会社コード、または登録者）が範囲外なら、無いものとして WTG-100030（または pbi と同じ扱い）で止める」を足し、脅威と対策と依存先（getExternalScope）を同じに直す。WTG 申請状態サービスに範囲つきの取得の口を足すなら、pbi design への差戻しとして扱う | 修正：依存先の公開契約に既にある getExternalScope で満たせ、範囲の判定が抜けると他社の申請を取り込めるため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 3.1 | 洗替の前にだけある行・後にだけある行を変更履歴に入れない扱い | answer:design-authoring-generate[contract-info-import] |
| traceability | specs/contract-info-import/design.md § API 契約（API Contract） / 1.4 | 渡された 9 項目をセッションの値のままタスクのパラメータにし、DB から引き直さない扱い | answer:design-authoring-generate[contract-info-import] |
| traceability | specs/contract-info-import/design.md § 状態管理（State Management） / 1.7 | バッチが動き出したときに審査フェーズ・状態（14.5）を確かめ直さない扱い | answer:design-authoring-generate[contract-info-import] |
| steering-conformance | specs/contract-info-import/design.md § 機能固有のエラー処理（Error Handling） | WTG-200009・警告の WTG-000072 に住所の値を出す（steering/non-functional.md からの逸脱として明記済み） | answer:design-authoring-generate[contract-info-import] |
| steering-conformance | specs/contract-info-import/design.md § セキュリティ上の考慮（Security Considerations） | タスクのパラメータに申請者・起案者の氏名を入れ一覧に出す（steering/security.md からの逸脱として明記済み） | answer:design-authoring-generate[contract-info-import] |
| dependency-boundary-conformance | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 2.1 | pbi design の出力 CSV が「契約情報取込で読める形」でない食い違い（upstream-carryover として明記済み） | answer:design-authoring-generate[contract-info-import] |
| dependency-boundary-conformance | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 2.9 | TWTGM110 の物理削除と pbi design の「行は物理削除しない」の食い違い（例外として明記済み） | answer:design-authoring-generate[contract-info-import] |
| evidence-guard | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 契約区分 | 対応表 2 の No.8 の値（341・241・141、X-11 の返り値 "1"）と design の値（003・001・002、"S"・"D"）の違い。回答が P78 のキー3 と S・D を指定 | answer:design-authoring-generate[contract-info-import] |
| dependency-boundary-conformance | specs/contract-info-import/design.md § サービスインターフェース（Service Interface） | 同じ申請No のタスクがあるときも WTG-100030 を使い、新しいキーを作らない扱い | answer:design-authoring-generate[contract-info-import] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 8 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-08T16:09:28+09:00 |  |  |  |
| feature:contract-info-import | 1 | 9 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-08T16:09:28+09:00 |  |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 1 | 修正 | AI 推奨を採用: 値は人の回答で確定しており、逸脱の明記と持ち越しの記録だけが欠けているため | Junichi Noumi | 2026-10-08T16:16:33+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 2 | 修正 | 修正案の A。WTG-100030 を logError で出し、件数のメッセージは出しません（取込をしていないため） | Junichi Noumi | 2026-10-08T16:16:37+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 3 | 修正 | 修正案の A。エラーで取り消したときも警告は出し、件数の {2} は警告の件数、{0}・{1} は 0、{3} はエラーのあった行の数です | Junichi Noumi | 2026-10-08T16:16:40+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 4 | 修正 | 修正案の A。洗替の前に発行依頼書が無ければ、担当エリア・担当エリア名は NULL です | Junichi Noumi | 2026-10-08T16:16:44+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 5 | 修正 | AI 推奨を採用: 出す値は人の回答で確定しており、steering との食い違いの明記と持ち越しの記録が欠けているため | Junichi Noumi | 2026-10-08T16:16:48+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 6 | 修正 | AI 推奨を採用: 既存コードで決められる実装の置き場と条件の記述が欠けているため | Junichi Noumi | 2026-10-08T16:16:51+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 7 | 修正 | 修正案の A。警告は logWarn で出し、警告だけのときは警告終了を受け入れます。Q-DS-CI-012 の 5 の「正常終了」はこの内容に直します | Junichi Noumi | 2026-10-08T16:16:55+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 10 | 修正 | AI 推奨を採用: 依存先の公開契約に既にある getExternalScope で満たせ、範囲の判定が抜けると他社の申請を取り込めるため | Junichi Noumi | 2026-10-08T16:16:58+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 2 | 2026-10-08T16:32:12+09:00 | ①② | ["specs/contract-info-import/design.md"] | {"specs/contract-info-import/design.md":"e10ddaceda22b57a59ce8aad45ad2d0e92d4e245a01d3c1602fdeac99b4939a4"} | 3 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務のあいまい・不足 | 要判断 | 4b97ec8f81861b0a | fd47e3700381b780 | specs/contract-info-import/design.md § 取込画面 Service / 実行の手順 3 | 同じ申請No のタスクの確認 | STaskList のパラメータで申請No を比べる条件があいまいで、先頭の項目を見逃しうる | 意味判定：1.8 に対応する処理はあるが、条件の書き方が不足。design の手順 3 は「パラメータ（`parameter`）がタブで区切った `g_ApplicationNo=申請No` を含む行があれば `WTG-100030`」とだけ書く。既存の `BatchCommonService.toTSVString`（`wing/src/main/java/jp/co/kccs/wt/common/service/BatchCommonService.java:73`〜`:93`）は各項目を「キー=値」＋タブで連結し、先頭にタブは付かない（末尾にだけ付く）。既存の取込画面はパラメータを `HashMap` で作る（`wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg040/service/Pwtgo040Service.java:106`）ため項目の順は決まらず、`g_ApplicationNo` が先頭に来ることがある。両側をタブで囲んだ文字列で比べると先頭のときに一致せず、同じ申請No のタスクを見逃す。囲まずに `g_ApplicationNo=申請No` だけで比べると、申請No が前方一致する別の申請（例 `=12` と `=123`）を誤って一致させる。状態の値（'0' 待機中・'1' 処理中。`Pzzzo011Service.java:205`〜`:211`）と列（`STaskList.parameter`・`status`。`Pzzzo011Mapper.xml:67`〜`:69`）は既存と一致することを確かめた | 手順 3 の比べ方を「パラメータの先頭にタブを付けた文字列（タブ＋`parameter`）が、タブ＋`g_ApplicationNo=`＋申請No＋タブ を含む」と書く（または `parameter` をタブで分け、`g_ApplicationNo` の値と完全一致で比べる） | 修正：既存コードで決まる比べ方の記述が欠けており、1.8 の多重実行の判定が漏れうるため | 確認済み |  |  |
| 2 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | 95ccf33fe44782b3 | fd47e3700381b780 | specs/contract-info-import/design.md § 取込画面 Service / 実行の手順 2 ほか 1 か所 | 社外ユーザーの範囲 | 範囲の判定に使う発行依頼書の会社コードの取り方が無く、画面から送られた値で判定しうる | 手順 2 は「申請（発行依頼書の契約稟議起案者_会社コード、または申請の登録者）が範囲外なら無いものとして `WTG-100030`」とする（ほか：セキュリティ上の考慮の脅威と対策「社外ユーザーの範囲外の申請」）。pbi design の公開契約では、`getApplication` の出力は申請（`TWTGM080`：依頼内容・審査フェーズ・状態・申請回数・元申請No・排他用の値ほか）で、発行依頼書（`TWTGM100`）の会社コードを返さない。`getExternalScope` は自社の会社コードとユーザーID を返すだけ（pbi design § サービスインターフェース）。本書の取込画面 Service の呼び出し先と取込画面 Mapper（`STaskList` の確認だけ）にも、申請No で `TWTGM100` を引く口が無い。セッションの 9 項目にある契約稟議起案者の会社コードは `POST /wtg090` で画面から送られる値（API 契約）で、これで判定すると値の書き換えで範囲外の申請を取り込める。pbi design は申請を取り出す SQL の条件に範囲（自社の契約稟議起案会社か本人の登録）を加え、契約稟議起案会社は申請No で引いた `TWTGM100` の 1 件目の契約稟議起案者_会社コードとしている（pbi design § セキュリティ上の考慮・バリデーション設計）。design-check 1 回目 #10 の修正で入った判定の、値の出所が残っている | 取込画面 Mapper に「申請No で `TWTGM100` の契約稟議起案者_会社コードを引く」を足し（コンポーネント一覧・ファイル配置計画の Mapper の説明も）、手順 2 に「会社コードは DB から引き、セッションの値は使わない。登録者は `getApplication` の結果の `RegisteredPerson` と比べる」と書く。WTG 申請状態サービスに範囲つきの取得の口を足すなら、pbi design への差戻しとして扱う | 修正：判定に要る値の取り方が欠けており、送られた値を使うと他社の申請を取り込めるため | 確認済み |  |  |
| 3 | evidence-guard | 業務のあいまい・不足 | 要判断 | f5124989bedd9db0 | 293efec102f3fc03 | specs/contract-info-import/design.md § 機能固有のエラー処理（Error Handling） ほか 2 か所 | バッチの WTG-100030 | バッチが WTG-100030 を出すが、バッチが読む JAVA-KIT のメッセージに足す予定が無い | 根拠の飛躍。design は、バッチの開始時にすでに取込中なら「`WTG-100030` を `logError` で出す」とする（機能固有のエラー処理の返し方・ドメインモデルの取込中・エラー時の分岐フローの E0）。一方、design 自身が「バッチのメッセージは JAVA-KIT の DB から読む」（既存アーキテクチャの分析）とし、JAVA-KIT に足すのは `WTG-200008`〜`WTG-200012` だけ（機能固有エラーコード、移行方針、移行対象ファイル一覧の「5 行」）。`WTG-100030` は pbi design が wing の `messages.properties` にだけ足すキー（pbi design § 変更する既存ファイル）。JAVA-KIT の DB に `WTG-100030` があることの根拠は、requirements・steering・pbi design のどこにも無い。design-check 1 回目 #2 の判断（`WTG-100030` を `logError` で出す）を実装するための前提が書かれていない | 決めること：A：JAVA-KIT のメッセージに `WTG-100030`（pbi design と同じ文言）を足し、移行方針・移行対象ファイル一覧を 6 行にする。B：JAVA-KIT の DB にすでにあるなら、その出典を書く | 質問：JAVA-KIT の DB にすでにあるかは承認済みの文書から分からず、投入の範囲が変わるため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| steering-conformance | specs/contract-info-import/design.md § 機能固有のエラー処理（Error Handling） | WTG-200009・WTG-000072 の住所の値と WTG-200011 の電話番号の値をバッチ処理状況に出す（steering からの逸脱として明記済み） | answer:design-authoring-generate[contract-info-import] |
| steering-conformance | specs/contract-info-import/design.md § セキュリティ上の考慮（Security Considerations） | タスクのパラメータに申請者と起案者の氏名を入れ、バッチ処理状況一覧に出る（steering からの逸脱として明記済み） | answer:design-authoring-generate[contract-info-import] |
| traceability | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 2.6 | 受付No が空のときとリバースデータのときに稟議バーコードNo を NULL にする（requirements 2.6 からの逸脱として明記済み） | answer:design-authoring-generate[contract-info-import] |
| traceability | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 2.9 | TWTGM110 を物理削除する（pbi design の「物理削除しない」の例外として明記済み） | answer:design-authoring-generate[contract-info-import] |
| evidence-guard | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 4.6 | 警告だけのときに警告終了とし、Q-DS-CI-012 の 5 の「正常終了」と異なる | verify:前回の人の判断（design-check 1 回目 #7、修正案の A）で決まっており、本文に明記済み |
| dependency-boundary-conformance | specs/contract-info-import/design.md § 依存してよい対象（Allowed Dependencies） | 契約区分の判定に WTKeikakuJudgeUtils.chkKichikyoku を使う（WTX_Batch の既存の共通部品で、ir design の内部への依存ではない。WTKeikakuJudgeUtils.java:98 を確かめた） | answer:design-authoring-generate[contract-info-import] |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 1 | 1 | feature:contract-info-import | 2 | system（自動）：再検査で再検出なし | 2026-10-08T16:36:46+09:00 |
| feature:contract-info-import | 1 | 2 | feature:contract-info-import | 2 | system（自動）：再検査で再検出なし | 2026-10-08T16:36:46+09:00 |
| feature:contract-info-import | 1 | 3 | feature:contract-info-import | 2 | system（自動）：再検査で再検出なし | 2026-10-08T16:36:46+09:00 |
| feature:contract-info-import | 1 | 4 | feature:contract-info-import | 2 | system（自動）：再検査で再検出なし | 2026-10-08T16:36:46+09:00 |
| feature:contract-info-import | 1 | 5 | feature:contract-info-import | 2 | system（自動）：再検査で再検出なし | 2026-10-08T16:36:46+09:00 |
| feature:contract-info-import | 1 | 6 | feature:contract-info-import | 2 | system（自動）：再検査で再検出なし | 2026-10-08T16:36:46+09:00 |
| feature:contract-info-import | 1 | 7 | feature:contract-info-import | 2 | system（自動）：再検査で再検出なし | 2026-10-08T16:36:46+09:00 |
| feature:contract-info-import | 1 | 8 | feature:contract-info-import | 2 | system（自動）：再検査で再検出なし | 2026-10-08T16:36:46+09:00 |
| feature:contract-info-import | 1 | 9 | feature:contract-info-import | 2 | system（自動）：再検査で再検出なし | 2026-10-08T16:36:46+09:00 |
| feature:contract-info-import | 1 | 10 | feature:contract-info-import | 2 | system（自動）：再検査で再検出なし | 2026-10-08T16:36:46+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-import | 2 | 1 | 修正 | AI 推奨を採用: 既存コードで決まる比べ方の記述が欠けており、1.8 の多重実行の判定が漏れうるため | Junichi Noumi | 2026-10-08T16:49:50+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-import | 2 | 2 | 修正 | AI 推奨を採用: 判定に要る値の取り方が欠けており、送られた値を使うと他社の申請を取り込めるため | Junichi Noumi | 2026-10-08T16:49:53+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 2 | 3 | 修正 | 修正案の A。WTG-100030 は今回の案件で新しく作るキーなので、JAVA-KIT の DB にはまだありません。WTG-200008〜200012 と一緒に、JAVA-KIT のメッセージに足してください（文言は物件基本情報登録変更と同じ） | Junichi Noumi | 2026-10-08T16:49:57+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 3 | 2026-10-08T16:52:28+09:00 | ①② | ["specs/contract-info-import/design.md"] | {"specs/contract-info-import/design.md":"6660bfaf7d152ab06d43f3a5e9b0b560ce2f8b532401dc2fdaf08aba255fcf00"} | 2 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務のあいまい・不足 | 要判断 | 09883b5ecbb50491 | d057a8e58ec71728 | specs/contract-info-import/design.md § 取込画面 Service / 実行の手順 2 | 発行依頼書が無い申請の範囲 | 発行依頼書（TWTGM100）がまだ無い申請で、社外ユーザーの範囲をどう判定するかが書かれていない | 意味判定：1.7（契約局取込ボタンを使える利用者。社外ユーザーは pbi の 6.5 の範囲）に対応する処理はあるが、境界の場合が足りない。design-check 2 回目 #2 の修正で、手順 2 は「範囲の判定に使う契約稟議起案者_会社コードは、取込画面 Mapper で申請No から `TWTGM100` を引いて取り」とした。取込は発行依頼書がまだ無い申請にも実行できる（ドメインモデルの「洗替の前に発行依頼書が無ければ NULL」。design-check 1 回目 #4）ので、`TWTGM100` が引けない場合がある。そのときの判定（会社コードが無いので登録者だけで見るか、範囲外とするか）が本書のどこにも無い。ir design は同じ判定で「発行依頼書がまだ無い申請は物件申請情報の範囲（pbi design の 6.5）で見る」と明記している（`specs/issue-request/design.md` § セキュリティ上の考慮）。pbi design の範囲は「自社の契約稟議起案会社か本人の登録」（`specs/property-basic-info/design.md` § セキュリティ上の考慮）。書かれていないと、引けないときに範囲外として本人が登録した申請の取込を拒む実装も、会社コードの比較を飛ばして範囲内とする実装もありうる | 手順 2 に「`TWTGM100` が引けない（発行依頼書がまだ無い）申請は、会社コードの条件を満たさないものとし、登録者（`getApplication` の結果の `RegisteredPerson`）が本人なら範囲内とする（ir design・pbi design の 6.5 と同じ）」を足す | 修正：ir design・pbi design に同じ判定の決まりがあり、本書の判定をそれに揃える記述だけが欠けているため | 確認済み |  |  |
| 2 | dependency-boundary-conformance | 業務のあいまい・不足 | 要判断 | 6301daa4b36d6e08 | f8c887ea62daee77 | specs/contract-info-import/design.md § 機能固有エラーコード / WTG-100030 ほか 2 か所 | WTG-100030 の置換文字 | 本 feature で出す WTG-100030 の {0}〜{2}（ステータス・状態区分・操作）に入れる値が無い | pbi design の公開の定義では、`WTG-100030` の文言は「ステータス、状態区分、操作の組み合わせが不正です。ステータス：{0}、状態区分：{1}、操作：{2}」で、置換文字を 3 つ持つ（`specs/property-basic-info/design.md` § 機能固有エラーコード）。本書は `WTG-100030` を (1) 画面で `canOperate`（契約局取込）が受け付けないとき、(2) 社外ユーザーの範囲外のとき、(3) 同じ申請No のタスクが待機中・処理中のとき（取込画面 Service の実行の手順 2・3）、(4) バッチの開始時にすでに取込中のとき（機能固有のエラー処理の返し方、ドメインモデルの取込中）に出し、JAVA-KIT のメッセージにも同じ文言で足す（機能固有エラーコード・移行方針。design-check 2 回目 #3）。しかし、どの場合も {0}〜{2} に何を入れるか（例：審査フェーズの名称、状態区分の名称、操作＝「契約局取込」）が書かれていない。(3)(4) は組合せの不正ではない場面で出すため、pbi design の `transit` の値の入れ方をそのまま使えない | 決めること：各場面の {0}・{1}・{2} の値。案 A：{0}＝申請の審査フェーズ（`P28` の名称）、{1}＝状態区分（`P27` の名称）、{2}＝「契約局取込」をどの場面でも入れる（範囲外のときは申請を無いものとして扱うので空にする）。案 B：場面ごとに別の値を表で定める | 質問：置換文字に入れる値は承認済みの文書と回答から決まらず、利用者がバッチ処理状況と画面で見る文言が変わるため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/contract-info-import/design.md § 取込画面 Service / 実行の手順 3 | 同じ申請No のタスクが待機中・処理中のときも、文言が組合せの不正である WTG-100030 を使い、新しいキーを作らない | answer:design-authoring-generate[contract-info-import] |
| steering-conformance | specs/contract-info-import/design.md § 機能固有エラーコード | WTG-200008〜WTG-200012 を JAVA-KIT のメッセージ（DB）にだけ足し、wing の messages.properties には足さない | answer:design-authoring-generate[contract-info-import] |
| evidence-guard | specs/contract-info-import/design.md § 移行方針（Migration Strategy） | 投入の文と手順は本 feature の tasks で作り、投入の実施は発注者が導入手順書に沿って行う（タスクID・出力コード・VE の 14 のテーブル・マスタ） | answer:design-authoring-generate[contract-info-import] |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 2 | 1 | feature:contract-info-import | 3 | system（自動）：再検査で再検出なし | 2026-10-08T16:56:36+09:00 |
| feature:contract-info-import | 2 | 2 | feature:contract-info-import | 3 | system（自動）：再検査で再検出なし | 2026-10-08T16:56:36+09:00 |
| feature:contract-info-import | 2 | 3 | feature:contract-info-import | 3 | system（自動）：再検査で再検出なし | 2026-10-08T16:56:36+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-import | 3 | 1 | 修正 | AI 推奨を採用: ir design・pbi design に同じ判定の決まりがあり、本書の判定をそれに揃える記述だけが欠けているため | Junichi Noumi | 2026-10-08T18:18:26+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 3 | 2 | 修正 | 修正案の A。どの場面でも {0}＝審査フェーズの名称（P28）、{1}＝状態区分の名称（P27）、{2}＝「契約局取込」とします。社外ユーザーの範囲外のときは、{0}・{1} を空にします（印刷・閲覧用帳票と同じ考え方） | Junichi Noumi | 2026-10-08T18:18:30+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 4 | 2026-10-08T18:26:59+09:00 | ①② | ["specs/contract-info-import/design.md"] | {"specs/contract-info-import/design.md":"4c8a75122096a3b0e11bc9879722b86ecf6a395fe1f145a45958d88a0f58b135"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| evidence-guard | specs/contract-info-import/design.md § 機能固有エラーコード / WTG-100030 | WTG-100030 の置換文字（{0}＝P28 の名称、{1}＝P27 の名称、{2}＝「契約局取込」、範囲外は {0}・{1} を空）の出典が上流（requirements・steering）に無い | verify:人の判断（design-check 3 回目 #2 の判断「修正案の A」と理由、Junichi Noumi 2026-10-08T18:18:30+09:00）で決まった値であり、根拠のない追記ではない |
| traceability | specs/contract-info-import/design.md § 取込画面 Service / 実行の手順 2 | 発行依頼書（TWTGM100）が無い申請は登録者だけで社外ユーザーの範囲を判定する記述が、1.7 と pbi 6.5 の範囲に合うか | verify:ir design § セキュリティ上の考慮（発行依頼書がまだ無い申請は物件申請情報の範囲で見る）と pbi design § セキュリティ上の考慮（自社の契約稟議起案会社か本人の登録）に一致し、問題は実在しない |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 3 | 1 | feature:contract-info-import | 4 | system（自動）：再検査で再検出なし | 2026-10-08T18:29:40+09:00 |
| feature:contract-info-import | 3 | 2 | feature:contract-info-import | 4 | system（自動）：再検査で再検出なし | 2026-10-08T18:29:40+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:contract-info-import | 4 | specs/contract-info-import/design.md | Junichi Noumi | 2026-10-08T18:33:40+09:00 | 4c8a75122096a3b0e11bc9879722b86ecf6a395fe1f145a45958d88a0f58b135 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 1 | 2026-10-08T18:54:39+09:00 | ①② | ["specs/contract-info-download/design.md"] | {"specs/contract-info-download/design.md":"1d5832b573e08c385d822a5ed5ae119e609e0ee8f50fb0bc1ff9d9079fb592de"} | 6 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | format-conformance | 書式 | 軽微 | 532b8712c103b71d | 16a07125ca65d310 | specs/contract-info-download/design.md § 変更する既存ファイル（Modified Files） | DSN_MODIFIED_FILE_N | 変更する既存ファイルのプレースホルダーが不要理由付きで残らず「なし」に置き換わっている | プレースホルダー削除。テンプレート（Templates/specs/_template/design.md 行368）は `- &lt;DSN_MODIFIED_FILE_N&gt; — &lt;DSN_MODIFIED_REASON_N&gt;`。本書 行532 は「- なし（メッセージを足さず、CSRF の照合設定も変えない。Q-DS-CD-008 の 1・Q-DS-CD-010 の 3）」で、プレースホルダーが値にも不要理由付きの残置にもなっていない（status-protocol §7 の保持の規約）。同じ節を承認済みの specs/contract-info-import/design.md 行557 は `&lt;DSN_MODIFIED_FILE_N&gt;（不要：…） — &lt;DSN_MODIFIED_REASON_N&gt;（不要：同上）` の形で残している。本書のほかの不要箇所（行137・267・338・379・577・578・601〜605・628）はプレースホルダーを残して不要理由を併記している | 行532 を「- &lt;DSN_MODIFIED_FILE_N&gt;（不要：既存のファイルは変えない。メッセージを足さず、CSRF の照合設定も変えない — Q-DS-CD-008 の 1・Q-DS-CD-010 の 3） — &lt;DSN_MODIFIED_REASON_N&gt;（不要：同上）」に置き換える | 修正：書式だけの直しで内容は変わらないため | 確認済み |  |  |
| 2 | traceability | 業務のあいまい・不足 | 要判断 | 88beb5f8cc15dd47 | 57a32d5dd78ab1cf | specs/contract-info-download/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 3.1 | CSV の列の並び（@CsvColumn） | CSV の列位置を name だけで決め、同じ見出しの No6・No44 の位置が定まらない | 意味判定（ID 対応あり・内容の確定不足）。要件 3.1 は「契約情報取込のリバースデータと同じ 381 列の形式」を求め、列の並びは取込にそのまま効く。本書 § データ契約と外部連携 の CSV（行291）は「381 列に @CsvColumn(name = 見出し) を付け … 見出し行は CsvEntityListHandler が @CsvColumn(name=…) から出す」とだけ書き、列の位置（position）を指定していない。§ ドメインモデル の CSV（行252）と出力の定義（specs/contract-info-download/csv-layout-wtg100.md の「注意」）は、No 6 と No 44 が同じ見出し「契約基本_基地局名_ｶﾅ」になるとする。名前で列を決める書き方では、同じ名前の 2 列が同じ位置に解決されるか、フィールドの宣言順（Java の仕様では getDeclaredFields の順は保証されない）に頼るおそれがあり、No 1〜381 の並びと No 6・No 44 の値の位置が本書から一意に決まらない。§ テスト戦略 の単体の CSV（行620）も見出しの並びだけを確かめ、値の位置を確かめる記述が無い | § データ契約と外部連携 の CSV に「381 列すべてに @CsvColumn(position = 出力の定義の No − 1, name = 見出し) を付け、列の並びを出力の定義の No で固定する。No 6 と No 44 は position で区別する」を足す。§ テスト戦略 の単体の CSV に「No 6 に基地局名_ｶﾅ、No 44 に予備項目3 の値が出る」を足す | 修正：業務の新しい事実は要らず、出力の定義の No をそのまま使えば列の並びが一意に決まるため | 確認済み |  |  |
| 3 | traceability | 業務のあいまい・不足 | 要判断 | b3dd83ebfd553849 | 6853f8ae7813a6ba | specs/contract-info-download/design.md § 契約情報ダウンロード Service / 出力の手順 4 | 作業用テーブルの会社の分け方 | ビューと作業用テーブルに会社コードが無く、他社の契約者・支払の行が入りうる | 本書 出力の手順 4（行415）「VWTGM010 から、選んだ行（計画基地局番号＋枝番）の 1基本情報・2契約者・3支払情報の行を全部 TWTGD050 に入れる … 選んだ行がログイン会社の TWTGM010 にあり … 合うものだけを入れる」。作業用テーブルの表（specs/contract-info-download/work-tables-wtg100.md 行26〜28・行32〜95）では、VWTGM010 の 1基本情報は「TWTGM010 の全行」で、VWTGM010 と TWTGD050（60 列）の列に会社コードが無い。このため、キーがログイン会社の TWTGM010 にあることは確かめられても、同じ計画基地局番号＋枝番を持つ他社の行（基本・契約者・支払）も VWTGM010 から TWTGD050 に入りうる。要件 3.1（選んだ行だけを出す）、本書 § セキュリティ上の考慮（行548「送られたキーをログイン会社の TWTGM010 と同じ絞り込みで確かめ直し」）、steering/database.md 行117（会社コードを検索条件に含め、会社ごとのデータを混ぜない）に照らすと、会社が複数ある場合の扱いが本書から決まらない。一方、ビューのコード名称は会社コード 'UQ' 固定で引く（本書 行278、csv-layout-wtg100.md 行18）ため、運用上の会社が 1 つだけである可能性もある。作業用テーブルが共通列（会社コードを含む）を持たないこと自体は回答（Q-DS-CD-002 の 2）で決まっており、ここでは指摘しない | 何を決めるか：会社が複数ある場合に、作業用テーブルへ他社の行が入らないことをどう保つか。案 A：契約情報の会社は 'UQ' だけなので扱わない、と出力の手順 4 に明記する。案 B：VWTGM010 に会社コードの列を足し（作業用テーブルの列は変えない）、TWTGD050 へ入れる条件に「会社コード＝ログイン会社」を足す。案 C：TWTGD050・TWTGD060 にも会社コードを持たせる（回答の表を変える） | 質問：ビューと作業用テーブルの列は回答者の表が正で、会社の扱いには業務・運用の事実が要るため | 確認済み |  |  |
| 4 | steering-conformance | 業務の欠落・矛盾 | 重大 | bc3b89379160250c | ff4e37fd961bbceb | specs/contract-info-download/design.md § バリデーション設計 | サーバーでの入力チェック | サーバーで検索条件の桁・形式を確かめない設計が security.md の入力検証と矛盾し、逸脱の記録が無い | 矛盾。本書 § バリデーション設計（行466〜468）「サーバーで行う入力チェックは、出力のときの未選択チェックだけ」「検索条件の桁は画面の入力桁（maxlength）と IME の入力モードで … 形式は確かめない」。steering/security.md `### 入り口 — 入力検証` の画面の層「必須・桁数・形式の入力チェックを行い、エラー時はメッセージを表示して処理を止める（REQ-063）／Service の checkXxx が BindingResult.rejectValue に…」、同 `### 共通ルール` 1「入力はサーバー側で必ず検査する」、steering/architecture.md `### フロントエンド（FE）` のしないこと「業務ルールの判定（サーバ側のインターセプタと Service が行う）」と両立しない。本書が意図した逸脱として記録しているのは requirements 4.1 だけ（行468）で、§ アーキテクチャ方式と境界図 の steering との整合（行160）にも、upstream-carryover（.aidd/.engine/upstream-carryover.md 行75〜80 の contract-info-download の節）にも、security.md の入力検証からの逸脱が無い。サーバーで確かめない扱いそのものは回答（Q-DS-CD-005）で決まっているため、指摘は steering からの逸脱の記録の欠落に限る | § バリデーション設計 の 3 つ目の項目に「steering/security.md の `### 入り口 — 入力検証`（画面の層の桁数・形式のチェック）と `### 共通ルール` 1（入力はサーバー側で必ず検査する）からも意図して外れる。上流は Phase 5 の最後にまとめて直す（upstream-carryover）」を足し、upstream-carryover の contract-info-download の節に同じ行を足す | 修正：回答で決まった扱いを、ほかの意図した逸脱と同じ形で記録すれば足りるため | 確認済み |  |  |
| 5 | evidence-guard | 業務のあいまい・不足 | 要判断 | 9ec3494394fffbe2 | 1d2059daea8caa0f | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 一覧の 19 項目 | 契約先の 7 項目の取り方 | 一覧の契約先 7 項目を GWTG004 と同じ取り方とするが、GWTG004 が検索条件で絞る手順を書いていない | 根拠の飛躍。本書 行242「『契約先/…』の 7 項目は GWTG004 と同じ取り方で、その契約の契約者情報のうち契約者区分 1 の行を、契約者番号の降順で並べた先頭の 1 行から取る（Pwtgo004Mapper.xml:769〜:793、Pwtgo004Service.java:410〜:413）」。挙げた GWTG004 のコードは、まず検索条件の法人名/個人名・法人名/個人名(ｶﾅ)・所属部署名・電話番号を条件に契約者区分 1 の行を引き（wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg002/service/Pwtgo004Service.java:404〜:419、wing/src/main/resources/jp/co/kccs/wt/function/wtg/wtg002/Pwtgo004Mapper.xml:823〜:836）、当たらないときだけ条件を外して引き直す（同 Service:433〜:460）。このため、法人名で検索したとき GWTG004 は条件に合う契約者を契約先として出すが、本書の書き方では条件に合わない契約者が出ることがある。回答（Q-DS-CD-003）は「GWTG004 と同じ取り方です（Pwtgo004Service の契約者の整理）」と「契約者区分 1 の行のうち、契約者番号の降順で先頭の 1 行」の両方を述べており、どちらに寄せるかが本書から決まらない。なお GWTG004 は Service:408 で法人名の条件をカナの値で上書きし、Mapper:824 で法人名を完全一致で比べる | 何を決めるか：一覧の契約先 7 項目に検索条件を効かせるか。案 A：GWTG004 と同じく、検索条件の法人名/個人名・カナなどで契約者区分 1 の行を絞って先頭を出し、当たらなければ条件を外した先頭を出す（比べ方を検索条件と同じ部分一致にするか、GWTG004 のとおりにするかも決める）。案 B：検索条件に関係なく、契約者区分 1 の行を契約者番号の降順で並べた先頭を出す（本書のまま。出典の「GWTG004 と同じ取り方」を「GWTG004 と同じ並び」に直す） | 質問：回答の 2 つの記述が食い違い、どちらにするかは業務の判断が要るため | 確認済み |  |  |
| 6 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | cafadf062ea1589e | 9387e2a397cd7816 | specs/contract-info-download/design.md § API 契約（API Contract） / /wtg100 | /wtg100 の申請No の受け渡し | /wtg100 の申請No のパラメータ名が無く、pbi design の口も FunctionID を渡さない | 本書 API 契約の `/wtg100` の Request（行367）は「FunctionID、申請No」で、申請No の要求パラメータ名を書いていない。§ データ契約と外部連携 の物件基本情報登録変更との口（行289）も「/wtg100?FunctionID=WTG100 に申請No を足して」とだけ書く。依存先の公開契約 specs/property-basic-info/design.md 行566（API 契約 `/wtg070/keyakuDl`：契約情報ダウンロード画面（GWTG100）を別ウインドウで開く）と行576（「/wtg100 を別ウインドウで開き、申請No だけを渡す（14.14）」）は FunctionID を渡す形になっておらず、パラメータ名も無い。既存の GWTG004 の初期表示は @RequestParam("FunctionID") を必須で受ける（wing/src/main/java/jp/co/kccs/wt/function/wtg/wtg002/controller/Pwtgo004Controller.java:76）ため、同じ作りで pbi design のとおりに開くと FunctionID が無く初期表示できない。FunctionID を渡す口の形は回答（Q-DS-CD-008 の 1）で決まっているが、本書・依存先の両方で受け渡しの名前が決まっていない | § API 契約 の `/wtg100` の Request に申請No のパラメータ名と、FunctionID＝`WTG100` を受けることを書き、§ データ契約と外部連携 の物件基本情報登録変更との口に同じ名前を書く。pbi design 行576 の「申請No だけを渡す」に FunctionID とパラメータ名を足すことを upstream-carryover（全機能をまたいだ確認）に記録する | 修正：口の形は回答で決まっており、名前を決めて両方の design にそろえれば足りるため | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 4 | steering/security.md（`### 入り口 — 入力検証`・`### 共通ルール` 1。Phase 5 の最後にまとめて直す upstream-carryover） | 回答で決まったサーバーで桁・形式を確かめない扱いと steering の記述が両立しないため |
| 6 | specs/property-basic-info/design.md（`/wtg070/keyakuDl` の口。14.14） | 依存先の公開契約が FunctionID とパラメータ名を持たず、本書の口と合わないため |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| format-conformance | specs/contract-info-download/design.md § 変更する既存ファイル（Modified Files） | 形式不備のため意味検査から外した | unchecked:形式不備 |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 1.3 | 代表契約局番・代表契約枝番を前方一致にし、requirements 1.3（GWTG004 と同じ）から外れる | answer:design-authoring-generate[contract-info-download] |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 2.1・2.2 | requirements の「計画マスタ（TWTBM080）」を工事案件マスタとして読み、行が無い契約情報を出す | answer:design-authoring-generate[contract-info-download] |
| traceability | specs/contract-info-download/design.md § バリデーション設計 / 4.1 | 検索条件の桁・形式のサーバーチェックとメッセージを持たず、requirements 4.1 から外れる | answer:design-authoring-generate[contract-info-download] |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 3.4 | 出力は表示中のページで選んだ行だけ（1 ページ 100 件まで）で、100 件を超えて 1 つの CSV にできない | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § 判断 3: 工事案件マスタに行が無い契約情報は絞り込みで落とさない | 工事案件マスタに行が無い契約情報を出す点が security.md 285 行目の「既存の WTB と同じ方式」から外れる | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） | TWTGD050・TWTGD060 が共通列・主キー・索引を持たず database.md の共通カラムと合わない | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § セキュリティ上の考慮（Security Considerations） | 渡された申請No の申請で画面を使えるかを確かめず、社外ユーザーの範囲も当てない | answer:design-authoring-generate[contract-info-download] |
| evidence-guard | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 一覧の 19 項目 | 一覧の並びに GWTG004 の ORDER BY にある支払内容区分・口座番号を含めない | answer:design-authoring-generate[contract-info-download] |
| evidence-guard | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） | ビューのコード名称をログイン会社でなく会社コード 'UQ' 固定で引く | answer:design-authoring-generate[contract-info-download] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-download | 1 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-08T19:05:40+09:00 |  |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-download | 1 | 4 | 修正 | AI 推奨を採用: 回答で決まった扱いを、ほかの意図した逸脱と同じ形で記録すれば足りるため | Junichi Noumi | 2026-10-08T19:14:44+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-download | 1 | 6 | 修正 | 申請No のパラメータ名は applicationNo | Junichi Noumi | 2026-10-08T19:14:48+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-download | 1 | 2 | 修正 | AI 推奨を採用: 業務の新しい事実は要らず、出力の定義の No をそのまま使えば列の並びが一意に決まるため | Junichi Noumi | 2026-10-08T19:14:51+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 1 | 3 | 修正 | 修正案の A。契約情報の会社は 'UQ' だけなので扱わない（ビューのコード名称を 'UQ' で引くのと同じ前提） | Junichi Noumi | 2026-10-08T19:14:55+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 1 | 5 | 修正 | 修正案の A。検索条件のうち契約者に掛かるもの（契約者番号＝前方一致、法人名/個人名・法人名/個人名(ｶﾅ)＝部分一致。入力があるものだけ）で契約者区分 1 の行を絞り、契約者番号の降順で先頭を出す。当たらなければ条件を外して先頭を出す。比べ方は検索条件と同じにし、GWTG004 の「法人名をカナで上書き」「法人名を完全一致」はまねしない | Junichi Noumi | 2026-10-08T19:15:31+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 2 | 2026-10-08T19:25:21+09:00 | ①② | ["specs/contract-info-download/design.md"] | {"specs/contract-info-download/design.md":"0d7083da44e16a6ffc3907fce0db8953f3544f28ffb68eed21db05de0c8f3d8a"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務のあいまい・不足 | 要判断 | d8ed44f353086c85 | 3446b3df3d01f0fa | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） / VWTGM010 | 住居_字_地番・住居_建物_ビルの元の列 | ビューの元にする表が、住居の字地番・建物ビルを TWTGM010 に無い ADDRESS_CD3・CD4 から取る | 意味判定（要件 3.1。ID 対応あり・内容の確定不足）。本書 § 物理データモデル の VWTGM010（行278）は「列はデータ種別ごとに意味が変わり、作業用テーブルの表のとおり」とし、§ ファイル配置計画（行525）と § 移行方針（行574）はビューの DDL をその表をもとに作るとする。作業用テーブルの表（specs/contract-info-download/work-tables-wtg100.md 行117・118）の 1基本情報は No 17「住居_字_地番 ← 契約基本情報ﾏｽﾀ.ADDRESS_CD3」、No 18「住居_建物_ビル ← 契約基本情報ﾏｽﾀ.ADDRESS_CD4」で、出力の定義（specs/contract-info-download/csv-layout-wtg100.md 行43・44、No 15・16）の取得元も同じ列を挙げる。既存の TWTGM010 の列は ADDRESS3・ADDRESS4 で（wing/src/main/resources/jp/co/kccs/wt/function/wtg/wtg002/Pwtgo005Mapper.xml:435〜:436 の UPDATE、Pwtgo004Mapper.xml:429・:434）、ADDRESS_CD3・ADDRESS_CD4 は wing の wtg の Mapper に 1 か所も無い。本書自身も一覧の 10・11（行231・232）と検索条件の建物、ﾋﾞﾙ（行202）で TWTGM010.ADDRESS3・ADDRESS4 を使い、出力の定義の TWTGD060 の物理名も ADDRESS3・ADDRESS4 である。表の「処理順_帳票用」の欄の食い違いは本書が注記で読み替えを決めている（行278）が、この 2 列には注記が無く、表のとおりにビューの DDL を作ると存在しない列を参照し、CSV の No 15・16 の値を作れない | § 物理データモデル の VWTGM010 の行に「作業用テーブルの表の 1基本情報の住居_字_地番・住居_建物_ビルの元（契約基本情報ﾏｽﾀ.ADDRESS_CD3・ADDRESS_CD4）は、TWTGM010 の ADDRESS3・ADDRESS4 と読む（出力の定義の TWTGD060 の物理名と同じ）」を足す | 修正：出力の定義の物理名と既存の列名から読み替えが一意に決まり、業務の新しい事実は要らないため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 1.3 | 代表契約局番・代表契約枝番を前方一致にし、requirements 1.3（GWTG004 と同じ）から外れる | answer:design-authoring-generate[contract-info-download] |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 2.1・2.2 | requirements の「計画マスタ（TWTBM080）」を工事案件マスタとして読み、行が無い契約情報を出す | answer:design-authoring-generate[contract-info-download] |
| traceability | specs/contract-info-download/design.md § バリデーション設計 / 4.1 | 検索条件の桁・形式のサーバーチェックとメッセージを持たず、requirements 4.1 から外れる | answer:design-authoring-generate[contract-info-download] |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 3.4 | 出力は表示中のページで選んだ行だけ（1 ページ 100 件まで）で、100 件を超えて 1 つの CSV にできない | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § バリデーション設計 | サーバーで検索条件の桁・形式を確かめず、security.md の入力検証から外れる（逸脱は記録済み） | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § 判断 3: 工事案件マスタに行が無い契約情報は絞り込みで落とさない | 工事案件マスタに行が無い契約情報を出す点が security.md 285 行目の「既存の WTB と同じ方式」から外れる | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § API 契約（API Contract） / /wtg100/csv | 作業用テーブルを書く出力の口が CSRF の照合に乗らない（照合の設定を変えない） | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） | TWTGD050・TWTGD060 が共通列・主キー・索引を持たず database.md の共通カラムと合わない | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § セキュリティ上の考慮（Security Considerations） | 渡された申請No の申請で画面を使えるかを確かめず、社外ユーザーの範囲も当てない | answer:design-authoring-generate[contract-info-download] |
| evidence-guard | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 一覧の 19 項目 | 一覧の並びに GWTG004 の ORDER BY にある支払内容区分・口座番号を含めない | answer:design-authoring-generate[contract-info-download] |
| evidence-guard | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / ベンダー／施工会社の絞り込み | 工事案件マスタへ計画マスタを経由して会社コードで結合し、既存の WTB（TWTBM080 を直接引く）と結合の形が違う | answer:design-authoring-generate[contract-info-download] |
| evidence-guard | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） | ビューのコード名称をログイン会社でなく会社コード 'UQ' 固定で引く | answer:design-authoring-generate[contract-info-download] |
| evidence-guard | specs/contract-info-download/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / CSV | 0 件のとき空の要素を 1 つ渡して見出し行だけを出す（申請状況検索一覧は null の要素 1 つ） | answer:design-authoring-generate[contract-info-download] |
| evidence-guard | specs/contract-info-download/design.md § セキュリティ上の考慮（Security Considerations） / ZMENUAUTH | ZMENUAUTH の行を、物件基本情報登録変更を使える権限区分と同じ数だけ足す | answer:design-authoring-generate[contract-info-download] |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 1 | 1 | feature:contract-info-download | 2 | system（自動）：再検査で再検出なし | 2026-10-08T19:33:18+09:00 |
| feature:contract-info-download | 1 | 2 | feature:contract-info-download | 2 | system（自動）：再検査で再検出なし | 2026-10-08T19:33:18+09:00 |
| feature:contract-info-download | 1 | 3 | feature:contract-info-download | 2 | system（自動）：再検査で再検出なし | 2026-10-08T19:33:18+09:00 |
| feature:contract-info-download | 1 | 4 | feature:contract-info-download | 2 | system（自動）：再検査で再検出なし | 2026-10-08T19:33:18+09:00 |
| feature:contract-info-download | 1 | 5 | feature:contract-info-download | 2 | system（自動）：再検査で再検出なし | 2026-10-08T19:33:18+09:00 |
| feature:contract-info-download | 1 | 6 | feature:contract-info-download | 2 | system（自動）：再検査で再検出なし | 2026-10-08T19:33:18+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-download | 2 | 1 | 修正 | 。_handoff の 2 ファイルも直して差し替えました。ADDRESS_CD3・ADDRESS_CD4 はどちらも ADDRESS3・ADDRESS4 に直しています（CSV の表の No 15・16、作業用テーブルの表の 17・18）。読み替えの文は足さず、表どおり ADDRESS3・ADDRESS4 と書いてください。FEE_MANAGE_KIND は、使わない「処理順_帳票用」の式の中だけなので、そのままで構いません | Junichi Noumi | 2026-10-08T19:51:45+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 3 | 2026-10-08T19:54:37+09:00 | ①② | ["specs/contract-info-download/design.md"] | {"specs/contract-info-download/design.md":"3babb9106f4ffd54b78ce57c1b82ca8b530200d4dd20fe1ced3223ac96066233"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 2 | 1 | feature:contract-info-download | 3 | system（自動）：再検査で再検出なし | 2026-10-08T19:58:17+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:contract-info-download | 3 | specs/contract-info-download/design.md | Junichi Noumi | 2026-10-08T20:00:35+09:00 | 3babb9106f4ffd54b78ce57c1b82ca8b530200d4dd20fe1ced3223ac96066233 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| cross | 1 | 2026-10-08T20:04:01+09:00 | ② | ["specs/property-basic-info/design.md","specs/issue-request/design.md","specs/issue-request-tutorial/design.md","specs/print-report/design.md","specs/application-status-search/design.md","specs/contract-info-import/design.md","specs/contract-info-download/design.md"] | {"specs/property-basic-info/design.md":"0829e28f5d3a4e0db44e191b174e2518eb0af483f10814026003e86d90d8c7df","specs/issue-request/design.md":"a543916db8517b94bdbefb90769055130c7b2e00eeb99f9027bf9f66402a5d63","specs/issue-request-tutorial/design.md":"c7f8713531fc963780c2491a50671b52e4cf15f36cb990cd416b9352b2d8c831","specs/print-report/design.md":"0290e7db58d30e25be4cb376978f5783a22fdb69718de5ba0c38ad157aad2f80","specs/application-status-search/design.md":"4644f42d210af2d852c7456f3387ac7540ec0fee02a5a0909a66dab3b7ca9b39","specs/contract-info-import/design.md":"4c8a75122096a3b0e11bc9879722b86ecf6a395fe1f145a45958d88a0f58b135","specs/contract-info-download/design.md":"3babb9106f4ffd54b78ce57c1b82ca8b530200d4dd20fe1ced3223ac96066233"} | 9 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ssot-consistency | 業務の欠落・矛盾 | 重大 | 4af627819b5fa3fe | dff0f16b070e29b6 | specs/contract-info-download/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 契約情報取込との口 ほか 1 か所 | リバースデータ 381 列の値の形 | 契約情報DLの381列のうちコードの列の値が、取込側の検査（名称で照合）と合わない | 【列の並び（回答者が求めた確認）】specs/contract-info-download/csv-layout-wtg100.md と、ci design が正とする _handoff/phase5-contract-info-import-reverse-381.md の No 1〜381 の項目名を突き合わせ、並びは全列で一致した。見出しの文字の違いは No 17・23・64・91・118・145・172（ｶﾅ と カナ）と No 44（予備項目3 の見出しが「契約基本_基地局名_ｶﾅ」）だけで、ci design は「見出しの文字は見ない」（§ドメインモデル ファイルの形）ので並びの問題は無い。&#10;【値の形の食い違い】CD design §ドメインモデル CSV「値はすべて文字列。日付は出力の定義で YYYY/MM/DD にしている列だけをその形で出し、ほかの列は元の値のまま」。csv-layout の取得元は No 48 契約者①_契約者区分＝CONSTRACT_KBN（1:契約者、2:関係者）、No 50 法人_個人区分＝CORP_PRIV_KBN（1:法人、2:個人）、No 35 受電方法＝ELECT_KIND（1:電力会社直受…）、No 197 支払情報①_消費税扱い＝TAX_KIND（名称は No 198）。取込側の検査表（_handoff/phase5-contract-info-import-checks.md 2-3）は、No 10 系 契約者区分「"契約者"または"関係者"以外の場合ｴﾗｰ」（WTG-200008）、No 11 系 法人_個人区分＝(4) P06 の名称で照合、No 9 受電方法＝(3) P43 の名称で照合、No 32 系 消費税扱い＝(10) P10 の名称で照合（WTG-000072）。コードのまま出すと取込の区分3 でエラーになり全件取り消しになるおそれがあり、CD の目的「選んだ行を契約情報取込にそのまま使える 381 列の CSV」（§概要）と食い違う。取込側の中でも、対応表（_handoff/phase5-contract-info-import-mapping.md No 177 ほか）は消費税扱いをコードのまま税区分へ入れるとしており、検査表と対応表が食い違う。 | 何を決めればよいか：契約者①〜⑤_契約者区分・法人_個人区分、契約基本_受電方法、支払情報①〜④_消費税扱いの値を、コードと名称のどちらで受け渡すか。案A：VWTGM010 でこれらを名称（"契約者"／"関係者"、P06・P43 の名称）にして出し、消費税扱いは取込の検査をキー3（コード）での照合に直す。案B：CD はコードのまま出し、取込のリバースデータの検査（(3)(4)(10)・契約者区分の許可値）と対応表をコードでの照合・変換に直す。決めた側の design（CD の csv-layout の取得元、または ci が正とする検査表・対応表）に書く。 | 質問：取込ファイルの値の形をどちらに合わせるかは業務の決定で、回答者の判断が要るため | 確認済み |  |  |
| 2 | ssot-consistency | 業務の欠落・矛盾 | 重大 | f62888f61f945a6b | 2658968d8f53f618 | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 洗替と変更履歴の順 ほか 2 か所 | 洗替後の TWTGM100・TWTGM140 の排他用の値 | 取込が登録し直す発行依頼書・契約局の行の排他用の値が決まっておらず、発行依頼書画面の排他の前提と合わない | ir design §データ契約と外部連携 サービス間「画面の更新・一時保存は開いている TWTGM100・TWTGM140 の行の ExclusiveFG を照合し、取込が行を書き換えた後の古い画面からの更新を排他エラーにする（取込が書き換えた行の ExclusiveFG を新しい値にすることを前提にする）」。ir は TWTGM080 をロックも照合もしない（§状態管理 並行制御）。ci design §洗替と変更履歴の順 2・3 は TWTGM140・TWTGM100 を削除して登録し直すが、登録する行の ExclusiveFG の値を書いていない（6. で TWTGM080 にだけ「新しい排他用の値」を入れる）。ci §データ契約 サービス間と §取込バッチ 状態管理 並行制御は「取込の後、TWTGM080 の排他用の値が変わるので、取込の前に開いていた画面からの更新は排他エラーになる（pbi design）」とし、TWTGM080 を照合しない発行依頼書登録変更画面には当てはまらない。登録する行に値を入れない（NULL）と、取込の後に開いた画面からの照合も成り立たなくなるおそれがある。 | ci design §洗替と変更履歴の順 3. に「登録する TWTGM140・TWTGM100 の行の ExclusiveFG には新しいランダム値を入れる（発行依頼書登録変更画面の排他の前提。ir design のサービス間）」を足す。§データ契約 サービス間と §状態管理 並行制御の文を「物件基本情報登録変更は TWTGM080 の、発行依頼書登録変更は TWTGM100・TWTGM140 の排他用の値が変わるので、取込の前に開いていた画面からの更新は排他エラーになる」に直す。 | 修正：ir design が前提として明記した事項を ci design に書き足すだけで、業務の新しい事実は要らないため | 確認済み |  |  |
| 3 | ssot-consistency | 業務の欠落・矛盾 | 重大 | f49c875611067fe5 | c68162ff8af41143 | specs/property-basic-info/design.md § このスペックが持たない責務（Out of Boundary） / 契約情報取込 ほか 3 か所 | 取込による TWTGM080 の基地局番号ほかと単独複数局フラグの更新 | 取込がTWTGM080の基地局番号群と単独複数局ﾌﾗｸﾞを書き換えるが、持ち主のpbi designに書かれていない | ci design §このスペックが持つ責務「取込の終わりの基地局番号ほかと単独複数局フラグの更新（2.8・Q-DS-CI-005）」、§洗替と変更履歴の順 6.「TWTGM080 の計画基地局番号・計画基地局名・基地局番号・基地局名・基地局名(ｶﾅ)・エリアコードを入れ直し、単独複数局フラグ（データ行が 2 行以上なら "1"、1 行なら "0"）と新しい排他用の値を入れる」。TWTGM080 の持ち主の pbi design は、取込に任せる範囲を「取込中への状態の変更と契約局情報の洗替」とだけ書き（§このスペックが持たない責務）、境界図も「物件申請情報の状態を直接更新」だけ。§画面の項目「単独局か複数局か（14.1・14.8）：契約局の件数からは決めず、『複数局切替』『単独局切替』ボタンで選ぶ」、§画面に出さない列「計画基地局番号…エリアｺｰﾄﾞは『更新』のときに…設定する」としており、取込が件数で単独複数局フラグを決めることと基地局番号群を書き換えることが無い。ir design §このスペックが持たない責務も「TWTGM080 の基地局番号・基地局名・エリアコードを契約局情報の連番 1 にそろえること → pbi（Q-DS-IR-021）」とし、取込の書換えに触れていない。同じ列を 2 つの feature が別の規則で書く（所有の二重化）が、持ち主の側で整理されておらず、upstream-carryover の pbi design の項目にも無い。 | pbi design §このスペックが持たない責務の契約情報取込の行を「契約情報取込画面（GWTG090）と取込バッチ（取込中への状態の変更と戻し、契約局情報・発行依頼書の洗替、取込の終わりの TWTGM080 の計画基地局番号・計画基地局名・基地局番号・基地局名・基地局名(ｶﾅ)・エリアコード・単独複数局フラグ・排他用の値の更新を含む）→ specs/contract-info-import/design.md」に直す。§画面の項目の単独局か複数局かに「契約情報取込の後は、取込がデータ行の数で設定した値で表示する（ci design・ci requirements 2.8）」を足す。upstream-carryover の pbi design の項目に加える。 | 修正：承認済みの ci requirements 2.8 と ci design で決まっている内容を、持ち主の pbi design に書き足すだけのため | 確認済み |  |  |
| 4 | ssot-consistency | 業務の欠落・矛盾 | 重大 | 019af6a02c9711bd | 7399bb248ad30103 | specs/property-basic-info/design.md § 移行方針（Migration Strategy） / 移行対象ファイル一覧 ほか 5 か所 | ZMENUAUTH の PWTGO070・PWTGO080 の行 | 物件基本情報・発行依頼書のZMENUAUTHの行が定義されず、子画面の行の決め方も別々 | AccessControlInterceptor はセッションのメニューID と @FuncID で ZMENUAUTH を引き、行が無ければ拒否する（wing/src/main/java/jp/co/kccs/wt/common/interceptor/AccessControlInterceptor.java:45〜54）。pbi design と ir design の移行方針・移行対象ファイル一覧には PWTGO070・PWTGO080 の ZMENUAUTH の行が無い（AS design は PWTGO060 の行を移行に挙げている）。一方、子画面の行は親の登録を基準に書かれている：print-report「PWTGO072・PWTGO073 の行を物件基本情報登録変更を開くメニューの行に足す（メニューの数 × 2）」、cd「物件基本情報登録変更を開くメニューのメニューID と PWTGO100 の組を、物件基本情報登録変更を使える権限区分と同じ数だけ」、ci「PWTGO090 の行は GWTG070 と同じ会社とメニュー（GWTG070 と同じメニューの数）」、tutorial「PWTGO081 の行は PWTGO080 を登録するメニューと同じものすべて」。基準の「物件基本情報登録変更を開くメニュー」「PWTGO080 を登録するメニュー」はどの design にも定義が無く、数え方も「メニューの数」と「権限区分の数」でそろっていない。物件基本情報登録変更はメニュー［WTG070］から開くほか、申請状況一覧（［WTG060］のメニュー）から forward:/wtg070/pushApplicationNo で開く（pbi design §この画面を開く経路、AS design §API 契約）ので、セッションのメニューID が WTG060 のものになる経路でも PWTGO070 とその先の PWTGO072・073・080・081・090・100 の行が要る。 | 何を決めればよいか：PWTGO070 と PWTGO080 を登録するメニュー（［WTG070］物件契約情報登録と［WTG060］物件契約情報申請状況検索/一覧のメニューID。権限区分ごとにメニューが分かれるならそのすべて）。決めたら、pbi design の移行方針に「ZMENUAUTH：PWTGO070 の行を［WTG070］と［WTG060］のメニューに登録する」、ir design の移行方針に「ZMENUAUTH：PWTGO080 の行を PWTGO070 と同じメニューに登録する」を足し、print-report・cd・ci・tutorial の行の決め方を「PWTGO070 を登録するメニューすべて」にそろえる。 | 質問：どのメニュー（権限区分）に登録するかは発注者の運用で決まり、design からは決められないため | 確認済み |  |  |
| 5 | ssot-consistency | 業務のあいまい・不足 | 要判断 | b5e399ce0ef107c0 | 4e9c4f854a971cdf | steering/api-standards.md § エラーハンドリング（API 契約） / 共通エラー形式 ほか 4 か所 | 画面内 JSON の口のエラー形状 | 画面内でJSONを返す口が3 featureに増えたが、エラーの返し方の規約が無く形がそろわない | api-standards.md は「画面以外から呼ばれる API を設けない（回答 7）」として全節を不要とし、§共通エラー形式・§分類も不要。各 design の画面内の非同期の口：pbi /wtg070/inputHassoKiboDate（Errors なし。日付だけを返す）、ir /wtg080/calcTaxAdjustment・/wtg080/changeKeiyakuSyubetsuTutorial（Errors なし。計算できないときは税額そのまま・調整額空）、tutorial /wtg081/next（HTTP 200 で result（ok／error）と messages の配列。error のとき values・clear・next を返さない）。エラーを返す形を定めたのは tutorial だけで、ほかの口でサーバー側が失敗したとき（予期しない例外で ExceptionResolver がエラー画面を返すとき）に画面のスクリプトがどう扱うかは、どの design にも無い。upstream-carryover は api-standards.md について「画面内で JSON を返す口が増える（/wtg081/next、/wtg080/calcTaxAdjustment・/wtg080/changeKeiyakuSyubetsuTutorial）」だけを挙げ、エラーの形と pbi の /wtg070/inputHassoKiboDate は挙げていない。pbi design §データ契約と外部連携は「画面の要求は API 契約のフォーム送信だけ」としており、自身の非同期の口と合わない。 | 何を決めればよいか：画面内の JSON の口のエラーの返し方を steering に置くか。案A：api-standards.md を開き直すときに §共通エラー形式へ「画面内の JSON の口は HTTP 200 で result（ok／error）と messages（messages.properties の文言の配列）を返す。予期しない例外は既存の ExceptionResolver に任せ、スクリプトは失敗時に値を入れない」を置き、ir・pbi の口もこれに合わせる。案B：規約は置かず不要のままとし、各 design に口ごとの失敗時の扱いを書く。どちらでも upstream-carryover の api-standards.md の項目に /wtg070/inputHassoKiboDate を加え、pbi design §データ契約の「フォーム送信だけ」を直す。 | 質問：steering に規約を足すか（Phase 2 の開き直し）は回答者の判断が要るため | 確認済み |  |  |
| 6 | ssot-consistency | 業務の欠落・矛盾 | 重大 | 83bc4c1e4e4b5e0f | a9e28e65a11d6d47 | specs/property-basic-info/design.md § バリデーション設計 / 文書バーコード 書類種別 ほか 2 か所 | WTG-000072 | WTG-000072を物件基本情報は行番号なしの文言で、取込は行番号付きで使い形が食い違う | 既存の wing/src/main/resources/messages.properties:490 は「WTG-000072=行数[{0}]:{1}[{2}]:ｺｰﾄﾞﾏｽﾀに登録されていません」（行番号・項目名・値の 3 つの置換文字）。ci design は取込の区分3・警告でこの形のまま使う（検査表の置換文字 {0}：行数／{1}：項目名／{2}：値）。pbi design §バリデーション設計（文書バーコード 書類種別）・§文書バーコード サービスインターフェース generate・§API 契約 /wtg073/create は「WTG-000072（既存）／ｺｰﾄﾞﾏｽﾀに登録されていません」としてポップアップに出し、置換文字を決めていない。そのまま出すと「行数[]:…」の形で表示される。同じキーを 2 つの feature が別の形で使っている（正は既存の messages.properties）。 | 何を決めればよいか：文書バーコードの書類種別の誤りに出すキー。案A：WTG-000072 のまま、{0} を空、{1} に「書類種別」、{2} に選んだコードを入れると pbi design に書く。案B：行番号の無い既存の WTG-000029（{0}:ﾏｽﾀに存在しません）に替え、{0} に「書類種別」を入れる。案C：WTG-1000xx の帯に新しいキーを足す。 | 質問：画面に出すキーと文言は回答者が決める事項のため（pbi の他のメッセージも回答者の指定による） | 確認済み |  |  |
| 7 | ssot-consistency | 業務の欠落・矛盾 | 重大 | 03c48a9140c67b07 | c1d39a16c92a1369 | specs/property-basic-info/design.md § ドメインモデル（Domain Model） / 文書バーコードNo ほか 2 か所 | バーコードの契約区分の文字（P78） | 文書バーコードNoはP78の文字項目2、稟議バーコードNoは文字項目1で契約区分を表し食い違う | pbi design「文書バーコードNo ＝ 基地局番号＋"-"＋エリア接頭語＋受付No＋"-"＋契約区分＋書類種別コード＋件数。…契約区分は TWTGM100.Keiyaku_Kbn をキー3 にして WTG/PARAM/P78 を引いた文字項目2」（Q-DS-PBI-007。.aidd/.engine/answer-ds-pbi-20261007-1421-Q007.txt:30）。ir design「稟議バーコードNo：その契約局の基地局番号（枝番なし）＋"-"＋P34 の文字項目1＋受付No＋"-"＋契約区分をキー3 にした P78 の文字項目1（ｵｰﾌﾟﾝ 241／屋内 141／鉄道 341）。TWTGM100.Keiyaku_Kbn の値そのものでも、P78 の文字項目2 でもない」（Q-DS-IR-012）。ci design の稟議バーコードNo も文字項目1（ir design の 3.2 と同じ形）。文書バーコードNo の先頭は稟議バーコードNo と同じ並び（基地局番号-エリア接頭語＋受付No-契約区分）で、文書バーコードは稟議バーコードNo ごとに件数を振る（11.7）が、契約区分の部分だけ引く文字項目が違う。意図した違いか取り違えかが design から読み取れない。 | 何を決めればよいか：文書バーコードNo の契約区分の部分に P78 の文字項目1（241／141／341）と文字項目2 のどちらを使うか。案A：文字項目1 にそろえ、文書バーコードNo の先頭が稟議バーコードNo と一致するようにする（pbi design を直し、upstream-carryover の pbi design の項目に加える）。案B：文字項目2 のままとし、稟議バーコードNo と別の文字を使う理由を pbi design に書く。 | 質問：どちらの記述も回答者の回答に基づき、業務上の正しい値は回答者しか決められないため | 確認済み |  |  |
| 8 | ssot-consistency | 文書間の参照 | 軽微 | eee1ee888cb3f794 | 9f01921c05b45687 | specs/contract-info-import/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 物件基本情報登録変更との口 ほか 1 か所 | /wtg090/back の戻り先 | 取込画面の戻る（/wtg090/back）が送る物件基本情報登録変更の口が書かれていない | ci design §物件基本情報登録変更との口「戻るは /wtg090/back から物件基本情報登録変更画面を申請No で出し直す」、§API 契約 /wtg090/back「物件基本情報登録変更画面を申請No で出し直す」とあり、pbi design のどの口へ送るかが無い。pbi design の口は /wtg070（新規）・/wtg070/pushApplicationNo（申請状況一覧から申請No）・/wtg070/search・/wtg070/return（セッションの申請No。バッチ処理状況一覧から）で、物件基本情報登録変更 Controller の呼び出し元（Inbound）にも契約情報取込は無い。upstream-carryover の pbi design の項目は発行依頼書登録変更からの戻りの入口だけを挙げている。 | ci design の /wtg090/back を「セッションの申請No を付けて forward:/wtg070/pushApplicationNo へ送り、物件基本情報登録変更画面を出し直す」と書く。pbi design の物件基本情報登録変更 Controller の呼び出し元に「契約情報取込画面（/wtg090/back）— 戻り（重要度: 中）」を足す（upstream-carryover の pbi design の項目に加える）。 | 修正：既存の口を指定するだけで、業務の新しい事実は要らないため | 確認済み |  |  |
| 9 | ssot-consistency | 文書間の参照 | 軽微 | 38c36e3db826a92d | b5ec17b2034b8e18 | specs/application-status-search/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 物件基本情報登録変更との口 ほか 1 か所 | /wtg060/return の呼び出し元 | 取込の実行後に/wtg060/returnへ来る経路が、申請状況一覧のdesignで違って書かれている | ci design §API 契約 /wtg090/execute「タスクを登録して forward:/wtg060/return」、§アーキテクチャ方式と境界図（取込画面 Controller から申請状況検索一覧へ forward /wtg060/return）。AS design §データ契約と外部連携「物件基本情報登録変更画面（と契約局取込）の戻るは /wtg070/returnList から /wtg060/return に戻り」とし、取込画面の実行の後に直接 /wtg060/return へ来る経路を書いていない（取込画面の戻る /wtg090/back は物件基本情報登録変更へ戻る）。AS design §申請状況検索一覧 Controller の呼び出し元（Inbound）にも契約情報取込が無い。 | AS design §物件基本情報登録変更との口の「（と契約局取込）」を削り、「契約情報取込画面の実行（/wtg090/execute）の後も forward:/wtg060/return で戻り、セッションの条件で前に見ていたページを再検索する（未検索なら初期表示）」を足す。§申請状況検索一覧 Controller の呼び出し元に「契約情報取込画面（/wtg090/execute の後）— 戻り（重要度: 中）」を足す。 | 修正：ci design の確定した遷移に合わせて記述を直すだけのため | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 5 | Phase 2（steering/api-standards.md） | 画面内の JSON の口のエラーの返し方の規約が steering に無く、置くかどうかは steering の開き直しで決めるため |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| dependency-cycle-detection | specs/property-basic-info/design.md § データ契約と外部連携（Data Contracts &amp; Integration） | pbi→ir（TWTGM100 の読取り・削除・複製）と ir→pbi（WTG 申請状態サービス）の組は Phase 3 で扱った循環と同じ根本原因で、新しい閉路を構成しない | answer:feature-decomposition-generate[] |
| dependency-cycle-detection | specs/print-report/design.md § 依存してよい対象（Allowed Dependencies） | pbi 画面→/wtg072/search と print-report Service→pbi Service（6.9 の判定）の組。判定の置き場は回答で案A（pbi Service を呼ぶ）に決定済み | answer:design-authoring-generate[print-report] |
| dependency-cycle-detection | specs/*/design.md の API 契約（pbi と ci・pbi と AS・ir と tutorial） | 戻る・コールバックの遷移と function/wtg/common の共通部品への呼出しで、feature 間の閉路を構成しない | verify:画面の戻り・コールバックと WTG 共通部品への呼出しは feature 間の依存の辺にならない |
| steering-conformance | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） | 作業用テーブル TWTGD050・TWTGD060 が共通列を持たない（steering/database.md の共通カラム） | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/issue-request-tutorial/design.md § バリデーション設計 | 増額分賃料・消費電力の桁をサーバーで検査しない（steering/security.md の入力検証） | answer:design-authoring-generate[issue-request-tutorial] |
| steering-conformance | specs/application-status-search/design.md・specs/contract-info-import/design.md § 機能固有のエラー処理（Error Handling） | 画面の業務エラーを例外にせず BindingResult で返す（steering/tech.md の例外処理フロー） | verify:既決（upstream-carryover「tech.md：画面の業務エラー・排他は BindingResult で返してよい場合」） |
| steering-conformance | specs/contract-info-download/design.md § API 契約（API Contract） | /wtg100/csv が作業用テーブルを書くが CSRF の照合に乗らない（steering/security.md の攻撃対策） | verify:既決（upstream-carryover「security.md 攻撃対策：CSRF は末尾一致の対象だけを照合する」） |
| ssot-consistency | specs/property-basic-info/design.md § データ契約と外部連携・API 契約・バリデーション設計 | 出力 CSV の 228 列と取込の形、/wtg070/keyakuDl・/wtg072/search・/wtg070/returnList・発行依頼書登録変更との口、既存とした WTX-100005・WTX-100011・WTX-100012・WTG-100018 の他 feature との食い違い | verify:既決（upstream-carryover の pbi design の項目） |
| ssot-consistency | specs/issue-request/design.md § データ契約と外部連携（チュートリアル（GWTG081）との受け渡し） | チュートリアルとの受け渡し（json.clear・入れる順・入れる項目）の食い違い | verify:既決（upstream-carryover の ir design の項目） |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| cross | 1 | 1 | 修正 | 修正案の A。ビュー VWTGM010 で、契約者区分は「契約者」「関係者」、法人_個人区分は「法人」「個人」（P06 の名称と同じ）にして出す。受電方法は、予備項目4（YOBI_KOMOKU4）に値があればその値、空なら ELECT_KIND を「1:電力会社直受」「2:テナント受電」「3:ａｕ受電」の文字にして出す（予備項目4 が空の古い契約は、取込で WTG-000072 になる。利用者が CSV の受電方法を P43 の名称に直してから取り込む）。消費税扱いはコードのまま出し、取込のリバースデータの検査は ZM040 のキー3 で照合する。_handoff の csv-layout-wtg100.md・work-tables-wtg100.md・phase5-contract-info-import-checks.md を直して差し替えたので、両方の design に反映してください | Junichi Noumi | 2026-10-08T20:40:14+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 1 | 2 | 修正 | AI 推奨を採用: ir design が前提として明記した事項を ci design に書き足すだけで、業務の新しい事実は要らないため | Junichi Noumi | 2026-10-08T20:40:18+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 1 | 3 | 修正 | AI 推奨を採用: 承認済みの ci requirements 2.8 と ci design で決まっている内容を、持ち主の pbi design に書き足すだけのため | Junichi Noumi | 2026-10-08T20:40:22+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| cross | 1 | 4 | 修正 | 。PWTGO070・PWTGO080 は［WTG070］と［WTG060］のメニュー（権限区分ごとに分かれていれば、そのすべて）に登録する。子画面（072・073・081・090・100）は「PWTGO070 を登録するメニューすべてに、メニューID ごとに 1 行」にそろえる。投入の文と手順は各 feature の tasks で作り、投入は発注者が導入手順書に沿って行う | Junichi Noumi | 2026-10-08T20:40:26+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| cross | 1 | 5 | 修正 | 修正案の B | Junichi Noumi | 2026-10-08T20:40:30+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| cross | 1 | 6 | 修正 | 修正案の A | Junichi Noumi | 2026-10-08T20:40:33+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| cross | 1 | 7 | 修正 | 修正案の B。文書バーコードNo の契約区分は 1 桁（屋内 1・オープン 2・鉄道 3。P78 の文字項目2）で、稟議バーコードNo の 3 桁（文字項目1）とは別の決まりなので、文字項目2 のままとする。理由を物件基本情報の design に書く | Junichi Noumi | 2026-10-08T20:40:37+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 1 | 8 | 修正 | AI 推奨を採用: 既存の口を指定するだけで、業務の新しい事実は要らないため | Junichi Noumi | 2026-10-08T20:40:41+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 1 | 9 | 修正 | AI 推奨を採用: ci design の確定した遷移に合わせて記述を直すだけのため | Junichi Noumi | 2026-10-08T20:40:45+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 6 | 2026-10-08T20:47:56+09:00 | ①② | ["specs/property-basic-info/design.md"] | {"specs/property-basic-info/design.md":"8bf1b6e70ae1125231d30b793d1c166820906f3216ea6dd53688a5d8bd5f1805"} | 2 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | dependency-boundary-conformance | 文書間の参照 | 軽微 | f7f47595859a3059 | 4faaa8c31d7f8a71 | specs/property-basic-info/design.md § API 契約（API Contract） / `/wtg070/pushApplicationNo` ほか 1 か所 | /wtg090/back の戻り先 | 取込画面からの戻りの受け口 pushApplicationNo の Request と開く経路に、取込画面が無い | 横断確認 1 回目 #8 の修正で、物件基本情報登録変更 Controller の呼び出し元（Inbound）に「契約情報取込画面（`/wtg090/back`）— 戻り。セッションの申請No を付けて `forward:/wtg070/pushApplicationNo` で受ける（重要度: 中。横断確認 1 回目 #8）」（行524）が足された。一方、契約情報取込が依存する公開の口である API 契約の表の `/wtg070/pushApplicationNo` の行（行544）は Request を「申請No（申請状況一覧から）」のままとしている。`- **この画面を開く経路**`（行579）も「新規登録はメニュー…、既存の申請は、申請状況一覧（GWTG060）の申請No のリンクから…（`/wtg070/pushApplicationNo`）」だけを挙げ、契約情報取込画面からの戻りが無い。同じ design の中で、呼び出し元の記述と口の契約の記述がそろっていない（ci design §API 契約 `/wtg090/back` の「物件基本情報登録変更画面を申請No で出し直す」が使う口） | 行544 の Request を「申請No（申請状況一覧から。契約情報取込画面の戻る `/wtg090/back` からは、セッションの申請No を付けた forward で受ける）」に直す。行579 の「この画面を開く経路」に「契約情報取込画面の戻る（`/wtg090/back`）からは `forward:/wtg070/pushApplicationNo` で申請No を受けて開き直す（横断確認 1 回目 #8）」を足す | 修正：人の判断で決まった #8 の口を、同じ design の口の表と開く経路にそろえるだけで、業務の新しい事実は要らないため | 確認済み |  |  |
| 2 | dependency-boundary-conformance | 文書間の参照 | 軽微 | 9e6c49a89cd1ebed | 6f49f48b6f626167 | specs/property-basic-info/design.md § アーキテクチャ方式と境界図（Architecture Pattern &amp; Boundary Map） / 契約情報取込バッチ ほか 1 か所 | 取込による TWTGM080 の基地局番号ほかと単独複数局フラグの更新 | 境界図が取込バッチの TWTGM080 の書込みを「状態を直接更新」だけとし、持たない責務の記述と合わない | 横断確認 1 回目 #3 の修正で、§このスペックが持たない責務の契約情報取込の行（行84）は「取込バッチ（取込中への状態の変更と戻し、契約局情報・発行依頼書の洗替、取込の終わりの TWTGM080 の計画基地局番号・計画基地局名・基地局番号・基地局名・基地局名(ｶﾅ)・エリアコード・単独複数局フラグ・排他用の値の更新を含む）」に直り、§画面の項目の単独局か複数局か（行599）にも取込の後の表示が足された。一方、境界図（行163）は `BATCH[契約情報取込バッチ contract-info-import] -.物件申請情報の状態を直接更新.-&gt; DB` のままで、取込が TWTGM080 の基地局番号ほか・単独複数局フラグ・排他用の値を書き換えることが図から読めない。あわせて §画面に出さない列（行597）は計画基地局番号・計画基地局名・基地局名・基地局名(ｶﾅ)・エリアｺｰﾄﾞを設定する経路を「更新」と修正稟議・再製本の複製だけとし、取込による入れ直しに触れていない（ci design §洗替と変更履歴の順 6.）。横断確認 1 回目 #3 の指摘内容は境界図も挙げていたが、人が採用した修正案には含まれていなかった | 行163 のラベルを「物件申請情報の状態・基地局番号ほか・単独複数局フラグを直接更新」に直す。行597 の末尾に「契約情報取込の後は、取込が最初のデータ行の基地局番号で計画マスタを引いて入れ直した値になる（`### このスペックが持たない責務（Out of Boundary）`、ci design）」を足す | 修正：#3 で決まった取込の書込みの範囲を、同じ design の境界図と画面に出さない列にそろえるだけで、業務の新しい事実は要らないため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| steering-conformance | specs/property-basic-info/design.md § 技術スタック（Technology Stack） / Infrastructure / Runtime | 開発端末の JDK 1.8 と steering/tech.md の JDK 1.7 の矛盾 | verify:重複（前回 2-7 で人が対応せず進めると判断済み。upstream-carryover の steering tech.md の項目） |
| steering-conformance | specs/property-basic-info/design.md § ドメインモデル（Domain Model） / 依頼内容 | 依頼内容を名称の文字列で持つことと steering/database.md の矛盾 | verify:重複（前回 2-11 で人が対応せず進めると判断済み） |
| steering-conformance | specs/property-basic-info/design.md § 物理データモデル（Physical Data Model） / 判定・権限ID・連番ほか | 判定・権限ID をコードマスタにせず連番などを Int とすることと steering/database.md の矛盾 | verify:重複（前回 2-12 で人が対応せず進めると判断済み） |
| steering-conformance | specs/property-basic-info/design.md § セキュリティ上の考慮（Security Considerations） / 組織の判定 | P71 のキー3 の「グループ」を権限区分と読むことと steering/security.md の矛盾 | verify:重複（前回 2-13 で人が対応せず進めると判断済み） |
| evidence-guard | specs/property-basic-info/design.md § サービスインターフェース（Service Interface） / canOperate の処理状況 ほか 2 か所 | 処理状況（/wtg070/taskList・/wtg070/return）に受け入れ基準が無い | verify:重複（前回 3-4 で人が対応せず進めると判断済み。canOperate の根拠は指示どおり書き直されている） |
| traceability | specs/property-basic-info/design.md § 状態管理（State Management） / 稟議・修正稟議 起案済 01・回覧中 02 ほか 1 か所 | 起案済・回覧中の申請者の番で更新などを受け付けないことと requirements 1.3・6.7・14.5 の不整合 | verify:重複（前回 5-1 で人が対応せず進めると判断済み） |
| traceability | specs/property-basic-info/design.md § サービスインターフェース（Service Interface） / canOperate の契約局情報追加 | 契約局情報追加を複数局に限ることと requirements 14.5 の不整合 | verify:重複（前回 5-2 で人が対応せず進めると判断済み） |
| steering-conformance | specs/property-basic-info/design.md § アーキテクチャ方式と境界図（Architecture Pattern &amp; Boundary Map） / steering との整合 ほか 2 か所 | TWTGM170 の権限ID を P82 と別体系にすること（行173 の「TWTGM170・P82 だけで判定」の文を含む）と steering/security.md・requirements の前提の矛盾 | verify:重複（前回 5-3 で人が対応せず進めると判断済み。同じ原因） |
| steering-conformance | specs/property-basic-info/design.md § API 契約（API Contract） / 注記 ほか 2 か所 | CSRF の照合を servlet-context.xml の末尾一致の URL だけにすることと steering/security.md の食い違い | verify:重複（前回 3-3 の判断で design に意図した外れとして明記済み。upstream-carryover の steering security.md の項目） |
| steering-conformance | specs/property-basic-info/design.md § 機能固有エラーコード / 表の後の注記 | 業務エラー・排他を BindingResult で返すことと steering/tech.md の食い違い | verify:重複（前回 3-2 の判断で design に意図した外れとして明記済み。upstream-carryover の steering tech.md の項目） |
| dependency-boundary-conformance | specs/property-basic-info/design.md § ドメインモデル（Domain Model） / 申請No の採番 ほか 13 か所 | 依存する design・既存コードと合わない記述のうち、upstream-carryover.md「物件基本情報登録変更の design（承認済み。開き直して直す）」ほかに人が挙げたもの（MAX区分（行237）、発行依頼書登録変更への遷移の GET の値と戻りの入口（行576）、複製の TWTGM100 の申請者、recordNumbering の発番日時・更新者名・判定 11（行478）、WTX-100011・WTX-100012・WTX-100005 を既存とした記述（行708・713・925）、WTG-100018 を既存とした記述（行743）、/wtg072/search の入力（行571）、基地局番号の初期表示、getApplication の出力（行473）、getApplicantName、/wtg070/returnList の戻り先（行572）、CSV の「契約情報取込で読める形」（行391）、TWTGM110 を物理削除しない記述への取込の例外（行263・618）、/wtg100 の FunctionID・applicationNo（行577）） | verify:既知の食い違い（.aidd/.engine/upstream-carryover.md に人の判断で挙げ、Phase 5 の最後にまとめて直すと決めたもの。今回の修正の範囲（横断確認 1 回目 #3〜#8）の外） |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:property-basic-info | 6 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-08T20:52:29+09:00 |  |  |  |
| feature:property-basic-info | 6 | 2 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-08T20:52:29+09:00 |  |  |  |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 7 | 2026-10-09T12:20:42+09:00 | ①② | ["specs/property-basic-info/design.md"] | {"specs/property-basic-info/design.md":"03331555d6ee0825bd90f023f17f4951d532f97b0f4bde7b7f50878d4cc4da03"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| steering-conformance | specs/property-basic-info/design.md § アーキテクチャ方式と境界図（Architecture Pattern &amp; Boundary Map） / steering との整合 | TWTGM170 の権限ID を P82 と別体系にすること（行173 の「TWTGM170・P82 だけで判定」の文を含む）と steering/security.md・requirements の前提の矛盾 | verify:重複（前回 5-3 で人が対応せず進めると判断済み。今回の変更は行163 の境界図のラベルだけで、行173 は変わっていない） |
| steering-conformance | specs/property-basic-info/design.md § API 契約（API Contract） / 注記 | CSRF の照合を servlet-context.xml の末尾一致の URL だけにすることと steering/security.md の食い違い | verify:重複（前回 3-3 の判断で design に意図した外れとして明記済み。upstream-carryover の steering security.md の項目） |
| traceability | specs/property-basic-info/design.md § API 契約（API Contract） / `/wtg070/addKeyaku`・`/wtg070/henshu` | 起案済・回覧中の申請者の番の扱い・契約局情報追加を複数局に限ることと requirements 1.3・6.7・14.5 の不整合 | verify:重複（前回 5-1・5-2 で人が対応せず進めると判断済み） |
| dependency-boundary-conformance | specs/property-basic-info/design.md § API 契約（API Contract） / `/wtg072/search` ほか 3 か所 | 依存する design・既存コードと合わない記述のうち、upstream-carryover.md に人が挙げたもの（/wtg072/search の入力（行571）、/wtg070/returnList の戻り先（行572）、発行依頼書登録変更への遷移の値と戻りの入口（行576）、/wtg100 の FunctionID・applicationNo（行577）） | verify:既知の食い違い（.aidd/.engine/upstream-carryover.md に人の判断で挙げ、Phase 5 の最後にまとめて直すと決めたもの。今回の修正の範囲（6-1・6-2）の外） |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 6 | 1 | feature:property-basic-info | 7 | system（自動）：再検査で再検出なし | 2026-10-09T12:23:25+09:00 |
| feature:property-basic-info | 6 | 2 | feature:property-basic-info | 7 | system（自動）：再検査で再検出なし | 2026-10-09T12:23:25+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:property-basic-info | 7 | specs/property-basic-info/design.md | Junichi Noumi | 2026-10-09T12:25:37+09:00 | 03331555d6ee0825bd90f023f17f4951d532f97b0f4bde7b7f50878d4cc4da03 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 7 | 2026-10-09T12:30:38+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md":"441ecb00e6dd9f455e6d5dfbd0de9c9249c120a980a4eac8d38d5d2cd5659c2c"} | 2 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 文書間の参照 | 軽微 | 30e46cc005de5942 | 9f4d1747c39f7f26 | specs/issue-request/design.md § アーキテクチャ方式と境界図（Architecture Pattern &amp; Boundary Map） / steering との整合 | 画面内の非同期の口 | steeringとの整合の行が画面内の非同期の口を税額計算だけとし、契約種別による選択肢の口が抜けている | 今回の修正（横断確認 1 回目 #5）で、§ データ契約と外部連携（Data Contracts &amp; Integration）の API は「画面の要求は API 契約のフォーム送信と、画面内で値を返す非同期の口 /wtg080/calcTaxAdjustment（税額計算）・/wtg080/changeKeiyakuSyubetsuTutorial（契約種別による選択肢）だけ」となり、§ API 契約（API Contract）の 2 行にも失敗時の扱いが入った。§ 発行依頼書登録変更 Controller の呼び出し元（Inbound）も「税額計算・契約種別による選択肢の非同期の取得」と 2 つを挙げる。一方、§ アーキテクチャ方式と境界図 の「steering との整合」は「画面内の非同期の取得（税額計算）は、既存の画面内の JSON 取得と同じ扱いで、画面以外から呼ばれる API にしない（steering/api-standards.md の本プロジェクトでの扱い）」と税額計算だけを挙げ、/wtg080/changeKeiyakuSyubetsuTutorial が無い。repair の指示「非同期の口があることとそろえる」に対し、同じ文書の中で口の数の記述がそろっていない | § アーキテクチャ方式と境界図 の「steering との整合」の該当文を「画面内の非同期の取得（税額計算 `/wtg080/calcTaxAdjustment`、契約種別による選択肢 `/wtg080/changeKeiyakuSyubetsuTutorial`）は、既存の画面内の JSON 取得と同じ扱いで、画面以外から呼ばれる API にしない」に直す | 修正：同じ文書の中の記述をそろえるだけで、業務の新しい事実は要らないため | 確認済み |  |  |
| 2 | traceability | 文書間の参照 | 軽微 | 54b768f9c4e65964 | a01466b7c950ca84 | specs/issue-request/design.md § このスペックが持たない責務（Out of Boundary） / 発注者 | ZMENUAUTH の PWTGO080 の行 | 発注者に任せる投入の一覧にZMENUAUTHのPWTGO080の行が無く、移行方針と合わない | 今回の修正（横断確認 1 回目 #4）で、§ 移行方針（Migration Strategy）に「ZMENUAUTH：PWTGO080 の行を…メニューID ごとに 1 行登録する。投入の文と手順は tasks で作り、投入は発注者が導入手順書に沿って行う」、§ 移行対象ファイル一覧 に ZMENUAUTH（PWTGO080 の行）の行が入った。一方、§ このスペックが持たない責務（Out of Boundary）の発注者の行は「コードマスタ（TWTZM040）・採番マスタ（TWTZM050）の行と、TWTGM160・TWTZM370 の値の投入、記入例の中身 → 発注者（### 移行方針（Migration Strategy）…）」で、ZMENUAUTH の行の投入が無い。移行方針が委譲先として挙げるものと、責務境界の委譲の一覧が対応していない | § このスペックが持たない責務（Out of Boundary）の発注者の行を「コードマスタ（`TWTZM040`）・採番マスタ（`TWTZM050`）・メニュー権限（`ZMENUAUTH`。`PWTGO080` の行）の行と、`TWTGM160`・`TWTZM370` の値の投入、記入例の中身 → 発注者（`### 移行方針（Migration Strategy）`、Q-DS-IR-009・Q-DS-IR-010・Q-DS-IR-012、横断確認 1 回目 #4）」に直す | 修正：移行方針に書いた委譲先を責務境界の一覧にも載せるだけで、業務の新しい事実は要らないため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/issue-request/design.md § ドメインモデル（Domain Model） / 発番 ほか 2 か所 | 発番で担当エリア等を保存する扱いが要件1.3・1.5・9.3と食い違う | verify:既決（design-check 1 回目 #1・2 回目 #1 で「対応せず進める」と判断済み。upstream-carryover） |
| traceability | specs/issue-request/design.md § セキュリティ上の考慮（Security Considerations） / 2.1 | 2.1の本人が登録した発行依頼書を申請の登録者で比べており要件と食い違う | verify:既決（design-check 1 回目 #2 で「対応せず進める」と判断済み。upstream-carryover） |
| traceability | specs/issue-request/design.md § 発行依頼書登録変更 Service / 作成組織 | 8.1のログインユーザーのグループを権限区分と読み替えている | verify:既決（design-check 1 回目 #3・2 回目 #2 で「対応せず進める」と判断済み。upstream-carryover） |
| traceability | specs/issue-request/design.md § バリデーション設計 / 9.6 | 9.6の所属必須に「選んだ会社が社内」の条件を足している | verify:既決（design-check 1 回目 #4 で「対応せず進める」と判断済み。upstream-carryover） |
| traceability | specs/issue-request/design.md § サービスインターフェース（Service Interface） / 照合する行が無いときの扱い | 契約局情報追加を発行依頼書が登録済みの申請だけにしており1.9から外れる | verify:既決（design-check 4 回目 #1 の判断で決めた逸脱。upstream-carryover） |
| steering-conformance | specs/issue-request/design.md § 機能固有エラーコード ほか 2 か所 | 業務・排他エラーを例外にせずBindingResultに積む方式がtech.mdと食い違う | verify:既決（design-check 1 回目 #6・2 回目 #3 で「対応せず進める」と判断済み。upstream-carryover） |
| steering-conformance | specs/issue-request/design.md § 技術スタック（Technology Stack） / Infrastructure / Runtime | 開発端末のJDK 1.8がtech.mdの必須ツールJDK 1.7と食い違う | verify:既決（design-check 1 回目 #7 で「対応せず進める」と判断済み。upstream-carryover） |
| steering-conformance | specs/issue-request/design.md § セキュリティ上の考慮（Security Considerations） / CSRF ほか 1 か所 | 一時保存・発番がCSRFの照合に乗らずsecurity.mdの攻撃対策と食い違う | answer:design-authoring-generate[issue-request] |
| steering-conformance | specs/issue-request/design.md § 論理データモデル（Logical Data Model） / 属性と型 ほか 1 か所 | 金額・調整額を文字で持つ型と、トランの種別Vがdatabase.mdと食い違う | answer:design-authoring-generate[issue-request] |
| dependency-boundary-conformance | specs/issue-request/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 物件基本情報登録変更との口 ほか 1 か所 | pbi designの公開契約に無い前提（戻りの入口・発番日時・getApplicantName・複製の申請者・基地局番号の初期表示）に依存。今回の pbi design の変更でもこれらは追加されていない | verify:既決（design-check 1 回目 #8・2 回目 #4 で「対応せず進める」と判断済み。upstream-carryover） |
| dependency-boundary-conformance | specs/issue-request/design.md § このスペックが持たない責務（Out of Boundary） / 単独局と複数局の切替 ほか 1 か所 | pbi design が契約情報取込による TWTGM080 の基地局番号群・単独複数局ﾌﾗｸﾞの更新を明記したが、本書の委譲の行は pbi だけを挙げる。本書はこれらの列を書かず読むだけで、依存の前提は変わらない | verify:横断確認 1 回目 #3 で扱い済み（持ち主の pbi design・ci design の記述で整理され、本書への修正は指示されていない） |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 7 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T12:34:18+09:00 |  |  |  |
| feature:issue-request | 7 | 2 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T12:34:18+09:00 |  |  |  |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 8 | 2026-10-09T12:45:39+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md":"7bedc0d4618ebcb9a1667ce749bf24513272ac9c19fbdebdfe1ac2954ab67fbb"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 7 | 1 | feature:issue-request | 8 | system（自動）：再検査で再検出なし | 2026-10-09T12:47:48+09:00 |
| feature:issue-request | 7 | 2 | feature:issue-request | 8 | system（自動）：再検査で再検出なし | 2026-10-09T12:47:48+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:issue-request | 8 | specs/issue-request/design.md | Junichi Noumi | 2026-10-09T12:50:27+09:00 | 7bedc0d4618ebcb9a1667ce749bf24513272ac9c19fbdebdfe1ac2954ab67fbb |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 2 | 対応せず進める | AI 推奨を採用: 人の回答（Q-DS-IR-014）に従った読み方として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 8 |
| feature:issue-request | 1 | 4 | 対応せず進める | AI 推奨を採用: item-rules.md（回答者が渡した資料）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 8 |
| feature:issue-request | 1 | 7 | 対応せず進める | AI 推奨を採用: pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 8 |
| feature:issue-request | 1 | 8 | 対応せず進める | AI 推奨を採用: design に明記され、pbi design は Phase 5 の最後にまとめて直す方針とされているため。直すまでは pbi の実装がこの前提を満たさない | feature:issue-request | 8 |
| feature:issue-request | 2 | 1 | 対応せず進める | AI 推奨を採用: 人の回答（Q-DS-IR-001 の C）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため。ただし承認済み requirements と両立しない状態は残る | feature:issue-request | 8 |
| feature:issue-request | 2 | 2 | 対応せず進める | AI 推奨を採用: グループを権限区分と読むことは物件基本情報と 1 回目の判断で決まっており、上流の文言は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 8 |
| feature:issue-request | 2 | 3 | 対応せず進める | AI 推奨を採用: pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 8 |
| feature:issue-request | 2 | 4 | 対応せず進める | AI 推奨を採用: design に明記され、pbi design は Phase 5 の最後にまとめて直す方針とされているため。直すまでは pbi の実装がこの前提を満たさない | feature:issue-request | 8 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 3 | 2026-10-09T12:53:04+09:00 | ①② | ["specs/issue-request-tutorial/design.md"] | {"specs/issue-request-tutorial/design.md":"9525adb816abae13d2df2c81482d21aafc3768d27ea27618280a17b15fb1676b"} | 2 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | steering-conformance | 業務の欠落・矛盾 | 重大 | 8495912cc088b0e0 | 8386e642b72fcab9 | specs/issue-request-tutorial/design.md § 技術スタック（Technology Stack） / Infrastructure / Runtime | 開発端末の JDK | 開発端末のJDK 1.8がtech.mdの必須ツールJDK 1.7と食い違う | 矛盾。steering/tech.md `### 必須ツール` は JDK を「1.7（1.7.0.55）／コンパイルと実行（回答 6）」と定め、`## コアテクノロジ` も「1.7（実行環境の JDK は 1.7.0.55）」としているが、design の技術スタックは「開発端末の JDK 1.8（-source/-target 1.7）」を開発端末でのコンパイルと自動テストの実行に使うとしている。design 自身が「steering/tech.md から意図して外れる。上流は Phase 5 の最後にまとめて直す（upstream-carryover）」と書き、根拠を Q-DS-PBI-014（物件基本情報登録変更と同じ）としている。上流の入力が変わったため全体を検査した結果、前回（1 回目 #1、判断「対応せず進める」）と同じ事項が同じ節に残っている（節の内容は 1 回目から変わっていない） | steering/tech.md の `### 必須ツール` に「開発端末は JDK 1.8（-source/-target 1.7）でもよい」を足す（Phase 2 への差戻し、または upstream-carryover での一括修正） | 対応せず進める：pbi design・ir design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | 確認済み |  |  |
| 2 | traceability | 業務のあいまい・不足 | 要判断 | 466a8634bf2378b7 | adc1790ca99a7490 | specs/issue-request-tutorial/design.md § API 契約（API Contract） / 画面のスクリプトの動き ほか 1 か所 | /wtg081/next の失敗時の画面の扱い | /wtg081/nextが予期しない例外で失敗したときの別ウインドウのスクリプトの扱いが無い | 非機能方針の反映を上流→下流で突き合わせた（意味判定：方針の置き場は示されているが、本 feature の口の異常系が未充足）。steering/non-functional.md 冒頭の分担は「機能固有の復旧手順は design.md の ## 機能固有のエラー処理（Error Handling）」とし、steering/api-standards.md は全節不要（回答 7）で画面内 JSON の口のエラーの共通形を持たない。設計横断確認 1 回目 #5（画面内 JSON の口のエラー形状）の判断は「修正案の B」＝「規約は置かず不要のままとし、各 design に口ごとの失敗時の扱いを書く」（.aidd/gates/phase-5-design.md）。これを受けて pbi design §データ契約と外部連携（/wtg070/inputHassoKiboDate）と ir design §データ契約と外部連携・§API 契約（/wtg080/calcTaxAdjustment・/wtg080/changeKeiyakuSyubetsuTutorial）は「口が失敗したとき（予期しない例外で既存の ExceptionResolver がエラー画面を返すとき）、画面のスクリプトは…値を入れず、入力済みの値を変えない（横断確認 1 回目 #5）」を書いた。本書は §機能固有のエラー処理 の返し方で「予期しない例外は既存の ExceptionResolver に任せる」とするだけで、§API 契約 の画面のスクリプトの動きは「result が ok なら…、error なら…」の 2 通りしか書いていない。/wtg081/next が JSON でなくエラー画面を返したときに、スクリプトが親画面へ値を渡すか、画面を進めるか、状態（state）を持ち直すかが決まっていない。§エラー時の分岐フロー にもこの分岐が無い | §API 契約 の画面のスクリプトの動きに「`/wtg081/next` が失敗したとき（予期しない例外で既存の `ExceptionResolver` がエラー画面を返すとき）、スクリプトは親画面へ値を渡さず、画面を進めず、状態を変えない（横断確認 1 回目 #5。ir design・pbi design の口と同じ扱い）」を足し、§機能固有のエラー処理 の返し方にも同じ扱いを 1 文で足す | 修正：横断確認 1 回目 #5 の判断（口ごとに失敗時の扱いを書く）と、ir design・pbi design の同じ種類の口の扱いに合わせて書き足すだけで、業務の新しい事実は要らないため | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | 人間による確認（steering/tech.md の修正、または本 design の修正） | 開発端末の JDK（Q-DS-PBI-014 の回答）が steering の必須ツールと食い違っている。steering 側を直す場合は Phase 2 が宛先になる |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/issue-request-tutorial/design.md § ドメインモデル（Domain Model） / 画面と進む先 | 画面を 11 にし、RRH数・System構成・UPS工事の 3 画面を使わない（requirements 1.3・1.9 から外れる） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § ドメインモデル（Domain Model） / 局種別の出し分け | 鋼管柱を KDDI⇒UQ だけに出す（requirements 1.8 から外れる） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § 設計判断（Design Decisions） / 判断 1 | ブラウザーの × で閉じることを防がない（requirements 1.10 から外れる） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § ドメインモデル（Domain Model） / 入れる値 | 入れる先に転貸情報の有無を足して 8 項目にする（requirements 2.1 から外れる） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § 設計判断（Design Decisions） / 判断 3 | 「空にする」操作で値を消す（requirements 2.2 の例外） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § このスペックが持たない責務（Out of Boundary） / 1.2 | 開ける人と状態はチュートリアル設定ボタンの表示だけで決め、/wtg081 では確かめない（1.2） | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § バリデーション設計 / 桁 | 桁（12・10）を入力欄の最大桁で止め、検査とメッセージを持たない（3.2・3.3） | answer:design-authoring-generate[issue-request-tutorial] |
| steering-conformance | specs/issue-request-tutorial/design.md § 機能固有のエラー処理（Error Handling） / 返し方 | 入力チェックの結果を BindingResult でなく JSON の result・messages で返す（tech.md の例外処理フロー） | answer:design-authoring-generate[issue-request-tutorial] |
| steering-conformance | specs/issue-request-tutorial/design.md § API 契約（API Contract） / /wtg081/next | 画面内で JSON を返す口が 1 つ増える（api-standards.md の「JSON を返すのは既存の 2 か所だけ」） | answer:design-authoring-generate[issue-request-tutorial] |
| steering-conformance | specs/issue-request-tutorial/design.md § セキュリティ上の考慮（Security Considerations） / 脅威と対策 | 開ける人と状態をサーバー側で判定しない（security.md の禁止「画面の表示だけで制御しない」） | answer:design-authoring-generate[issue-request-tutorial] |
| dependency-boundary-conformance | specs/issue-request-tutorial/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 親画面がするとき | json.clear の印・入れる順・入力できない項目に入れないこと・電気料等の切替・整形が ir design の公開契約にまだ無い（本書に upstream-carryover と明記） | answer:design-authoring-generate[issue-request-tutorial] |
| evidence-guard | specs/issue-request-tutorial/design.md § ファイル配置計画（File Structure Plan） / function/wtg/wtg081 | 機能ID WTG081 の自分のパッケージ・pwtgo081ZoomForm.html・ZOOM_DEFINE.pwtgo081=1000px,600px | answer:design-authoring-generate[issue-request-tutorial] |
| evidence-guard | specs/issue-request-tutorial/design.md § API 契約（API Contract） / 画面のスクリプトの動き | 着工予定日の初期値を利用者の PC の今日の日付にする | answer:design-authoring-generate[issue-request-tutorial] |
| traceability | specs/issue-request-tutorial/design.md § 移行方針（Migration Strategy） / ZMENUAUTH | ZMENUAUTH の投入の文と手順を tasks で作ること（横断確認 1 回目 #4 の判断の一部）が本書に無い。タスクの分割は tasks で決める | rule:B-04 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 3 | 1 | 対応せず進める | 前回（1 回目 #1）と同じ指摘で、箇所に変更がない: AI 推奨を採用: pbi design・ir design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | system（自動） | 2026-10-09T12:57:02+09:00 |  |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 3 | 2 | 修正 | AI 推奨を採用: 横断確認 1 回目 #5 の判断（口ごとに失敗時の扱いを書く）と、ir design・pbi design の同じ種類の口の扱いに合わせて書き足すだけで、業務の新しい事実は要らないため | Junichi Noumi | 2026-10-09T12:59:43+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 4 | 2026-10-09T13:01:41+09:00 | ①② | ["specs/issue-request-tutorial/design.md"] | {"specs/issue-request-tutorial/design.md":"bcad7f98ec585831c7119db075ee27d872ee16eb00345aa75b3b7d78ac9f8542"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 3 | 2 | feature:issue-request-tutorial | 4 | system（自動）：再検査で再検出なし | 2026-10-09T13:04:09+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:issue-request-tutorial | 4 | specs/issue-request-tutorial/design.md | Junichi Noumi | 2026-10-09T13:05:22+09:00 | bcad7f98ec585831c7119db075ee27d872ee16eb00345aa75b3b7d78ac9f8542 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 3 | 1 | 対応せず進める | 前回（1 回目 #1）と同じ指摘で、箇所に変更がない: AI 推奨を採用: pbi design・ir design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request-tutorial | 4 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:print-report | 5 | 2026-10-09T13:07:43+09:00 | ①② | ["specs/print-report/design.md"] | {"specs/print-report/design.md":"ebfa76def7ce6d9e5503ba27aac9d1ad8b052882340b663b0ced66ab205e5197"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| evidence-guard | specs/print-report/design.md § ドメインモデル（Domain Model） / 発行依頼書のページ（RWTG071） | 製本の情報と添付資料を発行依頼書のページに出さない（requirements 1.10 と異なる） | answer:design-authoring-generate[print-report] |
| evidence-guard | specs/print-report/design.md § ドメインモデル（Domain Model） / ファイル名 | 稟議バーコードNo が空なら申請No.pdf にする（requirements 3.3 と異なる） | answer:design-authoring-generate[print-report] |
| traceability | specs/print-report/design.md § ドメインモデル（Domain Model） / 契約局情報のページ（RWTG072） | 光インフラのとき物件名の列を出す（1.8 は No・基地局番号・基地局名）、40 局ごとにページを分ける（1.5・1.7 のページ数） | answer:design-authoring-generate[print-report] |
| steering-conformance | specs/print-report/design.md § 技術スタック（Technology Stack） / 原本 .xlsm | 原本を .xlsm のまま使い、steering/tech.md の「テンプレートは .xlsx」と異なる（upstream-carryover に記録済み） | answer:design-authoring-generate[print-report] |
| steering-conformance | specs/print-report/design.md § 技術スタック（Technology Stack） / zxing 3.4.1 | zxing 3.4.1 と本番 JDK 1.7 の関係を導入時に発注者の環境で確かめる（Q-DS-PR-015 の案 C） | answer:design-authoring-generate[print-report] |
| dependency-boundary-conformance | specs/print-report/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / /wtg072/search | pbi design の API 契約の /wtg072/search は POST・入力が申請No だけで、本書の 3 つの入力・GET と POST と異なる（Q-DS-PR-009。upstream-carryover で Phase 5 の最後に直す。本書は未反映である旨を明記済み） | answer:design-authoring-generate[print-report] |
| dependency-boundary-conformance | specs/print-report/design.md § 依存してよい対象（Allowed Dependencies） / 6.9 の判定 | 物件基本情報登録変更 Service の 6.9 の判定は pbi design のサービスインターフェースに無いが、同じ wtg070 パッケージの部品として呼び pbi design は変えない（Q-DS-PR-011 の 1 の案 A） | answer:design-authoring-generate[print-report] |
| evidence-guard | specs/print-report/design.md § 移行方針（Migration Strategy） / ZMENUAUTH の PWTGO073 | 文書バーコード（PWTGO073。pbi design の画面）の ZMENUAUTH の行を本 feature で足す（Q-DS-PR-011 の 4「PWTGO073 も同じ扱い」） | answer:design-authoring-generate[print-report] |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:print-report | 5 | specs/print-report/design.md | Junichi Noumi | 2026-10-09T13:11:35+09:00 | ebfa76def7ce6d9e5503ba27aac9d1ad8b052882340b663b0ced66ab205e5197 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 2026-10-09T13:13:51+09:00 | ①② | ["specs/application-status-search/design.md"] | {"specs/application-status-search/design.md":"56b1c92fd4bb8cd7362bbb0c0090dedf7aceeb7df6e5e2d7eee1fce86570f7a5"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | dependency-boundary-conformance | 業務のあいまい・不足 | 要判断 | cf8f3bf0e455d693 | 4e135cfbb040da62 | specs/application-status-search/design.md § 申請状況検索一覧 Controller ほか 1 か所 | `/wtg070/deleteShinse` の戻り先 | 申請の削除の後に一覧へ戻るときの受け口（/wtg060 か /wtg060/return か）が決まっていない | 依存先の pbi design（approved）§ API 契約の `/wtg070/deleteShinse` は、Response を「申請状況一覧（GWTG060）へ戻る（確認は画面で `WTG-100021`）」と定め、URL を書いていない。&#10;本書 § 申請状況検索一覧 Controller の呼び出し元（Inbound）は、メニュー・画面・物件基本情報登録変更画面（`/wtg070/returnList`）・契約情報取込画面（`/wtg090/execute` の後）だけで、削除の後の戻りが無い。§ データ契約と外部連携の「物件基本情報登録変更との口」も、戻るボタン（returnList）と取込の実行の後だけを書く。&#10;本書の口は、`/wtg060` が「検索条件のセッションを消す初期表示」、`/wtg060/return` が「セッションの条件で前に見ていたページを再検索（未検索なら初期表示）」で、どちらで受けるかで画面の結果が変わる（requirements 2.10「物件基本情報登録変更画面から戻ったとき、前の検索条件を残して、もう一度検索」に削除の後が入るかも決まっていない）。&#10;今回、上流の pbi design が横断確認の修正で変わったため全体を検査して見つけた。回答 Q-DS-AS-001・Q-DS-AS-009 は戻りの口として returnList だけを扱っている。 | 次のどちらかを決める。A：削除の後も `/wtg060/return` で受け、セッションの条件で前に見ていたページを再検索する（削除した申請は一覧から消える。未検索なら初期表示）。B：削除の後は `/wtg060` で受け、初期表示にする。決めた口を § 申請状況検索一覧 Controller の呼び出し元に「物件基本情報登録変更画面（`/wtg070/deleteShinse` の後）— 戻り」として足し、§ データ契約と外部連携の「物件基本情報登録変更との口」にも書く。pbi design の `/wtg070/deleteShinse` の Response に URL が無いことは、returnList と同じく upstream-carryover に足して Phase 5 の最後にまとめて直す | 質問：削除の後に前の条件で再検索するか初期表示にするかは業務の決めごとで、回答と上流からは決められない | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | specs/property-basic-info/design.md（Phase 5、upstream-carryover でまとめて直す） | `/wtg070/deleteShinse` の Response が「申請状況一覧（GWTG060）へ戻る」だけで、受ける URL（`/wtg060` か `/wtg060/return` か）を書いていない |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| dependency-boundary-conformance | specs/application-status-search/design.md § データ契約と外部連携（Data Contracts &amp; Integration） ほか 1 か所 | `/wtg070/returnList` の戻り先を pbi design の `/wtg060` ではなく `/wtg060/return` とする（回答 Q-DS-AS-001 で決まり、本書に意図した逸脱と upstream-carryover を明記。pbi design は今回の変更後も `/wtg060` のまま） | answer:design-authoring-generate[application-status-search] |
| dependency-boundary-conformance | specs/application-status-search/design.md § 機能固有エラーコード | pbi design の「既存の WTG-100018」と食い違い、本 feature で新しく足す（回答 Q-DS-AS-009 で決まり、upstream-carryover に記録済み） | answer:design-authoring-generate[application-status-search] |
| traceability | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 初期値 | 進捗検索(選択) の初期値「以上」と社外ユーザーの起案会社の初期値が、1.1 の「初期値を空」から外れる（回答で意図して外れると決まり、本書にも明記） | answer:design-authoring-generate[application-status-search] |
| traceability | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 一覧の 14 列 | 「他n局」を基地局番号にも付けるのは 2.3 から外れる（回答 Q-DS-AS-006 で決まり、本書にも明記） | answer:design-authoring-generate[application-status-search] |
| traceability | specs/application-status-search/design.md § ドメインモデル（Domain Model） / CSV | CSV の見出し（13 列目「発注希望日」、半角カナの表記）が一覧の列名と違う（回答 Q-DS-AS-010 で決まり、本書にも明記） | answer:design-authoring-generate[application-status-search] |
| evidence-guard | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 検索の範囲 | 社外ユーザーの絞り込みを、検索条件の表の「会社名」ではなく会社コードで比べる（回答 Q-DS-AS-005 の 2 で決まる） | answer:design-authoring-generate[application-status-search] |
| steering-conformance | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 社外ユーザー | P71 のキー3 を、security.md の「ログインユーザーのグループ」ではなく権限区分とする（回答 Q-DS-AS-005 で決まる） | answer:design-authoring-generate[application-status-search] |
| steering-conformance | specs/application-status-search/design.md § API 契約（API Contract） | アクション名 csv・page・clear・return・detail が tech.md の URL の例に無い（回答 Q-DS-AS-001・Q-DS-AS-010 で決まり、例は「など」で限定していない） | answer:design-authoring-generate[application-status-search] |
| evidence-guard | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 検索条件 | 38 項目の入力の形・一致の仕方・比べる列を、回答者が渡した検索条件の表に委ねる（回答 Q-DS-AS-002「その表のとおりにしてください」） | answer:design-authoring-generate[application-status-search] |
| evidence-guard | specs/application-status-search/design.md § バリデーション設計 | 桁の検査・日付・時刻・数字のキーと、範囲の逆転を検査しないこと（回答 Q-DS-AS-007 で決まり、キーは既存の messages.properties に実在） | answer:design-authoring-generate[application-status-search] |
| steering-conformance | specs/application-status-search/design.md § 技術スタック（Technology Stack） | 開発端末の JDK 1.8 が、tech.md の JDK 1.7 と食い違う | verify:pbi design（approved）の Q-DS-PBI-014 で人が決めた同じ逸脱で、本書にも意図して外れると明記し、upstream-carryover.md に記録済み。原因は上流の 1 か所で、重複になる |
| dependency-boundary-conformance | specs/application-status-search/design.md § 依存してよい対象（Allowed Dependencies） | feature-list の依存の列に無い issue-request の TWTGM100 を読む | verify:issue-request design（approved）が下流の読む形を公開契約にしており、内部実装への依存ではない |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 1 | 修正 | 修正案の A（削除の後も /wtg060/return で受け、前の条件で再検索する。未検索なら初期表示。pbi design の deleteShinse の Response は returnList と同じく upstream-carryover に足す） | Junichi Noumi | 2026-10-09T13:31:26+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 4 | 2026-10-09T13:33:37+09:00 | ①② | ["specs/application-status-search/design.md"] | {"specs/application-status-search/design.md":"e02dc7e42b09f7b5cd83f753e6b18b9a9d9f62d0353a23f842c755944a019449"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | dependency-boundary-conformance | 文書間の参照 | 軽微 | de8b2e8cf82ffd19 | 417b93b82ea8f372 | specs/application-status-search/design.md § 再確認が必要になる変更（Revalidation Triggers） ほか 1 か所 | `/wtg070/deleteShinse` の口 | 削除の後の戻り（deleteShinse）が再確認の対象と補足資料の口の一覧に無い | 今回の修正（design-check 3 回目 #1 の修正案 A）で、§ 申請状況検索一覧 Controller の呼び出し元（Inbound）に「物件基本情報登録変更画面（`/wtg070/deleteShinse` の後）— 戻り。`/wtg060/return` で受ける」が、§ データ契約と外部連携の「物件基本情報登録変更との口」に削除の後も `/wtg060/return` で受けることが足され、本書は pbi design の `/wtg070/deleteShinse` に新しく依存するようになった。&#10;一方、同じ口の一覧を持つ次の 2 か所は returnList までで、deleteShinse を挙げていない。&#10;・§ 再確認が必要になる変更（Revalidation Triggers）：「`/wtg070/pushApplicationNo`・`/wtg070/returnList` の口の変更（pbi design）」&#10;・§ 補足資料（Supporting References）の「物件基本情報登録変更との口と CSV の共通部品」の行：「`/wtg070/pushApplicationNo`・`/wtg070/returnList`、`getExternalScope`、`CsvUtils`」&#10;pbi design（approved）§ API 契約の `/wtg070/deleteShinse` の Response は「申請状況一覧（GWTG060）へ戻る」で、受ける URL は upstream-carryover で直す予定のため、pbi 側が変わったときに本書を再確認する対象に入れておく必要がある。修正の中身（削除の後も `/wtg060/return` で受ける）は上流・回答と食い違わない（requirements 2.10、pbi design の deleteShinse は URL を書いていない）。 | § 再確認が必要になる変更 の行を「`/wtg070/pushApplicationNo`・`/wtg070/returnList`・`/wtg070/deleteShinse`（削除の後の戻り先）の口の変更（pbi design）」に直す。§ 補足資料 の「物件基本情報登録変更との口と CSV の共通部品」の行の内容を「`/wtg070/pushApplicationNo`・`/wtg070/returnList`・`/wtg070/deleteShinse`、`getExternalScope`、`CsvUtils`」に直す | 修正：今回足した依存を、同じ口を並べる節に書き足すだけで、業務の新しい事実は要らない | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| dependency-boundary-conformance | specs/application-status-search/design.md § データ契約と外部連携（Data Contracts &amp; Integration） ほか 1 か所 | `/wtg070/returnList` の戻り先を pbi design の `/wtg060` ではなく `/wtg060/return` とする（回答 Q-DS-AS-001 で決まり、本書に意図した逸脱と upstream-carryover を明記。pbi design は `/wtg060` のまま） | answer:design-authoring-generate[application-status-search] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 4 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T13:36:39+09:00 |  |  |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 3 | 1 | feature:application-status-search | 4 | system（自動）：再検査で再検出なし | 2026-10-09T13:36:39+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 5 | 2026-10-09T13:41:07+09:00 | ①② | ["specs/application-status-search/design.md"] | {"specs/application-status-search/design.md":"32696c8e99e895008c9a84e8e9c0f98da61fbd800fb352fd06a5749c8171cc3a"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 4 | 1 | feature:application-status-search | 5 | system（自動）：再検査で再検出なし | 2026-10-09T13:44:49+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:application-status-search | 5 | specs/application-status-search/design.md | Junichi Noumi | 2026-10-09T13:50:01+09:00 | 32696c8e99e895008c9a84e8e9c0f98da61fbd800fb352fd06a5749c8171cc3a |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 5 | 2026-10-09T13:52:55+09:00 | ①② | ["specs/contract-info-import/design.md"] | {"specs/contract-info-import/design.md":"1f0d97d85481240538b33f7067f886ece5c27b89630e2182816191fe0954a11c"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | evidence-guard | 業務の欠落・矛盾 | 重大 | ca485ea9b03f2e92 | e997690e4d19bfc1 | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 入れる値 | 受電方法の照合 | 古い契約の受電方法を WTG-000072 とするが、検査表の※8 の値の成形・未登録時の扱いと食い違う | 区分：根拠の飛躍（本書が正とする検査表と食い違う）。本書 § ドメインモデル「入れる値」（横断確認 1 回目 #1 の反映）は「受電方法は予備項目4 か ELECT_KIND の名称にして出すので、名称で照合する。予備項目4 が空の古い契約から出た受電方法は P43 の名称と合わず WTG-000072 になるので、利用者が CSV の受電方法を P43 の名称に直してから取り込む」と書く。一方、差し替えた検査表 `_handoff/phase5-contract-info-import-checks.md` の 2-2 No.35 契約基本_受電方法には注記 ※8 が付き、※8 は「値の先頭から『1:』または『2:』を削除する／『3』始まりの場合は値を『KDDI受電』とする／その他は何もしない／値成形後、ﾁｪｯｸ処理・更新処理を実施する／ﾁｪｯｸ処理はせず、ｺｰﾄﾞﾏｽﾀに登録されていない値の場合は受電方法の取込内容を反映しない」とする。ELECT_KIND から出る値は「1:電力会社直受」「2:テナント受電」「3:ａｕ受電」（`specs/contract-info-download/csv-layout-wtg100.md` No.35、横断確認 1 回目 #1 の回答）で、※8 はまさにこの形の値を成形してから照合する決まりである。本書はこの成形に触れず、成形しないまま照合して WTG-000072 になるとしている。さらに ※8 の後半（チェックせず、未登録なら反映しない）は、同じ検査表の 2-3 No.9（(3) で取れなければ WTG-000072）とも両立しない。本書は検査表を「列ごとの検査の正」としているため、実装者は ※8 の成形をするか、未登録の値をエラーにするか反映しないだけにするかを決められない。契約者区分（2-3 No.10 ほか：許可値「契約者」「関係者」）・法人_個人区分（2-3 No.11 ほか：(4) P06 の名称）・消費税扱い（(10) の注記：リバースデータはキー3 で照合、対応表どおりコードのまま税区分へ）は本書の記述と検査表・対応表が一致することを確かめた。 | 何を決めればよいか：リバースデータの契約基本_受電方法の扱い。A：検査表 ※8 のとおり、先頭の「1:」「2:」を削り「3」始まりを「KDDI受電」にしてから P43 の名称で照合し、合わなければ WTG-000072（2-3 No.9）。本書の「古い契約は合わず WTG-000072」の文を ※8 の成形を書いた文に直し、※8 の後半（チェックせず反映しない）は検査表から外す。B：※8 の成形をしたうえで、P43 に無い値はエラーにせず受電方法を取り込まない（※8 の後半）。本書と検査表 2-3 No.9 をそのように直す。C：成形しない（本書の今の記述のまま）。検査表の ※8 を外す。 | 質問：本書が正とする検査表と人の回答（横断確認 1 回目 #1）の内容が食い違い、どちらに合わせるかは人が決める業務の事実のため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| dependency-boundary-conformance | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 洗替と変更履歴の順 4. | 契約局情報の変更履歴を連番だけで突き合わせ、ir design の手順（連番＋計画基地局番号で結ぶ）と違う | answer:design-authoring-generate[contract-info-import] |
| traceability | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 検査 | 4.3 の「基地局番号」を契約基地局番号だけ（枝番なし）で比べる | answer:design-authoring-generate[contract-info-import] |
| traceability | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 稟議バーコードNo | 受付No が空・リバースデータで稟議バーコードNo を付けない（2.6 からの逸脱。明記と持ち越し済み） | answer:design-authoring-generate[contract-info-import] |
| steering-conformance | specs/contract-info-import/design.md § 機能固有のエラー処理（Error Handling） / ログ | 警告に住所、WTG-200011 に電話番号、タスクのパラメータに氏名を出す（steering からの意図した逸脱。明記と持ち越し済み） | answer:design-authoring-generate[contract-info-import] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 5 | 1 | 修正 | 修正案の B（※8 の成形のあと P43 で照合し、無い値はエラーにせず受電方法のコードを反映しない。横断確認 1 回目 #1 の「古い契約は WTG-000072」「利用者が CSV を直してから取り込む」は回答者の誤りなので消してください。検査表 _handoff/phase5-contract-info-import-checks.md の 2-3 No.9 は「検査しない」に直しました） | Junichi Noumi | 2026-10-09T14:03:20+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 6 | 2026-10-09T14:06:37+09:00 | ①② | ["specs/contract-info-import/design.md"] | {"specs/contract-info-import/design.md":"f8c85c02fe3eac668a090b8cb084d4319381ea95428d4c25c7149c98c569bebc"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| dependency-boundary-conformance | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 洗替と変更履歴の順 4. | 契約局情報の変更履歴を連番だけで突き合わせ、ir design の手順（連番＋計画基地局番号で結ぶ）と違う | answer:design-authoring-generate[contract-info-import] |
| traceability | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 検査 | 4.3 の「基地局番号」を契約基地局番号だけ（枝番なし）で比べる | answer:design-authoring-generate[contract-info-import] |
| traceability | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 稟議バーコードNo | 受付No が空・リバースデータで稟議バーコードNo を付けない（2.6 からの逸脱。明記と持ち越し済み） | answer:design-authoring-generate[contract-info-import] |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 5 | 1 | feature:contract-info-import | 6 | system（自動）：再検査で再検出なし | 2026-10-09T14:10:03+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:contract-info-import | 6 | specs/contract-info-import/design.md | Junichi Noumi | 2026-10-09T14:11:57+09:00 | f8c85c02fe3eac668a090b8cb084d4319381ea95428d4c25c7149c98c569bebc |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 4 | 2026-10-09T14:15:39+09:00 | ①② | ["specs/contract-info-download/design.md"] | {"specs/contract-info-download/design.md":"e365aaa3c25a50d9a24dad8e438b02ebc77d61278d53da5492b16a4a793311a1"} | 2 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務のあいまい・不足 | 要判断 | 4650f08855d269b0 | e835de1ac038d3f4 | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） / VWTGM010 ほか 1 か所 | 契約者の処理順2 の並びのキー | 契約者①〜⑤の並びの「契約者区分」が、名称にした列かコードか本文で読めない | 意味判定（要件 3.1・3.5、ID 対応あり・内容があいまい）。横断確認 1 回目 #1 の反映で、ビュー VWTGM010 の 2契約者の「契約者区分」の列は CONSTRACT_KBN を名称（1→「契約者」、2→「関係者」）にした値になった（`work-tables-wtg100.md` の列一覧 No 6、`csv-layout-wtg100.md` の No 48）。一方、本文は処理順2 を「計画基地局番号＋枝番ごとに契約者区分・契約者番号の昇順の番号」（§物理データモデル VWTGM010）、「契約者区分の昇順・契約者番号の昇順で 1〜5 番目を入れる」（§ドメインモデル CSV の契約者①〜⑤）とだけ書き、並べるのがコードか名称の列かを書いていない。名称で並べると、文字コード・照合順によっては「関係者」が「契約者」より前になり、契約者①に入る行が変わる。出力の定義（本書の正）は「契約者区分（CONSTRACT_KBN）の昇順」（`csv-layout-wtg100.md` の「契約者①〜⑤・支払情報①〜④の入れ方」）とコードで並べると書いており、本文だけがあいまい。作業用テーブルの表の「VWTGM010 の絞り込みと処理順2」も「契約者区分」とだけ書く。他の箇所：§ドメインモデル（Domain Model） / CSV の契約者①〜⑤ | §物理データモデルの VWTGM010 の 2契約者を「処理順2＝計画基地局番号＋枝番ごとに契約者区分のコード（`CONSTRACT_KBN`。名称にする前の値）・契約者番号の昇順の番号」に、§ドメインモデルの契約者①〜⑤を「契約者区分のコード（`CONSTRACT_KBN`）の昇順・契約者番号の昇順で 1〜5 番目を入れる」に直す（出力の定義の書き方に合わせる） | 修正：業務の新しい事実は要らず、本書の正である出力の定義が CONSTRACT_KBN で並べると書いているので、本文をそれに合わせれば足りるため | 確認済み |  |  |
| 2 | traceability | 業務のあいまい・不足 | 要判断 | 162e1f65d2a8cd4f | 18e479dcc2533ef7 | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / CSV の値の形 | CSV の値の形（名称にする列） | CSV の値の形で名称にする列を 3 つだけ挙げ、登録状態の「コード:名称」が抜けている | 意味判定（要件 3.1、ID 対応あり・内容があいまい）。今回足した文は「日付は…その形で出し、ほかの列は元の値のまま。ただし、契約者①〜⑤_契約者区分は「契約者」「関係者」、法人_個人区分は「法人」「個人」…、契約基本_受電方法は…の文字にして、ビュー VWTGM010 で出す」と、元の値から変える列をこの 3 つに限るように読める。出力の定義（本書の正）の No 9 契約基本_登録状態は「契約基本情報ﾏｽﾀ.STATUS_KIND &#124;&#124; ':' &#124;&#124; ｺｰﾄﾞﾏｽﾀ.名称('WTG',PARAM,'P21')」（`csv-layout-wtg100.md` No 9、`work-tables-wtg100.md` 列一覧 No 11）で、コードに名称をつないだ値を出すが、本文の例外に入っていない。§データ契約と外部連携の「契約情報取込との口」も、渡す値の形を契約者区分・法人_個人区分・受電方法（名称）と消費税扱い（コード）だけで書いている。出力の定義が正なので実装の値は決まるが、本文の「ほかの列は元の値のまま」と食い違って読める | §ドメインモデルの CSV の文を「値はすべて文字列で、列ごとの値は出力の定義の取得元のとおり。日付は出力の定義で `YYYY/MM/DD` にしている列だけをその形で出し、ほかの日付の列は元の値のまま。契約基本_登録状態は「コード:名称」（`P21`）、契約者①〜⑤_契約者区分は…（以下、今の文のとおり）」に直す。「契約情報取込との口」の値の形は「列ごとの値は出力の定義のとおり。取込が照合に使う列のうち、契約者区分・法人_個人区分・受電方法は名称（文字）、消費税扱いはコードで渡す」とする | 修正：業務の新しい事実は要らず、本書の正である出力の定義に書いてある値の形を本文の例外に足せば足りるため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/contract-info-download/design.md § このスペックが持たない責務（Out of Boundary） | 「ci design は直さない」と書くが、ci design は横断確認の修正で値の形の記述が変わった。381 列の定義の持ち主と取込の design を直さない扱いは Q-DS-CD-001 の 6 の回答のとおり | answer:design-authoring-generate[contract-info-download] |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 一覧の 19 項目 | 一覧の受電方法は「2:ﾃﾅﾝﾄ受電」（半角）、CSV は「2:テナント受電」で表記が違う。一覧の表記は Q-DS-CD-003 の回答のとおり | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § バリデーション設計 | サーバーで検索条件の桁・形式を確かめない（security.md の入力検証から外れる）。Q-DS-CD-005 の回答で決まり、意図した逸脱として記録済み | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / ベンダー／施工会社の絞り込み | 工事案件マスタに行が無い契約情報を出す（security.md 285 行目の既存の WTB と同じ方式から外れる）。回答冒頭の「意図して外れる点」で決まり、記録済み | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § 技術スタック（Technology Stack） | 開発端末の JDK 1.8（tech.md の JDK 1.7 から外れる）。Q-DS-PBI-014 の回答で決まり、記録済み | answer:design-authoring-generate[property-basic-info] |
| dependency-boundary-conformance | specs/contract-info-download/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 物件基本情報登録変更との口 | pbi design の契約局DL の口は「申請No だけを渡す」で、本書は FunctionID と applicationNo を足す。開き方は Q-DS-CD-008 の 1 の回答のとおりで、pbi design は upstream-carryover で直す | answer:design-authoring-generate[contract-info-download] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-download | 4 | 1 | 対応せず進める | Phase 5 の最後の上流まとめ直しと横断確認で扱う | Junichi Noumi | 2026-10-09T14:20:41+09:00 | 対象外 | はい | 不採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-download | 4 | 2 | 対応せず進める | Phase 5 の最後の上流まとめ直しと横断確認で扱う | Junichi Noumi | 2026-10-09T14:20:46+09:00 | 対象外 | はい | 不採用 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:contract-info-download | 4 | specs/contract-info-download/design.md | Junichi Noumi | 2026-10-09T14:21:35+09:00 | e365aaa3c25a50d9a24dad8e438b02ebc77d61278d53da5492b16a4a793311a1 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 4 | 1 | 対応せず進める | Phase 5 の最後の上流まとめ直しと横断確認で扱う | feature:contract-info-download | 4 |
| feature:contract-info-download | 4 | 2 | 対応せず進める | Phase 5 の最後の上流まとめ直しと横断確認で扱う | feature:contract-info-download | 4 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| cross | 2 | 2026-10-09T14:23:07+09:00 | ② | ["specs/property-basic-info/design.md","specs/issue-request/design.md","specs/issue-request-tutorial/design.md","specs/print-report/design.md","specs/application-status-search/design.md","specs/contract-info-import/design.md","specs/contract-info-download/design.md"] | {"specs/property-basic-info/design.md":"03331555d6ee0825bd90f023f17f4951d532f97b0f4bde7b7f50878d4cc4da03","specs/issue-request/design.md":"7bedc0d4618ebcb9a1667ce749bf24513272ac9c19fbdebdfe1ac2954ab67fbb","specs/issue-request-tutorial/design.md":"bcad7f98ec585831c7119db075ee27d872ee16eb00345aa75b3b7d78ac9f8542","specs/print-report/design.md":"ebfa76def7ce6d9e5503ba27aac9d1ad8b052882340b663b0ced66ab205e5197","specs/application-status-search/design.md":"32696c8e99e895008c9a84e8e9c0f98da61fbd800fb352fd06a5749c8171cc3a","specs/contract-info-import/design.md":"f8c85c02fe3eac668a090b8cb084d4319381ea95428d4c25c7149c98c569bebc","specs/contract-info-download/design.md":"e365aaa3c25a50d9a24dad8e438b02ebc77d61278d53da5492b16a4a793311a1"} | 3 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ssot-consistency | 業務の欠落・矛盾 | 重大 | 497e41779641bc48 | 37d7311cefd4b06a | specs/property-basic-info/design.md § 判断 2: 申請単位の排他を物件申請情報の排他用の値 1 つで行う ほか 4 か所 | 申請の排他用の値（TWTGM080.ExclusiveFG）の範囲 | 発行依頼書登録変更の更新は申請の排他用の値を変えず、物件基本情報の排他の前提と食い違う | 【pbi design の取り決め】§判断 2「どの操作でも TWTGM080 の行を SELECT … FOR UPDATE でロックして ExclusiveFG を照合し、更新のたびに ExclusiveFG を変える」、採用理由「子のテーブルごとに排他を持つと、承認フローの操作と項目の更新が同時に通り、確認していない内容で回覧が進むおそれがある。申請単位で 1 つにすれば、画面を開いた後の変更はすべて検出できる」。§ドメインモデル 集約とトランザクション境界「根は物件申請情報（申請No）で、契約局情報・…・発行依頼書（読取りと削除・複製だけ）がぶら下がる。…申請の排他用の値（ExclusiveFG）を照合してから更新する」。§状態管理 並行制御「契約局情報・契約稟議ファイル・文書バーコードの更新も申請の ExclusiveFG で照合し、申請単位で直列にする」。§データ契約と外部連携（Data Contracts &amp; Integration） サービス間は取込（TWTGM080 の排他用の値を変える）だけを挙げ、発行依頼書登録変更に触れていない。&#10;【ir design の取り決め】§依存してよい対象 依存の制約・§ドメインモデル 集約とトランザクション境界・§状態管理 並行制御「更新・一時保存の排他は TWTGM100・TWTGM140 の ExclusiveFG だけで行う。TWTGM080 はロックも照合もしない」（design-check 1 回目 #9 の判断）。書いた TWTGM100・TWTGM140 の行の ExclusiveFG だけを新しい値にする。&#10;【食い違い】同じ「申請」の集約（ir design も「pbi design と同じ」とする）の排他の取り決めが 2 つの design で別の形になっている。ir の更新・一時保存は TWTGM080 の ExclusiveFG を変えないので、物件基本情報登録変更の画面を開いた後に発行依頼書・契約局情報が発行依頼書登録変更で更新されても、物件基本情報登録変更の承認フローの操作（確認・申請・承認など）と契約局情報の並替え・削除は排他エラーにならない。pbi design の判断 2 が避けるとした「確認していない内容で回覧が進む」状態が、同じ番の権限を持つ別の利用者どうしの間で起きうるが、pbi design の判断 2 の採用理由は「すべて検出できる」としたまま。逆向きでは、ir は物件基本情報登録変更の並替え・削除による行の変化を開いていた行の ExclusiveFG の照合（行が無ければ GEF-000027。ir §照合する行が無いときの扱い）で拾う前提だが、pbi design は並替え・削除で TWTGM140 の行の ExclusiveFG をどうするかを書いていない。取込（ci design）については横断確認 1 回目 #2 で両方の排他用の値を変えると決めたが、発行依頼書登録変更と物件基本情報登録変更の間の取り決めはどの design にも無い。 | 何を決めればよいか：物件基本情報登録変更の画面が、開いた後の発行依頼書登録変更による発行依頼書・契約局情報の変更を排他エラーにするか。&#10;案A：しない（ir design-check 1 回目 #9 の判断のまま）。pbi design の判断 2 の採用による影響と §データ契約と外部連携 サービス間に「発行依頼書登録変更の更新・一時保存は TWTGM080 の排他用の値を変えないので、物件基本情報登録変更の画面を開いた後の発行依頼書・契約局情報の変更は、物件基本情報登録変更の操作では排他エラーにならない（ir design）」を足し、判断 2 の採用理由の「画面を開いた後の変更はすべて検出できる」を「物件基本情報登録変更と取込による変更は検出できる」に直す。§状態管理 並行制御に「契約局情報の並替え・削除では、書き換えた TWTGM140 の行の ExclusiveFG を新しい値にする（発行依頼書登録変更の排他の前提。ir design）」を足す。&#10;案B：する。WTG 申請状態サービスに申請の排他用の値を新しい値にする口を足し、ir の更新・一時保存の最後に呼ぶ（ir design-check 1 回目 #9 の判断を見直し、pbi の公開契約に口を足す。どちらの design も直す）。 | 質問：同時に操作されたときに回覧を止めるかは業務の判断で、ir design-check 1 回目 #9 の判断を見直すかどうかを含むため | 確認済み |  |  |
| 2 | ssot-consistency | 工程・文書の分担 | 軽微 | 16558d74d26814a0 | 326cd3a168eafcf4 | specs/property-basic-info/design.md § 物理データモデル（Physical Data Model） / TWTGM140 ほか 1 か所 | TWTGM140 の全列の定義 | TWTGM140の全345列の定義がir側の資料にだけあり、持ち主のpbi designは別の言い方で参照しない | pbi design §このスペックが持つ責務 所有するデータ「契約局情報（TWTGM140）のテーブル定義」、§物理データモデル「全 345 列で、主な列は下の表。残りは発行依頼書の契約局ごとの項目で、契約局取込の形式と同じ並び（Q-DS-PBI-003）」と、主な列の表（13 行と「（残りの列）」の行）。全 345 列の表（列番号・項目名・型・桁）は specs/issue-request/db-TWTGM140.md にあり、ir design §物理データモデルは「定義は物件基本情報登録変更が持つ（pbi design）。…全 345 列は specs/issue-request/db-TWTGM140.md（回答者が渡した DB レイアウト。Q-DS-IR-004）」とする。print-report（§論理データモデル）と ci（§論理データモデル）も TWTGM140 の列を db-TWTGM140.md で引く。持ち主の pbi design はこの資料を参照しておらず、「契約局取込の形式と同じ並び」は db-TWTGM140.md の並び（No.1〜6 の共通列、No.7 申請No、No.8 稟議ﾊﾞｰｺｰﾄﾞNo、No.9 連番、…コードと名称・(ﾌﾘｰﾌｫｰﾑ) の組を含む 345 列）と同じ意味にならない（取込の 228 列とは列の数も違う）。主な列の項目名・型・桁は db-TWTGM140.md と一致しており（Ringi_Barcode_No 25、Renban Int 4、Keikaku_Kichikyoku_No 9 必須、Bukken_Name 100、Draft_Flg 1 など）、内容の食い違いではなく定義の置き場所の問題。表示名だけ、pbi が「代表局番号_枝番」、db-TWTGM140.md が「枝番」（Represent_SiteID_Branch）で違う。 | pbi design §物理データモデルの TWTGM140 の行を「…列は下の表。全 345 列の定義（列番号・項目名・型・桁）は specs/issue-request/db-TWTGM140.md（回答者が渡した DB レイアウト。Q-DS-IR-004）を正とする」に、主な列の表の「（残りの列）」の行の許可値を「specs/issue-request/db-TWTGM140.md のとおり」に直す。§補足資料（Supporting References）に同じ資料の行を足す。 | 修正：持ち主の design から既にある全列の資料を指すだけで、業務の新しい事実は要らないため | 確認済み |  |  |
| 3 | ssot-consistency | 業務の欠落・矛盾 | 重大 | 5c529ec1de08da16 | aff7cba2154021be | specs/property-basic-info/design.md § API 契約（API Contract） / 契約局情報欄に出す列 | 関係者の契約者区分の値 | 契約局情報欄の契約者の条件が契約者区分 "01" で、発行依頼書の値（1:契約者）と合わない | pbi design §API 契約（物件基本情報登録変更 Controller）の「契約局情報欄に出す列」：「発行依頼書（TWTGM100）の関係者1〜5 のうち契約者区分が "01"（契約者）で関係(地位) に「旧」を含まない人を…」（Q-DS-PBI-003。.aidd/.engine/answer-ds-pbi-20261007-1300-Q003-2-Q002-10.txt:8）。TWTGM100 の持ち主の ir design は §ドメインモデル 名称の列で「契約者区分名は固定（1→"契約者"、2→"関係者"）」、§バリデーション設計で「契約者区分は 1・2 だけ」（WTG-100020）とし、specs/issue-request/item-rules.md:57 も「固定の選択肢 1:契約者／2:関係者」。関係者の契約者区分の列（Kankeisha1〜5_Contract_Kbn。db-TWTGM100.md No.51 ほか）には 1 か 2 が入る。pbi 自身の出力 CSV の項目定義（specs/property-basic-info/csv-layout-wtg070.md:20 ほか）も「関係者1_契約区分="1"の場合"契約者"」で、同じ feature の中でも値が合わない。このままでは契約局情報欄の契約者が誰も出ない。ci・cd は名称「契約者」「関係者」で受け渡し、print-report は名称「契約者」で選んでおり、"01" を使うのは pbi のこの箇所だけ。 | 何を決めればよいか：契約局情報欄の契約者の条件の値。&#10;案A：pbi design を「契約者区分が "1"（契約者）」に直す（ir design・item-rules.md・pbi の csv-layout-wtg070.md と同じ値）。&#10;案B：契約者区分を "01"・"02" の 2 桁にそろえる（ir design・item-rules.md の選択肢と名称の入れ方、pbi の出力 CSV の項目定義、ci の取込の値の入れ方を直す）。 | 質問：pbi の値は回答（Q-DS-PBI-003 の補足）によるため取り違えかを回答者に確かめる必要がある。持ち主の ir design とほかの feature はどれも 1・2 なので、案 A のほうが直す箇所が少ない | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| ssot-consistency | specs/contract-info-import/design.md § ドメインモデル（Domain Model） / 洗替と変更履歴の順 4. | 取込の変更履歴の突き合わせが連番だけで、ir design の変更履歴の手順（会社コード・申請No・連番・計画基地局番号で結ぶ）と違う | answer:design-authoring-generate[contract-info-import] |
| ssot-consistency | specs/application-status-search/design.md § ドメインモデル（Domain Model） / 一覧の 14 列 起案日 | 起案日を審査権限 '01' の行で取り、pbi design で同じ審査権限を持つ起案者の取下げの行も当たりうる | answer:design-authoring-generate[application-status-search] |
| ssot-consistency | specs/property-basic-info/design.md § API 契約（API Contract）・移行方針・バリデーション設計 | /wtg070/returnList・/wtg070/deleteShinse の戻り先、/wtg070/keyakuDl の渡し方、/wtg072/search の入力、/wtg080/return の受け口、採番の MAX区分、既存とした WTX-100005・WTX-100011・WTX-100012・WTG-100018 の他 feature との食い違い | verify:既決（upstream-carryover の pbi design の項目） |
| ssot-consistency | specs/issue-request/design.md § 再確認が必要になる変更（Revalidation Triggers） | 契約情報ダウンロードを TWTGM100・TWTGM140 を読む側に挙げている | verify:既決（upstream-carryover「design 横断確認 1 回目の修正の回で C[対象外+]とし、最後にまとめて直すもの」の ir design の項目） |
| ssot-consistency | specs/issue-request/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / チュートリアル（GWTG081）との受け渡し | チュートリアルとの受け渡し（json.clear・入れる順・入れる項目・契約開始日・電気料の列）の食い違い | verify:既決（upstream-carryover の ir design の項目） |
| ssot-consistency | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / CSV 契約者①〜⑤の並び | 契約者①〜⑤の並びの契約者区分が名称にした列かコードか読めない | learned:design feature:contract-info-download 4-1 |
| ssot-consistency | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / CSV の値の形 | CSV の値の形で名称にする列から登録状態の「コード:名称」が抜けている | learned:design feature:contract-info-download 4-2 |
| ssot-consistency | specs/*/design.md の画面内で JSON を返す口（/wtg070/inputHassoKiboDate・/wtg080/calcTaxAdjustment・/wtg080/changeKeiyakuSyubetsuTutorial・/wtg081/next） | エラーの返し方の規約を steering に置かず、口ごとに失敗時の扱いを書く（形は口ごとに違う） | verify:既決（upstream-carryover「design 横断確認 1 回目で決まったもの」の api-standards.md の項目。横断確認 1 回目 #5 の案 B） |
| dependency-cycle-detection | specs/property-basic-info/design.md § データ契約と外部連携（Data Contracts &amp; Integration） | pbi→ir（TWTGM100 の読取り・削除・複製）と ir→pbi（WTG 申請状態サービス）の組は Phase 3 で扱った循環と同じ根本原因で、新しい閉路を構成しない | answer:feature-decomposition-generate[] |
| dependency-cycle-detection | specs/print-report/design.md § 依存してよい対象（Allowed Dependencies） | pbi 画面→/wtg072/search と print-report Service→pbi Service（6.9 の判定）の組。判定の置き場は回答で pbi Service を呼ぶと決定済み | answer:design-authoring-generate[print-report] |
| dependency-cycle-detection | specs/*/design.md の API 契約（pbi→ci→AS→pbi、pbi と ci・pbi と AS・ir と tutorial） | 画面の遷移・戻り（/wtg090/back・/wtg090/execute の後の /wtg060/return・/wtg060/detail・/wtg070/returnList）・コールバックと、function/wtg/common の共通部品への呼出しで、feature 間の閉路を構成しない | verify:画面の遷移・戻り・コールバックと WTG 共通部品への呼出しは feature 間の依存の辺にならない |
| steering-conformance | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） | 作業用テーブル TWTGD050・TWTGD060 が共通列を持たない（steering/database.md の共通カラム） | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/issue-request-tutorial/design.md § バリデーション設計 | 増額分賃料・消費電力の桁をサーバーで検査しない（steering/security.md の入力検証） | answer:design-authoring-generate[issue-request-tutorial] |
| steering-conformance | specs/property-basic-info・issue-request・application-status-search・contract-info-import・contract-info-download の design § 機能固有のエラー処理（Error Handling） | 画面の業務エラー・排他を例外にせず BindingResult で返す（print-report は steering/tech.md どおり ApplicationException）。feature ごとに扱いが分かれる | verify:既決（upstream-carryover「tech.md：画面の業務エラー・排他は BindingResult で返してよい場合」） |
| steering-conformance | specs/property-basic-info・issue-request・contract-info-download の design § API 契約（API Contract） | 更新系の URL（一時保存・発番・並替えほか、/wtg100/csv）が CSRF の照合に乗らない（steering/security.md の攻撃対策） | verify:既決（upstream-carryover「security.md 攻撃対策：CSRF は末尾一致の対象だけを照合する」） |
| steering-conformance | specs/*/design.md § 技術スタック（Technology Stack） | 開発端末の JDK 1.8（-source/-target 1.7）が steering/tech.md の必須ツール JDK 1.7 と違う | verify:既決（upstream-carryover「tech.md：開発端末のテスト実行は JDK 1.8 で -source/-target 1.7」） |
| steering-conformance | specs/property-basic-info・issue-request・application-status-search の design § セキュリティ上の考慮（Security Considerations） | P71 のキー3 を権限区分で引く（steering/security.md 285 行目の「ログインユーザーのグループ」） | verify:既決（upstream-carryover「security.md 285 行目」） |
| steering-conformance | specs/contract-info-import/design.md § 機能固有のエラー処理（Error Handling）・セキュリティ上の考慮 | 警告に住所・電話番号の値を出し、タスクのパラメータに氏名を入れる（steering/non-functional.md・security.md） | verify:既決（upstream-carryover の contract-info-import の項目） |
| steering-conformance | specs/contract-info-download/design.md § バリデーション設計・ドメインモデル | サーバーで検索条件の桁・形式を確かめない、工事案件マスタに行が無い契約情報を出す（steering/security.md） | verify:既決（upstream-carryover の contract-info-download の項目） |
| steering-conformance | specs/issue-request/design.md § 物理データモデル（Physical Data Model）・論理データモデル | トランの表の種別 V、金額・調整額を文字列で持つ（steering/database.md） | verify:既決（upstream-carryover の issue-request の項目） |
| steering-conformance | specs/print-report/design.md § 技術スタック（Technology Stack） | 原本を .xlsm のまま POI で使う（steering/tech.md の「テンプレートは .xlsx」） | verify:既決（upstream-carryover の print-report の項目） |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| cross | 1 | 1 | cross | 2 | system（自動）：再検査で再検出なし | 2026-10-09T14:33:58+09:00 |
| cross | 1 | 2 | cross | 2 | system（自動）：再検査で再検出なし | 2026-10-09T14:33:58+09:00 |
| cross | 1 | 3 | cross | 2 | system（自動）：再検査で再検出なし | 2026-10-09T14:33:58+09:00 |
| cross | 1 | 4 | cross | 2 | system（自動）：再検査で再検出なし | 2026-10-09T14:33:58+09:00 |
| cross | 1 | 6 | cross | 2 | system（自動）：再検査で再検出なし | 2026-10-09T14:33:58+09:00 |
| cross | 1 | 7 | cross | 2 | system（自動）：再検査で再検出なし | 2026-10-09T14:33:58+09:00 |
| cross | 1 | 8 | cross | 2 | system（自動）：再検査で再検出なし | 2026-10-09T14:33:58+09:00 |
| cross | 1 | 9 | cross | 2 | system（自動）：再検査で再検出なし | 2026-10-09T14:33:58+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 2 | 1 | 対応せず進める | 案 A の扱い（発行依頼書登録変更の更新・一時保存は TWTGM080 を更新せず、排他用の値が変わるのは発番のときだけ）。pbi design の文言は upstream-carryover に足し、Phase 5 の最後にまとめて直す | Junichi Noumi | 2026-10-09T14:37:39+09:00 | 後で決める | はい |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 2 | 2 | 対応せず進める | pbi design から specs/issue-request/db-TWTGM140.md を指す修正を upstream-carryover に足し、Phase 5 の最後にまとめて直す | Junichi Noumi | 2026-10-09T14:37:48+09:00 | 後で決める | はい |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 2 | 3 | 対応せず進める | 契約者区分は 1:契約者・2:関係者（"01" は回答者の取り違え）。pbi design の直しは upstream-carryover に足し、Phase 5 の最後にまとめて直す | Junichi Noumi | 2026-10-09T14:37:57+09:00 | 後で決める | はい |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| cross | 1 | 5 | cross | 2 | Junichi Noumi | 2026-10-09T14:38:32+09:00 |

## 確認

| スコープ | 回数 | 確認者 | 日時 | 原本SHA256 |
|---|---|---|---|---|
| cross | 2 | Junichi Noumi | 2026-10-09T14:38:53+09:00 | {"specs/property-basic-info/design.md": "03331555d6ee0825bd90f023f17f4951d532f97b0f4bde7b7f50878d4cc4da03", "specs/issue-request/design.md": "7bedc0d4618ebcb9a1667ce749bf24513272ac9c19fbdebdfe1ac2954ab67fbb", "specs/issue-request-tutorial/design.md": "bcad7f98ec585831c7119db075ee27d872ee16eb00345aa75b3b7d78ac9f8542", "specs/print-report/design.md": "ebfa76def7ce6d9e5503ba27aac9d1ad8b052882340b663b0ced66ab205e5197", "specs/application-status-search/design.md": "32696c8e99e895008c9a84e8e9c0f98da61fbd800fb352fd06a5749c8171cc3a", "specs/contract-info-import/design.md": "f8c85c02fe3eac668a090b8cb084d4319381ea95428d4c25c7149c98c569bebc", "specs/contract-info-download/design.md": "e365aaa3c25a50d9a24dad8e438b02ebc77d61278d53da5492b16a4a793311a1"} |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| cross | 2 | 1 | 対応せず進める | 案 A の扱い（発行依頼書登録変更の更新・一時保存は TWTGM080 を更新せず、排他用の値が変わるのは発番のときだけ）。pbi design の文言は upstream-carryover に足し、Phase 5 の最後にまとめて直す | cross | 2 |
| cross | 2 | 2 | 対応せず進める | pbi design から specs/issue-request/db-TWTGM140.md を指す修正を upstream-carryover に足し、Phase 5 の最後にまとめて直す | cross | 2 |
| cross | 2 | 3 | 対応せず進める | 契約者区分は 1:契約者・2:関係者（"01" は回答者の取り違え）。pbi design の直しは upstream-carryover に足し、Phase 5 の最後にまとめて直す | cross | 2 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:property-basic-info | 8 | 2026-10-09T18:41:35+09:00 | ①② | ["specs/property-basic-info/design.md"] | {"specs/property-basic-info/design.md":"03331555d6ee0825bd90f023f17f4951d532f97b0f4bde7b7f50878d4cc4da03"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/property-basic-info/design.md § 物理データモデル（Physical Data Model） / TWTGM140 | TWTGM140 の全 345 列のうち「残りの列」の定義の所在が本書から辿れない（参照先だった ir 側の db 資料が削除済みという事実を含む） | learned:design cross 2-2 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:property-basic-info | 8 | specs/property-basic-info/design.md | masato-teramoto | 2026-10-09T18:46:09+09:00 | 03331555d6ee0825bd90f023f17f4951d532f97b0f4bde7b7f50878d4cc4da03 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 9 | 2026-10-09T18:51:17+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md":"7bedc0d4618ebcb9a1667ce749bf24513272ac9c19fbdebdfe1ac2954ab67fbb"} | 3 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | format-conformance | 文書間の参照 | 軽微 | 406c817d39490539 | 77b2bf036e78ac85 | specs/issue-request/design.md § 補足資料（Supporting References） / 資料 7 行 ほか 42 か所 | 実在しない補足資料への参照 | 実在しない補足資料 9 件（db-TWTG*.md 8 件・item-rules.md）を 43 行で参照している | 参照先が実在しない。specs/issue-request/ には design.md と requirements.md しか無いことを Glob で確認した（db-TWTGA130.md・db-TWTGA150.md・db-TWTGM100.md・db-TWTGM140.md・db-TWTGM160.md・db-TWTGV030.md・db-TWTGV050.md・db-TWTZM370.md・item-rules.md の 9 件はどれも無い）。design.md 内の該当は 43 行（item-rules.md を含む行 27、db-*.md を含む行 19、両方を含む行 3）。内訳（design.md の行番号）：(a) 前書き 14（「回答者の指示でこの場所に置いたもの」と書いた説明そのものが事実と合わない）。(b) 達成目標 38。(c) 責務境界 73・112・113・115・130。(d) 論理データモデル 244（db-*.md と item-rules.md）。(e) 物理データモデル 255〜262（TWTGM100・TWTGM140・TWTGA130・TWTGA150・TWTGV030・TWTGV050・TWTGM160・TWTZM370 の各行に「全列は specs/issue-request/db-….md」）。(f) データ契約 291。(g) Service の責務と入力可否表 407・424・428・429・468。(h) バリデーション設計 542・548・559・562・565〜569。(i) 移行方針 710、移行対象ファイル一覧 726・727。(j) テスト戦略 754・757。(k) 補足資料の表 822〜828（9 件すべてを参照先に挙げる 7 行）。実在するのは specs/property-basic-info/csv-layout-wtg070.md など他の参照先のみ。他の feature の design にも同じ参照が残っている（contract-info-import 3 行・print-report 2 行・application-status-search 1 行。今回の検査対象外のため指摘にはしていない）。なお原本は specs の外の _handoff/phase5-ir-db-*.md と _handoff/phase5-ir-item-rules.md に残っており、回答（.aidd/.engine/answer-ds-ir-20261007-1959.txt 2・30・64 行付近）がそれを出典に挙げている。過去の人の判断との関係：1 回目 #4（9.6 の所属必須を item-rules.md に従って意図的に外す）は 対応せず進める で判断済みで、ここでは出し直さない（根拠にしたファイルが無くなった事実だけを (h) 559 行として数えた）。 | 次のどちらかに決めて直す。A：9 件を specs/issue-request/ に戻す（または _handoff の原本への参照に変える）。B：参照を外し、必要な内容を本文に取り込む（取り込む範囲は指摘 2・3 を参照）。どちらでも、前書き 14 行の説明、物理データモデル 255〜262 の「全列は…」、補足資料の表 822〜828 の参照先を実在する参照に合わせる。 | 質問：参照先を戻すか、本文に取り込むか、参照だけ外すかは人が決める事項のため | 確認済み |  |  |
| 2 | traceability | 業務のあいまい・不足 | 要判断 | 9ab64d5830674d88 | ed91e2366e415e60 | specs/issue-request/design.md § バリデーション設計 / 項目ごとの規則（item-rules.md） ほか 7 か所 | 項目ごとの入力チェック規則 | 入力チェックの項目別規則が item-rules.md だけにあり、本文で確定できない | 要件 9（9.1〜9.7）と 2.x・8.x を満たす入力チェックの項目別の必須・桁・形式・選択肢の元・入力できない場合・条件付き必須・相関・メッセージを、design 本文は「item-rules.md を正とする」（542 行）「item-rules.md のとおり」（38 行）と委ねている。item-rules.md が実在しないため、本文だけでは次を決められない。(1) 更新時に必須の全項目と桁数・形式（本文は 553〜557 行に一部の項目を列挙するのみ。「全項目の必須・桁・形式」は 542 行で item-rules.md に委ねる）。(2) 条件付き必須の中身（565 行「item-rules.md の条件付きの必須」、{0}・{1} に入る項目の組合せが不明。558・564 行の 2 種だけが本文にある）。(3) 入力できない項目（429 行「製本種別・支払方法・法人個人区分・発送先・契約種別による入力不可」の条件）。(4) 関係(地位)と契約種別・受電方法・役職氏名の整合（566 行）、転貸借の P53／P37 の組合せ（568 行）、TEL の桁（567 行）、郵便番号と住所の照合の対象項目（569・548 行）、案件小グループの工事案件での使用可否（562 行）。(5) コード値で持つ属性の選択肢の元の一覧（244 行「item-rules.md の『選択肢の元』」、112 行は P06〜P90 の範囲だけ）と、それをもとにした移行の TWTZM040 投入行（710 行・728 行）。(6) 契約区分の自動設定（468 行）は本文に判定規則があり自己完結しているが、「item-rules.md の 8」を出典にしている。契約情報取込の行のチェックもこの規則に合わせる前提（73・130・291 行）のため、下流にも影響する。出典：回答 Q-DS-IR-006（.aidd/.engine/answer-ds-ir-20261007-1959.txt 64 行付近）は規則の本体を _handoff/phase5-ir-item-rules.md に置いたと答えており、回答自体には規則の本体が無い。要件側は 9.1 に「必須・桁数・形式」とだけあり、項目ごとの値は requirements では決めない（finding-rules B-02。design で決める）ため、design 本文に定義が無い状態になっている。同じ原因（参照先の消失）は指摘 1 が参照の切れとして出しており、ここでは「定義が本文に残っていない」ことだけを扱う。 | 次から選ぶ。A：item-rules.md を戻し、参照先として復元する（指摘 1 の A）。B：項目ごとの規則（必須・桁・形式・選択肢の元・入力できない場合・条件付き必須・相関・メッセージ）を design 本文（バリデーション設計の表など）へ取り込む。C：_handoff/phase5-ir-item-rules.md を正本とし、参照先をそのパスに変える（specs の外の資料を正とする扱いの可否を人が決める）。 | 質問：項目別規則を本文に取り込むか、資料を戻すか、_handoff を正本とするかは業務側の判断が要るため | 確認済み |  |  |
| 3 | traceability | 業務のあいまい・不足 | 要判断 | 6fc6002cee782f4b | 51eb0ad82e3d6da1 | specs/issue-request/design.md § 物理データモデル（Physical Data Model） / TWTGM100・TWTGM140 ほか 6 か所 | テーブルの全列定義と投入データ | TWTGM100・140 ほかの全列定義と TWTGM160 の 25 件が本文だけでは定義できない | 要件 1.1・7.1・7.2・4.2・4.3 を満たす列の定義が db-*.md だけにある。(1) TWTGM100（353 列）・TWTGM140（345 列）・TWTGA130（353 列）・TWTGA150（345 列）・TWTGV030・TWTGV050 の全列の列名・型・桁・必須・許可値・並び（255〜260 行。本文にあるのは主な列と、TWTGM100 だけ・TWTGM140 だけの列の差、金額 2〜4 の桁が違うこと）。変更履歴の比べる範囲「No.7 Keiyaku_Kbn〜No.353 Draft_Flg」「No.7 Application_No〜No.345 Draft_Flg」（235 行・278 行）の No. は db-TWTGM100.md・db-TWTGM140.md の並びを前提にしており、並びが本文に無いと範囲を特定できない。(2) 名称の列・(ﾌﾘｰﾌｫｰﾑ) の列の入れ方と、コードと (ﾌﾘｰﾌｫｰﾑ) が組になる金額項目の一覧（213 行・231 行・291 行。例は電気料【月額】だけで、組になる項目の全体は本文に無い）。(3) TWTGM160 の 25 件の中身と、案件小グループ・その他①をキー3 に置き換えて投入する対応（261 行・710 行・726 行。本文は列の概要と、001・002 が汎用例であることだけ）。要件 4.2・4.3 は 25 件から選ぶ前提のため、投入データが決まらないとズームの動作（383 行）が確かめられない。(4) TWTZM370 は列と 4 行が本文（262 行・710 行）と回答 Q-DS-IR-018 に残っているため、自己完結している（指摘対象外）。軽減要因：steering/database.md の「マイグレーション」は DDL を発注者の DB レイアウト設計書から作ると定めており、列の最終の正本は発注者の資料である。ただし本文は 255〜260 行・補足資料で正を db-*.md と明記しているため、実装者（Mapper・Form・Info bean の 353 項目）が参照できる定義が design から辿れない。これは指摘 1 の参照切れとは別に、定義の置き場所を決める内容。 | 次から選ぶ。A：db-*.md 8 件を戻して参照先を復元する（指摘 1 の A）。B：design 本文または docs の DB レイアウトへ全列の定義を取り込む（列数が多いため補足資料として別ファイルに置く場合は、実在するパスを参照先にする）。C：発注者の DB レイアウト設計書を正本とし、design の参照先をその資料（名称・版）に変える。 | 質問：列定義と投入データの正本をどこに置くかは人が決めるため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| evidence-guard | specs/issue-request/design.md § 物理データモデル（Physical Data Model） / TWTGM100・TWTGM140 | 全 353 列・345 列、比べる範囲 No.7〜No.353・No.7〜No.345 の数値は資料が無くなっても回答に出典がある | answer:design-authoring-generate[issue-request] |
| evidence-guard | specs/issue-request/design.md § 物理データモデル（Physical Data Model） / TWTGM160 ほか | TWTGM160 の列の桁・25 件・TWTZM370 の 4 行の数値は回答 Q-DS-IR-009・Q-DS-IR-018 に出典がある | answer:design-authoring-generate[issue-request] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 9 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T18:55:49+09:00 |  |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 9 | 2 | 修正 |  | masato-teramoto | 2026-10-09T18:59:25+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 9 | 3 | 修正 |  | masato-teramoto | 2026-10-09T18:59:31+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 10 | 2026-10-09T19:03:46+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md":"832c47b0cc28093cee938b3184cdd52710ba04f2cd6364c463ecd0f032cac8fc"} | 3 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務の欠落・矛盾 | 重大 | f9039b471ed09eb8 | bc6a71f021e3c480 | specs/issue-request/design.md § 項目ごとの規則（Q-DS-IR-006） / 規則 2. 案件G・基本情報・作成組織・契約形態 / その他①〜④ | その他①〜④の桁 | その他①〜④の入力桁 100 が DB 列 Sonota1〜4_Freeform の 50 と食い違う | 規則 2 の「その他①〜④」の行（design.md 2824 行）は桁を 100 とし、データリスト WTG/PARAM/P35 の名称も手入力もこの桁まで受け付ける。一方、TWTGM100 の DB レイアウトは Sonota1〜4（コード列）が 20 桁、Sonota1_Freeform〜Sonota4_Freeform（手入力・名称を入れる列）が 50 桁（design.md 596〜603 行。No.320〜327）。51〜100 バイトを入力すると桁数の検査（GEF-000003）を通ったうえで、更新で 50 桁の列に入らない。同じ「(ﾌﾘｰﾌｫｰﾑ)」列の組のうち、ほかの項目（市区町村 50、契約事由 256、その他書類 100、添付資料 200、部数 10、関係(地位) 40 など）は規則の桁と DB の桁が一致しており、この 1 組だけ食い違う。規則 2 の記述は原本（_handoff/phase5-ir-item-rules.md 32 行）のとおりで、取り込みの欠落・改変ではない。前回までは DB の列定義が本文に無く、桁を突き合わせられなかった。TWTGM140・TWTGA150・TWTGV050 の対応列（Sonota1〜4_Freeform）の桁は個別には読んでいない（桁 50 の行の総数は原本の合計と一致）。 | 次から選ぶ。A：規則 2 の「その他①〜④」の桁を 50 に直す（DB レイアウトを正とする）。B：DB レイアウトの Sonota1〜4_Freeform を 100 に直す（TWTGM100・TWTGM140・TWTGA130・TWTGA150・TWTGV030・TWTGV050 の 6 表と、回答者の DB レイアウト設計書も同時に直す）。C：コード列（20 桁）に入る名称の長さと 100 の関係を確かめ、規則の 100 の意味（名称の最大長か入力桁か）を決める。 | 質問：どちらの桁が正しいかは回答者（DB レイアウト設計書と画面設計の持ち主）の判断が要るため | 確認済み |  |  |
| 2 | traceability | 文書間の参照 | 軽微 | a6f7bd42ae49681f | bc6a71f021e3c480 | specs/issue-request/design.md § 項目ごとの規則（Q-DS-IR-006） / 規則 1. UQ担当者入力欄・ヘッダー / 契約区分 | 契約区分の自動設定の参照先 | 規則 1 の契約区分が自動設定の参照を「下の 7.」とするが正しくは規則 8 | 規則 1 の「契約区分」の行（design.md 2815 行）の「入力できない場合」に「基地局番号を入れたとき自動設定（下の 7.）」とある。取り込み後の見出しは、規則 7 が「一時保存・発番のときの検査」（2937 行）、規則 8 が「契約区分の自動設定（基地局番号を入れたとき）」（2942 行）で、自動設定の本体は規則 8。ほかの相互参照（規則 0 の「下の 6.」＝規則 6、規則 2・3 の「下の 5.」＝規則 5）は合っている。原本（_handoff/phase5-ir-item-rules.md 23 行）も「下の 7.」で、原本の見出しも 7・8 の順のため、取り込みで生じたのではなく原本の誤記を引き継いだもの。 | 2815 行の「（下の 7.）」を「（規則 8）」に直す。 | 修正：参照番号を見出しに合わせるだけで足り、業務の判断は要らないため | 確認済み |  |  |
| 3 | traceability | 文書間の参照 | 軽微 | 6c7373eeb6f40b80 | 9e8c068b42d69383 | specs/issue-request/design.md § TWTGA130 の DB レイアウト（発行依頼書情報変更履歴。Q-DS-IR-013） / No.353 ほか 3 か所 | 一時保存フラグの列名と許可値 | TWTGA130 の No.353 が DRAFT_FLG で、「列名が同じ」の説明と合わない | TWTGA130 の前書き（design.md 989 行）は「列は TWTGM100 とまったく同じ（353 列。名前・型・桁が同じ）」とするが、No.353 の項目名は `DRAFT_FLG`（1348 行）で、TWTGM100 の `Draft_Flg`（629 行）と綴りが違う。変更履歴の比べる列の説明（235 行）は No.353 を `Draft_Flg` と書く。許可値も、TWTGM100（629 行）・TWTGM140（985 行）は「0：更新済 / 1：一時保存中」だが、TWTGA130（1348 行）・TWTGV030（2066 行）・TWTGA150（1703 行）・TWTGV050（2421 行）は空欄で、「名前・型・桁が同じ」の説明が許可値までは言っていないものの、読み手には同じ定義に見える。原本（_handoff/phase5-ir-db-TWTGA130.md 362 行ほか）のとおりの取り込みで、欠落・改変ではない。INSERT … SELECT * は列の並びで写すため動作には影響しないが、列名を書く Mapper の SQL・DDL では綴りの違いが残る。 | 989 行の説明に「ただし No.353 の項目名は DRAFT_FLG（DB レイアウトのまま）。変更履歴・トランの許可値は書かれていない（意味は TWTGM100 と同じ）」と注記する。または DB レイアウト設計書を確かめて項目名を Draft_Flg にそろえる。 | 修正：本文の説明を実際の定義に合わせる注記で足り、定義の変更は不要のため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| evidence-guard | specs/issue-request/design.md § 物理データモデル（Physical Data Model） / TWTGM100・TWTGM140 | 全 353 列・345 列、比べる範囲 No.7〜No.353・No.7〜No.345 の数値は回答に出典がある | answer:design-authoring-generate[issue-request] |
| evidence-guard | specs/issue-request/design.md § TWTGM160 の DB レイアウトと投入データ（ｻﾝﾌﾟﾙ文設定ﾏｽﾀ。Q-DS-IR-009） / 投入データ | TWTGM160 の列の桁・25 件、TWTZM370 の 4 行の数値は回答 Q-DS-IR-009・Q-DS-IR-018 に出典がある | answer:design-authoring-generate[issue-request] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request | 10 | 2 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T19:10:05+09:00 |  |  |  |
| feature:issue-request | 10 | 3 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T19:10:05+09:00 |  |  |  |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 9 | 1 | feature:issue-request | 10 | system（自動）：再検査で再検出なし | 2026-10-09T19:10:05+09:00 |
| feature:issue-request | 9 | 2 | feature:issue-request | 10 | system（自動）：再検査で再検出なし | 2026-10-09T19:10:05+09:00 |
| feature:issue-request | 9 | 3 | feature:issue-request | 10 | system（自動）：再検査で再検出なし | 2026-10-09T19:10:05+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 10 | 1 | 修正 |  | masato-teramoto | 2026-10-09T19:13:19+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 11 | 2026-10-09T19:15:54+09:00 | ①② | ["specs/issue-request/design.md"] | {"specs/issue-request/design.md": "8cf01f68fe35f51ecb925f5258243beb7a476500279d2757c8a0a7788c2917ec"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request | 10 | 1 | feature:issue-request | 11 | system（自動）：再検査で再検出なし | 2026-10-09T19:18:30+09:00 |
| feature:issue-request | 10 | 2 | feature:issue-request | 11 | system（自動）：再検査で再検出なし | 2026-10-09T19:18:30+09:00 |
| feature:issue-request | 10 | 3 | feature:issue-request | 11 | system（自動）：再検査で再検出なし | 2026-10-09T19:18:30+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:issue-request | 11 | specs/issue-request/design.md | masato-teramoto | 2026-10-09T19:18:59+09:00 | 8cf01f68fe35f51ecb925f5258243beb7a476500279d2757c8a0a7788c2917ec |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:issue-request | 1 | 2 | 対応せず進める | AI 推奨を採用: 人の回答（Q-DS-IR-014）に従った読み方として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 11 |
| feature:issue-request | 1 | 4 | 対応せず進める | AI 推奨を採用: item-rules.md（回答者が渡した資料）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 11 |
| feature:issue-request | 1 | 7 | 対応せず進める | AI 推奨を採用: pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 11 |
| feature:issue-request | 1 | 8 | 対応せず進める | AI 推奨を採用: design に明記され、pbi design は Phase 5 の最後にまとめて直す方針とされているため。直すまでは pbi の実装がこの前提を満たさない | feature:issue-request | 11 |
| feature:issue-request | 2 | 1 | 対応せず進める | AI 推奨を採用: 人の回答（Q-DS-IR-001 の C）に従った意図的な逸脱として design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため。ただし承認済み requirements と両立しない状態は残る | feature:issue-request | 11 |
| feature:issue-request | 2 | 2 | 対応せず進める | AI 推奨を採用: グループを権限区分と読むことは物件基本情報と 1 回目の判断で決まっており、上流の文言は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 11 |
| feature:issue-request | 2 | 3 | 対応せず進める | AI 推奨を採用: pbi design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request | 11 |
| feature:issue-request | 2 | 4 | 対応せず進める | AI 推奨を採用: design に明記され、pbi design は Phase 5 の最後にまとめて直す方針とされているため。直すまでは pbi の実装がこの前提を満たさない | feature:issue-request | 11 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 5 | 2026-10-09T19:21:55+09:00 | ①② | ["specs/issue-request-tutorial/design.md"] | {"specs/issue-request-tutorial/design.md":"bcad7f98ec585831c7119db075ee27d872ee16eb00345aa75b3b7d78ac9f8542"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | ab0e607c3cb9e607 | 1f0b54e4cad792e9 | specs/issue-request-tutorial/design.md § データ契約と外部連携（Data Contracts &amp; Integration） / 開き方 ほか 2 か所 | ir design の公開契約に無い、開く部品の読込とウインドウ名 | 開く部品の読込とウインドウ名 pwtgo081 が ir design に書かれていない | 本書は「発行依頼書登録変更画面のテンプレートが `pages/wtg/wtg081/pwtgo081ZoomForm.html` を読み込む」「ウインドウ名 `pwtgo081` の別ウインドウを `/zoom/wait` で開く」と書き、責務境界でも「ir design の画面がテンプレートに読み込む」としている（本書 § このスペックが持つ責務（This Spec Owns）、§ データ契約と外部連携 開き方、§ ファイル配置計画）。現在の `specs/issue-request/design.md`（再承認後）の § データ契約と外部連携 / チュートリアル（GWTG081）との受け渡し（2507〜2510 行）は、URL `/wtg081`・POST の渡し方・`window.opener[ウインドウ名 + 'callback'](json)`・項目名までで、`pwtgo081ZoomForm.html` を読み込むこと、ウインドウ名が `pwtgo081` であること、`ZOOM_DEFINE.pwtgo081` は書いていない。ir design § ファイル配置計画（3030 行）にも `pwtgo081ZoomForm.html` は無く、`pwtgo080.html・pwtgo080Script.html` が「ズームとチュートリアルのコールバック」を持つとだけある。`.aidd/.engine/upstream-carryover.md` の ir design 向け記述（50 行）はコールバック名 `pwtgo081callback` までで、開く部品の読込とウインドウ名は足されていない。本書 § データ契約と外部連携 親画面がするとき は「ir design の公開契約にまだ無い」事項を列挙しているが、この 2 点は含まれていない。なお、ir design の他の参照（`/wtg080/changeKeiyakuSyubetsuTutorial` の入出力、項目名 `inputInfo.contractSyubetsu`・`kyokuSyubetsu`・`sechiSetsubi`・`moveLeaseChinryo`・`moveLeaseDenkiryoFreeform`・`moveLeaseChakkoYoteiDate`・`moveLeaseKind`・`kddiRentalContract`・`moveLeaseContractStartDate`、`/wtg081?FunctionID=WTG081&amp;keiyakuKbn=` の POST、更新ボタンを出す条件、判断 5 の CSRF 照合の扱い、`WTG-100015` をチュートリアルが使うこと）は、現在の ir design と食い違わない。補足資料・本文のいずれにも、削除済みの補足資料（`db-*.md`・`item-rules.md`）への参照は無い。 | 本書の「ir design の画面がテンプレートに読み込む」を「ir design にまだ無い。親画面は `pwtgo081ZoomForm.html` を読み込み、ウインドウ名 `pwtgo081` で開く」に直し、§ データ契約と外部連携 親画面がするとき の「ir design の公開契約にまだ無い」事項に加える。upstream-carryover の ir design 向け記述に、開く部品 `pwtgo081ZoomForm.html` の読込とウインドウ名 `pwtgo081` を足す（Phase 5 の最後にまとめて直す）。 | 修正：判断 1・§ データ契約と外部連携の既存の扱い（上流は Phase 5 の最後にまとめて直す）と同じく、本書の書き方と upstream-carryover を直せば足り、業務の新しい事実は要らない | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | specs/issue-request/design.md（Phase 5 の最後の上流まとめ直し） | ir design の受け渡しの公開契約に、開く部品の読込とウインドウ名が無いため（本書の記述を直したうえで upstream-carryover に足す） |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 5 | 1 | 修正 | AI 推奨を採用: 判断 1・§ データ契約と外部連携の既存の扱い（上流は Phase 5 の最後にまとめて直す）と同じく、本書の書き方と upstream-carryover を直せば足り、業務の新しい事実は要らない | masato-teramoto | 2026-10-09T19:27:07+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 6 | 2026-10-09T19:29:37+09:00 | ①② | ["specs/issue-request-tutorial/design.md"] | {"specs/issue-request-tutorial/design.md": "d7c594a832cbe0fbab57395810305bccadf57f10983df788ca4e850bd0c1084a"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 5 | 1 | feature:issue-request-tutorial | 6 | system（自動）：再検査で再検出なし | 2026-10-09T19:32:05+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:issue-request-tutorial | 6 | specs/issue-request-tutorial/design.md | masato-teramoto | 2026-10-09T19:32:37+09:00 | d7c594a832cbe0fbab57395810305bccadf57f10983df788ca4e850bd0c1084a |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:issue-request-tutorial | 3 | 1 | 対応せず進める | 前回（1 回目 #1）と同じ指摘で、箇所に変更がない: AI 推奨を採用: pbi design・ir design と同じ扱いとして design に明記され、上流は Phase 5 の最後にまとめて直す方針とされているため | feature:issue-request-tutorial | 6 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:print-report | 6 | 2026-10-09T19:35:19+09:00 | ①② | ["specs/print-report/design.md"] | {"specs/print-report/design.md":"ebfa76def7ce6d9e5503ba27aac9d1ad8b052882340b663b0ced66ab205e5197"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | format-conformance | 文書間の参照 | 軽微 | 5dae0723a86d85f2 | 859927701a790ce3 | specs/print-report/design.md § 論理データモデル（Logical Data Model） / 属性と型 ほか 1 か所 | 削除済みの補足資料 db-TWTGM100.md・db-TWTGM140.md への参照 | 参照先 specs/issue-request/db-TWTGM100.md・db-TWTGM140.md が実在しない | 参照が切れている箇所は 2 か所。(1) 論理データモデル「属性と型」（243 行目）「`specs/issue-request/db-TWTGM100.md`・`specs/issue-request/db-TWTGM140.md` のとおり」。(2) 補足資料の表「発行依頼書の列」の参照先（652 行目）「`specs/issue-request/db-TWTGM100.md`・`specs/issue-request/db-TWTGM140.md`」。`specs/issue-request/` に実在するのは design.md と requirements.md だけで、db-*.md は削除済み（Glob で確認）。内容は現在の `specs/issue-request/design.md` へ取り込み済みで、`#### TWTGM100 の DB レイアウト（発行依頼書情報ﾏｽﾀ。Q-DS-IR-003）`（266 行目。全 353 列）と `#### TWTGM140 の DB レイアウト（契約局情報ﾏｽﾀ。Q-DS-IR-004）`（631 行目。全 345 列）に実在する。なお、本 design が使う列（稟議バーコードNo＝TWTGM140 の Ringi_Barcode_No・25 桁、連番 Renban、担当エリア名 Area_Name、基地局番号・基地局名・物件名、TWTGM080 の Tandoku_Fukusu_Flg・Moto_Application_No・Application_Date）は、ir design・pbi design の現在の列定義と名前・意味の食い違いが無いことを確かめた（本 design は列の型・桁を自分では書かず、参照だけをしている）。 | (1) 243 行目を「各属性と型は pbi design・ir design の物理データモデルと、`specs/issue-request/design.md` の `#### TWTGM100 の DB レイアウト（発行依頼書情報ﾏｽﾀ。Q-DS-IR-003）`・`#### TWTGM140 の DB レイアウト（契約局情報ﾏｽﾀ。Q-DS-IR-004）` のとおり」に直す。(2) 652 行目の参照先を「`specs/issue-request/design.md` の `#### TWTGM100 の DB レイアウト（発行依頼書情報ﾏｽﾀ。Q-DS-IR-003）`・`#### TWTGM140 の DB レイアウト（契約局情報ﾏｽﾀ。Q-DS-IR-004）`」に直す。 | 修正：参照先を現在の ir design の実在する節へ直すだけで解消し、業務の新しい事実は要らないため | 確認済み |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:print-report | 6 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T19:38:22+09:00 |  |  |  |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:print-report | 7 | 2026-10-09T19:41:02+09:00 | ①② | ["specs/print-report/design.md"] | {"specs/print-report/design.md":"e6d65db63292a5733f32042793e645f314b884f64423bea613d93d7f2d8fb620"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:print-report | 6 | 1 | feature:print-report | 7 | system（自動）：再検査で再検出なし | 2026-10-09T19:43:27+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:print-report | 7 | specs/print-report/design.md | masato-teramoto | 2026-10-09T19:43:59+09:00 | e6d65db63292a5733f32042793e645f314b884f64423bea613d93d7f2d8fb620 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 6 | 2026-10-09T19:46:55+09:00 | ①② | ["specs/application-status-search/design.md"] | {"specs/application-status-search/design.md": "32696c8e99e895008c9a84e8e9c0f98da61fbd800fb352fd06a5749c8171cc3a"} | 2 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | format-conformance | 文書間の参照 | 軽微 | bf3c352aa1efd1aa | 96e89156592a9142 | specs/application-status-search/design.md § 依存してよい対象（Allowed Dependencies） / 依存先（98 行） | `specs/issue-request/db-TWTGM100.md` | 削除済みの `db-TWTGM100.md` を参照しており、参照先が実在しない | 98 行に「発行依頼書（`TWTGM100`）の定義（ir design。`specs/issue-request/db-TWTGM100.md`）」とある。`specs/issue-request/` にあるのは `requirements.md` と `design.md` だけで、`db-TWTGM100.md` は存在しない（補足資料は削除済み）。本文内にこのパスを書いた箇所はここ 1 か所だけ（`specs/application-status-search/` 全体を検索）。補足資料の内容は `specs/issue-request/design.md` の見出し「#### TWTGM100 の DB レイアウト（発行依頼書情報ﾏｽﾀ。Q-DS-IR-003）」（266 行）に取り込まれており、その節が全 353 列（表示名・項目名・型・桁・必須・許可値）を持つ。本書が使う列（`Anken_Syo_Grp_Cd`・`Sonota1`・`Sonota1_Freeform`・`Keiyaku_Ringi_Kiansha_Kaisha_Cd`・`Keiyaku_Ringi_Kiansha_Kaisha_Name`・`Keiyaku_Ringi_Kiansha_Name`・`First_Pay_Day1`〜`4`）の列名・型（1:String）・桁（10・20・50・20・50・100・8）は、その節の定義と食い違っていない（発送希望日 `Hasso_Kibo_Date` と依頼内容 `Irai_Naiyo` は `TWTGM080` の列で、pbi design の定義と一致）。 | 98 行の「（ir design。`specs/issue-request/db-TWTGM100.md`）」を「（ir design。`specs/issue-request/design.md` の `#### TWTGM100 の DB レイアウト（発行依頼書情報ﾏｽﾀ。Q-DS-IR-003）`）」に直す。参照先の節は実在する。 | 修正：参照先の節が ir design に実在し、直すだけで解消できる | 確認済み |  |  |
| 2 | dependency-boundary-conformance | 文書間の参照 | 軽微 | 76208e0269b32236 | 96e89156592a9142 | specs/application-status-search/design.md § 依存してよい対象（Allowed Dependencies） / 依存先（98 行）ほか 1 か所 | 発行依頼書（`TWTGM100`）の定義（ir design） | feature-list の依存は pbi だけだが、ir design の定義を依存先に挙げている | `.aidd/feature-list.md` の application-status-search の依存列は「property-basic-info」だけで、`specs/application-status-search/requirements.md` の「前提と依存」の依存も property-basic-info だけ。一方、本書は「依存してよい対象（Allowed Dependencies）」の依存先（98 行）に ir design の `TWTGM100` の定義を挙げ、「再確認が必要になる変更（Revalidation Triggers）」（113 行）にも「pbi design・ir design」と書く。本書は `TWTGM100` を外部結合して起案会社・案件小グループ・初回支払日を比べる・出すので、ir design の DB レイアウトを読む実態はある（requirements 1.7 も契約稟議起案会社で絞る）。読むのは ir design の公開された DB レイアウトで、内部実装には触れておらず、公開契約経由の依存になっている。本書が ir design を依存として扱う書き方は Allowed Dependencies と Revalidation Triggers の 2 か所だけで、Out of Boundary（81 行）は発行依頼書の持ち主を `specs/issue-request/design.md` と正しく書く。食い違いは宣言（feature-list・requirements の依存）と実際の読み取りの間にある。 | 98 行の末尾に「feature-list の依存列は property-basic-info だけだが、本 feature は `TWTGM100` を外部結合で読むため ir design の DB レイアウトを読む。feature-list の依存列は Phase 5 の最後にまとめて直す（upstream-carryover）」と足す。本書の依存先の書き方は変えない。feature-list の依存列に issue-request を足すかどうかは人が決める。 | 修正：本書の書き方は公開契約を読むだけで境界を越えない。宣言とのずれは本書の upstream-carryover の書き方で残せる | 確認済み |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 2 | 人間による確認（`.aidd/feature-list.md` の application-status-search の依存列に issue-request を足すか。requirements の「前提と依存」も同様） | 原因は上流の依存の宣言（feature-list・requirements）が `TWTGM100` を読む実態を含まないこと。本書の記述では解消できない |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 6 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T19:50:45+09:00 |  |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:application-status-search | 6 | 2 | 修正 | AI 推奨を採用: 本書の書き方は公開契約を読むだけで境界を越えない。宣言とのずれは本書の upstream-carryover の書き方で残せる | masato-teramoto | 2026-10-09T19:52:24+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 7 | 2026-10-09T19:55:04+09:00 | ①② | ["specs/application-status-search/design.md"] | {"specs/application-status-search/design.md": "b0d59adc5f67c4377772191bd6d81adc4234cdaf73d7f61c30eac704d697f0fa"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:application-status-search | 6 | 1 | feature:application-status-search | 7 | system（自動）：再検査で再検出なし | 2026-10-09T19:57:46+09:00 |
| feature:application-status-search | 6 | 2 | feature:application-status-search | 7 | system（自動）：再検査で再検出なし | 2026-10-09T19:57:46+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:application-status-search | 7 | specs/application-status-search/design.md | masato-teramoto | 2026-10-09T19:58:13+09:00 | b0d59adc5f67c4377772191bd6d81adc4234cdaf73d7f61c30eac704d697f0fa |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 7 | 2026-10-09T20:01:06+09:00 | ①② | ["specs/contract-info-import/design.md"] | {"specs/contract-info-import/design.md":"f8c85c02fe3eac668a090b8cb084d4319381ea95428d4c25c7149c98c569bebc"} | 2 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | format-conformance | 文書間の参照 | 軽微 | 5d4b46e91a0c246d | 748c288b8256108a | specs/contract-info-import/design.md § 論理データモデル（Logical Data Model） / 属性と型 ほか 2 か所 | 削除済みの補足資料への参照 | 存在しない db-*.md・item-rules.md への参照が 3 か所ある | 参照先が実在しない（相対パス参照切れ）。specs/issue-request/ には requirements.md と design.md しか無く、db-*.md と item-rules.md は削除済みで、内容は ir design 本文へ取り込まれている。全 3 か所：(1) 122 行付近 § 再確認が必要になる変更（Revalidation Triggers）：`specs/issue-request/item-rules.md`。(2) 222 行付近 § 論理データモデル（Logical Data Model） / 属性と型：`specs/issue-request/db-TWTGM140.md`・`db-TWTGM100.md`・`db-TWTGV050.md`・`db-TWTGV030.md`・`db-TWTGA150.md`・`db-TWTGA130.md`（6 件）。(3) 699 行付近 § 補足資料（Supporting References）の「テーブルの定義と変更履歴の手順」行：`specs/issue-request/db-TWTGM100.md`・`db-TWTGM140.md`。ir design 側に対応する節は実在する（`specs/issue-request/design.md` の見出しを確認済み）。 | 参照先を `specs/issue-request/design.md` の次の節（見出し）へ直す。(1) item-rules.md → 「#### 項目ごとの規則（Q-DS-IR-006）」。(2) db-TWTGM140.md → 「#### TWTGM140 の DB レイアウト（契約局情報ﾏｽﾀ。Q-DS-IR-004）」、db-TWTGM100.md → 「#### TWTGM100 の DB レイアウト（発行依頼書情報ﾏｽﾀ。Q-DS-IR-003）」、db-TWTGV050.md → 「#### TWTGV050 の DB レイアウト（契約局情報ﾄﾗﾝ。Q-DS-IR-013）」、db-TWTGV030.md → 「#### TWTGV030 の DB レイアウト（発行依頼書情報ﾄﾗﾝ。Q-DS-IR-013）」、db-TWTGA150.md → 「#### TWTGA150 の DB レイアウト（契約局情報変更履歴。Q-DS-IR-013）」、db-TWTGA130.md → 「#### TWTGA130 の DB レイアウト（発行依頼書情報変更履歴。Q-DS-IR-013）」。(3) 補足資料の行は参照先を `specs/issue-request/design.md`（「#### TWTGM100 の DB レイアウト…」「#### TWTGM140 の DB レイアウト…」。変更履歴の手順は「### データ契約と外部連携（Data Contracts &amp; Integration）」の「変更履歴の手順」）に書き換え、db-*.md の 2 件を外す。 | 修正：参照先の内容は ir design の実在する節にあり、パスと見出しを直すだけで解消するため | 確認済み |  |  |
| 2 | dependency-boundary-conformance | 業務の欠落・矛盾 | 重大 | 5e6e6d63da049fcb | c079a088446ab563 | specs/contract-info-import/design.md § バリデーション設計 / 列ごとの必須・桁・形式（検査表を正とする） ほか 1 か所（金額。指摘内容に記載） | 検査表と ir の項目ごとの規則の桁 | その他①〜④の桁が検査表で 100、ir の規則 2 と DB 列は 50 | 本書は列ごとの桁を検査表（_handoff/phase5-contract-info-import-checks.md）を正とし（§ バリデーション設計の冒頭・§ ドメインモデル / 検査）、テーブルの列と型は ir design のとおりとする（§ 論理データモデル / 属性と型）。ir design は項目ごとの規則を「契約情報取込の行のチェックの元」としている（ir design の § 補足資料の項目ごとの規則の行）。ir design の現在の値と検査表が食い違う。(a) その他①〜④：検査表 1-2 の No.215〜218 は「最大：100」。ir design の「#### 項目ごとの規則（Q-DS-IR-006）」の規則 2 は「その他①〜④ … 50」（ir は 100 から 50 に直した）で、DB 列 Sonota1〜4_Freeform（TWTGM100 の No.321・323・325・327、TWTGM140 の No.318・320・322・324）も 50。51〜100 バイトの値が区分 3 の検査を通ったまま洗替の INSERT で桁あふれし、「エラーなら全件取消し」（4.2・4.5）の前提を満たさない。(b) 金額[1-4]・初回金額[1-4]（同じ原因。同種の食い違い）：検査表 No.121・130・139・148・157・166・175・184 は「最大：50 ※14」。ir design の規則 4 は金額を「11・数値、P72 の名称でも 11 バイト以内の数値でもない値は WTG-100016」としている（DB 列 Payment_FeeN_Freeform は 50）。取込でどちらの桁で検査するかが本書に書かれていない。備考（2000）・契約に関する特記事項（3000）は検査表側が ir に合わせて直してあり一致している。本回は検査表 1-2 の 228 列のうち、桁を持つ列を ir design の TWTGM100 の DB レイアウトと規則 2〜4 に照らして確認した（リバースデータ 381 列の 2-2・2-3 は全列を照合していない）。 | 本書の § バリデーション設計に、行チェックの桁は ir design の「項目ごとの規則（Q-DS-IR-006）」に合わせる旨と、検査表から外れる列（その他①〜④は 50）を明記し、検査表 No.215〜218 の桁も 50 に直す。金額[1-4]・初回金額[1-4]は、ir の 11 バイト以内の数値に合わせるか、検査表の 50 のままにして DB 列（50）で保存するかを決めて本書に書く。 | 修正：その他①〜④は DB 列が 50 で ir design が確定済みのため合わせる。金額の桁だけは取込で 11 と 50 のどちらにするか人の決定が要る | 確認済み |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-import | 7 | 1 | 修正 | 軽微（AIDD 内部の決まりごと）のため、AI が修正案で直す | system（自動） | 2026-10-09T20:05:39+09:00 |  |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-import | 7 | 2 | 修正 |  | masato-teramoto | 2026-10-09T20:07:00+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 8 | 2026-10-09T20:09:44+09:00 | ①② | ["specs/contract-info-import/design.md"] | {"specs/contract-info-import/design.md":"ae5933ac53ec20d549fb9d91ff896e06610778cf237b06837eb5c5941abd1692"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-import | 7 | 1 | feature:contract-info-import | 8 | system（自動）：再検査で再検出なし | 2026-10-09T20:12:44+09:00 |
| feature:contract-info-import | 7 | 2 | feature:contract-info-import | 8 | system（自動）：再検査で再検出なし | 2026-10-09T20:12:44+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:contract-info-import | 8 | specs/contract-info-import/design.md | masato-teramoto | 2026-10-09T20:13:40+09:00 | ae5933ac53ec20d549fb9d91ff896e06610778cf237b06837eb5c5941abd1692 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 5 | 2026-10-09T20:16:48+09:00 | ①② | ["specs/contract-info-download/design.md"] | {"specs/contract-info-download/design.md":"e365aaa3c25a50d9a24dad8e438b02ebc77d61278d53da5492b16a4a793311a1"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務のあいまい・不足 | 要判断 | 1ceb375aa2d72d29 | b7c642edd2a84eca | specs/contract-info-download/design.md § 補足資料（Supporting References） / 出力の定義・作業用テーブルとビュー ほか 2 か所 | 本書の正とした補足資料（csv-layout-wtg100・work-tables-wtg100） | 本書の正とした補足資料2件が削除済みで、381列等の定義が本文に無い | 【事実】design.md は削除済みの specs/contract-info-download/csv-layout-wtg100.md と specs/contract-info-download/work-tables-wtg100.md を「回答者の指示で本書の正」とし、参照先の欄（671 行・672 行）と冒頭の出典の表記（14 行）に置く。specs/contract-info-download/ には design.md と requirements.md しか無い（Glob で確認）。14 行は _handoff の原本パス（csv-layout-wtg100.md・work-tables-wtg100.md。実在する）と specs 側の写し 2 件を併記しており、実在しない specs 側のパスは 14 行 2 件・671 行 1 件・672 行 1 件の計 4 件。本文は「出力の定義」を 14 回（14・37・72・83・116・248・252・253×2・290・291×2・621・671 行）、「作業用テーブルの表」を 8 回（14・67・105・265・277・278×2・574 行）引いて定義を委ねている（「本書の正」「DDL の元」の語は 3 か所）。specs 配下でこの 2 ファイル名を指すのは本 design だけ（grep）。また、本 design 内に specs/issue-request/db-*.md・item-rules.md への参照は無い（grep で 0 件）。【本文だけで確定できるか】できない。本文にあるもの：381＝契約基本 46＋契約者①〜⑤ 各 27＋支払情報①〜④ 各 50 の枠数、契約者・支払の入れ方（旧を除く・区分と番号の昇順・支払有効期間TO が空・枠を超えた行は出さない）、並び、MS932・書き方、受電方法・契約者区分・法人_個人区分の値の形、No 6 と No 44 の見出しが同じこと、TWTGD050 が 60 列・TWTGD060 が実行ユーザーID＋381 列（String 500）という要約。本文に無いもの：(1) 381 列それぞれの見出し（No 1〜381。例として「契約基本_計画基地局番号」「契約者①_契約者番号」だけが出る）と、TWTGD060 の物理名（KEIKAKU_KICHIKYOKU_NO・CONSTRACT_CD_1 など 381 件）、(2) 各列の取得元（元の表の列・コードマスタ。例：No 12 住居_都道府県名←M05、No 34 更新形態←P07、No 41 UQ押印者_名称←P24、No 37 転貸借契約書名←P15）と、YYYY/MM/DD にする列の一覧（No 28〜31 ほか。本文は「出力の定義で YYYY/MM/DD にしている列だけ」と書くのみ）、(3) TWTGD050 の 60 列の列名・型・桁（USER_ID 20・DATA_SHUBETSU 9・SYORI_JYUN 85・FIELD_01〜FIELD_50 の桁 120/120/40/…/500・検索条件 4 列・SYORI_JYUN2 5）、(4) VWTGM010 のデータ種別ごとの列（1基本情報・2契約者・3支払情報で項目1〜50 に何を入れるか。別表は 56 行×3 種）と、検索条件 4 列の中身（登録状態の名称・代表契約局番・代表契約枝番・確定局番＝KICHIKYOKU_NO）、(5) TWTGD060 の列と FIELD_xx の対応（契約者①〜⑤・支払情報①〜④へ更新する列の突き合わせ）。このため、tasks が DDL（2 テーブルとビュー）と Pwtgo100CsvInfo の 381 件の @CsvColumn（position と name）を作る元が無く、テスト戦略の「見出し行が 381 の見出しのとおり」も照合先が無い。要件 3.1（契約情報取込のリバースデータと同じ 381 列）の中身を本文で確かめられない（ID 対応あり・内容未充足の意味判定）。【経緯】2026-10-09 に利用者が当該 2 ファイルと specs/issue-request/db-*.md・item-rules.md を削除済み。issue-request の design は補足資料の内容を本文へ取り込んで再承認、contract-info-import の design は削除済みの issue-request の補足資料への参照を直して再承認済み。原本は /home/kccs/Wing/_handoff/csv-layout-wtg100.md（381 行の項目表）と _handoff/work-tables-wtg100.md（TWTGD050 60 列、VWTGM010 の列表）に残っている。【参考】契約情報取込の design（697〜699 行）は _handoff/phase5-contract-info-import-reverse-381.md・checks.md を「回答者の指示で本書の正」として _handoff を直接指しており、application-status-search・print-report・issue-request-tutorial の各 design も _handoff を参照する。【重複】format-conformance（相対パス参照の参照先が存在しない）も同じ箇所・同じ原因を検出した。同じ原因は 1 件にまとめ、重大度の高い種類（業務のあいまい・不足）の本指摘に残した。 | 次から選ぶ（業務の事実＝どの資料を正にするかの決めが要るため、修正案は 1 つに決めない）。A 資料を戻す：_handoff の 2 ファイルを specs/contract-info-download/csv-layout-wtg100.md と work-tables-wtg100.md として置き直す。design は変えない。利用者が削除した方針と逆になる。B 本文へ取り込む：381 列の表・TWTGD050/TWTGD060・VWTGM010 の列表を design 本文（物理データモデルとデータ契約）へ移し、補足資料の 2 行は本文の節を指す形に直す（issue-request と同じ扱い）。design は大きく増え、契約情報取込のリバースの表と二重定義になる点は横断確認で確かめる。C _handoff の原本を正本にする：補足資料の 2 行と 14 行の出典を _handoff/csv-layout-wtg100.md・_handoff/work-tables-wtg100.md に直す（契約情報取込の design と同じ扱い）。_handoff が specs の外にあり、消えると再び定義が失われる。D 発注者の設計書を正本にする：発注者の資料（ファイル名・版・節を指定してもらう）を正とし、補足資料の 2 行をその資料に直す。資料の名前と置き場所は利用者が示す必要がある。いずれの場合も、取込側の表との列の並びの照合は横断確認で行う（Q-DS-CD-001 の 6）。 | 質問：4 案のどれを正本にするかは利用者が決める事実で、AI が決められない（利用者が既に資料を削除しており、A は意図と逆の可能性がある） | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| format-conformance | specs/contract-info-download/design.md § 補足資料（Supporting References） / 出力の定義・作業用テーブルとビュー | 削除済みの補足資料 2 件へのパス参照が切れている | verify:重複（traceabilityと同じ箇所・原因） |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / 検索条件 | 代表契約局番・代表契約枝番を前方一致にし、転貸借契約書名を足す（requirements 1.3 から意図して外れる） | answer:design-authoring-generate[contract-info-download] |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / ベンダー／施工会社の絞り込み | 計画マスタ（TWTBM080）を工事案件マスタの書き誤りと読む（requirements 2.1・2.2 から意図して外れる） | answer:design-authoring-generate[contract-info-download] |
| traceability | specs/contract-info-download/design.md § バリデーション設計 | サーバーで桁・形式を確かめない（requirements 4.1 から意図して外れる） | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § 判断 3 / ドメインモデル | 工事案件マスタに行が無い契約情報を出す点が security.md 285 行目の「既存の WTB と同じ方式」と違う | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § バリデーション設計 | サーバーでの桁・形式のチェックをしない点が security.md の入力検証と違う（逸脱は本文に記録済み） | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/contract-info-download/design.md § 技術スタック | 開発端末の JDK 1.8 が tech.md の JDK 1.7 と違う | answer:design-authoring-generate[property-basic-info] |
| traceability | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） / VWTGM010 ほか 1 か所 | 契約者①〜⑤の並びの「契約者区分」が、名称にした列かコードか本文で読めない | learned:design feature:contract-info-download 4-1 |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / CSV の値の形 | CSV の値の形で名称にする列が 3 つだけで、登録状態の「コード:名称」が抜けている | learned:design feature:contract-info-download 4-2 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 5 | 1 | 修正 |  | masato-teramoto | 2026-10-09T20:25:01+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 6 | 2026-10-09T20:28:49+09:00 | ①② | ["specs/contract-info-download/design.md"] | {"specs/contract-info-download/design.md":"5e7a77f99ee89f8f71b238e59461ec45685c230bcbc60e31731179c528e1f254"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | traceability | 業務のあいまい・不足 | 要判断 | adc4158e3776a4a0 | c506828f4414083f | specs/contract-info-download/design.md § 出力ボタンを押したときの流れ / 2 | 選んだ行の識別キー | 流れ2が選んだ行を「基地局番号＋枝番」と書き、計画基地局番号と別の列に読める | 取り込んだ「出力ボタンを押したときの流れ」2 は「選んだ行（基地局番号＋枝番）」と書く。同じ本文の流れ 3 と 4（「計画基地局番号＋枝番で突き合わせて」）、出力 CSV の項目定義の書き方（「契約基本情報 TWTGM010 の 計画基地局番号＋枝番」）、`### サービスインターフェース` の出力の入力（「選んだ行のキー（計画基地局番号＋枝番）」）と出力の手順 4 は、キーを計画基地局番号（KEIKAKU_KICHIKYOKU_NO）＋枝番としている。基地局番号（KICHIKYOKU_NO）は別の列で、CSV の先頭に置く行の判定に使う列でもあるため、流れ 2 だけが別の列を指すように読める。原本 `_handoff/work-tables-wtg100.md` 16 行目の表現をそのまま取り込んだもので、取り込みの誤りではなく原本由来の表現（意味判定。ID の対応ではなく本文内の食い違い）。 | 流れ 2 の「基地局番号＋枝番」を「計画基地局番号＋枝番」に直す（流れ 3・4、Service の出力の手順 4 と同じ）。原本どおりに取り込む決定を優先する場合は、この表現を残す理由を本文に 1 文添える。 | 修正：新しい業務の事実は要らず、本文の他の 5 か所と同じ「計画基地局番号＋枝番」に揃えれば足りるため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| traceability | specs/contract-info-download/design.md § VWTGM010 発行依頼書リバースデータビュー（3 つの SELECT を UNION ALL。データ種別で列の意味が変わる） / 2契約者 No 6 | 契約者①〜⑤の並びの「契約者区分」が、名称にした列かコードか読めない（取り込んだ表にも残る） | learned:design feature:contract-info-download 4-1 |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / CSV の値の形 | 名称にする列を 3 つだけ挙げ、登録状態の「コード:名称」が抜けている（取り込んだ表 No 9 に定義がある） | learned:design feature:contract-info-download 4-2 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 5 | 1 | feature:contract-info-download | 6 | system（自動）：再検査で再検出なし | 2026-10-09T20:33:21+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| feature:contract-info-download | 6 | 1 | 修正 | AI 推奨を採用: 新しい業務の事実は要らず、本文の他の 5 か所と同じ「計画基地局番号＋枝番」に揃えれば足りるため | masato-teramoto | 2026-10-09T20:34:14+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 7 | 2026-10-09T20:36:58+09:00 | ①② | ["specs/contract-info-download/design.md"] | {"specs/contract-info-download/design.md": "a62d04a8fd56bd8271c36c4a4050f14d14b25984f95c453c74159f177c33520c"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 6 | 1 | feature:contract-info-download | 7 | system（自動）：再検査で再検出なし | 2026-10-09T20:40:44+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:contract-info-download | 7 | specs/contract-info-download/design.md | masato-teramoto | 2026-10-09T20:42:02+09:00 | a62d04a8fd56bd8271c36c4a4050f14d14b25984f95c453c74159f177c33520c |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 4 | 1 | 対応せず進める | Phase 5 の最後の上流まとめ直しと横断確認で扱う | feature:contract-info-download | 7 |
| feature:contract-info-download | 4 | 2 | 対応せず進める | Phase 5 の最後の上流まとめ直しと横断確認で扱う | feature:contract-info-download | 7 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| cross | 3 | 2026-10-09T20:43:33+09:00 | ② | ["specs/property-basic-info/design.md","specs/issue-request/design.md","specs/issue-request-tutorial/design.md","specs/print-report/design.md","specs/application-status-search/design.md","specs/contract-info-import/design.md","specs/contract-info-download/design.md"] | {"specs/property-basic-info/design.md":"03331555d6ee0825bd90f023f17f4951d532f97b0f4bde7b7f50878d4cc4da03","specs/issue-request/design.md":"8cf01f68fe35f51ecb925f5258243beb7a476500279d2757c8a0a7788c2917ec","specs/issue-request-tutorial/design.md":"d7c594a832cbe0fbab57395810305bccadf57f10983df788ca4e850bd0c1084a","specs/print-report/design.md":"e6d65db63292a5733f32042793e645f314b884f64423bea613d93d7f2d8fb620","specs/application-status-search/design.md":"b0d59adc5f67c4377772191bd6d81adc4234cdaf73d7f61c30eac704d697f0fa","specs/contract-info-import/design.md":"ae5933ac53ec20d549fb9d91ff896e06610778cf237b06837eb5c5941abd1692","specs/contract-info-download/design.md":"a62d04a8fd56bd8271c36c4a4050f14d14b25984f95c453c74159f177c33520c"} | 3 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ssot-consistency | 業務の欠落・矛盾 | 重大 | d0c4e386e9a5747c | ab050ce8579d9542 | specs/contract-info-download/design.md § 出力 CSV の項目定義（381 列） / 項目一覧 No.44 ほか 7 か所 | 381 列の見出し | 出力 CSV の見出し 8 件が取込のリバース表と違い、No.44 は予備項目3 が基地局名_ｶﾅ | 契約情報ダウンロード design の項目一覧（464〜844 行）の 381 行と、契約情報取込のリバース表（`_handoff/phase5-contract-info-import-reverse-381.md`。ci design 697 行が「回答者の指示で本書の正」と指す。入力一覧外だが依頼により比較）を No.1〜381 の全行で突き合わせた。並び（No の順・列数 381）は全行で一致。見出しの違いは次の 8 件だけ（CD の見出し ／ リバース表の見出し）。No.17 契約基本_住居_カナ ／ 契約基本_住居_ｶﾅ。No.23 契約基本_登記_カナ ／ 契約基本_登記_ｶﾅ。No.44 契約基本_基地局名_ｶﾅ（No.6 と同じ見出しが重複する。値は YOBI_KOMOKU3）／ 契約基本_予備項目3。No.64 契約者①_カナ ／ 契約者①_ｶﾅ。No.91 契約者②_カナ ／ 契約者②_ｶﾅ。No.118 契約者③_カナ ／ 契約者③_ｶﾅ。No.145 契約者④_カナ ／ 契約者④_ｶﾅ。No.172 契約者⑤_カナ ／ 契約者⑤_ｶﾅ。CD design 456〜457 行は No.6 と No.44 が同じ見出しになること、ｶﾅ と カナ の混在を表のとおり出すことを明記している。ci design 192 行は「リバースデータの 381 列の並びはリバースの表（契約情報ダウンロードの出力と同じ。見出しの文字は見ない）」と書くため、取込の動作には影響しないが、「同じ」とする 2 つの文書で見出しの文字が違う。CD design 83 行・ci design 192 行は、並びが同じことを横断確認で確かめるとしている。 | 案 A：CD の見出しを取込側に合わせる（No.17・23・64・91・118・145・172 を「ｶﾅ」、No.44 を「契約基本_予備項目3」）。案 B：取込側の表（design の外の資料）を CD に合わせる。案 C：現状のまま（取込は見出しを見ないので、No.44 の重複見出しを許す）と決める。 | 質問：見出しの文字はどちらを正とするか。取込は見出しを見ないので動作には影響しない | 確認済み |  |  |
| 2 | ssot-consistency | 業務の欠落・矛盾 | 重大 | 01bb32e190ab9e96 | ab050ce8579d9542 | specs/contract-info-download/design.md § 出力 CSV の項目定義（381 列） / 項目一覧「取込側の型・バイト数」列 No.5 ほか 40 か所 | 取込側の型・バイト数 | 項目一覧の「取込側の型・バイト数」41 行が、取込のリバース表の型・桁と食い違う | CD design 460 行は「取込側の型・バイト数」を「契約情報取込で受け取るときの型・バイト数で、参考」とするが、取込のリバース表（`_handoff/phase5-contract-info-import-reverse-381.md`。ci design 697 行が正）と 41 行で値が違う（CD ／ リバース表）。No.5・6：ー 120 ／ ー ー。No.35：全角 2 ／ 全角 ー。No.57：数値 10⇒11 ／ 数値 10。No.59：半角 8⇒7 ／ 半角 8。契約者②：No.75 全角 100 ／ 全角 2、No.76 全角 100 ／ 全角 40、No.78 全角 100 ／ 全角 120、No.79・81 半角 100 ／ 半角 160、No.80 全角 100 ／ 全角 160、No.84 数値 10⇒11 ／ 数値 10、No.87 全角 ー ／ 全角 50、No.88 全角 100 ／ 全角 50。契約者③：No.102 全角 100 ／ 全角 2、No.103 全角 100 ／ 全角 40、No.104 全角 ー ／ 全角 2、No.105 全角 100 ／ 全角 120、No.106・108 半角 100 ／ 半角 160、No.107 全角 100 ／ 全角 160、No.114 全角 ー ／ 全角 50、No.115 全角 100 ／ 全角 50。契約者④：No.129 全角 100 ／ 全角 2、No.130 全角 100 ／ 全角 40、No.132 全角 100 ／ 全角 120、No.133・135 半角 100 ／ 半角 160、No.134 全角 100 ／ 全角 160、No.141 全角 ー ／ 全角 50、No.142 全角 100 ／ 全角 50。契約者⑤：No.156・157・159〜162・168・169 が ④ と同じ違い（No.156 全角 100 ／ 全角 2、No.157 全角 100 ／ 全角 40、No.159 全角 100 ／ 全角 120、No.160・162 半角 100 ／ 半角 160、No.161 全角 100 ／ 全角 160、No.168 全角 ー ／ 全角 50、No.169 全角 100 ／ 全角 50）。No.184：ー 2 ／ ー ー。No.221：ー 60 ／ ー ー。契約者①（No.47〜73）は「⇒」付きで取込側の表と合っているが、②〜⑤ は古い値のまま。取込側の表を正とするのが ci design の指示。 | 「取込側の型・バイト数」の列を、取込のリバース表の型・桁に合わせて直す。または参考列を削り、契約情報取込のリバース表を参照するだけにする。 | 修正：取込のリバース表が正と ci design が定めており、どちらに合わせるかは決まっているため | 確認済み |  |  |
| 3 | ssot-consistency | 文書間の参照 | 軽微 | fc6dee8b1e6f7183 | 7e14ff52e562ef5e | specs/issue-request/design.md § 再確認が必要になる変更（Revalidation Triggers） / TWTGM100・TWTGM140 の列の変更（128 行） | TWTGM100・TWTGM140 を読む側の列挙 | 128 行の読む側に契約情報ダウンロードを挙げるが読まず、申請状況検索一覧が漏れている | ir design 128 行は TWTGM100・TWTGM140 の列の変更で再確認が要る側を「印刷・閲覧用帳票、契約情報取込の洗替、契約情報ダウンロード、物件基本情報登録変更の出力 CSV」と挙げる。契約情報ダウンロード design は両テーブルを読まない（読むのは TWTGM010〜030・TWTBM010・TWTBM080・TWTZM040 と、TWTGM080 の Kichikyoku_No だけ。101・102・247・276〜278 行。247 行は「TWTGM140 は見ない」と明記。TWTGM100・TWTGM140 は同 design の本文に出てこない）。一方、申請状況検索一覧 design は TWTGM100（Anken_Syo_Grp_Cd・Sonota1・Sonota1_Freeform・First_Pay_Day1〜4・Keiyaku_Ringi_Kiansha_Kaisha_Cd・_Name・Keiyaku_Ringi_Kiansha_Name）と TWTGM140 を読み（98・113・190〜212・241 行）、自身の再確認の項目にも ir design・pbi design の列の変更を挙げる（113 行）が、ir design の 128 行には挙がっていない。TWTGM100 の列を変えても、申請状況検索一覧への再確認が ir 側から出ない。前者（契約情報ダウンロードが読まない）は upstream-carryover に気づきとして記録済みで、後者は今回新しく分かった。feature-list の依存列（申請状況検索一覧は物件基本情報登録変更だけ）と実態のずれ（upstream-carryover 記録済み）も同じ原因の延長で、新しい閉路にはならない（申請状況検索一覧 → 発行依頼書は DB の読取りだけで、逆向きの辺は無い）。 | 128 行の括弧書きを「印刷・閲覧用帳票、申請状況検索一覧、契約情報取込の洗替、物件基本情報登録変更の出力 CSV」に直す（契約情報ダウンロードを外し、申請状況検索一覧を足す）。 | 修正：事実は両 design の本文で確認でき、業務の新しい事実は要らないため | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| ssot-consistency | specs/property-basic-info/design.md § 物理データモデル（Physical Data Model） / TWTGM140 ほか 1 か所 | TWTGM140 の全 345 列の定義が ir design の本文にあり、持ち主の pbi design が別の言い方で参照している（削除済みの補足資料の指しも、pbi design の直しとして記録済み） | learned:design cross 2-2 |
| ssot-consistency | specs/property-basic-info/design.md § API 契約（API Contract） / 契約局情報欄に出す列 | 契約者の条件が契約者区分 "01" で、ir design の値（1:契約者・2:関係者）と合わない | learned:design cross 2-3 |
| ssot-consistency | specs/property-basic-info/design.md § 判断 2 ほか | 発行依頼書登録変更の更新が申請の排他用の値を変えない扱い（案 A） | learned:design cross 2-1 |
| ssot-consistency | specs/issue-request-tutorial/design.md § 概要・データ契約 / pwtgo081ZoomForm.html・ウインドウ名 pwtgo081・json.clear が ir design の公開契約に無い | ir design の受け渡し（ウインドウ名＋callback。値の名前）とチュートリアルの pwtgo081callback・値の名前は矛盾せず、無い部分は design に明記され upstream-carryover に記録済み | verify:既決（upstream-carryover の issue-request の項目。両 design が明記済みで矛盾は無い） |
| ssot-consistency | specs/application-status-search/design.md § 依存してよい対象（Allowed Dependencies） | feature-list の依存列（物件基本情報登録変更だけ）と、TWTGM100 を読む実態のずれ | verify:既決（upstream-carryover の application-status-search の項目。design が自ら明記。ir design 側の列挙漏れは指摘 3 で出した） |
| ssot-consistency | specs/contract-info-import/design.md § バリデーション設計 / 検査表から外れる桁 | その他①〜④の桁 50 は ir design 規則 2・DB 列と一致。金額・初回金額の桁 50 は ir design 規則 4（11 バイト以内の数値）と異なるが、ci design が人の決定（2026-10-09）として明記済み | verify:既決（ci design に人の決定として明記済みで、本文の食い違い自体が宣言されている） |
| ssot-consistency | steering/api-standards.md § 画面内で JSON を返す口 | 画面内 JSON 口のエラーの返し方は口ごとに違う | verify:既決（upstream-carryover の「design 横断確認 1 回目で決まったもの」。横断確認 1 回目 #5 の案 B） |
| dependency-cycle-detection | specs/*/design.md の API 契約（pbi と ci・pbi と AS・ci → AS・pbi と print-report・pbi と cd・ir と tutorial） | 画面の遷移・戻り・コールバックと WTG 共通部品への呼出しで、各 design の依存してよい対象は一方向。feature 間の閉路は構成しない | verify:画面の遷移・戻り・コールバックと WTG 共通部品への呼出しは feature 間の依存の辺にならない |
| steering-conformance | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） | 作業用テーブル TWTGD050・TWTGD060 が共通列を持たない（steering/database.md の共通カラム） | answer:design-authoring-generate[contract-info-download] |
| steering-conformance | specs/issue-request/design.md § 物理データモデル（Physical Data Model）・論理データモデル | トランの種別 V（steering/database.md はトラン F）、金額・調整額を文字で持つ（金額は数値） | answer:design-authoring-generate[issue-request] |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 3 | 1 | 対応せず進める | 見出しの文字は取込の動作に影響しないので後の工程で決める | masato-teramoto | 2026-10-09T20:54:51+09:00 | 後で決める |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 3 | 2 | 修正 | AI 推奨を採用: 取込のリバース表が正と ci design が定めており、どちらに合わせるかは決まっているため | masato-teramoto | 2026-10-09T20:54:55+09:00 |  |  | 採用 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 3 | 3 | 修正 | AI 推奨を採用: 事実は両 design の本文で確認でき、業務の新しい事実は要らないため | masato-teramoto | 2026-10-09T20:55:00+09:00 |  |  | 採用 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 8 | 2026-10-09T20:58:35+09:00 | ①② | ["specs/contract-info-download/design.md"] | {"specs/contract-info-download/design.md": "27ba55f3a7a9e22056ad895471864d26e75d5cfc687e37a50f384120f2a263d0"} | 0 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| feature:contract-info-download | 8 | specs/contract-info-download/design.md | masato-teramoto | 2026-10-09T21:02:19+09:00 | 27ba55f3a7a9e22056ad895471864d26e75d5cfc687e37a50f384120f2a263d0 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| feature:contract-info-download | 4 | 1 | 対応せず進める | Phase 5 の最後の上流まとめ直しと横断確認で扱う | feature:contract-info-download | 8 |
| feature:contract-info-download | 4 | 2 | 対応せず進める | Phase 5 の最後の上流まとめ直しと横断確認で扱う | feature:contract-info-download | 8 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| cross | 4 | 2026-10-09T21:04:12+09:00 | ② | ["specs/property-basic-info/design.md", "specs/issue-request/design.md", "specs/issue-request-tutorial/design.md", "specs/print-report/design.md", "specs/application-status-search/design.md", "specs/contract-info-import/design.md", "specs/contract-info-download/design.md"] | {"specs/property-basic-info/design.md": "03331555d6ee0825bd90f023f17f4951d532f97b0f4bde7b7f50878d4cc4da03", "specs/issue-request/design.md": "8cf01f68fe35f51ecb925f5258243beb7a476500279d2757c8a0a7788c2917ec", "specs/issue-request-tutorial/design.md": "d7c594a832cbe0fbab57395810305bccadf57f10983df788ca4e850bd0c1084a", "specs/print-report/design.md": "e6d65db63292a5733f32042793e645f314b884f64423bea613d93d7f2d8fb620", "specs/application-status-search/design.md": "b0d59adc5f67c4377772191bd6d81adc4234cdaf73d7f61c30eac704d697f0fa", "specs/contract-info-import/design.md": "ae5933ac53ec20d549fb9d91ff896e06610778cf237b06837eb5c5941abd1692", "specs/contract-info-download/design.md": "27ba55f3a7a9e22056ad895471864d26e75d5cfc687e37a50f384120f2a263d0"} | 1 |

### 指摘

| # | 観点 | 種類 | 重大度 | 同一性キー | 節ハッシュ | 対象箇所 | 対象の語 | 要約 | 指摘内容 | 修正案 | 推奨 | 確かめ役 | 判断 | 理由 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ssot-consistency | 文書間の参照 | 軽微 | fc6dee8b1e6f7183 | 7e14ff52e562ef5e | specs/issue-request/design.md § 再確認が必要になる変更（Revalidation Triggers） / TWTGM100・TWTGM140 の列の変更（128 行） | TWTGM100・TWTGM140 を読む側の列挙 | 128 行の読む側に契約情報ダウンロードを挙げるが読まず、申請状況検索一覧が漏れている | 前回（3 回目 #3）と同じ内容で、design は未修正（ir design 128 行は変更なし）。ir design 128 行は TWTGM100・TWTGM140 を読む側として「印刷・閲覧用帳票、契約情報取込の洗替、契約情報ダウンロード、物件基本情報登録変更の出力 CSV」を挙げる。しかし contract-info-download design は TWTGM100・TWTGM140 のテーブルを読まない（247 行「複数局の申請でも見るのはこの 1 つだけで、`TWTGM140` は見ない」。依存先 101〜105 行は TWTGM010〜030・TWBM010・TWBM080・TWTZM040・TWTGM080 の Kichikyoku_No・コードマスタのみ。TWTGM100／TWTGM140 の語は同 design にこの 1 か所だけ）。一方 application-status-search design は 98 行で TWTGM140 を読み、TWTGM100 を外部結合で読むと書く（本 feature は読むだけ）。そのため ir design の Revalidation Triggers の読む側に、application-status-search が無い。また契約情報取込が洗替で TWTGM100・TWTGM140 を書く側である点は同行の「洗替」で表されている。 | ir design 128 行の読む側から「契約情報ダウンロード」を外し、「申請状況検索一覧」（application-status-search。TWTGM100・TWTGM140 を読む）を足す。 | 修正：事実は両 design の本文で確認でき、業務の新しい事実は要らない（人の指示で Phase 5 の他の修正は対象外とする方針があるため、扱いは人の判断による） | 確認済み |  |  |

### 除外

| 観点 | 対象箇所 | 要約 | 除外の出典 |
|---|---|---|---|
| ssot-consistency | specs/property-basic-info/design.md § 判断 2: 申請単位の排他を物件申請情報の排他用の値 1 つで行う ほか 4 か所 | 発行依頼書登録変更の更新は申請の排他用の値を変えず、物件基本情報の排他の前提と食い違う | learned:design cross 2-1 |
| ssot-consistency | specs/property-basic-info/design.md § 物理データモデル（Physical Data Model） / TWTGM140 ほか 1 か所 | TWTGM140の全345列の定義がir側の資料にだけあり、持ち主のpbi designは別の言い方で参照しない | learned:design cross 2-2 |
| ssot-consistency | specs/property-basic-info/design.md § API 契約（API Contract） / 契約局情報欄に出す列 | 契約局情報欄の契約者の条件が契約者区分 "01" で、発行依頼書の値（1:契約者）と合わない | learned:design cross 2-3 |
| traceability | specs/contract-info-download/design.md § 物理データモデル（Physical Data Model） / VWTGM010 ほか 1 か所 | 契約者①〜⑤の並びの「契約者区分」が、名称にした列かコードか本文で読めない | learned:design feature:contract-info-download 4-1 |
| traceability | specs/contract-info-download/design.md § ドメインモデル（Domain Model） / CSV の値の形 | CSV の値の形で名称にする列を 3 つだけ挙げ、登録状態の「コード:名称」が抜けている | learned:design feature:contract-info-download 4-2 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| cross | 3 | 2 | cross | 4 | system（自動）：再検査で再検出なし | 2026-10-09T21:07:52+09:00 |
| cross | 3 | 3 | cross | 4 | system（自動）：同じ指摘を 4 回目 #1 へ引き継ぎ | 2026-10-09T21:07:52+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 | 却下区分 | 今後も同じ扱い | 推奨の採用 |
|---|---|---|---|---|---|---|---|---|---|
| cross | 4 | 1 | 対応せず進める | Phase 5 では他の修正は対象外とする（ユーザー指示） | masato-teramoto | 2026-10-09T21:08:14+09:00 | 対象外 |  | 不採用 |

## 確認

| スコープ | 回数 | 確認者 | 日時 | 原本SHA256 |
|---|---|---|---|---|
| cross | 4 | masato-teramoto | 2026-10-09T21:08:49+09:00 | {"specs/property-basic-info/design.md": "03331555d6ee0825bd90f023f17f4951d532f97b0f4bde7b7f50878d4cc4da03", "specs/issue-request/design.md": "8cf01f68fe35f51ecb925f5258243beb7a476500279d2757c8a0a7788c2917ec", "specs/issue-request-tutorial/design.md": "d7c594a832cbe0fbab57395810305bccadf57f10983df788ca4e850bd0c1084a", "specs/print-report/design.md": "e6d65db63292a5733f32042793e645f314b884f64423bea613d93d7f2d8fb620", "specs/application-status-search/design.md": "b0d59adc5f67c4377772191bd6d81adc4234cdaf73d7f61c30eac704d697f0fa", "specs/contract-info-import/design.md": "ae5933ac53ec20d549fb9d91ff896e06610778cf237b06837eb5c5941abd1692", "specs/contract-info-download/design.md": "27ba55f3a7a9e22056ad895471864d26e75d5cfc687e37a50f384120f2a263d0"} |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| cross | 2 | 1 | 対応せず進める | 案 A の扱い（発行依頼書登録変更の更新・一時保存は TWTGM080 を更新せず、排他用の値が変わるのは発番のときだけ）。pbi design の文言は upstream-carryover に足し、Phase 5 の最後にまとめて直す | cross | 4 |
| cross | 2 | 2 | 対応せず進める | pbi design から specs/issue-request/db-TWTGM140.md を指す修正を upstream-carryover に足し、Phase 5 の最後にまとめて直す | cross | 4 |
| cross | 2 | 3 | 対応せず進める | 契約者区分は 1:契約者・2:関係者（"01" は回答者の取り違え）。pbi design の直しは upstream-carryover に足し、Phase 5 の最後にまとめて直す | cross | 4 |
| cross | 3 | 1 | 対応せず進める | 見出しの文字は取込の動作に影響しないので後の工程で決める | cross | 4 |
| cross | 4 | 1 | 対応せず進める | Phase 5 では他の修正は対象外とする（ユーザー指示） | cross | 4 |
