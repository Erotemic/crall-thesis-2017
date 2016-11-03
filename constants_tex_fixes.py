# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import re
from utool.util_regex import regex_word

COMMON_ERRORS = [
    ('spacial', 'spatial',),
    ('image net', 'Image Net',),
    ('hand crafted', 'hand-crafted',),
]


ACRONYMN_LIST = [
    ('Scale Invariant Feature Transform', 'SIFT'),
    ('Selective Match Kernel', 'SMK'),
    ('bag of words', 'BoW'),
    ('Fisher Vector', 'FV'),
    ('Vector of Locally Aggregated Descriptors', 'VLAD'),
    ('Gaussian mixture model', 'GMM'),
    ('Hamming Embedding', 'HE'),
    (r'Local \Naive Bayes Nearest Neighbor', 'LNBNN'),
    (r'\Naive Bayes Nearest Neighbor', 'LNBNN'),
    ('Fast Library for Approximate Nearest Neighbors', 'FLANN'),

    ('Leaky Rectified Linear Unit', 'LRLU'),
    ('Rectified Linear Unit', 'RLU'),
]


CAPITAL_LIST = [
    'Great Zebra Count',
    'Great Zebra and Giraffe Count',
    'Gauss',
    'Hessian',
    'Hamming',
    #'TF-IDF',
    'Bayes',
    'Fisher',
    'Hamming',
    'Lincoln-Petersen',
    'Fisher Vector',
]

CAPITAL_TITLE_LIST = CAPITAL_LIST[:]


for full, acro in ACRONYMN_LIST:
    capfull = full[0].upper() + full[1:]
    CAPITAL_TITLE_LIST.append(capfull)


AUTHOR_NAME_MAPS = {
    #u'Perdòch': ['Perdoch', u'Perd\'och'],
    #u'Perd\'och': ['Perdoch', u'Perd\'och'],
    #u'Perd\\mkern-6mu\'och': ['Perdoch', u'Perd\'och'],
    u'Perdoch': ['Perdoch', u'Perd\'och'],
    u'Jégou': [u'Jegou'],
    u'Hervé': [u'Herve'],
    u'Ondřej': [u'Ondrej'],
    u'Jörg': [u'Jorg'],
    u'Schnörr': [u'Schnörr'],
    u'Jiří': ['Jiri'],
    u'Mikulík': ['Mikulik']

    #'Frédéric'
    #'Léon'
    #Sánchez
    # Türetken
    #Ladický
    #Tomás
    #Jiří
}

CONFERENCE_LIST = [
    'ECCV',
    'CVPR',
    'EMMCVPR',
    'NIPS',
    'ICDT',
    'ICCV',
    'ICML',
    'BMVC',
]

JOURNAL_LIST = [
    'IJCV'
    'TPAMI',
    'CVIU',
]

CONFERENCE_TITLE_MAPS = {
    'EMMCVPR': [
        regex_word('EMMCVPR'),
        'Energy Minimization Methods in Computer Vision and Pattern Recognition'
    ],

    'CVPR': [
        regex_word('CVPR'),
        '^Computer Vision and Pattern Recognition',
        r'Computer Vision, \d* IEEE \d*th International Conference on',
        'Computer Vision, 2003. Proceedings. Ninth IEEE International Conference on'
    ],

    'IJCV': [
        regex_word('IJCV'),
        'International Journal of Computer Vision',
    ],

    'ICCV': [
        regex_word('ICCV'),
        'International Conference on Computer Vision',
    ],

    'TPAMI': [
        regex_word('TPAMI'),
        'Transactions on Pattern Analysis and Machine Intelligence',
        'Pattern Analysis and Machine Intelligence, IEEE Transactions on',
    ],

    'ECCV': [
        regex_word('ECCV'),
        'Computer VisionECCV',
    ],

    'NIPS': [
        regex_word('NIPS'),
        'Advances in Neural Information Processing Systems',
    ],

    'Science': [
    ],

    'Nature': [
    ],

    'ICML': [
        regex_word('ICML'),
        '{International} {Conference} on {Machine} {Learning}',
    ],

    'WACV': [
        regex_word('WACV'),
    ],

    'CVIU': [],

    'ICPR': [
        regex_word('ICPR'),
    ],

    'BMVC': [
        regex_word('BMVC'),
        'BMVC92',
    ],

    'NN': [
        'Transactions on Neural Networks',
        '^Neural Networks$',
    ],

    'TIP': [
        'Transactions on Image Processing',
    ],

    'ICIP': [],

    'BMVA': [
        'Alvey vision conference',
    ],

    'IT': [
        'Transactions on Information Theory',
    ],

    'ACCV': [
        regex_word('ACCV'),
    ],
    'CoRR': [],
    'AMIDA': [],

    'IJCNN': ['International Joint Conference on Neural Networks'],

    'AAAI': [],

    'JMLR': [
        'Journal of Machine Learning Research',
        re.escape('J. Mach. Learn. Res.'),
    ],

    'SP': [
        'Transactions on Signal Processing',
    ],

    'CSUR': ['ACM Comput. Surv.', 'ACM Computing Surveys'],

    'ICASSP': [
        'International Conference on Acoustics, Speech and Signal Processing',
        regex_word('ICASSP'),
    ],

    'STOC': [
        'ACM symposium on Theory of computing',
    ],

    'Pattern Recognition': [
        '^Pattern Recognition$',
    ],

    'Pattern Recognition Letters': [
        '^Pattern Recognition Letters$',
    ],

    'VISAPP': [
        'International Conference on Computer Vision Theory and Applications',
    ],

    'ICOMIV': [
        'ACM International Conference on Multimedia',
    ],

    'CiSE': [
        'Computing in Science Engineering',
    ],

    'Journal of Cognitive Neuroscience': [],

    'IJCPR': [
        'International Joint Conference on Pattern Recognition',
    ],

    'Image and Vision Computing': [
        '^Image and Vision Computing$',
    ],

    'PAA': ['Pattern Analysis and Applications'],

    'Siggraph': [
        'ACM Siggraph Computer Graphics',
    ],

    'ICLR': ['International Conference on Learning Representations'],

    'Oecologia': [],

    'IJDAR': ['International Conference on Document Analysis and Recognition'],

    'CIVR': ['International Conference on Image and Video Retrieval'],

    'SoCG': ['Twentieth Annual Symposium on Computational Geometry'],

    'Advances in the Study of Behavior': [],

    'TOG': [r'\bACM TOG\b'],

    'PCM': ['Multimedia Information Processing'],

    'The Computer Journal': [],

    'Biometrics': [],

    'Python in Science': ['Python in Science'],

    'INRIA Research Report': [r'Rapport de recherche RR-[0-9]*, INRIA'],

    'Proceedings of the IEEE': [],

    'Foundations and Trends in Computer Graphics and Vision': [],

    'Foundations and Trends in Machine Learning': [u'Foundations and Trends® in Machine Learning'],

    'Communications ACM': [],

    'Biometrika': [],

    'ICDT': ['Database Theory — ICDT’99'],
}
