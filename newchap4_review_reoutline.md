----

# Review Procedure Outline

To identify individuals in a dynamic context we combine our algorithms with
human input. Manual reviews are an expensive but powerful resource.
Efficiently utilizing this resource requires a carefully defined procedure that
finds the appropriate trade-off between maximizing the information gained from
each manual interaction and minimizing the number of interactions.  Our review
procedure attempts to do as much automatic work as possible before falling back
on manual reviewers. Our procedure chooses the minimum number of reviews that
achieves animal identification. The procedure is robust and has mechanisms for
detecting errors and recovering from inconsistencies.

----
## Introduction

### Definitions
* The review procedure is formalized around the notion of a **review graph**.
    * The nodes in the review graph are annotations. 
    * Edges are comparisons between two annotations.
        * Each edge has a **review-state** that indicates if it is a: match,
          `no-match`, `not-comp`, or `unreviewed`.
* Individuals are identified by finding a **positive subgraph**. 
    * This is a subgraph of the review graph that only contains edges where the review-state is `match`. 
    * Each connected component (CC) in this subgraph is an identified individual.
* The minimal requirements to uniquely identify all individuals are:
    * Each CC is a spanning tree of positive (`match`) edges that connects
      all annotations belonging to an individual.
        * This determines a group of annotations that are sure to be the same
          individual.
    * Each pair of positive CCs is connected by a negative (`no-match`) edge.
        * This ensures that all CCs are distinct individuals (i.e. all merge
          cases have been found)
        * This determines an algorithm-independent groundtruth labeling.
    * Each positive CC must not contain a (`no-match`) edge between any of its
      vertices.
        * A `no-match` edge within a positive CC implies a split case. 
    * Note: negative edges do not contribute to the identification grouping,
      they only ensure that the positive CCs are complete.
    * Note: only a subset of edges need to be reviewed in order to determine a
      valid identification.

### Procedure overview
* The review procedure is to construct a review graph and assign labels to its
  edges in order to satisfy the identification requirements.
   * To construct the review graph: 
       * All annotations to be identified are used as nodes.
       * An algorithm initializes a sparse set of `unreviewed` candidate edges.
   * To assign labels to the edges:
       * A classifier predicts labels for each edge. Any confident prediction
         is automatically assigns its value to the edge review-state.
       * A subset of the remaining `unreviewed` edges are manually reviewed.

### Discussion outline
* We first consider a simplified version of this procedure. We assume that
  review errors do not occur.  In this context we:
    * Describe how candidate edges are chosen when constructing the review
      graph.
    * Describe how classifications are automatically assigned to edges.
    * Define an optimal ordering for reviewing the minimum number of edges.
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

----
## Review Procedures

### In a simplified context
* Simplifying assumptions: 
    1. Edge classifiers have high threshold and do not make errors.
    2. Users are perfect and do not make errors.
    3. The review graph is constructed such that there exists a subgraph where
       all of the annotations are connected.
* Review graph construction:
    * Given a set of annotations use these as nodes. 
    * Run the one-vs-many algorithm.
        * use each annotation as a query and the entire set of annotations as
          the database.
        * the result is a ranked list of database annotations
    * For each ranked list take the top `N` (we use `N=5`) annotation results
      and create an `unreviewed` candidate edge between the query and each
      result.
* Automatic classification:
    * Predict the probabilities of the match-state and photobomb-state on each
      edge using the one-vs-one classifiers.
    * We automatically review an edge if we are confident in its matching state
      and we are confident that it is not a photobomb.
    * Given a `state-threshold` for each state, automatically set review-state to 
      `state in {match, no-match, not-comp}` if:
        * `P(state) > state-threshold`, and
        * `P.argmax() == state`, and
        * `P(photobomb) < photobomb-threshold`.
* Prioritizing edges for user review:
    * To satisfy minimal identification requirements we observe:
        * Edges within existing CCs do not need to be reviewed. 
            * This means we only need to add edges to ensure each CC is at
              least a spanning tree.
        * Only one edge between any two CCs ever needs to be reviewed.
            * This  implies that Edges between CCs with at least one other
              negative review do not need to be reviewed.
    * Using these observations the minimum number of reviews is achieved by
      reviewing as many positive edges (between existing CCs) as possible
      before reviewing any negative edges. See [Appendix] for the proof.
    * This scheme prevents review of redundant edges which would increase the
      amount of work required by the user.
    * Edges to review are stored in a priority queue. 
    * We initialize the priority of each edge to `P(match)`. This measures
      the likelihood that an edge is positive.
    * We pop edges from the priority queue and present them to the user. 
      In each case the user can make one of three decisions:
        * Reviewing an edge as `no-match` between two existing CCs, indicates
          that the CCs are different individuals. The priority of other edges
          between those two CCs can be set to 0.
        * Reviewing an edge as `match` between two existing CCs they are
          merged into a single CC. The priority of edges within that CC can now be
          set to 0. The priority of edges between the new CC and all other CCs that 
          it is connected to via `no-match` edges are also set to 0.
        * Reviewing an edge as `not-comp` only sets its own priority to 0 and does
          not influence any other edge.
    * When the priority queue is empty identification has been completed.

