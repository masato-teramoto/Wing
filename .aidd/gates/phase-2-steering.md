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

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 4 | 2026-10-01T20:08:02+09:00 | ①② | ["steering/product.md", "steering/tech.md", "steering/architecture.md", "steering/security.md", "steering/non-functional.md", "steering/database.md", "steering/api-standards.md"] | {"steering/product.md": "f6dfe900256a1cf46840947c376e98b97b7fa10378caee69738615ddb2cb67d6", "steering/tech.md": "58cc32eb0ad29d7b7185bb02e710ce8d882e374f93eb0a609ae293e3903a4966", "steering/architecture.md": "98be0c57ba256c0aeaf1a66d69682e63b47d20ec0f91ab776589a54e5eb8c33d", "steering/security.md": "c5546222f23ea5d402a6637faec5c1054eba9aeb31a38ff3b75399be67e7341a", "steering/non-functional.md": "831016b1f41e7f6c4597559be5395ff3358283f3e2416f64e98a4d3f0902c314", "steering/database.md": "df811770e647124e79e310c0504232cd80834ec77d74f5b823be631ecd667db2", "steering/api-standards.md": "70eca8d2facbf08bfa22cf1ae1e781219ecab2066bb8129bf4a3414b0fdeddc1"} | 6 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | ssot-consistency | steering/security.md `## 基本方針` 5点目・`### 認証・認可の設計思想` 1点目・`#### 権限モデル`（採用理由）／ steering/security.md `#### 権限モデル`（モデル・定義の置き場・禁止） | 二重定義（食い違いの可能性）: 認可の方式。基本方針 5点目は「新しい認証・認可の仕組みを作らず、既存 wing の仕組みに乗せる（REQ-043・REQ-045）」、設計思想 1点目は「本プロジェクトで別の方式を作らない（REQ-043）」、採用理由は「既存 WTB と同様の権限制御方式に合わせる（REQ-043）」としている。一方、今回直した権限モデルは、承認フローで誰の番かを審査権限マスタ `TWTGM170` とコードマスタ `P82` で判定する段を加えている。`TWTGM170` は既存の wing・WTX・WTX_Batch・WTX_Common のソースに記述が見当たらず（WTX_Batch で見つかるのは `TWTGA130` だけ）、既存の仕組みでも WTB の方式でもない判定の段にあたる。7ファイルの分担では認可の方式は security.md が持ち、同じファイルの中で両立しない。Phase 2 3 回目 残件 1 の判断（「WTB と同様」は社外ユーザーを自社のデータに絞る考え方を指す）はデータ範囲についてのもので、承認フローの番の判定には及ばない。基本方針・設計思想・採用理由を権限モデルに合わせて直すかは人間の確認が要る |  |  |
| 2 | ssot-consistency | steering/security.md `#### チェックの適用箇所`（データ取得の行）／ steering/security.md `#### 所有権・エンティティ境界`（パターン） | 二重定義（食い違い）: 社外ユーザーのデータ範囲。データ取得の行は「社外ユーザーのとき、自社が関係するデータだけを検索条件で絞り込む」とし、今回直したパターンは「契約稟議起案会社が自社のデータと、その社外ユーザー本人が登録したデータだけ」とする。データ取得の行は参照先として `#### 所有権・エンティティ境界` を挙げているが、本文の「自社が関係するデータだけ」は本人が登録したデータ（契約稟議起案会社が未設定のものを含みうる）を含むかが読み取れず、引用（準拠）の形になっていない。7ファイルの分担では範囲の判定方法はパターンが持つ |  |  |
| 3 | ssot-consistency | steering/database.md `## 設計思想` 3点目 ／ steering/product.md `## ビジネスルール / ポリシー`（申請・承認の履歴） | 二重定義（同一内容）: 項目の変更履歴を持つ対象。product.md は「項目の変更履歴を持つのは発行依頼書（`TWTGA130`）だけとする」とし、database.md は product.md に「従う」と引用したうえで、「本案件では発行依頼書の `TWTGA130` だけが該当する」と同じ事実をもう一度書いている。内容は同じで食い違いは無い。7ファイルの分担ではシステム全体の業務上の決まりは product.md、表の種別（種別 `A` の履歴テーブル）は database.md が持つ。database.md 側の対象の列挙を引用だけにするかは人間の確認が要る |  |  |
| 4 | steering-conformance | steering/security.md `## 機密データ`（担当者の連絡先・契約者の個人情報の行）／ steering/security.md `#### 権限モデル`・`#### チェックの適用箇所`（画面の表示の行） | 粒度の不足（steering と design.md のどちらで補うかの確認）: 2 行とも「権限のある利用者にだけ表示し」とするが、どの権限を指すかが無い。権限モデルは画面を使える権限（`Kengen_Kbn`・`AccessControlInterceptor`）、承認フローの番（`TWTGM170`・`P82`）、社外ユーザーのデータ範囲、項目の出し分け（`TWTZM120`）を持ち、どれに当たれば表示してよいのかを各 design.md はこの記述を参照するだけでは決められない。feature ごとに独自解釈が生じうる（根拠: security.md `#### チェックの適用箇所` の画面の表示の行は、社外ユーザーに見せない項目を各 feature で定めるとしている） |  |  |
| 5 | steering-conformance | steering/product.md `## ビジネスルール / ポリシー`（申請・承認の履歴）／ steering/database.md `## 設計思想` 3点目 | 実体の混入（判断材料）: 物件基本情報の履歴は承認履歴 `TWTGM180` だけ、項目の変更履歴を持つのは発行依頼書の `TWTGA130` だけ、という個々のデータごとの履歴の持ち方と、その表名が書かれている。物件基本情報と発行依頼書で扱いが異なり、全 feature に等しく適用されるルールではないため、判定基準（steering は方針、spec は実体）に照らすと design.md 側の実体にあたる。記述は Phase 4 property-basic-info ゲート 1 回目 指摘15〜18 の差戻し指示に基づくもので、steering に置くかは人間の確認が要る |  |  |
| 6 | evidence-guard | steering/security.md `#### 所有権・エンティティ境界`（パターン） | 根拠の飛躍: パターンは社外ユーザーが見て操作できる範囲を「契約稟議起案会社が自社（P71 の文字項目2）のデータと、その社外ユーザー本人が登録したデータだけ」としているが、根拠とした差戻し指示（Phase 4 property-basic-info ゲート 1 回目 指摘15〜18）は「契約稟議起案会社が自社の申請と、本人が登録した申請とする」としており、対象は「申請」である。「データ」へ広げると、申請以外の WTG のデータ（取込・ダウンロードで扱う契約情報など）にも同じ範囲が当てはまる読み方になるが、その根拠は示されていない |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 4 | 1 | 対応せず進める | 認可の仕組みは既存のまま使う。承認フローで誰の番かは業務上の判定で、新しい認可の方式には当たらない。TWTGM170 は本案件で新しく作る審査権限マスタである | Junichi Noumi | 2026-10-01T20:17:59+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 4 | 2 | 対応せず進める | データ取得の行は、所有権とエンティティ境界のパターンに従う。範囲はパターンを正とする | Junichi Noumi | 2026-10-01T20:18:00+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 4 | 3 | 対応せず進める | 同じ内容で食い違いは無い。product.md を正とする | Junichi Noumi | 2026-10-01T20:18:02+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 4 | 4 | 対応せず進める | どの権限の利用者に表示するかは、各 feature の design で定める | Junichi Noumi | 2026-10-01T20:18:03+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 4 | 5 | 対応せず進める | 物件基本情報と発行依頼書で履歴の持ち方が違うことを全体で共有するため、steering に置く | Junichi Noumi | 2026-10-01T20:18:05+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 4 | 6 | 対応せず進める | このパターンは申請に当てはめる。申請以外のデータ（契約情報）の範囲は Phase 4 と Phase 5 で定める | Junichi Noumi | 2026-10-01T20:18:06+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 4 | steering/product.md | Junichi Noumi | 2026-10-01T20:18:08+09:00 | f6dfe900256a1cf46840947c376e98b97b7fa10378caee69738615ddb2cb67d6 |
| phase | 4 | steering/tech.md | Junichi Noumi | 2026-10-01T20:18:08+09:00 | 58cc32eb0ad29d7b7185bb02e710ce8d882e374f93eb0a609ae293e3903a4966 |
| phase | 4 | steering/architecture.md | Junichi Noumi | 2026-10-01T20:18:08+09:00 | 98be0c57ba256c0aeaf1a66d69682e63b47d20ec0f91ab776589a54e5eb8c33d |
| phase | 4 | steering/security.md | Junichi Noumi | 2026-10-01T20:18:08+09:00 | c5546222f23ea5d402a6637faec5c1054eba9aeb31a38ff3b75399be67e7341a |
| phase | 4 | steering/non-functional.md | Junichi Noumi | 2026-10-01T20:18:08+09:00 | 831016b1f41e7f6c4597559be5395ff3358283f3e2416f64e98a4d3f0902c314 |
| phase | 4 | steering/database.md | Junichi Noumi | 2026-10-01T20:18:08+09:00 | df811770e647124e79e310c0504232cd80834ec77d74f5b823be631ecd667db2 |
| phase | 4 | steering/api-standards.md | Junichi Noumi | 2026-10-01T20:18:08+09:00 | 70eca8d2facbf08bfa22cf1ae1e781219ecab2066bb8129bf4a3414b0fdeddc1 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| phase | 4 | 1 | 対応せず進める | 認可の仕組みは既存のまま使う。承認フローで誰の番かは業務上の判定で、新しい認可の方式には当たらない。TWTGM170 は本案件で新しく作る審査権限マスタである | phase | 4 |
| phase | 4 | 2 | 対応せず進める | データ取得の行は、所有権とエンティティ境界のパターンに従う。範囲はパターンを正とする | phase | 4 |
| phase | 4 | 3 | 対応せず進める | 同じ内容で食い違いは無い。product.md を正とする | phase | 4 |
| phase | 4 | 4 | 対応せず進める | どの権限の利用者に表示するかは、各 feature の design で定める | phase | 4 |
| phase | 4 | 5 | 対応せず進める | 物件基本情報と発行依頼書で履歴の持ち方が違うことを全体で共有するため、steering に置く | phase | 4 |
| phase | 4 | 6 | 対応せず進める | このパターンは申請に当てはめる。申請以外のデータ（契約情報）の範囲は Phase 4 と Phase 5 で定める | phase | 4 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 5 | 2026-10-02T10:48:23+09:00 | ①② | ["steering/product.md", "steering/tech.md", "steering/architecture.md", "steering/security.md", "steering/non-functional.md", "steering/database.md", "steering/api-standards.md"] | {"steering/product.md": "1efed322f96e4244b36b57ef6b9090ca82fe8aaa7c10d9ff51589d30dbe4b397", "steering/tech.md": "58cc32eb0ad29d7b7185bb02e710ce8d882e374f93eb0a609ae293e3903a4966", "steering/architecture.md": "98be0c57ba256c0aeaf1a66d69682e63b47d20ec0f91ab776589a54e5eb8c33d", "steering/security.md": "c46d9d175156e139f61c19d58e4b7fb3d7bc5e3c1e3c4395802c2bef449f6b8b", "steering/non-functional.md": "831016b1f41e7f6c4597559be5395ff3358283f3e2416f64e98a4d3f0902c314", "steering/database.md": "8eac00445a5e85e7b58e9659a0f4bad94bdbf8581846fcf56a693883a12ec681", "steering/api-standards.md": "70eca8d2facbf08bfa22cf1ae1e781219ecab2066bb8129bf4a3414b0fdeddc1"} | 4 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | traceability | .aidd/requirement-list.md REQ-027 ／ steering/product.md `## ビジネスルール / ポリシー`（申請・承認の履歴）／ steering/database.md `## 設計思想` 3点目 | 内容の食い違い（層② 意味判定: ID対応あり・内容未充足）: REQ-027 は「発行依頼書の履歴管理を行う（各申請・承認時に項目に変更があれば履歴テーブルへ登録する）」とするが、product.md のポリシーは REQ-027 を引用したうえで、発行依頼書（`TWTGA130`）と契約局情報（`TWTGA150`）の変更履歴は「発行依頼書登録変更画面の更新と発番のときに登録する。承認フローの操作では登録しない」としている（Phase 4 issue-request 作成中の差戻し指示）。登録の契機が要求の「各申請・承認時」と合わず、承認時の登録を除く記述になっている。database.md 3点目はこのポリシーに従うとしている。要求の詳細化として扱えるのか、要求一覧の見直しが必要なのかは人間の確認が要る |  |  |
| 2 | ssot-consistency | steering/product.md `## 主要ユースケース` 4 ／ steering/security.md `#### チェックの適用箇所`（画面の表示の行） | 二重定義（食い違いの可能性）: 帳票を閲覧・印刷する利用者。product.md のユースケース 4 は「発行依頼を行う利用者が、登録した物件基本情報の帳票（表紙情報・発行依頼書・契約局情報）を PDF で閲覧・印刷する（REQ-016〜REQ-018）」とする。一方、今回足した security.md の画面の表示の行は「閲覧と印刷のボタンは組織がプロセス管理4G（`P71` の G6）のときだけ…表示する」とする。product.md の対象ユーザーには社外ユーザーを含む発行依頼の利用者が挙がっており、プロセス管理4G 以外の発行依頼者が閲覧・印刷できるかで両者が両立しない読み方になる。7ファイルの分担では代表的な利用シナリオは product.md、画面と操作の権限は security.md が持つ。どちらに揃えるかは人間の確認が要る |  |  |
| 3 | steering-conformance | steering/security.md `#### チェックの適用箇所`（画面の表示の行。根拠: 同ファイル `#### チェックの適用箇所` の分担文「権限名の一覧やリソースごとの対応表は `specs/&lt;feature&gt;/design.md` の `### セキュリティ上の考慮（Security Considerations）`。ここに書く例はあくまで書き方の見本であり、一覧ではない」） | 実体の混入（判断材料）: 今回足した記述は、閲覧・印刷ボタンと再製本ボタンという個々の画面部品ごとの表示条件と、その判定値（`P71` の G6、所属組織 KDDI・K-ENG）を持ち、さらに「組織の判定のしかたは property-basic-info の design で定める」として特定の feature を名指ししている。全 feature に等しく適用されるルールではなく、判定基準（steering は方針、spec は実体）に照らすと各 feature の design.md 側の実体にあたる。記述は Phase 4 issue-request 作成中の差戻し指示に基づくもので、steering に置くかは人間の確認が要る |  |  |
| 4 | steering-conformance | steering/security.md `#### 権限モデル`（モデル・定義の置き場・禁止） | 粒度の不足（steering と design.md のどちらで補うかの確認）: モデルと定義の置き場は、承認フローの「申請者・確認者・承認者」の権限を審査権限マスタ `TWTGM170` と `P82` で判定するとし、禁止でも「申請者・確認者・承認者の番の判定は `TWTGM170` と `P82` 以外の仕組みで作らない」としている。一方、今回足した記述は「起案者の権限は全員が持ち、`TWTGM170` では管理しない」とする。「申請者」と「起案者」が同じ役割か別の役割か（申請の操作に `TWTGM170` の申請者の権限が要るのか、全員ができるのか）が書かれておらず、各 design.md はこの記述を参照するだけでは申請の操作の権限判定を決められない。feature ごとに独自解釈が生じうる |  |  |

