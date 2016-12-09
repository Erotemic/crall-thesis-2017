Chapter 4 - Graph Based Identification
======================================

TODO:
Expand this in terms of algorithms 
write out detailed steps of the end-to-end system.
Include only a brief mention of extra work such as multicut / probability
updates / probability based diameter augmentation

Follow flow of

Constructing graph
Classifying edges
Thresholds for automatic review
Prioritizing edges for user review
Redundant edges for error correction

Details of connected component algorithm
proof of baseline prioritization scheme
proof of review minimization under diameter assumption


### Goals
* Have some automated method of handling photobombs
* Expand definition of matching to include non-comparable
* Accurately cluster all annotations of the same individual
* Exploit information from multiple images
* Minimize the number of user reviews
* Recover from split/merge errors
* Reformulate workflow tasks under a common graph based framework

### On-line setting
* We are given a set of new images
* We group images into occurrences
* We detect annotations within images
* We match annotations within occurrences to form encounters
* We match encounters against a database of exemplars, merge matched
  annotations, add new annotations, and correct any error in name labeling.
* We choose new exemplars


### Off-line setting
* We scan the database for potential name labeling errors
* We update learned measures


-----------------------------------
4.1 Automatic occurrence clustering
-----------------------------------
* Distance between space-time features
* Agglomerative clustering defines occurrences


----------------------------------
4.2 Learning the 1-v-1 classifiers
----------------------------------
Problem: 
Scores returned by the one-vs-many algorithm are not separable enough to make
automatic decisions. There is no way to determine if a high score is due to a
correct match or a photobomb. Additionally when two annotations may have low
scores because they are not-comparable they should not be marked as different
animals.

Solution:
Train a two classifiers. The first assigns a probability of {match, no-match,
not-comparable} to any pair of annotations. The second assigns probabilities of
{photobomb, not-photobomb}.

### Constructing a training set
* How do we choose a set of annotation pairs?
* Important to train with hard negatives
* Generating not-comparable labels without groundtruth

* TODO: DESCRIBE HOW EDGES ARE CHOSEN FOR TRAINING

### Constructing feature vectors
* Features represent a pair of annotations
* Features must be fixed length
* Prune uninformative features / choose informative features

### Constructing the classifier
* Main classifier for {match, no-match, not-comparable}
* Additional classifier for {photobomb, not-photobomb}
* Missing information, i.e. feature vectors will contain NaN values
* Advantages of Random Forests:
    * Handles missing values
    * Probabilistic multi-class classification
    * Fast to train 
* Random Forests can make probabilistic classifications

### Choosing operating points 
* For each classifier choose an operating point for each class.
* Pairs of annotations above these operating points can be safely 
  labeled as one of the six states in:
     {match, no-match, not-comparable} X {photobomb, not-photobomb}.
* Use ROC evaluation criteria for determining operating points.
    * Need to take special care in the multiclass-case
    * See experiments


--------------------------------------
4.3 Prioritizing edges for user-review
--------------------------------------
Problem: Even with automatic review user input is still needed. This forms an
active learning problem.  Humans need to be in the loop in order for the users
to gain confidence in the system and for the system to generalize to new data.
It is important find the right trade-off that minimizes the number of user
interactions while also maximizing the accuracy of the resulting clusters.

Solution: We adapt the same graph structure used to exploit multiple images. 
We use a connected component algorithm to infer which edges need review. The
probability of matching defines the priority of edges that need review.
Additional redundant edges are added in order to expose and correct errors.

### Graph Construction
* Each edge in the graph has attributes: 
  {score, reviewed state, inferred state}
* All edges above the positive operating point are classified as matching.
* All edges under the negative operating point are classified as not matching.
* All other edges are prioritized for user review. 

### Connected Component Review Algorithm:
* Edges within components do not need to be reviewed 
* Edges between components with at least one other negative review do not
  need to be reviewed.
* Priority is based on matching probability. Non-matching edges are considered
  next, and not-comparable edges are considered last because they add the least
  amount of information.  Reviewing positive edges first is strictly better for
  minimizing the number of reviews.
* If the user stops reviewing all other edges are considered not matched
  because it is much more likely for a random edge to be negative than
  positive.
* It may be necessary to review redundant edges given that humans and
  algorithms make mistakes.


