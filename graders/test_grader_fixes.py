"""Row-level credit on the objection map and the wider recovery-count correction.

Fictional fixture throughout: an invented letter and an invented filed document.
"""
import pytest

from graders import taskgrader as tg

LETTER = 'The fictional agency asks for a completed ninety day study and a sampling plan.'
FILED = 'The fictional filing includes a completed sampling plan for every cohort enrolled.'
QUOTE = 'a completed sampling plan for every cohort'


@pytest.fixture
def workspace(tmp_path):
    (tmp_path/'ind').mkdir()
    (tmp_path/'letter.txt').write_text(LETTER)
    (tmp_path/'ind/a.txt').write_text(FILED)
    return tmp_path


def gold():
    cite = {'path': 'ind/a.txt', 'page': 1}
    letter = {'path': 'letter.txt', 'page': 1}
    rows = [('h1', 'hold_deficiency', 'absent', []),
            ('c1', 'non_hold_comment', 'present', [cite]),
            ('c2', 'non_hold_comment', 'partially_present', [cite])]
    return {'task_id': 'hold-objection-map', 'schema_version': 2,
            'verification': {'status': 'synthetic_fixture', 'verified_by': 'test',
                             'verified_at': '2026-11-14', 'method': 'fictional fixture'},
            'criteria': [{'id': f'C{n}', 'item_id': key, 'desc': 'Check the item'}
                         for n, (key, *_) in enumerate(rows, 1)],
            'items': [{'item_id': key, 'kind': 'objection',
                       'expected': {'objection_id': key, 'category': category, 'status': status},
                       'accept': {'objection_cite': letter, 'filed_cites': cites}}
                      for key, category, status, cites in rows]}


def row(key, category, status, quote=QUOTE):
    cite = None if status == 'absent' else {'path': 'ind/a.txt', 'page': 1, 'quote': quote}
    return {'id': key, 'category': category, 'status': status, 'cite': cite}


def score(items, workspace):
    return tg.grade_v2({'items': items}, workspace, gold(), 'objection')


def test_objection_reference_answer_scores_one(workspace):
    result, _ = score([row('h1', 'hold_deficiency', 'absent'),
                       row('c1', 'non_hold_comment', 'present'),
                       row('c2', 'non_hold_comment', 'partially_present')], workspace)
    assert result == 1


def test_objection_correct_categories_alone_earn_nothing(workspace):
    # Every category is right and every status is wrong.
    result, details = score([row('h1', 'hold_deficiency', 'present'),
                             row('c1', 'non_hold_comment', 'absent'),
                             row('c2', 'non_hold_comment', 'absent')], workspace)
    assert result == 0
    assert all(item['credit'] == 0 for item in details['items'].values())


def test_objection_right_status_with_unsupported_quote_earns_nothing_for_that_row(workspace):
    result, details = score([row('h1', 'hold_deficiency', 'absent'),
                             row('c1', 'non_hold_comment', 'present', quote='words that are not in the filed document'),
                             row('c2', 'non_hold_comment', 'partially_present')], workspace)
    assert details['items']['c1']['credit'] == 0
    assert result == pytest.approx(2/3)


def test_objection_all_absent_earns_only_the_truly_absent_rows(workspace):
    result, _ = score([row('h1', 'hold_deficiency', 'absent'),
                       row('c1', 'non_hold_comment', 'absent'),
                       row('c2', 'non_hold_comment', 'absent')], workspace)
    assert result == pytest.approx(1/3)


RECOVERY = {'type': 'contains', 'accept': ['0', 'zero', 'none'],
            'any': ['0/4', '0 of 4', 'no gliosis', 'zero']}


@pytest.mark.parametrize('given', ['0', 'Zero', '0/4', '0/4 (no gliosis in recovery animals)',
                                   'No gliosis at the 28-day recovery timepoint',
                                   '0 of 4 recovery animals showed gliosis'])
def test_correction_accepts_exact_label_or_a_phrase_naming_the_value(given):
    assert tg._correction_matches(given, RECOVERY)


@pytest.mark.parametrize('given', ['1/4', '1/4 animals at the 30-day recovery timepoint', '30', 'gliosis'])
def test_correction_rejects_values_that_do_not_name_the_correction(given):
    assert not tg._correction_matches(given, RECOVERY)