### 差戻し先候補

| 指摘番号 | 宛先 | 理由 |
|---|---|---|
| 1 | 人間による確認 | 要求一覧 REQ-027 の登録契機と、Phase 4 の差戻し指示で決めた登録契機のどちらを正とするか（要求一覧を Phase 1 で見直すか、steering の記述を直すか）は人間の判断が要る |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 5 | 1 | 対応せず進める | 要求の詳細化として扱い、要求一覧は見直さない。&#10;REQ-027 の「各申請・承認時」は、承認フローの各担当が自分の番で発行依頼書を更新したときと、申請者が発番したときを指すと読む。&#10;変更履歴は、その更新と発番で項目に変更があったときに登録する。&#10;申請依頼・確認・承認などのボタンを押しただけでは、項目は変わらないので登録しない。 | Junichi Noumi | 2026-10-02T10:57:38+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 5 | 2 | 対応せず進める | 画面と操作の権限は security.md を正とする。&#10;閲覧と印刷のボタンを使えるのは、プロセス管理4G（P71 の G6）の利用者だけである。&#10;product.md のユースケース4は代表的な利用の流れを示すもので、閲覧と印刷を誰でもできるという意味ではないと読む。 | Junichi Noumi | 2026-10-02T10:57:40+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 5 | 3 | 対応せず進める | steering に置いたままにする。&#10;組織によってボタンを出し分けるという方式は、承認フローの番による判定とは別の仕組みである。&#10;そのため、権限モデルの一つとして steering に示しておく。&#10;閲覧と印刷のボタン、再製本ボタン、判定値は、その方式の書き方の見本として残す。&#10;各 feature の部品ごとの表示条件の一覧は、それぞれの design で定める。 | Junichi Noumi | 2026-10-02T10:57:43+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 5 | 4 | 対応せず進める | 起案者と申請者は別の役割である。&#10;起案者の操作は全員ができる。新規の登録・更新・申請依頼・取下げ・削除が当たる。&#10;申請者の操作は、TWTGM170 に申請者（P82 の 02）として登録された利用者だけができる。発番・確認・申請・差戻し・取下げが当たる。&#10;確認者（03）と承認者（04）も同じく TWTGM170 で判定する。&#10;各 design は、このゲート記録の判断を参照して権限の判定を定める。 | Junichi Noumi | 2026-10-02T10:57:45+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 5 | steering/product.md | Junichi Noumi | 2026-10-02T10:57:47+09:00 | 1efed322f96e4244b36b57ef6b9090ca82fe8aaa7c10d9ff51589d30dbe4b397 |
| phase | 5 | steering/tech.md | Junichi Noumi | 2026-10-02T10:57:47+09:00 | 58cc32eb0ad29d7b7185bb02e710ce8d882e374f93eb0a609ae293e3903a4966 |
| phase | 5 | steering/architecture.md | Junichi Noumi | 2026-10-02T10:57:47+09:00 | 98be0c57ba256c0aeaf1a66d69682e63b47d20ec0f91ab776589a54e5eb8c33d |
| phase | 5 | steering/security.md | Junichi Noumi | 2026-10-02T10:57:47+09:00 | c46d9d175156e139f61c19d58e4b7fb3d7bc5e3c1e3c4395802c2bef449f6b8b |
| phase | 5 | steering/non-functional.md | Junichi Noumi | 2026-10-02T10:57:47+09:00 | 831016b1f41e7f6c4597559be5395ff3358283f3e2416f64e98a4d3f0902c314 |
| phase | 5 | steering/database.md | Junichi Noumi | 2026-10-02T10:57:47+09:00 | 8eac00445a5e85e7b58e9659a0f4bad94bdbf8581846fcf56a693883a12ec681 |
| phase | 5 | steering/api-standards.md | Junichi Noumi | 2026-10-02T10:57:47+09:00 | 70eca8d2facbf08bfa22cf1ae1e781219ecab2066bb8129bf4a3414b0fdeddc1 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| phase | 5 | 1 | 対応せず進める | 要求の詳細化として扱い、要求一覧は見直さない。&#10;REQ-027 の「各申請・承認時」は、承認フローの各担当が自分の番で発行依頼書を更新したときと、申請者が発番したときを指すと読む。&#10;変更履歴は、その更新と発番で項目に変更があったときに登録する。&#10;申請依頼・確認・承認などのボタンを押しただけでは、項目は変わらないので登録しない。 | phase | 5 |
| phase | 5 | 2 | 対応せず進める | 画面と操作の権限は security.md を正とする。&#10;閲覧と印刷のボタンを使えるのは、プロセス管理4G（P71 の G6）の利用者だけである。&#10;product.md のユースケース4は代表的な利用の流れを示すもので、閲覧と印刷を誰でもできるという意味ではないと読む。 | phase | 5 |
| phase | 5 | 3 | 対応せず進める | steering に置いたままにする。&#10;組織によってボタンを出し分けるという方式は、承認フローの番による判定とは別の仕組みである。&#10;そのため、権限モデルの一つとして steering に示しておく。&#10;閲覧と印刷のボタン、再製本ボタン、判定値は、その方式の書き方の見本として残す。&#10;各 feature の部品ごとの表示条件の一覧は、それぞれの design で定める。 | phase | 5 |
| phase | 5 | 4 | 対応せず進める | 起案者と申請者は別の役割である。&#10;起案者の操作は全員ができる。新規の登録・更新・申請依頼・取下げ・削除が当たる。&#10;申請者の操作は、TWTGM170 に申請者（P82 の 02）として登録された利用者だけができる。発番・確認・申請・差戻し・取下げが当たる。&#10;確認者（03）と承認者（04）も同じく TWTGM170 で判定する。&#10;各 design は、このゲート記録の判断を参照して権限の判定を定める。 | phase | 5 |

