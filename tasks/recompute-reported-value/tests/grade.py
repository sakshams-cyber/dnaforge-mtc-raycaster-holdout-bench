"""Task verifier entrypoint. Scientific gold and schema are supplied by humans."""
import sys
from gradelib import load_answer, write_score
from taskgrader import grade

if __name__ == '__main__':
    try:
        gold = load_answer(sys.argv[3])
        if not gold or gold.get('kind') != 'numeric':
            score, details = 0, {'grader_error': 'missing_numeric_gold'}
        else:
            score, details = grade(*sys.argv[1:4])
    except Exception as exc:
        score, details = 0, {'grader_error': type(exc).__name__}
    write_score(score, details)
