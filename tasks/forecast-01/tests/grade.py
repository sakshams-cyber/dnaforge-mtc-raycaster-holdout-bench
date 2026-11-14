# Forecast task verifier entrypoint. Gold values are read by humans from the held-back filing.
import sys
from gradelib import write_score
from forecastgrader import grade

if __name__ == '__main__':
    try:
        score, details = grade(*sys.argv[1:4])
    except Exception as exc:
        score, details = 0, {'grader_error': type(exc).__name__}
    write_score(score, details)
