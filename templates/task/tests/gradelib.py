"""Strict, dependency-light primitives shared by task verifiers.

Paths refer to files inside the staged workspace; PDF pages and spreadsheet
coordinates are 1-based. This module is copied into task tests, never the image.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import subprocess
import unicodedata
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path


def load_answer(path):
    try:
        def unique_pairs(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError('Duplicate JSON key')
                result[key] = value
            return result
        def invalid_constant(value):
            raise ValueError('Non-finite JSON number')
        value = json.loads(Path(path).read_text(), object_pairs_hook=unique_pairs,
                           parse_constant=invalid_constant)
        return value if isinstance(value, dict) else None
    except (OSError, ValueError, UnicodeError):
        return None


def validate(answer, schema_dict):
    """Supported JSON-schema subset; reject unsupported constraints explicitly."""
    errors = []
    supported = {'type', 'required', 'properties', 'additionalProperties', 'items',
                 'enum', 'minItems', 'maxItems', 'minLength', 'minimum', 'maximum',
                 'description', 'title', '$schema'}

    def visit(value, schema, where):
        if set(schema) - supported:
            raise ValueError(f'Unsupported schema keys: {set(schema) - supported}')
        types = {'object': lambda v: isinstance(v, dict),
                 'array': lambda v: isinstance(v, list),
                 'string': lambda v: isinstance(v, str),
                 'number': lambda v: type(v) is int or (type(v) is float and math.isfinite(v)),
                 'integer': lambda v: type(v) is int,
                 'boolean': lambda v: type(v) is bool,
                 'null': lambda v: v is None}
        kind = schema.get('type')
        kinds = kind if isinstance(kind, list) else [kind]
        if kind and not any(k in types and types[k](value) for k in kinds):
            errors.append(f'{where}: expected {kind}')
            return
        if 'enum' in schema and not any(type(value) is type(v) and value == v for v in schema['enum']):
            errors.append(f'{where}: invalid enum')
        if isinstance(value, dict):
            for key in schema.get('required', []):
                if key not in value:
                    errors.append(f'{where}: missing {key}')
            for key, val in value.items():
                props = schema.get('properties', {})
                if key in props:
                    visit(val, props[key], f'{where}.{key}')
                elif schema.get('additionalProperties') is False:
                    errors.append(f'{where}: unexpected {key}')
        if isinstance(value, list):
            if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', float('inf')):
                errors.append(f'{where}: invalid length')
            if 'items' in schema:
                for i, val in enumerate(value):
                    visit(val, schema['items'], f'{where}[{i}]')
        if isinstance(value, str) and len(value) < schema.get('minLength', 0):
            errors.append(f'{where}: string too short')
        if type(value) in (int, float):
            if (type(value) is float and not math.isfinite(value)) or value < schema.get('minimum', -float('inf')) or value > schema.get('maximum', float('inf')):
                errors.append(f'{where}: invalid number')
    visit(answer, schema_dict, '$')
    return errors


def norm_text(s):
    s = unicodedata.normalize('NFKC', str(s)).casefold()
    s = s.replace('μ', 'µ')
    s = re.sub('[‐‑‒–—−]', '-', s)
    return ' '.join(s.split())


def norm_path(p, workspace):
    if not isinstance(p, str) or not p or '\\' in p or '\x00' in p:
        return None
    root = Path(workspace).resolve()
    path = Path(p)
    if '..' in path.parts:
        return None
    # Canonical in-container prefix is also accepted during local sanity runs.
    if p.startswith('/app/workspace/'):
        path = Path(p.removeprefix('/app/workspace/'))
    target = (root / path).resolve()
    try:
        relative = target.relative_to(root)
    except ValueError:
        return None
    return relative.as_posix() if target.is_file() else None


@lru_cache(maxsize=64)
def _file_pages(path, mtime, size):
    p = Path(path)
    if p.suffix.lower() == '.pdf':
        texts = []
        try:
            import pdfplumber
            with pdfplumber.open(p) as pdf:
                texts = [page.extract_text() or '' for page in pdf.pages]
        except Exception:
            pass
        if not any(t.strip() for t in texts):
            try:
                from pypdf import PdfReader
                texts = [page.extract_text() or '' for page in PdfReader(p).pages]
            except Exception:
                pass
        if not any(t.strip() for t in texts):
            try:
                result = subprocess.run(['pdftotext', '-layout', str(p), '-'],
                                        capture_output=True, text=True, check=True, timeout=60)
                texts = result.stdout.removesuffix('\f').split('\f')
            except (OSError, subprocess.SubprocessError):
                pass
        return tuple(texts)
    if p.suffix.lower() not in {'.txt', '.md', '.csv', '.tsv'}:
        raise ValueError('Use cell_value for spreadsheet files')
    try:
        text = p.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:
        text = p.read_text(encoding='latin-1')
    matches = list(re.finditer(r'^=+\s*PAGE\s+(\d+)\s*=+\s*$', text, re.M))
    if matches:
        numbers = [int(m[1]) for m in matches]
        if numbers != list(range(1, len(matches) + 1)):
            raise ValueError('Page markers must be contiguous and 1-based')
        return tuple(text[m.end():matches[i+1].start() if i+1 < len(matches) else len(text)]
                     for i, m in enumerate(matches))
    return tuple(text.split('\f'))


def file_pages(path):
    p = Path(path).resolve()
    stat = p.stat()
    return list(_file_pages(str(p), stat.st_mtime_ns, stat.st_size))


def quote_in_file(quote, path, page=None, min_len=20):
    if not isinstance(quote, str) or len(norm_text(quote)) < min_len:
        return False
    try:
        pages = file_pages(path)
        if page is not None:
            if type(page) is not int or not 1 <= page <= len(pages):
                return False
            pages = [pages[page-1]]
        return any(norm_text(quote) in norm_text(text) for text in pages)
    except (OSError, ValueError):
        return False


def cell_value(path, sheet, row, col):
    """Coordinates are 1-based; flat tables use an empty or format-named sheet."""
    if type(row) is not int or row < 1:
        return None
    if isinstance(col, str):
        if not re.fullmatch('[A-Za-z]+', col):
            return None
        n = 0
        for ch in col.upper():
            n = n * 26 + ord(ch) - 64
        col = n
    if type(col) is not int or col < 1:
        return None
    p = Path(path)
    try:
        if p.suffix.lower() in {'.csv', '.tsv'}:
            fmt = p.suffix.lower()[1:]
            if sheet not in (None, '', fmt):
                return None
            delim = '\t' if fmt == 'tsv' else ','
            for encoding in ('utf-8-sig', 'latin-1'):
                try:
                    with p.open(newline='', encoding=encoding) as f:
                        rows = list(csv.reader(f, delimiter=delim))
                    break
                except UnicodeDecodeError:
                    continue
            return rows[row-1][col-1] if row <= len(rows) and col <= len(rows[row-1]) else None
        if p.suffix.lower() == '.xlsx':
            from openpyxl import load_workbook
            wb = load_workbook(p, read_only=True, data_only=True)
            try:
                if sheet not in wb.sheetnames:
                    return None
                ws = wb[sheet]
                return ws.cell(row, col).value if row <= ws.max_row and col <= ws.max_column else None
            finally:
                wb.close()
    except (OSError, ValueError, KeyError):
        return None
    return None


def num_close(a, b, rtol=0.02, atol=0.0):
    if type(a) not in (int, float) or type(b) not in (int, float):
        return False
    return math.isfinite(a) and math.isfinite(b) and abs(a-b) <= max(atol, rtol*abs(b))


def parse_number(value):
    """Finite decimal with explicit syntax; no guessing signs, units or missingness.

    Accept grouped thousands, scientific notation and parenthesized negatives.
    Zero stays zero; ND, <LOD, percent signs and prose are not numeric values.
    """
    if isinstance(value, bool) or value is None:
        raise ValueError('Not a number')
    text = unicodedata.normalize('NFKC', str(value)).strip().replace('−', '-')
    if len(text)>128:
        raise ValueError('Numeric representation too long')
    negative = text.startswith('(') and text.endswith(')')
    if negative:
        text = text[1:-1].strip()
        if text.startswith(('+', '-')):
            raise ValueError('Ambiguous sign')
    pattern = r'[+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
    if not re.fullmatch(pattern, text):
        raise ValueError('Invalid numeric syntax')
    try:
        number = Decimal(text.replace(',', ''))
    except InvalidOperation as exc:
        raise ValueError('Invalid decimal') from exc
    if not number.is_finite() or abs(number.as_tuple().exponent)>1000 or (number and abs(number.adjusted())>1000):
        raise ValueError('Non-finite number')
    return -number if negative else number


# Only unit conversions whose dimensions are unambiguous are supported.
# No mg/kg-to-mg, biological activity, molecular weight, or time-point inference.
_UNITS = {
    'g': ('mass', '1'), 'mg': ('mass', '.001'), 'µg': ('mass', '.000001'),
    'ug': ('mass', '.000001'), 'ng': ('mass', '.000000001'),
    'g/l': ('concentration', '1'), 'mg/ml': ('concentration', '1'),
    'mg/l': ('concentration', '.001'), 'µg/ml': ('concentration', '.001'),
    'ug/ml': ('concentration', '.001'), 'ng/ml': ('concentration', '.000001'),
    '%': ('fraction', '.01'), 'fraction': ('fraction', '1'),
}


def quantity_close(value, unit, expected, expected_unit, rtol=0, atol=0):
    """Compare after declared unit conversion; atol is in expected_unit."""
    try:
        actual, target = parse_number(value), parse_number(expected)
        relative, absolute = parse_number(rtol), parse_number(atol)
        if relative < 0 or absolute < 0:
            return False
        unit, expected_unit = norm_text(unit), norm_text(expected_unit)
        if unit != expected_unit:
            left, right = _UNITS.get(unit), _UNITS.get(expected_unit)
            if not left or not right or left[0] != right[0]:
                return False
            actual = actual*Decimal(left[1])/Decimal(right[1])
        return abs(actual-target) <= max(absolute, relative*abs(target))
    except (ValueError, InvalidOperation):
        return False


def location_key(ref, workspace):
    """Canonical path plus exact 1-based cell/page, rejecting nonexistent values."""
    path = norm_path(ref.get('path'), workspace)
    if path is None:
        return None
    if 'row' in ref or 'col' in ref or 'sheet' in ref:
        row, col, sheet = ref.get('row'), ref.get('col'), ref.get('sheet')
        if cell_value(Path(workspace)/path, sheet, row, col) is None:
            return None
        if isinstance(col, str):
            n = 0
            for ch in col.upper(): n = n*26+ord(ch)-64
            col = n
        return (path, sheet or Path(path).suffix.lower()[1:], row, col)
    page = ref.get('page')
    try:
        if type(page) is int and 1 <= page <= len(file_pages(Path(workspace)/path)):
            return (path, page)
    except (OSError, ValueError):
        pass
    return None


def evidence_check(ref, workspace):
    """Check location and supplied source value/quote without judging semantics."""
    key = location_key(ref, workspace)
    if key is None:
        return False
    if len(key) == 4:
        if 'value' not in ref:
            return False
        actual = cell_value(Path(workspace)/key[0], key[1], key[2], key[3])
        return norm_text(actual) == norm_text(ref['value'])
    return quote_in_file(ref.get('quote'), Path(workspace)/key[0], key[1])


def primary_failure(checks):
    """First failed stage, with all independent booleans retained by the caller."""
    for name in ('format', 'grounding', 'extraction', 'method', 'calculation', 'comparison'):
        if checks.get(name) is False:
            return name
    return 'correct'


def set_f1(pred_keys, gold_keys):
    pred, gold = set(pred_keys), set(gold_keys)
    tp = len(pred & gold)
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(gold) if gold else 0.0
    return precision, recall, 2*precision*recall/(precision+recall) if precision+recall else 0.0


def write_score(score, details, output_dir=None):
    score = float(score)
    score = min(1.0, max(0.0, score)) if math.isfinite(score) else 0.0
    out = Path(output_dir or os.environ.get('HOLDOUT_SCORE_DIR', '/logs/verifier'))
    out.mkdir(parents=True, exist_ok=True)
    (out / 'reward.txt').write_text(f'{score:.12g}\n')
    result = {'score': score, 'reward': score, 'details': details}
    if 'criteria' in details:
        result.update({key: details[key] for key in ('criteria', 'criteria_met', 'criteria_total', 'pass')})
    (out / 'score.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return score
