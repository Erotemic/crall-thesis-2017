#Chapter 4 - Graph Based Identification
---------------------------------------

## Introduction
To identify individuals in a dynamic context we will view the set of all
annotations as a graph. In this graph we place an edge between any two
annotations we wish to compare. We develop a probabilistic algorithm to answer
the following questions between any pair of annotations:
 
* Is this pair comparable and are they the same or different?
* Is this pair a photobomb?

A full set of answers to these questions allows us to partition the graph into
individuals by cutting any edge that is not labeled as "same" and then
inspecting the connected components. However, answering all these questions on
a complete graph would take `O(len(V) ** 2)` time. As the number of individuals
in the graph grows the vast majority of the edges will be labeled as different.
Considering that all that is needed to make the identifications are positive
reviews we observe that some of these edges may be omitted. Specifically we can
omit any number of edges and still determine the underlying connected
components as long as each underlying component is connected by comparable
edges. 

Given this graph, a probabilistic answer to these two questions on each edge,
and a tunable operating point, we can automatically determine some clustering
of annotations highly likely to be the same.  However, several challenges
remain. 

* Because automatic decisions are made only in the context of a pair of
  annotations, what happens when the graph is in an inconsistent state? 
  (i.e. the inferred equivalence relation is not transitive e.g. A is the same
   as B is the same as C but is different from A)
    * We develop an algorithm for detecting when an error has occurred
      (transitivity is violated).
    * We develop an algorithm that suggests what edges could have caused the
      error.
* The decisions under the operating point threshold must be left to manual
  reviewers. Is there a way to minimize the number of user interactions?
    * We develop an algorithm for prioritizing edges to review based on
      connected compoments.
* User reviewers are not always correct. Is there a way to detect and recover
  from user and algorithm error?
    * We assuming a reviewer is less likely to make the same mistake twice.
    * If we do not trust a single decision then we must ask for additional
      (redundant) decisions. 
    * Note this increases the number of reviews that are now necessary.
    * We describe a method for increasing confidence in the labeling while still 
      minimizing the number of reviews based on augmenting the diameter of the
      graph.
    * By combining this method with error detection we can address split and
      merge errors.

An outline of this chapter is as follows: 

* We describe how we will learn 1-vs-1 classifiers to address the problem of
  answering questions between pairs of annotations.
* We will describe how to construct the identification graph.
* We describe our automatic review procedure and how to detect and correct
  inconsistencies that arise. 
* We describe an algorithm to prioritize uncertain edges to review under the
  assumption that a manual reviewer is always accurate.
* We relax this assumption by adding a small set of redundant edges for user
  review.
* We describe how errors in this review process can be detected and corrected
  using redundant edges.
* We describe experiments to test the accuracy of our automatic algorithms as
  well as the effectiveness of out user review strategy.

----------------------------------
##4.2 Learning the 1-v-1 classifiers
----------------------------------
Problem: 

* The one-vs-many algorithm scores are not separable enough to make automatic
  decisions.
* The one-vs-many algorithm cannot determine if a high score is due to a
  correct match or a photobomb.
* When two annotations may have low scores because they are not-comparable they
  should not be marked as different animals.

Solution:

* Train a verification mechanism that can be applied to one-vs-many results.
* The verification mechanism operates on pairs of annotations and classifies
  them independent of the rest of the database just as a manual verifier would.
* Train two classifiers. 
* The first assigns a probability of {match, no-match, not-comparable} to any
  pair of annotations.
* The second assigns probabilities of {photobomb, not-photobomb}.

In this section we describe:

* How we construct a training set of annotation pairs with labels.
* How we construct a fixed-length feature vector for a pair of annotations.
* How we use the set of labeled feature vectors to fit the classifiers.

### Constructing training pairs
* Output: 
    * A set of annotation pairs.
    * Match state labels: {match, no-match, not-comparable}.
    * Photobomb state labels: {photobomb, not-photobomb}
