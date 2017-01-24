----

# TODO:
    * ensure that the part where one-vs-many is rerun is incorporated
    * come up with a careful and clear motivation 
    * come up with a very short and concise process summary

* The other intro is fine for a thesis paper, but for a conference paper it has
  to get to the technical part quicker.

# Review Procedure Outline


### Intro and Motivation Version 1

To identify individuals in a dynamic context we combine our algorithms with
  human input.
Manual reviews are an expensive but powerful resource.
Efficiently utilizing this resource requires a carefully defined procedure
  that finds the appropriate trade-off between maximizing the information gained
  from each manual interaction and minimizing the number of interactions.
Our review procedure attempts to do as much automatic work as possible before
  falling back on manual reviewers.
Our procedure chooses the minimum number of reviews that achieves animal
  identification up to a specified redundancy level to minimize the risk of
  errors.
The procedure is robust and has mechanisms for detecting errors and recovering
  from inconsistencies.


### Intro and Motivation Version 2

This chapter defines a procedure to organize a large set of unidentified
  images into groups of individuals.
To a human, this process might be done by making piles of photographs
  (annotations), one for every individual.
However, as the number of piles become large, the time it takes to find the
  right pile for a new image becomes prohibitive.
To a computer, this is a clustering procedure.
Annotations can be viewed as nodes on a graph, and edges can be drawn to
  connect matching individuals.
However, a single misclassified edge can result in many misclassified
  annotations.
Therefore, we are motivated to combine the search speed of a computer with the
  verification accuracy of a human, but this is a challenging task.
Manual reviews are a powerful but expensive resource, and we should only
  interact with a manual reviewer when necessary.
We must also design around the fact that humans will occasionally make
  mistakes.


To identify individuals while addressing these challenges we propose an
  algorithm with "humans in the loop".
A computer vision algorithm finds candidate edges that suggest the identify of
  a new annotation.
A learned classifier is used to classify any edges above a confidence
  threshold.
A human reviewer checks which (if any) of the remaining suggestions are
  correct.
We ensure that the number of manual reviews is small using a priority
  mechanism to determine the order in which candidate matches are presented.
This works in conjunction with an inference mechanism that uses the graph
  structure to determine which candidate edges need to be reviewed.
Because human reviewers will occasionally make mistakes, the inference
  mechanism includes a redundancy criteria that detects and corrects these
  mistakes.
A termination criteria determines when identification is complete.

---------------
## Introduction
---------------

### Definitions and Terms
* The review procedure is formalized around the notion of a **decision graph**.
    * A decision graph is `G = (V, E)`.
    * The set of nodes `V` is the set of annotations.
    * The set of edges `E = E_p ∪ E_n ∪ E_i` is composed of three disjoint
      sets:
        * `E_p` is the set of positive edges between comparable annotations of
          the same animal.
        * `E_n` is the set of negative edges between comparable annotations
          between of different animals.
        * `E_i` is the set of incomparable edges between annotations that are
          not-comparable.
* Individuals are identified by **positive connected components (PCC)**.
    * Each PCC is a connected component in a subgraph `G_p = (V, E_p) ⊆ G`.


### Identification Criteria
* There are several criteria that a decision graph can satisfy.
    * Minimal Satisfaction Criteria:
        * Consistency: A PCC is consistent iff it contains no negative edges.
        * Completeness: For every pair of PCCs there is at least one negative
          edge between them.
    * Redundancy:
        * K-positive-redundancy:
            * A PCC is "k-positive-redundant" if it is consistent and it
              contains no cut-sets involving fewer than `k` positive edges. 
            * This is the equivalent to "k-edge-connectedness".
            * Note: A PCC that is k-positive-redundant is also
              (k-1)-positive-redundant (for `k ≥ 2`).
            * A graph has this property if all PCCs have this property.
        * K-negative-redundancy: 
            * A pair of PCCs is "k-negative-redundant" if there are `k` negative edges
              between them.
            * A graph has this property if all pairs of PCCs have this
              property.
            * For a graph to be "k-negative-redundant", it requires O(k N^2)
              negative decisions (where N is the number of individuals).
            * `1`-negative-redundancy is equivalent to completeness.
        * K-redundancy is tied to the number of decision mistakes that must be
          made in order for part of the graph to appear consistent or complete.
          Specifically, for PCC or pair of PCCs to both contain a mistake and
          be k-redundant then at least `k` mistakes must be made.
* Termination Criteria
    * Given parameters `kp` and `kn`
    * The review procedure terminates if the graph is consistent, complete,
      `(kp)`-positive-redundancy, and `(kn)`-negative-redundancy.
    * Note:
        * Negative edges do not contribute to the identification grouping, they
          only ensure that the positive PCCs are complete.
        * It will often be impractical to enforce that a graph must be complete
          in order to terminate.
        * At some point it will be necessary to infer that the remaining edges
          between PCCs are negative. This point must be chosen such that
          there is a high probability that the unreviewed pairs of PCCS are
          negative.


