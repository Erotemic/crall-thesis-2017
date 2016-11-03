#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
References:

    pip install pygnotero
    pip install git+https://github.com/smathot/Gnotero.git

    pip install mozrepl
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import re
import utool as ut


def find_item_types(clean_text):
    item_type_pat = ut.named_field('item_type', '\w+')
    pattern = '@' + item_type_pat + '{'
    #header_list = [match.string[match.start():match.end()] for match in re.finditer(item_type_pat, clean_text)]
    header_list = [match.groupdict()['item_type'] for match in re.finditer(pattern, clean_text)]
    header_list = ut.unique_keep_order2(header_list)
    header_reprs = '\n'.join(['    \'' + x + '\', ' for x in header_list])
    print(header_reprs)


def fix_bib(bib_fpath):
    r"""
    python fix_bib.py --dryrun --debug
    """

    DEBUG = ut.get_argflag('--debug')
    # Read in text and ensure ascii format
    dirty_text = ut.read_from(bib_fpath)
    #udata = dirty_text.decode("utf-8")
    #dirty_text = udata.encode("ascii", "ignore")
    #dirty_text = udata

    # I actually forget what this does
    brak_pat1 = r'\(\{' + '(?P<inside>.*)' + '\)\}'
    clean_text = re.sub(brak_pat1, r'\1', dirty_text)

    if DEBUG:
        find_item_types(clean_text)

    item_type_list = [
        'inproceedings',
        'article',
        'incollection',
        'misc',
        'book',
        'techreport',
        'phdthesis',
        'patent',
        'unpublished',
        'online',
    ]

    # Fields to remove
    fields_remove_list = [
        #'abstract',
        'file',
        'url',
        'address',
        'keywords',
        'doi',
        'issn',
        'annote',
    ]

    # Remove each field in the list
    for field in fields_remove_list:
        # pattern1 removes field + curly-braces without any internal curly-braces
        #  up to a newline. The line may or may not have a comma at the end
        field_pattern1 = field + r' = {[^}]*},? *\n'
        # pattern2 removes field + curly-braces in a greedy fashion up to a newline.
        # The line MUST have a comma at the end. (or else we might get too greedy)
        field_pattern2 = field + r' = {.*}, *\n'
        #print(field_pattern1)
        #print(field_pattern2)
        clean_text = re.sub(field_pattern1, '', clean_text, flags=re.MULTILINE)
        clean_text = re.sub(field_pattern2, '', clean_text, flags=re.MULTILINE)

        # some fields are very pesky (like annot)
        # Careful. Any at symobls may screw things up in an annot field
        REMOVE_NONSAFE = True
        if REMOVE_NONSAFE:
            next_header_field = ut.named_field('nextheader', '@' + ut.regex_or(item_type_list))
            next_header_bref = ut.bref_field('nextheader')

            field_pattern3 = field + r' = {[^@]*}\s*\n\s*}\s*\n\n' + next_header_field
            clean_text = re.sub(field_pattern3, r'}\n\n' + next_header_bref, clean_text, flags=re.MULTILINE | re.DOTALL)

            field_pattern4 = field + r' = {[^@]*},\s*\n\s*}\s*\n\n' + next_header_field
            clean_text = re.sub(field_pattern4, r'}\n\n' + next_header_bref, clean_text, flags=re.MULTILINE | re.DOTALL)

        if DEBUG:
            print(field)
            if field == 'annote':
                assert re.search(field_pattern1, clean_text, flags=re.MULTILINE) is None
                assert re.search(field_pattern2, clean_text, flags=re.MULTILINE) is None
                assert re.search(field_pattern3, clean_text, flags=re.MULTILINE) is None
                assert re.search(field_pattern4, clean_text, flags=re.MULTILINE) is None

                field_pattern_annot = 'annote = {'
                match = re.search(field_pattern_annot, clean_text, flags=re.MULTILINE)
                if match is not None:
                    print(match.string[match.start():match.end()])
                    print(match.string[match.start():match.start() + 1000])
                    #ut.embed()

                    #pattern = 'annote = {.*}'
                    #pattern = 'annote = {[^@]*} *'
                    #match = re.search(pattern, clean_text, flags=re.MULTILINE | re.DOTALL)
                    #print('----')
                    #print(match.string[match.start():match.end()])
                    #print('----')
                    #print(match.string[match.start():match.start() + 1000])
                    #print('----')

    # Clip abstract to only a few words
    clip_abstract = False
    # Done elsewhere now
    if clip_abstract:
        field = 'abstract'
        cmdpat_head = ut.named_field('cmdhead', field + r' = {')
        valpat1 = ut.named_field(field, '[^}]*')
        valpat2 = ut.named_field(field, '.*')
        cmdpat_tail1 = ut.named_field('cmdtail', '},? *\n')
        cmdpat_tail2 = ut.named_field('cmdtail', '}, *\n')

        field_pattern1 = cmdpat_head + valpat1 + cmdpat_tail1
        field_pattern1 = cmdpat_head + valpat2 + cmdpat_tail2

        def replace_func(match):
            groupdict_ = match.groupdict()
            oldval = groupdict_[field]
            newval = ' '.join(oldval.split(' ')[0:7])
            cmdhead = groupdict_['cmdhead']
            cmdtail = groupdict_['cmdtail']
            new_block = cmdhead + newval + cmdtail
            return new_block
        clean_text = re.sub(field_pattern1, replace_func, clean_text, flags=re.MULTILINE)
        clean_text = re.sub(field_pattern2, replace_func, clean_text, flags=re.MULTILINE)

    # Remove the {} around title words
    fix_titles = False
    if fix_titles:
        field = 'title'
        cmdpat_head = ut.named_field('cmdhead', field + r' = {')
        valpat1 = ut.named_field(field, '[^}]*')
        valpat2 = ut.named_field(field, '.*')
        cmdpat_tail1 = ut.named_field('cmdtail', '},? *\n')
        cmdpat_tail2 = ut.named_field('cmdtail', '}, *\n')

        field_pattern1 = cmdpat_head + valpat1 + cmdpat_tail1
        field_pattern1 = cmdpat_head + valpat2 + cmdpat_tail2

        def replace_func(match):
            groupdict_ = match.groupdict()
            oldval = groupdict_[field]
            newval = oldval.replace('}', '').replace('{', '')
            cmdhead = groupdict_['cmdhead']
            cmdtail = groupdict_['cmdtail']
            new_block = cmdhead + newval + cmdtail
            return new_block
        clean_text = re.sub(field_pattern1, replace_func, clean_text, flags=re.MULTILINE)
        clean_text = re.sub(field_pattern2, replace_func, clean_text, flags=re.MULTILINE)

    # Remove invalid characters from the bibtex tags
    bad_tag_characters = [':', '-']
    # Find invalid patterns
    tag_repl_list = []
    for item_type in item_type_list:
        prefix = '@' + item_type + '{'
        header_search = prefix + ut.named_field('bibtex_tag', '[^,]*')
        matchiter = re.finditer(header_search, clean_text)
        for match in matchiter:
            groupdict_ = match.groupdict()
            bibtex_tag = groupdict_['bibtex_tag']
            for char in bad_tag_characters:
                if char in bibtex_tag:
                    bibtex_tag_old = bibtex_tag
                    bibtex_tag_new = bibtex_tag.replace(char, '')
                    repltup = (bibtex_tag_old, bibtex_tag_new)
                    tag_repl_list.append(repltup)
                    bibtex_tag = bibtex_tag_new
    # Replace invalid patterns
    for bibtex_tag_old, bibtex_tag_new in tag_repl_list:
        clean_text = clean_text.replace(bibtex_tag_old, bibtex_tag_new)

    # The bibtext is now clean. Print it to stdout
    import mass_tex_fixes
    #print(clean_text)
    clean_text = mass_tex_fixes.fix_conference_title_names(clean_text)

    # Need to check
    #jegou_aggregating_2012

    # Fix the Journal Abreviations
    # References:
    # https://www.ieee.org/documents/trans_journal_names.pdf

    # Write out clean bibfile in ascii format
    clean_bib_fpath = ut.augpath(bib_fpath.replace(' ', '_'), '_clean')
    #encoded_text = clean_text.encode('ASCII', 'ignore')
    #encoded_text = clean_text.encode('utf8', 'ignore')

    if not ut.get_argflag('--dryrun'):
        ut.write_to(clean_bib_fpath, clean_text)


if __name__ == '__main__':
    #bib_fpath = 'nsf-mri-2014'
    bib_fpath = 'My Library.bib'
    fix_bib(bib_fpath)
