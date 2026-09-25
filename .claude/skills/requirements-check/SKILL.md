---
name: requirements-check
description: Phase 4（機能要件作成）の品質ゲート（featureスコープ）。specs/<feature>/requirements.md を検査する
disable-model-invocation: true
---

## 概要

対象 feature の `specs/<feature>/requirements.md` を検査する。`--item` で渡された feature 名を
すべての観点 Skill 呼び出しに引き継ぐ。① 形式検証で不備が見つかった場合、② 以降には進まない。

## 入力の範囲

以下の `*` / `<feature>` はホストが渡した明示的な対象・上流一覧への表記であり、Globで対象を発見して分母を決める指示ではない。必要なファイルが一覧に無ければfailedで返す。機械指摘は指定された findings_path だけから受け取り、snapshot と実行IDが一致するものを使う。

## 手順

1. `.claude/skills/format-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象パス | `specs/<feature>/requirements.md` | テンプレパス | `Templates/specs/_template/requirements.md` | ID書式 | 要件ID = 数値のみ（`1`, `1.1`）。当該ファイル内で重複しない | 追加検証 | 各要件に US と AC が存在する・フロントマターの `feature` が `.aidd/feature-list.md` の feature 名と一致する | 報告単位 | 要件ID |

   プレースホルダーは、不要理由が明記された箇所を指摘せず、理由の無いまま残る箇所を指摘する。

2. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（当該feature行の対応要求IDだけを分母とする要求ID突合）。

   | 上流 | `.aidd/feature-list.md`・`.aidd/requirement-list.md` | 下流 | `specs/<feature>/requirements.md` | 突合方向 | 双方向 | 対応の単位 | 要求ID | 分母の絞り込み | 当該 feature 行の対応要求IDのみ | 報告単位 | 未反映の要求ID／要求IDに紐づかない要件 |

   下流→上流では、各要件（`### 要件 N`）がいずれかの対応要求IDに紐づくかを見る。テンプレートに要求ID欄が
   無いため、ID の記載有無ではなく要件の内容で紐づけを判定し、紐づけ先を示せない要件を指摘する。上流→下流では
   要求の内容が要件で満たされているかまで意味判定する。

3. `.claude/skills/verifiable-criteria-check/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `specs/<feature>/requirements.md` の各要件AC |

4. `.claude/skills/ac-coverage-completeness/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `specs/<feature>/requirements.md` の各要件AC |

5. `.claude/skills/traceability/SKILL.md` を Read し、次を指定して実行する（非機能誤配置検出）。

   | 上流 | `steering/non-functional.md`・`steering/security.md` | 下流 | `specs/<feature>/requirements.md` | 突合方向 | 下流→上流 | 対応の単位 | 非機能/制約項目 | 分母の絞り込み | なし | 報告単位 | 誤配置の要件・AC |

6. `.claude/skills/evidence-guard/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `specs/<feature>/requirements.md` | 根拠 | `.aidd/feature-list.md`・`.aidd/requirement-list.md`・`steering/*.md` |

7. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（重複要件検出）。

   | 対象成果物 | `specs/<feature>/requirements.md` | 検査する事実の種類 | 要件が定義する振る舞い | SSoTの所在 | 先に記載された要件ID | 検査の型 | 二重定義 | 報告単位 | 重複と判定した要件IDの対 |

   文言ではなく振る舞いの同一性で判定する。加えて、ある要件が他の要件の受け入れ基準の部分集合になっている
   （独立した要件として存在する必要が無い）場合も INVEST の Independent 違反として指摘する。手順3・4で
   指摘済みの箇所は重ねない。

8. `.claude/skills/steering-conformance/SKILL.md` を Read し、次を指定して実行する。

   | 対象 | `specs/<feature>/requirements.md` | 参照する steering | `steering/*.md` 一式 | 検証観点 | steering への違反・矛盾・逸脱 | 報告単位 | 要件ID |

9. `.claude/skills/ssot-consistency/SKILL.md` を Read し、次を指定して実行する（Dependencies整合検証）。

   | 対象成果物 | `specs/<feature>/requirements.md`・`.aidd/feature-list.md` | 検査する事実の種類 | Dependencies記載 | 検査の型 | 参照切れ |

10. `.claude/skills/gate-report/SKILL.md` を Read し、蓄積した指摘を書き込む。

## 集約

snapshot の scope / run / at / artifacts をそのまま使う。指摘には呼んだ観点 Skill 名を gate として付け、最後の gate-report で1回だけ記録する。feature 別見出しへ挿入せず、実行ごとのブロックをファイル末尾に追加する。今回件数へ過去の持越しを含めない。

## 禁止

- 対象成果物の本文を書き換えない
- 判断・理由欄を埋めない
- ゲート記録を追記以外の形で変更しない
- 指示された観点 Skill 以外を勝手に実行しない
- 合否・重大度を自分で判断しない
- 他 feature の成果物・上流成果物を書き換えない
