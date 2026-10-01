"""Compare actual ID definitions against HEAD; missing evidence is explicit."""
from pathlib import Path
import subprocess
import phase_rules
import findings_stage
import quality_inputs

def main():
    context = phase_rules.ExecutionContext()
    if context.process != "intake":
        phase_rules.fail("unsupported revision-diff process")
    for target in context.gate_targets():
        compare(context, target)
    phase_rules.ok("revision comparison completed or limitation recorded")


def compare(context, target):
    try:
        inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=context.root,
                                capture_output=True, text=True, encoding="utf-8", timeout=10)
        if inside.returncode or inside.stdout.strip() != "true":
            raise ValueError("案件が git 管理されていないため、改版時の要求ID比較を行っていません（案件は git 管理が前提です）")
        result = subprocess.run(["git", "show", "HEAD:" + target], cwd=context.root,
                                capture_output=True, text=True, encoding="utf-8", timeout=10)
        if result.returncode:
            # First version (not yet committed / no commit): nothing to compare against.
            return
        previous = result.stdout
        current = Path(context.path(target)).read_text(encoding="utf-8")
        old = set(quality_inputs.requirements(previous))
        retired = set(quality_inputs.requirements(previous, retired=True))
        new = set(quality_inputs.requirements(current))
        new_retired = set(quality_inputs.requirements(current, retired=True))
        problems = []
        if (old | retired) - (new | new_retired):
            problems.append("以前の要求IDが廃止の記録なしに削除されています")
        if retired & new:
            problems.append("廃止済みの要求IDが有効な要求として再利用されています")
        maximum = max((int(i.split("-")[1]) for i in old | retired), default=0)
        if any(int(i.split("-")[1]) <= maximum for i in new - old):
            problems.append("新しい要求IDが過去の最大番号以下を使っています（欠番の再利用）")
        for problem in problems:
            findings_stage.append(context, "revision-diff-validity", target, problem)
    except FileNotFoundError:
        findings_stage.append(context, "revision-diff-validity", target, "git が見つからないため、改版時の要求ID比較を行っていません")
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        findings_stage.append(context, "revision-diff-validity", target, str(error))


if __name__ == "__main__":
    main()
