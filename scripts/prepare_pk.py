"""Stage the PK task and compute its private gold from the local pack.

    python scripts/prepare_pk.py --pack-root <pack>/divalent-sirna-ind-167326

Copies the manifest-listed TSV into the task workspace, computes gold with
tests/pk_benchmark.py, and writes tests/gold.json (verification pending) and
solution/answer.json. No scientific choices are made here.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from stage import stage  # noqa: E402

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pack-root', type=Path, required=True)
    ap.add_argument('--task', type=Path, default=ROOT/'tasks/pk-dose-proportionality')
    args = ap.parse_args()
    sys.path.insert(0, str(args.task/'tests'))
    from pk_benchmark import SEXES, DOSES, oracle_answer, reconstruct

    stage(args.task, args.pack_root.expanduser())
    gold = reconstruct(args.task/'environment/workspace/BioA_dog_plasma.tsv')
    previous = {}
    gold_path = args.task/'tests/gold.json'
    if gold_path.exists():
        previous = json.loads(gold_path.read_text()).get('verification', {})
    gold['verification'] = previous or {
        'status': 'pending_human_verification', 'who': '', 'how': '',
        'how_to_verify': 'Recompute Cmax and AUC0-24 for one sex/dose group by hand or in a spreadsheet '
                         'from BioA_dog_plasma.tsv and confirm it matches. Then set status to '
                         'human_verified and fill who/how.',
        'answerable_from_workspace': True,
        'evidence': []}
    gold['answer_schema'] = {'type': 'object', 'required': ['source_file', 'results', 'conclusion'],
                             'properties': {'source_file': {'type': 'string'}, 'results': {'type': 'object'},
                                            'conclusion': {'type': 'string'}}}
    gold_path.write_text(json.dumps(gold, indent=2)+'\n')
    (args.task/'solution').mkdir(exist_ok=True)
    (args.task/'solution/answer.json').write_text(json.dumps(oracle_answer(gold), indent=2)+'\n')
    print('Wrote', gold_path, 'and solution/answer.json')
    for sex in SEXES:
        for dose in DOSES:
            g = gold['results'][sex]['groups'][str(dose)]
            print(f'{sex} {dose} mg: Cmax={g["cmax_mean_ng_ml"]:.2f}  AUC0-24={g["auc0_24_mean_ng_h_ml"]:.2f}  BLQ rows={g["blq_rows_0_24"]}')
    for sex in SEXES:
        r = gold['results'][sex]['ratios']['20-200']
        print(f'{sex} 20->200 mg: AUC ratio {r["auc0_24_ratio"]:.2f} vs dose ratio {r["dose_ratio"]:.0f}')
    print('Conclusion by rule:', gold['conclusion'])