### Procedure Overview
The review procedure is to construct a decision graph that satisfies the
identification criteria.

* All annotations to be identified are used as nodes.
* An algorithm initializes a set of candidate edges.
* An automatic classifier predicts a label for each edges and any confident
  decision is added to the decision graph.
* The remaining candidate edges are prioritized and manually reviewed. 
* After a certain number of reviews candidate edges are recomputed using
  updated information.
* This repeats until the termination criteria is satisfied.

### Discussion Outline
* We first consider a simplified version of this procedure. We assume that
  review errors do not occur.  In this context we:
    * Describe how candidate edges are chosen.
    * Describe how edges are automatically classified.
    * Define a dynamic priority-based ordering for remaining candidates that
      results in the minimum number of user reviews.
* We then consider the practical case, where both users and algorithms make
  errors. In this context we:
    * Define and contrast inconsistencies versus mistakes.
    * We compare this context to the simplified context.
    * Describe an inconsistency recovery algorithm.
    * Describe a mistake discovery algorithm.
    * Discuss the implications of early stopping (stopping before all reviews
      are complete).
    * Discuss the implications of when it is not possible satisfy all
      identification requirements using the candidate edges.


## Review Procedure in a simplified context

### Simplifying assumptions: 
1. Classifier thresholds are set such that no errors are made.
2. Users do not make errors.
3. A subset of the candidate edges can satisfy the identification criteria
   (i.e. candidate edges are computed only once).
4. Redundancy parameters `kp` and `kn` are set to `0`.

### Initialization:
* Given a set of annotations use these as nodes. 
* Run the one-vs-many algorithm.
    * Use each annotation as a query and the entire set of annotations as
      the database.
    * The result is a ranked list of database annotations
* For each ranked list add the top `N` (we use `N=5`) query-result pairs to the
  set of candidate edges.

### Automatic classification:
* Predict the probabilities `P(match-state)` and `P(photobomb-state)` for each
  candidate edge using the one-vs-one classifiers.
* Automatically add an edge to the decision graph if we are confident in its
  matching state and we are confident that it is not a photobomb.
* Given a `state-threshold` for each `state in {match, no-match, not-comp}`,
  automatically add an edge to the appropriate decision edge set if:
    * `P(state) > state-threshold`, and
    * `P.argmax() == state`, and
    * `P(photobomb) < photobomb-threshold`.

### Prioritizing edges for user review:
* To satisfy minimal identification requirements we observe:
    * Each PCC needs enough reviews to be connected.
        * Therefore edges within existing PCCs do not need to be reviewed. 
    * Only one negative edge between any two PCCs needs to be reviewed.
        * Therefore edges between PCCs with at least one other negative review
          do not need to be reviewed.
* Using these observations the minimum number of reviews is achieved by
  reviewing as many positive edges (between existing PCCs) as possible
  before reviewing any negative edges. See [Appendix] for the proof.
* This scheme prevents review of redundant edges which would increase the
  amount of work required by the user.
* Edges to review are stored in a priority queue. 
* The initial priority of each edge is `P(match)` --- the likelihood that the
  edge is positive.
* The PCCS in `(V, E_p)` are dynamically maintained.
    * Dynamic connectivity data structure (Levels of Euler Tour Forests)
    * Euler Tours are maintained in a binary search tree with fast split and
      join capabilities. [Sun-2016]
* We pop edges from the priority queue and present them to the user. 
  In each case the user can make one of three decisions:
    * Reviewing an edge as `no-match` between two existing PCCs, indicates
      that the PCCs are different individuals. The priority of other edges
      between those two PCCs can be set to 0.
    * Reviewing an edge as `match` between two existing PCCs they are
      merged into a single PCC. The priority of edges within that PCC can now be
      set to 0. The priority of edges between the new PCC and all other PCCs that 
      it is connected to via `no-match` edges are also set to 0.
    * Reviewing an edge as `not-comp` only sets its own priority to 0 and does
      not influence any other edge.
* Identification is complete when the priority queue contains only no edges
  with positive priority.


## Review Procedure in a practical context

Removing the assumptions in the simplified procedure has three consequences:

1. Some mistakes will pass thresholds.
2. Users will make errors.
3. The one-vs-many algorithm might not add all necessary edges to the
   decision graph.