### In a practical context
* In a practical setting
    1. Some mistakes will pass thresholds.
    2. Users will make errors.
    3. The one-vs-many algorithm might not add all necessary edges to the
       review graph.
* Contrasting mistakes and inconsistency
    * **Mistake** - A review-state that differs from the groundtruth state.
    * **Inconsistency** - A positive CC with a negative edge.
    * Inconsistency Implications:
        * An Inconsistencies implies that a mistake is present although it does
          not determine which edge contains the mistake.
        * Inconsistencies can be used to detect that mistakes exist.
        * Inconsistencies can only be present if a cycle exists in positive CC
          (otherwise the CC would simply be split in two).
        * If a graph contains inconsistent reviews then it necessarily contains 
          redundant reviews.
    * Mistake Discovery: 
        * Mistakes can be present without inconsistencies.
        * Carefully selecting redundant edges to review can cause
          inconsistencies and therefore expose the existence of mistakes.
* Comparison with the simplified context:
    * Graph construction is the same except not all the necessary candidate
      edges may appear in the review graph.
        * This might cause false negatives, but does not cause serious
          practical problems because the probability of these missing edges
          actually matching is low.
    * Automatic decision making is the same except now auto-decisions may make
      mistakes and produce inconsistencies.
        * The review priority algorithm is modified with an algorithm for
          resolving inconsistencies (details in [section]).
    * The simplified review priority algorithm avoids reviewing redundant edges.
        * This implies that it is impossible for inconsistencies to be added
          and therefore to discover mistakes.
        * The review priority algorithm is modified with an algorithm for
          discovering mistakes. (details in [section]).
    * In the simplified algorithm all negative edges are reviewed even after
      the positive components have already been identified.
        * In practice the user will stop reviewing early. 
        * This might cause false negatives, but does not cause serious
          practical problems because the probability of these unreviewed edges
          actually matching is low.
* Inconsistency recovery algorithm:
    * An inconsistent state can be detected as any CC that contains a negative
      edge in the review graph.
    * Within an inconsistent CC find all edges labeled as `no-match`. 
    * For each no-match edges with endpoints `(s, t)` run a weighted min-st cut
      using the number of times an edge was reviewed as the weight. 
    * If the weight of the no-match edge is greater than the sum of the weights of
      the cut edges append the no-match edge to a list of candidate edges otherwise
      append the cut edges. 
    * Stack and return the list of all the candidate edges.
    * The review priority algorithm is modified by increase the priority of
      these flagged edges by `2`. This causes flagged edges to move to the top
      of the queue and be resolved before new reviews are considered.
* Mistake discovery algorithm:
    * To discover mistakes we must review redundant edges. 
    * We should choose a small number to minimize the number of reviews.
    * We should choose edges that are likely to discover an inconsistency if
      one exists.
    * Observe that in the simplified algorithm a long chain of edges would be
      linked as a CC. However, just a single error can cause the endpoints of this 
      chain to be different individuals. By choosing an algorithm which would
      compare these "far away" nodes we can discover errors or be more certain
      that the CC is indeed matched correctly.
    * We choose this set of edges as the minimum set of unreviewed edges that
      would reduce the diameter of the CC to less than a threshold. These set
      of edges can be found using an algorithm that solves the "Weighted Diameter
      Augmentation" problem. See [Appendix] for details.
    * The review priority algorithm is modified such that on the modification
      of a CC the all internal edges have their priority set to 0 except those
      that are the solution of the diameter augmentation instance.
    * Adding certain redundant edges to CCs with mistakes will cause
      inconsistencies which can then be resolved with the Inconsistency
      Recovery Algorithm.
* Discussion of early stopping:
    * In practice we do not review all negative edges between CCs.
    * There are too many reviews to be made: `choose(len(cs), 2)`. 
    * Reviewing negative edges not add to the knowledge of who individuals are,
      it increases the confidence that the grouping is correct.
    * Because pairs with high `P(match)` are reviewed first, the probability
      that remaining edges contain a significant number of positive matches is
      small. Therefore we expect only a small amount of error if we assume
      unreviewed edges are different.
* Discussion of missing candidate edges:
    * In practice we ignore matching edges that failed to be added to the review
      graph.
    * The reasoning is similar to why we don't review all negative edges, the
      probability that any particular edge not in the review graph is actually
      between correct individuals is low.
    * In the case where perfect information is desired it is possible to simply review all 
      edges in the priority queue and then add edges between annotations in
      pairs of unreviewed CCs until all pairs of CCs have a negative edge
      between them.

--------------

# Appendix

* Proof of optimality
    * Prioritizing review of matching edges (as measured by `P(match)`)
      minimizes the number of reviews
    * Let `cs = { ... { ... a ... } ...}` be the true annotation clusters.
    * For each `c in cs` at least `len(c) - 1` reviews will need to be made to
      create a spanning tree otherwise the annotations will not be connected. 
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
      CCs must be determined before you can guarantee that any two arbitrary pairs of 
      negative edges are not redundant).
    * Reviewing all positive edges first guarantees that all redundant edges
      are never encountered.
    * Therefore it is always better to review edges more likely to be positive
      first. 

* Diameter augmentation:
    * Given target diameter d, graph G=(V, E) and
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
          approximately solve the hitting set problem using a greedy approach.