----------------------------------------
4.4 Detecting and Recovering from Errors
----------------------------------------
Problem: The connected component algorithm will never generate an inconsistent
state. There will never be a connected component of matching edges that
contains a non-matching edge. This is because if a single component is marked
as the same or two components are marked as different an algorithm that
generates the minimum number of reviews will never suggest a new edge that
could cause an inconsistency.

Solution: We add a small number of redundant edges that are likely to cause
inconsistencies if they exist. After inconsistencies are generated they can be
detected and resolved.

### Redundant Edges for Error Detection
* Minimum cost diameter augmentation for choosing redundant edges
* This algorithm uses only the unweighted distance between nodes to determine
  which redundant edges should be added.
* Future Work:
    * Each connected component is assigned a probability that no mistakes were
      made classifying any of the edges within a connected component.
    * Any component with a low probability is marked for review. 
    * A new edge that maximizes the probability increase is selected for
      review.
    * Likewise each pair of components with a negative review is assigned a
      probability that any mistakes were made.

### Merge Case Detection
* Merges are handled naturally by the system. These are detected as high
  probability edges between two annotations in different unreviewed connected
  components.
* When two annotations are linked by a positive review their connected
  components merge.
* A problem occurs when two annotations in different components are incorrectly
  marked as not-matching.
* Redundant edges between two components already reviewed to be different may
  result in an inconsistency, which allows us to detect a merge case error.

### Split Case Detection
* Split cases occur if two annotations that should not match are marked as
  matching.
* Without redundant reviews it is impossible to detect these.
* An inconsistent state is when a connected component of positive reviews
  contains a negative review.

### Recovering from an Inconsistency
* Given an inconsistent connected component we use a minimum s-t-cut to
  suggest edges to re-review in the event of an error case.


--------------------------------
4.5 Automatic exemplar selection
--------------------------------
* Examine subgraph of probabilities for each individual.
* Create covering sets based on probabilities for each annotation based on a
  threshold.
* Use maximum weight minimum set cover to select a subset of annotations.
* Adjust threshold to find optimal cover.
* The optimal cover is the new set of exemplars.


---------------
4.6 Experiments 
---------------
Three things to evaluate

* Accuracy of rankings.
* Separability of the scores.
* Combined accuracy + separability with humans in the loop

### Accuracy of Rankings
* Results take the form CMC (cumulative match characteristics) curves
* Cross validated over random (but exclusive) query / database splits
* Rankings of 1-vs-1
* Rankings of 1-vs-M rankings
* Rankings of 1-vs-M with 1-vs-1 postprocessing
* Single Annotation Context
    * 1 query annotation per name
    * 1 database annotation per name
    * Annotations must be comparable
    * Singleton distractors
* Single Encounter Context
    * 1 query encounter per name
    * 1 database encounter per name
    * All annotations in database encounters must be comparable to at least one
      annotation in the query encounter.
    * Singleton distractors
* Multi Encounter Context
    * 1 query encounter per name
    * Multiple database encounters per name
    * Singleton distractors

### Separability of Scores
* We want to maximize class separability 
* ROC AUC / informedness / markedness / Matthews correlation coefficient
* Absolute Separability of 1-vs-1 
    * Evaluated with respect to a set of annotation pairs
    * Cross validated over K-Fold splits of annotation pairs
    * Evaluate using multiclass ROC AUC / Informedness / Markedness 
    * This gives an absolute measure of how well the classifiers work
    * Evaluate photobomb classification in binary case
    * Evaluate match classification conditioned on photobomb status
* Relative Separability of 1-vs-1 against 1-vs-M
    * Single annotation context for 1-v-M query 
    * Select pairs of annotations from results of 1-v-M query
        * Annotation pairs with ALL correct vsmany results at rank #1.
        * Annotation pairs that at least got some score in vsmany classification
    * Remove photobombs and non-comparable examples to give algorithms a fair fight.
      (this also lets us use binary ROC AUC)

### Graph Identification
* Reflects system performance from the user's perspective.
* Combines rankings + score separability experiments
* Cross Validation
    * Split database into test/train sets using K-Folds. For each fold, the
      names in the test set are disjoint from the names in the train set.
    * Use the train set to build a 1-vs-1 classifier. 