### Contrasting inconsistency and mistakes
* **Inconsistency** - A PCC containing more than zero negative edges.
* **Mistake** - A review-state that differs from the groundtruth state.
* Inconsistency Implications:
    * An inconsistency implies that a mistake is present, but it does not
      determine which edge contains the mistake.
    * Inconsistencies can be used to detect that mistakes exist.
    * Inconsistencies can only be present if a cycle exists in PCC
      (otherwise the PCC would simply be split in two).
    * If a graph contains inconsistent reviews then it necessarily contains 
      redundant reviews.
* Mistake Discovery: 
    * Mistakes can be present without inconsistencies.
    * Carefully selecting redundant edges to review can cause
      inconsistencies and therefore expose the existence of mistakes.

### Comparison with the simplified context
* Candidate edge selection is the same, except it is no longer guaranteed that
  it is possible to satisfy the identification constraints with these edges.
    * Some necessary positive and negative edges may be missing. 
    * The likelihood that these missing edges are negative is high. 
    * Therefore, unconnected PCCs can be said to have implicit negative edges. 
    * This may cause a small number of false negatives.
* Automatic decisions are the same except now mistakes can occur and possibly
  produce inconsistencies. 
* These inconsistencies are easily detected.
    * Detecting an inconsistency implies a mistake was made.
    * Resolving the inconsistency can correct a mistake.
    * The review priority algorithm is modified with an algorithm for resolving
      inconsistencies (details in [section]).
* Discovering mistakes requires redundant reviews.
    * The simplified review priority algorithm avoids reviewing redundant
      edges.
    * This implies that it is impossible for inconsistencies to be added and
      therefore to discover mistakes.
    * The review priority algorithm is modified with an algorithm for
      discovering mistakes. (details in [section]).
* The user will stop before all termination criteria has been satisfied. 
    * In practice the user will stop reviewing early. 
    * It is important that we are confident and have discovered as many PCCs as
      possible. It is less important that we verify all PCCs are indeed
      different.
    * This might cause false negatives, but does not cause serious practical
      problems because the probability of these unreviewed edges
      match is low.

### Inconsistency recovery
* An inconsistent state can be detected as any PCC that contains a negative
  edge in the decision graph.
* Within an inconsistent PCC find all edges labeled as `no-match`. 
* For each no-match edges with endpoints `(s, t)` run a weighted min-st cut
  using the number of times an edge was reviewed as the weight. 
* If the weight of the no-match edge is greater than the sum of the weights of
  the cut edges append the no-match edge to a list of candidate edges otherwise
  append the cut edges. 
* Stack and return the list of all the candidate edges.
* The review priority algorithm is modified by increase the priority of
  these flagged edges by `2`. This causes flagged edges to move to the top
  of the queue and be resolved before new reviews are considered.

### Mistake discovery
* To discover mistakes we must review redundant edges. 
* We should choose a small number to minimize the number of reviews.
* We should choose edges that are likely to discover an inconsistency if
  one exists.
* Observe that in the simplified algorithm a long chain of edges would be
  linked as a PCC. However, just a single error can cause the endpoints of this 
  chain to be different individuals. By choosing an algorithm which would
  compare these "far away" nodes we can discover errors or be more certain
  that the PCC is indeed matched correctly.
* Specifically we need to augment the minimal set of edges with a small set of
  redundant edges that is likely to expose any errors. 
* This is an edge-augmentation problem.
    * We use k-edge-connected augmentation because it has an intuitive
      interpretation.
    * For a PCC to be contain an undetected error, it must contain at least `k`
      internal errors.
    * Therefore as `k` increases the probability that there are undetected
      errors decreases.
    * See [Appendix] for details.
* The review priority algorithm is modified such that on the modification
  of a PCC the all internal edges have their priority set to 0 except those
  that are the solution of the diameter augmentation instance.
* Adding certain redundant edges to PCCs with mistakes will cause
  inconsistencies which can then be resolved with the Inconsistency
  Recovery Algorithm.

### Discussion of early stopping
* In practice we do not review all negative edges between PCCs.
* There are too many reviews to be made: `choose(len(pccs), 2)`. 
* Reviewing negative edges not add to the knowledge of who individuals are,
  it increases the confidence that the grouping is correct.
* Because pairs with high `P(match)` are reviewed first, the probability
  that remaining edges contain a significant number of positive matches is
  small. Therefore we expect only a small amount of error if we assume
  unreviewed edges are different.

### Discussion of missing candidate edges
* In practice we ignore matching edges that failed to be added to the review
  graph.
* The reasoning is similar to why we don't review all negative edges, the
  probability that any particular edge not in the decision graph is actually
  between correct individuals is low.
* In the case where perfect information is desired it is possible to simply
  review all edges in the priority queue and then add edges between annotations
  in pairs of unreviewed PCCs until all pairs of PCCs have a negative edge
  between them.


