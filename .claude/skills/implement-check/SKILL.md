---
name: implement-check
description: feature全体の実コードと承認済み仕様・タスク・実検証証跡を独立に照合する。
disable-model-invocation: true
---

## 入力

profile=implementation-code-v1。snapshot、implementation（review.jsonの内容）、tool_results_path、
tool_results_sha256、report_summary、required_aspects、上流一覧、unreviewed_inputs、gate_record_path。implementation.codeに列挙された実コードを読む。
上流は承認済みを前提とするが、unreviewed_inputsに挙げた入力（上流工程のtarget_reviewから外れたdraft）はapprovedでなくてよく、
それだけを理由に指摘しない。
作成Skillのsummaryだけで検査しない。manifestと全ツール実績の版一致を確認する。

## 今回の開発補助レポーティングの扱い

3観点に共通して、今回追加した人の閲覧用の生成レポートの表示・書式だけを理由とする
指摘・差戻し候補・追加の承認条件を作らない。対象は今回のtool_results_pathに記録された
summary.pathとreport_receipts[].reportの生成物で識別する。ディレクトリ名だけで一括除外しない。
レポートの仕様・結果・coverageは検査証跡として読む。結果の矛盾や検証不足は除外しない。
案件の単体テストは新規・既存・配置先・レポートでの利用有無を問わず、従来の評価対象とする。
テスト・adapter・実行設定・導入補助・依存定義は除外せず、案件の仕様・設計・完了条件で評価する。
ケースの収集漏れ、入力・期待値・assertionの変更、coverage対象の欠落、失敗の隠蔽も検査する。
レポート追加だけを根拠に、ケースの重複作成や新しい品質基準を要求しない。
製品コード、ビルド・デプロイへの実影響、製品要件そのもののレポート機能も従来どおり検査する。
implementation-toolsによる実行成否、必須出力、実ケース数、証跡の整合性・鮮度の確認は維持する。
機械検査の不合格を無視せず、過去の指摘・人間の判断・解消・承認を変更しない。

## 手順

繰り返し: feature ごと（per-feature）

1. `.claude/skills/implementation-traceability/SKILL.md` をReadし、要求・設計・タスクと実コードを照合する。
2. `.claude/skills/implementation-boundary/SKILL.md` をReadし、公開契約・Boundary・依存方向を検査する。
3. `.claude/skills/implementation-tests/SKILL.md` をReadし、完了条件に対するテストと実検証の十分性を検査する。
4. `.claude/skills/gate-report/SKILL.md` をReadし、snapshotに対応する今回の検査を追記する。

全観点を実施した場合だけlayers=①②とaspectsの全IDを返す。読み込み不能・未実施を
「指摘なし」としない。コードprofileでは本文・status・tasks・manifestは全て読取り専用。
指摘はgate名とコード上の対象箇所を持たせ、判断・解消・承認を記入しない。
結果には、読んだtool_results_pathのSHA256を`tool_results_sha256`として返す。
入力のハッシュと一致することを確認し、検査中に別試行へ変わった結果を混用しない。
