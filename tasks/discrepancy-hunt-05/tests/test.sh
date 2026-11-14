#!/bin/bash
set -u
mkdir -p /logs/verifier
if ! python3 /tests/grade.py /app/output/answer.json /app/workspace /tests/gold.json; then
  printf '0\n' > /logs/verifier/reward.txt
  printf '{"score":0,"details":{"grader_error":"process failed"}}\n' > /logs/verifier/score.json
fi