* Challenges:
    * Using all `choose(n, 2)` pairs results in an unbalanced training set
      with prohibitive training time.
    * Groundtruth may not be complete especially for photobomb and
      not-comparable examples.
* Matching training set:
    * For each annotation:
    * Rank the database using the vsmany algorithm score
    * Partition the result into two ranked lists: one for correct matches and
      one for incorrect matches.
    * Select annotations randomly and from the top, middle, bottom of the list.
    * For positive examples we select
        * 4 from the top, 2 from the middle, 2 from the bottom, and 2 randomly
    * For negative examples we select
        * 3 from the top, 2 from the middle, 1 from the bottom, and 2 randomly
    * Any duplicate pair is removed.
    * Random examples help ensure the training set selection is representative.
    * Positioned examples help ensure the training set contains varying degrees
      of classification difficulty.
    * For positive examples this often means selecting all positive pairs. 
    * The top negative examples are hard negatives (because the vsmany
      algorithm assigned them high scores).
    * The bottom, middle, and random negative examples can be seen as easy
      negative examples.
* Photobomb training set:
    * Augment the matching training set with all annotation-pairs marked as
      photobombs.
    * This does not guarantee that all other pairs are not-photobombs.
    * We do some amount of manual cleaning before training, but hope to use the
      trained classifier iteravely correct the training set.
* Labeling:
    * In most cases we can correctly assign {match, no-match} labels using the
      groundtruth.
    * Not-comparable is more difficult because that option was not available
      during most of our turking.
    * Guessing non-comparable without groundtruth
        * We use a strategy to guess if a pair is not-comparable by checking if
          the scores are under a threshold and that the labeled viewpoints are
          beyond a threshold distance. 
        * Note, to avoid bias we exclude viewpoint from our feature measures
          when using this strategy. Iterative relabeling will allow us to add
          this feature back in as the training set is curated.
    * We could build a UI to inspect the guesses.

### Constructing pairwise feature vectors
* For each annotation pair we create a fixed-length feature vector
* Feature vectors contain local and global information.
* Constructing local information:
    * A one-vs-one algorithm to creates a rich set of correspondences 
        * Reciprocal nearest neighbors form feature correspondences
        * The ratio test and spatial verification are used to refine matches.
        * For each feature correspondence we make a set of measurements that will
          be used to construct the feature:
            * SIFT distance, local normalizer distance
            * ratio of correspondence to local normalizer distance.
            * spatial verification error in location, scale, and orientation
            * keypoint attributes: relative xy-positions, scales, and
              forgroundness weights.
    * Summary statistics consolidate the unordered correspondences into
      a fixed length vector.
    * Order of the vector is determined by score type and summary type. 
    * The statistics we use for each local measurement type over all
      correspondences in a pair are:
        * `[sum, mean, std]`. 
    * We also include the number of matches.
* Constructing global information:
    * For each annotation pair we include the unary and pairwise
      properties:
        * Unary: Per-annotation time, gps-lat, gps-lon, viewpoint, and quality.
        * Pairwise: Distances between the unary values using an appropriate
          distance metric (absolute difference, haversine, etc.)
        * Using time and GPS we also include the "speed" of the annotation pair.
* Global attributes are concatenated with the local information.
* An example of a subset of a resulting feature vector looks something like this:
```python
        OrderedDict([('global(qual_1)',      nan),
                     ('global(qual_2)',      nan),
                     ('global(qual_delta)',  nan),
                     ('global(gps_1[0])',    -1.37),
                     ('global(gps_2[0])',    -1.41),
                     ('global(gps_1[1])',    36.81),
                     ('global(gps_2[1])',    36.77),
                     ('global(gps_delta)',   5.79),
                     ('len(matches)',        20),
                     ('sum(ratio)',          10.05),
                     ('mean(ratio)',         0.50),
                     ('std(ratio)',          0.09)])
```
* Notes:
    * Feature vectors may contain NaN values if it is not possible to compute 
      one of the dimensions. We use a classifier that can address this problem.
    * We have experimented with using individual properties of selected edges but
      found simple summary statistics to be superior. 
    * We have experimented with augmenting one-vs-one scores with vsmany LNBNN
      distinctivness but found this to negatively impact performance. However,
      because all of our measures are local we do not need to worry about
      covariance with database size. This gives a desirable property where any
      trained classifier trivially generalizes to other datasets and re-training is
      as simple as adding new annotation pairs. 
    * In our experiments we analyze how informative each feature dimension is.  We
      prune any uninformative features to reduce training / testing time.

