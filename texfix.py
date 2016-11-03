#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
References:
    http://www.cogsci.nl/blog/tutorials/97-writing-a-command-line-zotero-client-in-9-lines-of-code

    pip install pygnotero
    pip install git+https://github.com/smathot/Gnotero.git

CommandLine:

    ./texfix.py --findcite

    ./texfix.py --fixcap --dryrun

"""
from __future__ import absolute_import, division, print_function, unicode_literals
import re
import utool as ut
import six
import constants_tex_fixes
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
import logging
import logging.config
from latex_parser import LatexDocPart
print, rrr, profile = ut.inject2(__name__, '[texfix]')


#def fix_acronmy_capitlaization():
#    ACRONYMN_LIST
#    text = ut.read_from(tex_fpath)
#    text

logger = logging.getLogger(__name__)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s %(funcName)s:%(lineno)d: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'WARNING',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'WARNING',
            'formatter': 'standard',
            'propagate': True
        }
    }
})


def testdata_main(**kwargs):
    """
    >>> from texfix import *  # NOQA
    >>> self = root = testdata_main()
    """
    root = LatexDocPart.parse_fpath('main.tex', **kwargs)
    return root


def testdata_fpaths():
    dpath = '.'
    #tex_fpath_list = ut.ls(dpath, 'chapter*.tex') + ut.ls(dpath, 'appendix.tex')
    patterns = [
        'chapter*.tex',
        'sec-*.tex',
        'figdef*.tex',
        'def.tex'
    ]
    exclude_dirs = ['guts']
    tex_fpath_list = sorted(
        ut.glob(dpath, patterns, recursive=True, exclude_dirs=exclude_dirs)
    )
    tex_fpath_list = ut.get_argval('--fpaths', type_=list, default=tex_fpath_list)
    return tex_fpath_list


def check_common_errors():
    # TODO: check for common spelling mistakes like th

    common_spelling_errors = [
        'th'
        'principle compoment'
        'dependant'  # dependent
    ]
    print('common_spelling_errors = %r' % (common_spelling_errors,))


def check_doublewords():
    """
    ./texfix.py --fpaths chapter4-application.tex --check-doublewords
    ./texfix.py --check-doublewords
    ./texfix.py --fpaths main.tex --outline --asmarkdown --numlines=999 -w --ignoreinputstartswith=def,Crall,header,colordef,figdef
    text = ut.readfrom('outline_main.md')
    >>> from texfix import *  # NOQA
    """
    # TODO: Do this on a per section basis to remove math considerations automagically
    root = testdata_main(ignoreinputstartswith=['def', 'Crall', 'header', 'colordef', 'figdef'])
    #root = LatexDocPart.parse_fpath('chapter4-application.tex')
    root._config['asmarkdown'] = True
    root._config['numlines'] = 999
    #text = root.summary_str(outline=True)

    #document = root.find_descendant_type('document')

    import re
    #text = ut.readfrom('outline_main.md')
    #lines = text.split('\n')
    found_duplicates = []
    found_lines = []
    found_linenos = []

    def check_palendrome(sequence_norm):
        half1 = sequence_norm[0:len(sequence_norm) // 2]
        half2 = sequence_norm[len(sequence_norm) // 2:]
        return all([a == b for a, b in zip(half1, half2)])

    #for num, line in enumerate(lines):
    num = 0
    for x, node in enumerate(root.iter_nodes(invalid_types=['comment', 'equation'])):
        block = node.summary_str(outline=True, highlight=False, depth=1)
        for line in block.split('\n'):
            num += 1
            line_ = re.sub('\\$.*?\\$',  'mathpart' + str(num) + 'math', line)
            words = line_.split(' ')
            #if len(words) > 10:
            #    break
            for size in [2, 4, 6, 8, 10]:
                for sequence in ut.iter_window(words, size=size):
                    sequence_norm = [re.sub('[^a-zA-Z0-9]', '', s.lower()) for s in sequence]
                    if sequence_norm[0] == '' or 'mathpart' in sequence_norm[0]:
                        continue
                    #if ut.allsame(sequence_norm):
                    if check_palendrome(sequence_norm):
                        print('sequence_norm = %r' % (sequence_norm,))
                        print(('Potential repeat of %r ' % (sequence_norm,)) + node.parsed_location_span())
                        found_duplicates.append(sequence_norm)
                        found_lines.append(line_)
                        found_linenos.append(num)

    print('found_linenos = ' + '\n'.join(ut.lmap(str, found_linenos)))
    print('found_lines = ' + '\n'.join(found_lines))
    print('found_duplicates = ' + ut.repr3(found_duplicates, nl=1))

    proper_words = ['Identification', 'Park.', 'Discussion', 'Hamming',
                    'Grevy', 'Vector', 'Affine', 'Equation',
                    'Sweetwaters', 'National', 'Nairobi', 'The', 'Hessian',
                    'Fisher', 'Gaussian', 'Section', "Grevy's", 'Masai',
                    'Figure', 'Jason', 'March', 'Parham', 'Euclidean', 'Bayes',
                    'Chapter', 'Subsection', 'Lowe', 'Luigi', 'Dryad',
                    'Jablons', 'Wildbook', 'Apache', 'Hadoop', 'Zack',
                    'Lincoln', 'Peterson', 'Alessandro', 'Oddone', 'Earth',
                    'Darwin', 'Markov', 'Bayesian', 'Table', 'Boxer', 'Beagle',
                    'Platt', 'K']

    flagged_words = []

    #for num, line in enumerate(lines):
    for x, node in enumerate(root.iter_nodes(invalid_types=['comment', 'equation'])):
        block = node.summary_str(outline=True, highlight=False, depth=1)
        for line in block.split('\n'):
            #print('node.type_ = %r' % (node.type_,))
            #print('line = %r' % (line[0:20],))
            #if x > 30:
            #    break
            #if node.type_ in ['equation', 'comment']:
            #    continue
            line_ = re.sub('\\$.*?\\$',  'mathpart' + str(num) + 'math', line)
            line_ = re.sub('[0-9]+',  '', line_)
            line_ = re.sub('\'s\\b',  '', line_)
            line_ = re.sub('\\\\[A-Za-z]+\\b',  '', line_)
            line_ = line_.replace('#', '')
            line_ = line_.replace('\\', '')
            line_ = line_.replace('(', '')
            line_ = line_.replace('Nairobi National Park', '')
            line_ = line_.replace('Plains zebras', '')
            line_ = line_.replace('Ol Pejeta', '')
            line_ = line_.replace('Darwin Core', '')
            line_ = line_.replace(')', '')
            line_ = line_.replace('*', '')
            line_ = line_.lstrip(' ')
            words = line_.split(' ')
            flag = False
            for w in words[1:]:
                matches = re.findall('[A-Z]', w)
                if w in proper_words:
                    continue
                if len(matches) == 1:
                    #print(w)
                    print(('Bad caps word %r ' % (w,)) + node.fpath_root() + ' at line ' + str(node.line_num))
                    flagged_words.append(w)
                    flag = True
            if flag:
                pass
                print(line_)

    print('Found caps problems')
    hist = ut.dict_hist(flagged_words, ordered=True)
    print(ut.repr3(hist, nl=1))

    # Check for capital letters in the middle of sentences


def check_for_informal_words():
    """
    these are words I will really tend to use a whole lot when I probably
    should never use these words in a formal document
    """

    informal_word_list = [
        'much',
        'very',
        'really',
        'will',
    ]

    for word in informal_word_list:
        pass


def conjugate_stuff():
    """
    References:
        http://stackoverflow.com/questions/18942096/how-to-conjugate-a-verb-in-nltk-given-pos-tag
        pattern.en.conjugate(
            verb,
            tense="past",           # INFINITIVE, PRESENT, PAST, FUTURE
            person=3,               # 1, 2, 3 or None
            number="singular",      # SG, PL
            mood="indicative",      # INDICATIVE, IMPERATIVE, CONDITIONAL, SUBJUNCTIVE
            aspect="imperfective",  # IMPERFECTIVE, PERFECTIVE, PROGRESSIVE
            negated=False)          # True or False
    """
    import pattern.en
    verb = 'score'
    multi_dict = dict(
        mood=['indicative', 'imperative', 'conditional', 'subjunctive'],
        person=[1, 2, 3],  # , None],
        #number=['sg', 'pl'],
        aspect=['imperfective', 'perfective', 'progressive'],
        #negated=[False, True],
    )

    text = 'name score'
    for conjkw in ut.all_dict_combinations(multi_dict):
        words = text.split(' ')
        verb = words[-1]
        conj_verb = pattern.en.conjugate(verb, **conjkw)
        if conj_verb is not None:
            newtext = ' '.join(words[1:-1] + [conj_verb] if len(words) > 1 else [conj_verb])
            print(newtext)
            print(conjkw)
            print(conj_verb)


def find_citations(text):
    """
    tex_fpath = 'chapter1-intro.tex'
    """

    # remove comments
    text = re.sub('%.*', '', text)

    pattern = 'cite{' + ut.named_field('contents', '[^}]*') + '}'
    citekey_list = []
    for match in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
        contents = match.groupdict()['contents']
        #match.string[match.start():match.end()]
        citekey_list.extend(contents.replace(' ', '').replace('\n', '').split(','))
    return citekey_list


def fix_conference_title_names(clean_text, key_list=None):
    """
    mass bibtex fixes

    CommandLine:
        ./fix_bib.py
    """

    # Find citations from the tex documents
    if key_list is None:
        key_list = find_used_citations(testdata_fpaths())
        key_list = list(set(key_list))
        ignore = ['JP', '?']
        for item in ignore:
            try:
                key_list.remove(item)
            except ValueError:
                pass

    unknown_confkeys = []

    conference_keys = [
        'journal',
        'booktitle',
    ]

    ignore_confkey = [
    ]

    bib_database = bibtexparser.loads(clean_text)

    bibtex_dict = bib_database.get_entry_dict()

    isect = set(ignore_confkey).intersection(set(constants_tex_fixes.CONFERENCE_TITLE_MAPS.keys()))
    assert len(isect) == 0, repr(isect)

    #ut.embed()
    #conftitle_to_types_hist = ut.ddict(list)

    type_key = 'ENTRYTYPE'

    debug_author = ut.get_argval('--debug-author', type_=str, default=None)
    # ./fix_bib.py --debug_author=Kappes

    for key in bibtex_dict.keys():
        entry = bibtex_dict[key]

        if debug_author is not None:
            debug = debug_author in entry.get('author', '')
        else:
            debug = False

        if debug:
            print(' --- ENTRY ---')
            print(ut.repr3(entry))

        #if type_key not in entry:
        #    #entry[type_key] = entry['ENTRYTYPE']
        #    ut.embed()

        # Clip abstrat
        if 'abstract' in entry:
            entry['abstract'] = ' '.join(entry['abstract'].split(' ')[0:7])

        # Remove Keys
        remove_keys = [
            'note',
            'urldate',
            'series',
            'publisher',
            'isbn',
            'editor',
            'shorttitle',
            'copyright',
            'language',
            'month',
            # These will be put back in
            #'number',
            #'pages',
            #'volume',
        ]
        entry = ut.delete_dict_keys(entry, remove_keys)

        # Fix conference names
        confkeys = list(set(entry.keys()).intersection(set(conference_keys)))
        #entry = ut.delete_dict_keys(entry, ['abstract'])
        # TODO: FIX THESE IF NEEDBE
        #if len(confkeys) == 0:
        #    print(ut.dict_str(entry))
        #    print(entry.keys())
        if len(confkeys) == 1:
            confkey = confkeys[0]
            old_confval = entry[confkey]
            # Remove curly braces
            old_confval = old_confval.replace('{', '').replace('}', '')
            if old_confval in ignore_confkey:
                print(ut.dict_str(entry))
                continue

            new_confval_candiates = []
            if old_confval.startswith('arXiv'):
                continue

            for conf_title, patterns in constants_tex_fixes.CONFERENCE_TITLE_MAPS.items():
                if (conf_title == old_confval or
                      any([re.search(pattern, old_confval, flags=re.IGNORECASE)
                           for pattern in patterns])):
                    if debug:
                        print('old_confval = %r' % (old_confval,))
                        print('conf_title = %r' % (conf_title,))
                    new_confval = conf_title
                    new_confval_candiates.append(new_confval)

            if len(new_confval_candiates) == 0:
                new_confval = None
            elif len(new_confval_candiates) == 1:
                new_confval = new_confval_candiates[0]
            else:
                assert False, 'double match'

            if new_confval is None:
                if key in key_list:
                    unknown_confkeys.append(old_confval)
                #print(old_confval)
            else:
                # Overwrite old confval
                entry[confkey] = new_confval

            # Record info about types of conferneces
            true_confval = entry[confkey].replace('{', '').replace('}', '')

            # FIX ENTRIES THAT SHOULD BE CONFERENCES
            if true_confval in constants_tex_fixes.CONFERENCE_LIST:
                if entry[type_key] == 'inproceedings':
                    pass
                    #print(confkey)
                    #print(ut.dict_str(entry))
                elif entry[type_key] == 'article':
                    entry['booktitle'] = entry['journal']
                    del entry['journal']
                    #print(ut.dict_str(entry))
                elif entry[type_key] == 'incollection':
                    pass
                else:
                    raise AssertionError('UNKNOWN TYPE: %r' % (entry[type_key],))

                if 'booktitle' not in entry:
                    print('DOES NOT HAVE CORRECT CONFERENCE KEY')
                    print(ut.dict_str(entry))

                assert 'journal' not in entry, 'should not have journal'

                #print(entry['type'])
                entry[type_key] = 'inproceedings'

            # FIX ENTRIES THAT SHOULD BE JOURNALS
            if true_confval in constants_tex_fixes.JOURNAL_LIST:

                if entry[type_key] == 'article':
                    pass
                elif entry[type_key] == 'inproceedings':
                    pass
                    #print(ut.dict_str(entry))
                elif entry[type_key] == 'incollection':
                    pass
                else:
                    raise AssertionError('UNKNOWN TYPE: %r' % (entry['type'],))

                if 'journal' not in entry:
                    print('DOES NOT HAVE CORRECT CONFERENCE KEY')
                    print(ut.dict_str(entry))

                assert 'booktitle' not in entry, 'should not have booktitle'
                #print(entry['type'])
                #entry['type'] = 'article'

            #conftitle_to_types_hist[true_confval].append(entry['type'])

        elif len(confkeys) > 1:
            raise AssertionError('more than one confkey=%r' % (confkeys,))

        # Fix Authors
        if 'author' in entry:
            authors = six.text_type(entry['author'])
            for truename, alias_list in constants_tex_fixes.AUTHOR_NAME_MAPS.items():
                pattern = six.text_type(
                    ut.regex_or([ut.util_regex.whole_word(alias) for alias in alias_list]))
                authors = re.sub(pattern, six.text_type(truename), authors, flags=re.UNICODE)
            entry['author'] = authors

    """
    article = journal
    inprocedings = converence paper

    """

    #conftitle_to_types_set_hist = {key: set(val) for key, val in conftitle_to_types_hist.items()}
    #print(ut.dict_str(conftitle_to_types_set_hist))

    print(ut.list_str(sorted(unknown_confkeys)))
    print('len(unknown_confkeys) = %r' % (len(unknown_confkeys),))

    writer = BibTexWriter()
    writer.contents = ['comments', 'entries']
    writer.indent = '  '
    writer.order_entries_by = ('type', 'author', 'year')

    new_bibtex_str = bibtexparser.dumps(bib_database, writer)
    return new_bibtex_str

    # Grave
    #brak_pat2 = r'\{' + '(?P<inside>[A-Za-z-]*)' + '\}'
    #text = re.sub(brak_pat2, r'\1', text)


def fix_section_title_capitalization(tex_fpath, dryrun=True):
    # Read in text and ensure ascii format
    text = ut.read_from(tex_fpath)

    section_type_list = [
        'chapter',
        'section',
        'subsection',
        'subsubsection',
        'paragraph',
    ]
    re_section_type = ut.named_field('section_type', ut.regex_or(section_type_list))
    re_section_title = ut.named_field('section_title', '[^}]*')

    re_spaces = ut.named_field('spaces', '^ *')

    pattern = re_spaces + re.escape('\\') + re_section_type + '{' + re_section_title + '}'

    def fix_capitalization(match):
        dict_ = match.groupdict()
        section_title = dict_['section_title']
        #if section_title == 'The Great Zebra Count':
        #    return match.string[slice(*match.span())]
        #    #return 'The Great Zebra Count'
        # general logic
        #words = section_title.split(' ')
        tokens = re.split(ut.regex_or([' ', '/']), section_title)
        #if 'Coverage' in section_title:
        #    ut.embed()
        #    pass
        #words = [word if count == 0 else word.lower() for count, word in enumerate(words)]
        #new_section_title = ' '.join(words)
        tokens = [t if count == 0 else t.lower() for count, t in enumerate(tokens)]
        new_section_title = ''.join(tokens)

        # hacks for caps of expanded titles
        search_repl_list = constants_tex_fixes.CAPITAL_TITLE_LIST
        for repl in search_repl_list:
            new_section_title = re.sub(re.escape(repl), repl,
                                       new_section_title, flags=re.IGNORECASE)
        # hacks fo acronyms
        for full, acro in constants_tex_fixes.ACRONYMN_LIST:
            new_section_title = re.sub(r'\b' + re.escape(acro) + r'\b', acro,
                                       new_section_title, flags=re.IGNORECASE)

        #'the great zebra and giraffe count'

        #new_section_title = section_title.lower()
        new_text = dict_['spaces'] + '\\' + dict_['section_type'] + '{' + new_section_title + '}'
        VERBOSE = True
        if VERBOSE:
            old_text = match.string[slice(*match.span())]
            if new_text != old_text:
                print(ut.dict_str(dict_))
                print('--- REPL ---')
                print(old_text)
                print(new_text)
        return new_text

    #for match in re.finditer(pattern, text, flags=re.MULTILINE):
    #    fix_capitalization(match)

    new_text = re.sub(pattern, fix_capitalization, text, flags=re.MULTILINE)

    if not dryrun:
        ut.write_to(tex_fpath, new_text)
    else:
        ut.print_difftext(ut.get_textdiff(text, new_text, 0))
    #print(new_text[0:100])


def fix_section_common_errors(tex_fpath, dryrun=True):
    # Read in text and ensure ascii format
    text = ut.read_from(tex_fpath)

    new_text = text
    # Fix all capitals
    search_repl_list = constants_tex_fixes.CAPITAL_LIST
    for repl in search_repl_list:
        pattern = ut.regex_word(re.escape(repl))
        new_text = re.sub(pattern, repl, new_text, flags=re.IGNORECASE)
    #new_text = re.sub(pattern, fix_capitalization, text, flags=re.MULTILINE)

    if not dryrun:
        ut.write_to(tex_fpath, new_text)
    else:
        ut.print_difftext(ut.get_textdiff(text, new_text, 0))


def find_used_citations(tex_fpath_list):
    citekey_list = []
    for tex_fpath in tex_fpath_list:
        text = ut.read_from(tex_fpath)
        #print('\n\n+-----')
        local_cites = find_citations(text)
        citekey_list.extend(local_cites)
    return citekey_list


def findcite():
    """
    prints info about used and unused citations
    """
    tex_fpath_list = testdata_fpaths()
    citekey_list = find_used_citations(tex_fpath_list)

    # Find uncited entries
    #bibtexparser = ut.tryimport('bibtexparser')
    bib_fpath = 'My_Library_clean.bib'
    bibtex_str = ut.read_from(bib_fpath)
    bib_database = bibtexparser.loads(bibtex_str)
    bibtex_dict = bib_database.get_entry_dict()

    for key in bibtex_dict.keys():
        entry = bibtex_dict[key]
        entry = ut.map_dict_keys(six.text_type, entry)
        entry = ut.map_dict_keys(six.text_type.lower, entry)
        bibtex_dict[key] = entry

    print('ALL')
    ignore = ['JP', '?']
    citekey_list = ut.setdiff_ordered(sorted(ut.unique_keep_order2(citekey_list)), ignore)
    #print(ut.indentjoin(citekey_list))
    print('len(citekey_list) = %r' % (len(citekey_list),))

    unknown_keys = list(set(citekey_list) - set(bibtex_dict.keys()))
    unused_keys = list(set(bibtex_dict.keys()) - set(citekey_list))

    try:
        if len(unknown_keys) != 0:
            print('\nUNKNOWN KEYS:')
            print(ut.list_str(unknown_keys))
            raise AssertionError('unknown keys')
    except AssertionError as ex:
        ut.printex(ex, iswarning=True, keys=['unknown_keys'])

    @ut.argv_flag_dec(indent='    ')
    def close_keys():
        if len(unknown_keys) > 0:
            bibtex_dict.keys()
            print('\nDid you mean:')
            for key in unknown_keys:
                print('---')
                print(key)
                print(ut.closet_words(key, bibtex_dict.keys(), 3))
            print('L___')
        else:
            print('no unkown keys')
    close_keys()

    @ut.argv_flag_dec(indent='    ')
    def print_unused():
        print(ut.indentjoin(ut.sortedby(unused_keys, map(len, unused_keys))))

        print('len(unused_keys) = %r' % (len(unused_keys),))
    print_unused()

    all_authors = []
    for key in bibtex_dict.keys():
        entry = bibtex_dict[key]
        toremove = ['author', '{', '}', r'\\textbackslash']
        author = ut.multi_replace(entry.get('author', ''), toremove, '')
        authors = author.split(' and ')
        all_authors.extend(authors)

    @ut.argv_flag_dec(indent='    ')
    def author_hist():
        #print(all_authors)
        hist_ = ut.dict_hist(all_authors, ordered=True)
        hist_[''] = None
        del hist_['']
        print('Author histogram')
        print(ut.dict_str(hist_)[-1000:])
    author_hist()

    @ut.argv_flag_dec(indent='    ')
    def unused_important():
        important_authors = [
            'hinton',
            'chum',
            'Jegou',
            'zisserman',
            'schmid',
            'sivic',
            'matas',
            'lowe',
            'perronnin',
            'douze',
        ]

        for key in unused_keys:
            entry = bibtex_dict[key]
            author = entry.get('author', '')
            #authors = author.split(' and ')
            hasimportant = any(auth in author.lower() for auth in important_authors)
            if hasimportant or 'smk' in str(entry).lower():
                toremove = ['note', 'month', 'type', 'pages', 'urldate',
                            'language', 'volume', 'number', 'publisher']
                entry = ut.delete_dict_keys(entry, toremove)
                print(ut.dict_str(entry, strvals=True,
                                  key_order=['title', 'author', 'id']))
    unused_important()
    #print('\n\nEND FIND CITE')


def main():
    print(ut.bubbletext('TeX FiX'))
    #dryrun = ut.get_argflag('--dryrun')
    dryrun = not ut.get_argflag('-w')
    if dryrun:
        print('dryrun=True, specify --w to save any changes')
    find_text = ut.get_argval('--grep')
    if find_text is not None:
        tup = ut.grep(find_text,
                      fpath_list=testdata_fpaths(),
                      verbose=True)
        found_fpath_list, found_lines_list, found_lxs_list = tup
    else:
        print('~~~ --grep [text] ~~~')

    findrepl = ut.get_argval('--sed', type_=list, default=None)
    if findrepl is not None:
        assert len(findrepl) == 2, 'must specify a search and replace'
        search, repl = findrepl
        tup = ut.sed(search, repl, fpath_list=testdata_fpaths(),
                     verbose=True, force=not dryrun)

    @ut.argv_flag_dec(indent='    ')
    def fix_common_errors():
        for tex_fpath in testdata_fpaths():
            fix_section_common_errors(tex_fpath, dryrun)

    @ut.argv_flag_dec(indent='    ')
    def fixcap():
        for tex_fpath in testdata_fpaths():
            fix_section_title_capitalization(tex_fpath, dryrun)

    @ut.argv_flag_dec(indent='    ')
    def glossterms():
        re_glossterm = ut.named_field('glossterm', '.' + ut.REGEX_NONGREEDY)
        pat = r'\\glossterm{' + re_glossterm + '}'
        tup = ut.grep(pat, fpath_list=testdata_fpaths(), verbose=True)
        found_fpath_list, found_lines_list, found_lxs_list = tup
        glossterm_list = []
        for line in ut.flatten(found_lines_list):
            match = re.search(pat, line)
            glossterm = match.groupdict()['glossterm']
            glossterm_list.append(glossterm)
        print('Glossary Terms: ')
        print(ut.repr2(ut.dict_hist(glossterm_list), nl=True, strvals=True))

    @ut.argv_flag_dec(indent='    ')
    def fix_chktex():
        """
        ./texfix.py --fixcite --fix-chktex
        """
        import parse
        fpaths = testdata_fpaths()
        print('Running chktex')
        output_list = [ut.cmd('chktex', fpath, verbose=False)[0] for fpath in fpaths]

        fixcite = ut.get_argflag('--fixcite')
        fixlbl = ut.get_argflag('--fixlbl')
        fixcmdterm = ut.get_argflag('--fixcmdterm')

        for fpath, output in zip(fpaths, output_list):
            text = ut.readfrom(fpath)
            buffer = text.split('\n')
            pat = '\n' + ut.positive_lookahead('Warning')
            warn_list = list(filter(lambda x: x.startswith('Warning'), re.split(pat, output)))
            delete_linenos = []

            if not (fixcmdterm or fixlbl or fixcite):
                print(' CHOOSE A FIX ')

            modified_lines = []

            for warn in warn_list:
                warnlines = warn.split('\n')
                pres = parse.parse('Warning {num} in {fpath} line {lineno}: {warnmsg}', warnlines[0])
                if pres is not None:
                    fpath_ = pres['fpath']
                    lineno = int(pres['lineno']) - 1
                    warnmsg = pres['warnmsg']
                    try:
                        assert fpath == fpath_, ('%r != %r' % (fpath, fpath_))
                    except AssertionError:
                        continue
                    if 'No errors printed' in warn:
                        #print('Cannot fix')
                        continue
                    if lineno in modified_lines:
                        print('Skipping modified line')
                        continue
                    if fixcmdterm and warnmsg == 'Command terminated with space.':
                        print('Fix command termination')
                        errorline = warnlines[1]  # NOQA
                        carrotline = warnlines[2]
                        pos = carrotline.find('^')
                        if 0:
                            print('pos = %r' % (pos,))
                            print('lineno = %r' % (lineno,))
                            print('errorline = %r' % (errorline,))
                        modified_lines.append(lineno)
                        line = buffer[lineno]
                        pre_, post_ = line[:pos], line[pos + 1:]
                        newline = (pre_ + '{} ' + post_).rstrip(' ')
                        #print('newline   = %r' % (newline,))
                        buffer[lineno] = newline
                    elif fixlbl and warnmsg == 'Delete this space to maintain correct pagereferences.':
                        print('Fix label newline')
                        fpath_ = pres['fpath']
                        errorline = warnlines[1]  # NOQA
                        new_prevline = buffer[lineno - 1].rstrip() + errorline.lstrip(' ')
                        buffer[lineno - 1] = new_prevline
                        modified_lines.append(lineno)
                        delete_linenos.append(lineno)
                    elif fixcite and re.match('Non-breaking space \\(.~.\\) should have been used', warnmsg):
                        #print(warnmsg)
                        #print('\n'.join(warnlines))
                        print('Fix citation space')
                        carrotline = warnlines[2]
                        pos = carrotline.find('^')
                        modified_lines.append(lineno)
                        line = buffer[lineno]
                        if line[pos] == ' ':
                            pre_, post_ = line[:pos], line[pos + 1:]
                            newline = (pre_ + '~' + post_).rstrip(' ')
                        else:
                            pre_, post_ = line[:pos + 1], line[pos + 1:]
                            newline = (pre_ + '~' + post_).rstrip(' ')
                            print(warn)
                            print(line[pos])
                            assert False
                            #assert line[pos] == ' ', '%r' % line[pos]
                            break
                        if len(pre_.strip()) == 0:
                            new_prevline = buffer[lineno - 1].rstrip() + newline.lstrip(' ')
                            buffer[lineno - 1] = new_prevline
                            delete_linenos.append(lineno)
                        else:
                            #print('newline   = %r' % (newline,))
                            buffer[lineno] = newline
                    #print(warn)

            if len(delete_linenos) > 0:
                mask = ut.index_to_boolmask(delete_linenos, len(buffer))
                buffer = ut.compress(buffer, ut.not_list(mask))
            newtext = '\n'.join(buffer)

            #ut.dump_autogen_code(fpath, newtext, 'tex', fullprint=False)
            ut.print_difftext(ut.get_textdiff(text, newtext, num_context_lines=4))
            if ut.get_argflag('-w'):
                ut.writeto(fpath, newtext)
            else:
                print('Specify -w to finialize change')

    @ut.argv_flag_dec(indent='    ')
    def reformat():
        """
        ./texfix.py --reformat --fpaths NewParts.tex
        >>> from texfix import *  # NOQA
        """
        fpaths = testdata_fpaths()

        for fpath in fpaths:
            text = ut.readfrom(fpath)
            root = LatexDocPart.parse_text(text, debug=0)

            if ut.get_argflag('--fixcref'):
                root.find(' \\\\cref')
                continue

            #print(root.children)
            #root.children = root.children[0:5]
            #print('Parsed Str Short')
            new_text = '\n'.join(root.reformat_blocks(debug=0))
            # remove trailing spaces
            new_text = re.sub(' *$', '', new_text, flags=re.MULTILINE)
            # remove double newlines
            new_text = re.sub('(\n *)+\n+', '\n\n', new_text, flags=re.MULTILINE)

            if ut.get_argflag('--summary'):
                print('---summary---')
                root.print_summary()
                print('---/summary---')
                # ut.colorprint(root.summary_str(), 'blue')

            numchars1 = len(text.replace(' ', '').replace('\n', ''))
            numchars2 = len(new_text.replace(' ', '').replace('\n', ''))

            print('numchars1 = %r' % (numchars1,))
            print('numchars2 = %r' % (numchars2,))
            #assert numchars1 == numchars2, '%r == %r' % (numchars1, numchars2)

            print('old newlines = %r' % (text.count('\n'),))
            print('new newlines = %r' % (new_text.count('\n'),))

            #import unicodedata
            #new_text = unicodedata.normalize('NFKD', new_text).encode('ascii','ignore')
            #print('new_text = %r' % (new_text,))

            ut.dump_autogen_code(fpath, new_text, codetype='latex', fullprint=False)

    @ut.argv_flag_dec(indent='    ')
    def outline():
        """
        ./texfix.py --fpaths chapter4-application.tex --outline --asmarkdown --numlines=999 -w --ignoreinputstartswith=def,Crall,header,colordef,figdef
        """
        fpaths = testdata_fpaths()

        for fpath in fpaths:
            text = ut.readfrom(fpath)
            root = LatexDocPart.parse_text(text, debug=0)

            # HACK
            new_text = '\n'.join(root.reformat_blocks(debug=0))
            # remove trailing spaces
            new_text = re.sub(' *$', '', new_text, flags=re.MULTILINE)
            # remove double newlines
            new_text = re.sub('(\n *)+\n+', '\n\n', new_text, flags=re.MULTILINE)

            document = root.find_descendant_type('document')
            #document = root.find_descendant_type('section', pat='Identification')
            print('document = %r' % (document,))
            if document is not None:
                root = document

            sectionpat = ut.get_argval('--section', default=None)
            if sectionpat is not None:
                root = root.find_descendant_type('section', pat=sectionpat)
                print('root = %r' % (root,))
                if root is None:
                    import utool
                    utool.embed()
                    raise Exception('section %r does not exist' % (sectionpat))
            #print(root.get_debug_tree_text())

            #ut.colorprint(root.summary_str(outline=True), 'yellow')
            print('---outline---')
            outline = True
            # outline = False
            outline_text = root.summary_str(outline=outline, highlight=False)
            summary = root.summary_str(outline=outline, highlight=True)
            if not ut.get_argflag('-w'):
                print(summary)
            print('---/outline---')
            if root._config['asmarkdown']:
                codetype = 'markdown'
                newext = '.md'
            else:
                codetype = 'latex'
                newext = None

            ut.dump_autogen_code(ut.augpath(fpath, augpref='outline_', newext=newext),
                                 outline_text, codetype=codetype,
                                 fullprint=False)

    @ut.argv_flag_dec(indent='    ')
    def tozip():
        re_fpath = ut.named_field('fpath', 'figure.*?[jp][pn]g') + '}'
        patterns = ['chapter4-application.tex', 'figdef4*', 'main.tex',
                    'def.tex', 'Crall*', 'thesis.cls', 'header*',
                    'colordef.tex', '*.bib']
        exclude_dirs = ['guts']
        fpaths = sorted(
            ut.glob('.', patterns, recursive=True, exclude_dirs=exclude_dirs)
        )

        tup = ut.grep(re_fpath, fpath_list=fpaths, verbose=True)
        found_fpath_list, found_lines_list, found_lxs_list = tup
        fig_fpath_list = []
        for line in ut.flatten(found_lines_list):
            if not line.startswith('%'):
                for match in re.finditer(re_fpath, line):
                    fig_fpath = match.groupdict()['fpath']
                    if 'junc' not in fig_fpath and 'markov' not in fig_fpath and 'bayes' not in fig_fpath:
                        fig_fpath_list += [fig_fpath]

        fpath_list = fig_fpath_list + fpaths
        ut.archive_files('chap4.zip', fpath_list)

    fix_common_errors()
    fixcap()
    glossterms()
    fix_chktex()
    reformat()
    outline()
    tozip()

    ut.argv_flag_dec(check_doublewords, indent='    ')()
    ut.argv_flag_dec(findcite, indent='    ')()

    print('Use --fpaths to specify specific files')


if __name__ == '__main__':
    """
    ./texfix.py --reformat --fpaths chapter4-application.tex
    ./texfix.py --fix-chktex --fixcmdterm
    ./texfix.py --fix-chktex --fixcite --fpaths old-chapter4-application.tex
    ./texfix.py --fix-chktex --fixlbl --fpaths old-chapter4-application.tex
    ./texfix.py --reformat --fpaths old-chapter4-application.tex
    ./texfix.py --outline --fpaths old-chapter4-application.tex
    ./texfix.py --grep " encounter "

    ./texfix.py --dryrun --fixcap
    ./texfix.py

    ./texfix.py --findcite


    ./texfix.py --fixcap

    ./texfix.py --fix-common-errors --dryrun

    from texfix import *

    pip install bibtexparser

    # TODO: Rectify number styles
    # http://tex.stackexchange.com/questions/38820/numbers-outside-math-environment

    ./texfix.py --grep " \\d+,?\\d* "

    ./texfix.py --grep "\\$\\d+,?\\d*\\$"
    ./texfix.py --grep "\<three\>"
    ./texfix.py --grep "\<two\>"
    ./texfix.py --grep "\<one\>"

    ./texfix.py --grep "\c\<we\>"
    ./texfix.py --grep "\c\<us\>"

    ./texfix.py --grep "encounter"
    ./texfix.py --grep "figure.*[jp][pn]g"

    ./texfix.py --sed "\<encounter\>" "occurrence" -w
    ./texfix.py --sed "\<encountername\>" "occurrencename"
    ./texfix.py --sed "Encounter" "Occurrence"
    ./texfix.py --sed "occurence" "occurrence"
    ./texfix.py --sed "intraencounter" "intraoccurrence"
    ./texfix.py --sed "Intraencounter" "Intraoccurrence" -w

    >>> from texfix import *  # NOQA
    """
    main()
