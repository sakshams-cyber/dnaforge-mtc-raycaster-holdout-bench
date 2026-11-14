"""PK reconstruction task on a fictional TSV with the pack's column names."""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tasks/pk-dose-proportionality/tests'))
from pk_benchmark import grade, oracle_answer, reconstruct  # noqa: E402

GOLD = reconstruct(ROOT/'fixtures/eval_pk_smoke/source-data/ind_enabling/BioA_dog_plasma.tsv')


def test_oracle_scores_one_and_empty_zero():
    assert grade(GOLD, oracle_answer(GOLD))['reward'] == 1.0
    assert grade(GOLD, {})['reward'] == 0.0


def test_single_wrong_field_scores_zero():
    for edit in (lambda a: a['results']['F']['groups']['60'].update(cmax_mean_ng_ml=1.0),
                 lambda a: a['results']['M']['ratios']['20-200'].update(auc0_24_ratio=10.0),
                 lambda a: a.update(conclusion='approximately_dose_proportional_overall'),
                 lambda a: a['results']['M']['groups']['20'].update(evidence_animal_ids=['x', 'y']),
                 lambda a: a.update(items=[])):
        answer = copy.deepcopy(oracle_answer(GOLD))
        edit(answer)
        assert grade(GOLD, answer)['reward'] == 0.0


def test_conclusion_follows_the_data():
    assert GOLD['conclusion'] == 'greater_than_dose_proportional_overall'