### Defining the classification problem
* We are given a training set pairwise feature vectors and
  match/photobomb labelings, `(X, y)`. This is the classic input a supervised
  learning problem.
* We choose to construct two classifiers:
    * Main classifier for {match, no-match, not-comparable} will learn
      `P(match_state | X)`.
    * Additional classifier for {photobomb, not-photobomb} will learn
      `P(photobomb_state | X)`.
* As a baseline we will train both classifier independently using the same
  feature set. 
* There are many choices of learning algorithms.
    * We want the output to be probabilistic and multi-class
    * The classifier needs a way of handling missing information, i.e. feature
      vectors will contain NaN values.
    * For these reasons we choose a random forest as the learning algorithm.

#### Random Forest Details
* Advantages of Random Forests:
    * Handles missing values
    * Probabilistic multi-class classification
    * Fast to train 
* A random forest is an ensemble of decision trees.
* Each decision tree is bootstrapped --- i.e. trained on a randomly selected
  subset of the data. 
* To grow a decision tree each node chooses a feature dimension and a test that
  induces a binary split on the data.
* The chosen feature dimension and tests are chosen to maximize information
  gain --- i.e. maximize the difference between the entropy (with respect to
  the target labels) in the parent node and the weighted average of the entropy
  in the children nodes.
* Feature importance can be determined by summing the information gain achieved
  at each node split using that feature.
* To handle missing data each decision tree uses the "separate class"
  method `[ding_investigation_2010]`.
    * The separate class method treats missing values as a separate measurement.
    * In the case of a categorical feature (like quality or viewpoint) each missing
      value is replaced with an unused value that indicates a new category.
    * In the case numerical data each NaN value is replaced with an extremely high
      or low value to simulate this effect.
    * There is strong in the literature that best way to handle missing data is the
      separate class method when the likelihood that data is missing is dependant
        on the target class.
    * This is the case with many of our features (e.g. if there are only `N-1`
      correspondences then the last correspondence value will be NaN which is
        indicative of a non match case).
    * In the case where a NaN value might not be informative (e.g. quality review
      is missing), then the forest should disregard it just as if it was a normal
      non-predictive feature.
* To tune the hyperparameters of the classifier for each species we use
  grid search with 3-fold cross validation.


-------------------------------------------
##4.3 Constructing the identification graph
-------------------------------------------
Problem: Given a set `V`, of annotations to identify it would be costly
(`O(len(V) ** 2)` time) to execute the one-vs-one identification algorithm on
each pair.

Solution: We use the one-vs-many algorithm which has been shown to have high
recall to determine a set of candidate edges E, and use these to construct our
graph G=(V, E). Details are as follows:

* Given a set of annotations run a execute the one-vs-many algorithm using each
  annotation as a query and the entire set of annotations as the database.
  Note, it is also possible to execute only a subset of annotations as a query
  --- e.g. in the case where an occurrence is identified against a database of
  exemplars.
* For each returned ranked list take the top N (we use N=5) results.
* Create an undirected edge between the query and each of its top results.

--------------------------------------
##4.4 Prioritizing edges for user-review
--------------------------------------
Problem: Even with automatic review user input is still needed. This forms an
active learning problem.  Humans need to be in the loop in order for the users
to gain confidence in the system and for the system to generalize to new data.
It is important find the right trade-off that minimizes the number of user
interactions while also maximizing the accuracy of the resulting clusters.

