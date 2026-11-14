"""Task verifier entrypoint. Scientific gold and schema are supplied by humans."""
import sys
from gradelib import write_score
from taskgrader import grade

if __name__ == '__main__':
    try:
        score, details = grade(*sys.argv[1:4], task_kind='activity')
    except Exception as exc:
        score, details = 0, {'grader_error': type(exc).__name__}
    write_score(score, details)