## 実行

| スコープ | 回数 | 実行日時 | 実行した層 | 対象成果物 | 原本SHA256 | 指摘件数 |
|---|---|---|---|---|---|---|
| phase | 6 | 2026-10-05T15:44:21+09:00 | ①② | ["steering/product.md", "steering/tech.md", "steering/architecture.md", "steering/security.md", "steering/non-functional.md", "steering/database.md", "steering/api-standards.md"] | {"steering/product.md": "cde5dd8a1007c53f93a270de63e01d294d38f47695e96027d52b6b4862bc149b", "steering/tech.md": "58cc32eb0ad29d7b7185bb02e710ce8d882e374f93eb0a609ae293e3903a4966", "steering/architecture.md": "98be0c57ba256c0aeaf1a66d69682e63b47d20ec0f91ab776589a54e5eb8c33d", "steering/security.md": "34061564b8c5b8c28e5ca2f4a9b744b06d9d58417ddbbff7ab150c9ef1027bbf", "steering/non-functional.md": "ae87c72271e4f3d8593e2f666edc7bb0931cf4d0ca78dafbb21ab7264303f0ac", "steering/database.md": "832d98b289c53f8c8adc9a7dfb25bf0f8b1f54b9c1cc473c6480fa9927a20e21", "steering/api-standards.md": "70eca8d2facbf08bfa22cf1ae1e781219ecab2066bb8129bf4a3414b0fdeddc1"} | 8 |