Solution: We use a connected component algorithm to infer which edges need
review. The probability of matching defines the priority of edges that need
review. 

**Terminology**: For the remainder of this chapter we will use "connected
component" (CC) to refer to the connected components of matching edges --- i.e.
connected components a subgraph of G that contains edges that have been
reviewed as the same.

### Automatic review
* The one-vs-one classifiers are applied to each edge in the graph. Each edges
  now stores its matching and photobomb state probabilities.
* For each classifier we assume that some operating point has been chosen for 
  each classifier state. (See Experiments for details on choosing operating
  points). In other words we have 5 thresholds: 
    * match threshold
    * no-match threshold
    * not-comparable threshold
    * photobomb threshold
    * not-photobomb threshold
* Ideally, an automated review for `state` is applied to each edge if `P(state) > state-threshold`.
  Note (thresholds must be either be above .5 to avoid simultaneously choosing
  two mutually exclusive states or the definition can be changed to choose
  `state` if `P(state) > state-threshold and P.argmax() == state` )
* However, our initial approach will be subject to several heuristics:
     * We will not try to automatically classify not-photobombs and
       not-comparable by setting their thresholds to infinity. 
     * We will not auto-review the matching state of any pair that is likely to
       be a photobomb.
* Under these heuristics the automatic review rules are:
    * Each edge with P(photobomb) > photobomb-threshold is auto-reviewed as a photobomb.
    * Each non-photobomb edge with P(match) > match-threshold is auto-reviewed as match.
    * Each non-photobomb edge with P(no-match) > no-match-threshold is auto-reviewed as no-match.
* Note: because these edge reviews are independent of the graph (i.e. we have
  not done any sort of probabilistic inference) automatic reviews may trigger
  an inconsistent state.
* All edges without a matching state label must now be considered for user review.


### Handling Inconsistent State.

* Detection
    * An inconsistent state can easily be detected as any CC that contains a
      negative edge in the original graph.
* Recovery
    * Within an inconsistent CC find all edges labeled as no-match. 
    * For each no-match edges with endpoints `(s, t)` run a weighted min-st cut
      using the number of times an edge was reviewed as the weight. 
    * If the weight of the no-match edge is greater than the sum of the weights of
      the cut edges append the no-match edge to a list of candidate edges otherwise
      append the cut edges. 
    * Stack and return the list of all the candidate edges.

### Connected Component Review Algorithm:
* Assuming that a user is always correct we make the following observations: 
    * Edges within CCs do not need to be reviewed 
    * Edges between CCs with at least one other negative review do not
      need to be reviewed.
    * Reviewing positive edges first is strictly better for minimizing the
      number of reviews. See [Proof-1].
    * If the user has made all positive reviews then there is no benefit (in
      terms of identification) to continue labeling negative cases. For most
      datasets the number of required negative reviews will be much higher
      than the number of positive reviews [See Corollary-1]
    * Therefore if the user may simply stops reviewing after not being asked to
      review a positive match for a sufficient amount of time.
* Using these observations the priority review algorithm is as follows:
    * We want to review all positive matches first. We therefore
      assign each edge a priority based of (P(match) * P(not-photobomb) * 1 -
      P(not-comparable)) using the assumption that photobomb annotations are
      less likely to match.
    * All reviewed edges have their priority set to zero.
    * All edges within a consistent CC have their priority set to zero.
    * All edges within an inconsistent CC we run the inconsistency recovery
      algorithm and set the priority of all edges to zero except those flagged
      as potential error edges.
    * All edge between two CCs with at least one negative review have their
      priorities set to zero.
    * As new reviews are dynamically added to the system only the priorities of
      the directly influenced CCs and their neighboring CCs need to be updated.
      We store the number of times each edge is reviewed.
    * This is implemented efficiently using a dictionary-heap based priority
      queue. 


