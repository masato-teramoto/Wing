<!--
  ビルドコピー（手編集禁止）: 出典 run_id: 13-CT-ADR-001-1（runs/13/13-CT-ADR-001-1/output.md の全文コピー）
  CT-ADR-001 判定 PASS 10.0（judged_by: claude-opus-4-8・Critical Fail なし・INV-05/08 は N/A 除外）
  資産カード: KA-ART-001@0.1.0 / compiled_at: 2026-07-08
-->
---
title: "ADR-0001: judge（受入判定）のモデルを claude-opus-4-8 に固定する"
status: "Accepted"
date: "2026-07-06"
authors: "usa（人間裁定）"
deciders: "usa"
stakeholders: "loop-engine 保守者 / 全 Contract の判定工程 / /loop-calibrate・/loop-report の運用"
tags: ["architecture", "decision", "judge", "calibration"]
supersedes: ""
superseded_by: ""
---

# ADR-0001: judge（受入判定）のモデルを claude-opus-4-8 に固定する

## Status

Accepted（2026-07-06 人間裁定により確定）

## Context

loop-engine の受入判定ゲート（loop-verifier）は、Contract の required_invariants を採点し
Critical Fail を検出する judge である。この judge の信頼性は、judge↔human 一致率の校正
（/loop-calibrate）によって担保される設計だが、校正結果はモデル固有である — あるモデルで
測った一致率は、別のモデルで動く judge の信頼性を何も保証しない。

従来、loop-verifier のモデルは明示指定されておらず、Claude Code の親セッションが使う
モデルをそのまま継承していた。このため、同一の Contract・同一のケースであっても、
起動元セッションのモデル差で判定が変わり得る状態にあった。

この懸念は実測で確認された。cycle 9 において、fable-5 で動いた判事の判定と、
claude-opus-4-8 による再判定との間で、Critical Fail の構成（DEV-01 / DEV-03 の該当有無）が
反転した。Contract 文面もケースも同一であり、差分はモデルのみ — 判定結果に model が
交絡していることを示す直接の証拠である。判事モデルが未固定のままでは、校正プールに
異なるモデルの判定が混入し、judge↔human 一致率という校正指標そのものが無意味化する。

## Decision

loop-verifier エージェントのモデルを claude-opus-4-8 に固定する（.claude/agents/loop-verifier.md
の frontmatter で `model: opus` を明示指定）。

- 判定メタ台帳 judge_runs.csv の model 列は、この固定モデルと一致していなければならない。
- 判事モデルを変更する場合は、変更後モデルで /loop-calibrate（judge↔human 一致の校正）を
  やり直すことを必須とする。校正なしのモデル切り替えは行わない。

選定理由: 校正はモデル固有である以上、判定の再現性を得る最小の介入は「判事の同一性を
構成として固定し、変更を校正イベントに結びつける」ことである。cycle 9 の反転が示す通り、
モデルを固定しない限り校正データは蓄積可能な資産にならない。

## Consequences

### Positive

- **POS-001**: 校正プール（judge↔human 一致率）が有効になる。判定がすべて同一モデルで
  行われるため、蓄積された一致率が判事の信頼性としてエンジン全体で一度確立できる。
- **POS-002**: モデルドリフトが測定可能になる。判事側を固定した定点があるため、生成側や
  Contract 改訂の効果と、モデル差に起因するぶれを分離して観測できる。
- **POS-003**: judge_runs.csv の model 列が構成上の期待値を持ち、台帳との不一致を
  異常（構成逸脱）として機械的に検出できる。

### Negative

- **NEG-001**: 判事モデルが世代的に古くなっても即座に乗り換えられない。乗り換えには
  全 Contract の再校正コスト（校正ケースの再判定と一致率の再測定）が伴う。
- **NEG-002**: 固定判事（claude-opus-4-8）以外のモデルによる判定は校正母数から除外され、
  混入した場合は固定判事による再判定コストが生じる。
- **NEG-003**: 判事の品質上限が固定モデルの能力に拘束される。より判定能力の高い新モデルの
  恩恵を受けるには NEG-001 の再校正を先に払う必要がある。

## Alternatives Considered

### 案1: 親セッションのモデルを継承する（現状放置 / do nothing）

- **ALT-001**: **Description**: loop-verifier にモデルを明示指定せず、起動元 Claude Code
  セッションのモデルをそのまま使い続ける。
- **ALT-002**: **Rejection Reason**: cycle 9 の Critical Fail 反転（fable-5 判事と
  claude-opus-4-8 再判定で DEV-01/03 の該当が反転）が示す通り、親モデル差が判定に交絡し、
  校正が無効化される。校正を前提とする自律モード（validated）の成立条件を壊すため却下。

### 案2: 複数モデルの合議判定

- **ALT-003**: **Description**: 複数モデルで並行判定し、多数決や全会一致などの合議規則で
  最終 verdict を決めることで、単一モデルの癖を平均化する。
- **ALT-004**: **Rejection Reason**: 判定コストがモデル数分に増加するうえ、「合議規則自体を
  どう校正するか」という新たな校正問題を持ち込む。単一モデル固定なら校正対象は判事1体で
  済むところ、合議では規則と各構成モデルの両方が校正対象になり、問題を解かずに移動させる
  だけになるため却下。

### 案3: プロンプト強化のみでモデル非依存化

- **ALT-005**: **Description**: Contract の採点基準や loop-verifier の指示文を精緻化し、
  どのモデルで実行しても同じ判定になるようプロンプト側で吸収する。
- **ALT-006**: **Rejection Reason**: cycle 9 の反転は同一 Contract 文面のもとで起きており、
  「文面を十分精緻化すればモデル非依存になる」という仮説は実測に反する。プロンプト改善は
  一致率向上の手段としては併用するが、モデル固定の代替にはならないため却下。

## Implementation Notes

- **IMP-001**: .claude/agents/loop-verifier.md の frontmatter に `model: opus` を指定し、
  コメントとして本決定の要旨（固定理由・cycle 9 の実測・変更時は /loop-calibrate 再実施）を
  併記する（実施済み）。
- **IMP-002**: judge 実行のたびに judge_runs.csv へ model を記録する既存規律（CLAUDE.md
  不変の規律4）を、本決定の監視面として使う。model 列が固定モデルと不一致の run は
  校正母数から除外する。
- **IMP-003**: 判事モデルを更新する場合の手順 — (1) 本 ADR を Superseded に更新し新 ADR と
  双方向リンク、(2) 新モデルで /loop-calibrate を再実施、(3) 昇格基準充足と人間承認の後に
  切り替え。

## References

- **REF-001**: 関連 ADR — なし。本 ADR はこのリポジトリ最初の ADR であり、ADR-0001 を
  連番の起点として払い出す。
- **REF-002**: .claude/agents/loop-verifier.md（決定の適用先。frontmatter `model: opus` と
  決定理由コメント）
- **REF-003**: ledgers/judge_runs.csv（model 列の記録規律）/ CLAUDE.md「不変の規律」4・7
- **REF-004**: .claude/skills/loop-calibrate（モデル変更時に再実施する校正手順）