### 指摘

| # | 観点 | 対象箇所 | 指摘内容 | 判断 | 理由 |
|---|---|---|---|---|---|
| 1 | ssot-consistency | steering/product.md `## 主要ユースケース` 4 ／ steering/security.md `#### チェックの適用箇所`（画面の表示の行） | 二重定義（食い違いの可能性）: 帳票の閲覧・印刷ができる利用者。今回直したユースケース 4 は「組織がプロセス管理4G の申請者・確認者・承認者（再製本依頼では起案者も）」が閲覧・印刷するとし、役割（申請者・確認者・承認者）による限定と、再製本依頼のときに起案者を加える条件を持つ。一方 security.md の画面の表示の行は「閲覧と印刷のボタンは組織がプロセス管理4G（`P71` の G6）のときだけ」「再製本ボタンは所属組織が KDDI か K-ENG のときだけ」表示するとし、閲覧・印刷に役割の限定は無く、再製本は組織（KDDI・K-ENG）で出し分ける。7ファイルの分担では画面と操作の権限は security.md が持つ（Phase 2 5 回目 残件 2 の判断も security.md を正とする）。ユースケース 4 の役割の限定と起案者の条件は security.md に無く、引用（準拠）の形にもなっていない。security.md に足すか、ユースケース 4 の記述を代表例に戻すかは人間の確認が要る |  |  |
| 2 | ssot-consistency | steering/security.md `#### 所有権・エンティティ境界`（パターン）／ steering/security.md `#### チェックの適用箇所`（データ取得の行） | 二重定義（食い違いの可能性）: 社外ユーザーとして絞り込む対象の判定方法。パターンの冒頭は「WTG の社内と社外の判定は、コードマスタ（`TWTZM040`）の識別 WTG・PARAM・P71 で行う」と WTG 全体の判定として書く。一方、今回足した既存の契約情報（`TWTGM010`〜`TWTGM070`）の絞り込みは「ログインユーザーのベンダー区分か施工会社区分に値があるときだけ当てはめ、両方とも空の利用者には絞り込みをしない」とし、P71 ではなく AuthContext のベンダー区分・施工会社区分で対象者を決めている。データ取得の行は「社外ユーザーのとき」に絞り込むとしている。P71 で社外と判定されるがベンダー区分・施工会社区分が空の利用者（またはその逆）を、契約情報で絞り込むかが読み分けられない。7ファイルの分担では範囲の判定方法はこのパターンが持つ（Phase 2 4 回目 残件 2）。契約情報だけ別の判定とする意図かを、パターン冒頭の「WTG の社内と社外の判定」の書き方とあわせて人間の確認が要る |  |  |
| 3 | ssot-consistency | steering/product.md `## ビジネスルール / ポリシー`（申請・承認の履歴）／ steering/database.md `## クエリパターン`（洗替の行） | 二重定義（同一内容。一部は片側にだけある）: 契約情報取込の洗替で変更履歴に登録する行。product.md は「契約情報取込（contract-info-import）も、洗替のときに `TWTGA150`・`TWTGA130` に変更履歴を登録する。登録するのは内容が変わった行の取込前の内容だけとする」とし、database.md の洗替の行は「契約情報取込では、洗替の前の内容をトランに写し、洗替の後と比べて、変わった行だけを変更履歴に登録する」としている。変わった行だけを登録するという同じ事実が両方にあり、database.md 側は product.md への引用（準拠）の形になっていない。登録するのが取込前の内容であることは product.md にだけあり、database.md の記述からは読み取れない。7ファイルの分担では業務上の決まりは product.md、DB 側の実装方針は database.md が持つ。database.md 側を引用に置き換えるかは人間の確認が要る |  |  |
| 4 | steering-conformance | steering/security.md `## 機密データ`（マイナンバーを受け取った日の行） | 実体の混入（判断材料）: 今回足した行は、特定の取込ファイルの 1 列（マイナンバーを受け取った日）について「テーブルには保存しない。ログへの出し方は contract-info-import の design で定める」とし、特定の feature を名指ししている。この列を扱うのは契約情報取込だけで、全 feature に等しく適用されるルールではなく、判定基準（steering は方針、spec は実体）に照らすと contract-info-import の design.md 側の実体にあたる（根拠: security.md 冒頭の書き方「全機能に共通する方針だけを書く。特定の機能にしか当てはまらない判断は書かない」）。記述は人間の開き直しの指示に基づくもので、steering に置くかは人間の確認が要る |  |  |
| 5 | steering-conformance | steering/security.md `#### 所有権・エンティティ境界`（パターン。既存の WTG の契約情報の絞り込み） | 実体の混入（判断材料）: 今回足した記述は、既存の契約情報の表（`TWTGM010`〜`TWTGM070`）を名指しして WTB の計画マスタの方式で絞り込むこと、その適用条件（ベンダー区分か施工会社区分に値があるとき）を定め、「contract-info-download で使う」と特定の feature の利用に限っている。全 feature に等しく適用されるルールとして書かれておらず、判定基準に照らすと contract-info-download の design.md 側の実体にあたる。一方、他の feature（申請状況検索など）が既存の契約情報を引く場合にも同じ方式を当てはめる趣旨であれば、「contract-info-download で使う」の限定と両立しない。全体のルールとするか、feature の実体とするかは人間の確認が要る（根拠: security.md 冒頭の書き方、Phase 2 4 回目 残件 6 の判断「申請以外のデータ（契約情報）の範囲は Phase 4 と Phase 5 で定める」） |  |  |
| 6 | steering-conformance | steering/database.md `## クエリパターン`（洗替の行） | 実体の混入（判断材料）: 洗替の行は、既存の `PWTGB030Job` の退避・削除・入れ直しのやり方を「すべての洗替の決まりではない」としたうえで、契約情報取込に限った手順（洗替の前の内容をトランに写し、洗替の後と比べて変わった行だけを変更履歴に登録する）を書いている。全 feature に等しく適用される洗替のルールが示されず、特定の feature の処理手順だけが書かれており、判定基準に照らすと contract-info-import の design.md 側の実体にあたる（根拠: database.md 冒頭の書き方「全フィーチャーに共通するルールだけを書く。特定のテーブルにしか当てはまらない内容は書かない」）。各 design.md がこの行を参照しても、契約情報取込以外の洗替をどう書くかは決められない。steering に置くかは人間の確認が要る |  |  |
| 7 | steering-conformance | steering/database.md `## 接続 / トランザクション`（トランザクション（バッチ）の行） | 実体の混入（判断材料）: 今回足した例外は「契約情報取込で物件申請情報の状態を取込中にする更新と、元の状態に戻す更新は、取込の本体とは別に確定させる。取込がエラーで全件取り消しになったときも、元の状態に戻す」とし、特定の feature の特定のデータの更新に限った扱いになっている。全バッチに等しく適用されるルール（ジョブ全体で 1 つのトランザクション）の例外として、どの条件なら別に確定させてよいかの一般的な基準は書かれておらず、判定基準に照らすと contract-info-import の design.md 側の実体にあたる（根拠: database.md 冒頭の書き方）。steering に置くかは人間の確認が要る |  |  |
| 8 | steering-conformance | steering/non-functional.md `### サービス提供時間`（休日判定の行） | 実体の混入と記述の矛盾（判断材料）: 休日判定の行は、プレースホルダー `&lt;SERVICE_HOURS_HOLIDAY_CALENDAR&gt;` を「保守運用は既存 WiNG の運用に従い、本プロジェクトでは定めない」として不要としたうえで、同じ行に「申請状況検索の進捗の日数（営業日）は、既存 WiNG のコードマスタにある休日の登録（会社ごと）を使って数える」と足している。この節はサービスを提供する曜日・時間帯の判定基準を定める節で、足した記述は特定の feature（申請状況検索）の業務上の日数計算のルールにあたり、全サービスに共通する内容ではない（根拠: non-functional.md 冒頭の書き方「特定のフィーチャーにしか当てはまらない内容は書かない」）。また「本プロジェクトでは定めない」とした行に本プロジェクトの規則が書かれ、不要理由と記述が両立しない読み方になる。feature の requirements・design に置くか、全体の営業日の数え方として別の場所に置くかは人間の確認が要る |  |  |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 1 | 対応せず進める | 食い違いではない。security.md の画面の表示の行は、ボタンを出す組織の条件を書いたもの。ユースケース 4 は、その組織の中で実際に帳票を使う役割を書いたもの。役割の条件の詳細は specs/print-report/requirements.md の 3.5 にある。 | Junichi Noumi | 2026-10-05T18:24:40+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 2 | 対応せず進める | 契約情報だけ別の判定にする意図どおり。P71 による社内と社外の判定は、本案件で新しく作る申請のデータに使う。既存の契約情報は既存 WiNG のデータなので、既存の WTB と同じベンダー区分と施工会社区分で判定する。P71 で社外でも区分が空なら、契約情報では絞り込まない。 | Junichi Noumi | 2026-10-05T18:24:43+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 3 | 対応せず進める | 同じ事実が 2 か所にあるが、中身は合っている。product.md が業務の決まり、database.md がその DB 側のやり方として残す。 | Junichi Noumi | 2026-10-05T18:24:46+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 4 | 対応せず進める | steering に置く。マイナンバーに関わる情報は、どの feature で扱うかによらず保存しないという方針として読む。今は契約情報取込だけが当たる。 | Junichi Noumi | 2026-10-05T18:24:49+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 5 | 対応せず進める | steering に置く。既存の契約情報を引くときは、どの feature でも同じ方式を使うという全体の決まりとして読む。「contract-info-download で使う」は、今使う feature を示した例と読む。 | Junichi Noumi | 2026-10-05T18:24:52+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 6 | 対応せず進める | steering に置く。「PWTGB030Job のやり方はすべての洗替の決まりではない」が全体の決まりで、契約情報取込の手順はその例として残す。ほかの洗替のやり方は、各 feature の design で決める。 | Junichi Noumi | 2026-10-05T18:24:55+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 7 | 対応せず進める | steering に置く。ジョブ全体で 1 つのトランザクションという決まりの例外を、決まりの隣に書いておかないと、契約情報取込の design が steering と食い違うため。例外は今のところこの 1 つだけ。 | Junichi Noumi | 2026-10-05T18:24:58+09:00 |