----------------------------------------
##4.4 Detecting and Recovering from Errors
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
* Within each CC (using only reviewed edges) we want to add edges to ensure the
  diameter of each CC is no more than D.
* We want to choose a only a small number of edges that satisfy this
  constraint. We also want these edges to be comparable.
* Framed as Diameter Augmentation ("Diameter-d"): 
  Given target diameter d, graph G=(V, E) and
  candidate non-edges ~E, find the smallest set of non-edges E' ⊆ ~E such that
  the diameter of the augmented graph G'=(V, E E') is at most E'. 
* In general this problem is NP-hard, but in the unit-cost unit-length case there
  is an approximation algorithm with approximation ratio O(log(choose(|V|, 2)) * log(d)).
* The basic idea of the approximation algorithm is to:
    * Reformulate the problem as "Restricted Diameter-d" which adds the constraint that
      any new path between nodes that violate the diameter constraint in the original graph  
      must contain either exactly 1 or exactly 2 consecutive edges in ~E. It turns out that 
      any solution to "Restricted Diameter-d" is a solution to "Diameter-d".
    * Construct an integer linear program (ILP) that solves "Restricted
      Diameter-d". For the details of this ILP see [Dodis99].
    * Solve a relaxed version of the ILP to obtain fractional values.
    * Either apply a randomized rounding scheme to achieve an integral solution OR 
      define an instance of hitting set using the fractional values and then 
      approximiately solve the hitting set problem using a greedy approach.
* We can use this same idea between consistent CCs with at least one negative
  reviewed edge if we care about detecting false negatives. However, we would
  use a different (larger) diameter parameter and we would also include the no-match edges 
  in the d-diameter graph.

### Merge Case Detection
* Most merges are handled naturally by the system. These are detected as high
  probability edges between two annotations in different unreviewed connected
  components.
* A problem occurs when two annotations in different components are incorrectly
  marked as not-matching.
* Redundant edges between two components already reviewed to be different may
  result in an inconsistency, which allows us to detect a merge case error.
* A small set of these redundant edges can be found using diameter augmentation
  between CCs.

### Split Case Detection
* Split cases occur if two annotations that should not match are marked as
  matching.
* Without redundant reviews it is impossible to detect these.
* An inconsistent state is when a connected component of positive reviews
  contains a negative review.

---------------
##4.6 Experiments 
---------------
Experiments will evaluate:

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
* Results will be in the form of ROC AUC (using the 1-vs-rest strategy for
  multiclass labels).
* Absolute Separability of 1-vs-1 
    * Evaluated with respect to a set of annotation pairs
    * Cross validated over K-Fold splits of annotation pairs
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

### End-to-End Identification Accuracy
* Reflects system performance from the user's perspective.
* Combines rankings + score separability experiments
* Cross Validation
    * Split database into test/train sets using K-Folds. For each fold, the
      names in the test set are disjoint from the names in the train set.
    * Use the train set to build a 1-vs-1 classifier. 
* Setup
    * Build the graph as described in (Section 4.3)
    * Score the edges in the graph using the 1-vs-1 classifier.
* Evaluation
    * Each test predicts a partitioning, i.e. a cut value of True or False for
      every edge in the complete graph.
    * This labeling of the complete graph can be compared to the groundtruth.
    * Each edge is labeled as a true/false positive/negative.
    * For each test record the number of reviews and ROC AUC.
