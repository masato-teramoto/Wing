---
name: aidd-mode-switch
description: 全件方式の案件を Feature 方式へ 1 回だけ切り替える。確認表示を人に示し、確定と回答されたときだけ切り替える。
---

# /aidd-mode-switch

## 手順

1. `.claude/skills/aidd-common/references/host-protocol.md` を読む。呼出し先の順の正は `.claude/skills/aidd-common/command.yaml` の `aidd-mode-switch`。
2. `advance --call mode-switch` を実行し、返却の `preview`（確認表示：引き継ぐもの・引き継がないもの・戻せないこと・切替を止めている残作業・owner の候補）をそのまま人に示す。状態は変わらない。`switch_allowed` が false なら `reasons` を示す。
3. 切替を止めている残作業があれば、それを示して終える（切り替えない）。
4. 人に確定するかを聞く。確定と回答されたときだけ、`switch-mode --action mode-switch-confirm` に `{"confirm": true, "reason": "<理由>"}` を渡す。owner を選ぶよう示された場合は、人が選んだ `owner`（候補の feature 名、または「候補なし」と `owner_reason`）を加える。
5. 確定しなければ何も呼ばない。利用者の発言の解釈で確定しない。

切替は 1 回限りで、Feature 方式から全件方式へは戻せない。最初の feature はこのコマンドでは選ばず、次に打つ工程の入口の計画停止点で選ぶ（select-scope）。
