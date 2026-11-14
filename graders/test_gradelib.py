import json
from pathlib import Path

import pytest

from graders.gradelib import (cell_value, file_pages, load_answer, norm_path,
                             norm_text, num_close, quote_in_file, set_f1,
                             validate, write_score)


def test_answers(tmp_path):
    p = tmp_path/'answer.json'
    assert load_answer(p) is None
    for content in ['bad', '[]', 'null']:
        p.write_text(content)
        assert load_answer(p) is None
    p.write_text('{"items": []}')
    assert load_answer(p) == {'items': []}


def test_schema():
    schema = {'type': 'object', 'required': ['n'], 'additionalProperties': False,
              'properties': {'n': {'type': 'integer', 'minimum': 1}}}
    assert validate({'n': 1}, schema) == []
    for a in [{}, {'n': True}, {'n': 0}, {'n': 1, 'extra': 2}]:
        assert validate(a, schema)
    assert validate({'n': float('nan')}, {'type': 'object', 'properties': {'n': {'type': 'number'}}})
    with pytest.raises(ValueError):
        validate({}, {'oneOf': []})
    assert validate(['x'], {'type': 'array', 'minItems': 2, 'items': {'type': 'integer'}})
    assert validate('x', {'type': 'string', 'minLength': 2})
    assert validate(True, {'enum': [1]})


def test_normalizers_and_symlinks(tmp_path):
    assert norm_text('Ａ  μg—DOSE\n') == 'a µg-dose'
    root = tmp_path/'ws'; root.mkdir()
    (root/'a.txt').write_text('hello')
    outside = tmp_path/'secret'; outside.write_text('secret')
    (root/'escape').symlink_to(outside)
    assert norm_path('a.txt', root) == 'a.txt'
    assert norm_path('/app/workspace/a.txt', root) == 'a.txt'
    for p in ['../secret', str(outside), 'escape', 'missing', 'a\\b', '']:
        assert norm_path(p, root) is None


def test_pages_and_quotes(tmp_path):
    p = tmp_path/'doc.md'
    p.write_text('=== PAGE 1 ===\nA sufficiently long statement about a dose.\n=== PAGE 2 ===\nA different sufficiently long statement here.')
    assert len(file_pages(p)) == 2
    assert quote_in_file('A SUFFICIENTLY  long statement about a dose.', p, 1)
    assert not quote_in_file('A sufficiently long statement about a dose.', p, 2)
    assert not quote_in_file('dose', p, 1)
    assert not quote_in_file('A sufficiently long statement about a dose.', p, 0)
    assert not quote_in_file('A sufficiently long statement about a dose.', p, True)
    p.write_text('Changed sufficiently long statement here.')
    assert len(file_pages(p)) == 1
    assert not quote_in_file('A sufficiently long statement about a dose.', p)


def test_pdf(tmp_path):
    from reportlab.pdfgen.canvas import Canvas
    p = tmp_path/'doc.pdf'; c = Canvas(str(p))
    c.drawString(30, 700, 'A sufficiently long source statement.'); c.showPage(); c.save()
    assert quote_in_file('A sufficiently long source statement.', p, 1)


def test_cells(tmp_path):
    from openpyxl import Workbook
    p = tmp_path/'a.csv'; p.write_text('id,value\nrow1,2.5\n')
    assert cell_value(p, 'csv', 2, 'B') == '2.5'
    for sheet, row, col in [('wrong', 1, 1), ('csv', 0, 1), ('csv', 3, 1), ('csv', 1, 9)]:
        assert cell_value(p, sheet, row, col) is None
    wb = Workbook(); ws = wb.active; ws.title = 'Data'; ws['B2'] = 2.5
    x = tmp_path/'a.xlsx'; wb.save(x)
    assert cell_value(x, 'Data', 2, 'B') == 2.5
    assert cell_value(x, 'Missing', 2, 'B') is None
    assert cell_value(x, 'Data', 10, 'B') is None


def test_numbers_sets_and_score(tmp_path):
    assert num_close(102, 100)
    assert not num_close(103, 100)
    assert not num_close(True, 1)
    assert not num_close(float('inf'), float('inf'))
    assert not num_close('100', 100)
    assert set_f1(['a', 'a'], ['a']) == (1, 1, 1)
    assert set_f1([], []) == (0, 0, 0)
    assert set_f1(['a','b'], ['a'])[0] == 0.5
    assert write_score(2, {}, tmp_path) == 1
    assert write_score(float('nan'), {}, tmp_path) == 0
    assert json.loads((tmp_path/'score.json').read_text())['score'] == 0