* Evaluating Semi-Automatic Partitioning
    * Use groundtruth to simulate a reviewer.
        * We can use some model of user error to force a reviewer to make a mistake.
        * By default we assume error rate is indepenent of the annotation pairs
        * Feed edges to the simulated reviewer in priority order until the
          priority queue is empty. Then stop.
    * Automatically classify any edge above its assignment threshold. 
    * Manually review all edges in priority order (this includes
      inconsistencies induced by the threshold).
    * We can examine the trade-off between the AUC and number of user reviews
      to choose appropriate review thresholds.
    * Special cases:
        * Fully manual review:
            * Can evaluate fully manual partitioning by setting review
              thresholds to infinity
            * In this test precision and accuracy are only dependant on the
              1-v-M rankings, but the amount of user reviews will be large.
        * Full automatic review:
            * Set all thresholds to zero and change the state of any inconsistent edge to 
              either match or not-comp depending on which state has the second
              highest probability after non-match.
            * Report classification statistics to compare algorithms and provide a
              baseline.
            * In this test precision and accuracy depend entirely on the algorithms, but no
              user reviews are needed.


---------------------------------------
#Appendix
---------------------------------------


#### Proof-1
We want to achieve perfect-id by reviewing the minimum number of edges.  Given
a set of edges that need review it is always better to review edges that are
more likely to be correct first.

**Claim**: 
Assuming a perfect reviewer, it is strictly better to review positive edges
before negative edges.

**Proof**:

* Let `cs = { ... { ... a ... } ...}` be the true annotation clusters.
* For each `c in cs` at least `len(c) - 1` reviews will need to be made,
  to create a spanning tree otherwise the annotations will not be connected. 
  Thus the minimum number of positive reviews is: 
  `sum(len(c) - 1 for c in cs)`
* To ensure that there are no merge cases there must be at least one negative
  review between each pair of CCs.  Thus the minimum number of negative reviews
  needed is
  `choose(len(cs), 2)`.
  (Note: `choose` is the binomial coefficient) 
* Positive and negative edges are mutually exclusive, therefore the minimum
  number of reviews required is: 
    `sum(len(c) - 1 for c in cs) + choose(len(cs), 2)`. 
* A second negative review between components or a second positive edge within
  a component is mutually exclusive from the set of minimal reviews and thus
  strictly increases the total number of reviews.
* When reviewing a positive edge it is always possible to determine if it would
  be redundant with another positive edge that exists. (Positive components are
  spanning trees and a redundant edge would add a cycle. Adding a non-redundant
  positive edge either adds a branch to the spanning tree or joins to spanning
  trees which is still a spanning tree).
* On the other hand when reviewing a negative edge it is not always possible to 
  determine if it is redundant with some other negative edge that exists. This
  is because redundant negative edges are defined between positive CCs. (all positive 
  CCs must be determined before you can gaurentee that any two arbitrary pairs of 
  negative edges are not redundant).
* Reviewing all positive edges first guarantees that all redundant edges
  are never encountered.
* Therefore it is always better to review edges more likely to be positive
  first. 
* Note: if a negative edge was mistakenly reviewed (e.g. in the case where the classifier 
  produced a false positive) then it impacts the total number of reviews at
  most by 1 (and only if it happens to be redundant with some other negative edge that
  was also mistakenly reviewed before a positive edge) because adding negative
  reviews still increases knowledge about redundancy, just not in a way that is
  useful without a sufficiently large set of positive reviews.

#### Corollary-1
**Claim**: 
The number of negative reviews needed is usually much larger than the number of
positive reviews.

**Proof**:
The number of positive reviews can be re-expressed as
`sum(len(c) - 1 for c in cs) = mean(len(c) for c in cs) * len(cs) - len(cs)`

We now consider and simplify the ratio between the number of positive reviews
and the number of negative reviews.
Let the average number of annotations per name be: `a=mean(len(c) for c in cs)`.
Let the number of names be `n=len(cs)`.
```
   numer         |          denom
-----------------------------------------
a * n - n        |   n * (n - 1) / 2
2 * a * n - n    |   n * (n - 1)
2 * a - 1        |   n - 1
2 * a            |   n
```
Thus if n > 2 * a, then the number of negative reviews is greater than the
number of positive reviews. For most species we will see many more individuals
than we will see images of specific individuals. Therefore the corollary is true.