## 判断

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 判断者 | 日時 |
|---|---|---|---|---|---|---|
| phase | 6 | 8 | 対応せず進める | 「本プロジェクトでは定めない」は保守運用のサービス提供の休日のことで、営業日の数え方は別の話と読む。営業日を数えるときに既存の休日の登録を使うことは、全体の決まりとして残す。今は申請状況検索だけが当たる。 | Junichi Noumi | 2026-10-05T18:25:00+09:00 |

## 承認

| スコープ | 回数 | 対象成果物 | 承認者 | 承認日時 | 原本SHA256 |
|---|---|---|---|---|---|
| phase | 6 | steering/product.md | Junichi Noumi | 2026-10-05T18:25:03+09:00 | cde5dd8a1007c53f93a270de63e01d294d38f47695e96027d52b6b4862bc149b |
| phase | 6 | steering/tech.md | Junichi Noumi | 2026-10-05T18:25:03+09:00 | 58cc32eb0ad29d7b7185bb02e710ce8d882e374f93eb0a609ae293e3903a4966 |
| phase | 6 | steering/architecture.md | Junichi Noumi | 2026-10-05T18:25:03+09:00 | 98be0c57ba256c0aeaf1a66d69682e63b47d20ec0f91ab776589a54e5eb8c33d |
| phase | 6 | steering/security.md | Junichi Noumi | 2026-10-05T18:25:03+09:00 | 34061564b8c5b8c28e5ca2f4a9b744b06d9d58417ddbbff7ab150c9ef1027bbf |
| phase | 6 | steering/non-functional.md | Junichi Noumi | 2026-10-05T18:25:03+09:00 | ae87c72271e4f3d8593e2f666edc7bb0931cf4d0ca78dafbb21ab7264303f0ac |
| phase | 6 | steering/database.md | Junichi Noumi | 2026-10-05T18:25:03+09:00 | 832d98b289c53f8c8adc9a7dfb25bf0f8b1f54b9c1cc473c6480fa9927a20e21 |
| phase | 6 | steering/api-standards.md | Junichi Noumi | 2026-10-05T18:25:03+09:00 | 70eca8d2facbf08bfa22cf1ae1e781219ecab2066bb8129bf4a3414b0fdeddc1 |

