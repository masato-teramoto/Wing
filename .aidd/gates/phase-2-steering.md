---
format_version: 2
phase: steering
created_at: 2026-10-01T17:00:40+09:00
---

# ゲート記録

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 1 | 2026-10-01T17:00:40+09:00 | ① | ["steering/product.md", "steering/tech.md", "steering/architecture.md", "steering/security.md", "steering/non-functional.md", "steering/database.md", "steering/api-standards.md"] | {"steering/product.md": "e2019e35953898d251801920d5c4d36bc5c8418ba8d3e2ac95cf2b0808169367", "steering/tech.md": "df7defa3e316b5c3563d2576eff5d10d8d7fd8757e374d985a4e62301cc91e50", "steering/architecture.md": "d57f6500969a5a92e72a02fd60b7f609c45ec4e7ba1df56cced8d0340e9768d2", "steering/security.md": "fe6a799ac0ba8b2b709535154ad28cb13df53cad50eedb00fa1617b92c14df1c", "steering/non-functional.md": "386d92f4b4e572cd4bda280c7b2d0ce4757ad16f8344053aa65547ebacdcb24d", "steering/database.md": "52256e748a53199269dc75629e4ab3c747100c3ac2485bacf89f762cdfb96b56", "steering/api-standards.md": "70eca8d2facbf08bfa22cf1ae1e781219ecab2066bb8129bf4a3414b0fdeddc1"} | 1 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | format-conformance | steering/tech.md / ## テスト方針 &gt; ### 配置 / 命名 &gt; #### 配置パターン（パターン表） | プレースホルダー削除: テンプレート（Templates/steering/tech.md）の配置パターン表は 2 行目に `&lt;TEST_LAYOUT_PATTERN_ALT&gt;` / `&lt;TEST_LAYOUT_EXAMPLE_ALT&gt;` / `&lt;TEST_LAYOUT_NOTE_ALT&gt;` を持つが、成果物の表は 1 行目（PRIMARY）だけで、この 3 つのプレースホルダーが値にも不要理由付きの残置にもならず消えている（`_N` の可変スロットではない固定スロット。保持が規約） |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 1 | 1 | 修正 | 消した2行目を戻す。3つの欄は不要とし、理由は「自動テストは必須でないため、基本の置き場所以外は定めない」。ほかの6ファイルにも同じ消し方が無いか確かめて、あれば同じく戻す。修正後に①②で再検査する | Junichi Noumi | 2026-10-01T17:45:02+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 2 | 2026-10-01T17:46:26+09:00 | ①② | ["steering/product.md", "steering/tech.md", "steering/architecture.md", "steering/security.md", "steering/non-functional.md", "steering/database.md", "steering/api-standards.md"] | {"steering/product.md": "e2019e35953898d251801920d5c4d36bc5c8418ba8d3e2ac95cf2b0808169367", "steering/tech.md": "64e88c56d90fdd369bab0a6c45f740d13616d72779920589dca735deff1a0b52", "steering/architecture.md": "d57f6500969a5a92e72a02fd60b7f609c45ec4e7ba1df56cced8d0340e9768d2", "steering/security.md": "fe6a799ac0ba8b2b709535154ad28cb13df53cad50eedb00fa1617b92c14df1c", "steering/non-functional.md": "386d92f4b4e572cd4bda280c7b2d0ce4757ad16f8344053aa65547ebacdcb24d", "steering/database.md": "52256e748a53199269dc75629e4ab3c747100c3ac2485bacf89f762cdfb96b56", "steering/api-standards.md": "70eca8d2facbf08bfa22cf1ae1e781219ecab2066bb8129bf4a3414b0fdeddc1"} | 21 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | traceability | .aidd/requirement-list.md REQ-046 / steering 7ファイル（steering/database.md `## マイグレーション` ほか） | 未反映（層② 意味判定: ID対応なし・内容未充足）: REQ-046「データ移行については、発注者にてテストを実施することを前提とする」が steering のどこにも反映されていない。database.md `## マイグレーション` は DDL の作成と適用だけを扱い、データ移行とそのテストの分担の記述が無い |  |  |
| 2 | traceability | .aidd/requirement-list.md REQ-062 / steering/tech.md `### Git 戦略`・steering/non-functional.md `## デプロイ / リリース` | 未反映（層② 意味判定: ID対応なし・内容未充足）: REQ-062「PJ期間中の月次保守でプログラム改修を行う場合、WTG_契約・管財管理機能は対象外とする（案件と同時リリースとする場合は対応可能）」が反映されていない。案件ブランチから master へのマージとリリースの記述に、PJ 期間中の月次保守との並行改修・同時リリースの扱いが無い |  |  |
| 3 | traceability | .aidd/requirement-list.md REQ-047 / steering 7ファイル（該当なし） | 未反映（層② 意味判定: ID対応なし）: REQ-047（工期・体制・見積りは提案者が提案し、第7章のマイルストーンは発注者の希望日程）に対応する記述が steering 7ファイルに無い。steering のテンプレートにはプロジェクト管理事項を受ける節が無く、steering の対象外とするかは人間の判断が要る |  |  |
| 4 | traceability | .aidd/requirement-list.md REQ-048 / steering 7ファイル（該当なし） | 未反映（層② 意味判定: ID対応なし）: REQ-048（議事録は定例毎に納品する）に対応する記述が steering 7ファイルに無い。steering のテンプレートにはプロジェクト管理事項を受ける節が無く、steering の対象外とするかは人間の判断が要る |  |  |
| 5 | traceability | .aidd/requirement-list.md REQ-049 / steering 7ファイル（該当なし） | 未反映（層② 意味判定: ID対応なし）: REQ-049（工程完了報告書を各工程完了毎に納品する）に対応する記述が steering 7ファイルに無い。steering のテンプレートにはプロジェクト管理事項を受ける節が無く、steering の対象外とするかは人間の判断が要る |  |  |
| 6 | traceability | .aidd/requirement-list.md REQ-052 / steering 7ファイル（該当なし） | 未反映（層② 意味判定: ID対応なし）: REQ-052（RFP の概算スケジュール。確定日付として扱えるのは §7-1 のマイルストーンのみ）に対応する記述が steering 7ファイルに無い（REQ-051 は non-functional.md の環境・リリース承認に引用があるが、REQ-052 の引用・反映は無い）。steering の対象外とするかは人間の判断が要る |  |  |
| 7 | traceability | .aidd/requirement-list.md REQ-053 / steering 7ファイル（該当なし） | 未反映（層② 意味判定: ID対応なし）: REQ-053（実案件と同等以上の体制を提案する）に対応する記述が steering 7ファイルに無い。steering のテンプレートにはプロジェクト管理事項を受ける節が無く、steering の対象外とするかは人間の判断が要る |  |  |
| 8 | traceability | .aidd/requirement-list.md REQ-054 / steering 7ファイル（該当なし） | 未反映（層② 意味判定: ID対応なし）: REQ-054（プロジェクトオーナー・PM・PL の役割定義）に対応する記述が steering 7ファイルに無い。steering のテンプレートにはプロジェクト管理事項を受ける節が無く、steering の対象外とするかは人間の判断が要る |  |  |
| 9 | traceability | .aidd/requirement-list.md REQ-055 / steering 7ファイル（該当なし） | 未反映（層② 意味判定: ID対応なし）: REQ-055（ステアリングコミッティ・定例会議・個別検討会などの会議体の開催）に対応する記述が steering 7ファイルに無い。steering のテンプレートにはプロジェクト管理事項を受ける節が無く、steering の対象外とするかは人間の判断が要る |  |  |
| 10 | traceability | .aidd/requirement-list.md REQ-056 / steering 7ファイル（non-functional.md `#### エスカレーション` は不要理由付きのプレースホルダー） | 未反映（層② 意味判定: ID対応なし）: REQ-056（納期・品質・コストの重要課題をプロジェクト体制に従ってエスカレーションし協議の場を設定する）に対応する記述が無い。non-functional.md `#### エスカレーション` は障害対応のエスカレーションで、不要理由（回答 6）も保守運用についてのもの。steering の対象外とするかは人間の判断が要る |  |  |
| 11 | traceability | .aidd/requirement-list.md REQ-057 / steering/tech.md `### Git 戦略` | 未反映（層② 意味判定: ID対応なし・内容未充足）: REQ-057（情報共有には Backlog を使用する）の引用が無い。tech.md の Backlog はソース管理（Backlog の Git、ABA603）としての記述だけで、情報共有の手段としての方針は無い。steering の対象外とするかは人間の判断が要る |  |  |
| 12 | traceability | .aidd/requirement-list.md REQ-058 / steering 7ファイル（該当なし） | 未反映（層② 意味判定: ID対応なし）: REQ-058（Backlog の起票の入力規則）に対応する記述が steering 7ファイルに無い（tech.md のコミットメッセージ規則「課題キー＋内容」は起票規則とは別）。steering の対象外とするかは人間の判断が要る |  |  |
| 13 | traceability | .aidd/requirement-list.md REQ-059 / steering 7ファイル（該当なし） | 未反映（層② 意味判定: ID対応なし）: REQ-059（ドキュメントの提供元ごとの Backlog 格納場所）に対応する記述が steering 7ファイルに無い（tech.md `#### 運用ルール一覧` の仕様管理は steering・specs・docs のリポジトリ管理だけを定める）。steering の対象外とするかは人間の判断が要る |  |  |
| 14 | traceability | 全体方針チェック: 帳票 PDF 出力（REQ-016〜REQ-018） / steering/tech.md `## 主要ライブラリ`（PDF 変換）・`## コアテクノロジ`・`### 必須ツール`／steering/architecture.md `## アーキテクチャ概要` | 全体方針の不足（層② 意味判定）: tech.md の PDF 変換は「サーバー上の OpenOffice（localhost の 8100 番ポート）に接続して変換する」（回答 Q-STR-102）ことを前提とするが、OpenOffice は tech.md `## コアテクノロジ`（ランタイム）・`### 必須ツール` にも、architecture.md の構成・配置モデルにも無く、製品・版・どのサーバーに置くかが全体方針で決まっていない。既存の wing・WTX・WTX_Batch の本番の設定・コードにも OpenOffice の記述は見当たらない（WTX_Common のテストデータだけ） |  |  |
| 15 | ssot-consistency | steering/security.md `## 入力検証 / 出力エスケープ` &gt; `### 共通ルール` #1 ／ steering/tech.md `## 主要ライブラリ`（バリデーション）／ steering/security.md `### 入り口 — 入力検証`（画面の行） | 二重定義（食い違い）: 入力検証の方式。security.md 共通ルール #1 は「入力はサーバー側で必ず検査する（Bean Validation と `ValidationUtils`。回答 Q-STR-110）」とし、tech.md のバリデーションは「専用ライブラリの注釈は使わず、Service の `checkXxx` で `BindingResult.rejectValue` にエラーを積む手書き方式…hibernate-validator 5.0.1 の注釈は使われていない」とし、security.md の入り口の画面の行も手書き方式だけを書いている。7ファイルの分担ではライブラリの選定は tech.md が持つ。security.md 側の出典は人間の回答（Q-STR-110）、tech.md 側の出典は既存 wing の実装（`wing/src/main/java` に javax.validation の注釈の使用は無い）で、どちらに揃えるかは人間の確認が要る |  |  |
| 16 | ssot-consistency | steering/security.md `## セキュリティログ` #1 ／ steering/non-functional.md `#### 出力する` #2・#3 | 二重定義（同一内容）: 要求ごとのログ項目。security.md は「要求ごとに、利用者ID・グループID・機能ID・URI・接続元 IP・セッションID を記録する（LoggingInterceptor）」とし、non-functional.md は同じ LoggingInterceptor の機能ID・URI・接続元 IP・セッションID（と利用者ID・グループID）を出力項目として定めている。内容は同じで、引用（準拠）の形になっていない。security.md の分担文はログの形式と共通フィールドを non-functional.md `### ログ方針` を正とし、security.md には記録する対象と記録自体の守り方だけを書くとしている |  |  |
| 17 | ssot-consistency | steering/product.md `## ビジネスルール / ポリシー`（既存 WTG 機能の保全）／ steering/non-functional.md `## 基本方針` 3点目 | 二重定義（同一内容）: 既存の WTG 機能をデグレードさせない（REQ-044）という方針を、product.md のポリシーと non-functional.md の基本方針がそれぞれ記述しており、non-functional.md 側は product.md を引用（準拠）する形になっていない。7ファイルの分担ではシステム全体の業務上の決まりは product.md が持つ。non-functional.md で運用方針として別に持つ意図かは人間の確認が要る |  |  |
| 18 | steering-conformance | steering/security.md `#### 所有権・エンティティ境界`（パターン・検証タイミング） | 粒度の不足（steering と design.md のどちらで補うかの確認）: 社外ユーザーのデータ範囲を「計画マスタ（`TWTBM080`）の `Bs_Vendor_Cd` または `Motouke_Kaisya_Cd` が自社に一致するデータだけ」とする WTB の方式を書いているが、本プロジェクトの WTG のデータ（物件基本情報・発行依頼書・契約情報）を計画マスタへどう結び付けて判定するかの規則が無い。各 design.md はこの記述を参照するだけでは判定の結合先を決められず、feature ごとに独自解釈が生じうる（REQ-038・REQ-043・REQ-064。根拠: security.md `#### チェックの適用箇所` のデータ取得の行がこの節を参照） |  |  |
| 19 | iso25010-coverage | データガバナンス（信頼性/セキュリティの下位観点） / steering/non-functional.md・steering/architecture.md（参照: steering/security.md `## 機密データ`） | 保持期間・削除・越境移転の方針が無い: non-functional.md `#### 出力しない` は契約者の個人情報（氏名、住所、連絡先）を扱う前提だが、業務データ・個人情報の保持期間と削除の方針も、「不要」とその理由も無い（database.md `## バックアップ / リカバリ` の不要理由はバックアップに限られる）。security.md `## 機密データ` の種別もパスワードだけで、個人情報の扱いが無い。越境移転についても記述と不要理由が無い |  |  |
| 20 | iso25010-coverage | 互換性（クライアント環境） / steering/non-functional.md・steering/architecture.md（参照: steering/tech.md `### 推奨 OS / IDE`） | 利用者側のクライアント環境の方針が無い: 回答 6 はクライアントを Windows 11 と Edge と指定しているが、steering に利用者側の対応ブラウザ・クライアント環境の記述が無く、不要の理由も無い（tech.md の Windows 11 は開発端末の推奨 OS として書かれている） |  |  |
| 21 | stride-coverage | サービス拒否（Denial of Service） / steering/security.md | STRIDE の「サービス拒否」への対応方針（検知・防御・記録のいずれか）が security.md に無く、該当しない理由も無い（`## 攻撃対策（主要パターン）` にも該当する行が無い） |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 1 | 対応せず進める | データ移行のテストは発注者が行う前提で、システムの作り方を定める steering の対象外のため | Junichi Noumi | 2026-10-01T18:00:37+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 2 | 対応せず進める | 月次保守との並行改修の扱いは保守運用の取り決めで、steering の対象外のため | Junichi Noumi | 2026-10-01T18:00:38+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 3 | 対応せず進める | プロジェクト管理の事項で、steering の対象外のため | Junichi Noumi | 2026-10-01T18:00:39+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 4 | 対応せず進める | 同上 | Junichi Noumi | 2026-10-01T18:00:40+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 5 | 対応せず進める | 同上 | Junichi Noumi | 2026-10-01T18:00:41+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 6 | 対応せず進める | 同上 | Junichi Noumi | 2026-10-01T18:00:42+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 7 | 対応せず進める | 同上 | Junichi Noumi | 2026-10-01T18:00:43+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 8 | 対応せず進める | 同上 | Junichi Noumi | 2026-10-01T18:00:44+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 9 | 対応せず進める | 同上 | Junichi Noumi | 2026-10-01T18:00:45+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 10 | 対応せず進める | 同上 | Junichi Noumi | 2026-10-01T18:00:46+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 11 | 対応せず進める | 同上 | Junichi Noumi | 2026-10-01T18:00:47+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 12 | 対応せず進める | 同上 | Junichi Noumi | 2026-10-01T18:00:48+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 13 | 対応せず進める | 同上 | Junichi Noumi | 2026-10-01T18:00:49+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 14 | 修正 | tech.md のランタイムと必須ツール、architecture.md の配置に OpenOffice を足す。内容は「Tomcat と同じアプリケーションサーバーに常駐させ、localhost の 8100 番ポートで待ち受ける。版は本番サーバーに導入済みのものに従う」 | Junichi Noumi | 2026-10-01T18:00:50+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 15 | 修正 | tech.md に合わせる。入力検証は Service の checkXxx で BindingResult.rejectValue にエラーを積む方式とし、Bean Validation の注釈は使わない。security.md の共通ルール1を直す。Q-STR-110 の「Bean Validation と ValidationUtils」は誤りとして訂正する | Junichi Noumi | 2026-10-01T18:00:51+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 16 | 修正 | security.md の要求ごとのログ項目を消し、non-functional.md のログ方針に準拠する引用に置き換える | Junichi Noumi | 2026-10-01T18:00:52+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 17 | 修正 | non-functional.md の基本方針3点目を、product.md のポリシーへの引用に置き換える | Junichi Noumi | 2026-10-01T18:00:53+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 18 | 修正 | security.md に WTG の規則を足す。WTG の社内と社外の判定は、コードマスタ WTG の PARAM P71 で行う（キー3 がログインユーザーのグループ、文字項目1 が "1" なら社外）。社外ユーザーが見て操作できるのは、契約稟議起案会社が自社（P71 の文字項目2）のデータだけとする。社外ユーザーには一部の項目を表示せず、入力もさせない（どの項目かは各 feature で定める）。WTB の計画マスタによる方式は、WTG の新しいデータには使わない | Junichi Noumi | 2026-10-01T18:00:54+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 19 | 対応せず進める | 保持期間と削除は既存 WiNG の運用に従い、本案件では定めない。データは国内のサーバーだけで扱い、越境移転は無い | Junichi Noumi | 2026-10-01T18:00:55+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 20 | 修正 | non-functional.md に利用者のクライアント環境を足す。Windows 11 と Edge（WTZ 共通の非機能要求のとおり） | Junichi Noumi | 2026-10-01T18:00:56+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 21 | 対応せず進める | 社内と協力会社だけが使う既存 WiNG の基盤の対策に従い、本案件では定めない | Junichi Noumi | 2026-10-01T18:00:57+09:00 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 3 | 2026-10-01T18:01:56+09:00 | ①② | ["steering/product.md", "steering/tech.md", "steering/architecture.md", "steering/security.md", "steering/non-functional.md", "steering/database.md", "steering/api-standards.md"] | {"steering/product.md": "e2019e35953898d251801920d5c4d36bc5c8418ba8d3e2ac95cf2b0808169367", "steering/tech.md": "58cc32eb0ad29d7b7185bb02e710ce8d882e374f93eb0a609ae293e3903a4966", "steering/architecture.md": "98be0c57ba256c0aeaf1a66d69682e63b47d20ec0f91ab776589a54e5eb8c33d", "steering/security.md": "45a1baa66763e451328062e1c98c15291fa49a28701ef28b7fc8d96834531063", "steering/non-functional.md": "1c144434d7acefb1db259340ce3eb9c6a66ea45489c2cc89fd098b94bd1027e6", "steering/database.md": "52256e748a53199269dc75629e4ab3c747100c3ac2485bacf89f762cdfb96b56", "steering/api-standards.md": "70eca8d2facbf08bfa22cf1ae1e781219ecab2066bb8129bf4a3414b0fdeddc1"} | 2 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | ssot-consistency | steering/security.md `### 認証・認可の設計思想` 1点目・`#### 権限モデル`（採用理由）／ steering/product.md `## ビジネスルール / ポリシー`（権限による制御）／ steering/security.md `#### 所有権・エンティティ境界`（パターン） | 二重定義（食い違いの可能性）: 社外ユーザー（ベンダー／施工会社）の権限制御方式。security.md の設計思想は「既存 WTB と同様のベンダー／施工会社の権限制御方式に合わせ、本プロジェクトで別の方式を作らない（REQ-043）」、権限モデルの採用理由は「既存 WTB と同様の権限制御方式に合わせる」、product.md のポリシーは「既存 WTB と同様の権限制御方式に従う」と書いている。一方、今回直した所有権・エンティティ境界のパターンは「WTB の計画マスタ（`TWTBM080`）による方式は、WTG の新しいデータには使わない」とし、P71 と契約稟議起案会社で判定する。7ファイルの分担では認可の方式は security.md が持つ。「WTB と同様」が社外ユーザーを自社のデータに絞る考え方を指すのか、WTB の判定方式そのものを指すのかが読み分けられず、設計思想・採用理由・product.md の記述をパターンに合わせて直すかは人間の確認が要る |  |  |
| 2 | steering-conformance | steering/security.md `#### 所有権・エンティティ境界`（パターン）・`#### チェックの適用箇所`（データ取得の行） | 粒度の不足（steering と design.md のどちらで補うかの確認）: パターンは計画マスタの方式を「WTG の新しいデータには使わない」とするが、「新しいデータ」の範囲（物件基本情報・発行依頼書だけか、取込・ダウンロードで扱う契約情報も含むか）が無く、新しいデータに当たらない WTG のデータ（REQ-034・REQ-036〜REQ-039 の契約情報）にどちらの方式を使うかも書かれていない。既存の WTG のバッチ（`WTX_Batch/src/jp/co/kccs/wt/wtg/wtg110/PWTGB110Job.java`）は P71 で社外と判定したうえで `TWTBM080` で絞り込んでいる。各 design.md はこの記述を参照するだけでは契約情報の絞り込み方を決められず、feature ごとに独自解釈が生じうる |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 3 | 1 | 対応せず進める | 「WTB と同様」は、社外ユーザーを自社のデータに絞るという考え方を指す。判定の方式は所有権とエンティティ境界のパターンを正とする | Junichi Noumi | 2026-10-01T18:11:39+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 3 | 2 | 対応せず進める | 契約情報の取込とダウンロードでの絞り込み方は、Phase 4 と Phase 5 の各 feature で定める | Junichi Noumi | 2026-10-01T18:11:40+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 1 | 1 | phase | 3 | Junichi Noumi | 2026-10-01T18:11:41+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 14 | phase | 3 | Junichi Noumi | 2026-10-01T18:11:42+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 15 | phase | 3 | Junichi Noumi | 2026-10-01T18:11:43+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 16 | phase | 3 | Junichi Noumi | 2026-10-01T18:11:45+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 17 | phase | 3 | Junichi Noumi | 2026-10-01T18:11:46+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 18 | phase | 3 | Junichi Noumi | 2026-10-01T18:11:47+09:00 |

