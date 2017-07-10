# import bibtexparser
from fixtex import fix_bib
import utool as ut
import numpy as np
import pandas as pd

pd.options.display.max_rows = 20
pd.options.display.max_columns = 40
pd.options.display.width = 160
pd.options.display.float_format = lambda x: '%.4f' % (x,)

# PARSE DATABASE
# full_bibman = fix_bib.BibMan('FULL.bib', doc='thesis')

bibman = fix_bib.BibMan('final-bib.bib', doc='thesis')
bibman.sort_entries()
bibman.write_testfile()
bibman.printdiff()
bibman.save()

print('bibman.unregistered_pubs = {}'.format(ut.repr4(bibman.unregistered_pubs)))
for pub in bibman.unregistered_pubs:
    if 'None' in str(pub):
        print(ut.repr4(pub.entry))


df = pd.DataFrame.from_dict(bibman.cleaned, orient='index')
del df['abstract']

# want = text.count('@')
want = len(df)

# paged_items = df[~pd.isnull(df['pub_abbrev'])]
# has_pages = ~pd.isnull(paged_items['pages'])
# print('have pages {} / {}'.format(has_pages.sum(), len(has_pages)))
# print(ut.repr4(paged_items[~has_pages]['title'].values.tolist()))

df.loc[pd.isnull(df['pub_type']), 'pub_type'] = 'None'

entrytypes = dict(list(df.groupby('pub_type')))
n_grouped = sum(map(len, entrytypes.values()))
assert n_grouped == want

pub_types = {
    'journal': None,
    'conference': None,
    'incollection': None,
    'online': None,
    'thesis': None,
    'report': None,
    'book': None,
}

for unknown in set(entrytypes.keys()).difference(set(pub_types)):
    print('unknown = {!r}'.format(unknown))
    g = entrytypes[unknown]
    g = g[g.columns[~np.all(pd.isnull(g), axis=0)]]
    print('g = {!r}'.format(g))

ignore = {
    'conference': ['eventtitle', 'doi', 'urldate', 'location', 'volume'],
    'journal': ['doi', 'urldate', 'issue', 'number', 'volume'],
    'book': ['urldate'],
    'thesis': ['urldate'],
    'online': ['type'],
    'report': ['urldate'],
}
for v in ignore.values():
    v.append('eprinttype')
    v.append('eprint')

print('Entry type freq:')
print(ut.map_vals(len, entrytypes))

for e, g in entrytypes.items():
    print('\n --- TYPE = %r' % (e.upper(),))
    g = g[g.columns[~np.all(pd.isnull(g), axis=0)]]
    missing_cols = g.columns[np.any(pd.isnull(g), axis=0)]
    if e in ignore:
        missing_cols = missing_cols.difference(ignore[e])
    print('missing_cols = {!r}'.format(missing_cols.tolist()))
    for col in missing_cols:
        print('col = {!r}'.format(col))
        print(g[pd.isnull(g[col])].index.tolist())

for e, g in entrytypes.items():
    print('e = %r' % (e,))
    g = g[g.columns[~np.all(pd.isnull(g), axis=0)]]
    if 'pub_full' in g.columns:
        place_title = g['pub_full'].tolist()
        print(ut.repr4(ut.dict_hist(place_title)))
    else:
        print(g)
        print('Unknown publications')

if 'report' in entrytypes:
    g = entrytypes['report']
    missing = g[pd.isnull(g['title'])]
    if len(missing):
        print('Missing Title')
        print(ut.repr4(missing[['title', 'author']].values.tolist()))

if 'journal' in entrytypes:
    g = entrytypes['journal']
    g = g[g.columns[~np.all(pd.isnull(g), axis=0)]]

    missing = g[pd.isnull(g['journal'])]
    if len(missing):
        print('Missing Journal')
        print(ut.repr4(missing[['title', 'author']].values.tolist()))

if 'conference' in entrytypes:
    g = entrytypes['conference']
    g = g[g.columns[~np.all(pd.isnull(g), axis=0)]]

    missing = g[pd.isnull(g['booktitle'])]
    if len(missing):
        print('Missing Booktitle')
        print(ut.repr4(missing[['title', 'author']].values.tolist()))

if 'incollection' in entrytypes:
    g = entrytypes['incollection']
    g = g[g.columns[~np.all(pd.isnull(g), axis=0)]]

    missing = g[pd.isnull(g['booktitle'])]
    if len(missing):
        print('Missing Booktitle')
        print(ut.repr4(missing[['title', 'author']].values.tolist()))

if 'thesis' in entrytypes:
    g = entrytypes['thesis']
    g = g[g.columns[~np.all(pd.isnull(g), axis=0)]]
    missing = g[pd.isnull(g['institution'])]
    if len(missing):
        print('Missing Institution')
        print(ut.repr4(missing[['title', 'author']].values.tolist()))