## 残件

| スコープ | 回数 | 指摘番号 | 判断 | 理由 | 承認スコープ | 承認回数 |
|---|---|---|---|---|---|---|
| phase | 6 | 1 | 対応せず進める | 食い違いではない。security.md の画面の表示の行は、ボタンを出す組織の条件を書いたもの。ユースケース 4 は、その組織の中で実際に帳票を使う役割を書いたもの。役割の条件の詳細は specs/print-report/requirements.md の 3.5 にある。 | phase | 6 |
| phase | 6 | 2 | 対応せず進める | 契約情報だけ別の判定にする意図どおり。P71 による社内と社外の判定は、本案件で新しく作る申請のデータに使う。既存の契約情報は既存 WiNG のデータなので、既存の WTB と同じベンダー区分と施工会社区分で判定する。P71 で社外でも区分が空なら、契約情報では絞り込まない。 | phase | 6 |
| phase | 6 | 3 | 対応せず進める | 同じ事実が 2 か所にあるが、中身は合っている。product.md が業務の決まり、database.md がその DB 側のやり方として残す。 | phase | 6 |
| phase | 6 | 4 | 対応せず進める | steering に置く。マイナンバーに関わる情報は、どの feature で扱うかによらず保存しないという方針として読む。今は契約情報取込だけが当たる。 | phase | 6 |
| phase | 6 | 5 | 対応せず進める | steering に置く。既存の契約情報を引くときは、どの feature でも同じ方式を使うという全体の決まりとして読む。「contract-info-download で使う」は、今使う feature を示した例と読む。 | phase | 6 |
| phase | 6 | 6 | 対応せず進める | steering に置く。「PWTGB030Job のやり方はすべての洗替の決まりではない」が全体の決まりで、契約情報取込の手順はその例として残す。ほかの洗替のやり方は、各 feature の design で決める。 | phase | 6 |
| phase | 6 | 7 | 対応せず進める | steering に置く。ジョブ全体で 1 つのトランザクションという決まりの例外を、決まりの隣に書いておかないと、契約情報取込の design が steering と食い違うため。例外は今のところこの 1 つだけ。 | phase | 6 |
| phase | 6 | 8 | 対応せず進める | 「本プロジェクトでは定めない」は保守運用のサービス提供の休日のことで、営業日の数え方は別の話と読む。営業日を数えるときに既存の休日の登録を使うことは、全体の決まりとして残す。今は申請状況検索だけが当たる。 | phase | 6 |
