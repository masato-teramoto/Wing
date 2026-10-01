---
name: aidd-common
description: 設定されたアクションを順次実行し、待機・外部実行・再開を仲介する共通基盤。入口コマンドから読み込む。単体では工程を持たない。
disable-model-invocation: true
---

# aidd-common

[engine.md](engine.md) の L0 実行プロトコルに従う。Skill の emit → 実行 → report、agent の起動仲介、script の実行、再開点の保存を共通化する。

この配布ディレクトリには複数レイヤーの原本を合成する。

| 配布内の置き場 | 原本の所有元 |
|---|---|
| bin/、engine.md、本ファイル | L0: 実行基盤とホストの実行仲介 |
| command.yaml / flow.yaml / action.yaml / gate.yaml | L3: main_flow の定義（入口のコマンド・flow・アクション・ゲート） |
| scripts/、references/ の進行規則 | L3: 入力・進捗・差戻し・人間判断・承認 |
| scripts/ の品質観点検査 | L4: 成果物の検査 |

各ファイルの管理原本は配布ルートの `.main-flow-assets.json` で確認する。
main_flow の規則は [references/runtime-boundary.md](references/runtime-boundary.md) から参照する。L3 の生成／修正 Skill が検査 agent を起動したり、ゲート記録・進捗・承認を直接更新したりしない。
