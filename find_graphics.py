import utool as ut
from fixtex import latex_parser


def testdata_fpaths():
    dpath = '.'
    #tex_fpath_list = ut.ls(dpath, 'chapter*.tex') + ut.ls(dpath, 'appendix.tex')
    patterns = [
        'chapter*.tex',
        'sec-*.tex',
        'figdef*.tex',
        'def.tex',
        'pairwise-classifier.tex',
        'graph-id.tex',
        'appendix.tex',
        'main.tex',
        'graph_id.tex',
    ]
    exclude_dirs = ['guts']
    tex_fpath_list = sorted(
        ut.glob(dpath, patterns, recursive=True, exclude_dirs=exclude_dirs)
    )
    tex_fpath_list = ut.get_argval('--fpaths', type_=list, default=tex_fpath_list)
    return tex_fpath_list

fpaths = testdata_fpaths()

fpath = 'main.tex'
text = ut.readfrom(fpath)
root = latex_parser.LatexDocPart.parse_text(text, debug=None)

# root._config['asmarkdown'] = True
# root._config['numlines'] = float('inf')

commands = list(root.find_descendant_types('newcommand'))

figcommands = []
for self in commands:
    if self.fpath_root() in {'colordef.tex', 'def.tex', 'CrallDef.tex'}:
        continue
    figcommands.append(self)

cmd_to_fpaths = ut.ddict(list)
for self in figcommands:
    keys = [tup[0] for tup in self.parse_command_def()]
    if len(keys) == 0:
        print(self)
        continue
    assert len(keys) <= 1
    cmd = keys[0]
    figures = list(self.find_descendant_types('figure'))
    for fig in figures:
        fig = figures[0]
        text = fig.summary_str(outline=True, numlines=float('inf'))
        fpaths = [info['fpath'] for info in fig.parse_includegraphics()]
        if fpaths:
            cmd_to_fpaths[cmd].extend(fpaths)


for key in cmd_to_fpaths.keys():
    cmd = key.lstrip('\\')
    if not root.find_descendant_type(cmd):
        print(key)

from os.path import abspath, dirname
used_fpaths = ut.flatten(cmd_to_fpaths.values())
used_fpaths = set(ut.emap(abspath, used_fpaths))

all_fpaths = set(ut.emap(abspath, ut.glob('.', ['*.png', '*.jpg'], recursive=True)))

unused = list(all_fpaths - used_fpaths)

unuse_dirs = ut.group_items(unused, ut.emap(dirname, unused))


semi_used = {}
for dpath, fpaths in unuse_dirs.items():
    used_in_dpath = set(ut.ls(dpath)) - set(fpaths)
    if len(used_in_dpath) == 0:
        # completely unused directories
        print(dpath)
    else:
        semi_used[dpath] = fpaths

print(ut.repr4(list(semi_used.keys())))
