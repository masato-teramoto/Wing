---
name: design-cross-check
description: Phase 5 の横断品質ゲート。全 feature の design.md をまたいだ契約整合を検査する
disable-model-invocation: true
---

## 概要

`design-cross-gate`（全 feature の design.md が揃った後に1回だけ呼ばれる）の event 本体として
実行される。`specs/*/design.md` 一式を対象に、feature をまたいだ契約衝突・循環依存・エラー
形状・業務コードの重複を検査する。横断スコープは承認対象の文書を持たないため、`status` を
遷移させない。

## 入力の範囲

以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 手順

1. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（契約衝突検出）。

   | 対象成果物 | `specs/*/design.md` 一式 | 検査する事実の種類 | API/Event/Data Contracts | SSoTの所在 | 契約を公開している側の feature の design | 検査の型 | 二重定義 | 報告単位 | 別形状に定義されている API / イベント / データ1件 |

   同じ API / イベント / データの別形状での定義と、所有の二重化を見る。

2. `.claude/skills/dependency-cycle-detection/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `specs/*/design.md` の API/Event Contracts | 依存の単位 | feature（API/Event 呼び出し） | 依存の向き | 呼び出し元→呼び出し先 |

   各 design の API/Event Contracts から「この feature が呼び出す他 feature の API/Event」を辺として明示的に
   列挙してから閉路を探す。`.aidd/feature-list.md` の依存列の循環（Phase 3 で検出済み）と同じ組は、API
   呼び出しレベルで新たな閉路を構成しない限り重ねない。

3. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（エラー形状統一検証）。

   | 対象成果物 | `specs/*/design.md` 一式・`steering/api-standards.md` | 検査する事実の種類 | エラーレスポンスの形状（RFC 7807 相当のフィールド構成: 種別識別子・要約・ステータス・詳細・発生箇所） | SSoTの所在 | `steering/api-standards.md` のエラーレスポンス規約。規約が無ければ最初に定義した feature の design | 検査の型 | 二重定義 + 参照切れ | 報告単位 | 別形状のエラーレスポンスを定義している feature の対 |

   全 feature が同じフィールド構成か、フィールド名・意味が食い違っていないかを見る。design が規約を参照して
   いる箇所は参照先の実在も確かめる。`steering/api-standards.md` にエラーレスポンス規約が無い場合は、規約自体の
   欠落として指摘する（Phase 2 への差戻し候補）。

4. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（業務コード重複検出）。

   | 対象成果物 | `specs/*/design.md` 一式・`steering/*.md`（設計ルールの参照用） | 検査する事実の種類 | 業務コード・業務エラーコード・区分値・エンティティの定義 | SSoTの所在 | 規則は steering の設計ルール、実体は最初に定義した feature の design | 検査の型 | 二重定義 | 報告単位 | 別形状に定義されている要素1件 |

   同じ要素が feature ごとに別形状で定義されていないかに加え、定義が steering の設計ルール（採番・区分値・
   エンティティ設計の規則）に沿っているかを、規則側を正として突き合わせる。Phase 6 の集約時に衝突させないことが目的である。

5. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する（feature 横断の設計ルール準拠）。

   | 対象 | `specs/*/design.md` 一式 | 参照する steering | `steering/` 7ファイル一式 | 検証観点 | アーキテクチャ・DB・API・業務コードの設計ルールを全 feature が同じように守っているか |

   steering 自体の妥当性は評価しない。feature ごとに別解釈している箇所は、どちらを直すかを人に問う形で書く。

6. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。

## 禁止

- 対象の design.md をいずれも書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否・重大度を自分で判断しない
- `status` を遷移させない
