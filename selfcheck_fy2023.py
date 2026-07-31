import io, re, json, sys

ann_path = 'data/annotated/NVDA_FY2023_annotation.json'
tpl_path = 'data/annotated/ORCL_FY2024_annotation.json'
raw_path = 'data/raw/nvda_fy2023_10k.html'

with io.open(ann_path, encoding='utf-8') as f:
    ann = json.load(f)
print('[1] json.load OK')

with io.open(tpl_path, encoding='utf-8') as f:
    tpl = json.load(f)
assert list(ann.keys()) == list(tpl.keys()), (list(ann.keys()), list(tpl.keys()))
print('[2] top-level 9 keys match ORCL template:', list(ann.keys()))
assert len(ann.keys()) == 9

# weights
ws = [d['weight'] for d in ann['dimension_scores']]
s = sum(ws)
print('[3] weights:', ws, 'sum =', round(s, 6))
assert abs(s - 1.0) < 1e-9, 'weights sum != 1'

# weighted composite
comp = sum(d['score'] * d['weight'] for d in ann['dimension_scores'])
rep = ann['composite_score']['weighted_score']
print('[4] computed composite =', round(comp, 4), '| reported =', rep, '| diff =', abs(comp - rep))
assert abs(comp - rep) <= 0.01, 'composite mismatch'

# score_breakdown internal consistency
for k, v in ann['composite_score']['score_breakdown'].items():
    assert abs(v['score'] * v['weight'] - v['weighted']) < 1e-9, k
print('[5] score_breakdown consistent')

# verbatim quote check (at least 5 required; check all signal excerpts' first sentences)
with io.open(raw_path, encoding='utf-8', errors='replace') as f:
    raw = f.read()

def detag(x):
    x = re.sub(r'<[^>]+>', '', x)
    x = x.replace('&nbsp;', ' ').replace('&#160;', ' ').replace('&amp;', '&')
    return re.sub(r'\s+', ' ', x)

full = detag(raw)

def fragments(excerpt):
    # split on ' ... ' ellipsis; each fragment must appear verbatim
    return [re.sub(r'\s+', ' ', fr.strip(' .')) for fr in excerpt.split('...') if len(fr.strip(' .')) > 25]

ok, fail = 0, 0
for sig in ann['risk_signals']:
    for fr in fragments(sig['text_excerpt']):
        if fr in full:
            ok += 1
        else:
            fail += 1
            print('  MISS', sig['signal_id'], ':', fr[:80])
print('[6] verbatim fragments OK =', ok, ', MISS =', fail, ', signals =', len(ann['risk_signals']))
assert ok >= 5 and fail == 0

assert 8 <= len(ann['risk_signals']) <= 12
print('[7] signal count in 8-12 range:', len(ann['risk_signals']))

# id sequence
ids = [s['signal_id'] for s in ann['risk_signals']]
exp = ['NVDA-FY2023-SIG-%03d' % i for i in range(1, len(ids) + 1)]
assert ids == exp, ids
print('[8] signal_id sequence OK:', ids[0], '...', ids[-1])

# cross-year anchor: recompute FY2024 confirmed composite
with io.open('data/annotated/NVDA_FY2024_annotation.json', encoding='utf-8') as f:
    ref = json.load(f)
ref_comp = sum(d['score'] * d['weight'] for d in ref['dimension_scores'])
print('[9] FY2024 confirmed composite recomputed =', round(ref_comp, 4), '(reported 3.10)')
assert abs(ref_comp - 3.10) <= 0.01

print('\nALL CHECKS PASSED')
print('FY2023: D1=%d D2=%d D3=%d D4=%d D5=%d -> %.2f' % tuple(
    [d['score'] for d in ann['dimension_scores']] + [comp]))
