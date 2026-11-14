"""Read-only, local source inspection; no grader, gold, model or network access.

JSON output preserves physical page/cell coordinates and original numeric text.
Optional JSONL trace stores call metadata and output hashes, not source excerpts.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time


def source_path(workspace, name):
    root = Path(workspace).resolve()
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:
        raise ValueError('Use workspace-relative paths without traversal')
    path = (root/p).resolve()
    path.relative_to(root)
    if not path.is_file(): raise ValueError('File does not exist')
    return path


def text_pages(path):
    if path.suffix.lower() == '.pdf':
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return [page.extract_text(layout=True) or '' for page in pdf.pages]
    text = path.read_text(encoding='utf-8-sig')
    parts = re.split(r'^=+\s*PAGE\s+(\d+)\s*=+\s*$',text,flags=re.M)
    if len(parts)>1:
        numbers = [int(parts[i]) for i in range(1,len(parts),2)]
        if numbers != list(range(1,len(numbers)+1)):
            raise ValueError('Noncontiguous page markers')
        return [parts[i] for i in range(2,len(parts),2)]
    return text.split('\f')


def inspect(workspace, operation, path=None, page=1, sheet=None, row=None, col=None,
            query=None, limit=10):
    root=Path(workspace).resolve()
    if type(limit) is not int or not 1<=limit<=100:
        raise ValueError('limit must be 1..100')
    if operation=='list':
        files=[]
        for p in sorted(root.rglob('*')):
            if p.is_file() and not p.is_symlink():
                source_path(root,p.relative_to(root).as_posix())
                files.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,
                              'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        return {'files':files}
    if operation=='search':
        if not query or len(query)>200: raise ValueError('query must have 1..200 characters')
        hits=[]
        candidates=[source_path(root,path)] if path else sorted(root.rglob('*'))
        for p in candidates:
            if not p.is_file() or p.is_symlink() or p.suffix.lower() not in {'.pdf','.txt','.md','.csv'}:
                continue
            relative=p.relative_to(root).as_posix()
            source_path(root,relative)
            for number,text in enumerate(text_pages(p),1):
                # Literal case-insensitive search with original offsets retained.
                for match in re.finditer(re.escape(query),text,re.I):
                    start=match.start()
                    hits.append({'path':relative,'page':number,'offset':start,
                                 'snippet':text[max(0,start-80):start+len(query)+80]})
                    if len(hits)>=limit: return {'hits':hits,'limit_reached':True}
        return {'hits':hits,'limit_reached':False}
    p=source_path(root,path)
    if operation=='cell':
        if type(row) is not int or row<1: raise ValueError('row is 1-based')
        if isinstance(col,str):
            if not re.fullmatch('[A-Za-z]+',col): raise ValueError('Invalid column')
            number=0
            for ch in col.upper(): number=number*26+ord(ch)-64
            col=number
        if type(col) is not int or col<1: raise ValueError('column is 1-based')
        if p.suffix.lower()=='.csv':
            if sheet not in (None,'','csv'): raise ValueError('CSV sheet is csv')
            with p.open(newline='',encoding='utf-8-sig') as f: rows=list(csv.reader(f))
            if row>len(rows) or col>len(rows[row-1]): raise ValueError('Cell does not exist')
            return {'path':path,'sheet':'csv','row':row,'col':col,'value':rows[row-1][col-1],
                    'header_row':rows[0], 'source_row':rows[row-1]}
        if p.suffix.lower()=='.xlsx':
            from openpyxl import load_workbook
            wb=load_workbook(p,data_only=False)
            try:
                if sheet not in wb.sheetnames: raise ValueError('Sheet does not exist')
                ws=wb[sheet]
                if row>ws.max_row or col>ws.max_column: raise ValueError('Cell does not exist')
                cell=ws.cell(row,col)
                return {'path':path,'sheet':sheet,'row':row,'col':col,'value':cell.value,
                        'formula_not_evaluated':cell.data_type=='f',
                        'merged_ranges':[str(r) for r in ws.merged_cells.ranges],
                        'header_row':[c.value for c in ws[1]],
                        'source_row':[c.value for c in ws[row]]}
            finally: wb.close()
        raise ValueError('Cell access supports CSV/XLSX')
    if operation!='page': raise ValueError('Unknown operation')
    if type(page) is not int or page<1: raise ValueError('page is 1-based')
    if p.suffix.lower()=='.pdf':
        import pdfplumber
        with pdfplumber.open(p) as pdf:
            if page>len(pdf.pages): raise ValueError('Page does not exist')
            source=pdf.pages[page-1]
            tables=[]
            for number,table in enumerate(source.find_tables(),1):
                tables.append({'table':number,'bbox':table.bbox,'rows':table.extract(),
                               'row_cell_boxes':[r.cells for r in table.rows]})
            return {'path':path,'page':page,'text':source.extract_text(layout=True) or '',
                    'words':source.extract_words(),'tables':tables,
                    'note':'Extraction may be incomplete. Empty/merged cells are not inferred; inspect the original PDF.'}
    pages=text_pages(p)
    if page>len(pages): raise ValueError('Page does not exist')
    return {'path':path,'page':page,'text':pages[page-1]}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workspace',type=Path,default=Path('/app/workspace'))
    ap.add_argument('--trace',type=Path)
    ap.add_argument('operation',choices=['list','search','page','cell'])
    for name in ('path','sheet','query','col'): ap.add_argument('--'+name)
    for name,default in [('page',1),('row',None),('limit',10)]:
        ap.add_argument('--'+name,type=int,default=default)
    args=vars(ap.parse_args()); trace=args.pop('trace'); start=time.monotonic()
    try:
        output=inspect(**args); status='ok'; exit_code=0
    except Exception as exc:
        output={'error':type(exc).__name__};status='error';exit_code=1
    encoded=json.dumps(output,default=str,ensure_ascii=False)
    if trace:
        trace.parent.mkdir(parents=True,exist_ok=True)
        event={'time':datetime.now(timezone.utc).isoformat(),'operation':args['operation'],
               'path':args['path'],'status':status,'elapsed_sec':time.monotonic()-start,
               'page':args['page'],'sheet':args['sheet'],'row':args['row'],'col':args['col'],
               'query_sha256':hashlib.sha256((args['query'] or '').encode()).hexdigest(),
               'output_sha256':hashlib.sha256(encoded.encode()).hexdigest(),
               'output_bytes':len(encoded.encode())}
        with trace.open('a') as f: f.write(json.dumps(event)+'\n')
    print(encoded)
    raise SystemExit(exit_code)