### Recomputing candidate edges
 * The one-vs-many algorithm is re-invoked with new name labels. (Note the
   nearest neighbor matching returns the `K` nearest neighbors not belonging to
   the same individual.) (Note this requires a bit of reworking in the actual
   pipeline and requires certain caches to be disabled).

--------------

# Appendix

## Proof of optimality
* Prioritizing review of matching edges (as measured by `P(match)`)
  minimizes the number of reviews
* Let `pccs = { ... { ... a ... } ...}` be the true annotation clusters.
* For each `pcc in pccs` at least `len(pcc) - 1` reviews will need to be made
  to connect the annotations.  Thus the minimum number of positive reviews is: 
  `sum(len(pcc) - 1 for pcc in pccs)`.
* To ensure that there are no merge cases there must be at least one negative
  review between each pair of PCCs.  Thus the minimum number of negative reviews
  needed is `choose(len(pccs), 2)`. (Note: `choose` is the binomial coefficient)
* Because positive and negative edges are disjoint the minimum total number of
  reviews required is: 
    `sum(len(pcc) - 1 for pcc in pccs) + choose(len(pccs), 2)`. 
* A second negative review between components or a second positive edge within
  a component is mutually exclusive from the set of minimal reviews and thus
  strictly increases the total number of reviews.
* When reviewing a positive edge it is always possible to determine if it would
  be redundant with another positive edge that exists. (test if the edge adds a
  cycle to a spanning tree of the PCC).
* On the other hand when reviewing a negative edge it is not always possible to 
  determine if it is redundant with some other negative edge that exists. This
  is because redundant negative edges are defined between positive PCCs. (all positive 
  PCCs must be determined before you can guarantee that any two arbitrary pairs of 
  negative edges are not redundant).
* Reviewing all positive edges first guarantees that all redundant edges
  are never encountered.
* Therefore it is always better to review edges more likely to be positive
  first. 


## Edge Augmentation
* There are many types of edges augmentation
    * d-diameter augmentation 
    * k-vertex-connected augmentation 
    * k-edge-connected augmentation 


## Augmentation K-edge-connected:
* Add a minimum number of edges such that a graph is k-connected.
* Polynomial time for unweighted case.
    * Edge-Connectivity Augmentation Problems  [Watanabe-Nakamura-87]
    * `O(k * min(k, |V|) * |V|^4 * (k|V| + |E|))`
    * `O(k^3 * V^5 + k * V^4 * E)`
* Weighted case is NP-hard
    * On a Smallest Augmentation to k-Edge-connect a Graph [Watanabe-Nakamura-84]
    * <http://www.cs.bme.hu/~dmarx/papers/marx-vegh-conn-icalp2013.pdf>

## Augmentation Diameter-D:
* Given target diameter d, graph `G=(V, E)` and
  candidate non-edges `~E`, find the smallest set of non-edges `E' ⊆ ~E` such that
  the diameter of the augmented graph `G'=(V, E ∪ E')` is at most `E'`. 
* In general this problem is NP-hard, but in the unit-cost unit-length case there
  is an approximation algorithm with approximation ratio O(log(choose(|V|, 2)) * log(d)).
* The basic idea of the approximation algorithm is to:
    * Reformulate the problem as "Restricted Diameter-d" which adds the
      constraint that any new path between nodes that violate the diameter
      constraint in the original graph  must contain either exactly 1 or
      exactly 2 consecutive edges in `~E`. It turns out that any solution to
      "Restricted Diameter-d" is a solution to "Diameter-d".
    * Construct an integer linear program (ILP) that solves "Restricted
      Diameter-d". For the details of this ILP see [Dodis-99].
    * Solve a relaxed version of the ILP to obtain fractional values.
    * Either apply a randomized rounding scheme to achieve an integral solution OR 
      define an instance of hitting set using the fractional values and then 
      approximately solve the hitting set problem using a greedy approach.

## Automatic exemplar selection
* Extract PCC for each individual.
* Use maximum weight minimum set cover to select a subset of annotations.
* Create covering sets by thresholding match probabilities on edges in the PCC
    * Use the one-vs-many algorithm to rank each annotation in the PCC against the PCC
    * Augment the PCC with the top 5 results from the one-vs-many algorithm.
    * Predict one-vs-one match probabilities for all edges in the PCC
    * Cut edges under a threshold
    * Each annotation's covering set is defined by its neighbors.
* Adjust threshold to find optimal cover with a specific number of exemplars.
* The optimal cover is the new set of exemplars.

-------------
# New Idea Scrap


## Exemplars for Redundancy Criterion
* Use exemplars for termination criterion
* If we enforce that there are only 4-5 exemplars per viewpoint, then we can
  afford to augment each PCC into a complete graph and force the user to
  predict on that graph.
