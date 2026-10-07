"""レビューで人に見せる指摘の並び（重大 → 要判断の束 → 持ち越し）。提示（approval）と回答の読み取り（host_session）が同じ並びを使う。

束は、最新の検査回の指摘のうち system が判断したもの・重大を除き、観点と種類が同じものが 2 件以上あるときに作る。
束の番号は、同じ検査回の間は判断の記入で変わらない（判断済みの指摘も束に残る）。

種類を持たない旧形式の指摘（改修前の版で検査したもの）は、まだ判断していないものを「切り替え前の指摘」の 1 つの束にまとめる
（`legacy` が真の束）。最新の回の旧形式の指摘と、前回までの回から持ち越した未判断の旧形式の指摘が入る。
旧形式の指摘は再評価（reevaluation）で、新しい決まりの指摘として見直せる。
"""
from dataclasses import dataclass, field

import review_contract

INDIVIDUAL_LIMIT = 20  # 要判断を 1 件ずつ出す上限。超えた分は束ごとの件数で出す


@dataclass
class Bundle:
    name: str
    scope: str
    gate: str
    kind: str
    findings: list = field(default_factory=list)
    legacy: bool = False

LEGACY_GATE = "切り替え前の指摘"


def is_legacy(finding):
    """種類を持たない旧形式の指摘で、まだ人も system も判断していないもの。"""
    return not finding.kind and not finding.has_decision


@dataclass
class ScopeView:
    scope: str
    run: object
    critical: list = field(default_factory=list)      # 重大（1 件ずつ）
    singles: list = field(default_factory=list)       # 要判断のうち束にならないもの
    bundles: list = field(default_factory=list)       # 要判断の束
    auto_fix: list = field(default_factory=list)      # system が「修正」と判断した軽微（AI が直す）
    auto_kept: list = field(default_factory=list)     # 前回と同じ判断を system が引き継いだもの
    auto_resolved: list = field(default_factory=list)  # 今回の再検査で system が解消を記録したもの
    excluded: list = field(default_factory=list)      # 前提に当たるため検査役が出さなかったもの
    carried: list = field(default_factory=list)       # 前回までの指摘で、まだ残っているもの


def scope_view(record, scope, numbering):
    run = record.latest(scope)
    view = ScopeView(scope, run, excluded=list(run.excluded))
    groups, legacy = {}, []
    for finding in run.findings:
        if finding.by_system:
            (view.auto_fix if finding.decision == "修正" else view.auto_kept).append(finding)
        elif finding.level == "重大":
            view.critical.append(finding)
        elif finding.kind:
            groups.setdefault((finding.gate, finding.kind), []).append(finding)
        elif finding.has_decision:
            view.singles.append(finding)  # 判断済みの旧形式は 1 件ずつ（判断の変更用）
        else:
            legacy.append(finding)
    for (gate, kind), members in groups.items():
        if len(members) >= 2:
            numbering[0] += 1
            view.bundles.append(Bundle("束%d" % numbering[0], scope, gate, kind, members))
        else:
            view.singles.extend(members)
    view.singles.sort(key=lambda f: f.number)
    carried_legacy = [f for f in record.relevant(scope) if f.run != run.number and is_legacy(f)]
    legacy = carried_legacy + legacy
    if len(legacy) >= 2:
        numbering[0] += 1
        view.bundles.append(Bundle("束%d" % numbering[0], scope, LEGACY_GATE, "", legacy, legacy=True))
    else:
        view.singles.extend(legacy)
    view.auto_resolved = [f for r in record.runs if r.scope == scope for f in r.findings
                          if f.resolved and f.resolved_run == run.number and f.resolved_by.startswith("system")]
    in_bundle = {f.key for b in view.bundles if b.legacy for f in b.findings}
    view.carried = [f for f in record.relevant(scope) if f.run != run.number and f.key not in in_bundle]
    return view


def views(context, record=None):
    record = record or review_contract.read(context)
    numbering = [0]
    return [scope_view(record, scope, numbering) for scope in review_contract.scopes(context)]


def bundles(context, record=None):
    """束の名前 → 束。"""
    return {bundle.name: bundle for view in views(context, record) for bundle in view.bundles}