## 解消

| スコープ | 回数 | 指摘番号 | 再検査スコープ | 再検査回数 | 確認者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 2 | 20 | phase | 3 | Junichi Noumi | 2026-10-01T18:11:48+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 3 | steering/product.md | Junichi Noumi | 2026-10-01T18:11:49+09:00 | e2019e35953898d251801920d5c4d36bc5c8418ba8d3e2ac95cf2b0808169367 |
| phase | 3 | steering/tech.md | Junichi Noumi | 2026-10-01T18:11:49+09:00 | 58cc32eb0ad29d7b7185bb02e710ce8d882e374f93eb0a609ae293e3903a4966 |
| phase | 3 | steering/architecture.md | Junichi Noumi | 2026-10-01T18:11:49+09:00 | 98be0c57ba256c0aeaf1a66d69682e63b47d20ec0f91ab776589a54e5eb8c33d |
| phase | 3 | steering/security.md | Junichi Noumi | 2026-10-01T18:11:49+09:00 | 45a1baa66763e451328062e1c98c15291fa49a28701ef28b7fc8d96834531063 |
| phase | 3 | steering/non-functional.md | Junichi Noumi | 2026-10-01T18:11:49+09:00 | 1c144434d7acefb1db259340ce3eb9c6a66ea45489c2cc89fd098b94bd1027e6 |
| phase | 3 | steering/database.md | Junichi Noumi | 2026-10-01T18:11:49+09:00 | 52256e748a53199269dc75629e4ab3c747100c3ac2485bacf89f762cdfb96b56 |
| phase | 3 | steering/api-standards.md | Junichi Noumi | 2026-10-01T18:11:49+09:00 | 70eca8d2facbf08bfa22cf1ae1e781219ecab2066bb8129bf4a3414b0fdeddc1 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| phase | 3 | 1 | 対応せず進める | 「WTB と同様」は、社外ユーザーを自社のデータに絞るという考え方を指す。判定の方式は所有権とエンティティ境界のパターンを正とする | phase | 3 |
| phase | 3 | 2 | 対応せず進める | 契約情報の取込とダウンロードでの絞り込み方は、Phase 4 と Phase 5 の各 feature で定める | phase | 3 |
