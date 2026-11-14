"""Verifier entrypoint for the PK reconstruction task: wraps pk_benchmark.grade for Harbor.

Usage: grade.py <answer.json> <workspace> <gold.json>. Writes reward.txt and score.json.
"""
import json
import sys
from pathlib import Path

from gradelib import write_score
from pk_benchmark import grade

if __name__ == '__main__':
    answer_path, _workspace, gold_path = sys.argv[1:4]
    try:
        gold = json.loads(Path(gold_path).read_text())
        record = gold.get('verification', {})
        if record.get('status') not in {'human_verified', 'synthetic_fixture'} or not record.get('who') or not record.get('how'):
            score, details = 0, {'grader_error': 'unverified_gold'}
        else:
            try:
                answer = json.loads(Path(answer_path).read_text())
                if not isinstance(answer, dict):
                    answer = {}
            except (OSError, ValueError):
                answer = {}
            result = grade(gold, answer)
            score = result['reward']
            details = {'kind': 'pk_reconstruction', 'checks_failed': result['checks_failed'],
                       'failed_fields': result['failed_fields'],
                       'primary_failure': 'correct' if score == 1 else
                       ('missing' if not answer else 'calculation')}
    except Exception as exc:
        score, details = 0, {'grader_error': type(exc).__name__}
    write_score(score, details)
