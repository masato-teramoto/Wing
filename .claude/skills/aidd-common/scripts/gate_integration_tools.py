"""L4 tool gate at the project level; L3 supplies the project verification contract (_project.json)."""
import phase_rules
import implementation_project

if __name__ == '__main__':
    try:
        implementation_project.final_project(phase_rules.gate_context())
    except (ValueError, OSError, KeyError) as error:
        phase_rules.fail(str(error))
    phase_rules.ok('all project integration commands completed and passed')
