"""L4 ACE gate for implement-cross-ace-run[<chunk>] (execution independent, L4-5)."""
import phase_rules
import cross_code_review

if __name__ == '__main__':
    try:
        result = cross_code_review.review(phase_rules.gate_context())
    except (ValueError, OSError, KeyError) as error:
        phase_rules.fail(str(error))
    if result['status'] != 'passed':
        phase_rules.fail('cross ACE chunk %s: %s (%d incomplete)' % (result['chunk'], result['status'], len(result['incomplete'])))
    phase_rules.ok('cross ACE chunk %s reviewed: %d files, %d excluded' % (result['chunk'], len(result['reviewed']), len(result['excluded'])))
