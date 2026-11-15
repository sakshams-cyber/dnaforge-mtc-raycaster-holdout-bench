"""Propose a reproducible ELISA well aggregation for a summary claim."""
import argparse
import json
from pathlib import Path

import pandas as pd


def recompute(pack, plate, row):
    folder = pack / 'source-data/elisa'
    summary = pd.read_csv(folder / f'{plate}_summary.tsv', sep='\t').iloc[row - 2]
    path = folder / f'{plate}.tsv'
    wells = pd.read_csv(path, sep='\t')
    values = wells.loc[wells['detail'].eq(summary['sample'])
                       & wells['standard_curve'].eq(summary['standard_curve']), 'ngml_trunc'].dropna()
    if len(values) != 2:
        raise ValueError('Expected two numeric wells for the same sample and curve')
    return {'reported': float(summary['ngml_av']),
            'values': {'mean_ng_ml': float(values.mean()), 'sum_ng_ml': float(values.sum()),
                       'range_ng_ml': float(values.max() - values.min())},
            'well_cells': [f'L{index + 2}' for index in values.index],
            'inputs': [{'path': path.relative_to(pack).as_posix(), 'sheet': ''}]}


def main(plate, row):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack', type=Path, default=Path('data/pack3'))
    parser.add_argument('--oracle', action='store_true', help='Print the task answer format')
    args = parser.parse_args()
    result = recompute(args.pack, plate, row)
    if args.oracle:
        mean = result['values']['mean_ng_ml']
        reported = result['reported']
        result = {'values': result['values'], 'method': 'raw_mean', 'inputs': result['inputs'],
                  'matches_reported': abs(mean - reported) <= 0.02 * abs(reported)}
    print(json.dumps(result, allow_nan=False))


if __name__ == '__main__':
    main('026', 8)