* Setup
    * Apply 1-vs-M matching to the test set. 
    * Only these edges will be considered for subsequent processing.
    * Refine the scores with the 1-vs-1 classifier.
* Evaluation
    * Each test predicts a partitioning, i.e. a cut value of True or False for
      every edge in the complete graph.
    * This labeling of the complete graph can be compared to the groundtruth.
    * Each edge is labeled as a true/false positive/negative.
    * From these we can compute binary classification metrics such as precision and
      recall.
    * An operating point can be selected for any test involving an adjustable
      threshold
    * For each test record the number of reviews and the Matthews correlation
      coefficient (MCC).
    * Evaluating Manual Partitioning
        * Use groundtruth to simulate a perfect reviewer.
        * Using the priority order manually review edges until the priority queue is
          empty. 
        * In this test precision and accuracy are only dependant on the 1-v-M rankings,
          but the amount of user reviews will be large.
    * Evaluating Automatic Partitioning
        * Thresholds: Link all annotations above a threshold. Do assign any negative
          labels to avoid inconsistent edges.
        * Multicut
        * Alpha Expansion
        * Report classification statistics to compare algorithms and provide a
          baseline.
        * In this test precision and accuracy depend entirely on the algorithms, but no
          user reviews are needed.
    * Evaluating Semi-Automatic Partitioning
        * Previous two examples are special cases.
        * Can measure precision / recall as a function of thresholds
        * Thresholds: Automatically classify any edge above its assignment threshold. 
            Manually review all edges in priority order (this includes inconsistencies
            induced by the threshold).
        * Multicut: Assign a multicut partitioning, but only review edges above
          their threshold that agree with the multicut partitioning. All other
          edges are reviewed in priority order.
        * Alpha Expansion: same protocol as multicut.
        * We can examine the trade-off between the MCC and number of user reviews
          to choose appropriate review thresholds.

-------
Details
=======

Proof-1
---------
We want to achieve perfect-id by reviewing the minimum number of edges.  Given
a set of edges that need review it is always better to review edges that are
more likely to be correct first.

**Claim**: 
Assuming a perfect reviewer, it is strictly better to review positive edges
before negative edges.

**Proof**:
Let `cs = { ... { ... a ... } ...}` be the true annotation clusters.

For each `c in cs` at least `len(c) - 1` reviews will need to be made
to connect the annotations.

At least `(len(cs) ** 2 - len(cs) / 2)` reviews will need to be made
to ensure that there are no merge cases. 

The minimum number of reviews required is: 
`sum(len(c) - 1 for c in cs) + (len(cs) ** 2 - len(cs) / 2)`. 

It would be redundant to review edges between components that already have one
negative review. Reviewing negative edges before positive edges might cause a
reviewer to review one of these edges before it could be inferred that it was
redundant. Therefore it is always better to review edges more likely to be
positive first. 

    
------
Extras
======

---------------------------------------------
4.6 Bootstrapping classifiers for new species
---------------------------------------------
Problem: Initially classifiers are untrained. To generalize to new species 
we need a method of bootstrapping the classifiers.

Solution: All reviews can be marked for user review until enough training data
has been gathered to construct the classifiers. 

* This is the almost the same as if no edge meets the automatic
decision thresholds. The only difference is that the scores
on the edges are not probabilities.
* Can use the same techniques for prioritizing edges for reviews.
Reviewing edges creates training data. Over time a classifier can be
trained.
* This is an active learning framework with humans in the loop.
    

------------------------------
4.3 Exploiting multiple images
------------------------------
Problem: 
The predicted probabilities over many sets of annotations forms a graph.
Information from multiple images could be used to infer a joint probability 
distribution over all annotations.

Solution: 
Form a graph with probabilities on edges and use graph inference techniques to
infer either a posterior assignment or a posterior probability distribution.

### Posterior Assignment
* We use multicut to determine the most likely partitioning of the annotations
  given the initial graph.
* All probabilities are first converted into two state probabilities of {same,
  different} for each edge.
* This only produces yes/no decisions so only the automatic decision are
  influenced, there is no update to posterior probabilities on the edges.

### Future Work: Posterior Probabilities
* This is future work
* This may be able to update the original 6-state probability. 
* Some algorithm to correctly infer posterior marginal probabilities on
  each edge.
    * Belief propagation on 3-clique-based MRF?
