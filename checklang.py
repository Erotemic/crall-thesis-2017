#!/usr/bin/env python
"""
fixtex --fpaths chapter1-intro.tex --outline --asmarkdown --numlines=999 --shortcite -w && ./checklang.py outline_chapter1-intro.md
fixtex --fpaths chapter2-related-work.tex --outline --asmarkdown --numlines=999 --shortcite -w && ./checklang.py outline_chapter2-related-work.md
fixtex --fpaths chapter3-matching.tex --outline --asmarkdown --numlines=999 --shortcite -w && ./checklang.py outline_chapter3-matching.md
fixtex --fpaths chapter4-pairclf.tex --outline --asmarkdown --numlines=999 --shortcite -w && ./checklang.py outline_chapter4-pairclf.md
fixtex --fpaths chapter5-graphid.tex --outline --asmarkdown --numlines=999 --shortcite -w && ./checklang.py outline_chapter5-graphid.md
fixtex --fpaths chapter6-conclusion.tex --outline --asmarkdown --numlines=999 --shortcite -w && ./checklang.py outline_chapter6-conclusion.md
fixtex --fpaths appendix.tex --outline --asmarkdown --numlines=999 --shortcite -w && ./checklang.py outline_appendix.md


fixtex --fpaths chapter4-pairclf.tex --outline --asmarkdown --numlines=999 --shortcite --debug-latex
"""
import utool as ut
import parse
import re

DISABLE_RULES = [
    'WHITESPACE_RULE',
    'EN_QUOTES',
    'COMMA_PARENTHESIS_WHITESPACE',
    'ENGLISH_WORD_REPEAT_BEGINNING_RULE',
    'EN_UNPAIRED_BRACKETS',
    # 'LARGE_NUMBER_OF',
]


class Spelling(object):
    NAMES = {
        'Jablons', 'Weideman', 'Lanczos', 'Parham', 'Mahalanobis', 'Wildbook',
        'Grévy', 'Zisserman', 'Scikit', 'Sivic', 'Munkres', 'Gaussians',
        'Pejeta', 'Boiman', 'Sweetwaters', 'Mpala', 'Hellinger', 'Simonoff',
    }

    ACCRONYMNS = {
        'DCNN', 'LReLU', 'GPU', 'SVM', 'MCC', 'PCC',
    }

    NORMAL = {
        'tf-idf', 'tf', 'idf', 'intra-image', 'intra-occurrence',
        'intra-class', 'non-poseable', 'orderless', 'iteratively',
        'timestamps', 'timedelta', 'agglomerative', 'haversines',
        'preprocessed',


        'verifier', 'accuracies', 'accuracies', 'photobomb-state',
        'probabilistically',
        'pre-existing', 'pre-conditions', 'multiclass', 'activations',
        'affine', 'interpretable', 'undirected', 'pairiwse', 'asymptotes',
        'binarized', 'bottlenose', 'centroid', 'centroids', 'codebook',
        'codebooks', 'confusors', 'dataset', 'datasets', 'detections',
        'discriminative', 'distractors', 'frontalized', 'distinctivness',
        'frontleft', 'geolocation', 'groundtruth,', 'homography',
        'homography-based', 'hyperparameter', 'hyperplanes', 'invariance',
        'kd-tree', 'kd-trees', 'keypoint', 'keypoints', 'labelings',
        'lionfish', 'non-projective', 'projective', 'normalizer', 'occluders',
        'ok', 'per-dataset', 'photobomb', 'photobombing', 'photobombs',
        'quadratically', 'hypersphere', 'quantization', 'poseable',
        'downweighted', 'query-to-normalizer', 'quantization', 'quantize',
        'quantizing', 'quantized', 'quantizes', 'resight', 'resighting',
        'resightings', 'resighted', 'scalable', 'sight-resight', 'subgraph',
        'thresholding', 'undiscoverable', 'normalizers', 'unnormalized',
        'eigenvectors', 'discriminatively', 'trilinear', 'speeded',
        'discretized', 'matchable', 'radians', 'maxima', 'extrema', 'minima',
        'un-cropped', 'piecewise', 'unreviewed', 'untraced', 'dimensionality',

        'foregroundness', 'Fisherfaces',  'eigenfaces', 'overfitting',
        'groundtruth', 'renormalized',

        'burstiness', 'bursty', 'pre-trained', 'pre-filtered', 'pre-training',
        'pre-computed', 'saliency', 'downsampling', 'superpixel-based',
        'RANSAC-inliers', 'outliers', 'haversine', 'unary', 'parameterizes',
        'timestamp', 'convolving', 'extremal', 'incomparability', 'nan',
        'downsampled', 'subgraphs', 'subfigure', 'multicut', 'inlier',
        'inliers', 'maxout', 'encodings', 'convolutional', 'sigmoid',
        'unordered', 'keypoint-descriptor', 'convolved', 'resampling', 'iff',
    }

    EDGE_CASE = {
        'hoc', 'Ol', 'pred',
    }

    EXTRA = {
        # '^n',
        # 'yy',
        # 'xx',
        # 'xy',
        # 'yx',
        'annot', 'xy-locations', 'annotSL', 'Figure~', 'argmax', 'inv',
        'nameSL', 'paren', 'bincase', 'eq', 'teq', 'forall', 'annotSL'
        'NScoreExpt',
        # 'ori_', 'scale_', '_x', 't_', '_y', 'pt_', 'desc_K', 'M_i', 'E_p',
        # 'E_n', 'E_i', 'desc_j', 'desc_i', 'sum_',
        # 'Matches_',
        'modfn', 'subseteq', 'cdot', 'elltwosqrd', 'atantwo', 'tohmg', 'unhmg',
        'inII', 'inI', 'isinlier', 'timedist', 'th',  'fg', 'Real^' 'txt',
        'FGIntraExpt', 'SMKExpt', 'KExptB', 'KExptA', 'kptstype', 'frac',
        'amech', 'fmech', 'dsize', 'qsize', 'elltwo', 'dsize', 'dpername',
        'poisson', 'leftarrow', 'Algorithm~', 'pvar', 'alg', 'binom', 'clf',
        'mathop', 'inconpcc', 'leftarrorow', 'emph', 'jpg', 'kredun', 'kredun',
        'leq', 'decisiongraph', 'giga', 'vec', 'opname', 'ldots',
        'quantization', 'argmin',
        'Pred',
    }


