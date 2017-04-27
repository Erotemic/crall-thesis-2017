

* Ideally we would have a graph containing a diverse and representative set of
  positive, negative, and incomparable edges.

* Often we are just given a set of annotations (or worse images) with name
  labels.

* a tree of positive edges can be added to each name in these datasets
* automatic viewpoint classifications can be used to guess if a pair is
  incomparable.

* each edge is given a user-id, categorical confidence, and timestamp to
  identify who did the review and their confidence level. 
    * Confidence levels are "unspecified", "guessing", "pretty sure", and "absolutely sure".
    * The user-id can store an algorithm name or a human username.
    * For a human confidence is self reported and defaults to "pretty sure"
    * For an algorithm that uses image information (like the pairwise classifier) the confidence is unspecified, meaning that the produced scores should be considered instead.
    * For an algorithm that uses heuristics (like algorithm that converts name labels to a tree) the confidence is specified as guessing.

* To curate a dataset the pairwise classifier can be trained using the heuristically generated edges.
* Then edges are prioritized for review based on their hardness. 
* Redundancy criteria is disabled in this case, but inconsistency recovery is not.
* The user then starts to correct errors and the resulting inconsistencies. 
* Whenever a user makes a review the confidence on the edge is updated, which
  prevents it from being shown again.


* GZMaster had no labeled incomparable cases and nothing can be inferred from
  viewpoint
* PZ_PB_RF_TRAIN has no labeled incomparable cases and a few can be inferred
  from viewpoint.


* When marking an existing positive edge as negative (and the other positive
  cases exist) you should predict edges within and between the new PCCs C and D
to make sure that the guessed edges don't have more of the same error.
This would prevent cycling between splitting and merging.
