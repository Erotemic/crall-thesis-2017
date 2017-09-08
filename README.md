# Identifying Individual Animals using Ranking, Verification, and Connectivity


## Abstract

In this thesis we address the problem of identifying individual animals using images in the context of assisting
  an ecologist in performing a population census.
We are motivated by events like the ``Great Zebra Count'' where thousands of images of zebras and giraffes were
  collected in Nairobi National Park over two days.
By grouping all images that contain the same individual we can census these populations.
This problem is challenging because images are collected outdoors and contain occlusion, lighting, and quality
  variations and because the animals exhibit viewpoint and pose variations.

Our first contribution is an algorithm that ranks a database of images by their similarity to a query.
A manual reviewer inspects only the top few results for each query --- significantly reducing the search space
  --- and determines if the animals match.
Using this algorithm alone, we analyzed the images from the Great Zebra Count and performed a population census.
Our second contribution is a verification algorithm that determines the probability that two images are from the
  same animal, that they are not, or that there is not enough to decide.
This algorithm is used with the ranking algorithm to re-rank results and automatically verify high confidence
  image pairs.

Our third contribution is a semi-automatic graph identification algorithm.
The approach represents each image as a node in the graph and incrementally forms edges between nodes determined
  to the same animal.
The ranking and verification algorithms are used to search for candidate edges and estimate their probability of
  matching.
Based on these probabilities, edges are prioritized for review and placed in the graph when they are
  automatically verified or manually reviewed.
Redundant connections are added to detect and recover from errors.
A termination criterion determines when identification is finished.
Using the graph algorithm we perform a population census on the scale of the Great Zebra Count using less than
  25% of the manual reviews required by the original method.

-----

The PDF can be viewed via this link: https://github.com/Erotemic/crall-thesis-2017/blob/master/crall-thesis_2017-08-10_compressed.pdf 

and downloaded via this link: https://github.com/Erotemic/crall-thesis-2017/raw/master/crall-thesis_2017-08-10_compressed.pdf


The bibtex citation entry is: 

```bibtex
@phdthesis{crall_identifying_2017,
  address = {Troy, NY},
  author = {Crall, Jonathan P.},
  school = {Department of Computer Science, Rensselaer Polytechnic Institute},
  title = {Identifying {Individual} {Animals} using {Ranking}, {Verification}, and {Connectivity}},
  type = {Ph.{D}. {Thesis}},
  year = {2017}
}
```
