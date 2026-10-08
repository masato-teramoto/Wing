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
