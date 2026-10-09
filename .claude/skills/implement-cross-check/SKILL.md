---
name: implement-cross-check
description: 全 feature の実装承認後に、feature をまたいだ実コードと全体結合確認・横断 ACE の結果を照合する。
disable-model-invocation: true
---

## 入力

profile=implementation-cross-v1。snapshot、cross_review（cross_review_path の内容：全 feature の実装承認行、
全体結合確認の受領証のパス、ACE 計画・チャンク・再利用した受領証・ACE 対象外）、reviews（feature ごとの review.json）、
project_config（`_project.json`：build・smoke の checks、owner、wrapper）、smoke_note、gate_record_path。
reviews の各 review.json の code に列挙された実コードと、smoke wrapper を読む。
作成 Skill や feature 単位の検査の summary だけで検査しない。受領証と ACE の結果は読取り専用の証跡として読む。

## 観点（feature をまたぐもの）

- コード側の依存境界：利用側が提供側の公開契約（design の公開契約・API）経由でだけ依存しているか。
  提供側の内部への直接参照・提供側 Boundary 内の書換え・スタブやバイパスの残存（§6.12 のハリボテ）を指摘する。
- 要求 ID の実装網羅（全件の traceability）：全 feature の要求 ID が、いずれかの feature の実コードとテストに対応するか。
- 業務コードの重複、共有 DB スキーマ・マイグレーション・共通ライブラリの整合。
- 全体結合確認の妥当性：`_project.json` の build・smoke と smoke wrapper が、Platform の公開契約を実際に呼んでいるか。
  受領証の合否は L3 が照合済みなので、合否ではなく経路の中身（何を呼び、何を確かめたか）を見る。
- ACE の機械指摘は cross_review のチャンクの結果をそのまま載せる（重ねて言い換えない）。ACE 対象外のファイルは
  件数・理由・一覧を示す。指摘にはしないが、黙って除外しない。

合否は出さず指摘として返し、人が判断する。

## 共通ルール

指摘は `.claude/skills/finding-rules/SKILL.md`（検査役が手順の前に読む）に従って出す。重大度は出さない。
どの手順でも、ほかの手順で指摘済みの箇所・同じ原因は重ねない。

## 手順

1. `.claude/skills/implementation-traceability/SKILL.md` を Read し、全 feature をまとめて要求・設計・タスクと実コードを照合する（全件）。
2. `.claude/skills/implementation-boundary/SKILL.md` を Read し、feature をまたぐ範囲で公開契約・Boundary・依存方向を検査する。
3. 上の「観点」のうち 1・2 で見ていないもの（重複、共有スキーマ、全体結合確認の妥当性）を検査し、ACE の指摘と ACE 対象外を載せる。
4. `.claude/skills/finding-verification/SKILL.md` を Read し、蓄積した指摘を確かめる。
5. `.claude/skills/gate-report/SKILL.md` を Read し、snapshot に対応する今回の検査を scope `cross` で追記する。

全観点を実施した場合だけ layers=①② と aspects の全 ID を返す。読み込み不能・未実施を「指摘なし」としない。
本文・review.json・受領証・tasks・manifest は全て読取り専用。指摘は gate 名とコード上の対象箇所を持たせ、判断・解消・承認を記入しない。
