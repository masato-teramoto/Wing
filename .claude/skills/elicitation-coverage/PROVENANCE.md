# PROVENANCE — elicitation-coverage

## 生成

| 項目 | 値 |
|---|---|
| 生成器 | `capabilities/supply/scripts/build-elicitation-skill.sh`（決定論・fail-closed） |
| 生成規則の正本 | `capabilities/supply/packs/elicitation-coverage-pack.md`（§1.3 件数照合・§1.4 パス分割・§1.5 鮮度ゲート・§2 出力契約） |
| compiled_at | 2026-08-03 |
| 手編集 | **禁止**。レコードを直して再生成する |

## 出典（SSOT＝レコード層。adr/0009 二層モデル）

| ブロック | レコードファイル | sha256 | 出典文書 | 版 | 件数 | 鮮度 |
|---|---|---|---|---|---|---|
| A | `records/c02-deliverable-defs.yaml` | `b360096c5acc0a7fd7f2abe78d8732be4bc5c81c386644914cd02db749cebee5` | Q07A22-C02 システム設計開発手順書（要件定義） | 2.0.3 | 38 | current |
| B | `records/elicitation-question-bank.yaml` | `e3f09721cac0af07b229a4a9ad3c81b0d9333d66897cbae8d5cf91e6242b509a` | IMS12A41-F09-01〜04 ヒアリングシート | 1.0.1 | 177 | frozen-suspect-H5 |

同梱の検証器（機密内容を含まない汎用 YAML 検証器・依存は bash と perl のみ）:

| ファイル | 複製元 | sha256 |
|---|---|---|
| `scripts/check-coverage-report.sh` | `capabilities/supply/scripts/check-coverage-report.sh` | `4172d44340fbf1e9a02cf497fed9ccc7f1c8c5d148deb604ab031fa43b9867db` |

同梱理由: R1（省略の検出）と R2（発明ID の検出）が**全件走査保証の唯一の検証手段**であり、
検証器なしでは本パックの中核的な保証を供給先で確認できないため（2026-08-03 判断）。

ブロックB 内訳: F09-01=39 / F09-02=45 / F09-03=64（22+42の2パス） / F09-04=29。

## 機密区分と供給範囲

- **社外秘・本リポジトリ内利用可（ゲート2 H-4）** を継承する。
- **2026-08-03 裁定2**（export-policy §2 規則3「本リポジトリ外への供給は個別の人間裁定を要する」）により、
  次の条件を満たす供給先に限りリポジトリ外への配置を許可する:
  1. 社内の管理下にあること
  2. 社外に露出しないこと
  3. 撤収可能であること
- 上記を満たさない配置・再配布・社外共有は**禁止**。
- 供給の記録は `factory/ledgers/consumer-supply.csv` に行う（記録外の配布をしない）。

## 撤収手順

1. 供給先の `elicitation-coverage/` ディレクトリを削除する（本パックは外部状態を持たないため、これで原状復帰）。
2. `factory/ledgers/consumer-supply.csv` の当該行を `status=withdrawn` に更新する。
3. 撤収の事実を `factory/docs/consumer-supply-withdrawal.md` に追記する。

## 鮮度契約

- レコード層が SSOT。原本改訂（台帳 version 更新）時は当該ブロックを stale とし、
  再抽出＋出口条件再通過まで供給から外す（pack §4-5）。
- 供給先での独自鮮度管理・手修正は禁止（export-policy §4 規則7）。再生成で追随する。

## 既知の限定

- ブロックB（177問）は `frozen-suspect` 源泉であり、**H-5割引＝参考質問扱い**。
  「切る」基準は `packs/elicitation-run-design.md` §5 に事前明文化済み。
- 本パックの出力は**効果の証拠ではない**。効果実測は `protocols/stage2-prospective-run.md` の段階2による（adr/0006）。
- 全 AI 出力は**認定レビュアー承認用ドラフト**（IMS12A33-G02 制約）。

- 2026-08-24: 検証用改変 — B3 pass（F09-Q-085〜106）を注入対象外に変更（SKILL.md のみ。原本 l2-1.0-rc1 からの差分は表1行・合計注記・目安1行）。
