--- Tues December 6 2016 ---

I've written code that trains a photobomb and match classifier.  The match
classifier is pretty good, but the photobomb detector is not.  Some of the
training data needs to be relabeled.

Current challenges that I need to resolve:

The data that I'm using is a subset of a larger dataset.  I also have that
small dataset duplicated on several machines.  I want to fix the data in the
smaller dataset, but I need to be able to propagate those changes across
machines and also back to the larger dataset.

* For the small database on different machines, I can fix the labels on one
  machine and then rsync them to my other machine.
* For merging back into the larger database I need to extend the merge database
  code to overwrite existing entries with new updated entries.

Some examples are misclassified.
I want to see if any of those failure cases are actually labeling errors.
However, I don't want to keep looking at the same misclassified examples. 
I want the program to know how many times I've reviewed a pair so it only 
shows me those that I've reviewed the least.

* I need to have annotation inference write and read from the staging database. 
* The actual annotation matching table needs to be updated to include a how
  many reviews in the staging database agree with the result and how many
  disagree.
