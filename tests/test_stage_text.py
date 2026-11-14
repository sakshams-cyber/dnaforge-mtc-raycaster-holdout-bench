"""Plant edits must leave no formatting trace and never disturb page markers."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from stage_text import _substitute  # noqa: E402


def apply(text, before, after):
    pattern = r'(?<![\w.,])' + r'\s+'.join(re.escape(w) for w in before.split()) + r'(?!\w|[.,]\d)'
    found = list(re.finditer(pattern, text))
    assert len(found) == 1
    return _substitute(text, found[0], before, after)


def test_table_cell_keeps_column_alignment():
    row = '   3 - Mid      60      120.0      20.0      4\n'
    out = apply(row, '20.0', '5.5')
    assert out == '   3 - Mid      60      120.0       5.5      4\n'


def test_prose_word_swap_keeps_line_breaks():
    text = 'The limit in ferrets was\n50 mg, the top dose.\n'
    assert apply(text, 'ferrets was 50 mg', 'ferrets was 5 mg') == 'The limit in ferrets was\n5 mg, the top dose.\n'


def test_sentence_replacement_rewraps_only_its_paragraph():
    text = ('===== PAGE 1 =====\nHeader line\n\n'
            'Alpha beta gamma delta epsilon zeta eta theta.\n'
            'One two three four five six seven eight nine.\n'
            'Ten eleven twelve thirteen fourteen fifteen x.\n'
            'Short end.\n\nNext paragraph stays.\n')
    out = apply(text, 'One two three four five six seven eight nine.', 'Gone.')
    assert out.startswith('===== PAGE 1 =====\nHeader line\n\nAlpha beta gamma delta epsilon zeta eta theta.\n')
    assert out.endswith('\n\nNext paragraph stays.\n')
    assert 'Gone. Ten eleven twelve' in out and 'One two' not in out
    assert max(len(line) for line in out.split('\n')) <= 46
