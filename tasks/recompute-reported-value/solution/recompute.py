"""Recompute the selected arithmetic mean from its source wells."""
import argparse
import json
from pathlib import Path

import pandas as pd


def recompute(workspace):
    folder = workspace / 'source-data/elisa'
    summary = pd.read_csv(folder / '026_summary.tsv', sep='\t').iloc[6]
    well_path = folder / '026.tsv'
    wells = pd.read_csv(well_path, sep='\t')
    matched = wells.loc[(wells['detail'] == summary['sample'])
                        & (wells['standard_curve'] == summary['standard_curve']), 'ngml_trunc'].dropna()
    if len(matched) != 2:
        raise ValueError('Expected exactly two usable wells for the selected sample and curve')
    return {'reported': float(summary['ngml_av']), 'recomputed': float(matched.mean()),
            'inputs': [{'path': well_path.relative_to(workspace).as_posix(), 'sheet': '',
                        'row': int(row) + 2, 'col': 'L'} for row in matched.index]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workspace', type=Path)
    args = parser.parse_args()
    print(json.dumps(recompute(args.workspace), allow_nan=False))
