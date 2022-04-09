Identifying Individual Animals using Ranking, Verification, and Connectivity
============================================================================

.. image:: https://i.imgur.com/qAW51Uc.png

Abstract
--------

In this thesis we address the problem of identifying individual animals using
images in the context of assisting an ecologist in performing a population
census.  We are motivated by events like the "Great Zebra Count" where
thousands of images of zebras and giraffes were collected in Nairobi National
Park over two days.  By grouping all images that contain the same individual we
can census these populations.  This problem is challenging because images are
collected outdoors and contain occlusion, lighting, and quality variations and
because the animals exhibit viewpoint and pose variations.

Our first contribution is an algorithm that ranks a database of images by their
similarity to a query.  A manual reviewer inspects only the top few results for
each query --- significantly reducing the search space --- and determines if
the animals match.  Using this algorithm alone, we analyzed the images from the
Great Zebra Count and performed a population census.  Our second contribution
is a verification algorithm that determines the probability that two images are
from the same animal, that they are not, or that there is not enough to decide.
This algorithm is used with the ranking algorithm to re-rank results and
automatically verify high confidence image pairs.

Our third contribution is a semi-automatic graph identification algorithm.  The
approach represents each image as a node in the graph and incrementally forms
edges between nodes determined to the same animal.  The ranking and
verification algorithms are used to search for candidate edges and estimate
their probability of matching.  Based on these probabilities, edges are
prioritized for review and placed in the graph when they are automatically
verified or manually reviewed.  Redundant connections are added to detect and
recover from errors.  A termination criterion determines when identification is
finished.  Using the graph algorithm we perform a population census on the
scale of the Great Zebra Count using less than 25% of the manual reviews
required by the original method.

Citation
--------

The bibtex citation entry is: 

.. code:: bibtex

    @phdthesis{crall_identifying_2017,
      address = {Troy, NY},
      author = {Crall, Jonathan P.},
      school = {Department of Computer Science, Rensselaer Polytechnic Institute},
      title = {Identifying {Individual} {Animals} using {Ranking}, {Verification}, and {Connectivity}},
      type = {Ph.{D}. {Thesis}},
      year = {2017}
    }

Full Text and Slides
--------------------

The full text PDF is available on GitHub to be 
`viewed <https://github.com/Erotemic/crall-thesis-2017/blob/master/crall-thesis_2017-08-10_compressed.pdf>`__ or 
`downloaded <https://github.com/Erotemic/crall-thesis-2017/raw/master/crall-thesis_2017-08-10_compressed.pdf>`__.

Google slides hosts my original 
`defense presentation (2017-07) <https://docs.google.com/presentation/d/1mhq76mL98ViPaIELM8-t1786RGg5cPFLJcZxPAMhM8g>`__  and 
`candidacy presentation (2016-05) <https://docs.google.com/presentation/d/1OHchKzz6-hoh8imlrrP-SkpW7YKEbF2GF7Pdl8bzWW4>`__. These can
also be found on IPFS via the following CIDS: ``QmezNaQ2GypcN8951DxXWEkZdwxtZb8tohWKjHqqGVRDUi`` and ``QmZDsmeJTwiQKFeCAWA5Vpq1hrK96xkmmLfgkSQ2DDp5qs``.

Full Source
-----------

The final state of the repo including all images needed to reproduce the PDF
have been uploaded to IPFS (as of 2022-04-09).  The root CID is:
``QmTD1nZ4pbrB1SnjkLGt9Cs37mZbabXqjn6YZaAKVEoSvY``. And the main relevant data
CIDS are:

.. code:: 

    QmUkJhNSLDSgBnvxu5TLiXGU8LCR7tfS9s2meWCZZQ6bnL crall-thesis-2017/guts
    QmScScfpeKA2CtShuin5o5af5MN3NFhQBLeDqEUb435qXu crall-thesis-2017/notes
    QmPmpgBGw2kHPRVBg6z9m28PNLAzCKMe29QvJ3YvWZRo1G crall-thesis-2017/tmp/figures1
    QmUYQFvdWEVYEsmf5wNfHTPzWrHtaiZjcSanf5FsD74NYu crall-thesis-2017/tmp/figures2
    QmNqvbG1ng6z3bATR4XRyPiSGVExHaoLUQszqYFeARrBoc crall-thesis-2017/tmp/figures3
    QmeuC9tYezC75yRLrG7tvCT7tXrQYsLWtvVw62ZYGDEBBw crall-thesis-2017/tmp/figures4
    QmWmkVJv48A5RTGSm8H92qUHvcKeKsKugHbYsua8ktMjQV crall-thesis-2017/tmp/figures5
    QmTs6PB5148DouDWKAv8WB9Q2zdx3crCBb3W88bHjLLkfM crall-thesis-2017/tmp/figuresC
    QmUf1YkuEdmEczm6j237rgtUwSKaNkL4uCCq4QFZrfDL2c crall-thesis-2017/tmp/figuresGraph
    QmajtiHvGuQ4vbVPH36R6E5KAxpQao5R7XGre8aqa8iWPK crall-thesis-2017/tmp/figuresX
    QmXwq83V6WBtd8vSV3JNHTyYvH3HiU6CzA46jDtSV6xGwD crall-thesis-2017/tmp/figuresY
    QmZKeYDeVkKMbmEvL7ue8r8uG2TqB6aJXhX2dhNLKsawD3 crall-thesis-2017/tmp/figures_graph
    QmZuc9FyH6mJ1hsMwKv77rbyGeWzLGCjrCd8gyXNtCh9JJ crall-thesis-2017/tmp/figures_new3
    QmQd9zEb2SxbweNcLMGmnx34AvBJWCp4PUbrdgZkP1RTVG crall-thesis-2017/tmp/figures_pairclf
    QmTD1nZ4pbrB1SnjkLGt9Cs37mZbabXqjn6YZaAKVEoSvY crall-thesis-2017

Selected Figures
----------------

The following is a selection of figures from the this that provides a visual
summary of the contents.


.. image:: https://i.imgur.com/yvRcGu7.png
.. image:: https://i.imgur.com/5XYRAly.png
.. image:: https://i.imgur.com/t68q2L8.png
.. image:: https://i.imgur.com/rkOzoD2.png
.. image:: https://i.imgur.com/577HtKb.png
.. image:: https://i.imgur.com/59t3Qu8.png
.. image:: https://i.imgur.com/BjatIK9.png
.. image:: https://i.imgur.com/sD5RDZ1.png
.. image:: https://i.imgur.com/BjonGFU.png
.. image:: https://i.imgur.com/RnghQVI.png
.. image:: https://i.imgur.com/9yDc2KS.png
.. image:: https://i.imgur.com/RKLUBdV.png
.. image:: https://i.imgur.com/GRBJfLV.png
.. image:: https://i.imgur.com/Lcb82aD.png
.. image:: https://i.imgur.com/xsDBrpv.png
.. image:: https://i.imgur.com/v7Trn5c.png
.. image:: https://i.imgur.com/ZDEb4dr.png
