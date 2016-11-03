"""
./texfix.py --reformat --outline  --fpaths chapter4-application.tex
./texfix.py --reformat --fpaths chapter4-application.tex --print
./texfix.py --reformat --outline  --fpaths testchap.tex

./texfix.py --fpaths chapter4-application.tex --reformat

./texfix.py --fpaths chapter4-application.tex --outline --showtype --numlines
./texfix.py --fpaths chapter4-application.tex --outline --showtype --numlines --singleline
./texfix.py --fpaths chapter4-application.tex --outline --showtype --numlines --singleline | less -R


./texfix.py --fpaths chapter4-application.tex --outline --noshowtype --numlines --singleline --noindent

./texfix.py --fpaths chapter4-application.tex --outline --showtype --numlines --singleline --noindent

./texfix.py --fpaths chapter4-application.tex --outline --numlines --singleline --sections=0:-6

./texfix.py --fpaths chapter4-application.tex --outline --numlines --singleline --keeplabel --fpaths figdef1.tex

# Write outline for entire thesis
./texfix.py --outline --keeplabel -w

./texfix.py --outline --keeplabel --fpaths chapter*.tex --numlines --singleline -w
./texfix.py --outline --keeplabel --fpaths chapter2-related-work.tex --numlines --singleline -w
./texfix.py --outline --keeplabel --fpaths chapter1-intro.tex  -w
./texfix.py --outline --keeplabel --fpaths figdef1.tex -w
./texfix.py --outline --keeplabel --fpaths figdef1.tex --showtype

./texfix.py --outline --keeplabel --fpaths sec-3-4-expt.tex --showtype --debug-latex


./texfix.py --outline --keeplabel --fpaths sec-2-1-featdetect.tex --print --showtype --debug-latex
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import re
import utool as ut
print, rrr, profile = ut.inject2(__name__, '[texparse]')


def find_nth_pos(str_, list_, n):
    pos_list = [[m.start() for m in re.finditer(c, str_)] for c in list_]
    # print(repr(re.escape(c)))
    pos_list = sorted(ut.flatten(pos_list))
    # pos_list = [str_.find(c) for c in list_]
    # pos_list = [p for p in pos_list if p > -1]
    if len(pos_list) >= n:
        return pos_list[n - 1]
    else:
        return len(str_)


@ut.memoize
def hack_read_figdict():
    fig_defs = [
        LatexDocPart.parse_fpath('figdef1.tex'),
        LatexDocPart.parse_fpath('figdef2.tex'),
        LatexDocPart.parse_fpath('figdef3.tex'),
        LatexDocPart.parse_fpath('figdef4.tex'),
        LatexDocPart.parse_fpath('figdef5.tex'),
        LatexDocPart.parse_fpath('figdefexpt.tex'),
        LatexDocPart.parse_fpath('figdefindiv.tex'),
        LatexDocPart.parse_fpath('figdefdbinfo.tex'),
    ]
    # figdict = figdef1.parse_figure_captions()
    figdict = ut.dict_union(*[f.parse_figure_captions()[0] for f in fig_defs])
    return figdict


class _Reformater(object):

    _config = ut.argparse_dict({
            'compress_consecutive': False,
            #'skip_subtypes': ['comment', 'def'],
            'skip_subtypes': ['comment', 'devmark'],
            #'skip_types': ['comment', 'keywords', 'outline', 'devnewpage'],
            # 'skip_types': ['comment', 'keywords', 'outline', 'devnewpage', 'equation', 'devcomment'],
            'skip_types': ['comment', 'keywords', 'outline', 'devnewpage',
                           'devcomment', 'renewcommand', 'newcommand', 'setcounter',
                           'bibliographystyle', 'bibliography'],
            'numlines': 0,
            'max_width': 120,
            'nolabel': True,
            'showtype': False,
            'asmarkdown': False,
            'includeon': True,
            'full': [],
            'remove_leading_space': True,
            #skip_subtypes = ['comment']
    })

    def _put_debug_type(self, block, outline=False):
        """
        Prefixes a summary block with parser debuging information
        """
        show_type = not outline or self._config['showtype']
        # show_type = True
        if show_type:
            type_just = 20
            type_str = self.type_
            if self.subtype is not None:
                type_str += '.' + self.subtype
            type_part = type_str.ljust(15) + ('(%3d)' % (len(self.lines)))
            block = ut.hz_str(type_part.ljust(type_just) + ' ', block)
        return block

    def in_full_outline_section(self, outline):
        if outline:
            fullformat_types = self._config['full']
        else:
            fullformat_types = []
        container_type = self.get_ancestor(self.toc_heirarchy).type_
        return container_type in fullformat_types

    def _summary_headerblocks(self, outline=False):
        """
        Create a new formatted headerblock for the node summary string
        """

        if len(self.lines) == 0:
            return []
        elif self.type_ == 'lines':
            header_block = self.get_lines(outline)
        else:
            header_block = self.get_header(outline)
        header_block = self._put_debug_type(header_block, outline)
        header_blocks = [header_block]
        return header_blocks

    def is_header(self):
        return self.type_ in self.toc_heirarchy

    def get_lines(self, outline=False):
        # Use ... to represent lines unless a full reformat is requested for anutline
        if self.in_full_outline_section(outline):
            header_block = ut.unindent('\n'.join(self.reformat_blocks(stripcomments=False)))
        elif self._config['numlines'] == 0:
            if self.type_ == 'lines' and self.parent.type_ in ['itemize', 'enumerate']:
                header_block = ''
            else:
                if self.subtype == 'space':
                    header_block = ''
                else:
                    header_block = '...'
        else:
            #header_block = '\ldots'
            if self.subtype == 'space':
                header_block = ''
            else:
                if self._config['asmarkdown']:
                    header_block = '\n'.join(self.get_sentences())
                else:
                    header_block = ut.unindent('\n'.join(self.reformat_blocks(stripcomments=False)))

            if self._config['numlines'] >= 1 and self.subtype == 'par':
                if self.parent_type() in self.rawformat_types:
                    #if self.parent.type_ == 'pythoncode*':
                    # hack to not do next hack for pythoncode
                    header_block = '\n'.join(self.lines)
                else:
                    # hack to return the n sentences from every paragrpah
                    pos = find_nth_pos(header_block, ['\\.',  ':\r'], self._config['numlines'])
                    header_block = header_block[:pos + 1]

        # only remove labels from ends of nonempty lines
        if self._config['nolabel']:
            pref = ut.positive_lookbehind('[^ ]')
            header_block = re.sub(pref + '\\\\label{.*$', '', header_block, flags=re.MULTILINE)

        header_block = ut.unindent(header_block)
        if self._config['asmarkdown']:
            pass
        else:
            header_block = ut.indent(header_block, ('    ' * self.level))
        # header_block = ut.indent(ut.unindent(header_block), ('    ' * self.level))
        return header_block

    def get_header(self, outline=False):
        if outline:
            # Print introduction
            # allow_multiline_headers = True
            allow_multiline_headers = False
        else:
            allow_multiline_headers = False

        if self.is_header():
            header_block = self.lines[0]
        else:
            if allow_multiline_headers and len(self.lines) > 1:
                # Header is multiline
                header_block = '\n'.join(self.lines)
                max_width = self._config['max_width']
                header_block = ut.format_multi_paragraphs(header_block, myprefix=True, sentence_break=True, max_width=max_width)
                if self.type_ == 'ImageCommand':
                    header_block = header_block.replace('ImageCommand', 'ImageCommandDraft')
                if self.type_ == 'MultiImageFigure':
                    header_block = header_block.replace('MultiImageFigure', 'MultiImageFigureDraft')
                if self.type_ == 'MultiImageFigureII':
                    header_block = header_block.replace('MultiImageFigureII', 'MultiImageFigureDraft')
            else:
                header_block = self.lines[0]

        if self._config['nolabel']:
            # only remove labels from ends of nonempy lines
            pref = ut.positive_lookbehind('[^ ]')
            header_block = re.sub(pref + '\\\\label{.*$', '', header_block, flags=re.MULTILINE)
        header_block = ut.unindent(header_block)

        if self._config['asmarkdown']:
            try:
                header_block = header_block.replace('\\%s{' % self.type_, '')

                if header_block.endswith('}'):
                    header_block = header_block[:-1]

                header_level = (self.toc_heirarchy + ['paragraph']).index(self.type_) + 1

                if header_level == 1:
                    header_block =  header_block + '\n' + '=' * len(header_block)
                elif header_level == 2:
                    header_block =  header_block + '\n' + '-' * len(header_block)
                else:
                    header_block = ('#' * header_level) + ' ' + header_block
            except ValueError:
                if self.type_ in ['itemize', 'enumerate']:
                    header_block = ''
                elif self.type_ in ['item']:
                    header_block = header_block.replace('\\item', '*')
                elif self.type_ in ['equation']:
                    header_block = '\n$$'
                elif self.type_ in ['pythoncode*']:
                    header_block = '\n```python'
                else:
                    header_block = '\n'.join(self.lines)
                    # raise

        else:
            header_block = ut.indent(header_block, ('    ' * self.level))

        return header_block

    def _summary_footerblocks(self, outline=False):
        """
        Create a new formatted footerblock for the node summary string
        """
        if self._config['asmarkdown']:
            return []

        if len(self.footer) > 0:
            footer_block = '\n'.join([l.strip() for l in self.footer])
            footer_block = ut.indent(footer_block, '    ' * self.level)

            footer_block = self._put_debug_type(footer_block, outline)
            footer_blocks = [footer_block]
        else:
            footer_blocks = []
        return footer_blocks

    def summary_str_blocks(self, outline=False, depth=None):
        """
        Recursive function that builds summary strings
        """
        if depth is not None:
            depth = depth - 1
            if depth < 0:
                return []

        if outline:
            skip_types = self._config['skip_types']
            skip_subtypes =  self._config['skip_subtypes']
        else:
            skip_types = []
            skip_subtypes = []
            #skip_subtypes = ['comment', 'def']
            #skip_subtypes = ['comment']

        # Skip certain node types
        child_nodes = self.children
        def is_skiptype(node):
            skip_types_ = skip_types
            skip_figures = self._config['asmarkdown']
            skip_figures = False
            if skip_figures:
                hackfigtypes = ['mergecase', 'splitcase', 'popest',
                                'ThreeSixty', 'PoseExample',
                                'OcclusionAndDistractors',
                                'ShadowAndIllumination',
                                'OccurrenceCompliment', 'Quality', 'Age',
                                'doubledepc']
                skip_types_ += hackfigtypes
                if x.type_.lower().endswith('figure'):
                    return False
            return x.type_ not in skip_types

        skip_type_flags = [is_skiptype(x)  for x in child_nodes]
        child_nodes = ut.compress(child_nodes, skip_type_flags)

        skip_subtype_flags = [x.subtype not in skip_subtypes for x in child_nodes]
        child_nodes = ut.compress(child_nodes, skip_subtype_flags)

        if self._config['remove_leading_space']:
            if len(child_nodes) > 2:
                # remove first space in sections
                if child_nodes[0].subtype == 'space':
                    child_nodes = child_nodes[1:]

        # Correct way to remove double spaces
        flags = [(count == 0 or count == len(child_nodes) - 1) or not (x.subtype == 'space' and y.subtype == 'space')
                 for count, (x, y) in enumerate(ut.itertwo(child_nodes, wrap=True))]
        child_nodes = ut.compress(child_nodes, flags)

        # combine / collapse / merge consecutive nodes of the same subtype.
        # FIXME: CAUSES BUGS CHANGES INTERNAL STATE. VERY BAD
        if self._config['compress_consecutive'] and False:
            import numpy as np
            if self._config['numlines'] > 0 or self.in_full_outline_section(outline):
                flags = [not (x.type_ == 'lines' and y.type_ == 'lines' and x.subtype == y.subtype)
                         for (x, y) in ut.itertwo(child_nodes)]
            else:
                flags = [not (x.type_ == 'lines' and y.type_ == 'lines')
                         for (x, y) in ut.itertwo(child_nodes)]

            # Merge lines in the grouped nodes together
            grouped_nodes = np.split(child_nodes, np.where(flags)[0] + 1)
            child_nodes = []
            for nodes in grouped_nodes:
                if len(nodes) == 0:
                    pass
                elif len(nodes) == 1:
                    child_nodes.append(nodes[0])
                else:
                    node = nodes[0]
                    for node_ in nodes[1:]:
                        if node.subtype == 'space' and node_.subtype != 'space':
                            node.subtype = node_.subtype
                        node.lines += node_.lines[:]
                    child_nodes.append(node)

        #if self.type_ == 'chapter':
        #    section_slice = ut.get_argval('--sections', type_='fuzzy_subset', default=slice(None, None, None))
        #    child_nodes = child_nodes[section_slice]

        header_blocks = self._summary_headerblocks(outline=outline)
        # Make child strings
        child_blocks = ut.flatten([child.summary_str_blocks(outline=outline, depth=depth)
                                   for child in child_nodes])

        footer_blocks = self._summary_footerblocks(outline=outline)

        if self.type_ == 'equation' and outline:
            if self._config['asmarkdown']:
                # http://jaxedit.com/mark/
                footer_blocks = ['$$\n']
            else:
                header_blocks[0] += r'\end{equation}'
                child_blocks = []
                footer_blocks = []
            pass
        if self.type_ == 'pythoncode*' and outline:
            if self._config['asmarkdown']:
                footer_blocks = ['```\n']
            else:
                header_blocks[0] += r'\end{pythoncode*}'
                child_blocks = []
                footer_blocks = []
            pass

        block_parts = []
        block_parts += header_blocks
        block_parts += child_blocks
        block_parts += footer_blocks
        return block_parts

    def summary_str(self, outline=False, highlight=False, depth=None):
        block_parts = self.summary_str_blocks(outline, depth=depth)
        summary = '\n'.join(block_parts)

        if outline:
            # Hack to deal with figures
            if self._config['includeon'] and self._config['asmarkdown']:
                figdict = hack_read_figdict()
                for key, val in figdict.items():
                    figcomment = strip_latex_comments(val)
                    figcomment = re.sub(r'\\caplbl{' + ut.named_field('inside', '.*?') + '}', '', figcomment)
                    # figcomment = '*' + '\n'.join(ut.split_sentences2(figcomment)) + '*'
                    figcomment = '\n'.join(ut.split_sentences2(figcomment))
                    figstr = '![`%s`](%s.jpg)' % (key, key) + '\n' + figcomment
                    # figstr = '![%s](figures1/%s.jpg)' % (figcomment, key)
                    summary = summary.replace('\\' + key + '{}', figstr)
            if self._config['asmarkdown']:
                summary = re.sub(r'\\rpipe{}', r'=>', summary)
                summary = re.sub(r'\\rarrow{}', r'->', summary)
                summary = re.sub(r'\\rmultiarrow{}', r'\\*->', summary)

            # hack to replace straightup definitions
            # TODO: read from def.tex
            cmd_map, cmd_map1 = self.read_static_defs()
            defmap = self.parse_newcommands()
            cmd_map.update(defmap.get(0, {}))
            cmd_map1.update(defmap.get(1, {}))

            #cmd_map = {}
            for key, val in cmd_map.items():
                summary = summary.replace(key + '{}', val)
                summary = summary.replace(key + '}', val + '}')  # hack

        # HACK for \\an
        def argrepl(match):
            firstchar = match.groups()[0][0]
            if firstchar.lower() in ['a', 'e', 'i', 'o', 'u']:
                astr = 'an'
            else:
                astr = 'a'
            if ut.get_match_text(match)[1] == 'A':
                astr = ut.to_camel_case(astr)
            argcmd_val = '%s #1' % (astr,)
            return argcmd_val.replace('#1', match.groupdict()['arg1'])

        # hand aan Aan
        pat = '\\\\[Aa]an{' + ut.named_field('arg1', '[ A-Za-z0-9_]*?') + '}'
        summary = re.sub(pat, argrepl, summary)

        #cmd_map = {}
        if outline:
            # Try and hack replace commands with one arg
            for key, val in cmd_map1.items():
                val_ = val.replace('\\', r'\\').replace('#1', ut.bref_field('arg1'))
                pat = '\\' + key + '{' + ut.named_field('arg1', '[ A-Za-z0-9_]*?') + '}'
                # re.search(pat, summary)
                # summary_ = summary
                summary = re.sub(pat, val_, summary)
            #cmd_map = {}
            for key, val in cmd_map.items():
                summary = summary.replace(key + '{}', val)
                summary = summary.replace(key + '}', val + '}')  # hack
                # Be very careful when replacing versions without curlies
                esckey = re.escape(key)
                keypat = esckey + '\\b'
                summary = re.sub(keypat, re.escape(val), summary)

            # Try and hack replace commands with one arg
            for key, val in cmd_map1.items():
                val_ = val.replace('\\', r'\\').replace('#1', ut.bref_field('arg1'))
                pat = '\\' + key + '{' + ut.named_field('arg1', '[ =,A-Za-z0-9_]*?') + '}'
                # re.search(pat, summary)
                #summary_ = summary
                summary = re.sub(pat, val_, summary)
                # if 'pvar' in key:
                #     if summary_ == summary:
                #         raise Exception('agg')

        if self._config['asmarkdown']:
            summary = re.sub(r'\\ensuremath', r'', summary)
            summary = re.sub(r'\\_', r'_', summary)
            summary = re.sub(r'\\ldots{}', r'...', summary)
            summary = re.sub(r'\\eg{}', r'e.g.', summary)
            summary = re.sub(r'\\Eg{}', r'E.g.', summary)
            # summary = re.sub(r'\\wrt{}', r'w.r.t.', summary)
            summary = re.sub(r'\\wrt{}', r'with respect to', summary)
            summary = re.sub(r'\\etc{}', r'etc.', summary)
            summary = re.sub(r'\\ie{}', r'i.e.', summary)
            summary = re.sub(r'\\st{}', r'-st', summary)
            summary = re.sub(r'\\nd{}', r'-nd', summary)
            # summary = re.sub(r'\\glossterm{', r'\\textbf{', summary)
            summary = re.sub(r'glossterm', r'textbf', summary)
            summary = re.sub(r'\\OnTheOrderOf{' + ut.named_field('inside', '.*?') + '}', '~10^{' + ut.bref_field('inside') + '}', summary)
            summary = re.sub(r'~\\cite{' + ut.named_field('inside', '.*?') + '}', ' ![cite](' + ut.bref_field('inside') + ')', summary)
            summary = re.sub(r'~\\cite\[.*?\]{' + ut.named_field('inside', '.*?') + '}', ' ![cite][' + ut.bref_field('inside') + ']', summary)
            # summary = re.sub(r'~\\cite{' + ut.named_field('inside', '.*?') + '}', '', summary)
            # summary = re.sub(r'~\\cite\[.*?\]{' + ut.named_field('inside', '.*?') + '}', '', summary)
            def parse_cref(match):
                if match.re.pattern.startswith('~'):
                    pref = ' '
                else:
                    pref = ''
                inside = match.groupdict()['inside']
                parts = inside.split(',')
                type_ = parts[0][0:parts[0].find(':')]
                # phrase = '[' + ut.conj_phrase(parts, 'and') + ']()'
                phrase = ut.conj_phrase(['[`' + p + '`]()' for p in parts], 'and')
                # phrase = '[' + ','.join(parts) + ']()'
                if type_ == 'fig':
                    return pref + 'Figure ' + phrase
                elif type_ == 'sec':
                    return pref + 'Section ' + phrase
                elif type_ == 'subsec':
                    return pref + 'Subsection ' + phrase
                elif type_ == 'chap':
                    return pref + 'Chapter ' + phrase
                elif type_ == 'eqn':
                    return pref + 'Equation ' + phrase
                elif type_ == 'tbl':
                    return pref + 'Table  ' + phrase
                elif type_ == 'sub':
                    return pref + phrase
                elif type_ == '#':
                    return pref + phrase
                else:
                    raise Exception(type_ + ' groupdict=' + str(match.groupdict()))
            summary = re.sub(r'~\\[Cc]ref{' + ut.named_field('inside', '.*?') + '}', parse_cref, summary)
            summary = re.sub(r'\\Cref{' + ut.named_field('inside', '.*?') + '}', parse_cref, summary)

            summary = re.sub(r'\\emph{' + ut.named_field('inside', '.*?') + '}', '*' + ut.bref_field('inside') + '*', summary)
            summary = re.sub(r'\\textbf{' + ut.named_field('inside', '.*?') + '}', '**' + ut.bref_field('inside') + '**', summary)
            summary = re.sub(r'\$\\tt{' + ut.named_field('inside', '[A-Z0-9a-z_]*?') + '}\$', '*' + ut.bref_field('inside') + '*', summary)
            # summary = re.sub(r'{\\tt{' + ut.named_field('inside', '.*?') + '}}', '*' + ut.bref_field('inside') + '*', summary)
            summary = re.sub(r'{\\tt{' + ut.named_field('inside', '.*?') + '}}', '`' + ut.bref_field('inside') + '`', summary)
            summary = re.sub('\n\n(\n| )*', '\n\n', summary)
            summary = re.sub(ut.positive_lookbehind('\s') + ut.named_field('inside', '[a-zA-Z]+') + '{}', ut.bref_field('inside'), summary)
            summary = re.sub( ut.negative_lookbehind('`') + '``' + ut.negative_lookahead('`'), '"', summary)
            summary = re.sub('\'\'', '"', summary)

        if highlight:
            if self._config['asmarkdown']:
                # pip install pygments-markdown-lexer
                summary = ut.highlight_text(summary, 'markdown')
            else:
                summary = ut.highlight_text(summary, 'latex')
            summary = ut.highlight_regex(summary, r'^[a-z.]+ *\(...\)',
                                         reflags=re.MULTILINE,
                                         color='darkyellow')
        return summary

    def parse_newcommands(self):
        # Hack to read all defined commands in this document
        def_list = list(self.find_descendant_types('newcommand'))
        redef_list = list(self.find_descendant_types('renewcommand'))
        def_list += redef_list
        defmap = ut.odict()
        newcommand_pats = [
            '\\\\(re)?newcommand{' + ut.named_field('key', '\\\\' + ut.REGEX_VARNAME) + '}{' + ut.named_field('val', '.*') + '}',
            '\\\\(re)?newcommand{' + ut.named_field('key', '\\\\' + ut.REGEX_VARNAME) + '}\[1\]{' + ut.named_field('val', '.*') + '}',
        ]
        for defnode in def_list:
            sline = '\n'.join(defnode.lines).strip()
            for nargs, pat in enumerate(newcommand_pats):
                match = re.match(pat, sline)
                if match is not None:
                    key = match.groupdict()['key']
                    val = match.groupdict()['val']
                    val = val.replace('\\zspace', '')
                    val = val.replace('\\xspace', '')
                    defmap[nargs] = cmd_map = defmap.get(nargs, {})
                    cmd_map[key] = val

        usage_pat = ut.regex_or(['\\\\' + ut.REGEX_VARNAME + '{}', '\\\\' + ut.REGEX_VARNAME])
        cmd_map0 = defmap.get(0, {})
        for key in cmd_map0.keys():
            val = cmd_map0[key]
            changed = None
            while changed or changed is None:
                changed = False
                for match in re.findall(usage_pat, val):
                    key2 = match.replace('{}', '')
                    if key2 in cmd_map0:
                        val = val.replace(match, cmd_map0[key2])
                        changed = True
                if changed:
                    cmd_map0[key] = val
        return defmap
        # print(ut.repr3(cmd_map))

    @staticmethod
    @ut.memoize
    def read_static_defs():
        """
        Reads global and static newcommand definitions in def and CrallDef
        """
        def_node = LatexDocPart.parse_fpath('def.tex')
        defmap = def_node.parse_newcommands()
        cmd_map = defmap[0]
        cmd_map1 = defmap[1]

        if 0:
            cralldef = LatexDocPart.parse_fpath('CrallDef.tex')
            crall_defmap = cralldef.parse_newcommands()
            cmd_map.update(crall_defmap.get(0, {}))
            cmd_map1.update(crall_defmap.get(1, {}))
        return cmd_map, cmd_map1
        #else:
        #    lines = []
        #    lines += ut.read_from('def.tex').split('\n')
        #    cmd_map = ut.odict()
        #    cmd_map1 = ut.odict()
        #    pat = '\\\\(re)?newcommand{' + ut.named_field('key', '\\\\' + ut.REGEX_VARNAME) + '}{' + ut.named_field('val', '.*') + '}'
        #    pat1 = '\\\\(re)?newcommand{' + ut.named_field('key', '\\\\' + ut.REGEX_VARNAME) + '}\[1\]{' + ut.named_field('val', '.*') + '}'

        #    for line in lines:
        #        sline = line.strip()
        #        if sline.startswith('\\newcommand'):
        #            match = re.match(pat, sline)
        #            if match is not None:
        #                key = match.groupdict()['key']
        #                val = match.groupdict()['val']
        #                val = val.replace('\\zspace', '')
        #                val = val.replace('\\xspace', '')
        #                cmd_map[key] = val
        #            match = re.match(pat1, sline)
        #            if match is not None:
        #                key = match.groupdict()['key']
        #                val = match.groupdict()['val']
        #                val = val.replace('\\zspace', '')
        #                val = val.replace('\\xspace', '')
        #                cmd_map1[key] = val

        #    # Expand inside defs
        #    usage_pat = ut.regex_or(['\\\\' + ut.REGEX_VARNAME + '{}', '\\\\' + ut.REGEX_VARNAME])
        #    for key in cmd_map.keys():
        #        val = cmd_map[key]
        #        changed = None
        #        while changed or changed is None:
        #            changed = False
        #            for match in re.findall(usage_pat, val):
        #                key2 = match.replace('{}', '')
        #                if key2 in cmd_map:
        #                    val = val.replace(match, cmd_map[key2])
        #                    changed = True
        #            if changed:
        #                cmd_map[key] = val
        #    return cmd_map, cmd_map1

    def reformat_text(self):
        return '\n'.join(self.reformat_blocks())

    def reformat_blocks(self, debug=False, stripcomments=False):
        """
        # TODO: rectify this with summary string blocks
        """

        #use_indent = False
        #sentence_break = False
        is_rawformat = self.parent_type() in self.rawformat_types
        # is_rawformat = True
        if debug:
            print('-----------------')
            print('Formating Part %s - %s' % (self.type_, self.subtype,))
            print('lines = ' + ut.repr3(self.lines))
            print('is_rawformat = %r' % (is_rawformat,))
            print('self.parent_type() = %r' % (self.parent_type(),))

        use_indent = True
        myprefix = True
        sentence_break = True

        # FORMAT HEADER
        if is_rawformat:
            raw = '\n'.join([line for line in self.lines])
            header_block = ut.unindent(raw)
        else:
            header_block = '\n'.join([line.strip() for line in self.lines])
            # header_block = '\n'.join([line for line in self.lines])

        if use_indent:
            header_block = ut.indent(header_block, '    ' * self.level)

        # is_rawformat = True
        if self.type_ == 'lines' and not is_rawformat and self.subtype != 'comment':
            max_width = self._config['max_width']
            header_block_ = ut.format_multi_paragraphs(
                header_block, myprefix=myprefix,
                max_width=max_width,
                sentence_break=sentence_break, debug=0 * debug)
            header_block = header_block_
        else:
            header_block = header_block
        header_blocks = [header_block]

        # Hack to remove spaces in equation
        if self.parent_type() == 'equation':
            if len(header_blocks) == 1 and header_blocks[0].strip() == '':
                header_blocks = []

        if self.type_ == 'root':
            header_blocks = []

        # FORMAT FOOTER
        if len(self.footer) > 0:
            footer_block = '\n'.join([line.strip() for line in self.footer])
            if use_indent:
                footer_block = ut.indent(footer_block, '    ' * self.level)
            footer_blocks = [footer_block]
        else:
            footer_blocks = []

        if debug:
            print('+ -- Formated Header ')
            print(header_blocks)
            print('L___')

        if debug:
            print('+ -- Formated Footer ')
            print(footer_blocks)
            print('L___')

        # FORMAT BODY

        body_blocks = ut.flatten([child.reformat_blocks(debug=debug)
                                  for child in self.children])

        blocks = (header_blocks + body_blocks + footer_blocks)

        if stripcomments:
            # pat = ut.REGEX_LATEX_COMMENT
            blocks = ut.lmap(strip_latex_comments, blocks)
            #pat = (ut.negative_lookbehind(re.escape('\\')) + re.escape('%')) + '.*'
            # blocks = [re.sub('\n *' + pat, '', block, flags=re.MULTILINE) for block in blocks]
            # blocks = [re.sub(pat, '', block, flags=re.MULTILINE) for block in blocks]

        return blocks


def strip_latex_comments(block):
    pat = ut.REGEX_LATEX_COMMENT
    #pat = (ut.negative_lookbehind(re.escape('\\')) + re.escape('%')) + '.*'
    block = re.sub('\n *' + pat, '', block, flags=re.MULTILINE)
    block = re.sub(pat, '', block, flags=re.MULTILINE)
    return block


class _LatexConst(object):
    # table of contents heirarchy
    #toc_heirarchy = ['chapter', 'section', 'subsection', 'subsubsection']
    toc_heirarchy = ['document', 'chapter', 'section', 'subsection', 'subsubsection']
    # things that look like \<type_>
    header_list = ['chapter', 'section', 'subsection', 'subsubsection', 'paragraph', 'item']
    # things that look like \begin{<type_>}\end{type_>}
    section_list = ['document', 'equation', 'itemize', 'enumerate', 'table', 'comment', 'pythoncode*']
    container_list = toc_heirarchy + ['paragraph', 'item', 'if', 'else']

    # This defines what is allowed to be nested in what
    ancestor_lookup = {
        'document'      : ['root'],
        'chapter'       : ['root', 'document'],
        'section'       : ['chapter'],
        'subsection'    : ['section'],
        'subsubsection' : ['subsection'],
        'paragraph'     : toc_heirarchy + ['item'],
        'itemize'       : toc_heirarchy + ['item'],
        'enumerate'     : toc_heirarchy + ['item'],
        'pythoncode*'   : toc_heirarchy,
        'equation'      : toc_heirarchy + ['paragraph', 'item'],
        'comment'       : toc_heirarchy + ['paragraph', 'item'],
        'item'          : ['itemize', 'enumerate'],
        'table'         : ['renewcommand', 'newcommand'] + [toc_heirarchy],
        'if'            : ['if'] + toc_heirarchy + ['paragraph', 'item'],
        'fi'            : 'if',
        'else'          : 'if',
    }
    rawformat_types = ['equation', 'comment', 'pythoncode*']


def get_testtext():
    r"""
    Args:
        text (str):
            debug (None): (default = None)

    Returns:
        LatexDocPart: root

    CommandLine:
        python latex_parser.py --exec-get_testtext --debug-latex --max-width=70

    Example:
        >>> # DISABLE_DOCTEST
        >>> from latex_parser import *  # NOQA
        >>> cls = LatexDocPart
        >>> text = get_testtext()
        >>> debug = True
        >>> self = root = cls.parse_text(text, 'text', debug=debug)
        >>> ut.colorprint('-- DEBUG TREE---', 'yellow')
        >>> print(self.get_debug_tree_text())
        >>> ut.colorprint('--- PRINT RAW LINES ---', 'yellow')
        >>> print(root.tostr())
        >>> ut.colorprint('--- PRINT SUMMARY --', 'yellow')
        >>> root.print_summary()
        >>> ut.colorprint('-- REFORMAT BLOCKS ---', 'yellow')
        >>> output_text = self.reformat_text()
        >>> print(output_text)
    """
    text = ut.codeblock(
        r'''
        % tex comments
        \newif\ifchecka{}
        \chapter{my chapter}\label{chap:chap1}

            Chapter 1 sentence 1 is long long long long long long long long long too long.
            Chapter 1 sentence 2 is short.

            \section{section 1}\label{sec:sec1}
                \newifcond
                \ifcond
                   cond1
                \else
                    cond2
                \fi

                \subsection{subsection 1.1}
                    \devcomment{ one }
                    Subsection 1.1.1 sentence 1.
                    % subsection comment
                    Subsection 1.1.1 sentence 2.

                    \devcomment{ one
                        foobar
                    }

            \section{section2}\label{sec:sec2}

                Section 1.2 sentence 1.
                Section 1.2 sentence 2.

        \chapter{chapter 2}\label{sec:chap1}
            pass

        Onetwo

        ''')
    return text


class _Parser(object):
    @classmethod
    def parse_fpath(cls, fpath, **kwargs):
        text = ut.read_from(fpath)
        root = cls.parse_text(text, name=fpath, **kwargs)
        return root

    @classmethod
    def parse_text(cls, text, name=None, debug=None, ignoreinputstartswith=[]):
        r"""
        PARSE LATEX

        CommandLine:
            ./texfix.py --reformat --fpaths chapter4-application.tex
            ./texfix.py --reformat --fpaths figdefdbinfo.tex --debug-latex
            ./texfix.py --reformat --fpaths main.tex --debug-latex --includeon=False
        """

        debug = ut.get_argflag('--debug-latex') or debug
        root = cls('root', subtype=name)
        node = root

        text = ut.ensure_unicode(text)

        buff = text.split('\n')

        ignoreinputstartswith = ut.get_argval('--ignoreinputstartswith', type_=list, default=ignoreinputstartswith)

        if debug:
            ut.colorprint(' --- PARSE LATEX --- ', 'yellow')
            action = ['MAKE root']
            actstr = ut.highlight_text((', '.join(action)).ljust(25), 'yellow')
            dbgjust = 35
            print(actstr )
            #print('root = %r' % (root.tostr(),))

        for count, line in enumerate(buff):
            #print(repr(line))
            action = []
            RECORD_ACTION = action.append

            sline = line.strip()
            indent = ut.get_indentation(line)  # NOQA

            # header_list = ['chapter', 'section', 'subsection', 'paragraph', 'item']
            # section_list = ['equation', 'itemize', 'table', 'comment']
            header_list = cls.header_list
            section_list = cls.section_list

            try:
                parent_type = node.parent_type()
            except Exception as ex:
                ut.printex(ex, keys=['count', 'line'])
                raise

            in_comment  = parent_type == 'comment'

            # Flag is set to true when line type is determined
            found = False

            # Check for standard chapter, section, subsection header definitions
            for key in header_list:
                if sline.startswith('\\' + key) and not in_comment:
                    # Mabye this is a naming issue.
                    anscestor = node.find_root(key)  # FIXME: should be ancestor?
                    RECORD_ACTION('HEADER(%s)' % key)
                    node = anscestor.append_part(key, line_num=count)
                    node.lines.append(line)
                    found = True
                    break

            if not found:
                # Check for begin / end blocks like document, equation, and itemize.
                for key in section_list:
                    if sline.startswith('\\begin{' + key + '}') and not in_comment:
                        # Mabye this is a naming issue.
                        anscestor = node.find_root(key)  # FIXME: should be ancestor?
                        node = anscestor.append_part(key, line_num=count)
                        RECORD_ACTION('BEGIN_KEY(%s)' % key)
                        #RECORD_ACTION('ANCESTOR(%s)' % (anscestor.nice()))
                        #RECORD_ACTION('node(%s)' % (node.nice()))
                        node.lines.append(line)
                        found = True
                        break

                    if sline.startswith('\\end{' + key + '}'):
                        if in_comment and key != 'comment':
                            break
                        anscestor = node.get_ancestor([key])
                        RECORD_ACTION('END_KEY(%s)' % key)
                        anscestor.footer.append(line)
                        parent_node = anscestor.parent
                        #parent_node = anscestor
                        #RECORD_ACTION('ANCESTOR(%s)' % (anscestor.nice()))
                        #RECORD_ACTION('PARENT(%s)' % (parent_node.nice()))
                        try:
                            assert parent_node is not None, str((repr(node), sline, count))
                        except AssertionError:
                            print('Error')
                            print('-- Outline -----')
                            root.print_outline()
                            print('-------')
                            print('Error')
                            print('node = %r' % (node,))
                            print('anscestor = %r' % (anscestor,))
                            print('parent_node = %r' % (parent_node,))
                            print('count = %r' % (count,))
                            print('sline = %r' % (sline,))
                            raise
                        node = parent_node
                        found = True
                        break

                # Check if statement
                if 1:
                    if sline.startswith('\\if') and not in_comment:
                        # Mabye this is a naming issue.
                        key = 'if'
                        condition_var = sline[slice(3, sline.find('{') if '{' in sline else None)]
                        anscestor = node.find_root(key)  # FIXME: should be ancestor?
                        node = anscestor.append_part(key, subtype=condition_var, line_num=count)
                        RECORD_ACTION('BEGIN_IF(%s)' % condition_var)
                        #RECORD_ACTION('ANCESTOR(%s)' % (anscestor.nice()))
                        #RECORD_ACTION('node(%s)' % (node.nice()))
                        node.lines.append(line)
                        found = True

                    if sline.startswith('\\else') and not in_comment:
                        # Mabye this is a naming issue.
                        key = 'else'
                        anscestor = node.get_ancestor(['if'])
                        condition_var = anscestor.subtype
                        node = anscestor.append_part(key, subtype=condition_var, line_num=count)
                        RECORD_ACTION('ELSE(%s)' % condition_var)
                        node.lines.append(line)
                        found = True

                    if sline == '\\fi' and not in_comment:
                        key = 'fi'
                        anscestor = node.get_ancestor(['if'])
                        condition_var = anscestor.subtype
                        RECORD_ACTION('ENDIF(%s)' % condition_var)
                        anscestor.footer.append(line)
                        #print('node = %r' % (node,))
                        #print('anscestor = %r' % (anscestor,))
                        #print('parent_node = %r' % (parent_node,))
                        parent_node = anscestor.parent
                        try:
                            assert parent_node is not None, 'parent of %r is None' % (node,)
                        except AssertionError:
                            print('anscestor = %r' % (anscestor,))
                            anscestor.print_debug_tree()
                            raise

                        node = parent_node
                        print('node = %r' % (node,))
                        found = True

            # HACK
            # Check for special hacked commands
            special_texcmds = ['keywords', 'relatedto', 'outline', 'input', 'include',
                               'ImageCommand', 'MultiImageCommandII',
                               'SingleImageCommand', 'newcommand',
                               'renewcommand', 'devcomment', 'setcounter',
                               'bibliographystyle', 'bibliography' ]
            if not found and not in_comment:
                texcmd_pat = ut.named_field('texcmd', ut.util_regex.REGEX_VARNAME)
                regex = r'\s*\\' + texcmd_pat + '{'
                match = re.match(regex, sline)
                if match:
                    texmcd = match.groupdict()['texcmd']
                    simpleregex = r'^\s*\\' + texcmd_pat + '{}$'
                    simplematch = re.match(simpleregex, sline)
                    # HACK FOR SPECIAL CASES COMMANDS
                    if texmcd in special_texcmds or simplematch:
                        curlycount = sline.count('{') - sline.count('}')
                        if node.type_ == 'lines':
                            #print('FIX THIS')
                            node = node.find_ancestor_container()  # hack, fix this
                            pass
                        if curlycount == 0:
                            # HACK
                            RECORD_ACTION('BEGIN_X{%s}' % texmcd)
                            if texmcd in ['input', 'include'] and root._config['includeon']:
                                # Read and parse input
                                fname = line.replace('\\' + texmcd + '{', '').replace('}', '').strip()
                                fname = ut.ensure_ext(fname, '.tex')
                                flag = True
                                for tmp in ignoreinputstartswith:
                                    if fname.startswith(tmp):
                                        flag = False
                                if flag:
                                    input_node = LatexDocPart.parse_fpath(fname)
                                    node = node.append_part(input_node, line_num=count)
                                else:
                                    node = node.append_part(texmcd, istexcmd=True, line_num=count)
                                    if True:
                                        node.lines.append('')
                                        RECORD_ACTION('IGNORE(%s)' % texmcd)
                                    else:
                                        pass
                            else:
                                node = node.append_part(texmcd, istexcmd=True, line_num=count)
                                node.lines.append(line)
                            node.curlycount = curlycount
                            found = True
                            if node.curlycount == 0:
                                RECORD_ACTION('END_X(%s)' % texmcd)
                                #RECORD_ACTION('PARENT(%s)' % (node.parent.nice()))
                                node = node.parent
                        else:
                            RECORD_ACTION('BEGIN_X(%s){' % texmcd)
                            #node = node.find_ancestor_container()  # hack, fix this
                            node = node.append_part(texmcd, istexcmd=True, line_num=count)
                            node.lines.append(line)
                            node.curlycount = curlycount
                            found = True

            # Everything else is interpreted as soem sort of lines object
            if not found:
                #ancestor_container = node.find_ancestor_container()
                #ancestor_container.children
                #print('ancestor_container = %r' % (ancestor_container,))
                #print('ancestor_container.children = %r' % (ancestor_container.children,))
                # Parse subtype of line
                subtype = None
                if len(sline) == 0:
                    subtype = 'space'
                elif sline.startswith('%'):
                    if re.match('% [ A-Z0-9]+$', sline):
                        subtype = 'devmark'
                    else:
                        subtype = 'comment'
                # elif any(sline.startswith(x) for x in ['\\newcommand',
                #                                        '\\renewcommand']):
                #     subtype = 'def'
                elif len(sline) > 0:
                    if node.parent_type() in ['equation']:
                        subtype = 'math'
                    else:
                        subtype = 'par'
                #hack_can_append_lines = True

                if node.type_ in special_texcmds:
                    curlycount = sline.count('{') - sline.count('}')
                    node.curlycount += curlycount
                    RECORD_ACTION('append special line')
                    #hack_can_append_lines = False
                    node.lines.append(line)
                    found = True
                    if node.curlycount == 0:
                        action.append('}END(%s)' % texmcd)
                        #RECORD_ACTION('PARENT\'(%s)' % (node.parent.nice()))
                        node = node.parent

                elif node.type_ != 'lines':
                    RECORD_ACTION('MAKE %s lines' % (subtype,))
                    node = node.append_part('lines', subtype=subtype, line_num=count)
                else:
                    if node.type_ == 'lines' and node.subtype != subtype:
                        RECORD_ACTION('MAKE %s sub-lines' % (subtype,))
                        node = node.parent.append_part('lines', subtype=subtype, line_num=count)
                        #RECORD_ACTION('PARENT\'(%s)' % (node.parent.nice()))
                if node.type_ == 'lines':
                    #if node.type_ not in special_texcmds:
                    #if hack_can_append_lines:
                    RECORD_ACTION('append lines')
                    node.lines.append(line)

            if debug:
                actstr = (', '.join(action))
                dbgjust = max(dbgjust, len(actstr) + 1)
                actstr2 = ut.highlight_text(actstr.ljust(dbgjust), 'yellow')
                #print(repr(node.parent) + '--' + repr(node))
                print(actstr2 + ' %3d ' % (count,) + repr(line))
        if debug:
            ut.colorprint(' --- END PARSE LATEX --- ', 'yellow')
            #utool.embed()
            #print(root.tostr(1))
            #print(ut.repr3(ut.lmap(repr, root.children)))
            #chap = root.children[-1]
            #print(ut.repr3(ut.lmap(repr, chap.children)))
        return root


class LatexDocPart(_Reformater, _Parser, _LatexConst, ut.NiceRepr):
    """
    Class that contains parse-tree-esque heierarchical blocks of latex and can
    reformat them.
    """

    def __init__(self, type_='root', parent=None, level=0, istexcmd=False, subtype=None, line_num=None):
        self.type_ = type_
        self.subtype = subtype
        self.level = level
        self.parent = parent
        # Parsed line num
        self.line_num = line_num
        self.lines = []
        self.footer = []
        self.children = []
        self.istexcmd = istexcmd  # Is this needed anymore?
        self.curlycount = 0

    def to_netx_graph(self):
        """
        >>> from texfix import *  # NOQA
        >>> self = root = testdata_main()
        >>> import plottool as pt
        >>> pt.qt4ensure()
        >>> graph = self.to_netx_graph()
        >>> print(len(graph.node))
        """
        import networkx as nx
        graph = nx.DiGraph()
        adjacency_list = self.adjacency_list()
        nodes = list(adjacency_list.keys())
        edges = [(u, v) for u, children in adjacency_list.items() for v in children]
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        return graph

    def adjacency_list(self):
        node = self.nicerepr()
        adjacency_list = ut.odict([
            (node, [child.nicerepr() for child in self.children])
        ])
        for child in self.children:
            adjacency_list.update(child.adjacency_list())
        return adjacency_list

    def iter_nodes(self, invalid_types=[]):
        yield self
        for child in self.children:
            if child.type_ not in invalid_types:
                for node in child.iter_nodes(invalid_types=invalid_types):
                    yield node

    def __nice__(self):
        type_str = self.type_
        if self.subtype is not None:
            type_str += '.' + self.subtype
        #return '(%s -- %d) L%s' % (type_str, len(self.lines), self.level)
        return '(%s -- %d)' % (type_str, len(self.lines))

    def nice(self):
        return self.__nice__()

    def nicerepr(self):
        return repr(self).replace(self.__class__.__name__, '')

    def __str__(self):
        return self.tostr()

    def tolist(self):
        list_ = [child if len(child.children) == 0 else child.tolist() for child in self.children]
        return list_

    def tolist2(self):
        if len(self.children) == 0:
            return [self]
        else:
            return [self.lines[:]] + [child.tolist2() for child in self.children]

    def tostr(self):
        lines = self.lines[:]
        lines += [child.tostr() for child in self.children]
        lines += self.footer
        return '\n'.join(lines)

    def print_outline(self, depth=None):
        summary = self.summary_str(outline=True, highlight=True, depth=depth)
        print(summary)

    def print_summary(self, depth=None):
        summary = self.summary_str(outline=False, highlight=True, depth=depth)
        print(summary)

    def get_debug_tree_blocks(self, indent=''):
        treeblocks = [indent + self.nicerepr()]
        for child in self.children:
            child_treeblocks = child.get_debug_tree_blocks(indent=indent + '    ')
            treeblocks.extend(child_treeblocks)
        return treeblocks

    def get_debug_tree_text(self):
        treetext = '\n'.join(self.get_debug_tree_blocks())
        return treetext

    def print_debug_tree(self):
        print(self.get_debug_tree_text())

    def fpath_root(self):
        """ returns file path that this node was parsed in """
        return self.find_ancestor_type('root').subtype

    def parsed_location_span(self):
        """ returns file path that this node was parsed in """
        idx = self.parent.children.index(self)
        sibling = None if len(self.parent.children) == idx else self.parent.children[idx + 1]
        return self.fpath_root() + ' between lines %r and %r' % (self.line_num, sibling.line_num)
        #return self.find_ancestor_type('root').subtype

    def title(self):
        if len(self.lines) == 0:
            return None
        valid_headers = self.header_list[:]
        valid_headers.remove('item')
        # parse curlies
        if self.type_ in valid_headers:
            # recombine part only in section header.
            # these functions are very preliminary
            parsed_blocks = ut.parse_nestings(self.lines[0])
            title = ut.recombine_nestings(parsed_blocks[1][1][1:-1])
            return title
        return None

    def find_descendant_type(self, type_, pat=None):
        gen = self.find_descendant_types(type_, pat)
        import six
        try:
            return six.next(gen)
        except StopIteration:
            return None
        #for child in self.children:
        #    if child.type_ == type_:
        #        if pat is None:
        #            return child
        #        else:
        #            title = child.title()
        #            if pat == title:
        #                return child
        #    descendant = child.find_descendant_type(type_, pat=pat)
        #    if descendant is not None:
        #        return descendant
        #return None

    def find_descendant_types(self, type_, pat=None):
        for child in self.children:
            if child.type_ == type_:
                if pat is None:
                    yield child
                else:
                    title = child.title()
                    if pat == title:
                        yield child
            for descendant in child.find_descendant_types(type_, pat=pat):
                yield descendant

    def find_ancestor_type(self, type_):
        parent = self.parent
        if parent.type_ == type_:
            return parent
        else:
            anscestor = parent.find_ancestor_type(type_)
            if anscestor is not None:
                return anscestor
        return None

    def find(self, regexpr_list, findtype=('lines', 'par'), verbose=False):
        r"""
        list_ = ut.total_flatten(root.tolist2())
        list_ = root.find(' \\\\cref')
        self = list_[-1]
        """
        returnlist = []
        regexpr_list = ut.ensure_iterable(regexpr_list)
        if self.type_ in [findtype[0]] and (findtype[1] is None or self.subtype in [findtype[1]]):
            found_lines, found_lxs = ut.greplines(self.get_sentences(), regexpr_list)
            found_fpath_list = ['<string>']
            grepresult = [found_fpath_list, [found_lines], [found_lxs]]
            grepstr = ut.make_grep_resultstr(grepresult, regexpr_list, reflags=0, colored=True)
            if grepstr.strip():
                if verbose:
                    print(grepstr.strip('\n'))
                returnlist += [self]
        for child in self.children:
            returnlist += child.find(regexpr_list, findtype)
        return returnlist

    def parse_figure_captions(self):
        r"""
        Returns:
            dict: figdict

        CommandLine:
            python -m latex_parser parse_figure_captions --show

        Example:
            >>> # DISABLE_DOCTEST
            >>> from latex_parser import *  # NOQA
            >>> debug = False
            >>> text = ut.readfrom('figdefexpt.tex')
            >>> self = LatexDocPart.parse_text(text, debug)
            >>> fig_defs = [LatexDocPart.parse_fpath(fpath) for fpath in ut.glob('.', 'figdef*')]
            >>> fpathsdict = ut.dict_union(*[f.parse_figure_captions()[1]['fpaths'] for f in fig_defs])
            >>> defined_fpaths = ut.flatten(fpathsdict.values())
            >>> undefined_fpaths = [f for f in defined_fpaths if not exists(f)]
            >>> used_fpaths = sorted([f for f in defined_fpaths if exists(f)])
            >>> figsizes = [ut.util_cplat.get_file_nBytes(f) for f in used_fpaths]
            >>> sortx = ut.argsort(figsizes)
            >>> sort_sizes = ut.take(figsizes, sortx)
            >>> sort_paths = ut.take(used_fpaths, sortx)
            >>> offenders = [(ut.util_str.byte_str2(s), p) for s, p in zip(sort_sizes, sort_paths)]
            >>> print(ut.repr3(offenders, nl=1))

            # Quantize pngs to make them a bit smaller
            for p in ut.ProgIter(sort_paths):
                if p.endswith('.png'):
                    ut.cmd('pngquant --quality=65-80 -f --ext .png ' + p)

            unused_dpath = 'unused_figures'

            #for x in undefined_fpaths:
            #    y = unused_dpath + '/' + ut.tail(x, 1, False)
            #    if exists(y):
            #        print(x)
            #        print(y)
            #        ut.move(y, x)

            dpaths = ut.unique([dirname(p) for p in sort_paths])
            allfigs = sorted([ut.tail(z, 2, False) for z in ut.flatten([ut.ls(p) for p in dpaths])])
            unused_figs = ut.setdiff(allfigs, used_fpaths)
            ut.ensuredir(unused_dpath)
            [ut.ensuredir(unused_dpath + '/' + d) for d in dpaths]
            move_list = [(f, unused_dpath + '/' + ut.util_path.tail(f, 2, trailing=False)) for f in unused_figs]
            [ut.move(a, b) for a, b in move_list]
            pngquant --quality=65-80

        HACK
        list_ = ut.total_flatten(root.tolist2())
        list_ = root.find(' \\\\cref')
        self = list_[-1]
        self = root
        """
        # defs = self.find('.*', ('lines', 'def'))
        # Read definitions of figures to grab the captions
        def_list = self.find('.*', ('newcommand', None))
        #def_list += self.find('.*', ('newcommand', None))
        singleimg = self.find('.*', ('SingleImageCommand', None))
        multiimg = self.find('.*', ('MultiImageCommandII', None))
        ref = ut.partial(ut.named_field)

        between = '(\n|\s)*'
        sep = '}{'
        sep = between + '}' + between + '{' + between

        figdict = {}
        figdict2 = ut.defaultdict(dict)

        pat = ''.join([
            '\\\\MultiImageCommandII{', ref('cmdname', '.*?'), sep,
            ref('width', '.*?'), sep, ref('caplbl', '.*?'), sep,
            ref('caption', '.*?'), '}{',
        ])
        imgpath_pattern = r'[/a-zA-Z_0-9\.]*?\.(png|jpg|jpeg)\b'
        for node in multiimg:
            text = str(node)
            match = re.match(pat, text, flags=re.DOTALL)
            figname = (match.groupdict()['cmdname'])
            figcap = (match.groupdict()['caption'])
            figdict[figname] = figcap
            figdict2['caption'][figname] = figcap
            fpaths = [ut.get_match_text(m) for m in re.finditer(imgpath_pattern, text)]
            figdict2['fpaths'][figname] = fpaths

        pat = ''.join([
            '\\\\SingleImageCommand{', ref('cmdname', '.*?'), sep,
            ref('width', '.*?'), sep, ref('caplbl', '.*?'), sep,
            ref('caption', '.*?'), '}{',
        ])
        for node in singleimg:
            text = str(node)
            match = re.match(pat, text, flags=re.DOTALL)
            figname = (match.groupdict()['cmdname'])
            figcap = (match.groupdict()['caption'])
            figdict[figname] = figcap
            figdict2['caption'][figname] = figcap
            fpaths = [ut.get_match_text(m) for m in re.finditer(imgpath_pattern, text)]
            figdict2['fpaths'][figname] = fpaths

        for node in def_list:
            text = str(node)
            # match = re.search('\\\\caption\[[^\]]*\]{.*}(\n|\s)*\\label', text, flags=re.DOTALL)
            match = re.search('\\\\newcommand{\\\\' + ref('cmdname', '.*?') +
                              '}.*\\\\caption\[.*\]{' + ref('caption', '.*?') +
                              '}(\n|\s)*\\\\label', text, flags=re.DOTALL)
            if match is None:
                if ut.VERBOSE:
                    print('WARNING match = %r' % (match,))
                    print('NONE DEF')
                    print(str(node))
                continue
            figname = (match.groupdict()['cmdname'])
            figcap = (match.groupdict()['caption'])
            figdict[figname] = figcap
            figdict2['caption'][figname] = figcap
            fpaths = [ut.get_match_text(m) for m in re.finditer(imgpath_pattern, text)]
            figdict2['fpaths'][figname] = fpaths

        return figdict, figdict2

    def get_sentences(self):
        lines = [re.sub(ut.REGEX_LATEX_COMMENT + r'\s*$', '', l, flags=re.MULTILINE) for l in self.lines]
        # lines = ut.lmap(strip_latex_comments, self.lines)
        sentences = ut.split_sentences2('\n'.join(lines))
        return sentences

    def parent_type(self):
        return None if self.parent is None else self.parent.type_

    def get_ancestor(self, target_types):
        if self.type_ in target_types or self.parent is None:
            return self
        elif self.type_ != target_types:
            return self.parent.get_ancestor(target_types)

    def find_root(self, type_):
        node = None
        ancestors = self.ancestor_lookup[type_]
        node = self.get_ancestor(ancestors)
        return node

    def find_ancestor_container(self):
        node = self.get_ancestor(self.container_list)
        return node

    def append_part(self, type_='root', istexcmd=False, subtype=None, line_num=None):
        noincrease_types = ['root']
        #noincrease_types = ['root', 'item', 'paragraph', 'chapter']
        #noincrease_types = ['root', 'item']
        # noincrease_types = ['root', 'item', 'chapter']
        noincrease_types = ['root', 'document', 'chapter', 'paragraph']
        if self.type_ in noincrease_types or ut.get_argflag('--noindent'):
            level = self.level
        else:
            level = self.level + 1

        if isinstance(type_, LatexDocPart):
            # Node created externally
            new_node = type_
            new_node.parent = self
        else:
            new_node = LatexDocPart(type_=type_, parent=self, level=level,
                                    istexcmd=istexcmd, subtype=subtype,
                                    line_num=line_num)
        self.children.append(new_node)
        return new_node


if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/latex/crall-candidacy-2015
        python ~/latex/crall-candidacy-2015/latex_parser.py
        python ~/latex/crall-candidacy-2015/latex_parser.py --allexamples
    """
    import multiprocessing
    multiprocessing.freeze_support()  # for win32
    import utool as ut  # NOQA
    ut.doctest_funcs()
