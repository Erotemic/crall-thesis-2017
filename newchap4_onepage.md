## Chapter 4 - Graph Based Identification

* We first consider a pair of annotations and the questions: "Is the pair
  comparable and are they the same or different?" and "Is the pair a
photobomb?"
* The answers to these questions are assigned to edges on a graph of annotations. 
  We solve the individual identification problem by partitioning this graph 
  into connected components.
* We consider answering these questions using a combination of automatic
  classification and user review.
* We minimize the number of questions presented to a user.
* We develop a strategy to detect and recover from errors.
* **4.2 Learning the 1-v-1 classifiers**
    * Construct a training set of annotation pairs with labels in {match,
      no-match, not-comparable} and {photobomb, not-photobomb} using the top
      middle, bottom, and random results of the 1-vs-M algorithm.
    * **Constructing pairwise feature vectors**
        * For each annotation pair we create a fixed-length feature vector of local
          and global features.
        * Local features measured using reciprocal nearest neighbor 1-vs-1 matching.
            * Measure are: SIFT distance, local normalizer distance, ratio of correspondence
              to local normalizer distance.  spatial verification error in
              location, scale, orientation, keypoint attributes: relative xy-positions,
              scales, and forgroundness weights.
            * Summary statistics (`[sum, mean, std, len]`) consolidate the unordered
              correspondences into a fixed length vector.
        * Global unary and pairwise properties such as per-annotation time,
          gps-lat, gps-lon, viewpoint, and quality and distances between the
          unary values using an appropriate distance metric.
    * Random Forest classifiers learn `P(match_state | X)` and
      `P(photobomb_state | X)`.
    * To handle missing data (NaN values) each decision tree uses the "separate
      class" method `[ding_investigation_2010]`.
* **4.3 Constructing the identification graph**
    * Create graph `G = (V, E)` using all annotations as nodes `V`. The 1-vs-M
      search algorithm is applied to each annotation. An edge is drawn between
      each query and the N=5 top ranked results.
    * The 1-vs-1 classifiers are applied to each edge and the probabilities are
      recorded as attributes.
* **4.4 Minimizing user reviews.**
    * **Automatic decisions**
        * Each edge is assigned a matching / photobomb state if the
          probabilities are above a threshold.
    * **Connected Component Review Algorithm:**
        * Consider the connected compoments using only the edges where the
          decision was that the animals were the same. 
        * Each edge is assigned a review priority based on it liklihood of
          matching and not being a photobomb. (We show how this minimizes the
          number of user decisions)
        * Edges within these compoments and edges between compoments with at
          least one negative review are not consiered for review and have
          priority set to zero.
    * **Handling Inconsistent State.**
        * An inconsistent state is detected when a CC contains a negative edge.
        * For negative edge with endpoints `(s, t)` run a weighted min-st cut
          using the number of times an edge was reviewed as the weight to
          determine potential fixes.
* **4.4 Detecting and Recovering from Errors**
    * To detect errors (inconsistencies) a small set of redundant edges are
      added to the graph that shrink each CC's diameter. (using an
      approximation to the diameter augmentation problem).
    * This handles merge and split cases.
* **4.6 Experiments**
    * Evaluate the accuracy of rankings and separability of the scores.
    * Evaluate the combined accuracy + separability with humans in the loop
      (using a automated model of a non-perfect user)


## Work that has been completed
* I'm able to construct 1-vs-1 features for arbitrary pairs of annotations.
* I've trained 1-vs-1 classifiers for matching and photobombs.
* I've curated a dataset of plain zebras with photobomb labels.
* I've set up the graph-based algorithm structure, this involves: 
    * Constructing the graph edges
    * Creating 1-vs-1 training sets.
    * The priority based connected component review algorithm.
    * The inconsistent edge detection algorithm.
    * A GUI for interacting and visualizing the graph structure.
* I've written a proof showing that my method for assigning priorities
  minimizes the number of reviews.
* I've set up experiments to evaluate separability and rankings. (I've seen
  improvements in accuracy from .92 to over .97).
* I've inspected what the most important features for match classification are
  and pruned features that are not impactful.
* I've implemented a baseline greedy solution to the diameter augmentation
  problem (there are no approximation guarantees).
* I've implemented the set cover algorithm for choosing exemplars.
* A comparison of the VLAD-based ASMK algorithm against the 1-vs-M algorithm.
  (My ASMK implementation was verified on the Oxford Buildings dataset). Using
  comparable configurations the results for
    * Plains zebras 
        * LNBNN: 75.6% @ rank 1.
        * ASMK: 69.69% @ rank 1.
    * Grévy's zebras
        * LNBNN: 84.94% @rank 1.
        * ASMK is: 70.87% @rank 1.

## Work remaining
* Implement the relaxed integer linear program based diameter augmentation
  algorithm.
* Evaluate the photobomb classifier.
* Write the end-to-end test of the system. This involves an engineering effort
  to integrate all of these smaller components.