IGNORE_SPELLING = set()

for word in Spelling.NAMES:
    IGNORE_SPELLING.add(word)

for word in Spelling.ACCRONYMNS:
    IGNORE_SPELLING.add(word)
    IGNORE_SPELLING.add(word + 's')

for word in Spelling.NORMAL:
    IGNORE_SPELLING.add(word)
    IGNORE_SPELLING.add(word[0].upper() + word[1:])

for word in Spelling.EDGE_CASE:
    IGNORE_SPELLING.add(word)

for word in Spelling.EXTRA:
    IGNORE_SPELLING.add(word)


LANGTOOL_JAR = '~/opt/LanguageTool-3.7/languagetool-commandline.jar'


def find_error_text(lines):
    carrot_row = None
    for count, line in enumerate(lines):
        if set(line) == set(' ^'):
            carrot_row = count
            break
    if carrot_row is not None:
        match = re.search('\\^+', lines[carrot_row])
        error_text = lines[carrot_row - 1][match.start():match.end()]
    else:
        error_text = None
    return error_text


def should_ignore(item):
    lines = item.split('\n')
    rule_line = lines[0]
    rule_fmt1 = '{item_num}.) Line {r}, column {c}, Rule ID: {ruleid}[{n}]'
    rule_fmt2 = '{item_num}.) Line {r}, column {c}, Rule ID: {ruleid}'
    result = parse.parse(rule_fmt1, rule_line)
    if result is None:
        result = parse.parse(rule_fmt2, rule_line)
    if result is not None:
        error_text = find_error_text(lines)
        if result['ruleid'] == 'EN_UNPAIRED_BRACKETS':
            if error_text in {'\''}:
                return True
        if result['ruleid'] == 'MORFOLOGIK_RULE_EN_US':
            if error_text in IGNORE_SPELLING:
                return True
            if '_' in error_text:
                return True
            if '$' in item and len(error_text) <= 2:
                return True
            if '$' in error_text:
                # maybe too agressive
                return True
            if error_text + '.jpg' in item:
                return True
            if error_text + '.png' in item:
                return True
            if '\\' + error_text in item:
                return True
        if result['ruleid'] == 'CURRENCY':
            return True
        if result['ruleid'] == 'POSSESSIVE_APOSTROPHE':
            if error_text in {'plains'}:
                return True
        if result['ruleid'] in {'PHRASE_REPETITION', 'ENGLISH_WORD_REPEAT_RULE'}:
            if '###' in item:
                return True
        if result['ruleid'] == 'THE_SUPERLATIVE':
            if error_text in {
                'rd$ nearest', '$ nearest', 'reciprocal nearest',
                'of nearest', 'Bayes nearest',
                'second nearest',
                             }:
                return True
        if result['ruleid'] == 'EN_COMPOUNDS':
            if error_text in {'small time'}:
                return True
        if result['ruleid'] == 'EVERY_EACH_SINGULAR':
            if error_text in {'maxima'}:
                return True
        if result['ruleid'] == 'A_PLURAL':
            if error_text in {'a maxima'}:
                return True
        if result['ruleid'] == 'IN_A_X_MANNER':
            if error_text in {
                'in a timely manner'
            }:
                return True

        if result['ruleid'] == 'A_INFINITVE':
            if error_text in {
                'the SIFT', 'The SIFT', 'a SIFT',
                'The shortlist', 'a shortlist', 'A shortlist', 'Bayes nearest',
                'a refresh', 'the refresh', 'a merge',
                'A merge',
            }:
                return True
    else:
        print('UNABLE TO PARSE')
        print(item)
    return False


def check_language(fpath):
    """
    fpath = 'outline_chapter2-related-work.md'
    """
    jarpath = ut.truepath(LANGTOOL_JAR)
    base_args = ['java', '-jar', jarpath]
    args = base_args[:]
    args += ['-l', 'en-US']
    if DISABLE_RULES:
        args += ['--disable', ','.join(DISABLE_RULES)]
    args += [fpath]

    print('Checking fpath = %r' % (fpath,))
    assert ut.checkpath(fpath)
    info = ut.cmd2(' '.join(args))
    out = info['out']

    items = out.split('\n\n')
    if items and items[0].startswith('No language specified, using'):
        items = items[1:]
    if items and items[0].startswith('Expected text language:'):
        items = items[1:]
    if items and items[0].startswith('Working on '):
        items = items[1:]

    print('Found %d errors' % (len(items),))

    for item in items:
        if not should_ignore(item):
            print('\n')
            print(item)
    print('Done checking fpath = %r' % (fpath,))


if __name__ == '__main__':
    varargs = ut.get_cmdline_varargs()
    if len(varargs) != 1:
        raise ValueError('Expected exactly one filepath. Got {}'.format(varargs))
    fpath = varargs[0]
    check_language(fpath)
